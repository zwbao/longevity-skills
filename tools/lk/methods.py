"""Find, list and describe methods: read-only views of catalog.json, intents.json and skill.json."""

from __future__ import annotations

import re
import unicodedata
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .library import Library, LKError

VALIDATION_ZH = {
    "reproduced": "已复现论文",
    "reproduced_secondary": "已与独立实现核对",
    "draft": "仍在验证",
}
EVIDENCE_INTENTS = {"intervention_evidence", "gene_variant"}
PROFILE_WORDS = {
    "age": {"age", "年龄", "实足年龄", "岁数"},
    "sex": {"sex", "gender", "性别"},
}


def status_of(s: Dict[str, Any]) -> Tuple[str, str]:
    """(status, why_zh). status: runnable | draft | lookup | tool | not_runnable."""
    tier = s.get("tier")
    if not s.get("has_script") or not s.get("entry"):
        return "not_runnable", "没有可运行的脚本"
    if tier == "C":
        return "not_runnable", "C 类只收录（动物、细胞或队列统计量），不用来回答个人问题"
    if tier == "A" and s.get("validation_status") == "draft":
        # Drafts may take a whole file (methylation betas) whose columns skill.json does not declare;
        # the script checks that file itself. Either way they run only with allow_draft.
        return "draft", "仍在验证：默认不运行，加 --allow-draft 才运行"
    if s.get("inputs_status") != "verified":
        return "not_runnable", "输入没有在 skill.json 里声明完整，不能自动运行"
    if tier == "A":
        return "runnable", ""
    if tier == "B":
        return "lookup", "B 类查表：把这个人的值放到论文报告的数旁边，不是对这个人运行论文模型"
    return "tool", "工具：包装已发布的程序或数据库"


def label_of(s: Dict[str, Any]) -> str:
    tier = s.get("tier")
    if tier == "A":
        v = s.get("validation_status") or "draft"
        return f"已发表模型（{VALIDATION_ZH.get(v, v)}）"
    if tier == "B":
        return "论文查表（不是对这个人运行论文模型）"
    if tier == "C":
        return "只收录"
    return "工具"


def paper_of(s: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    p = s.get("paper") or {}
    if not p:
        return None
    return {k: p[k] for k in ("doi", "title", "title_zh", "journal", "year", "article_url") if p.get(k)}


def summary(s: Dict[str, Any]) -> Dict[str, Any]:
    status, why = status_of(s)
    out = {"name": s["name"], "tier": s.get("tier"), "status": status, "label_zh": label_of(s),
           "blurb_zh": s.get("blurb_zh", "")}
    if why:
        out["why_zh"] = why
    return out


def _requirements(s: Dict[str, Any]) -> Dict[str, Any]:
    inputs = s.get("inputs") or []
    meas = [i for i in inputs if i.get("from", "measurements") == "measurements"]
    req = [f"{i.get('label_zh', i['key'])}" + (f"（{i['unit']}）" if i.get("unit") not in (None, "", "1") else "")
           for i in meas if i.get("required")]
    profile = [i["key"] for i in inputs if i.get("from") == "profile" and i.get("required")]
    args = [i.get("label_zh", i["key"]) for i in inputs if i.get("from") == "argument" and i.get("required")]
    out: Dict[str, Any] = {"required_measurements": req, "optional_measurements": sum(1 for i in meas if not i.get("required"))}
    if profile:
        out["profile"] = profile
    if args:
        out["required_answers"] = args
    if not inputs:
        out["note_zh"] = "输入是整份文件（例如甲基化 beta 值表），用 measurements_file 传入"
    return out


def _fold(text: str) -> str:
    return unicodedata.normalize("NFKC", str(text)).casefold()


def _trigger_hits(text: str, triggers: Sequence[str]) -> int:
    t = _fold(text)
    hits = 0
    for trig in triggers:
        if trig.startswith("re:"):
            try:
                if re.search(trig[3:], t, re.IGNORECASE):
                    hits += 1
            except re.error:
                continue
        elif _fold(trig) and _fold(trig) in t:
            hits += 1
    return hits


def find(lib: Library, text: str, limit: int = 3) -> Dict[str, Any]:
    """Match the person's words to intents (substring triggers, `re:` regexes; ties go to the higher priority)."""
    scored = []
    for it in lib.intents:
        hits = _trigger_hits(text, it.get("triggers", []))
        if hits:
            scored.append((hits, it.get("priority", 0), it))
    scored.sort(key=lambda x: (-x[0], -x[1]))
    intents = []
    for hits, _, it in scored[:limit]:
        methods = []
        for name in it.get("skills", []):
            s = lib.skills.get(name)
            if s:
                methods.append(summary(s))
        entry = {"intent": it["id"], "label_zh": it.get("label_zh", ""), "hits": hits,
                 "data": it.get("data", []), "methods": methods}
        if it["id"] in EVIDENCE_INTENTS:
            entry["next_zh"] = "问某个药、补剂、饮食或基因有没有证据：用 evidence（MCP 里是 query_evidence），传对象的名字"
        intents.append(entry)
    out: Dict[str, Any] = {"query": text, "intents": intents, **lib.stamp()}
    if not intents:
        out["note_zh"] = "没有对上的意图。下面是全部可直接运行的方法；问证据用 evidence。"
        out["runnable"] = [summary(s) for s in lib.skills.values() if status_of(s)[0] == "runnable"]
    return out


def _have_index(lib: Library, s: Dict[str, Any]):
    kit = lib.skillkit
    meas = [i for i in (s.get("inputs") or []) if i.get("from", "measurements") == "measurements"]
    return kit, meas, kit.alias_index(meas)


def methods(lib: Library, intent: Optional[str] = None, have: Optional[List[str]] = None,
            include_lookups: bool = False) -> Dict[str, Any]:
    want = {"runnable", "draft"} | ({"lookup", "tool"} if include_lookups else set())
    names: List[str]
    if intent:
        match = [it for it in lib.intents if it["id"] == intent]
        if not match:
            raise LKError(f"no intent {intent!r}; ids: {', '.join(it['id'] for it in lib.intents)}", "unknown_intent", 2)
        names = [n for n in match[0].get("skills", []) if n in lib.skills]
    else:
        names = sorted(lib.skills)
    have = [h.strip() for h in (have or []) if h and h.strip()]
    rows = []
    for name in names:
        s = lib.skills[name]
        status, _ = status_of(s)
        if status not in want:
            continue
        row = {**summary(s), "intents": s.get("intents", []), **_requirements(s)}
        if have:
            row.update(_coverage(lib, s, have))
        rows.append(row)
    if have:
        rows.sort(key=lambda r: (len(r.get("missing", [])), r["status"] != "runnable", r["name"]))
    else:
        rows.sort(key=lambda r: (r["status"] != "runnable", r["tier"] != "A", r["name"]))
    out: Dict[str, Any] = {"methods": rows, "count": len(rows), **lib.stamp()}
    if not include_lookups:
        out["note_zh"] = "只列出 A 类（按论文印出的方法算这个人）。B 类查表和工具加 --all；问证据用 evidence。"
    return out


def _coverage(lib: Library, s: Dict[str, Any], have: List[str]) -> Dict[str, Any]:
    kit, meas, index = _have_index(lib, s)
    got = set()
    for item in have:
        for v in kit.name_variants(item):
            if v in index:
                got.add(index[v][0]["key"])
                break
    folded = {kit.fold_name(h) for h in have}
    missing = [i.get("label_zh", i["key"]) for i in meas if i.get("required") and i["key"] not in got]
    for key in [i["key"] for i in (s.get("inputs") or []) if i.get("from") == "profile" and i.get("required")]:
        if not ({kit.fold_name(w) for w in PROFILE_WORDS.get(key, {key})} & folded):
            missing.append({"age": "年龄", "sex": "性别"}.get(key, key))
    used = [i.get("label_zh", i["key"]) for i in meas if i["key"] in got]
    out = {"uses_from_have": used, "missing": missing, "complete": not missing}
    if not meas and not (s.get("inputs") or []):
        out["complete"] = False
        out["missing"] = ["整份输入文件"]
    return out


def describe(lib: Library, name: str) -> Dict[str, Any]:
    s = lib.skill(name)
    m = lib.manifest(name)
    status, why = status_of(s)
    entry = m.get("entry") or {}
    inputs = []
    for i in m.get("inputs") or []:
        row = {k: i[k] for k in ("key", "label_zh", "unit", "range", "required", "from", "note_zh", "unit_required") if k in i}
        if i.get("accept"):
            row["accept_units"] = sorted(i["accept"])
        if i.get("aliases"):
            row["aliases"] = i["aliases"][:8]
        if i.get("loinc"):
            row["loinc"] = i["loinc"]
        if i.get("from") == "argument":
            row["answer"] = "yes 或 no" if not i.get("unit") else row.get("unit", "")
        inputs.append(row)
    validation = m.get("validation") or {}
    v_out: Dict[str, Any] = {"status": validation.get("status"),
                             "label_zh": VALIDATION_ZH.get(validation.get("status", ""), "")}
    if validation.get("examples"):
        v_out["examples"] = [{k: ex.get(k) for k in ("locator", "values", "tolerance") if ex.get(k) is not None}
                             for ex in validation["examples"][:3]]
    if validation.get("gap_zh"):
        v_out["gap_zh"] = validation["gap_zh"]
    out: Dict[str, Any] = {
        "name": name, "tier": s.get("tier"), "status": status, "label_zh": label_of(s),
        "species": s.get("species"), "evidence": s.get("evidence"), "blurb_zh": s.get("blurb_zh", ""),
        "description": s.get("description", ""), "paper": paper_of(m), "validation": v_out,
        "inputs": inputs,
        "outputs": [{k: o[k] for k in ("key", "label_zh", "unit", "note_zh") if k in o} for o in m.get("outputs") or []],
        "takes": {k: bool(entry.get(f"{k}_flag")) for k in ("age", "sex", "medications", "targets")},
        **lib.stamp(),
    }
    if why:
        out["why_zh"] = why
    if status in ("runnable", "draft", "lookup", "tool"):
        out["run_example"] = _example(name, m)
    return out


def _example(name: str, m: Dict[str, Any]) -> str:
    entry = m.get("entry") or {}
    parts = ["longevity", "run", name]
    if entry.get("age_flag"):
        parts += ["--age", "<年龄>"]
    if entry.get("sex_flag"):
        parts += ["--sex", "<male|female>"]
    for i in (m.get("inputs") or []):
        if i.get("from", "measurements") == "measurements" and i.get("required"):
            unit = f" {i['unit']}" if i.get("unit") not in (None, "", "1") else ""
            parts += ["-m", f"'{i.get('label_zh', i['key'])}=<值>{unit}'"]
        elif i.get("from") == "argument" and i.get("required"):
            parts += ["--answer", f"{i['key']}=<yes|no>"]
    if not m.get("inputs"):
        parts += ["--measurements-file", "<文件>"]
    return " ".join(parts)
