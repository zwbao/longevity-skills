"""Printed per-item scores first: Schröder et al. 2011, Table 2.

Frequency column: Yes, ≥4 Tbsp, ≥2, ≥3, <1, <1, <1, ≥7 cups,
≥3, ≥3, <2, ≥3, Yes, ≥2.
Footnote 1: 'Criterion to score 1 point. Otherwise, 0 recorded.'
The inputs at each cutoff and the expected 0/1 are printed in this table;
the tests do not claim a published individual participant's total score.
"""

import csv
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report as report
from presets import ITEMS


# These are Table 2's printed boundaries, independent of implementation presets.
PRINTED = [
    ("olive_oil_main_yes", 1, 1),
    ("olive_oil_tbsp_day", 4, 1),
    ("vegetables_servings_day", 2, 1),
    ("fruit_pieces_day", 3, 1),
    ("red_meat_servings_day", 1, 0),
    ("butter_margarine_cream_servings_day", 1, 0),
    ("sweet_carbonated_drinks_cups_day", 1, 0),
    ("wine_cups_week", 7, 1),
    ("pulses_servings_week", 3, 1),
    ("fish_seafood_servings_week", 3, 1),
    ("commercial_pastry_times_week", 2, 0),
    ("nuts_servings_week", 3, 1),
    ("white_meat_preferred_yes", 1, 1),
    ("sofrito_times_week", 2, 1),
]


def test_table2_printed_per_item_scores():
    for key, printed_input, printed_score in PRINTED:
        assert report.score_item(key, printed_input) == printed_score


def test_table2_olive_oil_condition_and_otherwise():
    # Table 2 row 2: ≥4 Tbsp; footnote 1 explicitly assigns 1 or otherwise 0.
    assert report.score_item("olive_oil_tbsp_day", 4) == 1
    assert report.score_item("olive_oil_tbsp_day", 0) == 0


def write_csv(path, values, unit="1"):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["item", "value", "unit"])
        writer.writerows((k, v, unit) for k, v in values.items())
    return path


def run(tmp_path, values, extra=(), unit="1"):
    path = write_csv(tmp_path / "measurements.csv", values, unit)
    out = tmp_path / "out"
    p = subprocess.run([sys.executable, str(ROOT / "scripts/personal_report.py"),
                        "--measurements", str(path), "--out", str(out), *extra],
                       text=True, capture_output=True)
    return p, out


def test_manifest_matches_presets():
    manifest = json.loads((ROOT / "skill.json").read_text())
    specs = {s["key"]: s for s in manifest["inputs"] if s["from"] == "measurements"}
    assert set(specs) == set(ITEMS)
    for key, item in ITEMS.items():
        assert specs[key]["unit"] == item["unit"]
        assert specs[key]["range"] == item["range"]
    assert {s["key"] for s in manifest["outputs"]} == {"medas_total", *[f"item_{n:02d}_score" for n in range(1, 15)]}


def test_cli_printed_item_scores_and_total(tmp_path):
    values = {k: x for k, x, _ in PRINTED}
    p, out = run(tmp_path, values)
    assert p.returncode == 0, p.stderr
    result = json.loads((out / "result.json").read_text())["outputs"]
    for n, (_, _, expected) in enumerate(PRINTED, 1):
        assert result[f"item_{n:02d}_score"]["value"] == expected
    # Aggregation invariant, not a claimed published participant example.
    assert result["medas_total"]["value"] == sum(x[2] for x in PRINTED)
    text = (out / "report.md").read_text()
    assert text.index("论文卡片") < text.index("你的结果")
    assert "边界" in text and "不建议为了得分开始或增加饮酒" in text
    assert "10.3945/jn.110.135566" in text


@pytest.mark.parametrize("change,unit", [
    ({"olive_oil_tbsp_day": 4}, "mg/dL"),
    ({"olive_oil_tbsp_day": -1}, "1"),
    ({"olive_oil_tbsp_day": "NaN"}, "1"),
    ({"olive_oil_main_yes": 0.5}, "1"),
])
def test_bad_input_exits_three_without_result(tmp_path, change, unit):
    values = {k: x for k, x, _ in PRINTED}
    values.update(change)
    p, out = run(tmp_path, values, unit=unit)
    assert p.returncode == 3, p.stderr
    assert (out / "problems.json").exists()
    assert not (out / "result.json").exists()
    assert not (out / "levers.json").exists()
    text = (out / "report.md").read_text()
    assert "论文卡片" in text and "这次没有计算" in text and "边界" in text


def test_missing_item_never_imputed(tmp_path):
    values = {k: x for k, x, _ in PRINTED}
    del values["wine_cups_week"]
    p, out = run(tmp_path, values)
    assert p.returncode == 3
    assert any(x["key"] == "wine_cups_week" and x["kind"] == "missing"
               for x in json.loads((out / "problems.json").read_text())["problems"])


def test_aliases_and_targets_use_same_scoring(tmp_path):
    values = {k: x for k, x, _ in PRINTED}
    values["每日橄榄油汤匙数"] = values.pop("olive_oil_tbsp_day")
    targets = write_csv(tmp_path / "targets.csv", {"每周商业糕点次数": 1})
    p, out = run(tmp_path, values, ["--targets", str(targets), "--age", "40", "--sex", "female"])
    assert p.returncode == 0, p.stderr
    levers = json.loads((out / "levers.json").read_text())
    # Table 2 explicitly assigns 1 to <2 times/week and 0 at 2.
    assert levers["levers"][0]["item_score"] == 1
    assert levers["levers"][0]["medas_total_delta"] == 1
    assert levers["targets"]["medas_total"] == levers["current"]["medas_total"] + 1
    assert len(levers["sensitivity"]) == 14
    assert "超出" in (out / "report.md").read_text()


def test_invalid_target_clears_previous_success(tmp_path):
    values = {k: x for k, x, _ in PRINTED}
    p, out = run(tmp_path, values)
    assert p.returncode == 0
    targets = write_csv(tmp_path / "targets.csv", {"nuts_servings_week": -1})
    p, out = run(tmp_path, values, ["--targets", str(targets)])
    assert p.returncode == 3
    assert not (out / "result.json").exists()
    assert not (out / "levers.json").exists()
