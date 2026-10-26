"""Calf circumference change groups and odds ratios against Zhang et al., JAMA Netw Open 2026 (CLHLS).

Expected odds ratios are the model 4 rows of Table 2 (absolute) and Table 3 (relative)
and the stratified rows of Table 4, as printed. Cut points come from Methods
"CC Measurement". The paper prints no individual worked example, so these tests check
the grouping and the table lookup only (validation stays draft). All inputs are synthetic.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report as pr
import skillkit
from presets import (ABS_CUTS_CM, ABS_LABELS, CC_VALID_CM, COHORT, PER_10PCT, PER_1CM, REL_CUTS_PCT, REL_LABELS,
                     TABLE2_MODEL4, TABLE3_MODEL4, TABLE4_ABS, TABLE4_REL)

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
    assert ABS_CUTS_CM == (3.0, 5.0) and REL_CUTS_PCT == (10.0, 20.0) and CC_VALID_CM == (15.0, 50.0)
    # Table 2, model 4
    assert [row[0] for row in TABLE2_MODEL4] == [1.0, 1.27, 1.32, 1.33]
    assert TABLE2_MODEL4[3] == (1.33, 1.10, 1.60)
    # Table 3, model 4
    assert [row[0] for row in TABLE3_MODEL4] == [1.0, 1.10, 1.26, 1.48]
    assert TABLE3_MODEL4[3] == (1.48, 1.20, 1.84)
    assert PER_1CM == (1.03, 1.02, 1.05) and PER_10PCT == (1.10, 1.06, 1.15)
    # Table 4
    assert TABLE4_ABS["female"][3] == (1.44, 1.11, 1.87) and TABLE4_REL["80plus"][3] == (1.64, 1.23, 2.18)
    assert TABLE4_ABS["male"][1] == (1.08, 0.79, 1.49) and TABLE4_REL["under80"][3] == (1.22, 0.95, 1.56)
    assert (COHORT["n"], COHORT["falls"], COHORT["falls_pct"]) == (7068, 1671, 23.64)


@pytest.mark.parametrize("base,follow,group", [
    (32.0, 32.0, 0), (32.0, 33.5, 0), (32.0, 31.9, 1), (32.0, 29.1, 1), (32.0, 29.0, 2),
    (32.0, 27.1, 2), (32.0, 27.0, 3), (32.0, 22.0, 3),
])
def test_absolute_cut_points(base, follow, group):
    assert pr.absolute_group(pr.absolute_change(base, follow)) == group


@pytest.mark.parametrize("base,follow,group", [
    (30.0, 30.0, 0), (30.0, 31.0, 0), (30.0, 29.9, 1), (30.0, 27.1, 1), (30.0, 27.0, 2),
    (30.0, 24.1, 2), (30.0, 24.0, 3), (30.0, 20.0, 3),
])
def test_relative_cut_points(base, follow, group):
    assert pr.relative_group(pr.relative_change(base, follow)) == group


def test_paper_table2_table3_lookup(tmp_path: Path):
    # 34.0 -> 28.0 cm: absolute decrease 6 cm (>= 5 cm), relative 17.6% (10% to < 20%).
    code, result, report, _ = _run(tmp_path, [("基线小腿围", "34.0", "cm"), ("随访小腿围", "28.0", "cm")])
    assert code == 0
    assert result["calf_change_cm"]["value"] == pytest.approx(-6.0)
    assert result["calf_change_pct"]["value"] == pytest.approx(-17.65, abs=0.01)
    assert result["absolute_category"]["value"] == ABS_LABELS[3]
    assert result["absolute_or"]["value"] == 1.33
    assert result["relative_category"]["value"] == REL_LABELS[2]
    assert result["relative_or"]["value"] == 1.26
    assert "1.10–1.60" in report and "1.05–1.51" in report
    assert "## 论文卡片" in report and "边界:" in report and "10.1001/jamanetworkopen.2026.40127" in report


def test_strata_rows_for_sex_and_age(tmp_path: Path):
    rows = [("calf baseline", "30.0", "cm"), ("calf followup", "23.5", "cm")]  # -6.5 cm, -21.7%
    code, result, report, _ = _run(tmp_path, rows, sex="女", age="85")
    assert code == 0
    assert result["relative_or"]["value"] == 1.48
    assert "表 4 女性" in report and "1.44（95% 置信区间 1.11–1.87）" in report
    assert "表 4 80 岁及以上" in report and "1.64（95% 置信区间 1.23–2.18）" in report


def test_no_decrease_is_reference(tmp_path: Path):
    code, result, report, _ = _run(tmp_path, [("第一次小腿围", "31", "cm"), ("第二次小腿围", "31.4", "cm")])
    assert code == 0
    assert result["absolute_or"]["value"] == 1.0 and result["relative_or"]["value"] == 1.0
    assert "参照组" in report and "好的信号" in report and "你患有" not in report


def test_mm_input_converts(tmp_path: Path):
    code, result, _, _ = _run(tmp_path, [("基线小腿围", "320", "mm"), ("随访小腿围", "300", "mm")])
    assert code == 0 and result["calf_change_cm"]["value"] == pytest.approx(-2.0)


def test_under_60_is_noted(tmp_path: Path):
    code, _, report, _ = _run(tmp_path, [("基线小腿围", "36", "cm"), ("随访小腿围", "35", "cm")], age="50")
    assert code == 0 and "不在论文人群" in report


def test_wrong_unit_is_caught(tmp_path: Path):
    # 13 inches typed without a unit is below the 15 cm floor.
    code, result, _, out = _run(tmp_path, [("基线小腿围", "13", ""), ("随访小腿围", "12", "")])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert problems[0]["key"] == "calf_baseline_cm" and problems[0]["kind"] == "range"
    assert all(item["value"] is None for item in result.values())


def test_unknown_unit_and_missing_value_are_refused(tmp_path: Path):
    code, _, _, _ = _run(tmp_path, [("基线小腿围", "32", "ft"), ("随访小腿围", "30", "cm")])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    code2, _, _, out2 = _run(tmp_path, [("基线小腿围", "32", "cm")], name="nofollow")
    assert code2 == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out2 / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert ("calf_followup_cm", "missing") in {(p["key"], p["kind"]) for p in problems}


def test_bad_sex_is_refused(tmp_path: Path):
    code, _, _, _ = _run(tmp_path, [("基线小腿围", "32", "cm"), ("随访小腿围", "30", "cm")], sex="x")
    assert code == skillkit.EXIT_INPUT_PROBLEM


def test_manifest_matches_script():
    keys = [item["key"] for item in MANIFEST["inputs"]]
    assert keys == ["calf_baseline_cm", "calf_followup_cm", "sex", "age"]
    for key in ("calf_baseline_cm", "calf_followup_cm"):
        spec = skillkit.spec_by_key(MANIFEST, key)
        assert spec["unit"] == "cm" and spec["range"] == list(CC_VALID_CM) and spec["required"] is True
    assert MANIFEST["population"]["age_years"][0] == COHORT["min_age"]
    assert MANIFEST["inputs_status"] == "verified"
    assert MANIFEST["validation"]["status"] == "draft"
    assert [o["key"] for o in MANIFEST["outputs"]] == ["calf_change_cm", "calf_change_pct", "absolute_category",
                                                      "absolute_or", "relative_category", "relative_or"]
