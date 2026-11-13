"""DG1-HC10 public-only probes, independent context control and budget tests."""
import unittest
import json
from interbank_policy import base,choose as candidate_choice,interbank_delta
from conventional_jsd import control,choose as conventional_choice,jsd
from eval_dev import SEEDS,PhysicalWorld,one_world


class DiscriminatingProbeTests(unittest.TestCase):
    def test_interbank_disagreement_is_pure_and_selects_real_causal_action(self):
        m=base.DualRegimeCausalCells()
        m.banks=[[1]*4,[2]*4]
        m.splits=1
        old=m.snapshot()
        self.assertEqual(interbank_delta(m,0,0),1)
        self.assertEqual(candidate_choice(m,0,0,8),("causal",0))
        self.assertEqual(m.snapshot(),old)

    def test_missing_second_context_falls_back_to_bounded_HC09_policy(self):
        m=base.DualRegimeCausalCells()
        for s in range(16):
            self.assertEqual(candidate_choice(m,s,0,8),m.choose(s,0,8))
        for bad in ((-1,0,8),(16,0,8),(0,9,8),(0,0,9),(0,True,8)):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    candidate_choice(m,*bad)

    def test_conventional_jsd_is_independently_calculated(self):
        m=control.ConventionalContextModel()
        m.contexts=[[1]*4,[2]*4]
        m.created=1
        frozen=m.snapshot()
        self.assertAlmostEqual(jsd(m,0,0),1.0)
        self.assertEqual(conventional_choice(m,0,0,8),("causal",0))
        self.assertEqual(m.snapshot(),frozen)
        self.assertEqual(control.ConventionalContextModel.restore(frozen).snapshot(),frozen)

    def test_charged_flip_no_model_training_label(self):
        w=PhysicalWorld(81001,"ABA")
        learner=base.DualRegimeCausalCells()
        state=81001%16
        old=learner.snapshot()
        moved=w.execute_physical_flip(state,2)
        self.assertEqual(moved,state^4)
        self.assertEqual(w.charged,1)
        self.assertEqual(learner.snapshot(),old)
        after=w.execute_causal(moved,0,0)
        learner.observe(moved,0,after)
        self.assertEqual(w.charged,2)
        self.assertEqual(learner.observations,1)

    def test_evaluator_queries_do_not_charge_or_feed_model(self):
        w=PhysicalWorld(81017,"OOD_cubic")
        for state in range(16):
            for action in range(4):
                w.evaluator_only_next(state,action,0)
        self.assertEqual(w.charged,0)
        for bad in ((-1,0,0),(16,0,0),(0,4,0),(0,0,2),(True,0,0)):
            with self.assertRaises(ValueError):
                w.evaluator_only_next(*bad)
        self.assertEqual(w.charged,0)

    def test_one_world_equal_action_allowances_and_cold_parity(self):
        for seed,group in ((81001,"ABA"),(81009,"stationary_majority"),
                           (81017,"OOD_cubic")):
            world=one_world(seed,group)
            expected=40 if group=="ABA" else 48
            for name,receipt in world["arms"].items():
                self.assertEqual(receipt["charged_real_actions"],expected,name)
                self.assertEqual(receipt["charged_mechanism_actions"]+
                                 receipt["charged_exogenous_flips"],expected,name)
                self.assertLessEqual(receipt["charged_exogenous_flips"],8,name)
                self.assertTrue(receipt["cold_restore_identical"],name)
                self.assertLessEqual(receipt["snapshot_bytes"],4096,name)
                self.assertEqual(sum(receipt["final"][k] for k in
                                 ("correct","wrong_confident","abstained")),64,name)
                if group=="ABA":
                    self.assertEqual(set(receipt["intermediate_evaluator_only"]),
                                     {"16","32","40"})
                    self.assertEqual(receipt["final"],
                                     receipt["intermediate_evaluator_only"]["40"])

    def test_fixed_cohorts_and_isolation(self):
        all_seeds=[s for cohort in SEEDS.values() for s in cohort]
        self.assertEqual(len(all_seeds),24)
        self.assertEqual(len(set(all_seeds)),24)
        for family,seeds in SEEDS.items(): self.assertEqual(len(seeds),8)
        with self.assertRaises(ValueError):
            PhysicalWorld(81001,"OOD_cubic")

    def test_previous_model_cold_restore_and_corruptions_fail_closed(self):
        for model in (base.DualRegimeCausalCells,control.ConventionalContextModel):
            m=model()
            m.observe(0,0,0)
            m.observe(0,0,1)
            src=m.snapshot()
            self.assertEqual(model.restore(src).snapshot(),src)
            changed=bytearray(src)
            changed[len(src)//2]^=1
            for bad in (bytes(changed),src[:-1],src+b"x",bytearray(src)):
                with self.subTest(model=model.__name__,length=len(bad)):
                    with self.assertRaises(ValueError):
                        model.restore(bad)

    def test_no_hidden_regime_or_training_oracle_parameter(self):
        w=PhysicalWorld(81001,"ABA")
        with self.assertRaises(TypeError):
            candidate_choice(base.DualRegimeCausalCells(),0,0,8,hidden_context=1)
        with self.assertRaises(TypeError):
            conventional_choice(control.ConventionalContextModel(),0,0,8,oracle=True)


if __name__=="__main__":
    unittest.main()
