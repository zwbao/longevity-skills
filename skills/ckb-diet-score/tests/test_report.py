"""Rule boundaries and goal handling; expected outputs use printed scoring/HRs."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from personal_report import calculate, levers
from presets import FOODS


class ReportTests(unittest.TestCase):
    def test_each_printed_scoring_criterion(self):
        # Methods: daily vegetables, daily fruit, meat 1–6, legumes >=4, fish >=1.
        cases = [
            ("fresh_vegetables_days_per_week", {0: 0, 6: 0, 7: 1}),
            ("fresh_fruit_days_per_week", {0: 0, 6: 0, 7: 1}),
            ("red_meat_days_per_week", {0: 0, 1: 1, 6: 1, 7: 0}),
            ("legumes_days_per_week", {0: 0, 3: 0, 4: 1, 7: 1}),
            ("fish_days_per_week", {0: 0, 1: 1, 7: 1}),
        ]
        for key, examples in cases:
            for frequency, point in examples.items():
                values = {k: 0 for k, *_ in FOODS}
                values[key] = frequency
                result = calculate(values)
                self.assertEqual(result[key.removesuffix("_days_per_week") + "_points"], point)
                self.assertEqual(result["diet_score"], point)
                self.assertEqual(result["all_cause_hr"], 1.00)  # Table 1: 0–1 referent.
                self.assertIsNone(result["all_cause_ci_lower"])

    def test_targets_recompute_table_rows(self):
        values = dict(zip([k for k, *_ in FOODS], [7, 7, 1, 4, 1]))
        scenario = levers(values, {"fish_days_per_week": 0, "red_meat_days_per_week": 0}, "pooled")
        self.assertEqual(scenario["current"]["diet_score"], 5)
        self.assertEqual(scenario["current"]["all_cause_hr"], 0.74)
        for entry in scenario["levers"]:
            self.assertEqual(entry["outputs"]["diet_score"], 4)
            self.assertEqual(entry["outputs"]["all_cause_hr"], 0.80)
        self.assertEqual(scenario["targets"]["outputs"]["diet_score"], 3)
        self.assertEqual(scenario["targets"]["outputs"]["all_cause_hr"], 0.84)
        self.assertEqual(scenario["current"]["low_risk_diet"], 1)
        self.assertEqual(scenario["targets"]["outputs"]["low_risk_diet"], 0)
        # The meat upper boundary is deliberately not monotonic: 7 days fails.
        values["red_meat_days_per_week"] = 6
        scenario = levers(values, {}, "pooled")
        meat = next(x for x in scenario["sensitivity"] if x["key"] == "red_meat_days_per_week")
        above = next(x for x in meat["scenarios"] if x["to"] == 7)
        self.assertEqual(above["outputs"]["all_cause_hr"], 0.80)
        self.assertEqual(above["outputs"]["diet_score"], 4)

    def test_cli_targets_sex_and_input_errors(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "out"
            target = Path(d) / "target.csv"
            target.write_text("marker,value,unit\n鱼,0,d\n")
            cmd = [sys.executable, str(ROOT / "scripts/personal_report.py"), "--diet",
                   str(ROOT / "references/input-format.csv"), "--targets", str(target),
                   "--sex", "female", "--out", str(out)]
            run = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            result = json.loads((out / "result.json").read_text())["outputs"]
            self.assertEqual(result["all_cause_hr"]["value"], 0.71)  # S4, diet 5.
            scenarios = json.loads((out / "levers.json").read_text())
            self.assertEqual(scenarios["targets"]["outputs"]["all_cause_hr"], 0.75)  # S4, diet 4.
            self.assertEqual(scenarios["targets"]["outputs"]["diet_score"], 4)
            for rows in ("marker,value,unit\n鱼,1,g\n", "marker,value,unit\n鱼,9,d\n",
                         "marker,value,unit\n未知,1,d\n", "marker,value,unit\n"):
                target.write_text(rows)
                run = subprocess.run(cmd, capture_output=True, text=True)
                self.assertEqual(run.returncode, 3, run.stderr)
                self.assertFalse((out / "result.json").exists())
                self.assertTrue((out / "problems.json").exists())
            target.write_text("marker,value,unit\n鱼,0,d\n")
            for extra in (("--age", "nan"), ("--sex", "unknown")):
                run = subprocess.run(cmd + list(extra), capture_output=True, text=True)
                self.assertEqual(run.returncode, 3, run.stderr)


if __name__ == "__main__":
    unittest.main()
