"""NKR-11 source-free falsifiable intervention-repair and negative tests."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

from yggdrasil.native_intervention_repair import (
    BUNDLE_SCHEMA, SOURCE_KIND, SOURCE_MODE,
    IntegerCausalSignature, NativeInterventionRepair,
    canonical, digest,
)
from yggdrasil.public_causal_cells import PublicCausalCells

SCRIPT = (Path(__file__).resolve().parents[1]
          / "research/contrib/chatgpt/NKR-11/experiment.py")
spec = importlib.util.spec_from_file_location("nkr11_frozen_env", SCRIPT)
study = importlib.util.module_from_spec(spec)
spec.loader.exec_module(study)


def model_and_world(world_id=0):
    env = study.ComputationalEnvironment(world_id)
    warm = study.collect_warmup(env)
    raw = study.evidence(f"warm-bundle-world-{world_id:02d}", warm)
    model = NativeInterventionRepair.from_warmup(raw, digest(raw))
    return env, model, warm


class NativeInterventionRepairTests(unittest.TestCase):
    def test_frozen_12_world_intervention_shift_transfer_and_symbolic_controls(self):
        result = study.run_frozen()
        counts = result["totals"]
        self.assertEqual(counts["worlds"], 12)
        self.assertEqual(counts["cold_queries"], 192)
        self.assertEqual(counts["old_retention_queries"], 384)
        self.assertEqual(counts["public_observations_per_world"], 16)
        self.assertEqual(counts["contradiction_triggers"], 12)
        self.assertEqual(counts["new_full_rank_signatures"], 12)
        self.assertEqual(counts["native_correct"], counts["exact_symbolic_correct"])
        self.assertEqual(counts["native_correct"], counts["instant_reset_correct"])
        self.assertEqual(counts["old_retained_correct"], 384)
        self.assertLessEqual(counts["passive_correct"], counts["native_correct"])
        self.assertLessEqual(counts["random_correct"], counts["native_correct"])
        self.assertEqual(result["source_checkpoint_count"], 12)
        self.assertFalse(result["scientific_pass"])
        self.assertFalse(result["strong_control_superiority"])
        self.assertFalse(result["native_accepted"])
        self.assertEqual(result["new_authentic_real_world_facts"], 0)
        self.assertTrue(result["no_hidden_cold_labels_in_training"])
        self.assertTrue(result["original_yggdrasil_causal_state_unchanged"])

    def test_first_public_contradiction_triggers_repair_without_world_phase(self):
        env, old, warm = model_and_world(0)
        before = old.checkpoint_sha256
        self.assertEqual(old.prior(0, 1), 1)
        repair = study.collect_paired_interventions(env)
        self.assertEqual(repair[0][1:4], (0, 1, 0))
        raw = study.evidence("repair-bundle-world-00", repair)
        candidate, receipt = old.stage_public_interventions(raw, digest(raw))
        self.assertEqual(receipt["new_events"], 16)
        self.assertNotEqual(old.checkpoint_sha256, candidate.checkpoint_sha256)
        self.assertEqual(old.checkpoint_sha256, before)
        self.assertFalse(old.change_detected)
        self.assertTrue(candidate.change_detected)
        self.assertEqual(candidate.new_rank, 10)
        for x in study.COLD_CONTEXTS:
            for a in (0, 1):
                pred = candidate.predict(x, a)
                self.assertEqual(pred["classification"],
                                 "UNVERIFIED_NEW_RELATION_OUTCOME")
                self.assertEqual(pred["public_outcome"], env.intervene(x, a))
                self.assertFalse(pred["verified_new_world_fact"])
                self.assertFalse(pred["can_write_causal_owner"])
                self.assertFalse(pred["native_accepted"])

    def test_repair_does_not_change_original_causal_model_or_cold_restore(self):
        env, old, _ = model_and_world(3)
        native_before = PublicCausalCells().snapshot()
        old_bytes = old.checkpoint()
        raw = study.evidence("repair-bundle-world-03",
                             study.collect_paired_interventions(env))
        changed, _ = old.stage_public_interventions(raw, digest(raw))
        restored = NativeInterventionRepair(changed.checkpoint(),
                                             changed.checkpoint_sha256)
        self.assertEqual(restored.checkpoint(), changed.checkpoint())
        self.assertEqual(old.checkpoint(), old_bytes)
        for x in range(16):
            for a in (0, 1):
                self.assertEqual(restored.prior(x, a), old.prior(x, a))
                self.assertEqual(restored.prior(x, a),
                                 env.intervene(x, a, old_mechanism=True))
        self.assertEqual(PublicCausalCells().snapshot(), native_before)
        same, receipt = restored.stage_public_interventions(raw, digest(raw))
        self.assertIs(same, restored)
        self.assertEqual(receipt["classification"], "DUPLICATE_NO_EFFECT")
        self.assertEqual(receipt["new_events"], 0)

    def test_absence_of_first_contradiction_cannot_activate_repair(self):
        _, old, _ = model_and_world(1)
        agreeing = [("public-probe-12345", 0, 0, old.prior(0, 0))]
        raw = study.evidence("public-agree-only-01", agreeing)
        next_, receipt = old.stage_public_interventions(raw, digest(raw))
        self.assertIs(next_, old)
        self.assertFalse(next_.change_detected)
        self.assertEqual(receipt["classification"],
                         "NO_FIRST_PUBLIC_CONTRADICTION_NO_CHANGE")
        self.assertEqual(old.predict(7, 1)["classification"], "WARM_PRIOR_ONLY")

    def test_unidentifiable_public_counterfactual_abstains_not_fabricated(self):
        partial = IntegerCausalSignature((("partial-event-01", 0, 1, 0),))
        self.assertEqual(partial.rank, 1)
        self.assertEqual(partial.predict(0, 1), 0)
        self.assertIsNone(partial.predict(7, 0))
        self.assertIsNone(partial.predict(15, 1))

    def test_ref_and_source_id_rebind_or_replay_strictly_rejected(self):
        env, old, warm = model_and_world(2)
        next_raw = study.evidence(
            "warm-bundle-world-02", study.collect_paired_interventions(env))
        with self.assertRaisesRegex(ValueError, "NKR11_SOURCE_ID_REBOUND"):
            old.stage_public_interventions(next_raw, digest(next_raw))
        repair = study.collect_paired_interventions(env)
        repair[0] = (warm[0][0], *repair[0][1:])
        raw = study.evidence("repair-bundle-world-02", repair)
        with self.assertRaisesRegex(ValueError, "NKR11_PUBLIC_SOURCE_REF_REPLAY"):
            old.stage_public_interventions(raw, digest(raw))
        raw = study.evidence("repair-bundle-world-02",
                             study.collect_paired_interventions(env))
        changed, _ = old.stage_public_interventions(raw, digest(raw))
        rebound = study.evidence("repair-bundle-world-02",
                                 [("new-ref-event-01", 0, 1, 0)])
        with self.assertRaisesRegex(ValueError, "NKR11_SOURCE_ID_REBOUND"):
            changed.stage_public_interventions(rebound, digest(rebound))

    def test_only_exact_pinned_public_observations_and_kind_are_accepted(self):
        env, old, _ = model_and_world(4)
        repair = study.collect_paired_interventions(env)
        raw = study.evidence("repair-bundle-world-04", repair)
        with self.assertRaisesRegex(ValueError, "NKR11_PUBLIC_BUNDLE_SHA_DRIFT"):
            old.stage_public_interventions(raw, "0"*64)
        tampered = json.loads(raw.decode("ascii"))
        tampered["source_kind"] = "invented_hypothesis"
        wrong = canonical(tampered)
        with self.assertRaises(PermissionError):
            old.stage_public_interventions(wrong, digest(wrong))
        tampered["source_kind"] = SOURCE_KIND
        tampered["source_mode"] = "owner_live_verified"
        wrong = canonical(tampered)
        with self.assertRaises(PermissionError):
            old.stage_public_interventions(wrong, digest(wrong))
        bad = list(repair)
        bad[1] = (bad[0][0], *bad[1][1:])
        wrong = study.evidence("repair-invalid-ref-04", bad)
        with self.assertRaisesRegex(ValueError, "NKR11_DUPLICATE_REF_OR_INTERVENTION"):
            old.stage_public_interventions(wrong, digest(wrong))

    def test_canonical_checkpoint_shas_bind_each_evidence_bundle(self):
        env, old, _ = model_and_world(5)
        repair_raw = study.evidence("repair-bundle-world-05",
                                    study.collect_paired_interventions(env))
        model, _ = old.stage_public_interventions(repair_raw, digest(repair_raw))
        obj = json.loads(model.checkpoint().decode("ascii"))
        obj["scientific_pass"] = True
        fake = canonical(obj)
        with self.assertRaisesRegex(ValueError, "NKR11_CHECKPOINT_SCHEMA_OR_ACCEPTANCE"):
            NativeInterventionRepair(fake, digest(fake))
        obj["scientific_pass"] = False
        obj["warm_records"][0][3] ^= 1
        fake = canonical(obj)
        with self.assertRaisesRegex(ValueError, "NKR11_WARM_SOURCE_SHA_DRIFT"):
            NativeInterventionRepair(fake, digest(fake))
        obj = json.loads(model.checkpoint().decode("ascii"))
        obj["repair_records"][-1][3] ^= 1
        fake = canonical(obj)
        with self.assertRaisesRegex(ValueError, "NKR11_REPAIR_SOURCE_SHA_DRIFT"):
            NativeInterventionRepair(fake, digest(fake))
        with self.assertRaisesRegex(ValueError, "NKR11_CHECKPOINT_SHA_DRIFT"):
            NativeInterventionRepair(model.checkpoint(), "0"*64)

    def test_invalid_frozen_context_and_binary_values_fail_closed(self):
        _, old, _ = model_and_world(7)
        base = [("public-invalid-000", 0, 1, 0)]
        for bad in (
            [("public-invalid-000", 16, 1, 0)],
            [("public-invalid-000", 0, 3, 0)],
            [("public-invalid-000", 0, 1, 3)],
            [("public-invalid-000", True, 1, 0)],
            base * 33,
        ):
            raw = study.evidence("repair-invalid-bundle-07", bad)
            with self.assertRaises(ValueError):
                old.stage_public_interventions(raw, digest(raw))
        with self.assertRaises(ValueError):
            old.predict(-1, 1)
        with self.assertRaises(ValueError):
            old.prior(0, True)

if __name__ == "__main__":
    unittest.main()
