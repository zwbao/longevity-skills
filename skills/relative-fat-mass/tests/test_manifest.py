"""Engineering checks, NOT reproduction of a printed personal example.

The paper prints Eqs. (1–3) but no paired individual inputs/output.
Synthetic rows below test the contract; validation must remain draft.
"""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import presets

MANIFEST = json.loads((ROOT / 'skill.json').read_text())


class ManifestTests(unittest.TestCase):
    def run_report(self, directory, rows='height_cm,170,cm\nwaist_cm,85,cm\n',
                   age='40', sex='male', targets=None):
        directory = Path(directory)
        source = directory / 'measurements.csv'
        source.write_text('marker,value,unit\n' + rows)
        command = [sys.executable, str(ROOT / 'scripts/personal_report.py'),
                   '--measurements', str(source), '--out', str(directory / 'out')]
        if age is not None:
            command += ['--age', age]
        if sex is not None:
            command += ['--sex', sex]
        if targets is not None:
            target = directory / 'targets.csv'
            target.write_text('marker,value,unit\n' + targets)
            command += ['--targets', str(target)]
        result = subprocess.run(command, capture_output=True, text=True)
        return result, directory / 'out'

    def test_manifest_constants_and_units(self):
        # Printed Eq. (3): 64 - (20 × height/waist) + (12 × sex).
        self.assertEqual(presets.INTERCEPT, 64)
        self.assertEqual(presets.RATIO_COEFFICIENT, -20)
        self.assertEqual(presets.SEX_COEFFICIENT, 12)
        specs = {s['key']: s for s in MANIFEST['inputs']}
        for key, unit in presets.INPUT_UNITS.items():
            self.assertEqual(specs[key]['unit'], unit)
        self.assertEqual(MANIFEST['validation']['status'], 'draft')
        self.assertEqual(MANIFEST['inputs_status'], 'draft')

    def test_result_uses_published_sex_specific_equations(self):
        # Synthetic input; expected expressions are printed Eqs. (1) and (2).
        # These are not paper examples and are not used to claim reproduction.
        for sex, intercept in [('female', 76), ('male', 64)]:
            with self.subTest(sex=sex), tempfile.TemporaryDirectory() as d:
                result, out = self.run_report(d, sex=sex)
                self.assertEqual(result.returncode, 0, result.stderr)
                payload = json.loads((out / 'result.json').read_text())
                self.assertAlmostEqual(payload['outputs']['rfm_pct']['value'],
                                       intercept - 20 * (170 / 85))
                report = (out / 'report.md').read_text()
                self.assertLess(report.index('论文卡片'), report.index('你的结果'))
                self.assertIn(presets.BOUNDARY, report)
                self.assertIn('暂定', report)
                self.assertTrue((out / 'levers.json').exists())

    def test_aliases_and_exact_unit_conversions(self):
        sources = ['身高,1.7,m\n腰围,850,mm\n',
                   'Height,170,cm\nWaist circumference,85,cm\n',
                   f'height_cm,{170 / 2.54},in\nwaist_cm,{85 / 2.54},in\n']
        values = []
        for rows in sources:
            with tempfile.TemporaryDirectory() as d:
                result, out = self.run_report(d, rows)
                self.assertEqual(result.returncode, 0, result.stderr)
                values.append(json.loads((out / 'result.json').read_text())['outputs']['rfm_pct']['value'])
        for value in values:
            self.assertAlmostEqual(value, values[0])

    def test_bad_inputs_clear_stale_outputs_and_exit_three(self):
        cases = [
            ('height_cm,170,kg\nwaist_cm,85,cm\n', '40', 'male', None),
            ('height_cm,1700,cm\nwaist_cm,85,cm\n', '40', 'male', None),
            ('height_cm,170,cm\n', '40', 'male', None),
            ('身高,170,\n腰围,85,cm\n', '40', 'male', None),
            ('height_cm,nan,cm\nwaist_cm,85,cm\n', '40', 'male', None),
            ('height_cm,170,cm\nwaist_cm,85,cm\n', None, 'male', None),
            ('height_cm,170,cm\nwaist_cm,85,cm\n', '19', 'male', None),
            ('height_cm,170,cm\nwaist_cm,85,cm\n', 'nan', 'male', None),
            ('height_cm,170,cm\nwaist_cm,85,cm\n', '40', None, None),
            ('height_cm,170,cm\nwaist_cm,85,cm\n', '40', '0.5', None),
            ('height_cm,170,cm\nwaist_cm,85,cm\n', '40', 'male', 'waist_cm,80,kg\n'),
            ('height_cm,170,cm\nwaist_cm,85,cm\n', '40', 'male', 'height_cm,180,cm\n'),
            ('height_cm,170,cm\nwaist_cm,85,cm\n', '40', 'male', 'unknown,80,cm\n'),
            ('height_cm,170,cm\nwaist_cm,30,cm\n', '40', 'male', None),
            ('height_cm,170,cm\nwaist_cm,85,cm\n', '40', 'male', 'waist_cm,30,cm\n'),
        ]
        for rows, age, sex, targets in cases:
            with self.subTest(rows=rows, age=age, sex=sex, targets=targets), tempfile.TemporaryDirectory() as d:
                self.run_report(d)
                result, out = self.run_report(d, rows, age, sex, targets)
                self.assertEqual(result.returncode, 3, result.stderr)
                self.assertTrue(json.loads((out / 'problems.json').read_text())['problems'])
                self.assertFalse((out / 'result.json').exists())
                self.assertFalse((out / 'levers.json').exists())
                report = (out / 'report.md').read_text()
                self.assertIn('论文卡片', report)
                self.assertIn(presets.BOUNDARY, report)
                self.assertNotIn('你的结果', report)

    def test_targets_and_sensitivities_match_finite_differences(self):
        with tempfile.TemporaryDirectory() as d:
            result, out = self.run_report(d, targets='腰围,80,cm\n')
            self.assertEqual(result.returncode, 0, result.stderr)
            levers = json.loads((out / 'levers.json').read_text())
            self.assertAlmostEqual(levers['targets']['rfm_pct'], 64 - 20 * (170 / 80))
            self.assertAlmostEqual(levers['levers'][0]['rfm_delta_pp'],
                                   levers['targets']['rfm_pct'] - levers['current']['rfm_pct'])
            self.assertLess(levers['levers'][0]['rfm_delta_pp'], 0)
            for item in levers['sensitivity']:
                if item['key'] not in ('height_cm', 'waist_cm'):
                    continue
                vals = {'height_cm': 170, 'waist_cm': 85}
                step = 1e-4
                vals[item['key']] += step
                high = 64 - 20 * vals['height_cm'] / vals['waist_cm']
                vals[item['key']] -= 2 * step
                low = 64 - 20 * vals['height_cm'] / vals['waist_cm']
                self.assertAlmostEqual(item['rfm_pp_per_unit'], (high - low) / (2 * step), places=7)

    def test_age_is_context_and_sex_codes_are_explicit(self):
        values = []
        for age, sex in [('40', 'female'), ('75', '1'), ('95', '女')]:
            with tempfile.TemporaryDirectory() as d:
                result, out = self.run_report(d, age=age, sex=sex)
                self.assertEqual(result.returncode, 0, result.stderr)
                values.append(json.loads((out / 'result.json').read_text())['outputs']['rfm_pct']['value'])
                if age != '40':
                    self.assertIn('验证年龄范围', (out / 'report.md').read_text())
        self.assertEqual(values[0], values[1])
        self.assertEqual(values[1], values[2])

    def test_missing_file_is_structured_input_problem(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / 'out'
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/personal_report.py'),
                '--measurements', str(Path(d) / 'missing.csv'), '--age', '40', '--sex', 'male',
                '--out', str(out)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 3, result.stderr)
            self.assertTrue((out / 'problems.json').exists())


if __name__ == '__main__':
    unittest.main()
