"""Folstein et al. (1975), pp. 190, 196–197: printed maximum-score example.

Appendix maxima: 5, 5, 3, 5, 3; language components 2, 1, 3, 1, 1, 1.
p. 190: "the maximum score is 21." and "Maximum total score is 30."
The second section is printed as "nine" (Appendix: 9).
This checks the printed scoring endpoint, not a reconstructed patient case.
"""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
MAXIMUM = {
    "time_orientation_score": 5, "place_orientation_score": 5,
    "registration_score": 3, "attention_score": 5, "recall_score": 3,
    "naming_score": 2, "repetition_score": 1, "command_score": 3,
    "reading_score": 1, "writing_score": 1, "copying_score": 1,
    "registration_learned": 1,
}


class TestManifest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.manifest = json.loads((ROOT / "skill.json").read_text())

    def run_report(self, values=None, units=None, aliases=False, path=None):
        values = MAXIMUM.copy() if values is None else values
        units = units or {}
        specs = {s["key"]: s for s in self.manifest["inputs"]}
        source = self.base / "scores.csv"
        source.write_text("marker,value,unit\n" + "".join(
            f"{specs[k]['label_zh'] if aliases else k},{v},{units.get(k, specs[k]['unit'])}\n"
            for k, v in values.items()), encoding="utf-8")
        out = self.base / "out"
        proc = subprocess.run([sys.executable, str(ROOT / "scripts/personal_report.py"),
                               "--measurements", str(path or source), "--out", str(out)],
                              capture_output=True, text=True)
        return proc, out

    def test_printed_maximum_scores(self):
        proc, out = self.run_report()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        result = json.loads((out / "result.json").read_text())["outputs"]
        self.assertEqual(result["part_one_score"]["value"], 21)
        self.assertEqual(result["part_two_score"]["value"], 9)
        self.assertEqual(result["mmse_total_score"]["value"], 30)
        report = (out / "report.md").read_text()
        self.assertLess(report.index("## 论文卡片"), report.index("## 你的结果"))
        self.assertIn("边界:", report)
        self.assertIn("10.1016/0022-3956(75)90026-6", report)

    def test_manifest_matches_presets(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        import presets
        specs = {s["key"]: s for s in self.manifest["inputs"]}
        self.assertEqual(set(specs), set(MAXIMUM))
        for key, maximum in MAXIMUM.items():
            self.assertEqual(specs[key]["range"], [0, maximum])
            self.assertEqual(specs[key]["unit"], presets.INPUT_UNITS[key])
            self.assertEqual(tuple(specs[key]["range"]), presets.INPUT_RANGES[key])

    def test_aliases(self):
        proc, out = self.run_report(aliases=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads((out / "result.json").read_text())["outputs"]["mmse_total_score"]["value"], 30)

    def test_invalid_inputs_clear_old_result(self):
        proc, out = self.run_report()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        cases = []
        cases.append((MAXIMUM.copy(), {"attention_score": "mg/L"}, "unit"))
        for key, value, kind in [
            ("attention_score", 6, "range"), ("registration_score", -1, "range"),
            ("recall_score", 2.5, "integer"), ("registration_learned", 0, "protocol"),
            ("registration_learned", 0.5, "integer"), ("naming_score", "nan", "parse"),
        ]:
            data = dict(MAXIMUM, **{key: value})
            cases.append((data, {}, kind))
        for key in MAXIMUM:
            data = MAXIMUM.copy()
            del data[key]
            cases.append((data, {}, "missing"))
        for data, units, kind in cases:
            with self.subTest(data=data, units=units):
                proc, out = self.run_report(data, units)
                self.assertEqual(proc.returncode, 3, proc.stderr)
                self.assertFalse((out / "result.json").exists())
                problems = json.loads((out / "problems.json").read_text())["problems"]
                self.assertIn(kind, {p["kind"] for p in problems})
                report = (out / "report.md").read_text()
                self.assertIn("## 论文卡片", report)
                self.assertIn("边界:", report)
                self.assertNotIn("## 你的结果", report)
        proc, out = self.run_report()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertFalse((out / "problems.json").exists())

    def test_unreadable_file(self):
        proc, out = self.run_report(path=self.base / "absent.csv")
        self.assertEqual(proc.returncode, 3, proc.stderr)
        self.assertTrue((out / "problems.json").exists())


if __name__ == "__main__":
    unittest.main()
