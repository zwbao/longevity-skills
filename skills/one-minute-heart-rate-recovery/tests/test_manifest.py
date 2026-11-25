"""Engineering checks, NOT a reproduction of a printed patient example.

Table 1, p. 1353 prints NORMAL (REDUCTION OF >12 bpm) and ABNORMAL
(REDUCTION OF ≤12 bpm). The 150/138 pair below is synthetic, chosen to
exercise that printed boundary; the paper does not print this patient.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import presets

MANIFEST = json.loads((ROOT / "skill.json").read_text())


def run(tmp_path, rows=None, age="57", protocol="cole-1999", out=None):
    out = out or tmp_path / "out"
    args = [sys.executable, str(ROOT / "scripts/personal_report.py"), "--out", str(out)]
    if rows is not None:
        path = tmp_path / "measurements.csv"
        path.write_text("marker,value,unit\n" + rows, encoding="utf-8")
        args += ["--measurements", str(path)]
    if age is not None:
        args += ["--age", age]
    if protocol is not None:
        args += ["--protocol", protocol]
    proc = subprocess.run(args, capture_output=True, text=True)
    return proc, out


VALID = "峰值心率,150,bpm\n恢复1分钟心率,138,次/分\n"


def test_manifest_and_printed_boundary():
    specs = {s["key"]: s for s in MANIFEST["inputs"]}
    assert set(presets.MEASUREMENT_KEYS) == {s["key"] for s in MANIFEST["inputs"] if s["from"] == "measurements"}
    assert all(specs[k]["unit"] == "/min" for k in presets.MEASUREMENT_KEYS)
    assert presets.ABNORMAL_CUTOFF_BPM == 12
    assert presets.classify(12) == "abnormal"
    assert MANIFEST["validation"]["status"] == "draft"


def test_synthetic_boundary_report(tmp_path):
    proc, out = run(tmp_path, VALID)
    assert proc.returncode == 0, proc.stderr
    outputs = json.loads((out / "result.json").read_text())["outputs"]
    assert outputs["hrr_1min_bpm"]["value"] == 12
    assert outputs["hrr_category"]["value"] == "abnormal"
    report = (out / "report.md").read_text()
    assert report.index("## 论文卡片") < report.index("## 你的结果")
    assert "暂定" in report and "独立验证" in report
    assert report.rstrip().endswith(presets.BOUNDARY)
    assert not (out / "problems.json").exists()


@pytest.mark.parametrize("rows,age,protocol", [
    (None, "57", "cole-1999"),
    ("peak_hr_bpm,150,/min\n", "57", "cole-1999"),
    (VALID.replace("bpm", "Hz"), "57", "cole-1999"),
    (VALID.replace("150", "1500"), "57", "cole-1999"),
    (VALID.replace("150", "nan"), "57", "cole-1999"),
    (VALID + "peak_hr_bpm,151,/min\n", "57", "cole-1999"),
    (VALID, None, "cole-1999"),
    (VALID, "child", "cole-1999"),
    (VALID, "17", "cole-1999"),
    (VALID, "nan", "cole-1999"),
    (VALID, "57", None),
    (VALID, "57", "seated"),
])
def test_bad_or_missing_input_returns_problems(tmp_path, rows, age, protocol):
    proc, out = run(tmp_path, rows, age, protocol)
    assert proc.returncode == 3, proc.stderr
    assert json.loads((out / "problems.json").read_text())["problems"]
    outputs = json.loads((out / "result.json").read_text())["outputs"]
    assert all(item["value"] is None for item in outputs.values())
    report = (out / "report.md").read_text()
    assert "## 论文卡片" in report
    assert "## 你的结果" not in report
    assert report.rstrip().endswith(presets.BOUNDARY)


def test_units_equivalent_and_no_stale_results(tmp_path):
    proc, out = run(tmp_path, VALID)
    baseline = json.loads((out / "result.json").read_text())
    canonical = "peak_hr_bpm,150,/min\nrecovery_hr_1min_bpm,138,/min\n"
    proc, out = run(tmp_path, canonical)
    assert proc.returncode == 0
    assert json.loads((out / "result.json").read_text()) == baseline
    proc, out = run(tmp_path, canonical, protocol="unknown")
    assert proc.returncode == 3
    assert all(x["value"] is None for x in json.loads((out / "result.json").read_text())["outputs"].values())
    proc, out = run(tmp_path, canonical)
    assert proc.returncode == 0
    assert not (out / "problems.json").exists()


def test_both_sides_of_boundary_and_negative_recovery(tmp_path):
    # Synthetic software cases, not published patient examples.
    for recovery, category in [(137, "normal"), (139, "abnormal"), (160, "abnormal")]:
        proc, out = run(tmp_path, f"peak_hr_bpm,150,/min\nrecovery_hr_1min_bpm,{recovery},/min\n")
        assert proc.returncode == 0
        outputs = json.loads((out / "result.json").read_text())["outputs"]
        assert outputs["hrr_category"]["value"] == category
        if recovery == 160:
            assert outputs["hrr_1min_bpm"]["value"] < 0
            assert "未下降" in (out / "report.md").read_text()
