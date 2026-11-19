"""CKAD47 disjoint engineering fixtures, no DEV/held scientific seed scored."""
import importlib.util
import math
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location("ckad47_engineering_fixture",HERE/"campaign.py")
D=importlib.util.module_from_spec(sp)
sp.loader.exec_module(D)


class CKAD47FixtureTests(unittest.TestCase):
    def test_pre_source_contract_and_first_use_fence(self):
        self.assertEqual(D.PREREG,"b0d71e48848a92d10ed78019d40dffb7af0f505c")
        self.assertEqual(D.DEV,(47111,47112))
        self.assertEqual((D.OLD,D.NEW_END,D.TOTAL),(96,192,240))
        self.assertEqual(D.PROBES,(96,112,128,144,160,176,192,208,224))
        self.assertEqual(len(D.MAPS),24)
        self.assertTrue(set(D.DEV).isdisjoint(D.PILOT+D.PRIMARY))
        for seed in (*D.PILOT,*D.PRIMARY,46111,0):
            with self.assertRaisesRegex(ValueError,"CKAD47_ONLY_REGISTERED_DEV"):
                D.evaluate(seed)
        with self.assertRaisesRegex(ValueError,"CKAD47_ONLY_REGISTERED_DEV"):
            D.world_events(D.PRIMARY[0],0)

    def test_genuine_four_distinct_effects_and_disjoint_source(self):
        events,private=D.world_events(0,0)
        self.assertEqual(len(events),240)
        self.assertEqual(sorted(private["mapping_evaluator_only"]),[0,1,2,3])
        self.assertEqual(len({id for id,_ in events}),240)
        self.assertTrue(all(row["a1"] in (0,1) and row["a2"] in (0,1)
                         for _,row in events[:96]))
        self.assertTrue(all(row["a1"] in (2,3) and row["a2"] in (2,3)
                         for _,row in events[96:192]))
        self.assertTrue(all(row["a1"] in (0,1) and row["a2"] in (0,1)
                         for _,row in events[192:]))
        self.assertTrue(all(set(row)=={"s0","a1","s1","a2","s2","y"}
                            for _,row in events))
        self.assertEqual(D.world_events(0,0),D.world_events(0,0))
        self.assertNotEqual(D.world_events(0,0),D.world_events(0,1))

    def test_all_three_models_real_source_training_exact_checkpoint(self):
        events,_=D.world_events(0,0)
        for mode in D.ARMS[:3]:
            m=D.QuadCausalLearner(mode)
            for t,event in enumerate(events):
                if t in (95,96,128,191,192):
                    read_before=m.checkpoint()
                    self.assertTrue(0<m.predict_reward(3,2,3)<1)
                    self.assertAlmostEqual(sum(m.predict_next(2,3)),1,delta=1e-12)
                    self.assertEqual(read_before,m.checkpoint())
                m.observe(*event)
                if t==95:old=m.ledger[:96].copy()
            self.assertEqual(m.n,240)
            self.assertEqual(m.ledger[:96],old)
            self.assertEqual(sum(sum(c) for c in m.reward),240)
            if mode=="native_fourway_effect":
                self.assertEqual(sum(sum(c) for c in m.effects),480)
                self.assertGreater(sum(m.effects[2]),0)
                self.assertGreater(sum(m.effects[3]),0)
            elif mode=="fully_fitted_tabular":
                self.assertEqual(sum(sum(sum(c) for c in row)
                                     for row in m.tabular),480)
            else:
                self.assertAlmostEqual(sum(m.weights),1,delta=1e-12)
                self.assertGreater(max(m.weights),1/24)
            raw=m.checkpoint()
            cold=D.QuadCausalLearner.restore(raw,D._sha(raw))
            self.assertEqual(raw,cold.checkpoint())
            self.assertEqual(m.predict_reward(3,2,3),cold.predict_reward(3,2,3))
            proof=m.custody(events[-1])
            self.assertTrue(proof["first96_unchanged"] and proof["conflict_atomic"])
            self.assertEqual(m.checkpoint(),raw)

    def test_composition_uses_learned_action_effects_not_binary_alias(self):
        m=D.QuadCausalLearner("native_fourway_effect")
        m.effects[0]=[96,0,0,0]
        m.effects[1]=[0,96,0,0]
        m.effects[2]=[0,0,96,0]
        m.effects[3]=[0,0,0,96]
        m.reward=[[96,0],[0,96],[0,96],[96,0]]
        self.assertGreater(m.predict_reward(0,1,2),.9)
        self.assertLess(m.predict_reward(0,1,1),.15)
        self.assertGreater(m.predict_next(0,3)[3],.9)
        self.assertLess(m.predict_next(0,3)[1],.05)

    def test_exact_posterior_composes_joint_mapping_not_marginal_product(self):
        m=D.QuadCausalLearner("exact_bijective_bayes")
        m.reward=[[90,0],[0,90],[0,90],[90,0]]
        probs=m.predict_reward(0,2,2)
        joint=0.
        for weight,perm in zip(m.weights,D.MAPS):
            for s1,p1 in enumerate(D._transition_distribution(0,perm[2])):
                for s2,p2 in enumerate(D._transition_distribution(s1,perm[2])):
                    failures,successes=m.reward[s2]
                    joint+=weight*p1*p2*(successes+1)/(failures+successes+2)
        self.assertAlmostEqual(probs,joint,delta=1e-14)
        self.assertTrue(0<probs<1)
        self.assertEqual(m.checkpoint(),D.QuadCausalLearner.restore(
            m.checkpoint(),D._sha(m.checkpoint())).checkpoint())

    def test_nonxor_negative_falsifies_state_invariance(self):
        # A genuine state-dependent effect is OUTSIDE the proposed XOR
        # grammar; fully fitted tabular must outperform source-transport.
        structured=D.QuadCausalLearner("native_fourway_effect")
        tabular=D.QuadCausalLearner("fully_fitted_tabular")
        for t in range(128):
            s=t%4
            s1=s if s<2 else s^1
            row={"s0":s,"a1":0,"s1":s1,
                 "a2":1,"s2":s1,"y":s1&1}
            ident=D._sha(f"ckad47-nonxor-negative-only|{t}")
            structured.observe(ident,row)
            tabular.observe(ident,row)
        got=structured.predict_next(0,0)[0]
        control=tabular.predict_next(0,0)[0]
        self.assertGreater(control,got+.30)
        self.assertEqual(structured.n,tabular.n)
        self.assertFalse(got>.9)

    def test_actual_outcome_source_atomicity_and_nonfuture_probe(self):
        data,_=D.world_events(0,1)
        m=D.QuadCausalLearner("native_fourway_effect")
        for event in data[:101]:m.observe(*event)
        before=m.checkpoint()
        self.assertEqual(m.observe(*data[100]).checkpoint(),before)
        corrupt=dict(data[100][1],y=1-data[100][1]["y"])
        with self.assertRaisesRegex(ValueError,"CKAD47_CONFLICTING_SOURCE_ID"):
            m.observe(data[100][0],corrupt)
        self.assertEqual(m.checkpoint(),before)
        with self.assertRaisesRegex(ValueError,"CKAD47_CHECKPOINT_SHA"):
            D.QuadCausalLearner.restore(before,"0"*64)
        with self.assertRaisesRegex(ValueError,"CKAD47_QUAD"):
            m.predict_reward(4,0,1)

    def test_predeclared_scientific_classifier_and_strong_controls(self):
        def fake(seed,c=.135,exact=.132,tab=.15,early=.14,cold=.14):
            groups={}
            for label in D.PHASES:
                x={"native_fourway_effect":c,
                   "exact_bijective_bayes":exact,
                   "fully_fitted_tabular":tab,
                   "uniform_negative":.25}
                if label=="novel_early":x["native_fourway_effect"]=early
                if label=="cold_return":x["native_fourway_effect"]=cold
                groups[label]={"expected_brier":x}
            receipts=[{"cold_exact":True,"first96_unchanged":True,
                       "conflict_atomic":True,"duplicate_idempotent":True,
                       "same_original_first96_as_at_source_time":True}
                       for _ in range(6)]
            return {"seed":seed,"groups":groups,"model_receipts":receipts}
        a,b=[fake(seed) for seed in D.DEV]
        self.assertEqual(D.classify([a,b]),"DEV_FEASIBLE_NOT_SCIENTIFIC")
        self.assertEqual(D.classify([a,fake(D.DEV[1],c=.145)]),"DEV_NO_GO")
        self.assertEqual(D.classify([a,fake(D.DEV[1],tab=.142)]),"DEV_NO_GO")
        self.assertEqual(D.classify([a,fake(D.DEV[1],early=.152)]),"DEV_NO_GO")
        self.assertEqual(D.classify([a,fake(D.DEV[1],cold=.145)]),"DEV_NO_GO")
        with self.assertRaises(AssertionError):D.classify([b,a])


if __name__=="__main__":
    unittest.main()
