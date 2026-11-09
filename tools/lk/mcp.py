"""A stdio MCP server over the same functions the command line uses.

Newline-delimited JSON-RPC 2.0 on stdin/stdout; logs go to stderr. Standard library only.
Tool names follow LongPi's native tools (find_methods, read_method, run_method,
query_evidence, review_change, review_trend) so a host can switch between them.
"""

from __future__ import annotations

import json
import sys
import traceback
from typing import Any, Callable, Dict, List, Optional

from . import evidence, methods, noise
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
         "intent": {"type": "string", "description": "an intent id from a previous result"},
         "include_lookups": {"type": "boolean", "description": "also list tier-B lookups and tools"}}}},
    {"name": "read_method",
     "description": "Inputs (units, accepted units, ranges), outputs, validation status and paper of one method.",
     "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}},
    {"name": "run_method",
     "description": "Run one method for one person. Tier C and undeclared methods are refused; draft methods need "
                    "allow_draft. Input problems (unit, range, missing value) come back as status input_problem with reasons.",
     "inputSchema": {"type": "object", "properties": {
         "name": {"type": "string"},
         "age": {"type": "number"},
         "sex": {"type": "string", "enum": ["male", "female"]},
         "measurements": _MEAS,
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
    if not isinstance(values, list) or not values:
        raise LKError(f"{what} must be a non-empty list of numbers", "bad_input", 2)
    out = []
    for v in values:
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            raise LKError(f"{what}: {v!r} is not a number", "bad_input", 2)
        out.append(repr(float(v)))
    return out


def _noise(lib: Library, argv: List[str]) -> Dict[str, Any]:
    try:
        return {**noise.compute(argv, str(lib.root)), **lib.stamp()}
    except ValueError as exc:
        raise LKError(str(exc), "bad_input", 2)


def call(lib: Library, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    if name == "find_methods":
        out: Dict[str, Any] = {}
        if args.get("text"):
            out["find"] = methods.find(lib, str(args["text"]))
        if args.get("have") or args.get("intent") or args.get("include_lookups") or not args.get("text"):
            out["methods"] = methods.methods(lib, intent=args.get("intent"), have=args.get("have"),
                                             include_lookups=bool(args.get("include_lookups")))
        return out
    if name == "read_method":
        return methods.describe(lib, str(args.get("name", "")))
    if name == "run_method":
        payload = {k: args.get(k) for k in ("age", "sex", "measurements", "medications", "targets", "measurements_file")}
        payload["arguments"] = args.get("answers") or {}
        return run_method(lib, str(args.get("name", "")), payload, allow_draft=bool(args.get("allow_draft")),
                          allow_mixed_dates=bool(args.get("allow_mixed_dates")),
                          include_report=bool(args.get("include_report")))
    if name == "query_evidence":
        ents = args.get("entities")
        if isinstance(ents, str):
            ents = [ents]
        return evidence.query(lib, ents or [], limit=int(args.get("limit") or 12))
    if name == "review_change":
        argv = ["change", "--marker", str(args.get("marker", "")), "--before", *_num_list(args.get("before"), "before"),
                "--after", *_num_list(args.get("after"), "after")]
        if args.get("gap_days") is not None:
            argv += ["--gap-days", str(int(args["gap_days"]))]
        return _noise(lib, argv)
    if name == "review_trend":
        series = args.get("series")
        if not isinstance(series, list) or not series:
            raise LKError("series must be a non-empty list of {date, value, unit?}", "bad_input", 2)
        tokens = []
        for p in series:
            if not isinstance(p, dict) or not p.get("date") or p.get("value") is None:
                raise LKError(f"series point {p!r} needs date and value", "bad_input", 2)
            tok = f"{p['date']}:{p['value']}" + (f":{p['unit']}" if p.get("unit") else "")
            tokens.append(tok)
        return _noise(lib, ["trend", "--marker", str(args.get("marker", "")), "--series", *tokens])
    if name == "plan_experiment":
        mode = args.get("mode")
        if mode not in ("plan", "predict"):
            raise LKError("mode must be plan or predict", "bad_input", 2)
        if mode == "predict" and not args.get("intervention"):
            raise LKError("predict needs an intervention", "bad_input", 2)
        argv = [mode, "--marker", str(args.get("marker", ""))]
        for key, flag in (("intervention", "--intervention"), ("baseline", "--baseline"), ("unit", "--unit"),
                          ("repeats", "--repeats"), ("per_units", "--per-units")):
            if args.get(key) is not None:
                argv += [flag, str(args[key])]
        if mode == "predict" and args.get("adherence") is not None:
            argv += ["--adherence", str(args["adherence"])]
        return _noise(lib, argv)
    raise LKError(f"unknown tool {name!r}", "unknown_tool", 2)


class Server:
    def __init__(self, lib: Library, out=None, log=None) -> None:
        self.lib = lib
        self.out = out or sys.stdout
        self.log = log or sys.stderr

    def send(self, message: Dict[str, Any]) -> None:
        self.out.write(json.dumps(message, ensure_ascii=False) + "\n")
        self.out.flush()

    def handle(self, msg: Any) -> Optional[Dict[str, Any]]:
        if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0":
            return {"jsonrpc": "2.0", "id": None, "error": {"code": -32600, "message": "invalid request"}}
        method, mid = msg.get("method"), msg.get("id")
        is_request = "id" in msg
        if not isinstance(method, str):
            return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32600, "message": "invalid request"}} if is_request else None
        handlers: Dict[str, Callable[[Dict[str, Any]], Any]] = {
            "initialize": self.initialize, "ping": lambda p: {},
            "tools/list": lambda p: {"tools": TOOLS}, "tools/call": self.tools_call,
            "resources/list": lambda p: {"resources": []}, "prompts/list": lambda p: {"prompts": []},
        }
        if not is_request:  # notifications (initialized, cancelled, ...) need no answer
            return None
        fn = handlers.get(method)
        if fn is None:
            return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"method not found: {method}"}}
        params = msg.get("params") or {}
        if not isinstance(params, dict):
            return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32602, "message": "params must be an object"}}
        try:
            return {"jsonrpc": "2.0", "id": mid, "result": fn(params)}
        except Exception as exc:  # never let one bad call end the session
            traceback.print_exc(file=self.log)
            return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32603, "message": f"internal error: {exc}"}}

    def initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        asked = params.get("protocolVersion")
        version = asked if asked in SUPPORTED else FALLBACK
        return {"protocolVersion": version, "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "longevity-skills", "version": self.lib.release},
                "instructions": INSTRUCTIONS}

    def tools_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        name = params.get("name")
        args = params.get("arguments") or {}
        if not isinstance(args, dict):
            args = {}
        try:
            result = call(self.lib, str(name), args)
            is_error = False
        except LKError as exc:
            result, is_error = {"error": exc.code, "message": str(exc)}, True
        except Exception as exc:  # report, do not crash
            traceback.print_exc(file=self.log)
            result, is_error = {"error": "internal", "message": str(exc)}, True
        return {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}], "isError": is_error}

    def serve(self, stream=None) -> int:
        stream = stream or sys.stdin
        for line in stream:
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except ValueError:
                self.send({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "parse error"}})
                continue
            if isinstance(msg, list):  # batches (2025-03-26) are answered one by one
                replies = [r for r in (self.handle(m) for m in msg) if r is not None]
                if replies:
                    self.out.write(json.dumps(replies, ensure_ascii=False) + "\n")
                    self.out.flush()
                continue
            reply = self.handle(msg)
            if reply is not None:
                self.send(reply)
        return 0
