import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import BOUNDARY, FA_ILF_D, LIHBA_R_MULTIMODAL


def test_laterality_formula():
    assert personal_report.laterality(2, 1) == (2 - 1) / (2 + 1)
    assert personal_report.laterality(1, 1) == 0
    assert personal_report.laterality(1, -1) is None
    assert FA_ILF_D == 3.64
    assert LIHBA_R_MULTIMODAL == -0.123


def test_report_keeps_index(tmp_path: Path):
    regions = tmp_path / "regions.csv"
    regions.write_text("name,left,right\n海马,2,1\n", encoding="utf-8")
    meds = tmp_path / "meds.txt"
    meds.write_text("不存在的药\n", encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n谷丙转氨酶,80,U/L\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "out", regions, meds, labs).read_text(encoding="utf-8")
    bare = personal_report.report(tmp_path / "bare", regions, None, None).read_text(encoding="utf-8")
    assert f"边界: {BOUNDARY}" in text
    assert "不能据此停" in text
    assert "0.3333" in text
    assert "谷丙转氨酶 80" in text
    assert "不增删方法算出的名单" in text
    assert "该开始" not in text
    assert "建议停" not in text
    assert _index(bare) == _index(text)


def _index(text: str) -> list[str]:
    return [line for line in text.splitlines() if line.startswith("- 海马")]


def test_blank_run(tmp_path: Path):
    text = personal_report.report(tmp_path / "blank").read_text(encoding="utf-8")
    assert text.splitlines()[0] == "# 半球侧化"
    assert "这次没有给出左右测量" in text
    assert "3.64" not in text
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
