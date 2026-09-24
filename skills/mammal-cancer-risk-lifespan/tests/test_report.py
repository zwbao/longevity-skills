import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import BOUNDARY, N_INDIVIDUALS, N_NECROPSY, species_rows


def listed(body):
    grab = False
    rows = []
    for line in body.splitlines():
        if line.startswith("## "):
            if grab:
                break
            grab = line == "## 方法算出的名单"
            continue
        if grab:
            rows.append(line)
    return rows


def test_public_ratio():
    row = species_rows()["Acinonyx_jubatus"]
    assert abs(float(row["CMR"]) - 8 / 225) < 1e-12
    kowari = float(species_rows()["Dasyuroides_byrnei"]["CMR"])
    assert abs(kowari - 0.571428571428571) < 1e-12
    assert personal_report.cmr_ratio(8, 225) == 8 / 225
    assert N_INDIVIDUALS == 110148


def test_report_boundary_meds_and_labs(tmp_path: Path):
    meas = tmp_path / "measurements.csv"
    meas.write_text(
        "name,value\nspecies,kowari\nneoplasia,2\nknown_deaths,10\n",
        encoding="utf-8",
    )
    meds = tmp_path / "meds.txt"
    meds.write_text("布洛芬\n", encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n谷丙转氨酶,80,U/L\n", encoding="utf-8")
    bare = personal_report.report(tmp_path / "bare", meds, None, meas)
    full = personal_report.report(tmp_path / "full", meds, labs, meas)
    text = full.read_text(encoding="utf-8")
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
    assert "不能据此停" in text
    assert "布洛芬" in text
    assert "谷丙转氨酶 80 U/L" in text
    assert listed(text) == listed(bare.read_text(encoding="utf-8"))
    title = text.splitlines()[0]
    assert title.startswith("# ")
    assert not any(ch.isdigit() for ch in title)
    assert str(N_INDIVIDUALS) not in text
    assert str(N_NECROPSY) not in text
    assert "Dasyuroides_byrnei" in text
    assert "0.571429" in text
    assert "按计数的癌症死亡比例：0.2" in text
