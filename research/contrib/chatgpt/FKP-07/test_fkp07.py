"""Public *fixture only* pre-primary tests; never open DEV 800..823 here."""
import importlib
import unittest

src=importlib.import_module('source')
rep=importlib.import_module('repair')


class TestFKP07(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.laws=tuple(src.public.laws())

    def test_original_fkp06_family_exact_and_fixtures(self):
        self.assertEqual(src.N_LAWS,107880)
        preflight=src.source_preflight()
        self.assertEqual(preflight['hypotheses'],107880)
        self.assertFalse(preflight['primary_opened'])
        self.assertEqual(len(preflight['fixtures']),2)

    def test_public_only_bounded_actual_feedback(self):
        w=src.SourceOwnerWorld(880,self.laws)
        v=w.public_view()
        self.assertEqual(len(set(v.action_pool)),128)
        self.assertEqual(len(set(v.held_inputs)),256)
        self.assertFalse(set(v.action_pool)&set(v.held_inputs))
        with self.assertRaises(ValueError):w.observe(v.held_inputs[0])
        with self.assertRaises(PermissionError):w.dev_held_labels(v.held_inputs)
        outcomes=[w.observe(a) for a in v.action_pool[:64]]
        self.assertTrue(all(x in (0,1) for x in outcomes))
        self.assertEqual(w.used_actions,64)
        with self.assertRaises(PermissionError):w.observe(v.action_pool[64])
        with self.assertRaises(ValueError):w.observe(v.action_pool[0])
        self.assertEqual(len(w.dev_held_labels(v.held_inputs)),256)

    def test_real_inplace_repair_preserves_unrelated_programs(self):
        weights=rep.SharedWeights()
        replay=rep.ReplayControl()
        law_a=(0,1,2,3);law_b=(4,5,6,7);new=(0,1,8,9)
        for i,law in ((0,law_a),(1,law_b)):
            weights.update(i,law);replay.update(i,law)
        original=tuple(weights.predict(1,s) for s in (0,2**31-1,0x11223344))
        before=weights.snapshot()
        weights.update(0,new);replay.update(0,new)
        self.assertNotEqual(before,weights.snapshot())
        self.assertEqual(tuple(weights.counters),tuple(replay.counters))
        self.assertEqual(tuple(weights.predict(1,s) for s in (0,2**31-1,0x11223344)),original)
        self.assertEqual(weights.program(0),new)
        self.assertEqual(weights.program(1),law_b)
        # Proper causal inverse edit returns to the exact original snapshot.
        weights.update(0,law_a)
        self.assertEqual(weights.snapshot(),before)

    def test_integrity_restoration_no_growth_and_tamper(self):
        w=rep.SharedWeights()
        self.assertEqual(rep.RAW_LEARNED_BYTES,1120)
        self.assertEqual(len(w.snapshot()),rep.CHECKPOINT_BYTES)
        for i in range(32):
            w.update(i,(i,(i+1)%32,(i+2)%32,(i+3)%32))
        self.assertEqual(rep.SharedWeights.restore(w.snapshot()).snapshot(),w.snapshot())
        corrupt=bytearray(w.snapshot());corrupt[23]^=1
        with self.assertRaises(ValueError):rep.SharedWeights.restore(bytes(corrupt))
        # Even a correctly rehashed but inconsistent weight table is rejected.
        import hashlib
        changed=bytearray(w.snapshot());changed[5]^=1
        changed[-32:]=hashlib.sha256(changed[:-32]).digest()
        with self.assertRaises(ValueError):rep.SharedWeights.restore(bytes(changed))
        with self.assertRaises(ValueError):w.update(32,(0,1,2,3))
        with self.assertRaises(ValueError):w.update(0,(0,0,1,2))

    def test_unknown_context_abstains_and_old_overwrite_fails(self):
        w=rep.SharedWeights();bad=rep.NaiveOverwrite()
        self.assertIsNone(w.predict(4,100))
        a=(0,1,2,3);b=(4,5,6,7)
        w.update(0,a);w.update(1,b)
        bad.update(0,a);bad.update(1,b)
        witness=3
        self.assertEqual(w.predict(0,witness),1)
        self.assertNotEqual(w.predict(0,witness),bad.predict(0,witness))
        self.assertEqual(len(w.counters),496)

if __name__=='__main__':unittest.main()
