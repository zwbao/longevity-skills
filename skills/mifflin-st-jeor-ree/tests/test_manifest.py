"""Printed cohort means, not invented patients: Mifflin 1990 Tables 1 and 3."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
spec = importlib.util.spec_from_file_location('msj_report', ROOT / 'scripts/personal_report.py')
report = importlib.util.module_from_spec(spec)
spec.loader.exec_module(report)
from presets import INPUT_UNITS


def test_printed_table3_means():
    # Table 1: All men (n = 251): 87.5 ± 14.4 kg, 178.3 ± 6.8 cm, 44.4 ± 14.3 y.
    # Table 3: MSJE males 1775 ± 192 kcal/d.
    # Table 1: All women (n = 247): 70.2 ± 14.1 kg, 164.2 ± 6.3 cm, 44.6 ± 14.0 y.
    # Table 3: MSJE females 1348 ± 179 kcal/d.
    # Linear prediction commutes with taking means. Input rounding plus output
    # rounding allows 0.05*(9.99+6.25+4.92)+0.5 = 1.558 kcal/d; use 1.6.
    for weight, height, age, sex, expected in [
        (87.5, 178.3, 44.4, 'male', 1775),
        (70.2, 164.2, 44.6, 'female', 1348),
    ]:
        result = report.calculate({'weight_kg': weight, 'height_cm': height}, age, sex)
        assert abs(result['ree_original_kcal_d'] - expected) <= 1.6
        # Eqs 7–8 round weight/age coefficients. Account for that known change,
        # without asserting a self-generated expected value for the rounded model.
        rounding_shift = 0.01 * weight - 0.08 * age
        assert abs(result['ree_simplified_kcal_d'] - rounding_shift - expected) <= 1.6


class ManifestTests(unittest.TestCase):
    def test_printed_means(self):
        test_printed_table3_means()

    def test_manifest_units(self):
        manifest = json.loads((ROOT / 'skill.json').read_text())
        self.assertEqual({x['key']: x.get('unit', '') for x in manifest['inputs']}, INPUT_UNITS)

    def cli(self, folder, raw='marker,value,unit\n体重,87.5,kg\n身高,178.3,cm\n',
            age='44.4', sex='male', targets=None):
        path = folder / 'measurements.csv'
        path.write_text(raw)
        cmd = [sys.executable, str(ROOT / 'scripts/personal_report.py'),
               '--measurements', str(path), '--out', str(folder / 'out')]
        if age is not None:
            cmd += ['--age', age]
        if sex is not None:
            cmd += ['--sex', sex]
        if targets is not None:
            path = folder / 'targets.csv'
            path.write_text(targets)
            cmd += ['--targets', str(path)]
        return subprocess.run(cmd, capture_output=True, text=True)

    def test_cli_result_and_card(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            run = self.cli(folder)
            self.assertEqual(run.returncode, 0, run.stderr)
            data = json.loads((folder / 'out/result.json').read_text())['outputs']
            self.assertAlmostEqual(data['ree_original_kcal_d']['value'], 1775, delta=1.6)
            text = (folder / 'out/report.md').read_text()
            self.assertLess(text.index('论文卡片'), text.index('你的结果'))
            self.assertIn('边界：', text)
            self.assertIn('每日总能量消耗', text)
            self.assertTrue((folder / 'out/levers.json').exists())

    def test_invalid_inputs_clear_stale_outputs(self):
        cases = [
            {'raw': 'marker,value,unit\nweight_kg,87.5,cm\nheight_cm,178.3,cm\n'},
            {'raw': 'marker,value,unit\nweight_kg,875,kg\nheight_cm,178.3,cm\n'},
            {'raw': 'marker,value,unit\nweight_kg,87.5,kg\n'},
            {'raw': 'marker,value,unit\n体重,87.5,\n身高,178.3,cm\n'},
            {'raw': 'marker,value,unit\nweight_kg,nan,kg\nheight_cm,178.3,cm\n'},
            {'age': None}, {'age': 'oops'}, {'age': 'nan'}, {'age': '18'}, {'age': '79'},
            {'sex': None}, {'sex': 'unknown'},
            {'targets': 'marker,value,unit\nweight_kg,70,cm\n'},
            {'targets': 'marker,value,unit\nheight_cm,175,cm\n'},
            {'targets': 'marker,value,unit\nunknown,1,1\n'},
            {'targets': 'marker,value,unit\n'},
        ]
        for case in cases:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as tmp:
                folder = Path(tmp)
                self.assertEqual(self.cli(folder).returncode, 0)
                run = self.cli(folder, **case)
                self.assertEqual(run.returncode, 3, run.stderr)
                self.assertTrue(json.loads((folder / 'out/problems.json').read_text())['problems'])
                self.assertFalse((folder / 'out/result.json').exists())
                self.assertFalse((folder / 'out/levers.json').exists())
                text = (folder / 'out/report.md').read_text()
                self.assertIn('论文卡片', text)
                self.assertIn('边界', text)
                self.assertNotIn('你的结果', text)

    def test_units_and_targets(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            # Metric conversion preserves Table 1 male mean inputs.
            run = self.cli(folder, raw='marker,value,unit\nWeight,87500,g\nHeight,1.783,m\n',
                           targets='marker,value,unit\n体重,80,kg\n')
            self.assertEqual(run.returncode, 0, run.stderr)
            levers = json.loads((folder / 'out/levers.json').read_text())
            self.assertAlmostEqual(levers['current']['ree_original_kcal_d'], 1775, delta=1.6)
            # Analytical sensitivities are the printed Eq 3 and Eq 8 coefficients.
            sensitivity = {x['key']: x for x in levers['sensitivity']}
            self.assertEqual(sensitivity['weight_kg']['derivatives']['ree_original_kcal_d'], 9.99)
            self.assertEqual(sensitivity['weight_kg']['derivatives']['ree_simplified_kcal_d'], 10)
            self.assertEqual(len(sensitivity), 4)
            self.assertEqual(levers['targets']['outputs'], levers['levers'][0]['outputs'])
            self.assertAlmostEqual(levers['targets']['delta']['ree_original_kcal_d'], 9.99 * (80 - 87.5))
            self.assertFalse(sensitivity['height_cm']['modifiable'])
            # Invalid targets removed by a subsequent valid run.
            self.assertEqual(self.cli(folder, targets='marker,value,unit\nweight_kg,800,kg\n').returncode, 3)
            self.assertEqual(self.cli(folder).returncode, 0)
            self.assertFalse((folder / 'out/problems.json').exists())

    def test_female_conversion_and_population_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            run = self.cli(folder, raw=f'marker,value,unit\nWeight,{70.2 / 0.45359237},lb\nHeight,{164.2 / 2.54},in\n',
                           age='44.6', sex='女')
            self.assertEqual(run.returncode, 0, run.stderr)
            data = json.loads((folder / 'out/result.json').read_text())['outputs']
            self.assertAlmostEqual(data['ree_original_kcal_d']['value'], 1348, delta=1.6)
            self.assertEqual(self.cli(folder, age='19', sex='female').returncode, 0)
            self.assertIn('超出', (folder / 'out/report.md').read_text())


if __name__ == '__main__':
    unittest.main()
