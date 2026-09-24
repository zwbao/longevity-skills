import csv
import gzip
import json
import sys
from pathlib import Path

import numpy as np

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import labs
import names
import personal_report
import reference_data


def test_promoter_window_keeps_upstream_1500_only():
    genes = reference_data.promoter_genes_from_row("RBL2;RBL2;OTHER", "-220;-1419;223")
    assert genes == {"RBL2"}
    assert reference_data.promoter_genes_from_row("FAR", "-1600") == set()
    assert reference_data.promoter_genes_from_row("BODY", "40") == set()


def test_breast_cancer_counts_match_manuscript_logic():
    rows = [
        ["gender: F", "gender: F", "gender: F", "gender: F"],
        ["", "cancer type (icd-10): C50", "cancer type (icd-10): C18", ""],
    ]
    groups = reference_data.assign_groups("breast_cancer", rows, 4)
    assert groups == ["control", "case", "exclude", "control"]


def test_ra_groups_match_disease_state():
    rows = [["disease state: rheumatoid arthritis", "disease state: Normal", "disease state: other"]]
    assert reference_data.assign_groups("ra", rows, 3) == ["case", "control", "exclude"]


def test_series_matrix_aggregates_promoter_probes(tmp_path: Path):
    matrix = tmp_path / "mini.txt.gz"
    text = "\n".join(
        [
            "!Sample_geo_accession\t\"GSM1\"\t\"GSM2\"",
            "!Sample_characteristics_ch1\tage (y): 40\tage (y): 70",
            "!series_matrix_table_begin",
            "ID_REF\tGSM1\tGSM2",
            "cg1\t0.2\t0.8",
            "cg2\t0.4\t0.6",
            "cg3\t0.9\t0.9",
            "!series_matrix_table_end",
            "",
        ]
    )
    with gzip.open(matrix, "wt", encoding="utf-8") as handle:
        handle.write(text)
    probe_map = {"cg1": {"GENE"}, "cg2": {"GENE"}, "cg3": {"OTHER"}}
    samples, genes, beta = reference_data.aggregate_promoter_beta(matrix, probe_map, "aging")
    assert [sample["sample_id"] for sample in samples] == ["GSM1", "GSM2"]
    assert samples[1]["age"] == 70
    gene_i = genes.index("GENE")
    assert beta[0, gene_i] == np.float32(0.3)
    assert beta[1, gene_i] == np.float32(0.7)


def test_chinese_medicine_and_sex_and_lab_bounds(tmp_path: Path):
    assert names.normalize_sex("女") == "F"
    assert names.medication_match("烟酸片", "Niacin", "CIDm1", ["niacin"])
    assert not names.medication_match("阿司匹林", "Niacin", "CIDm1", ["niacin"])
    checkup = tmp_path / "panel.txt"
    checkup.write_text("肾小球滤过率 48 ml/min\n", encoding="utf-8")
    lines = labs.lab_lines(labs.parse_labs(checkup))
    assert any("肾小球滤过率 48" in line and "低于参考下限" in line for line in lines)
    assert any("不会据此删掉或推荐化合物" in line for line in lines)


def test_chemical_catalog_prefers_readable_alias(tmp_path: Path):
    path = tmp_path / "sources.tsv.gz"
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        handle.write(
            "chemical\talias\tsource\n"
            "CIDm1\tN02BA01\tATC\n"
            "CIDm1\taspirin\tWiki\n"
            "CIDm2\twater\tChEBI\n"
        )
    catalog = reference_data.load_chemical_catalog(path)
    assert set(catalog) == {"CIDm1"}
    assert catalog["CIDm1"]["name"] == "aspirin"
    assert "aspirin" in catalog["CIDm1"]["aliases"]


def test_atc_chemical_filter(tmp_path: Path):
    path = tmp_path / "sources.tsv.gz"
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        handle.write("# ATC comment\nchemical\talias\tsource\nCID1\taspirin\tATC\nCID2\twater\tChEBI\n")
    assert reference_data.load_atc_chemicals(path) == {"CID1"}


def test_personal_report_uses_frozen_bundle_without_download(tmp_path: Path):
    genes = [f"g{i}" for i in range(12)]
    bundle = tmp_path / "prepared" / "aging"
    bundle.mkdir(parents=True)
    np.save(bundle / "genes.npy", np.array(genes))
    np.save(bundle / "young_mean.npy", np.full(len(genes), 0.4, dtype=np.float32))
    modules = [{"hub": "g0", "genes": genes[:8], "mean_delta": 0.2, "p_value": 0.001, "n_genes": 8}]
    features = [
        {
            "module_hub": "g0",
            "hallmark": None,
            "compound_id": "POS",
            "compound_name": "Niacin",
            "aliases": ["niacin", "nicotinic acid"],
            "target_genes": genes[:4],
            "non_target_genes": genes[4:8],
            "n_targets": 10,
            "is_positive": False,
            "is_known_drug": False,
        },
        {
            "module_hub": "g0",
            "hallmark": None,
            "compound_id": "NEG",
            "compound_name": "Decoy",
            "target_genes": genes[8:12],
            "non_target_genes": genes[4:8],
            "n_targets": 10,
            "is_positive": False,
            "is_known_drug": False,
        },
    ]
    (bundle / "modules.json").write_text(json.dumps(modules), encoding="utf-8")
    (bundle / "features.json").write_text(json.dumps(features), encoding="utf-8")
    (bundle / "bundle.json").write_text(
        json.dumps(
            {
                "preset": "aging",
                "geo": "GSE40279",
                "n_samples_used_for_deltas": 4,
                "n_genes": len(genes),
                "n_modules": 1,
                "n_compounds": 2,
                "n_features": 2,
                "delta_mode": "aging_young_mean",
                "compound_pool": "test",
            }
        ),
        encoding="utf-8",
    )
    beta = tmp_path / "me.csv"
    values = [0.7, 0.8, 0.9, 1.0, 0.35, 0.4, 0.45, 0.5, 0.4, 0.4, 0.4, 0.4]
    with beta.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["sample_id", *genes])
        writer.writerow(["me", *values])
    meds = tmp_path / "meds.txt"
    meds.write_text("烟酸\n阿司匹林肠溶片\n", encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n谷丙转氨酶,72,U/L\n", encoding="utf-8")
    out = tmp_path / "out"
    personal_report.report(
        "aging", beta, out, age=60, sex="男", medications=meds, labs=labs, layout="samples", cache=tmp_path
    )
    text = (out / "report.md").read_text(encoding="utf-8")
    assert "1. Niacin" in text
    assert "烟酸：对应名单上的 Niacin，排在第 1 位" in text
    assert "阿司匹林肠溶片：名单里没有这个名字。不能据此停药。" in text
    assert "谷丙转氨酶 72" in text
    assert "高于参考上限" in text
    assert "不是治疗建议" in text
    assert "importance" not in text
