"""Expected RRs are transcribed from Supplementary Tables 13–16, with gamma.

These tests validate the published table readout, not a refit of MR-BRT.
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
spec = importlib.util.spec_from_file_location("dietary_report", ROOT / "scripts/personal_report.py")
report = importlib.util.module_from_spec(spec)
spec.loader.exec_module(report)


def test_printed_processed_meat():
    # Table 13: 50 1.3 (1.12, 1.52); 50 1.26 (1.08, 1.47)
    # Table 14: 50 1.15 (0.97, 1.36)
    assert report.lookup("meat_t2d", 50) == (1.3, 1.12, 1.52)
    assert report.lookup("meat_crc", 50) == (1.26, 1.08, 1.47)
    assert report.lookup("meat_ihd", 50) == (1.15, 0.97, 1.36)

def test_printed_ssb():
    # Table 15, with heterogeneity: 250 1.2 (1.07, 1.34),
    # 250 1.07 (1.03, 1.12); 750 1.29 (1.1, 1.50).
    assert report.lookup("ssb_t2d", 250) == (1.2, 1.07, 1.34)
    assert report.lookup("ssb_ihd", 250) == (1.07, 1.03, 1.12)
    assert report.lookup("ssb_ihd", 750) == (1.29, 1.1, 1.50)

def test_printed_tfa():
    # Table 16: 1 1.11 (1, 1.24); 4 1.3 (1, 1.68).
    assert report.lookup("tfa_ihd", 1) == (1.11, 1, 1.24)
    assert report.lookup("tfa_ihd", 4) == (1.3, 1, 1.68)


class ManifestTests(unittest.TestCase):
    def run_cli(self, directory, rows, targets=None):
        d = Path(directory)
        (d / "input.csv").write_text("marker,value,unit\n" + rows, encoding="utf-8")
        cmd = [sys.executable, str(ROOT / "scripts/personal_report.py"),
               "--measurements", str(d / "input.csv"), "--age", "50", "--out", str(d / "out")]
        if targets is not None:
            (d / "targets.csv").write_text("marker,value,unit\n" + targets, encoding="utf-8")
            cmd += ["--targets", str(d / "targets.csv")]
        return subprocess.run(cmd, capture_output=True, text=True)

    def test_manifest_and_cli(self):
        manifest = json.loads((ROOT / "skill.json").read_text())
        measurement_specs = {s["key"]: s for s in manifest["inputs"] if s["from"] == "measurements"}
        self.assertEqual({k: v["unit"] for k, v in measurement_specs.items()}, report.INPUT_UNITS)
        self.assertEqual(len(report.TABLE_ROWS), 39)
        with tempfile.TemporaryDirectory() as d:
            p = self.run_cli(d, "加工肉,50,g/d\n含糖饮料,250,g/d\n反式脂肪供能占比,0.01,1\n")
            self.assertEqual(p.returncode, 0, p.stderr)
            out = Path(d) / "out"
            values = json.loads((out / "result.json").read_text())["outputs"]
            self.assertEqual(values["meat_t2d_rr"]["value"], 1.3)
            self.assertEqual(values["ssb_t2d_rr"]["value"], 1.2)
            self.assertEqual(values["tfa_ihd_rr"]["value"], 1.11)
            text = (out / "report.md").read_text()
            self.assertLess(text.index("论文卡片"), text.index("你的摄入量"))
            self.assertIn(report.BOUNDARY, text)
            self.assertTrue((out / "levers.json").exists())

    def test_bad_inputs_remove_stale_results(self):
        for rows in ["加工肉,50,mg/dL\n", "加工肉,401,g/d\n", "加工肉,60,g/d\n",
                     "", "加工肉,nan,g/d\n", "反式脂肪供能占比,1,g/d\n"]:
            with self.subTest(rows=rows), tempfile.TemporaryDirectory() as d:
                self.assertEqual(self.run_cli(d, "加工肉,50,g/d\n").returncode, 0)
                p = self.run_cli(d, rows)
                self.assertEqual(p.returncode, 3, p.stderr)
                out = Path(d) / "out"
                self.assertTrue((out / "problems.json").exists())
                self.assertFalse((out / "result.json").exists())
                self.assertFalse((out / "levers.json").exists())
                text = (out / "report.md").read_text()
                self.assertIn("论文卡片", text)
                self.assertNotIn("1.30", text)

    def test_missing_table_cell_is_not_filled(self):
        self.assertIsNone(report.lookup("meat_ihd", 150))
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(self.run_cli(d, "加工肉,150,g/d\n").returncode, 0)
            values = json.loads((Path(d) / "out/result.json").read_text())["outputs"]
            self.assertIsNone(values["meat_ihd_rr"]["value"])
            # Table 13: 150 1.56 (1.22, 2.03).
            self.assertEqual(values["meat_t2d_rr"]["value"], 1.56)

    def test_targets_use_printed_rows(self):
        with tempfile.TemporaryDirectory() as d:
            p = self.run_cli(d, "加工肉,100,g/d\n", "加工肉,50,g/d\n")
            self.assertEqual(p.returncode, 0, p.stderr)
            lever = json.loads((Path(d) / "out/levers.json").read_text())
            # Table 13 has 100 -> 1.5 and 50 -> 1.3.
            self.assertEqual(lever["current"]["meat_t2d_rr"], 1.5)
            self.assertEqual(lever["targets"]["outputs"]["meat_t2d_rr"], 1.3)
            self.assertAlmostEqual(lever["levers"][0]["delta"]["meat_t2d_rr"], 1.3 - 1.5)
            self.assertIsNone(lever["sensitivity"][0]["derivative"])
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(self.run_cli(d, "加工肉,50,g/d\n", "含糖饮料,250,g/d\n").returncode, 3)

    def test_invalid_age_and_reference(self):
        for age in (None, "unknown", "nan", "17"):
            with self.subTest(age=age), tempfile.TemporaryDirectory() as d:
                d = Path(d)
                (d / "input.csv").write_text("marker,value,unit\n加工肉,50,g/d\n")
                cmd = [sys.executable, str(ROOT / "scripts/personal_report.py"),
                       "--measurements", str(d / "input.csv"), "--out", str(d / "out")]
                if age is not None:
                    cmd += ["--age", age]
                p = subprocess.run(cmd, capture_output=True, text=True)
                self.assertEqual(p.returncode, 3, p.stderr)
                self.assertTrue((d / "out/problems.json").exists())
        self.assertEqual(report.lookup("meat_t2d", 0), (1, None, None))
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(self.run_cli(d, "加工肉,0,g/d\n").returncode, 0)


if __name__ == "__main__":
    unittest.main()
