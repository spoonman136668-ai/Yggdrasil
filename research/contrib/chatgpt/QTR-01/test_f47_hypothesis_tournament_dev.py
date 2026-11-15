"""F47 frozen source-free hypothesis tournament tests and negative controls."""
import json
import tempfile
from pathlib import Path
import unittest

from f47_hypothesis_tournament_dev import (
    POLICY, BUDGETS, DEGREES, MODES, POLICIES, PATTERNS, SEEDS, SIZES,
    World, RowBudgetArm, RejectedF47, freeze, qualitative_votes,
    signed_category, validate_one_world, run,
)
from f46_active_intervention_dev import LocalLearner, MLE, F46Rejected
from f45_context_causal_induction_dev import LocalContextWeights


class TestF47(unittest.TestCase):
    def test_frozen_source_and_explicit_science_fence(self):
        p=freeze()
        self.assertEqual(p["status"],"FROZEN_BEFORE_F47_CODE_OR_RESULTS")
        self.assertEqual(p["source_parent"],
                         "e3fc033c8b9e3bd06d456cf4584914c9ce0c6dc4")
        self.assertEqual(p["worlds"]["sizes_high_first"],[64,32,16])
        self.assertEqual(p["worlds"]["seeds"],[127,131,137])
        self.assertEqual(p["worlds"]["budgets_mean_repetitions_high_first"],[24,12,6])
        self.assertTrue(all(p["fences"].values()))

    def test_prereg_drift_rejected_without_mutating_source(self):
        raw=POLICY.read_bytes()
        document=json.loads(raw)
        document["frozen_go"]["b12_native_tournament_direct_gain_over_uniform_min"]=0
        with tempfile.TemporaryDirectory() as td:
            changed=Path(td)/"tampered.json"
            changed.write_text(json.dumps(document),encoding="utf-8")
            with self.assertRaisesRegex(RejectedF47,"PREREG_SOURCE_CUSTODY_DRIFT"):
                freeze(changed)
        self.assertEqual(POLICY.read_bytes(),raw)

    def test_distinct_new_hidden_worlds_and_context_rules(self):
        for n in SIZES:
            for seed in SEEDS:
                a=World(n,seed)
                b=World(n,seed)
                self.assertEqual(a.evaluator_only_truth(),b.evaluator_only_truth())
                self.assertEqual(a.mode,MODES[seed])
                hist=a.evaluator_degree_histogram()
                self.assertEqual(set(hist),set(map(str,DEGREES)))
                self.assertEqual(sum(hist.values()),n)
                self.assertEqual(len(a.intervene(0,1,0,0)),n)
                self.assertEqual(a.intervene(0,1,0,0),b.intervene(0,1,0,0))
                truth=a.evaluator_only_truth()
                self.assertTrue(all(s!=t and v in (-1,1)
                                    for (c,s,t),v in truth.items()))
                if seed==131:
                    self.assertTrue(all(c==1 for (c,s,t) in truth))
                if seed==137:
                    self.assertTrue(all(truth[(1,s,t)]==-v
                                        for (c,s,t),v in truth.items() if c==0))
                if seed==127:
                    self.assertTrue(all(truth[(1,s,t)]==v
                                        for (c,s,t),v in truth.items() if c==0))
        for n,seed in ((8,127),(128,127),(64,91),(64,True)):
            with self.subTest(n=n,seed=seed),self.assertRaisesRegex(
                    RejectedF47,"UNREGISTERED_WORLD"):
                World(n,seed)

    def test_public_intervention_fence(self):
        w=World(16,127)
        for args in ((16,0,0,0),(0,2,0,0),(0,1,2,0),(0,1,0,48)):
            with self.subTest(args=args),self.assertRaisesRegex(
                    RejectedF47,"INVALID_PUBLIC_INTERVENTION"):
                w.intervene(*args)

    def test_tournament_is_categorical_not_f46_continuous_uncertainty(self):
        self.assertEqual(signed_category(0.44),0)
        self.assertEqual(signed_category(-0.45),-1)
        self.assertEqual(signed_category(0.45),1)
        m=MLE(16)
        world=World(16,137)
        for c in (0,1):
            for k in range(6):
                m.observe_pair(0,c,world.intervene(0,c,0,k),
                               world.intervene(0,c,1,k))
        votes=qualitative_votes(m,0)
        self.assertEqual(len(votes),2)
        self.assertTrue(all(isinstance(z,int) and z>=0 for z in votes))
        self.assertEqual(PATTERNS,((1,1),(0,1),(1,-1)))

    def test_four_pair_coverage_precedes_discretion(self):
        w=World(16,127)
        arm=RowBudgetArm("native_tournament",16,127)
        for step in range(2*16*4):
            arm.step(w,step)
        self.assertTrue(all(count==4 for row in arm.native.seen for count in row))
        self.assertEqual(arm.priority_votes_count,0)
        arm.step(w,2*16*4)
        self.assertEqual(arm.priority_votes_count,1)
        self.assertEqual(sum(sum(row) for row in arm.native.seen),2*16*4+1)

    def test_source_f47_uses_unmodified_native_and_mle_cold_semantics(self):
        w=World(16,127)
        m=LocalLearner(16)
        control=MLE(16)
        for s in range(16):
            for c in (0,1):
                for k in range(4):
                    off=w.intervene(s,c,0,k)
                    on=w.intervene(s,c,1,k)
                    m.observe_pair(s,c,off,on)
                    control.observe_pair(s,c,off,on)
        self.assertEqual(m.inferred(),control.independent_inferred())
        snap=m.checkpoint()
        self.assertEqual(snap,LocalLearner.restore(snap).checkpoint())
        for bad in (snap[:-1],snap+b"\x00",snap[:-1]+bytes((snap[-1]^1,))):
            with self.assertRaises(F46Rejected):
                LocalLearner.restore(bad)

    def test_passive_only_cannot_identify_signed_causes(self):
        w=World(16,131)
        m=LocalContextWeights(16)
        for s in range(16):
            for c in (0,1):
                for k in range(4):
                    m.observe(s,c,0,w.intervene(s,c,0,k))
        self.assertEqual(m.inferred(),{})

    def test_single_world_all_budgets_and_qualitative_policy_distinctness(self):
        worlds,sec=validate_one_world(16,127)
        self.assertGreaterEqual(sec,0)
        self.assertEqual([w["mean_paired_repetitions"] for w in worlds],[24,12,6])
        for row in worlds:
            self.assertEqual(set(row["policies"]),set(POLICIES))
            b=row["mean_paired_repetitions"]
            for p in row["policies"].values():
                self.assertEqual(p["pairs"],2*16*b)
                self.assertEqual(p["individual_actions"],4*16*b)
                self.assertEqual(p["public_outcome_bits"],4*16*16*b)
                self.assertTrue(p["cold_restore_exact"])
                self.assertTrue(p["tamper_rejected"])
                self.assertTrue(p["real_intervention_held_unrelated_row"])
                self.assertTrue(p["same_stream_independent_MLE_equal"])
            tour=row["policies"]["native_tournament"]
            self.assertGreaterEqual(tour["minimum_pair_count_per_row"],4)
            self.assertLessEqual(tour["maximum_pair_count_per_row"],2*b)

    def test_frozen_nine_worlds_three_budgets_full_negative_or_positive(self):
        d=run()
        self.assertEqual(d["scales_high_first"],[64,32,16])
        self.assertEqual(d["seeds"],[127,131,137])
        self.assertEqual(d["budgets_high_first"],[24,12,6])
        self.assertEqual(len(d["world_results"]),27)
        self.assertTrue(d["all_action_budgets_equal"])
        self.assertTrue(d["all_cold_and_interference_controls_pass"])
        self.assertTrue(d["all_native_min_exploration_and_row_caps"])
        self.assertIn(d["classification"],(
            "DEV_TOURNAMENT_ACTIVE_POLICY_GO","DEV_TOURNAMENT_ACTIVE_POLICY_NO_GO"))
        for k in ("hidden_world_graph_provided_to_learner",
                  "protected_scientific_first_use","accepted_native_source_changed",
                  "scientific_pass","deployed"):
            self.assertIs(d[k],False)


if __name__=="__main__":
    unittest.main()
