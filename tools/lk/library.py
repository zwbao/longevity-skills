"""Find the library on disk and read its files."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ENV = "LONGEVITY_SKILLS_HOME"
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,99}$")


class LKError(Exception):
    """An error the caller can act on. `code` is stable; the message is for people."""

    def __init__(self, message: str, code: str = "error", exit_code: int = 1) -> None:
        super().__init__(message)
        self.code = code
        self.exit_code = exit_code


def is_library(path: Path) -> bool:
    return (path / "catalog.json").is_file() and (path / "intents.json").is_file() and (path / "skills").is_dir()


def locate(given: Optional[str] = None) -> Path:
    """--library, else $LONGEVITY_SKILLS_HOME, else the copy installed with the package, else the checkout around it."""
    if given:
        path = Path(given).expanduser()
        if not is_library(path):
            raise LKError(f"--library {given} is not a longevity-skills library (needs catalog.json, intents.json, skills/)",
                          "library_not_found", 2)
        return path.resolve()
    if os.environ.get(ENV):
        path = Path(os.environ[ENV]).expanduser()
        if not is_library(path):
            raise LKError(f"${ENV}={os.environ[ENV]} is not a longevity-skills library", "library_not_found", 2)
        return path.resolve()
    here = Path(__file__).resolve().parent
    for path in [here / "library", *list(here.parents)[:3]]:
        if is_library(path):
            return path.resolve()
    raise LKError("longevity-skills library not found: pass --library <path> or set $" + ENV, "library_not_found", 2)


class Library:
    def __init__(self, root: Path) -> None:
        self.root = root
        self._catalog: Optional[Dict[str, Any]] = None
        self._intents: Optional[Dict[str, Any]] = None
        self._by_name: Optional[Dict[str, Dict[str, Any]]] = None
        self._manifests: Dict[str, Dict[str, Any]] = {}
        self._skillkit = None
        self._commit: Optional[str] = None

    # --- files ---
    def read_json(self, relative: str) -> Any:
        return json.loads((self.root / relative).read_text(encoding="utf-8"))

    @property
    def catalog(self) -> Dict[str, Any]:
        if self._catalog is None:
            self._catalog = self.read_json("catalog.json")
        return self._catalog

    @property
    def intents(self) -> List[Dict[str, Any]]:
        if self._intents is None:
            self._intents = self.read_json("intents.json")
        return self._intents["intents"]

    @property
    def skills(self) -> Dict[str, Dict[str, Any]]:
        if self._by_name is None:
            self._by_name = {s["name"]: s for s in self.catalog["skills"]}
        return self._by_name

    def skill(self, name: str) -> Dict[str, Any]:
        if not isinstance(name, str) or not NAME_RE.match(name):
            raise LKError(f"not a method name: {name!r}", "unknown_method", 2)
        if name not in self.skills:
            close = [n for n in self.skills if name in n or n in name][:5]
            hint = f"; did you mean {', '.join(close)}" if close else "; list them with `longevity methods`"
            raise LKError(f"no method named {name!r}{hint}", "unknown_method", 2)
        return self.skills[name]

    def manifest(self, name: str) -> Dict[str, Any]:
        self.skill(name)
        if name not in self._manifests:
            self._manifests[name] = self.read_json(f"skills/{name}/skill.json")
        return self._manifests[name]

    def skill_dir(self, name: str) -> Path:
        self.skill(name)
        return self.root / "skills" / name

    # --- versions ---
    @property
    def release(self) -> str:
        path = self.root / "VERSION"
        if path.is_file():
            return path.read_text(encoding="utf-8").strip()
        return str(self.catalog.get("version", "unknown"))

    @property
    def commit(self) -> Optional[str]:
        if self._commit is None:
            self._commit = ""
            if (self.root / ".git").exists():
                try:
                    done = subprocess.run(["git", "-C", str(self.root), "rev-parse", "--short", "HEAD"],
                                          capture_output=True, text=True, timeout=3)
                    if done.returncode == 0:
                        self._commit = done.stdout.strip()
                except (OSError, subprocess.SubprocessError):
                    pass
        return self._commit or None

    def stamp(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {"release": self.release}
        if self.commit:
            out["commit"] = self.commit
        return out

    # --- shared helpers ---
    @property
    def skillkit(self):
        """The canonical tools/skillkit/skillkit.py of this library (name matching and unit folding)."""
        if self._skillkit is None:
            import importlib.util

            path = self.root / "tools" / "skillkit" / "skillkit.py"
            spec = importlib.util.spec_from_file_location("longevity_skillkit", path)
            if spec is None or spec.loader is None:
                raise LKError(f"cannot load {path}", "library_broken")
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module  # dataclasses look the module up by name
            spec.loader.exec_module(module)
            self._skillkit = module
        return self._skillkit


def open_library(given: Optional[str] = None) -> Library:
    return Library(locate(given))
