"""Offline categorical lookup, not an individual or causal risk model."""
import argparse
import json
from pathlib import Path

import skillkit
from paper_card import lines as paper_card_lines
from presets import (BOUNDARY, CATEGORIES, CUTPOINTS, INPUT_KEY, LABELS, STRATA, TABLES, TITLE)


def category(value, status):
    if value == 0:
        return status
    for name, upper in zip(CATEGORIES, CUTPOINTS):
        if value < upper:
            return name
    return 'higher'


def row_result(cat, sex):
    rr, lower, upper = TABLES[sex][cat]
    return {'category': cat, 'stratum': sex, 'rr': rr, 'ci_lower': lower, 'ci_upper': upper}


def lookup(value, status, sex):
    return {INPUT_KEY: value, **row_result(category(value, status), sex)}


def collect(path, manifest, target=False):
    try:
        data = skillkit.collect_file(path, manifest)
    except (OSError, ValueError, UnicodeError) as exc:
        return {}, [skillkit.Problem(INPUT_KEY, '日均纯酒精摄入量', 'file', f'无法读取文件：{exc}')]
    problems = list(data.problems)
    if data.unmatched:
        problems.append(skillkit.Problem(INPUT_KEY, '日均纯酒精摄入量', 'unknown',
                                        '无法识别项目：' + '、'.join(data.unmatched)))
    if target:
        for p in problems:
            p.message_zh = '目标文件：' + p.message_zh
    return data.values, problems


def levers(value, status, sex, target=None):
    current = lookup(value, status, sex)
    cat = current['category']
    neighbors = []
    if cat in CATEGORIES:
        index = CATEGORIES.index(cat)
        for j in (index-1, index+1):
            if 0 <= j < len(CATEGORIES):
                other = row_result(CATEGORIES[j], sex)
                neighbors.append({'category': CATEGORIES[j], 'label_zh': LABELS[CATEGORIES[j]],
                                  'outputs': other, 'rr_delta': round(other['rr']-current['rr'], 10)})
    data = {
        'schema': 'longevity-levers/1', 'model': 'alcohol-mortality-risk-lookup',
        'model_zh': '完全调整的饮酒量分档关联查表', 'current': current,
        'sensitivity': [{'key': INPUT_KEY, 'unit': 'g/d', 'value': value,
                         'method': 'adjacent_printed_categories', 'neighbors': neighbors,
                         'note_zh': '只比较相邻分档；不提供连续导数，同档不变不表示真实风险不变。零摄入按饮酒史分类，无连续敏感度。'}],
        'levers': [],
        'note_zh': '这是两个饮酒量分档的人群关联值之差，不是改变饮酒后的因果效应；不计算差值置信区间，也不寻找最佳饮酒量。',
    }
    if target is not None:
        other = lookup(target, 'current', sex)
        delta = round(other['rr']-current['rr'], 10)
        data['targets'] = {'values': {INPUT_KEY: target}, 'outputs': other, 'rr_delta': delta}
        data['levers'] = [{'key': INPUT_KEY, 'label_zh': '日均纯酒精摄入量', 'unit': 'g/d',
                           'from': value, 'to': target, 'outputs': other, 'rr_delta': delta}]
    return data


def result_lines(result):
    lower, upper = result['ci_lower'], result['ci_upper']
    ci = '参照行未印出区间' if lower is None else f'{lower:.2f}–{upper:.2f}'
    lines = [f"匹配分档：{LABELS[result['category']]}；使用{STRATA[result['stratum']]}的完全调整列。", '',
             '| 全因死亡人群 RR | 人群估计的 95% 置信区间 |', '|---:|---|', f"| {result['rr']:.2f} | {ci} |"]
    if lower is None:
        lines += ['', 'RR=1 是参照定义，不表示没有死亡风险。']
    elif lower <= 1 <= upper:
        lines += ['', '该置信区间包含 1，未显示与终身不饮酒者存在统计学显著差异；这不等于证明安全或有保护作用。']
    else:
        lines += ['', '该分档的人群 RR 置信区间高于 1，表示观察研究中的风险升高关联。']
    return lines


def render(result, target=None):
    lines = [f'# {TITLE}', '', *paper_card_lines(), '', '## 你的查表结果', '',
             f"你提供的日均纯乙醇摄入量为 {result[INPUT_KEY]:g} g/d。", '', *result_lines(result), '',
             '参照是终身不饮酒者；性别分层时参照为相同性别的终身不饮酒者。RR 不是个人死亡概率，置信区间也不是个人预测区间。', '',
             '日均量需包含不饮酒的日子，不是每个饮酒日或单次的量。本文不能充分区分集中大量饮酒与分散饮酒；自报量可能低报，不据此做数值修正。', '',
             '研究主要汇总一般人群观察性队列；排除了仅按既有疾病或重度、问题性、依赖性饮酒筛选的队列。其结果未对你的疾病、地区或饮酒方式做校准。', '',
             '年龄仅作成人输入检查，不套用按队列中位年龄分组的表 3；没有年龄与性别联合的个人模型。']
    if result['category'] == 'former':
        lines += ['', '既往饮酒者的结果反映其历史暴露和人群差异，不能解释为停止饮酒导致风险升高，也不能预测停止饮酒后的变化。']
    if target is not None:
        lines += ['', '## 你指定的饮酒量情景', '', f'情景日均量：{target:g} g/d。只展示你指定的查表对照，不是饮酒建议。', '',
                  *result_lines(lookup(target, 'current', result['stratum'])), '',
                  '两档数值的差不是改变饮酒后的因果效应；同档数值相同也不代表真实风险相同。']
    lines += ['', f'边界: {BOUNDARY}']
    return '\n'.join(lines)+'\n'


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument('--measurements', type=Path)
    parser.add_argument('--targets', type=Path)
    parser.add_argument('--age', help='可选成人年龄，不参与查表')
    parser.add_argument('--sex', help='male/female；省略时用总体表')
    parser.add_argument('--drinking-status', help='current/former/lifetime_abstainer；零摄入时必须提供饮酒史')
    parser.add_argument('--out', type=Path, default=Path('out'))
    args = parser.parse_args(argv)
    manifest = skillkit.load_manifest(__file__)
    args.out.mkdir(parents=True, exist_ok=True)
    for name in ('problems.json', 'result.json', 'report.md', 'levers.json'):
        (args.out/name).unlink(missing_ok=True)
    values, problems = collect(args.measurements, manifest)
    value = values.get(INPUT_KEY)
    sex = args.sex or 'overall'
    if args.sex is not None and args.sex not in ('male', 'female'):
        problems.append(skillkit.Problem('sex', '性别', 'parse', '性别只接受 male 或 female；省略时使用总体表。'))
    if args.age is not None:
        try:
            age = skillkit.parse_number(args.age)
            problems += skillkit.check_scalar(manifest, 'age', age)
        except ValueError:
            problems.append(skillkit.Problem('age', '年龄', 'parse', '年龄须为有限数值。'))
    status = args.drinking_status
    if status is not None and status not in ('current', 'former', 'lifetime_abstainer'):
        problems.append(skillkit.Problem('drinking_status', '饮酒史', 'parse', '饮酒史只接受 current、former、lifetime_abstainer。'))
    if value is not None:
        if value == 0 and status not in ('former', 'lifetime_abstainer'):
            problems.append(skillkit.Problem('drinking_status', '饮酒史', 'missing',
                '零摄入不能区分终身不饮酒与既往饮酒者。请说明饮酒史：--drinking-status lifetime_abstainer 或 former；不能把近期未饮酒当作终身不饮酒。'))
        elif value > 0:
            if status in ('former', 'lifetime_abstainer'):
                problems.append(skillkit.Problem('drinking_status', '饮酒史', 'inconsistent', '非零日均量与不饮酒状态矛盾，请核对通常饮酒量与饮酒史。'))
            elif status is None:
                status = 'current'
    target = None
    if args.targets is not None:
        targets, errors = collect(args.targets, manifest, True)
        problems += errors
        target = targets.get(INPUT_KEY)
        if target is not None and (target == 0 or status != 'current'):
            problems.append(skillkit.Problem(INPUT_KEY, '目标情景', 'unsupported',
                '目标比较仅支持当前饮酒者的两个正值摄入量分档。论文未给出改变饮酒史后的风险轨迹，不能把零摄入目标映射为终身不饮酒或预测停止饮酒后的风险。'))
    if problems:
        path = skillkit.write_problems(args.out, problems, TITLE, BOUNDARY)
        body = path.read_text(encoding='utf-8').split('\n', 1)[1]
        path.write_text('\n'.join([f'# {TITLE}', '', *paper_card_lines(), '', body]), encoding='utf-8')
        skillkit.write_result(args.out, manifest, {s['key']: None for s in manifest['outputs']})
        return skillkit.EXIT_INPUT_PROBLEM
    result = lookup(value, status, sex)
    skillkit.write_result(args.out, manifest, result)
    (args.out/'report.md').write_text(render(result, target), encoding='utf-8')
    (args.out/'levers.json').write_text(json.dumps(levers(value, status, sex, target), ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
