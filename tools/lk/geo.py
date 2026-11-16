"""Read the sample annotations of a GEO series (the part above the data table), from two public formats.

`parse_series_matrix_header` reads the header of a GEO `*_series_matrix.txt` file; `parse_sdrf` reads the
`E-GEOD-<n>.sdrf.txt` file of the EBI BioStudies mirror. Both give  {sample id: {"title", "source", "fields"}}.

Which annotation holds chronological age, and which one names the individual a sample came from, is a judgement
about each study. `field_summary` lists every annotation with examples so the caller can decide; `ages_from` and
`subjects_from` take the caller's choice, and only guess (flagged `guessed`) when none is given.

Standard library only.
"""

from __future__ import annotations

import csv
import io
import re
from typing import Any, Dict, List, Optional, Tuple

Samples = Dict[str, Dict[str, Any]]
_GSM = re.compile(r"GSM\d+")


def _unquote(cell: str) -> str:
    cell = cell.strip()
    return cell[1:-1] if len(cell) >= 2 and cell[0] == '"' and cell[-1] == '"' else cell


def parse_series_matrix_header(text: str) -> Samples:
    ids: List[str] = []
    rows: List[Tuple[str, List[str]]] = []
    for line in text.splitlines():
        if line.startswith("!series_matrix_table_begin"):
            break
        if not line.startswith("!Sample_"):
            continue
        cells = line.split("\t")
        key, vals = cells[0][len("!Sample_"):], [_unquote(c) for c in cells[1:]]
        if key == "geo_accession":
            ids = vals
        rows.append((key, vals))
    samples: Samples = {s: {"title": "", "source": "", "fields": {}} for s in ids}
    for key, vals in rows:
        for s, v in zip(ids, vals):
            if not v:
                continue
            if key == "title":
                samples[s]["title"] = v
            elif key.startswith("source_name"):
                samples[s]["source"] = v
            elif key.startswith("characteristics"):
                name, sep, value = v.partition(":")
                if sep and value.strip():
                    samples[s]["fields"].setdefault(name.strip().lower(), value.strip())
            elif key == "description":
                samples[s]["fields"].setdefault("description", v)
    return samples


def parse_sdrf(text: str) -> Samples:
    reader = csv.reader(io.StringIO(text), delimiter="\t")
    header = next(reader, [])
    samples: Samples = {}
    for row in reader:
        gsm = next((m.group(0) for cell in row for m in [_GSM.search(cell)] if m), None)
        if not gsm or gsm in samples:
            continue
        entry: Dict[str, Any] = {"title": "", "source": "", "fields": {}}
        for name, value in zip(header, row):
            value = value.strip()
            if not value:
                continue
            m = re.match(r"\s*(Characteristics|FactorValue|Factor Value)\s*\[(.+?)\]\s*$", name, re.I)
            if m:
                entry["fields"].setdefault(m.group(2).strip().lower(), value)
            elif re.match(r"\s*Comment\s*\[\s*Sample_title\s*\]", name, re.I):
                entry["title"] = value
            elif re.match(r"\s*Comment\s*\[\s*Sample_source_name\s*\]", name, re.I):
                entry["source"] = value
            elif re.match(r"\s*Comment\s*\[\s*Sample_description\s*\]", name, re.I):
                entry["fields"].setdefault("description", value)
        samples[gsm] = entry
    return samples


def field_summary(samples: Samples) -> List[Dict[str, Any]]:
    """Every annotation, how many samples carry it, how many different values, and a few examples."""
    seen: Dict[str, List[str]] = {}
    for entry in samples.values():
        for name, value in entry["fields"].items():
            seen.setdefault(name, []).append(value)
    out = []
    for name, values in seen.items():
        distinct = list(dict.fromkeys(values))
        out.append({"field": name, "samples": len(values), "distinct": len(distinct), "examples": distinct[:5],
                    "numeric_share": round(sum(_years(v, name) is not None for v in values) / len(values), 2)})
    return sorted(out, key=lambda r: -r["samples"])


_AGE_UNIT = {"y": 1.0, "yr": 1.0, "yrs": 1.0, "year": 1.0, "years": 1.0, "yo": 1.0,
             "mo": 1 / 12, "month": 1 / 12, "months": 1 / 12, "wk": 1 / 52.18, "wks": 1 / 52.18, "week": 1 / 52.18,
             "weeks": 1 / 52.18, "d": 1 / 365.25, "day": 1 / 365.25, "days": 1 / 365.25}


def _years(value: str, field: str = "") -> Optional[float]:
    m = re.match(r"^\s*(\d+(?:\.\d+)?)\s*([A-Za-z]+)?\.?\s*(?:old)?\s*$", value)
    if not m:
        return None
    unit = (m.group(2) or "").lower()
    if unit and unit not in _AGE_UNIT:
        return None
    if not unit:
        unit = next((u for u in ("month", "week", "day") if u in field.lower()), "year")
    years = float(m.group(1)) * _AGE_UNIT[unit]
    return years if 0 <= years <= 125 else None


_NOT_CHRONOLOGICAL = re.compile(r"gestation|onset|diagnos|death|menopause|menarche|accel|dnam|epigen|predict|estimat|"
                                r"group|categor|range|bin|decade|tertile|quartile|at (?:first|last)|smok|mother|father|"
                                r"maternal|paternal|parent|passage|culture|storage|post[- ]?mortem|pmi", re.I)


def ages_from(samples: Samples, field: Optional[str] = None) -> Dict[str, Any]:
    """{field, ages: {sample: years}, guessed}. With no field given, the best 'age' annotation is guessed."""
    guessed = field is None
    if field is None:
        best: Tuple[float, int, str] = (0.0, 0, "")
        for row in field_summary(samples):
            name = row["field"]
            if not re.search(r"(?<![a-z])age(?![a-z])", name) or _NOT_CHRONOLOGICAL.search(name):
                continue
            score = (row["numeric_share"] * row["samples"], -len(name), name)
            if score[0] > best[0] or (score[0] == best[0] and score[1] > best[1]):
                best = score  # type: ignore[assignment]
        field = best[2] or None
    ages: Dict[str, float] = {}
    if field:
        for s, entry in samples.items():
            y = _years(entry["fields"].get(field.lower(), ""), field)
            if y is not None:
                ages[s] = y
    return {"field": field, "ages": ages, "guessed": guessed}


_SUBJECT = re.compile(r"^(?:subject|individual|patient|donor|participant|person)(?:[ _-]?(?:id|no|number|code|identifier))?$", re.I)


def subjects_from(samples: Samples, field: Optional[str] = None) -> Dict[str, Any]:
    """{field, subjects: {sample: individual}, guessed}. Guessed only from an annotation that names the individual
    and repeats across samples; twin or family identifiers are never taken as the same individual."""
    guessed = field is None
    if field is None:
        for row in field_summary(samples):
            if _SUBJECT.match(row["field"]) and 1 < row["distinct"] < row["samples"]:
                field = row["field"]
                break
    subjects = {s: e["fields"][field.lower()] for s, e in samples.items() if field and e["fields"].get(field.lower())} if field else {}
    return {"field": field, "subjects": subjects, "guessed": guessed}
