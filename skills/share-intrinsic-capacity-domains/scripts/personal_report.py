#!/usr/bin/env python3
"""Score complete SHARE IC domains and optionally compare two observations."""
from __future__ import annotations

import argparse
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (INPUTS, RAW_MAX, STANDARD_MAX, DOMAIN_ZH, GROUP_KEYS,
                     FLUENCY_BINS, FLUENCY_TOP_SCORE, RECALL_BINS,
                     RATING_SCORES, BINARY_SCORES, BINARY_KEYS, RATING_KEYS, BOUNDARY)


def item_score(key: str, value: float) -> int:
    """Table 1, applied only to checked, integer inputs."""
    if key not in INPUTS or not float(value).is_integer():
        raise ValueError('Unknown item or non-integer observation')
    low, high = INPUTS[key]['range']
    if not low <= value <= high:
        raise ValueError('Observation out of range')
    if key in BINARY_KEYS:
        return BINARY_SCORES[value]
    if key in RATING_KEYS:
        return RATING_SCORES[value]
    if key == 'animal_fluency_count':
        return next((score for upper, score in FLUENCY_BINS if value <= upper), FLUENCY_TOP_SCORE)
    if key == 'delayed_recall_count':
        return next(score for upper, score in RECALL_BINS if value <= upper)
    return int(value)  # orientation and subtraction: one point per correct answer


def assess(values: dict[str, float]) -> dict[str, float]:
    outputs = {}
    for domain, keys in GROUP_KEYS.items():
        if all(key in values for key in keys):
            for key in keys:
                outputs[f'{key}_points'] = item_score(key, values[key])
            raw = sum(outputs[f'{key}_points'] for key in keys)
            outputs[f'{domain}_raw'] = raw
            outputs[f'{domain}_score'] = raw / RAW_MAX[domain] * STANDARD_MAX
    return outputs


def read_checked(path, manifest, *, expected_domains=None):
    try:
        collected = skillkit.collect_file(path, manifest)
    except (OSError, ValueError) as exc:
        return {}, [skillkit.Problem('measurements', '测量文件', 'file', f'无法读取测量文件：{exc}')]
    problems = list(collected.problems)
    for name in collected.unmatched:
        problems.append(skillkit.Problem(name, name, 'unknown', f'未识别项目「{name}」。本技能只接受已列出的三个分域；请核对名称。'))
    touched = set(collected.values) | {p.key for p in problems}
    domains = {d for d, keys in GROUP_KEYS.items() if touched.intersection(keys)}
    if expected_domains is not None:
        domains |= set(expected_domains)
    if not domains:
        problems.append(skillkit.Problem('domain', '完整分域', 'missing', '至少提供一个完整分域，例如认知的时间定向、动物命名、连续减七和延迟回忆四项。'))
    for domain in domains:
        for key in GROUP_KEYS[domain]:
            spec = INPUTS[key]
            if key not in collected.values and not any(p.key == key for p in problems):
                problems.append(skillkit.Problem(key, spec['label'], 'missing', f'{DOMAIN_ZH[domain]}分域缺少{spec["label"]}。{spec["note"]}'))
    for key, value in collected.values.items():
        if not value.is_integer():
            problems.append(skillkit.Problem(key, INPUTS[key]['label'], 'integer', f'{INPUTS[key]["label"]}必须是整数计数或编码，不接受小数。'))
    return collected.values, problems


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--measurements', type=Path)
    parser.add_argument('--baseline', type=Path, help='可选：上次测量，须覆盖本次全部分域；相同 CSV 格式')
    parser.add_argument('--age', help='可选：本次年龄，仅用于提示研究人群范围')
    parser.add_argument('--sex', help='可选：male/female/男/女，仅作背景，不改变计分')
    parser.add_argument('--out', type=Path, default=Path('out'))
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True, exist_ok=True)
    for filename in ('result.json', 'problems.json', 'report.md'):
        (args.out / filename).unlink(missing_ok=True)
    values, problems = read_checked(args.measurements, manifest)
    age = None
    if args.age is not None:
        try:
            age = skillkit.parse_number(args.age)
            problems += skillkit.check_scalar(manifest, 'age', age)
        except ValueError:
            problems.append(skillkit.Problem('age', '实足年龄', 'parse', '实足年龄需要有限数值，单位为岁。'))
    if args.sex is not None and args.sex.lower() not in ('male', 'female', '男', '女', 'm', 'f'):
        problems.append(skillkit.Problem('sex', '性别', 'category', '性别可填 male、female、男或女。此项不参与计算，也可以不填。'))
    baseline = {}
    if args.baseline is not None:
        expected = {d for d, keys in GROUP_KEYS.items() if set(keys).intersection(values)}
        baseline, baseline_problems = read_checked(args.baseline, manifest, expected_domains=expected)
        for problem in baseline_problems:
            problem.message_zh = '上次测量：' + problem.message_zh
        problems += baseline_problems
    outputs = {spec['key']: None for spec in manifest['outputs']}
    if problems:
        skillkit.write_problems(args.out, problems, 'SHARE 内在能力分域计分', BOUNDARY)
        text = (args.out / 'report.md').read_text(encoding='utf-8')
        (args.out / 'report.md').write_text('\n'.join(paper_card_lines()) + '\n\n' + text, encoding='utf-8')
        skillkit.write_result(args.out, manifest, outputs)
        return skillkit.EXIT_INPUT_PROBLEM
    current = assess(values)
    previous = assess(baseline) if args.baseline else {}
    outputs.update(current)
    lines = [*paper_card_lines(), '', '# 你的内在能力分域计分', '',
             '分数越高表示按本研究定义保留的能力越多；没有个人诊断切点或同龄人百分位。', '',
             '| 分域 | 原始分 | 标准化分（0–10） |', '|---|---:|---:|']
    for domain in GROUP_KEYS:
        score_key = f'{domain}_score'
        if score_key not in current:
            lines.append(f'| {DOMAIN_ZH[domain]} | 未提供 | 未计算 |')
            continue
        lines.append(f'| {DOMAIN_ZH[domain]} | {current[f"{domain}_raw"]:g}/{RAW_MAX[domain]} | {current[score_key]:.2f} |')
        if score_key in previous:
            outputs[f'{domain}_baseline_score'] = previous[score_key]
            outputs[f'{domain}_change'] = current[score_key] - previous[score_key]
    if previous:
        lines += ['', '## 两次测量对比', '', '差值为本次减上次；正值为上升，负值为下降。未按年折算，也不代表干预效果。', '',
                  '| 分域 | 上次 | 本次 | 差值 |', '|---|---:|---:|---:|']
        for domain in GROUP_KEYS:
            if outputs[f'{domain}_change'] is not None:
                lines.append(f'| {DOMAIN_ZH[domain]} | {outputs[f"{domain}_baseline_score"]:.2f} | {outputs[f"{domain}_score"]:.2f} | {outputs[f"{domain}_change"]:+.2f} |')
    lines += ['', '## 本次逐项核对', '', '| 项目 | 输入计数或编码 | 计分 |', '|---|---:|---:|']
    for key, value in values.items():
        lines.append(f'| {INPUTS[key]["label"]} | {value:g} | {current[f"{key}_points"]:g} |')
    lines += ['', '请核对测试方式：认知须为 SHARE 对应测验结果；感官须为原有自评编码。困难和辅助器具使用均以 1 表示有、0 表示无，不直接导入其他编码。',
              '', '未计算心理、活力分域和完整 IC 总分：CASP 队列分位切点未公布，BMI 恰好为 30 的活力计分未定义。三个分域不求和或扩展为总分。',
              '', '认知分数受测验语言、教育和重复练习影响。两次比较需要相同测验和编码；本研究未给出个人变化的临床意义阈值。',
              '', '感官计分包含眼镜和助听器使用情况；分值变化不表示停用辅助器具会改善健康。']
    if age is not None:
        lines += ['', f'本次年龄：{age:g} 岁。年龄不参与此计分。']
        if age < 50 or age > 95:
            lines.append('本次年龄超出研究基线实际年龄范围（50–95 岁），结果的外推适用性未验证。')
    if args.sex is not None:
        lines += ['', '性别作为背景记录，不参与这三个分域计分；本报告不套用人群性别平均差异。']
    lines += ['', f'边界: {BOUNDARY}', '']
    (args.out / 'report.md').write_text('\n'.join(lines), encoding='utf-8')
    skillkit.write_result(args.out, manifest, outputs)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
