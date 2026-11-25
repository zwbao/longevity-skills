"""Printed examples, written before implementation; pp. 324–325 and 329."""

import json
import csv
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report as report
import presets


def test_printed_frailty_example():
    # Methods, pp. 324–325: 92 candidate items, 12 unperformed,
    # 80 assessed, 16 present; "the frailty index is 16/80 = 0.2."
    assert presets.MAX_ITEMS == 92
    assert report.frailty_index(16, 80) == pytest.approx(0.2, abs=1e-12)


def test_printed_survival_examples():
    # p. 329: q = 0.20, T = 24 months, V = 4.8, P = 0.55;
    # T = 60 months, V = 12, P = 0.16. Printed probabilities have 2 decimals.
    assert report.survival_probability(0.20, 24) == pytest.approx(0.55, abs=0.005)
    assert report.survival_probability(0.20, 60) == pytest.approx(0.16, abs=0.005)


def run_cli(tmp_path, rows, extra=()):
    csv = tmp_path / "measurements.csv"
    csv.write_text("marker,value,unit\n" + "\n".join(rows) + "\n")
    out = tmp_path / "out"
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/personal_report.py"),
         "--measurements", str(csv), "--age", "82", "--out", str(out), *extra],
        capture_output=True, text=True,
    )
    return proc, out


def test_manifest_and_printed_example_in_result(tmp_path):
    manifest = json.loads((ROOT / "skill.json").read_text())
    assert [(x["key"], x["unit"]) for x in manifest["inputs"]
            if x["from"] == "measurements"] == list(presets.COUNT_INPUTS)
    proc, out = run_cli(tmp_path, ["缺陷数,16,1", "已评估项数,80,1"])
    assert proc.returncode == 0, proc.stderr
    values = json.loads((out / "result.json").read_text())["outputs"]
    assert values["frailty_index"]["value"] == pytest.approx(0.2)
    text = (out / "report.md").read_text()
    assert text.index("论文卡片") < text.index("你的结果")
    assert "10.1100/tsw.2001.58" in text
    assert report.BOUNDARY in text
    for months, expected in ((24, 55), (60, 16)):
        assert values[f"historical_survival_{months}mo_pct"]["value"] == pytest.approx(expected, abs=0.5)


@pytest.mark.parametrize("rows", [
    ["缺陷数,16,%", "已评估项数,80,1"],
    ["缺陷数,16,1", "已评估项数,93,1"],
    ["缺陷数,16,1"],
    ["缺陷数,81,1", "已评估项数,80,1"],
    ["缺陷数,16.5,1", "已评估项数,80,1"],
    ["缺陷数,16,1", "已评估项数,0,1"],
    ["缺陷数,NaN,1", "已评估项数,80,1"],
])
def test_invalid_input_exits_three(tmp_path, rows):
    proc, out = run_cli(tmp_path, rows)
    assert proc.returncode == 3, proc.stderr
    assert json.loads((out / "problems.json").read_text())["problems"]
    assert not (out / "levers.json").exists()
    values = json.loads((out / "result.json").read_text())["outputs"]
    assert all(v["value"] is None for v in values.values())
    text = (out / "report.md").read_text()
    assert "你的结果" not in text and report.BOUNDARY in text
    assert text.index("论文卡片") < text.index("输入没有通过检查")


def test_targets_hold_denominator_fixed(tmp_path):
    target = tmp_path / "target.csv"
    # Reuse the printed 16/80 -> 0.2 as the target; starting count is synthetic.
    target.write_text("marker,value,unit\n缺陷数,16,1\n")
    proc, out = run_cli(tmp_path, ["缺陷数,20,1", "已评估项数,80,1"],
                        ["--targets", str(target)])
    assert proc.returncode == 0, proc.stderr
    levers = json.loads((out / "levers.json").read_text())
    assert levers["schema"] == "longevity-levers/1"
    assert levers["targets"]["frailty_index"] == pytest.approx(0.2)
    assert levers["levers"][0]["frailty_index_delta"] == pytest.approx(
        0.2 - levers["current"]["frailty_index"])
    slope = levers["sensitivity"][0]["frailty_index_per_unit"]
    assert slope == pytest.approx(report.frailty_index(21, 80) - report.frailty_index(20, 80))
    assert levers["sensitivity"][1]["target_allowed"] is False


@pytest.mark.parametrize("target_rows", [
    "缺陷数,16,1\n已评估项数,92,1\n",  # denominator cannot be a lever
    "缺陷数,81,1\n",                     # greater than current denominator
    "缺陷数,16,%\n",                     # count is not percent
    "缺陷数,NaN,1\n",
    "unknown,16,1\n",
    "",
])
def test_bad_targets_remove_stale_results(tmp_path, target_rows):
    rows = ["缺陷数,16,1", "已评估项数,80,1"]
    proc, out = run_cli(tmp_path, rows)
    assert proc.returncode == 0
    target = tmp_path / "target.csv"
    target.write_text("marker,value,unit\n" + target_rows)
    proc, out = run_cli(tmp_path, rows, ["--targets", str(target)])
    assert proc.returncode == 3, proc.stderr
    assert not (out / "levers.json").exists()
    assert all(v["value"] is None for v in json.loads((out / "result.json").read_text())["outputs"].values())


def test_zero_deficits_do_not_promise_survival(tmp_path):
    proc, out = run_cli(tmp_path, ["缺陷数,0,1", "已评估项数,80,1"])
    assert proc.returncode == 0
    result = json.loads((out / "result.json").read_text())["outputs"]
    assert result["frailty_index"]["value"] == 0
    assert result["historical_survival_24mo_pct"]["value"] is None
    assert result["historical_survival_60mo_pct"]["value"] is None
    assert "不输出生存概率" in (out / "report.md").read_text()


@pytest.mark.parametrize("age", ["64", "107", "not-a-number", "inf"])
def test_age_scope_and_format(tmp_path, age):
    proc, out = run_cli(tmp_path, ["缺陷数,16,1", "已评估项数,80,1"], ["--age", age])
    assert proc.returncode == 3, proc.stderr
    assert (out / "problems.json").exists()


def test_missing_file_and_missing_age(tmp_path):
    out = tmp_path / "out"
    proc = subprocess.run([sys.executable, str(ROOT / "scripts/personal_report.py"),
                           "--measurements", str(tmp_path / "absent.csv"),
                           "--out", str(out)], capture_output=True, text=True)
    assert proc.returncode == 3, proc.stderr
    problems = json.loads((out / "problems.json").read_text())["problems"]
    assert {p["kind"] for p in problems} >= {"missing", "file"}


def test_appendix_and_manifest_ranges():
    manifest = json.loads((ROOT / "skill.json").read_text())
    spec = {s["key"]: s for s in manifest["inputs"]}
    assert spec["deficits_count"]["range"] == [0, presets.MAX_ITEMS]
    assert spec["assessed_count"]["range"] == [1, presets.MAX_ITEMS]
    assert spec["age"]["range"] == list(presets.AGE_RANGE)
    with (ROOT / "references/appendix.csv").open() as f:
        rows = list(csv.DictReader(f))
    assert [int(r["number"]) for r in rows] == list(range(1, 93))
    assert len({r["code"] for r in rows}) == 92
    assert sum(r["original_twenty"] == "true" for r in rows) == 20
