import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import personal_report
from presets import BOUNDARY, CPG_COEF


def test_report_boundary_meds_and_labs(tmp_path: Path):
    meas = tmp_path / "m.csv"
    meas.write_text("item,value\n" + "".join(f"{site},0.4\n" for site in CPG_COEF), encoding="utf-8")
    meds = tmp_path / "meds.txt"
    meds.write_text("不存在的药\n", encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n谷丙转氨酶,80,U/L\n", encoding="utf-8")
    code = personal_report.main(["--measurements", str(meas), "--medications", str(meds), "--labs", str(labs), "--out", str(tmp_path / "out")])
    assert code == 0
    text = (tmp_path / "out" / "report.md").read_text(encoding="utf-8")
    assert "## 论文卡片" in text
    assert text.splitlines()[-1] == f"边界: {BOUNDARY}"
    assert "不存在的药：名单里没有这个名字。不能据此停。" in text
    assert "谷丙转氨酶 80 U/L" in text
    assert "不增删" in text
    for word in ("该开始", "建议停", "建议开始", "死亡风险"):
        assert word not in text
    title = text.splitlines()[0]
    assert title.startswith("# ") and not any(ch.isdigit() for ch in title)
    result = json.loads((tmp_path / "out" / "result.json").read_text(encoding="utf-8"))
    assert result["outputs"]["dnam_ic"]["value"] is not None


def test_no_measurements_lists_missing_sites(tmp_path: Path):
    code = personal_report.main(["--out", str(tmp_path / "out")])
    assert code == 3
    text = (tmp_path / "out" / "report.md").read_text(encoding="utf-8")
    assert "缺少" in text and text.splitlines()[-1] == f"边界: {BOUNDARY}"
