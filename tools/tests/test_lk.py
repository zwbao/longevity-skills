"""Tests for the `longevity` engine (tools/lk): find, methods, describe, run, evidence, MCP.

Paper-printed examples are run through the engine end to end (the same path an agent uses),
so a change in the runner that distorts inputs fails here, not only in the skill's own tests.
"""
from __future__ import annotations

import io
import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from tools.lk import cli, evidence, methods  # noqa: E402
from tools.lk.library import Library, LKError, locate  # noqa: E402
from tools.lk.mcp import TOOLS, Server  # noqa: E402
from tools.lk.run import run  # noqa: E402

LIB = Library(REPO)


def lk(*argv: str) -> tuple:
    """Run the root launcher the way an agent would; return (exit code, JSON)."""
    done = subprocess.run([sys.executable, str(REPO / "longevity"), *argv], capture_output=True, text=True, timeout=300)
    return done.returncode, json.loads(done.stdout)


def egfr(age, sex, scr_mg_dl):
    out = run(LIB, "ckd-epi-2021-egfr", {"age": age, "sex": sex,
                                          "measurements": [{"item": "肌酐", "value": scr_mg_dl, "unit": "mg/dL"}]})
    assert out["status"] == "ok", out
    return out["outputs"]


class LibraryTest(unittest.TestCase):
    def test_locates_the_checkout(self):
        self.assertEqual(locate(), REPO.resolve())
        self.assertEqual(LIB.release, (REPO / "VERSION").read_text().strip())

    def test_rejects_bad_names(self):
        for bad in ("../skills", "ckd-epi-2021-egfr/../x", "", "A", "x" * 200):
            with self.assertRaises(LKError):
                LIB.skill(bad)

    def test_bad_library_path(self):
        with self.assertRaises(LKError):
            locate(str(REPO / "skills"))


class FindAndListTest(unittest.TestCase):
    def test_find_routes_biological_age(self):
        out = methods.find(LIB, "我想知道我的生物年龄是多少")
        self.assertEqual(out["intents"][0]["intent"], "biological_age")
        names = [m["name"] for m in out["intents"][0]["methods"]]
        self.assertIn("accelerated-biological-aging-risk", names)

    def test_find_evidence_intent_points_to_evidence(self):
        out = methods.find(LIB, "NMN 有没有用")
        self.assertTrue(any("next_zh" in i for i in out["intents"]), out)

    def test_methods_lists_tier_a_only_by_default(self):
        out = methods.methods(LIB)
        tiers = {m["tier"] for m in out["methods"]}
        self.assertEqual(tiers, {"A"})
        a = [s for s in LIB.skills.values() if s["tier"] == "A"]
        self.assertEqual(out["count"], len(a))

    def test_have_marks_complete_and_missing(self):
        out = methods.methods(LIB, have=["肌酐", "年龄", "性别", "白蛋白"])
        by = {m["name"]: m for m in out["methods"]}
        self.assertTrue(by["ckd-epi-2021-egfr"]["complete"])
        self.assertFalse(by["china-par-ascvd-risk"]["complete"])
        self.assertIn("收缩压", by["china-par-ascvd-risk"]["missing"])

    def test_describe(self):
        d = methods.describe(LIB, "ckd-epi-2021-egfr")
        cr = next(i for i in d["inputs"] if i["key"] == "creatinine_umol_l")
        self.assertIn("mg/dL", cr["accept_units"])
        self.assertEqual(d["validation"]["status"], "reproduced")
        self.assertEqual(d["paper"]["doi"], "10.1056/nejmoa2102953")
        self.assertIn("longevity run ckd-epi-2021-egfr", d["run_example"])


class PrintedExamplesTest(unittest.TestCase):
    """Values printed in the papers, computed through the engine."""

    def test_ckd_epi_2021_table_s11(self):
        # NEJM 2021 supplementary Table S11 panel a, NonBlack rows: age 50 and 75, creatinine 0.6/1/1.5/2 mg/dL.
        printed = {("male", 50): [118, 92, 56, 40], ("male", 75): [101, 79, 48, 34],
                   ("female", 50): [109, 69, 42, 30], ("female", 75): [94, 59, 36, 26]}
        for (sex, age), values in printed.items():
            for scr, want in zip((0.6, 1.0, 1.5, 2.0), values):
                self.assertAlmostEqual(egfr(age, sex, scr)["egfr_cr"]["value"], want, delta=1, msg=(sex, age, scr))
        self.assertEqual(egfr(50, "male", 1.0)["gfr_category"]["value"], "G1")

    def test_china_par_table2(self):
        # Circulation 2016 Table 2: the same profile at ages 40-70 (men, women).
        table = {40: (2.2, 2.4), 50: (5.4, 5.4), 60: (11.0, 10.1), 70: (19.6, 17.1)}
        rows = [{"item": "收缩压", "value": 130, "unit": "mmHg"}, {"item": "总胆固醇", "value": 210, "unit": "mg/dL"},
                {"item": "高密度脂蛋白胆固醇", "value": 55, "unit": "mg/dL"}, {"item": "腰围", "value": 80, "unit": "cm"}]
        answers = {"treated": False, "smoker": False, "diabetes": True, "north": True, "urban": True, "family_history": False}
        for age, (men, women) in table.items():
            for sex, want in (("male", men), ("female", women)):
                out = run(LIB, "china-par-ascvd-risk", {"age": age, "sex": sex, "measurements": rows, "arguments": answers})
                self.assertEqual(out["status"], "ok", out)
                self.assertAlmostEqual(out["outputs"]["risk_10y_pct"]["value"], want, delta=max(0.1, want * 0.02), msg=(age, sex))

    def test_navy_body_fat_appendix_a(self):
        # Report 84-11 Appendix A (men): circumference value 16.0 in (abdomen - neck), height 65.0 in -> 13 %.
        inch = 2.54
        out = run(LIB, "navy-circumference-body-fat", {"sex": "male", "measurements": [
            {"item": "腰围", "value": 36 * inch, "unit": "cm"}, {"item": "颈围", "value": 20 * inch, "unit": "cm"},
            {"item": "身高", "value": 65 * inch, "unit": "cm"}]})
        self.assertEqual(out["status"], "ok", out)
        fat = next(v["value"] for k, v in out["outputs"].items() if isinstance(v["value"], float) and "fat" in k)
        self.assertAlmostEqual(fat, 13, delta=1)


class RulesTest(unittest.TestCase):
    def test_every_result_is_stamped(self):
        out = run(LIB, "ckd-epi-2021-egfr", {"age": 50, "sex": "male", "measurements": [{"item": "肌酐", "value": 1, "unit": "mg/dL"}]})
        for key in ("release", "tier", "label_zh", "validation_status", "paper"):
            self.assertIn(key, out)
        self.assertEqual(out["label_zh"], "已发表模型（已复现论文）")

    def test_unit_problem_stops_the_run(self):
        out = run(LIB, "ckd-epi-2021-egfr", {"age": 50, "sex": "male",
                                             "measurements": [{"item": "肌酐", "value": 1, "unit": "mmol/dL"}]})
        self.assertEqual(out["status"], "input_problem")
        self.assertNotIn("outputs", out)
        self.assertEqual(out["problems"][0]["kind"], "unit")

    def test_mixed_dates_are_refused(self):
        rows = [{"item": "收缩压", "value": 130, "unit": "mmHg", "date": "2026-01-01"},
                {"item": "腰围", "value": 80, "unit": "cm", "date": "2026-06-01"}]
        out = run(LIB, "china-par-ascvd-risk", {"age": 60, "sex": "male", "measurements": rows})
        self.assertEqual((out["status"], out["code"]), ("refused", "mixed_dates"))

    def test_draft_needs_allow_draft(self):
        draft = next(s["name"] for s in LIB.skills.values() if methods.status_of(s)[0] == "draft")
        out = run(LIB, draft, {})
        self.assertEqual((out["status"], out["code"]), ("refused", "draft"))

    def test_tier_c_is_refused(self):
        c = next(s["name"] for s in LIB.skills.values() if s["tier"] == "C")
        out = run(LIB, c, {})
        self.assertEqual((out["status"], out["code"]), ("refused", "not_runnable"))

    def test_unknown_answer_key(self):
        with self.assertRaises(LKError):
            run(LIB, "ckd-epi-2021-egfr", {"arguments": {"smoker": "no"}})

    def test_bad_answer_value(self):
        with self.assertRaises(LKError):
            run(LIB, "china-par-ascvd-risk", {"arguments": {"smoker": "maybe"}})

    def test_newline_in_item_is_rejected(self):
        with self.assertRaises(LKError):
            run(LIB, "ckd-epi-2021-egfr", {"measurements": [{"item": "肌酐\n收缩压", "value": 1, "unit": "mg/dL"}]})


class EvidenceTest(unittest.TestCase):
    def test_entity_with_only_animal_rows(self):
        out = evidence.query(LIB, ["亚精胺"])
        r = out["results"][0]
        self.assertEqual(r["counts"]["human"], 0)
        self.assertIn("没有关于它的人群研究", r["note_zh"])
        self.assertTrue(all(row["doi"] for g in ("animal", "cell", "other") if g in r for row in r[g]["rows"]))

    def test_unknown_entity(self):
        r = evidence.query(LIB, ["一种不存在的补剂xyz"])["results"][0]
        self.assertEqual(r["matched"], 0)
        self.assertIn("没有收录不等于没有研究", r["note_zh"])

    def test_trial_effects_are_listed(self):
        r = evidence.query(LIB, ["减盐"])["results"][0]
        self.assertTrue(r.get("trial_effects"), r)


class CommandLineTest(unittest.TestCase):
    def test_launcher_run_and_exit_codes(self):
        code, out = lk("run", "ckd-epi-2021-egfr", "--age", "75", "--sex", "female", "-m", "肌酐=1.5 mg/dL")
        self.assertEqual((code, out["outputs"]["egfr_cr"]["value"]), (0, 36.0))  # Table S11
        code, out = lk("run", "ckd-epi-2021-egfr", "--age", "75", "--sex", "female", "-m", "肌酐=1.5 mmol/dL")
        self.assertEqual((code, out["status"]), (3, "input_problem"))
        code, out = lk("run", "no-such-method")
        self.assertEqual((code, out["error"]), (2, "unknown_method"))

    def test_change_matches_the_hand_calculation(self):
        # triglycerides are log-normal in the table: the band is asymmetric
        code, out = lk("change", "--marker", "甘油三酯", "--before", "1.8", "--after", "1.5")
        self.assertEqual((code, out["verdict"], out["band_pct"], out["change_pct"]), (0, "within_noise", [-45.6, 83.8], -16.7))

    def test_help(self):
        done = subprocess.run([sys.executable, str(REPO / "longevity"), "--help"], capture_output=True, text=True)
        self.assertEqual(done.returncode, 0)
        self.assertIn("longevity run", done.stdout)


class McpTest(unittest.TestCase):
    def session(self, *messages):
        out, log = io.StringIO(), io.StringIO()
        Server(LIB, out=out, log=log).serve(io.StringIO("\n".join(json.dumps(m) if not isinstance(m, str) else m
                                                                   for m in messages) + "\n"))
        return [json.loads(line) for line in out.getvalue().splitlines()]

    def test_handshake_list_call(self):
        replies = self.session(
            {"jsonrpc": "2.0", "id": 1, "method": "initialize",
             "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "t", "version": "0"}}},
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
            {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "run_method", "arguments": {
                "name": "ckd-epi-2021-egfr", "age": 50, "sex": "male",
                "measurements": [{"item": "肌酐", "value": 1.0, "unit": "mg/dL"}]}}},
            {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "review_change", "arguments": {
                "marker": "收缩压", "before": [138], "after": [131]}}},
            {"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": "query_evidence",
                                                                            "arguments": {"entities": ["亚精胺"]}}},
            {"jsonrpc": "2.0", "id": 6, "method": "tools/call", "params": {"name": "find_methods",
                                                                            "arguments": {"text": "肾小球滤过率"}}},
        )
        self.assertEqual(len(replies), 6)  # the notification gets no reply
        self.assertEqual(replies[0]["result"]["protocolVersion"], "2025-06-18")
        self.assertEqual({t["name"] for t in replies[1]["result"]["tools"]}, {t["name"] for t in TOOLS})
        ran = json.loads(replies[2]["result"]["content"][0]["text"])
        self.assertEqual(ran["outputs"]["egfr_cr"]["value"], 92.0)
        self.assertEqual(json.loads(replies[3]["result"]["content"][0]["text"])["verdict"], "within_noise")
        self.assertEqual(json.loads(replies[4]["result"]["content"][0]["text"])["results"][0]["counts"]["human"], 0)
        found = json.loads(replies[5]["result"]["content"][0]["text"])
        self.assertEqual(found["find"]["intents"][0]["intent"], "kidney_function")

    def test_errors_do_not_end_the_session(self):
        replies = self.session(
            "{not json",
            {"jsonrpc": "2.0", "id": 1, "method": "no/such"},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "nope", "arguments": {}}},
            {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "review_change",
                                                                            "arguments": {"marker": "LDL", "before": "x"}}},
            {"jsonrpc": "2.0", "id": 4, "method": "initialize", "params": {"protocolVersion": "1999-01-01"}},
            {"jsonrpc": "2.0", "id": 5, "method": "ping"},
        )
        self.assertEqual(replies[0]["error"]["code"], -32700)
        self.assertEqual(replies[1]["error"]["code"], -32601)
        self.assertTrue(replies[2]["result"]["isError"])
        self.assertTrue(replies[3]["result"]["isError"])
        self.assertEqual(replies[4]["result"]["protocolVersion"], "2025-06-18")
        self.assertEqual(replies[5]["result"], {})


if __name__ == "__main__":
    unittest.main()
