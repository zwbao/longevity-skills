"""Dispatch consistency with the coach and analyst repositories (WS-G.3).

The coach's standalone host doc names everyday methods (常用方法) and the
analyst names skills it runs outside its tier rule (module-level *_SKILLS
whitelists in lalib/methods.py). Every name must be a skill in this library,
and a tier A skill that is still a draft must carry 仍在验证 on the coach line
that mentions it.

The repositories are found through LONGEVITY_COACH_DIR / LONGEVITY_ANALYST_DIR,
else as sibling checkouts of this one. A repository that is not there is
skipped, so the check is optional in CI.
"""

from __future__ import annotations

import ast
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .common import ROOT

COACH_DOC = Path("skills/longevity-coach/hosts/standalone.md")
ANALYST_METHODS = Path("skills/longevity-analyst/scripts/lalib/methods.py")
COMMON_METHODS = "常用方法"
STILL_CHECKING = "仍在验证"
_NAME = re.compile(r"`([a-z0-9][a-z0-9-]*[a-z0-9])`")


def repo(env: str, sibling: str) -> Optional[Path]:
    """The checkout named by env, else ../<sibling>; None when absent."""
    value = os.environ.get(env)
    path = Path(value) if value else ROOT.parent / sibling
    return path if path.is_dir() else None


def coach_lines(text: str) -> List[Tuple[int, str]]:
    return [(number, line) for number, line in enumerate(text.splitlines(), 1) if line.strip()]


def whitelists(source: str) -> Dict[str, List[str]]:
    """Module-level NAME_SKILLS = {...} / [...] / (...) / frozenset({...}) of string literals."""
    found: Dict[str, List[str]] = {}
    for node in ast.parse(source).body:
        targets = node.targets if isinstance(node, ast.Assign) else [node.target] if isinstance(node, ast.AnnAssign) else []
        value = getattr(node, "value", None)
        for target in targets:
            if not (isinstance(target, ast.Name) and target.id.endswith("_SKILLS")) or value is None:
                continue
            if isinstance(value, ast.Call) and getattr(value.func, "id", "") in {"frozenset", "set", "tuple", "list"} and value.args:
                value = value.args[0]
            if isinstance(value, (ast.Set, ast.List, ast.Tuple)):
                found[target.id] = [item.value for item in value.elts if isinstance(item, ast.Constant) and isinstance(item.value, str)]
    return found


def check_coach(doc: Path, manifests: Dict[str, Dict[str, Any]]) -> List[str]:
    errors: List[str] = []
    where = f"{doc.name}"
    for number, line in coach_lines(doc.read_text(encoding="utf-8")):
        names = _NAME.findall(line)
        if COMMON_METHODS in line:
            for name in names:
                if name not in manifests:
                    errors.append(f"{where}:{number}: 常用方法 names {name!r}, which is not in catalog.json")
        for name in names:
            data = manifests.get(name)
            if data and data["tier"] == "A" and (data.get("validation") or {}).get("status") == "draft" and STILL_CHECKING not in line:
                errors.append(f"{where}:{number}: {name} is a tier A draft; the line that mentions it must say {STILL_CHECKING}")
    return errors


def check_analyst(methods: Path, manifests: Dict[str, Dict[str, Any]]) -> List[str]:
    errors: List[str] = []
    for list_name, names in whitelists(methods.read_text(encoding="utf-8")).items():
        for name in names:
            if name not in manifests:
                errors.append(f"{methods.name}: {list_name} names {name!r}, which is not in catalog.json")
    return errors


def check(manifests: Dict[str, Dict[str, Any]]) -> Tuple[List[str], List[str]]:
    """(errors, notes). Notes say which repositories were skipped."""
    errors: List[str] = []
    notes: List[str] = []
    coach = repo("LONGEVITY_COACH_DIR", "longevity-coach-skill")
    if coach and (coach / COACH_DOC).exists():
        errors += check_coach(coach / COACH_DOC, manifests)
    else:
        notes.append("coach repository not found (set LONGEVITY_COACH_DIR); skipped")
    analyst = repo("LONGEVITY_ANALYST_DIR", "longevity-analyst-skill")
    if analyst and (analyst / ANALYST_METHODS).exists():
        errors += check_analyst(analyst / ANALYST_METHODS, manifests)
    else:
        notes.append("analyst repository not found (set LONGEVITY_ANALYST_DIR); skipped")
    return errors, notes
