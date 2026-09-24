#!/usr/bin/env python3
"""Run published aging clocks with pyaging on one person's feature matrix.

pyaging (Camillo, Bioinformatics 2024) holds the clock weights; this script
does not copy them. It checks the matrix, runs the named clocks, and writes a
report with every value and every warning pyaging printed. pyaging and pandas
are imported only when clocks run, so the checks and the report can be tested
without them.
"""

from __future__ import annotations

import argparse
import contextlib
import csv
import io
import json
import math
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import skillkit

TITLE = "pyaging 衰老时钟"
BOUNDARY = (
    "时钟读数是模型估计，不是诊断，也不是开始或停止任何药物的理由。"
    "缺失探针被补值时读数会变，报告照录 pyaging 的提示。DunedinPACE 是速度，不是年龄。"
)
DEFAULT_CLOCKS = ("horvath2013",)
MAX_SAMPLES = 20
MAX_BYTES = 200_000_000
EXIT_MISSING_RUNTIME = 4
SPEED_CLOCKS = {"dunedinpace"}


def manifest() -> dict:
    return skillkit.load_manifest(__file__)


def card_lines() -> List[str]:
    tool = manifest().get("tool", {})
    lines = ["## 工具卡片", "", "**pyaging**", ""]
    lines.append(f"版本 {tool.get('version', '')}（{tool.get('commit', '')}）。Camillo。Bioinformatics，2024。doi:{tool.get('doi', '')}。")
    lines += ["", f"[代码]({tool.get('upstream', '')}) · [DOI](https://doi.org/{tool.get('doi', '')})", ""]
    lines.append("pyaging 把已发表的甲基化、转录组和血液化学时钟放在同一个框架里运行。个人报告只照录它对你交来的矩阵算出的数，不重新训练任何时钟。")
    return lines


def read_header(path: Path) -> Tuple[List[str], int]:
    """Column names and the number of data rows, without loading the whole file into pandas."""
    with path.open(encoding="utf-8-sig", errors="replace", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader, [])
        rows = sum(1 for row in reader if any(cell.strip() for cell in row))
    return header, rows


def beta_problems(path: Path, metadata: List[str]) -> List[skillkit.Problem]:
    """Methylation beta values must be on the 0–1 scale."""
    outside = 0
    total = 0
    with path.open(encoding="utf-8-sig", errors="replace", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            for key, value in list(row.items())[1:]:
                if key in metadata or value in ("", None):
                    continue
                try:
                    number = float(value)
                except ValueError:
                    continue
                total += 1
                if not (0.0 <= number <= 1.0):
                    outside += 1
    if total and outside / total > 0.01:
        return [skillkit.Problem(
            "matrix", "甲基化矩阵", "range",
            f"矩阵里有 {outside} 个值不在 0 到 1 之间。甲基化时钟要 β 值；百分比请除以 100，M 值请先换成 β 值。",
        )]
    return []


def check_matrix(path: Optional[Path], metadata: List[str], data_type: str) -> List[skillkit.Problem]:
    if path is None or not path.exists():
        return [skillkit.Problem("matrix", "特征矩阵", "missing", "缺少特征矩阵文件。")]
    if path.suffix.lower() in {".idat", ".pdf", ".xlsx"}:
        return [skillkit.Problem("matrix", "特征矩阵", "parse", f"{path.name} 不是 CSV。IDAT 要先预处理成 β 值矩阵，PDF 和表格请导出成 CSV。")]
    if path.stat().st_size > MAX_BYTES:
        return [skillkit.Problem("matrix", "特征矩阵", "parse", "矩阵文件超过 200 MB。只保留要跑的时钟用到的列。")]
    header, rows = read_header(path)
    if len(header) < 2 or rows == 0:
        return [skillkit.Problem("matrix", "特征矩阵", "parse", "矩阵需要表头，第一列是样本名，其余列是特征，至少一行数据。")]
    if rows > MAX_SAMPLES:
        return [skillkit.Problem("matrix", "特征矩阵", "parse", f"矩阵有 {rows} 个样本。个人读出最多 {MAX_SAMPLES} 个。")]
    return beta_problems(path, metadata) if data_type == "methylation" else []


def predict(path: Path, clocks: List[str], metadata: List[str]) -> Tuple[Dict[str, Dict[str, float]], List[str]]:
    """Run pyaging. Returns {sample: {clock: value}} and the lines pyaging printed."""
    import pandas as pd  # noqa: PLC0415 - optional dependency
    import pyaging as pya  # noqa: PLC0415 - optional dependency

    frame = pd.read_csv(path, index_col=0)
    captured = io.StringIO()
    with contextlib.redirect_stdout(captured), contextlib.redirect_stderr(captured):
        adata = pya.pp.df_to_adata(frame, metadata_cols=[col for col in metadata if col in frame.columns])
        pya.pred.predict_age(adata, clocks)
    values: Dict[str, Dict[str, float]] = {}
    for sample, row in adata.obs.iterrows():
        values[str(sample)] = {clock: float(row[clock]) for clock in clocks if clock in row and _finite(row[clock])}
    warnings = [line.strip() for line in captured.getvalue().splitlines() if _is_warning(line)]
    return values, warnings


def _finite(value) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _is_warning(line: str) -> bool:
    lower = line.lower()
    return any(word in lower for word in ("missing", "imput", "warning", "not found", "absent"))


def render(values: Dict[str, Dict[str, float]], clocks: List[str], warnings: List[str], age: Optional[float]) -> str:
    lines = [f"# {TITLE}", "", *card_lines(), "", "## 时钟读数", ""]
    for sample, by_clock in values.items():
        lines.append(f"### 样本 {sample}")
        for clock in clocks:
            if clock not in by_clock:
                lines.append(f"- {clock}：没有读数。")
                continue
            value = by_clock[clock]
            if clock in SPEED_CLOCKS:
                lines.append(f"- {clock}：{value:.3f}（每过一年的衰老速度，不是年龄）")
            else:
                gap = f"，减实足年龄 {value - age:+.1f} 岁" if age is not None else ""
                lines.append(f"- {clock}：{value:.1f} 岁{gap}")
        lines.append("")
    lines += ["## pyaging 的提示", ""]
    lines += [f"- {line}" for line in warnings] if warnings else ["pyaging 没有打印缺失或补值提示。"]
    lines += ["", f"边界: {BOUNDARY}"]
    return "\n".join(lines) + "\n"


def outputs_for(values: Dict[str, Dict[str, float]]) -> Dict[str, Optional[float]]:
    declared = [item["key"] for item in manifest().get("outputs", [])]
    first = next(iter(values.values()), {})
    result: Dict[str, Optional[float]] = {}
    for key in declared:
        clock = key[len("dnam_"):] if key.startswith("dnam_") else key
        result[key] = first.get(clock)
    return result


def run(matrix: Optional[Path], clocks: List[str], metadata: List[str], data_type: str, age: Optional[float], out_dir: Path) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    problems = check_matrix(matrix, metadata, data_type)
    problems += [item for item in skillkit.check_scalar(manifest(), "age", age) if item.kind != "missing"]
    if problems:
        path = skillkit.write_problems(out_dir, problems, TITLE, BOUNDARY)
        skillkit.write_result(out_dir, manifest(), {key: None for key in outputs_for({})})
        sys.stdout.write(str(path) + "\n")
        return skillkit.EXIT_INPUT_PROBLEM
    try:
        values, warnings = predict(matrix, clocks, metadata)
    except ImportError as error:
        problem = skillkit.Problem("runtime", "pyaging", "runtime", f"这台机器上的 Python 没有安装 pyaging 或 pandas（{error}）。请用装了 pyaging 的解释器运行，不要改用别的年龄估计。")
        skillkit.write_problems(out_dir, [problem], TITLE, BOUNDARY)
        return EXIT_MISSING_RUNTIME
    report = out_dir / "report.md"
    report.write_text(render(values, clocks, warnings, age), encoding="utf-8")
    skillkit.write_result(out_dir, manifest(), outputs_for(values))
    sys.stdout.write(str(report) + "\n")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run pyaging clocks on one feature matrix")
    parser.add_argument("--matrix", type=Path)
    parser.add_argument("--clocks", default=",".join(DEFAULT_CLOCKS), help="comma-separated pyaging clock names")
    parser.add_argument("--metadata-cols", default="age", help="comma-separated covariate columns that are not features")
    parser.add_argument("--data-type", choices=["methylation", "other"], default="methylation")
    parser.add_argument("--age", type=float)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    clocks = [item.strip().lower() for item in args.clocks.split(",") if item.strip()]
    metadata = [item.strip() for item in args.metadata_cols.split(",") if item.strip()]
    return run(args.matrix, clocks, metadata, args.data_type, args.age, args.out)


if __name__ == "__main__":
    raise SystemExit(main())
