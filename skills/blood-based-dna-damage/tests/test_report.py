import math
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import (
    BOUNDARY,
    FIG4A_DOWN_MEDIAN_BP,
    FIG4A_P,
    FIG4A_UP_N,
    FIG4B_DOWN_N,
    FIG4B_P,
    LOG2FC_ABS,
    PADJ_MAX,
    SEVERE_N,
    VISIT1_PD,
)


def test_public_counts():
    assert VISIT1_PD == 484
    assert FIG4A_UP_N == 576
    assert FIG4A_DOWN_MEDIAN_BP == 19076
    assert FIG4A_P == 0.0555
    assert FIG4B_DOWN_N == 229
    assert FIG4B_P == 0.0011
    assert SEVERE_N == 226
    assert LOG2FC_ABS == 0.322
    assert PADJ_MAX == 0.05


def test_length_bias_direction(tmp_path: Path):
    meas = tmp_path / "measurements.csv"
    meas.write_text(
        "gene,log2fc,padj,length_bp\n"
        "SHORT,1.0,0.01,1000\n"
        "ALSO,0.5,0.01,3000\n"
        "LONG,-1.2,0.001,80000\n"
        "LONGER,-0.9,0.02,120000\n"
        "SKIP,0.1,0.01,90000\n",
        encoding="utf-8",
    )
    text = personal_report.report(tmp_path / "out", None, None, meas).read_text(encoding="utf-8")
    assert "SKIP" not in text
    assert "下调基因更长" in text
    assert "80000" in text or "80,000" in text or "100000" in text or "中位长度 100000" in text
    assert "Fig. 4b" in text
    p_value = personal_report.mann_whitney_p([1, 2, 3], [4, 5, 6])
    assert p_value == 0.1


def _section(text: str, heading: str) -> str:
    lines = text.splitlines()
    start = lines.index(heading)
    end = start + 1
    while end < len(lines) and not lines[end].startswith("## "):
        end += 1
    return "\n".join(lines[start:end])


def test_report_boundary_meds_and_labs(tmp_path: Path):
    meas = tmp_path / "measurements.csv"
    meas.write_text(
        "gene,log2fc,padj,length_bp\nSHORT,1,0.01,1000\nLONG,-1,0.01,90000\n",
        encoding="utf-8",
    )
    meds = tmp_path / "meds.txt"
    meds.write_text("左旋多巴\n", encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n谷丙转氨酶,80,U/L\n", encoding="utf-8")
    bare = personal_report.report(tmp_path / "bare", None, None, meas)
    full = personal_report.report(tmp_path / "full", meds, labs, meas)
    text = full.read_text(encoding="utf-8")
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
    assert "不能据此停" in text
    assert "左旋多巴" in text
    assert "谷丙转氨酶 80" in text
    assert "不增删" in text
    assert _section(text, "## 方法算出的名单") == _section(bare.read_text(encoding="utf-8"), "## 方法算出的名单")
    assert "该开始" not in text
    assert "建议停" not in text
    assert "建议开始" not in text
    title = text.splitlines()[0]
    assert title.startswith("# ")
    assert not any(ch.isdigit() for ch in title)
    assert math.isfinite(personal_report.mann_whitney_p([10.0], [20.0]))
