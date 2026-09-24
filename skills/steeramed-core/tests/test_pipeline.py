import csv
import json
import sys
from pathlib import Path

import numpy as np
import pytest
from scipy import stats

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import build_modules
import delta
import evidence_chain
import recall
import run_pipeline
import sa_score
import selection as select
import summarize_chain
from presets import resolve_preset


def test_welch_matches_scipy():
    rng = np.random.default_rng(0)
    a = rng.normal(size=40)
    b = rng.normal(size=35) + 0.4
    expected = stats.ttest_ind(a, b, equal_var=False).statistic
    assert sa_score.welch_t(a, b) == pytest.approx(expected)


def test_sa_sign_follows_target_minus_nontarget():
    values = np.array([1.0, 1.2, 0.8, 0.0, 0.1, -0.1])
    score = sa_score.compute_sa_score(values, [0, 1, 2], [3, 4, 5])
    assert score > 0
    assert sa_score.compute_sa_score(values, [0, 1], [3, 4, 5]) == 0.0


def test_vectorized_sa_matches_scalar():
    rng = np.random.default_rng(1)
    matrix = rng.normal(size=(5, 12))
    pairs = [{"target_idx": [0, 1, 2], "non_target_idx": [3, 4, 5, 6]}]
    column = sa_score.compute_sa_matrix(matrix, pairs)[:, 0]
    for row in range(5):
        assert column[row] == pytest.approx(
            sa_score.compute_sa_score(matrix[row], pairs[0]["target_idx"], pairs[0]["non_target_idx"])
        )


def test_paper_match_keeps_caliper():
    ages = np.array([30, 33, 36, 40, 70])
    sexes = np.array(["M", "M", "M", "M", "M"])
    matched, rule = delta.match_controls(32, "M", ages, sexes, k=10, caliper=5, min_controls=3)
    assert rule == "caliper"
    assert list(matched) == [1, 0, 2]

    too_few, rule = delta.match_controls(32, "M", ages, sexes, k=10, caliper=1, min_controls=3)
    assert rule == "none"
    assert len(too_few) == 0

    repo, rule = delta.match_controls(32, "M", ages, sexes, k=3, caliper=1, min_controls=3, fallback="repo")
    assert rule == "repo_no_caliper"
    assert list(repo) == [1, 0, 2]


def test_aging_delta_uses_young_mean_and_excludes_gap():
    beta = np.array(
        [
            [0.2, 0.2],
            [0.4, 0.4],
            [9.0, 9.0],
            [1.0, 0.0],
        ]
    )
    result = delta.compute_aging_deltas(
        ["y1", "y2", "gap", "old"],
        beta,
        np.array([40, 49, 52, 70]),
    )
    assert result.sample_ids == ["old"]
    assert result.deltas[0] == pytest.approx([0.7, -0.3])


def test_module_selection_ranks_by_pvalue():
    mean_delta = np.array([0.2, 0.2, 0.2, 0.0, 0.0])
    modules = [
        {"hub": "flat", "genes": ["g3", "g4"]},
        {"hub": "shifted", "genes": ["g0", "g1", "g2"]},
    ]
    gene_to_idx = {f"g{i}": i for i in range(5)}
    selected = select.select_modules(mean_delta, modules, gene_to_idx, top_n=1)
    assert [row["hub"] for row in selected] == ["shifted"]


def test_importance_counts_features_not_patients():
    pairs = [
        _pair("A", "m1"),
        _pair("A", "m2"),
        _pair("B", "m3"),
    ]
    ranking = select.rank_patient(np.array([5.0, 4.0, 3.0]), pairs, top_k=50)
    assert [(row["compound_id"], row["importance"]) for row in ranking] == [("A", 2), ("B", 1)]


def test_feature_selection_uses_mean_absolute_sa():
    sa = np.array(
        [
            [0.0, 10.0, 3.0],
            [5.0, 0.0, 3.0],
            [5.0, 0.0, 3.0],
            [5.0, 0.0, 3.0],
        ]
    )
    keep, _ = select.select_features(sa, top_n=2)
    assert list(keep) == [0, 2]


def test_recall_baseline_matches_manuscript_approximation():
    baseline = recall.random_baseline(14, 1500, 10)
    assert baseline == pytest.approx(1 - (1 - 14 / 1500) ** 10)
    assert baseline == pytest.approx(0.089, abs=0.001)
    report = recall.recall_report([["drug"] , ["other"]], {"drug"}, n_candidates=1500, ks=(10,))
    assert report["by_k"][0]["recall"] == 0.5


def test_target_window_does_not_exempt_positives():
    compounds = [
        {"id": "wide", "name": "Wide", "targets": ["a"], "n_targets": 1000, "is_positive": True},
        {"id": "fit", "name": "Fit", "targets": ["a"], "n_targets": 80, "is_positive": False},
    ]
    kept = select.filter_compounds(compounds, min_targets=60, max_targets=300)
    assert [row["id"] for row in kept] == ["fit"]


def test_build_modules_filters_overlap_and_score():
    edge = Path("/tmp/steeramed_edges.tsv")
    genes = Path("/tmp/steeramed_genes.txt")
    out = Path("/tmp/steeramed_modules.json")
    hub_neighbors = [f"g{i}" for i in range(25)]
    lines = ["protein1 protein2 score\n"]
    lines += "".join(f"HUB {gene} 500\n" for gene in hub_neighbors)
    lines += "HUB far 100\n"
    edge.write_text("".join(lines), encoding="utf-8")
    genes.write_text("\n".join(["HUB", *hub_neighbors, "far"]), encoding="utf-8")
    assert build_modules.main(["--edges", str(edge), "--genes", str(genes), "--min-size", "20", "--out", str(out)]) == 0
    modules = json.loads(out.read_text(encoding="utf-8"))
    hubs = {module["hub"] for module in modules}
    assert "HUB" in hubs
    hub_module = next(module for module in modules if module["hub"] == "HUB")
    assert "far" not in hub_module["genes"]
    assert len(hub_module["genes"]) == 26


def test_end_to_end_recovers_planted_compound(tmp_path: Path):
    genes = [f"g{i}" for i in range(20)]
    sample_ids = [f"c{i}" for i in range(6)] + [f"k{i}" for i in range(6)]
    beta = np.full((12, 20), 0.5)
    beta[:6, :5] = 0.8
    beta_path = tmp_path / "beta.csv"
    _write_samples(beta_path, sample_ids, genes, beta)
    meta_path = tmp_path / "meta.csv"
    with meta_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["sample_id", "age", "sex", "group"])
        for i, sid in enumerate(sample_ids):
            writer.writerow([sid, 50, "M", "case" if i < 6 else "control"])
    modules = [
        {"hub": "g0", "genes": genes[:10], "hallmark": "Inflammation"},
        {"hub": "g10", "genes": genes[10:], "hallmark": "Other"},
    ]
    compounds = [
        {"id": "POS", "name": "Planted", "targets": ["g0", "g1", "g2", "g3"], "n_targets": 10, "is_positive": True},
        {"id": "NEG", "name": "Decoy", "targets": ["g15", "g16", "g17", "g18"], "n_targets": 10, "is_positive": False},
    ]
    module_path = tmp_path / "modules.json"
    compound_path = tmp_path / "compounds.json"
    module_path.write_text(json.dumps(modules), encoding="utf-8")
    compound_path.write_text(json.dumps(compounds), encoding="utf-8")
    out = tmp_path / "out"
    code = run_pipeline.main(
        [
            "--preset",
            "depression",
            "--beta",
            str(beta_path),
            "--meta",
            str(meta_path),
            "--modules",
            str(module_path),
            "--compounds",
            str(compound_path),
            "--individual-bootstrap",
            "5",
            "--group-bootstrap",
            "5",
            "--out",
            str(out),
        ]
    )
    assert code == 0
    summary = (out / "summary.md").read_text(encoding="utf-8")
    assert "不是治疗建议" in summary
    assert "disease-informed" in summary
    recall_payload = json.loads((out / "recall.json").read_text(encoding="utf-8"))
    recall10 = next(row for row in recall_payload["by_k"] if row["k"] == 10)
    assert recall10["recall"] == 1.0
    chain = json.loads(next((out / "evidence").glob("*.json")).read_text(encoding="utf-8"))
    assert chain["top_compounds"][0]["compound_id"] == "POS"
    assert chain["bootstrap_stability"]["POS"] == 100.0
    text = summarize_chain.summarize(chain)
    assert "Layer 1" in text and "Layer 4" in text
    assert "不是治疗建议" in text


def test_preset_aliases_and_aging_chem_window():
    assert resolve_preset("bc")["preset"] == "breast_cancer"
    assert resolve_preset("mdd")["chem_max_targets"] is None
    aging = resolve_preset("aging")
    assert aging["delta_mode"] == "aging_young_mean"
    assert aging["chem_min_targets"] == 5


def _pair(cid: str, hub: str) -> dict:
    return {
        "compound_id": cid,
        "compound_name": cid,
        "module_hub": hub,
        "hallmark": None,
        "is_positive": cid == "A",
        "is_known_drug": cid == "A",
        "n_targets": 4,
        "target_genes": ["g0", "g1", "g2"],
    }


def _write_samples(path: Path, sample_ids: list[str], genes: list[str], matrix: np.ndarray) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["sample_id", *genes])
        for sid, row in zip(sample_ids, matrix):
            writer.writerow([sid, *row])
