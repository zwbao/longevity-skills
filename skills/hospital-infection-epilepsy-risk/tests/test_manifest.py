"""skill.json inputs match the script, and a wrong input stops the lookup.

Before the kit, a negative number of years was put in the first window, a
cohort the paper does not have was silently read as UK Biobank, and text or a
unit after the number ("两年", "18,mo") crashed with a traceback, so months
could not be given at all.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report
import skillkit
from presets import BOUNDARY, SITES, WINDOWS

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))
# Keys build() reads from the measurement rows.
SCRIPT_KEYS = ["years", "site", "cohort", "cvd_prs", "cvd_score", "cvd_history"]


def _csv(path: Path, rows, header=None) -> Path:
    header = header or ",".join(MANIFEST["entry"]["measurements_header"])
    path.write_text("\n".join([header] + [",".join(row) for row in rows]) + "\n", encoding="utf-8")
    return path


def _before(measurements: Path, age=None) -> str:
    """The report the unchanged loader, build() and render() write."""
    values = personal_report.load_measurements(measurements)
    list_lines, notes, intro = personal_report.build(values, age)
    text = personal_report.render(list_lines, notes, [], [], intro)
    return personal_report._with_paper_card(text)


def _result(out: Path) -> dict:
    result = json.loads((out / "result.json").read_text(encoding="utf-8"))
    assert result["skill"] == "hospital-infection-epilepsy-risk"
    return result["outputs"]


def test_manifest_matches_script():
    specs = skillkit.input_specs(MANIFEST)
    assert [spec["key"] for spec in specs] == SCRIPT_KEYS
    assert tuple(spec["key"] for spec in specs if "unit" not in spec) == personal_report.TEXT_KEYS
    years = skillkit.spec_by_key(MANIFEST, "years")
    assert years["unit"] == "a" and skillkit.unit_factor(years, "mo") * 12 == 1.0
    for cohort in WINDOWS:
        assert cohort in skillkit.spec_by_key(MANIFEST, "cohort")["note_zh"]
    sites = {site for per_cohort in SITES.values() for site in per_cohort}
    assert all(site in skillkit.spec_by_key(MANIFEST, "site")["note_zh"] for site in sites)
    assert not any(spec["required"] for spec in MANIFEST["inputs"])
    age = skillkit.spec_by_key(MANIFEST, "age")
    assert (age["from"], age["flag"], age["unit"]) == ("profile", "--age", "a")
    assert MANIFEST["inputs_status"] == "verified"
    entry = MANIFEST["entry"]
    assert (entry["measurements_flag"], entry["age_flag"], entry["result_json"]) == ("--measurements", "--age", True)
    assert personal_report.has_header(",".join(entry["measurements_header"]))
    assert [item["key"] for item in MANIFEST["outputs"]] == ["infection_window"]


@pytest.mark.parametrize(
    "text, window",
    [
        ("name,value\ncohort,ukb\nyears,2\nsite,pneumonia\n", ">1-3"),
        ("name,value\ncohort,sweden\nyears,0.5\nsite,cns\ncvd_history,有\n", "<1"),
        ("name,value\nyears,1\n", ">1-3"),
        ("name,value\nyears,10\n", ">5-10"),
        ("name,value\nyears,12\nsite,viral\n", ">10"),
        ("name,value\ncohort,sweden\nsite,viral\n", None),
        ("name,value\ncohort,ukb\ncvd_score,high\ncvd_prs,高\n", None),
        ("years,4\nsite,bacterial\n", ">3-5"),
    ],
    ids=["ukb-pneumonia", "sweden-cns", "exactly-1", "exactly-10", "over-10", "site-without-ratio", "joint", "no-header"],
)
def test_documented_files_give_the_same_report(tmp_path: Path, text, window):
    measurements = tmp_path / "m.csv"
    measurements.write_text(text, encoding="utf-8")
    out = tmp_path / "out"
    assert personal_report.main(["--measurements", str(measurements), "--out", str(out)]) == 0
    assert (out / "report.md").read_text(encoding="utf-8") == _before(measurements)
    values = personal_report.load_measurements(measurements)
    expected = personal_report.window_key(float(values["years"])) if "years" in values else None
    assert _result(out)["infection_window"]["value"] == window == expected
    assert not (out / "problems.json").exists()


def test_months_other_names_and_age(tmp_path: Path):
    rows = [("感染距今年数", "18", "mo"), ("感染部位", "pneumonia", ""), ("对照的队列", "ukb", "")]
    out = tmp_path / "out"
    code = personal_report.main(["--measurements", str(_csv(tmp_path / "m.csv", rows)), "--age", "60", "--out", str(out)])
    assert code == 0
    old = tmp_path / "old.csv"
    old.write_text("name,value\nyears,1.5\nsite,pneumonia\ncohort,ukb\n", encoding="utf-8")
    assert (out / "report.md").read_text(encoding="utf-8") == _before(old, 60)
    assert _result(out)["infection_window"]["value"] == ">1-3"


@pytest.mark.parametrize(
    "rows, age, reason",
    [
        ([("years", "-1", "")], None, "不在合理范围"),
        ([("years", "2", "%")], None, "不能换算"),
        ([("years", "两年", "")], None, "不是一个可以计算的数"),
        ([("years", "2", ""), ("感染距今年数", "3", "")], None, "出现了两次"),
        ([("years", "2", ""), ("cohort", "china", "")], None, "只收 ukb、sweden"),
        ([("site", "cns", ""), ("site", "pneumonia", "")], None, "出现了两次"),
        ([("years", "2", "")], "400", "实足年龄"),
    ],
    ids=["negative", "unit", "text", "duplicate-years", "cohort", "duplicate-site", "age"],
)
def test_wrong_input_is_refused(tmp_path: Path, rows, age, reason):
    out = tmp_path / "out"
    argv = ["--measurements", str(_csv(tmp_path / "m.csv", rows)), "--out", str(out)] + (["--age", age] if age else [])
    assert personal_report.main(argv) == skillkit.EXIT_INPUT_PROBLEM
    text = (out / "report.md").read_text(encoding="utf-8")
    assert text.splitlines()[0] == "# 感染与晚年癫痫"
    assert "## 论文卡片" in text
    assert "输入没有通过检查，所以这次没有对照论文里的比值比" in text and reason in text
    assert "## 方法算出的名单" not in text and "比值比是" not in text
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
    assert json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert _result(out)["infection_window"]["value"] is None


def test_nothing_given_is_not_a_problem(tmp_path: Path):
    out = tmp_path / "out"
    assert personal_report.main(["--out", str(out)]) == 0
    assert "这次没有给出感染距指数日的年数" in (out / "report.md").read_text(encoding="utf-8")
    assert _result(out)["infection_window"]["value"] is None
    assert not (out / "problems.json").exists()
