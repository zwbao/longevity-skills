"""skill.json inputs match the script, and unit or range mistakes stop the readout.

Before the kit, a BMI of 310 (a weight in the BMI row) passed the age-BMI
sentence, text in the BMI row was dropped without a word, an age of 500 was
reported as outside the atlas, and a row named BMI instead of bmi was ignored.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report
import skillkit
from presets import BMI_CUT, BOUNDARY, FIG6C_AGE

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))


def _csv(path: Path, rows, header=None) -> Path:
    header = header or ",".join(MANIFEST["entry"]["measurements_header"])
    path.write_text("\n".join([header] + [",".join(row) for row in rows]) + "\n", encoding="utf-8")
    return path


def _before(measurements: Path, age: float) -> str:
    """The report the unchanged file reader and method_lines() write."""
    return personal_report._with_paper_card(personal_report.render(age, [], None, measurements))


def _result(out: Path) -> dict:
    result = json.loads((out / "result.json").read_text(encoding="utf-8"))
    assert result["skill"] == "testis-transcriptomic-atlas-lifespan"
    return result["outputs"]


def test_manifest_matches_script():
    specs = skillkit.input_specs(MANIFEST)
    assert [spec["key"] for spec in specs] == ["bmi"]
    assert (specs[0]["unit"], specs[0]["required"]) == ("kg/m^2", False)
    low, high = specs[0]["range"]
    assert low < BMI_CUT < high
    age = skillkit.spec_by_key(MANIFEST, "age")
    assert (age["from"], age["flag"], age["unit"], age["required"]) == ("profile", "--age", "a", True)
    assert age["range"][0] < FIG6C_AGE < age["range"][1]
    assert MANIFEST["inputs_status"] == "verified"
    entry = MANIFEST["entry"]
    assert (entry["measurements_flag"], entry["age_flag"], entry["result_json"]) == ("--measurements", "--age", True)
    assert personal_report.has_header(",".join(entry["measurements_header"]))
    assert [item["key"] for item in MANIFEST["outputs"]] == ["age_group", "age_over_45_and_bmi_30"]


@pytest.mark.parametrize(
    "text, age, group, statement",
    [
        (personal_report.SAMPLE_MEASUREMENTS, 50, "50多岁", "是"),
        ("item,value\nbmi,24\n", 50, "50多岁", "否"),
        ("item,value\nbmi,31\n", 40, "40多岁", "否"),
        ("gene,value\nbmi,32\n", 62, "60多岁", "是"),
        ("bmi,waist_cm\n30,90\n", 46, "40多岁", "是"),
        ("item,value\nbmi,31\n", 75, None, None),
        ("item,value\n", 35, "30多岁", None),
    ],
    ids=["sample", "lean", "under-45", "gene-layout", "wide-row", "outside-atlas", "no-bmi"],
)
def test_documented_files_give_the_same_report(tmp_path: Path, text, age, group, statement):
    measurements = tmp_path / "m.csv"
    measurements.write_text(text, encoding="utf-8")
    out = tmp_path / "out"
    assert personal_report.main(["--measurements", str(measurements), "--age", str(age), "--out", str(out)]) == 0
    report = (out / "report.md").read_text(encoding="utf-8")
    assert report == _before(measurements, float(age))
    outputs = _result(out)
    assert outputs["age_group"]["value"] == group == personal_report.decade_label(float(age))
    assert outputs["age_over_45_and_bmi_30"]["value"] == statement
    if statement == "是":
        assert "按这句写法，年龄和体质指数同时落在里面。" in report
    elif statement == "否":
        assert "按这句写法，没有同时落在里面。" in report
    assert not (out / "problems.json").exists()


def test_unit_and_other_names_are_read(tmp_path: Path):
    out = tmp_path / "out"
    rows = [("BMI", "31", "kg/m²")]
    assert personal_report.main(["--measurements", str(_csv(tmp_path / "m.csv", rows)), "--age", "50", "--out", str(out)]) == 0
    old = tmp_path / "old.csv"
    old.write_text(personal_report.SAMPLE_MEASUREMENTS, encoding="utf-8")
    assert (out / "report.md").read_text(encoding="utf-8") == _before(old, 50.0)


@pytest.mark.parametrize(
    "rows, age, reason",
    [
        ([("bmi", "310", "")], "50", "不在合理范围"),
        ([("bmi", "31", "kg")], "50", "不能换算"),
        ([("bmi", "超重", "")], "50", "不是一个可以计算的数"),
        ([("bmi", "31", ""), ("体质指数", "28", "")], "50", "出现了两次"),
        ([("bmi", "31", "")], "500", "实足年龄"),
        ([("bmi", "31", "")], None, "缺少实足年龄"),
    ],
    ids=["weight-not-bmi", "unit", "text", "duplicate", "age-range", "no-age"],
)
def test_wrong_or_missing_input_is_refused(tmp_path: Path, rows, age, reason):
    out = tmp_path / "out"
    argv = ["--measurements", str(_csv(tmp_path / "m.csv", rows)), "--out", str(out)]
    if age is not None:
        argv += ["--age", age]
    assert personal_report.main(argv) == skillkit.EXIT_INPUT_PROBLEM
    text = (out / "report.md").read_text(encoding="utf-8")
    assert text.splitlines()[0] == "# 睾丸衰老阶段"
    assert "## 论文卡片" in text
    assert "输入没有通过检查，所以没有对照衰老阶段" in text and reason in text
    assert "这次按年龄把你放在" not in text and "## 方法算出的名单" not in text
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
    assert json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert {key: item["value"] for key, item in _result(out).items()} == {"age_group": None, "age_over_45_and_bmi_30": None}


def test_a_good_run_clears_old_problems(tmp_path: Path):
    out = tmp_path / "out"
    bad = _csv(tmp_path / "bad.csv", [("bmi", "310", "")])
    assert personal_report.main(["--measurements", str(bad), "--age", "50", "--out", str(out)]) == skillkit.EXIT_INPUT_PROBLEM
    good = _csv(tmp_path / "good.csv", [("bmi", "31", "")])
    assert personal_report.main(["--measurements", str(good), "--age", "50", "--out", str(out)]) == 0
    assert not (out / "problems.json").exists()
    assert _result(out)["age_group"]["value"] == "50多岁"
