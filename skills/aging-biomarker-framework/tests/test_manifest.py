"""skill.json inputs match presets, and a value that is not a predicted age stops the computation.

Before skillkit, an age acceleration (3.2) written as GrimAge2 gave an age
deviation of -56.80, DunedinPACE (a pace, about 1) was subtracted from the
chronological age, and a number the table could not parse crashed with a
traceback.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report
import skillkit
from presets import ALIASES, CLOCKS, PACE_CLOCKS

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))
WIDE = "name,predicted,age\nGrimAge2,70,60\nPhenoAge,55,60\nDunedinPACE,1.08,60\nHannum,62,60\n表型年龄,57.5,60\n"


def _csv(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    return path


def _run(out: Path, clocks: Path, *extra: str):
    code = personal_report.main(["--clocks", str(clocks), "--out", str(out), *extra])
    text = (out / "report.md").read_text(encoding="utf-8")
    outputs = json.loads((out / "result.json").read_text(encoding="utf-8"))["outputs"]
    return code, text, {key: item["value"] for key, item in outputs.items()}


def test_manifest_matches_presets():
    declared = {item["key"]: item for item in MANIFEST["inputs"] if item["from"] == "measurements"}
    for clock in CLOCKS:
        assert skillkit.normalize_unit(declared[clock]["unit"]) == ("1" if clock in PACE_CLOCKS else "a")
    for alias, clock in ALIASES.items():
        assert personal_report.input_key(alias) == clock, alias
    assert set(personal_report.DEVIATION_OUTPUTS) <= set(declared)
    assert not set(personal_report.DEVIATION_OUTPUTS) & set(PACE_CLOCKS)
    assert [item["key"] for item in MANIFEST["outputs"]] == list(personal_report.DEVIATION_OUTPUTS.values())
    assert declared["PhenoAge"]["output_of"] == ["dnam_phenoage"]
    assert declared["blood_phenoage"]["output_of"] == ["phenoage"]
    age = skillkit.spec_by_key(MANIFEST, "age")
    assert age["from"] == "profile" and age["flag"] == MANIFEST["entry"]["age_flag"] == "--age"
    assert MANIFEST["entry"]["measurements_flag"] == "--clocks"


def test_inputs_are_verified():
    assert MANIFEST["inputs_status"] == "verified"


def test_age_acceleration_written_as_predicted_age_is_refused(tmp_path: Path):
    clocks = _csv(tmp_path / "clocks.csv", "name,predicted,age\nGrimAge2,3.2,60\n")
    code, text, result = _run(tmp_path / "out", clocks)
    assert code == skillkit.EXIT_INPUT_PROBLEM
    assert "不算年龄偏差" in text and "不在合理范围" in text and "年龄加速值" in text
    assert "-56.80" not in text and "的年龄偏差是" not in text
    assert all(value is None for value in result.values())


def test_wrong_units_are_refused(tmp_path: Path):
    clocks = _csv(tmp_path / "clocks.csv", "name,value,unit\nDunedinPACE,1.05,a\nGrimAge2,70,mg/dL\n")
    code, text, result = _run(tmp_path / "out", clocks, "--age", "60")
    assert code == skillkit.EXIT_INPUT_PROBLEM
    assert text.count("不能换算") == 2
    assert "年龄偏差是" not in text
    assert result["grimage2_age_deviation"] is None


@pytest.mark.parametrize("table, extra", [
    ("name,predicted,age\nGrimAge2,70,600\n", ()),
    ("name,predicted,age\nGrimAge2,70,60\n", ("--age", "400")),
    ("name,predicted,age\nGrimAge2,abc,60\n", ()),
    ("clock,predicted,age\nGrimAge2,70,60\n", ()),
])
def test_bad_age_number_or_header_is_refused(tmp_path: Path, table: str, extra: tuple):
    code, text, result = _run(tmp_path / "out", _csv(tmp_path / "clocks.csv", table), *extra)
    assert code == skillkit.EXIT_INPUT_PROBLEM
    assert "输入没有通过检查" in text and "10.00" not in text
    assert result["grimage2_age_deviation"] is None


def test_result_json_holds_the_deviations(tmp_path: Path):
    code, text, result = _run(tmp_path / "out", _csv(tmp_path / "clocks.csv", WIDE))
    assert code == 0
    assert not (tmp_path / "out" / "problems.json").exists()
    assert result["grimage2_age_deviation"] == pytest.approx(10)
    assert result["dnam_phenoage_age_deviation"] == pytest.approx(-5)
    assert result["blood_phenoage_age_deviation"] == pytest.approx(-2.5)
    assert result["horvath_skin_blood_age_deviation"] is None
    assert result["grimage_age_deviation"] is None
    assert "- DunedinPACE：衰老速度 1.08。" in text and "-58.92" not in text
    assert "- Hannum：年龄偏差 2.00。基准表里没有这个时钟名字。" in text
    assert "- 表型年龄：年龄偏差 -2.50。基准表里没有这个时钟名字。" in text


def test_value_unit_table_with_age_flag(tmp_path: Path):
    table = "name,value,unit\nGrimAge2,70,岁\nDNAm PhenoAge,55,years\n"
    code, _text, result = _run(tmp_path / "out", _csv(tmp_path / "clocks.csv", table), "--age", "60")
    assert code == 0
    assert result["grimage2_age_deviation"] == pytest.approx(10)
    assert result["dnam_phenoage_age_deviation"] == pytest.approx(-5)
    code, _text, result = _run(tmp_path / "row", _csv(tmp_path / "row.csv", "name,value,unit\nGrimAge2,70,a\nage,60,岁\n"))
    assert code == 0 and result["grimage2_age_deviation"] == pytest.approx(10)


def test_missing_chronological_age_is_not_a_problem(tmp_path: Path):
    code, text, result = _run(tmp_path / "out", _csv(tmp_path / "clocks.csv", "name,value,unit\nGrimAge2,70,a\n"))
    assert code == 0
    assert "GrimAge2：没有实足年龄，不算年龄偏差。" in text
    assert result["grimage2_age_deviation"] is None
