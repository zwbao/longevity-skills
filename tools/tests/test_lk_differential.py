"""Engine vs the method's own script, for every tier-A method: the same inputs give the same result.

The engine checks and normalises declared measurements before the script runs (one row per input, named by its
key, in the input's unit). Fed rows that are already in that form, the script called directly must produce the
same result.json, problems or report as the script called through the engine.
"""
from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from tools.lk.library import Library  # noqa: E402
from tools.lk.run import run  # noqa: E402

LIB = Library(REPO)


def synthetic(manifest):
    rows = []
    for i in manifest.get("inputs") or []:
        if i.get("from", "measurements") != "measurements":
            continue
        lo, hi = i.get("range") or [0, 1]
        unit = i.get("unit") if i.get("unit") not in (None, "1") else ""
        rows.append({"item": i["key"], "value": repr(float(f"{lo + (hi - lo) * 0.3:.6g}")), "unit": unit})
    answers = {i["key"]: "no" for i in manifest.get("inputs") or [] if i.get("from") == "argument" and "是否" in i.get("label_zh", "")}
    return rows, answers


def direct(name, manifest, rows, answers):
    e = manifest["entry"]
    tmp = Path(tempfile.mkdtemp())
    out = tmp / "out"
    cmd = [sys.executable, str(LIB.skill_dir(name) / e["script"])]
    if rows and e.get("measurements_flag"):
        f = tmp / "m.csv"
        with f.open("w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            hdr = e.get("measurements_header") or ["item", "value", "unit"]
            w.writerow(hdr[:3] if len(hdr) >= 3 else [*hdr, "unit"])
            for r in rows:
                w.writerow([r["item"], r["value"], r["unit"]])
        cmd += [e["measurements_flag"], str(f)]
    if e.get("age_flag"):
        cmd += [e["age_flag"], "55"]
    if e.get("sex_flag"):
        cmd += [e["sex_flag"], "female"]
    for k, v in answers.items():
        spec = next(i for i in manifest["inputs"] if i["key"] == k)
        cmd += [spec.get("flag") or "--" + k.replace("_", "-"), v]
    cmd += [e.get("out_flag", "--out"), str(out)]
    done = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    read = lambda n: json.loads((out / n).read_text(encoding="utf-8")) if (out / n).exists() else None  # noqa: E731
    report = (out / "report.md").read_text(encoding="utf-8") if (out / "report.md").exists() else None
    return done.returncode, read("result.json"), read("problems.json"), report


class DifferentialTest(unittest.TestCase):
    def test_every_tier_a_method(self):
        names = sorted(s["name"] for s in LIB.skills.values() if s["tier"] == "A")
        self.assertEqual(len(names), sum(1 for s in LIB.skills.values() if s["tier"] == "A"))
        for name in names:
            with self.subTest(name):
                m = LIB.manifest(name)
                rows, answers = synthetic(m)
                eng = run(LIB, name, {"age": 55, "sex": "female", "measurements": rows, "arguments": answers}, allow_draft=True)
                rc, result, problems, report = direct(name, m, rows, answers)
                if problems and problems.get("problems"):
                    self.assertEqual(eng["status"], "input_problem")
                    if eng.get("checked_by") != "engine":
                        self.assertEqual(eng["problems"], problems["problems"])
                elif not m["entry"].get("result_json") and report is not None and rc in (0, 3):
                    self.assertEqual(eng.get("report_md"), report)
                elif result is not None and rc == 0:
                    self.assertIn(eng["status"], ("ok", "not_computed"))
                    self.assertEqual(eng["outputs"], json.loads(json.dumps(result["outputs"]).replace("NaN", "null")))
                else:
                    self.assertIn(eng["status"], ("error", "missing_dependency"))


if __name__ == "__main__":
    unittest.main()
