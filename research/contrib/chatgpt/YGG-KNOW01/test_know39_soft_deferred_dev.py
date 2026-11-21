"""KNOW39 mock-only controls; all FIT/HELD source access denied."""
import json,os,unittest
from know33_local_metaplastic_dev import canonical,digest
from know36_noisy_retention_dev import fit_hazard,x_for
from know39_soft_deferred_dev import (
    SoftDeferred,cold,models,protocol,private_y,proof,held_world,ARMS
)
class Know39Safety(unittest.TestCase):
    def test_source_gate_and_prereg_frozen(self):
        saved=os.environ.pop("YGG_KNOW39_HELD_ONE_SHOT",None)
        try:
            with self.assertRaisesRegex(ValueError,"SOURCE_DENIED"):
                private_y(29303,0,"A")
            with self.assertRaisesRegex(ValueError,"FIRST_USE_DENIED"):
                proof()
            p=protocol()
            s=p["source"]
            self.assertEqual(s["fit_unique_events"],3072)
            self.assertEqual(s["held_unique_events"],9216)
            self.assertEqual(len(set(sum(s["fit"].values(),[])+sum(s["held"].values(),[]))),36)
            self.assertFalse(p["authority"]["native_weights_changed"])
        finally:
            if saved is not None:
                os.environ["YGG_KNOW39_HELD_ONE_SHOT"]=saved

    def test_soft_forecast_and_no_prewrite(self):
        m=SoftDeferred("soft",.03125)
        h=SoftDeferred("hard_readout",.03125)
        for t in range(7):
            # All predictive belief changes remain epistemic only.
            m.observe(t,t,0)
            h.observe(t,t,0)
        self.assertEqual(sum(map(sum,m.seen)),0)
        self.assertEqual(len(m.pending),7)
        self.assertEqual(len(h.pending),7)
        self.assertTrue(0<=m.prob(2)<=1)
        self.assertEqual(cold(m).checkpoint(),m.checkpoint())
        m.observe(7,7,1)
        self.assertEqual(sum(map(sum,m.seen)),8)
        self.assertEqual(len(m.pending),0)

    def test_full_mock_stream_cold_and_no_held(self):
        ms=models(.03125)
        self.assertEqual(set(ms),set(ARMS))
        for t in range(256):
            x=x_for(t)
            y=int(bool(x&1)!=bool((t//64)%2))
            for m in ms.values():
                self.assertTrue(0<=m.prob(x)<=1)
                m.observe(t,x,y)
            if t+1 in (64,128,192,256):
                ms={k:cold(m) for k,m in ms.items()}
        self.assertTrue(all(m.received==256 for m in ms.values()))
        p=protocol()
        calls=[]
        def dummy(seed,t,law):
            calls.append((seed,t,law))
            return int((seed+3*t+len(law))%11<5)
        h,cost=fit_hazard({"source":{"fit_seeds":p["source"]["fit"]}},
                          witness=dummy)
        self.assertEqual(len(calls),3072)
        self.assertEqual(len(cost),3)
        calls.clear()
        w=held_world(99939,"B1",h,witness=dummy)
        self.assertEqual(len(calls),384)
        self.assertEqual(w["source_calls"],384)
        self.assertEqual(w["arm_events"],448)
        self.assertEqual(set(w["elapsed_ns"]),set(ARMS))
        self.assertEqual(set(w["scores"]),{"B_first","A_return","B_second"})

    def test_reject_bad_cold_or_forged_witness(self):
        m=SoftDeferred("soft",.03125)
        for args in ((1,0,1),(0,True,1),(0,0,True),(0,8,1)):
            with self.assertRaises(ValueError):m.observe(*args)
        m.observe(0,0,1)
        raw=m.checkpoint()
        with self.assertRaises(ValueError):
            SoftDeferred.restore(raw,"0"*64)
        dup=raw.replace(b'"kind":',b'"kind":"bad","kind":',1)
        with self.assertRaises(ValueError):
            SoftDeferred.restore(dup,digest(dup))
        d=json.loads(raw);d["seen"][0][0]=6
        forged=canonical(d)
        with self.assertRaises(ValueError):
            SoftDeferred.restore(forged,digest(forged))
        self.assertEqual(cold(m).checkpoint(),raw)
if __name__=="__main__":
    unittest.main()
