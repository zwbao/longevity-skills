import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import BOUNDARY, MATURITY_YEARS, N_SAMPLES, models


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
    blood = models()["blood"]
    assert blood["intercept"] == 35.60282572
    assert len(blood["weights"]) == 40
    assert len(models()["pan1"]["weights"]) == 47
    assert personal_report.f_inverse(0) == MATURITY_YEARS
    assert personal_report.f_inverse(1) == 11.5
    zeros = {cg: 0.0 for cg in blood["weights"]}
    age, missing = personal_report.predict("blood", zeros)
    assert missing == []
    assert age == blood["intercept"]
    partial = dict(zeros)
    partial.pop(next(iter(partial)))
    assert personal_report.predict("blood", partial)[0] is None


def test_report_boundary_meds_and_labs(tmp_path: Path):
    weights = models()["blood"]["weights"]
    rows = ["name,value", "tissue,blood", "queen,yes"]
    rows.extend(f"{cg},0" for cg in weights)
    meas = tmp_path / "measurements.csv"
    meas.write_text("\n".join(rows) + "\n", encoding="utf-8")
    meds = tmp_path / "meds.txt"
    meds.write_text("布洛芬\n", encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n谷丙转氨酶,80,U/L\n", encoding="utf-8")
    bare = personal_report.report(tmp_path / "bare", meds, None, meas, None)
    full = personal_report.report(tmp_path / "full", meds, labs, meas, None)
    text = full.read_text(encoding="utf-8")
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
    assert "不能据此停" in text
    assert "布洛芬" in text
    assert "谷丙转氨酶 80 U/L" in text
    assert listed(text) == listed(bare.read_text(encoding="utf-8"))
    title = text.splitlines()[0]
    assert title.startswith("# ")
    assert not any(ch.isdigit() for ch in title)
    assert str(N_SAMPLES) not in text
    assert "35.6028" in text
    assert "交互系数" in text
    assert "不把缺的位点补 0" not in text
