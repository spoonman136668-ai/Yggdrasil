"""FKP-09 fixture-only tests. Never instantiate original 900..915 source law."""
import hashlib
import unittest

from source import Source,BITS,CONTEXTS,FIXTURE,cohort,parity,public_masks
from model import SharedCausalCore,PAIR_INDEXES
from run_dev import conventional_exact_posterior

class FKP09FixtureTests(unittest.TestCase):
    def test_public_split_and_protected_source_fence(self):
        self.assertEqual(len(PAIR_INDEXES),8128)
        self.assertEqual(len(CONTEXTS),16)
        self.assertEqual(cohort(850),"fixture")
        owner=Source()
        view=owner.public_view(850)
        self.assertEqual(len(view.choices),128)
        self.assertEqual(len(view.held_masks),128)
        self.assertFalse(set(view.choices)&set(view.held_masks))
        self.assertEqual(public_masks(850),(view.choices,view.held_masks))
        with self.assertRaises(PermissionError):
            owner.public_view(1900)
        with self.assertRaises(PermissionError):
            owner.held_dev(850,view.held_masks)
        with self.assertRaises(PermissionError):
            Source(protected_key=b"k"*32).public_view(850)
        with self.assertRaises(PermissionError):
            Source(protected_key=b"x")
        with self.assertRaises(ValueError):
            cohort(900.0)
        with self.assertRaises(PermissionError):
            owner.observe_core(4,0)

    def test_real_fixture_actions_are_counted_and_never_replayed(self):
        owner=Source()
        view=owner.public_view(851)
        vals=tuple(owner.observe_context(851,a) for a in view.choices[:32])
        self.assertEqual(len(vals),32)
        self.assertTrue(all(bit in (0,1) for bit in vals))
        self.assertEqual(owner.context_charged(851),32)
        with self.assertRaises(PermissionError):
            owner.observe_context(851,view.choices[0])
        with self.assertRaises(PermissionError):
            owner.observe_context(851,view.choices[32])
        with self.assertRaises(ValueError):
            owner.observe_context(851,view.held_masks[0])
        for i in range(128):
            self.assertIn(owner.observe_core(0,i),(0,1))
        self.assertEqual(owner.core_charged(0),128)
        with self.assertRaises(PermissionError):
            owner.observe_core(0,0)
        with self.assertRaises(ValueError):
            owner.observe_core(0,128)

    @staticmethod
    def fixture_memory():
        base=int.from_bytes(hashlib.sha256(b"FKP09-public-fixture-only").digest()[:16],"big")
        mem=SharedCausalCore()
        observations=tuple((i,(base>>i)&1) for i in range(BITS))
        mem.learn_initial_core(observations)
        view=Source().public_view(852)
        true_law=base^(1<<21)^(1<<77)
        history=tuple((x,parity(x&true_law)) for x in view.choices[:32])
        fitted=mem.learn_context(900,history)
        return mem,view,history,base,fitted

    def test_fit_is_genuine_and_independent_bayes_matches_frozen_transcript(self):
        mem,view,history,base,fit=self.fixture_memory()
        self.assertEqual(len(history),32)
        self.assertGreaterEqual(fit["pair_candidates"],1)
        self.assertEqual(tuple(parity(x&(base^mem.adapters[900])) for x,y in history),
                         tuple(y for x,y in history))
        conventional=conventional_exact_posterior(base,history,view.held_masks)
        self.assertEqual(mem.predict(900,view.held_masks),
                         conventional["lex_exact_prediction"])
        self.assertEqual(len(conventional["bayes_prediction"]),128)
        with self.assertRaises(ValueError):
            mem.learn_context(900,history)
        with self.assertRaises(ValueError):
            mem.predict(901,view.held_masks)
        with self.assertRaises(ValueError):
            mem.learn_context(901,history[:-1])

    def test_actual_shared_core_update_and_atomic_overflow(self):
        mem,view,history,base,fit=self.fixture_memory()
        predictions=mem.predict(900,view.held_masks)
        for step,(a,b) in enumerate(((3,6),(10,19),(27,101)),1):
            newbase=mem.base^(1<<a)^(1<<b)
            record=mem.rebase(tuple((i,(newbase>>i)&1) for i in range(BITS)))
            self.assertEqual(record["shared_synapse_flips"],2)
            self.assertEqual(mem.base,newbase)
            self.assertEqual(mem.predict(900,view.held_masks),predictions)
        self.assertLessEqual(mem.adapters[900].bit_count(),8)
        previous=mem.snapshot()
        # Fresh shock toggles 16 bits disjoint from current adapter; it must
        # NOT overwrite any old learned memory before capacity validation.
        unused=[i for i in range(BITS) if not (mem.adapters[900]>>i)&1][:16]
        shock=mem.base
        for i in unused:shock^=1<<i
        with self.assertRaisesRegex(ValueError,"CAPACITY_OVERFLOW"):
            mem.rebase(tuple((i,(shock>>i)&1) for i in range(BITS)))
        self.assertEqual(mem.snapshot(),previous)

    def test_fixed_bytes_cold_restore_and_tamper_abstention(self):
        mem,view,history,base,fit=self.fixture_memory()
        self.assertEqual(len(mem.raw_weights()),144)
        receipt=mem.snapshot()
        self.assertEqual(len(receipt),180)
        cold=SharedCausalCore.restore(receipt)
        self.assertEqual(cold.snapshot(),receipt)
        self.assertEqual(cold.predict(900,view.held_masks),
                         mem.predict(900,view.held_masks))
        invalid=bytearray(receipt);invalid[9]^=1
        with self.assertRaises(ValueError):
            SharedCausalCore.restore(bytes(invalid))
        with self.assertRaises(ValueError):
            SharedCausalCore.restore(receipt[:-1])
        with self.assertRaises(ValueError):
            mem.learn_initial_core(tuple((i,0) for i in range(BITS)))

if __name__=="__main__":
    unittest.main()
