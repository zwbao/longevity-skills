import sys
from decimal import Decimal
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import personal_report
from presets import (
    ARTICLE_URL,
    BOUNDARY,
    BULK_SKIP,
    CODE_EACH_TAIL,
    CODE_SPLIT,
    CV_FOLDS,
    DOI_URL,
    FIGURES,
    FULL_TEXT_READ,
    IMM_SKIP,
    N_ALPHAS,
    PAGE_INPUT,
    PAPER_SPLIT,
    PAPER_TAIL_FRACTION,
    PT_SKIP,
    TABLE_S3_ROWS,
    TABLE_S3_URL,
    TAGE_INPUT,
    TCR_INPUT,
    UNREADABLE,
    aging_pace,
    linear_score,
)


def _section(text: str, heading: str) -> str:
    lines = text.splitlines()
    start = lines.index(heading)
    end = start + 1
    while end < len(lines) and not lines[end].startswith("## "):
        end += 1
    return "\n".join(lines[start:end])


def _write_zeros(path: Path, models, keys) -> None:
    lines = ["clock,cell_type,feature,value"]
    for key in keys:
        for feature in models[key]:
            if feature == "(Intercept)":
                continue
            lines.append(f"{key[0]},{key[1]},{feature},0")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_published_counts_stay_on_their_figures():
    assert FULL_TEXT_READ is True
    assert N_ALPHAS == 99
    assert CV_FOLDS == 10
    assert PAPER_SPLIT != CODE_SPLIT
    assert PAPER_TAIL_FRACTION == Decimal("0.20")
    assert CODE_EACH_TAIL == 21
    assert int(Decimal(230) * PAPER_TAIL_FRACTION) != CODE_EACH_TAIL
    by_figure = {(fig, metric): value for fig, _what, metric, value in FIGURES}
    assert by_figure[("图2B", "MAE")] == Decimal("8.48")
    assert by_figure[("图2C", "MAE")] == Decimal("4.96")
    assert by_figure[("图2E", "MAE")] == Decimal("5.44")
    assert by_figure[("图S2A", "MAE")] == Decimal("12.07")
    assert by_figure[("图2F", "R")] == Decimal("0.90")
    assert by_figure[("图2F", "MAE")] == Decimal("5.66")
    assert by_figure[("图2H", "R")] == Decimal("0.89")
    models = personal_report.load_models()
    assert sum(len(coefs) for coefs in models.values()) == TABLE_S3_ROWS
    assert models[("tAge", "Th2")]["(Intercept)"] == Decimal("31.91935275")
    assert models[("tAge", "Th2")]["AAGAB"] == Decimal("0.253516632")
    assert models[("pAge", "")]["(Intercept)"] == Decimal("65.41807581")
    assert models[("TCRAge", "")]["gender"] == Decimal("7.769725047")


def test_linear_score_uses_every_coefficient():
    coefs = {"(Intercept)": Decimal("10"), "A": Decimal("2"), "B": Decimal("-1")}
    assert linear_score(coefs, {"A": Decimal("3"), "B": Decimal("4")}) == Decimal("12")
    zeros = aging_pace(
        [Decimal(0), Decimal(1), Decimal(2)],
        [Decimal(1), Decimal(3), Decimal(5)],
    )
    assert zeros == [Decimal(0), Decimal(0), Decimal(0)]
    assert "aging_pace(" not in Path(personal_report.__file__).read_text(encoding="utf-8")


def test_scores_complete_inputs_and_keeps_the_card(tmp_path: Path):
    models = personal_report.load_models()
    sheet = tmp_path / "features.csv"
    _write_zeros(sheet, models, [("pAge", ""), ("tAge", "Th2"), ("TCRAge", "")])
    text = personal_report.report(tmp_path / "out", 60, None, None, sheet, sex="女").read_text(encoding="utf-8")
    assert text.splitlines()[0] == "# 免疫衰老时钟"
    assert not any(ch.isdigit() for ch in text.splitlines()[0])
    assert ARTICLE_URL in text
    assert DOI_URL in text
    assert TABLE_S3_URL in text
    assert "RUNX1 在 T 细胞里随年龄下降" in text
    assert "pAge：65.42 岁。" + PAGE_INPUT in text
    assert "tAge（Th2）：31.92 岁。" + TAGE_INPUT in text
    assert "TCRAge：70.74 岁。" + TCR_INPUT in text
    assert PT_SKIP in text
    assert IMM_SKIP in text
    assert BULK_SKIP in text
    assert "65.41807581" not in text
    for _fig, _what, _metric, value in FIGURES:
        assert str(value) not in text
    male = personal_report.report(tmp_path / "male", 60, None, None, sheet, sex="男").read_text(encoding="utf-8")
    male_score = linear_score(
        models[("TCRAge", "")],
        {name: Decimal(0) for name in models[("TCRAge", "")] if name != "(Intercept)"} | {"gender": Decimal(1)},
    )
    assert f"TCRAge：{personal_report.years(male_score)}" in male
    assert _section(text, "## 这次算出的时钟") != _section(male, "## 这次算出的时钟")


def test_incomplete_input_is_not_scored(tmp_path: Path):
    sheet = tmp_path / "partial.csv"
    sheet.write_text(
        "clock,cell_type,feature,value\npAge,,cMC,1\ntAge,Th2,AAGAB,1\nimmAge,,Tn_CD8,0.2\n",
        encoding="utf-8",
    )
    text = personal_report.report(tmp_path / "out", 60, None, None, sheet, sex="女").read_text(encoding="utf-8")
    clock = _section(text, "## 这次算出的时钟")
    assert "pAge：缺" in clock
    assert "没有算" in clock
    assert "65.42" not in text
    assert "75.42" not in text
    assert "31.92" not in text
    assert IMM_SKIP in text
    assert "Tn_CD8" not in clock.split("immAge")[0]


def test_boundary_medicine_labs_and_unreadable(tmp_path: Path):
    models = personal_report.load_models()
    sheet = tmp_path / "features.csv"
    _write_zeros(sheet, models, [("pAge", "")])
    extra = tmp_path / "with_gene.csv"
    extra.write_text(sheet.read_text(encoding="utf-8") + "tAge,Th2,RUNX1,1\n", encoding="utf-8")
    meds = tmp_path / "meds.txt"
    meds.write_text("不存在的药\n", encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n谷丙转氨酶,80,U/L\n", encoding="utf-8")
    bare = personal_report.report(tmp_path / "bare", 60, meds, None, sheet, sex="女")
    full = personal_report.report(tmp_path / "full", 60, meds, labs, sheet, sex="女")
    text = full.read_text(encoding="utf-8")
    bare_text = bare.read_text(encoding="utf-8")
    assert text.rstrip().splitlines()[-1] == f"边界: {BOUNDARY}"
    assert "不能据此停" in text
    assert "谷丙转氨酶 80" in text
    assert "不增删" in text
    assert "该开始" not in text
    assert "建议停" not in text
    assert "建议开始" not in text
    assert _section(text, "## 方法算出的名单") == _section(bare_text, "## 方法算出的名单")
    assert _section(text, "## 这次算出的时钟") == _section(bare_text, "## 这次算出的时钟")
    assert "名单是空的。" in _section(text, "## 方法算出的名单")
    gene_text = personal_report.report(tmp_path / "gene", 60, meds, labs, extra, sex="女").read_text(encoding="utf-8")
    assert "RUNX1" not in _section(gene_text, "## 方法算出的名单")
    pdf = tmp_path / "clock.pdf"
    pdf.write_bytes(b"%PDF-1.4")
    unread = personal_report.report(tmp_path / "pdf", None, None, None, pdf).read_text(encoding="utf-8")
    assert UNREADABLE in unread
    assert "65.42" not in unread
    assert DOI_URL in unread
    assert "全文不在手边" not in text
    assert "生物年龄是" not in text
    assert "免疫年龄是" not in text
