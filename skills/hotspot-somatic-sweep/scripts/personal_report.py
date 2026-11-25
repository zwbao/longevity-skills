#!/usr/bin/env python3
"""One blood SNV record: observed VAF and the published hotspot-sweep screen."""
import argparse
import math
import re
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import BOUNDARY, COUNT_RANGES, HOTSPOTS, MIN_VARIANT_READS, STATUS_ZH, SWEEP_VAF_FRACTION

TITLE = '血液热点变异与克隆扫荡筛查条件'


def normalize_variant(text):
    m = re.fullmatch(r'([A-Z][A-Z0-9]*)[ :_]+(?:P\.)?([A-Z][1-9][0-9]*[A-Z*])', text.strip().upper())
    if not m:
        raise ValueError('请提供基因和单字母蛋白替换，例如 SF3B1 p.K700E；不接受只有基因名、rs 编号、未注释坐标或多条变异。')
    change = m[2]
    if change.endswith('X'):
        change = change[:-1] + '*'
    return f'{m[1]} p.{change}'


def readout(variant, total, alt):
    variant = normalize_variant(variant)
    vaf = alt / total
    if variant not in HOTSPOTS:
        status = 'outside_panel'
    elif alt < MIN_VARIANT_READS:
        status = 'insufficient_support'
    elif vaf > SWEEP_VAF_FRACTION:
        status = 'meets_screen'
    else:
        status = 'below_or_equal_cutoff'
    return {'variant': variant, 'vaf_fraction': vaf, 'vaf_pct': 100 * vaf, 'screen_status': status}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--measurements', type=Path)
    parser.add_argument('--variant')
    parser.add_argument('--age')
    parser.add_argument('--sex')
    parser.add_argument('--out', type=Path, default=Path('out'))
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True, exist_ok=True)
    problems = []
    try:
        collected = skillkit.collect_file(args.measurements, manifest)
        problems.extend(collected.problems)
        values = collected.values
        if collected.unmatched:
            problems.append(skillkit.Problem('measurements', '测量文件', 'unknown', '存在无法识别的项目：' + '、'.join(collected.unmatched) + '。请只提供这条变异的总读段数和突变支持读段数。'))
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        values = {}
        problems.append(skillkit.Problem('measurements', '测量文件', 'parse', f'无法读取测量表：{exc}'))
    for key in COUNT_RANGES:
        if key in values and not values[key].is_integer():
            problems.append(skillkit.Problem(key, key, 'integer', '读段计数必须是整数，不能填 VAF 百分比或四舍五入的估计数。'))
    if all(k in values for k in COUNT_RANGES) and values['variant_reads_count'] > values['total_reads_count']:
        problems.append(skillkit.Problem('variant_reads_count', '突变支持读段数', 'inconsistent', '突变支持读段数不能超过同一位点的总读段数。'))
    variant = None
    if not args.variant:
        problems.append(skillkit.Problem('variant', '基因与蛋白改变', 'missing', '缺少这条变异的基因与蛋白改变，例如 --variant "SF3B1 p.K700E"。'))
    else:
        try:
            variant = normalize_variant(args.variant)
        except ValueError as exc:
            problems.append(skillkit.Problem('variant', '基因与蛋白改变', 'parse', str(exc)))
    age = None
    if args.age is not None:
        try:
            age = skillkit.parse_number(args.age)
            problems.extend(skillkit.check_scalar(manifest, 'age', age))
        except ValueError:
            problems.append(skillkit.Problem('age', '年龄', 'parse', '年龄必须是有限数值，单位为岁。'))
    sex = None
    if args.sex is not None:
        sex = {'女': '女', 'female': '女', 'f': '女', '男': '男', 'male': '男', 'm': '男'}.get(args.sex.strip().lower())
        if sex is None:
            problems.append(skillkit.Problem('sex', '性别', 'parse', '性别可写女/female 或男/male；该字段只作研究人群背景，不参与计算。'))
    card = [f'# {TITLE}', '', *paper_card_lines(), '']
    if problems:
        skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        body = skillkit.problems_markdown(problems, TITLE, BOUNDARY).split('\n', 2)[2]
        (args.out / 'report.md').write_text('\n'.join(card) + '\n' + body, encoding='utf-8')
        skillkit.write_result(args.out, manifest, {x['key']: None for x in manifest['outputs']})
        return skillkit.EXIT_INPUT_PROBLEM
    (args.out / 'problems.json').unlink(missing_ok=True)
    result = readout(variant, values['total_reads_count'], values['variant_reads_count'])
    skillkit.write_result(args.out, manifest, result)
    lines = card + [
        '## 本次记录', '',
        f"变异：{result['variant']}。",
        f"同一位点总读段数：{values['total_reads_count']:g}；支持这一替换的读段数：{values['variant_reads_count']:g}。",
        f"计算 VAF：{result['vaf_pct']:.6f}%（比例 {result['vaf_fraction']:.15g}）。", '',
        STATUS_ZH[result['screen_status']], '',
        f'论文规则：在指定热点替换名单内，支持读段至少 {MIN_VARIANT_READS} 条，VAF 严格大于 {100 * SWEEP_VAF_FRACTION:g}%；恰好位于切点不满足条件。判定使用未四舍五入的比例。', '',
        '这是对已提供且经实验室质控的血液测序记录作核对。基因和蛋白改变应已按论文所列注释确认；本报告不处理原始测序数据，不自动区分胚系变异、测序伪差和体细胞变异，也不把 VAF 换算成受影响细胞比例。', '',
        '这次只检查一条记录。论文在人群层面要求至少一条合格热点变异满足条件；一条未命中不能代表其他变异未命中。论文中的风险关联不是你的发病概率。', '',
    ]
    if age is not None or sex is not None:
        lines += [f"背景信息：年龄 {age if age is not None else '未提供'} 岁；性别 {sex or '未提供'}。这些信息不改变计算结果。", '']
    if age is not None and not 40 <= age <= 70:
        lines += ['你的年龄不在论文图 5f 所述约 40–70 岁人群范围内，不能直接外推该人群关联。', '']
    lines += ['如需解释这条变异，请把完整测序报告、血常规和既往病史交给血液专科核实。', '', f'边界: {BOUNDARY}']
    (args.out / 'report.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
