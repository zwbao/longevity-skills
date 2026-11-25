#!/usr/bin/env python3
"""Original 2009 Schonberg score and printed validation-cohort risk lookup."""
import argparse
import json
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (AGE_POINTS, BMI_CUTOFF, BMI_LOW_POINTS, CATEGORY_POINTS,
                     HOSPITAL_POINTS, RISK_ROWS, TARGET_KEYS, LABELS, CATEGORY_LABELS,
                     INPUT_UNITS)

TITLE = 'Schonberg五年死亡风险指数'
BOUNDARY = ('这是美国社区居住、可自报健康状况且无已报告痴呆的65岁及以上人群的历史队列分档估计，'
            '不是个人剩余寿命或因果干预效果；不适用于养老机构居民或痴呆患者，'
            '不能据此开始或停止药物、筛查或其他治疗。')
SCENARIO_NOTE = ('目标比较只是在同一张历史风险表中替换输入；不代表达成目标能造成相应风险下降。'
                 'BMI阈值不构成增重建议，住院次数不构成避免必要住院的建议。'
                 '敏感度列出单项评分档位替换，不是连续导数或推荐目标。')


def score_terms(values):
    age = values['age_years']
    if age < AGE_POINTS[0][0]:
        raise ValueError('年龄不在原研究范围')
    terms = {'age_years': next(p for lower, p in reversed(AGE_POINTS) if age >= lower),
             'bmi_kg_m2': BMI_LOW_POINTS if values['bmi_kg_m2'] < BMI_CUTOFF else 0}
    for key, points in CATEGORY_POINTS.items():
        value = values[key]
        if int(value) != value or not 0 <= value < len(points):
            raise ValueError(f'{key}: 无效类别')
        terms[key] = points[int(value)]
    count = values['hospitalizations_count']
    if int(count) != count or count < 0:
        raise ValueError('无效住院次数')
    terms['hospitalizations_count'] = HOSPITAL_POINTS[min(int(count), len(HOSPITAL_POINTS)-1)]
    return terms


def risk_for_score(score):
    if int(score) != score or not 0 <= score <= maximum_score():
        raise ValueError('无效积分')
    _, band, risk, low, high = next(row for row in reversed(RISK_ROWS) if score >= row[0])
    return {'risk_band': band, 'mortality_5y_pct': risk,
            'mortality_5y_ci_low_pct': low, 'mortality_5y_ci_high_pct': high}


def maximum_score():
    return AGE_POINTS[-1][1] + BMI_LOW_POINTS + sum(max(p) for p in CATEGORY_POINTS.values()) + max(HOSPITAL_POINTS)


def calculate(values):
    terms = score_terms(values)
    score = sum(terms.values())
    return {'total_score': score, **risk_for_score(score),
            **{f'{key}_points': value for key, value in terms.items()}}


def categorical_problems(values):
    problems = []
    for key, value in values.items():
        if key != 'bmi_kg_m2' and not float(value).is_integer():
            problems.append(skillkit.Problem(key, LABELS.get(key, key), 'category',
                                            f'{LABELS.get(key, key)}必须填写整数，不能插值或四舍五入。'))
    return problems


def collect(path, manifest, targets=False):
    try:
        collected = skillkit.collect_file(path, manifest)
    except (OSError, ValueError, TypeError) as exc:
        return {}, [skillkit.Problem('targets' if targets else 'measurements', '输入表', 'file',
                                     f'无法读取输入表：{exc}')]
    problems = [p for p in collected.problems if not (targets and p.kind == 'missing')]
    problems += categorical_problems(collected.values)
    for name in collected.unmatched:
        problems.append(skillkit.Problem(name, name, 'unknown', f'未识别项目「{name}」，请按输入说明核对名称。'))
    if targets:
        for key in collected.values:
            if key not in TARGET_KEYS:
                problems.append(skillkit.Problem(key, LABELS[key], 'target',
                                                f'{LABELS[key]}是既往诊断，不能作为可逆目标；请保留原始病史。'))
        if not collected.values and not problems:
            problems.append(skillkit.Problem('targets', '目标表', 'missing', '目标表至少需要一项允许比较的输入。'))
    return collected.values, problems


def levers(values, targets):
    current = calculate(values)
    terms = score_terms(values)
    sensitivity = []
    for key, term in terms.items():
        if key == 'age_years':
            alternatives = [(f'{lower}岁起的年龄档', points) for lower, points in AGE_POINTS]
        elif key == 'bmi_kg_m2':
            alternatives = [(f'<{BMI_CUTOFF} kg/m²', BMI_LOW_POINTS), (f'≥{BMI_CUTOFF} kg/m²', 0)]
        elif key == 'hospitalizations_count':
            alternatives = [(('至少2' if i == 2 else str(i)) + '次', p) for i, p in enumerate(HOSPITAL_POINTS)]
        else:
            labels = CATEGORY_LABELS.get(key, ('否', '是'))
            alternatives = list(zip(labels, CATEGORY_POINTS[key]))
        contrasts = []
        for category, points in alternatives:
            changed = current['total_score'] - term + points
            contrasts.append({'category_zh': category, 'points': points,
                              'total_score': changed, 'score_delta': points - term,
                              'mortality_5y_pct': risk_for_score(changed)['mortality_5y_pct'],
                              'mortality_delta_pp': risk_for_score(changed)['mortality_5y_pct'] - current['mortality_5y_pct']})
        sensitivity.append({'key': key, 'label_zh': LABELS[key], 'value': values[key],
                            'unit': INPUT_UNITS.get(key, '1'),
                            'current_points': term, 'target_allowed': key in TARGET_KEYS,
                            'kind': 'discrete_category_contrast', 'alternatives': contrasts})
    result = {'schema': 'longevity-levers/1', 'model': 'schonberg-mortality-index-2009',
              'model_zh': TITLE, 'current': current, 'sensitivity': sensitivity,
              'levers': [], 'note_zh': SCENARIO_NOTE}
    if targets:
        for key, target in targets.items():
            moved = calculate(dict(values, **{key: target}))
            result['levers'].append({'key': key, 'label_zh': LABELS[key],
                                     'unit': INPUT_UNITS[key],
                                     'from': values[key], 'to': target,
                                     'total_score': moved['total_score'],
                                     'score_delta': moved['total_score'] - current['total_score'],
                                     'mortality_5y_pct': moved['mortality_5y_pct'],
                                     'mortality_delta_pp': moved['mortality_5y_pct'] - current['mortality_5y_pct']})
        together = calculate(dict(values, **targets))
        result['targets'] = {'values': targets, **together,
                             'score_delta': together['total_score'] - current['total_score'],
                             'mortality_delta_pp': together['mortality_5y_pct'] - current['mortality_5y_pct']}
    return result


def display_value(key, value):
    if key in CATEGORY_LABELS:
        return CATEGORY_LABELS[key][int(value)]
    if key in CATEGORY_POINTS:
        return '是' if value else '否'
    if key == 'bmi_kg_m2':
        return f'{value:g} kg/m²'
    if key == 'age_years':
        return f'{value:g}岁'
    if key == 'hospitalizations_count':
        return f'{value:g}次'
    return f'{value:g}'


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument('--measurements', type=Path)
    parser.add_argument('--age', help='已满周岁整数，至少65岁')
    parser.add_argument('--sex', help='male/female或男/女')
    parser.add_argument('--targets', type=Path)
    parser.add_argument('--out', type=Path, default=Path('out'))
    args = parser.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    for name in ('problems.json', 'result.json', 'levers.json', 'report.md'):
        (args.out / name).unlink(missing_ok=True)
    manifest = skillkit.load_manifest(__file__)
    values, problems = collect(args.measurements, manifest)
    try:
        age = None if args.age is None else skillkit.parse_number(args.age)
        problems += skillkit.check_scalar(manifest, 'age_years', age)
        if age is not None:
            values['age_years'] = age
            problems += categorical_problems({'age_years': age})
    except ValueError:
        problems.append(skillkit.Problem('age_years', '年龄', 'parse', '年龄需要有限数值的已满周岁整数。'))
    sexes = {'male': 1, 'female': 0, '男': 1, '女': 0}
    sex = (args.sex or '').strip().lower()
    if sex not in sexes:
        problems.append(skillkit.Problem('sex', '性别', 'category', '缺少或无法识别性别，请填写male/男或female/女。'))
    else:
        values['male'] = sexes[sex]
    targets = {}
    if args.targets is not None:
        targets, target_problems = collect(args.targets, manifest, targets=True)
        problems += target_problems
        if targets.get('smoking_code') == 0 and values.get('smoking_code', 0) != 0:
            problems.append(skillkit.Problem('smoking_code', '吸烟状态', 'target',
                                            '既往或目前吸烟者不能通过目标改为从未吸烟；戒烟后属于既往吸烟。'))
    if problems:
        path = skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        content = path.read_text()
        heading, rest = content.split('\n', 1)
        path.write_text(heading + '\n\n' + '\n'.join(paper_card_lines()) + '\n' + rest, encoding='utf-8')
        print(path)
        return skillkit.EXIT_INPUT_PROBLEM
    result = calculate(values)
    comparison = levers(values, targets)
    lines = [f'# {TITLE}', '', *paper_card_lines(), '', '## 你的结果', '',
             f"总积分：**{result['total_score']}分**；对应表3的 **{result['risk_band']}分** 档。",
             f"验证队列同档五年死亡风险：**{result['mortality_5y_pct']}%**，"
             f"该档人群估计的95%置信区间为 **{result['mortality_5y_ci_low_pct']}%–{result['mortality_5y_ci_high_pct']}%**。", '',
             '这是相同积分档的人群估计，置信区间并非个人结局的上下界；不用于推算还能活多少年。', '',
             '| 项目 | 你的输入 | 积分 |', '|---|---|---|']
    for key, points in score_terms(values).items():
        lines.append(f'| {LABELS[key]} | {display_value(key, values[key])} | {points} |')
    lines += ['', '## 如何理解', '',
              '按2009年原版积分相加，再查验证队列的风险档；同档内不插值，18分及以上共用最高档。',
              '研究使用1997–2000年美国NHIS自报信息，随访截至2002年底；验证来自同一调查的随机拆分，'
              '并非独立临床队列验证。对今天或其他国家人群的适用性尚不能由本次计算确定。',
              '仅适用于社区居住、能自行回答且无痴呆的老年人；若不符合这些条件，请勿把本读出作为适用的风险估计。']
    if targets:
        together = comparison['targets']
        lines += ['', '## 你指定的情景', '',
                  f"同时替换目标后：{together['total_score']}分，对应同档风险{together['mortality_5y_pct']}%；"
                  f"相对当前查表值变化{together['mortality_delta_pp']:+g}个百分点。", '',
                  '| 单项替换 | 原值 → 目标 | 积分变化 | 风险查表值变化（百分点） |', '|---|---|---|---|']
        for item in comparison['levers']:
            key = item['key']
            lines.append(f"| {item['label_zh']} | {display_value(key, item['from'])} → {display_value(key, item['to'])} | "
                         f"{item['score_delta']:+g} | {item['mortality_delta_pp']:+g} |")
    lines += ['', SCENARIO_NOTE, '', f'边界：{BOUNDARY}', '']
    (args.out / 'report.md').write_text('\n'.join(lines), encoding='utf-8')
    skillkit.write_result(args.out, manifest, result)
    (args.out / 'levers.json').write_text(json.dumps(comparison, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(args.out / 'report.md')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
