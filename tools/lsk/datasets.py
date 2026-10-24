"""data/: shared reference tables the personal harness reads.

biological_variation.json  within-person variation per marker (reference change value)
readout_noise.json         technical-replicate noise of computed readouts (epigenetic clocks)
effects.jsonl              average intervention effects from trials and meta-analyses

Both hold medical constants, so every row names its source and says whether it
was checked against that source (verified). The checks here keep the shape
honest and confirm each number appears in the quoted source text; they cannot
tell whether the source itself is right.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List

from . import jsonschema_lite
from .common import ROOT, SCHEMA, read_json, read_jsonl

BIOVAR = ROOT / "data" / "biological_variation.json"
EFFECTS = ROOT / "data" / "effects.jsonl"
READOUT_NOISE = ROOT / "data" / "readout_noise.json"


def check_biovar() -> List[str]:
    if not BIOVAR.exists():
        return []
    schema = read_json(SCHEMA / "biological_variation.schema.json")
    data = read_json(BIOVAR)
    errors = [f"data/biological_variation.json{message}" for message in jsonschema_lite.validate(data, schema)]
    seen: Dict[str, int] = {}
    codes: Dict[str, str] = {}
    for index, row in enumerate(data.get("markers", []) if isinstance(data, dict) else []):
        if not isinstance(row, dict):
            continue
        key = row.get("key", "")
        if key in seen:
            errors.append(f"data/biological_variation.json: duplicate marker key {key}")
        seen[key] = index
        for code in row.get("loinc", []) + row.get("device_codes", []):
            if code in codes and codes[code] != key:
                errors.append(f"data/biological_variation.json: code {code} is on both {codes[code]} and {key}")
            codes[code] = key
        source = row.get("cvi_source", {}) if isinstance(row.get("cvi_source"), dict) else {}
        if "biologicalvariation.eu" in str(source.get("url", "")):
            errors.append(f"data/biological_variation.json: {key} cites the EFLM database, whose terms restrict redistribution; use a journal article")
        if row.get("verified"):
            if "doi" not in source:
                errors.append(f"data/biological_variation.json: {key} is verified but its CVI source has no DOI")
            if not source.get("quote"):
                errors.append(f"data/biological_variation.json: {key} is verified but its CVI source has no quote")
            else:
                missing = numbers_missing(source["quote"], [row.get("cvi_pct")] + list(row.get("cvi_ci_pct") or []))
                if missing:
                    errors.append(f"data/biological_variation.json: {key} quote does not contain {', '.join(str(item) for item in missing)}; copy the numbers exactly as printed")
        if "long_term_cvi_pct" in row:
            long_term = row.get("long_term_source") if isinstance(row.get("long_term_source"), dict) else {}
            if not long_term.get("doi") or not long_term.get("quote"):
                errors.append(f"data/biological_variation.json: {key} has long_term_cvi_pct but no long_term_source with a DOI and a quote")
            elif numbers_missing(long_term["quote"], [row["long_term_cvi_pct"]]):
                errors.append(f"data/biological_variation.json: {key} long_term_source quote does not contain {row['long_term_cvi_pct']}; copy the number exactly as printed")
            if "biologicalvariation.eu" in str(long_term.get("url", "")):
                errors.append(f"data/biological_variation.json: {key} long_term_source cites the EFLM database; use a journal article")
        elif "long_term_source" in row:
            errors.append(f"data/biological_variation.json: {key} has long_term_source but no long_term_cvi_pct")
    return errors


def check_readout_noise() -> List[str]:
    if not READOUT_NOISE.exists():
        return []
    where = "data/readout_noise.json"
    schema = read_json(SCHEMA / "readout_noise.schema.json")
    data = read_json(READOUT_NOISE)
    errors = [f"{where}{message}" for message in jsonschema_lite.validate(data, schema)]
    seen: Dict[str, str] = {}
    keys: List[str] = []
    for row in data.get("readouts", []) if isinstance(data, dict) else []:
        if not isinstance(row, dict):
            continue
        key = row.get("key", "")
        if key in keys:
            errors.append(f"{where}: duplicate readout key {key}")
        keys.append(key)
        for name in [key] + list(row.get("match") or []):
            if fold(name) in seen and seen[fold(name)] != key:
                errors.append(f"{where}: {name} names both {seen[fold(name)]} and {key}")
            seen[fold(name)] = key
        source = row.get("source", {}) if isinstance(row.get("source"), dict) else {}
        wanted = [row[name] for name in ("sd_abs", "icc") if isinstance(row.get(name), (int, float))]
        if not wanted:
            errors.append(f"{where}: {key} gives neither sd_abs nor icc")
        missing = numbers_missing(source.get("quote", ""), wanted)
        if missing:
            errors.append(f"{where}: {key} quote does not contain {', '.join(str(item) for item in missing)}; copy the numbers exactly as printed")
        quote = str(source.get("quote", ""))
        if "\u2026" in quote or "..." in quote:
            errors.append(f"{where}: {key} quote is cut with an ellipsis; copy one continuous span")
    return errors


def load_biovar() -> Dict[str, Any]:
    return read_json(BIOVAR) if BIOVAR.exists() else {"markers": []}


def check_effects() -> List[str]:
    if not EFFECTS.exists():
        return []
    schema = read_json(SCHEMA / "effect.schema.json")
    biovar = {row.get("key"): row for row in load_biovar().get("markers", [])}
    markers = set(biovar)
    errors: List[str] = []
    seen: Dict[str, int] = {}
    for index, row in enumerate(read_jsonl(EFFECTS), start=1):
        where = f"data/effects.jsonl:{index}"
        for message in jsonschema_lite.validate(row, schema):
            errors.append(f"{where}{message}")
        if not isinstance(row, dict):
            continue
        if row.get("id") in seen:
            errors.append(f"{where}: duplicate id {row.get('id')} (also line {seen[row['id']]})")
        seen[row.get("id")] = index
        key = row.get("marker_key")
        if key and BIOVAR.exists() and key not in markers:
            errors.append(f"{where}: marker_key {key} is not in data/biological_variation.json")
        ci = row.get("effect", {}).get("ci")
        value = row.get("effect", {}).get("value")
        if isinstance(ci, list) and len(ci) == 2 and isinstance(value, (int, float)) and not min(ci) <= value <= max(ci):
            errors.append(f"{where}: effect value {value} is outside its confidence interval {ci}")
        if row.get("verified") and row.get("verified_by") not in ("person", "quote_match"):
            errors.append(f"{where}: verified rows say who checked them (verified_by: person or quote_match)")
        missing = numbers_missing_from_quote(row)
        if missing:
            errors.append(f"{where}: the quote does not contain {', '.join(str(item) for item in missing)}; copy the numbers exactly as printed")
        quote = str(row.get("quote", ""))
        if "\u2026" in quote or "..." in quote:
            errors.append(f"{where}: the quote is cut with an ellipsis; copy one continuous span")
        names = marker_names(row, biovar.get(key) or {})
        if quote and not any(fold(item) in fold(quote) for item in names if item):
            errors.append(f"{where}: the quote never names the marker ({', '.join(item for item in names if item)}); quote the span that says which measure moved")
        if isinstance(value, (int, float)) and value < 0 and not sign_shown(quote, value):
            errors.append(f"{where}: effect {value} is negative but the quote shows neither a minus sign on it nor a word for a fall")
    return errors


_DASHES = str.maketrans({"\u2212": "-", "\u2013": "-", "\u2010": "-", "\u2011": "-", "\u00b7": "."})
_FALL = re.compile(r"reduc|decreas|lower|declin|fell|fall|drop|loss|less|slow|降低|下降|减少|减慢|减轻|改善", re.I)


def fold(text: str) -> str:
    return re.sub(r"\s+", " ", str(text).translate(_DASHES)).casefold()


def marker_names(row: Dict[str, Any], marker: Dict[str, Any]) -> List[str]:
    return [row.get("marker", ""), row.get("marker_zh", ""), marker.get("label_zh", ""), *marker.get("aliases", [])] + list(row.get("marker_terms") or [])


def sign_shown(quote: str, value: float) -> bool:
    text = fold(quote)
    digits = f"{abs(value):.10f}".rstrip("0").rstrip(".")
    if re.search(rf"-\s?{re.escape(digits)}(?:\.?0*)(?!\d)", text):
        return True
    return bool(_FALL.search(text))


_NUMBER = re.compile(r"\d+(?:\.\d+)?")


def numbers_missing(quote: str, wanted: List[Any]) -> List[float]:
    """Numbers (sign aside) that do not appear in a verbatim quote."""
    text = str(quote).replace("\u00b7", ".").replace("\u2212", "-")
    have = {float(item) for item in _NUMBER.findall(text)}
    return [abs(item) for item in wanted if isinstance(item, (int, float)) and not any(abs(abs(item) - seen) < 1e-9 for seen in have)]


def numbers_missing_from_quote(row: Dict[str, Any]) -> List[float]:
    """Effect value and interval bounds (sign aside) that do not appear in the verbatim quote."""
    effect = row.get("effect") or {}
    return numbers_missing(row.get("quote", ""), [effect.get("value")] + list(effect.get("ci") or []))
