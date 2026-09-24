import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report

def _opening(text: str) -> str:
    lines = text.splitlines()
    try:
        start = lines.index("## 论文卡片")
    except ValueError:
        return lines[2]
    for i in range(start + 1, len(lines)):
        if lines[i].startswith("## "):
            j = i - 1
            while j > start and lines[j] == "":
                j -= 1
            return lines[j]
    return lines[2]


from presets import BOUNDARY

from presets import (
    BOTTOM5_PROTAGEGAP_YEARS,
    CKB_N,
    CKB_R,
    CKB_R2,
    FINNGEN_N,
    FINNGEN_R,
    PANEL_PROTEINS,
    PROTAGE_PROTEINS,
    PROTAGE20_R,
    PROTEINS,
    TEST_N,
    TEST_R,
    TEST_R2,
    TOP5_PROTAGEGAP_YEARS,
    UKB_N,
)


def test_public_counts():
    assert UKB_N == 45441
    assert TEST_N == 13633
    assert CKB_N == 3977
    assert FINNGEN_N == 1990
    assert PANEL_PROTEINS == 2897
    assert len(PROTEINS) == PROTAGE_PROTEINS == 204
    assert PROTEINS["ADA"] == "Adenosine deaminase"
    assert PROTEINS["ACRV1"] == "Acrosomal protein SP-10"
    assert TEST_R == 0.94 and TEST_R2 == 0.88
    assert CKB_R == 0.92 and CKB_R2 == 0.82
    assert FINNGEN_R == 0.94
    assert PROTAGE20_R == 0.89
    assert TOP5_PROTAGEGAP_YEARS == 6.3
    assert BOTTOM5_PROTAGEGAP_YEARS == -6.0


def test_gap_uses_supplied_protage_not_shap(tmp_path: Path):
    meas = tmp_path / "measurements.csv"
    meas.write_text("item,value\nprotage,71.3\nADA,10\n", encoding="utf-8")
    path = personal_report.report(tmp_path / "out", None, None, meas, 65)
    text = path.read_text(encoding="utf-8")
    assert "6.3 年" in text
    assert "Adenosine deaminase" in text
    assert "P00813" not in text
    assert "前 5%" in text
    assert "SHAP" not in text
    assert "45441" not in text
    assert "标题不写" not in text


def _section(text: str, heading: str) -> str:
    lines = text.splitlines()
    start = lines.index(heading)
    end = start + 1
    while end < len(lines) and not lines[end].startswith("## "):
        end += 1
    return "\n".join(lines[start:end])


def test_report_boundary_meds_and_labs(tmp_path: Path):
    meds = tmp_path / "meds.txt"
    meds.write_text("不存在的药\n", encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n谷丙转氨酶,80,U/L\n", encoding="utf-8")
    bare = personal_report.report(tmp_path / "bare", None, None, None)
    full = personal_report.report(tmp_path / "full", meds, labs, None)
    text = full.read_text(encoding="utf-8")
    first = _opening(bare.read_text(encoding="utf-8"))
    assert first.endswith("。")
    assert "标题不写" not in first
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
    assert "不能据此停" in text
    assert "不存在的药" in text
    assert "谷丙转氨酶 80" in text
    assert "不增删" in text
    assert _section(text, "## 方法算出的名单") == _section(
        bare.read_text(encoding="utf-8"), "## 方法算出的名单"
    )
    assert "该开始" not in text
    assert "建议停" not in text
    assert "建议开始" not in text
    title = text.splitlines()[0]
    assert title.startswith("# ")
    assert not any(ch.isdigit() for ch in title)
