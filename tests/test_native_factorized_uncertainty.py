"""NKR-15: source-safe partial baseline/readout and original retention tests."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

from yggdrasil.native_operator_discovery import NativeOperatorDiscovery
from yggdrasil.native_intervention_repair import digest, canonical
from yggdrasil.public_causal_cells import PublicCausalCells

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location(
    "nkr15_frozen_experiment", ROOT/"research/contrib/chatgpt/NKR-15/experiment.py")
study=importlib.util.module_from_spec(spec)
spec.loader.exec_module(study)
nkr14=study.nkr14


def scenario(world):
    env=nkr14.HiddenWorld(world)
    warm=nkr14.warmup(env)
    raw=nkr14.freeze_bundle(f"nkr15-fixture-warm-{world}",warm)
    prior=NativeOperatorDiscovery.from_warmup(raw,digest(raw))
    observations=nkr14.source_visible_actions(env)
    public=nkr14.freeze_bundle(f"nkr15-fixture-public-{world}",observations)
    return env,prior,observations,public


class NativeFactorizedUncertaintyTests(unittest.TestCase):
    def test_frozen_baseline_only_repair_and_unrestricted_fallback(self):
        result=study.run_frozen()
        m=result["totals"]
        self.assertTrue(result["frozen_dev_threshold_met"])
        self.assertEqual(m["qualified_new_world_models"],11)
        self.assertEqual(m["identified_conjunction_operators"],2)
        self.assertEqual(m["baseline_only_models"],9)
        self.assertEqual(m["insufficient_evidence_refusals"],1)
        self.assertEqual(m["conditional_cold_correct"],98)
        self.assertEqual(m["conditional_cold_coverage"],104)
        self.assertEqual(m["conditional_cold_confident_wrong"],6)
        self.assertEqual(m["unrestricted_cold_correct"],88)
        self.assertEqual(m["unrestricted_cold_coverage"],88)
        self.assertEqual(m["unrestricted_cold_confident_wrong"],0)
        self.assertEqual(m["independent_conservative_correct"],96)
        self.assertEqual(m["old_retention"],384)
        self.assertEqual(m["single_sensor_noise_false_repairs"],0)
        self.assertEqual(result["old_conjunction_conditional_correct"],129)
        self.assertFalse(result["scientific_pass"])
        self.assertFalse(result["native_accepted"])

    def test_unsupported_action_effect_still_retains_action_zero_baseline(self):
        env,prior,observations,public=scenario(0)
        preserved=prior.checkpoint()
        next_,receipt=prior.stage_public_interventions(public,digest(public))
        self.assertEqual(receipt["classification"],
                         "SOURCE_SUPPORTED_BASELINE_ONLY_EFFECT_UNKNOWN")
        self.assertTrue(next_.operator_discovered)  # original staged-repair flag
        self.assertFalse(next_.operator_supported)
        self.assertEqual(next_.operator_masks,())
        self.assertNotEqual(next_.checkpoint(),preserved)
        self.assertEqual(prior.checkpoint(),preserved)
        for x in nkr14.COLD:
            self.assertEqual(next_.predict(x,0)["public_outcome"],
                             env.intervene(x,0))
            safe=next_.predict_unrestricted(x,0)
            self.assertEqual(safe["public_outcome"],env.intervene(x,0))
            self.assertEqual(safe["classification"],
                             "UNVERIFIED_ACTION_ZERO_PARITY_BASELINE")
            self.assertEqual(next_.predict(x,1)["classification"],
                             "UNKNOWN_ABSTAIN")
            self.assertIsNone(next_.predict_unrestricted(x,1)["public_outcome"])
        self.assertFalse(next_.predict_unrestricted(9,0)["can_write_causal_owner"])

    def test_qualified_wrong_conjunction_is_explicitly_only_conditional(self):
        env,prior,_,source=scenario(8)
        candidate,_=prior.stage_public_interventions(source,digest(source))
        self.assertTrue(candidate.operator_supported)
        # The original NKR14 failure was a false consequence at x6 action1
        # because the fixed conjunction grammar omitted OR-of-conjunctions.
        for x in nkr14.COLD:
            cautious=candidate.predict_unrestricted(x,1)
            self.assertIsNone(cautious["public_outcome"])
            self.assertEqual(cautious["classification"],
                             "UNKNOWN_UNRESTRICTED_ACTION_EFFECT")
        self.assertEqual(candidate.predict_unrestricted(6,0)["public_outcome"],
                         env.intervene(6,0))
        self.assertFalse(candidate.predict_unrestricted(6,0)["native_accepted"])

    def test_single_mismatch_world_and_sensor_error_stay_unqualified(self):
        env,prior,observations,source=scenario(2)
        original=prior.checkpoint()
        candidate,receipt=prior.stage_public_interventions(source,digest(source))
        self.assertIs(candidate,prior)
        self.assertEqual(receipt["classification"],
                         "INSUFFICIENT_CHANGE_EVIDENCE")
        self.assertEqual(candidate.checkpoint(),original)
        for x in nkr14.COLD:
            for action in (0,1):
                safe=candidate.predict_unrestricted(x,action)
                self.assertIsNone(safe["public_outcome"])
                self.assertEqual(safe["classification"],
                                 "UNKNOWN_NO_NEW_SOURCE_QUALIFICATION")

    def test_hash_cold_restore_and_replay_fail_closed(self):
        env,prior,_,source=scenario(1)
        before_native=PublicCausalCells().snapshot()
        updated,_=prior.stage_public_interventions(source,digest(source))
        cold=NativeOperatorDiscovery(updated.checkpoint(),
                                     updated.checkpoint_sha256)
        self.assertEqual(cold.predict_unrestricted(9,0),
                         updated.predict_unrestricted(9,0))
        unchanged,dup=cold.stage_public_interventions(source,digest(source))
        self.assertIs(unchanged,cold)
        self.assertEqual(dup["new_events"],0)
        with self.assertRaisesRegex(ValueError,"NKR11_PUBLIC_BUNDLE_SHA_DRIFT"):
            prior.stage_public_interventions(source,"0"*64)
        serialized=json.loads(updated.checkpoint())
        serialized["repair"]["proposal"]["base_mask"]^=1
        tampered=canonical(serialized)
        with self.assertRaisesRegex(ValueError,
                                    "NKR13_REPAIR_PROPOSAL_RECONSTRUCTION_DRIFT"):
            NativeOperatorDiscovery(tampered,digest(tampered))
        self.assertEqual(before_native,PublicCausalCells().snapshot())

    def test_direct_observation_is_not_mistaken_for_heldout_prediction(self):
        env,prior,_,source=scenario(0)
        staged,_=prior.stage_public_interventions(source,digest(source))
        seen=staged.predict_unrestricted(0,1)
        self.assertEqual(seen["classification"],
                         "DIRECTLY_OBSERVED_PUBLIC_OUTCOME_NOT_COLD_PREDICTION")
        self.assertEqual(seen["public_outcome"],env.intervene(0,1))
        self.assertFalse(seen["verified_new_world_fact"])
        with self.assertRaises(ValueError):
            staged.predict_unrestricted(16,0)
        with self.assertRaises(ValueError):
            staged.predict_unrestricted(0,2)
        self.assertFalse(staged.predict_unrestricted(7,0)["scientific_pass"])


if __name__=="__main__":
    unittest.main()
