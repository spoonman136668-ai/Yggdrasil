"""NKR-13: bounded operator proposals, faithful cold source and noise fence."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

from yggdrasil.native_operator_discovery import (
    NativeOperatorDiscovery, canonical, digest, _fit_candidate)
from yggdrasil.public_causal_cells import PublicCausalCells

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location(
    "nkr13_test_fixture",ROOT/"research/contrib/chatgpt/NKR-13/experiment.py")
study=importlib.util.module_from_spec(spec)
spec.loader.exec_module(study)
envmod=study.nkr12


def setup(world=0, *, noise=False):
    env=envmod.IndependentActionWorld(world,mode="noise" if noise else "nonlinear")
    warm=envmod.observations(env,warm=True)
    original=envmod.bundle(f"nkr13-test-warm-{world:02d}",warm)
    prior=NativeOperatorDiscovery.from_warmup(original,digest(original))
    repair=envmod.observations(env,inject_single_sensor_noise=noise)
    raw=envmod.bundle(f"nkr13-test-repair-{world:02d}",repair)
    return env,prior,repair,raw


class OperatorDiscoveryTests(unittest.TestCase):
    def test_frozen_12_world_metric_and_strong_symbolic_tie(self):
        outcome=study.run_frozen()
        t=outcome["totals"]
        self.assertEqual(t["worlds"],12)
        self.assertEqual(t["cold_queries"],192)
        self.assertEqual(t["native_correct"],129)
        self.assertEqual(t["native_coverage"],129)
        self.assertEqual(t["native_confident_wrong"],0)
        self.assertEqual(t["strong_symbolic_correct"],129)
        self.assertEqual(t["strong_symbolic_confident_wrong"],0)
        self.assertEqual(t["strong_native_prediction_mismatches"],0)
        self.assertEqual(t["prior_memory_retained"],384)
        self.assertEqual(t["mechanism_changes_detected"],12)
        self.assertEqual(t["cold_replay_equal"],12)
        self.assertEqual(t["noise_false_repairs"],0)
        self.assertEqual(t["single_sensor_flip_refused"],4)
        self.assertTrue(outcome["frozen_dev_threshold_met"])
        self.assertFalse(outcome["scientific_pass"])
        self.assertFalse(outcome["accepted_native"])
        self.assertFalse(outcome["independent_strong_control_superiority"])

    def test_induced_conjunction_not_hardcoded_world_mask(self):
        env,old,events,source=setup(0)
        old_raw=old.checkpoint()
        successor,receipt=old.stage_public_interventions(source,digest(source))
        self.assertEqual(receipt["classification"],
                         "SOURCE_SUPPORTED_OPERATOR_PROPOSAL")
        self.assertTrue(successor.operator_discovered)
        self.assertEqual(successor.operator_masks,(3,))
        self.assertEqual(old.checkpoint(),old_raw)
        for x in envmod.COLD:
            for a in (0,1):
                self.assertEqual(successor.predict(x,a)["public_outcome"],
                                 env.execute(x,a))
        self.assertFalse(successor.predict(15,1)["native_accepted"])
        self.assertFalse(successor.predict(15,1)["verified_new_world_fact"])
        self.assertFalse(successor.predict(15,1)["can_write_causal_owner"])

    def test_unidentified_conjunctions_abstain_instead_of_guessing(self):
        env,prior,events,raw=setup(2)
        restored,_=prior.stage_public_interventions(raw,digest(raw))
        self.assertGreater(len(restored.operator_masks),1)
        self.assertEqual(restored.predict(6,1)["classification"],"UNKNOWN_ABSTAIN")
        self.assertIsNone(restored.predict(6,1)["public_outcome"])
        self.assertEqual(restored.predict(6,0)["public_outcome"],
                         env.execute(6,0))
        self.assertEqual(restored.predict(15,1)["public_outcome"],
                         env.execute(15,1))
        self.assertEqual(prior.predict(6,1)["classification"],"WARM_PRIOR_ONLY")

    def test_sensor_spike_no_permanent_operator_or_old_memory_change(self):
        for world in range(4):
            with self.subTest(world=world):
                env,prior,events,raw=setup(world,noise=True)
                before=prior.checkpoint()
                candidate,receipt=prior.stage_public_interventions(
                    raw,digest(raw))
                self.assertIs(candidate,prior)
                self.assertFalse(candidate.operator_discovered)
                self.assertEqual(receipt["classification"],
                                 "INSUFFICIENT_CHANGE_EVIDENCE")
                self.assertEqual(prior.checkpoint(),before)
                self.assertEqual(prior.prior(3,1),
                                 env.execute(3,1,warm=True))

    def test_cold_repair_and_public_sha_tamper_no_acceptance(self):
        env,prior,events,raw=setup(10)
        old=prior.checkpoint()
        native=PublicCausalCells().snapshot()
        new,_=prior.stage_public_interventions(raw,digest(raw))
        self.assertTrue(new.operator_discovered)
        cold=NativeOperatorDiscovery(new.checkpoint(),new.checkpoint_sha256)
        self.assertEqual(cold.operator_masks,new.operator_masks)
        self.assertEqual(cold.predict(15,1),new.predict(15,1))
        self.assertEqual(prior.checkpoint(),old)
        self.assertEqual(PublicCausalCells().snapshot(),native)
        with self.assertRaisesRegex(ValueError,"NKR13_CHECKPOINT_SHA_DRIFT"):
            NativeOperatorDiscovery(new.checkpoint(),"0"*64)
        document=json.loads(new.checkpoint())
        document["scientific_pass"]=True
        forged=canonical(document)
        with self.assertRaisesRegex(ValueError,"NKR13_CHECKPOINT_CONTRACT_DRIFT"):
            NativeOperatorDiscovery(forged,digest(forged))
        document=json.loads(new.checkpoint())
        document["repair"]["proposal"]["candidate_masks"]=[1]
        forged=canonical(document)
        with self.assertRaisesRegex(ValueError,"NKR13_REPAIR_PROPOSAL_RECONSTRUCTION_DRIFT"):
            NativeOperatorDiscovery(forged,digest(forged))
        document=json.loads(new.checkpoint())
        document["repair"]["records"][0][3]^=1
        forged=canonical(document)
        with self.assertRaisesRegex(ValueError,"NKR13_REPAIR_PUBLIC_SOURCE_DRIFT"):
            NativeOperatorDiscovery(forged,digest(forged))

    def test_wrong_kind_order_source_rebound_and_duplicate_no_effect(self):
        _,old,rows,raw=setup(1)
        with self.assertRaisesRegex(ValueError,"NKR11_PUBLIC_BUNDLE_SHA_DRIFT"):
            old.stage_public_interventions(raw,"0"*64)
        decoded=json.loads(raw)
        decoded["source_kind"]="hypothesis"
        invalid=canonical(decoded)
        with self.assertRaises(PermissionError):
            old.stage_public_interventions(invalid,digest(invalid))
        decoded=json.loads(raw)
        decoded["records"][0],decoded["records"][1]=decoded["records"][1],decoded["records"][0]
        invalid=canonical(decoded)
        with self.assertRaisesRegex(ValueError,"NKR13_FROZEN_ACTION_SEQUENCE_CHANGED"):
            old.stage_public_interventions(invalid,digest(invalid))
        decoded=json.loads(raw)
        decoded["source_id"]="nkr13-test-warm-01"
        invalid=canonical(decoded)
        with self.assertRaisesRegex(ValueError,"NKR13_FEEDBACK_REUSES_WARM_SOURCE"):
            old.stage_public_interventions(invalid,digest(invalid))
        new,_=old.stage_public_interventions(raw,digest(raw))
        same,receipt=new.stage_public_interventions(raw,digest(raw))
        self.assertIs(same,new)
        self.assertEqual(receipt["new_events"],0)
        decoded=json.loads(raw)
        decoded["records"][0][3]^=1
        altered=canonical(decoded)
        with self.assertRaisesRegex(ValueError,"NKR13_REPAIR_SOURCE_REBOUND"):
            new.stage_public_interventions(altered,digest(altered))

    def test_unsupported_operator_family_does_not_promote_speculation(self):
        _,prior,rows,raw=setup(0)
        # Keep two contradictions but deliberately falsify the
        # context-independent base parity at an a0 non-singleton position.
        noisy=json.loads(raw)
        for row in noisy["records"]:
            if row[1]==3 and row[2]==0:
                row[3]^=1
        altered=canonical(noisy)
        candidate,receipt=prior.stage_public_interventions(altered,digest(altered))
        self.assertIs(candidate,prior)
        self.assertEqual(receipt["classification"],"UNSUPPORTED_CONTEXT_BASE_ABSTAIN")
        self.assertFalse(prior.operator_discovered)

if __name__=="__main__":
    unittest.main()
