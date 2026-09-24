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


from presets import BOUNDARY


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
    assert _opening(text) == "没有提供性别，所以这次没有算出细胞类型的预测年龄。"


def test_adipocyte_uses_published_weights(tmp_path: Path):
    meas = tmp_path / "measurements.csv"
    meas.write_text(
        "item,value\n"
        "sex,女\n"
        "TNMD.6578.29,1\n"
        "SEMA3G.5628.21,1\n"
        "NRP1.5542.22,1\n"
        "MEOX2.23039.56,1\n",
        encoding="utf-8",
    )
    found, _proteins, sex = personal_report.scored(personal_report.read_rows(meas))
    names = [item[0] for item in found]
    assert sex == 1
    assert "Adipocytes" in names
    adipocyte = next(item for item in found if item[0] == "Adipocytes")
    assert f"{adipocyte[1]:.2f}" == "74.45"
    text = personal_report.report(tmp_path / "out", None, None, meas).read_text(encoding="utf-8")
    assert "Adipocytes：预测年龄 74.45 岁" in text
    assert "算不出年龄差" in text
    assert "0.25" not in text
    assert "建议停" not in text


def test_three_proteins_do_not_score(tmp_path: Path):
    meas = tmp_path / "measurements.csv"
    meas.write_text("item,value\nsex,男\nTNMD.6578.29,1\nSEMA3G.5628.21,1\nNRP1.5542.22,1\n", encoding="utf-8")
    found, _proteins, _sex = personal_report.scored(personal_report.read_rows(meas))
    assert found == []
