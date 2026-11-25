"""Table 3 transcription and synthetic boundary checks, NOT a worked-example reproduction.

Studenski et al. 2014, Table 3 (Men; Women):
Recommended: grip strength (GSMAX): <26 kg; <16 kg.
Alternate: grip strength adjusted for BMI (GSMAXBMI): <1.0; <0.56.
Recommended: ALM adjusted for BMI (ALMBMI): <0.789; <0.512.
Alternate: ALM: <19.75 kg; <15.02 kg.
No individual input/output example was found in the article or Appendix Tables 1–4.
"""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import presets


class TestManifest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.manifest = json.loads((ROOT / "skill.json").read_text())

    def run_report(self, rows=None, sex="male", age="75"):
        if rows is None:
            rows = "grip_max_kg,26,kg\nalm_kg,19.725,kg\nbmi_kg_m2,25,kg/m^2\n"
        csv = self.base / "input.csv"
        csv.write_text("marker,value,unit\n" + rows)
        out = self.base / "out"
        args = [sys.executable, str(ROOT / "scripts/personal_report.py"),
                "--measurements", str(csv), "--out", str(out)]
        if sex is not None:
            args += ["--sex", sex]
        if age is not None:
            args += ["--age", age]
        proc = subprocess.run(args, capture_output=True, text=True)
        report = (out / "report.md").read_text()
        return proc, out, report

    def test_table3_constants(self):
        # Printed constants only; does not claim to reproduce a personal example.
        self.assertEqual(presets.CUTPOINTS["male"],
                         {"grip_max_kg": 26, "grip_bmi": 1.0, "alm_bmi": 0.789, "alm_kg": 19.75})
        self.assertEqual(presets.CUTPOINTS["female"],
                         {"grip_max_kg": 16, "grip_bmi": 0.56, "alm_bmi": 0.512, "alm_kg": 15.02})

    def test_manifest_matches_presets(self):
        specs = {s["key"]: s for s in self.manifest["inputs"]}
        self.assertEqual(set(specs), set(presets.INPUT_UNITS) | {"sex"})
        for key, unit in presets.INPUT_UNITS.items():
            self.assertEqual(specs[key]["unit"], unit)
            self.assertEqual(specs[key]["range"], list(presets.INPUT_RANGES[key]))
        self.assertEqual(self.manifest["validation"]["status"], "draft")

    def test_recommended_exact_boundaries_are_not_low(self):
        # Artificial boundary fixtures; ratio expected values are Table 3 cutpoints.
        for sex, grip, alm, expected in [("male", "26", "19.725", 0.789),
                                         ("female", "16", "12.8", 0.512)]:
            with self.subTest(sex=sex):
                proc, out, report = self.run_report(
                    f"grip_max_kg,{grip},kg\nalm_kg,{alm},kg\nbmi_kg_m2,25,kg/m^2\n", sex)
                self.assertEqual(proc.returncode, 0, proc.stderr)
                result = json.loads((out / "result.json").read_text())["outputs"]
                self.assertEqual(result["alm_bmi"]["value"], expected)
                self.assertEqual(result["weakness"]["value"], "not_below_cutpoint")
                self.assertEqual(result["low_lean_mass"]["value"], "not_below_cutpoint")
                self.assertLess(report.index("## 论文卡片"), report.index("## 你的结果"))
                self.assertIn("边界:", report)
                self.assertIn("10.1093/gerona/glu010", report)

    def test_all_four_strict_inequalities_and_independent_criteria(self):
        from personal_report import calculate
        # Synthetic fixtures at and immediately below each printed threshold.
        for sex, cuts in presets.CUTPOINTS.items():
            for output, key, bmi in [("weakness", "grip_max_kg", 25),
                                     ("weakness_bmi_alternate", "grip_bmi", 25),
                                     ("low_lean_mass", "alm_bmi", 25),
                                     ("low_lean_mass_alternate", "alm_kg", 25)]:
                from decimal import Decimal
                threshold = Decimal(str(cuts[key]))
                for below in (False, True):
                    value = threshold - (Decimal("0.00001") if below else 0)
                    if key.endswith("bmi"):
                        value *= bmi
                    data = {"grip_max_kg": 35, "alm_kg": 25, "bmi_kg_m2": bmi}
                    data["grip_max_kg" if "grip" in key else "alm_kg"] = float(value)
                    self.assertEqual(calculate(data, sex)[output],
                                     "below_cutpoint" if below else "not_below_cutpoint")
        result = calculate({"grip_max_kg": 26, "alm_kg": 19.725, "bmi_kg_m2": 25}, "male")
        self.assertEqual(result["low_lean_mass"], "not_below_cutpoint")
        self.assertEqual(result["low_lean_mass_alternate"], "below_cutpoint")

    def test_aliases_and_exact_unit_conversion(self):
        proc, out, _ = self.run_report("握力,26000,g\n四肢瘦体重,19725,g\n体质指数,25,kg/m2\n", "男")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        result = json.loads((out / "result.json").read_text())["outputs"]
        self.assertEqual(result["alm_bmi"]["value"], 0.789)

    def test_bad_inputs_exit_three_and_remove_stale_results(self):
        proc, out, _ = self.run_report()
        self.assertEqual(proc.returncode, 0)
        cases = [
            ("grip_max_kg,26,N\nalm_kg,19.725,kg\nbmi_kg_m2,25,kg/m^2\n", "male", "75", "unit"),
            ("grip_max_kg,26000,kg\nalm_kg,19.725,kg\nbmi_kg_m2,25,kg/m^2\n", "male", "75", "range"),
            ("grip_max_kg,26,kg\nbmi_kg_m2,25,kg/m^2\n", "male", "75", "missing"),
            (None, None, "75", "missing"), (None, "unknown", "75", "value"),
            (None, "male", None, "missing"), (None, "male", "bad", "value"),
            (None, "male", "64", "range"),
            ("grip_max_kg,nan,kg\nalm_kg,19.725,kg\nbmi_kg_m2,25,kg/m^2\n", "male", "75", None),
        ]
        for rows, sex, age, kind in cases:
            with self.subTest(rows=rows, sex=sex, age=age):
                proc, out, report = self.run_report(rows, sex, age)
                self.assertEqual(proc.returncode, 3, proc.stderr)
                self.assertFalse((out / "result.json").exists())
                problems = json.loads((out / "problems.json").read_text())["problems"]
                if kind:
                    self.assertIn(kind, {p["kind"] for p in problems})
                self.assertIn("## 论文卡片", report)
                self.assertNotIn("## 你的结果", report)
        proc, out, _ = self.run_report()
        self.assertEqual(proc.returncode, 0)
        self.assertFalse((out / "problems.json").exists())


if __name__ == "__main__":
    unittest.main()
