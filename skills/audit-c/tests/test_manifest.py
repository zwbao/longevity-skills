"""Paper-derived per-item expectations, written before the implementation.

Bush et al. (1998), Patients and methods / Measures, question 2:
3 to 4 drinks (1 point); 5 to 6 drinks (2 points)
Response codes below are local zero-based option indices, not published scores.
"""
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def test_printed_quantity_per_term_scores():
    from personal_report import item_points
    # Printed inputs: typical drinking day of 3–4 drinks and 5–6 drinks.
    assert item_points("q2", 2) == 1
    assert item_points("q2", 3) == 2


def test_all_printed_response_scores():
    from personal_report import item_points
    # Measures: options in their printed order, including the duplicate scores.
    for question, expected in [
        ("q1", [0, 1, 2, 3, 4, 4]),
        ("q2", [0, 0, 1, 2, 3, 4]),
        ("q3", [0, 1, 2, 3, 4]),
    ]:
        for code, points in enumerate(expected):
            assert item_points(question, code) == points


def test_manifest_matches_presets():
    from presets import MEASUREMENTS
    manifest = json.loads((ROOT / "skill.json").read_text())
    assert {x["key"]: (x["unit"], tuple(x["range"])) for x in manifest["inputs"]
            if x["from"] == "measurements"} == MEASUREMENTS
    assert manifest["validation"]["status"] == "reproduced"
    assert manifest["inputs_status"] == "verified"


# Synthetic integration input; no claim that this is a printed participant.
VALID = [("q1_response_code", "1", "1"),
         ("q2_response_code", "2", "1"),
         ("q3_response_code", "1", "1")]


def run_report(tmp_path, rows=VALID, extra=()):
    path = tmp_path / "answers.csv"
    path.write_text("marker,value,unit\n" + "\n".join(",".join(r) for r in rows) + "\n")
    out = tmp_path / "out"
    run = subprocess.run([sys.executable, str(ROOT / "scripts/personal_report.py"),
                          "--measurements", str(path), "--out", str(out), *extra],
                         capture_output=True, text=True)
    return run, out


def test_result_and_report(tmp_path):
    run, out = run_report(tmp_path, extra=("--sex", "male", "--age", "67"))
    assert run.returncode == 0, run.stderr
    values = json.loads((out / "result.json").read_text())["outputs"]
    assert values["audit_c_total_score"]["value"] == 3
    assert values["screen_ge3"]["value"] == "positive"
    assert values["screen_ge4"]["value"] == "negative"
    report = (out / "report.md").read_text()
    assert report.index("## 论文卡片") < report.index("## 你的结果")
    assert "边界:" in report and "诊断" in report
    assert "男性" in report and "6 杯" in report


@pytest.mark.parametrize("score,ge3,ge4", [
    (0, "negative", "negative"), (2, "negative", "negative"),
    (3, "positive", "negative"), (4, "positive", "positive"),
    (12, "positive", "positive"),
])
def test_inclusive_published_thresholds(score, ge3, ge4):
    from personal_report import screens
    assert screens(score) == {"screen_ge3": ge3, "screen_ge4": ge4}


@pytest.mark.parametrize("value,unit", [("6", "1"), ("-1", "1"),
    ("1.5", "1"), ("2", "mg/dL"), ("nan", "1"), ("abc", "1")])
def test_invalid_input(tmp_path, value, unit):
    run, out = run_report(tmp_path, [("q1_response_code", value, unit), *VALID[1:]])
    assert run.returncode == 3, run.stderr
    assert (out / "problems.json").exists()
    assert not (out / "result.json").exists()
    report = (out / "report.md").read_text()
    assert "## 论文卡片" in report and "边界:" in report
    assert "## 你的结果" not in report


def test_missing_and_stale_outputs(tmp_path):
    assert run_report(tmp_path)[0].returncode == 0
    run, out = run_report(tmp_path, VALID[:-1])
    assert run.returncode == 3 and not (out / "result.json").exists()
    problems = json.loads((out / "problems.json").read_text())["problems"]
    assert any(p["key"] == "q3_response_code" and p["kind"] == "missing" for p in problems)
    assert run_report(tmp_path)[0].returncode == 0
    assert not (out / "problems.json").exists()


def test_inconsistent_abstinence(tmp_path):
    run, out = run_report(tmp_path, [("q1_response_code", "0", "1"), *VALID[1:]])
    assert run.returncode == 3
    assert not (out / "result.json").exists()


def test_aliases_and_female_applicability(tmp_path):
    rows = [("饮酒频率选项", "1", "1"), ("AUDIT-C Q2 response", "2", "1"),
            ("单次至少六杯频率选项", "1", "1")]
    run, out = run_report(tmp_path, rows, ("--sex", "female"))
    assert run.returncode == 0, run.stderr
    report = (out / "report.md").read_text()
    assert "本研究未验证你所属性别人群的筛查性能" in report
    values = json.loads((out / "result.json").read_text())["outputs"]
    assert values["screen_ge4"]["value"] == "negative"


@pytest.mark.parametrize("extra", [("--age", "nan"), ("--age", "-1"), ("--sex", "typo")])
def test_invalid_context(tmp_path, extra):
    run, out = run_report(tmp_path, extra=extra)
    assert run.returncode == 3
    assert (out / "problems.json").exists()
