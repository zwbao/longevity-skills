import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import comorbidity_index, self_health_index, smoking_score
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


def test_published_indices():
    assert smoking_score(9.9) == (0, "不吸烟")
    assert smoking_score(10)[0] == 1
    assert smoking_score(100)[0] == 2
    assert smoking_score(200)[0] == 3
    assert self_health_index(0, 1, 0, 1) == 8
    index, present = comorbidity_index(["高血压", "糖尿病", "不在二十二项里"])
    assert present == ["hypertension", "diabetes mellitus"]
    assert index == 2 / 22
    from presets import (
        ASCVD_AUC_20Y,
        CHRONAGE_AUC_20Y,
        COMORBIDITIES,
        LINAGE_AUC_20Y,
        PCAGE_AUC_20Y,
    )
    assert len(COMORBIDITIES) == 22
    assert PCAGE_AUC_20Y == 0.8643
    assert LINAGE_AUC_20Y == 0.8655
    assert ASCVD_AUC_20Y == 0.7594
    assert CHRONAGE_AUC_20Y == 0.8289


def test_medicine_does_not_add_a_comorbidity(tmp_path: Path):
    meas = tmp_path / "m.txt"
    meas.write_text("comorbidity=hypertension\ncotinine_ng_ml=10\n", encoding="utf-8")
    meds = tmp_path / "meds.txt"
    meds.write_text("高血压\n不存在的药\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "out", 60, meds, None, meas).read_text(encoding="utf-8")
    assert "- 高血压" in text
    assert "不能据此停" in text
    assert "并存病指数" in text
    assert "LinAge" not in text
    huq = tmp_path / "huq.txt"
    huq.write_text("huq050=4\n", encoding="utf-8")
    huq_text = personal_report.report(tmp_path / "huq", 60, None, None, huq).read_text(encoding="utf-8")
    assert "就医使用指数：4" in huq_text
    title = text.splitlines()[0]
    assert not any(ch.isdigit() for ch in title)
