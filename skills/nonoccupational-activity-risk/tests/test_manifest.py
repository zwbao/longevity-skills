"""Expected values transcribed from Garcia et al. 2023, Table 1 and eMethods 5.
Written before the calculator. No expected RR is generated from its curve data.
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


def report_module():
    spec = importlib.util.spec_from_file_location('activity_report', ROOT / 'scripts/personal_report.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Table 1: columns 4.375, 8.75, 17.5 mMET-hours/week; each tuple is RR, lower, upper.
PRINTED = {
    'all_cause_mortality': [(0.77, 0.73, 0.80), (0.69, 0.65, 0.73), (0.66, 0.62, 0.70)],
    'cvd_mortality': [(0.81, 0.77, 0.85), (0.71, 0.66, 0.77), (0.65, 0.60, 0.71)],
    'cancer_mortality': [(0.90, 0.88, 0.93), (0.85, 0.81, 0.89), (0.82, 0.78, 0.86)],
    'cvd_incidence': [(0.83, 0.79, 0.87), (0.73, 0.69, 0.79), (0.67, 0.63, 0.72)],
    'chd_incidence': [(0.86, 0.83, 0.90), (0.79, 0.74, 0.84), (0.74, 0.69, 0.80)],
    'stroke_incidence': [(0.86, 0.83, 0.90), (0.80, 0.75, 0.85), (0.77, 0.72, 0.82)],
    'heart_failure_incidence': [(0.90, 0.85, 0.96), (0.84, 0.75, 0.93), (0.77, 0.68, 0.87)],
    'cancer_incidence': [(0.93, 0.91, 0.95), (0.88, 0.85, 0.92), (0.85, 0.81, 0.89)],
    'head_neck_incidence': [(0.74, 0.59, 0.94), (0.65, 0.46, 0.91), (0.63, 0.42, 0.94)],
    'myeloid_leukaemia_incidence': [(0.80, 0.66, 0.97), (0.75, 0.60, 0.95), (0.75, 0.60, 0.94)],
    'myeloma_incidence': [(0.84, 0.74, 0.95), (0.75, 0.61, 0.92), (0.72, 0.57, 0.92)],
    'gastric_cardia_incidence': [(0.86, 0.78, 0.95), (0.78, 0.66, 0.91), (0.73, 0.60, 0.88)],
    'lung_incidence': [(0.89, 0.87, 0.92), (0.84, 0.81, 0.88), (0.83, 0.76, 0.91)],
    'liver_incidence': [(0.90, 0.83, 0.98), (0.84, 0.73, 0.96), (0.78, 0.66, 0.93)],
    'endometrial_incidence': [(0.94, 0.90, 0.99), (0.90, 0.84, 0.97), (0.87, 0.80, 0.95)],
    'colon_incidence': [(0.96, 0.93, 0.99), (0.93, 0.87, 0.99), (0.90, 0.84, 0.97)],
    'breast_incidence': [(0.97, 0.96, 0.99), (0.95, 0.92, 0.97), (0.92, 0.88, 0.96)],
    'bladder_incidence': [(0.93, 0.84, 1.02), (0.90, 0.80, 1.02), (0.90, 0.81, 1.01)],
    'rectum_incidence': [(0.96, 0.92, 1.01), (0.95, 0.88, 1.02), (0.96, 0.88, 1.04)],
    'oesophageal_incidence': [(0.97, 0.89, 1.05), (0.95, 0.82, 1.09), (0.94, 0.79, 1.12)],
    'prostate_incidence': [(1.00, 0.99, 1.02), (1.01, 0.98, 1.04), (1.01, 0.96, 1.05)],
    'kidney_incidence': [(1.02, 0.92, 1.13), (1.03, 0.89, 1.19), (1.04, 0.88, 1.24)],
}


class ManifestTests(unittest.TestCase):
    def test_table1_all_outcomes(self):
        """All 198 printed RR/CI numbers, at the paper's three exposure levels."""
        report = report_module()
        for key, triplets in PRINTED.items():
            for exposure, expected in zip((4.375, 8.75, 17.5), triplets):
                with self.subTest(outcome=key, exposure=exposure):
                    row = report.lookup(key, exposure)
                    for column, value in zip(('RR', 'lb', 'ub'), expected):
                        self.assertAlmostEqual(row[column], value, delta=0.005)

    def test_emethods5_duration_example(self):
        # p.9: "Example: 2 hours of moderate physical activity";
        # "2 hours * 3.5 MET = 7 mMET.hrs" (figure's activity component).
        r = report_module()
        self.assertEqual(r.activity_volume({'light_min_week': 0, 'moderate_min_week': 2 * 60,
                                           'vigorous_min_week': 0}), 7)

    def run_cli(self, directory, rows, extra=()):
        p = Path(directory)
        (p / 'input.csv').write_text('marker,value,unit\n' + rows, encoding='utf-8')
        return subprocess.run([sys.executable, str(ROOT / 'scripts/personal_report.py'),
                               '--measurements', str(p / 'input.csv'), '--age', '50',
                               '--out', str(p / 'out'), *extra], capture_output=True, text=True)

    def test_cli_table1_and_units(self):
        # Methods: 2.5 hours at 3.5 mMET = 8.75; Table 1 all-cause RR 0.69 (0.65–0.73).
        with tempfile.TemporaryDirectory() as d:
            p = self.run_cli(d, '每周轻强度非职业活动时长,0,min\n每周中等强度非职业活动时长,2.5,h\n每周高强度非职业活动时长,0,min\n')
            self.assertEqual(p.returncode, 0, p.stderr)
            outputs = json.loads((Path(d) / 'out/result.json').read_text())['outputs']
            self.assertEqual(outputs['activity_mmet_h_week']['value'], 8.75)
            for suffix, value in [('rr', 0.69), ('ci_lower', 0.65), ('ci_upper', 0.73)]:
                self.assertAlmostEqual(outputs['all_cause_mortality_' + suffix]['value'], value, delta=0.005)
            text = (Path(d) / 'out/report.md').read_text()
            self.assertLess(text.index('论文卡片'), text.index('本次活动量'))
            self.assertIn('边界:', text)
            self.assertTrue((Path(d) / 'out/levers.json').exists())

    def test_wrong_inputs_exit3(self):
        for rows in ['light_min_week,0,min\nmoderate_min_week,150,steps\nvigorous_min_week,0,min\n',
                     'light_min_week,0,min\nmoderate_min_week,-1,min\nvigorous_min_week,0,min\n',
                     'light_min_week,0,min\nmoderate_min_week,150,min\n',
                     'light_min_week,0,min\nmoderate_min_week,nan,min\nvigorous_min_week,0,min\n']:
            with self.subTest(rows=rows), tempfile.TemporaryDirectory() as d:
                p = self.run_cli(d, rows)
                self.assertEqual(p.returncode, 3, p.stderr)
                self.assertTrue((Path(d) / 'out/problems.json').exists())
                self.assertFalse((Path(d) / 'out/result.json').exists())

    def test_manifest_presets_agree(self):
        r = report_module()
        manifest = json.loads((ROOT / 'skill.json').read_text())
        inputs = {x['key']: x for x in manifest['inputs']}
        for key in r.INTENSITIES:
            self.assertEqual(inputs[key]['unit'], 'min')
            self.assertEqual(inputs[key]['range'], [0, r.MAX_WEEK_MINUTES])
        self.assertEqual(set(PRINTED), set(r.OUTCOMES))


if __name__ == '__main__':
    unittest.main()

# Module-level entry points keep the exact manifest test locators executable by pytest.
def test_table1_all_outcomes():
    ManifestTests('test_table1_all_outcomes').test_table1_all_outcomes()


def test_emethods5_duration_example():
    ManifestTests('test_emethods5_duration_example').test_emethods5_duration_example()
