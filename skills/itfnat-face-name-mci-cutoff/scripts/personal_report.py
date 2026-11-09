#!/usr/bin/env python3
"""ItFNAT delayed free recall and MoCA adjusted scores against the MCI cut-offs of
Scaramuzzi et al. (GeroScience 2026, Table 4), with the likelihood ratio of the side
of the cut-off the person falls on.

Constants and sources are in presets.py; the contract is in references/contract.md.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import BOUNDARY, COHORT, DELONG, DFR_CUTOFF, MOCA_CUTOFF, TABLE4

TITLE = "人脸-姓名联想记忆（ItFNAT 延迟自由回忆）与 MoCA 的轻度认知障碍切点"

TESTS = {
    "dfr": {"key": "itfnat_dfr_adjusted_score", "cutoff": DFR_CUTOFF, "name_zh": "ItFNAT 延迟自由回忆校正分"},
    "moca": {"key": "moca_adjusted_score", "cutoff": MOCA_CUTOFF, "name_zh": "MoCA 校正总分"},
}

# Unmatched row names that look like the raw (unadjusted) version of an input.
_RAW_HINTS = {
    "moca": ("moca", "蒙特利尔", "montreal"),
    "dfr": ("dfr", "delayed free", "延迟自由回忆"),
}


def positive_likelihood_ratio(sens_pct: float, spec_pct: float) -> float:
    """PLR = sensitivity / (1 - specificity)."""
    return (sens_pct / 100) / (1 - spec_pct / 100)


def negative_likelihood_ratio(sens_pct: float, spec_pct: float) -> float:
    """NLR = (1 - sensitivity) / specificity."""
    return (1 - sens_pct / 100) / (spec_pct / 100)


def classify(test: str, score: float) -> dict:
    """Table 4: positive (MCI-like) when the adjusted score is <= the cut-off."""
    row = TABLE4[test]
    positive = score <= TESTS[test]["cutoff"]
    lr = positive_likelihood_ratio(row["sens"], row["spec"]) if positive else negative_likelihood_ratio(row["sens"], row["spec"])
    return {"score": score, "positive": positive, "lr": lr}


def raw_score_problems(unmatched: list) -> list:
    problems = []
    for test, hints in _RAW_HINTS.items():
        for name in unmatched:
            folded = name.strip().lower()
            if any(h in folded for h in hints):
                label = TESTS[test]["name_zh"]
                problems.append(skillkit.Problem(
                    TESTS[test]["key"], label, "missing",
                    f"“{name}”看起来是没有校正的分数。论文的切点只用于按意大利常模校正后的{label}"
                    f"（ItFNAT 按年龄校正，MoCA 按年龄和受教育年限校正），请在名称里写明“校正分”，"
                    "或者请施测的神经心理师给出校正分；原始分或中文版 MoCA 分不能直接套这个切点。"))
                break
    return problems


def _result_word(test: str, res: dict) -> str:
    cut = TESTS[test]["cutoff"]
    return f"≤ {cut:g}（切点以下，提示轻度认知障碍样）" if res["positive"] else f"> {cut:g}（切点以上）"


def _category(test: str, res: dict) -> str:
    cut = TESTS[test]["cutoff"]
    return f"≤{cut:g} 阳性" if res["positive"] else f">{cut:g} 阴性"


def _with_paper_card(text: str) -> str:
    rows = text.splitlines()
    return "\n".join([rows[0], "", *paper_card_lines(), "", *rows[1:]]) + "\n"


def report_lines(results: dict, unused: list) -> list:
    lines = [f"# {TITLE}", "", "## 输入", ""]
    for test, res in results.items():
        lines.append(f"- {TESTS[test]['name_zh']}：{res['score']:g}")
    if unused:
        lines.append(f"- 没有用到的行：{'、'.join(unused)}")
    lines += ["", "## 结果", ""]
    for test, res in results.items():
        row = TABLE4[test]
        side = "阳性似然比" if res["positive"] else "阴性似然比"
        lines.append(
            f"- {TESTS[test]['name_zh']} {res['score']:g}：{_result_word(test, res)}。"
            f"按论文表 4 的灵敏度 {row['sens']:.2f}% 和特异度 {row['spec']:.2f}%，这一侧的{side}是 {res['lr']:.3f}。")
    lines += ["", "## 这意味着什么", ""]
    for test, res in results.items():
        if res["positive"]:
            lines.append(
                f"- {TESTS[test]['name_zh']}落在切点以下。似然比 {res['lr']:.2f} 的意思是：在论文样本里，"
                f"这样的分数在轻度认知障碍组出现的比例约是认知健康组的 {res['lr']:.1f} 倍。它提高了需要进一步评估的理由，但不是诊断。")
        else:
            lines.append(
                f"- {TESTS[test]['name_zh']}在切点以上。似然比 {res['lr']:.2f} 的意思是：在论文样本里，"
                f"这样的分数在轻度认知障碍组出现的比例约是认知健康组的 {res['lr']:.2f} 倍，偏向认知健康，但不能排除。")
    dfr, moca = TABLE4["dfr"], TABLE4["moca"]
    lines.append(
        f"- 两个切点在论文里是分开评估的：延迟自由回忆特异度较高（{dfr['spec']:.2f}%），MoCA 灵敏度较高（{moca['sens']:.2f}%）。"
        "论文没有评估两项合用，所以这里不把两个似然比相乘，也不给合并结论。")
    if len(results) == 2 and results["dfr"]["positive"] != results["moca"]["positive"]:
        lines.append("- 两项结果不一致时，论文的说法是两者提供互补信息；更需要由专业人员结合完整评估来判断。")
    lines += ["", "## 说明", "",
              f"- 论文人群：{COHORT['region_zh']} {COHORT['n']} 名社区成年志愿者（{COHORT['n_ch']} 名认知健康、{COHORT['n_mci']} 名轻度认知障碍），"
              f"平均 {COHORT['mean_age']} 岁，平均受教育 {COHORT['mean_education']} 年；分组由神经心理师按 DSM-5 轻度神经认知障碍和 Petersen 标准做出，没有影像或生物标志物。",
              f"- 表 4：延迟自由回忆 AUC {dfr['auc']:.3f}（{dfr['auc_ci'][0]:.3f}–{dfr['auc_ci'][1]:.3f}），MoCA AUC {moca['auc']:.3f}"
              f"（{moca['auc_ci'][0]:.3f}–{moca['auc_ci'][1]:.3f}），两者差 {DELONG['delta_auc']:.3f}，DeLong 检验 p = {DELONG['p']:.3f}，没有差别。这些是队列的数，不是你的结果。",
              "- 切点用的是校正分：ItFNAT 延迟自由回忆按 ItFNAT 意大利常模做年龄校正，MoCA 按意大利 MoCA 8.1 常模做年龄和教育校正。校正公式在常模论文里，本技能不从原始分换算。",
              "- 不算患病概率：阳性、阴性预测值取决于样本里病例的比例，换一个人群就变；似然比不随比例变，所以这里只给似然比。"]
    lines += ["", f"边界: {BOUNDARY}"]
    return lines


def write_report(out_dir: Path, measurements: Path | None) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    stale = out_dir / "problems.json"
    if stale.exists():
        stale.unlink()
    manifest = skillkit.load_manifest(__file__)
    collected = skillkit.collect_file(measurements, manifest)
    problems = list(collected.problems)
    problems += raw_score_problems(collected.unmatched)
    if not problems and not collected.values:
        problems.append(skillkit.Problem(
            "itfnat_dfr_adjusted_score", "ItFNAT 延迟自由回忆校正分", "missing",
            "缺少 ItFNAT 延迟自由回忆校正分和 MoCA 校正总分，至少要有一项（按意大利常模校正后的分数）。"))
    empty = {spec["key"]: None for spec in manifest["outputs"]}
    if problems:
        path = skillkit.write_problems(out_dir, problems, TITLE, BOUNDARY)
        path.write_text(_with_paper_card(path.read_text(encoding="utf-8")), encoding="utf-8")
        skillkit.write_result(out_dir, manifest, empty)
        return path
    results = {test: classify(test, collected.values[spec["key"]])
               for test, spec in TESTS.items() if spec["key"] in collected.values}
    path = out_dir / "report.md"
    path.write_text(_with_paper_card("\n".join(report_lines(results, list(collected.unmatched))) + "\n"), encoding="utf-8")
    outputs = dict(empty)
    if "dfr" in results:
        outputs["dfr_cutoff_result"] = _category("dfr", results["dfr"])
        outputs["dfr_likelihood_ratio"] = round(results["dfr"]["lr"], 3)
    if "moca" in results:
        outputs["moca_cutoff_result"] = _category("moca", results["moca"])
        outputs["moca_likelihood_ratio"] = round(results["moca"]["lr"], 3)
    skillkit.write_result(out_dir, manifest, outputs)
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path,
                        help="CSV item,value,unit：ItFNAT 延迟自由回忆校正分、MoCA 校正总分（至少一项，unit 写 score 或留空）")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    path = write_report(args.out, args.measurements)
    sys.stdout.write(str(path) + "\n")
    return skillkit.EXIT_INPUT_PROBLEM if (args.out / "problems.json").exists() else 0


if __name__ == "__main__":
    raise SystemExit(main())
