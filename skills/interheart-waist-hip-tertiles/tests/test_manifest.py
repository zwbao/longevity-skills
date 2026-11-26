"""Published Table 3 lookup cells; circumference fixtures are synthetic, not paper cases."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import personal_report as report
import presets


@pytest.mark.parametrize("tertile,expected", [
    (2, (1.12, 1.01, 1.25)),
    (3, (1.62, 1.45, 1.80)),
])
def test_table_3_printed_lookup(tertile, expected):
    # Table 3: Abdominal obesity (2 vs 1), (3 vs 1), Adjusted for all.
    # Exact reproduction of the printed lookup, not a refit of the regression.
    assert report.lookup(tertile) == expected


def run(tmp_path, rows="waist_cm,92,cm\nhip_cm,100,cm\n", extra=()):
    path = tmp_path / "measurements.csv"
    path.write_text("marker,value,unit\n" + rows)
    return subprocess.run([
        sys.executable, str(ROOT / "scripts/personal_report.py"),
        "--measurements", str(path), "--sex", "male", "--out", str(tmp_path / "out"),
        *extra,
    ], capture_output=True, text=True)


def outputs(tmp_path):
    return {k: v["value"] for k, v in json.loads(
        (tmp_path / "out/result.json").read_text())["outputs"].items()}


def test_manifest_matches_presets():
    manifest = json.loads((ROOT / "skill.json").read_text())
    assert {x["key"]: x["unit"] for x in manifest["inputs"]
            if x["from"] == "measurements"} == presets.INPUT_UNITS
    # Methods p 939 prints these sex-specific cutoffs.
    assert tuple(map(float, presets.CUTPOINTS["male"])) == (0.90, 0.95)
    assert tuple(map(float, presets.CUTPOINTS["female"])) == (0.83, 0.90)


def test_cli_printed_lookup_and_card(tmp_path):
    assert run(tmp_path).returncode == 0
    result = outputs(tmp_path)
    assert result["waist_hip_ratio"] == 0.92  # synthetic 92 / 100 arithmetic check
    assert result["tertile"] == 2
    assert (result["category_or"], result["category_or_ci_low"],
            result["category_or_ci_high"]) == (1.12, 1.01, 1.25)
    text = (tmp_path / "out/report.md").read_text()
    assert text.index("论文卡片") < text.index("你的测量")
    assert presets.BOUNDARY in text and "边界:" in text
    assert "99%" in text and "个人心梗概率" in text


@pytest.mark.parametrize("sex,waist,tertile", [
    ("male", "89", 1), ("male", "92", 2), ("male", "96", 3),
    ("female", "82", 1), ("female", "85", 2), ("female", "91", 3),
])
def test_sex_specific_categories(tmp_path, sex, waist, tertile):
    assert run(tmp_path, f"waist_cm,{waist},cm\nhip_cm,100,cm\n",
               ("--sex", sex)).returncode == 0
    assert outputs(tmp_path)["tertile"] == tertile


@pytest.mark.parametrize("sex,waist,hip", [
    ("male", "90", "100"), ("male", "95", "100"),
    ("female", "83", "100"), ("female", "90", "100"),
    ("male", "85.5", "95"),
])
def test_exact_cutpoints_remain_unassigned(tmp_path, sex, waist, hip):
    assert run(tmp_path, f"waist_cm,{waist},cm\nhip_cm,{hip},cm\n",
               ("--sex", sex)).returncode == 0
    data = outputs(tmp_path)
    assert data["tertile"] is None and data["category_or"] is None
    assert "边界" in data["category"]


@pytest.mark.parametrize("rows,extra", [
    ("waist_cm,92,kg\nhip_cm,100,cm\n", ()),
    ("waist_cm,92,cm,unexpected_column\nhip_cm,100,cm\n", ()),
    ("waist_cm,920,cm\nhip_cm,100,cm\n", ()),
    ("waist_cm,92,cm\n", ()),
    ("waist_cm,nan,cm\nhip_cm,100,cm\n", ()),
    ("waist_cm,92,cm\nhip_cm,0,cm\n", ()),
    ("waist_cm,92,cm\nhip_cm,100,cm\n", ("--sex", "unknown")),
    ("waist_cm,92,cm\nhip_cm,100,cm\n", ("--age", "bad")),
])
def test_invalid_input_exits_three(tmp_path, rows, extra):
    assert run(tmp_path, rows, extra).returncode == 3
    assert (tmp_path / "out/problems.json").exists()
    assert all(x is None for x in outputs(tmp_path).values())
    assert not (tmp_path / "out/levers.json").exists()
    assert "论文卡片" in (tmp_path / "out/report.md").read_text()


def test_conversion_aliases(tmp_path):
    assert run(tmp_path, "腰围,0.92,m\n臀围,1000,mm\n").returncode == 0
    assert outputs(tmp_path)["waist_hip_ratio"] == pytest.approx(0.92)
    assert outputs(tmp_path)["category_or"] == 1.12


def test_missing_arguments_structured(tmp_path):
    proc = subprocess.run([sys.executable, str(ROOT / "scripts/personal_report.py"),
                           "--out", str(tmp_path / "out")], capture_output=True)
    assert proc.returncode == 3
    problems = json.loads((tmp_path / "out/problems.json").read_text())["problems"]
    assert {p["key"] for p in problems} >= {"waist_cm", "hip_cm", "sex"}


def test_target_scenario_and_stale_cleanup(tmp_path):
    target = tmp_path / "targets.csv"
    target.write_text("marker,value,unit\n腰围,88,cm\n")
    assert run(tmp_path, extra=("--targets", str(target))).returncode == 0
    data = json.loads((tmp_path / "out/levers.json").read_text())
    assert data["schema"] == "longevity-levers/1"
    assert data["current"]["tertile"] == 2
    assert data["targets"]["tertile"] == 1
    assert data["targets"]["waist_hip_ratio"] == 0.88
    assert "因果" in data["note_zh"]
    assert run(tmp_path, "waist_cm,92,cm\n").returncode == 3
    assert not (tmp_path / "out/levers.json").exists()


def test_invalid_targets_and_boundary_target(tmp_path):
    target = tmp_path / "targets.csv"
    for row in ["腰围,1000,cm", "unknown,50,cm", ""]:
        target.write_text("marker,value,unit\n" + row + "\n")
        assert run(tmp_path, extra=("--targets", str(target))).returncode == 3
    target.write_text("marker,value,unit\n腰围,90,cm\n")
    assert run(tmp_path, extra=("--targets", str(target))).returncode == 0
    data = json.loads((tmp_path / "out/levers.json").read_text())
    assert data["targets"]["tertile"] is None
    assert data["targets"]["category_or"] is None
