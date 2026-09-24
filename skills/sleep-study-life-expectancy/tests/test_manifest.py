"""skill.json inputs match the script, and unit or range mistakes stop the subtraction.

Before the kit, an age-estimate error written where the estimate belongs was
subtracted again, an age of 700 gave a difference, and a unit after the value
(age_estimate,78,岁) crashed with a traceback.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report
import skillkit
from presets import BOUNDARY, TITLE

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))
# Names build() reads from the measurement file.
SCRIPT_NAMES = ("age_estimate", "年龄估计")


def _csv(path: Path, rows, header=None) -> Path:
    header = header or ",".join(MANIFEST["entry"]["measurements_header"])
    path.write_text("\n".join([header] + [",".join(row) for row in rows]) + "\n", encoding="utf-8")
    return path


def _result(out: Path) -> dict:
    result = json.loads((out / "result.json").read_text(encoding="utf-8"))
    assert result["skill"] == "sleep-study-life-expectancy"
    return result["outputs"]


def _before(measurements: Path, age: float) -> str:
    """The report the unchanged loader and render functions write."""
    text = personal_report.render_report(personal_report.load_measurements(measurements), [], [], age)
    return personal_report._with_paper_card(text)


def test_manifest_matches_script():
    specs = skillkit.input_specs(MANIFEST)
    assert [spec["key"] for spec in specs] == ["age_estimate"]
    index = skillkit.alias_index(specs)
    for name in SCRIPT_NAMES:
        assert index[skillkit.fold_name(name)][0]["key"] == "age_estimate"
    assert (specs[0]["unit"], specs[0]["required"]) == ("a", True)
    age = skillkit.spec_by_key(MANIFEST, "age")
    assert (age["from"], age["flag"], age["unit"], age["required"]) == ("profile", "--age", "a", True)
    assert MANIFEST["inputs_status"] == "verified"
    entry = MANIFEST["entry"]
    assert (entry["measurements_flag"], entry["age_flag"], entry["result_json"]) == ("--measurements", "--age", True)
    assert personal_report.has_header(",".join(entry["measurements_header"]))
    assert {item["key"]: item["unit"] for item in MANIFEST["outputs"]} == {"age_estimate_error": "a"}


@pytest.mark.parametrize(
    "text",
    ["name,value\nage_estimate,78\n", "年龄估计,78\n", "项目,结果\n年龄估计,78.5\n"],
    ids=["documented", "no-header", "chinese-header"],
)
def test_documented_files_give_the_same_report(tmp_path: Path, text):
    measurements = tmp_path / "m.csv"
    measurements.write_text(text, encoding="utf-8")
    out = tmp_path / "out"
    assert personal_report.main(["--measurements", str(measurements), "--age", "70", "--out", str(out)]) == 0
    before = _before(measurements, 70.0)
    assert (out / "report.md").read_text(encoding="utf-8") == before
    estimate = float(personal_report.load_measurements(measurements).get("age_estimate") or
                     personal_report.load_measurements(measurements)["年龄估计"])
    assert f"年龄差 {estimate - 70.0:g} 岁" in before
    assert _result(out)["age_estimate_error"]["value"] == pytest.approx(estimate - 70.0)
    assert _result(out)["age_estimate_error"]["unit"] == "a"
    assert not (out / "problems.json").exists()


def test_unit_column_is_read(tmp_path: Path):
    out = tmp_path / "out"
    code = personal_report.main(["--measurements", str(_csv(tmp_path / "m.csv", [("PSG age", "78", "岁")])), "--age", "70", "--out", str(out)])
    assert code == 0
    old = tmp_path / "old.csv"
    old.write_text("name,value\nage_estimate,78\n", encoding="utf-8")
    assert (out / "report.md").read_text(encoding="utf-8") == _before(old, 70.0)


@pytest.mark.parametrize(
    "rows, age, reason",
    [
        ([("age_estimate", "78", "%")], "70", "不能换算"),
        ([("age_estimate", "8", "")], "70", "不在合理范围"),
        ([("age_estimate", "七十八", "")], "70", "不是一个可以计算的数"),
        ([("age_estimate", "78", ""), ("年龄估计", "80", "")], "70", "出现了两次"),
        ([("age_estimate", "78", "")], "700", "实足年龄"),
        ([("age_estimate", "78", "")], None, "缺少实足年龄"),
        ([("sleep_efficiency", "85", "%")], "70", "缺少年龄估计"),
    ],
    ids=["unit", "error-not-estimate", "text", "duplicate", "age-range", "no-age", "no-estimate"],
)
def test_wrong_or_missing_input_is_refused(tmp_path: Path, rows, age, reason):
    out = tmp_path / "out"
    argv = ["--measurements", str(_csv(tmp_path / "m.csv", rows)), "--out", str(out)]
    if age is not None:
        argv += ["--age", age]
    assert personal_report.main(argv) == skillkit.EXIT_INPUT_PROBLEM
    text = (out / "report.md").read_text(encoding="utf-8")
    assert text.splitlines()[0] == f"# {TITLE}"
    assert "## 论文卡片" in text
    assert "输入没有通过检查，所以年龄差不算" in text and reason in text
    assert "年龄差 " not in text.split("## 输入没有通过检查")[1]
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
    assert json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert _result(out)["age_estimate_error"]["value"] is None


def test_a_good_run_clears_old_problems(tmp_path: Path):
    out = tmp_path / "out"
    bad = _csv(tmp_path / "bad.csv", [("age_estimate", "78", "%")])
    assert personal_report.main(["--measurements", str(bad), "--age", "70", "--out", str(out)]) == skillkit.EXIT_INPUT_PROBLEM
    good = _csv(tmp_path / "good.csv", [("age_estimate", "78", "")])
    assert personal_report.main(["--measurements", str(good), "--age", "70", "--out", str(out)]) == 0
    assert not (out / "problems.json").exists()
