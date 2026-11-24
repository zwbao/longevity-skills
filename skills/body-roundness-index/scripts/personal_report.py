"""Personal waist-based body roundness, using the published geometric model."""
import argparse
import copy
import json
import math
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import BOUNDARY, BRI_OFFSET, BRI_SCALE


def calculate(values):
    h, w = values['height_cm'], values['waist_cm']
    if not (math.isfinite(h) and math.isfinite(w) and h > 0 and 0 < w < math.pi * h):
        raise ValueError('腰围和身高必须为正数，且腰围必须小于 π × 身高，才能构成论文所定义的椭圆。')
    eccentricity = math.sqrt(1 - (w / (math.pi * h)) ** 2)
    return {'bri': BRI_OFFSET - BRI_SCALE * eccentricity, 'waist_eccentricity': eccentricity}


def collect(path, manifest):
    try:
        result = skillkit.collect_file(path, manifest)
    except (OSError, ValueError, TypeError) as exc:
        return {}, [skillkit.Problem('', '测量表', 'file', f'无法读取测量表：{exc}')]
    problems = list(result.problems)
    for name in result.unmatched:
        problems.append(skillkit.Problem(name, name, 'unknown', f'无法识别「{name}」；本表仅接受身高和腰围。'))
    return dict(result.values), problems


def levers(values, targets):
    current = calculate(values)
    h, w = values['height_cm'], values['waist_cm']
    slope = BRI_SCALE * w / (math.pi**2 * h**2 * current['waist_eccentricity'])
    result = {
        'schema': 'longevity-levers/1', 'model': 'body_roundness_index',
        'model_zh': '腰围版身体圆度指数（Thomas 2013）', 'current': current,
        'sensitivity': [{'key': 'waist_cm', 'label_zh': '腰围', 'unit': 'cm',
                         'value': w, 'bri_per_unit': slope}],
        'levers': [],
        'note_zh': '保持身高固定的数学情景；目标由使用者提供，不代表健康目标或干预效果。身高不作为可改变的杠杆。'
    }
    if targets:
        moved = calculate({**values, **targets})
        delta = moved['bri'] - current['bri']
        result['levers'] = [{'key': 'waist_cm', 'label_zh': '腰围', 'unit': 'cm',
                             'from': w, 'to': targets['waist_cm'], 'bri_delta': delta}]
        result['targets'] = {'values': targets, **moved, 'bri_delta': delta}
    return result


def add_card(text):
    title, rest = text.split('\n', 1)
    return '\n'.join([title, '', *paper_card_lines(), '', rest.lstrip('\n')])


def main(argv=None):
    parser = argparse.ArgumentParser(description='根据身高和腰围计算 BRI')
    parser.add_argument('--measurements', type=Path)
    parser.add_argument('--age', help='可选背景信息，不进入几何公式')
    parser.add_argument('--sex', help='可选背景信息，不进入几何公式')
    parser.add_argument('--targets', type=Path, help='仅腰围目标，marker,value,unit')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    for name in ('result.json', 'problems.json', 'levers.json', 'report.md'):
        (args.out / name).unlink(missing_ok=True)
    manifest = skillkit.load_manifest(__file__)
    values, problems = collect(args.measurements, manifest)
    targets = {}
    if args.targets is not None:
        target_manifest = copy.deepcopy(manifest)
        target_manifest['inputs'] = [s for s in target_manifest['inputs'] if s['key'] == 'waist_cm']
        targets, target_problems = collect(args.targets, target_manifest)
        for p in target_problems:
            p.message_zh = '目标表：' + p.message_zh
        problems.extend(target_problems)
    if not problems:
        try:
            outputs = calculate(values)
            scenarios = levers(values, targets)
        except ValueError as exc:
            problems.append(skillkit.Problem('waist_cm', '腰围与身高', 'geometry', str(exc)))
    if problems:
        path = skillkit.write_problems(args.out, problems, '身体圆度指数 BRI', BOUNDARY)
        path.write_text(add_card(path.read_text(encoding='utf-8')), encoding='utf-8')
        skillkit.write_result(args.out, manifest, {s['key']: None for s in manifest['outputs']})
        return skillkit.EXIT_INPUT_PROBLEM
    rows = ['# 身体圆度指数 BRI', '', *paper_card_lines(), '', '## 你的结果', '',
            f"身高 {values['height_cm']:g} cm，腰围 {values['waist_cm']:g} cm。",
            f"身体圆度指数 BRI：**{outputs['bri']:.2f}**（无单位）。",
            f"腰围椭圆偏心率：{outputs['waist_eccentricity']:.6f}（无单位）。", '',
            '在身高固定时，腰围越大，BRI 越高，所代表的体形越圆。偏心率则越低。',
            '研究基于成人测量。腰围测量部位会影响结果；重复比较时应使用相同部位和方法。',
            '原研究 NHANES 和 St. Luke’s 的腰围在髂嵴上缘测量；Kiel 使用下肋与髂嵴之间的方法。',
            '本报告不计算体脂率、内脏脂肪和健康区间，也不把人群 BRI 分布当作个人诊断阈值。']
    if targets:
        rows += ['', '## 你提供的腰围情景', '',
                 f"若身高固定、腰围为 {targets['waist_cm']:g} cm，BRI 为 {scenarios['targets']['bri']:.2f}，相差 {scenarios['targets']['bri_delta']:+.2f}。",
                 scenarios['note_zh']]
    rows += ['', f'边界: {BOUNDARY}', '']
    (args.out / 'report.md').write_text('\n'.join(rows), encoding='utf-8')
    skillkit.write_result(args.out, manifest, outputs)
    (args.out / 'levers.json').write_text(json.dumps(scenarios, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
