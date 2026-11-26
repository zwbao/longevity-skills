"""Contract tests written before implementation.

No published individual genotype + total GPS example was found in the article,
Supplementary Figures 1–3, Tables 1–10, reporting summary or released weights.
These are engineering tests with explicitly synthetic dosages and literal source
weights; they do NOT turn validation.status into reproduced.
"""
import csv
import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def values(out):
    return {k: v["value"] for k, v in json.loads((out / "result.json").read_text())["outputs"].items()}


@pytest.fixture
def model(tmp_path, monkeypatch):
    import personal_report as report
    import presets
    source = ROOT / "tests/fixtures/bc_weights.tsv"
    archive = tmp_path / "bc.zip"
    with zipfile.ZipFile(archive, "w") as z:
        z.writestr("weights.txt", source.read_bytes())
    spec = dict(presets.MODELS["bc"], count=2, member="weights.txt",
                zip_sha256=hashlib.sha256(archive.read_bytes()).hexdigest())
    monkeypatch.setitem(presets.MODELS, "bc", spec)
    monkeypatch.setattr(report, "obtain_weights", lambda *a, **kw: archive)
    return report


def run(model, tmp_path, text, extra=()):
    path = tmp_path / "dosages.csv"
    path.write_text(text, encoding="utf-8")
    out = tmp_path / "out"
    code = model.main(["--genotypes", str(path), "--disease", "bc", "--build", "hg19",
                       "--sex", "female", "--out", str(out), *extra])
    return code, out


HEADER = "variant,dosage_allele,dosage_copies,unit\n"
ROWS = "10:123337335:A:G,A,1,1\n16:52599188:T:C,T,0,1\n"


def test_manifest_and_published_variant_counts():
    import presets
    m = json.loads((ROOT / "skill.json").read_text())
    spec = next(s for s in m["inputs"] if s["key"] == "dosage_copies")
    assert (spec["unit"], spec["range"]) == (presets.DOSAGE_UNIT, list(presets.DOSAGE_RANGE))
    # Table 1: these are source inventory counts, NOT personal score examples.
    assert {k: v["count"] for k, v in presets.MODELS.items()} == {
        "cad": 6630150, "af": 6730541, "t2d": 6917436, "ibd": 6907112, "bc": 5218}
    assert m["validation"]["status"] == "draft"


def test_literal_weight_with_synthetic_one_copy(model, tmp_path):
    code, out = run(model, tmp_path, HEADER + ROWS)
    assert code == 0
    # Broad BreastCancer v3 row 1: A weight 0.2376.
    assert values(out)["raw_score"] == pytest.approx(0.2376, abs=1e-12)
    report = (out / "report.md").read_text()
    assert report.index("论文卡片") < report.index("你的原始分数")
    assert "边界:" in report and "不能据此开始或停止用药" in report
    assert "百分位" in report and "未经个人示例复现" in report
    assert values(out)["variants_scored"] == 2


def test_other_allele_dosage_is_complemented_and_order_independent(model, tmp_path):
    text = HEADER + "16:52599188:C:T,C,2,1\n10:123337335:G:A,G,1,1\n"
    code, out = run(model, tmp_path, text)
    assert code == 0
    assert values(out)["raw_score"] == pytest.approx(0.2376, abs=1e-12)


def test_fractional_dosage_alias_and_extra_variant(model, tmp_path):
    # Same total one effect-allele copy distributed across identical repeated runs.
    text = HEADER.replace("dosage_copies", "DS") + ROWS.replace(
        "A,1,1", "G,1,1") + "1:100:A:C,A,0,1\n"
    code, out = run(model, tmp_path, text)
    assert code == 0 and values(out)["raw_score"] == pytest.approx(0.2376)
    assert values(out)["extra_variants"] == 1
    code, out = run(model, tmp_path, HEADER + ROWS.replace("A,1,1", "A,0.5,1"))
    assert code == 0
    assert 2 * values(out)["raw_score"] == pytest.approx(0.2376)


@pytest.mark.parametrize("text,extra", [
    (HEADER, ()),
    (HEADER + ROWS.splitlines()[0] + "\n", ()),
    (HEADER + ROWS.replace("16:52599188", "16:52599189"), ()),
    (HEADER + ROWS.replace("A,1,1", "A,1,mg/dL"), ()),
    (HEADER + ROWS.replace("A,1,1", "A,3,1"), ()),
    (HEADER + ROWS.replace("A,1,1", "A,nan,1"), ()),
    (HEADER + ROWS.replace("A,1,1", "A,inf,1"), ()),
    (HEADER + ROWS.replace("A,1,1", "A,,1"), ()),
    (HEADER + ROWS.replace("A,1,1", "C,1,1"), ()),
    (HEADER + ROWS.replace("A,1,1", "A,1,"), ()),
    (HEADER + ROWS + ROWS.splitlines()[0] + "\n", ()),
    (HEADER + ROWS, ("--build", "hg38")),
    (HEADER + ROWS, ("--sex", "male")),
    (HEADER + ROWS, ("--age", "nan")),
    (HEADER + ROWS, ("--disease", "unknown")),
    ("garbage\n", ()),
])
def test_bad_input_exits_3_without_score(model, tmp_path, text, extra):
    code, out = run(model, tmp_path, text, extra)
    assert code == 3
    assert json.loads((out / "problems.json").read_text())["problems"]
    assert all(v is None for v in values(out).values())
    report = (out / "report.md").read_text()
    assert "论文卡片" in report and "边界:" in report
    assert "你的原始分数" not in report


def test_invalid_rerun_removes_stale_success(model, tmp_path):
    assert run(model, tmp_path, HEADER + ROWS)[0] == 0
    code, out = run(model, tmp_path, HEADER)
    assert code == 3 and values(out)["raw_score"] is None
    assert not (out / "provenance.json").exists()
    assert run(model, tmp_path, HEADER + ROWS)[0] == 0
    assert not (out / "problems.json").exists()


def test_missing_arguments_subprocess(tmp_path):
    out = tmp_path / "out"
    proc = subprocess.run([sys.executable, str(ROOT / "scripts/personal_report.py"),
                           "--out", str(out)], capture_output=True, text=True)
    assert proc.returncode == 3, proc.stderr
    assert values(out)["raw_score"] is None


def test_corrupt_cache_is_rejected_without_network(tmp_path):
    import personal_report as report
    import presets
    (tmp_path / "bc.zip").write_bytes(b"not the released archive")
    with pytest.raises(report.ResourceError):
        report.obtain_weights("bc", tmp_path, offline=True)


def test_released_weights_are_not_exponentiated(tmp_path):
    import personal_report as report
    rows = list(csv.DictReader((ROOT / "tests/fixtures/cad_weights.tsv").open(), delimiter="\t"))
    # Broad CoronaryArteryDisease v3 first row: literal weight 1.4113e-06.
    first = rows[0]
    assert report.contribution(1, first["effect_allele"], first["effect_allele"],
                               float(first["effect_weight"])) == 1.4113e-06
