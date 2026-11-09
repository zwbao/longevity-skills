"""Run one method through its skill.json `entry` contract and return one JSON result.

Rules every host gets, whatever agent calls this:
- tier C and methods whose inputs are not declared are refused;
- tier A methods still in validation (`draft`) are refused unless allow_draft;
- measurements whose sampling dates differ, or where only some rows are dated, are refused unless allow_mixed_dates
  (rows in a measurements_file with a date column included);
- for every method that declares its measurement inputs, the engine itself matches each row to an input, converts
  it with the declared factors and checks the range with the library's skillkit before the script runs, and hands
  the script one row per input, named by its key, in the input's own unit. A problem stops the run. Scripts that
  never call skillkit (some lookups) get the same protection;
- every result carries the release, the method's tier, label, validation status and paper;
- a run whose declared outputs all come back empty is reported as not_computed, not ok.
"""

from __future__ import annotations

import csv
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

from .library import Library, LKError
from .methods import argument_kind, label_of, paper_of, status_of

DEFAULT_TIMEOUT = 180
YES = {"1", "yes", "y", "true", "是", "有"}
NO = {"0", "no", "n", "false", "否", "无", "没有"}
SEX = {"male": "male", "m": "male", "男": "male", "man": "male", "男性": "male",
       "female": "female", "f": "female", "女": "female", "woman": "female", "女性": "female"}
MEAS_RE = re.compile(r"^\s*(?P<item>[^=]+?)\s*=\s*(?P<value>[-+]?[0-9.]+(?:[eE][-+]?\d+)?)\s*(?P<unit>.*?)\s*$")
DATE_COLUMNS = ("date", "sample_date", "sampling_date", "日期", "采样日期", "检测日期", "采集日期", "报告日期")
OUTPUT_FILES = ("result.json", "problems.json", "report.md", "levers.json", "cpic_recommendations.json")


def bad(message: str) -> LKError:
    return LKError(message, "bad_input", 3)


def parse_measurement(text: str) -> Dict[str, Any]:
    """`肌酐=78 umol/L` or `肌酐=78 umol/L @2026-10-01` -> {item, value, unit, date}."""
    when = None
    if "@" in text:
        text, when = text.rsplit("@", 1)
        when = when.strip() or None
    m = MEAS_RE.match(text)
    if not m:
        raise bad(f"measurement {text!r} should look like 名称=数值 单位, e.g. 肌酐=78 umol/L")
    row: Dict[str, Any] = {"item": m.group("item"), "value": m.group("value"), "unit": m.group("unit")}
    if when:
        row["date"] = when
    return row


def norm_date(value: Any) -> str:
    text = str(value).strip() if isinstance(value, (str, int)) else ""
    m = (re.match(r"^(\d{4})[-/.年](\d{1,2})[-/.月](\d{1,2})日?$", text)
         or re.match(r"^(\d{4})(\d{2})(\d{2})$", text))
    try:
        if not m:
            raise ValueError
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3))).isoformat()
    except ValueError:
        raise bad(f"date {value!r} is not a date; use YYYY-MM-DD")


def _no_breaks(*fields: str) -> None:
    for f in fields:
        if "\n" in f or "\r" in f:
            raise bad(f"{f!r} contains a line break")


def _clean_rows(rows: Any, what: str) -> List[Dict[str, Any]]:
    if rows is None:
        return []
    if not isinstance(rows, list):
        raise bad(f"{what} must be a list of {{item, value, unit}}")
    out = []
    for r in rows:
        if isinstance(r, str):
            r = parse_measurement(r)
        if not isinstance(r, dict) or not isinstance(r.get("item"), (str, int)) or not str(r.get("item")).strip():
            raise bad(f"each {what} row needs an item name: {r!r}")
        value = r.get("value")
        if isinstance(value, bool) or value is None or not isinstance(value, (str, int, float)):
            raise bad(f"{what} row {r.get('item')!r} needs a number")
        if isinstance(value, float) and not math.isfinite(value):
            raise bad(f"{what} row {r.get('item')!r} has a non-finite value")
        unit = r.get("unit")
        if unit is not None and not isinstance(unit, str):
            raise bad(f"{what} row {r.get('item')!r}: unit must be text")
        row = {"item": str(r["item"]).strip(), "value": str(value).strip(), "unit": (unit or "").strip()}
        _no_breaks(row["item"], row["value"], row["unit"])
        if r.get("date") not in (None, ""):
            row["date"] = norm_date(r["date"])
        out.append(row)
    return out


def _rows_from_file(lib: Library, path: Path) -> List[Dict[str, Any]]:
    """Rows of a name/value/unit[/date] table, read with the library's own column rules."""
    kit = lib.skillkit
    try:
        table = kit.read_rows(path)
    except (OSError, UnicodeDecodeError, csv.Error) as exc:
        raise bad(f"cannot read measurements_file {path}: {exc}")
    if not table:
        return []
    fields = list(table[0].keys())
    name_col = kit._column(fields, kit.NAME_COLUMNS)
    value_col = kit._column(fields, kit.VALUE_COLUMNS)
    unit_col = kit._column(fields, kit.UNIT_COLUMNS)
    date_col = kit._column(fields, DATE_COLUMNS)
    if name_col is None or value_col is None:
        raise bad("measurements_file needs a name column and a value column, e.g. item,value,unit[,date]")
    rows = []
    for t in table:
        if not t.get(name_col) or t.get(value_col, "") == "":
            continue
        row = {"item": t[name_col], "value": t[value_col], "unit": t.get(unit_col, "") if unit_col else ""}
        if date_col and t.get(date_col):
            row["date"] = t[date_col]
        rows.append(row)
    return _clean_rows(rows, "measurements_file")


def _file_dates(lib: Library, path: Path) -> List[Optional[str]]:
    """Dates in a whole input file (e.g. a beta table) that has a date column; [] when it has none."""
    kit = lib.skillkit
    try:
        table = kit.read_rows(path)
    except (OSError, UnicodeDecodeError, csv.Error):
        return []
    if not table:
        return []
    date_col = kit._column(list(table[0].keys()), DATE_COLUMNS)
    if not date_col:
        return []
    return [norm_date(t[date_col]) if t.get(date_col) else None for t in table]


def _dates_problem(dates: List[Optional[str]]) -> Optional[str]:
    present = sorted({d for d in dates if d})
    if len(present) > 1:
        return f"这些测量来自不同的采样日期（{'、'.join(present)}）"
    if present and any(d is None for d in dates):
        return f"只有一部分测量写了采样日期（{present[0]}），其余没写，无法确认是同一次采样"
    return None


def _write_rows(path: Path, header: List[str], rows: List[Dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(header[:3] if len(header) >= 3 else [*header, "unit"][:3])
        for r in rows:
            w.writerow([r.get("item", ""), r.get("value", ""), r.get("unit", "") or ""])


def _str_list(values: Any, what: str) -> List[str]:
    if values is None:
        return []
    if isinstance(values, str):
        values = [values]
    if not isinstance(values, list) or not all(isinstance(v, str) for v in values):
        raise bad(f"{what} must be a list of strings")
    for v in values:
        _no_breaks(v)
    return [v.strip() for v in values if v.strip()]


def _plain(value: Any) -> Any:
    """NaN and infinities are not JSON; report them as null."""
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {k: _plain(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_plain(v) for v in value]
    return value


def _head(lib: Library, name: str, s: Dict[str, Any]) -> Dict[str, Any]:
    head = {"schema": "longevity-run/1", "method": name, "tier": s.get("tier"), "label_zh": label_of(s),
            "validation_status": s.get("validation_status"), "paper": paper_of(s), **lib.stamp()}
    return head


def refusal(head: Dict[str, Any], code: str, message_zh: str, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    out = {**head, "status": "refused", "code": code, "message_zh": message_zh}
    if extra:
        out.update(extra)
    return out


def _argument_tokens(spec: Dict[str, Any], kind: str, value: Any) -> List[str]:
    """Command-line tokens for one `from: argument` input: yes/no answers, switches, file paths, numbers or text."""
    key = spec["key"]
    flag = spec.get("flag") or "--" + key.replace("_", "-")

    def yes_no(v: Any) -> bool:
        if isinstance(v, bool):
            return v
        text = str(v).strip().lower() if isinstance(v, (str, int)) else ""
        if text in YES:
            return True
        if text in NO:
            return False
        raise bad(f"{key}: answer yes or no (是/否), got {v!r}")

    def one(v: Any) -> str:
        if isinstance(v, bool) or not isinstance(v, (str, int, float)):
            raise bad(f"{key}: expected a number or text, got {v!r}")
        if isinstance(v, float) and not math.isfinite(v):
            raise bad(f"{key}: non-finite number")
        text = str(v).strip()
        _no_breaks(text)
        if not text:
            raise bad(f"{key}: empty value")
        return text

    if kind == "switch":
        return [flag] if yes_no(value) else []
    if kind == "yes_no":
        return [f"{flag}={'yes' if yes_no(value) else 'no'}"]
    if kind == "file":
        if not isinstance(value, str) or not value.strip():
            raise bad(f"{key}: give the path of the file")
        path = Path(value).expanduser()
        if not path.is_file():
            raise bad(f"{key}: file {value} not found")
        return [f"{flag}={path.resolve()}"]
    if kind == "multi":
        values = value if isinstance(value, list) else [value]
        return [f"{flag}={one(v)}" for v in values]
    return [f"{flag}={one(value)}"]  # `=` keeps values such as -1.5e-1 from reading as flags


def run(lib: Library, name: str, payload: Dict[str, Any], allow_draft: bool = False, allow_mixed_dates: bool = False,
        include_report: bool = False, out_dir: Optional[str] = None, timeout: int = DEFAULT_TIMEOUT) -> Dict[str, Any]:
    s = lib.skill(name)
    head = _head(lib, name, s)
    status, why = status_of(s)
    if status == "not_runnable":
        hint = "；问论文对某个对象说了什么，用 evidence" if s.get("tier") == "C" else ""
        return refusal(head, "not_runnable", why + hint)
    if status == "draft" and not allow_draft:
        return refusal(head, "draft", "这个方法还没核对上论文印出的示例（仍在验证），默认不运行。确需运行请加 --allow-draft，结果会标明仍在验证。")
    if not isinstance(payload, dict):
        raise bad("the input must be a JSON object")

    manifest = lib.manifest(name)
    entry = manifest.get("entry") or {}
    skill_dir = lib.skill_dir(name)
    script = (skill_dir / entry["script"]).resolve()
    if skill_dir.resolve() not in script.parents or not script.is_file():
        raise LKError(f"{name}: entry script {entry.get('script')!r} is missing", "library_broken")

    kit = lib.skillkit
    meas_specs = kit.input_specs(manifest, "measurements") if manifest.get("inputs") else []
    measurements = _clean_rows(payload.get("measurements"), "measurements")
    mfile = payload.get("measurements_file")
    if mfile is not None:
        if measurements:
            raise bad("give measurements or measurements_file, not both")
        if not isinstance(mfile, str) or not Path(mfile).expanduser().is_file():
            raise bad(f"measurements_file {mfile!r} not found")
        if not entry.get("measurements_flag"):
            raise bad(f"{name} does not take a measurements file")
        mpath = Path(mfile).expanduser().resolve()
        if meas_specs:  # a declared table: read it like typed-in rows, so every check below applies
            measurements, mpath = _rows_from_file(lib, mpath), None
            dates: List[Optional[str]] = [r.get("date") for r in measurements]
        else:
            dates = _file_dates(lib, mpath)
    else:
        mpath = None
        dates = [r.get("date") for r in measurements]
    targets = _clean_rows(payload.get("targets"), "targets")
    meds = _str_list(payload.get("medications"), "medications")

    problem = _dates_problem(dates)
    if problem and not allow_mixed_dates:
        return refusal(head, "mixed_dates", problem + "。论文的方法按同一次采样计算，混用会算错。请只交同一次的结果；"
                       "确需混用请加 --allow-mixed-dates。", {"dates": sorted({d for d in dates if d})})

    arg_specs = {i["key"]: i for i in (manifest.get("inputs") or []) if i.get("from") == "argument"}
    answers = payload.get("arguments") or {}
    if not isinstance(answers, dict):
        raise bad("arguments must be an object {key: value}")
    unknown = sorted(set(answers) - set(arg_specs))
    if unknown:
        accepted = ", ".join(sorted(arg_specs)) or "（这个方法不接受）"
        raise bad(f"{name} does not take {', '.join(unknown)}; it takes: {accepted}")

    # The engine checks declared measurements itself, with the same skillkit the scripts use.
    checked: Optional[Dict[str, Any]] = None
    rows_for_script = measurements
    if measurements and meas_specs:
        collected = kit.collect_measurements(measurements, manifest)
        if collected.problems:
            return {**head, "status": "input_problem", "checked_by": "engine",
                    "problems": [p.as_dict() for p in collected.problems], "inputs_used": measurements,
                    "message_zh": "输入没有通过检查，这次没有计算。改正后重新运行；缺的项不要用别的数代替。"}
        units = {spec["key"]: spec.get("unit", "") for spec in meas_specs}
        rows_for_script = [{"item": key, "value": repr(float(v)), "unit": "" if units[key] in (None, "1") else units[key]}
                           for key, v in collected.values.items()]
        unmatched = set(collected.unmatched)
        rows_for_script += [r for r in measurements if r["item"] in unmatched]
        checked = {"matched": {k: round(v, 6) for k, v in collected.values.items()},
                   "unmatched": sorted(unmatched)}
    elif measurements and not entry.get("measurements_flag"):
        raise bad(f"{name} does not take a measurements table")

    if out_dir:
        try:
            out = Path(out_dir).expanduser().resolve()
        except (RuntimeError, OSError) as exc:
            raise bad(f"--out {out_dir!r}: {exc}")
        if out.exists() and (not out.is_dir() or any(out.iterdir())):
            raise bad(f"--out {out} must be a new or empty directory")
    tmp = Path(tempfile.mkdtemp(prefix="longevity-run-"))
    try:
        if not out_dir:
            out = tmp / "out"
        cmd: List[str] = [sys.executable, str(script)]
        if rows_for_script:
            csv_path = tmp / "measurements.csv"
            _write_rows(csv_path, entry.get("measurements_header") or ["item", "value", "unit"], rows_for_script)
            cmd += [entry["measurements_flag"], str(csv_path)]
        elif mpath is not None:
            cmd += [entry["measurements_flag"], str(mpath)]
        if payload.get("age") is not None and entry.get("age_flag"):
            age = payload["age"]
            if isinstance(age, bool) or not isinstance(age, (int, float, str)):
                raise bad(f"age {age!r} is not a number")
            try:
                age = float(age)
            except ValueError:
                raise bad(f"age {payload['age']!r} is not a number")
            if not math.isfinite(age):
                raise bad("age must be a finite number")
            cmd += [f"{entry['age_flag']}={age:g}"]
        if payload.get("sex") is not None and entry.get("sex_flag"):
            sex = SEX.get(str(payload["sex"]).strip().lower())
            if not sex:
                raise bad(f"sex {payload['sex']!r}: use male or female (男/女)")
            cmd += [entry["sex_flag"], sex]
        script_text = script.read_text(encoding="utf-8", errors="replace")
        for key, value in answers.items():
            cmd += _argument_tokens(arg_specs[key], argument_kind(arg_specs[key], script_text), value)
        if meds and entry.get("medications_flag"):
            med_file = tmp / "medications.txt"
            med_file.write_text("\n".join(meds) + "\n", encoding="utf-8")
            cmd += [entry["medications_flag"], str(med_file)]
        if targets and entry.get("targets_flag"):
            tfile = tmp / "targets.csv"
            _write_rows(tfile, entry.get("measurements_header") or ["item", "value", "unit"], targets)
            cmd += [entry["targets_flag"], str(tfile)]
        if payload.get("include_cpic_text") is True and entry.get("cpic_text_flag"):
            cmd += [entry["cpic_text_flag"]]
        cmd += [entry.get("out_flag", "--out"), str(out)]

        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
        try:
            done = subprocess.run(cmd, cwd=str(tmp), capture_output=True, text=True, timeout=timeout, env=env,
                                  stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired:
            return {**head, "status": "error", "code": "timeout", "message_zh": f"运行超过 {timeout} 秒，已停止。"}
        result = _collect(lib, name, manifest, head, done, out, measurements, include_report,
                          drafted=(status == "draft"), kept=out_dir)
        if checked:
            result["checked_by_engine"] = checked
        return _plain(result)
    finally:
        # Inputs live in tmp; with out_dir the outputs live elsewhere and are kept.
        shutil.rmtree(tmp, ignore_errors=True)


def _read(path: Path) -> Optional[Any]:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _collect(lib: Library, name: str, manifest: Dict[str, Any], head: Dict[str, Any],
             done: subprocess.CompletedProcess, out: Path, measurements: List[Dict[str, Any]],
             include_report: bool, drafted: bool, kept: Optional[str]) -> Dict[str, Any]:
    result = _read(out / "result.json")
    problems = _read(out / "problems.json")
    base: Dict[str, Any] = dict(head)
    if drafted:
        base["label_zh"] += "：结果仍在验证，不能当作已核对的读数"
    if measurements:
        base["inputs_used"] = measurements
    report = out / "report.md"
    report_only = not (manifest.get("entry") or {}).get("result_json")
    if problems and problems.get("problems"):
        base.update(status="input_problem", problems=problems["problems"],
                    message_zh="输入没有通过检查，这次没有计算。改正后重新运行；缺的项不要用别的数代替。")
        arg_keys = {i["key"] for i in (manifest.get("inputs") or []) if i.get("from") == "argument"}
        asked = [p.get("key") for p in problems["problems"] if p.get("key") in arg_keys]
        if asked:  # the script's own message names its flag (--urban yes); through this engine it is an answer
            base["hint_zh"] = ("这些项在 longevity 里用 --answer 键=值 传入（MCP 里放在 answers），例如 "
                               + "、".join(f"--answer {k}=yes" for k in asked[:3]) + "。")
    elif report_only and report.is_file() and done.returncode in (0, 3):
        # Methods without result.json put everything in the report; exit 3 means the input was refused.
        include_report = True
        if done.returncode == 0:
            base.update(status="ok", outputs={}, note_zh="这个方法只输出报告（report_md），没有结构化数值。")
        else:
            base.update(status="input_problem", problems=[], message_zh="输入没有通过检查，这次没有计算。原因见 report_md。")
    elif result is not None and done.returncode == 0:
        outputs = result.get("outputs", {})
        if outputs and all((v or {}).get("value") is None for v in outputs.values()):
            include_report = True
            base.update(status="not_computed", outputs=outputs,
                        message_zh="脚本运行了，但一个读数也没有算出来（通常是缺了必需的输入）。原因见 report_md。")
        else:
            base.update(status="ok", outputs=outputs)
        for extra, key in (("levers.json", "levers"), ("cpic_recommendations.json", "cpic_recommendations")):
            data = _read(out / extra)
            if data is not None:
                base[key] = data
    else:
        err = (done.stderr or "").strip()
        missing = re.search(r"ModuleNotFoundError: No module named '([^']+)'", err)
        if missing:
            req = lib.skill_dir(name) / "scripts" / "requirements.txt"
            hint = f"；需要的包见 {req.relative_to(lib.root)}" if req.is_file() else ""
            base.update(status="missing_dependency", module=missing.group(1),
                        message_zh=f"这个方法需要 Python 包 {missing.group(1)}，当前环境没有安装{hint}。")
        else:
            last = next((line.strip() for line in reversed(err.splitlines()) if line.strip()), "")
            base.update(status="error", exit_code=done.returncode, error_line=last[:300], stderr_tail=err[-1500:],
                        message_zh="脚本运行出错，没有得到结果。不要用别的方法或估算代替这个读数。")
    if include_report and report.is_file():
        base["report_md"] = report.read_text(encoding="utf-8")
    if kept:
        base["out_dir"] = str(out)
    return base
