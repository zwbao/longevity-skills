"""skill.json matches presets, the published bands hold at every edge, and bad input stops the run.

Expected values come only from printed numbers: range 5-25 and cut-off 21
(Rosen 1999 abstract), the five bands 5-7, 8-11, 12-16, 17-21, 22-25 (Rhoden
2002 abstract). No person-level worked example is printed.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report
import skillkit
from presets import BANDS, CUTOFF, ITEMS, KEYS, TOTAL_MAX, TOTAL_MIN, band, total

MANIFEST = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))


def _answers_for(score: int) -> dict:
    """Five 1-5 item scores that add up to score (synthetic)."""
    left = score - 5
    out = {}
    for key in KEYS:
        extra = min(4, left)
        out[key] = 1 + extra
        left -= extra
    assert total(out) == score
    return out


def _csv(path: Path, answers: dict, unit: str = "") -> Path:
    path.write_text("item,value,unit\n" + "".join(f"{k},{v},{unit}\n" for k, v in answers.items()), encoding="utf-8")
    return path


def _run(tmp_path: Path, answers: dict, *flags: str, unit: str = ""):
    out = tmp_path / "out"
    args = ["--measurements", str(_csv(tmp_path / "m.csv", answers, unit)), *flags, "--out", str(out)]
    code = personal_report.main(args)
    outputs = json.loads((out / "result.json").read_text(encoding="utf-8"))["outputs"]
    return code, (out / "report.md").read_text(encoding="utf-8"), outputs, out


def test_manifest_matches_presets():
    declared = [item for item in MANIFEST["inputs"] if item["from"] == "measurements"]
    assert [item["key"] for item in declared] == list(KEYS)
    for item, (key, number, topic) in zip(declared, ITEMS):
        assert item["unit"] == "score" and item["range"] == [1, 5] and item["required"] is True
        assert f"第{number}题" in item["label_zh"] and topic in item["label_zh"]
    sex = skillkit.spec_by_key(MANIFEST, "sex")
    assert (sex["from"], sex["flag"], sex["required"]) == ("profile", "--sex", True)
    attempted = skillkit.spec_by_key(MANIFEST, "attempted")
    assert (attempted["from"], attempted["flag"]) == ("argument", "--attempted")
    assert MANIFEST["entry"]["sex_flag"] == "--sex"
    assert MANIFEST["inputs_status"] == "verified"
    assert [(o["key"], o["unit"]) for o in MANIFEST["outputs"]] == [("iief5_score", "score"), ("iief5_band", "")]


def test_printed_range_cutoff_and_bands():
    assert (TOTAL_MIN, TOTAL_MAX, CUTOFF) == (5, 25, 21)
    assert [(low, high) for low, high, _label, _en in BANDS] == [(22, 25), (17, 21), (12, 16), (8, 11), (5, 7)]
    covered = sorted(score for low, high, _l, _e in BANDS for score in range(low, high + 1))
    assert covered == list(range(5, 26))
    with pytest.raises(ValueError):
        band(4)


@pytest.mark.parametrize(
    "score, label",
    [(5, "重度"), (7, "重度"), (8, "中度"), (11, "中度"), (12, "轻到中度"), (16, "轻到中度"),
     (17, "轻度"), (21, "轻度"), (22, "无勃起功能障碍"), (25, "无勃起功能障碍")],
)
def test_every_band_edge(tmp_path: Path, score, label):
    code, text, outputs, out = _run(tmp_path, _answers_for(score), "--sex", "male", "--age", "55", "--attempted", "yes")
    assert code == 0
    assert outputs["iief5_score"]["value"] == score
    assert outputs["iief5_band"]["value"] == label
    assert f"得分是 **{score}**" in text and f"「{label}」" in text
    assert not (out / "problems.json").exists()


def test_plain_lines_and_fen_unit(tmp_path: Path):
    measures = tmp_path / "m.txt"
    measures.write_text("第1题,4,分\n第2题,4\n第3题,3\n第4题,4\n第5题,3\n", encoding="utf-8")
    out = tmp_path / "out"
    assert personal_report.main(["--measurements", str(measures), "--sex", "男", "--out", str(out)]) == 0
    result = json.loads((out / "result.json").read_text(encoding="utf-8"))["outputs"]
    assert result["iief5_score"]["value"] == 18 and result["iief5_band"]["value"] == "轻度"


@pytest.mark.parametrize(
    "change, flags, reason",
    [
        ({"iief5_item3": "0"}, ["--sex", "male"], "没有尝试性交"),
        ({}, ["--sex", "female"], "不适用于女性"),
        ({}, [], "需要性别"),
        ({}, ["--sex", "male", "--attempted", "no"], "只适用于过去 6 个月尝试过性交的男性"),
        ({}, ["--sex", "male", "--attempted", "maybe"], "只接受 yes 或 no"),
        ({"iief5_item1": "6"}, ["--sex", "male"], "不在合理范围"),
        ({"iief5_item2": "3.5"}, ["--sex", "male"], "整数"),
        ({"iief5_item5": None}, ["--sex", "male"], "缺少"),
        ({}, ["--sex", "male", "--age", "150"], "实足年龄"),
    ],
    ids=["zero", "female", "no-sex", "not-attempted", "attempted-text", "above-5", "half", "missing", "age"],
)
def test_bad_input_stops_the_computation(tmp_path: Path, change, flags, reason):
    answers = _answers_for(18)
    for key, value in change.items():
        if value is None:
            answers.pop(key)
        else:
            answers[key] = value
    code, text, outputs, out = _run(tmp_path, answers, *flags)
    assert code == skillkit.EXIT_INPUT_PROBLEM
    assert outputs["iief5_score"]["value"] is None and outputs["iief5_band"]["value"] is None
    assert (out / "problems.json").exists()
    assert "输入没有通过检查" in text and reason in text
    assert "## 论文卡片" in text
    assert text.rstrip().splitlines()[-1].startswith("边界: ")


def test_wrong_unit_is_refused(tmp_path: Path):
    code, text, outputs, _out = _run(tmp_path, _answers_for(20), "--sex", "male", unit="mmol/L")
    assert code == skillkit.EXIT_INPUT_PROBLEM and outputs["iief5_score"]["value"] is None
    assert "不能换算" in text


def test_standard_dispatch_flags_are_accepted_and_ignored(tmp_path: Path):
    meds = tmp_path / "meds.txt"
    meds.write_text("氨氯地平\n", encoding="utf-8")
    code, _text, outputs, _out = _run(tmp_path, _answers_for(23), "--sex", "male", "--medications", str(meds), "--labs", str(meds))
    assert code == 0 and outputs["iief5_band"]["value"] == "无勃起功能障碍"
