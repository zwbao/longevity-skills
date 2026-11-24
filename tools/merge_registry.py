"""Three-way merge for registry/papers.jsonl, keyed by DOI.

Two pipeline branches of the same week (evidence and index) both add rows to
the registry, and a line merge reports a conflict wherever their rows are
neighbours. Rows are independent, so merge them per DOI:

- a row only one side added or changed: take that side;
- a row both sides changed differently: take the later `updated`; on a tie the
  higher tier (A > B > C > tool > pending > rejected), so a paper that one
  branch turned into evidence is not set back to pending by the other;
- a row one side deleted and the other left alone: delete it.

Used as a git merge driver:
    git config merge.registry.driver "python3 tools/merge_registry.py %O %A %B"
with `registry/papers.jsonl merge=registry` in .gitattributes. Writes the
result to the second path and exits 0.
"""

from __future__ import annotations

import json
import sys
from typing import Dict

RANK = {"A": 5, "B": 4, "C": 3, "tool": 2, "pending": 1, "rejected": 0}


def load(path: str) -> Dict[str, dict]:
    rows: Dict[str, dict] = {}
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                row = json.loads(line)
                rows[row["doi"]] = row
    return rows


def pick(ours: dict, theirs: dict) -> dict:
    left = (str(ours.get("updated") or ""), RANK.get(ours.get("tier"), -1))
    right = (str(theirs.get("updated") or ""), RANK.get(theirs.get("tier"), -1))
    return theirs if right > left else ours


def merge(base: Dict[str, dict], ours: Dict[str, dict], theirs: Dict[str, dict]) -> Dict[str, dict]:
    merged: Dict[str, dict] = {}
    for doi in set(base) | set(ours) | set(theirs):
        b, o, t = base.get(doi), ours.get(doi), theirs.get(doi)
        if o == t:
            row = o
        elif o == b:
            row = t
        elif t == b:
            row = o
        elif o is None or t is None:  # one side deleted, the other changed: keep the change
            row = o or t
        else:
            row = pick(o, t)
        if row is not None:
            merged[doi] = row
    return merged


def main(argv: list) -> int:
    base_path, ours_path, theirs_path = argv[1:4]
    merged = merge(load(base_path), load(ours_path), load(theirs_path))
    with open(ours_path, "w", encoding="utf-8") as handle:
        for doi in sorted(merged):
            handle.write(json.dumps(merged[doi], ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
