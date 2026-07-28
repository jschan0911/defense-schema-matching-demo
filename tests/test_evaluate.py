from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "evaluate", ROOT / "experiments" / "evaluate.py"
)
assert SPEC and SPEC.loader
evaluate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(evaluate)


class EvaluationTests(unittest.TestCase):
    def test_no_match_aware_metrics(self) -> None:
        truth = {
            ("S", "one"): {("T", "a")},
            ("S", "many"): {("T", "a"), ("T", "b")},
            ("S", "none"): set(),
        }
        predictions = {
            ("S", "one"): [("T", "a")],
            ("S", "many"): [("T", "a"), ("T", "x")],
        }
        values = evaluate.metrics_at_k(truth, predictions, 3)
        self.assertAlmostEqual(values["hit_rate"], 1.0)
        self.assertAlmostEqual(values["macro_recall"], 0.75)
        self.assertAlmostEqual(values["any_hit"], 1.0)
        self.assertAlmostEqual(values["micro_pair_recall"], 2 / 3)
        self.assertAlmostEqual(values["precision"], 2 / 3)
        self.assertAlmostEqual(values["pair_f1"], 2 / 3)
        self.assertAlmostEqual(values["no_match_detection_rate"], 1.0)


if __name__ == "__main__":
    unittest.main()
