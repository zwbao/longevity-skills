"""Readings on synthetic genotypes; wording rules (no doses, APOE only on request)."""

import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report  # noqa: E402

HEADER = "# rsid\tchromosome\tposition\tgenotype\n"


def run(tmp_path, rows, apoe=False):
    path = tmp_path / "genome.txt"
    path.write_text(HEADER + "".join(f"{rsid}\t1\t1\t{genotype}\n" for rsid, genotype in rows), encoding="utf-8")
    text = personal_report.write_report(tmp_path / "out", path, apoe).read_text(encoding="utf-8")
    result = json.loads((tmp_path / "out" / "result.json").read_text(encoding="utf-8"))
    return text, {key: item["value"] for key, item in result["outputs"].items()}


@pytest.mark.parametrize("genotype, copies", [("GG", 0), ("GA", 1), ("AG", 1), ("AA", 2)])
def test_aldh2_copies(tmp_path, genotype, copies):
    _, out = run(tmp_path, [("rs671", genotype)])
    assert out["aldh2_rs671_copies"] == copies


def test_aldh2_heterozygote_reading_and_action(tmp_path):
    """Brooks 2009: heterozygote ORs 3.7 to 18.1; 'high-risk patients can be assessed for endoscopic cancer screening'."""
    text, _ = run(tmp_path, [("rs671", "GA")])
    section = text.split("## 喝酒", 1)[1].split("## ", 1)[0]
    assert "3.7–18.1" in section
    assert "可以考虑不喝或少喝酒" in section and "胃镜" in section


def test_mthfr_tt_suggests_a_homocysteine_test_not_a_supplement_dose(tmp_path):
    text, out = run(tmp_path, [("rs1801133", "AA")])
    assert out["mthfr_rs1801133_copies"] == 2
    section = text.split("## 叶酸", 1)[1].split("## ", 1)[0]
    assert "可以考虑查一次血同型半胱氨酸" in section
    assert "ACMG" in section


def test_mthfr_ct_has_no_action(tmp_path):
    text, _ = run(tmp_path, [("rs1801133", "GA")])
    section = text.split("## 叶酸", 1)[1].split("## ", 1)[0]
    assert "可以考虑" not in section


def test_lactase_gg_says_the_site_does_not_separate_chinese_people(tmp_path):
    text, out = run(tmp_path, [("rs4988235", "GG")])
    assert out["lct_rs4988235_copies"] == 0
    assert "区分不了" in text


def test_strand_mismatch_is_not_read(tmp_path):
    text, out = run(tmp_path, [("rs671", "CT")])
    assert out["aldh2_rs671_copies"] is None
    assert "链方向" in text


def test_apoe_is_off_by_default(tmp_path):
    text, out = run(tmp_path, [("rs671", "GG"), ("rs429358", "TC"), ("rs7412", "CC")])
    assert out["apoe_genotype"] is None
    assert "ε4" not in text and "ε3" not in text


@pytest.mark.parametrize("r1, r2, expected", [
    ("TT", "CC", "ε3/ε3"), ("TC", "CC", "ε3/ε4"), ("CC", "CC", "ε4/ε4"),
    ("TT", "CT", "ε2/ε3"), ("TT", "TT", "ε2/ε2"), ("TC", "CT", "ε2/ε4"),
])
def test_apoe_genotypes_on_request(tmp_path, r1, r2, expected):
    text, out = run(tmp_path, [("rs429358", r1), ("rs7412", r2)], apoe=True)
    assert out["apoe_genotype"] == expected
    section = text.split("## 血脂：APOE", 1)[1]
    assert "可以考虑查一次血脂" in section
    assert "不解读那一部分" in section
    for word in ("阿尔茨海默", "风险增加", "倍"):
        assert word not in section


def test_rare_apoe_combination_is_not_named(tmp_path):
    _, out = run(tmp_path, [("rs429358", "CC"), ("rs7412", "CT")], apoe=True)
    assert out["apoe_genotype"] is None


def test_no_dose_anywhere(tmp_path):
    text, _ = run(tmp_path, [("rs671", "AA"), ("rs1801133", "AA"), ("rs4988235", "GG"), ("rs429358", "CC"), ("rs7412", "CC")], apoe=True)
    assert not re.search(r"\d+(\.\d+)?\s*(mg|μg|µg|ug|毫克|微克|IU)", text, re.IGNORECASE)
