#!/usr/bin/env python3
"""Local, standard-library-only IBI arithmetic and exploratory comparison."""
import argparse
import csv
import json
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import BOUNDARY, IBI_THRESHOLD, INPUT_UNITS, SCALE_NOTE, STRATA_ZH, STUDY_MIN_AGE, TITLE


def stratum(ibi):
    return 'low' if ibi < IBI_THRESHOLD else 'high'


def calculate(values):
    nlr = values['neutrophils_10e9_l'] / values['lymphocytes_10e9_l']
    ibi = values['crp_mg_l'] * nlr
    return {'nlr': nlr, 'ibi_mg_l': ibi, 'ibi_stratum': stratum(ibi)}


def levers(values, targets, manifest):
    current = calculate(values)
    c, n, l = (values[k] for k in INPUT_UNITS)
    slopes = dict(zip(INPUT_UNITS, (n / l, c / l, -c * n / l**2)))
    specs = {s['key']: s for s in skillkit.input_specs(manifest)}
    out = {
        'schema': 'longevity-levers/1', 'model': 'inflammatory_burden_index',
        'model_zh': TITLE, 'current': current,
        'sensitivity': [{'key': k, 'label_zh': specs[k]['label_zh'],
                         'unit': INPUT_UNITS[k], 'value': values[k],
                         'ibi_per_unit': slopes[k]} for k in INPUT_UNITS],
        'levers': [],
        'note_zh': '仅为公式的假设情景与局部导数，不预测干预效果；不把血细胞计数或 IBI 切点设为健康目标。',
    }
    if targets:
        for key, target in targets.items():
            moved = calculate(dict(values, **{key: target}))
            out['levers'].append({
                'key': key, 'label_zh': specs[key]['label_zh'], 'unit': INPUT_UNITS[key],
                'from': values[key], 'to': target, **moved,
                'ibi_delta': moved['ibi_mg_l'] - current['ibi_mg_l'],
            })
        together = calculate(dict(values, **targets))
        out['targets'] = {'values': targets, **together,
                          'ibi_delta': together['ibi_mg_l'] - current['ibi_mg_l']}
    return out


def collect(path, manifest, partial=False):
    try:
        got = skillkit.collect_file(path, manifest)
    except (OSError, ValueError, UnicodeError, csv.Error) as exc:
        return {}, [skillkit.Problem('measurements', '测量表', 'file', f'无法读取测量表：{exc}')]
    problems = [p for p in got.problems if not (partial and p.kind == 'missing')]
    if partial and got.unmatched:
        problems.append(skillkit.Problem('targets', '目标表', 'unknown',
                                        '目标表存在无法识别的指标：' + '、'.join(got.unmatched)))
    if partial and not got.values and not problems:
        problems.append(skillkit.Problem('targets', '目标表', 'missing', '目标表没有可计算的指标。'))
    return got.values, problems


def main():
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument('--measurements', type=Path)
    parser.add_argument('--targets', type=Path)
    parser.add_argument('--age', type=float, help='可选背景，不进入公式')
    parser.add_argument('--sex', help='可选背景，不进入公式')
    parser.add_argument('--out', type=Path, default=Path('out'))
    args = parser.parse_args()
    manifest = skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True, exist_ok=True)
    for name in ('result.json', 'problems.json', 'levers.json', 'report.md'):
        (args.out / name).unlink(missing_ok=True)
    values, problems = collect(args.measurements, manifest)
    problems += skillkit.check_scalar(manifest, 'age', args.age)
    targets = {}
    if args.targets is not None:
        targets, target_problems = collect(args.targets, manifest, partial=True)
        problems += target_problems
    card = [f'# {TITLE}', '', *paper_card_lines(), '']
    if problems:
        skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        error_body = skillkit.problems_markdown(problems, TITLE, BOUNDARY).split('\n', 2)[2]
        (args.out / 'report.md').write_text('\n'.join(card) + '\n' + error_body, encoding='utf-8')
        return skillkit.EXIT_INPUT_PROBLEM
    result = calculate(values)
    skillkit.write_result(args.out, manifest, result)
    scenarios = levers(values, targets, manifest)
    (args.out / 'levers.json').write_text(json.dumps(scenarios, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    lines = card + ['## 你的结果', '',
                    '| 指标 | 本次读数 |', '|---|---|']
    for spec in skillkit.input_specs(manifest):
        key = spec['key']
        lines.append(f"| {spec['label_zh']} | {values[key]:.6g} {INPUT_UNITS[key]} |")
    lines += [f"| 中性粒细胞/淋巴细胞比值 | {result['nlr']:.6g} |",
              f"| IBI（按 CRP mg/L 计） | {result['ibi_mg_l']:.6g} mg/L |",
              f"| 探索分组 | {STRATA_ZH[result['ibi_stratum']]} |", '',
              f'论文切点：{IBI_THRESHOLD}；低组为小于切点，高组包含等于切点。分组使用未四舍五入的计算值。', '',
              SCALE_NOTE, '',
              f'该研究人体主分析使用美国较早期调查中年满 {STUDY_MIN_AGE} 岁的受试者；其他年龄和人群的分层意义未在本文得到验证。', '',
              '这次不计算衰弱指数、三基因分子评分或甲基化衰老速度；横断面相关不能说明改变某项化验会使衰老变慢。', '']
    if args.age is not None and args.age < STUDY_MIN_AGE:
        lines += ['你提供的年龄低于研究甲基化样本的年龄下限；这里仅显示算术读数。', '']
    if targets:
        together = scenarios['targets']
        lines += ['## 你提供的假设情景', '',
                  f"所有指定值同时成立时，IBI 为 {together['ibi_mg_l']:.6g} mg/L，"
                  f"相对本次变化 {together['ibi_delta']:+.6g} mg/L。", '', scenarios['note_zh'], '']
    lines += [f'边界：{BOUNDARY}', '']
    (args.out / 'report.md').write_text('\n'.join(lines), encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
