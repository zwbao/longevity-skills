"""Printed table inputs/outputs are specified before the implementation.

Table 1, Diet score, All causes / Cardiovascular diseases / Cancer,
HR (95% CI); Tables S3 and S4 use the same columns for men and women.
These validate a published lookup, not refitting a Cox model or predicting
an individual's absolute mortality. Frequency examples test the printed
Methods scoring rule; they are not claimed to be observed patient cases.
"""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


class ManifestTests(unittest.TestCase):
    def test_table1_printed_diet_rows(self):
        from personal_report import lookup
        expected = {
            0: ((1.00, None, None), (1.00, None, None), (1.00, None, None)),
            1: ((1.00, None, None), (1.00, None, None), (1.00, None, None)),
            2: ((0.90, 0.88, 0.92), (0.88, 0.84, 0.91), (0.95, 0.91, 0.99)),
            3: ((0.84, 0.81, 0.87), (0.81, 0.77, 0.85), (0.92, 0.87, 0.98)),
            4: ((0.80, 0.76, 0.84), (0.73, 0.67, 0.79), (0.92, 0.85, 1.00)),
            5: ((0.74, 0.65, 0.85), (0.62, 0.49, 0.80), (0.80, 0.64, 0.99)),
        }
        for score, row in expected.items():
            self.assertEqual(lookup(score, "pooled"), row)

    def test_sex_specific_printed_diet_rows(self):
        from personal_report import lookup
        # Appendix Table S3 (men), Table S4 (women): Diet score = 5.
        self.assertEqual(lookup(5, "male"),
                         ((0.78, 0.65, 0.94), (0.64, 0.46, 0.89), (0.90, 0.68, 1.20)))
        self.assertEqual(lookup(5, "female"),
                         ((0.71, 0.58, 0.88), (0.64, 0.44, 0.93), (0.67, 0.48, 0.93)))

    def run_report(self, folder, rows, extra=()):
        path = Path(folder) / "diet.csv"
        path.write_text("marker,value,unit\n" + rows, encoding="utf-8")
        out = Path(folder) / "out"
        proc = subprocess.run([sys.executable, str(ROOT / "scripts/personal_report.py"),
                               "--diet", str(path), "--age", "50", "--out", str(out),
                               *extra], capture_output=True, text=True)
        return proc, out

    @staticmethod
    def valid_rows():
        return ("fresh_vegetables_days_per_week,7,d\n"
                "fresh_fruit_days_per_week,7,d\n"
                "red_meat_days_per_week,1,d\n"
                "legumes_days_per_week,4,d\n"
                "fish_days_per_week,1,d\n")

    def test_manifest_units_and_result(self):
        from presets import FOODS, FREQUENCY_UNIT
        manifest = json.loads((ROOT / "skill.json").read_text())
        specs = [x for x in manifest["inputs"] if x["from"] == "measurements"]
        self.assertEqual([x["key"] for x in specs], [x[0] for x in FOODS])
        self.assertTrue(all(x["unit"] == FREQUENCY_UNIT and x["range"] == [0, 7] for x in specs))
        with tempfile.TemporaryDirectory() as d:
            proc, out = self.run_report(d, self.valid_rows())
            self.assertEqual(proc.returncode, 0, proc.stderr)
            result = json.loads((out / "result.json").read_text())["outputs"]
            # All five Methods criteria met; Table 1 Diet score 5 all-cause HR.
            self.assertEqual(result["diet_score"]["value"], 5)
            self.assertEqual(result["all_cause_hr"]["value"], 0.74)
            self.assertEqual(result["all_cause_ci_lower"]["value"], 0.65)
            self.assertEqual(result["all_cause_ci_upper"]["value"], 0.85)
            report = (out / "report.md").read_text()
            self.assertLess(report.index("10.1016/"), report.index("你的饮食得分"))
            self.assertIn("边界", report)
            self.assertIn("人群", report)
            self.assertTrue((out / "levers.json").exists())

    def test_invalid_input_stops_and_removes_stale_results(self):
        bad = [self.valid_rows().replace("7,d", "7,g", 1),
               self.valid_rows().replace("7,d", "8,d", 1),
               self.valid_rows().replace("fish_days_per_week,1,d\n", ""),
               self.valid_rows().replace("7,d", "nan,d", 1)]
        for rows in bad:
            with self.subTest(rows=rows), tempfile.TemporaryDirectory() as d:
                good, out = self.run_report(d, self.valid_rows())
                self.assertEqual(good.returncode, 0, good.stderr)
                proc, out = self.run_report(d, rows)
                self.assertEqual(proc.returncode, 3, proc.stderr)
                self.assertTrue(json.loads((out / "problems.json").read_text())["problems"])
                self.assertFalse((out / "result.json").exists())
                self.assertFalse((out / "levers.json").exists())
                report = (out / "report.md").read_text()
                self.assertNotIn("你的饮食得分", report)
                self.assertIn("10.1016/", report)


if __name__ == "__main__":
    unittest.main()
