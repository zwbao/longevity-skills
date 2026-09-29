"""skill.json matches the script, the plus-strand bases match the sources, bad input exits 3."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report  # noqa: E402
import skillkit  # noqa: E402
from presets import APOE, VARIANTS  # noqa: E402

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))
SCRIPT = (ROOT / "scripts" / "personal_report.py").read_text(encoding="utf-8")
HEADER = "# rsid\tchromosome\tposition\tgenotype\n"


def _file(tmp_path, text, name="genome.txt"):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def test_every_declared_flag_is_parsed():
    for spec in MANIFEST["inputs"]:
        assert f'"{spec["flag"]}"' in SCRIPT, spec["key"]


def test_declared_outputs_are_written(tmp_path):
    path = _file(tmp_path, HEADER + "rs671\t12\t112241766\tGG\n")
    personal_report.write_report(tmp_path / "out", path)
    result = json.loads((tmp_path / "out" / "result.json").read_text(encoding="utf-8"))
    assert set(result["outputs"]) == {item["key"] for item in MANIFEST["outputs"]}


def test_plus_strand_bases_match_grch38_records():
    # Ensembl GRCh38 allele strings, strand 1: rs671 G/A, rs1801133 G/A(/C), rs4988235 G/A(/C/T),
    # rs429358 T/C, rs7412 C/T.
    for variant in VARIANTS.values():
        assert f"{variant['reference']}/{variant['effect']}" in variant["grch38"]
    assert APOE["sites"] == {"rs429358": ("T", "C"), "rs7412": ("C", "T")}


def test_paper_card_cites_brooks_2009(tmp_path):
    path = _file(tmp_path, HEADER + "rs671\t12\t112241766\tGA\n")
    text = personal_report.write_report(tmp_path / "out", path).read_text(encoding="utf-8")
    card = text.split("## 喝酒", 1)[0]
    assert "10.1371/journal.pmed.1000050" in card and "Brooks" in card


def test_no_file_exits_3(tmp_path):
    assert personal_report.main(["--out", str(tmp_path / "out")]) == skillkit.EXIT_INPUT_PROBLEM


def test_not_a_genotype_file_exits_3(tmp_path):
    path = _file(tmp_path, "项目,结果,单位\n白蛋白,45,g/L\n", "labs.csv")
    assert personal_report.main(["--genotype", str(path), "--out", str(tmp_path / "out")]) == skillkit.EXIT_INPUT_PROBLEM


def test_file_without_panel_sites_exits_3(tmp_path):
    path = _file(tmp_path, HEADER + "rs4477212\t1\t82154\tAA\n")
    assert personal_report.main(["--genotype", str(path), "--out", str(tmp_path / "out")]) == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((tmp_path / "out" / "problems.json").read_text(encoding="utf-8"))
    assert problems["problems"][0]["kind"] == "coverage"


def test_good_file_exits_0(tmp_path):
    path = _file(tmp_path, HEADER + "rs671\t12\t112241766\tGA\n")
    assert personal_report.main(["--genotype", str(path), "--out", str(tmp_path / "out")]) == 0


def test_shared_parser_copies_are_identical():
    other = ROOT.parent / "cpic-pharmacogenomics" / "scripts" / "genotype_file.py"
    if other.exists():
        assert other.read_bytes() == (ROOT / "scripts" / "genotype_file.py").read_bytes()
