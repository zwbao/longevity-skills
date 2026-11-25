"""Figure S1 (p. 17B): printed response-column scores, not a clinical validation."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]


def presets():
    spec = importlib.util.spec_from_file_location("sated_presets", ROOT / "scripts/presets.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_figure_s1_printed_item_scores():
    # Verbatim Figure S1 column headings:
    # Rarely/Never (0)   Sometimes (1)   Usually/Always (2)
    p = presets()
    assert p.response_score("Rarely/Never") == 0
    assert p.response_score("Sometimes") == 1
    assert p.response_score("Usually/Always") == 2


def run(tmp_path, values=None, unit="score", targets=None):
    p = presets()
    values = [2] * 5 if values is None else values
    rows = ["marker,value,unit"] + [f"{key},{value},{unit}" for (key, _, _), value in zip(p.ITEMS, values)]
    path = tmp_path / "answers.csv"
    path.write_text("\n".join(rows) + "\n")
    args = [sys.executable, str(ROOT / "scripts/personal_report.py"), "--measurements", str(path), "--out", str(tmp_path / "out")]
    if targets is not None:
        target = tmp_path / "targets.csv"
        target.write_text(targets)
        args += ["--targets", str(target)]
    result = subprocess.run(args, capture_output=True, text=True)
    return result, tmp_path / "out"


def test_manifest_matches_presets():
    manifest = json.loads((ROOT / "skill.json").read_text())
    inputs = [x for x in manifest["inputs"] if x["from"] == "measurements"]
    assert [(x["key"], x["label_zh"], x["unit"]) for x in inputs] == list(presets().ITEMS)
    assert all(x["range"] == [0, 2] for x in inputs)
    assert manifest["validation"]["status"] == "reproduced"


@pytest.mark.parametrize("answer,total", [(0, 0), (2, 10)])
def test_figure_s1_total_endpoints(tmp_path, answer, total):
    # Figure S1 prints item range 0-2 and total range 0-10.
    # These are arithmetic endpoint checks, not a printed filled-out patient case.
    proc, out = run(tmp_path, [answer] * 5)
    assert proc.returncode == 0, proc.stderr
    result = json.loads((out / "result.json").read_text())["outputs"]
    assert result["sated_total_score"]["value"] == total
    for key, _, _ in presets().ITEMS:
        assert result[key]["value"] == answer
    report = (out / "report.md").read_text()
    assert report.index("论文卡片") < report.index("你的回答")
    assert "10.5665/sleep.3298" in report
    assert "边界：" in report and "尚未经过心理测量学验证" in report


@pytest.mark.parametrize("values,unit", [([2]*5, "h"), ([3]*5, "score"), ([1.5]*5, "score"), ([2]*4, "score"), (["nan"]*5, "score"), (["oops"]*5, "score")])
def test_invalid_inputs_exit_three_without_scores(tmp_path, values, unit):
    proc, out = run(tmp_path, values, unit)
    assert proc.returncode == 3, proc.stderr
    assert json.loads((out / "problems.json").read_text())["problems"]
    assert not (out / "result.json").exists()
    assert not (out / "levers.json").exists()
    report = (out / "report.md").read_text()
    assert "论文卡片" in report and "边界：" in report
    assert "SATED 总分：" not in report


def test_target_scenario_and_stale_output_cleanup(tmp_path):
    proc, out = run(tmp_path, [0]*5, targets="marker,value,unit\nsatisfaction_score,2,score\n")
    assert proc.returncode == 0, proc.stderr
    scenario = json.loads((out / "levers.json").read_text())
    assert scenario["targets"]["sated_total_score"] == 2  # S1 printed item increment
    assert scenario["levers"][0]["sated_total_score_delta"] == 2
    proc, out = run(tmp_path, [0]*5, targets="marker,value,unit\nsatisfaction_score,1.5,score\n")
    assert proc.returncode == 3
    assert not (out / "result.json").exists()
    assert not (out / "levers.json").exists()


def test_missing_file_is_input_problem(tmp_path):
    proc = subprocess.run([sys.executable, str(ROOT / "scripts/personal_report.py"), "--measurements", str(tmp_path / "absent.csv"), "--out", str(tmp_path / "out")], capture_output=True, text=True)
    assert proc.returncode == 3, proc.stderr
    assert (tmp_path / "out/problems.json").exists()


def test_chinese_aliases_and_invalid_age(tmp_path):
    path = tmp_path / "chinese.csv"
    path.write_text("marker,value,unit\n" + "\n".join(f"{label},1,score" for _, label, _ in presets().ITEMS))
    args = [sys.executable, str(ROOT / "scripts/personal_report.py"), "--measurements", str(path), "--out", str(tmp_path / "out")]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    result = json.loads((tmp_path / "out/result.json").read_text())["outputs"]
    for key, _, _ in presets().ITEMS:
        assert result[key]["value"] == 1  # Figure S1: Sometimes (1)
    for invalid_age in ("child", "12", "nan"):
        proc = subprocess.run(args + ["--age", invalid_age], capture_output=True, text=True)
        assert proc.returncode == 3, proc.stderr
        assert not (tmp_path / "out/result.json").exists()
