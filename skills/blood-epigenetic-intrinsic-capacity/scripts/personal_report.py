#!/usr/bin/env python3
"""DNAm intrinsic capacity (Fuentealba et al., Nature Aging 2025).

DNAm IC = intercept + sum(coefficient x beta) over the 91 CpGs of
Supplementary Table 1 (elastic net on EPIC beta values). Rows are read through
skill.json by skillkit: a missing site, a beta outside 0 to 1, a unit that is
not a beta, or an unparsable row stops the computation (exit code 3).
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import BOUNDARY, CPG_COEF, IC_INTERCEPT

TITLE = "甲基化内在能力"


def dnam_ic(betas: dict[str, float]) -> float:
    """Supplementary Table 1: intercept plus each coefficient times the site's beta."""
    return IC_INTERCEPT + sum(coef * betas[site] for site, coef in CPG_COEF.items())


def load_meds(path: Path | None) -> list[str]:
    if path is None:
        return []
    names = []
    for line in path.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if text and not text.startswith("#"):
            names.append(text)
    return names


def read_rows(path: Path | None) -> list[dict[str, str]]:
    if path is None:
        return []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        sample = handle.read(4096)
        handle.seek(0)
        if not sample.strip():
            return []
        dialect = csv.Sniffer().sniff(sample, delimiters=",\t")
        return list(csv.DictReader(handle, dialect=dialect))


def lab_lines(path: Path | None) -> list[str]:
    rows = read_rows(path)
    lines = ["## 体检", ""]
    if not rows:
        lines.append("没有提供体检。体检不增删方法算出的名单。")
        return lines
    lines.append("下面照录体检数值。体检不增删方法算出的名单。")
    for row in rows:
        cells = {(k or "").strip(): (v or "").strip() for k, v in row.items()}
        item = cells.get("项目") or cells.get("item") or cells.get("name")
        value = cells.get("结果") or cells.get("value") or cells.get("result")
        unit = cells.get("单位") or cells.get("unit") or ""
        if item and value:
            lines.append(f"- {item} {value}{' ' + unit if unit else ''}")
    return lines


def medication_lines(meds: list[str]) -> list[str]:
    lines = ["## 你正在使用的药", ""]
    if not meds:
        lines.append("没有提供现用药。")
        return lines
    for name in meds:
        lines.append(f"- {name}：名单里没有这个名字。不能据此停。")
    return lines


def _with_paper_card(text: str) -> str:
    if "## 论文卡片" in text:
        return text
    rows = text.splitlines()
    if not rows or not rows[0].startswith("# "):
        return text
    rest = rows[1:]
    while rest and rest[0] == "":
        rest = rest[1:]
    out = "\n".join([rows[0], "", *paper_card_lines(), "", *rest])
    return out + "\n" if text.endswith("\n") else out


def render(score: float, meds: list[str], labs: Path | None) -> str:
    lines = [
        f"# {TITLE}",
        "",
        f"按补充表 1 的截距和 91 个位点系数，用你交的甲基化 β 值算出甲基化内在能力是 {score:.3f}。",
        "论文的内在能力在 0 到 1 之间，越高越好；建模只用了实测内在能力在 0.55 到 1 之间的人。",
        "",
        "## 方法算出的名单",
        "",
        f"- 甲基化内在能力 {score:.3f}（用上 {len(CPG_COEF)} 个位点）",
        "",
        *medication_lines(meds),
        "",
        *lab_lines(labs),
        "",
        f"边界: {BOUNDARY}",
    ]
    return "\n".join(lines) + "\n"


def report(out: Path, meds: Path | None, labs: Path | None, measurements: Path | None) -> Path:
    out.mkdir(parents=True, exist_ok=True)
    stale = out / "problems.json"
    if stale.exists():
        stale.unlink()
    manifest = skillkit.load_manifest(__file__)
    collected = skillkit.collect_file(measurements, manifest)
    if collected.problems:
        path = skillkit.write_problems(out, collected.problems, TITLE, BOUNDARY)
        path.write_text(_with_paper_card(path.read_text(encoding="utf-8")), encoding="utf-8")
        skillkit.write_result(out, manifest, {"dnam_ic": None})
        return path
    betas = {site: collected.values[site] for site in CPG_COEF}
    score = dnam_ic(betas)
    path = out / "report.md"
    path.write_text(_with_paper_card(render(score, load_meds(meds), labs)), encoding="utf-8")
    skillkit.write_result(out, manifest, {"dnam_ic": score})
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--measurements", type=Path)
    parser.add_argument("--medications", type=Path)
    parser.add_argument("--labs", type=Path)
    parser.add_argument("--age", type=float, help="accepted for the common interface; the model does not use it")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    path = report(args.out, args.medications, args.labs, args.measurements)
    print(path)
    if (args.out / "problems.json").exists():
        return skillkit.EXIT_INPUT_PROBLEM
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
