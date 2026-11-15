"""ST4 source-only mechanics/negative fixtures, never candidate science."""
import json
import unittest

from research.nci04_st4.paired_world import (
    blind_design, PrivatePairedWorld, source_paired_trial,
    public_bits, check_public, rotation, delayed_mask, rotate_byte, TRIALS
)
from research.nci04_st4.source_audit import (
    evaluate_counts,TRAIN_LAWS,TRAIN_SEEDS
)


class ST4SourceOnly(unittest.TestCase):
    def test_public_bit_roundtrip_and_rotation(self):
        for n in (0,1,3,127,128,255):
            self.assertEqual(check_public(public_bits(n)),n)
        self.assertEqual(rotate_byte(129,1),3)
        for bad in (True, -1, 256, 1.5):
            with self.assertRaises(ValueError):
                public_bits(bad)

    def test_actor_design_never_uses_hidden_law(self):
        all_probes=set()
        first_arm=set()
        for seed in TRAIN_SEEDS:
            for trial in range(TRIALS):
                d=blind_design(seed,trial)
                self.assertEqual(set(d["arm_order"]),
                                 {"treatment","control"})
                self.assertIn(d["probe_action"],(0,1,3))
                all_probes.add(d["probe_action"])
                first_arm.add(d["arm_order"][0])
        self.assertEqual(all_probes,{0,1,3})
        self.assertEqual(first_arm,{"treatment","control"})

    def test_real_pair_same_current_state_and_probe_different_history(self):
        r=source_paired_trial(3,100,0)
        self.assertTrue(r["same_initial_public"])
        self.assertTrue(r["same_pre_probe_public"])
        self.assertTrue(r["same_current_probe_action"])
        self.assertEqual(r["treatment_first_action"],2)
        self.assertEqual(r["control_first_action"],3)
        self.assertEqual(r["original_action_steps"],4)
        self.assertEqual(len(r["paired_original_action_consequence_sha256"]),64)
        self.assertEqual(
            r["different_real_probe_outcomes"], delayed_mask(3)!=0
        )
        self.assertFalse(r["learner_seen_private_law_or_paired_labels"])

    def test_no_immediate_causal_effect_of_delayed_action(self):
        left=PrivatePairedWorld(5,101,0)
        right=PrivatePairedWorld(5,101,0)
        x0=left.public()
        p_a,y_a=left.step(2)
        p_b,y_b=right.step(3)
        self.assertEqual(p_a,p_b)
        self.assertEqual(y_a,y_b)
        self.assertNotEqual(p_a,x0)
        act=blind_design(101,0)["probe_action"]
        a,_=left.step(act)
        b,_=right.step(act)
        self.assertEqual(
            check_public(a)^check_public(b),delayed_mask(5)
        )

    def test_two_real_source_steps_and_byte_exact_cold_restart(self):
        model=PrivatePairedWorld(7,103,4)
        model.step(2)
        snap=model.snapshot()
        other=PrivatePairedWorld.restore(snap)
        self.assertEqual(other.snapshot(),snap)
        self.assertEqual(model.step(3),other.step(3))
        self.assertEqual(model.snapshot(),other.snapshot())
        with self.assertRaises(ValueError):
            model.step(3)

    def test_no_invalid_public_action_mutates_private_source(self):
        w=PrivatePairedWorld(3,100,0)
        snap=w.snapshot()
        for bad in (-1,4,True,1.5,"2"):
            with self.assertRaises(ValueError):
                w.step(bad)
            self.assertEqual(w.snapshot(),snap)

    def test_canonical_source_checkpoint_rejects_tampering(self):
        w=PrivatePairedWorld(3,100,0)
        base=json.loads(w.snapshot())
        for mutate in (
            lambda d:d.update(schema="wrong"),
            lambda d:d.update(pending=256),
            lambda d:d.update(public=-1),
            lambda d:d.update(trial=16),
            lambda d:d.update(law=True),
            lambda d:d.update(step=3),
        ):
            p=dict(base);mutate(p)
            with self.assertRaises(ValueError):
                PrivatePairedWorld.restore(
                    json.dumps(p,sort_keys=True,separators=(",",":"))
                )

    def test_frozen_identifiability_boundary_and_fail_closed_negatives(self):
        counts={law:192 for law in TRAIN_LAWS}
        probes={0:512,1:512,3:512}
        orders={"treatment":768,"control":768}
        r=evaluate_counts(1536,counts,probes,orders)
        self.assertEqual(r["disposition"],
                         "SOURCE_BALANCED_INTERVENTIONS_IDENTIFIABLE_DEV_ONLY")
        counts[TRAIN_LAWS[0]]=181 # below 95% of 192
        self.assertEqual(
            evaluate_counts(1536,counts,probes,orders)["disposition"],
            "SOURCE_COUNTERFACTUAL_IDENTIFIABILITY_NO_GO"
        )
        counts[TRAIN_LAWS[0]]=192
        probes[3]=99
        self.assertEqual(
            evaluate_counts(1536,counts,probes,orders)["disposition"],
            "SOURCE_COUNTERFACTUAL_IDENTIFIABILITY_NO_GO"
        )
        probes[3]=512
        self.assertEqual(
            evaluate_counts(1499,counts,probes,orders)["disposition"],
            "SOURCE_COUNTERFACTUAL_IDENTIFIABILITY_NO_GO"
        )
        with self.assertRaises(ValueError):
            evaluate_counts(1536,counts,{0:512,1:512},orders)


if __name__=="__main__":
    unittest.main()
