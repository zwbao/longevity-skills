"""Printed per-term checks first; full personal examples lack Townsend.

Tables 3/4, model C: rheumatoid arthritis HR 1.24/1.23 and cholesterol
ratio (per unit) HR 1.17/1.19. These do not validate absolute risk.
No manufactured expected personal score: CLI output is compared to the
frozen, published ClinRisk C function in test_reference.py.
"""
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import presets

MANIFEST = json.loads((ROOT / 'skill.json').read_text())


def sample():
    # Synthetic operational fixture, not a paper example.
    v = {key: 0 for key in presets.BINARY_KEYS}
    v.update(bmi_kg_m2=27, tc_hdl_ratio=4, sbp_mmhg=130, sbp_sd_mmhg=10,
             townsend_score=0.5, ethnicity=1, smoking=0, sbp_readings_n=3,
             prior_cvd=0, statin_use=0)
    return v


def run_cli(values, sex='male', age='44', targets=None, out=None):
    td = Path(tempfile.mkdtemp())
    path = td / 'input.csv'
    specs = {x['key']: x for x in MANIFEST['inputs']}
    path.write_text('marker,value,unit\n' + ''.join(
        f'{k},{v},{specs[k].get("unit", "")}\n' for k, v in values.items()))
    out = out or td / 'out'
    cmd = [sys.executable, str(ROOT / 'scripts/personal_report.py'),
           '--measurements', str(path), '--out', str(out)]
    if age is not None: cmd += ['--age', age]
    if sex is not None: cmd += ['--sex', sex]
    if targets is not None:
        target = td / 'targets.csv'
        target.write_text(targets)
        cmd += ['--targets', str(target)]
    return subprocess.run(cmd, capture_output=True, text=True), out


class ManifestTests(unittest.TestCase):
    def test_printed_term_hazard_ratios(self):
        for sex, ra_hr, ratio_hr in [('female', 1.24, 1.17), ('male', 1.23, 1.19)]:
            base = sample()
            p = presets.risk(44, sex, base) / 100
            for key, increment, expected in [('b_ra', 1, ra_hr), ('tc_hdl_ratio', 1, ratio_hr)]:
                changed = dict(base)
                changed[key] += increment
                q = presets.risk(44, sex, changed) / 100
                hr = math.log1p(-q) / math.log1p(-p)
                self.assertAlmostEqual(hr, expected, delta=0.005)

    def test_manifest_units(self):
        specs = {x['key']: x for x in MANIFEST['inputs']}
        for key, unit in presets.MODEL_UNITS.items():
            self.assertEqual(specs[key]['unit'], unit)
        self.assertEqual(MANIFEST['validation']['status'], 'draft')

    def test_valid_output_and_targets(self):
        result, out = run_cli(sample(), targets='marker,value,unit\nsbp,120,mmHg\nBMI,25,kg/m^2\n')
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads((out / 'result.json').read_text())
        self.assertEqual(payload['outputs']['risk_10y_pct']['value'], presets.risk(44, 'male', sample()))
        levers = json.loads((out / 'levers.json').read_text())
        self.assertEqual(len(levers['levers']), 2)
        changed = dict(sample(), sbp_mmhg=120, bmi_kg_m2=25)
        self.assertEqual(levers['targets']['risk_10y_pct'], presets.risk(44, 'male', changed))
        report = (out / 'report.md').read_text()
        self.assertLess(report.index('论文卡片'), report.index('你的结果'))
        self.assertIn('边界', report)
        self.assertIn('仍在验证', report)

    def test_bad_inputs_exit_three_and_no_stale_scores(self):
        good, out = run_cli(sample())
        self.assertEqual(good.returncode, 0, good.stderr)
        cases = [dict(sample(), sbp_mmhg=1000), dict(sample(), smoking=1.5),
                 dict(sample(), b_type1=1, b_type2=1), dict(sample(), prior_cvd=1),
                 dict(sample(), statin_use=1), dict(sample(), sbp_readings_n=1)]
        missing = sample(); missing.pop('townsend_score'); cases.append(missing)
        missing = sample(); missing.pop('b_impotence2'); cases.append(missing)
        for vals in cases:
            result, _ = run_cli(vals, out=out)
            self.assertEqual(result.returncode, 3, result.stderr)
            self.assertTrue((out / 'problems.json').exists())
            self.assertFalse((out / 'result.json').exists())
            self.assertFalse((out / 'levers.json').exists())
            self.assertNotIn('你的结果', (out / 'report.md').read_text())
        for age, sex in [('nan','male'), ('44.5','male'), (None,'male'), ('44',None), ('44','other')]:
            result, _ = run_cli(sample(), age=age, sex=sex)
            self.assertEqual(result.returncode, 3, result.stderr)

    def test_bad_units_and_targets(self):
        for targets in ['marker,value,unit\nsbp,120,mg/dL\n',
                        'marker,value,unit\nb_type1,1,1\n',
                        'marker,value,unit\nunknown,1,1\n']:
            result, out = run_cli(sample(), targets=targets)
            self.assertEqual(result.returncode, 3, result.stderr)
            self.assertFalse((out / 'result.json').exists())
        # Wrong unit in the measurement file itself, not just targets.
        rows = [{'marker':k, 'value':str(v), 'unit':next(x.get('unit','') for x in MANIFEST['inputs'] if x['key']==k)} for k,v in sample().items()]
        next(x for x in rows if x['marker']=='sbp_mmhg')['unit']='mg/dL'
        import skillkit
        self.assertTrue(any(p.kind=='unit' for p in skillkit.collect_measurements(rows, MANIFEST).problems))

    def test_female_does_not_require_erectile_flag(self):
        vals = sample(); vals.pop('b_impotence2')
        result, out = run_cli(vals, sex='female')
        self.assertEqual(result.returncode, 0, result.stderr)

if __name__ == '__main__':
    unittest.main()
