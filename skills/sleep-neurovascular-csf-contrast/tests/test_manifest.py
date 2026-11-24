"""Expected effects are printed in Supplementary Table 3, PDF page 5.

Each row exercises the personal contrast equation on a printed pathway input.
These are per-term reproductions, not observed individual CSF predictions.
"""
import json
import math
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import personal_report as report
import presets


def test_printed_indirect_effects():
    # S3: a1=2.178, a2=1.342, d21=0.376, b1=0.804, b2=0.610.
    # Printed indirect1=1.751, indirect2=0.818, indirect3=0.500.
    # Power ratio = 10**(printed dB difference / 10), by definition of dB.
    cases = [(2.178, 0, 1.751), (0, 1.342, 0.818),
             (0, 2.178 * 0.376, 0.500)]
    for eeg_db, bold_db, printed in cases:
        result = report.calculate({
            "eeg_nrem_power_ratio": 10 ** (eeg_db / 10),
            "bold_nrem_power_ratio": 10 ** (bold_db / 10),
        })
        # Coefficients and effects rounded to three decimals; propagation
        # of half-last-digit rounding is bounded by 0.002 dB for these rows.
        assert math.isclose(result["csf_power_difference_db"], printed,
                            abs_tol=0.002, rel_tol=0)


def run_cli(tmp_path, text, *extra):
    path = tmp_path / "measurements.csv"
    path.write_text(text, encoding="utf-8")
    out = tmp_path / "out"
    run = subprocess.run([sys.executable, str(ROOT / "scripts/personal_report.py"),
                          "--measurements", str(path), "--age", "23",
                          "--reference-age", "23", "--out", str(out), *extra],
                         capture_output=True, text=True)
    return run, out


def test_manifest_matches_presets():
    manifest = json.loads((ROOT / "skill.json").read_text())
    assert manifest["inputs_status"] == "verified"
    specs = {s["key"]: s for s in manifest["inputs"]}
    for key in presets.RATIO_KEYS:
        assert specs[key]["unit"] == "1"
        assert specs[key]["accept"] == {"%": 0.01}
        assert specs[key]["range"] == list(presets.RATIO_RANGE)
    assert presets.COEFFICIENTS == {"eeg_nrem_power_ratio": 0.804,
                                    "bold_nrem_power_ratio": 0.610}


def test_cli_reproduces_printed_neural_term(tmp_path):
    ratio = 10 ** (2.178 / 10)
    run, out = run_cli(tmp_path, f"marker,value,unit\nEEG NREM power ratio,{ratio},1\nBOLD NREM power ratio,100,%\n")
    assert run.returncode == 0, run.stderr
    result = json.loads((out / "result.json").read_text())["outputs"]
    assert math.isclose(result["csf_power_difference_db"]["value"], 1.751, abs_tol=0.002)
    assert math.isclose(result["eeg_power_difference_db"]["value"], 2.178, abs_tol=1e-12)
    text = (out / "report.md").read_text()
    assert text.index("论文卡片") < text.index("你的模型对比")
    assert presets.BOUNDARY in text


def test_bad_inputs_remove_stale_results(tmp_path):
    valid = "marker,value,unit\neeg_nrem_power_ratio,1,1\nbold_nrem_power_ratio,1,1\n"
    for invalid in [valid.replace(",1,1", ",1,uV", 1),
                    valid.replace(",1,1", ",0,1", 1),
                    valid.replace(",1,1", ",1001,1", 1),
                    valid.replace(",1,1", ",NaN,1", 1),
                    "marker,value,unit\neeg_nrem_power_ratio,1,1\n"]:
        ok, out = run_cli(tmp_path, valid)
        assert ok.returncode == 0
        bad, out = run_cli(tmp_path, invalid)
        assert bad.returncode == 3, bad.stderr
        assert (out / "problems.json").exists()
        assert not (out / "result.json").exists()
        assert not (out / "levers.json").exists()
        assert "你的模型对比" not in (out / "report.md").read_text()
        assert "论文卡片" in (out / "report.md").read_text()


def test_age_gap_and_cross_group_rejected(tmp_path):
    valid = "marker,value,unit\neeg_nrem_power_ratio,1,1\nbold_nrem_power_ratio,1,1\n"
    for flag, age in [("--age", "45"), ("--reference-age", "65"), ("--age", "nonsense")]:
        run, out = run_cli(tmp_path, valid, flag, age)
        assert run.returncode == 3, run.stderr
        assert (out / "problems.json").exists()


def test_targets_use_same_equation_and_reject_unknown_rows(tmp_path):
    valid = "marker,value,unit\neeg_nrem_power_ratio,1,1\nbold_nrem_power_ratio,1,1\n"
    targets = tmp_path / "targets.csv"
    targets.write_text(f"marker,value,unit\neeg_nrem_power_ratio,{10 ** (2.178 / 10)},1\n")
    run, out = run_cli(tmp_path, valid, "--targets", str(targets))
    assert run.returncode == 0, run.stderr
    levers = json.loads((out / "levers.json").read_text())
    assert math.isclose(levers["targets"]["csf_power_difference_db"], 1.751, abs_tol=0.002)
    assert math.isclose(levers["levers"][0]["csf_power_difference_delta_db"], 1.751, abs_tol=0.002)
    assert math.isclose(levers["sensitivity"][0]["db_per_db"], 0.804)
    targets.write_text("marker,value,unit\nEEG typo,2,1\n")
    bad, out = run_cli(tmp_path, valid, "--targets", str(targets))
    assert bad.returncode == 3
    assert not (out / "result.json").exists()
