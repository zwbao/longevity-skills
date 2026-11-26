"""Topic and evidence-level labels, the coverage reference list, and the coverage table.

schema/taxonomy.json holds the controlled values. Claims, effects and skills carry
`topic`; claims also carry `evidence_level`. An agent assigns both row by row (the
weekly pipeline's extraction prompt and its `label` command); this module only
checks the values and counts.

coverage/reference.jsonl lists what a complete library should hold, per topic and
layer, with the DOI of each item. `python3 -m tools.lsk coverage` writes
coverage.json and docs/coverage.md: per cell, how many rows the library has and
how many reference items it covers, plus the items still missing.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from . import jsonschema_lite
from .common import EVIDENCE, REGISTRY, ROOT, SCHEMA, read_json, read_jsonl, write_json
from .doi import normalize_doi

TAXONOMY = SCHEMA / "taxonomy.json"
REFERENCE = ROOT / "coverage" / "reference.jsonl"
EFFECTS = ROOT / "data" / "effects.jsonl"
COVERAGE_JSON = ROOT / "coverage.json"
COVERAGE_MD = ROOT / "docs" / "coverage.md"
LAYERS = ("method", "population", "reference_data", "mechanism")


def taxonomy() -> Dict[str, Any]:
    return read_json(TAXONOMY)


def topic_ids() -> List[str]:
    return [item["id"] for item in taxonomy()["topics"]]


def level_ids() -> List[str]:
    return [item["id"] for item in taxonomy()["evidence_levels"]]


def human_levels() -> Set[str]:
    return {item["id"] for item in taxonomy()["evidence_levels"] if item["human"]}


def check_topic(value: Any, where: str, topics: Set[str]) -> List[str]:
    if value is None:
        return []
    if not isinstance(value, list) or not value:
        return [f"{where}: topic must be a non-empty list"]
    return [f"{where}: topic {item!r} is not in schema/taxonomy.json" for item in value if item not in topics]


def check_labels(rows: Iterable[Dict[str, Any]], label: str, with_level: bool) -> List[str]:
    """Invalid values only. A missing label is counted by label_share(), not reported as an error,
    because rows arrive from several branches and the pipeline labels them after the fact."""
    topics, levels = set(topic_ids()), set(level_ids())
    errors: List[str] = []
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            continue
        where = f"{label}:{index}"
        errors += check_topic(row.get("topic"), where, topics)
        if with_level and row.get("evidence_level") is not None and row["evidence_level"] not in levels:
            errors.append(f"{where}: evidence_level {row['evidence_level']!r} is not in schema/taxonomy.json")
    return errors


def label_share() -> str:
    claims, effects = read_jsonl(EVIDENCE), read_jsonl(EFFECTS) if EFFECTS.exists() else []
    both = sum(1 for row in claims if row.get("topic") and row.get("evidence_level"))
    labelled_effects = sum(1 for row in effects if row.get("topic"))
    return (f"topic/evidence_level: {both} of {len(claims)} claims labelled, "
            f"{labelled_effects} of {len(effects)} effects have a topic")


def load_reference() -> List[Dict[str, Any]]:
    return read_jsonl(REFERENCE) if REFERENCE.exists() else []


def check_reference() -> List[str]:
    if not REFERENCE.exists():
        return []
    schema = read_json(SCHEMA / "coverage_reference.schema.json")
    topics = set(topic_ids())
    errors: List[str] = []
    seen: Dict[str, int] = {}
    for index, row in enumerate(load_reference(), start=1):
        where = f"coverage/reference.jsonl:{index}"
        errors += [f"{where}: {message}" for message in jsonschema_lite.validate(row, schema)]
        if not isinstance(row, dict):
            continue
        if row.get("topic") not in topics:
            errors.append(f"{where}: topic {row.get('topic')!r} is not in schema/taxonomy.json")
        if row.get("id") in seen:
            errors.append(f"{where}: duplicate id {row['id']} (also line {seen[row['id']]})")
        seen[row.get("id")] = index
        if not (row.get("doi") or row.get("skill") or row.get("file") or row.get("url")):
            errors.append(f"{where}: give a doi, a skill, a file or a url, so the item can be found")
        for path in row.get("file") or []:
            if ".." in path.split("/"):
                errors.append(f"{where}: file {path!r} must be a path inside the repository")
    return errors


def _layer_of_claim(row: Dict[str, Any], human: Set[str]) -> Optional[str]:
    level = row.get("evidence_level")
    if not level:
        return None
    if level in human and "human" in (row.get("species") or []):
        return "population"
    if level == "narrative":
        return "background"
    return "mechanism"


def _substantive(row: Dict[str, Any]) -> bool:
    """A row that says something about its entity: not a bare mention."""
    return row.get("direction") != "named"


def build(manifests: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    tax = taxonomy()
    topics = [item["id"] for item in tax["topics"]]
    human = human_levels()
    claims = read_jsonl(EVIDENCE)
    effects = read_jsonl(EFFECTS) if EFFECTS.exists() else []
    registry = {row["doi"]: row for row in read_jsonl(REGISTRY) if row.get("doi")}

    cells: Dict[Tuple[str, str], Dict[str, Any]] = {
        (topic, layer): {"rows": 0, "papers": set(), "skills": [], "effects": 0} for topic in topics for layer in LAYERS}
    background: Counter = Counter()
    unlabelled = {"claims": 0, "effects": 0, "skills": 0}

    # Which DOIs and skills each layer holds, for matching reference items.
    held: Dict[str, Set[str]] = {layer: set() for layer in LAYERS}
    skills_by_layer: Dict[str, Set[str]] = {layer: set() for layer in LAYERS}

    for name, data in manifests.items():
        doi = normalize_doi((data.get("paper") or data.get("tool") or {}).get("doi") or "")
        tier = data.get("tier")
        if tier in {"A", "tool"}:
            skills_by_layer["method"].add(name)
            skills_by_layer["mechanism"].add(name)
            skills_by_layer["reference_data"].add(name)
            if doi:
                held["method"].add(doi)
                held["mechanism"].add(doi)
                held["reference_data"].add(doi)
        elif tier == "B" and doi and "human" in (data.get("species") or []):
            held["population"].add(doi)
        if doi and tier in {"B", "C"}:
            held["mechanism"].add(doi)
        if tier not in {"A", "tool"}:
            continue
        if not data.get("topic"):
            unlabelled["skills"] += 1
            continue
        for topic in data["topic"]:
            if (topic, "method") in cells:
                cells[(topic, "method")]["skills"].append(name)
                if doi:
                    cells[(topic, "method")]["papers"].add(doi)

    for row in claims:
        layer = _layer_of_claim(row, human)
        doi = normalize_doi((row.get("source") or {}).get("doi") or "")
        if layer in LAYERS and doi and _substantive(row):
            held[layer].add(doi)
        if not row.get("topic") or layer is None:
            unlabelled["claims"] += 1
            continue
        if not _substantive(row):
            continue
        for topic in row["topic"]:
            if layer == "background":
                background[topic] += 1
                continue
            if (topic, layer) in cells:
                cells[(topic, layer)]["rows"] += 1
                if doi:
                    cells[(topic, layer)]["papers"].add(doi)

    for row in effects:
        doi = normalize_doi(row.get("doi") or "")
        if doi:
            held["population"].add(doi)
        if not row.get("topic"):
            unlabelled["effects"] += 1
            continue
        for topic in row["topic"]:
            if (topic, "population") in cells:
                cells[(topic, "population")]["effects"] += 1
                if doi:
                    cells[(topic, "population")]["papers"].add(doi)

    reference = load_reference()
    ref_by_cell: Dict[Tuple[str, str], List[Dict[str, Any]]] = defaultdict(list)
    for item in reference:
        layer = item["layer"]
        dois = {normalize_doi(value) for value in item.get("doi") or []}
        found = sorted(dois & held[layer])
        found_skills = sorted(set(item.get("skill") or []) & (skills_by_layer[layer] | (set(manifests) if layer == "population" else set())))
        found_files = sorted(path for path in item.get("file") or [] if (ROOT / path).exists())
        ref_by_cell[(item["topic"], layer)].append({
            "id": item["id"], "item": item["item"], "item_zh": item["item_zh"], "priority": item.get("priority", "P1"),
            "status": item["status"], "covered": bool(found or found_skills or found_files),
            "by": found + found_skills + found_files, "doi": sorted(dois),
        })

    table = []
    for topic in tax["topics"]:
        row = {"topic": topic["id"], "label_zh": topic["label_zh"], "background_rows": background[topic["id"]], "cells": {}}
        for layer in LAYERS:
            cell = cells[(topic["id"], layer)]
            items = ref_by_cell.get((topic["id"], layer), [])
            dates = [registry[doi].get("updated") for doi in cell["papers"] if doi in registry and registry[doi].get("updated")]
            row["cells"][layer] = {
                "rows": cell["rows"], "effects": cell["effects"], "papers": len(cell["papers"]), "skills": sorted(cell["skills"]),
                "latest": max(dates) if dates else None,
                "reference": len(items), "covered": sum(1 for item in items if item["covered"]),
                "missing": [item for item in items if not item["covered"]],
            }
        table.append(row)
    total_ref = len(reference)
    total_cov = sum(1 for cell in ref_by_cell.values() for item in cell if item["covered"])
    return {
        "schema": "longevity-coverage/1",
        "reference_items": total_ref, "reference_covered": total_cov,
        "unlabelled": unlabelled,
        "topics": table,
    }


def render_md(data: Dict[str, Any]) -> str:
    tax = taxonomy()
    layer_label = {item["id"]: item["label_zh"] for item in tax["layers"]}
    lines = [
        "# 覆盖度表",
        "",
        "由 `python3 -m tools.lsk coverage` 生成，请勿手改。行是主题，列是知识层。",
        "每格：库内条目数（方法为技能数；人群证据为人类研究证据条数，括号内为效应量）· 参照清单已覆盖 / 应有。",
        "只点名、没有结论的证据行不计入；叙述性综述与背景陈述单列。参照清单见 `coverage/reference.jsonl`，"
        "状态 draft 为 agent 起草、reviewed 为第二位 agent 复核、confirmed 为人工确认。",
        "",
        f"参照清单合计：已覆盖 {data['reference_covered']} / {data['reference_items']}。"
        f"尚未标注主题：证据 {data['unlabelled']['claims']} 条、效应量 {data['unlabelled']['effects']} 条、技能 {data['unlabelled']['skills']} 个。",
        "",
        "| 主题 | " + " | ".join(layer_label[layer] for layer in LAYERS) + " | 背景陈述 |",
        "| --- | " + " | ".join("---" for _ in LAYERS) + " | --- |",
    ]
    for row in data["topics"]:
        cells = []
        for layer in LAYERS:
            cell = row["cells"][layer]
            count = len(cell["skills"]) if layer == "method" else cell["rows"]
            text = f"{count}"
            if layer == "population" and cell["effects"]:
                text += f"（{cell['effects']}）"
            if cell["reference"]:
                text += f" · {cell['covered']}/{cell['reference']}"
            cells.append(text)
        lines.append(f"| {row['label_zh']} | " + " | ".join(cells) + f" | {row['background_rows']} |")
    lines += ["", "## 缺口", "", "参照清单里还没有进库的条目，按主题和层列出（P0 优先）。", ""]
    order = {"P0": 0, "P1": 1, "P2": 2}
    for row in data["topics"]:
        missing = [(layer, item) for layer in LAYERS for item in row["cells"][layer]["missing"]]
        if not missing:
            continue
        lines.append(f"### {row['label_zh']}")
        lines.append("")
        for layer, item in sorted(missing, key=lambda pair: (order.get(pair[1]["priority"], 1), LAYERS.index(pair[0]))):
            doi = f"（{', '.join(item['doi'])}）" if item["doi"] else ""
            lines.append(f"- {item['priority']} · {layer_label[layer]} · {item['item_zh']}{doi}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write(manifests: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    data = build(manifests)
    write_json(COVERAGE_JSON, data)
    COVERAGE_MD.parent.mkdir(parents=True, exist_ok=True)
    text = render_md(data)
    if not COVERAGE_MD.exists() or COVERAGE_MD.read_text(encoding="utf-8") != text:
        COVERAGE_MD.write_text(text, encoding="utf-8")
    return data


def missing_dois(manifests: Dict[str, Dict[str, Any]], priorities: Iterable[str] = ("P0", "P1", "P2")) -> List[str]:
    """DOIs of reference items not yet covered: the seed list for a targeted pipeline run."""
    wanted = set(priorities)
    out: List[str] = []
    for row in build(manifests)["topics"]:
        for layer in LAYERS:
            for item in row["cells"][layer]["missing"]:
                if item["priority"] in wanted:
                    out += [doi for doi in item["doi"] if doi not in out]
    return out
