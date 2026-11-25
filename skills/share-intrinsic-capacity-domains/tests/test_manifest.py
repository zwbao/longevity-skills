"""Paper-first tests: Table 1's printed per-item scores, not invented patients.

The integration fixtures are synthetic input-contract checks, not published
individual cases. No aggregate cohort mean is treated as a personal example.
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import personal_report as report
import presets
import skillkit


def test_table1_delayed_recall_scores():
    # Table 1: "0–1 words were scored 0; 2–3 words scored 1; 4 words scored
    # 2 points; 5–6 words scored 3; 7–8 words scored 4; and 9–10 words scored 5"
    printed = [(0, 0), (1, 0), (2, 1), (3, 1), (4, 2),
               (5, 3), (6, 3), (7, 4), (8, 4), (9, 5), (10, 5)]
    for words, points in printed:
        assert report.item_score('delayed_recall_count', words) == points


def test_table1_fluency_scores():
    # Table 1: "0–5 words were scored 0; 6–9 scored as 1 point; 10–13 2
    # points; 14–17 3 points, and 18 + scored 4 points (0–4 points)"
    for words, points in [(0, 0), (5, 0), (6, 1), (9, 1), (10, 2),
                          (13, 2), (14, 3), (17, 3), (18, 4)]:
        assert report.item_score('animal_fluency_count', words) == points


def test_table1_locomotion_and_sensory_scores():
    # Table 1: difficulty/aid yes -> 0 points; no -> 2 points.
    # Sensory ratings: "5 scored 0, 3–4 scored 1, 1–2 scored 2".
    for key in presets.BINARY_KEYS:
        assert report.item_score(key, 1) == 0
        assert report.item_score(key, 0) == 2
    for key in presets.RATING_KEYS:
        for rating, points in [(5, 0), (3, 1), (4, 1), (1, 2), (2, 2)]:
            assert report.item_score(key, rating) == points


def manifest():
    return json.loads((ROOT / 'skill.json').read_text())


def run(tmp_path, rows, extra=()):
    path = tmp_path / 'inputs.csv'
    path.write_text('item,value,unit\n' + '\n'.join(','.join(map(str, r)) for r in rows) + '\n')
    out = tmp_path / 'out'
    code = report.main(['--measurements', str(path), '--out', str(out), *extra])
    return code, json.loads((out / 'result.json').read_text())['outputs'], out


def cognition_rows():
    # Synthetic upper endpoints; raw maxima are printed in Table 1.
    return [('orientation_correct_count', 4, '1'), ('animal_fluency_count', 18, '1'),
            ('serial_sevens_correct_count', 5, '1'), ('delayed_recall_count', 10, '1')]


def test_manifest_matches_presets_and_standardization(tmp_path):
    specs = {s['key']: s for s in manifest()['inputs'] if s['from'] == 'measurements'}
    assert set(specs) == set(presets.INPUTS)
    for key, spec in specs.items():
        assert spec['unit'] == presets.INPUTS[key]['unit']
        assert spec['range'] == list(presets.INPUTS[key]['range'])
    # Table 1 prints maxima 18, 10, 10; Methods prints standardized range 0–10.
    assert presets.RAW_MAX == {'cognition': 18, 'locomotion': 10, 'sensory': 10}
    code, outputs, out = run(tmp_path, cognition_rows())
    assert code == 0
    assert outputs['cognition_raw']['value'] == 18
    assert outputs['cognition_score']['value'] == 10
    assert outputs['locomotion_score']['value'] is None
    text = (out / 'report.md').read_text()
    assert text.startswith('## 论文卡片')
    assert presets.BOUNDARY in text
    assert '总分' in text


@pytest.mark.parametrize('bad_value,bad_unit', [(10, 'kg'), (11, '1'), (4.5, '1'), ('nan', '1')])
def test_bad_inputs_exit_3(tmp_path, bad_value, bad_unit):
    rows = cognition_rows()
    rows[-1] = ('delayed_recall_count', bad_value, bad_unit)
    code, outputs, out = run(tmp_path, rows)
    assert code == 3
    assert all(item['value'] is None for item in outputs.values())
    assert json.loads((out / 'problems.json').read_text())['problems']
    assert (out / 'report.md').read_text().startswith('## 论文卡片')


def test_partial_domain_requires_missing_items(tmp_path):
    code, outputs, out = run(tmp_path, cognition_rows()[:-1])
    assert code == 3
    problems = json.loads((out / 'problems.json').read_text())['problems']
    assert any(p['key'] == 'delayed_recall_count' and p['kind'] == 'missing' for p in problems)
    assert all(item['value'] is None for item in outputs.values())


def test_empty_input_explains_required_measurements(tmp_path):
    code, _, out = run(tmp_path, [])
    assert code == 3
    assert '认知' in (out / 'report.md').read_text()


def test_aliases_and_standalone_locomotion(tmp_path):
    specs = [s for s in manifest()['inputs'] if s.get('group') == 'locomotion']
    rows = [(s['aliases'][0], 0, '1') for s in specs]
    code, outputs, _ = run(tmp_path, rows)
    assert code == 0
    assert outputs['locomotion_raw']['value'] == 10
    assert outputs['locomotion_score']['value'] == 10
    assert outputs['cognition_score']['value'] is None


def test_baseline_and_stale_outputs(tmp_path):
    rows = cognition_rows()
    baseline = tmp_path / 'baseline.csv'
    baseline.write_text('item,value,unit\n' + '\n'.join(f'{key},0,1' for key, _, _ in rows))
    code, outputs, out = run(tmp_path, rows, ['--baseline', str(baseline)])
    assert code == 0
    assert outputs['cognition_baseline_score']['value'] == 0
    assert outputs['cognition_change']['value'] == outputs['cognition_score']['value'] - outputs['cognition_baseline_score']['value']
    code, outputs, out = run(tmp_path, rows[:-1])
    assert code == 3
    assert all(item['value'] is None for item in outputs.values())
    code, outputs, out = run(tmp_path, rows)
    assert code == 0
    assert not (out / 'problems.json').exists()
    assert outputs['cognition_change']['value'] is None


def test_baseline_missing_domain_and_unknown_measurement(tmp_path):
    baseline = tmp_path / 'baseline.csv'
    baseline.write_text('item,value,unit\nph048d1,0,1\n')
    code, _, out = run(tmp_path, cognition_rows(), ['--baseline', str(baseline)])
    assert code == 3
    code, _, out = run(tmp_path, cognition_rows() + [('casp', 40, 'score')])
    assert code == 3


def test_missing_file_and_invalid_age(tmp_path):
    out = tmp_path / 'out'
    assert report.main(['--measurements', str(tmp_path / 'absent.csv'), '--out', str(out)]) == 3
    assert (out / 'problems.json').exists()
    code, _, _ = run(tmp_path, cognition_rows(), ['--age', 'bad'])
    assert code == 3
