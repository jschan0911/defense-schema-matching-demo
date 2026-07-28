from __future__ import annotations

import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DataTests(unittest.TestCase):
    def test_three_isolated_cases_are_registered(self) -> None:
        catalog = json.loads((ROOT / "cases" / "catalog.json").read_text())
        cases = {item["id"]: item for item in catalog["cases"]}
        self.assertEqual(
            set(cases),
            {
                "usaspending-ocds",
                "reference-demo-reconstruction",
                "d2b-contract-standard",
            },
        )
        self.assertIsNone(cases["d2b-contract-standard"]["predictions"])

    def test_reference_demo_observed_data_and_baseline_are_bounded(self) -> None:
        payload = json.loads(
            (
                ROOT / "cases" / "reference_demo_reconstruction" / "datasets.json"
            ).read_text()
        )
        self.assertIn("합성", payload["notice"])
        self.assertEqual(len(payload["datasets"]), 5)
        baseline = json.loads(
            (
                ROOT
                / "cases"
                / "reference_demo_reconstruction"
                / "observable_reference.json"
            ).read_text()
        )
        self.assertEqual(baseline["page_reported_total"], 16)
        self.assertEqual(baseline["fully_visible_candidates_recorded"], 9)
        self.assertEqual(len(baseline["candidates"]), 9)
        self.assertFalse(
            (
                ROOT
                / "cases"
                / "reference_demo_reconstruction"
                / "predictions.csv"
            ).exists()
        )
        with (
            ROOT / "cases" / "reference_demo_reconstruction" / "ontology_schema.csv"
        ).open(newline="") as handle:
            schema = list(csv.DictReader(handle))
        self.assertEqual(len(schema), 27)
        self.assertTrue(
            all(row["sample_values_policy"] == "not_passed_primary" for row in schema)
        )
        adapter = json.loads(
            (ROOT / "outputs" / "reference_demo" / "adapter_manifest.json").read_text()
        )
        self.assertEqual(
            adapter["official_commit"],
            "1339fedf8113fc3746d5664f1453248e47ee310c",
        )
        self.assertEqual(
            adapter["adapter_patch_sha256"],
            "491efc93e9672ed13387ccba6feedbfa6014886a4239de6dccfa38cdd663f7d0",
        )
        self.assertEqual(
            adapter["adapter_modified_upstream_files"],
            [
                "utils/llm.py",
                "utils/embedding.py",
                "schema_matching/column_rank.py",
            ],
        )
        self.assertEqual(len(adapter["benchmarks"]), 5)
        estimate = json.loads(
            (ROOT / "outputs" / "reference_demo" / "dry_run_estimate.json").read_text()
        )
        self.assertTrue(estimate["gate_passed"])
        self.assertFalse(estimate["network_or_model_calls_made"])
        comparison = json.loads(
            (ROOT / "outputs" / "reference_demo" / "comparison.json").read_text()
        )
        self.assertEqual(comparison["schemora_status"], "not_run")
        self.assertIsNone(comparison["candidate_similarity"])
        self.assertFalse(comparison["gold_metrics"]["publishable"])

    def test_korean_case_has_source_target_and_draft_gold(self) -> None:
        payload = json.loads(
            (ROOT / "cases" / "d2b_contract_standard" / "datasets.json").read_text()
        )
        self.assertEqual(
            [item["role"] for item in payload["datasets"]], ["Source", "Target"]
        )
        with (ROOT / "cases" / "d2b_contract_standard" / "gold_mapping.csv").open(
            newline=""
        ) as handle:
            gold = list(csv.DictReader(handle))
        self.assertEqual(len(gold), 13)
        self.assertTrue(
            all(
                row["review_status"] == "requires_independent_procurement_sme_review"
                for row in gold
            )
        )

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
