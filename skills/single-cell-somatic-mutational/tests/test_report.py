import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import (
    BOUNDARY,
    N_CELLS,
    NON_OA_SNV,
    OA_LESION_SNV,
    OA_NONLESION_INDEL_P,

)


def test_public_counts():
    assert N_CELLS == 100
    assert NON_OA_SNV == 56
    assert OA_LESION_SNV == 19
    assert OA_NONLESION_INDEL_P == 0.1170



def test_formula(tmp_path: Path):
    assert personal_report.mutation_burden(100, 0.5, 0.5) == 400
    meas = tmp_path / "measurements.csv"
    meas.write_text(
        "cell,group,observed_snv,coverage_snv,sensitivity_snv,observed_indel,coverage_indel,sensitivity_indel\n"
        "A,non_oa,100,0.5,0.5,10,0.4,0.5\n"
        "B,oa_lesion,100,0.5,0.1,10,0.4,0.1\n",
        encoding="utf-8",
    )
    text = personal_report.report(tmp_path / "out", None, None, meas).read_text(encoding="utf-8")
    assert "- A" in text
    assert "400" in text
    assert "- B" not in text



def _section(text: str, heading: str) -> str:
    lines = text.splitlines()
    start = lines.index(heading)
    end = start + 1
    while end < len(lines) and not lines[end].startswith("## "):
        end += 1
    return "\n".join(lines[start:end])


def test_report_boundary_meds_and_labs(tmp_path: Path):
    meas = tmp_path / "measurements.csv"
    meas.write_text('cell,group,observed_snv,coverage_snv,sensitivity_snv,observed_indel,coverage_indel,sensitivity_indel\nA,non_oa,100,0.5,0.5,10,0.4,0.5\n', encoding="utf-8")
    meds = tmp_path / "meds.txt"
    meds.write_text('布洛芬\n', encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n谷丙转氨酶,80,U/L\n", encoding="utf-8")
    bare = personal_report.report(tmp_path / "bare", None, None, meas)
    full = personal_report.report(tmp_path / "full", meds, labs, meas)
    text = full.read_text(encoding="utf-8")
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
    assert "不能据此停" in text
    assert '布洛芬' in text
    assert "谷丙转氨酶 80" in text
    assert "不增删" in text
    assert _section(text, "## 方法算出的名单") == _section(bare.read_text(encoding="utf-8"), "## 方法算出的名单")
    assert "该开始" not in text
    assert "建议停" not in text
    assert "建议开始" not in text
    title = text.splitlines()[0]
    assert title.startswith("# ")
    assert not any(ch.isdigit() for ch in title)
    assert "400" in text
    assert "- A" in text

