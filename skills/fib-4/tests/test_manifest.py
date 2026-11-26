"""Printed FIB-4 examples first; remaining checks enforce the input contract."""
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ManifestTests(unittest.TestCase):
    def run_report(self, directory, rows=None, age="45", source_exists=True):
        directory = Path(directory)
        source = directory / "measurements.csv"
        if source_exists:
            source.write_text("item,value,unit\n" + (rows if rows is not None else
                              "AST,110,U/L\nALT,100,U/L\nPLT,99,10^9/L\n"), encoding="utf-8")
        command = [sys.executable, str(ROOT / "scripts/personal_report.py"),
                   "--measurements", str(source), "--out", str(directory / "out")]
        if age is not None:
            command += ["--age", age]
        return subprocess.run(command, capture_output=True, text=True), directory / "out"

    def test_paper_example_five(self):
        # Results, Development of a Novel Model to Predict Fibrosis, example 1:
        # 45 years; AST 110 U/L; PLT 99 x 10^9/L; ALT 100 U/L; FIB-4 = 5.
        with tempfile.TemporaryDirectory() as d:
            proc, out = self.run_report(d, "AST,110,U/L\nALT,100,U/L\nPLT,99,10^9/L\n", "45")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            result = json.loads((out / "result.json").read_text())["outputs"]
            self.assertAlmostEqual(result["fib4_index"]["value"], 5, delta=1e-12)

    def test_paper_example_one(self):
        # Same section, example 2: 35 years; AST 75; PLT 263; ALT 100;
        # printed FIB-4 = 1.0 (one decimal). Tolerance 0.05 is half that digit.
        with tempfile.TemporaryDirectory() as d:
            proc, out = self.run_report(d, "AST,75,U/L\nALT,100,U/L\nPLT,263,10^9/L\n", "35")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            result = json.loads((out / "result.json").read_text())["outputs"]
            self.assertAlmostEqual(result["fib4_index"]["value"], 1.0, delta=0.05)
            # Rounded printed 1.0 must not promote the raw value into Table 5B's high band.
            self.assertEqual(result["moderate_advanced_fibrosis_band"]["value"], "indeterminate")

    def test_manifest_units_and_published_cuts(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        import presets
        manifest = json.loads((ROOT / "skill.json").read_text())
        self.assertEqual({s["key"]: s["unit"] for s in manifest["inputs"]}, presets.INPUT_UNITS)
        self.assertEqual(presets.ADVANCED_CUTS, (1.45, 3.25))
        self.assertEqual(presets.MODERATE_ADVANCED_CUTS, (0.6, 1.0))
        self.assertEqual(manifest["validation"]["status"], "reproduced")
        self.assertEqual(manifest["inputs_status"], "verified")

    def test_both_tables_use_exact_inclusive_cutoffs(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        import presets
        for cuts in [presets.ADVANCED_CUTS, presets.MODERATE_ADVANCED_CUTS]:
            lower, upper = cuts
            self.assertEqual(presets.band(lower, cuts), "low")
            self.assertEqual(presets.band(math.nextafter(lower, math.inf), cuts), "indeterminate")
            self.assertEqual(presets.band(math.nextafter(upper, -math.inf), cuts), "indeterminate")
            self.assertEqual(presets.band(upper, cuts), "high")

    def test_aliases_units_and_chinese_report_reproduce_first_example(self):
        # Same published first example, represented in alternate exact units.
        rows_list = [
            "谷草转氨酶,110,U/L\n谷丙转氨酶,100,U/L\n血小板计数,99000,/µL\n",
            f"SGOT,{110 / 60},µkat/L\nSGPT,{100 / 60},ukat/L\nplatelet count,99,10^3/µL\n",
            "ast_u_l,110,\nalt_u_l,100,\nplatelets_10e9_l,99,\n",
        ]
        for rows in rows_list:
            with self.subTest(rows=rows), tempfile.TemporaryDirectory() as d:
                proc, out = self.run_report(d, rows)
                self.assertEqual(proc.returncode, 0, proc.stderr)
                result = json.loads((out / "result.json").read_text())["outputs"]
                self.assertAlmostEqual(result["fib4_index"]["value"], 5, delta=1e-12)
                self.assertEqual(result["advanced_fibrosis_band"]["value"], "high")
                self.assertEqual(result["moderate_advanced_fibrosis_band"]["value"], "high")
                report = (out / "report.md").read_text()
                self.assertLess(report.index("论文卡片"), report.index("你的结果"))
                self.assertIn("边界:", report)
                self.assertIn("HIV/HCV 共感染", report)
                self.assertIn("不能直接外推到一般体检人群", report)
                self.assertNotIn("80%", report)

    def test_invalid_inputs_exit_three_without_stale_result(self):
        default = "AST,110,U/L\nALT,100,U/L\nPLT,99,10^9/L\n"
        cases = [
            (default.replace("AST,110,U/L", "AST,110,mg/dL"), "45"),
            (default.replace("PLT,99", "PLT,99000"), "45"),
            (default.replace("ALT,100,U/L\n", ""), "45"),
            (default.replace("AST,110,U/L", "AST,110,"), "45"),
            (default.replace("PLT,99,10^9/L", "PLT,99,"), "45"),
            (default.replace("ALT,100", "ALT,0"), "45"),
            (default.replace("AST,110", "AST,-1"), "45"),
            (default.replace("PLT,99", "PLT,0"), "45"),
            (default.replace("ALT,100", "ALT,nan"), "45"),
            (default.replace("AST,110", "AST,>110"), "45"),
            (default + "AST,120,U/L\n", "45"),
            (default, None), (default, "nan"), (default, "inf"),
            (default, "unknown"), (default, "18"), (default, "17"), (default, "121"),
            ("", "45"),
        ]
        for rows, age in cases:
            with self.subTest(rows=rows, age=age), tempfile.TemporaryDirectory() as d:
                proc, out = self.run_report(d)
                self.assertEqual(proc.returncode, 0, proc.stderr)
                proc, out = self.run_report(d, rows, age)
                self.assertEqual(proc.returncode, 3, proc.stderr)
                self.assertFalse((out / "result.json").exists())
                self.assertTrue(json.loads((out / "problems.json").read_text())["problems"])
                report = (out / "report.md").read_text()
                self.assertIn("论文卡片", report)
                self.assertIn("边界:", report)
                self.assertNotIn("你的结果", report)
                self.assertNotIn("指数：**", report)

    def test_missing_file_and_recovery_clear_problems(self):
        with tempfile.TemporaryDirectory() as d:
            proc, out = self.run_report(d, source_exists=False)
            self.assertEqual(proc.returncode, 3, proc.stderr)
            self.assertTrue((out / "problems.json").exists())
            proc, out = self.run_report(d)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertFalse((out / "problems.json").exists())
            self.assertTrue((out / "result.json").exists())

    def test_outside_entry_and_observed_range_are_not_clamped(self):
        # Engineering range check; this is NOT another printed personal example.
        with tempfile.TemporaryDirectory() as d:
            proc, out = self.run_report(d, "AST,110,U/L\nALT,100,U/L\nPLT,40,10^9/L\n")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            result = json.loads((out / "result.json").read_text())["outputs"]
            self.assertGreater(result["fib4_index"]["value"], 10)
            report = (out / "report.md").read_text()
            self.assertIn("低于原研究入组下限", report)
            self.assertIn("超出论文报告的观测范围", report)


if __name__ == "__main__":
    unittest.main()
