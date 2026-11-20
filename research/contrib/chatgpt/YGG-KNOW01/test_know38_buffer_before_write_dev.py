"""KNOW38 mock-only tests; no new FIT, HELD or original-world access."""
import json
import os
import unittest
from know33_local_metaplastic_dev import canonical,digest
from know36_noisy_retention_dev import fit_hazard,x_for
from know38_buffer_before_write_dev import (
    ARMS,BufferBank,cold,models,held_world,private_y,proof,protocol,
)

class Know38Tests(unittest.TestCase):
    def test_frozen_protocol_and_unopened_source(self):
        old=os.environ.pop("YGG_KNOW38_HELD_ONE_SHOT",None)
        try:
            with self.assertRaisesRegex(ValueError,"SOURCE_DENIED"):
                private_y(27307,0,"A")
            with self.assertRaisesRegex(ValueError,"FIRST_USE_DENIED"):
                proof()
            p=protocol()
            self.assertEqual(p["source"]["fit_source_events"],3072)
            self.assertEqual(p["source"]["held_unique_source_events"],9216)
            all_seeds=sum(p["source"]["fit"].values(),[])+sum(p["source"]["held"].values(),[])
            self.assertEqual(len(set(all_seeds)),36)
            self.assertFalse(p["scope"]["protected_new_original_world_first_use"])
        finally:
            if old is not None:
                os.environ["YGG_KNOW38_HELD_ONE_SHOT"]=old

    def test_no_long_term_writes_before_eighth_group_witness(self):
        m=BufferBank()
        for t in range(7):
            m.observe(t,t%2,t%2)
        self.assertEqual(sum(map(sum,m.seen)),0)
        self.assertEqual(len(m.pending[0]),7)
        self.assertEqual(cold(m).checkpoint(),m.checkpoint())
        m.observe(7,1,1)
        self.assertEqual(sum(map(sum,m.seen)),8)
        self.assertEqual(len(m.pending[0]),0)
        self.assertLess(len(m.checkpoint()),4096)

    def test_all_models_cold_at_boundaries_and_injected_evaluator(self):
        ms=models(.03125)
        self.assertEqual(set(ms),set(ARMS))
        for t in range(256):
            x=x_for(t)
            y=int(bool(x&1)^bool((t//64)%2))
            for m in ms.values():
                self.assertTrue(0<=m.prob(x)<=1)
                m.observe(t,x,y)
            if t+1 in (64,128,192,256):
                ms={name:cold(m) for name,m in ms.items()}
        self.assertTrue(all(m.received==256 for m in ms.values()))
        p=protocol()
        calls=[]
        def mock(seed,t,law):
            calls.append((seed,t,law))
            return int((seed+5*t+len(law))%13<6)
        h,cost=fit_hazard({"source":{"fit_seeds":p["source"]["fit"]}},witness=mock)
        self.assertEqual(len(calls),3072)
        self.assertEqual(len(cost),3)
        calls.clear()
        w=held_world(99381,"B1",h,witness=mock)
        self.assertEqual(len(calls),384)
        self.assertEqual(w["source_calls"],384)
        self.assertEqual(w["model_events_per_arm"],448)
        self.assertEqual(set(w["scores"]),{"B_first","A_return","B_second"})
        self.assertEqual(set(w["cost_ns"]),set(ARMS))

    def test_bad_inputs_and_cold_rejection(self):
        m=BufferBank()
        for event in ((1,0,1),(0,True,1),(0,0,True),(0,8,1)):
            with self.assertRaises(ValueError):
                m.observe(*event)
        m.observe(0,0,1)
        raw=m.checkpoint()
        with self.assertRaises(ValueError):
            BufferBank.restore(raw,"0"*64)
        dup=raw.replace(b'"kind":',b'"kind":"fake","kind":',1)
        with self.assertRaises(ValueError):
            BufferBank.restore(dup,digest(dup))
        d=json.loads(raw)
        d["seen"][0][0]=6
        forged=canonical(d)
        with self.assertRaises(ValueError):
            BufferBank.restore(forged,digest(forged))
        self.assertEqual(cold(m).checkpoint(),raw)

if __name__=="__main__":
    unittest.main()
