"""skill.json matches presets; the cut points are the ones the paper prints;
wrong units, out-of-range values and non-codes stop the score with exit 3.

The paper (Marent et al., GeroScience 2026, Methods, "Multidimensional sleep
health score") prints the cut points but no person's score, so these tests
check the printed cut points and their boundaries, not a printed example;
validation in skill.json stays draft.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report
import presets
import skillkit

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))

# Methods, "Multidimensional sleep health score", verbatim.
PRINTED = (
    "Favourable device-measured domains were defined as follows: sleep duration of 6–8 h per night, "
    "sleep efficiency ≥ 85%, sleep timing with sleep midpoint between 02:00 and 04:00, and sleep "
    "regularity based on night-to-night variability in sleep midpoint < 60 min."
)

GOOD = [
    ("睡眠时长", "7", "h"),
    ("睡眠效率", "88", "%"),
    ("睡眠中点", "3", "h"),
    ("睡眠中点标准差", "30", "min"),
    ("PSQI 总体睡眠质量", "1", ""),
    ("PSQI 白天犯困", "0", ""),
]


def _csv(path: Path, rows) -> Path:
    path.write_text("\n".join(["item,value,unit"] + [",".join(r) for r in rows]) + "\n", encoding="utf-8")
    return path


def _run(tmp_path: Path, rows, *extra):
    out = tmp_path / "out"
    code = personal_report.main(["--measurements", str(_csv(tmp_path / "m.csv", rows)), "--out", str(out), *extra])
    return code, out


def _outputs(out: Path) -> dict:
    return {k: v["value"] for k, v in json.loads((out / "result.json").read_text(encoding="utf-8"))["outputs"].items()}


def _replace(rows, name, value, unit):
    return [(name, value, unit) if r[0] == name else r for r in rows]


def test_printed_cut_points_match_presets():
    assert "6–8 h" in PRINTED and (presets.DURATION_LOW_H, presets.DURATION_HIGH_H) == (6, 8)
    assert "≥ 85%" in PRINTED and presets.EFFICIENCY_MIN_PCT == 85
    assert "between 02:00 and 04:00" in PRINTED
    assert (presets.MIDPOINT_EARLIEST_H, presets.MIDPOINT_LATEST_H) == (2, 4)
    assert "< 60 min" in PRINTED and presets.MIDPOINT_SD_BELOW_MIN == 60
    assert presets.SCORE_MAX == 6 and len(presets.DOMAINS) == 6
    # Results: "the multidimensional sleep health score was 5 (IQR 4–6)"
    assert presets.COHORT_MEDIAN_SCORE == 5 and presets.COHORT_IQR_SCORE == (4, 6)


def test_manifest_matches_presets():
    measured = [i["key"] for i in MANIFEST["inputs"] if i["from"] == "measurements"]
    assert measured == [input_key for _f, input_key, _n, _r in presets.DOMAINS]
    outputs = [o["key"] for o in MANIFEST["outputs"]]
    assert outputs == ["sleep_health_score"] + [f for f, _i, _n, _r in presets.DOMAINS]
    spec = {i["key"]: i for i in MANIFEST["inputs"]}
    assert skillkit.unit_factor(spec["sleep_duration_h"], "min") * 360 == pytest.approx(presets.DURATION_LOW_H)
    assert skillkit.unit_factor(spec["sleep_efficiency_pct"], "1") * 0.85 == pytest.approx(presets.EFFICIENCY_MIN_PCT)
    assert skillkit.unit_factor(spec["sleep_midpoint_sd_min"], "h") * 1 == presets.MIDPOINT_SD_BELOW_MIN
    assert MANIFEST["inputs_status"] == "verified"
    assert MANIFEST["validation"]["status"] == "draft"
    assert MANIFEST["entry"]["targets_flag"] == "--targets" and MANIFEST["entry"]["levers_json"] is True


def test_all_favourable_scores_six(tmp_path: Path):
    code, out = _run(tmp_path, GOOD)
    assert code == 0
    got = _outputs(out)
    assert got["sleep_health_score"] == 6
    assert all(got[f] == 1 for f, _i, _n, _r in presets.DOMAINS)
    text = (out / "report.md").read_text(encoding="utf-8")
    assert text.startswith("# 六维睡眠健康评分")
    assert "## 论文卡片" in text and "10.1007/s11357-026-02518-y" in text
    assert f"边界: {presets.BOUNDARY}" in text


def test_all_unfavourable_scores_zero(tmp_path: Path):
    rows = [
        ("sleep_duration_h", "5.5", ""),
        ("sleep_efficiency_pct", "80", ""),
        ("sleep_midpoint_clock_h", "1.5", ""),
        ("sleep_midpoint_sd_min", "75", ""),
        ("psqi_sleep_quality_code", "2", ""),
        ("psqi_trouble_awake_code", "3", ""),
    ]
    code, out = _run(tmp_path, rows)
    assert code == 0
    got = _outputs(out)
    assert got["sleep_health_score"] == 0
    assert all(got[f] == 0 for f, _i, _n, _r in presets.DOMAINS)


@pytest.mark.parametrize(
    "key,value,expected",
    [
        ("duration_favourable", 6.0, True),
        ("duration_favourable", 8.0, True),
        ("duration_favourable", 5.99, False),
        ("duration_favourable", 8.01, False),
        ("efficiency_favourable", 85.0, True),
        ("efficiency_favourable", 84.99, False),
        ("timing_favourable", 2.0, True),
        ("timing_favourable", 4.0, True),
        ("timing_favourable", 4.01, False),
        ("timing_favourable", 27.5, True),  # GGIR hours from the previous midnight: 03:30
        ("timing_favourable", 23.9, False),
        ("regularity_favourable", 59.9, True),
        ("regularity_favourable", 60.0, False),
        ("satisfaction_favourable", 1, True),
        ("satisfaction_favourable", 2, False),
        ("alertness_favourable", 1, True),
        ("alertness_favourable", 2, False),
    ],
)
def test_boundaries(key, value, expected):
    assert presets.favourable(key, value) is expected


def test_minutes_and_fraction_are_converted(tmp_path: Path):
    rows = _replace(GOOD, "睡眠时长", "350", "min")       # 5.83 h: unfavourable
    rows = _replace(rows, "睡眠效率", "0.86", "1")          # 86 %: favourable
    rows = _replace(rows, "睡眠中点标准差", "1.5", "h")     # 90 min: unfavourable
    code, out = _run(tmp_path, rows)
    assert code == 0
    got = _outputs(out)
    assert (got["duration_favourable"], got["efficiency_favourable"], got["regularity_favourable"]) == (0, 1, 0)
    assert got["sleep_health_score"] == 4


@pytest.mark.parametrize(
    "row",
    [
        ("睡眠效率", "0.86", ""),            # fraction without unit, read as 0.86 %
        ("睡眠时长", "420", ""),             # minutes without unit, read as 420 h
        ("睡眠时长", "7", "kg"),             # unknown unit
        ("PSQI 总体睡眠质量", "1.5", ""),    # not an answer code
        ("PSQI 白天犯困", "4", ""),          # out of 0–3
    ],
)
def test_bad_input_exits_3_without_score(tmp_path: Path, row):
    code, out = _run(tmp_path, _replace(GOOD, row[0], row[1], row[2]))
    assert code == skillkit.EXIT_INPUT_PROBLEM == 3
    assert (out / "problems.json").exists()
    assert not (out / "result.json").exists()
    text = (out / "report.md").read_text(encoding="utf-8")
    assert "/ 6" not in text and "边界:" in text


def test_missing_domain_exits_3(tmp_path: Path):
    code, out = _run(tmp_path, [r for r in GOOD if r[0] != "睡眠中点"])
    assert code == 3
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert [p["key"] for p in problems] == ["sleep_midpoint_clock_h"]


def test_levers_each_target_alone_and_together(tmp_path: Path):
    rows = _replace(GOOD, "睡眠效率", "80", "%")
    rows = _replace(rows, "睡眠中点标准差", "90", "min")
    targets = _csv(tmp_path / "t.csv", [("睡眠效率", "86", "%"), ("睡眠中点标准差", "45", "min")])
    code, out = _run(tmp_path, rows, "--targets", str(targets))
    assert code == 0
    assert _outputs(out)["sleep_health_score"] == 4
    levers = json.loads((out / "levers.json").read_text(encoding="utf-8"))
    assert levers["schema"] == "longevity-levers/1"
    assert levers["current"]["sleep_health_score"] == 4
    deltas = {item["key"]: item["sleep_health_score_delta"] for item in levers["levers"]}
    assert deltas == {"sleep_efficiency_pct": 1, "sleep_midpoint_sd_min": 1}
    assert levers["targets"]["sleep_health_score"] == 6
    flags = {item["key"]: item["favourable"] for item in levers["sensitivity"]}
    assert flags["sleep_efficiency_pct"] is False and flags["sleep_duration_h"] is True


def test_young_age_note(tmp_path: Path):
    code, out = _run(tmp_path, GOOD, "--age", "40")
    assert code == 0
    assert "55 岁及以上" in (out / "report.md").read_text(encoding="utf-8")
