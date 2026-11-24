#!/usr/bin/env python3
"""Evaluate the printed MitoAge linear formula on prepared ln-RFU features."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import DERIVATION_AGES, INTERCEPT, PREPROCESSING, PROTEINS, SEX_MALE_WEIGHT, WEIGHTS

TITLE = 'MitoAge 蛋白分值'
BOUNDARY = 'MitoAge 仍在验证，是血清作用下细胞呼吸能力相关的研究分值，不是年龄岁数、疾病诊断或干预效果；不能据此开始或停止药物。'
NOTE = '目标情景仅替换公式输入，不代表改变该蛋白会改善线粒体功能；不设健康目标、优先级或药物建议。'


def score(values: dict[str, float], male: int) -> float:
    return math.fsum([INTERCEPT, SEX_MALE_WEIGHT * male, *(w * values[k] for k, w in WEIGHTS.items())])


def levers(values: dict[str, float], targets: dict[str, float], male: int) -> dict:
    current = score(values, male)
    result = {
        'schema': 'longevity-levers/1', 'model': 'mitoage_score',
        'model_zh': 'MitoAge线性分值（仍在验证）',
        'current': {'mitoage_score': current},
        'sensitivity': [
            {'key': p['key'], 'label_zh': p['label_zh'], 'unit': '1',
             'value': values[p['key']], 'score_per_unit': WEIGHTS[p['key']]}
            for p in PROTEINS
        ],
        'levers': [], 'note_zh': NOTE,
    }
    for key, target in targets.items():
        moved = dict(values, **{key: target})
        result['levers'].append({
            'key': key, 'unit': '1', 'from': values[key], 'to': target,
            'mitoage_score': score(moved, male),
            'mitoage_delta': WEIGHTS[key] * (target - values[key]),
        })
    if targets:
        result['targets'] = {
            'values': targets, 'mitoage_score': score(dict(values, **targets), male),
            'mitoage_delta': math.fsum(WEIGHTS[k] * (v - values[k]) for k, v in targets.items()),
        }
    return result


def collect(path, manifest, *, partial=False):
    try:
        collected = skillkit.collect_file(path, manifest)
    except (OSError, ValueError, TypeError) as exc:
        return {}, [skillkit.Problem('measurements', '蛋白数据表', 'file', f'无法读取数据表：{exc}')]
    problems = [p for p in collected.problems if not (partial and p.kind == 'missing')]
    # Strict table membership also prevents silently ignoring misspelled targets.
    problems.extend(skillkit.Problem(name, name, 'unknown', f'未识别指标 {name}；请使用技能列出的蛋白名称或SeqId。') for name in collected.unmatched)
    if partial and not collected.values and not problems:
        problems.append(skillkit.Problem('targets', '目标数据表', 'missing', '目标表没有可用的蛋白目标值。'))
    return collected.values, problems


def write_failure(out, problems):
    skillkit.write_problems(out, problems, TITLE, BOUNDARY)
    path = out / 'report.md'
    body = path.read_text(encoding='utf-8').split('\n', 1)[1]
    path.write_text('\n'.join([f'# {TITLE}', '', *paper_card_lines(), '', body]), encoding='utf-8')
    return skillkit.EXIT_INPUT_PROBLEM


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--measurements', type=Path)
    parser.add_argument('--sex', help='male/男 或 female/女，Table 2的男性指示变量')
    parser.add_argument('--age', help='仅作适用人群提示，不进公式')
    parser.add_argument('--preprocessing', help='确认数据为somascan-1.3k-ln-qc')
    parser.add_argument('--targets', type=Path, help='可选目标ln-RFU，同测量文件表头')
    parser.add_argument('--out', type=Path, default=Path('out'))
    args = parser.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    for name in ('result.json', 'levers.json', 'problems.json', 'report.md'):
        (args.out / name).unlink(missing_ok=True)
    manifest = skillkit.load_manifest(__file__)
    values, problems = collect(args.measurements, manifest)
    targets = {}
    if args.targets is not None:
        targets, target_problems = collect(args.targets, manifest, partial=True)
        problems.extend(target_problems)
    sex = (args.sex or '').strip().casefold()
    sex_codes = {'male': 1, '男': 1, 'female': 0, '女': 0}
    if sex not in sex_codes:
        problems.append(skillkit.Problem('sex', '模型所用性别', 'missing' if not sex else 'category', '请提供male/男或female/女，用于论文男性指示变量；不能猜测或省略性别项。'))
    if args.preprocessing != PREPROCESSING:
        problems.append(skillkit.Problem('preprocessing', '数据处理确认', 'preprocessing', '需要SomaScan 1.3K相同SeqId、实验室质控后自然对数RFU；确认数据确实符合后传入 --preprocessing somascan-1.3k-ln-qc。不要对log2、NPX、z分数或原始RFU仅改单位名。'))
    age = None
    if args.age is not None:
        try:
            age = skillkit.parse_number(args.age)
            problems.extend(skillkit.check_scalar(manifest, 'age', age))
        except ValueError:
            problems.append(skillkit.Problem('age', '实足年龄', 'number', '实足年龄必须是有限数值，单位为岁。'))
    if problems:
        return write_failure(args.out, problems)
    male = sex_codes[sex]
    value = score(values, male)
    scenario = levers(values, targets, male)
    skillkit.write_result(args.out, manifest, {'mitoage_score': value})
    (args.out / 'levers.json').write_text(json.dumps(scenario, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    report = [f'# {TITLE}', '', *paper_card_lines(), '', '## 你的结果', '',
              f'- MitoAge线性分值：{value:.6f}（仍在验证）。',
              '- 已使用全部25项蛋白的自然对数RFU和论文性别项；实足年龄不进入公式。',
              '- 这是按公开权重计算的分值，不是年龄岁数。尚无完整个人算例核验绝对尺度，不解释为实测呼吸率，也不设正常、异常或年轻、衰老分档。',
              '- 保留公式的原始线性结果，包括负值；不截零，不自行加均值、标准差或做指数变换。']
    if age is None:
        report += ['- 未提供年龄，无法核对研究年龄范围。']
    elif not DERIVATION_AGES[0] <= age <= DERIVATION_AGES[1]:
        report += [f'- 你的年龄为{age:g}岁，超出研究22–92岁范围，属于外推。']
    else:
        report += [f'- 你的年龄为{age:g}岁，位于研究22–92岁范围内；这不等于已获个人临床验证。']
    if targets:
        report += ['', '## 目标情景', '', NOTE,
                   f"全部目标代入后的分值：{scenario['targets']['mitoage_score']:.6f}；变化：{scenario['targets']['mitoage_delta']:+.6f}。"]
        labels = {p['key']:p['label_zh'] for p in PROTEINS}
        report += [f"- 仅改变{labels[p['key']]}：{p['from']:g} → {p['to']:g} ln(RFU)，分值变化 {p['mitoage_delta']:+.6f}。" for p in scenario['levers']]
    report += ['', '## 输入与证据范围', '',
               '输入必须由同平台检测及质控流程准备。技能不使用单人的25项测量重建研究中的队列离群值处理或KNN填补；缺测即停止。不同平台或批次的数据不能仅凭相同蛋白名称视为可比。',
               '论文使用健康成年人同一次采样的资料与原代细胞实验；跨时间变化、外部人群适用性和临床干预获益尚不能由本分值确定。',
               '', f'边界：{BOUNDARY}']
    (args.out / 'report.md').write_text('\n'.join(report)+'\n', encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
