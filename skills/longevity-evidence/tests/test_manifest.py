"""Evidence query: matching, grouping, citations, boundary, and result.json."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import query  # noqa: E402

ROWS = [
    {"id": "demo-a:rapamycin", "entity": "rapamycin", "entity_zh": "雷帕霉素", "entity_type": "drug",
     "aliases": ["sirolimus", "西罗莫司"], "claim_zh": "在果蝇实验里延长了寿命。", "direction": "extends_lifespan",
     "species": ["drosophila"], "evidence": "animal", "source": {"skill": "demo-a", "doi": "10.1/a", "locator": "Fig. 1"}},
    {"id": "demo-b:metformin", "entity": "metformin", "entity_zh": "二甲双胍", "entity_type": "drug",
     "claim_zh": "在人群队列里和较慢的衰老指标变化相关。", "direction": "associated",
     "species": ["human"], "evidence": "cohort", "source": {"skill": "demo-b", "doi": "10.1/b", "locator": "正文"}},
    {"id": "demo-c:FOXO3", "entity": "FOXO3", "entity_type": "gene", "claim_zh": "在百岁老人里被点名的长寿相关基因。",
     "direction": "named", "species": ["human"], "evidence": "case_control", "source": {"skill": "demo-c", "locator": "Table 1"}},
    {"id": "demo-d:urolithin-A", "entity": "urolithin A", "entity_zh": "尿石素A", "entity_type": "compound",
     "claim_zh": "在细胞实验里诱导线粒体自噬。", "species": ["cell_line"], "evidence": "in_vitro",
     "source": {"skill": "demo-d", "locator": "Fig. 2"}},
]


def _claims(tmp_path: Path) -> Path:
    path = tmp_path / "claims.jsonl"
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in ROWS), encoding="utf-8")
    return path


def test_manifest_is_verified():
    manifest = json.loads((ROOT / "skill.json").read_text(encoding="utf-8"))
    assert manifest["kind"] == "evidence" and manifest["inputs_status"] == "verified"
    assert {item["key"] for item in manifest["outputs"]} == {"match_count", "human_count"}


def test_search_by_chinese_name_alias_and_substring():
    assert [row["id"] for row in query.search(ROWS, "西罗莫司")] == ["demo-a:rapamycin"]
    assert [row["id"] for row in query.search(ROWS, "Rapamycin")] == ["demo-a:rapamycin"]
    assert [row["id"] for row in query.search(ROWS, "urolithin")] == ["demo-d:urolithin-A"]
    assert query.search(ROWS, "NMN") == []
    assert query.search(ROWS, "A") == []


def test_report_groups_and_cites(tmp_path):
    code = query.main(["--entity", "雷帕霉素", "--entity", "二甲双胍", "--entity", "NMN",
                       "--claims", str(_claims(tmp_path)), "--out", str(tmp_path / "out")])
    assert code == 0
    text = (tmp_path / "out" / "report.md").read_text(encoding="utf-8")
    rapa = text.split("## 查询：雷帕霉素")[1].split("## 查询：")[0]
    assert "没有关于它的人群研究" in rapa and "### 动物实验（1 条）" in rapa
    assert "[DOI](https://doi.org/10.1/a)" in rapa and "Fig. 1" in rapa
    metformin = text.split("## 查询：二甲双胍")[1].split("## 查询：")[0]
    assert "### 人群研究（1 条：队列研究 1；按证据强度排列）" in metformin
    assert "证据库里没有「NMN」" in text and "skills/evipedia/" in text
    assert text.splitlines()[-1].startswith("边界: ")
    for word in ("建议服用", "该开始", "剂量为"):
        assert word not in text
    result = json.loads((tmp_path / "out" / "result.json").read_text(encoding="utf-8"))["outputs"]
    assert result["match_count"]["value"] == 2 and result["human_count"]["value"] == 1


def test_medications_keep_the_stop_boundary(tmp_path):
    meds = tmp_path / "meds.txt"
    meds.write_text("二甲双胍\n阿司匹林\n", encoding="utf-8")
    query.main(["--medications", str(meds), "--claims", str(_claims(tmp_path)), "--out", str(tmp_path / "out")])
    text = (tmp_path / "out" / "report.md").read_text(encoding="utf-8")
    assert "- 二甲双胍：证据库里有 1 条说法。不能据此停。" in text
    assert "- 阿司匹林：证据库里没有收录。不能据此停。" in text


def test_every_real_claim_row_is_well_formed():
    rows = query.load_claims()
    for row in rows:
        assert row["id"].startswith(row["source"]["skill"] + ":")
        assert row["claim_zh"] and row["species"]


def test_human_studies_are_ordered_by_design_strength():
    import query
    rows = [
        {"entity": "X", "entity_type": "compound", "claim_zh": "横断面研究里和 X 相关。", "species": ["human"], "evidence": "cross_sectional", "source": {"skill": "s", "doi": ""}},
        {"entity": "X", "entity_type": "compound", "claim_zh": "随机试验里 X 降低了指标。", "species": ["human"], "evidence": "rct", "source": {"skill": "s", "doi": ""}},
        {"entity": "X", "entity_type": "compound", "claim_zh": "队列研究里 X 和结局相关。", "species": ["human"], "evidence": "cohort", "source": {"skill": "s", "doi": ""}},
    ]
    text = query.render(["X"], {"X": rows}, [], {}, 3, 1)
    assert text.index("随机试验里") < text.index("队列研究里") < text.index("横断面研究里")
    assert "随机对照试验 1，队列研究 1，横断面研究 1；按证据强度排列" in text
