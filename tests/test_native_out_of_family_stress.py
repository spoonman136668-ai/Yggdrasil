"""NKR-12: freeze source-free misspecification/noise falsification controls."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

from yggdrasil.native_intervention_repair import (
    NativeInterventionRepair,digest,
)
from yggdrasil.public_causal_cells import PublicCausalCells

SCRIPT=(Path(__file__).resolve().parents[1]/
        "research/contrib/chatgpt/NKR-12/experiment.py")
spec=importlib.util.spec_from_file_location("nkr12_frozen_experiment",SCRIPT)
study=importlib.util.module_from_spec(spec)
spec.loader.exec_module(study)


def sample(world, *, mode="nonlinear"):
    env=study.IndependentActionWorld(world,mode=mode)
    old=study.observations(env,warm=True)
    raw=study.bundle(f"nkr12-warm-fixture-{world:02d}",old)
    prior=NativeInterventionRepair.from_warmup(raw,digest(raw))
    return env,prior,study.observations(env)


class NativeOutOfFamilyStressTests(unittest.TestCase):
    def test_frozen_full_stress_exposes_confident_errors_and_safe_refusal(self):
        result=study.run_frozen()
        m=result["totals"]
        self.assertEqual(m["nonlinear_worlds"],12)
        self.assertEqual(m["sensor_noise_worlds"],4)
        self.assertEqual(m["cold_queries"],192)
        self.assertEqual(m["first_contradictions"],12)
        self.assertEqual(m["old_retention_correct"],384)
        self.assertGreater(m["native_confident_cold_errors"],0)
        self.assertGreater(m["native_rejected_inconsistent_evidence"],0)
        self.assertGreater(m["strong_abstained_on_native_wrong"],0)
        self.assertEqual(m["single_sensor_noise_false_repairs"],0)
        self.assertEqual(m["single_noise_old_checkpoint_preserved"],4)
        self.assertTrue(result["frozen_falsification_criteria_met"])
        self.assertFalse(result["scientific_pass"])
        self.assertFalse(result["native_accepted"])
        self.assertFalse(result["hypothesis_family_expanded_in_native"])

    def test_full_and_incomplete_conjunctions_are_outside_original_feature_family(self):
        # A degree-two trigger is revealed in x3 (0b0011) and yields a
        # contradiction that cannot be fitted by a parity-only relation.
        env,prior,records=sample(0)
        raw=study.bundle("nkr12-two-bit-public-00",records)
        original=prior.checkpoint()
        with self.assertRaisesRegex(ValueError,
                                    "NKR11_CONTRADICTORY_SAME_EPOCH_EVIDENCE"):
            prior.stage_public_interventions(raw,digest(raw))
        self.assertEqual(prior.checkpoint(),original)
        fit=study.independent_broader_symbolic_fit(records)
        self.assertEqual(fit[2],(3,))
        self.assertEqual(study.independent_broader_symbolic_predict(fit,15,1),
                         env.execute(15,1))

    def test_unseen_high_order_action_relation_causes_confident_wrong_prediction(self):
        # Four-way AND requires context 15, never sampled in the 16
        # training observations. NKR11 reports a confident but wrong value.
        env,prior,records=sample(10)
        raw=study.bundle("nkr12-four-bit-public-10",records)
        model,receipt=prior.stage_public_interventions(raw,digest(raw))
        self.assertTrue(model.change_detected)
        self.assertEqual(receipt["new_events"],16)
        native=model.predict(15,1)["public_outcome"]
        truth=env.execute(15,1)
        self.assertIsNotNone(native)
        self.assertNotEqual(native,truth)
        # The independent equally informed conjunction-family control
        # abstains because multiple masks remain source-consistent.
        fit=study.independent_broader_symbolic_fit(records)
        self.assertGreater(len(fit[2]),1)
        self.assertIsNone(study.independent_broader_symbolic_predict(fit,15,1))
        self.assertEqual(model.predict(15,1)["native_accepted"],False)

    def test_action_pair_custody_and_hidden_probes_never_observed_in_fit(self):
        env,prior,records=sample(8)
        self.assertEqual(len(records),16)
        self.assertEqual(len({(r[1],r[2]) for r in records}),16)
        self.assertEqual(records[0][1:3],(0,1))
        self.assertEqual(set(r[1] for r in records),set(study.TRAIN))
        self.assertFalse(set(study.COLD)&set(study.TRAIN))
        self.assertEqual(records[0][3],0)
        self.assertEqual(prior.prior(0,1),1)
        self.assertEqual(len(study.COLD),8)
        with self.assertRaises(ValueError):
            study.IndependentActionWorld(12)
        with self.assertRaises(ValueError):
            env.execute(16,1)

    def test_first_misleading_public_observation_refuses_permanent_repair(self):
        env,prior,_=sample(2,mode="noise")
        old=prior.checkpoint()
        measured=study.observations(env,inject_single_sensor_noise=True)
        self.assertEqual(
            sum(int(prior.prior(x,a)!=y) for _,x,a,y in measured),1)
        raw=study.bundle("nkr12-noise-only-02",measured)
        with self.assertRaisesRegex(ValueError,
                                    "NKR11_CONTRADICTORY_SAME_EPOCH_EVIDENCE"):
            prior.stage_public_interventions(raw,digest(raw))
        self.assertEqual(prior.checkpoint(),old)
        self.assertFalse(prior.change_detected)

    def test_source_sha_is_exact_not_a_real_world_authenticity_certificate(self):
        env,prior,records=sample(11)
        before=PublicCausalCells().snapshot()
        raw=study.bundle("nkr12-source-fixture-11",records)
        with self.assertRaisesRegex(ValueError,"NKR11_PUBLIC_BUNDLE_SHA_DRIFT"):
            prior.stage_public_interventions(raw,"0"*64)
        strong=study.independent_broader_symbolic_fit(records)
        self.assertIn(study.AND_MASKS[11],strong[2])
        self.assertFalse(prior.change_detected)
        self.assertEqual(PublicCausalCells().snapshot(),before)


if __name__=="__main__":
    unittest.main()
