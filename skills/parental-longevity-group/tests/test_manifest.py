"""Parental longevity grouping against Seidu et al., GeroScience 2026 (Gothenburg H70).

The cut-off (85) and the exclusion (a parent who died before 41) are quoted from
Methods, "Definition of the PL groups" and "Study population"; the group sizes from
Results, "Baseline characteristics at age 70". The paper prints no individual worked
example, so these tests check the rules only (validation stays draft). All inputs are
synthetic.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report as pr
import skillkit
from presets import COHORT, EARLY_DEATH_EXCLUSION_YEARS, GROUP_BY_REACHED, SURVIVAL_CUTOFF_YEARS

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))


def _csv(path: Path, rows) -> Path:
    path.write_text("\n".join(["item,value,unit"] + [",".join(row) for row in rows]) + "\n", encoding="utf-8")
    return path


def _run(tmp_path: Path, rows, sex=None, age=None, name="out"):
    m = _csv(tmp_path / f"{name}.csv", rows)
    out = tmp_path / name
    args = ["--measurements", str(m), "--out", str(out)]
    if sex is not None:
        args += ["--sex", sex]
    if age is not None:
        args += ["--age", age]
    code = pr.main(args)
    result = json.loads((out / "result.json").read_text(encoding="utf-8"))["outputs"]
    report = (out / "report.md").read_text(encoding="utf-8")
    return code, result, report, out


def test_constants_are_as_printed():
    # Methods: "surviving to age 85"; "at least one parent died before age 41 years".
    assert SURVIVAL_CUTOFF_YEARS == 85 and EARLY_DEATH_EXCLUSION_YEARS == 41
    assert GROUP_BY_REACHED == {2: "high-PL", 1: "medium-PL", 0: "low-PL"}
    # Results: "17.2% had high-PL (n = 194), 43.3% had medium-PL (n = 488), and 39.4% had low-PL (n = 444)".
    assert (COHORT["n_high"], COHORT["n_medium"], COHORT["n_low"]) == (194, 488, 444)
    assert (COHORT["pct_high"], COHORT["pct_medium"], COHORT["pct_low"]) == (17.2, 43.3, 39.4)
    assert COHORT["n_high"] + COHORT["n_medium"] + COHORT["n_low"] == COHORT["n"] == 1126


@pytest.mark.parametrize("dead,alive,state", [
    (85, None, "reached"), (84.9, None, "not_reached"), (41, None, "not_reached"), (40.9, None, "early"),
    (None, 86, "reached"), (None, 85, "reached"), (None, 80, "pending"),
])
def test_parent_state_boundaries(dead, alive, state):
    assert pr.parent_state(dead, alive) == state


@pytest.mark.parametrize("states,group,status", [
    (["reached", "reached"], "high-PL", "determined"),
    (["reached", "not_reached"], "medium-PL", "determined"),
    (["not_reached", "not_reached"], "low-PL", "determined"),
    (["reached", "pending"], None, "provisional"),
    (["early", "reached"], None, "excluded"),
])
def test_group_rule(states, group, status):
    out = pr.classify(states)
    assert out["group"] == group and out["status"] == status


def test_high_with_living_parent_over_85(tmp_path: Path):
    # Methods: living parents "classified as long-lived, as all were above age 85".
    code, result, report, _ = _run(tmp_path, [("父亲去世时年龄", "88", "岁"), ("母亲目前年龄", "92", "岁")])
    assert code == 0
    assert result["pl_group"]["value"] == "high-PL" and result["pl_status"]["value"] == "determined"
    assert result["parents_reached_85"]["value"] == 2.0
    assert result["parents_mean_age_a"]["value"] == pytest.approx(90.0)
    assert "## 论文卡片" in report and "边界:" in report and "10.1007/s11357-026-02501-7" in report
    assert "pTau217" in report and "FDR" in report


def test_medium_female_gets_interaction_note(tmp_path: Path):
    rows = [("father age at death", "72", "years"), ("mother age at death", "90", "years")]
    code, result, report, _ = _run(tmp_path, rows, sex="女", age="70")
    assert code == 0 and result["pl_group"]["value"] == "medium-PL"
    assert "性别交互" in report
    assert "FDR" not in report  # the FDR caveat concerns high-PL findings only


def test_low_is_reference(tmp_path: Path):
    code, result, report, _ = _run(tmp_path, [("父亲享年", "70", "岁"), ("母亲享年", "84", "岁")])
    assert code == 0 and result["pl_group"]["value"] == "low-PL"
    assert "参照组" in report and "不说明你个人" in report


def test_living_parent_under_85_is_provisional(tmp_path: Path):
    code, result, report, _ = _run(tmp_path, [("父亲去世时年龄", "90", "岁"), ("母亲目前年龄", "78", "岁")], age="50")
    assert code == 0
    assert result["pl_group"]["value"] is None and result["pl_status"]["value"] == "provisional"
    assert result["pl_group_floor"]["value"] == "medium-PL"
    assert "未定" in report and "不一定适用" in report


def test_early_parent_death_is_excluded(tmp_path: Path):
    code, result, report, _ = _run(tmp_path, [("父亲去世时年龄", "35", "岁"), ("母亲去世时年龄", "90", "岁")])
    assert code == 0
    assert result["pl_group"]["value"] is None and result["pl_status"]["value"] == "excluded"
    assert "41 岁前去世" in report


def test_missing_parent_is_refused(tmp_path: Path):
    code, result, _, out = _run(tmp_path, [("父亲去世时年龄", "88", "岁")])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert ("mother_death_age_a", "missing") in {(p["key"], p["kind"]) for p in problems}
    assert all(item["value"] is None for item in result.values())


def test_both_death_and_current_is_refused(tmp_path: Path):
    rows = [("父亲去世时年龄", "88", "岁"), ("父亲目前年龄", "90", "岁"), ("母亲去世时年龄", "80", "岁")]
    code, _, _, out = _run(tmp_path, rows)
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert problems[0]["kind"] == "duplicate"


def test_wrong_unit_and_out_of_range_are_refused(tmp_path: Path):
    # Age typed in months is out of range; an unknown unit is refused.
    code, result, report, _ = _run(tmp_path, [("父亲去世时年龄", "1020", ""), ("母亲去世时年龄", "80", "岁")])
    assert code == skillkit.EXIT_INPUT_PROBLEM and result["pl_group"]["value"] is None and "high-PL" not in report
    code2, _, _, _ = _run(tmp_path, [("父亲去世时年龄", "88", "kg"), ("母亲去世时年龄", "80", "岁")], name="unit")
    assert code2 == skillkit.EXIT_INPUT_PROBLEM


def test_bad_sex_is_refused(tmp_path: Path):
    code, _, _, _ = _run(tmp_path, [("父亲去世时年龄", "88", "岁"), ("母亲去世时年龄", "80", "岁")], sex="x")
    assert code == skillkit.EXIT_INPUT_PROBLEM


def test_report_gives_no_dose_or_medication_advice(tmp_path: Path):
    _, _, report, _ = _run(tmp_path, [("父亲去世时年龄", "88", "岁"), ("母亲去世时年龄", "80", "岁")])
    for word in ("mg", "剂量", "停药", "开始服用"):
        assert word not in report


def test_manifest_matches_script():
    keys = [item["key"] for item in MANIFEST["inputs"]]
    assert keys == ["father_death_age_a", "father_current_age_a", "mother_death_age_a", "mother_current_age_a",
                    "sex", "age"]
    for key in keys[:4]:
        spec = skillkit.spec_by_key(MANIFEST, key)
        assert spec["unit"] == "a" and spec["from"] == "measurements"
    assert MANIFEST["inputs_status"] == "verified"
    assert MANIFEST["validation"]["status"] == "draft"
    assert [o["key"] for o in MANIFEST["outputs"]] == ["pl_group", "pl_status", "pl_group_floor",
                                                      "parents_reached_85", "parents_mean_age_a"]
