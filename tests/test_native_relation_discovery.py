"""NKR-09: source-free rule creation, feedback, retention and strong controls."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

from yggdrasil.native_cumulative_facts import canonical, digest
from yggdrasil.native_relation_discovery import (
    NativeRelationDiscovery, FEEDBACK_SCHEMA,
)
from yggdrasil.public_causal_cells import PublicCausalCells

SCRIPT = (Path(__file__).resolve().parents[1]
          / "research/contrib/chatgpt/NKR-09/experiment.py")
spec = importlib.util.spec_from_file_location("nkr09_frozen_fixture", SCRIPT)
study = importlib.util.module_from_spec(spec)
spec.loader.exec_module(study)


def feedback(*, records, ident="feedback-fixture-v1", kind="public_target_outcome",
             mode="engineering_fixture_only"):
    return canonical({"schema": FEEDBACK_SCHEMA,
                      "source_id": ident, "source_mode": mode,
                      "source_kind": kind, "records": records})


class NativeRelationDiscoveryTests(unittest.TestCase):
    def test_frozen_induction_feedback_transfer_and_symbolic_control(self):
        result = study.run_frozen()
        self.assertEqual(result["frozen_rule_counts"],
                         [[15, 11, 12, 24], [15, 13, 14, 8],
                          [16, 11, 12, 8], [16, 13, 14, 24]])
        self.assertEqual(result["feedback_labels_revealed"], 8)
        self.assertEqual(result["protected_cold_queries"], 12)
        self.assertEqual(result["cold_static_hits1"], 3)
        self.assertEqual(result["cold_after_feedback_hits1"], 9)
        self.assertEqual(result["cold_equal_evidence_symbolic_hits1"], 9)
        self.assertEqual(result["cold_gain_over_static_hits1"], 6)
        self.assertEqual(result["unrelated_relation_retention_hits1_before"], 9)
        self.assertEqual(result["unrelated_relation_retention_hits1_after"], 9)
        self.assertTrue(result["unknown_relation_abstains"])
        self.assertFalse(result["scientific_pass"])
        self.assertFalse(result["accepted_native"])

    def test_rules_are_discovered_not_preseeded_by_target_identifiers(self):
        facts, edges, _ = study.staged_fixture()
        learner = NativeRelationDiscovery(facts)
        self.assertEqual(
            [(r["target_relation"], r["first_relation"],
              r["second_relation"], r["training_support"])
             for r in learner.rules()],
            [(15, 11, 12, 24), (15, 13, 14, 8),
             (16, 11, 12, 8), (16, 13, 14, 24)])
        self.assertEqual(learner.predict(41, 29)["classification"],
                         "UNKNOWN_ABSTAIN")
        self.assertEqual(learner.predict(41, 987654)["classification"],
                         "UNKNOWN_ABSTAIN")
        self.assertEqual(learner.predict(1, 15)["classification"],
                         "ALREADY_OBSERVED_NOT_EVALUABLE")
        self.assertEqual(facts.fact(41, 15, 40041)["classification"],
                         "UNKNOWN_ABSTAIN")

    def test_immutable_feedback_checkpoint_dedup_and_cold_replay(self):
        facts, _, truth = study.staged_fixture()
        before = PublicCausalCells().snapshot()
        learner = NativeRelationDiscovery(facts)
        first_hash = learner.checkpoint_sha256
        source_hash = facts.checkpoint_sha256
        raw = study.microfeedback(truth)
        next_, receipt = learner.stage_feedback(raw, digest(raw))
        self.assertEqual(receipt["new_feedback"], 8)
        self.assertNotEqual(first_hash, next_.checkpoint_sha256)
        self.assertEqual(first_hash, learner.checkpoint_sha256)
        self.assertEqual(source_hash, facts.checkpoint_sha256)
        restored = NativeRelationDiscovery(
            facts, next_.checkpoint(), checkpoint_sha256=next_.checkpoint_sha256)
        self.assertEqual(restored.checkpoint(), next_.checkpoint())
        self.assertEqual(restored.predict(41, 15)["proposals"],
                         next_.predict(41, 15)["proposals"])
        unchanged, dup = restored.stage_feedback(raw, digest(raw))
        self.assertIs(unchanged, restored)
        self.assertEqual(dup["classification"], "DUPLICATE_FEEDBACK_BUNDLE_NO_EFFECT")
        self.assertEqual(dup["new_feedback"], 0)
        self.assertEqual(PublicCausalCells().snapshot(), before)

    def test_untrusted_feedback_and_rebound_identity_rejected(self):
        facts, _, truth = study.staged_fixture()
        native = NativeRelationDiscovery(facts)
        raw = study.microfeedback(truth)
        for bad in (
            feedback(records=[[33,15,truth[(33,15)],"source:01"]],
                     kind="composed_path_inference"),
            feedback(records=[[33,15,truth[(33,15)],"source:01"]],
                     mode="owner_certified"),
        ):
            with self.assertRaises(PermissionError):
                native.stage_feedback(bad, digest(bad))
        with self.assertRaisesRegex(ValueError, "NKR09_FEEDBACK_BUNDLE_PIN_MISMATCH"):
            native.stage_feedback(raw, "0"*64)
        first, _ = native.stage_feedback(raw, digest(raw))
        attack = feedback(records=[[33,15,truth[(33,15)],"attack:01"]],
                          ident="nkr09-8-synthetic-outcomes-only")
        with self.assertRaisesRegex(ValueError, "NKR09_FEEDBACK_SOURCE_REBOUND"):
            first.stage_feedback(attack, digest(attack))

    def test_malformed_or_replayed_feedback_never_writes_into_ledger(self):
        facts, _, truth = study.staged_fixture()
        initial = NativeRelationDiscovery(facts)
        before = facts.checkpoint()
        for rows, code in (
            ([[33,15,99999999,"bad:1"]], "NKR09_FEEDBACK_UNSUPPORTED_TARGET"),
            ([[1,15,20001,"bad:1"]], "NKR09_FEEDBACK_ALREADY_OBSERVED"),
            ([[33,15,truth[(33,15)],"same:1"],
              [33,15,truth[(33,15)],"same:2"]], "NKR09_FEEDBACK_REF_OR_QUERY_REPLAY"),
            ([[33,15,truth[(33,15)],"same:2"],
              [34,15,truth[(34,15)],"same:1"]], "NKR09_FEEDBACK_SOURCE_REF_ORDER"),
        ):
            bad = feedback(records=rows, ident="invalid-"+code)
            with self.subTest(code=code), self.assertRaisesRegex(ValueError, code):
                initial.stage_feedback(bad, digest(bad))
            self.assertEqual(facts.checkpoint(), before)
        self.assertEqual(initial.predict(41,15)["proposals"][0]["object_q"],
                         20041)

    def test_sha_tamper_source_mismatch_and_bad_checkpoint_rejected(self):
        facts, _, truth = study.staged_fixture()
        initial = NativeRelationDiscovery(facts)
        raw = study.microfeedback(truth)
        adjusted, _ = initial.stage_feedback(raw, digest(raw))
        document = json.loads(adjusted.checkpoint())
        document["scientific_pass"] = True
        attack = canonical(document)
        with self.assertRaisesRegex(ValueError, "NKR09_CHECKPOINT_SOURCE_OR_RULE_DRIFT"):
            NativeRelationDiscovery(facts, attack, checkpoint_sha256=digest(attack))
        with self.assertRaisesRegex(ValueError, "NKR09_CHECKPOINT_PIN_MISMATCH"):
            NativeRelationDiscovery(facts, adjusted.checkpoint(),
                                     checkpoint_sha256="0"*64)
        document["scientific_pass"] = False
        document["rules"].append([999,1,2,999])
        modified = canonical(document)
        with self.assertRaisesRegex(ValueError, "NKR09_CHECKPOINT_SOURCE_OR_RULE_DRIFT"):
            NativeRelationDiscovery(facts, modified,
                                     checkpoint_sha256=digest(modified))

    def test_feedback_does_not_conflate_compound_hypothesis_with_observed_fact(self):
        facts, _, truth = study.staged_fixture()
        original_facts = facts.checkpoint()
        learner = NativeRelationDiscovery(facts)
        result = learner.predict(41,15)
        self.assertEqual(result["classification"],
                         "UNVERIFIED_ADAPTIVE_RELATION_HYPOTHESES")
        self.assertFalse(result["verified_new_knowledge"])
        self.assertFalse(result["can_write_causal_consequence"])
        next_, _ = learner.stage_feedback(study.microfeedback(truth),
                                           digest(study.microfeedback(truth)))
        self.assertEqual(facts.checkpoint(), original_facts)
        self.assertEqual(facts.fact(41,15,40041)["classification"],
                         "UNKNOWN_ABSTAIN")
        self.assertEqual(next_.predict(41,15)["proposals"][0]["object_q"],40041)
        self.assertEqual(next_.predict(53,16)["proposals"][0]["object_q"],40053)


if __name__ == "__main__":
    unittest.main()
