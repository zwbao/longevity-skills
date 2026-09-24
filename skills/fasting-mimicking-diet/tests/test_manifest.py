"""skill.json inputs match the script, and implausible inputs stop the report.

Run by hand against the old script: a baseline of 400, an age gap of -3.2 as
the follow-up, --age 400 and a fasting glucose of 5.6 (mmol/L read as mg/dL)
gave a normal-looking report ("前后差 -403.2 年", "预计变化 -27.0583 年",
"空腹血糖是 6") and exit code 0.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report
import skillkit
from presets import BOUNDARY, CHANGE_INTERCEPT, CHANGE_ON_AGE, CHANGE_ON_BIOAGE, GLUCOSE_AT_RISK

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))
INPUTS = {item["key"]: item for item in MANIFEST["inputs"]}
BIOAGE_KEYS = ["biological_age_baseline", "biological_age_followup"]


def _csv(path: Path, rows) -> Path:
    lines = ["item,value,unit"] + [",".join(row) for row in rows]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _run(tmp_path: Path, rows, *extra: str):
    out = tmp_path / "out"
    code = personal_report.main(["--measurements", str(_csv(tmp_path / "m.csv", rows)), *extra, "--out", str(out)])
    report = (out / "report.md").read_text(encoding="utf-8")
    result = json.loads((out / "result.json").read_text(encoding="utf-8"))
    return code, report, result


def _assert_nothing_computed(report: str, result: dict) -> None:
    assert "后一次减去前一次是" not in report
    assert "预计变化是" not in report
    assert "- 前后差" not in report and "- 预计变化" not in report
    assert all(item["value"] is None for item in result["outputs"].values())
    assert report.splitlines()[0] == f"# {personal_report.TITLE}"
    assert "## 论文卡片" in report
    assert report.splitlines()[-1] == f"边界: {BOUNDARY}"


def test_manifest_matches_script():
    measured = [key for key, item in INPUTS.items() if item["from"] == "measurements"]
    assert measured == ["biological_age_baseline", "biological_age_followup", "glucose_mg_dl", "bmi"]
    index = skillkit.alias_index(skillkit.input_specs(MANIFEST))
    # Every row name the script read before skill.json existed still lands on the same input.
    old_names = {
        "biological_age_baseline": "biological_age_baseline",
        "biological_age_followup": "biological_age_followup",
        "glucose": "glucose_mg_dl",
        "空腹血糖": "glucose_mg_dl",
        "bmi": "bmi",
    }
    for name, key in old_names.items():
        assert index[skillkit.fold_name(name)][0]["key"] == key
    for key in BIOAGE_KEYS + ["age"]:
        assert skillkit.normalize_unit(INPUTS[key]["unit"]) == "a"
    # The paper's glucose cut-off (99) is mg/dL; mmol/L converts by the declared factor.
    assert skillkit.normalize_unit(INPUTS["glucose_mg_dl"]["unit"]) == "mg/dl"
    low, high = INPUTS["glucose_mg_dl"]["range"]
    assert low < GLUCOSE_AT_RISK < high
    assert skillkit.unit_factor(INPUTS["glucose_mg_dl"], "mmol/L") == pytest.approx(18.016)
    assert INPUTS["age"]["from"] == "profile" and INPUTS["age"]["flag"] == MANIFEST["entry"]["age_flag"] == "--age"
    assert MANIFEST["entry"]["measurements_flag"] == "--measurements"
    assert MANIFEST["entry"]["result_json"] is True
    declared = [item["key"] for item in MANIFEST["outputs"]]
    assert declared == list(personal_report.OUTPUT_KEYS)
    assert set(personal_report.compute({}, None)) == set(declared)
    assert all(item["unit"] == "a" for item in MANIFEST["outputs"])


def test_status_and_no_cross_method_chaining():
    # The paper's biological age is the seven-marker KDM age. A phenotypic age
    # is a different quantity, so the harness must not chain it into this
    # equation; the note says so instead.
    assert MANIFEST["inputs_status"] == "verified"
    ages = [item for item in MANIFEST["inputs"] if item.get("unit") == "a" and item["key"] != "age"]
    assert [item["key"] for item in ages] == BIOAGE_KEYS
    for item in ages:
        assert "output_of" not in item
        assert "KDM" in item["note_zh"]
        assert item["range"] == [0, 130]
    assert len({item["group"] for item in ages}) == 1
    assert "前一次" in INPUTS["biological_age_baseline"]["label_zh"]
    assert "后一次" in INPUTS["biological_age_followup"]["label_zh"]
    assert "output_of" not in INPUTS["age"]
    assert INPUTS["age"]["range"] == [18, 110]


def test_biological_age_of_400_is_refused(tmp_path: Path):
    code, report, result = _run(tmp_path, [("biological_age_baseline", "400", ""), ("biological_age_followup", "47.5", "")], "--age", "52")
    assert code == skillkit.EXIT_INPUT_PROBLEM
    assert "不在合理范围" in report and "400" in report
    _assert_nothing_computed(report, result)
    assert (tmp_path / "out" / "problems.json").exists()


def test_age_gap_passed_as_age_is_refused(tmp_path: Path):
    code, report, result = _run(tmp_path, [("biological_age_baseline", "50", ""), ("随访生物年龄", "-3.2", "")])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    assert "不是生物年龄减实足年龄的差" in report
    _assert_nothing_computed(report, result)


def test_chronological_age_out_of_range_is_refused(tmp_path: Path):
    code, report, result = _run(tmp_path, [("biological_age_baseline", "45", "")], "--age", "400")
    assert code == skillkit.EXIT_INPUT_PROBLEM
    assert "实足年龄" in report and "18–110" in report
    _assert_nothing_computed(report, result)


def test_glucose_in_mmol_needs_its_unit(tmp_path: Path):
    code, report, result = _run(tmp_path, [("biological_age_baseline", "50", ""), ("空腹血糖", "5.6", "")])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    assert "mmol/L" in report
    _assert_nothing_computed(report, result)
    code, report, _result = _run(tmp_path, [("biological_age_baseline", "50", ""), ("空腹血糖", "5.6", "mmol/L")])
    assert code == 0
    assert "空腹血糖是 101 mg/dL" in report


def test_result_json_holds_the_computed_outputs(tmp_path: Path):
    (tmp_path / "out").mkdir()
    (tmp_path / "out" / "problems.json").write_text("{}", encoding="utf-8")
    rows = [("基线生物年龄", "50", "岁"), ("biological_age_followup", "47.5", "")]
    code, report, result = _run(tmp_path, rows, "--age", "52")
    assert code == 0
    assert not (tmp_path / "out" / "problems.json").exists()
    predicted = CHANGE_INTERCEPT + CHANGE_ON_BIOAGE * 50 + CHANGE_ON_AGE * 52
    assert result["skill"] == "fasting-mimicking-diet"
    assert result["outputs"]["bioage_change"]["value"] == pytest.approx(-2.5)
    assert result["outputs"]["bioage_change_predicted"]["value"] == pytest.approx(predicted)
    assert "-2.5 年" in report and f"{predicted:.4f}" in report


def test_missing_rows_keep_the_old_wording(tmp_path: Path):
    code, report, result = _run(tmp_path, [("biological_age_baseline", "45", "")])
    assert code == 0
    assert "没有算出生物年龄" in report
    assert result["outputs"]["bioage_change"]["value"] is None
    assert result["outputs"]["bioage_change_predicted"]["value"] is None
