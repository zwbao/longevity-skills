"""Table 2 (2010 panels): expected cells transcribed before implementation."""
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import personal_report as report
import presets


@pytest.mark.parametrize("area,amount,expected", [
    ("urban", 8.3, [(1.48, 1.39, 1.59), (2.28, 1.90, 2.74), (1.36, 1.19, 1.56), (2.94, 1.99, 4.35)]),
    ("urban", 19.2, [(1.70, 1.60, 1.80), (3.28, 2.82, 3.83), (1.73, 1.53, 1.96), (5.40, 4.04, 7.23)]),
    ("urban", 34.9, [(1.93, 1.75, 2.12), (4.12, 3.24, 5.24), (2.24, 1.85, 2.71), (7.26, 4.66, 11.32)]),
    ("rural", 7.7, [(1.25, 1.20, 1.29), (1.81, 1.57, 2.09), (1.27, 1.16, 1.39), (1.52, 1.36, 1.70)]),
    ("rural", 19.3, [(1.17, 1.13, 1.22), (2.38, 2.14, 2.65), (1.14, 1.03, 1.27), (1.32, 1.18, 1.47)]),
    ("rural", 35.3, [(1.27, 1.20, 1.34), (3.20, 2.75, 3.72), (1.37, 1.16, 1.61), (1.34, 1.13, 1.59)]),
])
def test_table_2_printed_rows(area, amount, expected):
    # Inputs are the table's printed group means, not individual patient cases.
    actual = report.lookup(amount, area)
    for key, cell in zip(presets.OUTCOMES, expected):
        assert tuple(actual[f"{key}_{s}"] for s in ("rr", "gsci_lower", "gsci_upper")) == cell


def run(tmp_path, rows="tobacco_amount_g_d,19.2,g/d\n", extra=None):
    path = tmp_path / "measurements.csv"
    path.write_text("marker,value,unit\n" + rows)
    return subprocess.run([sys.executable, str(ROOT / "scripts/personal_report.py"),
        "--measurements", str(path), "--age", "55", "--sex", "male", "--area", "urban",
        "--smoking", "current", "--regular-six-months", "yes", "--out", str(tmp_path / "out")]
        + (extra or []), capture_output=True, text=True)


def test_manifest_and_success(tmp_path):
    manifest = json.loads((ROOT / "skill.json").read_text())
    assert {x["key"]: x["unit"] for x in manifest["inputs"] if x["from"] == "measurements"} == presets.INPUT_UNITS
    assert run(tmp_path).returncode == 0
    out = json.loads((tmp_path / "out/result.json").read_text())["outputs"]
    assert out["all_cause_mortality_rr"]["value"] == 1.70
    assert out["all_cause_mortality_gsci_lower"]["value"] == 1.60
    assert out["all_cause_mortality_gsci_upper"]["value"] == 1.80
    body = (tmp_path / "out/report.md").read_text()
    assert body.index("论文卡片") < body.index("你的查表结果")
    assert "10.1016/s0140-6736(15)00340-2" in body
    assert "组别特异性" in body and "边界:" in body and presets.BOUNDARY in body


@pytest.mark.parametrize("amount,rr", [(1,1.48),(14.999,1.48),(15,1.70),(24.999,1.70),(25,1.93),(200,1.93)])
def test_cutpoints(amount, rr):
    assert report.lookup(amount, "urban")["all_cause_mortality_rr"] == rr


@pytest.mark.parametrize("rows,extra", [
    ("tobacco_amount_g_d,19.2,mg/d\n", []),
    ("tobacco_amount_g_d,201,g/d\n", []),
    ("tobacco_amount_g_d,0,g/d\n", []),
    ("tobacco_amount_g_d,nan,g/d\n", []),
    ("tobacco_amount_g_d,-1,g/d\n", []),
    ("", []),
    ("每日烟草当量,20,\n", []),
    ("unknown,20,g/d\n", []),
    ("tobacco_amount_g_d,20,g/d\n", ["--sex", "female"]),
    ("tobacco_amount_g_d,20,g/d\n", ["--age", "80"]),
    ("tobacco_amount_g_d,20,g/d\n", ["--age", "39"]),
    ("tobacco_amount_g_d,20,g/d\n", ["--age", "nan"]),
    ("tobacco_amount_g_d,20,g/d\n", ["--age", "55.5"]),
    ("tobacco_amount_g_d,20,g/d\n", ["--area", "unknown"]),
    ("tobacco_amount_g_d,20,g/d\n", ["--smoking", "stopped_choice"]),
    ("tobacco_amount_g_d,20,g/d\n", ["--smoking", "never"]),
    ("tobacco_amount_g_d,20,g/d\n", ["--regular-six-months", "no"]),
])
def test_invalid_input_exits_three(tmp_path, rows, extra):
    assert run(tmp_path, rows, extra).returncode == 3
    assert (tmp_path / "out/problems.json").exists()
    assert not (tmp_path / "out/levers.json").exists()
    assert all(x["value"] is None for x in json.loads((tmp_path / "out/result.json").read_text())["outputs"].values())
    body = (tmp_path / "out/report.md").read_text()
    assert "论文卡片" in body and presets.BOUNDARY in body
    assert "你的查表结果" not in body


def test_alias_and_illness_cessation(tmp_path):
    assert run(tmp_path, "每日烟草当量,19.2,g/d\n", ["--smoking", "stopped_ill"]).returncode == 0
    out = json.loads((tmp_path / "out/result.json").read_text())["outputs"]
    assert out["all_cause_mortality_rr"]["value"] == 1.70
    assert "停烟前" in (tmp_path / "out/report.md").read_text()


def test_missing_inputs_are_structured(tmp_path):
    proc = subprocess.run([sys.executable, str(ROOT / "scripts/personal_report.py"), "--out", str(tmp_path / "out")])
    assert proc.returncode == 3
    keys = {p["key"] for p in json.loads((tmp_path / "out/problems.json").read_text())["problems"]}
    assert keys >= {"tobacco_amount_g_d", "age", "sex", "area", "smoking", "regular_six_months"}


def test_targets_and_stale_outputs(tmp_path):
    target = tmp_path / "targets.csv"
    target.write_text("marker,value,unit\ntobacco_amount_g_d,8.3,g/d\n")
    assert run(tmp_path, extra=["--targets", str(target)]).returncode == 0
    data = json.loads((tmp_path / "out/levers.json").read_text())
    assert data["schema"] == "longevity-levers/1"
    assert data["current"]["all_cause_mortality_rr"] == 1.70
    assert data["targets"]["outputs"]["all_cause_mortality_rr"] == 1.48
    assert data["levers"][0]["rr_delta"]["all_cause_mortality_rr"] == pytest.approx(1.48 - 1.70)
    assert data["sensitivity"][0]["derivative"] is None
    assert "因果" in data["note_zh"]
    target.write_text("marker,value,unit\ntobacco_amount_g_d,0,g/d\n")
    assert run(tmp_path, extra=["--targets", str(target)]).returncode == 3
    assert not (tmp_path / "out/levers.json").exists()


def test_rural_pattern_is_not_monotonized():
    assert report.lookup(7.7, "rural")["all_cause_mortality_rr"] == 1.25
    assert report.lookup(19.3, "rural")["all_cause_mortality_rr"] == 1.17
    assert report.lookup(35.3, "rural")["all_cause_mortality_rr"] == 1.27
