"""Report wording: paper card first, boundary kept, no dose or start/stop advice."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

import personal_report
from presets import BOUNDARY
from test_manifest import ARGS_NONE, ROWS, _csv


def test_report_starts_with_paper_card_and_keeps_boundary(tmp_path: Path):
    m = _csv(tmp_path / "m.csv", ROWS)
    args = ["--measurements", str(m), "--age", "102", *ARGS_NONE, "--out", str(tmp_path / "out")]
    args[args.index("--antihypertensive-medication") + 1] = "yes"
    assert personal_report.main(args) == 0
    text = (tmp_path / "out" / "report.md").read_text(encoding="utf-8")
    head = text.split("## 结果")[0]
    assert "10.1093/gerona/glag196" in head
    assert f"边界: {BOUNDARY}" in text
    assert "百岁老人" in text and "1 项（满分 11）" in text
    for phrase in ("建议服用", "建议停用", "开始服用", "剂量", "mg/天"):
        assert phrase not in text


def test_problem_report_also_has_card_and_boundary(tmp_path: Path):
    m = _csv(tmp_path / "m.csv", ROWS[:3])
    assert personal_report.main(["--measurements", str(m), "--age", "60", "--out", str(tmp_path / "out")]) == 3
    text = (tmp_path / "out" / "report.md").read_text(encoding="utf-8")
    assert "10.1093/gerona/glag196" in text and "边界" in text
