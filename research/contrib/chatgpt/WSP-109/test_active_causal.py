"""Fixture-only WSP109 tests; NEVER evaluate FIT/TRANSFER world oracle queries.

All observations use preregistered fixture seeds 51001 and 51002, disjoint
from the frozen 31001..31012 and 41001..41012 test cohorts.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
import sys
import unittest

import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from world import (
    HYPOTHESES, ALL_4_BIT_MASKS, FIT_SEEDS, TRANSFER_SEEDS,
    FIXTURE_SEEDS, N_RULES, ACTION_BUDGET, private_law,
    feature_bits, query_scene, path_features, masked_feedback,
    random_action_sequence,
)
from learners import (
    DirectWeightPosterior, SymbolicBayes, ConventionalLogistic,
    _expected_entropy,
)
from experiment import anonymous_context, train_one_world, predict_pair


def fixture(seed):
    direct=DirectWeightPosterior()
    same=SymbolicBayes()
    optimal=SymbolicBayes()
    random=SymbolicBayes()
    fixed=SymbolicBayes()
    conventional=ConventionalLogistic()
    observations, posteriors=train_one_world(
        seed,direct,same,optimal,random,fixed,conventional)
    return direct,same,optimal,random,fixed,conventional,observations,posteriors


class TestPartialCausalDiscrimination(unittest.TestCase):
    def test_hypothesis_family_and_hidden_fixture_are_valid(self):
        self.assertEqual(len(ALL_4_BIT_MASKS),126)
        self.assertEqual(len(HYPOTHESES),36)
        self.assertEqual(len(set(HYPOTHESES)),36)
        self.assertTrue(all(int(x).bit_count()==4 for x in HYPOTHESES))
        self.assertEqual(len(FIT_SEEDS),12)
        self.assertEqual(len(TRANSFER_SEEDS),12)
        self.assertTrue(set(FIT_SEEDS).isdisjoint(TRANSFER_SEEDS))
        self.assertTrue(set(FIXTURE_SEEDS).isdisjoint(FIT_SEEDS+TRANSFER_SEEDS))
        for seed in FIXTURE_SEEDS:
            self.assertEqual(private_law(seed).bit_count(),4)
            self.assertIn(private_law(seed),HYPOTHESES)

    def test_all_policies_use_three_distinct_action_feedback(self):
        for seed in FIXTURE_SEEDS:
            direct,same,optimal,random,fixed,conv,observed,posterior=fixture(seed)
            for policy in ("greedy","depth3","random","fixed"):
                self.assertEqual(len(observed[policy]),ACTION_BUDGET)
                self.assertEqual(len(set(k for k,_ in observed[policy])),3)
                self.assertTrue(all(outcome is masked_feedback(seed,k)
                                    for k,outcome in observed[policy]))
            self.assertEqual([k for k,_ in observed["fixed"]],[0,1,2])
            self.assertEqual(tuple(k for k,_ in observed["random"]),
                             random_action_sequence(seed))
            self.assertEqual(observed["greedy"],[(k,same.observed[anonymous_context(seed)][k])
                            for k,_ in observed["greedy"]])
            self.assertEqual(posterior["direct_greedy"]["count"],
                             posterior["symbolic_greedy"]["count"])
            self.assertGreaterEqual(posterior["direct_greedy"]["count"],1)
            self.assertLessEqual(posterior["direct_greedy"]["count"],36)
            self.assertEqual(len(conv.theta),1)
            self.assertLessEqual(max(conv.gradients.values()),1e-9)

    def test_numeric_direct_matches_independent_symbolic_for_all_fixture_actions(self):
        for seed in FIXTURE_SEEDS:
            direct,same,optimal,rand,fixed,conv,_,_=fixture(seed)
            context=anonymous_context(seed)
            for index in range(64):
                scene=query_scene(seed,index)
                pred=predict_pair(context,scene,direct,same,optimal,rand,fixed,conv)
                for state in ("before","after"):
                    self.assertEqual(pred[state]["direct_greedy"],
                                     pred[state]["symbolic_greedy"])
                self.assertTrue(all(type(value) is bool
                                for arm in pred.values() for value in arm.values()))

    def test_budgeted_observations_leave_actual_ambiguity(self):
        result=[]
        for seed in FIXTURE_SEEDS:
            direct,same,opt,rand,fixed,conv,obs,post=fixture(seed)
            result.append(post["direct_greedy"]["count"])
            self.assertEqual(
                sum(int(x) for x in direct.weights[anonymous_context(seed)]),
                post["direct_greedy"]["count"])
        self.assertTrue(all(x>1 for x in result))

    def test_optimal_depth_planner_minimizes_expected_future_entropy(self):
        symbolic=SymbolicBayes()
        ctx="fixture-plan"
        symbolic.start(ctx)
        k=symbolic.choose_depth3(ctx)
        pool=tuple(sorted(HYPOTHESES))
        candidates=[]
        for kind in range(9):
            rest=tuple(j for j in range(9) if j!=kind)
            a=tuple(x for x in pool if x & (1<<kind))
            b=tuple(x for x in pool if not x & (1<<kind))
            cost=(len(a)/36*_expected_entropy(a,rest,2)
                 +len(b)/36*_expected_entropy(b,rest,2))
            candidates.append(cost)
        self.assertAlmostEqual(candidates[k],min(candidates),places=12)
        self.assertEqual(k,candidates.index(min(candidates)))
        symbolic.observe(ctx,k,bool(private_law(FIXTURE_SEEDS[0]) & (1<<k)))
        self.assertNotEqual(symbolic.choose_depth3(ctx),k)

    def test_cold_restore_hash_and_observation_consistency(self):
        direct=DirectWeightPosterior()
        for seed in FIXTURE_SEEDS:
            ctx=anonymous_context(seed)
            direct.start(ctx)
            for kind in (0,3,5):
                direct.program(ctx,kind,masked_feedback(seed,kind))
        snapshot=direct.snapshot()
        copy=DirectWeightPosterior.restore(snapshot)
        for seed in FIXTURE_SEEDS:
            ctx=anonymous_context(seed)
            self.assertTrue(np.array_equal(copy.weights[ctx],direct.weights[ctx]))
            f=path_features(query_scene(seed,0).after(),
                            query_scene(seed,0).source,
                            query_scene(seed,0).target)
            self.assertEqual(copy.predict(ctx,f),direct.predict(ctx,f))
        tampered=json.loads(snapshot)
        first=sorted(tampered["payload"])[0]
        tampered["payload"][first]["weights"][0]=7
        with self.assertRaises(ValueError):
            DirectWeightPosterior.restore(json.dumps(tampered))
        with self.assertRaises(ValueError):
            DirectWeightPosterior.restore(json.dumps({"schema":"fake"}))

    def test_overbudget_and_contradictory_actions_fail_closed(self):
        seed=FIXTURE_SEEDS[0]
        ctx="fixture-boundary"
        n=DirectWeightPosterior()
        n.start(ctx)
        n.program(ctx,0,masked_feedback(seed,0))
        with self.assertRaises(ValueError):
            n.program(ctx,0,not masked_feedback(seed,0))
        with self.assertRaises(ValueError):
            n.program(ctx,20,True)
        for kind in (2,5):
            n.program(ctx,kind,masked_feedback(seed,kind))
        with self.assertRaises(ValueError):
            n.choose_greedy(ctx)
        with self.assertRaises(ValueError):
            n.program(ctx,8,masked_feedback(seed,8))

    def test_no_oracle_feedback_is_injected_into_learner_module(self):
        from pathlib import Path
        source=(HERE/"learners.py").read_text(encoding="utf-8")
        for forbidden in (
            "private_law(", "masked_feedback(", "private_query_truth(",
            "oracle(", "query_scene(",
        ):
            self.assertNotIn(forbidden,source)
        self.assertFalse("WSP-101" in source)

    def test_action_effect_requires_two_hop_intervention(self):
        for seed in FIXTURE_SEEDS:
            changed_observation=0
            for index in range(64):
                scene=query_scene(seed,index)
                before=feature_bits(path_features(
                    scene.before,scene.source,scene.target))
                after=feature_bits(path_features(
                    scene.after(),scene.source,scene.target))
                self.assertEqual((before^after).bit_count(),1)
                self.assertEqual(scene.action in scene.before,not scene.add)
                self.assertEqual(scene.action in scene.after(),scene.add)
                changed_observation+=int(before!=after)
            self.assertEqual(changed_observation,64)

    def test_repeat_fixture_action_choices_and_conventional_fit(self):
        seed=FIXTURE_SEEDS[1]
        one=fixture(seed)
        two=fixture(seed)
        self.assertEqual(one[-2],two[-2])
        self.assertEqual(one[-1],two[-1])
        c1=one[-3]
        c2=two[-3]
        ctx=anonymous_context(seed)
        self.assertTrue(np.array_equal(c1.theta[ctx],c2.theta[ctx]))
        self.assertTrue(math.isfinite(c1.gradients[ctx]))


if __name__=="__main__":
    unittest.main()
