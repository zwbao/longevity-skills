"""PHDI scoring against Supplementary Table 1 of Diez-Echave et al., J Gerontol A 2026 (Seniors-ENRICA).

Every cutoff and weight is checked against Supplementary Table 1 as printed.
The paper prints the score range ("The total PHDI score ranged from 0 to 140")
but no individual intake with its PHDI, so validation stays draft. Intermediate
expectations below are hand arithmetic from the printed cutoffs (proportional
scoring, Methods); all intakes are synthetic.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report as pr
import skillkit
from presets import COHORT_PHDI, COMPONENTS, PHDI_MAX, TABLE2_MODEL3, WHOLE_GRAIN_MAX

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))

# Intakes at or beyond every 10-point cutoff, and at or beyond every 0-point cutoff.
BEST = {"whole_grains_g_d": 90, "tubers_g_d": 50, "vegetables_g_d": 300, "fruit_g_d": 200, "dairy_g_d": 250,
        "red_meat_g_d": 14, "poultry_g_d": 29, "eggs_g_d": 13, "fish_g_d": 28, "nuts_g_d": 50, "legumes_g_d": 100,
        "soy_g_d": 50, "unsat_oil_pct_energy": 21, "sat_fat_pct_energy": 0, "added_sugar_pct_energy": 5}
WORST = {"whole_grains_g_d": 0, "tubers_g_d": 200, "vegetables_g_d": 0, "fruit_g_d": 0, "dairy_g_d": 1000,
         "red_meat_g_d": 100, "poultry_g_d": 100, "eggs_g_d": 120, "fish_g_d": 0, "nuts_g_d": 0, "legumes_g_d": 0,
         "soy_g_d": 0, "unsat_oil_pct_energy": 3.5, "sat_fat_pct_energy": 10, "added_sugar_pct_energy": 25}


def _csv(path: Path, values: dict, units: bool = True) -> Path:
    rows = ["item,value,unit"]
    for key, value in values.items():
        rows.append(f"{key},{value},{COMPONENTS[key][2] if units else ''}" if isinstance(value, (int, float)) else f"{key},{value}")
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")
    return path


def _run(tmp_path: Path, values: dict, sex="female", age=None, name="out", targets=None, raw_rows=None):
    m = tmp_path / f"{name}.csv"
    if raw_rows is not None:
        m.write_text("\n".join(["item,value,unit"] + raw_rows) + "\n", encoding="utf-8")
    else:
        _csv(m, values)
    out = tmp_path / name
    args = ["--measurements", str(m), "--out", str(out)]
    if sex is not None:
        args += ["--sex", sex]
    if age is not None:
        args += ["--age", age]
    if targets is not None:
        args += ["--targets", str(_csv(tmp_path / f"{name}_targets.csv", targets))]
    code = pr.main(args)
    result = json.loads((out / "result.json").read_text(encoding="utf-8"))["outputs"]
    report = (out / "report.md").read_text(encoding="utf-8")
    return code, result, report, out


def test_cutoffs_are_supplementary_table_1():
    # (intake scoring 0, intake scoring 10, weight), Supplementary Table 1 rows 1-15.
    printed = {
        "whole_grains_g_d": (0, None, 1), "tubers_g_d": (200, 50, 1), "vegetables_g_d": (0, 300, 1),
        "fruit_g_d": (0, 200, 1), "dairy_g_d": (1000, 250, 1), "red_meat_g_d": (100, 14, 1),
        "poultry_g_d": (100, 29, 1), "eggs_g_d": (120, 13, 1), "fish_g_d": (0, 28, 1), "nuts_g_d": (0, 50, 1),
        "legumes_g_d": (0, 100, 0.5), "soy_g_d": (0, 50, 0.5), "unsat_oil_pct_energy": (3.5, 21, 1),
        "sat_fat_pct_energy": (10, 0, 1), "added_sugar_pct_energy": (25, 5, 1),
    }
    assert list(COMPONENTS) == list(printed)
    assert [row[0] for row in COMPONENTS.values()] == list(range(1, 16))
    for key, (zero, ten, weight) in printed.items():
        assert COMPONENTS[key][3:] == (zero, ten, weight)
    assert WHOLE_GRAIN_MAX == {"female": 75, "male": 90}


def test_score_range_is_0_to_140():
    # Methods: "The total PHDI score ranged from 0 to 140".
    assert PHDI_MAX == 140
    for sex in ("female", "male"):
        assert pr.phdi(BEST, sex)["total"] == pytest.approx(140)
        assert pr.phdi(WORST, sex)["total"] == pytest.approx(0)
    assert pr.component_max("legumes_g_d") == 5 and pr.component_max("soy_g_d") == 5


@pytest.mark.parametrize("key,intake,points", [
    ("vegetables_g_d", 150, 5.0),          # halfway 0 -> 300
    ("vegetables_g_d", 600, 10.0),         # capped above 300
    ("tubers_g_d", 125, 5.0),              # halfway 200 -> 50
    ("tubers_g_d", 20, 10.0),              # below 50 is full score
    ("dairy_g_d", 625, 5.0),               # halfway 1000 -> 250
    ("red_meat_g_d", 57, 5.0),             # halfway 100 -> 14
    ("legumes_g_d", 50, 2.5),              # weight 0.5
    ("soy_g_d", 25, 2.5),
    ("unsat_oil_pct_energy", 12.25, 5.0),  # halfway 3.5 -> 21 % TEI
    ("sat_fat_pct_energy", 5, 5.0),
    ("added_sugar_pct_energy", 15, 5.0),
    ("added_sugar_pct_energy", 30, 0.0),
])
def test_proportional_scoring(key, intake, points):
    assert pr.component_score(key, intake, "female") == pytest.approx(points)


def test_whole_grain_cutoff_is_sex_specific():
    assert pr.component_score("whole_grains_g_d", 75, "female") == pytest.approx(10)
    assert pr.component_score("whole_grains_g_d", 75, "male") == pytest.approx(10 * 75 / 90)
    assert pr.component_score("whole_grains_g_d", 45, "male") == pytest.approx(5)


def test_full_report(tmp_path: Path):
    values = dict(BEST, vegetables_g_d=150, legumes_g_d=50, added_sugar_pct_energy=15)
    code, result, report, out = _run(tmp_path, values, sex="女", age="70")
    assert code == 0
    # 140 - 5 (vegetables) - 2.5 (legumes) - 5 (sugar)
    assert result["phdi_total"]["value"] == pytest.approx(127.5)
    assert result["score_vegetables_g_d"]["value"] == pytest.approx(5.0)
    assert "## 论文卡片" in report and "10.1093/gerona/glag244" in report and "边界:" in report
    assert "0.52（95% 置信区间 0.38–0.70）" in report and "0.62（95% 置信区间 0.49–0.79）" in report
    assert "不判断你落在哪一个三分位" in report
    assert report.index("## 论文卡片") < report.index("## 结果")
    lev = json.loads((out / "levers.json").read_text(encoding="utf-8"))
    veg = next(item for item in lev["sensitivity"] if item["key"] == "vegetables_g_d")
    assert veg["points_per_unit"] == pytest.approx(10 / 300)
    fish = next(item for item in lev["sensitivity"] if item["key"] == "fish_g_d")
    assert fish["points_per_unit"] == 0


def test_targets_write_levers(tmp_path: Path):
    values = dict(BEST, vegetables_g_d=150, red_meat_g_d=100)
    code, result, _, out = _run(tmp_path, values, sex="male", targets={"vegetables_g_d": 300, "red_meat_g_d": 57})
    assert code == 0 and result["phdi_total"]["value"] == pytest.approx(125)
    lev = json.loads((out / "levers.json").read_text(encoding="utf-8"))
    deltas = {item["key"]: item["phdi_delta"] for item in lev["levers"]}
    assert deltas == pytest.approx({"vegetables_g_d": 5.0, "red_meat_g_d": 5.0})
    assert lev["targets"]["phdi_total"] == pytest.approx(135)


def test_under_60_is_noted(tmp_path: Path):
    code, _, report, _ = _run(tmp_path, BEST, sex="male", age="45")
    assert code == 0 and "不在论文人群" in report


def test_chinese_names_are_read(tmp_path: Path):
    rows = ["全谷物,75,g/d", "薯类,50,g/d", "蔬菜,300,g/d", "水果,200,g/d", "奶类,250,g/d", "红肉,14,g/d",
            "禽肉,29,g/d", "蛋类,13,g/d", "鱼和贝类,28,g/d", "坚果,50,g/d", "杂豆,100,g/d", "大豆和豆制品,50,g/d",
            "不饱和植物油,21,%", "饱和脂肪,0,%", "添加糖,0.05,1"]
    code, result, _, _ = _run(tmp_path, {}, sex="F", raw_rows=rows)
    assert code == 0 and result["phdi_total"]["value"] == pytest.approx(140)


def test_grams_for_fat_without_unit_are_refused(tmp_path: Path):
    # 40 g of oil written as a bare number under a Chinese name must state its unit (% of energy).
    rows = [f"{key},{value},{COMPONENTS[key][2]}" for key, value in BEST.items() if key != "unsat_oil_pct_energy"]
    rows.append("植物油,40,")
    code, result, report, out = _run(tmp_path, {}, raw_rows=rows)
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert problems[0]["key"] == "unsat_oil_pct_energy"
    assert all(item["value"] is None for item in result.values())
    assert "PHDI：**" not in report


def test_out_of_range_and_wrong_unit_are_refused(tmp_path: Path):
    code, result, _, out = _run(tmp_path, dict(BEST, eggs_g_d=5000))
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert ("eggs_g_d", "range") in {(p["key"], p["kind"]) for p in problems}
    assert result["phdi_total"]["value"] is None
    rows = [f"{key},{value},{COMPONENTS[key][2]}" for key, value in BEST.items() if key != "fish_g_d"] + ["fish_g_d,200,g/wk"]
    code2, _, _, _ = _run(tmp_path, {}, raw_rows=rows, name="unit")
    assert code2 == skillkit.EXIT_INPUT_PROBLEM


def test_missing_component_and_sex_are_refused(tmp_path: Path):
    partial = {k: v for k, v in BEST.items() if k != "nuts_g_d"}
    code, _, _, out = _run(tmp_path, partial)
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert ("nuts_g_d", "missing") in {(p["key"], p["kind"]) for p in problems}
    code2, _, _, out2 = _run(tmp_path, BEST, sex=None, name="nosex")
    assert code2 == skillkit.EXIT_INPUT_PROBLEM
    assert any(p["key"] == "sex" for p in json.loads((out2 / "problems.json").read_text(encoding="utf-8"))["problems"])


def test_cohort_numbers_are_as_printed():
    # Table 1 and Table 2 (Model 3).
    assert COHORT_PHDI["Seniors-ENRICA-1"]["tertile_means"] == (79.5, 90.8, 102.2)
    assert COHORT_PHDI["Seniors-ENRICA-2"]["tertile_means"] == (83.5, 93.3, 103.5)
    assert TABLE2_MODEL3["Seniors-ENRICA-1"]["t3"] == (0.62, 0.42, 0.92)
    assert TABLE2_MODEL3["Seniors-ENRICA-2"]["t3"] == (0.40, 0.24, 0.65)
    assert TABLE2_MODEL3["pooled"]["t3"] == (0.52, 0.38, 0.70)


def test_manifest_matches_script():
    keys = [item["key"] for item in MANIFEST["inputs"]]
    assert keys == list(COMPONENTS) + ["sex", "age"]
    for key, row in COMPONENTS.items():
        spec = skillkit.spec_by_key(MANIFEST, key)
        assert spec["unit"] == row[2] and spec["required"] is True and spec["range"][0] == 0
        assert spec.get("unit_required", False) == (row[2] == "%")
    assert [o["key"] for o in MANIFEST["outputs"]] == ["phdi_total"] + [f"score_{k}" for k in COMPONENTS]
    assert MANIFEST["inputs_status"] == "verified" and MANIFEST["validation"]["status"] == "draft"
    assert MANIFEST["entry"]["targets_flag"] == "--targets" and MANIFEST["entry"]["levers_json"] is True
