import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import BOUNDARY, ELB_K, ELB_MIN, N_CRYPTS, N_INDIVIDUALS, species_table


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


def test_public_numbers():
    human = species_table()["Human"]
    assert abs(human["rate"] - 47.1245407279692) < 1e-6
    assert abs(human["lifespan_80"] - 83.66666667) < 1e-4
    assert abs(species_table()["Mouse"]["rate"] - 796.423850330549) < 1e-6
    assert ELB_K == 3206.4
    assert N_CRYPTS == 208
    assert personal_report.per_year(100, 10) == 10
    assert abs(personal_report.model_rate(human["lifespan_80"]) - ELB_K / human["lifespan_80"]) < 1e-9


def test_report_boundary_meds_and_labs(tmp_path: Path):
    meas = tmp_path / "measurements.csv"
    meas.write_text("name,value\nspecies,human\nsubstitution_burden,100\n", encoding="utf-8")
    meds = tmp_path / "meds.txt"
    meds.write_text("布洛芬\n", encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n谷丙转氨酶,80,U/L\n", encoding="utf-8")
    bare = personal_report.report(tmp_path / "bare", meds, None, meas, 10)
    full = personal_report.report(tmp_path / "full", meds, labs, meas, 10)
    text = full.read_text(encoding="utf-8")
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
    assert "不能据此停" in text
    assert "布洛芬" in text
    assert "谷丙转氨酶 80 U/L" in text
    assert listed(text) == listed(bare.read_text(encoding="utf-8"))
    title = text.splitlines()[0]
    assert title.startswith("# ")
    assert not any(ch.isdigit() for ch in title)
    assert str(N_CRYPTS) not in text
    assert str(N_INDIVIDUALS) not in text
    assert str(ELB_MIN) not in text
    assert "隐窝年替换率：10" in text
    assert "3206.4" in text
