"""Report and scenario contracts; numerical fixtures are Figure 3 endpoints."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import test_manifest as fixtures

ROOT = fixtures.ROOT


class ReportTests(unittest.TestCase):
    def test_zero_endpoint_report_and_error_card(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            edits = [(k, row[1], "%" if k.endswith("_pct") else "1") for k, row in fixtures.PRINTED.items()]
            p = fixtures.ManifestTests().run_cli(root, edits=edits)
            self.assertEqual(p.returncode, 0, p.stderr)
            values = json.loads((root / "out/result.json").read_text())["outputs"]
            # Each component's zero-score standard is printed in Figure 3.
            for key, item in values.items():
                if key != "hei_total_score":
                    self.assertEqual(item["value"], 0)
            p = fixtures.ManifestTests().run_cli(root, drop="sodium_density_ratio")
            self.assertEqual(p.returncode, 3)
            text = (root / "out/report.md").read_text()
            self.assertLess(text.index("## 论文卡片"), text.index("## 输入没有通过检查"))
            self.assertIn("边界:", text)

    def test_joint_target_can_have_inconsistent_single_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = fixtures.ManifestTests().run_cli(root, targets=[
                ("whole_fruits_density_ratio", 2.5, "1"),
                ("total_fruits_density_ratio", 2.5, "1"),
            ])
            self.assertEqual(p.returncode, 0, p.stderr)
            payload = json.loads((root / "out/levers.json").read_text())
            whole = next(item for item in payload["levers"] if item["key"] == "whole_fruits_density_ratio")
            self.assertIsNone(whole["outputs"])
            self.assertTrue(whole["problems"])
            self.assertEqual(payload["targets"]["outputs"]["whole_fruits_score"], 5)
            self.assertIn("未计算单项情景", (root / "out/report.md").read_text())

    def test_missing_file_returns_structured_problem(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = subprocess.run([sys.executable, str(ROOT / "scripts/personal_report.py"),
                                "--measurements", str(root / "missing.csv"), "--age", "40",
                                "--out", str(root / "out")], capture_output=True, text=True)
            self.assertEqual(p.returncode, 3, p.stderr)
            payload = json.loads((root / "out/problems.json").read_text())
            self.assertEqual(payload["problems"][0]["kind"], "file")


if __name__ == "__main__":
    unittest.main()
