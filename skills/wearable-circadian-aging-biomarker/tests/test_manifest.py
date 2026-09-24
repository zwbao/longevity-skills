"""skill.json inputs match presets, and unit mistakes stop the computation.

Before the kit, MESOR in g (0.03), an acrophase in clock hours under the radian
name, and a negative acrophase all produced a normal-looking CosinorAge.
"""

import json
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report
import skillkit
from presets import MEASUREMENTS, PI, cosinor_age

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))
VALID = [("mesor", "30", ""), ("amplitude", "20", ""), ("acrophase_rad", "3.5", "1")]


def _csv(path: Path, rows) -> Path:
    lines = [",".join(MANIFEST["entry"]["measurements_header"])] + [",".join(row) for row in rows]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _expected(acrophase_rad, age=60):
    return cosinor_age(Decimal("30"), Decimal("20"), Decimal(str(acrophase_rad)), Decimal(str(age)))


def _shown(value) -> str:
    return str(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def _outputs(out: Path) -> dict:
    result = json.loads((out / "result.json").read_text(encoding="utf-8"))
    assert result["skill"] == "wearable-circadian-aging-biomarker"
    return result["outputs"]


def test_manifest_matches_presets():
    declared = {item["key"]: item for item in MANIFEST["inputs"] if item["from"] == "measurements"}
    assert list(declared) == [key for key, _names, _unit in MEASUREMENTS]
    index = skillkit.alias_index(skillkit.input_specs(MANIFEST))
    for key, names, unit in MEASUREMENTS:
        assert key in names
        assert skillkit.normalize_unit(declared[key].get("unit", "")) == skillkit.normalize_unit(unit)
        for name in names:
            assert index[skillkit.fold_name(name)][0]["key"] == key
    age = skillkit.spec_by_key(MANIFEST, "age")
    assert (age["from"], age["flag"], age["unit"], age["required"]) == ("profile", "--age", "a", True)
    assert MANIFEST["inputs_status"] == "verified"
    assert MANIFEST["entry"]["result_json"] is True
    assert personal_report.has_header(",".join(MANIFEST["entry"]["measurements_header"]))
    assert {item["key"]: item["unit"] for item in MANIFEST["outputs"]} == {"cosinorage": "a", "cosinorage_advance": "a"}


@pytest.mark.parametrize(
    "rows, age, reason",
    [
        ([("MESOR", "0.03", ""), ("振幅", "0.02", ""), ("acrophase", "3.5", "")], "60", "不在合理范围"),
        ([("MESOR", "30", ""), ("振幅", "20", ""), ("acrophase", "13.37", "")], "60", "不在合理范围"),
        ([("MESOR", "30", ""), ("振幅", "20", ""), ("acrophase", "-3.5", "")], "60", "负的相位"),
        ([("MESOR", "30", ""), ("振幅", "20", ""), ("acrophase_time", "837", "")], "60", "min"),
        ([("MESOR", "30", ""), ("振幅", "20", ""), ("峰时", "210", "deg")], "60", "不能换算"),
        ([("MESOR", "30", ""), ("振幅", "20", ""), ("峰时", "13:57", "")], "60", "不是一个可以计算的数"),
        (VALID, "400", "实足年龄"),
    ],
    ids=["g-not-mg", "hours-as-radians", "negative-acrophase", "minutes-without-unit", "degrees", "clock-text", "age"],
)
def test_wrong_unit_or_range_stops_the_computation(tmp_path: Path, rows, age, reason):
    out = tmp_path / "out"
    code = personal_report.main(["--measurements", str(_csv(tmp_path / "m.csv", rows)), "--age", age, "--out", str(out)])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    text = (out / "report.md").read_text(encoding="utf-8")
    assert text.splitlines()[0] == "# 可穿戴加速度的昼夜年龄"
    assert "## 论文卡片" in text
    assert "输入没有通过检查" in text and reason in text
    assert "CosinorAge 是" not in text and "CosinorAgeAdvance" not in text
    assert _shown(_expected("3.5")) not in text
    assert text.rstrip().splitlines()[-1].startswith("边界: ")
    assert (out / "problems.json").exists()
    assert {key: item["value"] for key, item in _outputs(out).items()} == {"cosinorage": None, "cosinorage_advance": None}


def test_result_json_holds_the_computed_age(tmp_path: Path):
    out = tmp_path / "out"
    code = personal_report.main(["--measurements", str(_csv(tmp_path / "m.csv", VALID)), "--age", "60", "--out", str(out)])
    assert code == 0
    expected = _expected("3.5")
    assert f"CosinorAge 是 {_shown(expected)} 岁" in (out / "report.md").read_text(encoding="utf-8")
    outputs = _outputs(out)
    assert outputs["cosinorage"]["value"] == pytest.approx(float(expected))
    assert outputs["cosinorage_advance"]["value"] == pytest.approx(float(expected) - 60)
    assert outputs["cosinorage"]["unit"] == "a"
    assert not (out / "problems.json").exists()


def test_clock_hours_minutes_and_chinese_names_give_the_same_age(tmp_path: Path):
    radians = Decimal("13.95") * 2 * PI / Decimal(24)
    expected = float(_expected(radians))
    minutes = [("mesor", "30", ""), ("amplitude", "20", ""), ("acrophase_time", "837", "min")]
    personal_report.report(tmp_path / "a", 60.0, None, None, _csv(tmp_path / "a.csv", minutes))
    assert _outputs(tmp_path / "a")["cosinorage"]["value"] == pytest.approx(expected, rel=1e-7)
    legacy = tmp_path / "b.txt"
    legacy.write_text("节律中值,30\n余弦振幅,20\n峰时,13.95\n性别,女\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "b", 60.0, None, None, legacy).read_text(encoding="utf-8")
    assert _outputs(tmp_path / "b")["cosinorage"]["value"] == pytest.approx(expected)
    assert "不算分性别年龄" in text


def test_missing_input_keeps_the_old_wording(tmp_path: Path):
    partial = tmp_path / "part.txt"
    partial.write_text("MESOR,30\nacrophase,3.5\n", encoding="utf-8")
    out = tmp_path / "out"
    assert personal_report.main(["--measurements", str(partial), "--age", "60", "--out", str(out)]) == 0
    text = (out / "report.md").read_text(encoding="utf-8")
    assert "缺振幅。缺的项不用 0 填。" in text
    assert not (out / "problems.json").exists()
    assert _outputs(out)["cosinorage"]["value"] is None
