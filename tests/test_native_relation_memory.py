"""NKR-01 preregistered fabricated-only native contextual relation tests."""
import unittest

from yggdrasil.public_causal_cells import PublicCausalCells
from yggdrasil.native_relation_memory import NativeRelationMemory

TRAIN = (0, 1, 2, 4, 8)
HELDOUT = (3, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15)

def truth(slot, context, action):
    """Public deterministic intervention consequence; no hidden source."""
    return 1 ^ action ^ (context.bit_count() & 1) ^ (slot & 1)

def trained():
    cells, memory = PublicCausalCells(), NativeRelationMemory()
    for slot in range(16):
        ret = slot >= 7
        address = slot - 7 if ret else slot
        for context in TRAIN:
            for action in (0, 1):
                outcome = truth(slot, context, action)
                cells.observe(address, action, outcome, retained=ret)
                assert memory.observe_public(address, context, action, outcome,
                                             f"public:slot{slot}:{context}:{action}",
                                             retained=ret)
    return cells, memory

class NativeRelationTests(unittest.TestCase):
    def test_nogradient_no_hidden_first_use_oracle_import(self):
        import inspect
        import yggdrasil.native_relation_memory as module
        c = inspect.getsource(module)
        for bad in ("from oracle", "import oracle", "WSP-114/native",
                    "WSP-115/experiment_v2", "backprop", "gradient_descent"):
            self.assertNotIn(bad, c)

    def test_all_native_slots_rank_template_dedup(self):
        _, bank = trained()
        self.assertEqual(bank.unique_observations, 160)
        self.assertEqual(bank.ADDRESSES, 16)
        self.assertEqual(bank.MAX_UNIQUE_OBSERVATIONS, 512)
        self.assertEqual(bank.unique_programmed_profiles, 2)
        self.assertIs(bank._weights[0], bank._weights[2])
        self.assertIs(bank._weights[1], bank._weights[3])
        for slot in range(16):
            retained = slot >= 7
            address = slot - 7 if retained else slot
            self.assertEqual(bank.rank(address, retained=retained), 10)

    def test_frozen_heldout_context_gain_on_real_native_decision_path(self):
        cells, bank = trained()
        baseline_correct = novel_correct = 0
        for slot in range(16):
            ret = slot >= 7
            address = slot - 7 if ret else slot
            old = cells.choose(address, retained=ret)
            self.assertIn(old, (0, 1))
            for ctx in HELDOUT:
                self.assertNotIn(ctx, TRAIN)
                new = cells.choose_contextual(address, ctx, bank, retained=ret)
                self.assertIn(new, (0, 1))
                novel_correct += truth(slot, ctx, new)
                baseline_correct += truth(slot, ctx, old)
                for action in (0, 1):
                    self.assertEqual(bank.predict(address, ctx, action, retained=ret),
                                     truth(slot, ctx, action))
        self.assertEqual(novel_correct, 176)
        self.assertLessEqual(baseline_correct, 140)
        self.assertGreaterEqual(novel_correct - baseline_correct, 36)

    def test_exact_legacy_checkpoint_and_existing_functions_unchanged(self):
        cells, bank = trained()
        checkpoint = cells.snapshot()
        self.assertEqual(len(checkpoint), 164)
        restored = PublicCausalCells.restore(checkpoint)
        self.assertEqual(restored.snapshot(), checkpoint)
        for slot in range(16):
            ret = slot >= 7
            address = slot - 7 if ret else slot
            self.assertEqual(cells.choose(address, retained=ret),
                             restored.choose(address, retained=ret))
            self.assertEqual(cells.choose_wilson(address, retained=ret),
                             restored.choose_wilson(address, retained=ret))
            self.assertEqual(cells.observed_action_contrast(address, retained=ret),
                             restored.observed_action_contrast(address, retained=ret))
        self.assertEqual(cells.snapshot(), checkpoint)
        self.assertEqual(bank.unique_observations, 160)

    def test_duplicate_cross_source_idempotent_conflicting_evidence_atomic(self):
        _, bank = trained()
        initial = bank.checkpoint()
        self.assertFalse(bank.observe_public(0, 0, 0, truth(0, 0, 0),
                                             "another_source"))
        self.assertEqual(bank.checkpoint(), initial)
        with self.assertRaises(ValueError):
            bank.observe_public(0, 0, 0, 1 - truth(0, 0, 0), "conflict")
        self.assertEqual(bank.checkpoint(), initial)
        with self.assertRaises(ValueError):
            bank.observe_public(0, 3, 0, 1 - truth(0, 3, 0), "incompatible")
        self.assertEqual(bank.checkpoint(), initial)

    def test_unidentified_relation_falls_back_to_incumbent(self):
        cells = PublicCausalCells()
        bank = NativeRelationMemory()
        cells.observe(0, 0, 1)
        cells.observe(0, 1, 0)
        old = cells.choose(0)
        self.assertIsNone(bank.predict(0, 15, 0))
        self.assertEqual(cells.choose_contextual(0, 15, bank), old)
        self.assertTrue(bank.observe_public(0, 0, 0, 1, "first"))
        self.assertEqual(cells.choose_contextual(0, 15, bank), old)
        self.assertEqual(cells.snapshot(), PublicCausalCells.restore(cells.snapshot()).snapshot())

    def test_cold_replay_tamper_rejection(self):
        cells, bank = trained()
        checkpoint = bank.checkpoint()
        restored = NativeRelationMemory.restore(checkpoint)
        self.assertEqual(restored.checkpoint(), checkpoint)
        self.assertEqual(restored.unique_programmed_profiles, 2)
        for slot in range(16):
            ret = slot >= 7
            address = slot - 7 if ret else slot
            for ctx in HELDOUT:
                self.assertEqual(cells.choose_contextual(address, ctx, restored, retained=ret),
                                 cells.choose_contextual(address, ctx, bank, retained=ret))
        tampered = bytearray(checkpoint)
        tampered[-40] ^= 1
        for bad in (bytes(tampered), checkpoint[:-1], b"{}", bytearray(checkpoint),
                    b"X" * 65001):
            with self.subTest(kind=type(bad), size=len(bad)):
                with self.assertRaises(ValueError):
                    NativeRelationMemory.restore(bad)
        self.assertEqual(bank.checkpoint(), checkpoint)

    def test_invalid_record_preflight_without_mutation(self):
        bank = NativeRelationMemory()
        before = bank.checkpoint()
        bad = ((7, 0, 0, 1, "x", False), (9, 0, 0, 1, "x", True),
               (0, -1, 0, 1, "x", False), (0, 16, 0, 1, "x", False),
               (0, True, 0, 1, "x", False), (0, 0, 2, 1, "x", False),
               (0, 0, 1, 2, "x", False), (0, 0, 0, 1, "", False),
               (0, 0, 0, 1, " ", False), (0, 0, 0, 1, "x" * 129, False),
               (0, 0, 0, 1, "x", 1))
        for address,ctx,action,outcome,source,ret in bad:
            with self.subTest(sample=(address,ctx,action,outcome,source,ret)):
                with self.assertRaises(ValueError):
                    bank.observe_public(address,ctx,action,outcome,source,retained=ret)
                self.assertEqual(bank.checkpoint(), before)
        cells = PublicCausalCells()
        for bad_call in ((0, 0, None), (0, -1, bank), (7, 0, bank)):
            with self.assertRaises(ValueError):
                cells.choose_contextual(*bad_call)

    def test_new_post_restore_observations_replay_identically(self):
        before = NativeRelationMemory()
        self.assertTrue(before.observe_public(0, 0, 0, 1, "first"))
        restored = NativeRelationMemory.restore(before.checkpoint())
        for memory in (before, restored):
            memory.observe_public(0, 1, 0, 0, "second")
            memory.observe_public(0, 0, 1, 0, "third")
        self.assertEqual(restored.checkpoint(), before.checkpoint())

if __name__ == "__main__":
    unittest.main()
