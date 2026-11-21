"""Fixed authored packets; no scientific cohort, source, or world replay."""
import json
import unittest
from research.mh09_delayed_credit import DelayedCredit,canonical
from research.mh10_frozen_recall import FrozenBank,EvidenceRecall,fit_bayes_fixture

X=(1,0,0,0)
POS=(1,1,1)
NEG=(-1,-1,-1)
ZERO=(0,0,0)

def packets(y, count=4):
    return tuple(p for k in range(count) for p in (("action",k,X),("feedback",k,y)))

def banks(kind="mh09", count=32):
    if kind=="bayes":
        return tuple(fit_bayes_fixture(packets(y,count)) for y in (POS,NEG))
    result=[]
    for y in (POS,NEG):
        m=DelayedCredit(mode="fixed",utility=False)
        for op,k,v in packets(y,count):
            if op=="action": m.begin(k,v)
            else: m.feedback(k,v)
        result.append(FrozenBank.from_mh09(m.checkpoint()))
    return tuple(result)

class MH10Tests(unittest.TestCase):
    def test_bayes_posterior_closed_form(self):
        b=fit_bayes_fixture(packets(POS))
        p,v=b.predict(X)
        for x in p: self.assertAlmostEqual(x,64/65)
        self.assertAlmostEqual(v,.0625+1/65)
        self.assertEqual(b,FrozenBank.from_bayes(b.raw))

    def test_prior_uncertainty_for_unseen_feature(self):
        b=fit_bayes_fixture(packets(POS))
        self.assertEqual(b.predict((0,1,0,0)),((0.,0.,0.),1.0625))

    def test_underfit_bank_abstains_instead_of_forced_retrieval(self):
        m=EvidenceRecall(banks("mh09",count=4))
        for k in range(8): m.begin(k,X); m.feedback(k,POS)
        self.assertIsNone(m.choice())
        self.assertGreater(m.posterior()[2],.95)

    def test_receipt_order_and_cold_restore_stable(self):
        source=banks("bayes")
        a=EvidenceRecall(source); b=EvidenceRecall(source)
        for k in range(3): a.begin(k,X); b.begin(k,X)
        for k in (2,0,1): a.feedback(k,(POS,NEG,POS)[k])
        for k in (0,1,2): b.feedback(k,(POS,NEG,POS)[k])
        self.assertEqual(a.posterior(),b.posterior())
        self.assertEqual(a.checkpoint(),b.checkpoint())
        self.assertEqual(a.posterior(),EvidenceRecall.restore(a.checkpoint()).posterior())

    def test_no_retrieval_before_feedback(self):
        for kind in ("mh09","bayes"):
            m=EvidenceRecall(banks(kind))
            self.assertIsNone(m.begin(0,X))
            self.assertIsNone(m.begin(1,X))
            self.assertEqual(m.posterior(),(1/3,)*3)
            self.assertIsNone(m.feedback(1,POS))
            self.assertEqual(m.feedback(0,POS),0)
            self.assertIsNotNone(m.begin(2,X))

    def test_return_and_frozen_state_both_arms(self):
        for kind in ("mh09","bayes"):
            original=banks(kind)
            m=EvidenceRecall(original)
            for k,y in enumerate((POS,)*8+(NEG,)*8+(POS,)*8):
                m.begin(k,X); m.feedback(k,y)
                if k in (7,15,23): self.assertEqual(m.choice(),(0,1,0)[k//8])
            self.assertEqual([b.raw for b in m.banks],[b.raw for b in original])
            self.assertEqual(len(m.evidence),8)

    def test_unknown_and_ambiguous_abstain(self):
        m=EvidenceRecall(banks("bayes"))
        for k in range(8): m.begin(k,X); m.feedback(k,ZERO)
        self.assertIsNone(m.choice())
        self.assertGreater(m.posterior()[2],.95)
        b=banks("bayes")[0]
        t=EvidenceRecall((b,b))
        for k in range(4): t.begin(k,X); t.feedback(k,POS)
        self.assertIsNone(t.choice())

    def test_cold_checkpoint_pending_and_original_order(self):
        a=EvidenceRecall(banks("bayes"))
        a.begin(0,X); a.begin(1,X); a.begin(2,X)
        b=EvidenceRecall.restore(a.checkpoint())
        for k in (2,0,1):
            self.assertEqual(a.feedback(k,POS),b.feedback(k,POS))
        self.assertEqual(a.checkpoint(),b.checkpoint())
        self.assertEqual(a.choice(),0)

    def test_feedback_rejection_is_transactional(self):
        m=EvidenceRecall(banks("bayes"))
        m.begin(0,X)
        before=m.checkpoint()
        for k,y in ((1,POS),(True,POS),(0,(float("nan"),0,0)),(0,(3,0,0))):
            with self.assertRaises(ValueError): m.feedback(k,y)
            self.assertEqual(m.checkpoint(),before)
        m.feedback(0,POS)
        with self.assertRaises(ValueError): m.feedback(0,POS)

    def test_capacity_and_no_silent_expiry(self):
        m=EvidenceRecall(banks())
        for k in range(8): m.begin(k,X)
        before=m.checkpoint()
        with self.assertRaises(ValueError): m.begin(8,X)
        self.assertEqual(before,m.checkpoint())
        m.feedback(7,POS); m.begin(8,X); m.feedback(8,POS)
        with self.assertRaises(ValueError): m.begin(9,X)

    def test_no_private_labels_and_canonical_restore(self):
        m=EvidenceRecall(banks("bayes"))
        with self.assertRaises(TypeError): m.begin(0,X,regime="A")
        m.begin(0,X)
        d=json.loads(m.checkpoint())
        for field,value in (("clock",True),("evidence",[[0,[0.,0.,0.]]]),("phase","A"),("pending",d["pending"]*2)):
            bad=dict(d); bad[field]=value
            with self.assertRaises(ValueError): EvidenceRecall.restore(canonical(bad))

    def test_bayes_bad_identity_and_no_unresolved_mh09_archive(self):
        with self.assertRaises(ValueError): fit_bayes_fixture((("action",0,X),("feedback",1,POS)))
        m=DelayedCredit(); m.begin(0,X)
        with self.assertRaises(ValueError): FrozenBank.from_mh09(m.checkpoint())

if __name__=="__main__": unittest.main()
