"""compare-age: age-direction vote between two omics profiles."""

import gzip
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.lk import compare  # noqa: E402
from tools.lk.library import Library  # noqa: E402

LIB = Library(ROOT)


def _strongest(modality, n=30):
    ref = compare._load(LIB, modality)
    return sorted(ref.items(), key=lambda kv: -abs(kv[1][0]))[:n]


def test_profile_shifted_along_age_directions_looks_older():
    for modality in ("proteomics", "methylation"):
        feats = _strongest(modality)
        older = {k: (1.0 if w > 0 else -1.0) for k, (w, _b, _p) in feats}
        younger = {k: -v for k, v in older.items()}
        out = compare.compare_from_payload(LIB, {"profile_a": younger, "profile_b": older})
        assert out["status"] == "ok" and out["outputs"]["looks_older"] == "B", (modality, out)
        assert out["outputs"]["weighted_share_for_A_older"] == 0.0
        swapped = compare.compare_from_payload(LIB, {"profile_a": older, "profile_b": younger})
        assert swapped["outputs"]["looks_older"] == "A"


def test_text_formats_are_read():
    feats = _strongest("proteomics", 12)
    text = "; ".join(f"{k} (A: {1.0 if w > 0 else -1.0:.2f}, B: {-1.0 if w > 0 else 1.0:.2f}, A much higher)" for k, (w, _b, _p) in feats)
    out = compare.compare_from_payload(LIB, {"panel_text": "Top proteins: " + text})
    assert out["outputs"]["looks_older"] == "A" and out["outputs"]["features_used"] == 12
    cpgs = _strongest("methylation", 12)
    text = " | ".join(f"{k} (chr1:1, +, OpenSea). In GENE body. Beta. A: {0.6 if w > 0 else 0.4}, B: {0.4 if w > 0 else 0.6}, A higher."
                      for k, (w, _b, _p) in cpgs)
    out = compare.compare_from_payload(LIB, {"panel_text": text})
    assert out["outputs"]["looks_older"] == "A" and out["method"].endswith("(methylation)")
    blocks = ("Participant A:\n" + "; ".join(f"{k} ({1.0 if w > 0 else -1.0})" for k, (w, _b, _p) in feats)
              + "\nParticipant B:\n" + "; ".join(f"{k} ({-1.0 if w > 0 else 1.0})" for k, (w, _b, _p) in feats))
    assert compare.compare_from_payload(LIB, {"panel_text": blocks})["outputs"]["looks_older"] == "A"


def test_too_few_features_is_refused_not_guessed():
    out = compare.compare_from_payload(LIB, {"profile_a": {"ELN": 1.0, "XYZ1": 2}, "profile_b": {"ELN": 0.0, "XYZ1": 1}})
    assert out["status"] == "input_problem"
    weak = [k for k, v in compare._load(LIB, "proteomics").items() if 1e-4 < v[2] < 0.05][:8]
    out = compare.compare_from_payload(LIB, {"profile_a": {k: 1.0 for k in weak}, "profile_b": {k: 0.0 for k in weak}})
    assert out["status"] == "ok" and out["outputs"]["low_confidence"] is True, "few strong proteins: nominal ones, flagged"
    out = compare.compare_from_payload(LIB, {"profile_a": {"ELN": 1.0}, "profile_b": {"ELN": 0.0}})
    assert out["status"] == "input_problem"
    assert compare.compare_from_payload(LIB, {"panel_text": "nothing to compare"})["status"] == "input_problem"


def test_reference_files_match_their_sources_shape():
    with gzip.open(ROOT / "data/reference/olink_age_direction_ckb.csv.gz", "rt") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 2923 and {"gene", "sd_per_year", "se", "p"} <= set(rows[0])
    eln = next(r for r in rows if r["gene"] == "ELN")
    assert abs(float(eln["sd_per_year"]) - 0.068943) < 1e-4, "ELN is the strongest age protein in CKB eTable 5"


def test_panel_ref_reads_the_saved_prompt_and_rejects_paths(tmp_path, monkeypatch):
    from tools.lk import store
    from tools.lk.library import LKError
    monkeypatch.setenv("LONGEVITY_CACHE", str(tmp_path))
    feats = _strongest("proteomics", 12)
    text = "; ".join(f"{k} (A: {1.0 if w > 0 else -1.0:.2f}, B: {-1.0 if w > 0 else 1.0:.2f})" for k, (w, _b, _p) in feats)
    ref = store.save(text)
    assert compare.compare_from_payload(LIB, {"panel_ref": ref})["outputs"]["looks_older"] == "A"
    for bad in ("../../etc/passwd", "ABCDEF0123456789", ref[:-1]):
        try:
            compare.compare_from_payload(LIB, {"panel_ref": bad})
        except LKError:
            pass
        else:
            raise AssertionError(bad)
