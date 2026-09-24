"""skill.json inputs match the script, and implausible inputs stop the report.

Run by hand against the old script: GrimAge rows of 400 and -3 gave a
stability of 0.00248 and exit code 0; a table without a biological_age column
and a time_years of 2019-03 ended in a traceback; NA was dropped silently.

The paper's "phenoage" is the DNA-methylation PhenoAge. The blood phenotypic
age that accelerated-biological-aging-risk outputs arrives as
phenoage_visit1..4 and is listed as 血检表型年龄, outside the paper's table.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report
import presets
import skillkit

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))
INPUTS = {item["key"]: item for item in MANIFEST["inputs"]}


def _run(tmp_path: Path, text: str):
    measurements = tmp_path / "m.csv"
    measurements.write_text(text, encoding="utf-8")
    out = tmp_path / "out"
    code = personal_report.main(["--measurements", str(measurements), "--out", str(out)])
    report = (out / "report.md").read_text(encoding="utf-8")
    result = json.loads((out / "result.json").read_text(encoding="utf-8"))
    values = {key: item["value"] for key, item in result["outputs"].items()}
    return code, report, values


def _assert_nothing_computed(report: str, values: dict) -> None:
    assert "未缩放的个体稳定度是" not in report
    assert "## 方法算出的名单" not in report
    assert all(value is None for value in values.values())
    assert set(values) == set(personal_report.OUTPUT_KEYS.values())
    assert report.splitlines()[0] == f"# {personal_report.TITLE}"
    assert "## 论文卡片" in report
    assert report.splitlines()[-1] == presets.BOUNDARY


def test_manifest_matches_script():
    measured = [key for key, item in INPUTS.items() if item["from"] == "measurements"]
    assert measured == ["biological_age", "time_years", *personal_report.VISIT_KEYS]
    visits = [item for item in MANIFEST["inputs"] if item.get("group") == "phenoage"]
    assert tuple(item["key"] for item in visits) == personal_report.VISIT_KEYS
    for number, item in enumerate(visits, start=1):
        assert f"第{number}次血检表型年龄" in item["label_zh"]
    for key in ("biological_age", "time_years", *personal_report.VISIT_KEYS):
        assert skillkit.normalize_unit(INPUTS[key]["unit"]) == "a"
    # Every clock render_body can list has exactly one declared output.
    clocks = {name for name, _category, _includes_ca in presets.CLOCKS} | {presets.BLOOD_PHENOAGE}
    assert set(personal_report.OUTPUT_KEYS) == clocks
    assert all(presets.known_clock(name) for name in clocks)
    assert [item["key"] for item in MANIFEST["outputs"]] == list(personal_report.OUTPUT_KEYS.values())
    assert all(item["unit"] == "1" for item in MANIFEST["outputs"])
    entry = MANIFEST["entry"]
    assert entry["measurements_flag"] == "--measurements"
    assert entry["measurements_header"] == ["item", "value", "unit"]
    assert entry["result_json"] is True
    assert "age_flag" not in entry


def test_status_and_phenoage_chaining():
    assert MANIFEST["inputs_status"] == "verified"
    for key in personal_report.VISIT_KEYS:
        assert INPUTS[key]["output_of"] == ["phenoage"]
        assert INPUTS[key]["range"] == [0, 130]
    # The clock-table column holds the paper's clocks, mostly methylation clocks.
    # A blood phenotypic age written there as "phenoage" would be filed as the
    # paper's DNAm PhenoAge, so it is not chained.
    assert "output_of" not in INPUTS["biological_age"]
    assert INPUTS["biological_age"]["range"] == [0, 130]


def test_clock_age_of_400_is_refused(tmp_path: Path):
    code, report, values = _run(tmp_path, "clock,biological_age\nGrimAge,400\nGrimAge,41\nPhenoAge,40\nPhenoAge,42\n")
    assert code == skillkit.EXIT_INPUT_PROBLEM
    assert "GrimAge 读成 400 a" in report and "不在合理范围 0–130 a" in report
    _assert_nothing_computed(report, values)
    assert (tmp_path / "out" / "problems.json").exists()


def test_age_gap_passed_as_blood_phenoage_is_refused(tmp_path: Path):
    code, report, values = _run(tmp_path, "item,value,unit\nphenoage_visit1,-3.2,a\nphenoage_visit2,50,a\n")
    assert code == skillkit.EXIT_INPUT_PROBLEM
    assert "不是它减实足年龄的差" in report
    _assert_nothing_computed(report, values)


@pytest.mark.parametrize("text, expected", [
    ("clock,value\nGrimAge,40\nGrimAge,41\n", "clock,biological_age"),
    ("clock,biological_age,time_years\nSkin & Blood,40,2019-03\nSkin & Blood,44,2020-03\n", "2019-03"),
    ("clock,biological_age\nGrimAge,NA\nGrimAge,41\n", "「NA」"),
    ("clock,biological_age,unit\nHannum,480,months\nHannum,492,months\n", "不能换算"),
])
def test_malformed_tables_are_refused_with_a_reason(tmp_path: Path, text: str, expected: str):
    code, report, values = _run(tmp_path, text)
    assert code == skillkit.EXIT_INPUT_PROBLEM
    assert expected in report
    _assert_nothing_computed(report, values)


def test_rows_for_clocks_outside_the_table_are_not_checked(tmp_path: Path):
    code, report, values = _run(tmp_path, "clock,biological_age\nPhenoAge,40\nPhenoAge,42\nGrimAgeAccel,-2.5\n")
    assert code == 0
    assert values["stability_index_dnam_phenoage"] == pytest.approx(0.5)
    assert "grimageaccel" not in report.casefold()


def test_result_json_holds_the_computed_outputs(tmp_path: Path):
    (tmp_path / "out").mkdir()
    (tmp_path / "out" / "problems.json").write_text("{}", encoding="utf-8")
    fixture = "clock,biological_age\nPhenoAge,40\nPhenoAge,42\nPhenoAge,44\nGrimAge,50\nNotAPaperClock,3\n"
    code, report, values = _run(tmp_path, fixture)
    assert code == 0
    assert not (tmp_path / "out" / "problems.json").exists()
    assert values["stability_index_dnam_phenoage"] == pytest.approx(0.375)
    assert values["stability_index_grimage"] is None
    assert values["stability_index_blood_phenoage"] is None
    assert "未缩放的个体稳定度是 0.375" in report


def test_blood_phenoage_visits_are_listed_outside_the_paper_table(tmp_path: Path):
    code, report, values = _run(tmp_path, "item,value,unit\nphenoage_visit1,48,a\nphenoage_visit2,50,岁\nphenoage_visit3,49,\n")
    assert code == 0
    # Pairwise absolute differences 2, 1, 1: mean 4/3, stability 0.75.
    assert values["stability_index_blood_phenoage"] == pytest.approx(0.75)
    assert values["stability_index_dnam_phenoage"] is None
    line = next(row for row in report.splitlines() if row.startswith(f"- {presets.BLOOD_PHENOAGE}："))
    assert "未缩放的个体稳定度是 0.75" in line and "论文表格以外" in line
    assert "表观遗传" not in line
