"""HC07 source-only engineering tests. These are NOT frozen science results."""
import json
import unittest

from affine_cells import (
    AffineCausalCells, FULL, SNAP_LIMIT, program_effect,
    state_checked, action_checked,
)
from bayesian_graph_control import (
    BayesianGraphController, predicts_effect,
)
from eval_dev import SEEDS, SourceWorld, one_world


class CausalGraphTests(unittest.TestCase):
    def test_two_independent_implementations_match_all_affine_rules(self):
        for state in range(16):
            for program in range(32):
                self.assertEqual(program_effect(state,program),
                                 predicts_effect(state,program))

    def test_public_interventions_reveal_unknown_dependency_graph(self):
        # A unit-only hand-crafted observation sequence, not primary science.
        target_program=(0b1010<<1)|1
        model=AffineCausalCells()
        for state in range(16):
            physical_after=state^(program_effect(state,target_program)<<2)
            model.observe(state,2,physical_after)
        self.assertEqual(model.surviving[2],1<<target_program)
        for state in range(16):
            expected=state^(program_effect(state,target_program)<<2)
            self.assertEqual(model.predict(state,2),expected)
        self.assertEqual(model.logical_hypothesis_bits,128)

    def test_bayesian_control_independent_posterior_cold_parity(self):
        model=BayesianGraphController()
        for state in range(16):
            model.observe(state,1,state^(predicts_effect(state,15)<<1))
        self.assertEqual(model.posterior_masks[1],1<<15)
        checkpoint=model.snapshot()
        self.assertEqual(BayesianGraphController.restore(checkpoint).snapshot(),
                         checkpoint)

    def test_pre_learning_model_abstains_and_choose_has_no_effect(self):
        for klass in (AffineCausalCells,BayesianGraphController):
            m=klass()
            snap=m.snapshot()
            self.assertIsNone(m.predict(7,0))
            for state in range(16):
                self.assertIn(m.choose(state),range(4))
            self.assertEqual(m.snapshot(),snap)

    def test_conflicting_unrepresentable_public_evidence_fails_closed(self):
        model=AffineCausalCells()
        for s in range(16):
            model.observe(s,0,s^(program_effect(s,1)<<0))
        self.assertEqual(model.surviving[0],1<<1)
        model.observe(0,0,0) # h1 predicted toggle; contradiction
        self.assertEqual(model.surviving[0],0)
        self.assertEqual(model.violations,1)
        self.assertIsNone(model.predict(0,0))

    def test_public_input_rejection_is_atomic(self):
        for klass in (AffineCausalCells,BayesianGraphController):
            m=klass()
            snap=m.snapshot()
            for item in ((-1,0,0),(0,4,0),(16,0,0),
                         (0,0,2),(True,0,0),(0,True,0),(0,0,16)):
                with self.subTest(klass=klass.__name__,item=item):
                    with self.assertRaises(ValueError):
                        m.observe(*item)
                    self.assertEqual(m.snapshot(),snap)
            with self.assertRaises(TypeError):
                m.observe(0,0,0,regime="hidden")

    def test_checkpoint_bytes_integrity_and_type_fail_closed(self):
        for klass in (AffineCausalCells,BayesianGraphController):
            m=klass()
            m.observe(0,0,0)
            blob=m.snapshot()
            self.assertLessEqual(len(blob),SNAP_LIMIT)
            self.assertEqual(klass.restore(blob).snapshot(),blob)
            corrupted=bytearray(blob)
            corrupted[len(corrupted)//2]^=1
            for bad in (bytes(corrupted),blob[:-1],blob+b"x",
                        bytearray(blob),b"x"*(SNAP_LIMIT+1)):
                with self.subTest(klass=klass.__name__,length=len(bad)):
                    with self.assertRaises(ValueError):
                        klass.restore(bad)
            parsed=json.loads(blob)
            if klass is AffineCausalCells:
                parsed["payload"]["surviving"][0]=-1
            else:
                parsed["payload"]["posterior_masks"][0]=FULL+1
            with self.assertRaises(ValueError):
                klass.restore(json.dumps(parsed).encode("ascii"))

    def test_same_real_action_budget_in_frozen_source(self):
        for seed,cohort in ((51001,"rewired"),(51009,"old_ring"),
                            (51017,"non_affine"),(51025,"phase_switch")):
            row=one_world(seed,cohort)
            for name,arm in row["arms"].items():
                self.assertEqual(arm["real_physical_actions"],
                                 25 if cohort=="phase_switch" else 32)
                self.assertTrue(arm["cold_restore_exact"])
                self.assertLessEqual(arm["checkpoint_bytes"],1024)
                self.assertEqual(sum(arm["score"][k] for k in
                    ("correct","wrong_confident","abstained")),64)
                self.assertEqual(arm["score"]["unseen_total"],
                    sum(arm["score"]["unseen_"+k] for k in
                        ("correct","wrong_confident","abstained")))

    def test_heldout_audit_not_a_free_physical_action(self):
        world=SourceWorld(51001,"rewired")
        for i in range(16):
            for a in range(4):
                world.true_successor_for_audit(i,a,0)
        self.assertEqual(world.physical_actions,0)
        state=51001%16
        world.execute_real_action(state,0,0)
        self.assertEqual(world.physical_actions,1)

    def test_source_cohorts_are_disjoint_and_frozen(self):
        observed=set()
        for cohort,seeds in SEEDS.items():
            self.assertEqual(len(seeds),8)
            self.assertFalse(observed.intersection(seeds))
            observed.update(seeds)
        self.assertEqual(len(observed),32)
        with self.assertRaises(ValueError):
            SourceWorld(51001,"phase_switch")


if __name__=="__main__":
    unittest.main()
