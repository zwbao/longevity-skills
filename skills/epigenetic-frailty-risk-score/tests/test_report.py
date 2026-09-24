import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import BOUNDARY


def _list_section(text: str) -> str:
    start = text.index("## 方法算出的名单")
    end = text.index("## 体检")
    return text[start:end]


def test_boundary_medicine_and_labs(tmp_path: Path):
    meds = tmp_path / "meds.txt"
    meds.write_text("不存在的药\n", encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n谷丙转氨酶,80,U/L\n", encoding="utf-8")
    out = personal_report.report(tmp_path / "out", 60, meds, labs, None)
    text = out.read_text(encoding="utf-8")
    assert text.rstrip().splitlines()[-1] == f"边界: {BOUNDARY}"
    assert "不能据此停" in text
    assert "谷丙转氨酶 80" in text
    assert "该开始" not in text
    assert "建议停" not in text
    bare = personal_report.report(tmp_path / "bare", 60, meds, None, None)
    assert _list_section(text) == _list_section(bare.read_text(encoding="utf-8"))


def test_fig4_equation():
    from presets import EFRS, efrs
    zeros = {site: 0.0 for site, _coef in EFRS if site != "intercept"}
    assert efrs(zeros) == 0.204
    betas = dict(zeros)
    betas["cg00921350"] = 1.0
    assert efrs(betas) == 0.204 - 0.209
    assert efrs({}) is None
    dropped = dict(zeros)
    del dropped["cg23458887"]
    assert efrs(dropped) is None


def test_deficit_proportion_uses_printed_denominators(tmp_path: Path):
    from presets import ESTHER_DEFICITS, KORA_DEFICITS, frailty_proportion
    assert ESTHER_DEFICITS == 31
    assert KORA_DEFICITS == 33
    assert frailty_proportion(0, 31) == 0
    assert frailty_proportion(8, 31) == 8 / 31
    assert frailty_proportion(34, 33) is None
    meas = tmp_path / "d.txt"
    meas.write_text("esther_deficits=8\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "d", 60, None, None, meas).read_text(encoding="utf-8")
    assert "没有风险分" in text
    assert "属于衰弱" in text
    assert "cg00921350" not in text


def test_fi_cut_does_not_edit_cpgs(tmp_path: Path):
    from presets import frailty_band
    assert frailty_band(0.10) == "非衰弱"
    assert frailty_band(0.20) == "衰弱前期"
    assert frailty_band(0.25) == "衰弱"
    meas = tmp_path / "m.txt"
    meas.write_text("fi=0.25\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "o", 60, None, None, meas).read_text(encoding="utf-8")
    assert "没有风险分" in text
    assert "cg00921350" not in text
