"""Printed per-component scores: Guralnik et al. 1994, M87/M94.

The expected scores below are printed categories, not program-generated results.
"""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from personal_report import balance_score, timed_score, assess
from presets import INPUT_UNITS, WALK_BANDS, CHAIR_BANDS


def test_paper_walk_categories():
    # Table A1 footnote: Category 1: ≥ 5.7 sec.; Category 2: 4.1–5.6 sec.;
    # Category 3: 3.2–4.0 sec.; Category 4: ≤ 3.1 sec.
    for seconds, expected in [(5.7, 1), (4.1, 2), (5.6, 2),
                              (3.2, 3), (4.0, 3), (3.1, 4)]:
        assert timed_score(seconds, WALK_BANDS) == expected


def test_paper_chair_categories():
    # Table A2 footnote: Category 1: ≥ 16.7 sec.; Category 2: 13.7–16.6 sec.;
    # Category 3: 11.2–13.6 sec.; Category 4: ≤ 11.1 sec.
    for seconds, expected in [(16.7, 1), (13.7, 2), (16.6, 2),
                              (11.2, 3), (13.6, 3), (11.1, 4)]:
        assert timed_score(seconds, CHAIR_BANDS) == expected


def test_paper_balance_categories():
    # Table 1 columns: Category / Side-by-Side / Semi-tandem / Full Tandem.
    # 0 / 0–9 / < 10 / –; 1 / 10 / 0–9 / –;
    # 2 / – / 10 / 0–2; 3 / – / 10 / 3–9; 4 / – / 10 / 10.
    for side, semi, tandem, expected in [
        (0, 0, None, 0), (9, 9, None, 0), (10, 9, None, 1),
        (None, 10, 0, 2), (None, 10, 2, 2),
        (None, 10, 3, 3), (None, 10, 9, 3), (None, 10, 10, 4),
    ]:
        assert balance_score(semi, side, tandem) == expected


# Composite fixture combines printed component rows; it is not a printed person.
BASE = {'semi_tandem_s': (10, 's'), 'full_tandem_s': (10, 's'),
        'walk_completed': (1, '1'), 'walk_8ft_trial1_s': (5.7, 's'),
        'walk_8ft_trial2_s': (3.1, 's'), 'chair_completed': (1, '1'),
        'five_chair_stands_s': (11.1, 's')}


def run_cli(folder, rows, targets=None):
    path = folder / 'measurements.csv'
    path.write_text('item,value,unit\n' + ''.join(f'{k},{v},{u}\n' for k, (v, u) in rows.items()))
    cmd = [sys.executable, str(ROOT / 'scripts/personal_report.py'),
           '--measurements', str(path), '--out', str(folder / 'out')]
    if targets is not None:
        t = folder / 'targets.csv'
        t.write_text('item,value,unit\n' + ''.join(f'{k},{v},{u}\n' for k, (v, u) in targets.items()))
        cmd += ['--targets', str(t)]
    return subprocess.run(cmd, capture_output=True, text=True)


def test_manifest_units():
    manifest = json.loads((ROOT / 'skill.json').read_text())
    assert {s['key']: s['unit'] for s in manifest['inputs'] if s['from'] == 'measurements'} == INPUT_UNITS


def test_cli_printed_components_and_summary():
    with tempfile.TemporaryDirectory() as tmp:
        folder = Path(tmp)
        proc = run_cli(folder, BASE)
        assert proc.returncode == 0, proc.stderr
        result = json.loads((folder / 'out/result.json').read_text())['outputs']
        # Printed component outputs: Table 1 category 4; A1 category 4; A2 category 4.
        assert [result[k]['value'] for k in ('balance_score', 'walk_score', 'chair_score')] == [4, 4, 4]
        assert result['sppb_score']['value'] == sum(result[k]['value'] for k in ('balance_score', 'walk_score', 'chair_score'))
        report = (folder / 'out/report.md').read_text()
        assert report.index('论文卡片') < report.index('你的结果')
        assert '边界:' in report
        assert not (folder / 'out/problems.json').exists()


def test_input_failures_and_no_stale_result():
    cases = [dict(BASE, walk_8ft_trial1_s=(5.7, 'kg')),
             dict(BASE, full_tandem_s=(11, 's')),
             {k: v for k, v in BASE.items() if k != 'chair_completed'},
             {k: v for k, v in BASE.items() if k != 'walk_8ft_trial2_s'},
             dict(BASE, five_chair_stands_s=(11.15, 's')),
             dict(BASE, full_tandem_s=(2.5, 's')),
             dict(BASE, walk_completed=(0.5, '1')),
             dict(BASE, chair_completed=(0, '1')),
             dict(BASE, semi_tandem_s=(9, 's'), side_by_side_s=(10, 's')),
             dict(BASE, five_chair_stands_s=('nan', 's'))]
    for rows in cases:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            assert run_cli(folder, BASE).returncode == 0
            proc = run_cli(folder, rows)
            assert proc.returncode == 3, (proc.stdout, proc.stderr, rows)
            out = folder / 'out'
            assert json.loads((out / 'problems.json').read_text())['problems']
            assert not (out / 'result.json').exists()
            assert not (out / 'levers.json').exists()
            assert '你的结果' not in (out / 'report.md').read_text()
            assert '论文卡片' in (out / 'report.md').read_text()


def test_known_inability_is_not_missing():
    rows = {'semi_tandem_s': (0, 's'), 'side_by_side_s': (0, 's'),
            'walk_completed': (0, '1'), 'chair_completed': (0, '1')}
    with tempfile.TemporaryDirectory() as tmp:
        folder = Path(tmp)
        assert run_cli(folder, rows).returncode == 0
        outputs = json.loads((folder / 'out/result.json').read_text())['outputs']
        # M86 assigns unable-to-complete walk/chair a printed score of 0; Table 1 gives balance 0.
        assert all(item['value'] == 0 for item in outputs.values())


def test_units_and_target_scenarios():
    with tempfile.TemporaryDirectory() as tmp:
        folder = Path(tmp)
        converted = dict(BASE)
        del converted['walk_8ft_trial2_s']
        converted['8英尺步行第二次时间'] = (3100, 'ms')
        assert run_cli(folder, converted, {'five_chair_stands_s': (16.7, 's')}).returncode == 0
        levers = json.loads((folder / 'out/levers.json').read_text())
        assert levers['targets']['outputs']['chair_score'] == 1  # Table A2
        assert levers['levers'][0]['outputs']['chair_score'] == 1
        assert levers['targets']['sppb_score_delta'] == levers['levers'][0]['sppb_score_delta']
        assert levers['sensitivity']
        # Target times may not be attached to a declared inability.
        assert run_cli(folder, BASE, {'chair_completed': (0, '1')}).returncode == 3


if __name__ == '__main__':
    tests = [unittest.FunctionTestCase(v) for k, v in list(globals().items())
             if k.startswith('test_') and callable(v)]
    result = unittest.TextTestRunner().run(unittest.TestSuite(tests))
    raise SystemExit(not result.wasSuccessful())
