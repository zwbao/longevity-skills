"""A stdio MCP server over the same functions the command line uses.

Newline-delimited JSON-RPC 2.0 on stdin/stdout; logs go to stderr. Standard library only.
Tool names follow LongPi's native tools (find_methods, read_method, run_method,
query_evidence, review_change, review_trend) so a host can switch between them.
"""

from __future__ import annotations

import json
import math
import sys
import traceback
from typing import Any, Callable, Dict, List, Optional

from . import compare, evidence, methods, noise, panel, reference
from .library import Library, LKError
from .run import run as run_method

SUPPORTED = ["2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05"]
FALLBACK = "2025-06-18"  # answered when the client asks for a version not listed above

INSTRUCTIONS = (
    "Longevity and ageing methods from published papers, with an evidence store and within-person variation data. "
    "Typical flow: find_methods (the person's words, or what data they have) -> read_method -> run_method. "
    "Ask about a drug, supplement, diet or gene with query_evidence. Ask whether a lab change is real with review_change "
    "(two values or two groups) or review_trend (dated series). Every result names its source; animal or cell results "
    "are not human effects, and nothing here is a dose or a reason to start or stop a medicine."
)

_MEAS = {"type": "array", "description": "Lab or body measurements from ONE sampling occasion.",
         "items": {"type": "object", "properties": {
             "item": {"type": "string", "description": "name as on the report, e.g. 肌酐, creatinine, 收缩压"},
             "value": {"type": "number"},
             "unit": {"type": "string", "description": "unit as on the report, e.g. mg/dL, umol/L, mmHg"},
             "date": {"type": "string", "description": "sampling date YYYY-MM-DD (optional; mixed dates are refused)"}},
             "required": ["item", "value"]}}

TOOLS: List[Dict[str, Any]] = [
    {"name": "find_methods",
     "description": "Find methods for a question or for the data a person has. Give `text` (the person's words) to match "
                    "intents, and/or `have` (measurement names they have) to see which tier-A methods are complete and what "
                    "is missing. Returns method names with status (runnable, draft, lookup).",
     "inputSchema": {"type": "object", "properties": {
         "text": {"type": "string"},
         "have": {"type": "array", "items": {"type": "string"}},
         "panel_text": {"type": "string", "description": "a pasted lab panel or profile, any language, possibly several "
                                                         "people; returns which methods each person's data completes"},
         "intent": {"type": "string", "description": "an intent id from a previous result"},
         "include_lookups": {"type": "boolean", "description": "also list tier-B lookups and tools"}}}},
    {"name": "read_method",
     "description": "Inputs (units, accepted units, ranges), outputs, validation status and paper of one method.",
     "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}},
    {"name": "run_method",
     "description": "Run one method for one person (pass the panel as panel_text, or rows as measurements). Tier C and "
                    "undeclared methods are refused; draft methods need "
                    "allow_draft. Input problems (unit, range, missing value) come back as status input_problem with reasons.",
     "inputSchema": {"type": "object", "properties": {
         "name": {"type": "string"},
         "age": {"type": "number"},
         "sex": {"type": "string", "enum": ["male", "female"]},
         "measurements": _MEAS,
         "panel_ref": {"type": "string", "description": "id of the prompt saved by the prompt hook; use instead of copying long data"},
         "person": {"type": "string", "description": "which person (A, B, ...) when the panel describes several"},
         "panel_text": {"type": "string", "description": "instead of measurements: one person's pasted panel as text, any "
                                                         "language (e.g. 'Albumin (g/dL) 4.30; Creatinine (umol/L) 57.77; ...'); "
                                                         "age and sex are read from it when not given"},
         "answers": {"type": "object", "description": "yes/no answers the method asks for, keyed as read_method lists them "
                                                      "(e.g. smoker, diabetes, treated, north)",
                     "additionalProperties": {"type": ["boolean", "string", "number"]}},
         "medications": {"type": "array", "items": {"type": "string"}},
         "targets": {**_MEAS, "description": "target values for the levers output, where the method supports it"},
         "measurements_file": {"type": "string", "description": "path to a whole input file (e.g. methylation betas)"},
         "allow_draft": {"type": "boolean"},
         "allow_mixed_dates": {"type": "boolean"},
         "include_report": {"type": "boolean", "description": "also return the method's own report in Markdown"}},
         "required": ["name"]}},
    {"name": "estimate_age",
     "description": "What age a person's routine labs and body measurements look like, from a reference model this "
                    "library fitted on public US NHANES data (2011-2016; held-out 2017-2018 mean error about 10 years). "
                    "Not a published method and not a biological age. Returns an estimate, a 90% interval and the "
                    "probability of each age band (18-29 ... 70+). Use when the age is unknown or to compare people. "
                    "Pass panel_text (any language; several people are estimated one by one) or measurements, and sex.",
     "inputSchema": {"type": "object", "properties": {
         "panel_text": {"type": "string"},
         "panel_ref": {"type": "string", "description": "id of the prompt saved by the prompt hook; use instead of copying long data"},
         "measurements": _MEAS,
         "sex": {"type": "string", "enum": ["male", "female"]},
         "bands": {"type": "string", "description": "age bands to report probabilities for, e.g. '18-30, 30-45, 45-60, 60-75, 75+' "
                                                    "(a shared edge belongs to the higher band); default decades"}}}},
    {"name": "compare_age",
     "description": "Which of two plasma proteomic (Olink NPX) or blood methylation (CpG beta/M) profiles looks older. "
                    "Votes over every protein or CpG both profiles have, using its direction of change with age in a "
                    "published cohort (proteins: China Kadoorie Biobank, Iona 2025; CpGs: Generation Scotland, McCartney "
                    "2020), weighted by association strength. Needs no reference means; both profiles must come from the "
                    "same platform. Gives A/B and a weighted share, not an age. Pass panel_text (e.g. 'ELN (A: 0.31, B: -0.12); ...' "
                    "or two 'Participant A/B' blocks) or profile_a and profile_b.",
     "inputSchema": {"type": "object", "properties": {
         "panel_text": {"type": "string"},
         "panel_ref": {"type": "string", "description": "id of the prompt saved by the prompt hook; use instead of copying long data"},
         "profile_a": {"type": "object", "additionalProperties": {"type": "number"}},
         "profile_b": {"type": "object", "additionalProperties": {"type": "number"}},
         "modality": {"type": "string", "enum": ["proteomics", "methylation"]}}}},
    {"name": "query_evidence",
     "description": "What the papers collected in this library state about drugs, supplements, diets, genes or proteins: "
                    "grouped into human studies, animal and cell experiments, each row with DOI and location; plus "
                    "trial-average effects. An entity that is not collected is not evidence of safety or of no effect.",
     "inputSchema": {"type": "object", "properties": {
         "entities": {"type": "array", "items": {"type": "string"}, "minItems": 1},
         "limit": {"type": "integer", "minimum": 1, "maximum": 100, "description": "rows per group (default 12)"}},
         "required": ["entities"]}},
    {"name": "review_change",
     "description": "Is the change between earlier and later values of one marker beyond normal within-person variation? "
                    "Values must be in the same unit; several values per side are means of separate days.",
     "inputSchema": {"type": "object", "properties": {
         "marker": {"type": "string"},
         "before": {"type": "array", "items": {"type": "number"}, "minItems": 1},
         "after": {"type": "array", "items": {"type": "number"}, "minItems": 1},
         "gap_days": {"type": "integer"}},
         "required": ["marker", "before", "after"]}},
    {"name": "review_trend",
     "description": "Slow drift over several dated values of one marker (pairs, first vs latest, and a slope test).",
     "inputSchema": {"type": "object", "properties": {
         "marker": {"type": "string"},
         "series": {"type": "array", "items": {"type": "object", "properties": {
             "date": {"type": "string"}, "value": {"type": ["number", "string"]}, "unit": {"type": "string"}},
             "required": ["date", "value"]}, "minItems": 1}},
         "required": ["marker", "series"]}},
    {"name": "plan_experiment",
     "description": "Could one person see an intervention's effect on a marker? mode plan: trial-average effect against the "
                    "person's noise band and how many repeat measurements are needed; mode predict: probability of "
                    "detecting and of a truly favourable change (statistical model).",
     "inputSchema": {"type": "object", "properties": {
         "mode": {"type": "string", "enum": ["plan", "predict"]},
         "marker": {"type": "string"}, "intervention": {"type": "string"},
         "baseline": {"type": "number"}, "unit": {"type": "string"},
         "repeats": {"type": "integer", "minimum": 1}, "per_units": {"type": "number"},
         "adherence": {"type": "number"}},
         "required": ["mode", "marker"]}},
]


def _num_list(values: Any, what: str) -> List[str]:
    if isinstance(values, (int, float)) and not isinstance(values, bool):
        values = [values]
    if not isinstance(values, list) or not values:
        raise LKError(f"{what} must be a non-empty list of numbers", "bad_input", 3)
    out = []
    for v in values:
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
            raise LKError(f"{what}: {v!r} is not a finite number", "bad_input", 3)
        out.append(repr(float(v)))
    return out


def _str_list(values: Any, what: str) -> List[str]:
    """A list of non-empty strings; a single string counts as a list of one (never split into characters)."""
    if values is None:
        return []
    if isinstance(values, str):
        values = [values]
    if not isinstance(values, list) or not all(isinstance(v, str) for v in values):
        raise LKError(f"{what} must be a list of strings", "bad_input", 3)
    return [v for v in values if v.strip()]


def _int(value: Any, what: str, minimum: int = 1) -> int:
    if isinstance(value, bool):
        raise LKError(f"{what} must be an integer", "bad_input", 3)
    try:
        number = int(value)
    except (TypeError, ValueError):
        raise LKError(f"{what} must be an integer, got {value!r}", "bad_input", 3)
    if number < minimum or (isinstance(value, float) and value != number):
        raise LKError(f"{what} must be an integer >= {minimum}, got {value!r}", "bad_input", 3)
    return number


def _number(value: Any, what: str) -> str:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise LKError(f"{what} must be a finite number, got {value!r}", "bad_input", 3)
    return repr(float(value))


def _noise(lib: Library, argv: List[str]) -> Dict[str, Any]:
    try:
        return {**noise.compute(argv, str(lib.root)), **lib.stamp()}
    except ValueError as exc:
        raise LKError(str(exc), "bad_input", 3)


def _text(value: Any, what: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise LKError(f"{what} must be a non-empty string", "bad_input", 3)
    if value.lstrip().startswith("-"):  # would be read as an option by the variation parser
        raise LKError(f"{what} cannot start with '-': {value!r}", "bad_input", 3)
    return value


def call(lib: Library, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    if name == "find_methods":
        out: Dict[str, Any] = {}
        text = args.get("text")
        if text is not None and not isinstance(text, str):
            raise LKError("text must be a string", "bad_input", 3)
        have = _str_list(args.get("have"), "have")
        if args.get("panel_text") is not None:
            if not isinstance(args["panel_text"], str):
                raise LKError("panel_text must be a string", "bad_input", 3)
            out["panel"] = panel.detect(lib, args["panel_text"])
            if not text and not have:
                return out
        if text:
            out["find"] = methods.find(lib, text)
        if have or args.get("intent") or args.get("include_lookups") or not text:
            out["methods"] = methods.methods(lib, intent=args.get("intent") or None, have=have,
                                             include_lookups=bool(args.get("include_lookups")))
        return out
    if name == "read_method":
        return methods.describe(lib, str(args.get("name", "")))
    if name == "run_method":
        payload = {k: args.get(k) for k in ("age", "sex", "measurements", "targets", "measurements_file", "panel_text",
                                            "panel_ref", "person")}
        payload["medications"] = _str_list(args.get("medications"), "medications")
        answers = args.get("answers") or {}
        if not isinstance(answers, dict):
            raise LKError("answers must be an object {key: value}", "bad_input", 3)
        payload["arguments"] = answers
        return run_method(lib, str(args.get("name", "")), payload, allow_draft=args.get("allow_draft") is True,
                          allow_mixed_dates=args.get("allow_mixed_dates") is True,
                          include_report=args.get("include_report") is True)
    if name == "estimate_age":
        return reference.estimate_from_payload(lib, {k: args.get(k) for k in ("panel_text", "panel_ref", "measurements", "sex", "bands")})
    if name == "compare_age":
        return compare.compare_from_payload(lib, {k: args.get(k) for k in ("panel_text", "panel_ref", "profile_a", "profile_b", "modality")})
    if name == "query_evidence":
        limit = _int(args["limit"], "limit") if args.get("limit") is not None else 12
        return evidence.query(lib, _str_list(args.get("entities"), "entities"), limit=limit)
    if name == "review_change":
        argv = ["change", "--marker", _text(args.get("marker"), "marker"),
                "--before", *_num_list(args.get("before"), "before"), "--after", *_num_list(args.get("after"), "after")]
        if args.get("gap_days") is not None:
            argv += ["--gap-days", str(_int(args["gap_days"], "gap_days", minimum=0))]
        return _noise(lib, argv)
    if name == "review_trend":
        series = args.get("series")
        if not isinstance(series, list) or not series:
            raise LKError("series must be a non-empty list of {date, value, unit?}", "bad_input", 3)
        tokens = []
        for p in series:
            if not isinstance(p, dict) or not isinstance(p.get("date"), str) or p.get("value") is None:
                raise LKError(f"series point {p!r} needs a date string and a value", "bad_input", 3)
            value = p["value"]
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                value = _number(value, "series value")
            elif not isinstance(value, str):  # strings carry censored values such as "<0.5"
                raise LKError(f"series value {value!r} must be a number or a string", "bad_input", 3)
            parts = [p["date"].strip(), str(value).strip()]
            if p.get("unit"):
                parts.append(str(p["unit"]).strip())
            if any(":" in x for x in parts[:2]) or any(x.startswith("-") and not x[1:2].isdigit() for x in parts):
                raise LKError(f"series point {p!r} has a ':' or a leading '-' it cannot carry", "bad_input", 3)
            tokens.append(":".join(parts))
        return _noise(lib, ["trend", "--marker", _text(args.get("marker"), "marker"), "--series", *tokens])
    if name == "plan_experiment":
        mode = args.get("mode")
        if mode not in ("plan", "predict"):
            raise LKError("mode must be plan or predict", "bad_input", 3)
        if mode == "predict" and not args.get("intervention"):
            raise LKError("predict needs an intervention", "bad_input", 3)
        argv = [mode, "--marker", _text(args.get("marker"), "marker")]
        if args.get("intervention") is not None:
            argv += ["--intervention", _text(args["intervention"], "intervention")]
        if args.get("unit") is not None:
            argv += ["--unit", _text(args["unit"], "unit")]
        if args.get("baseline") is not None:
            argv += ["--baseline", _number(args["baseline"], "baseline")]
        if args.get("per_units") is not None:
            argv += ["--per-units", _number(args["per_units"], "per_units")]
        if args.get("repeats") is not None:
            argv += ["--repeats", str(_int(args["repeats"], "repeats"))]
        if mode == "predict" and args.get("adherence") is not None:
            argv += ["--adherence", _number(args["adherence"], "adherence")]
        return _noise(lib, argv)
    raise RpcError(-32602, f"unknown tool: {name!r}")


class RpcError(Exception):
    def __init__(self, code: int, message: str) -> None:
        super().__init__(message)
        self.code = code


TOOL_NAMES = {t["name"] for t in TOOLS}
# Results whose status means the tool did not produce what was asked; refusals and input problems are answers.
ERROR_STATUSES = {"error", "missing_dependency"}


class Server:
    """stdio MCP server. Protocol messages go to the real stdout; anything else printed while serving goes to stderr."""

    def __init__(self, lib: Library, out=None, log=None) -> None:
        self.lib = lib
        self.out = out
        self.log = log or sys.stderr

    def _write(self, payload: Any) -> None:
        # allow_nan=False: NaN/Infinity are not JSON; a result that has them is a bug, reported as an error instead.
        text = json.dumps(payload, ensure_ascii=False, allow_nan=False) + "\n"
        if hasattr(self.out, "buffer"):
            self.out.buffer.write(text.encode("utf-8"))
        else:
            self.out.write(text)
        self.out.flush()

    def send(self, message: Any) -> None:
        try:
            self._write(message)
        except ValueError:  # NaN in a result
            mid = message.get("id") if isinstance(message, dict) else None
            self._write({"jsonrpc": "2.0", "id": mid, "error": {"code": -32603, "message": "result held a non-finite number"}})

    @staticmethod
    def _error(mid: Any, code: int, message: str) -> Dict[str, Any]:
        return {"jsonrpc": "2.0", "id": mid, "error": {"code": code, "message": message}}

    def handle(self, msg: Any) -> Optional[Dict[str, Any]]:
        if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0":
            return self._error(None, -32600, "invalid request")
        if "method" not in msg and ("result" in msg or "error" in msg):
            return None  # a response to a request this server never sends; ignore
        method, mid = msg.get("method"), msg.get("id")
        is_request = "id" in msg
        if is_request and (isinstance(mid, bool) or not isinstance(mid, (str, int))):
            return self._error(None, -32600, "id must be a string or an integer")
        if not isinstance(method, str):
            return self._error(mid, -32600, "invalid request") if is_request else None
        handlers: Dict[str, Callable[[Dict[str, Any]], Any]] = {
            "initialize": self.initialize, "ping": lambda p: {},
            "tools/list": lambda p: {"tools": TOOLS}, "tools/call": self.tools_call,
            "resources/list": lambda p: {"resources": []}, "prompts/list": lambda p: {"prompts": []},
        }
        if not is_request:  # notifications (initialized, cancelled, ...) need no answer
            return None
        fn = handlers.get(method)
        if fn is None:
            return self._error(mid, -32601, f"method not found: {method}")
        params = msg.get("params")
        if params is None:
            params = {}
        if not isinstance(params, dict):
            return self._error(mid, -32602, "params must be an object")
        try:
            return {"jsonrpc": "2.0", "id": mid, "result": fn(params)}
        except RpcError as exc:
            return self._error(mid, exc.code, str(exc))
        except Exception:  # never let one bad call end the session, never send a traceback to the client
            traceback.print_exc(file=self.log)
            return self._error(mid, -32603, "internal error")

    def initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        asked = params.get("protocolVersion")
        version = asked if asked in SUPPORTED else FALLBACK
        return {"protocolVersion": version, "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "longevity-skills", "version": self.lib.release},
                "instructions": INSTRUCTIONS}

    def tools_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        name = params.get("name")
        if not isinstance(name, str) or name not in TOOL_NAMES:
            raise RpcError(-32602, f"unknown tool: {name!r}")
        args = params.get("arguments")
        if args is None:
            args = {}
        if not isinstance(args, dict):
            raise RpcError(-32602, "arguments must be an object")
        try:
            result = call(self.lib, name, args)
            is_error = isinstance(result, dict) and result.get("status") in ERROR_STATUSES
        except LKError as exc:
            result, is_error = {"error": exc.code, "message": str(exc)}, True
        except (TypeError, ValueError, KeyError, AttributeError, ZeroDivisionError, OverflowError) as exc:
            traceback.print_exc(file=self.log)
            result, is_error = {"error": "bad_input", "message": f"{type(exc).__name__}: {exc}"}, True
        try:
            text = json.dumps(result, ensure_ascii=False, allow_nan=False)
        except ValueError:
            text, is_error = json.dumps({"error": "bad_input", "message": "the result held a non-finite number"}), True
        return {"content": [{"type": "text", "text": text}], "isError": is_error}

    def _line(self, raw: bytes) -> None:
        line = raw.decode("utf-8", errors="replace").strip()
        if not line:
            return
        try:
            msg = json.loads(line)
        except (ValueError, RecursionError):
            self.send(self._error(None, -32700, "parse error"))
            return
        if isinstance(msg, list):  # batches (2025-03-26) are answered together
            if not msg:
                self.send(self._error(None, -32600, "empty batch"))
                return
            replies = [r for r in (self.handle(m) for m in msg) if r is not None]
            if replies:
                self.send(replies)
            return
        reply = self.handle(msg)
        if reply is not None:
            self.send(reply)

    def serve(self, stream=None) -> int:
        """Read newline-delimited JSON-RPC as bytes (UTF-8, bad bytes replaced) until EOF."""
        real_stdout = sys.stdout
        if self.out is None:
            self.out = real_stdout
        if stream is None:
            stream = sys.stdin.buffer
        sys.stdout = sys.stderr  # stray prints from anything we call cannot corrupt the protocol stream
        try:
            for raw in stream:
                if isinstance(raw, str):
                    raw = raw.encode("utf-8", errors="replace")
                try:
                    self._line(raw)
                except Exception:  # keep serving whatever one line did
                    traceback.print_exc(file=self.log)
                    try:
                        self.send(self._error(None, -32603, "internal error"))
                    except Exception:
                        pass
        finally:
            sys.stdout = real_stdout
        return 0
