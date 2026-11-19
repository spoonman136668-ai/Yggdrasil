"""CKAD45 fixed engineering fixtures: NEVER score a registered DEV or held seed."""
from __future__ import annotations
import hashlib
import importlib.util
import json
import math
import sys
import unittest
from pathlib import Path
from yggdrasil.native_context_basis import canonical,digest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("ckad45_fixture_unit",HERE/"campaign.py")
D=importlib.util.module_from_spec(spec)
spec.loader.exec_module(D)


def source_fixture(t,policy):
    """Unregistered source identities/outcomes unrelated to CKAD45 DEV worlds."""
    c=(t//3)&1
    views=((c,(t//5)&1),(c,(t//7)&1))
    x1=policy.choose_first(views[0],t)
    s2=c^x1^int(80<=t<140)
    x2=policy.choose_second(views[0],t,x1,s2)
    y=(c&x1)^(s2&x2)
    row={"s1":c,"x1":x1,"s2":s2,"x2":x2,"y":y}
    ident=hashlib.sha256(f"ckad45-disjoint-unit|{policy.policy}|{t}".encode()).hexdigest()
    return ident,views,row


class CKAD45Tests(unittest.TestCase):
    def test_protocol_seed_gate_and_boundaries(self):
        self.assertEqual(D.PREREG,"ab6f435adcbb09116efde103c4be5614db6f1d0c")
        self.assertEqual(D.DEV,(45111,45112))
        self.assertEqual((D.N,D.FIRST_CHANGE,D.RETURN,D.WARM),(232,92,164,48))
        self.assertEqual(D.PROBE_STEP,8)
        self.assertEqual(len(D.POLICIES),6)
        self.assertTrue(set(D.DEV).isdisjoint(D.PILOT+D.PRIMARY+D.EXCLUDED))
        for seed in (*D.PILOT,*D.PRIMARY,*D.EXCLUDED):
            with self.assertRaisesRegex(ValueError,"CKAD45_ONLY_REGISTERED_DEV"):
                D.score_seed(seed)
        self.assertEqual(D.private_phase(91),"stable_A")
        self.assertEqual(D.private_phase(92),"early_B")
        self.assertEqual(D.private_phase(164),"early_return_A")
        self.assertEqual(D.private_phase(188),"late_return_A")

    def test_private_true_family_and_common_exogenous_receipts(self):
        a=D.exogenous(999,0)
        self.assertEqual(len(a),D.N)
        self.assertEqual(a,D.exogenous(999,0))
        self.assertNotEqual(a,D.exogenous(999,1))
        for world in (0,1):
            probabilities=[D.true_probabilities(world,t,c,x,s,b)
                 for t in (0,92,164,220) for c in (0,1)
                 for x in (0,1) for s in (0,1) for b in (0,1)]
            self.assertTrue(all(p in (.15,.85) and q in (.1,.9)
                                for p,q in probabilities))
            self.assertNotEqual(D._true_bits(world,"A",1,1,0,1),
                                D._true_bits(world,"B",1,1,0,1))
        with self.assertRaises(ValueError):
            D.exogenous(D.PRIMARY[0],0)

    def test_causal_rule_IG_matches_exact_entropy_decomposition(self):
        m=D.PolicyLearner("exact_info_gain",999,0)
        e=.5*D.binary_entropy(.85)+.5*D.binary_entropy(.15)
        for context in (0,1):
            view=(context,0)
            for first in (0,1):
                p=m.causal.read("short",view,first)
                self.assertAlmostEqual(
                    m._score(view,first),
                    D.binary_entropy(p),delta=1e-15)
                self.assertGreaterEqual(m._score(view,first)-e,0)
        with self.assertRaises(ValueError):
            D.binary_entropy(float("nan"))

    def test_each_policy_trains_exactly_one_event_and_two_actions(self):
        for policy in D.POLICIES:
            agent=D.PolicyLearner(policy,999,0)
            for t in range(D.N):
                if t==D.WARM:agent.begin_stream()
                ident,views,row=source_fixture(t,agent)
                before=agent.causal.checkpoint()
                p=agent.predict_stage1(views[0],row["x1"])
                q=agent.predict_stage2(views[0],row["x1"],row["s2"],row["x2"])
                self.assertEqual(before,agent.causal.checkpoint())
                agent.observe(ident,views,row,(p,q))
            self.assertEqual(agent.n,D.N)
            self.assertEqual(agent.causal.n,D.N)
            self.assertEqual(len(agent.actual_actions),D.N)
            self.assertEqual(len(agent.cover_transition.values())>=1,True)
            receipt=agent.check_cold_and_source((ident,views,row))
            self.assertEqual(receipt["chosen_actions"],2*D.N)
            self.assertTrue(receipt["source_unique"])
            self.assertTrue(receipt["prefix48_exact"])
            self.assertTrue(receipt["cold_exact"])
            if policy=="fixed_zero_negative":
                self.assertTrue(all(x==(0,0) for x in agent.actual_actions))

    def test_probe_nontraining_on_common_unseen_action_grid(self):
        agent=D.PolicyLearner("ipfc_contradiction",999,0)
        for t in range(56):
            if t==D.WARM:agent.begin_stream()
            ident,views,row=source_fixture(t,agent)
            agent.observe(ident,views,row,(agent.predict_stage1(views[0],row["x1"]),
                           agent.predict_stage2(views[0],row["x1"],row["s2"],row["x2"])))
        oldn=agent.native.checkpoint()
        oldc=agent.causal.checkpoint()
        before=agent.n
        vals=D.examiner(agent,0,56)
        self.assertTrue(.0<vals["causal"]<1.0)
        self.assertTrue(.0<vals["native"]<1.0)
        self.assertEqual(agent.n,before)
        self.assertEqual(agent.native.checkpoint(),oldn)
        self.assertEqual(agent.causal.checkpoint(),oldc)
        self.assertAlmostEqual((D._expected_brier(.85,.85)+
                                D._expected_brier(.90,.90))*.5,.10875,delta=1e-14)
        self.assertEqual(agent.probe_checks,1)

    def test_active_falsifier_uses_only_past_prequential_loss(self):
        m=D.PolicyLearner("ipfc_contradiction",999,0)
        baseline=D.PolicyLearner("exact_info_gain",999,0)
        view=(1,0)
        self.assertEqual(m._score(view,0),baseline._score(view,0))
        for _ in range(D.RECENT):m.loss_history.append(.22)
        m.causal.transition.full[0]=5.0
        m.causal.transition.short[0]=-5.0
        # The frozen active score adds only witnessed full-vs-short
        # disagreement; no environment probability enters m._score.
        p=m.causal.read("short",view,0)
        q=m.causal.read("full",view,0)
        expected=D.binary_entropy(p)+D.DISAGREE*(q-p)*(q-p)
        self.assertAlmostEqual(m._score(view,0),expected,delta=1e-14)
        m.loss_history.clear()
        self.assertAlmostEqual(m._score(view,0),D.binary_entropy(p),delta=1e-14)

    def test_frozen_gate_requires_best_control_and_native_transfer(self):
        def fake(seed,chosen=.110,other=.128,native=.115,diff=.2,early=.118):
            groups={}
            for phase in (*D.PHASES,"pooled_late_shift_and_return"):
                groups[phase]={"causal":{k:(chosen if k=="ipfc_contradiction" else other)
                               for k in D.POLICIES},
                               "native":{k:(native if k=="ipfc_contradiction" else .120)
                               for k in D.POLICIES}}
                if phase=="early_return_A":
                    for k in D.POLICIES:
                        groups[phase]["causal"][k]=(early if k=="ipfc_contradiction" else .115)
            return {"seed":seed,"metrics":groups,
                    "candidate_action_difference_fraction":diff,
                    "worlds":[{"source_unique":True,"prefix48_exact":True,
                      "cold_exact":True,"duplicate_idempotent":True,
                      "conflict_atomic":True}]}
        a,b=[fake(s) for s in D.DEV]
        self.assertEqual(D.classify([a,b]),"DEV_FEASIBLE_NOT_SCIENTIFIC")
        self.assertEqual(D.classify([a,fake(D.DEV[1],chosen=.125)]),"DEV_NO_GO")
        self.assertEqual(D.classify([a,fake(D.DEV[1],diff=.05)]),"DEV_NO_GO")
        self.assertEqual(D.classify([a,fake(D.DEV[1],native=.13)]),"DEV_NO_GO")
        self.assertEqual(D.classify([a,fake(D.DEV[1],early=.13)]),"DEV_NO_GO")
        with self.assertRaises(AssertionError):D.classify([b,a])


if __name__=="__main__":
    unittest.main()
