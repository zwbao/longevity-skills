"""Handgrip cut-offs and hazard ratios against Pérez-Sousa et al., GeroScience 2026 (MHAS).

Cut-offs come from Methods "Statistical analysis" (EWGSOP2 < 27 kg men, < 16 kg women;
FNIH < 26 kg men, < 16 kg women). Expected hazard ratios are the rows of Supplementary
Table S3 as printed (three decimals). The paper prints no individual worked example, so
these tests check the grouping and the table lookup only (validation stays draft).
All inputs are synthetic.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report as pr
import skillkit
from presets import COHORT, CUTOFFS_KG, LABELS, PER_SD, S3, S3_SAMPLE

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))


def _csv(path: Path, rows) -> Path:
    path.write_text("\n".join(["item,value,unit"] + [",".join(row) for row in rows]) + "\n", encoding="utf-8")
    return path


def _run(tmp_path: Path, rows, sex="male", age=None, name="out"):
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
    # Methods "Statistical analysis": EWGSOP2 (< 27 kg in men and < 16 kg in women), FNIH (< 26 kg in men and < 16 kg in women).
    assert CUTOFFS_KG == {"ewgsop2": {"male": 27.0, "female": 16.0}, "fnih": {"male": 26.0, "female": 16.0}}
    # Supplementary Table S3.
    assert S3[("ewgsop2", "male")]["model1"] == (2.112, 1.537, 2.901)
    assert S3[("ewgsop2", "male")]["model2"] == (2.302, 1.653, 3.206)
    assert S3[("fnih", "male")]["model1"] == (2.002, 1.449, 2.766)
    assert S3[("fnih", "male")]["model2"] == (2.237, 1.596, 3.136)
    assert S3[("ewgsop2", "female")]["model1"] == (1.531, 1.093, 2.144)
    assert S3[("ewgsop2", "female")]["model2"] == (1.268, 0.893, 1.799)
    assert S3[("ewgsop2", "female")] == S3[("fnih", "female")]
    assert (S3[("ewgsop2", "male")]["n_low"], S3[("ewgsop2", "male")]["deaths_low"]) == (190, 84)
    assert (S3[("fnih", "male")]["n_low"], S3[("fnih", "male")]["deaths_low"]) == (155, 72)
    assert (S3[("ewgsop2", "female")]["n_low"], S3[("ewgsop2", "female")]["deaths_low"]) == (157, 49)
    assert S3_SAMPLE == {"male": (726, 173), "female": (1039, 179)}
    # Abstract / Results.
    assert (COHORT["n"], COHORT["deaths"], COHORT["followup_median_months"]) == (1917, 371, 109)
    assert PER_SD[("absolute", "male")] == (0.53, 0.44, 0.65)
    assert PER_SD[("allometric", "male")] == (0.60, 0.48, 0.75)
    assert PER_SD[("allometric", "female")] == (0.80, 0.68, 0.94)


@pytest.mark.parametrize("sex,grip,ew,fn", [
    ("male", 25.9, True, True), ("male", 26.0, True, False), ("male", 26.9, True, False),
    ("male", 27.0, False, False), ("male", 40.0, False, False),
    ("female", 15.9, True, True), ("female", 16.0, False, False), ("female", 24.0, False, False),
])
def test_cut_points_are_strictly_below(sex, grip, ew, fn):
    assert pr.is_low(grip, sex, "ewgsop2") is ew
    assert pr.is_low(grip, sex, "fnih") is fn


def test_paper_s3_lookup_men_below_both(tmp_path: Path):
    code, result, report, _ = _run(tmp_path, [("握力", "24.5", "kg"), ("身高", "165", "cm")], age="68")
    assert code == 0
    assert result["ewgsop2_category"]["value"] == LABELS[0] and result["fnih_category"]["value"] == LABELS[0]
    assert result["ewgsop2_mortality_hr"]["value"] == 2.302
    assert result["fnih_mortality_hr"]["value"] == 2.237
    assert result["allometric_hgs_kg_m2"]["value"] == pytest.approx(24.5 / 1.65 ** 2, abs=1e-3)
    assert "1.653–3.206" in report and "1.596–3.136" in report and "2.112" in report
    assert "## 论文卡片" in report and "边界:" in report and "10.1007/s11357-026-02639-4" in report


def test_men_between_fnih_and_ewgsop2(tmp_path: Path):
    code, result, report, _ = _run(tmp_path, [("handgrip strength", "26.5", "kg")])
    assert code == 0
    assert result["ewgsop2_mortality_hr"]["value"] == 2.302
    assert result["fnih_mortality_hr"]["value"] == 1.0 and result["fnih_category"]["value"] == LABELS[1]
    assert result["allometric_hgs_kg_m2"]["value"] is None and "没给身高" in report


def test_women_below_16_not_significant_after_adjustment(tmp_path: Path):
    code, result, report, _ = _run(tmp_path, [("握力", "14", "kg")], sex="女", age="72")
    assert code == 0
    assert result["ewgsop2_mortality_hr"]["value"] == 1.268 == result["fnih_mortality_hr"]["value"]
    assert "0.893–1.799" in report and "跨过 1" in report and "1.531" in report


def test_reference_group_is_good_news(tmp_path: Path):
    code, result, report, _ = _run(tmp_path, [("握力", "38", "kg")], age="55")
    assert code == 0
    assert result["ewgsop2_mortality_hr"]["value"] == 1.0 and result["fnih_mortality_hr"]["value"] == 1.0
    assert "参照组" in report and "好的信号" in report and "你患有" not in report


def test_pounds_convert(tmp_path: Path):
    code, result, _, _ = _run(tmp_path, [("grip", "55", "lb")])  # 24.9 kg
    assert code == 0 and result["ewgsop2_mortality_hr"]["value"] == 2.302


def test_under_50_is_noted(tmp_path: Path):
    code, _, report, _ = _run(tmp_path, [("握力", "40", "kg")], age="40")
    assert code == 0 and "不在论文人群" in report


def test_grip_without_unit_is_refused(tmp_path: Path):
    code, result, report, out = _run(tmp_path, [("握力", "60", "")])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert problems[0]["key"] == "grip_kg"
    assert all(item["value"] is None for item in result.values())
    assert "2.302" not in report


def test_out_of_range_grip_is_refused(tmp_path: Path):
    code, result, _, out = _run(tmp_path, [("握力", "250", "kg")])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert problems[0]["key"] == "grip_kg" and problems[0]["kind"] == "range"
    assert all(item["value"] is None for item in result.values())


def test_height_in_metres_without_unit_is_caught(tmp_path: Path):
    code, _, _, out = _run(tmp_path, [("握力", "30", "kg"), ("身高", "1.70", "")])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert problems[0]["key"] == "height_cm"


@pytest.mark.parametrize("sex", [None, "x"])
def test_missing_or_bad_sex_is_refused(tmp_path: Path, sex):
    code, _, _, out = _run(tmp_path, [("握力", "30", "kg")], sex=sex)
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert "sex" in {p["key"] for p in problems}


def test_missing_grip_is_refused(tmp_path: Path):
    code, _, _, out = _run(tmp_path, [("身高", "170", "cm")])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert ("grip_kg", "missing") in {(p["key"], p["kind"]) for p in problems}


def test_manifest_matches_script():
    keys = [item["key"] for item in MANIFEST["inputs"]]
    assert keys == ["grip_kg", "height_cm", "sex", "age"]
    grip = skillkit.spec_by_key(MANIFEST, "grip_kg")
    assert grip["unit"] == "kg" and grip["unit_required"] is True and grip["accept"]["lb"] == 0.45359237
    assert skillkit.spec_by_key(MANIFEST, "height_cm")["unit"] == "cm"
    assert MANIFEST["population"]["age_years"][0] == COHORT["min_age"]
    assert MANIFEST["inputs_status"] == "verified"
    assert MANIFEST["validation"]["status"] == "draft"
    assert [o["key"] for o in MANIFEST["outputs"]] == ["ewgsop2_category", "ewgsop2_mortality_hr", "fnih_category",
                                                      "fnih_mortality_hr", "allometric_hgs_kg_m2"]
