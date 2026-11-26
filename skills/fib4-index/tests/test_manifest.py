"""Draft validation: the paper prints no individual input/output pair.

Table 1 gives the formula; Table 5 prints <1.30, 1.30–2.67, >2.67.
Synthetic fixtures below test software behavior, not a published patient.
No cohort means/medians are substituted for an individual's measurements.
"""
import json
import math
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def test_table5_threshold_contract():
    from personal_report import classify
    assert classify(1.30) == "indeterminate"
    assert classify(2.67) == "indeterminate"
    assert classify(math.nextafter(1.30, -math.inf)) == "low"
    assert classify(math.nextafter(2.67, math.inf)) == "high"


def test_manifest_matches_presets():
    from presets import INPUTS
    manifest = json.loads((ROOT / "skill.json").read_text())
    assert {s["key"]: (s["unit"], tuple(s["range"])) for s in manifest["inputs"]} == INPUTS
    assert manifest["validation"]["status"] == "draft"
    assert manifest["inputs_status"] == "draft"


VALID = "marker,value,unit\nAST,50,U/L\nALT,100,U/L\nPLT,200,10^9/L\n"


def run_report(tmp_path, content=VALID, age="50", targets=None):
    path = tmp_path / "labs.csv"
    path.write_text(content)
    out = tmp_path / "out"
    args = [sys.executable, str(ROOT / "scripts/personal_report.py"),
            "--measurements", str(path), "--out", str(out)]
    if age is not None:
        args += ["--age", age]
    if targets is not None:
        target = tmp_path / "targets.csv"
        target.write_text(targets)
        args += ["--targets", str(target)]
    return subprocess.run(args, capture_output=True, text=True), out


def test_normal_result_uses_table1_formula(tmp_path):
    run, out = run_report(tmp_path)
    assert run.returncode == 0, run.stderr
    outputs = json.loads((out / "result.json").read_text())["outputs"]
    # Algebraic check of Table 1 on synthetic inputs; not printed-example validation.
    assert outputs["fib4_index"]["value"] == pytest.approx(50 * 50 / (200 * math.sqrt(100)))
    assert outputs["fib4_category"]["value"] == "low"
    report = (out / "report.md").read_text()
    assert report.index("## 论文卡片") < report.index("## 你的结果")
    assert "边界:" in report and "仍在验证" in report
    assert "概率" in report and "不能据此开始或停止用药" in report


@pytest.mark.parametrize("old,new", [
    ("50,U/L", "50,mg/dL"), ("200,10^9/L", "0,10^9/L"),
    ("100,U/L", "0,U/L"), ("50,U/L", "nan,U/L"),
    ("50,U/L", "50,"), ("200,10^9/L", "200000,10^9/L"),
    ("PLT,200,10^9/L\n", ""),
])
def test_bad_measurements_exit_three(tmp_path, old, new):
    run, out = run_report(tmp_path, VALID.replace(old, new))
    assert run.returncode == 3, run.stderr
    assert (out / "problems.json").exists()
    assert not (out / "result.json").exists()
    assert not (out / "levers.json").exists()
    report = (out / "report.md").read_text()
    assert "## 论文卡片" in report and "边界:" in report
    assert "## 你的结果" not in report


@pytest.mark.parametrize("age", [None, "unknown", "nan", "17", "130"])
def test_missing_or_invalid_age(tmp_path, age):
    run, out = run_report(tmp_path, age=age)
    assert run.returncode == 3
    assert (out / "problems.json").exists()


def test_units_aliases_and_stale_files(tmp_path):
    _, out = run_report(tmp_path)
    baseline = json.loads((out / "result.json").read_text())
    alternative = "项目,结果,单位\n谷草转氨酶,0.8333333333333333,ukat/L\n谷丙转氨酶,100,IU/L\n血小板计数,200000,/uL\n"
    run, out = run_report(tmp_path, alternative)
    assert run.returncode == 0, run.stderr
    result = json.loads((out / "result.json").read_text())
    assert result["outputs"]["fib4_index"]["value"] == pytest.approx(baseline["outputs"]["fib4_index"]["value"])
    run, out = run_report(tmp_path, age=None)
    assert run.returncode == 3 and not (out / "result.json").exists()
    run, out = run_report(tmp_path)
    assert run.returncode == 0 and not (out / "problems.json").exists()


def test_targets_are_formula_scenarios(tmp_path):
    run, out = run_report(tmp_path, targets="marker,value,unit\nAST,25,U/L\n")
    assert run.returncode == 0, run.stderr
    levers = json.loads((out / "levers.json").read_text())
    assert levers["targets"]["fib4_index"] * 2 == pytest.approx(levers["current"]["fib4_index"])
    assert levers["levers"][0]["fib4_index"] == levers["targets"]["fib4_index"]
    slopes = {x["key"]: x["score_per_unit"] for x in levers["sensitivity"]}
    assert slopes["ast_u_l"] > 0 and slopes["alt_u_l"] < 0 and slopes["platelets_10e9_l"] < 0


@pytest.mark.parametrize("target", [
    "ALT,0,U/L", "AST,20,mg/dL", "age,40,a", "unknown,2,1", "",
])
def test_invalid_targets_do_not_silently_disappear(tmp_path, target):
    run, out = run_report(tmp_path, targets="marker,value,unit\n" + target + "\n")
    assert run.returncode == 3, run.stderr
    assert (out / "problems.json").exists() and not (out / "result.json").exists()


def test_missing_file_is_input_problem(tmp_path):
    out = tmp_path / "out"
    run = subprocess.run([sys.executable, str(ROOT / "scripts/personal_report.py"),
                          "--measurements", str(tmp_path / "absent.csv"), "--age", "50", "--out", str(out)])
    assert run.returncode == 3 and (out / "problems.json").exists()
