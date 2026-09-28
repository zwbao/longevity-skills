"""pyaging entry: matrix checks, the report, and result.json, without pyaging installed."""

import csv
import json
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report  # noqa: E402
import skillkit  # noqa: E402

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))
YEARS = ["years"]


def _matrix(path: Path, values) -> Path:
    path.write_text("sample,cg00000029,cg00000108,age\n" + "".join(f"s{i},{a},{b},50\n" for i, (a, b) in enumerate(values)), encoding="utf-8")
    return path


def _plain_matrix(path: Path, header: str, rows) -> Path:
    path.write_text(header + "\n" + "".join(row + "\n" for row in rows), encoding="utf-8")
    return path


def _stub(values, warnings=(), units=None, filled=None):
    """A predict() replacement that returns fixed values and records what it was given."""
    calls = []

    def fake_predict(path, clocks, metadata, covariates):
        calls.append({"clocks": list(clocks), "metadata": list(metadata), "covariates": dict(covariates)})
        return personal_report.Prediction(values, list(warnings), dict(units or {}), dict(filled or {}))

    fake_predict.calls = calls
    return fake_predict


def _report(tmp_path) -> str:
    return (tmp_path / "out" / "report.md").read_text(encoding="utf-8")


def _outputs(tmp_path) -> dict:
    return json.loads((tmp_path / "out" / "result.json").read_text(encoding="utf-8"))["outputs"]


def test_manifest_is_verified_and_prefixes_dnam_outputs():
    assert MANIFEST["inputs_status"] == "verified"
    assert MANIFEST["entry"]["runtime"] == "pyaging"
    keys = [item["key"] for item in MANIFEST["outputs"]]
    assert "phenoage" not in keys, "DNAm PhenoAge must not share the blood PhenoAge output key"
    assert all(key.startswith("dnam_") for key in keys)


def test_every_declared_output_names_its_pyaging_clock():
    keys = [item["key"] for item in MANIFEST["outputs"]]
    assert sorted(keys) == sorted(personal_report.OUTPUT_CLOCKS)
    assert personal_report.OUTPUT_CLOCKS["dnam_phenoage"] == "dnamphenoage"
    assert "phenoage" not in personal_report.OUTPUT_CLOCKS.values(), "pyaging phenoage is the blood-chemistry clock"
    units = {item["key"]: item["unit"] for item in MANIFEST["outputs"]}
    assert units["dnam_tl"] == "kb" and units["dnam_grimage"] == "a" and units["dnam_dunedinpoam38"] == "1"


def test_sex_is_a_profile_input_with_its_flag():
    assert MANIFEST["entry"]["sex_flag"] == "--sex"
    sex = next(item for item in MANIFEST["inputs"] if item["key"] == "sex")
    assert sex["from"] == "profile" and sex["flag"] == "--sex" and sex["required"] is False


def test_percent_values_are_refused(tmp_path):
    code = personal_report.main(["--matrix", str(_matrix(tmp_path / "m.csv", [(45, 60)])), "--out", str(tmp_path / "out")])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    text = (tmp_path / "out" / "report.md").read_text(encoding="utf-8")
    assert "0 到 1" in text and "岁" not in text.split("## 输入没有通过检查")[1].split("边界")[0].replace("实足年龄", "")


def test_age_column_is_not_read_as_a_beta_value(tmp_path, monkeypatch):
    monkeypatch.setattr(personal_report, "predict", _stub({"s0": {"horvath2013": 51.0}}, units={"horvath2013": YEARS}))
    matrix = _matrix(tmp_path / "m.csv", [(0.45, 0.6)])
    assert personal_report.main(["--matrix", str(matrix), "--out", str(tmp_path / "out")]) == 0


def test_idat_and_missing_files_are_refused(tmp_path):
    idat = tmp_path / "x.idat"
    idat.write_bytes(b"\x00")
    assert personal_report.main(["--matrix", str(idat), "--out", str(tmp_path / "a")]) == skillkit.EXIT_INPUT_PROBLEM
    assert personal_report.main(["--matrix", str(tmp_path / "none.csv"), "--out", str(tmp_path / "b")]) == skillkit.EXIT_INPUT_PROBLEM


def test_report_and_result_with_a_stubbed_pyaging(tmp_path, monkeypatch):
    fake = _stub(
        {"s0": {"horvath2013": 52.3, "dunedinpace": 1.04}},
        ["3 missing features were imputed"],
        {"horvath2013": YEARS, "dunedinpace": ["biological years per chronological year"]},
    )
    monkeypatch.setattr(personal_report, "predict", fake)
    matrix = _matrix(tmp_path / "m.csv", [(0.45, 0.6)])
    code = personal_report.main(["--matrix", str(matrix), "--clocks", "horvath2013,dunedinpace", "--age", "50", "--out", str(tmp_path / "out")])
    assert code == 0
    text = _report(tmp_path)
    assert "horvath2013：52.3 岁，减实足年龄 +2.3 岁" in text
    assert "不是年龄" in text
    assert "imputed" in text
    assert text.splitlines()[-1].startswith("边界: ")
    result = _outputs(tmp_path)
    assert result["dnam_horvath2013"]["value"] == 52.3
    assert result["dnam_dunedinpace"]["value"] == 1.04
    assert result["dnam_hannum"]["value"] is None


def test_missing_runtime_is_reported_not_guessed(tmp_path, monkeypatch):
    def no_pyaging(path, clocks, metadata, covariates):
        raise ImportError("No module named 'pyaging'")

    monkeypatch.setattr(personal_report, "predict", no_pyaging)
    code = personal_report.main(["--matrix", str(_matrix(tmp_path / "m.csv", [(0.4, 0.5)])), "--out", str(tmp_path / "out")])
    assert code == personal_report.EXIT_MISSING_RUNTIME
    assert "没有安装 pyaging" in (tmp_path / "out" / "report.md").read_text(encoding="utf-8")


# Bug 1: GrimAge takes age and sex as model features; pyaging fills a missing one with a 65-year-old woman.

def test_grimage_without_age_and_sex_is_refused(tmp_path, monkeypatch):
    fake = _stub({"s0": {"grimage": 70.0}}, units={"grimage": YEARS})
    monkeypatch.setattr(personal_report, "predict", fake)
    matrix = _plain_matrix(tmp_path / "m.csv", "sample,cg00000029", ["s0,0.4"])
    code = personal_report.main(["--matrix", str(matrix), "--clocks", "grimage", "--out", str(tmp_path / "out")])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    assert fake.calls == [], "pyaging must not run"
    text = _report(tmp_path)
    assert "--age" in text and "--sex" in text and "65 岁女性" in text
    assert all(item["value"] is None for item in _outputs(tmp_path).values())


def test_grimage_with_age_but_no_sex_is_refused(tmp_path, monkeypatch):
    fake = _stub({"s0": {"grimage": 70.0}}, units={"grimage": YEARS})
    monkeypatch.setattr(personal_report, "predict", fake)
    matrix = _plain_matrix(tmp_path / "m.csv", "sample,cg00000029", ["s0,0.4"])
    code = personal_report.main(["--matrix", str(matrix), "--clocks", "grimage", "--age", "50", "--out", str(tmp_path / "out")])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    text = _report(tmp_path)
    assert "--sex" in text and "性别（female）" in text
    assert "实足年龄（age）" not in text


def test_age_only_clock_runs_without_sex(tmp_path, monkeypatch):
    fake = _stub({"s0": {"grimage2packyrs": 12.0}}, units={"grimage2packyrs": ["pack-years"]})
    monkeypatch.setattr(personal_report, "predict", fake)
    matrix = _plain_matrix(tmp_path / "m.csv", "sample,cg00000029", ["s0,0.4"])
    code = personal_report.main(["--matrix", str(matrix), "--clocks", "grimage2packyrs", "--age", "50", "--out", str(tmp_path / "out")])
    assert code == 0
    assert fake.calls[0]["covariates"] == {"age": 50.0}
    assert "grimage2packyrs：12 包年（不是年龄" in _report(tmp_path)


def test_bad_sex_text_is_refused(tmp_path, monkeypatch):
    monkeypatch.setattr(personal_report, "predict", _stub({}))
    matrix = _plain_matrix(tmp_path / "m.csv", "sample,cg00000029", ["s0,0.4"])
    code = personal_report.main(["--matrix", str(matrix), "--clocks", "grimage", "--age", "50", "--sex", "x", "--out", str(tmp_path / "out")])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    text = _report(tmp_path)
    assert "--sex 只接受" in text
    assert "性别（female）" not in text, "a bad --sex is a parse problem, not also a missing one"


def test_sex_words_map_to_female_indicator():
    for raw in ("f", "F", "female", "Female", "女", "女性"):
        assert personal_report.parse_sex(raw) == 1.0, raw
    for raw in ("m", "M", "male", "男", "男性"):
        assert personal_report.parse_sex(raw) == 0.0, raw
    assert personal_report.parse_sex("x") is None and personal_report.parse_sex(None) is None


def test_matrix_columns_supply_age_and_female(tmp_path, monkeypatch):
    fake = _stub({"s0": {"grimage": 55.0}, "s1": {"grimage": 70.0}}, units={"grimage": YEARS})
    monkeypatch.setattr(personal_report, "predict", fake)
    matrix = _plain_matrix(tmp_path / "m.csv", "sample,cg00000029,age,female", ["s0,0.4,50,1", "s1,0.5,65,0"])
    code = personal_report.main(["--matrix", str(matrix), "--clocks", "grimage", "--out", str(tmp_path / "out")])
    assert code == 0
    assert fake.calls[0]["covariates"] == {}, "matrix columns are already in the frame"
    text = _report(tmp_path)
    assert "grimage：55.0 岁，减实足年龄 +5.0 岁" in text
    assert "grimage：70.0 岁，减实足年龄 +5.0 岁" in text, "each sample uses its own age column"


def test_blank_or_bad_covariate_column_is_refused(tmp_path, monkeypatch):
    monkeypatch.setattr(personal_report, "predict", _stub({}))
    matrix = _plain_matrix(tmp_path / "m.csv", "sample,cg00000029,age,female", ["s0,0.4,,F"])
    code = personal_report.main(["--matrix", str(matrix), "--clocks", "grimage", "--out", str(tmp_path / "out")])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    text = _report(tmp_path)
    assert "age 列" in text and "female 列只能填 0（男）或 1（女）" in text


def test_flag_and_column_that_disagree_are_refused(tmp_path, monkeypatch):
    fake = _stub({"s0": {"grimage": 55.0}}, units={"grimage": YEARS})
    monkeypatch.setattr(personal_report, "predict", fake)
    matrix = _plain_matrix(tmp_path / "m.csv", "sample,cg00000029,age,female", ["s0,0.4,50,1"])
    code = personal_report.main(["--matrix", str(matrix), "--clocks", "grimage", "--age", "50", "--sex", "男", "--out", str(tmp_path / "out")])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    assert fake.calls == []
    assert "--sex 和矩阵的 female 列不一致" in _report(tmp_path)


def test_prepare_frame_keeps_covariates_out_of_metadata():
    class Frame:
        def __init__(self):
            self.data = {"cg00000029": [0.4], "age": [50.0], "batch": [1.0]}

        @property
        def columns(self):
            return list(self.data)

        def __setitem__(self, name, value):
            self.data[name] = [value] * 1

    frame, kept = personal_report.prepare_frame(Frame(), ["age", "batch", "female", "absent"], {"age": 50.0, "female": 1.0})
    assert kept == ["batch"]
    assert frame.data["female"] == [1.0] and frame.data["age"] == [50.0]


class _FakeFrame:
    """Just enough of a pandas DataFrame for predict()."""

    def __init__(self, header, rows):
        self.index_name = None
        self.index = None
        self.data = {name: [row[i] for row in rows] for i, name in enumerate(header)}

    @property
    def columns(self):
        return list(self.data)

    def set_index(self, name):
        self.index = [str(value) for value in self.data.pop(name)]
        self.index_name = name
        return self

    def __setitem__(self, name, value):
        self.data[name] = [value] * len(self.index)


def _fake_modules(monkeypatch, clock_values, units, missing=None):
    """Install fake pandas and pyaging modules; return the list that records df_to_adata calls."""
    seen = []

    def read_csv(path, converters=None, **kwargs):
        assert converters == {0: str}
        with open(path, encoding="utf-8", newline="") as handle:
            rows = list(csv.reader(handle))
        header, body = rows[0], rows[1:]
        typed = [[row[0]] + [float(cell) for cell in row[1:]] for row in body]
        return _FakeFrame(header, typed)

    class Obs:
        def __init__(self, samples):
            self.rows = {sample: {} for sample in samples}

        def iterrows(self):
            return iter(self.rows.items())

    class AnnData:
        def __init__(self, frame):
            self.obs = Obs(frame.index)
            self.uns = {}

    def df_to_adata(frame, metadata_cols=None):
        seen.append({"columns": {name: list(values) for name, values in frame.data.items()}, "metadata_cols": list(metadata_cols or [])})
        return AnnData(frame)

    def predict_age(adata, clocks):
        for clock in clocks:
            for row in adata.obs.rows.values():
                row[clock] = clock_values[clock]
            adata.uns[f"{clock}_metadata"] = {"clock_name": clock, "unit": units[clock]}
            adata.uns[f"{clock}_missing_features"] = list((missing or {}).get(clock, []))

    pandas = types.ModuleType("pandas")
    pandas.read_csv = read_csv
    pyaging = types.ModuleType("pyaging")
    pyaging.pp = types.SimpleNamespace(df_to_adata=df_to_adata)
    pyaging.pred = types.SimpleNamespace(predict_age=predict_age)
    monkeypatch.setitem(sys.modules, "pandas", pandas)
    monkeypatch.setitem(sys.modules, "pyaging", pyaging)
    return seen


def test_frame_handed_to_pyaging_carries_age_and_female(tmp_path, monkeypatch):
    seen = _fake_modules(monkeypatch, {"grimage": 58.2, "dnamtl": 7.1}, {"grimage": YEARS, "dnamtl": ["kilobases"]})
    matrix = _matrix(tmp_path / "m.csv", [(0.45, 0.6)])
    code = personal_report.main([
        "--matrix", str(matrix), "--clocks", "grimage,dnamtl", "--age", "50", "--sex", "女",
        "--metadata-cols", "age,batch", "--out", str(tmp_path / "out"),
    ])
    assert code == 0
    [call] = seen
    assert call["columns"]["age"] == [50.0]
    assert call["columns"]["female"] == [1.0]
    assert "age" not in call["metadata_cols"] and "female" not in call["metadata_cols"]
    text = _report(tmp_path)
    assert "grimage：58.2 岁，减实足年龄 +8.2 岁" in text
    assert "dnamtl：7.1 kb（千碱基）" in text
    result = _outputs(tmp_path)
    assert result["dnam_grimage"]["value"] == 58.2
    assert result["dnam_tl"]["value"] == 7.1 and result["dnam_tl"]["unit"] == "kb"


def test_male_is_written_as_zero(tmp_path, monkeypatch):
    seen = _fake_modules(monkeypatch, {"grimage2": 48.0}, {"grimage2": YEARS})
    matrix = _plain_matrix(tmp_path / "m.csv", "sample,cg00000029", ["01,0.4"])
    code = personal_report.main(["--matrix", str(matrix), "--clocks", "grimage2", "--age", "45", "--sex", "m", "--out", str(tmp_path / "out")])
    assert code == 0
    assert seen[0]["columns"]["female"] == [0.0] and seen[0]["columns"]["age"] == [45.0]
    assert "### 样本 01" in _report(tmp_path), "sample names stay text"


def test_covariate_filled_by_pyaging_is_refused_after_the_run(tmp_path, monkeypatch):
    _fake_modules(monkeypatch, {"newclock": 61.0}, {"newclock": YEARS}, missing={"newclock": ["cg1", "female"]})
    matrix = _plain_matrix(tmp_path / "m.csv", "sample,cg00000029", ["s0,0.4"])
    code = personal_report.main(["--matrix", str(matrix), "--clocks", "newclock", "--age", "50", "--out", str(tmp_path / "out")])
    assert code == skillkit.EXIT_INPUT_PROBLEM
    text = _report(tmp_path)
    assert "newclock" in text and "性别（female）" in text and "61" not in text


# Bug 2: only year-unit clocks are ages.

def test_non_year_outputs_carry_their_unit_and_no_gap(tmp_path, monkeypatch):
    fake = _stub(
        {"s0": {"dnamtl": 7.123, "zhangmortality": 0.42, "epitoc1": 0.061, "horvath2013": 48.0}},
        units={"dnamtl": ["kilobases"], "zhangmortality": ["unitless"], "epitoc1": ["beta value"], "horvath2013": YEARS},
    )
    monkeypatch.setattr(personal_report, "predict", fake)
    matrix = _matrix(tmp_path / "m.csv", [(0.45, 0.6)])
    code = personal_report.main(["--matrix", str(matrix), "--clocks", "dnamtl,zhangmortality,epitoc1,horvath2013", "--age", "50", "--out", str(tmp_path / "out")])
    assert code == 0
    lines = {line.split("：")[0]: line for line in _report(tmp_path).splitlines() if line.startswith("- ")}
    assert lines["- dnamtl"] == "- dnamtl：7.123 kb（千碱基）（不是年龄，不和实足年龄相减）"
    assert "无单位分数" in lines["- zhangmortality"] and "β 值" in lines["- epitoc1"]
    for clock in ("dnamtl", "zhangmortality", "epitoc1"):
        assert "岁" not in lines[f"- {clock}"] and "减实足年龄 " not in lines[f"- {clock}"]
    assert lines["- horvath2013"] == "- horvath2013：48.0 岁，减实足年龄 -2.0 岁"
    result = _outputs(tmp_path)
    assert result["dnam_tl"]["value"] == 7.123
    assert result["dnam_zhangmortality"]["value"] == 0.42
    assert result["dnam_epitoc1"]["value"] == 0.061


def test_unknown_unit_is_not_an_age(tmp_path, monkeypatch):
    monkeypatch.setattr(personal_report, "predict", _stub({"s0": {"horvath2013": 48.0}}))
    matrix = _matrix(tmp_path / "m.csv", [(0.45, 0.6)])
    assert personal_report.main(["--matrix", str(matrix), "--age", "50", "--out", str(tmp_path / "out")]) == 0
    line = next(line for line in _report(tmp_path).splitlines() if line.startswith("- horvath2013"))
    assert "没有记录单位" in line and "岁" not in line


# Bug 3: result.json carries every declared clock, and blood PhenoAge never becomes dnam_phenoage.

def test_result_json_carries_new_outputs_and_keeps_blood_phenoage_out(tmp_path, monkeypatch):
    fake = _stub(
        {"s0": {"phenoage": 61.0, "dnamphenoage": 47.5, "skinandblood": 49.1, "dunedinpoam38": 0.98}},
        units={"phenoage": YEARS, "dnamphenoage": YEARS, "skinandblood": YEARS, "dunedinpoam38": ["biological years per chronological year"]},
    )
    monkeypatch.setattr(personal_report, "predict", fake)
    matrix = _matrix(tmp_path / "m.csv", [(0.45, 0.6)])
    code = personal_report.main(["--matrix", str(matrix), "--clocks", "phenoage,dnamphenoage,skinandblood,dunedinpoam38", "--age", "50", "--out", str(tmp_path / "out")])
    assert code == 0
    result = _outputs(tmp_path)
    assert result["dnam_phenoage"]["value"] == 47.5
    assert result["dnam_skinandblood"]["value"] == 49.1
    assert result["dnam_dunedinpoam38"]["value"] == 0.98
    assert 61.0 not in [item["value"] for item in result.values()]
    assert "dunedinpoam38：0.980（每过一年的衰老速度，不是年龄）" in _report(tmp_path)
