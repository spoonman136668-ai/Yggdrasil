"""KNOW37 mock-only, no FIT/HELD or original-world access."""
import json
import os
import unittest
from know33_local_metaplastic_dev import canonical,digest
from know36_noisy_retention_dev import fit_hazard,x_for
from know37_local_hysteresis_dev import (
    Mem,cold,models,private_y,proof,protocol,held_world,ARMS,
)

class Know37Unit(unittest.TestCase):
    def test_prereg_denial(self):
        old=os.environ.pop("YGG_KNOW37_HELD_ONE_SHOT",None)
        try:
            with self.assertRaisesRegex(ValueError,"HELD_DENIED"):
                private_y(25013,0,"A")
            with self.assertRaisesRegex(ValueError,"FIRST_USE_DENIED"):
                proof()
            p=protocol()
            self.assertEqual(p["source"]["held_unique_events"],9216)
            self.assertFalse(p["authority"]["native_training"])
        finally:
            if old is not None:
                os.environ["YGG_KNOW37_HELD_ONE_SHOT"]=old

    def test_full_mock_stream_cold(self):
        ms=models(.03125)
        self.assertEqual(set(ms),set(ARMS))
        for t in range(256):
            x=x_for(t)
            y=(x+(t//64))%2
            for m in ms.values():
                self.assertTrue(0<=m.prob(x)<=1)
                m.observe(t,x,y)
            if t+1 in (64,128,192,256):
                ms={k:cold(m) for k,m in ms.items()}
        self.assertTrue(all(m.received==256 for m in ms.values()))
        self.assertLess(len(ms["candidate"].checkpoint()),4096)

    def test_mock_full_evaluator_path_no_source(self):
        p=protocol()
        calls=[]
        def fake(seed,t,law):
            calls.append((seed,t,law))
            return int((seed+3*t+len(law))%11<5)
        h,cost=fit_hazard(
            {"source":{"fit_seeds":p["source"]["fit"]}},witness=fake)
        self.assertEqual(len(calls),3072)
        self.assertIn(h,(.0078125,.03125,.125))
        self.assertEqual(len(cost),3)
        calls.clear()
        w=held_world(99731,"B1",h,witness=fake)
        self.assertEqual(len(calls),384)
        self.assertEqual(w["model_events_per_arm"],448)
        self.assertEqual(set(w["scores"]),{"B_first","A_return","B_second"})

    def test_bad_events_tamper_duplicate_and_cold(self):
        m=Mem()
        for args in ((1,0,1),(0,False,1),(0,0,True),(0,8,1)):
            with self.assertRaises(ValueError):
                m.observe(*args)
        m.observe(0,0,1)
        raw=m.checkpoint()
        with self.assertRaises(ValueError):
            Mem.restore(raw,"0"*64)
        rawdup=raw.replace(b'"kind":',b'"kind":"fake","kind":',1)
        with self.assertRaises(ValueError):
            Mem.restore(rawdup,digest(rawdup))
        d=json.loads(raw)
        d["seen"][0][0]=6
        forged=canonical(d)
        with self.assertRaises(ValueError):
            Mem.restore(forged,digest(forged))
        self.assertEqual(cold(m).checkpoint(),raw)

if __name__=="__main__":
    unittest.main()
