"""SKILLCOURT cutoffs against Giesche et al., GeroScience 2026 (doi:10.1007/s11357-026-02477-4).

Expected constants are quoted from Results, "Discrimination analyses": the exploratory
cutoffs 28.6 s (Random Star Run; unadjusted AUC 0.66, 55% sensitivity, 76% specificity),
0.62 s and 0.88 s (simple and choice stepping reaction; unadjusted AUC 0.63 and 0.61).
The paper prints no individual worked example, so these tests check the constants and
the side-of-cutoff logic only (validation stays draft). All inputs are synthetic.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report as pr
import skillkit
from presets import ADJUSTED, COHORT, CUTOFFS, SIDE_ABOVE, SIDE_BELOW

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))


def _run(tmp_path: Path, rows, age=None, name="out"):
    m = tmp_path / f"{name}.csv"
    m.write_text("\n".join(["item,value,unit"] + [",".join(r) for r in rows]) + "\n", encoding="utf-8")
    out = tmp_path / name
    args = ["--measurements", str(m), "--out", str(out)]
    if age is not None:
        args += ["--age", age]
    code = pr.main(args)
    result = json.loads((out / "result.json").read_text(encoding="utf-8"))["outputs"]
    report = (out / "report.md").read_text(encoding="utf-8")
    return code, result, report, out


def test_constants_are_as_printed():
    rsr = CUTOFFS["random_star_run_s"]
    assert (rsr["cutoff_s"], rsr["unadjusted_auc"], rsr["sensitivity_pct"], rsr["specificity_pct"]) == (28.6, 0.66, 55, 76)
    assert CUTOFFS["skillcourt_simple_reaction_s"]["cutoff_s"] == 0.62
    assert CUTOFFS["skillcourt_choice_reaction_s"]["cutoff_s"] == 0.88
    assert CUTOFFS["skillcourt_simple_reaction_s"]["unadjusted_auc"] == 0.63
    assert CUTOFFS["skillcourt_choice_reaction_s"]["unadjusted_auc"] == 0.61
    assert ADJUSTED["random_star_run_s"] == {"or_per_sd": 1.82, "auc": 0.73, "sensitivity_pct": 70, "specificity_pct": 71}
    assert ADJUSTED["skillcourt_simple_reaction_s"] == {"or_per_sd": 1.58, "auc": 0.72, "sensitivity_pct": 63, "specificity_pct": 75}
    assert (COHORT["n"], COHORT["fallers"], COHORT["non_fallers"], COHORT["rsr_n"]) == (231, 103, 128, 172)


@pytest.mark.parametrize("key,value,above", [
    ("random_star_run_s", 28.5, False), ("random_star_run_s", 28.6, True), ("random_star_run_s", 35.0, True),
    ("skillcourt_simple_reaction_s", 0.61, False), ("skillcourt_simple_reaction_s", 0.62, True),
    ("skillcourt_choice_reaction_s", 0.87, False), ("skillcourt_choice_reaction_s", 0.88, True),
])
def test_side_of_cutoff(key, value, above):
    assert pr.assess({key: value})[key] is above


def test_all_three_inputs(tmp_path: Path):
    rows = [("Random Star Run", "31.2", "s"), ("简单踏步反应时间", "0.58", "s"), ("SKILLCOURT CRT", "0.91", "s")]
    code, result, report, _ = _run(tmp_path, rows, age="72")
    assert code == 0
    assert result["random_star_run_side"]["value"] == SIDE_ABOVE
    assert result["simple_reaction_side"]["value"] == SIDE_BELOW
    assert result["choice_reaction_side"]["value"] == SIDE_ABOVE
    assert result["tests_at_or_above_cutoff"]["value"] == 2
    assert "28.6 秒" in report and "灵敏度 55%，特异度 76%" in report
    assert "## 论文卡片" in report and "边界:" in report and "10.1007/s11357-026-02477-4" in report


def test_single_input_and_ms(tmp_path: Path):
    code, result, report, _ = _run(tmp_path, [("RSR", "25400", "ms")])
    assert code == 0
    assert result["random_star_run_side"]["value"] == SIDE_BELOW
    assert result["simple_reaction_side"]["value"] is None
    assert result["tests_at_or_above_cutoff"]["value"] == 0
    assert "没有提供，不对照" in report and "25.4 秒" in report


def test_under_60_is_noted(tmp_path: Path):
    code, _, report, _ = _run(tmp_path, [("随机星形跑", "27", "s")], age="50")
    assert code == 0 and "不在论文人群" in report


def test_ms_without_unit_is_out_of_range(tmp_path: Path):
    code, result, _, out = _run(tmp_path, [("SC SRT", "620", "")])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert problems[0]["key"] == "skillcourt_simple_reaction_s" and problems[0]["kind"] == "range"
    assert all(item["value"] is None for item in result.values())


def test_wrong_unit_is_refused(tmp_path: Path):
    code, _, _, _ = _run(tmp_path, [("RSR", "0.5", "min")])
    assert code == skillkit.EXIT_INPUT_PROBLEM


def test_nothing_given_is_refused(tmp_path: Path):
    code, result, report, out = _run(tmp_path, [("TUG", "9.1", "s")])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert problems[0]["kind"] == "missing"
    assert result["tests_at_or_above_cutoff"]["value"] is None
    assert "至少提供" in report


def test_manifest_matches_script():
    keys = [item["key"] for item in MANIFEST["inputs"]]
    assert keys == list(CUTOFFS) + ["age"]
    for key in CUTOFFS:
        spec = skillkit.spec_by_key(MANIFEST, key)
        assert spec["unit"] == "s" and spec["accept"] == {"ms": 0.001}
        lo, hi = spec["range"]
        assert lo < CUTOFFS[key]["cutoff_s"] < hi
    assert MANIFEST["population"]["age_years"][0] == COHORT["min_age"]
    assert MANIFEST["inputs_status"] == "verified"
    assert MANIFEST["validation"]["status"] == "draft"
    assert [o["key"] for o in MANIFEST["outputs"]] == [s["output"] for s in CUTOFFS.values()] + ["tests_at_or_above_cutoff"]
