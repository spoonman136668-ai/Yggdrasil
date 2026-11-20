"""KNOW36 mock-only negative controls, no FIT/HELD source access."""
import os
import unittest
from know33_local_metaplastic_dev import digest
from know36_noisy_retention_dev import (
    ARMS, Comparator, RandomBank, cold, brier, models, private_y,
    proof, protocol, x_for,
)

class Know36Test(unittest.TestCase):
    def test_source_guard_and_prereg(self):
        prior=os.environ.pop("YGG_KNOW36_HELD_ONE_SHOT",None)
        try:
            with self.assertRaisesRegex(ValueError, "HELD_DENIED"):
                private_y(123,0,"A")
            with self.assertRaisesRegex(ValueError, "FIRST_USE_GATE"):
                proof()
            p=protocol()
            self.assertEqual(p["source"]["fit_unique_events"],3072)
            self.assertEqual(p["source"]["held_unique_events"],9216)
            s=p["source"]
            seeds=sum(s["fit_seeds"].values(),[])+sum(s["held_seeds"].values(),[])
            self.assertEqual(len(set(seeds)),36)
            self.assertFalse(p["authority"]["native_model_changed"])
        finally:
            if prior is not None: os.environ["YGG_KNOW36_HELD_ONE_SHOT"]=prior

    def test_full_mock_stream_and_cold_restore(self):
        ms=models(.03125)
        self.assertEqual(set(ms),set(ARMS))
        for t in range(256):
            x=x_for(t)
            # Fixed injected mock: NEVER calls FIT/HELD generator.
            y=int(bool(x&1) ^ bool((t//64)%2))
            for m in ms.values():
                p=m.prob(x)
                self.assertGreaterEqual(p,0.0)
                self.assertLessEqual(p,1.0)
                m.observe(t,x,y)
            if t+1 in (64,128,192,256):
                ms={name:cold(m) for name,m in ms.items()}
        for name,m in ms.items():
            with self.subTest(model=name):
                self.assertEqual(m.received,256)
                self.assertEqual(m.checkpoint(),cold(m).checkpoint())
        self.assertLess(len(ms["candidate"].checkpoint()),4096)
        self.assertLess(len(ms["hmm"].checkpoint()),4096)

    def test_invalid_event_and_score_controls(self):
        m=Comparator("hmm")
        with self.assertRaises(ValueError):
            m.observe(1,0,1)
        with self.assertRaises(ValueError):
            m.observe(0,False,1)
        with self.assertRaises(ValueError):
            m.observe(0,0,True)
        r=RandomBank()
        with self.assertRaises(ValueError):
            r.observe(0,0,2)
        self.assertAlmostEqual(brier(.5,.85),.25)
        self.assertAlmostEqual(brier(.85,.85),.1275)
        self.assertTrue(all([x_for(t) for t in range(16)].count(x)==2
                            for x in range(8)))

if __name__=="__main__":
    unittest.main()
