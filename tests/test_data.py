from __future__ import annotations

import csv
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DataTests(unittest.TestCase):
    def rows(self, name: str) -> list[dict[str, str]]:
        with (ROOT / "data" / name).open(encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))

    def test_fixed_schema_sizes_and_hashes(self) -> None:
        source = self.rows("source_schema.csv")
        target = self.rows("target_ontology.csv")
        manifest = json.loads(
            (ROOT / "data" / "schema_manifest.json").read_text(encoding="utf-8")
        )
        self.assertEqual(len(source), 55)
        self.assertEqual(len({row["TableName"] for row in source}), 5)
        self.assertEqual(len(target), 108)
        self.assertEqual(len({row["ObjectType"] for row in target}), 10)
        self.assertTrue(manifest["target_fixed_before_gold"])
        self.assertFalse(manifest["llm_generated_metadata"])

    def test_gold_is_complete_and_targets_exist(self) -> None:
        source = {
            (row["TableName"], row["ColumnName"])
            for row in self.rows("source_schema.csv")
        }
        target = {
            (row["ObjectType"], row["PropertyName"])
            for row in self.rows("target_ontology.csv")
        }
        gold = self.rows("gold_mapping.csv")
        self.assertEqual(
            source,
            {(row["source_table"], row["source_column"]) for row in gold},
        )
        self.assertGreaterEqual(
            len(
                {
                    (row["source_table"], row["source_column"])
                    for row in gold
                    if row["mapping_type"] == "no-match"
                }
            ),
            5,
        )
        for row in gold:
            if row["target_object_type"]:
                self.assertIn(
                    (row["target_object_type"], row["target_property"]), target
                )
            self.assertTrue(row["rationale"])
            self.assertTrue(row["evidence_location"])


if __name__ == "__main__":
    unittest.main()
