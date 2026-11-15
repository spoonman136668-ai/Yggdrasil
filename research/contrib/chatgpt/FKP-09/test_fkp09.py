"""FKP-09 fixture-only pre-primary tests. NEVER sample DEV or protected labels."""
import hashlib
import unittest

from source import Source, cohort, context_slot, PAID, HELD
from model import (SharedWeights,ConventionalIncremental,direct_solve,
                   conventional_exact_solve,replay_counts,predict_program,
                   RAW_BYTES,CHECKPOINT_BYTES)

class FKP09Fixtures(unittest.TestCase):
    def feedback(self,seed,n=128):
        source=Source()
        view=source.view(seed)
        observations=tuple((x,source.observe(seed,x)) for x in view.choices[:n])
        self.assertEqual(source.charged(seed),n)
        return observations,view

    def test_protocol_identity_protected_and_disjoint(self):
        self.assertEqual(cohort(700),"fixture")
        self.assertEqual(cohort(900),"original")
        self.assertEqual(cohort(940),"revision")
        self.assertEqual(cohort(980),"negative")
        self.assertEqual(cohort(1900),"protected")
        self.assertEqual(context_slot(900),0)
        self.assertEqual(context_slot(940),0)
        with self.assertRaises(ValueError):context_slot(980)
        with self.assertRaises(ValueError):cohort(True)
        with self.assertRaises(PermissionError):Source().view(1900)
        with self.assertRaises(PermissionError):Source().held_dev(700,())
        v=Source().view(700)
        self.assertEqual(len(set(v.choices)),PAID)
        self.assertEqual(len(set(v.held)),HELD)
        self.assertFalse(set(v.choices)&set(v.held))

    def test_paid_source_reuse_and_held_fence(self):
        owner=Source();v=owner.view(700)
        self.assertIn(owner.observe(700,v.choices[0]),(0,1))
        with self.assertRaises(PermissionError):owner.observe(700,v.choices[0])
        with self.assertRaises(ValueError):owner.observe(700,v.held[0])
        self.assertEqual(owner.charged(700),1)

    def test_exact_64input_unenumerated_parity_and_independent_control(self):
        history,view=self.feedback(700)
        self.assertEqual(direct_solve(history[:16])[0],"UNDERDETERMINED")
        self.assertEqual(direct_solve(history[:32])[0],"UNDERDETERMINED")
        a,ap,rank=direct_solve(history)
        b,bp,brank=conventional_exact_solve(history)
        self.assertEqual((a,b,rank,brank),("EXACT","EXACT",65,65))
        self.assertEqual(ap,bp)
        self.assertEqual(tuple(predict_program(ap,x) for x,y in history),
                         tuple(y for x,y in history))
        self.assertEqual(len(view.held),512)

    def test_actual_contradiction_in_place_and_no_collateral(self):
        a,_=self.feedback(700)
        b,_=self.feedback(701)
        c,_=self.feedback(703)
        pa=direct_solve(a)[1]
        pb=direct_solve(b)[1]
        pc=direct_solve(c)[1]
        self.assertNotEqual(pa,pb)
        direct=SharedWeights()
        conventional=ConventionalIncremental()
        direct.update(0,pa);conventional.update(0,pa)
        direct.update(1,pc);conventional.update(1,pc)
        before=direct.program(1)
        raw_len=len(direct.raw_weights())
        direct.update(0,pb);conventional.update(0,pb)
        self.assertEqual(direct.program(0),pb)
        self.assertEqual(direct.program(1),before)
        self.assertEqual(len(direct.raw_weights()),raw_len)
        self.assertEqual(raw_len,RAW_BYTES)
        self.assertEqual(tuple(direct.counts),replay_counts(direct.all_programs()))
        self.assertEqual(tuple(direct.counts),tuple(conventional.counts))
        self.assertEqual(direct.snapshot(),SharedWeights.restore(direct.snapshot()).snapshot())
        before_snap=direct.snapshot()
        with self.assertRaises(ValueError):direct.update(32,pb)
        with self.assertRaises(ValueError):direct.update(0,2**65)
        self.assertEqual(direct.snapshot(),before_snap)

    def test_checkpoint_tamper_and_fake_integrity(self):
        m=SharedWeights()
        m.update(0,(1<<0)|(1<<64))
        m.update(31,(1<<63)|(1<<64))
        blob=m.snapshot()
        self.assertEqual(len(blob),CHECKPOINT_BYTES)
        self.assertEqual(len(m.raw_weights()),RAW_BYTES)
        self.assertEqual(SharedWeights.restore(blob).snapshot(),blob)
        tampered=bytearray(blob);tampered[19]^=1
        with self.assertRaises(ValueError):SharedWeights.restore(bytes(tampered))
        # A valid checksum cannot hide a contradictory aggregate matrix.
        tampered=bytearray(blob[:-32]);tampered[4]^=1
        resigned=bytes(tampered)+hashlib.sha256(tampered).digest()
        with self.assertRaises(ValueError):SharedWeights.restore(resigned)

    def test_outside_family_recognized_without_false_confidence(self):
        history,_=self.feedback(702)
        a,p,_=direct_solve(history)
        b,q,_=conventional_exact_solve(history)
        self.assertEqual(a,"INCONSISTENT")
        self.assertEqual(b,"INCONSISTENT")
        self.assertIsNone(p)
        self.assertIsNone(q)

if __name__=="__main__":
    unittest.main()
