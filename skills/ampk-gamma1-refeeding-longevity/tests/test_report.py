import sys
from decimal import Decimal
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import BOUNDARY, PBMC_DONORS, R2_ON_FIGURE, mpi_group

SAMPLE = """name,value
adl,0.5
iadl,0.5
spmsq,0.5
cirs_ci,0.5
mna_sf,0.5
ess,0.5
nm,0.5
social,0.5
prkag1,1.2
"""


def _section(text: str, heading: str) -> str:
    lines = text.splitlines()
    start = lines.index(heading)
    end = start + 1
    while end < len(lines) and not lines[end].startswith("## "):
        end += 1
    return "\n".join(lines[start:end])


def test_bins():
    assert mpi_group(Decimal("0")) == "MPI-1"
    assert mpi_group(Decimal("0.33")) == "MPI-1"
    assert mpi_group(Decimal("0.335")) == "gap"
    assert mpi_group(Decimal("0.5")) == "MPI-2"
    assert mpi_group(Decimal("0.66")) == "MPI-2"
    assert mpi_group(Decimal("0.665")) == "cutoff_conflict"
    assert mpi_group(Decimal("0.67")) == "MPI-3"
    assert mpi_group(Decimal("1")) == "MPI-3"
    assert PBMC_DONORS == 93


def test_report_boundary_meds_and_labs(tmp_path: Path):
    meds = tmp_path / "meds.txt"
    meds.write_text("阿司匹林\n", encoding="utf-8")
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
    assert "预后指数：0.5，MPI-2（衰弱前期）。" in text
    assert "缺斜率和截距" in text
    assert str(PBMC_DONORS) not in text
    assert R2_ON_FIGURE[0] not in text
