"""Offline, standard-library-only individual Table 4 comparison."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import AGE_BANDS, BOUNDARY, METRICS, TABLE4, TITLE, YARD_TO_M


def evaluate(age, sex, values):
    if not math.isfinite(age) or int(age) != age or not 60 <= age <= 94:
        raise ValueError('年龄须为 60–94 周岁')
    if sex not in TABLE4:
        raise ValueError('论文只提供 male/female 两类标准')
    index = (int(age) - 60) // 5
    lo, hi = AGE_BANDS[index]
    result = {'age_band': f'{lo}–{hi}'}
    for metric in METRICS:
        key, prefix = metric['key'], metric['output']
        cutoff = TABLE4[sex][key][index]
        if key == 'walk_6min_m':
            cutoff *= YARD_TO_M
        result[prefix + '_cutoff'] = cutoff
        value = values.get(key)
        margin = None if value is None else metric['direction'] * (value - cutoff)
        # Only numerical representation tolerance, not a clinical buffer.
        if margin is not None and math.isclose(margin, 0, abs_tol=1e-9):
            margin = 0.0
        result[prefix + '_value'] = value
        result[prefix + '_margin'] = margin
        result[prefix + '_status'] = None if margin is None else (
            'meets_standard' if margin >= 0 else 'below_standard')
    return result


def levers(age, sex, values, targets):
    current = evaluate(age, sex, values)
    payload = {
        'schema': 'longevity-levers/1', 'model': 'senior-fitness-independence',
        'model_zh': TITLE, 'current': current, 'sensitivity': [], 'levers': [],
        'note_zh': '固定年龄和性别，只比较假设成绩；敏感度是有利方向差距对本项成绩的斜率。分档是阶跃函数，切点处无导数；不表示训练效果或失能风险变化。',
    }
    for metric in METRICS:
        key, prefix = metric['key'], metric['output']
        if key not in values:
            continue
        payload['sensitivity'].append({
            'key': key, 'label_zh': metric['label'], 'unit': metric['unit'],
            'value': values[key], 'output_key': prefix + '_margin',
            'margin_per_unit': metric['direction'],
            'cutoff': current[prefix + '_cutoff'],
        })
        if key in targets:
            changed = evaluate(age, sex, dict(values, **{key: targets[key]}))
            payload['levers'].append({
                'key': key, 'label_zh': metric['label'], 'unit': metric['unit'],
                'from': values[key], 'to': targets[key], 'outputs': changed,
                'margin_delta': changed[prefix + '_margin'] - current[prefix + '_margin'],
            })
    if targets:
        payload['targets'] = {'values': targets, 'outputs': evaluate(age, sex, dict(values, **targets))}
    return payload


def collect(path, manifest):
    try:
        found = skillkit.collect_file(path, manifest)
    except (OSError, ValueError) as exc:
        return {}, [skillkit.Problem('measurements', '测量表', 'file', f'无法读取测量表：{exc}')]
    problems = list(found.problems)
    for name in found.unmatched:
        problems.append(skillkit.Problem(name, name, 'unknown', f'无法识别项目「{name}」，请核对项目名称。'))
    for metric in METRICS:
        value = found.values.get(metric['key'])
        if value is not None and metric['unit'] == '1' and not value.is_integer():
            problems.append(skillkit.Problem(metric['key'], metric['label'], 'integer', f'{metric["label"]}须为整数次数。'))
    if not found.values and not problems:
        problems.append(skillkit.Problem('measurements', 'SFT 测量', 'missing', '至少提供一项已完成的标准化 SFT 测量，不能用零代替未测项目。'))
    return found.values, problems


def main():
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument('--measurements', type=Path)
    parser.add_argument('--age', help='整数周岁，60–94')
    parser.add_argument('--sex', help='male/female，或男/女')
    parser.add_argument('--targets', type=Path)
    parser.add_argument('--out', type=Path, default=Path('out'))
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    for name in ('result.json', 'levers.json', 'problems.json', 'report.md'):
        (args.out / name).unlink(missing_ok=True)
    manifest = skillkit.load_manifest(__file__)
    values, problems = collect(args.measurements, manifest)
    age = None
    try:
        age = None if args.age is None else float(args.age)
        age_problems = skillkit.check_scalar(manifest, 'age', age)
        problems.extend(age_problems)
        if age is not None and not age_problems and not age.is_integer():
            problems.append(skillkit.Problem('age', '年龄', 'integer', '请提供整数周岁；本方法不插值。'))
    except ValueError:
        problems.append(skillkit.Problem('age', '年龄', 'parse', '年龄必须是 60–94 的整数周岁。'))
    sex = {'男': 'male', '女': 'female', 'm': 'male', 'f': 'female'}.get(
        (args.sex or '').strip().lower(), (args.sex or '').strip().lower())
    if sex not in TABLE4:
        problems.append(skillkit.Problem('sex', '论文分组性别', 'missing' if not sex else 'category', '须提供论文分组性别 male/female（男/女）；不推断分组。'))
    targets = {}
    if args.targets is not None:
        targets, target_problems = collect(args.targets, manifest)
        problems.extend(target_problems)
        for key in targets:
            if key not in values:
                problems.append(skillkit.Problem(key, key, 'missing', f'目标项目 {key} 缺少当前测量，无法比较。'))
    if problems:
        path = skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        content = path.read_text(encoding='utf-8').split('\n', 2)[2]
        path.write_text('\n'.join([f'# {TITLE}', '', *paper_card_lines(), '', content]), encoding='utf-8')
        return skillkit.EXIT_INPUT_PROBLEM
    output = evaluate(age, sex, values)
    skillkit.write_result(args.out, manifest, output)
    scenarios = levers(age, sex, values, targets)
    (args.out / 'levers.json').write_text(json.dumps(scenarios, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    lines = [f'# {TITLE}', '', *paper_card_lines(), '', '## 你的结果', '',
             f'年龄组：{output["age_band"]} 岁；论文分组：{"男性" if sex == "male" else "女性"}。', '',
             '| 项目 | 你的成绩 | 论文切点 | 有利方向差距 | 对照结果 |',
             '|---|---:|---:|---:|---|']
    for metric in METRICS:
        prefix = metric['output']
        cutoff = output[prefix + '_cutoff']
        unit = '次' if metric['unit'] == '1' else metric['unit']
        sign = '≥' if metric['direction'] == 1 else '≤'
        threshold = f'{sign} {cutoff:g} {unit}'
        if metric['key'] == 'walk_6min_m':
            threshold += f'（原表 {cutoff / YARD_TO_M:g} 码）'
        value = output[prefix + '_value']
        margin = output[prefix + '_margin']
        status = output[prefix + '_status']
        score = '未提供' if value is None else f'{value:g} {unit}'
        difference = '—' if margin is None else f'{margin:+g} {unit}'
        label = '未评估' if status is None else ('达到参考标准' if status == 'meets_standard' else '未达到参考标准')
        lines.append(f'| {metric["label"]} | {score} | {threshold} | {difference} | {label} |')
    lines += ['', '差距为正表示在有利方向超过切点；起立行走用“切点减成绩”，其余用“成绩减切点”。',
              '2 分钟踏步是 6 分钟步行的替代耐力测试；若两项都测，分别显示，不合并总分。未提供的项目不作推断。',
              '这些切点来自美国社区老年人横断面资料及文献调整；达到切点不能保证今后的独立生活，未达到也不等于现在失能。对其他人群的适用性仍需验证。',
              '只适用于按 SFT 规范完成的测试：弯举女性用 5 磅、男性用 8 磅测试负重；踏步计右膝达到规定高度的次数；起立行走距离为 8 英尺（2.4384 米），不能用 3 米 TUG 替代。测试负重是测量条件，不是训练处方。']
    if targets:
        lines += ['', '## 假设目标成绩', '', '固定年龄和性别，逐项代入你提供的目标成绩：']
        for item in scenarios['levers']:
            metric = next(m for m in METRICS if m['key'] == item['key'])
            status = item['outputs'][metric['output'] + '_status']
            label = '达到参考标准' if status == 'meets_standard' else '未达到参考标准'
            lines.append(f'- {item["label_zh"]}：{item["from"]:g} → {item["to"]:g}，{label}。')
        lines += ['', scenarios['note_zh']]
    lines += ['', f'边界：{BOUNDARY}', '']
    (args.out / 'report.md').write_text('\n'.join(lines), encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
