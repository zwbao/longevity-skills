"""Rule checks written before implementation; not a printed patient example.

Chung et al. 2008, p. 821, Appendix 2:
"High risk of OSA: answering yes to three or more items"
Appendix 1 applies the analogous cutoff at two affirmative answers.
The paper prints no individual input/total pair; validation remains draft.
"""

import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def test_appendix_risk_rules():
    from personal_report import classify

    # Categories come from Appendices 1 and 2, not from running the script.
    for count in range(5):
        assert classify(count, "stop") == ("high" if count >= 2 else "low")
    for count in range(9):
        assert classify(count, "stop_bang") == ("high" if count >= 3 else "low")


def test_manifest_matches_presets():
    from presets import MEASUREMENTS

    manifest = json.loads((ROOT / "skill.json").read_text())
    assert {i["key"]: (i["unit"], tuple(i["range"])) for i in manifest["inputs"]
            if i["from"] == "measurements"} == MEASUREMENTS
    assert manifest["validation"]["status"] == "draft"
    assert manifest["inputs_status"] == "draft"


# Synthetic plumbing fixture: two STOP affirmatives, all three BANG numeric
# inputs exactly at the printed strict cutoffs, female. Not a published case.
VALID = [
    ("snoring_binary", "1", "1"),
    ("tiredness_binary", "0", "1"),
    ("observed_apnea_binary", "0", "1"),
    ("hypertension_binary", "1", "1"),
    ("bmi_kg_m2", "35", "kg/m^2"),
    ("neck_circumference_cm", "40", "cm"),
]


def run_report(tmp_path, rows=VALID, profile=("--age", "50", "--sex", "female")):
    csv_path = tmp_path / "measurements.csv"
    csv_path.write_text("marker,value,unit\n" + "\n".join(",".join(row) for row in rows) + "\n")
    out = tmp_path / "out"
    process = subprocess.run([
        sys.executable, str(ROOT / "scripts/personal_report.py"),
        "--measurements", str(csv_path), "--out", str(out), *profile,
    ], text=True, capture_output=True)
    return process, out


def results(out):
    return {k: v["value"] for k, v in json.loads((out / "result.json").read_text())["outputs"].items()}


def test_result_and_report_at_strict_cutoffs(tmp_path):
    process, out = run_report(tmp_path)
    assert process.returncode == 0, process.stderr
    data = results(out)
    assert data["stop_score"] == data["stop_bang_score"] == 2
    assert data["stop_category"] == "high"
    assert data["stop_bang_category"] == "low"
    assert all(data[k] == 0 for k in ("bmi_score", "age_score", "neck_score", "male_score"))
    report = (out / "report.md").read_text()
    assert report.index("## 论文卡片") < report.index("## 你的结果")
    assert "边界:" in report and "不能排除" in report and "仍在验证" in report
    assert not (out / "problems.json").exists()


@pytest.mark.parametrize("key,value,unit", [
    ("bmi_kg_m2", "35", "kg"),
    ("neck_circumference_cm", "400", "cm"),
    ("snoring_binary", "0.5", "1"),
    ("tiredness_binary", "2", "1"),
    ("observed_apnea_binary", "不知道", "1"),
    ("bmi_kg_m2", "nan", "kg/m^2"),
])
def test_bad_input_exits_three(tmp_path, key, value, unit):
    rows = [(k, value, unit) if k == key else (k, v, u) for k, v, u in VALID]
    process, out = run_report(tmp_path, rows)
    assert process.returncode == 3, process.stderr
    assert (out / "problems.json").exists()
    assert not (out / "result.json").exists()
    report = (out / "report.md").read_text()
    assert "## 论文卡片" in report and "边界:" in report
    assert "## 你的结果" not in report


@pytest.mark.parametrize("index", range(len(VALID)))
def test_missing_measurement_exits_three(tmp_path, index):
    process, out = run_report(tmp_path, VALID[:index] + VALID[index + 1:])
    assert process.returncode == 3
    problems = json.loads((out / "problems.json").read_text())["problems"]
    assert any(p["key"] == VALID[index][0] and p["kind"] == "missing" for p in problems)


@pytest.mark.parametrize("profile", [(), ("--age", "50"), ("--sex", "male"),
    ("--age", "17", "--sex", "male"), ("--age", "unknown", "--sex", "male"),
    ("--age", "50", "--sex", "unknown"), ("--age", "inf", "--sex", "male")])
def test_missing_or_invalid_profile_exits_three(tmp_path, profile):
    process, out = run_report(tmp_path, profile=profile)
    assert process.returncode == 3
    assert (out / "problems.json").exists() and not (out / "result.json").exists()


def test_aliases_and_exact_unit_conversion(tmp_path):
    rows = [("Snoring", "1", "1"), ("白天疲倦", "0", "1"),
            ("Observed apnea", "0", "1"), ("高血压", "1", "1"),
            ("BMI", "35", "kg/m^2"), ("颈围", "400", "mm")]
    process, out = run_report(tmp_path, rows)
    assert process.returncode == 0, process.stderr
    assert results(out)["neck_score"] == 0
    rows[-1] = ("Neck circumference", "16", "in")  # 40.64 cm, strictly >40
    process, out = run_report(tmp_path, rows)
    assert process.returncode == 0, process.stderr
    assert results(out)["neck_score"] == 1
    assert results(out)["stop_bang_category"] == "high"


def test_each_bang_item_independently_changes_total(tmp_path):
    baseline, out = run_report(tmp_path)
    assert baseline.returncode == 0
    for key, value, output in [("bmi_kg_m2", "35.1", "bmi_score"),
                               ("neck_circumference_cm", "40.1", "neck_score")]:
        rows = [(k, value if k == key else v, u) for k, v, u in VALID]
        process, out = run_report(tmp_path, rows)
        assert process.returncode == 0
        assert results(out)[output] == 1 and results(out)["stop_bang_score"] == 3
    for profile, output in [(("--age", "50.1", "--sex", "female"), "age_score"),
                            (("--age", "50", "--sex", "男"), "male_score")]:
        process, out = run_report(tmp_path, profile=profile)
        assert process.returncode == 0
        assert results(out)[output] == 1 and results(out)["stop_bang_score"] == 3


def test_stale_outputs_removed(tmp_path):
    assert run_report(tmp_path)[0].returncode == 0
    process, out = run_report(tmp_path, VALID[:-1])
    assert process.returncode == 3 and not (out / "result.json").exists()
    process, out = run_report(tmp_path)
    assert process.returncode == 0 and not (out / "problems.json").exists()
