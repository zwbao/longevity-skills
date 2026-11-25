"""skill.json matches presets; printed weights; unit and range mistakes stop the computation.

The paper prints no worked EDISEA example (validation: draft). The weight test
checks that the full-precision Source Data Fig. 2b weights round to the
three-decimal weights printed in the Results text and in Supplementary Data 2
("Primary model"): tea (0.003), whole grains (0.002), fruits (0.002),
fries (-0.021), liquor (-0.013), beer (-0.011), processed meat (-0.008),
sugar-sweetened beverages (-0.002), artificially sweetened beverages (-0.002),
margarine (-0.002). That checks the transcription, not a reproduction.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report
import skillkit
from presets import FOODS, PRINTED_WEIGHTS_3DP, Q1_Q5_MEDIANS, WEIGHTS

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))

SERVINGS = {
    "tea_serv_d": 2, "whole_grains_serv_d": 1.5, "fruits_serv_d": 2, "fries_serv_d": 0.1, "liquor_serv_d": 0,
    "beer_serv_d": 0.5, "processed_meat_serv_d": 0.3, "ssb_serv_d": 0.2, "asb_serv_d": 0, "margarine_serv_d": 0,
}
CHINESE = [("茶", "2"), ("全谷物", "1.5"), ("水果", "2"), ("薯条", "0.1"), ("烈酒", "0"), ("啤酒", "0.5"),
           ("加工肉", "0.3"), ("含糖饮料", "0.2"), ("代糖饮料", "0"), ("人造黄油", "0")]


def _csv(path: Path, rows) -> Path:
    lines = ["item,value,unit"] + [",".join(row) if len(row) == 3 else f"{row[0]},{row[1]}," for row in rows]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _by_hand(servings, energy=None):
    factor = 1.0 if energy is None else 2000.0 / energy
    return sum(weight * servings[key] * factor for key, _label, _name, weight in FOODS)


def test_source_data_weights_round_to_printed_weights():
    printed = [0.003, 0.002, 0.002, -0.021, -0.013, -0.011, -0.008, -0.002, -0.002, -0.002]
    assert [PRINTED_WEIGHTS_3DP[key] for key, *_ in FOODS] == printed
    for key, _label, _name, weight in FOODS:
        assert round(weight, 3) == pytest.approx(PRINTED_WEIGHTS_3DP[key], abs=1e-12)
    assert sum(1 for w in WEIGHTS.values() if w > 0) == 3
    assert Q1_Q5_MEDIANS["tea_serv_d"] == (0.12, 0.87)


def test_manifest_matches_presets():
    declared = [item for item in MANIFEST["inputs"] if item["from"] == "measurements"]
    keys = [item["key"] for item in declared]
    assert keys[:10] == [key for key, *_ in FOODS]
    assert keys[10] == "energy_kcal_d"
    for item, (key, label, _name, _w) in zip(declared, FOODS):
        assert item["label_zh"] == label and item["required"] is True and item["range"] == [0, 30]
    assert MANIFEST["inputs_status"] == "verified"
    assert MANIFEST["validation"]["status"] == "draft"
    assert {item["key"] for item in MANIFEST["outputs"]} == {"edisea"}
    assert MANIFEST["entry"]["targets_flag"] == "--targets" and MANIFEST["entry"]["levers_json"] is True


def test_chinese_names_without_energy(tmp_path: Path):
    code = personal_report.main(["--intake", str(_csv(tmp_path / "in.csv", CHINESE)), "--out", str(tmp_path / "out")])
    assert code == 0
    expected = _by_hand(SERVINGS)
    result = json.loads((tmp_path / "out" / "result.json").read_text(encoding="utf-8"))
    assert result["outputs"]["edisea"]["value"] == pytest.approx(expected)
    text = (tmp_path / "out" / "report.md").read_text(encoding="utf-8")
    assert f"{expected:.4f}" in text
    assert "## 论文卡片" in text and "10.1038/s41467-026-77790-9" in text
    assert "没有提供每日总能量" in text
    assert "边界:" in text
    assert not (tmp_path / "out" / "problems.json").exists()


def test_energy_rescales_to_2000_kcal(tmp_path: Path):
    rows = [(key, str(value)) for key, value in SERVINGS.items()] + [("energy_kcal_d", "2500")]
    code = personal_report.main(["--intake", str(_csv(tmp_path / "in.csv", rows)), "--sex", "女", "--out", str(tmp_path / "out")])
    assert code == 0
    result = json.loads((tmp_path / "out" / "result.json").read_text(encoding="utf-8"))
    assert result["outputs"]["edisea"]["value"] == pytest.approx(_by_hand(SERVINGS, 2500))
    assert result["outputs"]["edisea"]["value"] == pytest.approx(_by_hand(SERVINGS) * 0.8)
    assert "可信" not in (tmp_path / "out" / "report.md").read_text(encoding="utf-8")  # 2500 is inside women's 500-3500
    rows[-1] = ("energy_kcal_d", "3800")
    code = personal_report.main(["--intake", str(_csv(tmp_path / "in2.csv", rows)), "--sex", "女", "--out", str(tmp_path / "out2")])
    assert code == 0
    text = (tmp_path / "out2" / "report.md").read_text(encoding="utf-8")
    assert "高于 3500 千卡" in text and "不可信" in text


def test_wrong_unit_stops(tmp_path: Path):
    rows = [row if row[0] != "茶" else ("茶", "2", "g") for row in CHINESE]
    code = personal_report.main(["--intake", str(_csv(tmp_path / "in.csv", rows)), "--out", str(tmp_path / "out")])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    assert (tmp_path / "out" / "problems.json").exists()
    text = (tmp_path / "out" / "report.md").read_text(encoding="utf-8")
    assert "没有 EDISEA" in text and "你的 EDISEA 是" not in text
    result = json.loads((tmp_path / "out" / "result.json").read_text(encoding="utf-8"))
    assert result["outputs"]["edisea"]["value"] is None


def test_kilojoules_out_of_range_stop(tmp_path: Path):
    rows = list(CHINESE) + [("总能量", "8400")]
    code = personal_report.main(["--intake", str(_csv(tmp_path / "in.csv", rows)), "--out", str(tmp_path / "out")])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    assert "你的 EDISEA 是" not in (tmp_path / "out" / "report.md").read_text(encoding="utf-8")


def test_missing_food_stops(tmp_path: Path):
    rows = [row for row in CHINESE if row[0] != "啤酒"]
    code = personal_report.main(["--intake", str(_csv(tmp_path / "in.csv", rows)), "--out", str(tmp_path / "out")])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((tmp_path / "out" / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert any(item["key"] == "beer_serv_d" and item["kind"] == "missing" for item in problems)


def test_levers_with_targets(tmp_path: Path):
    intake = _csv(tmp_path / "in.csv", CHINESE)
    targets = _csv(tmp_path / "t.csv", [("啤酒", "0"), ("茶", "3")])
    code = personal_report.main(["--intake", str(intake), "--targets", str(targets), "--out", str(tmp_path / "out")])
    assert code == 0
    levers = json.loads((tmp_path / "out" / "levers.json").read_text(encoding="utf-8"))
    assert levers["schema"] == "longevity-levers/1"
    per = {item["key"]: item["per_unit"] for item in levers["sensitivity"]}
    assert per["fries_serv_d"] == pytest.approx(WEIGHTS["fries_serv_d"])
    moved = {item["key"]: item["edisea_delta"] for item in levers["levers"]}
    assert moved["beer_serv_d"] == pytest.approx(-0.5 * WEIGHTS["beer_serv_d"])
    assert moved["tea_serv_d"] == pytest.approx(1 * WEIGHTS["tea_serv_d"])
    assert levers["targets"]["edisea_delta"] == pytest.approx(moved["beer_serv_d"] + moved["tea_serv_d"])
