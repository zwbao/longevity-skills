"""BIA-ACC operational OSA phenotype: cut-offs as printed in Ilich et al., GeroScience 2026, Methods.

Printed thresholds (section "Anthropometric and bioimpedance measurements"):
T-score >= -1.0 within reference range; < -1.0 and > -2.5 moderately reduced; <= -2.5 markedly
reduced. S-score <= -1.0 reduced. Fat mass >= 25% of body weight in men and >= 32% in women.
OSA = all three at once. The paper prints no individual example (validation is draft).
All inputs below are synthetic.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report as pr
from presets import BONE_LABELS, FAT_PCT_ADIPOSITY, OSA_LABELS, S_REDUCED, STUDY, T_MARKED, T_REFERENCE_LOWER, YES_NO

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))


def _csv(path: Path, rows) -> Path:
    path.write_text("\n".join(["item,value,unit"] + [",".join(row) for row in rows]) + "\n", encoding="utf-8")
    return path


def _run(tmp_path: Path, rows, sex="female", age=None, name="out"):
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
    assert (T_REFERENCE_LOWER, T_MARKED, S_REDUCED) == (-1.0, -2.5, -1.0)
    assert FAT_PCT_ADIPOSITY == {"male": 25.0, "female": 32.0}
    assert (STUDY["n"], STUDY["women"], STUDY["men"]) == (9717, 6412, 3305)


def test_manifest_keys_match_script():
    keys = {spec["key"] for spec in MANIFEST["inputs"]}
    assert {"bia_acc_t_score", "bia_acc_s_score", "body_fat_pct", "sex", "age"} == keys
    units = {spec["key"]: spec.get("unit") for spec in MANIFEST["inputs"]}
    assert units["body_fat_pct"] == "%" and units["bia_acc_t_score"] == "score"
    assert {o["key"] for o in MANIFEST["outputs"]} == set(pr.classify(0, 0, 20, "male"))
    assert MANIFEST["validation"]["status"] == "draft"


@pytest.mark.parametrize("t,expected", [(-1.0, 0), (0.5, 0), (-1.01, 1), (-2.49, 1), (-2.5, 2), (-3.4, 2)])
def test_bone_category_printed_bounds(t, expected):
    assert pr.bone_category(t) == BONE_LABELS[expected]
    assert pr.bone_reduced(t) == (expected > 0)


@pytest.mark.parametrize("s,reduced", [(-1.0, True), (-0.99, False), (-2.1, True), (0.3, False)])
def test_muscle_printed_bound(s, reduced):
    assert pr.muscle_reduced(s) is reduced


@pytest.mark.parametrize("sex,fat,expected", [("male", 25, True), ("male", 24.9, False),
                                              ("female", 32, True), ("female", 31.9, False), ("female", 28, False)])
def test_adiposity_printed_sex_specific(sex, fat, expected):
    assert pr.adiposity(fat, sex) is expected


def test_osa_needs_all_three(tmp_path: Path):
    rows = [("BIA-ACC T-score", "-1.6", ""), ("S-score", "-1.2", ""), ("体脂率", "36", "%")]
    code, result, report, _ = _run(tmp_path, rows, sex="female", age="52")
    assert code == 0
    assert result["bone_category"]["value"] == BONE_LABELS[1]
    assert result["components_met"]["value"] == 3
    assert result["osa_phenotype"]["value"] == OSA_LABELS[1]
    assert "## 论文卡片" in report and "边界:" in report
    assert "不是骨质疏松、肌少症或肥胖的临床诊断" in report
    assert "DXA" in report


def test_same_values_differ_by_sex(tmp_path: Path):
    rows = [("BIA-ACC T-score", "-1.5", ""), ("S-score", "-1.0", ""), ("体脂率", "28", "%")]
    _, men, _, _ = _run(tmp_path, rows, sex="male", name="m")
    _, women, report, _ = _run(tmp_path, rows, sex="female", name="f")
    assert men["osa_phenotype"]["value"] == OSA_LABELS[1]
    assert women["osa_phenotype"]["value"] == OSA_LABELS[0]
    assert women["components_met"]["value"] == 2 and women["adiposity"]["value"] == YES_NO[0]
    assert "越过论文切点" in report


def test_out_of_range_score_stops(tmp_path: Path):
    rows = [("BIA-ACC T-score", "-15", ""), ("S-score", "-1.2", ""), ("体脂率", "36", "%")]
    m = _csv(tmp_path / "bad.csv", rows)
    out = tmp_path / "bad"
    assert pr.main(["--measurements", str(m), "--sex", "female", "--out", str(out)]) == 3
    assert (out / "problems.json").exists()
    result = json.loads((out / "result.json").read_text(encoding="utf-8"))["outputs"]
    assert result["osa_phenotype"]["value"] is None


def test_fraction_body_fat_and_wrong_unit_stop(tmp_path: Path):
    rows = [("BIA-ACC T-score", "-1.6", ""), ("S-score", "-1.2", ""), ("体脂率", "0.36", "%")]
    m = _csv(tmp_path / "frac.csv", rows)
    out = tmp_path / "frac"
    assert pr.main(["--measurements", str(m), "--sex", "female", "--out", str(out)]) == 3
    rows = [("BIA-ACC T-score", "-1.6", ""), ("S-score", "-1.2", ""), ("体脂率", "36", "kg")]
    m = _csv(tmp_path / "kg.csv", rows)
    out2 = tmp_path / "kg"
    assert pr.main(["--measurements", str(m), "--sex", "female", "--out", str(out2)]) == 3
    assert not (out2 / "report.md").read_text(encoding="utf-8").count("符合论文")


def test_missing_sex_or_score_stops(tmp_path: Path):
    rows = [("BIA-ACC T-score", "-1.6", ""), ("体脂率", "36", "%")]
    m = _csv(tmp_path / "miss.csv", rows)
    out = tmp_path / "miss"
    assert pr.main(["--measurements", str(m), "--sex", "female", "--out", str(out)]) == 3
    assert "S 值" in (out / "report.md").read_text(encoding="utf-8")
    rows = [("BIA-ACC T-score", "-1.6", ""), ("S-score", "-1.2", ""), ("体脂率", "36", "%")]
    m = _csv(tmp_path / "nosex.csv", rows)
    out2 = tmp_path / "nosex"
    assert pr.main(["--measurements", str(m), "--out", str(out2)]) == 3


def test_dxa_t_score_name_is_not_matched(tmp_path: Path):
    rows = [("骨密度T值", "-1.6", ""), ("S-score", "-1.2", ""), ("体脂率", "36", "%")]
    m = _csv(tmp_path / "dxa.csv", rows)
    out = tmp_path / "dxa"
    assert pr.main(["--measurements", str(m), "--sex", "female", "--out", str(out)]) == 3


def test_all_clear_and_age_note(tmp_path: Path):
    rows = [("BIA-ACC T-score", "0.2", ""), ("S-score", "0.1", ""), ("体脂率", "20", "%")]
    code, result, report, _ = _run(tmp_path, rows, sex="male", age="95")
    assert code == 0
    assert result["components_met"]["value"] == 0
    assert "好的信号" in report and "不在研究人群" in report
    assert "开始服用" not in report and "停药" not in report
