#!/usr/bin/env python3
"""Fetch the two official, non-record metadata inputs used by the case study."""

from __future__ import annotations

import hashlib
import json
import urllib.request
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "data" / "public"
SOURCES = {
    "usaspending_data_dictionary.json": (
        "https://api.usaspending.gov/api/v2/references/data_dictionary/"
    ),
    "ocds_release_schema_1_1_5.json": (
        "https://standard.open-contracting.org/schema/1__1__5/release-schema.json"
    ),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    PUBLIC.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, object] = {
        "accessed_date": date.today().isoformat(),
        "contains_raw_award_records": False,
        "files": {},
    }
    for filename, url in SOURCES.items():
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "defense-schema-matching-demo/0.1"},
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            data = response.read()
        parsed = json.loads(data)
        if not isinstance(parsed, dict):
            raise ValueError(f"{filename}: expected a JSON object")
        path = PUBLIC / filename
        path.write_bytes(data)
        manifest["files"][filename] = {  # type: ignore[index]
            "url": url,
            "sha256": sha256(data),
            "bytes": len(data),
        }
    manifest_path = PUBLIC / "fetch_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
