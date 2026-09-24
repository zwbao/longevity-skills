import sys
from decimal import Decimal
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import BOUNDARY, DOSE_MG_PER_KG, OLD_OVER_YOUNG, PROTEOME_PXD, nucleus_ratio

SAMPLE = """name,value
sirt2_nucleus,9
sirt2_total,27
"""


def _section(text: str, heading: str) -> str:
    lines = text.splitlines()
    start = lines.index(heading)
    end = start + 1
    while end < len(lines) and not lines[end].startswith("## "):
        end += 1
    return "\n".join(lines[start:end])


def test_ratio():
    assert nucleus_ratio(Decimal("9"), Decimal("27")) == Decimal("9") / Decimal("27")
    assert nucleus_ratio(Decimal("1"), Decimal("0")) is None
    assert DOSE_MG_PER_KG == 10
    assert OLD_OVER_YOUNG == "1/3"


def test_report_boundary_meds_and_labs(tmp_path: Path):
    meds = tmp_path / "meds.txt"
    meds.write_text("阿司匹林\n烟酰胺单核苷酸\n", encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n谷丙转氨酶,80,U/L\n", encoding="utf-8")
    meas = tmp_path / "measurements.csv"
    meas.write_text(SAMPLE, encoding="utf-8")
    bare = personal_report.report(tmp_path / "bare", None, None, meas, 70)
    full = personal_report.report(tmp_path / "full", meds, labs, meas, 70)
    text = full.read_text(encoding="utf-8")
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
    assert "不能据此停" in text
    assert "谷丙转氨酶 80" in text
    assert "不增删" in text
    assert _section(text, "## 方法算出的名单") == _section(
        bare.read_text(encoding="utf-8"), "## 方法算出的名单"
    )
    assert "该开始" not in text
    assert "建议停" not in text
    title = text.splitlines()[0]
    assert title.startswith("# ")
    assert not any(ch.isdigit() for ch in title)
    assert "核内比总量：0.3333。" in text
    assert "这个名字出现在名单里。不能据此停。" in text
    assert "阿司匹林：名单里没有这个名字。不能据此停。" in text
    assert OLD_OVER_YOUNG not in text
    assert PROTEOME_PXD not in text
    assert "10 mg/kg" not in text
