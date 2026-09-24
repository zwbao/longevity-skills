import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import BOUNDARY, CLOCKS, DOSE, RANDOMIZED_N


def test_published_effects():
    assert RANDOMIZED_N == 220
    assert CLOCKS["DunedinPACE"]["m12"][0] == -0.29
    assert CLOCKS["DunedinPACE"]["m24"][0] == -0.25
    assert CLOCKS["PCPhenoAge"]["m24"][0] == 0.05
    assert CLOCKS["PCGrimAge"]["m12"][0] == -0.04
    assert CLOCKS["PCGrimAge"]["m24"][2] == 0.17
    assert DOSE["iv20_m12"][0] == -0.43


def test_report_keeps_clocks(tmp_path: Path):
    clocks = tmp_path / "clocks.csv"
    clocks.write_text("name,value\nDunedinPACE,0.95\n", encoding="utf-8")
    meds = tmp_path / "meds.txt"
    meds.write_text("不存在的药\n", encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n谷丙转氨酶,80,U/L\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "out", clocks, meds, labs).read_text(encoding="utf-8")
    bare = personal_report.report(tmp_path / "bare", clocks, None, None).read_text(encoding="utf-8")
    assert f"边界: {BOUNDARY}" in text
    assert "不能据此停" in text
    assert "0.95" in text
    assert "-0.29" in text
    assert "-0.25" not in text
    assert "谷丙转氨酶 80" in text
    assert "不增删方法算出的名单" in text
    assert "该开始" not in text
    assert "建议停" not in text
    assert _clocks(bare) == _clocks(text)


def _clocks(text: str) -> list[str]:
    return [line for line in text.splitlines() if line.startswith("- Dunedin") or line.startswith("- PC ")]


def test_blank_run(tmp_path: Path):
    text = personal_report.report(tmp_path / "blank").read_text(encoding="utf-8")
    assert text.splitlines()[0] == "# 限食试验时钟"
    assert "这次没有给出时钟数值" in text
    assert "-0.29" not in text
    assert "-0.43" not in text
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
