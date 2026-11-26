"""Printed expectations: Kivipelto et al. 2006, Tables 2–4 (pp. 737–738)."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
spec = importlib.util.spec_from_file_location("caide_report", ROOT / "scripts/personal_report.py")
report = importlib.util.module_from_spec(spec)
spec.loader.exec_module(report)
from presets import INPUT_UNITS

BASE = {"education_years": 10, "sbp_mmhg": 140, "bmi_kg_m2": 30,
        "total_cholesterol_mmol_l": 6.5, "active": 1}


def test_table3_printed_risk_lookup():
    # Table 3, Score / Risk cells, both endpoints of every printed interval.
    for model, rows in [(1, [(0, 5, 1.0), (6, 7, 1.9), (8, 9, 4.2),
                            (10, 11, 7.4), (12, 15, 16.4)]),
                        (2, [(0, 5, 0.3), (6, 8, 1.7), (9, 10, 4.6),
                            (11, 12, 4.4), (13, 18, 16.3)])]:
        for low, high, expected in rows:
            for score in (low, high):
                assert report.lookup(score, model)["risk_pct"] == expected


def test_table4_printed_profiles():
    # Table 4 prints categories, not exact measurements: fixtures choose values
    # within those categories. Expected totals and probabilities are printed.
    profiles = [
        (dict(BASE), 46, "female", 0, (0, 0.13), (0, 0.09)),
        (dict(BASE, education_years=9, sbp_mmhg=141,
              total_cholesterol_mmol_l=6.6, active=0), 53, "female", 0,
         (10, 6.91), (10, 4.06)),
        (dict(BASE, education_years=6, sbp_mmhg=141, bmi_kg_m2=31,
              total_cholesterol_mmol_l=6.6, active=0), 54, "male", 1,
         (15, 35.55), (18, 48.93)),
    ]
    for values, age, sex, apoe, first, second in profiles:
        for model, expected in [(1, first), (2, second)]:
            result = report.score(dict(values, apoe_e4=apoe), age, sex, model)
            assert result["total_score"] == expected[0]
            # Table 4 rounds percentages to 2 decimals; half of the last unit.
            assert abs(result["model_risk_20y_pct"] - expected[1]) <= 0.005


class ManifestTests(unittest.TestCase):
    def test_paper_examples(self):
        test_table3_printed_risk_lookup()
        test_table4_printed_profiles()

    def test_manifest_units(self):
        manifest = json.loads((ROOT / "skill.json").read_text())
        self.assertEqual({s["key"]: s.get("unit", "") for s in manifest["inputs"]}, INPUT_UNITS)

    def run_cli(self, folder, values=None, age="46", sex="female", model="1", targets=None, raw=None):
        csv = folder / "measurements.csv"
        if raw is None:
            raw = "marker,value,unit\n" + "".join(
                f"{k},{v},{INPUT_UNITS[k]}\n" for k, v in (BASE if values is None else values).items())
        csv.write_text(raw)
        cmd = [sys.executable, str(ROOT / "scripts/personal_report.py"),
               "--measurements", str(csv), "--model", model, "--out", str(folder / "out")]
        if age is not None:
            cmd += ["--age", age]
        if sex is not None:
            cmd += ["--sex", sex]
        if targets is not None:
            path = folder / "targets.csv"
            path.write_text(targets)
            cmd += ["--targets", str(path)]
        return subprocess.run(cmd, capture_output=True, text=True)

    def test_cli_printed_profile_and_card(self):
        for model, expected in [("1", 0.13), ("2", 0.09)]:
            with tempfile.TemporaryDirectory() as tmp:
                folder = Path(tmp)
                run = self.run_cli(folder, dict(BASE, apoe_e4=0), model=model)
                self.assertEqual(run.returncode, 0, run.stderr)
                result = json.loads((folder / "out/result.json").read_text())["outputs"]
                self.assertEqual(result["total_score"]["value"], 0)
                self.assertAlmostEqual(result["model_risk_20y_pct"]["value"], expected, delta=0.005)
                text = (folder / "out/report.md").read_text()
                self.assertLess(text.index("论文卡片"), text.index("你的结果"))
                self.assertIn("边界：", text)

    def test_bad_inputs_exit3_and_clear_stale_outputs(self):
        valid = "marker,value,unit\n" + "".join(f"{k},{v},{INPUT_UNITS[k]}\n" for k, v in BASE.items())
        cases = [
            {"raw": valid.replace("sbp_mmhg,140,mmHg", "sbp_mmhg,140,kg")},
            {"values": dict(BASE, sbp_mmhg=1400)},
            {"values": {k: v for k, v in BASE.items() if k != "active"}},
            {"values": dict(BASE, active=0.5)}, {"values": dict(BASE, education_years=6.5)},
            {"values": dict(BASE, apoe_e4=2), "model": "2"}, {"model": "2"},
            {"age": "38"}, {"age": "65"}, {"age": "46.5"}, {"age": "nan"},
            {"age": "wrong"}, {"age": None}, {"sex": "unknown"}, {"sex": None},
            {"targets": "marker,value,unit\neducation_years,10,a\n"},
            {"targets": "marker,value,unit\napoe_e4,0,1\n"},
            {"targets": "marker,value,unit\nunknown,1,1\n"},
            {"targets": "marker,value,unit\nsbp_mmhg,140,kg\n"},
            {"targets": "marker,value,unit\n"},
            {"raw": valid + "SBP,150,mmHg\n"},
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
                self.assertIn("论文卡片", (folder / "out/report.md").read_text())

    def test_table2_thresholds_and_targets(self):
        for model in (1, 2):
            for age, expected in [(46, 0), (47, 3), (53, 3), (54, 4 if model == 1 else 5)]:
                self.assertEqual(report.score(dict(BASE, apoe_e4=0), age, "female", model)["age_score"], expected)
            for education, expected in [(10, 0), (9, 2 if model == 1 else 3),
                                         (7, 2 if model == 1 else 3), (6, 3 if model == 1 else 4)]:
                self.assertEqual(report.score(dict(BASE, education_years=education, apoe_e4=0), 46,
                                              "female", model)["education_score"], expected)
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            run = self.run_cli(folder, dict(BASE, sbp_mmhg=141),
                               targets="marker,value,unit\nSBP,140,mmHg\n")
            self.assertEqual(run.returncode, 0, run.stderr)
            data = json.loads((folder / "out/levers.json").read_text())
            self.assertEqual(data["levers"][0]["score_delta"], 0 - 2)
            self.assertEqual(data["targets"]["outputs"]["total_score"], 0)
            self.assertEqual(len(data["sensitivity"]), 8)

    def test_units_aliases_and_cutoffs(self):
        manifest = json.loads((ROOT / "skill.json").read_text())
        import skillkit
        rows = [{"marker": "总胆固醇", "value": 251.3225, "unit": "mg/dL"},
                {"marker": "SBP", "value": 20, "unit": "kPa"}]
        data = skillkit.collect_measurements(rows, manifest)
        self.assertAlmostEqual(data.values["total_cholesterol_mmol_l"], 6.5)
        self.assertAlmostEqual(data.values["sbp_mmhg"], 20 * 7.500617)
        for model, threshold in [(1, 9), (2, 10)]:
            self.assertEqual(report.cutoff(threshold, model), "at_or_above_cutoff")
            self.assertEqual(report.cutoff(threshold - 1, model), "below_cutoff")


if __name__ == "__main__":
    unittest.main()
