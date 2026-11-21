"""Literal interface fixtures, not an evaluated scientific cohort."""
import json
import unittest
from research.mh09_delayed_credit import canonical
from research.mh10_frozen_recall import fit_bayes_fixture, FrozenBank
from research.test_mh10_frozen_recall import banks, X, POS, NEG, ZERO
from research.mh11_memory_formation import MemoryFormation, TRAIN, VERIFY

def event(m,y,x=X):
    k=m.clock; p=m.begin(k,x); m.feedback(k,y)
    return p

def advance(m,y,n):
    for _ in range(n): event(m,y)

class MH11Tests(unittest.TestCase):
    def test_stationary_no_creation(self):
        for kind in ("mh09","bayes"):
            m=MemoryFormation(banks(kind)[0])
            raw=m.old.raw
            advance(m,POS,40)
            self.assertEqual(m.phase,"watch")
            self.assertIsNone(m.candidate)
            self.assertEqual(m.old.raw,raw)

    def test_both_arms_create_only_after_separate_validation(self):
        for kind in ("mh09","bayes"):
            m=MemoryFormation(banks(kind)[0])
            raw=m.old.raw
            advance(m,NEG,3)
            self.assertEqual(m.phase,"collect")
            self.assertEqual(len(m.rows),0)
            advance(m,NEG,TRAIN)
            self.assertEqual(m.phase,"validate")
            self.assertEqual([r[0] for r in m.rows],list(range(3,35)))
            candidate=m.candidate.raw
            advance(m,NEG,VERIFY-1)
            self.assertEqual(m.phase,"validate")
            with self.assertRaises(ValueError): m.start_recall()
            event(m,NEG)
            self.assertEqual(m.phase,"sealed")
            self.assertEqual(m.candidate.raw,candidate)
            self.assertEqual(m.old.raw,raw)
            self.assertEqual([r[0] for r in m.validation],list(range(35,39)))
            r=m.start_recall()
            self.assertEqual(r.clock,m.clock)
            self.assertIsNone(r.choice())
            for k in range(r.clock,r.clock+8):
                r.begin(k,X); r.feedback(k,POS)
            self.assertEqual(r.choice(),0)
            self.assertEqual([b.raw for b in r.banks],[raw,candidate])

    def test_no_false_creation_on_short_contradiction(self):
        m=MemoryFormation(banks("bayes")[0])
        advance(m,NEG,2); event(m,POS)
        self.assertEqual(m.phase,"watch")
        self.assertEqual(m.reject,0)
        self.assertIsNone(m.candidate)

    def test_failed_collection_stops_without_overwrite(self):
        m=MemoryFormation(banks("bayes")[0]); original=m.old.raw
        advance(m,NEG,3+5); event(m,POS)
        self.assertEqual(m.phase,"stopped")
        advance(m,NEG,40)
        self.assertIsNone(m.candidate)
        self.assertEqual(m.old.raw,original)
        self.assertEqual(m.checkpoint(),MemoryFormation.restore(m.checkpoint()).checkpoint())

    def test_failed_validation_does_not_train_or_admit(self):
        m=MemoryFormation(banks("bayes")[0])
        advance(m,NEG,3+TRAIN)
        raw=m.candidate.raw
        event(m,POS)
        self.assertEqual(m.phase,"stopped")
        self.assertEqual(m.candidate.raw,raw)
        self.assertEqual(m.validation[-1][3],False)
        with self.assertRaises(ValueError): m.start_recall()
        self.assertEqual(m.checkpoint(),MemoryFormation.restore(m.checkpoint()).checkpoint())

    def test_restart_with_unresolved_packet(self):
        m=MemoryFormation(banks("mh09")[0]); advance(m,NEG,11)
        k=m.clock; m.begin(k,X)
        n=MemoryFormation.restore(m.checkpoint())
        for a in (m,n):
            a.feedback(k,NEG); advance(a,NEG,39-a.clock)
        self.assertEqual(m.phase,"sealed")
        self.assertEqual(m.checkpoint(),n.checkpoint())

    def test_restart_at_validation_and_sealed(self):
        m=MemoryFormation(banks("bayes")[0]); advance(m,NEG,3+TRAIN+2)
        n=MemoryFormation.restore(m.checkpoint())
        for a in (m,n): advance(a,NEG,2)
        self.assertEqual(m.checkpoint(),n.checkpoint())
        self.assertEqual(m.checkpoint(),MemoryFormation.restore(m.checkpoint()).checkpoint())

    def test_single_outstanding_and_bad_feedback_transactional(self):
        m=MemoryFormation(banks("bayes")[0]); m.begin(0,X)
        raw=m.checkpoint()
        with self.assertRaises(ValueError): m.begin(1,X)
        with self.assertRaises(ValueError): m.feedback(1,NEG)
        with self.assertRaises(ValueError): m.feedback(0,(float("nan"),0,0))
        self.assertEqual(m.checkpoint(),raw)
        m.feedback(0,NEG)
        with self.assertRaises(ValueError): m.feedback(0,NEG)

    def test_no_third_bank_or_hidden_label(self):
        m=MemoryFormation(banks("bayes")[0])
        with self.assertRaises(TypeError): m.begin(0,X,regime="new")
        advance(m,NEG,39)
        with self.assertRaises(ValueError): m.begin(m.clock,X)
        self.assertEqual(len(m.start_recall().banks),2)

    def test_candidate_is_bound_to_exact_recorded_training_rows(self):
        for kind in ("mh09","bayes"):
            m=MemoryFormation(banks(kind)[0])
            advance(m,NEG,3+TRAIN)
            self.assertEqual(m.phase,"validate")
            raw=m.checkpoint()
            self.assertEqual(MemoryFormation.restore(raw).checkpoint(),raw)

            # An otherwise well-formed bank of the *same* kind and
            # precision is not proof it was trained on these rows.
            swap=json.loads(raw)
            swap["candidate"]=m.old.record()
            with self.assertRaisesRegex(ValueError,"candidate/training receipt"):
                MemoryFormation.restore(canonical(swap))

            # A modified but still decidedly contradictory public
            # consequence must not silently retain the old frozen bank.
            edited=json.loads(raw)
            edited["rows"][0][2][0]=-0.75
            with self.assertRaisesRegex(ValueError,"candidate/training receipt"):
                MemoryFormation.restore(canonical(edited))

            # No negative attempt may mutate the original candidate.
            self.assertEqual(MemoryFormation.restore(raw).candidate.raw,m.candidate.raw)

    def test_bad_receipt_and_checkpoint_identity_rejected(self):
        m=MemoryFormation(banks("bayes")[0]); advance(m,NEG,39)
        d=json.loads(m.checkpoint()); d["validation"][0][3]=False
        with self.assertRaises(ValueError): MemoryFormation.restore(canonical(d))
        d=json.loads(m.checkpoint()); d["rows"][1][0]=d["rows"][0][0]
        with self.assertRaises(ValueError): MemoryFormation.restore(canonical(d))

if __name__=="__main__": unittest.main()
