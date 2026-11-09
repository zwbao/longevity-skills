"""Command line: `longevity <command>`. Every command prints one JSON object on stdout (`--help` prints text)."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, List, Optional

from . import evidence, methods, noise
from .library import Library, LKError, open_library
from .run import parse_measurement
from .run import run as run_method

NOISE_COMMANDS = {"change", "trend", "plan", "predict", "markers"}
EXIT = {"ok": 0, "input_problem": 3, "not_computed": 3, "refused": 4, "missing_dependency": 5, "error": 1}
ERROR_EXIT = {"bad_input": 3, "usage": 2, "unknown_method": 2, "unknown_intent": 2, "library_not_found": 2}

USAGE = """\
longevity: methods, evidence and within-person variation from the longevity-skills library. Output is JSON.

  longevity find 我的生物年龄是多少                     match the person's words to intents and methods
  longevity methods [--intent ID] [--have 肌酐,白蛋白] [--all]   tier-A methods; with --have, what is still missing
  longevity describe ckd-epi-2021-egfr                 inputs, units, ranges, outputs, validation, paper
  longevity run ckd-epi-2021-egfr --age 62 --sex female -m '肌酐=78 umol/L'
  longevity run china-par-ascvd-risk --input person.json   (or --input - for stdin)
  longevity evidence NMN [雷帕霉素 ...]                 what the collected papers state, grouped human/animal/cell
  longevity change --marker 收缩压 --before 138 --after 131       is a change beyond normal variation
  longevity trend --marker 空腹血糖 --series 2024-09-03:5.0 2025-09-02:5.3 2026-09-01:5.6
  longevity plan --marker 收缩压 --intervention 减盐 --baseline 138 --unit mmHg --repeats 14
  longevity predict ... | longevity markers
  longevity mcp                                        serve all of this over stdio MCP
  longevity version

Global options: --library PATH (or --library=PATH) before the command, --pretty anywhere.
Exit codes: 0 ok, 2 usage, 3 input problem or nothing computed, 4 refused, 5 missing dependency, 1 error.
"""


class Parser(argparse.ArgumentParser):
    """argparse that reports errors as JSON (through LKError) instead of printing usage and exiting."""

    def error(self, message: str):  # type: ignore[override]
        raise LKError(f"{self.prog}: {message}", "usage", 2)


def _dump(obj: Any, pretty: bool) -> str:
    return json.dumps(obj, ensure_ascii=False, allow_nan=False, indent=2 if pretty else None)


def _print(obj: Any, pretty: bool) -> None:
    try:
        text = _dump(obj, pretty)
    except ValueError:  # NaN/Infinity are not JSON
        text = _dump({"error": "bad_output", "message": "the result held a non-finite number"}, pretty)
    sys.stdout.write(text + "\n")
    sys.stdout.flush()


def _split_csv(values: Optional[List[str]]) -> List[str]:
    out: List[str] = []
    for v in values or []:
        out += [x.strip() for x in v.replace("，", ",").replace("、", ",").split(",") if x.strip()]
    return out


def _run_parser() -> argparse.ArgumentParser:
    p = Parser(prog="longevity run", description="Run one method for one person.")
    p.add_argument("name")
    p.add_argument("--input", help="JSON file (or - for stdin): {age, sex, measurements:[{item,value,unit,date}], "
                                   "arguments:{key: value}, medications:[...], targets:[...], measurements_file}")
    p.add_argument("--age", type=float)
    p.add_argument("--sex")
    p.add_argument("-m", "--measurement", action="append", default=[], metavar="ITEM=VALUE UNIT[@DATE]")
    p.add_argument("--answer", action="append", default=[], metavar="KEY=VALUE", help="e.g. smoker=no diabetes=yes")
    p.add_argument("--medication", action="append", default=[])
    p.add_argument("--measurements-file")
    p.add_argument("--allow-draft", action="store_true")
    p.add_argument("--allow-mixed-dates", action="store_true")
    p.add_argument("--report", action="store_true", help="include the method's Markdown report")
    p.add_argument("--out", help="keep the method's output files in this new or empty directory")
    p.add_argument("--timeout", type=int, default=180)
    return p


def _read_input(path: str) -> Dict[str, Any]:
    try:
        raw = sys.stdin.buffer.read().decode("utf-8") if path == "-" else open(path, encoding="utf-8").read()
    except (OSError, UnicodeDecodeError) as exc:
        raise LKError(f"--input {path}: {exc}", "bad_input", 3)
    try:
        payload = json.loads(raw)
    except (ValueError, RecursionError) as exc:
        raise LKError(f"--input is not valid JSON: {exc}", "bad_input", 3)
    if not isinstance(payload, dict):
        raise LKError("--input must be a JSON object", "bad_input", 3)
    if "answers" in payload and "arguments" not in payload:
        payload["arguments"] = payload.pop("answers")
    return payload


def cmd_run(lib: Library, argv: List[str]) -> Dict[str, Any]:
    a = _run_parser().parse_args(argv)
    payload: Dict[str, Any] = _read_input(a.input) if a.input else {}
    if a.age is not None:
        payload["age"] = a.age
    if a.sex:
        payload["sex"] = a.sex
    if a.measurement:
        payload["measurements"] = list(payload.get("measurements") or []) + [parse_measurement(m) for m in a.measurement]
    if a.answer:
        answers = dict(payload.get("arguments") or {})
        for item in a.answer:
            if "=" not in item:
                raise LKError(f"--answer {item!r} should be KEY=VALUE", "bad_input", 3)
            k, v = item.split("=", 1)
            k = k.strip().replace("-", "_")
            if k in answers:  # repeated answers (e.g. --answer drug=A --answer drug=B) become a list
                answers[k] = (answers[k] if isinstance(answers[k], list) else [answers[k]]) + [v.strip()]
            else:
                answers[k] = v.strip()
        payload["arguments"] = answers
    if a.medication:
        payload["medications"] = list(payload.get("medications") or []) + a.medication
    if a.measurements_file:
        payload["measurements_file"] = a.measurements_file
    return run_method(lib, a.name, payload, allow_draft=a.allow_draft, allow_mixed_dates=a.allow_mixed_dates,
                      include_report=a.report, out_dir=a.out, timeout=a.timeout)


def _globals(argv: List[str]):
    library, pretty, rest = None, False, []
    if "--pretty" in argv:
        pretty = True
        argv = [x for x in argv if x != "--pretty"]
    while argv and (argv[0] == "--library" or argv[0].startswith("--library=")):
        flag = argv.pop(0)
        if flag.startswith("--library="):
            library = flag.split("=", 1)[1]
        elif argv:
            library = argv.pop(0)
        else:
            raise LKError("--library needs a path", "usage", 2)
    rest = argv
    return library, pretty, rest


def main(argv: Optional[List[str]] = None) -> int:
    for stream in (sys.stdout, sys.stderr):  # JSON with Chinese text must not depend on the console code page
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except (ValueError, OSError):
                pass
    argv = list(sys.argv[1:] if argv is None else argv)
    pretty = "--pretty" in argv
    lib: Optional[Library] = None
    try:
        library, pretty, argv = _globals(argv)
        if not argv or argv[0] in ("-h", "--help", "help"):
            sys.stdout.write(USAGE)
            return 0 if argv else 2
        cmd, rest = argv[0], argv[1:]
        lib = open_library(library)
        if cmd == "mcp":
            from .mcp import Server
            return Server(lib).serve()
        if cmd == "version":
            out: Dict[str, Any] = {"library": str(lib.root), **lib.stamp(), "python": sys.version.split()[0],
                                   "methods": sum(1 for s in lib.skills.values() if methods.status_of(s)[0] == "runnable")}
        elif cmd == "find":
            if not rest:
                raise LKError("find needs the person's words", "usage", 2)
            out = methods.find(lib, " ".join(rest))
        elif cmd == "methods":
            p = Parser(prog="longevity methods")
            p.add_argument("--intent")
            p.add_argument("--have", action="append", help="comma-separated measurement names")
            p.add_argument("--all", action="store_true", help="also tier-B lookups and tools")
            a = p.parse_args(rest)
            out = methods.methods(lib, intent=a.intent, have=_split_csv(a.have), include_lookups=a.all)
        elif cmd in ("describe", "read"):
            if len(rest) != 1:
                raise LKError(f"{cmd} takes one method name", "usage", 2)
            out = methods.describe(lib, rest[0])
        elif cmd == "run":
            out = cmd_run(lib, rest)
            _print(out, pretty)
            return EXIT.get(out.get("status", "error"), 1)
        elif cmd == "evidence":
            p = Parser(prog="longevity evidence")
            p.add_argument("names", nargs="*")
            p.add_argument("--entity", action="append", default=[])
            p.add_argument("--medication", action="append", default=[])
            p.add_argument("--limit", type=int, default=12)
            a = p.parse_args(rest)
            out = evidence.query(lib, a.names + a.entity, limit=a.limit, medications=a.medication)
        elif cmd in NOISE_COMMANDS:
            try:
                out = {**noise.compute([cmd, *rest], str(lib.root)), **lib.stamp()}
            except noise.HelpShown:
                return 0
            except ValueError as exc:
                raise LKError(str(exc), "bad_input", 3)
        else:
            raise LKError(f"unknown command {cmd!r}; run `longevity --help`", "usage", 2)
    except LKError as exc:
        err: Dict[str, Any] = {"error": exc.code, "message": str(exc)}
        if lib is not None:
            err.update(lib.stamp())
        _print(err, pretty)
        return ERROR_EXIT.get(exc.code, exc.exit_code)
    _print(out, pretty)
    return 0


if __name__ == "__main__":
    sys.exit(main())
