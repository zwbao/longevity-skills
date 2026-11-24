"""Paper normalization example plus input and geometric invariance checks.

The printed example is an index mapping, not a human kinematic worked result.
Accordingly validation remains draft; synthetic geometry is not paper validation.
"""
import csv
import json
import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import personal_report as pr
import presets

MANIFEST = json.loads((ROOT / "skill.json").read_text())


def test_printed_normalization_index_mapping():
    # Methods, Normalization of Segmented Data: five time-points -> 10 bins;
    # "1, 1, 2, 2, … 5, 5". These are source indices, NOT joint coordinates.
    assert pr.normalize([1, 2, 3, 4, 5], 10) == [1, 1, 2, 2, 3, 3, 4, 4, 5, 5]
    assert presets.CYCLE_BINS == 25  # Methods: default 25 cycle-bins


def frames():
    # Synthetic, nonclinical geometry solely for software checks.
    result = []
    for i in range(40):
        theta = 2 * math.pi * i / 40
        result.append(dict(time_s=i / 100, hip_x_cm=i, hip_y_cm=90,
                           knee_x_cm=i + math.sin(theta), knee_y_cm=50,
                           ankle_x_cm=i + 2 * math.sin(theta), ankle_y_cm=10,
                           midfoot_x_cm=i + 12, midfoot_y_cm=5))
    return result


def run(tmp_path, data, name="out", change=None):
    rows = []
    for frame in data:
        for key in presets.FRAME_KEYS:
            rows.append([key, str(frame[key]), "s" if key == "time_s" else "cm"])
    if change:
        change(rows)
    path = tmp_path / (name + ".csv")
    with path.open("w") as f:
        w = csv.writer(f); w.writerow(["item", "value", "unit"]); w.writerows(rows)
    out = tmp_path / name
    code = pr.main(["--measurements", str(path), "--out", str(out)])
    return code, out


def test_manifest_keys_units_and_normal_result(tmp_path):
    specs = {x["key"]: x for x in MANIFEST["inputs"] if x["from"] == "measurements"}
    assert set(specs) == set(presets.FRAME_KEYS)
    assert specs["time_s"]["unit"] == "s"
    assert all(specs[k]["unit"] == "cm" for k in presets.FRAME_KEYS if k != "time_s")
    code, out = run(tmp_path, frames())
    assert code == 0
    outputs = json.loads((out / "result.json").read_text())["outputs"]
    assert set(outputs) == {x["key"] for x in MANIFEST["outputs"]}
    assert all(math.isfinite(x["value"]) for x in outputs.values())
    assert outputs["ankle_angle_min_deg"]["value"] <= outputs["ankle_angle_max_deg"]["value"]
    text = (out / "report.md").read_text()
    assert text.index("论文卡片") < text.index("本次步态")
    assert "边界:" in text and "暂定" in text
    assert len(list(csv.DictReader((out / "cycle.csv").open()))) == 25


def test_coordinate_translation_and_unit_conversion(tmp_path):
    _, a = run(tmp_path, frames(), "original")
    translated = [{k: v if k == "time_s" else v + 20 for k, v in frame.items()} for frame in frames()]
    _, b = run(tmp_path, translated, "translated")
    def millimeters(rows):
        for row in rows:
            if row[0] != "time_s":
                row[1] = str(float(row[1]) * 10); row[2] = "mm"
    _, c = run(tmp_path, frames(), "mm", millimeters)
    def values(out):
        return {k: v["value"] for k, v in json.loads((out / "result.json").read_text())["outputs"].items()}
    assert values(a) == pytest.approx(values(b))
    assert values(a) == pytest.approx(values(c))


@pytest.mark.parametrize("fault", ["unit", "range", "missing", "nan", "time", "geometry", "unknown"])
def test_input_faults_stop_and_remove_stale_outputs(tmp_path, fault):
    _, out = run(tmp_path, frames())
    def change(rows):
        if fault == "unit": rows[1][2] = "kg"
        elif fault == "range": rows[1][1] = "1000000"
        elif fault == "missing": del rows[1]
        elif fault == "nan": rows[1][1] = "nan"
        elif fault == "time": rows[len(presets.FRAME_KEYS)][1] = rows[0][1]
        elif fault == "unknown": rows[1][0] = "wrong_joint"
        elif fault == "geometry":
            rows[3][1] = rows[5][1]; rows[4][1] = rows[6][1]
    code, out = run(tmp_path, frames(), change=change)
    assert code == 3
    assert json.loads((out / "problems.json").read_text())["problems"]
    assert not (out / "result.json").exists()
    assert not (out / "cycle.csv").exists()
    report = (out / "report.md").read_text()
    assert "论文卡片" in report and "边界:" in report
    assert "本次步态" not in report
