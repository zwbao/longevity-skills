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


def test_relative_age_uses_fig4_lifespan():
    from presets import relative_age
    assert relative_age(15.5, "nmr") == 15.5 / 31
    assert relative_age(2, "mouse") == 0.5
    assert relative_age(61.25, "human") == 0.5


def test_methylation_age_needs_every_site(tmp_path: Path):
    from personal_report import INTERCEPT, WEIGHTS, methylation_age, years

    partial = tmp_path / "partial.txt"
    one = next(iter(WEIGHTS))
    partial.write_text(f"species=nmr\n{one},0.5\n", encoding="utf-8")
    text = personal_report.report(tmp_path / "partial-out", 31, None, None, partial).read_text(encoding="utf-8")
    assert "不填补，不算甲基化年龄" in text
    assert "甲基化年龄：这次没有算" in text

    full = tmp_path / "full.txt"
    full.write_text("".join(f"{site},0\n" for site in WEIGHTS), encoding="utf-8")
    scored = personal_report.report(tmp_path / "full-out", None, None, None, full).read_text(encoding="utf-8")
    assert f"甲基化年龄是 {years(INTERCEPT)} 岁" in scored
    assert methylation_age({site: __import__("decimal").Decimal("0") for site in WEIGHTS}) == INTERCEPT


def test_gene_list_omits_cartpt(tmp_path: Path):
    text = personal_report.report(tmp_path / "o", 31, None, None, None).read_text(encoding="utf-8")
    section = text.split("## 方法算出的名单", 1)[1].split("## 你正在使用的药", 1)[0]
    assert "Tert" in section and "Prpf19" in section
    assert "Cartpt" not in section
    assert "相对年龄是 1.0000" in text
    assert "3.133" not in text
    assert "11.87" not in text
    from presets import CROSSOVER_RELATIVE, CROSSOVER_YEARS
    assert CROSSOVER_YEARS == {"nmr": 11.87, "mouse": 1.66, "human": 70.69}
    assert CROSSOVER_RELATIVE["nmr"] == 0.383
