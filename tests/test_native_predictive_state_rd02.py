"""Frozen CAP04-RD02 engineering source/negative audit; not science."""
import importlib.util
from pathlib import Path
import json
import unittest

from yggdrasil.native_context_basis import canonical
from yggdrasil.native_predictive_state_split import PredictiveStateSplit

PATH = Path(__file__).resolve().parents[1] / (
    "research/contrib/chatgpt/YGG-CAP04/rd02_engineering.py")
spec = importlib.util.spec_from_file_location("cap04_rd02_frozen_engineering", PATH)
rd02 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rd02)


class RD02EngineeringTests(unittest.TestCase):
    def test_engineering_source_identity_clock_and_novel_pairs(self):
        for name in rd02.SOURCE_NAMES:
            with self.subTest(name=name):
                records = rd02.source(name)
                self.assertEqual(len(records), 256)
                self.assertEqual(len({x["id"] for x in records}), 256)
                self.assertEqual(
                    len({(records[t-1]["action"], records[t]["action"])
                         for t in range(64, 192)}), 16)
                for t, row in enumerate(records):
                    self.assertEqual(
                        row["action"],
                        rd02.ARMS[rd02.ACTION_CYCLE[
                            (t + int(name == rd02.SOURCE_NAMES[1])) % 16]])
                    self.assertEqual(row["post"][1], row["s2"])
                    if t:
                        past = records[t - 1]["post"]
                        self.assertEqual(
                            row["views"], ((past[0], past[1]),
                                           (past[1], past[2])))
                    if t < 64 or t >= 192:
                        self.assertEqual(row["y"], row["s2"])
                    else:
                        self.assertEqual(
                            row["y"], records[t - 1]["action"][0] & row["s2"])
        for fake in (99917, 99931, "99917", "cap04-rd02-source-c"):
            with self.assertRaisesRegex(ValueError,
                                        "SOURCE_NOT_REGISTERED_ENGINEERING"):
                rd02.source(fake)

    def test_decision_is_frozen_and_counterfactual_result_not_science(self):
        names = rd02.CANDIDATES + rd02.CONTROLS
        def phase(start):
            # Contract-only numbers, no scored source, no model training.
            scores = {name: {"two_stage": 0.25, "terminal": 0.25}
                      for name in names}
            scores["direct"] = {"two_stage": start, "terminal": start}
            scores["direct_sham"] = {"two_stage": .25, "terminal": .25}
            return scores
        scores = {"novel": phase(.20), "a_return": phase(.20),
                  "pooled": phase(.20)}
        probes = {
            "a_anchor": {"a_probe_brier": {"direct": .10}},
            "b_endpoint": {"a_probe_brier": {"direct": .10}},
            "a_return_endpoint": {"a_probe_brier": {"direct": .10}},
        }
        self.assertEqual(rd02.decision(scores, probes),
                         ("RD02_ENGINEERING_FEASIBLE", []))
        scores["pooled"]["direct"]["two_stage"] = .26
        status, errors = rd02.decision(scores, probes)
        self.assertEqual(status, "RD02_ENGINEERING_NO_GO")
        self.assertIn("POOLED_BEST_CONTROL", errors)
        self.assertFalse(PredictiveStateSplit(reward_mode="direct").count)

    def test_two_source_prequential_scores_and_tamper_rejected(self):
        for name in rd02.SOURCE_NAMES:
            with self.subTest(name=name):
                result = rd02.run(name)
                raw = canonical(result)
                proof = rd02.audit(raw)
                self.assertEqual(proof["rows_verified"], 256)
                self.assertEqual(proof["source_name"], name)
                self.assertIs(proof["scientific_pass"], False)
                self.assertIn(result["status"], (
                    "RD02_ENGINEERING_NO_GO", "RD02_ENGINEERING_FEASIBLE"))
                self.assertEqual(
                    result["snapshots"]["a_anchor"]["models"]["direct"]["events"],
                    64)
                self.assertEqual(
                    result["snapshots"]["b_endpoint"]["models"]["direct"]["events"],
                    192)
                self.assertEqual(
                    result["snapshots"]["a_return_endpoint"]["models"]["direct"]["events"],
                    256)
                forgery = json.loads(raw)
                forgery["rows"][0]["y"] ^= 1
                with self.assertRaisesRegex(ValueError, "AUDIT_REJECTED"):
                    rd02.audit(canonical(forgery))
                forgery = json.loads(raw)
                forgery["phase_scores"]["pooled"]["direct"]["two_stage"] += .01
                with self.assertRaisesRegex(ValueError, "AUDIT_REJECTED"):
                    rd02.audit(canonical(forgery))


if __name__ == "__main__":
    unittest.main()
