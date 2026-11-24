"""Count-based frailty index and historical gamma survival model."""

import argparse
import json
import math
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import COUNT_INPUTS, GAMMA_RATE, GAMMA_SHAPE, HORIZONS_MONTHS

TITLE = "缺陷累积虚弱指数"
BOUNDARY = (
    "本报告仅重算已评估缺陷的比例及原论文探索性生存模型，不能预测你的实际寿命、"
    "诊断虚弱或痴呆，也不能据此开始、停止或调整药物；目标情景不是干预效果或延寿承诺。"
)


def frailty_index(deficits, assessed):
    return deficits / assessed


def survival_probability(q, months):
    """Equation (4): regularized upper incomplete gamma Q(k, lambda*q*T).

    Compute its complement via the convergent lower-gamma series. On this
    skill's domain x <= 0.209*60, cancellation is negligible at report precision.
    Zero is defined mathematically here, but suppressed in personal outputs.
    """
    if not (0 <= q <= 1 and months in HORIZONS_MONTHS):
        raise ValueError("Unsupported index or horizon")
    x = GAMMA_RATE * q * months
    if x == 0:
        return 1.0
    term = total = 1.0 / GAMMA_SHAPE
    for n in range(1, 1000):
        term *= x / (GAMMA_SHAPE + n)
        total += term
        if abs(term) <= abs(total) * 1e-15:
            lower = total * math.exp(
                GAMMA_SHAPE * math.log(x) - x - math.lgamma(GAMMA_SHAPE)
            )
            return min(1.0, max(0.0, 1.0 - lower))
    raise ArithmeticError("Gamma series did not converge")


def calculate(values):
    q = frailty_index(values["deficits_count"], values["assessed_count"])
    result = {"frailty_index": q}
    for months in HORIZONS_MONTHS:
        result[f"historical_survival_{months}mo_pct"] = (
            100 * survival_probability(q, months) if q > 0 else None
        )
    return result


def count_problems(values):
    problems = []
    for key, _unit in COUNT_INPUTS:
        if key in values and not float(values[key]).is_integer():
            problems.append(skillkit.Problem(key, key, "integer", "缺陷数和已评估项数必须是整数，不接受加权分数。"))
    if all(key in values for key, _ in COUNT_INPUTS):
        if values["deficits_count"] > values["assessed_count"]:
            problems.append(skillkit.Problem("deficits_count", "缺陷数", "inconsistent", "缺陷数不能大于已评估项数。"))
    return problems


def read_counts(path, manifest, partial=False):
    try:
        collected = skillkit.collect_file(path, manifest)
    except (OSError, ValueError, TypeError) as exc:
        return {}, [skillkit.Problem("measurements", "输入文件", "file", f"无法读取输入表：{exc}")]
    problems = [p for p in collected.problems if not (partial and p.kind == "missing")]
    if collected.unmatched:
        problems.append(skillkit.Problem("measurements", "输入名称", "unknown", "无法识别项目：" + "、".join(collected.unmatched)))
    problems += count_problems(collected.values)
    if partial and not collected.values and not problems:
        problems.append(skillkit.Problem("targets", "目标", "missing", "目标表至少需要一项缺陷计数。"))
    return collected.values, problems


def levers(values, targets):
    current = calculate(values)
    d, m = values["deficits_count"], values["assessed_count"]
    sensitivity = []
    # Analytic derivatives of q; denominator sensitivity is informational only.
    for key, slope in (("deficits_count", 1 / m), ("assessed_count", -d / m**2)):
        sensitivity.append({"key": key, "unit": "1", "value": values[key],
                            "frailty_index_per_unit": slope,
                            "target_allowed": key == "deficits_count"})
    out = {"schema": "longevity-levers/1", "model": "deficit-accumulation-frailty-index",
           "model_zh": TITLE, "current": current, "sensitivity": sensitivity, "levers": [],
           "note_zh": "仅比较同一组已评估项目的假设计数；改变分母不是健康改善。缺陷并非都可逆，模型差值不代表治疗获益。"}
    if targets:
        moved = calculate({**values, **targets})
        delta = {f"{key}_delta": moved[key] - current[key]
                 if moved[key] is not None and current[key] is not None else None
                 for key in current}
        for key, target in targets.items():
            if key == "deficits_count":
                out["levers"].append({"key": key, "unit": "1", "from": values[key],
                                      "to": target, **delta})
        out["targets"] = {"values": targets, **moved, **delta}
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--measurements", type=Path)
    parser.add_argument("--age", help="实足年龄（岁）；研究范围为65–106岁")
    parser.add_argument("--sex", help="可选背景信息，不进入公式")
    parser.add_argument("--targets", type=Path)
    parser.add_argument("--out", type=Path, default=Path("out"))
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    for name in ("problems.json", "result.json", "levers.json", "report.md"):
        (out / name).unlink(missing_ok=True)
    values, problems = read_counts(args.measurements, manifest)
    try:
        age = float(args.age) if args.age is not None else None
        problems += skillkit.check_scalar(manifest, "age", age)
    except ValueError:
        age = None
        problems.append(skillkit.Problem("age", "实足年龄", "parse", "实足年龄需要填写数字（岁）。"))
    targets = {}
    if args.targets is not None:
        targets, more = read_counts(args.targets, manifest, partial=True)
        problems += more
        if "assessed_count" in targets and targets["assessed_count"] != values.get("assessed_count"):
            problems.append(skillkit.Problem("assessed_count", "已评估项数", "target", "目标情景必须保持同一组项目和分母，不能通过改变已评估项数制造改善。"))
        problems += count_problems({**values, **targets})
    heading = [f"# {TITLE}", "", *paper_card_lines(), ""]
    if problems:
        path = skillkit.write_problems(out, problems, TITLE, BOUNDARY)
        body = path.read_text(encoding="utf-8").split("\n", 2)[2]
        path.write_text("\n".join(heading) + "\n" + body, encoding="utf-8")
        skillkit.write_result(out, manifest, {x["key"]: None for x in manifest["outputs"]})
        return skillkit.EXIT_INPUT_PROBLEM
    result = calculate(values)
    lines = heading + ["## 你的结果", "",
        f"实足年龄：{age:g} 岁（仅用于核对适用范围，不进入公式）。",
        f"已评估 {values['assessed_count']:g} 项，存在缺陷 {values['deficits_count']:g} 项；虚弱指数 q = {result['frailty_index']:.4f}。",
        "未评估项目不计入分母，也不当作正常；分子与分母必须来自同一次、同一组二元项目评估。",
        "指数是缺陷所占比例，不是年龄、衰老速度或诊断分档。项目少、漏评有偏或项目集合改变会影响解释。", "",
        "## 原论文生存模型", "",
        "以下是历史研究公式的探索性输出，没有在你的所在地或当代人群校准；原文用记录了死亡时间的子样本拟合，未交代完整的删失处理，不能当作你的临床生存概率。"]
    if result["frailty_index"] == 0:
        lines += ["本次未记录缺陷。公式在 q=0 时退化为任意所列时间均生存，因此不输出生存概率；这不代表没有健康风险。"]
    else:
        for months in HORIZONS_MONTHS:
            lines += [f"{months} 个月：模型生存概率 {result[f'historical_survival_{months}mo_pct']:.1f}%。"]
    if targets:
        lines += ["", "目标情景已写入 levers.json；只是同一评估集合下的数学变化，不能解释为延寿效果。"]
    lines += ["", f"边界：{BOUNDARY}"]
    (out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    skillkit.write_result(out, manifest, result)
    (out / "levers.json").write_text(json.dumps(levers(values, targets), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
