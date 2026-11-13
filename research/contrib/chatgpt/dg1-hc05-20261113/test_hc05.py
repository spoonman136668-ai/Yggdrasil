"""HC05 source-only engineering tests; source worlds are never model imports."""
import json
import unittest

from model import (
    CausalProbeCells, ConventionalEquivalentPlanner, FULL_MASK,
    MAX_CHECKPOINT_BYTES, gini, local_effect,
)
from eval_dev import CHARGED_ACTIONS, one_world, one_policy, PhysicalWorld


class CausalInterventionsTests(unittest.TestCase):
    def test_initial_version_space_abstains_outside_observations(self):
        m = CausalProbeCells()
        self.assertEqual(m.logical_mask_bits, 24)
        self.assertEqual(m.masks, [FULL_MASK]*4)
        self.assertIsNone(m.predict(0,0))
        m.observe(0,0,0)  # Effect 0, sign=0, own slope still unknown.
        self.assertEqual(m.predict(0,0),0)
        self.assertIsNone(m.predict(1,0))
        self.assertEqual(m.observations,1)

    def test_real_contrasting_public_consequences_identify_law(self):
        m=CausalProbeCells()
        # Chosen physical world from hypothesis h=0 (parity neighbors).
        for state in (0,1,2):
            after=state ^ (local_effect(state,0,0)<<0)
            m.observe(state,0,after)
        self.assertEqual(m.masks[0],1)
        for state in range(16):
            self.assertEqual(m.predict(state,0),
                             state ^ (local_effect(state,0,0)<<0))

    def test_lookahead_is_pure_and_cannot_query_physics(self):
        model=CausalProbeCells()
        before=model.snapshot()
        for state in range(16):
            action=model.choose_lookahead(state)
            self.assertIn(action,range(4))
        self.assertEqual(model.snapshot(),before)
        self.assertEqual(model.observations,0)
        self.assertEqual(model.choose_greedy(0),0)

    def test_one_world_has_exact_same_charged_budget(self):
        row=one_world(31001,"stationary")
        arms=row["arms"]
        for name,record in arms.items():
            self.assertEqual(record["real_actions"],CHARGED_ACTIONS)
            self.assertLessEqual(record["checkpoint_bytes"],MAX_CHECKPOINT_BYTES)
            self.assertEqual(record["logical_hypothesis_bits"],24)
            self.assertTrue(record["cold_restore_parity"])
            self.assertEqual(sum(record["scored"][k] for k in
                             ("correct","wrong_confident","abstained")),64)
        self.assertEqual(arms["lookahead"]["ledger_sha256"],
                         arms["conventional"]["ledger_sha256"])
        self.assertEqual(arms["lookahead"]["scored"],
                         arms["conventional"]["scored"])

    def test_source_in_class_consensus_never_asserts_wrong_rule(self):
        for seed in (31002,31005):
            row=one_world(seed,"stationary")
            self.assertEqual(row["arms"]["lookahead"]["scored"]["wrong_confident"],0)

    def test_unknown_majority_family_failure_is_recorded_not_suppressed(self):
        row=one_world(31013,"out_of_grammar")
        score=row["arms"]["lookahead"]["scored"]
        self.assertEqual(sum(score[x] for x in
                         ("correct","wrong_confident","abstained")),64)

    def test_cold_restore_and_checksum_fails_closed(self):
        m=CausalProbeCells()
        m.observe(0,0,0)
        cp=m.snapshot()
        self.assertEqual(CausalProbeCells.restore(cp).snapshot(),cp)
        self.assertLessEqual(len(cp),MAX_CHECKPOINT_BYTES)
        edited=bytearray(cp)
        edited[15] ^= 1
        for bad in (bytes(edited),cp[:-1],cp+b" ",bytearray(cp),
                    b"x"*(MAX_CHECKPOINT_BYTES+1)):
            with self.subTest(type=type(bad).__name__,length=len(bad)):
                with self.assertRaises(ValueError):
                    CausalProbeCells.restore(bad)
        forged=json.loads(cp)
        forged["payload"]["masks"][1]=127
        with self.assertRaises(ValueError):
            CausalProbeCells.restore(json.dumps(forged).encode())

    def test_invalid_public_outcome_does_not_mutate(self):
        m=CausalProbeCells()
        initial=m.snapshot()
        for vals in ((0,0,2),(-1,0,0),(16,0,0),
                     (0,4,0),(True,0,0),(0,True,0),
                     (0,0,True),(0,0,16)):
            with self.subTest(vals=vals):
                with self.assertRaises(ValueError):
                    m.observe(*vals)
                self.assertEqual(m.snapshot(),initial)

    def test_all_six_causal_hypotheses_follow_boolean_effects(self):
        for state in range(16):
            for action in range(4):
                for h in range(6):
                    self.assertIn(local_effect(state,action,h),(0,1))
        self.assertEqual(gini(FULL_MASK,0,0),gini(FULL_MASK,8,0))

    def test_recorded_trajectory_is_independent_of_evaluator_queries(self):
        w=PhysicalWorld(31003)
        s=31003%16
        for t in range(CHARGED_ACTIONS):
            s=w.execute(s,t%4)
        self.assertEqual(w.executed_actions,CHARGED_ACTIONS)
        for state in range(16):
            w.counterfactual_for_evaluator_only(state,1)
        self.assertEqual(w.executed_actions,CHARGED_ACTIONS)


if __name__=="__main__":
    unittest.main()
