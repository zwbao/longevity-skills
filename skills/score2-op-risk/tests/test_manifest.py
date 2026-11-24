"""Printed examples first: published supplement, Methods Table 3 (p. 14).

Female/male: age 75, TC 5.5, HDL 1.3 mmol/L, SBP 140 mmHg,
no diabetes, current smoker. Original risk: 24.4%, 29.7%; low-region:
14%, 19.3%. The last two use scales inconsistent with Methods Table 1.
"""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from personal_report import compute
import presets

EXAMPLE = {'sbp_mmhg': 140, 'tc_mmol_l': 5.5, 'hdl_mmol_l': 1.3,
           'smoker': 1, 'diabetes': 0}

class TestManifest(unittest.TestCase):
    def test_printed_original_risks(self):
        for sex, expected in [('female', 24.4), ('male', 29.7)]:
            with self.subTest(sex=sex):
                self.assertAlmostEqual(compute(EXAMPLE, 75, sex, 'low')['original_risk_10y_pct'],
                                       expected, delta=0.05)

    @unittest.expectedFailure
    def test_printed_female_calibrated_risk_unresolved(self):
        self.assertAlmostEqual(compute(EXAMPLE, 75, 'female', 'low')['risk_10y_pct'],
                               14.0, delta=0.05)

    @unittest.expectedFailure
    def test_printed_male_calibrated_risk_unresolved(self):
        self.assertAlmostEqual(compute(EXAMPLE, 75, 'male', 'low')['risk_10y_pct'],
                               19.3, delta=0.05)


    def test_manifest_matches_presets(self):
        manifest = json.loads((ROOT/'skill.json').read_text())
        specs = {s['key']: s for s in manifest['inputs']}
        for key, unit in presets.MEASUREMENT_UNITS.items():
            self.assertEqual(specs[key]['unit'], unit)
        for key, bounds in presets.INPUT_RANGES.items():
            self.assertEqual(specs[key]['range'], list(bounds))
        self.assertEqual(manifest['validation']['status'], 'draft')
        self.assertEqual(set(presets.COEFFICIENTS), {'male', 'female'})
        self.assertEqual(len(presets.COUNTRIES), 4)

    def run_cli(self, folder, csv=None, targets=None, **flags):
        folder = Path(folder)
        measurements = folder/'input.csv'
        measurements.write_text(csv if csv is not None else
            'marker,value,unit\nSBP,140,mmHg\nTC,5.5,mmol/L\nHDL-C,1.3,mmol/L\nsmoker,1,1\ndiabetes,0,1\n')
        args = {'age': '75', 'sex': 'female', 'country': 'France', 'prior-cvd': 'no'}
        args.update(flags)
        command = [sys.executable, str(ROOT/'scripts/personal_report.py'),
                   '--measurements', str(measurements), '--out', str(folder/'out')]
        for key, value in args.items():
            if value is not None:
                command += ['--'+key, str(value)]
        if targets is not None:
            path = folder/'targets.csv'
            path.write_text(targets)
            command += ['--targets', str(path)]
        result = subprocess.run(command, capture_output=True, text=True)
        return result, folder/'out'

    def assert_input_problem(self, run, out):
        self.assertEqual(run.returncode, 3, run.stderr)
        self.assertTrue(json.loads((out/'problems.json').read_text())['problems'])
        result = json.loads((out/'result.json').read_text())
        self.assertTrue(all(x['value'] is None for x in result['outputs'].values()))
        self.assertFalse((out/'levers.json').exists())
        report = (out/'report.md').read_text()
        self.assertIn('边界:', report)
        self.assertIn('10.1093/eurheartj/ehab312', report)
        self.assertNotIn('**', report.split('## 输入没有通过检查')[-1])

    def test_cli_printed_original_risk_and_report(self):
        with tempfile.TemporaryDirectory() as folder:
            run, out = self.run_cli(folder)
            self.assertEqual(run.returncode, 0, run.stderr)
            result = json.loads((out/'result.json').read_text())['outputs']
            self.assertAlmostEqual(result['original_risk_10y_pct']['value'], 24.4, delta=0.05)
            self.assertEqual(result['risk_region']['value'], 'low')
            report = (out/'report.md').read_text()
            self.assertLess(report.index('10.1093/eurheartj/ehab312'), report.index('## 本次估计'))
            self.assertIn('仍在验证', report)
            self.assertIn(presets.BOUNDARY, report)
            self.assertFalse((out/'problems.json').exists())

    def test_unit_conversions_preserve_printed_example(self):
        factor = 10/386.65
        csv = ('marker,value,unit\n收缩压,'+str(140/7.500617)+',kPa\n总胆固醇,'+
               str(5.5/factor)+',mg/dL\n高密度脂蛋白胆固醇,'+str(1.3/factor)+
               ',mg/dL\n当前吸烟,1,1\n糖尿病史,0,1\n')
        with tempfile.TemporaryDirectory() as folder:
            run, out = self.run_cli(folder, csv=csv)
            self.assertEqual(run.returncode, 0, run.stderr)
            actual = json.loads((out/'result.json').read_text())['outputs']['original_risk_10y_pct']['value']
            self.assertAlmostEqual(actual, 24.4, delta=0.05)

    def test_invalid_measurements_clear_previous_result(self):
        base = 'marker,value,unit\nSBP,140,mmHg\nTC,5.5,mmol/L\nHDL-C,1.3,mmol/L\nsmoker,1,1\ndiabetes,0,1\n'
        cases = [base.replace('140,mmHg', '140,mg/dL'),
                 base.replace('140,mmHg', '999,mmHg'),
                 base.replace('5.5,mmol/L', '5.5,'),
                 base.replace('5.5,mmol/L', 'NaN,mmol/L'),
                 base.replace('1.3,mmol/L', '6,mmol/L'),
                 base.replace('smoker,1,1', 'smoker,0.5,1'),
                 base.replace('diabetes,0,1\n', ''),
                 base+'SBP,160,mmHg\n']
        for bad in cases:
            with self.subTest(csv=bad), tempfile.TemporaryDirectory() as folder:
                run, out = self.run_cli(folder)
                self.assertEqual(run.returncode, 0)
                run, out = self.run_cli(folder, csv=bad)
                self.assert_input_problem(run, out)

    def test_missing_or_wrong_profile(self):
        cases = [{'age': None}, {'age': 'bad'}, {'age': 'nan'}, {'age': 'inf'},
                 {'age': 69}, {'age': 90}, {'sex': None}, {'sex': 'other'},
                 {'country': 'China'}, {'country': None}, {'prior-cvd': None}, {'prior-cvd': 'yes'}]
        for args in cases:
            with self.subTest(args=args), tempfile.TemporaryDirectory() as folder:
                run, out = self.run_cli(folder, **args)
                self.assert_input_problem(run, out)

    def test_invalid_targets_stop_computation(self):
        cases = ['marker,value,unit\nSBP,120,mg/dL\n',
                 'marker,value,unit\nSBP,999,mmHg\n',
                 'marker,value,unit\nsmoker,0.5,1\n',
                 'marker,value,unit\ndiabetes,0,1\n',
                 'marker,value,unit\nunknown,100,1\n',
                 'marker,value,unit\n',
                 'marker,value,unit\nTC,1,mmol/L\n',
                 # Both targets together are coherent, but TC alone is not.
                 'marker,value,unit\nTC,1,mmol/L\nHDL-C,0.5,mmol/L\n']
        for targets in cases:
            with self.subTest(targets=targets), tempfile.TemporaryDirectory() as folder:
                run, out = self.run_cli(folder, targets=targets)
                self.assert_input_problem(run, out)

    def test_target_identity_and_sensitivity(self):
        with tempfile.TemporaryDirectory() as folder:
            run, out = self.run_cli(folder, targets='marker,value,unit\nSBP,140,mmHg\n')
            self.assertEqual(run.returncode, 0, run.stderr)
            data = json.loads((out/'levers.json').read_text())
            self.assertEqual(data['targets']['risk_delta_pct'], 0)
            self.assertEqual(data['levers'][0]['risk_delta_pct'], 0)
            self.assertEqual(data['validation_status'], 'draft')
            self.assertEqual(len(data['sensitivity']), 4)
            for item in data['sensitivity']:
                key = item['key']
                if key == 'smoker':
                    hi = compute(dict(EXAMPLE, smoker=1), 75, 'female', 'low')['risk_10y_pct']
                    lo = compute(dict(EXAMPLE, smoker=0), 75, 'female', 'low')['risk_10y_pct']
                    numerical = hi-lo
                else:
                    step = 1e-4
                    hi = compute(dict(EXAMPLE, **{key: EXAMPLE[key]+step}), 75, 'female', 'low')['risk_10y_pct']
                    lo = compute(dict(EXAMPLE, **{key: EXAMPLE[key]-step}), 75, 'female', 'low')['risk_10y_pct']
                    numerical = (hi-lo)/(2*step)
                self.assertAlmostEqual(item['per_unit'], numerical, delta=1e-6)

    def test_all_regions_and_target_scenarios(self):
        for country, region in [('France','low'),('USA','moderate'),('Poland','high'),('Egypt','very_high')]:
            for sex in ('male', 'female'):
                with self.subTest(country=country, sex=sex), tempfile.TemporaryDirectory() as folder:
                    run, out = self.run_cli(folder, country=country, sex=sex,
                       targets='marker,value,unit\nSBP,130,mmHg\nTC,5,mmol/L\nsmoker,0,1\n')
                    self.assertEqual(run.returncode, 0, run.stderr)
                    result = json.loads((out/'result.json').read_text())['outputs']
                    self.assertEqual(result['risk_region']['value'], region)
                    self.assertTrue(0 < result['risk_10y_pct']['value'] < 100)
                    data = json.loads((out/'levers.json').read_text())
                    self.assertEqual(len(data['levers']), 3)
                    self.assertLess(data['targets']['risk_pct'], data['current']['risk_pct'])

    def test_missing_files_write_problems(self):
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder)/'out'
            run = subprocess.run([sys.executable, str(ROOT/'scripts/personal_report.py'),
                '--measurements', str(Path(folder)/'absent.csv'), '--targets', str(Path(folder)/'absent-targets.csv'),
                '--age', '75', '--sex', 'female', '--country', 'France', '--prior-cvd', 'no', '--out', str(out)],
                capture_output=True, text=True)
            self.assert_input_problem(run, out)

if __name__ == '__main__':
    unittest.main()
