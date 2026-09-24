"""skill.json inputs match presets, and out-of-range values stop the binning.

Run by hand against the old script: a telomere length in kb passed as --z
(6.8) was put in the longest quartile, a kb value passed as --ltl (7.2) was
echoed as the raw measurement, and --z abc crashed with a traceback.
A raw T/S ratio passed as --z stays inside the z range; the refusal message
and SKILL.md say so, but no range can catch it.
"""

import json
import sys
from decimal import Decimal
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report
import skillkit
from presets import Q1_BELOW, Q2_BELOW, Q4_AT

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))
QUARTILES = ("最短", "次短", "次长", "最长")


def _result(out: Path) -> dict:
    return json.loads((out / "result.json").read_text(encoding="utf-8"))["outputs"]


def test_manifest_matches_presets():
    inputs = {item["key"]: item for item in MANIFEST["inputs"]}
    assert {key: (item["from"], item.get("flag")) for key, item in inputs.items()} == {
        "z": ("argument", "--z"),
        "ltl": ("argument", "--ltl"),
    }
    assert "measurements_flag" not in MANIFEST["entry"]
    for item in inputs.values():
        assert skillkit.normalize_unit(item["unit"]) == "1"
    low, high = inputs["z"]["range"]
    assert Decimal(str(low)) < Q1_BELOW < Q2_BELOW < Q4_AT < Decimal(str(high))
    assert inputs["z"]["required"] is True
    assert inputs["ltl"]["required"] is False
    assert [item["key"] for item in MANIFEST["outputs"]] == ["ltl_quartile"]
    assert "unit" not in MANIFEST["outputs"][0]


def test_inputs_are_verified():
    assert MANIFEST["inputs_status"] == "verified"
    assert MANIFEST["entry"]["result_json"] is True


@pytest.mark.parametrize("argv, label", [
    (["--z", "6.8"], "z 标准化对数端粒"),
    (["--z", "-4.5"], "z 标准化对数端粒"),
    (["--z", "nan"], "z 标准化对数端粒"),
    (["--ltl", "7.2"], "未标准化端粒 T/S 比值"),
    (["--z", "-0.7", "--ltl", "7200"], "未标准化端粒 T/S 比值"),
])
def test_out_of_range_stops_the_binning(tmp_path: Path, argv, label):
    out = tmp_path / "out"
    assert personal_report.main([*argv, "--out", str(out)]) == skillkit.EXIT_INPUT_PROBLEM
    text = (out / "report.md").read_text(encoding="utf-8")
    assert text.splitlines()[0] == "# 白细胞端粒"
    assert "## 论文卡片" in text
    assert f"{label} 读成" in text and "不在合理范围" in text
    assert "所以这次没有分档" in text
    assert "T/S 比值" in text and "kb" in text
    assert not any(name in text for name in QUARTILES)
    assert "- 端粒分档" not in text
    assert "相当于横断面" not in text
    assert "474074" not in text
    assert text.splitlines()[-1] == f"边界: {personal_report.BOUNDARY}"
    assert (out / "problems.json").exists()
    assert _result(out)["ltl_quartile"]["value"] is None


@pytest.mark.parametrize("z, expected", [
    ("-0.7", "最短"),
    ("-0.65", "次短"),
    ("-0.002", "次长"),
    ("0.65", "最长"),
])
def test_result_json_holds_the_quartile(tmp_path: Path, z, expected):
    out = tmp_path / "out"
    assert personal_report.main(["--z", z, "--out", str(out)]) == 0
    assert f"- 端粒分档：{expected}。" in (out / "report.md").read_text(encoding="utf-8")
    result = _result(out)["ltl_quartile"]
    assert result["value"] == expected
    assert result["unit"] == ""
    assert not (out / "problems.json").exists()


def test_raw_ratio_alone_has_no_quartile(tmp_path: Path):
    out = tmp_path / "out"
    assert personal_report.main(["--ltl", "1.2", "--out", str(out)]) == 0
    assert "这次不分档" in (out / "report.md").read_text(encoding="utf-8")
    assert _result(out)["ltl_quartile"]["value"] is None
    assert not (out / "problems.json").exists()


def test_z_that_is_not_a_number_is_an_argument_error(tmp_path: Path):
    with pytest.raises(SystemExit) as stopped:
        personal_report.main(["--z", "abc", "--out", str(tmp_path / "out")])
    assert stopped.value.code == 2


def test_a_good_run_clears_old_problems(tmp_path: Path):
    out = tmp_path / "out"
    assert personal_report.main(["--z", "6.8", "--out", str(out)]) == skillkit.EXIT_INPUT_PROBLEM
    assert personal_report.main(["--z", "-0.7", "--out", str(out)]) == 0
    assert not (out / "problems.json").exists()
    assert _result(out)["ltl_quartile"]["value"] == "最短"
