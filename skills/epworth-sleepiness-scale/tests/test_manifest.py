"""Table 1 prints the item scores 0, 1, 2, 3; no completed patient is printed.

Only item scoring is a paper reproduction. Mixed totals below are explicitly
synthetic arithmetic/integration checks, not reported patient observations.
"""

import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def test_table1_item_scores():
    from personal_report import calculate
    from presets import ITEM_KEYS

    # Table 1, p. 541: each response contributes its printed score, unchanged.
    # Exercise every response for every item, without claiming a printed total.
    for printed_score in (0, 1, 2, 3):
        result = calculate(dict.fromkeys(ITEM_KEYS, printed_score))
        for key in ITEM_KEYS:
            assert result[key] == printed_score


def test_manifest_matches_presets():
    from presets import ITEM_KEYS, ITEM_RANGE, ITEM_UNIT

    manifest = json.loads((ROOT / "skill.json").read_text())
    specs = [s for s in manifest["inputs"] if s["from"] == "measurements"]
    assert tuple(s["key"] for s in specs) == ITEM_KEYS
    assert all(s["unit"] == ITEM_UNIT and tuple(s["range"]) == ITEM_RANGE for s in specs)
    assert all(s["required"] and s["accept"] == {} for s in specs)


# Synthetic fixture for software behavior, not a participant in Johns 1991.
VALID = [(f"ess_item_{i}_score", str(value), "score")
         for i, value in enumerate((0, 1, 2, 3, 0, 1, 2, 3), 1)]


def run_report(tmp_path, rows=VALID, extra=()):
    source = tmp_path / "measurements.csv"
    source.write_text("marker,value,unit\n" + "\n".join(",".join(row) for row in rows) + "\n")
    out = tmp_path / "out"
    run = subprocess.run([sys.executable, str(ROOT / "scripts/personal_report.py"),
                          "--measurements", str(source), "--out", str(out), *extra],
                         capture_output=True, text=True)
    return run, out


def test_result_and_report(tmp_path):
    run, out = run_report(tmp_path)
    assert run.returncode == 0, run.stderr
    result = json.loads((out / "result.json").read_text())["outputs"]
    assert result["ess_total_score"]["value"] == 12  # Synthetic sum, not validation evidence.
    for key, value, _ in VALID:
        assert result[key]["value"] == int(value)
    text = (out / "report.md").read_text()
    assert text.index("## 论文卡片") < text.index("## 你的结果")
    assert "边界:" in text
    assert "不是诊断" in text
    assert not (out / "problems.json").exists()


@pytest.mark.parametrize("value,unit", [
    ("1", "mg/dL"), ("4", "score"), ("-1", "score"),
    ("1.5", "score"), ("nan", "score"), ("inf", "score"), ("unknown", "score"),
])
def test_wrong_input_exits_three(tmp_path, value, unit):
    run, out = run_report(tmp_path, [(VALID[0][0], value, unit), *VALID[1:]])
    assert run.returncode == 3, run.stderr
    assert json.loads((out / "problems.json").read_text())["problems"]
    assert not (out / "result.json").exists()
    text = (out / "report.md").read_text()
    assert "## 论文卡片" in text and "边界:" in text
    assert "## 你的结果" not in text


def test_missing_item_and_stale_result(tmp_path):
    assert run_report(tmp_path)[0].returncode == 0
    run, out = run_report(tmp_path, VALID[:-1])
    assert run.returncode == 3 and not (out / "result.json").exists()
    problems = json.loads((out / "problems.json").read_text())["problems"]
    assert any(p["key"] == "ess_item_8_score" and p["kind"] == "missing" for p in problems)
    assert run_report(tmp_path)[0].returncode == 0
    assert not (out / "problems.json").exists()


def test_aliases(tmp_path):
    manifest = json.loads((ROOT / "skill.json").read_text())
    labels = [s["label_zh"] for s in manifest["inputs"] if s["from"] == "measurements"]
    rows = [(labels[i] if i % 2 else f"ESS{i + 1}", v, u)
            for i, (_, v, u) in enumerate(VALID)]
    run, out = run_report(tmp_path, rows)
    assert run.returncode == 0, run.stderr
    assert json.loads((out / "result.json").read_text())["outputs"]["ess_total_score"]["value"] == 12


@pytest.mark.parametrize("extra", [("--age", "17"), ("--age", "bad"), ("--sex", "bad")])
def test_invalid_context(tmp_path, extra):
    run, out = run_report(tmp_path, extra=extra)
    assert run.returncode == 3
    assert (out / "problems.json").exists() and not (out / "result.json").exists()


def test_missing_file(tmp_path):
    out = tmp_path / "out"
    run = subprocess.run([sys.executable, str(ROOT / "scripts/personal_report.py"),
                          "--measurements", str(tmp_path / "absent.csv"), "--out", str(out)],
                         capture_output=True, text=True)
    assert run.returncode == 3
    assert (out / "problems.json").exists()


def test_duplicate_item_is_not_summed(tmp_path):
    run, out = run_report(tmp_path, [*VALID, (VALID[0][0], "3", "score")])
    assert run.returncode == 3
    assert not (out / "result.json").exists()
