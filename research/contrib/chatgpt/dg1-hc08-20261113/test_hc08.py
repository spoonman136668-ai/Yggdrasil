"""DG1-HC08 public-physics controls and source-only DEV engineering tests."""
import json
import unittest
from steering_policy import base, choose_intervention
from bayesian_steering_policy import bayes, decide_bayesian
from eval_dev import COHORTS,PhysicalWorld,one_world


class ChargedControllabilityTests(unittest.TestCase):
    def test_force_is_real_and_not_a_causal_training_observation(self):
        w=PhysicalWorld(51001,"known_absorbing_dev")
        m=base.AffineCausalCells()
        state=51001%16
        initial=m.snapshot()
        new=w.apply_forced_flip(state,2)
        self.assertEqual(new,state^4)
        self.assertEqual(w.costed_forced,1)
        self.assertEqual(w.total_charged,1)
        self.assertEqual(m.snapshot(),initial)
        before=w.costed_causal
        w.evaluate_without_charge(new,0,phase=0)
        self.assertEqual(w.costed_causal,before)
        after=w.apply_causal(new,0,phase=0)
        m.observe(new,0,after)
        self.assertEqual(m.observations,1)
        self.assertEqual(w.total_charged,2)

    def test_no_actuator_frozen_absorbing_replay(self):
        row=one_world(51001,"known_absorbing_dev")
        arm=row["arms"]["no_actuator"]
        self.assertEqual(arm["distinct_public_states"],1)
        self.assertEqual(arm["forced_flips"],0)
        self.assertEqual(arm["total_charged"],48)
        self.assertEqual(arm["score"]["correct"],4)
        self.assertEqual(arm["score"]["wrong_confident"],0)

    def test_actuator_can_reach_unseen_state_from_absorbing_state(self):
        row=one_world(51001,"known_absorbing_dev")
        self.assertGreater(row["arms"]["candidate"]["distinct_public_states"],1)
        self.assertGreater(row["arms"]["candidate"]["forced_flips"],0)
        self.assertEqual(row["arms"]["candidate"]["total_charged"],48)
        self.assertLessEqual(row["arms"]["candidate"]["forced_flips"],8)
        self.assertEqual(row["arms"]["candidate"]["sham_actions"],0)

    def test_candidate_selection_is_pure_and_actuation_capped(self):
        m=base.AffineCausalCells()
        before=m.snapshot()
        for s in range(16):
            kind,j=choose_intervention(m,s,0,8)
            self.assertEqual(kind,"causal")
            self.assertIn(j,range(4))
        self.assertEqual(m.snapshot(),before)
        m.surviving=[1,1,1,1]
        before=m.snapshot()
        kind,j=choose_intervention(m,9,0,8)
        self.assertEqual(kind,"flip")
        self.assertIn(j,range(4))
        self.assertEqual(m.snapshot(),before)
        self.assertEqual(choose_intervention(m,9,8,8),("causal",0))

    def test_bayesian_controller_has_independent_policy_and_same_interface(self):
        m=bayes.BayesianGraphController()
        old=m.snapshot()
        self.assertEqual(decide_bayesian(m,0,0,8)[0],"causal")
        m.posterior_masks=[1,1,1,1]
        self.assertEqual(decide_bayesian(m,9,0,8)[0],"flip")
        self.assertEqual(decide_bayesian(m,9,8,8),("causal",0))
        self.assertNotEqual(old,m.snapshot())

    def test_each_control_has_same_charged_step_budget(self):
        for seed,cohort in ((51002,"known_absorbing_dev"),
                            (61001,"unseen_rewired"),
                            (61013,"negative_majority"),
                            (61017,"unseen_ABA")):
            r=one_world(seed,cohort)
            charge=25 if cohort=="unseen_ABA" else 48
            limit=4 if cohort=="unseen_ABA" else 8
            for name,a in r["arms"].items():
                self.assertEqual(a["total_charged"],charge,name)
                self.assertEqual(a["causal_observations"]+
                                 a["forced_flips"]+a["sham_actions"],charge,name)
                self.assertLessEqual(a["forced_flips"]+a["sham_actions"],limit,name)
                self.assertTrue(a["cold_restore_exact"],name)
                self.assertEqual(a["logical_program_mask_bits"],128,name)
                self.assertEqual(sum(a["score"][k] for k in
                                 ("correct","wrong_confident","abstained")),64)

    def test_no_free_world_queries_or_hidden_regime_labels(self):
        w=PhysicalWorld(61017,"unseen_ABA")
        for s in range(16):
            for a in range(4):
                w.evaluate_without_charge(s,a,0)
        self.assertEqual(w.total_charged,0)
        w.apply_causal(0,0,phase=1)
        self.assertEqual(w.total_charged,1)
        self.assertRaises(TypeError,w.apply_causal,0,0,0,secret_graph=1)

    def test_checkpoint_integrity_and_invalid_inputs(self):
        for ctor in (base.AffineCausalCells,bayes.BayesianGraphController):
            m=ctor()
            s=m.snapshot()
            self.assertEqual(ctor.restore(s).snapshot(),s)
            tamper=bytearray(s)
            tamper[len(s)//2]^=1
            for bad in (bytes(tamper),s[:-1],s+b"x",bytearray(s)):
                with self.assertRaises(ValueError):
                    ctor.restore(bad)
        m=base.AffineCausalCells()
        snap=m.snapshot()
        for bad in ((0,0,2),(-1,0,0),(0,4,0),(0,0,16)):
            with self.assertRaises(ValueError):
                m.observe(*bad)
            self.assertEqual(m.snapshot(),snap)
        for args in ((9,-1,8),(9,9,8),(True,0,8),(9,0,9)):
            with self.assertRaises(ValueError):
                choose_intervention(m,*args)

    def test_new_cohorts_are_disjoint_and_replay_is_exploratory(self):
        self.assertEqual(len(COHORTS["known_absorbing_dev"]),3)
        allseeds=[seed for cohort,seeds in COHORTS.items()
                  if cohort!="known_absorbing_dev" for seed in seeds]
        self.assertEqual(len(allseeds),20)
        self.assertEqual(len(set(allseeds)),len(allseeds))
        self.assertFalse(set(allseeds)&set(COHORTS["known_absorbing_dev"]))


if __name__=="__main__":
    unittest.main()
