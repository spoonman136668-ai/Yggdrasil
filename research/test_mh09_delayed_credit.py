"""Literal mechanical fixtures only. Not scientific trial data."""
import json
import unittest
from research.mh09_delayed_credit import DelayedCredit,Rule,fit_engineering_packets,canonical

class MH09Tests(unittest.TestCase):
    def test_delayed_id_and_out_of_order_feedback(self):
        m=DelayedCredit()
        m.begin(0,(1,0,0,0)); m.begin(1,(0,1,0,0))
        m.feedback(1,(1,0,0))
        self.assertEqual(m.w[0][0],0.)
        self.assertGreater(m.w[0][1],0.)
        m.feedback(0,(-1,0,0))
        self.assertLess(m.w[0][0],0.)
        self.assertGreater(m.w[0][1],0.)
        with self.assertRaises(ValueError): m.feedback(0,(1,0,0))

    def test_cold_restore_with_pending_feedback(self):
        m=DelayedCredit(Rule((1,0,0,0,0,0,1)))
        m.begin(0,(1,0,0,0)); m.begin(1,(0,1,0,0))
        n=DelayedCredit.restore(m.checkpoint())
        self.assertEqual(m.checkpoint(),n.checkpoint())
        for x in (m,n):
            x.feedback(1,(1,0,0)); x.feedback(0,(-1,0,0))
        self.assertEqual(m.checkpoint(),n.checkpoint())

    def test_expiry_and_capacity_fail_closed(self):
        m=DelayedCredit()
        for k in range(8): m.begin(k,(1,0,0,0))
        before=m.checkpoint()
        with self.assertRaises(ValueError): m.begin(8,(1,0,0,0))
        self.assertEqual(before,m.checkpoint())
        m.feedback(7,(0,0,0)); m.begin(8,(1,0,0,0)); m.feedback(8,(0,0,0))
        before=m.checkpoint()
        with self.assertRaises(ValueError): m.begin(9,(1,0,0,0))
        self.assertEqual(before,m.checkpoint())

    def test_bad_feedback_transactional(self):
        m=DelayedCredit()
        m.begin(0,(1,0,0,0))
        before=m.checkpoint()
        for k,y in ((1,(0,0,0)),(True,(0,0,0)),(0,(float("nan"),0,0)),(0,(0,0))):
            with self.assertRaises(ValueError): m.feedback(k,y)
            self.assertEqual(before,m.checkpoint())
        m.feedback(0,(0,0,0))

    def test_zero_residual_does_not_protect(self):
        m=DelayedCredit()
        for k in range(8):
            m.begin(k,(1,0,0,0)); m.feedback(k,(0,0,0))
        self.assertEqual(m.q,[[0.]*4 for _ in range(3)])
        self.assertEqual(m.w,[[0.]*4 for _ in range(3)])

    def test_prior_usefulness_and_ablation(self):
        a=DelayedCredit(); b=DelayedCredit(utility=False)
        for m in (a,b):
            m.begin(0,(1,0,0,0)); m.feedback(0,(1,0,0))
            m.begin(1,(1,0,0,0)); m.feedback(1,(-1,0,0))
        self.assertGreater(a.q[0][0],0.)
        self.assertEqual(b.q[0][0],0.)
        self.assertEqual(a.q[0][1],0.)

    def test_no_trace_control(self):
        a=DelayedCredit(); b=DelayedCredit(trace=False)
        for m in (a,b):
            m.begin(0,(1,0,0,0)); m.begin(1,(0,1,0,0))
            m.feedback(0,(1,0,0))
        self.assertGreater(a.w[0][0],0.)
        self.assertEqual(b.w[0][0],0.)

    def test_fixed_and_robust_controls(self):
        a=DelayedCredit(mode="meta"); b=DelayedCredit(mode="fixed"); c=DelayedCredit(mode="robust")
        for m in (a,b,c):
            m.begin(0,(1,0,0,0)); m.feedback(0,(1,0,0))
            m.begin(1,(1,0,0,0)); m.feedback(1,(1,0,0))
        self.assertEqual(a.w,b.w)
        self.assertNotEqual(a.w,c.w)

    def test_fitter_bounded_deterministic_and_frozen(self):
        packets=[]
        for k in range(4): packets.extend((("action",k,(1,0,0,0)),("feedback",k,(1,0,0))))
        rule,receipt=fit_engineering_packets(packets)
        self.assertEqual((rule,receipt),fit_engineering_packets(packets))
        self.assertEqual(receipt["evaluations"],29)
        self.assertLess(receipt["selected_mse"],receipt["initial_mse"])
        self.assertNotEqual(rule,Rule())
        self.assertFalse(receipt["scientific_gain_verified"])
        m=DelayedCredit(rule); m.begin(0,(1,0,0,0)); m.feedback(0,(0,0,0))
        self.assertEqual(m.rule,rule)
        self.assertEqual(DelayedCredit.restore(m.checkpoint()).rule,rule)

    def test_malformed_checkpoint_and_private_fields(self):
        m=DelayedCredit()
        m.begin(0,(1,0,0,0))
        d=json.loads(m.checkpoint())
        for field,value in (("clock",True),("theta",[float("inf")]*7),("pending",d["pending"]*2),("phase","A")):
            bad=dict(d); bad[field]=value
            with self.assertRaises(ValueError):
                DelayedCredit.restore(json.dumps(bad).encode("ascii"))
        with self.assertRaises(TypeError): m.begin(1,(1,0,0,0),phase="A")

if __name__=="__main__": unittest.main()
