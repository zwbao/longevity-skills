"""Navy circumference body fat against the reports' own Appendix A tables, and the waist cut-offs.

Expected body-fat values are cells of the "PERCENT FAT ESTIMATION" tables printed
in Hodgdon & Beckett 1984 (men: Report 84-11 p. 20; women: Report 84-29 p. 19),
whole numbers in inches. The printed cm equations reproduce every checked men's
cell after rounding; the women's table agrees within rounding in the 15-40 %BF
band but runs up to about 1.8 points lower than the printed equation below
10 %BF (see references/contract.md), so women are tested in that band.
Cut-offs come from WHO 2008 Annex Table A1, WS/T 428-2013 Table 2 and the 0.5
waist-to-height boundary (Ashwell & Hsieh 2005; Browning et al. 2010).
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
from presets import (CM_PER_INCH, CN_LABELS, DERIVATION, MEN, MEN_TABLE_CELLS, SIRI, WHR_CUTOFF, WHTR_BOUNDARY, WOMEN,
                     WOMEN_TABLE_CELLS, WOMEN_TABLE_LEAN_CELL)

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
    assert (MEN["a"], MEN["b"], MEN["c"]) == (0.19077, 0.15456, 1.0324)
    assert (WOMEN["a"], WOMEN["b"], WOMEN["c"]) == (0.35004, 0.22100, 1.29579)
    assert SIRI == (4.95, 4.50)
    assert DERIVATION["male"]["n"] == 602 and DERIVATION["female"]["n"] == 214
    assert (WHTR_BOUNDARY, WHR_CUTOFF["male"], WHR_CUTOFF["female"]) == (0.5, 0.90, 0.85)


@pytest.mark.parametrize("cell", sorted(MEN_TABLE_CELLS))
def test_men_appendix_table(cell):
    value, height = cell
    # Circumference value = abdomen II - neck (inches); pick neck 15 in so abdomen = value + 15.
    neck = 15.0
    fat = pr.body_fat("male", (value + neck) * CM_PER_INCH, neck * CM_PER_INCH, height * CM_PER_INCH)
    assert round(fat) == MEN_TABLE_CELLS[cell]
    assert fat == pytest.approx(MEN_TABLE_CELLS[cell], abs=0.5)


@pytest.mark.parametrize("cell", sorted(WOMEN_TABLE_CELLS))
def test_women_appendix_table_mid_band(cell):
    value, height = cell
    # Circumference value = abdomen I + hip - neck (inches); pick neck 13 in and hip 38 in.
    neck, hip = 13.0, 38.0
    waist = value - hip + neck
    fat = pr.body_fat("female", waist * CM_PER_INCH, neck * CM_PER_INCH, height * CM_PER_INCH, hip * CM_PER_INCH)
    assert fat == pytest.approx(WOMEN_TABLE_CELLS[cell], abs=0.5)


def test_women_table_runs_low_for_lean_women():
    # Why women are tested only in the mid band: the printed table sits below the printed equation when lean.
    (value, height), printed = WOMEN_TABLE_LEAN_CELL
    neck, hip = 13.0, 38.0
    waist = value - hip + neck
    fat = pr.body_fat("female", waist * CM_PER_INCH, neck * CM_PER_INCH, height * CM_PER_INCH, hip * CM_PER_INCH)
    assert printed + 1 < fat < printed + 2


def test_inches_and_centimetres_give_the_same_report(tmp_path: Path):
    inch = [("身高", "68", "in"), ("颈围", "15", "in"), ("腰围", "35", "in")]
    cm = [("身高", str(68 * 2.54), "cm"), ("颈围", str(15 * 2.54), "cm"), ("腰围", str(35 * 2.54), "cm")]
    code, r_in, report, _ = _run(tmp_path, inch, name="inch")
    code2, r_cm, _, _ = _run(tmp_path, cm, name="cm")
    assert code == code2 == 0
    assert r_in["body_fat_pct"]["value"] == pytest.approx(r_cm["body_fat_pct"]["value"])
    assert round(r_in["body_fat_pct"]["value"]) == MEN_TABLE_CELLS[(20.0, 68.0)]  # 35 - 15 = 20 in, 68 in
    assert "## 论文卡片" in report and "边界:" in report and "doi.org/10.1017/S0954422410000144" in report
    assert "中国成人" in report and "3.52" in report


def test_women_need_hip_for_body_fat(tmp_path: Path):
    code, result, report, _ = _run(tmp_path, [("身高", "160", "cm"), ("颈围", "32", "cm"), ("腰围", "76", "cm")], sex="female")
    assert code == 0
    assert result["body_fat_pct"]["value"] is None
    assert "缺臀围" in report
    assert result["waist_height_ratio"]["value"] == pytest.approx(76 / 160)
    assert result["waist_hip_ratio"]["value"] is None
    assert result["central_obesity_cn"]["value"] == CN_LABELS[0]


@pytest.mark.parametrize("ratio,expected", [(0.499, "低于 0.5"), (0.5, "0.5 及以上"), (0.62, "0.5 及以上")])
def test_whtr_boundary(ratio, expected):
    assert pr.whtr_category(ratio) == expected


@pytest.mark.parametrize("sex,ratio,expected", [("male", 0.899, "低于切点"), ("male", 0.90, "达到切点"),
                                                ("female", 0.849, "低于切点"), ("female", 0.85, "达到切点")])
def test_who_whr_table_a1(sex, ratio, expected):
    assert pr.whr_category(ratio, sex) == expected


@pytest.mark.parametrize("sex,waist,expected", [("male", 84.9, 0), ("male", 85, 1), ("male", 89.9, 1), ("male", 90, 2),
                                                ("female", 79.9, 0), ("female", 80, 1), ("female", 84.9, 1), ("female", 85, 2)])
def test_ws_t_428_table2(sex, waist, expected):
    assert pr.central_obesity_cn(waist, sex) == CN_LABELS[expected]


def test_flags_and_advice_when_over_cutoffs(tmp_path: Path):
    rows = [("身高", "170", "cm"), ("颈围", "40", "cm"), ("腰围", "95", "cm"), ("臀围", "100", "cm")]
    code, result, report, _ = _run(tmp_path, rows, age="45")
    assert code == 0
    assert result["central_obesity_cn"]["value"] == "中心型肥胖"
    assert result["waist_hip_category"]["value"] == "达到切点"
    assert result["waist_height_category"]["value"] == "0.5 及以上"
    assert "提示腹部脂肪偏多" in report and "医生" in report
    assert "你患有" not in report


def test_all_below_cutoffs_is_good_news(tmp_path: Path):
    rows = [("身高", "175", "cm"), ("颈围", "37", "cm"), ("腰围", "78", "cm"), ("臀围", "95", "cm")]
    code, result, report, _ = _run(tmp_path, rows, age="30")
    assert code == 0
    assert result["central_obesity_cn"]["value"] == "未达切点"
    assert "好的信号" in report
    assert 0 < result["body_fat_pct"]["value"] < 40


def test_age_outside_derivation_is_noted(tmp_path: Path):
    rows = [("身高", "160", "cm"), ("颈围", "32", "cm"), ("腰围", "76", "cm"), ("臀围", "96", "cm")]
    code, _, report, _ = _run(tmp_path, rows, sex="female", age="60")
    assert code == 0 and "18–44" in report and "不在" in report


def test_waist_in_inches_without_unit_is_caught(tmp_path: Path):
    code, result, _, out = _run(tmp_path, [("腰围", "34", "")])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert problems[0]["key"] == "waist_cm" and problems[0]["kind"] == "range" and "单位是 in" in problems[0]["message_zh"]
    assert all(item["value"] is None for item in result.values())


def test_height_in_metres_without_unit_is_caught(tmp_path: Path):
    code, _, _, out = _run(tmp_path, [("身高", "1.72", ""), ("腰围", "80", "cm")])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert problems[0]["key"] == "height_cm" and "单位是 m，" in problems[0]["message_zh"]


def test_unknown_unit_and_missing_waist_are_refused(tmp_path: Path):
    code, _, _, out = _run(tmp_path, [("腰围", "80", "ft")])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    code2, _, _, out2 = _run(tmp_path, [("身高", "170", "cm")], name="nowaist")
    assert code2 == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out2 / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert ("waist_cm", "missing") in {(p["key"], p["kind"]) for p in problems}


@pytest.mark.parametrize("sex,age,key", [(None, None, "sex"), ("x", None, "sex"), ("male", "16", "age")])
def test_missing_sex_and_minors_are_refused(tmp_path: Path, sex, age, key):
    code, _, _, out = _run(tmp_path, [("腰围", "80", "cm")], sex=sex, age=age)
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert key in {p["key"] for p in problems}


def test_impossible_neck_is_not_computed(tmp_path: Path):
    code, result, report, _ = _run(tmp_path, [("身高", "170", "cm"), ("颈围", "60", "cm"), ("腰围", "58", "cm")])
    assert code == 0
    assert result["body_fat_pct"]["value"] is None and "核对" in report


def test_manifest_matches_script():
    keys = [item["key"] for item in MANIFEST["inputs"]]
    assert keys == ["waist_cm", "hip_cm", "neck_cm", "height_cm", "sex", "age"]
    for key in ("waist_cm", "hip_cm", "neck_cm", "height_cm"):
        spec = skillkit.spec_by_key(MANIFEST, key)
        assert spec["unit"] == "cm" and spec["accept"]["in"] == CM_PER_INCH
    assert MANIFEST["population"]["age_years"] == [DERIVATION["male"]["ages"][0], DERIVATION["male"]["ages"][1]]
    assert MANIFEST["inputs_status"] == "verified"
    assert [o["key"] for o in MANIFEST["outputs"]] == ["body_fat_pct", "waist_height_ratio", "waist_height_category",
                                                      "waist_hip_ratio", "waist_hip_category", "central_obesity_cn"]
