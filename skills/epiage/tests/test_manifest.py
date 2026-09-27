"""epiage manifest, vendored files, and the refusals that need no pandas.

The expected SHA-256 values were computed from gangchen/epiage-skill at
fcf4e3be1a5977e8f19641931a2f1219b058ed80, so these tests do not need a clone.
"""

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report  # noqa: E402
import skillkit  # noqa: E402

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))
COMMIT = "fcf4e3be1a5977e8f19641931a2f1219b058ed80"
UPSTREAM_SHA256 = {
    "scripts/compute_clocks.py": "6adb02923759d8c93eebcaef4a6dc6719f679d3b398607d889e7e5bcfb311868",
    "LICENSE-epiage": "24a4eee3a41c9b2f46c27d3486b316a762506d09b9360683abe3cbd45529d968",
    "NOTICE-epiage": "715f90b194ea8105bf10abb526d422046055b050afb6b6aa361beba89e611dbf",
    "references/model-audit.md": "86e608ebadabb4154a5a518bdd2d754aacdb905fb64c6d93bd9792f7e1002e64",
}
# sha256 of "<name> <sha256>\n" lines, sorted by name, over upstream epigenetic-clocks/data/
# minus the three IDAT-only SeSAMe files.
UPSTREAM_DATA_DIGEST = "76fd02422660bc897e7f137adc198e50698118bfa06bf061a55101b5450c1763"
EXCLUDED = {"sesame-reference-cache.tar.gz", "sesame-resources.json", "SESAME_DATA_LICENSE.txt"}
UNIT_MAP = {"years": "a", "years/year": "1", "beta": "1", "kb": "kb", "score": "score"}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def upstream_models():
    """(key, unit) for every model registered in the vendored CLOCKS table, read without pandas."""
    source = (ROOT / "scripts" / "compute_clocks.py").read_text(encoding="utf-8")
    block = source[source.index("CLOCKS = {"):source.index("MODEL_BLOCKERS")]
    return re.findall(r'^\s+"([a-z0-9_]+)":\s*dict\(.*?unit="([^"]+)"', block, re.M)


def test_tool_manifest_shape():
    assert MANIFEST["kind"] == "tool" and MANIFEST["tier"] == "tool"
    assert MANIFEST["inputs_status"] == "verified"
    assert MANIFEST["tool"]["commit"] == COMMIT[:7]
    assert MANIFEST["tool"]["license"] == "MIT"
    assert MANIFEST["entry"]["runtime"] == "scientific"
    assert (ROOT / "scripts" / "requirements.txt").read_text(encoding="utf-8").split() == ["pandas>=1.5", "numpy>=1.23"]
    flags = {item["key"]: item.get("flag") for item in MANIFEST["inputs"]}
    assert flags == {"betas": "--betas", "clocks": "--clocks", "age": "--age", "sex": "--sex", "sensitivity": "--sensitivity"}


def test_outputs_cover_every_upstream_model_with_its_unit():
    models = upstream_models()
    assert len(models) == 37
    outputs = {item["key"]: item for item in MANIFEST["outputs"]}
    assert len(outputs) == len(MANIFEST["outputs"])
    assert all(key.startswith("dnam_") for key in outputs)
    assert set(outputs) == {f"dnam_{key}" for key, _ in models}
    for key, unit in models:
        assert outputs[f"dnam_{key}"]["unit"] == UNIT_MAP[unit], key
    assert "phenoage" not in outputs, "DNAm PhenoAge must not share the blood PhenoAge output key"


def test_vendored_upstream_files_are_byte_identical():
    for relative, digest in UPSTREAM_SHA256.items():
        assert _sha256(ROOT / relative) == digest, relative
    names = sorted(path.name for path in (ROOT / "data").iterdir())
    assert not EXCLUDED & set(names)
    lines = "".join(f"{name} {_sha256(ROOT / 'data' / name)}\n" for name in names)
    assert hashlib.sha256(lines.encode()).hexdigest() == UPSTREAM_DATA_DIGEST


def test_data_files_are_declared_with_matching_sha256():
    declared = {item["path"]: item for item in MANIFEST["data_files"]}
    on_disk = {f"data/{path.name}" for path in (ROOT / "data").iterdir()}
    assert set(declared) == on_disk and len(on_disk) == 40
    for path, item in declared.items():
        assert item["sha256"] == _sha256(ROOT / path), path
        assert item["redistributable"] == "yes"
        assert item["source_url"] == f"https://raw.githubusercontent.com/gangchen/epiage-skill/{COMMIT}/epigenetic-clocks/{path}"


def test_upstream_never_opens_the_excluded_sesame_files():
    source = (ROOT / "scripts" / "compute_clocks.py").read_text(encoding="utf-8")
    for name in EXCLUDED:
        assert name not in source


def _write(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    return path


def _problems(out: Path):
    return json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]


def test_idat_file_and_directory_are_refused(tmp_path):
    idat = tmp_path / "203_R01C01_Grn.idat.gz"
    idat.write_bytes(b"\x1f\x8b")
    assert personal_report.main(["--betas", str(idat), "--out", str(tmp_path / "a")]) == skillkit.EXIT_INPUT_PROBLEM
    assert "SeSAMe" in (tmp_path / "a" / "report.md").read_text(encoding="utf-8")
    folder = tmp_path / "idats"
    folder.mkdir()
    assert personal_report.main(["--betas", str(folder), "--out", str(tmp_path / "b")]) == skillkit.EXIT_INPUT_PROBLEM
    assert "IDAT" in _problems(tmp_path / "b")[0]["message_zh"]


def test_missing_file_is_refused_and_result_is_empty(tmp_path):
    out = tmp_path / "out"
    assert personal_report.main(["--betas", str(tmp_path / "none.csv"), "--out", str(out)]) == skillkit.EXIT_INPUT_PROBLEM
    assert _problems(out)[0]["kind"] == "missing"
    result = json.loads((out / "result.json").read_text(encoding="utf-8"))["outputs"]
    assert set(result) == {item["key"] for item in MANIFEST["outputs"]}
    assert all(item["value"] is None for item in result.values())
    assert (out / "report.md").read_text(encoding="utf-8").splitlines()[-1].startswith("边界: ")


def test_percent_values_are_refused_not_rescaled(tmp_path):
    betas = _write(tmp_path / "b.csv", "CpG,me\ncg00000029,45.2\ncg00000108,60.1\ncg00000109,0.5\n")
    out = tmp_path / "out"
    assert personal_report.main(["--betas", str(betas), "--clocks", "horvath", "--out", str(out)]) == skillkit.EXIT_INPUT_PROBLEM
    message = _problems(out)[0]["message_zh"]
    assert "0 到 1" in message and "百分比" in message


def test_m_values_are_refused(tmp_path):
    betas = _write(tmp_path / "b.tsv", "CpG\tme\ncg00000029\t-2.5\ncg00000108\t3.1\n")
    assert personal_report.main(["--betas", str(betas), "--clocks", "horvath", "--out", str(tmp_path / "o")]) == skillkit.EXIT_INPUT_PROBLEM
    assert "M 值" in _problems(tmp_path / "o")[0]["message_zh"]


def test_a_single_out_of_range_beta_is_named(tmp_path):
    rows = "".join(f"cg{i:08d},0.5\n" for i in range(200))
    betas = _write(tmp_path / "b.csv", "CpG,me\n" + rows + "cg99999999,1.2\n")
    assert personal_report.main(["--betas", str(betas), "--clocks", "horvath", "--out", str(tmp_path / "o")]) == skillkit.EXIT_INPUT_PROBLEM
    assert "cg99999999" in _problems(tmp_path / "o")[0]["message_zh"]


def test_age_range_and_sex_words_are_checked(tmp_path):
    betas = _write(tmp_path / "b.csv", "CpG,me\ncg00000029,0.4\n")
    assert personal_report.main(["--betas", str(betas), "--age", "150", "--out", str(tmp_path / "a")]) == skillkit.EXIT_INPUT_PROBLEM
    assert _problems(tmp_path / "a")[0]["key"] == "age"
    assert personal_report.main(["--betas", str(betas), "--sex", "x", "--out", str(tmp_path / "b")]) == skillkit.EXIT_INPUT_PROBLEM
    assert _problems(tmp_path / "b")[0]["key"] == "sex"
    for word, code in (("男", "m"), ("Female", "f"), ("M", "m"), ("女性", "f")):
        assert personal_report.parse_sex(word) == (code, [])


def test_missing_runtime_is_reported_not_guessed(tmp_path, monkeypatch):
    def no_pandas():
        raise ImportError("No module named 'pandas'")

    monkeypatch.setattr(personal_report, "load_upstream", no_pandas)
    betas = _write(tmp_path / "b.csv", "CpG,me\ncg00000029,0.4\n")
    code = personal_report.main(["--betas", str(betas), "--clocks", "horvath", "--out", str(tmp_path / "out")])
    assert code == personal_report.EXIT_MISSING_RUNTIME == 4
    assert "pandas" in (tmp_path / "out" / "report.md").read_text(encoding="utf-8")
