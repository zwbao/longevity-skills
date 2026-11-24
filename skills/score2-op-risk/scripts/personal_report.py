#!/usr/bin/env python3
"""SCORE2-OP 2021, ten-year primary endpoint; regional validation is draft."""
import argparse
import json
import math
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (TITLE, BOUNDARY, GAP, CENTERS, COEFFICIENTS, BASE_SURVIVAL_10Y,
                     MEAN_LP, SCALES, REGION_LABELS, COUNTRIES, COUNTRY_ALIASES,
                     INPUT_RANGES, MODIFIABLE)


def compute(values, age, sex, region):
    a = age - CENTERS['age']
    sbp = values['sbp_mmhg'] - CENTERS['sbp_mmhg']
    tc = values['tc_mmol_l'] - CENTERS['tc_mmol_l']
    hdl = values['hdl_mmol_l'] - CENTERS['hdl_mmol_l']
    dm, sm = values['diabetes'], values['smoker']
    terms = (a, dm, sm, sbp, tc, hdl, a*dm, a*sm, a*sbp, a*tc, a*hdl)
    lp = sum(b*x for b, x in zip(COEFFICIENTS[sex], terms))
    # Algebraically identical to Methods Table 2; stable near zero risk.
    log_hazard = math.log(-math.log(BASE_SURVIVAL_10Y[sex])) + lp - MEAN_LP[sex]
    original = -math.expm1(-math.exp(log_hazard)) * 100
    scale1, scale2 = SCALES[region][sex]
    calibrated = -math.expm1(-math.exp(scale1 + scale2 * log_hazard)) * 100
    return {'risk_10y_pct': calibrated, 'original_risk_10y_pct': original,
            'linear_predictor': lp}


def cross_checks(values):
    problems = []
    for key in ('smoker', 'diabetes'):
        if key in values and values[key] not in (0, 1):
            problems.append(skillkit.Problem(key, key, 'category', '是否项只接受 0（否）或 1（是）。'))
    if all(k in values for k in ('tc_mmol_l', 'hdl_mmol_l')):
        if values['hdl_mmol_l'] >= values['tc_mmol_l']:
            problems.append(skillkit.Problem('hdl_mmol_l', '高密度脂蛋白胆固醇', 'range',
                                           'HDL 胆固醇必须低于总胆固醇，请核对项目和单位。'))
    return problems


def collect(path, manifest, partial=False):
    try:
        result = skillkit.collect_file(path, manifest)
    except (OSError, ValueError, TypeError) as exc:
        return {}, [skillkit.Problem('file', '测量文件', 'file', f'无法读取测量文件：{exc}')]
    problems = [p for p in result.problems if not (partial and p.kind == 'missing')]
    if partial:
        for key in result.values:
            if key not in MODIFIABLE:
                problems.append(skillkit.Problem(key, key, 'target', '该项不是可改变的目标；糖尿病史保持原值。'))
        if result.unmatched:
            problems.append(skillkit.Problem('targets', '目标值', 'target',
                                           '目标文件存在未知项目：' + '、'.join(result.unmatched)))
        if not result.values and not problems:
            problems.append(skillkit.Problem('targets', '目标值', 'missing', '目标文件没有可用目标。'))
    problems += cross_checks(result.values)
    return result.values, problems


def levers(values, age, sex, region, targets, manifest):
    def risk(v):
        return compute(v, age, sex, region)['risk_10y_pct']
    current = risk(values)
    sensitivities, moves = [], []
    # Continuous partial derivatives; smoking uses the finite 0 -> 1 contrast.
    a = age - CENTERS['age']
    b = COEFFICIENTS[sex]
    scale2 = SCALES[region][sex][1]
    p = current / 100
    prefactor = 100 * (1-p) * (-math.log1p(-p)) * scale2
    slopes = {'sbp_mmhg': b[3]+a*b[8], 'tc_mmol_l': b[4]+a*b[9],
              'hdl_mmol_l': b[5]+a*b[10]}
    for key in MODIFIABLE:
        spec = skillkit.spec_by_key(manifest, key)
        item = {'key': key, 'label_zh': spec['label_zh'], 'unit': spec['unit'], 'value': values[key]}
        if key == 'smoker':
            item.update(per_unit=risk(dict(values, smoker=1))-risk(dict(values, smoker=0)),
                        kind='discrete_0_to_1')
        else:
            item.update(per_unit=prefactor*slopes[key], kind='partial_derivative')
        sensitivities.append(item)
        if key in targets:
            moved = risk(dict(values, **{key: targets[key]}))
            moves.append({'key': key, 'label_zh': spec['label_zh'], 'unit': spec['unit'],
                          'from': values[key], 'to': targets[key], 'risk_pct': moved,
                          'risk_delta_pct': moved-current})
    payload = {'schema': 'longevity-levers/1', 'model': 'score2-op-risk',
               'model_zh': 'SCORE2-OP 十年主结局（仍在验证）', 'validation_status': 'draft',
               'current': {'risk_pct': current}, 'sensitivity': sensitivities, 'levers': moves,
               'note_zh': GAP + BOUNDARY}
    if targets:
        together = risk(dict(values, **targets))
        payload['targets'] = {'values': targets, 'risk_pct': together, 'risk_delta_pct': together-current}
    return payload


def write_report(args):
    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    for name in ('report.md', 'result.json', 'problems.json', 'levers.json'):
        (out / name).unlink(missing_ok=True)
    manifest = skillkit.load_manifest(__file__)
    values, problems = collect(args.measurements, manifest)
    try:
        age = float(args.age) if args.age is not None else None
        problems += skillkit.check_scalar(manifest, 'age', age)
    except ValueError:
        age = None
        problems.append(skillkit.Problem('age', '年龄', 'parse', '年龄必须是以岁为单位的数。'))
    sex = {'male': 'male', 'female': 'female', '男': 'male', '女': 'female',
           'm': 'male', 'f': 'female'}.get((args.sex or '').strip().lower())
    if sex is None:
        problems.append(skillkit.Problem('sex', '性别', 'missing' if args.sex is None else 'category',
                                       '需要原模型分层的性别：male/男 或 female/女。'))
    raw_country = (args.country or '').strip()
    country = COUNTRY_ALIASES.get(raw_country.lower(), raw_country)
    region = next((r for r, countries in COUNTRIES.items()
                   if country.lower() in [c.lower() for c in countries]), None)
    if region is None:
        problems.append(skillkit.Problem('country', '居住国家', 'missing' if not raw_country else 'population',
                         '需要补充 Table 2 所列的居住国家（英文名称）；中国不在校准表中，不能擅自指定地区。'))
    history = (args.prior_cvd or '').strip().lower()
    if history not in ('no', '0', '否', '无'):
        problems.append(skillkit.Problem('prior_cvd', '既往心血管病', 'missing' if not history else 'population',
                         '需明确无既往冠心病、卒中或外周动脉病（--prior-cvd no）；已有上述病史不适用。'))
    targets = {}
    if args.targets is not None:
        targets, target_problems = collect(args.targets, manifest, partial=True)
        problems += target_problems
        problems += cross_checks(dict(values, **targets))
        # Each one-at-a-time scenario must also be physiologically coherent.
        for key, val in targets.items():
            problems += cross_checks(dict(values, **{key: val}))
    if problems:
        report = skillkit.write_problems(out, problems, TITLE, BOUNDARY)
        content = report.read_text(encoding='utf-8').splitlines()
        report.write_text('\n'.join([content[0], '', *paper_card_lines(), '', *content[1:]])+'\n', encoding='utf-8')
        skillkit.write_result(out, manifest, {k['key']: None for k in manifest['outputs']})
        return skillkit.EXIT_INPUT_PROBLEM
    result = compute(values, age, sex, region)
    result['risk_region'] = region
    skillkit.write_result(out, manifest, result)
    lever_data = levers(values, age, sex, region, targets, manifest)
    (out/'levers.json').write_text(json.dumps(lever_data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    lines = [f'# {TITLE}', '', *paper_card_lines(), '', '## 本次估计', '',
             GAP, '', f"按论文参数表复算的十年心血管事件风险：**{result['risk_10y_pct']:.1f}%**（暂定值）。",
             '结局是首次非致死性心肌梗死、非致死性卒中或心血管死亡的复合结局。',
             f'年龄 {age:g} 岁；性别 {"男" if sex == "male" else "女"}；居住国家 {country}；{REGION_LABELS[region]}。',
             '这里的地区分组是论文的地理校准组，并非对这个人的风险分档。',
             f"收缩压 {values['sbp_mmhg']:g} mmHg；总胆固醇 {values['tc_mmol_l']:g} mmol/L；HDL 胆固醇 {values['hdl_mmol_l']:g} mmol/L。",
             f"当前吸烟：{'是' if values['smoker'] else '否'}；糖尿病史：{'是' if values['diabetes'] else '否'}。"]
    if targets:
        t = lever_data['targets']
        lines += ['', '## 用户指定目标的模型比较', '',
                  f"所有目标同时达到时为 {t['risk_pct']:.1f}%，比当前改变 {t['risk_delta_pct']:+.2f} 个百分点。",
                  '这些数值不表示治疗效果，也不代表应达到这些目标。']
        for m in lever_data['levers']:
            lines.append(f"- 仅把{m['label_zh']}从 {m['from']:g} 改为 {m['to']:g} {m['unit']}：{m['risk_pct']:.1f}%，变化 {m['risk_delta_pct']:+.2f} 个百分点。")
    lines += ['', '## 适用范围', '',
              '本实现仅计算十年主结局，不输出五年风险、含心衰住院的风险、风险等级或药物治疗收益。',
              '适用于无上述既往心血管病的老年人；本工具限制为 70–89 岁，这是实现范围，不是论文公布的推导年龄上限。',
              '使用当前测量值；论文未单独加入用药系数。近期开始治疗、明显衰弱或合并症可能影响解释。',
              '地区校准固定为该论文版本，不能将其他国家或族群自动归入某组。',
              '', f'边界: {BOUNDARY}']
    (out/'report.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument('--measurements', type=Path)
    parser.add_argument('--age')
    parser.add_argument('--sex')
    parser.add_argument('--country')
    parser.add_argument('--prior-cvd')
    parser.add_argument('--targets', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(argv)
    return write_report(args)

if __name__ == '__main__':
    raise SystemExit(main())
