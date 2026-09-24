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


from presets import (
    BONFERRONI_P,
    BOUNDARY,
    EBMD_COEF,
    EBMD_OFFSET,
    FRAX_CINDEX,
    FRAX_PLUS_CINDEX,
    HUNT_COMBINED_HR,
    N_APTAMERS_AFTER_EXCLUSION,
    N_WEIGHTED_PROTEINS,
    ELASTIC,
    LASSO,
    WEIGHTED,
    WEIGHTS_PRESENT,
    ebmd,
    score_panel,
)


def test_public_counts():
    assert BONFERRONI_P == 1.0e-5
    assert N_WEIGHTED_PROTEINS == 18
    assert N_APTAMERS_AFTER_EXCLUSION == 4979
    assert FRAX_CINDEX == 0.735
    assert FRAX_PLUS_CINDEX == 0.776
    assert HUNT_COMBINED_HR == 1.56
    assert WEIGHTS_PRESENT is True
    assert len(WEIGHTED) == 18
    assert len(LASSO) == 22
    assert len(ELASTIC) == 20
    assert WEIGHTED[0][6] == -0.327935708
    ghr = score_panel(WEIGHTED, [("GHR", 1.0), ("KLK3", 1.0), ("SERPINA3", 1.0)])
    assert ghr is not None
    assert abs(ghr[0] - (-0.327935708 + 0.23252896)) < 1e-12
    assert len(ghr[1]) == 2
    assert ebmd(100, 1500) == EBMD_COEF * (100 + 1500) - EBMD_OFFSET


def test_ebmd_and_missing_weights(tmp_path: Path):
    meas = tmp_path / "measurements.csv"
    meas.write_text(
        "item,value,flag\nbua,100,\nsos,1500,\nSOST,12,deprecated\nCXCL9,1.5,\n",
        encoding="utf-8",
    )
    text = personal_report.report(tmp_path / "out", None, None, meas).read_text(encoding="utf-8")
    assert f"{ebmd(100, 1500):.4f}" in text
    assert "蛋白风险分没有算出" in text
    assert "1.56" not in text
    assert "Supplementary" not in text
    assert "建议停" not in text


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
    assert "标题不写" not in text
    assert "这篇论文的个人读出" not in text
    assert _opening(text) == "没有对上蛋白风险分里的蛋白，也没有足跟超声的两个读数，所以这次没有算出蛋白风险分，也没有算出超声骨密度。"


def test_one_protein_uses_published_betas(tmp_path: Path):
    meas = tmp_path / "measurements.csv"
    meas.write_text("item,value\nGHR,1\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "out", None, None, meas).read_text(encoding="utf-8")
    assert "加权蛋白风险分是 -0.3279" in text
    assert "套索蛋白风险分是 -0.0026" in text
    assert "弹性网蛋白风险分是 0.0033" in text
    assert "生长激素受体" in text
    assert "1.56" not in text
    assert "0.735" not in text
