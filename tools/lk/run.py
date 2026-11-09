"""Run one method through its skill.json `entry` contract and return one JSON result.

Rules every host gets, whatever agent calls this:
- tier C and methods whose inputs are not declared are refused;
- tier A methods still in validation (`draft`) are refused unless allow_draft;
- measurements that carry different sampling dates are refused unless allow_mixed_dates;
- unit conversion and range checks stay in each skill's own skillkit: a problem stops the run;
- every result carries the release, the method's tier, label and validation status, and the paper.
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
from pathlib import Path
from typing import Any, Dict, List, Optional

from .library import Library, LKError
from .methods import label_of, paper_of, status_of

DEFAULT_TIMEOUT = 180
YES = {"1", "yes", "y", "true", "是", "有"}
NO = {"0", "no", "n", "false", "否", "无", "没有"}
SEX = {"male": "male", "m": "male", "男": "male", "man": "male", "男性": "male",
       "female": "female", "f": "female", "女": "female", "woman": "female", "女性": "female"}
MEAS_RE = re.compile(r"^\s*(?P<item>[^=]+?)\s*=\s*(?P<value>[-+]?[0-9.]+(?:[eE][-+]?\d+)?)\s*(?P<unit>.*?)\s*$")


def parse_measurement(text: str) -> Dict[str, Any]:
    """`肌酐=78 umol/L` or `肌酐=78 umol/L @2026-10-01` -> {item, value, unit, date}."""
    date = None
    if "@" in text:
        text, date = text.rsplit("@", 1)
        date = date.strip() or None
    m = MEAS_RE.match(text)
    if not m:
        raise LKError(f"measurement {text!r} should look like 名称=数值 单位, e.g. 肌酐=78 umol/L", "bad_input", 2)
    row: Dict[str, Any] = {"item": m.group("item"), "value": m.group("value"), "unit": m.group("unit")}
    if date:
        row["date"] = date
    return row


def _bool_text(value: Any) -> Optional[str]:
    if isinstance(value, bool):
        return "yes" if value else "no"
    text = str(value).strip().lower()
    if text in YES:
        return "yes"
    if text in NO:
        return "no"
    return None


def _write_rows(path: Path, header: List[str], rows: List[Dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(header[:3] if len(header) >= 3 else [*header, "unit"][:3])
        for r in rows:
            w.writerow([r.get("item", ""), r.get("value", ""), r.get("unit", "") or ""])


def _clean_rows(rows: Any, what: str) -> List[Dict[str, Any]]:
    if rows is None:
        return []
    if not isinstance(rows, list):
        raise LKError(f"{what} must be a list of {{item, value, unit}}", "bad_input", 2)
    out = []
    for r in rows:
        if isinstance(r, str):
            r = parse_measurement(r)
        if not isinstance(r, dict) or not str(r.get("item", "")).strip():
            raise LKError(f"each {what} row needs an item name: {r!r}", "bad_input", 2)
        value = r.get("value")
        if value is None or (isinstance(value, float) and not math.isfinite(value)):
            raise LKError(f"{what} row {r.get('item')!r} has no finite value", "bad_input", 2)
        row = {"item": str(r["item"]).strip(), "value": str(value).strip(), "unit": str(r.get("unit") or "").strip()}
        for bad in (row["item"], row["unit"]):
            if "\n" in bad or "\r" in bad:
                raise LKError(f"{what} row {r!r} contains a line break", "bad_input", 2)
        if r.get("date"):
            row["date"] = str(r["date"]).strip()
        out.append(row)
    return out


def refusal(lib: Library, name: str, code: str, message_zh: str, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    out = {"schema": "longevity-run/1", "status": "refused", "method": name, "code": code, "message_zh": message_zh,
           **lib.stamp()}
    if extra:
        out.update(extra)
    return out


def run(lib: Library, name: str, payload: Dict[str, Any], allow_draft: bool = False, allow_mixed_dates: bool = False,
        include_report: bool = False, out_dir: Optional[str] = None, timeout: int = DEFAULT_TIMEOUT) -> Dict[str, Any]:
    s = lib.skill(name)
    status, why = status_of(s)
    head = {"tier": s.get("tier"), "label_zh": label_of(s), "validation_status": s.get("validation_status")}
    if status == "not_runnable":
        hint = "；问论文对某个对象说了什么，用 evidence" if s.get("tier") == "C" else ""
        return refusal(lib, name, "not_runnable", why + hint, head)
    if status == "draft" and not allow_draft:
        return refusal(lib, name, "draft", "这个方法还没核对上论文印出的示例（仍在验证），默认不运行。确需运行请加 --allow-draft，结果会标明仍在验证。", head)

    manifest = lib.manifest(name)
    entry = manifest.get("entry") or {}
    skill_dir = lib.skill_dir(name)
    script = (skill_dir / entry["script"]).resolve()
    if skill_dir.resolve() not in script.parents or not script.is_file():
        raise LKError(f"{name}: entry script {entry.get('script')!r} is missing", "library_broken")

    measurements = _clean_rows(payload.get("measurements"), "measurements")
    targets = _clean_rows(payload.get("targets"), "targets")
    dates = sorted({r["date"] for r in measurements if r.get("date")})
    if len(dates) > 1 and not allow_mixed_dates:
        return refusal(lib, name, "mixed_dates",
                       f"这些测量来自不同的采样日期（{'、'.join(dates)}）。论文的方法按同一次采样计算，混用会算错。"
                       "请只交同一次的结果；确需混用请加 --allow-mixed-dates。", {**head, "dates": dates})

    inputs = manifest.get("inputs") or []
    arg_specs = {i["key"]: i for i in inputs if i.get("from") == "argument"}
    answers = payload.get("arguments") or {}
    if not isinstance(answers, dict):
        raise LKError("arguments must be an object {key: value}", "bad_input", 2)
    unknown = sorted(set(answers) - set(arg_specs))
    if unknown:
        accepted = ", ".join(sorted(arg_specs)) or "（这个方法不接受）"
        raise LKError(f"{name} does not take {', '.join(unknown)}; it takes: {accepted}", "bad_input", 2)

    tmp = Path(tempfile.mkdtemp(prefix="longevity-run-"))
    out = Path(out_dir).expanduser().resolve() if out_dir else tmp / "out"
    cmd: List[str] = [sys.executable, str(script)]
    try:
        if measurements:
            if not entry.get("measurements_flag"):
                raise LKError(f"{name} does not take a measurements table", "bad_input", 2)
            mfile = tmp / "measurements.csv"
            _write_rows(mfile, entry.get("measurements_header") or ["item", "value", "unit"], measurements)
            cmd += [entry["measurements_flag"], str(mfile)]
        elif payload.get("measurements_file"):
            if not entry.get("measurements_flag"):
                raise LKError(f"{name} does not take a measurements file", "bad_input", 2)
            mpath = Path(str(payload["measurements_file"])).expanduser()
            if not mpath.is_file():
                raise LKError(f"measurements_file {mpath} not found", "bad_input", 2)
            cmd += [entry["measurements_flag"], str(mpath.resolve())]
        if payload.get("age") is not None and entry.get("age_flag"):
            try:
                age = float(payload["age"])
            except (TypeError, ValueError):
                raise LKError(f"age {payload['age']!r} is not a number", "bad_input", 2)
            cmd += [entry["age_flag"], f"{age:g}"]
        if payload.get("sex") and entry.get("sex_flag"):
            sex = SEX.get(str(payload["sex"]).strip().lower())
            if not sex:
                raise LKError(f"sex {payload['sex']!r}: use male or female (男/女)", "bad_input", 2)
            cmd += [entry["sex_flag"], sex]
        for key, value in answers.items():
            spec = arg_specs[key]
            flag = spec.get("flag") or "--" + key.replace("_", "-")
            if spec.get("unit"):
                text = str(value).strip()
            else:
                text = _bool_text(value)
                if text is None:
                    raise LKError(f"{key}: answer yes or no (是/否), got {value!r}", "bad_input", 2)
            cmd += [flag, text]
        meds = payload.get("medications") or []
        if meds and entry.get("medications_flag"):
            mfile = tmp / "medications.txt"
            mfile.write_text("\n".join(str(x).strip() for x in meds if str(x).strip()) + "\n", encoding="utf-8")
            cmd += [entry["medications_flag"], str(mfile)]
        if targets and entry.get("targets_flag"):
            tfile = tmp / "targets.csv"
            _write_rows(tfile, entry.get("measurements_header") or ["item", "value", "unit"], targets)
            cmd += [entry["targets_flag"], str(tfile)]
        if payload.get("include_cpic_text") and entry.get("cpic_text_flag"):
            cmd += [entry["cpic_text_flag"]]
        cmd += [entry.get("out_flag", "--out"), str(out)]

        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
        try:
            done = subprocess.run(cmd, cwd=str(tmp), capture_output=True, text=True, timeout=timeout, env=env)
        except subprocess.TimeoutExpired:
            return refusal(lib, name, "timeout", f"运行超过 {timeout} 秒，已停止。", head) | {"status": "error"}
        return _collect(lib, name, s, manifest, head, done, out, measurements, include_report,
                        drafted=(status == "draft"), kept=out_dir)
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


def _collect(lib: Library, name: str, s: Dict[str, Any], manifest: Dict[str, Any], head: Dict[str, Any],
             done: subprocess.CompletedProcess, out: Path, measurements: List[Dict[str, Any]],
             include_report: bool, drafted: bool, kept: Optional[str]) -> Dict[str, Any]:
    result = _read(out / "result.json")
    problems = _read(out / "problems.json")
    base: Dict[str, Any] = {"schema": "longevity-run/1", "method": name, **head, "paper": paper_of(manifest),
                            **lib.stamp()}
    if drafted:
        base["label_zh"] += "：结果仍在验证，不能当作已核对的读数"
    if measurements:
        base["inputs_used"] = measurements
    report = out / "report.md"
    report_only = not (manifest.get("entry") or {}).get("result_json")
    if problems and problems.get("problems"):
        base.update(status="input_problem", problems=problems["problems"],
                    message_zh="输入没有通过检查，这次没有计算。改正后重新运行；缺的项不要用别的数代替。")
    elif report_only and report.is_file() and done.returncode in (0, 3):
        # Methods without result.json put everything in the report; exit 3 means the input was refused.
        include_report = True
        if done.returncode == 0:
            base.update(status="ok", outputs={}, note_zh="这个方法只输出报告（report_md），没有结构化数值。")
        else:
            base.update(status="input_problem", problems=[],
                        message_zh="输入没有通过检查，这次没有计算。原因见 report_md。")
    elif result is not None and done.returncode == 0:
        base.update(status="ok", outputs=result.get("outputs", {}))
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
