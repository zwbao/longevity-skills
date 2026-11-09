"""The lookup against the numbers Dremel et al. (Lancet Neurol 2026) print.

Every expected value below is typed from the paper (main-text Results, Table 2)
or its supplementary appendix (Table 6), not taken from presets.py or from the
script's own output.
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
NONE = ["--adpkd", "no", "--connective-tissue", "no", "--family-history", "no", "--atherosclerosis", "no",
        "--smoking", "never", "--hypertension", "no"]


def _run(tmp_path: Path, age="50", sex="female", **overrides):
    args = list(NONE)
    for key, value in overrides.items():
        flag = "--" + key.replace("_", "-")
        if flag in args:
            args[args.index(flag) + 1] = value
        else:
            args += [flag, value]
    out = tmp_path / "out"
    code = personal_report.main(["--age", age, "--sex", sex, *args, "--out", str(out)])
    result = json.loads((out / "result.json").read_text(encoding="utf-8"))["outputs"]
    report = (out / "report.md").read_text(encoding="utf-8")
    return code, {key: item["value"] for key, item in result.items()}, report


def test_manifest_matches_presets_and_script():
    keys = {item["key"] for item in MANIFEST["inputs"]}
    assert keys == {"age", "sex", "adpkd", "connective_tissue", "family_history", "atherosclerosis", "smoking",
                    "hypertension", "country"}
    assert set(personal_report.YES_NO_FLAGS) | {"family_history", "smoking", "country", "age", "sex"} == keys
    assert {item["key"] for item in MANIFEST["outputs"]} == set(personal_report.OUTPUT_KEYS)
    assert set(presets.GROUPS) <= keys
    age = next(item for item in MANIFEST["inputs"] if item["key"] == "age")
    assert age["unit"] == "a" and age["range"][0] <= presets.AGE_CUTOFF <= age["range"][1]


def test_reference_population():
    # Results: "was 3·9% (3·0–5·1, 0·9–14·3)"
    assert presets.REFERENCE_PREVALENCE == (3.9, 3.0, 5.1)
    assert presets.REFERENCE_PREDICTION_INTERVAL == (0.9, 14.3)


def test_paper_age_bands(tmp_path):
    # Results: "2·9% (1·7–4·5) in cohorts younger than 55 years and 5·2% (3·4–7·0) in cohorts older than 55 years"
    code, young, report = _run(tmp_path / "a", age="40")
    assert code == 0 and young["age_band"] == "<55" and young["age_band_prevalence_pct"] == 2.9
    assert "1.7–4.5" in report
    code, old, report = _run(tmp_path / "b", age="60")
    assert code == 0 and old["age_band"] == "≥55" and old["age_band_prevalence_pct"] == 5.2
    assert "3.4–7.0%" in report
    assert _run(tmp_path / "c", age="55")[1]["age_band_prevalence_pct"] == 5.2


def test_paper_sex(tmp_path):
    # Results: "women was 5·5% (95% CI 4·3–6·9, 3415 of 65020 participants) and 3·0% (2·2–4·0, 2122 of
    # 76130 participants) for men (RR for women 1·9 [95% CI 1·8–2·0])"
    _, woman, _ = _run(tmp_path / "f", sex="female")
    _, man, _ = _run(tmp_path / "m", sex="male")
    assert woman["sex_prevalence_pct"] == 5.5 and man["sex_prevalence_pct"] == 3.0
    assert woman["female_rr"] == 1.9 and man["female_rr"] is None
    # The printed crude counts reproduce the printed RR to its one decimal.
    crude_rr = (3415 / 65020) / (2122 / 76130)
    assert round(crude_rr, 1) == 1.9


TABLE2 = {
    # Table 2 row: participants with UIA/total, prevalence (95% CI), crude PR, age-and-sex adjusted PR (last column)
    "adpkd": (293, 1990, 12.8, 4.2, 4.4, (1.5, 12.6)),
    "atherosclerosis": (2229, 40970, 5.5, 1.7, 1.3, (0.8, 2.0)),
    "connective_tissue": (94, 879, 10.3, 3.3, 3.9, (2.0, 7.6)),
    "family_history": (412, 4252, 7.9, 2.5, 2.4, (0.5, 11.2)),
}


@pytest.mark.parametrize("group", sorted(TABLE2))
def test_paper_table2(tmp_path, group):
    events, total, prevalence, pr_crude, pr_adjusted, adjusted_ci = TABLE2[group]
    code, out, report = _run(tmp_path, **{group: "yes"})
    assert code == 0
    assert out["comorbidity_group"] == group
    assert out["comorbidity_group_prevalence_pct"] == prevalence
    assert out["comorbidity_group_count"] == 1
    assert out["adjusted_elevated_group_count"] == (1 if adjusted_ci[0] > 1 else 0)
    assert f"{events}/{total}" in report
    assert f"{pr_crude:.1f}（95% CI" in report
    assert f"校正年龄和性别后 {pr_adjusted:.1f}（95% CI {adjusted_ci[0]:.1f}–{adjusted_ci[1]:.1f}）" in report


def test_paper_family_subgroups(tmp_path):
    # Results: one affected relative "6·7% (4·0-10·9)", two or more "9·5% (7·9–11·4)"
    assert _run(tmp_path / "one", family_history="1")[1]["family_subgroup_prevalence_pct"] == 6.7
    assert _run(tmp_path / "two", family_history="2+")[1]["family_subgroup_prevalence_pct"] == 9.5
    _, one, report = _run(tmp_path / "order", family_history="1", atherosclerosis="yes")
    lines = report.splitlines()
    family_line = next(i for i, line in enumerate(lines) if line.startswith("- 一级亲属有动脉瘤性"))
    assert "6.7%（95% CI 4.0–10.9%）" in lines[family_line + 1]
    _, unknown, _ = _run(tmp_path / "yes", family_history="yes")
    assert unknown["family_subgroup_prevalence_pct"] is None and unknown["comorbidity_group_prevalence_pct"] == 7.9


def test_paper_smoking_and_hypertension(tmp_path):
    # Results: current smoking "1·4 (1·2–1·6)"; any definition of hypertension "1·6 (1·5–1·7)"
    _, out, report = _run(tmp_path / "s", smoking="current", hypertension="yes")
    assert out["current_smoking_rr"] == 1.4 and out["hypertension_rr"] == 1.6
    assert "1.2–1.6" in report and "1.5–1.7" in report
    _, former, report = _run(tmp_path / "f", smoking="former")
    assert former["current_smoking_rr"] is None and former["hypertension_rr"] is None
    assert "1.14（95% CI 1.07–1.22）" in report


def test_paper_country_china(tmp_path):
    # Appendix Table 6: "China 701 /10 689 8·5% (6·0-11·8) 3·7 (1·4-9·7) ... 2·1 (1·0-4·2)"
    _, out, report = _run(tmp_path, country="中国")
    assert out["country_prevalence_pct"] == 8.5 and out["country_pr_age_sex"] == 2.1
    assert "701/10689" in report and "3.7（95% CI 1.4–9.7）" in report and "2.1（95% CI 1.0–4.2）" in report
    _, usa, _ = _run(tmp_path / "us", country="USA")
    assert usa["country_prevalence_pct"] == 2.0 and usa["country_pr_age_sex"] is None


def test_several_groups_are_not_multiplied(tmp_path):
    code, out, report = _run(tmp_path, adpkd="yes", atherosclerosis="yes", hypertension="yes")
    assert code == 0
    assert out["comorbidity_group"] == "adpkd" and out["comorbidity_group_prevalence_pct"] == 12.8
    assert out["comorbidity_group_count"] == 2 and out["adjusted_elevated_group_count"] == 1
    assert "不相乘" in report


def test_no_group_and_boundary(tmp_path):
    code, out, report = _run(tmp_path)
    assert code == 0 and out["comorbidity_group"] == "none" and out["comorbidity_group_prevalence_pct"] is None
    assert report.splitlines()[0].startswith("# ")
    assert "边界" in report and presets.BOUNDARY in report
    assert "## 你落在论文的哪些人群" in report


def test_age_out_of_range_exits_3(tmp_path):
    code, out, report = _run(tmp_path, age="250")
    assert code == skillkit.EXIT_INPUT_PROBLEM
    assert all(value is None for value in out.values())
    problems = json.loads((tmp_path / "out" / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert {(item["key"], item["kind"]) for item in problems} == {("age", "range")}
    assert "5.2" not in report and "2.9" not in report


def test_bad_answer_and_missing_flag_exit_3(tmp_path):
    out = tmp_path / "out"
    code = personal_report.main(["--age", "50", "--sex", "女", "--adpkd", "maybe", "--smoking", "never", "--out", str(out)])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    kinds = {(item["key"], item["kind"]) for item in problems}
    assert ("adpkd", "parse") in kinds
    assert ("hypertension", "missing") in kinds and ("family_history", "missing") in kinds
    result = json.loads((out / "result.json").read_text(encoding="utf-8"))["outputs"]
    assert result["age_band_prevalence_pct"]["value"] is None


def test_missing_sex_exits_3(tmp_path):
    out = tmp_path / "out"
    code = personal_report.main(["--age", "50", *NONE, "--out", str(out)])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert ("sex", "missing") in {(item["key"], item["kind"]) for item in problems}
