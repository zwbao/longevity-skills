"""Expected scores are printed in Lindström & Tuomilehto 2003, Table 1.

Input fixtures select the printed categories; they are not patient examples.
"""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
spec = importlib.util.spec_from_file_location("diabetes_report", ROOT / "scripts/personal_report.py")
report = importlib.util.module_from_spec(spec)
spec.loader.exec_module(report)
from presets import INPUT_UNITS

BASE = {
    "bmi_kg_m2": 25, "waist_cm": 80, "bp_medication_ever": 0,
    "high_glucose_history": 0, "low_activity": 0, "daily_produce": 1,
    "antidiabetic_treatment": 0,
}


def test_table1_printed_age_bmi_scores():
    # Table 1: Age (years): 45–54 ... 0.650 2; 55–64 ... 0.940 3.
    # BMI (kg/m2): >25 to 30 ... 0.015 1.
    for age, expected in [(45, 2), (54, 2), (55, 3), (64, 3)]:
        assert report.score(BASE, age, "male")["age_score"] == expected
    assert report.score(dict(BASE, bmi_kg_m2=30), 45, "male")["bmi_score"] == 1


class ManifestTests(unittest.TestCase):
    def test_table1_remaining_categories(self):
        # Table 1 Score column; p. 727 specifies baseline categories = 0.
        for sex, waist, expected in [("male", 94, 3), ("male", 102, 4),
                                     ("female", 80, 3), ("female", 88, 4)]:
            self.assertEqual(report.score(dict(BASE, waist_cm=waist), 45, sex)["waist_score"], expected)
        for key, output, value, expected in [
            ("bmi_kg_m2", "bmi_score", 30.1, 3),  # representative of printed >30
            ("bp_medication_ever", "bp_medication_score", 1, 2),
            ("high_glucose_history", "high_glucose_score", 1, 5),
            ("low_activity", "activity_score", 1, 2),
            ("daily_produce", "produce_score", 0, 1),
        ]:
            self.assertEqual(report.score(dict(BASE, **{key: value}), 45, "male")[output], expected)
        self.assertEqual(report.score(BASE, 35, "male")["total_score"], 0)
        maximum = dict(BASE, bmi_kg_m2=30.1, waist_cm=102, bp_medication_ever=1,
                       high_glucose_history=1, low_activity=1, daily_produce=0)
        # Printed total range is 0 to 20 (Results p. 727).
        self.assertEqual(report.score(maximum, 64, "male")["total_score"], 20)

    def test_manifest_units(self):
        manifest = json.loads((ROOT / "skill.json").read_text())
        self.assertEqual({s["key"]: s.get("unit", "") for s in manifest["inputs"]}, INPUT_UNITS)

    def run_cli(self, folder, values=None, age="45", sex="male", targets=None, raw=None):
        csv = folder / "measurements.csv"
        if raw is None:
            raw = "marker,value,unit\n" + "".join(
                f"{key},{value},{INPUT_UNITS[key]}\n" for key, value in (BASE if values is None else values).items())
        csv.write_text(raw)
        cmd = [sys.executable, str(ROOT / "scripts/personal_report.py"), "--measurements", str(csv),
               "--out", str(folder / "out")]
        if age is not None:
            cmd += ["--age", age]
        if sex is not None:
            cmd += ["--sex", sex]
        if targets is not None:
            path = folder / "targets.csv"
            path.write_text(targets)
            cmd += ["--targets", str(path)]
        return subprocess.run(cmd, capture_output=True, text=True)

    def test_cli_printed_score_and_paper_card(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            run = self.run_cli(folder)
            self.assertEqual(run.returncode, 0, run.stderr)
            result = json.loads((folder / "out/result.json").read_text())["outputs"]
            # Only the Table 1 age 45–54 category contributes: printed score 2.
            self.assertEqual(result["total_score"]["value"], 2)
            self.assertEqual(result["age_score"]["value"], 2)
            text = (folder / "out/report.md").read_text()
            self.assertLess(text.index("论文卡片"), text.index("你的结果"))
            self.assertIn("边界", text)
            self.assertTrue((folder / "out/levers.json").exists())

    def test_bad_inputs_exit3_and_clear_stale_outputs(self):
        valid_csv = "marker,value,unit\n" + "".join(f"{k},{v},{INPUT_UNITS[k]}\n" for k, v in BASE.items())
        cases = [
            {"raw": valid_csv.replace("waist_cm,80,cm", "waist_cm,80,kg")},
            {"values": dict(BASE, waist_cm=800)},
            {"values": {k: v for k, v in BASE.items() if k != "daily_produce"}},
            {"values": dict(BASE, low_activity=0.5)},
            {"values": dict(BASE, antidiabetic_treatment=1)},
            {"age": "34"}, {"age": "65"}, {"age": "45.5"}, {"age": "nan"},
            {"age": "wrong"}, {"age": None}, {"sex": "unknown"}, {"sex": None},
            {"targets": "marker,value,unit\nbp_medication_ever,0,1\n"},
            {"targets": "marker,value,unit\nunknown,1,1\n"},
            {"targets": "marker,value,unit\nwaist_cm,80,kg\n"},
        ]
        for case in cases:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as tmp:
                folder = Path(tmp)
                self.assertEqual(self.run_cli(folder).returncode, 0)
                run = self.run_cli(folder, **case)
                self.assertEqual(run.returncode, 3, run.stderr)
                self.assertTrue(json.loads((folder / "out/problems.json").read_text())["problems"])
                self.assertFalse((folder / "out/result.json").exists())
                self.assertFalse((folder / "out/levers.json").exists())
                text = (folder / "out/report.md").read_text()
                self.assertIn("论文卡片", text)
                self.assertNotIn("你的总分", text)

    def test_targets_discrete_changes_and_unit_conversion(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            values = dict(BASE, waist_cm=102)
            run = self.run_cli(folder, values, targets="marker,value,unit\n腰围,0.94,m\n")
            self.assertEqual(run.returncode, 0, run.stderr)
            data = json.loads((folder / "out/levers.json").read_text())
            # Table 1 waist score 4 -> 3; age score stays 2.
            self.assertEqual(data["levers"][0]["score_delta"], 3 - 4)
            self.assertEqual(data["targets"]["outputs"]["waist_score"], 3)
            self.assertEqual(data["targets"]["outputs"]["age_score"], 2)
            self.assertEqual(len(data["sensitivity"]), len(INPUT_UNITS))

    def test_nine_point_cutoff(self):
        # Figure 1 and p. 728 print the >=9 cutoff.
        for history, expected in [(0, "below_cutoff"), (1, "at_or_above_cutoff")]:
            values = dict(BASE, bp_medication_ever=1, high_glucose_history=history)
            output = report.score(values, 45, "male")
            if history:
                self.assertEqual(output["total_score"], 9)
            self.assertEqual(output["cutoff_category"], expected)


if __name__ == "__main__":
    unittest.main()
