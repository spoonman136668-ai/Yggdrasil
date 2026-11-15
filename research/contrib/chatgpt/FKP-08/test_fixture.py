"""FKP-08 source-safe fixture qualification; never instantiate original DEV or protected worlds.

The only Source observations in this file use registered fixture context 700.
All 800..831 memory records below are locally constructed synthetic byte patterns:
they are NOT observations from the original FKP-08 development source.
This is engineering verification, not an original or independent science run.
"""
from __future__ import annotations

import hashlib
import unittest
from unittest import mock

import model
import source


class TestSourceFence(unittest.TestCase):
    def test_registered_cohort_boundaries_without_protected_access(self):
        self.assertEqual(source.cohort(700), "fixture")
        self.assertEqual(source.cohort(703), "fixture")
        self.assertEqual(source.cohort(800), "development")
        self.assertEqual(source.cohort(831), "development")
        self.assertEqual(source.cohort(1800), "primary")
        self.assertEqual(source.cohort(2815), "negative")
        for invalid in (699, 704, 799, 832, 1799, 1864, 2799, 2816, True):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                source.cohort(invalid)

    def test_fixture_action_accounting_and_evaluator_fence(self):
        owner = source.Source()
        public = owner.view(700, 1)
        self.assertEqual(len(public.choices), 128)
        self.assertEqual(len(public.held), 128)
        self.assertEqual(len(set(public.choices) & set(public.held)), 0)
        action = public.choices[0]
        self.assertIn(owner.observe(700, 1, action), (0, 1))
        self.assertEqual(owner.charged(700, 1), 1)
        with self.assertRaises(PermissionError):
            owner.observe(700, 1, action)
        with self.assertRaises(ValueError):
            owner.observe(700, 1, public.held[0])
        with self.assertRaises(PermissionError):
            owner.held_dev(700, 1, public.held)
        self.assertEqual(owner.charged(700, 1), 1)


class TestDirectMemory(unittest.TestCase):
    def test_genuine_fixture_repair_with_only_paid_evidence(self):
        owner = source.Source()
        base = tuple((x, owner.observe(700, 0, x)) for x in range(256))
        view = owner.view(700, 1)
        revision = tuple((x, owner.observe(700, 1, x)) for x in view.choices[:16])
        self.assertEqual(owner.charged(700, 0), 256)
        self.assertEqual(owner.charged(700, 1), 16)

        # Temporarily permit the registered fixture as a one-context model;
        # never persist or alter the real fixed 32-context production design.
        with mock.patch.object(model, "CONTEXTS", (700,)):
            memory = model.Memory()
            memory.set_base(700, base)
            before = memory.rule(700, 0)
            result = memory.fit(700, 1, revision)
            self.assertEqual(result["source_actions"], 16)
            self.assertEqual(result["best_mismatches"], 0)
            self.assertEqual(memory.rule(700, 0), before)
            self.assertEqual(
                memory.predict(700, 1, tuple(x for x, _ in revision)),
                tuple(y for _, y in revision),
            )
            with self.assertRaises(ValueError):
                memory.fit(700, 1, revision)
            with self.assertRaises(ValueError):
                memory.fit(700, 3, revision)
            with self.assertRaises(ValueError):
                memory.set_base(700, base)
        self.assertEqual(model.CONTEXTS, tuple(range(800, 832)))

    @staticmethod
    def synthetic_complete_memory():
        """Populate model storage using local constants, NOT any FKP-08 Source."""
        memory = model.Memory()
        motif_count = len(source.MOTIF_MASKS)
        for context in model.CONTEXTS:
            history = tuple(
                (state, ((context * 37 + state * 131 + (state >> 2)) >> 3) & 1)
                for state in range(256)
            )
            memory.set_base(context, history)
            for version in (1, 2, 3):
                left = (context + version) % (motif_count - 1)
                memory.patches[(context, version)] = (left, left + 1)
        return memory

    def test_fixed_capacity_cold_restore_and_historical_versions(self):
        memory = self.synthetic_complete_memory()
        snapshots = {
            (context, version): memory.rule(context, version)
            for context in model.CONTEXTS for version in range(4)
        }
        self.assertEqual(len(snapshots), 128)
        self.assertEqual(len(memory.raw_weights()), 1216)
        checkpoint = memory.snapshot()
        self.assertEqual(len(checkpoint), 1252)
        restored = model.Memory.restore(checkpoint)
        self.assertEqual(restored.snapshot(), checkpoint)
        self.assertEqual(
            {(c, v): restored.rule(c, v) for c in model.CONTEXTS for v in range(4)},
            snapshots,
        )
        sizes = model.standard_baseline_sizes(memory)
        self.assertEqual(sizes["bitsets_raw"], 4096)
        self.assertEqual(sizes["learned_delta_raw"], 1216)
        self.assertTrue(sizes["conventional_exact_delta_ties_candidate"])

        corrupt = bytearray(checkpoint)
        corrupt[17] ^= 1
        with self.assertRaises(ValueError):
            model.Memory.restore(bytes(corrupt))

        # Re-sign a malformed patch to verify structural rejection is not
        # merely an integrity-hash test.
        malformed = bytearray(checkpoint[:-32])
        malformed[4 + 1024:4 + 1026] = bytes((3, 3))
        malicious_checkpoint = bytes(malformed) + hashlib.sha256(malformed).digest()
        with self.assertRaises(ValueError):
            model.Memory.restore(malicious_checkpoint)

    def test_source_validation_is_fail_closed(self):
        memory = model.Memory()
        context = model.CONTEXTS[0]
        with self.assertRaises(ValueError):
            memory.set_base(context, ((0, 1),))
        with self.assertRaises(ValueError):
            memory.fit(context, 1, ((0, 1),) * 16)
        with self.assertRaises(ValueError):
            memory.rule(context, 0)
        with self.assertRaises(ValueError):
            memory.snapshot()


if __name__ == "__main__":
    unittest.main()
