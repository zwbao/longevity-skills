"""Table 1, p. 23: printed per-item recoding, written before implementation.

Printed excerpt: (i.e., 1 = 4, 2 = 3, 3 = 2, 4 = 1)
No complete participant response vector and total is printed in this paper.
CLI fixtures below are synthetic integration checks, not published participants.
"""

import csv
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def test_table1_printed_reverse_scores():
    from personal_report import item_points

    # Table 1's starred items and four printed input -> output pairs.
    for item in (1, 5, 6, 9, 10, 15, 16, 19, 20):
        assert item_points(item, 1) == 4
        assert item_points(item, 2) == 3
        assert item_points(item, 3) == 2
        assert item_points(item, 4) == 1


def test_table1_unstarred_items_keep_response():
    from personal_report import item_points

    for item in (2, 3, 4, 7, 8, 11, 12, 13, 14, 17, 18):
        for response in (1, 2, 3, 4):
            assert item_points(item, response) == response


def test_manifest_matches_presets():
    from presets import MEASUREMENTS, REVERSE_ITEMS

    manifest = json.loads((ROOT / "skill.json").read_text())
    assert {s["key"]: (s["unit"], tuple(s["range"]))
            for s in manifest["inputs"] if s["from"] == "measurements"} == MEASUREMENTS
    assert REVERSE_ITEMS == frozenset((1, 5, 6, 9, 10, 15, 16, 19, 20))
    assert manifest["validation"]["status"] == "reproduced"
    assert manifest["inputs_status"] == "verified"


def valid_rows():
    # Synthetic answers: every item is answered Never (Table 1 response code 1).
    return [(f"ucla_v3_item_{i:02d}_response_score", "1", "score")
            for i in range(1, 21)]


def run_report(tmp_path, rows=None, extra=()):
    path = tmp_path / "answers.csv"
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(("marker", "value", "unit"))
        writer.writerows(valid_rows() if rows is None else rows)
    out = tmp_path / "out"
    process = subprocess.run(
        [sys.executable, str(ROOT / "scripts/personal_report.py"),
         "--measurements", str(path), "--out", str(out), *extra],
        capture_output=True, text=True,
    )
    return process, out


def test_result_json_and_chinese_report(tmp_path):
    process, out = run_report(tmp_path)
    assert process.returncode == 0, process.stderr
    outputs = json.loads((out / "result.json").read_text())["outputs"]
    for item in (1, 5, 6, 9, 10, 15, 16, 19, 20):
        assert outputs[f"item_{item:02d}_score"]["value"] == 4
    for item in (2, 3, 4, 7, 8, 11, 12, 13, 14, 17, 18):
        assert outputs[f"item_{item:02d}_score"]["value"] == 1
    # Structural aggregation check; no invented published total is claimed.
    assert outputs["ucla_v3_total_score"]["value"] == sum(
        outputs[f"item_{i:02d}_score"]["value"] for i in range(1, 21))
    report = (out / "report.md").read_text()
    assert report.index("## 论文卡片") < report.index("## 你的结果")
    assert "边界:" in report and "不是精神疾病诊断" in report
    assert "未经本论文验证的中文译本" in report
    assert not (out / "problems.json").exists()


@pytest.mark.parametrize("value,unit", [
    ("1", "mg/dL"), ("0", "score"), ("5", "score"),
    ("1.5", "score"), ("nan", "score"), ("inf", "score"), ("never", "score"),
])
def test_invalid_response_exits_three(tmp_path, value, unit):
    rows = valid_rows()
    rows[0] = (rows[0][0], value, unit)
    process, out = run_report(tmp_path, rows)
    assert process.returncode == 3, process.stderr
    assert (out / "problems.json").exists()
    assert not (out / "result.json").exists()
    report = (out / "report.md").read_text()
    assert "## 论文卡片" in report and "边界:" in report
    assert "## 你的结果" not in report


def test_missing_response_and_short_form_rejected(tmp_path):
    for rows in (valid_rows()[:-1], valid_rows()[:10], []):
        process, out = run_report(tmp_path, rows)
        assert process.returncode == 3
        problems = json.loads((out / "problems.json").read_text())["problems"]
        assert any(p["key"] == "ucla_v3_item_20_response_score" and
                   p["kind"] == "missing" for p in problems)


def test_aliases_and_optional_context_do_not_change_score(tmp_path):
    process, out = run_report(tmp_path)
    assert process.returncode == 0
    expected = json.loads((out / "result.json").read_text())["outputs"]
    rows = [(f"UCLA V3 Q{i}" if i % 2 else f"UCLA第三版第{i}题", "1", "score")
            for i in range(1, 21)]
    process, out = run_report(tmp_path, rows, ("--age", "70", "--sex", "女"))
    assert process.returncode == 0, process.stderr
    assert json.loads((out / "result.json").read_text())["outputs"] == expected


@pytest.mark.parametrize("extra", [("--age", "unknown"), ("--age", "-1"),
                                   ("--sex", "invalid")])
def test_invalid_optional_context(tmp_path, extra):
    process, out = run_report(tmp_path, extra=extra)
    assert process.returncode == 3
    assert (out / "problems.json").exists()


def test_duplicate_and_unknown_items_rejected(tmp_path):
    rows = valid_rows()
    for additional in [(rows[0][0], "2", "score"), ("UCLA V3 Q21", "1", "score")]:
        process, out = run_report(tmp_path, rows + [additional])
        assert process.returncode == 3
        assert not (out / "result.json").exists()


def test_stale_outputs_cleared(tmp_path):
    assert run_report(tmp_path)[0].returncode == 0
    process, out = run_report(tmp_path, valid_rows()[:-1])
    assert process.returncode == 3 and not (out / "result.json").exists()
    process, out = run_report(tmp_path)
    assert process.returncode == 0 and not (out / "problems.json").exists()


def test_missing_file_exits_three(tmp_path):
    process, out = run_report(tmp_path, extra=("--measurements", str(tmp_path / "missing.csv")))
    assert process.returncode == 3
    assert (out / "problems.json").exists()
