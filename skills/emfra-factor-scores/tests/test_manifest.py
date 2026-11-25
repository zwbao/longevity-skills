"""Printed expectations: SM section 6, Table 65; weights: Table 64.

The paper defines the endpoints by all factor-specific recoded items being
0 or 2. These are theoretical examples, not observed patient records.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report
import presets


# Item order: 1, 2, 5, 6, 7, 11, 12, 15, 19 (Table 64).
# Raw inputs explicitly undo the factor-specific 2-X reversal in SM 5.3.
F1_MIN = [0, 0, 2, 0, 0, 0, 0, 0, 0]
F1_MAX = [2, 2, 0, 2, 2, 2, 2, 2, 2]
F2_MIN = [2, 0, 0, 2, 0, 0, 0, 2, 2]
F2_MAX = [0, 2, 2, 0, 2, 2, 2, 0, 0]


def test_paper_table65_endpoints():
    # Printed cells: MR1 Autonomy 0 2.696; MR2 Psychological distress 0 2.732.
    for raw, key, expected in [
        (F1_MIN, "autonomy_score", 0),
        (F1_MAX, "autonomy_score", 2.696),
        (F2_MIN, "psychological_distress_score", 0),
        (F2_MAX, "psychological_distress_score", 2.732),
    ]:
        values = dict(zip(presets.ITEM_KEYS, raw))
        assert personal_report.compute(values)[key] == pytest.approx(expected, abs=1e-12)


def manifest():
    return json.loads((ROOT / "skill.json").read_text())


def write_csv(path, raw=F1_MAX):
    path.write_text("marker,value,unit\n" + "".join(
        f"{key},{value},score\n" for key, value in zip(presets.ITEM_KEYS, raw)
    ))
    return path


def run(path, out, age="75", dementia="no"):
    command = [sys.executable, str(ROOT / "scripts/personal_report.py"),
               "--measurements", str(path), "--out", str(out)]
    if age is not None:
        command += ["--age", age]
    if dementia is not None:
        command += ["--dementia-diagnosis", dementia]
    return subprocess.run(command, capture_output=True, text=True)


def test_manifest_keys_units_weights_and_preprint():
    m = manifest()
    specs = [s for s in m["inputs"] if s["from"] == "measurements"]
    assert [s["key"] for s in specs] == list(presets.ITEM_KEYS)
    assert all(s["unit"] == presets.ITEM_UNIT and s["range"] == [0, 2] for s in specs)
    assert m["population"]["age_years"] == list(presets.OBSERVED_AGES)
    assert m["validation"]["status"] == "draft"
    assert m["validation"]["gap_zh"].startswith("预印本，未经同行评审")
    assert m["validation"]["examples"]
    # Signed, printed Table 64 rows; do not infer coefficients from computed scores.
    assert list(presets.WEIGHTS.values()) == [
        (0.233, -0.011), (0.405, 0.034), (-0.054, 0.157),
        (0.172, -0.009), (0.179, 0.032), (0.024, 0.388),
        (0.009, 0.510), (0.038, -0.157), (0.234, -0.068),
    ]


@pytest.mark.parametrize("raw,key,printed", [
    (F1_MAX, "autonomy_score", 2.696),
    (F2_MAX, "psychological_distress_score", 2.732),
    (F1_MIN, "autonomy_score", 0),
    (F2_MIN, "psychological_distress_score", 0),
])
def test_cli_printed_endpoints_round_to_two_places(tmp_path, raw, key, printed):
    path = write_csv(tmp_path / "items.csv", raw)
    out = tmp_path / "out"
    process = run(path, out)
    assert process.returncode == 0, process.stderr
    result = json.loads((out / "result.json").read_text())
    assert result["outputs"][key]["value"] == round(printed, 2)
    assert set(result["outputs"]) == {"autonomy_score", "psychological_distress_score"}
    report = (out / "report.md").read_text()
    assert report.index("论文卡片") < report.index("本次结果")
    assert presets.BOUNDARY in report
    assert "预印本，未经同行评审" in report
    assert not (out / "levers.json").exists()


@pytest.mark.parametrize("change,kind", [
    ("wrong_unit", "unit"), ("out_of_range", "range"),
    ("fraction", "category"), ("missing", "missing"),
    ("nan", "parse"), ("duplicate", "duplicate"),
    ("raw_alias", "missing"), ("reverse_alias", "missing"),
])
def test_bad_items_exit3_and_clear_previous_scores(tmp_path, change, kind):
    path = write_csv(tmp_path / "items.csv")
    out = tmp_path / "out"
    assert run(path, out).returncode == 0
    lines = path.read_text().splitlines()
    key = presets.ITEM_KEYS[0]
    if change == "wrong_unit":
        lines[1] = f"{key},2,kg"
    elif change == "out_of_range":
        lines[1] = f"{key},3,score"
    elif change == "fraction":
        lines[1] = f"{key},0.5,score"
    elif change == "missing":
        del lines[1]
    elif change == "nan":
        lines[1] = f"{key},NaN,score"
    elif change == "duplicate":
        lines.append(f"{key},1,score")
    elif change == "raw_alias":
        lines[1] = "Handgrip_mean,2,kg"
    elif change == "reverse_alias":
        lines[1] = "EMFRA_item1_trait_reverse,2,score"
    path.write_text("\n".join(lines) + "\n")
    assert run(path, out).returncode == 3
    problems = json.loads((out / "problems.json").read_text())["problems"]
    assert kind in {p["kind"] for p in problems}
    assert all(v["value"] is None for v in json.loads((out / "result.json").read_text())["outputs"].values())
    report = (out / "report.md").read_text()
    assert "论文卡片" in report and presets.BOUNDARY in report
    assert "2.70" not in report and "本次结果" not in report


@pytest.mark.parametrize("age,dementia", [
    (None, "no"), ("64", "no"), ("NaN", "no"), ("old", "no"),
    ("75", None), ("75", "unknown"), ("75", "yes"),
])
def test_population_missing_or_invalid_exit3(tmp_path, age, dementia):
    path = write_csv(tmp_path / "items.csv")
    out = tmp_path / "out"
    assert run(path, out, age, dementia).returncode == 3
    assert (out / "problems.json").exists()


def test_aliases_and_recovery_from_error(tmp_path):
    path = write_csv(tmp_path / "items.csv")
    out = tmp_path / "out"
    assert run(path, out, dementia=None).returncode == 3
    specs = [s for s in manifest()["inputs"] if s["from"] == "measurements"]
    text = path.read_text()
    for spec in specs:
        text = text.replace(spec["key"], spec["aliases"][0])
    path.write_text(text)
    assert run(path, out).returncode == 0
    assert not (out / "problems.json").exists()
    assert json.loads((out / "result.json").read_text())["outputs"]["autonomy_score"]["value"] == round(2.696, 2)


def test_unreadable_file_exit3(tmp_path):
    out = tmp_path / "out"
    assert run(tmp_path / "absent.csv", out).returncode == 3
    assert (out / "problems.json").exists()


def test_age_above_observed_sample_warns(tmp_path):
    path = write_csv(tmp_path / "items.csv")
    out = tmp_path / "out"
    assert run(path, out, age="100").returncode == 0
    assert "超出研究实际年龄范围" in (out / "report.md").read_text()
