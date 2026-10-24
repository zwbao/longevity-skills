"""--include-cpic-text prints CPIC's own recommendation text, verbatim and labelled; without it nothing changes."""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report  # noqa: E402
from cpic_calls import load_tables  # noqa: E402

# CPIC recommendation 8481447 (simvastatin, SLCO1B1 Decreased Function), as
# https://api.cpicpgx.org/v1/recommendation?id=eq.8481447 returned it on 2026-10-24.
SIMVASTATIN_8481447 = (
    "Prescribe an alternative statin depending on the desired potency (see Figure 1 of PMID: 35152405 for "
    "recommendations for alternative statins). If simvastatin therapy is warranted, limit dose to <20mg/day."
)


def _run(tmp_path, flag):
    dip = tmp_path / "dip.txt"
    dip.write_text("SLCO1B1 *1/*5\nCYP2C19 *2/*2\n", encoding="utf-8")
    meds = tmp_path / "meds.txt"
    meds.write_text("辛伐他汀片 20mg\n", encoding="utf-8")
    out = tmp_path / ("with" if flag else "without")
    path = personal_report.write_report(out, None, dip, meds, [], include_cpic_text=flag)
    return path.read_text(encoding="utf-8"), out


def test_every_snapshot_row_has_cpic_text_with_the_same_words_and_version():
    tables = load_tables()
    text = personal_report.load_text()
    assert text["schema"] == "cpic-recommendation-text/1"
    assert text["source"]["api"] == "https://api.cpicpgx.org/v1/"
    for entry in tables["drugs"].values():
        for row in entry["rows"]:
            record = text["recommendations"][str(row["id"])]
            assert " ".join(record["drugrecommendation"].split()) == row["recommendation"]
            assert (record["version"], record["classification"], record["lookupkey"]) == (row["version"], row["classification"], row["lookup"])
    assert text["recommendations"]["8481447"]["drugrecommendation"] == SIMVASTATIN_8481447


def test_flag_prints_cpic_text_verbatim_and_writes_json(tmp_path):
    report, out = _run(tmp_path, True)
    section = report.split("## CPIC 原文推荐（照录，英文）", 1)[1].split("## 数据来源", 1)[0]
    assert "标签：CPIC 指南" in section
    assert f"Recommendation: {SIMVASTATIN_8481447}" in section
    assert "CPIC 推荐 #8481447（第 1 版），对应 SLCO1B1: Decreased Function，推荐强度 Strong" in section
    assert "Implications (SLCO1B1): Increased simvastatin acid exposure as compared to normal function; increased risk of myopathy" in section
    assert "doi:10.1002/cpt.2557" in section
    assert "n/a" not in section
    payload = json.loads((out / "cpic_recommendations.json").read_text(encoding="utf-8"))
    assert payload["schema"] == "cpic-recommendations/1"
    simva = [item for item in payload["results"] if item["drug"] == "simvastatin"]
    assert len(simva) == 1
    item = simva[0]
    assert item["recommendation_id"] == 8481447 and item["version"] == 1
    assert item["drugrecommendation"] == SIMVASTATIN_8481447
    assert item["basis_kind"] == "cpic" and item["category"] == "avoid" and item["classification"] == "Strong"
    assert item["lookup"] == {"SLCO1B1": "Decreased Function"}
    tables = load_tables()
    listed = {(item["drug"], item["recommendation_id"]) for item in payload["results"]}
    assert ("clopidogrel", next(row["id"] for row in tables["drugs"]["clopidogrel"]["rows"]
                               if row["lookup"] == {"CYP2C19": "Poor Metabolizer"} and row["population"] == "CVI ACS PCI")) in listed


def test_without_flag_report_is_unchanged(tmp_path):
    plain, out = _run(tmp_path, False)
    assert "## CPIC 原文推荐" not in plain
    assert SIMVASTATIN_8481447[:40] not in plain
    assert not (out / "cpic_recommendations.json").exists()
    with_text, _ = _run(tmp_path, True)
    before = with_text.split("## CPIC 原文推荐（照录，英文）", 1)[0]
    assert before == plain.split("## 数据来源", 1)[0]


def test_command_line_flag(tmp_path):
    dip = tmp_path / "dip.txt"
    dip.write_text("SLCO1B1 *1/*5\n", encoding="utf-8")
    script = ROOT / "scripts" / "personal_report.py"
    done = subprocess.run([sys.executable, str(script), "--diplotypes", str(dip), "--include-cpic-text", "--out", str(tmp_path / "o")],
                          capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    assert (tmp_path / "o" / "cpic_recommendations.json").exists()
    manifest = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))
    assert manifest["entry"]["cpic_text_flag"] == "--include-cpic-text"
