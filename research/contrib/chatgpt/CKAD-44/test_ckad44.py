"""CKAD44 fixture-only negative controls, NOT any scored DEV or held cohort."""
import hashlib
import importlib.util
import json
import math
import sys
import unittest
from pathlib import Path
from yggdrasil.native_context_basis import digest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("ckad44_fixture_only",HERE/"campaign.py")
D=importlib.util.module_from_spec(spec)
spec.loader.exec_module(D)


def fixture(i,changed=False):
    # Separate fixture identities, no CKAD39/44 seed-derived episode values.
    c=(i*3//4)&1
    x1=(i//2)&1
    x2=(i//3)&1
    s2=(c^x1^int(changed))
    y=((c&x1)^(s2&x2)) if not changed else ((c&s2)|(x1&x2))
    ident=hashlib.sha256(("ckad44-fixture-only|"+str(i)).encode()).hexdigest()
    return ident,((c,(i//5)&1),(c,(i//7)&1)),{
       "s1":c,"x1":x1,"s2":s2,"x2":x2,"y":y}


class CKAD44FixtureTests(unittest.TestCase):
    def test_frozen_prereg_seeds_and_hypothesis(self):
        self.assertEqual(D.PREREG,"0c613f55a2e5d68d5bbc9ce21a5b8fbc8a84e0a7")
        self.assertEqual(D.DEV,(44111,44112))
        self.assertTrue(set(D.DEV).isdisjoint(D.PILOT+D.PRIMARY+D.EXCLUDED))
        for seed in (*D.PILOT,*D.PRIMARY,*D.EXCLUDED):
            with self.assertRaisesRegex(ValueError,"CKAD44_ONLY_REGISTERED_DEV"):
                D.run(seed)
        self.assertEqual((D.REFERENCE_EVENTS,D.EVIDENCE_WINDOW,D.RUN_CAP),(64,12,48))
        self.assertEqual(D.HAZARD,1/72)

    def test_genuine_training_frozen64_and_source_cold(self):
        m=D.ContrastiveCausalMemory()
        seen=[]
        for t in range(132):
            event=fixture(t,changed=t>=78 and t<110)
            before=m.checkpoint()
            p=m.read("contrastive_recall",event[1][0],event[2]["x1"])
            q=m.read("contrastive_recall",event[1][0],event[2]["x1"],
                    event[2]["s2"],event[2]["x2"])
            self.assertTrue(0<p<1 and 0<q<1)
            self.assertEqual(before,m.checkpoint())
            m.observe(*event)
            if t==63:
                original=m.reference.checkpoint()
            if t>63:
                self.assertEqual(m.reference.checkpoint(),original)
            seen.append(event)
        self.assertEqual(m.n,len(seen))
        self.assertEqual(m.adaptive.n,132)
        self.assertEqual(m.reference.n,64)
        self.assertEqual(len(m.history),12)
        raw=m.checkpoint()
        cold=D.ContrastiveCausalMemory.restore(raw,digest(raw))
        self.assertEqual(cold.checkpoint(),raw)
        self.assertEqual(cold._weight(),m._weight())
        for name in ("contrastive_recall","uniform_recall","frozen_reference",
                     "causal_discount93","causal_full","causal_dual"):
            self.assertEqual(m.read(name,(1,0),1,0,1),
                             cold.read(name,(1,0),1,0,1))
        self.assertIs(m.observe(*seen[-1]),m)
        self.assertEqual(m.checkpoint(),raw)
        corrupted=dict(seen[-1][2])
        corrupted["y"]^=1
        with self.assertRaisesRegex(ValueError,"CKAD44_CONFLICTING_SOURCE_ID"):
            m.observe(seen[-1][0],seen[-1][1],corrupted)
        self.assertEqual(m.checkpoint(),raw)

    def test_terminal_conditioning_is_not_reward_oracle(self):
        m=D.ContrastiveCausalMemory()
        for i in range(83):
            m.observe(*fixture(i,changed=68<=i<78))
        view=(1,0)
        before=m.checkpoint()
        a=m.read("contrastive_recall",view,1)
        b=m.read("contrastive_recall",view,1,1,0)
        c=m.read("contrastive_recall",view,1,0,0)
        self.assertTrue(all(0<v<1 for v in (a,b,c)))
        self.assertEqual(before,m.checkpoint())
        with self.assertRaises(ValueError):
            m.read("unregistered",view,1)
        # The terminal read may depend on already witnessed next_state, but
        # neither read sees or updates the terminal reward from THIS event.

    def test_source_beta_changepoint_cold_and_bounds(self):
        m=D.BayesianChangePoint()
        last=None
        for i in range(120):
            event=fixture(i,changed=45<=i<90)
            raw=m.checkpoint()
            p=m.predict(event[1][0],event[2]["x1"])
            q=m.predict(event[1][0],event[2]["x1"],event[2]["s2"],event[2]["x2"])
            self.assertTrue(0<p<1 and 0<q<1)
            self.assertEqual(raw,m.checkpoint())
            m.observe(*event)
            last=event
            self.assertLessEqual(len(m.states),D.RUN_CAP+1)
            self.assertAlmostEqual(sum(s["w"] for s in m.states),1,delta=1e-12)
        raw=m.checkpoint()
        cold=D.BayesianChangePoint.restore(raw,digest(raw))
        self.assertEqual(raw,cold.checkpoint())
        self.assertEqual(m.predict((1,0),1),cold.predict((1,0),1))
        self.assertIs(m.observe(*last),m)
        other=dict(last[2]);other["y"]^=1
        with self.assertRaisesRegex(ValueError,"CKAD44_BETA_CONFLICTING_SOURCE_ID"):
            m.observe(last[0],last[1],other)
        self.assertEqual(raw,m.checkpoint())

    def test_action_symbol_bijection_baseline_not_unfamiliar_transfer(self):
        # A source-consistent relabel of binary action identities must leave
        # the fully fitted generic Beta BOCPD *control* predictions invariant.
        # This does NOT demonstrate genuinely unfamiliar actions/worlds.
        original=D.BayesianChangePoint()
        relabeled=D.BayesianChangePoint()
        for t in range(60):
            identifier,views,row=fixture(t,changed=24<=t<45)
            new=dict(row)
            new["x1"]=1-new["x1"]
            new["x2"]=1-new["x2"]
            original.observe(identifier,views,row)
            relabeled.observe(identifier,views,new)
        for context in (0,1):
            for first in (0,1):
                v=(context,0)
                self.assertAlmostEqual(original.predict(v,first),
                    relabeled.predict(v,1-first),delta=1e-15)
                for second in (0,1):
                    for next_state in (0,1):
                        self.assertAlmostEqual(
                          original.predict(v,first,next_state,second),
                          relabeled.predict(v,1-first,next_state,1-second),
                          delta=1e-15)

    def test_nondiverse_evidence_cannot_force_reference(self):
        m=D.ContrastiveCausalMemory()
        for t in range(64):
            m.observe(*fixture(t))
        m.history.clear()
        for t in range(D.EVIDENCE_WINDOW):
            m.history.append({"lr":100.0,"x1":0,"x2":0})
        self.assertEqual(m._weight(),0.0)
        m.history.clear()
        for t in range(D.EVIDENCE_WINDOW):
            m.history.append({"lr":.5,"x1":t%2,"x2":(t//2)%2})
        self.assertGreater(m._weight(),.9)
        m.history.clear()
        self.assertEqual(m._weight(),0.0)

    def test_frozen_gate_compares_strongest_fully_fitted_control(self):
        def case(seed,candidate=.1,native=.13,strong=.12,masked=.16,late=.105):
            metrics={}
            for phase in (*D.PHASES,"pooled_late_shift_and_return"):
                v={a:.22 for a in D.ARMS}
                v["contrastive_recall"]=candidate
                v["native_stream"]=native
                v["causal_action_masked"]=masked
                for a in (*D.CONVENTIONAL,"beta_bocpd","uniform_recall",
                          "frozen_reference","causal_full","causal_discount93",
                          "causal_dual"):v[a]=strong
                if phase=="late_return_A":
                    v["contrastive_recall"]=late
                metrics[phase]={"brier":v}
            return {"seed":seed,"metrics":metrics,"worlds":[{
                "source_complete":True,"source_original48_exact":True,
                "frozen64_exact":True,"cold_exact":True,"read_only":True,
                "duplicate_idempotent":True,"conflict_atomic":True}]}
        a,b=[case(s) for s in D.DEV]
        self.assertEqual(D.classify([a,b]),"DEV_FEASIBLE_NOT_SCIENTIFIC")
        self.assertEqual(D.classify([a,case(D.DEV[1],strong=.109)]),"DEV_NO_GO")
        self.assertEqual(D.classify([a,case(D.DEV[1],candidate=.15)]),"DEV_NO_GO")
        self.assertEqual(D.classify([a,case(D.DEV[1],late=.125)]),"DEV_NO_GO")
        with self.assertRaises(AssertionError):D.classify([b,a])


if __name__=="__main__":
    unittest.main()
