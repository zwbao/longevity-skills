"""Prompt texts saved by the prompt hook, so tools can read the full data by a short id instead of the agent copying it.

Long pasted data (a 90,000-character methylation profile, 200 proteins for two people) is expensive for an agent to
copy into a tool call, and agents shorten it. The hook saves the prompt locally (never sent anywhere) under an id that
is the first 16 hex digits of its SHA-256; tools take panel_ref=<id>. Files older than two days are removed.
"""

from __future__ import annotations

import hashlib
import os
import re
import time
from pathlib import Path
from typing import Optional

from .library import LKError

KEEP_SECONDS = 2 * 24 * 3600


def _dir() -> Path:
    base = os.environ.get("LONGEVITY_CACHE") or os.path.join(os.path.expanduser("~"), ".cache", "longevity")
    return Path(base) / "prompts"


def save(text: str) -> str:
    ref = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
    d = _dir()
    d.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(d, 0o700)
    except OSError:
        pass
    path = d / f"{ref}.txt"
    if not path.exists():
        path.write_text(text, encoding="utf-8")
        os.chmod(path, 0o600)
    now = time.time()
    for old in d.glob("*.txt"):
        try:
            if now - old.stat().st_mtime > KEEP_SECONDS:
                old.unlink()
        except OSError:
            pass
    return ref


def load(ref: str) -> str:
    if not isinstance(ref, str) or not re.fullmatch(r"[0-9a-f]{16}", ref):
        raise LKError("panel_ref must be the 16-character id the prompt hook gave", "bad_input", 3)
    path = _dir() / f"{ref}.txt"
    if not path.is_file():
        raise LKError(f"panel_ref {ref} not found (saved prompts are kept two days); pass panel_text instead", "bad_input", 3)
    return path.read_text(encoding="utf-8")


def resolve(payload: dict) -> Optional[str]:
    """panel_text from panel_ref when given (panel_ref wins only if panel_text is absent)."""
    if payload.get("panel_text") is None and payload.get("panel_ref"):
        return load(payload["panel_ref"])
    return payload.get("panel_text")
