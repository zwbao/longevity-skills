"""Report wording: paper card first, boundary last, no medicine advice, cohort numbers not in the title."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import personal_report  # noqa: E402
from presets import BOUNDARY, COHORT_N  # noqa: E402
from test_manifest import _csv, answers  # noqa: E402


def _text(tmp_path: Path, n: int) -> str:
    return personal_report.report(tmp_path / f"out{n}", _csv(tmp_path / f"m{n}.csv", answers(n))).read_text(encoding="utf-8")


def test_card_boundary_and_wording(tmp_path: Path):
    for n in (0, 2, 5, 9):
        text = _text(tmp_path, n)
        lines = text.splitlines()
        assert lines[0].startswith("# ") and not any(ch.isdigit() for ch in lines[0])
        assert lines[2] == "## 论文卡片"
        assert text.rstrip().splitlines()[-1] == f"边界: {BOUNDARY}"
        assert "不是你自己会不会出现这些结局的概率" in text
        for banned in ("建议服用", "开始服用", "停用", "剂量为"):
            assert banned not in text
        assert str(COHORT_N) not in lines[0]


def test_zero_category_is_the_referent(tmp_path: Path):
    text = _text(tmp_path, 0)
    assert "参照组" in text and "比值比（95% CI）" not in text


def test_footnote_c_note_for_sexual_perpetration(tmp_path: Path):
    text = _text(tmp_path, 2)
    assert "| 对伴侣施加性暴力 | 0.0%（0 人） | 1.4%（12 人） | NA（并入参照组） |" in text
    assert "表 3 脚注 c" in text
