"""KNOW40 tests inject mock observations ONLY; never open fresh graph FIT/HELD."""
import os,unittest
from know40_structural_action_dev import (
 ARMS,HAZARDS,Symbolic,Lookup,structural_bit,q_for,action_regret,
 x_for,models,cold,protocol,private_y,proof,fit_hazards,held_world
)
class Know40MockOnly(unittest.TestCase):
    def test_prereg_source_denial_and_disjoint_graphs(self):
        prev=os.environ.pop("YGG_KNOW40_HELD_ONE_SHOT",None)
        try:
            with self.assertRaisesRegex(ValueError,"SOURCE_DENIED"):
                private_y(32003,0,"H1")
            with self.assertRaisesRegex(ValueError,"FIRST_USE_DENIED"):
                proof()
            p=protocol()
            all_seeds=sum(p["source"]["fit"].values(),[])+sum(p["source"]["held"].values(),[])
            self.assertEqual(len(set(all_seeds)),36)
            self.assertFalse(p["authority"]["native_training"])
            self.assertEqual(p["source"]["held_unique_source_calls"],9216)
            for graph in ("H1","H2"):
                self.assertEqual(sum(q_for(graph,c)!=q_for(graph,c^2)
                                     for c in range(8)),4)
                self.assertNotIn(graph,p["scm"]["fit_templates"])
        finally:
            if prev is not None:os.environ["YGG_KNOW40_HELD_ONE_SHOT"]=prev

    def test_forced_actions_and_causal_contrast(self):
        for b in range(0,256,16):
            pairs={(t%8,(t//8)%2) for t in range(b,b+16)}
            self.assertEqual(len(pairs),16)
        for g in ("F1","F2","H1","H2"):
            self.assertEqual(len([structural_bit(g,x) for x in range(8)]),8)
        m=Lookup()
        self.assertIn(action_regret(m,10,"H1"),(0,.7))
        self.assertEqual(m.received,0)

    def test_full_injected_fitter_and_held_sham(self):
        calls=[]
        def injected(seed,t,law):
            calls.append((seed,t,law))
            return int((seed+7*t+len(law))%13<6)
        p=protocol()
        h,scores,n=fit_hazards(p,witness=injected)
        self.assertEqual(n,3072)
        self.assertEqual(len(calls),3072)
        self.assertEqual(set(h),{"hmm","symbolic"})
        self.assertTrue(all(v in HAZARDS for v in h.values()))
        calls.clear()
        world=held_world(99940,"B1",h,witness=injected)
        self.assertEqual(len(calls),384)
        self.assertEqual(world["source_calls"],384)
        self.assertEqual(world["model_events_per_arm"],448)
        self.assertEqual(set(world["scores"]),{"B_first","A_return","B_second"})
        self.assertEqual(set(world["bytes"]),set(ARMS))
        self.assertEqual(set(world["random_policy_regret"]),{"B_first","A_return","B_second"})
        self.assertTrue(all(0<=v<=.7 for v in world["random_policy_regret"].values()))
        self.assertTrue(all(v==0 for v in world["oracle_policy_regret"].values()))
        self.assertLess(world["bytes"]["candidate"],4096)

    def test_full_stream_cold_and_strict_types(self):
        ms=models(.03125,.03125)
        self.assertEqual(set(ms),set(ARMS))
        for t in range(256):
            x=x_for(t)
            y=(x+t//64)%2
            for m in ms.values():
                self.assertTrue(0<=m.prob(x)<=1)
                m.observe(t,x,y)
            if t+1 in (64,128,192,256):
                ms={name:cold(m) for name,m in ms.items()}
        self.assertTrue(all(m.received==256 for m in ms.values()))
        m=Symbolic(.03125)
        with self.assertRaisesRegex(ValueError,"SYMBOLIC_EVENT"):
            m.observe(0,0,True)
        with self.assertRaisesRegex(ValueError,"SYMBOLIC_EVENT"):
            m.observe(1,0,1)
        self.assertEqual(cold(m).checkpoint(),m.checkpoint())
if __name__=="__main__":
    unittest.main()
