"""skill.json inputs match presets, and unit or range mistakes stop the report.

Before the kit, albumin in g/dL (3.8) was listed with no unit check, an age
of 400 chose the adult clock, text in the age row crashed with a traceback,
and an empty lab cell was listed with no value.
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
from presets import ADULT, BOUNDARY, PEDIATRIC

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))
# Names _age_difference() and render_body() accept for the two non-lab rows.
DIFFERENCE_NAMES = ("standardized_age_difference", "年龄差", "age_difference")
AGE_NAMES = ("age", "年龄")


def _csv(path: Path, rows, header=None) -> Path:
    header = header or ",".join(MANIFEST["entry"]["measurements_header"])
    path.write_text("\n".join([header] + [",".join(row) for row in rows]) + "\n", encoding="utf-8")
    return path


def _before(rows) -> str:
    """The report the unchanged render functions write for these raw rows."""
    return personal_report._with_paper_card(personal_report.render_report(rows, [], []))


def _result(out: Path) -> dict:
    result = json.loads((out / "result.json").read_text(encoding="utf-8"))
    assert result["skill"] == "life-cycle-biological-clock"
    return result["outputs"]


def test_manifest_matches_presets():
    specs = skillkit.input_specs(MANIFEST)
    index = skillkit.alias_index(specs)
    drivers = [*PEDIATRIC, *ADULT]
    assert [spec["key"] for spec in specs] == ["standardized_age_difference"] + [
        index[skillkit.fold_name(aliases[0])][0]["key"] for _display, aliases, _direction in drivers
    ]
    for display, aliases, _direction in drivers:
        key = index[skillkit.fold_name(aliases[0])][0]["key"]
        assert skillkit.spec_by_key(MANIFEST, key)["label_zh"] == display
        for name in aliases:
            assert index[skillkit.fold_name(name)][0]["key"] == key
    for name in DIFFERENCE_NAMES:
        assert index[skillkit.fold_name(name)][0]["key"] == "standardized_age_difference"
    assert not any(spec["required"] for spec in specs)
    age = skillkit.spec_by_key(MANIFEST, "age")
    assert (age["from"], age["flag"], age["unit"], age["required"]) == ("profile", "--age", "a", True)
    assert age["range"][0] < presets.AGE_SPLIT < age["range"][1]
    assert all(personal_report._is_age_row(name, age) for name in AGE_NAMES)
    assert not personal_report._is_age_row("年龄差", age)
    assert MANIFEST["inputs_status"] == "verified"
    entry = MANIFEST["entry"]
    assert (entry["measurements_flag"], entry["age_flag"], entry["result_json"]) == ("--measurements", "--age", True)
    assert personal_report.has_header(",".join(entry["measurements_header"]))
    assert [item["key"] for item in MANIFEST["outputs"]] == ["adult_band"]


def test_documented_file_gives_the_same_report(tmp_path: Path):
    measurements = tmp_path / "measurements.csv"
    presets.write_fixture(measurements)
    out = tmp_path / "out"
    assert personal_report.main(["--measurements", str(measurements), "--out", str(out)]) == 0
    assert (out / "report.md").read_text(encoding="utf-8") == _before(presets.fixture_rows())
    assert _result(out)["adult_band"]["value"] is None
    assert not (out / "problems.json").exists()


@pytest.mark.parametrize(
    "difference, band",
    [("3.2", "过度偏离"), ("0.4", "平均偏离"), ("-2", "两档之外")],
)
def test_adult_band_matches_the_list(tmp_path: Path, difference, band):
    raw = [{"indicator": "age", "value": "40"}, {"indicator": "standardized_age_difference", "value": difference},
           {"indicator": "urea", "value": "8"}, {"indicator": "rdw", "value": "13.5"}]
    rows = [(row["indicator"], row["value"], "") for row in raw]
    out = tmp_path / "out"
    assert personal_report.main(["--measurements", str(_csv(tmp_path / "m.csv", rows)), "--out", str(out)]) == 0
    assert (out / "report.md").read_text(encoding="utf-8") == _before(raw)
    listed = presets.render_body(raw)[1][0]["name"]
    assert band == (listed if listed in {"平均偏离", "过度偏离"} else "两档之外")
    assert _result(out)["adult_band"]["value"] == band


def test_units_are_converted_and_age_flag_is_used(tmp_path: Path):
    rows = [("白蛋白", "3.8", "g/dL"), ("尿素", "8.2", "mmol/L"), ("葡萄糖", "6.1", "mmol/L")]
    out = tmp_path / "out"
    code = personal_report.main(["--measurements", str(_csv(tmp_path / "m.csv", rows)), "--age", "40", "--out", str(out)])
    assert code == 0
    assert (out / "report.md").read_text(encoding="utf-8") == _before(presets.fixture_rows())


def test_child_clock_ignores_the_difference(tmp_path: Path):
    rows = [("age", "10", ""), ("standardized_age_difference", "4", ""), ("AST", "20", "U/L"), ("urea", "5", "")]
    out = tmp_path / "out"
    assert personal_report.main(["--measurements", str(_csv(tmp_path / "m.csv", rows)), "--out", str(out)]) == 0
    raw = [{"indicator": "age", "value": "10"}, {"indicator": "standardized_age_difference", "value": "4"},
           {"indicator": "ast", "value": "20"}, {"indicator": "urea", "value": "5"}]
    assert (out / "report.md").read_text(encoding="utf-8") == _before(raw)
    assert _result(out)["adult_band"]["value"] is None


@pytest.mark.parametrize(
    "rows, age, reason",
    [
        ([("albumin", "3.8", "")], "40", "不在合理范围"),
        ([("urea", "14", "mg/dL")], "40", "不能换算"),
        ([("RDW", "42", "fL")], "40", "不能换算"),
        ([("standardized_age_difference", "25", "")], "40", "不在合理范围"),
        ([("urea", "8.2", "")], "400", "实足年龄"),
        ([("age", "四十", ""), ("urea", "8.2", "")], None, "不是一个可以计算的数"),
        ([("urea", "8.2", "")], None, "缺少实足年龄"),
    ],
    ids=["albumin-g-dl", "urea-mg-dl", "rdw-sd", "difference", "age-range", "age-text", "no-age"],
)
def test_wrong_or_missing_input_is_refused(tmp_path: Path, rows, age, reason):
    out = tmp_path / "out"
    argv = ["--measurements", str(_csv(tmp_path / "m.csv", rows)), "--out", str(out)]
    if age is not None:
        argv += ["--age", age]
    assert personal_report.main(argv) == skillkit.EXIT_INPUT_PROBLEM
    text = (out / "report.md").read_text(encoding="utf-8")
    assert text.splitlines()[0] == "# 临床时钟对照"
    assert "## 论文卡片" in text
    assert "输入没有通过检查，所以这次没有对照时钟" in text and reason in text
    assert "## 方法算出的名单" not in text
    assert text.splitlines()[-1] == BOUNDARY
    assert text.count("边界:") == 1
    assert json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert _result(out)["adult_band"]["value"] is None
