"""Evidence lookup as JSON. Matching, grouping and wording come from the evidence skill's own query.py."""

from __future__ import annotations

import importlib.util
import re
import sys
from collections import OrderedDict
from typing import Any, Dict, List, Optional

from .library import Library, LKError, no_bytecode

_MODULES: Dict[str, Any] = {}


def _query_module(lib: Library):
    key = str(lib.root)
    if key not in _MODULES:
        path = lib.root / "skills" / "longevity-evidence" / "scripts" / "query.py"
        if not path.is_file():
            raise LKError("the evidence store (skills/longevity-evidence) is missing from this library", "library_broken")
        # query.py does `import skillkit` from its own directory.
        scripts = str(path.parent)
        added = scripts not in sys.path
        if added:
            sys.path.insert(0, scripts)
        try:
            spec = importlib.util.spec_from_file_location(f"longevity_evidence_query_{len(_MODULES)}", path)
            module = importlib.util.module_from_spec(spec)
            with no_bytecode():
                spec.loader.exec_module(module)
        finally:
            if added:
                sys.path.remove(scripts)
        _MODULES[key] = module
    return _MODULES[key]


def _paper(lib: Library, q, skill: str, source: Dict[str, Any]) -> Dict[str, Any]:
    paper: Dict[str, Any] = {}
    if skill and skill in lib.skills:
        paper = lib.skills[skill].get("paper") or {}
    if not paper:
        paper = {"title": source.get("title", ""), "journal": source.get("journal", ""), "year": source.get("year", "")}
    return {k: paper[k] for k in ("title_zh", "title", "journal", "year") if paper.get(k)}


def _row(lib: Library, q, row: Dict[str, Any]) -> Dict[str, Any]:
    source = row.get("source", {})
    out = {
        "entity": row.get("entity"),
        "type_zh": q.TYPE_ZH.get(row.get("entity_type", "other"), "其他"),
        "claim_zh": row.get("claim_zh"),
        "direction": row.get("direction"),
        "design": row.get("evidence"),
        "design_zh": q.DESIGN_ZH.get(row.get("evidence", ""), ""),
        "species": row.get("species", []),
        "doi": source.get("doi"),
        "locator": source.get("locator"),
        "paper": _paper(lib, q, source.get("skill", ""), source),
    }
    if row.get("entity_zh"):
        out["entity_zh"] = row["entity_zh"]
    if row.get("context_zh"):
        out["context_zh"] = row["context_zh"]
    if row.get("kind") == "list_member":
        out["list_member"] = True
    return out


def _effect(q, row: Dict[str, Any]) -> Dict[str, Any]:
    eff = row.get("effect", {})
    return {
        "id": row.get("id"), "intervention_zh": row.get("intervention_zh") or row.get("intervention"),
        "marker_zh": row.get("marker_zh") or row.get("marker"), "effect": eff,
        "duration_weeks": row.get("duration_weeks"), "population": row.get("population"),
        "design": row.get("design"), "design_zh": q.DESIGN_ZH.get(row.get("design", ""), row.get("design", "")),
        "doi": row.get("doi"),
        "checked_zh": "已人工核对" if row.get("verified_by") == "person" else "数字已对照原文引文，尚未人工复核",
    }


def query(lib: Library, entities: List[str], limit: int = 12, medications: Optional[List[str]] = None) -> Dict[str, Any]:
    for group in (entities or [], medications or []):
        if not isinstance(group, list) or not all(isinstance(x, str) for x in group):
            raise LKError("entities and medications must be lists of names", "bad_input", 3)
    entities = [e.strip() for e in entities or [] if e and e.strip()]
    medications = [m.strip() for m in medications or [] if m and m.strip()]
    if not entities and not medications:
        raise LKError("give at least one entity (a drug, supplement, diet, gene or protein name)", "bad_input", 3)
    limit = max(1, min(int(limit), 100))
    q = _query_module(lib)
    claims = q.load_claims(lib.root / "skills" / "longevity-evidence" / "data" / "claims.jsonl")
    trials = q.load_claims(lib.root / "data" / "effects.jsonl")
    results = []
    for name in entities:
        rows = q.search(claims, name)
        groups: Dict[str, List[Dict[str, Any]]] = OrderedDict((k, []) for k in q.BUCKETS)
        for row in rows:
            groups[q.bucket(row)].append(row)
        groups["human"].sort(key=lambda r: q.DESIGN_RANK.get(r.get("evidence", ""), 9))
        for items in groups.values():
            items.sort(key=lambda r: r.get("kind") == "list_member")
        entry: Dict[str, Any] = {"query": name, "matched": len(rows),
                                 "counts": {k: len(v) for k, v in groups.items()}}
        for key, label in q.BUCKETS.items():
            if groups[key]:
                entry[key] = {"label_zh": label, "rows": [_row(lib, q, r) for r in groups[key][:limit]],
                              "not_shown": max(0, len(groups[key]) - limit)}
        effects = q.search_effects(trials, name)
        if effects:
            entry["trial_effects"] = [_effect(q, r) for r in effects]
            entry["trial_effects_note_zh"] = "平均效应是一组人的平均，不是这个人会得到的变化，也不是用法。"
        # A specific form (维生素D3, vitamin K2, omega-3) with no human row: also show rows under the broader name,
        # labelled as such, so a cohort on "vitamin D supplementation" is not missed for "vitamin D3".
        stem = re.sub(r"(?<=[A-Za-z])[-\s]?\d$", "", name.strip())  # D3, K2, omega-3; never B12
        if not groups["human"] and stem != name.strip() and len(stem) >= 2:
            seen = {id(r) for r in rows}
            broader = [r for r in q.search(claims, stem) if id(r) not in seen and q.bucket(r) == "human"]
            if broader:
                entry["broader_name"] = {
                    "query": stem, "label_zh": f"名称更宽的人群研究（按「{stem}」检索，不专指{name}）",
                    "rows": [_row(lib, q, r) for r in broader[:limit]], "not_shown": max(0, len(broader) - limit)}
        if not rows and not effects:
            entry["note_zh"] = f"证据库里没有「{name}」。没有收录不等于没有研究，也不说明它安全或无效。"
        elif rows and not groups["human"]:
            entry["note_zh"] = "收录的论文里没有关于它的人群研究，只有动物、细胞或数据库里的说法；不能当成人的效果或剂量。"
        results.append(entry)
    out: Dict[str, Any] = {"schema": "longevity-evidence/1", "results": results,
                           "store": {"claims": len(claims), "trial_effects": len(trials),
                                     "papers": len({r.get('source', {}).get('doi') for r in claims})},
                           "boundary_zh": q.BOUNDARY, **lib.stamp()}
    if medications:
        out["medications"] = [{"name": m, "claims": len(q.search(claims, m)),
                               "note_zh": "证据库里的说法不能作为停药或换药的理由。"} for m in medications]
    return out
