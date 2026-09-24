import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import BOUNDARY, FRAIL_N, HR_VS_I, METABOLITES, SUBTYPE_N, XGB_AUC_TEST


def _write_means(path: Path, group_index: int) -> None:
    lines = ["name,value"]
    for key, row in METABOLITES.items():
        lines.append(f"{key},{row['mean'][group_index]}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_subtype_counts_and_published_hr():
    assert sum(SUBTYPE_N.values()) == FRAIL_N
    assert HR_VS_I["2型糖尿病"]["III"][0] == 2.24
    assert HR_VS_I["2型糖尿病"]["IV"][0] == 3.00
    assert HR_VS_I["COPD"]["IV"][0] == 1.15
    assert XGB_AUC_TEST == 0.757


def test_table2_means_land_on_that_subtype(tmp_path: Path):
    mets = tmp_path / "mets.csv"
    _write_means(mets, 5)
    nearest, distances = personal_report.nearest_subtype(personal_report.load_metabolites(mets))
    assert nearest == "IV"
    assert distances["IV"] == 0.0
    _write_means(mets, 2)
    nearest, _ = personal_report.nearest_subtype(personal_report.load_metabolites(mets))
    assert nearest == "I"


def test_report_keeps_boundary_and_does_not_drop_subtype(tmp_path: Path):
    mets = tmp_path / "mets.csv"
    _write_means(mets, 5)
    meds = tmp_path / "meds.txt"
    meds.write_text("阿司匹林肠溶片\n不存在的药\n", encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n谷丙转氨酶,80,U/L\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "out", mets, meds, labs, 0.25, None).read_text(encoding="utf-8")
    bare = personal_report.report(tmp_path / "bare", mets, None, None, None, None).read_text(encoding="utf-8")
    assert f"边界: {BOUNDARY}" in text
    assert "不能据此停" in text
    assert "亚型 IV" in text
    assert "谷丙转氨酶 80" in text
    assert "不增删方法算出的名单" in text
    assert "该开始" not in text
    assert "建议停" not in text
    assert _subtype_line(bare) == _subtype_line(text)


def _subtype_line(text: str) -> str:
    return next(line for line in text.splitlines() if line.startswith("- ") and "最近的是亚型" in line)


def test_blank_run(tmp_path: Path):
    text = personal_report.report(tmp_path / "blank").read_text(encoding="utf-8")
    assert text.splitlines()[0] == "# 代谢衰弱亚型"
    assert not any(ch.isdigit() for ch in text.splitlines()[0])
    assert "这次没有给出全部十一个核磁共振代谢物" in text
    assert "1.25" not in text
    assert "## 你正在使用的药" in text
    assert "## 体检" in text
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
