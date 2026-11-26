"""Printed anchors from Shams-White et al. 2023, Figure 3 (not fitted values)."""
import csv
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import personal_report as report
import presets

# Figure 3: input at maximum, input at zero, printed maximum points.
# Density ratios use the exact reference quantities documented in the manifest.
PRINTED = {
    "total_fruits_density_ratio": (0.8, 0, 5),
    "whole_fruits_density_ratio": (0.4, 0, 5),
    "total_vegetables_density_ratio": (1.1, 0, 5),
    "greens_beans_density_ratio": (0.2, 0, 5),
    "whole_grains_density_ratio": (1.5, 0, 10),
    "dairy_density_ratio": (1.3, 0, 10),
    "total_protein_density_ratio": (2.5, 0, 5),
    "seafood_plant_density_ratio": (0.8, 0, 5),
    "fatty_acids_ratio": (2.5, 1.2, 10),
    "refined_grains_density_ratio": (1.8, 4.3, 10),
    "sodium_density_ratio": (1.1, 2.0, 10),
    "added_sugars_energy_pct": (6.5, 26, 10),
    "saturated_fats_energy_pct": (8, 16, 10),
}


def test_figure3_added_sugars():
    # Verbatim cells: Added Sugars | 10 | ≤6.5% of energy | ≥26% of energy.
    # The last column heading specifies a minimum score of zero.
    assert report.component_score("added_sugars_energy_pct", 6.5) == 10
    assert report.component_score("added_sugars_energy_pct", 26) == 0


class ManifestTests(unittest.TestCase):
    def test_figure3_added_sugars(self):
        test_figure3_added_sugars()

    def test_all_figure3_endpoints(self):
        for key, (maximum_input, zero_input, points) in PRINTED.items():
            with self.subTest(key=key):
                self.assertAlmostEqual(report.component_score(key, maximum_input), points)
                self.assertEqual(report.component_score(key, zero_input), 0)
        # Figure 4 footnote c explicitly defines total HEI as out of 100 points.
        self.assertEqual(report.calculate({k: row[0] for k, row in PRINTED.items()})["hei_total_score"], 100)

    def run_cli(self, directory, edits=None, drop=None, targets=None, age="40"):
        rows = [[k, row[0], "%" if k.endswith("_pct") else "1"] for k, row in PRINTED.items() if k != drop]
        for key, value, unit in edits or []:
            rows = [r for r in rows if r[0] != key] + [[key, value, unit]]
        path = directory / "diet.csv"
        with path.open("w", newline="") as f:
            writer = csv.writer(f); writer.writerow(["item", "value", "unit"]); writer.writerows(rows)
        args = [sys.executable, str(ROOT / "scripts/personal_report.py"), "--measurements", str(path), "--out", str(directory / "out")]
        if age is not None:
            args += ["--age", age]
        if targets is not None:
            target_file = directory / "targets.csv"
            with target_file.open("w", newline="") as f:
                writer = csv.writer(f); writer.writerow(["item", "value", "unit"]); writer.writerows(targets)
            args += ["--targets", str(target_file)]
        return subprocess.run(args, capture_output=True, text=True)

    def test_manifest_keys_and_units(self):
        manifest = json.loads((ROOT / "skill.json").read_text())
        specs = {s["key"]: s for s in manifest["inputs"] if s["from"] == "measurements"}
        self.assertEqual(set(specs), set(PRINTED))
        self.assertEqual(set(specs), set(presets.COMPONENTS))
        for key, spec in specs.items():
            self.assertEqual(spec["unit"], presets.COMPONENTS[key]["unit"])

    def test_result_card_and_conversion(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = self.run_cli(root, edits=[("added_sugars_energy_pct", 0.065, "1")])
            self.assertEqual(p.returncode, 0, p.stderr)
            result = json.loads((root / "out/result.json").read_text())["outputs"]
            self.assertEqual(result["hei_total_score"]["value"], 100)
            self.assertEqual(result["added_sugars_score"]["value"], 10)
            text = (root / "out/report.md").read_text()
            self.assertLess(text.index("## 论文卡片"), text.index("你的记录"))
            self.assertIn("边界:", text)
            self.assertTrue((root / "out/levers.json").exists())

    def test_invalid_inputs_clear_previous_outputs(self):
        cases = [
            {"edits": [("sodium_density_ratio", 1100, "mg")]},
            {"edits": [("added_sugars_energy_pct", 101, "%")]},
            {"edits": [("fatty_acids_ratio", "nan", "1")]},
            {"drop": "whole_grains_density_ratio"},
            {"age": "1"}, {"age": None}, {"age": "wrong"},
            {"edits": [("whole_fruits_density_ratio", 2.5, "1")]},
            {"edits": [("saturated_fats_energy_pct", 0, "%")]},
            {"targets": [("added_sugars_energy_pct", 101, "%")]},
            {"targets": [("unknown_food", 1, "1")]},
        ]
        for case in cases:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.assertEqual(self.run_cli(root).returncode, 0)
                p = self.run_cli(root, **case)
                self.assertEqual(p.returncode, 3, p.stderr)
                out = root / "out"
                self.assertTrue(json.loads((out / "problems.json").read_text())["problems"])
                self.assertFalse((out / "result.json").exists())
                self.assertFalse((out / "levers.json").exists())
                self.assertNotIn("总分：", (out / "report.md").read_text())

    def test_target_scenario_uses_printed_endpoint(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = self.run_cli(root, targets=[("added_sugars_energy_pct", 26, "%")])
            self.assertEqual(p.returncode, 0, p.stderr)
            levers = json.loads((root / "out/levers.json").read_text())
            self.assertEqual(levers["schema"], "longevity-levers/1")
            self.assertEqual(levers["targets"]["outputs"]["added_sugars_score"], 0)
            self.assertEqual(len(levers["sensitivity"]), len(PRINTED))


if __name__ == "__main__":
    unittest.main()
