"""Cohort contrast (case versus control for a clock readout) and GEO sample annotations."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.lk import cohort, geo  # noqa: E402
from tools.lk.cli import main  # noqa: E402
from tools.lk.library import LKError  # noqa: E402

A = [61.2, 58.4, 66.1, 70.3, 55.9, 63.0, 68.8]
B = [54.1, 57.3, 52.8, 60.2, 49.9, 55.5]


def close(x, y, rel=1e-9):
    return abs(x - y) <= rel * max(1.0, abs(y))


def test_statistics_match_reference_values():
    # reference values computed with scipy 1.16 and statsmodels 0.14
    assert close(cohort.t_two_sided(2.0, 10), 0.07338803477074039)
    assert close(cohort.t_two_sided(40, 5), 1.8411962171772952e-07)
    diff, t, p = cohort.welch(A, B)
    assert close(diff, 8.419047619047625) and close(t, 3.3822410748814282) and close(p, 0.0065224814215314566)
    m, t, p = cohort.paired([1.2, -0.4, 2.1, 0.8, 1.9, 0.3])
    assert close(m, 0.9833333333333333) and close(t, 2.5254294810506233) and close(p, 0.052823562902414814)
    ages = [40, 45, 50, 55, 60, 65, 42, 47, 52, 57, 62, 67]
    y = [44.5, 50.1, 54.2, 60.3, 63.9, 70.2, 41.0, 46.8, 51.1, 56.7, 60.9, 66.5]
    beta, se, df = cohort.ols(y, [[1.0, g, a] for g, a in zip([1] * 6 + [0] * 6, ages)])
    assert close(beta[1], 5.3746666666666725) and close(se[1], 0.3013864728160058) and df == 9
    assert close(cohort.t_two_sided(beta[1] / se[1], df), 2.4901752175858033e-08, rel=1e-6)


def study():
    values = {f"c{i}": v for i, v in enumerate(A)} | {f"k{i}": v for i, v in enumerate(B)}
    ages = {s: 50 + 2 * i for i, s in enumerate(values)}
    return values, [f"c{i}" for i in range(len(A))], [f"k{i}" for i in range(len(B))], ages


def test_design_follows_measure_and_what_is_known():
    values, case, control, ages = study()
    plain = cohort.contrast(values, case, control, "age")
    assert plain["status"] == "ok" and plain["method"] == "welch" and plain["call"] == "higher"
    assert close(plain["p_value"], 0.0065224814215314566) and plain["effect_unit"] == "years"
    adjusted = cohort.contrast(values, case, control, "age", ages=ages)
    assert adjusted["method"] == "age_adjusted", "a raw clock output with known ages is compared at equal age"
    residual = cohort.contrast(values, case, control, "acceleration_residual", ages=ages)
    assert residual["method"] == "welch" and "residual of the clock on age" in residual["notes"][-1]
    assert cohort.contrast(values, case, control, "acceleration_difference", ages=ages)["status"] == "ok"
    no_age = cohort.contrast(values, case, control, "acceleration_residual")
    assert no_age["status"] == "not_computed" and no_age["reason"] == "needs_age", "an acceleration is never guessed without ages"
    strict = cohort.contrast(values, case, control, "age", alpha=0.001)
    assert strict["call"] == "not significant" and strict["direction"] == "higher"


def test_same_individuals_in_both_groups_are_paired_and_repeats_are_averaged():
    before = {f"b{i}": 60 + i for i in range(6)}
    after = {f"a{i}": 60 + i + d for i, d in enumerate([1.2, -0.4, 2.1, 0.8, 1.9, 0.3])}
    subjects = {f"b{i}": f"P{i}" for i in range(6)} | {f"a{i}": f"P{i}" for i in range(6)}
    r = cohort.contrast({**before, **after}, list(after), list(before), "age", subjects=subjects)
    assert r["method"] == "paired" and r["n_used"] == {"pairs": 6} and close(r["p_value"], 0.052823562902414814)
    values, case, control, _ = study()
    doubled = dict(values) | {"c0b": values["c0"] + 2}
    r = cohort.contrast(doubled, case + ["c0b"], control, "age", subjects={"c0": "X", "c0b": "X"})
    assert r["method"] == "welch+unit_means" and r["n_used"]["case"] == len(A), "two samples of one person count once"


def test_artefacts_overlaps_and_small_groups():
    values, case, control, _ = study()
    broken = dict(values) | {"c0": 5e6, "k0": "NA"}
    r = cohort.contrast(broken, case, control, "age")
    assert r["n_used"] == {"case": len(A) - 1, "control": len(B) - 1}, "outputs beyond 1000 and non-numbers are left out"
    r = cohort.contrast(values, case, control + ["c1"], "age")
    assert r["n_used"]["case"] == len(A) - 1 and "both groups" in r["notes"][0]
    tiny = cohort.contrast(values, case[:2], control, "age")
    assert tiny["status"] == "not_computed" and tiny["reason"] == "too_few"
    try:
        cohort.contrast(values, case, control, "biological")
    except LKError as exc:
        assert exc.code == "bad_input"
    else:
        raise AssertionError("an unknown measure is refused")


def test_threshold_text():
    assert cohort.alpha_from("two-tailed p-value < 0.05") == 0.05 and cohort.alpha_from("P ≤ 0.01") == 0.01
    assert cohort.alpha_from("p < 1 x 10-5") == 1e-05 and cohort.alpha_from(None) == 0.05 and cohort.alpha_from("nominal") == 0.05


HEADER = "\n".join([
    '!Series_title\t"Example"',
    '!Sample_title\t"case 1"\t"control 1"\t"control 2"',
    '!Sample_geo_accession\t"GSM1"\t"GSM2"\t"GSM3"',
    '!Sample_source_name_ch1\t"whole blood"\t"whole blood"\t"whole blood"',
    '!Sample_characteristics_ch1\t"age: 34"\t"age: 18 months"\t"age: 61 years"',
    '!Sample_characteristics_ch1\t"gestational age: 39"\t"gestational age: 40"\t"gestational age: 38"',
    '!Sample_characteristics_ch1\t"subject: P1"\t"subject: P1"\t"subject: P2"',
    '!Sample_characteristics_ch1\t"twin pair: T1"\t"twin pair: T1"\t"twin pair: T2"',
    "!series_matrix_table_begin",
    '"ID_REF"\t"GSM1"\t"GSM2"\t"GSM3"',
])
SDRF = ("Source Name\tComment [Sample_title]\tCharacteristics[age]\tCharacteristics[disease state]\tFactorValue [DISEASE STATE]\n"
        "GSM10 1\tPBL 1\t45\tnormal\tnormal\nGSM11 1\tPBL 2\t52\tTrisomy 21\tTrisomy 21\n")


def test_annotations_are_read_from_both_formats():
    samples = geo.parse_series_matrix_header(HEADER)
    assert list(samples) == ["GSM1", "GSM2", "GSM3"] and samples["GSM1"]["title"] == "case 1"
    age = geo.ages_from(samples)
    assert age["field"] == "age" and age["guessed"], "gestational age is not chronological age"
    assert age["ages"] == {"GSM1": 34.0, "GSM2": 1.5, "GSM3": 61.0}
    assert geo.ages_from(samples, "gestational age")["guessed"] is False, "the caller's choice is taken as given"
    who = geo.subjects_from(samples)
    assert who["field"] == "subject" and who["subjects"]["GSM2"] == "P1", "a twin pair is not one individual"
    mirror = geo.parse_sdrf(SDRF)
    assert geo.ages_from(mirror)["ages"] == {"GSM10": 45.0, "GSM11": 52.0} and mirror["GSM11"]["fields"]["disease state"] == "Trisomy 21"
    fields = {r["field"]: r for r in geo.field_summary(samples)}
    assert fields["age"]["samples"] == 3 and fields["twin pair"]["distinct"] == 2


def test_command_line_and_mcp_entry(tmp_path, capsys):
    values, case, control, ages = study()
    spec = tmp_path / "spec.json"
    spec.write_text(json.dumps({"values": values, "case": case, "control": control, "measure": "age", "ages": ages,
                                "threshold_text": "P < 0.05"}))
    assert main(["--library", str(ROOT), "contrast", "--input", str(spec)]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["status"] == "ok" and out["method"] == "age_adjusted" and "研究用途" in out["label_zh"]
    header = tmp_path / "GSE_header.txt"
    header.write_text(HEADER)
    assert main(["--library", str(ROOT), "annotations", str(header)]) == 0
    listed = json.loads(capsys.readouterr().out)
    assert listed["guess"] == {"age_field": "age", "samples_with_age": 3, "subject_field": "subject"}
    from tools.lk import mcp
    assert {"contrast_groups", "list_annotations"} <= {t["name"] for t in mcp.TOOLS}
