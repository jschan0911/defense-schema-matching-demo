from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "review_server", ROOT / "ui" / "backend" / "server.py"
)
assert SPEC and SPEC.loader
server = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(server)


class StoreTests(unittest.TestCase):
    def test_review_state_persists(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = server.Store(
                ROOT / "tests" / "fixtures" / "demo_predictions.csv",
                ROOT / "data" / "gold_mapping.csv",
                Path(directory) / "review.db",
            )
            rows, total = store.candidates("", "all", 100, 0)
            self.assertEqual(total, 3)
            self.assertEqual(store.summary()["pending"], 3)
            store.review([rows[0]["id"]], "approved")
            self.assertEqual(store.summary()["approved"], 1)
            approved, total = store.candidates("", "approved", 100, 0)
            self.assertEqual(total, 1)
            self.assertEqual(approved[0]["status"], "approved")


if __name__ == "__main__":
    unittest.main()
