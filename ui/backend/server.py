#!/usr/bin/env python3
"""Local review API and static server for real SCHEMORA prediction CSVs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import mimetypes
import sqlite3
import threading
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Protocol
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parents[2]
FRONTEND = ROOT / "ui" / "frontend"
ALLOWED_STATUS = {"pending", "approved", "ignored"}


def candidate_id(row: dict[str, str]) -> str:
    text = "|".join(
        row.get(key, "")
        for key in (
            "run_id",
            "source_table",
            "source_column",
            "rank",
            "target_object_type",
            "target_property",
        )
    )
    return hashlib.sha256(text.encode()).hexdigest()[:20]


class OntologySink(Protocol):
    def apply(self, mappings: list[dict[str, str]]) -> dict[str, object]: ...


class MockOntologySink:
    def apply(self, mappings: list[dict[str, str]]) -> dict[str, object]:
        return {
            "applied": False,
            "mock": True,
            "would_apply": len(mappings),
            "message": "Ontology mutation is intentionally not implemented.",
        }


class Store:
    def __init__(self, predictions: Path, gold: Path, database: Path) -> None:
        self.predictions_path = predictions
        self.gold_path = gold
        self.database = database
        self.lock = threading.Lock()
        self.rows: list[dict[str, str]] = []
        self.gold: dict[tuple[str, str], str] = {}
        database.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS reviews (
                    candidate_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL CHECK(status IN ('pending','approved','ignored')),
                    updated_at TEXT NOT NULL
                )
                """
            )
        self.reload()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database)
        connection.row_factory = sqlite3.Row
        return connection

    def reload(self) -> None:
        if not self.predictions_path.exists():
            raise FileNotFoundError(
                f"prediction CSV not found: {self.predictions_path}. "
                "Run SCHEMORA or start with --demo."
            )
        with self.gold_path.open(encoding="utf-8", newline="") as handle:
            gold_rows = list(csv.DictReader(handle))
        self.gold = {
            (row["source_table"], row["source_column"]): row["mapping_type"]
            for row in gold_rows
        }
        with self.predictions_path.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        for row in rows:
            row["id"] = candidate_id(row)
            row["mapping_type"] = self.gold.get(
                (row["source_table"], row["source_column"]), "unknown"
            )
        with self.lock:
            self.rows = rows

    def statuses(self) -> dict[str, str]:
        with self.connect() as connection:
            return {
                str(row["candidate_id"]): str(row["status"])
                for row in connection.execute(
                    "SELECT candidate_id, status FROM reviews"
                )
            }

    def candidates(
        self, query: str, status: str, limit: int, offset: int
    ) -> tuple[list[dict[str, str]], int]:
        statuses = self.statuses()
        needle = query.casefold()
        with self.lock:
            rows = [dict(row) for row in self.rows]
        result: list[dict[str, str]] = []
        for row in rows:
            row["status"] = statuses.get(row["id"], "pending")
            haystack = " ".join(
                row.get(key, "")
                for key in (
                    "source_table",
                    "source_column",
                    "target_object_type",
                    "target_property",
                    "explanation",
                )
            ).casefold()
            if needle and needle not in haystack:
                continue
            if status != "all" and row["status"] != status:
                continue
            result.append(row)
        return result[offset : offset + limit], len(result)

    def summary(self) -> dict[str, int]:
        statuses = self.statuses()
        with self.lock:
            identifiers = [row["id"] for row in self.rows]
        counts = {"total": len(identifiers), "pending": 0, "approved": 0, "ignored": 0}
        for identifier in identifiers:
            counts[statuses.get(identifier, "pending")] += 1
        return counts

    def review(self, identifiers: list[str], status: str) -> int:
        if status not in ALLOWED_STATUS:
            raise ValueError(f"invalid status: {status}")
        valid = {row["id"] for row in self.rows}
        chosen = [identifier for identifier in identifiers if identifier in valid]
        now = datetime.now(timezone.utc).isoformat()
        with self.connect() as connection:
            connection.executemany(
                """
                INSERT INTO reviews(candidate_id, status, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(candidate_id) DO UPDATE
                SET status=excluded.status, updated_at=excluded.updated_at
                """,
                [(identifier, status, now) for identifier in chosen],
            )
        return len(chosen)


class Handler(BaseHTTPRequestHandler):
    store: Store
    sink: OntologySink = MockOntologySink()

    def send_json(self, payload: object, status: int = 200) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def read_json(self) -> dict[str, object]:
        length = int(self.headers.get("Content-Length", "0"))
        if length > 1_000_000:
            raise ValueError("request body too large")
        return json.loads(self.rfile.read(length) or b"{}")

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/api/summary":
            self.send_json(self.store.summary())
            return
        if parsed.path == "/api/candidates":
            params = parse_qs(parsed.query)
            query = params.get("q", [""])[0]
            status = params.get("status", ["all"])[0]
            if status not in ALLOWED_STATUS | {"all"}:
                self.send_json({"error": "invalid status"}, 400)
                return
            limit = min(max(int(params.get("limit", ["200"])[0]), 1), 1000)
            offset = max(int(params.get("offset", ["0"])[0]), 0)
            rows, total = self.store.candidates(query, status, limit, offset)
            self.send_json({"rows": rows, "filtered_total": total})
            return
        self.serve_static(parsed.path)

    def do_POST(self) -> None:  # noqa: N802
        try:
            payload = self.read_json()
            if self.path == "/api/reviews":
                identifiers = payload.get("ids", [])
                status = str(payload.get("status", ""))
                if not isinstance(identifiers, list):
                    raise ValueError("ids must be a list")
                count = self.store.review([str(item) for item in identifiers], status)
                self.send_json({"updated": count, "summary": self.store.summary()})
                return
            if self.path == "/api/reload":
                self.store.reload()
                self.send_json({"reloaded": True, "summary": self.store.summary()})
                return
            if self.path == "/api/apply":
                rows, _ = self.store.candidates("", "approved", 1000, 0)
                self.send_json(self.sink.apply(rows))
                return
            self.send_json({"error": "not found"}, 404)
        except (ValueError, json.JSONDecodeError) as error:
            self.send_json({"error": str(error)}, 400)

    def serve_static(self, path: str) -> None:
        relative = "index.html" if path in {"", "/"} else path.lstrip("/")
        candidate = (FRONTEND / relative).resolve()
        try:
            candidate.relative_to(FRONTEND.resolve())
        except ValueError:
            self.send_error(HTTPStatus.FORBIDDEN)
            return
        if not candidate.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        data = candidate.read_bytes()
        content_type = (
            mimetypes.guess_type(candidate.name)[0] or "application/octet-stream"
        )
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format: str, *args: object) -> None:
        print(f"{self.address_string()} - {format % args}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--predictions",
        type=Path,
        default=ROOT / "outputs" / "predictions.csv",
    )
    parser.add_argument("--gold", type=Path, default=ROOT / "data" / "gold_mapping.csv")
    parser.add_argument("--db", type=Path, default=ROOT / "ui" / "review.db")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--demo", action="store_true")
    args = parser.parse_args()
    predictions = (
        ROOT / "tests" / "fixtures" / "demo_predictions.csv"
        if args.demo
        else args.predictions
    )
    Handler.store = Store(predictions, args.gold, args.db)
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(
        f"Review interface: http://{args.host}:{args.port} "
        f"({'DEMO fixture' if args.demo else 'REAL predictions'})"
    )
    server.serve_forever()


if __name__ == "__main__":
    main()
