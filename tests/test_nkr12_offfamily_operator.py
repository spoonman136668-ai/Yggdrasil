"""NKR-12: out-of-family causal action consequences and fail-closed negatives."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

from yggdrasil.native_intervention_repair import (
    NativeInterventionRepair, IntegerCausalSignature, canonical, digest,
)
from yggdrasil.public_causal_cells import PublicCausalCells

SOURCE = (Path(__file__).resolve().parents[1] /
          "research/contrib/chatgpt/NKR-12/experiment.py")
spec = importlib.util.spec_from_file_location("nkr12_outside_family", SOURCE)
study = importlib.util.module_from_spec(spec)
spec.loader.exec_module(study)


class OutsideFamilyCausalOperatorTests(unittest.TestCase):
    def test_all_twelve_worlds_frozen_offfamily_causal_falsification(self):
        before = PublicCausalCells().snapshot()
        result = study.run_frozen()
        totals = result["totals"]
        self.assertTrue(result["frozen_engineering_safety_pass"])
        self.assertEqual(result["classification"],
                         "OUTSIDE_FAMILY_NATIVE_REPRESENTATION_NO_GO_SAFE_REJECTION")
        self.assertEqual(totals["worlds"], 12)
        self.assertEqual(totals["old_public_actions"], 384)
        self.assertEqual(totals["new_public_actions"], 192)
        self.assertEqual(totals["cold_queries"], 192)
        self.assertEqual(totals["native_inconsistent_rejections"], 12)
        self.assertEqual(totals["native_accepted_repairs"], 0)
        self.assertEqual(totals["native_qualified_repair_coverage"], 0)
        self.assertEqual(totals["native_unsupported_confident_predictions"], 0)
        self.assertEqual(totals["first_public_contradictions"], 12)
        self.assertEqual(totals["old_retained_correct"], 384)
        self.assertEqual(totals["strong_reference_unique_fits"], 12)
        self.assertEqual(totals["strong_reference_correct"], 192)
        self.assertEqual(totals["strong_reference_covered"], 192)
        self.assertEqual(len(result["world_receipts"]), 12)
        self.assertFalse(result["scientific_pass"])
        self.assertFalse(result["accepted_native"])
        self.assertFalse(result["outside_family_native_learning_success"])
        self.assertFalse(result["historical_knowledge_source_opened"])
        self.assertEqual(PublicCausalCells().snapshot(), before)

    def test_exact_synthetic_source_first_contradiction_and_no_lookahead(self):
        for world in range(study.WORLDS):
            env = study.InterventionWorld(world)
            warm = study.warm_events(env)
            model_source = study.bundle(f"nkr12-warm-world-{world:02d}", warm)
            model = NativeInterventionRepair.from_warmup(
                model_source, digest(model_source))
            evidence = study.repair_events(env)
            self.assertEqual(len(evidence), 16)
            self.assertEqual(len({(x, a) for _, x, a, _ in evidence}), 16)
            self.assertEqual(evidence[0][1:], (0, 1, 0))
            self.assertEqual(model.prior(0, 1), 1)
            self.assertEqual({x for _, x, _, _ in evidence}, set(study.TRAIN))
            self.assertFalse(set(study.TRAIN) & set(study.COLD))
            self.assertEqual(env.action_calls, 48)

    def test_strong_conventional_exact_fitted_control_no_privileged_operator(self):
        for world in range(study.WORLDS):
            env = study.InterventionWorld(world)
            public = study.repair_events(env)
            solutions = study.conventional_fit(public)
            self.assertEqual(len(solutions), 1)
            # Reference fits only public selected action/consequence tuples.
            for x in study.COLD:
                for a in (0, 1):
                    self.assertEqual(study.conventional_predict(
                        solutions, x, a), env.intervene(x, a))

    def test_old_checkpoint_is_exact_byte_identical_after_rejected_operator(self):
        for world in range(study.WORLDS):
            env = study.InterventionWorld(world)
            old_raw = study.bundle(f"nkr12-warm-world-{world:02d}",
                                   study.warm_events(env))
            old = NativeInterventionRepair.from_warmup(
                old_raw, digest(old_raw))
            before = old.checkpoint()
            after_raw = study.bundle(f"nkr12-repair-world-{world:02d}",
                                     study.repair_events(env))
            with self.assertRaisesRegex(
                    ValueError, "NKR11_CONTRADICTORY_SAME_EPOCH_EVIDENCE"):
                old.stage_public_interventions(after_raw, digest(after_raw))
            self.assertEqual(old.checkpoint(), before)
            self.assertEqual(old.checkpoint_sha256, digest(before))
            self.assertFalse(old.change_detected)
            self.assertEqual(NativeInterventionRepair(
                before, digest(before)).checkpoint(), before)

    def test_one_observation_cannot_identify_unseen_context_effect(self):
        partial = IntegerCausalSignature((
            ("nkr12-partial-event-00", 0, 1, 0),))
        self.assertEqual(partial.rank, 1)
        self.assertEqual(partial.predict(0, 1), 0)
        self.assertIsNone(partial.predict(15, 1))
        self.assertIsNone(partial.predict(15, 0))

    def test_bad_source_kind_checksum_and_noncanonical_refused(self):
        env = study.InterventionWorld(0)
        raw = study.bundle("nkr12-warm-world-00", study.warm_events(env))
        model = NativeInterventionRepair.from_warmup(raw, digest(raw))
        new_raw = study.bundle("nkr12-repair-world-00",
                               study.repair_events(env))
        with self.assertRaisesRegex(ValueError,
                                    "NKR11_PUBLIC_BUNDLE_SHA_DRIFT"):
            model.stage_public_interventions(new_raw, "0"*64)
        obj = json.loads(new_raw)
        obj["source_kind"] = "inferred_fact"
        tampered = canonical(obj)
        with self.assertRaises(PermissionError):
            model.stage_public_interventions(tampered, digest(tampered))
        obj["source_kind"] = "observed_intervention"
        obj["source_mode"] = "owner_qualified"
        tampered = canonical(obj)
        with self.assertRaises(PermissionError):
            model.stage_public_interventions(tampered, digest(tampered))
        self.assertFalse(model.change_detected)

    def test_no_unearned_private_source_or_model_promotions(self):
        source = SOURCE.read_text(encoding="utf-8")
        self.assertNotIn("open_installed_session", source)
        self.assertNotIn("requests.get", source)
        self.assertNotIn("urlopen(", source)
        self.assertNotIn("from sklearn", source)
        self.assertEqual(len(study.GATES), 6)
        self.assertEqual(study.BASE_MASKS,
                         (1,2,4,8,3,5,6,9,10,12,13,14))
        self.assertEqual(study.TRAIN, (0,1,2,4,8,3,5,10))
        self.assertEqual(study.COLD, (6,7,9,11,12,13,14,15))
        for kind,i,j in study.GATES:
            self.assertIn(kind, ("AND", "OR"))
            self.assertNotEqual(i, j)


if __name__ == "__main__":
    unittest.main()
