"""skill.json inputs match the script, and unit or range mistakes stop the report.

Before the kit, a PhenoAge gap written where PhenoAge belongs was subtracted
from age again (-4 gave -52), a birth year of 70 was placed outside both
cohorts, and text in a number cell crashed with a traceback.
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
from presets import BOUNDARY, MEASURES

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))
# Columns render_body() reads from the one measurement row.
SCRIPT_KEYS = ["phenoage", "birth_year", "kdm_age_gap", "metabolomic_age_gap", "immune_aging", "adipose_aging"]


def _long(path: Path, rows) -> Path:
    header = ",".join(MANIFEST["entry"]["measurements_header"])
    path.write_text("\n".join([header] + [",".join(row) for row in rows]) + "\n", encoding="utf-8")
    return path


def _result(out: Path) -> dict:
    result = json.loads((out / "result.json").read_text(encoding="utf-8"))
    assert result["skill"] == "biological-aging-generational-shifts"
    return result["outputs"]


def test_manifest_matches_script():
    measured = [item["key"] for item in MANIFEST["inputs"] if item["from"] == "measurements"]
    assert measured == SCRIPT_KEYS
    fixture_columns = presets.fixture_rows()[0].keys()
    assert set(fixture_columns) == set(SCRIPT_KEYS) | {"age"}
    labels = dict(MEASURES)
    for key in ("kdm_age_gap", "metabolomic_age_gap", "immune_aging", "adipose_aging"):
        assert skillkit.spec_by_key(MANIFEST, key)["label_zh"] == labels[key]
    phenoage = skillkit.spec_by_key(MANIFEST, "phenoage")
    assert (phenoage["unit"], phenoage["required"], phenoage["output_of"]) == ("a", True, ["phenoage"])
    optional = [key for key in SCRIPT_KEYS if key != "phenoage"]
    assert not any(skillkit.spec_by_key(MANIFEST, key)["required"] for key in optional)
    age = skillkit.spec_by_key(MANIFEST, "age")
    assert (age["from"], age["flag"], age["unit"], age["required"]) == ("profile", "--age", "a", True)
    assert personal_report._is_age_row("age", age) and personal_report._is_age_row("年龄", age)
    assert MANIFEST["inputs_status"] == "verified"
    entry = MANIFEST["entry"]
    assert (entry["measurements_flag"], entry["age_flag"], entry["result_json"]) == ("--measurements", "--age", True)
    assert personal_report.has_header(",".join(entry["measurements_header"]))
    assert {item["key"]: item["unit"] for item in MANIFEST["outputs"]} == {"phenoage_gap": "a"}


def test_documented_wide_row_gives_the_same_report(tmp_path: Path):
    wide = tmp_path / "measurements.csv"
    presets.write_fixture(wide)
    out = tmp_path / "out"
    assert personal_report.main(["--measurements", str(wide), "--out", str(out)]) == 0
    before = personal_report._with_paper_card(personal_report.render_report(presets.fixture_rows(), [], []))
    assert (out / "report.md").read_text(encoding="utf-8") == before
    row = presets.fixture_rows()[0]
    expected = float(row["phenoage"]) - float(row["age"])
    assert f"未标准化差值是 {expected:g}" in before
    assert _result(out)["phenoage_gap"]["value"] == pytest.approx(expected)
    assert not (out / "problems.json").exists()


def test_long_file_with_age_flag_gives_the_same_report(tmp_path: Path):
    rows = [("表型年龄", "52", "岁"), ("出生年", "1970", ""), ("KDM年龄差", "1.5", "岁"), ("脂肪组织衰老", "0.2", "")]
    out = tmp_path / "out"
    code = personal_report.main(["--measurements", str(_long(tmp_path / "m.csv", rows)), "--age", "48", "--out", str(out)])
    assert code == 0
    before = personal_report._with_paper_card(personal_report.render_report(presets.fixture_rows(), [], []))
    assert (out / "report.md").read_text(encoding="utf-8") == before
    row = presets.fixture_rows()[0]
    assert _result(out)["phenoage_gap"]["value"] == pytest.approx(float(row["phenoage"]) - float(row["age"]))


@pytest.mark.parametrize(
    "rows, age, reason",
    [
        ([("phenoage", "52", "%")], "48", "不能换算"),
        ([("phenoage", "-4", "")], "48", "不在合理范围"),
        ([("phenoage", "52岁", "")], "48", "不是一个可以计算的数"),
        ([("phenoage", "52", ""), ("birth_year", "70", "")], "48", "不在合理范围"),
        ([("phenoage", "52", ""), ("kdm_age_gap", "61", "")], "48", "不在合理范围"),
        ([("phenoage", "52", ""), ("immune_aging", "0.3", "SD")], "48", "不能换算"),
        ([("phenoage", "52", "")], "480", "实足年龄"),
        ([("phenoage", "52", "")], None, "缺少实足年龄"),
        ([("birth_year", "1970", ""), ("kdm_age_gap", "1.5", "")], "48", "缺少表型年龄"),
    ],
    ids=["unit", "negative", "text", "two-digit-year", "kdm", "immune-unit", "age-range", "no-age", "no-phenoage"],
)
def test_wrong_or_missing_input_is_refused(tmp_path: Path, rows, age, reason):
    out = tmp_path / "out"
    argv = ["--measurements", str(_long(tmp_path / "m.csv", rows)), "--out", str(out)]
    if age is not None:
        argv += ["--age", age]
    assert personal_report.main(argv) == skillkit.EXIT_INPUT_PROBLEM
    text = (out / "report.md").read_text(encoding="utf-8")
    assert text.splitlines()[0] == "# 衰老测量对照"
    assert "## 论文卡片" in text
    assert "输入没有通过检查，所以没有算出年龄差" in text and reason in text
    assert "未标准化差值是" not in text
    assert text.splitlines()[-1] == BOUNDARY
    assert text.count("边界:") == 1
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))
    assert problems["problems"]
    assert _result(out)["phenoage_gap"]["value"] is None


def test_a_good_run_clears_old_problems(tmp_path: Path):
    out = tmp_path / "out"
    bad = _long(tmp_path / "bad.csv", [("phenoage", "52", "%")])
    assert personal_report.main(["--measurements", str(bad), "--age", "48", "--out", str(out)]) == skillkit.EXIT_INPUT_PROBLEM
    good = _long(tmp_path / "good.csv", [("phenoage", "52", "")])
    assert personal_report.main(["--measurements", str(good), "--age", "48", "--out", str(out)]) == 0
    assert not (out / "problems.json").exists()
    assert _result(out)["phenoage_gap"]["value"] == pytest.approx(52.0 - 48.0)
