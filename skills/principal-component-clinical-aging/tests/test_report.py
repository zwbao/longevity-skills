import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import personal_report
from presets import BOUNDARY, huq050_from_visits, self_health_index, smoking_score
from test_manifest import SEQN24, _csv


def test_report_keeps_boundary_and_does_not_advise(tmp_path: Path):
    meds = tmp_path / "meds.txt"
    meds.write_text("阿托伐他汀\n", encoding="utf-8")
    labs = tmp_path / "labs.csv"
    labs.write_text("项目,结果,单位\n谷丙转氨酶,80,U/L\n", encoding="utf-8")
    out = tmp_path / "out"
    code = personal_report.main(["--measurements", str(_csv(tmp_path / "m.csv", SEQN24)), "--age", "53", "--sex", "女",
                                 "--medications", str(meds), "--labs", str(labs), "--out", str(out)])
    assert code == 0
    text = (out / "report.md").read_text(encoding="utf-8")
    assert text.rstrip().splitlines()[-1] == f"边界: {BOUNDARY}"
    assert "## 论文卡片" in text
    assert "56.9 岁" in text
    assert "阿托伐他汀：LinAge 不读用药。不能据此停。" in text
    assert "谷丙转氨酶,80,U/L" in text
    for phrase in ("建议停", "建议服用", "应该开始"):
        assert phrase not in text


def test_methods_formulas():
    # Methods: self-health index = ((fair x 2) + (poor x 4)) x (1 - better x 0.5 + worse).
    assert self_health_index(0, 1, 0, 1) == 8
    assert self_health_index(1, 0, 1, 0) == 1
    # linAge.R digiCot(): <10, 10-<100, 100-<200, >=200.
    assert [smoking_score(x) for x in (9.9, 10, 99.9, 100, 199.9, 200)] == [0, 1, 1, 2, 2, 3]
    # NHANES 1999-2000 HUQ050 codes: 0, 1, 2-3, 4-9, 10-12, 13+.
    assert [huq050_from_visits(n) for n in (0, 1, 2, 3, 4, 9, 10, 12, 13, 40)] == [0, 1, 2, 2, 3, 3, 4, 4, 5, 5]
