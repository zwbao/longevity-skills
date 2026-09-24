import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report

def _opening(text: str) -> str:
    lines = text.splitlines()
    try:
        start = lines.index("## 论文卡片")
    except ValueError:
        return lines[2]
    for i in range(start + 1, len(lines)):
        if lines[i].startswith("## "):
            j = i - 1
            while j > start and lines[j] == "":
                j -= 1
            return lines[j]
    return lines[2]


from presets import *

def test_table1_and_hba1c(tmp_path: Path):
    assert UKB_N == 47600 and PROTEIN_ANALYTES == 1468 and ASSOCIATIONS == 3209
    assert len(TABLE1_CASES) == 24
    assert TABLE1_CASES["死亡"] == 4445 and TABLE1_CASES["2型糖尿病"] == 2822
    assert sum(1 for n in TABLE1_CASES.values() if n >= MIN_CASES) == PROTEIN_SCORES == 19
    assert len(FIG2B_OUTCOMES) == 6
    assert FEATURES_ENDOMETRIOSIS == 5 and FEATURES_MORTALITY == 201
    assert len(SCORE_WEIGHTS["子宫内膜异位症"]) == 5
    assert len(SCORE_WEIGHTS["死亡"]) == 201
    assert WEIGHTS_PRESENT is True
    meas = tmp_path / "m.csv"
    meas.write_text("item,value\nhba1c,50\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "out", None, None, meas).read_text(encoding="utf-8")
    assert "50 mmol/mol" in text
    assert "2型糖尿病" in text
    assert "0.89" not in text
    assert "标题不写" not in text



def test_endometriosis_linear_predictor(tmp_path: Path):
    feats = SCORE_WEIGHTS["子宫内膜异位症"]
    lines = ["item,value"] + [f"{gene},1" for gene, _pid, _coef in feats]
    meas = tmp_path / "m.csv"
    meas.write_text("\n".join(lines) + "\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "out", None, None, meas).read_text(encoding="utf-8")
    expected = sum(coef for _gene, _pid, coef in feats)
    assert f"{expected:.6f}" in text
    assert "子宫内膜异位症" in text
    section = _section(text, "## 方法算出的名单")
    assert "死亡" not in section
    assert "0.89" not in text


def _section(text: str, heading: str) -> str:
    lines = text.splitlines()
    start = lines.index(heading)
    end = start + 1
    while end < len(lines) and not lines[end].startswith("## "):
        end += 1
    return "\n".join(lines[start:end])


def test_report_boundary_meds_and_labs(tmp_path: Path):
    meds = tmp_path / "meds.txt"
    meds.write_text("不存在的药\n", encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n谷丙转氨酶,80,U/L\n", encoding="utf-8")
    bare = personal_report.report(tmp_path / "bare", None, None, None)
    full = personal_report.report(tmp_path / "full", meds, labs, None)
    text = full.read_text(encoding="utf-8")
    first = _opening(bare.read_text(encoding="utf-8"))
    assert first.endswith("。")
    assert "标题不写" not in first
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
    assert "不能据此停" in text
    assert "不存在的药" in text
    assert "谷丙转氨酶 80" in text
    assert "不增删" in text
    assert _section(text, "## 方法算出的名单") == _section(
        bare.read_text(encoding="utf-8"), "## 方法算出的名单"
    )
    assert "该开始" not in text
    assert "建议停" not in text
    assert "建议开始" not in text
    title = text.splitlines()[0]
    assert title.startswith("# ")
    assert not any(ch.isdigit() for ch in title)

