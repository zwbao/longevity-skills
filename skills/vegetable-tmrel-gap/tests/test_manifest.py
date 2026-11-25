"""Contract checks, not an independent reproduction of a printed personal example.

Results, Minimum risk level of vegetable intake: "We estimated a TMREL of
306–372 g per day, corresponding to approximately 4–5 servings per day."
Table 1 prints the comparator 0 g per day and the endpoints 306–372 g daily.
No printed personal gap example exists: validation remains draft. Nonzero
gap expectations below are arithmetic identities, not claimed paper outputs.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import presets


def run(tmp_path, value=None, unit="g/d", marker="蔬菜摄入量", target=None):
    out = tmp_path / "out"
    args = [sys.executable, str(ROOT / "scripts/personal_report.py"), "--out", str(out)]
    if value is not None:
        src = tmp_path / "intake.csv"
        src.write_text(f"marker,value,unit\n{marker},{value},{unit}\n", encoding="utf-8")
        args += ["--intake", str(src)]
    if target is not None:
        src = tmp_path / "targets.csv"
        src.write_text(f"marker,value,unit\n蔬菜摄入量,{target},g/d\n", encoding="utf-8")
        args += ["--targets", str(src)]
    return subprocess.run(args, capture_output=True, text=True), out


def test_printed_reference_endpoints_and_zero_comparator(tmp_path):
    # Only a transcription/arithmetic check; NOT independent model validation.
    assert presets.TMREL_LOWER_G_D == 306
    assert presets.TMREL_UPPER_G_D == 372
    proc, out = run(tmp_path, 0)
    assert proc.returncode == 0, proc.stderr
    result = json.loads((out / "result.json").read_text())["outputs"]
    assert result["lower_difference_g_d"]["value"] == 306
    assert result["upper_difference_g_d"]["value"] == 372


def test_manifest_matches_presets():
    manifest = json.loads((ROOT / "skill.json").read_text())
    spec = manifest["inputs"][0]
    assert (spec["key"], spec["unit"]) == (presets.INTAKE_KEY, presets.UNIT)
    assert spec["range"] == list(presets.INPUT_RANGE)
    assert manifest["validation"]["status"] == "draft"
    assert manifest["inputs_status"] == "draft"
    assert manifest["entry"]["targets_flag"] == "--targets"


@pytest.mark.parametrize("value,status", [(100, "below"), (306, "within"), (372, "within"), (400, "above")])
def test_gap_and_target_arithmetic(tmp_path, value, status):
    proc, out = run(tmp_path, value, target=306)
    assert proc.returncode == 0, proc.stderr
    result = json.loads((out / "result.json").read_text())["outputs"]
    assert result["lower_difference_g_d"]["value"] + value == 306
    assert result["upper_difference_g_d"]["value"] + value == 372
    assert result["position"]["value"] == status
    assert result["shortfall_g_d"]["value"] == max(0, 306 - value)
    lever = json.loads((out / "levers.json").read_text())
    assert lever["schema"] == "longevity-levers/1"
    assert lever["targets"]["values"][presets.INTAKE_KEY] == 306
    assert lever["targets"]["shortfall_g_d"] == 0
    assert lever["levers"][0]["lower_difference_g_d_delta"] == value - 306
    text = (out / "report.md").read_text()
    assert text.index("## 论文卡片") < text.index("## 你的摄入记录")
    assert "10.1038/s41591-022-01970-5" in text and presets.BOUNDARY in text
    assert "风险降低" not in text
    assert presets.POPULATION in text and "4,609,296" in text and "34个国家" in text


@pytest.mark.parametrize("value,unit", [(100,"kg"), (3001,"g/d"), (-1,"g/d"), ("NaN","g/d"), (100,""), (None,"g/d")])
def test_bad_input_exits_three_without_results(tmp_path, value, unit):
    proc, out = run(tmp_path, value, unit)
    assert proc.returncode == 3, proc.stderr
    assert (out / "problems.json").exists()
    assert not (out / "result.json").exists()
    assert not (out / "levers.json").exists()
    text = (out / "report.md").read_text()
    assert "## 论文卡片" in text and presets.BOUNDARY in text
    assert "## 你的摄入记录" not in text


def test_invalid_target_removes_stale_results_and_recovery(tmp_path):
    proc, out = run(tmp_path, 100, target=306)
    assert proc.returncode == 0
    proc, out = run(tmp_path, 100, target=-1)
    assert proc.returncode == 3
    assert not (out / "result.json").exists() and not (out / "levers.json").exists()
    proc, out = run(tmp_path, 100, marker="vegetable consumption")
    assert proc.returncode == 0
    assert not (out / "problems.json").exists()


def test_missing_file_exits_three(tmp_path):
    proc = subprocess.run([sys.executable, str(ROOT / "scripts/personal_report.py"),
        "--intake", str(tmp_path / "missing.csv"), "--out", str(tmp_path / "out")])
    assert proc.returncode == 3
    assert (tmp_path / "out/problems.json").exists()
