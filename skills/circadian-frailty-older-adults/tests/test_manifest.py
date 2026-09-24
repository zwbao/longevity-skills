"""skill.json inputs match presets, and input mistakes stop the computation.

Before the kit, M10 and L5 entered the wrong way round gave a relative amplitude
of -0.8389, and a negative M10 gave 1.5000; both looked like normal reports.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report
import skillkit
from presets import MEASUREMENTS

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))
# Table 1 means of the paper's cohort, in activity counts.
M10, L5 = "18172.7", "1591.6"
VALID = [("m10", M10, ""), ("l5", L5, ""), ("fatigue_effort", "1", "score"), ("fatigue_going", "0", "score")]


def _csv(path: Path, rows) -> Path:
    lines = [",".join(MANIFEST["entry"]["measurements_header"])] + [",".join(row) for row in rows]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _ra(m10: str, l5: str) -> float:
    return (float(m10) - float(l5)) / (float(m10) + float(l5))


def _outputs(out: Path) -> dict:
    result = json.loads((out / "result.json").read_text(encoding="utf-8"))
    assert result["skill"] == "circadian-frailty-older-adults"
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
    for key in ("fatigue_effort", "fatigue_going"):
        assert declared[key]["range"] == [0, 1]
    age = skillkit.spec_by_key(MANIFEST, "age")
    assert (age["from"], age["flag"], age["unit"], age["required"]) == ("profile", "--age", "a", False)
    assert MANIFEST["inputs_status"] == "verified"
    assert MANIFEST["entry"]["result_json"] is True
    assert personal_report.has_header(",".join(MANIFEST["entry"]["measurements_header"]))
    assert {item["key"]: item["unit"] for item in MANIFEST["outputs"]} == {"relative_amplitude": "1", "fatigue_score": "score"}


@pytest.mark.parametrize(
    "rows, age, reason",
    [
        ([("M10", L5, ""), ("L5", M10, ""), ("费力", "是", ""), ("提不起劲", "否", "")], "81", "填反了"),
        ([("M10", "-5", ""), ("L5", "1", ""), ("费力", "是", ""), ("提不起劲", "否", "")], "81", "不在合理范围"),
        ([("M10", M10, ""), ("L5", L5, ""), ("费力", "3", ""), ("提不起劲", "0", "")], "81", "频度分"),
        ([("M10", M10, ""), ("L5", L5, ""), ("fatigue_effort", "0.5", ""), ("fatigue_going", "0", "")], "81", "只能答是"),
        ([("M10", M10, "counts"), ("L5", L5, "counts"), ("费力", "是", ""), ("提不起劲", "否", "")], "81", "单位列留空"),
        ([("M10", M10, ""), ("L5", L5, ""), ("费力", "maybe", ""), ("提不起劲", "否", "")], "81", "不是一个可以计算的数"),
        (VALID, "810", "实足年龄"),
    ],
    ids=["l5-above-m10", "negative-m10", "frequency-answer", "half-answer", "unit-stated", "text-answer", "age"],
)
def test_wrong_input_stops_the_computation(tmp_path: Path, rows, age, reason):
    out = tmp_path / "out"
    code = personal_report.main(["--measurements", str(_csv(tmp_path / "m.csv", rows)), "--age", age, "--out", str(out)])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    text = (out / "report.md").read_text(encoding="utf-8")
    assert text.splitlines()[0] == "# 昼夜活动与衰弱"
    assert "## 论文卡片" in text
    assert "输入没有通过检查" in text and reason in text
    assert "相对振幅是" not in text and "疲劳分是" not in text
    assert f"{_ra(M10, L5):.4f}" not in text and f"{-_ra(M10, L5):.4f}" not in text
    assert text.rstrip().splitlines()[-1].startswith("边界: ")
    assert (out / "problems.json").exists()
    assert {key: item["value"] for key, item in _outputs(out).items()} == {"relative_amplitude": None, "fatigue_score": None}


def test_result_json_holds_the_computed_outputs(tmp_path: Path):
    out = tmp_path / "out"
    code = personal_report.main(["--measurements", str(_csv(tmp_path / "m.csv", VALID)), "--age", "81", "--out", str(out)])
    assert code == 0
    text = (out / "report.md").read_text(encoding="utf-8")
    assert f"相对振幅是 {_ra(M10, L5):.4f}" in text
    assert "疲劳分是 1" in text
    outputs = _outputs(out)
    assert outputs["relative_amplitude"]["value"] == pytest.approx(_ra(M10, L5))
    assert outputs["relative_amplitude"]["unit"] == "1"
    assert outputs["fatigue_score"]["value"] == 1
    assert outputs["fatigue_score"]["unit"] == "score"
    assert not (out / "problems.json").exists()


def test_yes_no_answers_and_chinese_names_still_work(tmp_path: Path):
    measures = tmp_path / "m.txt"
    measures.write_text(f"最活跃十小时,{M10}\n最不活跃五小时,{L5}\n费力,是\n提不起劲,是\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "out", 81.0, None, None, measures).read_text(encoding="utf-8")
    assert f"相对振幅是 {_ra(M10, L5):.4f}" in text
    assert "疲劳分是 2" in text
    assert _outputs(tmp_path / "out")["fatigue_score"]["value"] == 2


def test_missing_input_keeps_the_old_wording(tmp_path: Path):
    measures = tmp_path / "m.txt"
    measures.write_text("M10,3\nL5,1\n费力,是\n", encoding="utf-8")
    out = tmp_path / "out"
    assert personal_report.main(["--measurements", str(measures), "--out", str(out)]) == 0
    text = (out / "report.md").read_text(encoding="utf-8")
    assert "疲劳分缺一道题" in text and "相对振幅是 0.5000" in text
    assert not (out / "problems.json").exists()
    outputs = _outputs(out)
    assert outputs["relative_amplitude"]["value"] == pytest.approx(0.5)
    assert outputs["fatigue_score"]["value"] is None
