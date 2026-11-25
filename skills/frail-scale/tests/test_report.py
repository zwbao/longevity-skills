"""Additional scoring boundaries and integration properties."""

from itertools import product
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from personal_report import calculate, classify, fatigue_points, weight_loss_percent
from test_manifest import VALID, run_report


def test_appendix_fatigue_codes():
    # Appendix 1 prints codes 1–5 and recodes the first two as 1, others as 0.
    assert [fatigue_points(c) for c in (1, 2, 3, 4, 5)] == [1, 1, 0, 0, 0]


def test_methods_total_categories():
    # Methods FRAIL Questionnaire: 0 robust, 1–2 pre-frail, 3–5 frail.
    for total, category in [(0, "robust"), (1, "prefrail"), (2, "prefrail"),
                            (3, "frail"), (4, "frail"), (5, "frail")]:
        assert classify(total) == category


def test_methods_weight_boundary_and_gain():
    # Synthetic weights exercise the printed Methods >=5% threshold;
    # Appendix 1 omits equality. These are not printed participant records.
    base = {key: float(v) for key, v, _u in VALID}
    for current, point in [(76, 1), (76.000001, 0), (75.999999, 1), (84, 0)]:
        result = calculate({**base, "weight_current_kg": current})
        assert result["weight_loss_score"] == point
    assert weight_loss_percent(76, 80) == 5
    assert weight_loss_percent(84, 80) == -5


def test_every_component_combination_adds_without_reweighting():
    for f, r, a, i, w in product((0, 1), repeat=5):
        result = calculate({
            "fatigue_response_code": 1 if f else 5,
            "resistance_difficulty_binary": r,
            "ambulation_difficulty_binary": a,
            "illnesses_count": 5 if i else 0,
            "weight_current_kg": 76 if w else 80,
            "weight_year_ago_kg": 80,
        })
        assert result["frail_total_score"] == sum((f, r, a, i, w))
        assert result["frail_category"] == classify(sum((f, r, a, i, w)))


def test_age_context_does_not_change_score(tmp_path):
    run, out = run_report(tmp_path, extra=("--age", "75", "--sex", "女"))
    assert run.returncode == 0, run.stderr
    report = (out / "report.md").read_text()
    assert "49–65" in report and "适用性证据有限" in report
    assert "**1 / 5**" in report


def test_unreadable_file_and_absent_measurements(tmp_path):
    from personal_report import main

    for args in [[], ["--measurements", str(tmp_path / "absent.csv")]]:
        assert main([*args, "--out", str(tmp_path / "out")]) == 3
        assert (tmp_path / "out/problems.json").exists()
