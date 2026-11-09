import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report
from presets import BOUNDARY

FIXTURE = ROOT / "tests" / "fixtures" / "epg_aging_demo_450k.csv"


def _sample_rows():
    with FIXTURE.open(encoding="utf-8", newline="") as handle:
        row = next(csv.DictReader(handle))
    return [(k, v) for k, v in row.items() if k != "sample"]


def test_report_card_boundary_meds_labs(tmp_path: Path):
    meas = tmp_path / "m.csv"
    meas.write_text("item,value\n" + "".join(f"{k},{v}\n" for k, v in _sample_rows()) + "cg99999999,0.5\n", encoding="utf-8")
    meds = tmp_path / "meds.txt"
    meds.write_text("二甲双胍\n", encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n超敏C反应蛋白,2.1,mg/L\n", encoding="utf-8")
    out = tmp_path / "out"
    code = personal_report.main(["--measurements", str(meas), "--age", "58", "--medications", str(meds),
                                 "--labs", str(labs), "--out", str(out)])
    assert code == 0
    text = (out / "report.md").read_text(encoding="utf-8")
    lines = text.splitlines()
    assert lines[0].startswith("# ") and not any(ch.isdigit() for ch in lines[0])
    assert "## 论文卡片" in text and text.index("## 论文卡片") < text.index("## 你的结果")
    assert lines[-1] == f"边界: {BOUNDARY}"
    assert "二甲双胍：这个方法不涉及任何药物，不能据此停" in text
    assert "超敏C反应蛋白 2.1 mg/L" in text and "不增删" in text
    assert "58 岁" in text and "不是生物年龄" in text
    assert "另有 1 行" in text
    assert "EPIC 芯片模型）：没有算" in text
    for word in ("建议开始", "建议停", "剂量", "你的死亡风险是"):
        assert word not in text
    result = json.loads((out / "result.json").read_text(encoding="utf-8"))["outputs"]
    assert result["dmp_dvp_450k_score"]["value"] is not None


def test_no_measurements_exits_3(tmp_path: Path):
    out = tmp_path / "out"
    code = personal_report.main(["--out", str(out)])
    assert code == 3
    text = (out / "report.md").read_text(encoding="utf-8")
    assert "## 论文卡片" in text and "缺 789 个" in text and "缺 598 个" in text
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
    problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))["problems"]
    assert len(problems) == 598


def test_age_out_of_range_exits_3(tmp_path: Path):
    meas = tmp_path / "m.csv"
    meas.write_text("item,value\n" + "".join(f"{k},{v}\n" for k, v in _sample_rows()), encoding="utf-8")
    code = personal_report.main(["--measurements", str(meas), "--age", "580", "--out", str(tmp_path / "out")])
    assert code == 3
