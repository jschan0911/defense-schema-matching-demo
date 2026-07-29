from __future__ import annotations

import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "cases" / "reference_demo_reconstruction"
OUTPUT = ROOT / "outputs" / "reference_demo"


class DataTests(unittest.TestCase):
    def test_only_reference_demo_is_registered(self) -> None:
        catalog = json.loads((ROOT / "cases" / "catalog.json").read_text())
        self.assertEqual(len(catalog["cases"]), 1)
        case = catalog["cases"][0]
        self.assertEqual(case["id"], "reference-demo-reconstruction")
        self.assertEqual(
            case["predictions"], "outputs/reference_demo/predictions.csv"
        )

    def test_observed_data_and_baseline_are_bounded(self) -> None:
        payload = json.loads((CASE / "datasets.json").read_text())
        self.assertIn("합성", payload["notice"])
        self.assertEqual(len(payload["datasets"]), 5)

        baseline = json.loads((CASE / "observable_reference.json").read_text())
        self.assertEqual(baseline["page_reported_total"], 16)
        self.assertEqual(baseline["fully_visible_candidates_recorded"], 9)
        self.assertEqual(len(baseline["candidates"]), 9)
        self.assertEqual(
            baseline["confidence_bands_observed"],
            {
                "높음": "score >= 90",
                "중간": "70 <= score <= 89",
                "낮음": "score < 70",
            },
        )

    def test_schema_and_execution_are_frozen(self) -> None:
        with (CASE / "ontology_schema.csv").open(newline="") as handle:
            schema = list(csv.DictReader(handle))
        self.assertEqual(len(schema), 28)
        self.assertTrue(
            all(row["sample_values_policy"] == "not_passed_primary" for row in schema)
        )

        adapter = json.loads((OUTPUT / "adapter_manifest.json").read_text())
        self.assertEqual(
            adapter["official_commit"],
            "1339fedf8113fc3746d5664f1453248e47ee310c",
        )
        self.assertEqual(
            adapter["adapter_patch_sha256"],
            "491efc93e9672ed13387ccba6feedbfa6014886a4239de6dccfa38cdd663f7d0",
        )
        self.assertEqual(len(adapter["benchmarks"]), 5)
        self.assertIn("zero-row mapping parquet", adapter["input_policy"]["gold"])

        with (OUTPUT / "predictions.csv").open(newline="") as handle:
            predictions = list(csv.DictReader(handle))
        self.assertEqual(len(predictions), 135)

    def test_positive_only_evaluation_boundaries(self) -> None:
        manifest = json.loads((CASE / "gold_manifest.json").read_text())
        self.assertEqual(manifest["conceptual_positive_relations"], 4)
        self.assertEqual(manifest["directed_evaluation_rows"], 5)
        self.assertFalse(manifest["complete_for_all_source_fields"])
        self.assertFalse(manifest["publishable_precision_or_f1"])

        comparison = json.loads((OUTPUT / "comparison.json").read_text())
        self.assertEqual(comparison["schemora_status"], "loaded")
        self.assertEqual(
            comparison["saved_link_positive_recovery"]["at_k"]["5"][
                "directed_hits"
            ],
            4,
        )
        self.assertFalse(comparison["gold_metrics"]["publishable"])

    def test_ui_score_semantics_are_documented(self) -> None:
        guide = (ROOT / "docs" / "ui_score_guide_ko.md").read_text()
        self.assertIn("round(vector_score × 100)", guide)
        self.assertIn("높음 `≥90`", guide)
        self.assertIn("확률·정확도·신뢰도가 아님", guide)

    def test_ranked_results_are_complete_and_sorted(self) -> None:
        with (OUTPUT / "predictions_by_rank.csv").open(newline="") as handle:
            rows = list(csv.DictReader(handle))
        keys = [
            (
                int(row["rank"]),
                row["source_table"],
                row["source_column"],
                row["target_object_type"],
                row["target_property"],
            )
            for row in rows
        ]
        self.assertEqual(len(rows), 135)
        self.assertEqual(keys, sorted(keys))

        report = (ROOT / "docs" / "schemora_ranked_results.md").read_text()
        self.assertIn("후보 **135건 전체**", report)
        self.assertEqual(
            sum(line.startswith("| 1 | `") for line in report.splitlines()),
            28,
        )

    def test_readme_embeds_both_ui_screenshots(self) -> None:
        readme = (ROOT / "README.md").read_text()
        self.assertIn(
            "![Reference 관찰값 UI](docs/assets/reference-ui-observed-values.jpg)",
            readme,
        )
        self.assertIn(
            "![SCHEMORA 결과 UI](docs/assets/schemora-ui-actual-results.jpg)",
            readme,
        )


if __name__ == "__main__":
    unittest.main()
