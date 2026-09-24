"""pyaging entry: matrix checks, the report, and result.json, without pyaging installed."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report  # noqa: E402
import skillkit  # noqa: E402

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))


def _matrix(path: Path, values) -> Path:
    path.write_text("sample,cg00000029,cg00000108,age\n" + "".join(f"s{i},{a},{b},50\n" for i, (a, b) in enumerate(values)), encoding="utf-8")
    return path


def test_manifest_is_verified_and_prefixes_dnam_outputs():
    assert MANIFEST["inputs_status"] == "verified"
    assert MANIFEST["entry"]["runtime"] == "pyaging"
    keys = [item["key"] for item in MANIFEST["outputs"]]
    assert "phenoage" not in keys, "DNAm PhenoAge must not share the blood PhenoAge output key"
    assert all(key.startswith("dnam_") for key in keys)


def test_percent_values_are_refused(tmp_path):
    code = personal_report.main(["--matrix", str(_matrix(tmp_path / "m.csv", [(45, 60)])), "--out", str(tmp_path / "out")])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    text = (tmp_path / "out" / "report.md").read_text(encoding="utf-8")
    assert "0 到 1" in text and "岁" not in text.split("## 输入没有通过检查")[1].split("边界")[0].replace("实足年龄", "")


def test_idat_and_missing_files_are_refused(tmp_path):
    idat = tmp_path / "x.idat"
    idat.write_bytes(b"\x00")
    assert personal_report.main(["--matrix", str(idat), "--out", str(tmp_path / "a")]) == skillkit.EXIT_INPUT_PROBLEM
    assert personal_report.main(["--matrix", str(tmp_path / "none.csv"), "--out", str(tmp_path / "b")]) == skillkit.EXIT_INPUT_PROBLEM


def test_report_and_result_with_a_stubbed_pyaging(tmp_path, monkeypatch):
    def fake_predict(path, clocks, metadata):
        return {"s0": {"horvath2013": 52.3, "dunedinpace": 1.04}}, ["3 missing features were imputed"]

    monkeypatch.setattr(personal_report, "predict", fake_predict)
    matrix = _matrix(tmp_path / "m.csv", [(0.45, 0.6)])
    code = personal_report.main(["--matrix", str(matrix), "--clocks", "horvath2013,dunedinpace", "--age", "50", "--out", str(tmp_path / "out")])
    assert code == 0
    text = (tmp_path / "out" / "report.md").read_text(encoding="utf-8")
    assert "horvath2013：52.3 岁，减实足年龄 +2.3 岁" in text
    assert "不是年龄" in text
    assert "imputed" in text
    assert text.splitlines()[-1].startswith("边界: ")
    result = json.loads((tmp_path / "out" / "result.json").read_text(encoding="utf-8"))["outputs"]
    assert result["dnam_horvath2013"]["value"] == 52.3
    assert result["dnam_dunedinpace"]["value"] == 1.04
    assert result["dnam_hannum"]["value"] is None


def test_missing_runtime_is_reported_not_guessed(tmp_path, monkeypatch):
    def no_pyaging(path, clocks, metadata):
        raise ImportError("No module named 'pyaging'")

    monkeypatch.setattr(personal_report, "predict", no_pyaging)
    code = personal_report.main(["--matrix", str(_matrix(tmp_path / "m.csv", [(0.4, 0.5)])), "--out", str(tmp_path / "out")])
    assert code == personal_report.EXIT_MISSING_RUNTIME
    assert "没有安装 pyaging" in (tmp_path / "out" / "report.md").read_text(encoding="utf-8")
