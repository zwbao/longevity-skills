import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import BOUNDARY, CTBA_IPA, DEMOGRAPHIC_IPA, HR_Q4_VS_Q1, IPA_DROP, TABLE2


def test_table2_male_40_matches_figure_case():
    alive, dead = TABLE2["male"]["40-59"]["muscle_density"]
    assert (alive, dead) == (40, 34)
    assert IPA_DROP["muscle_density"] == 5.1
    assert CTBA_IPA == 29.2
    assert DEMOGRAPHIC_IPA == 21.7
    assert HR_Q4_VS_Q1 == 8.73


def test_case_example_orders_by_ipa_drop(tmp_path: Path):
    meas = tmp_path / "ct.csv"
    meas.write_text(
        "name,value\nsex,male\nmuscle_density,32.9\naortic_calcium,12342\n"
        "visceral_fat_density,-88.7\nbone_density,110\nvsr,1.99\n",
        encoding="utf-8",
    )
    meds = tmp_path / "meds.txt"
    meds.write_text("阿司匹林肠溶片\n", encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n谷丙转氨酶,80,U/L\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "out", meas, meds, labs, 55).read_text(encoding="utf-8")
    assert text.endswith(f"边界: {BOUNDARY}\n")
    assert "不能据此停" in text
    assert "谷丙转氨酶 80 U/L" in text
    numbered = [line for line in text.splitlines() if line[:2] in {"1.", "2.", "3.", "4.", "5.", "6.", "7.", "8."}]
    assert numbered[0].startswith("1. 骨骼肌密度")
    assert "腹主动脉钙化积分" in numbered[1]
    assert "内脏脂肪与皮下脂肪比值" not in "\n".join(numbered)
    assert "该开始" not in text
    assert "建议停" not in text
    bare = personal_report.report(tmp_path / "bare", meas, meds, None, 55).read_text(encoding="utf-8")
    def listed(body: str) -> list[str]:
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
    assert listed(text) == listed(bare)


def test_blank_run(tmp_path: Path):
    text = personal_report.report(tmp_path / "blank", None, None, None).read_text(encoding="utf-8")
    assert text.splitlines()[0] == "# 腹部影像生物标志"
    assert not any(ch.isdigit() for ch in text.splitlines()[0])
    assert "这次没有提供年龄和影像测量" in text
    assert "8.73" not in text
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
