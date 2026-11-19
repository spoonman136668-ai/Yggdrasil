"""ACT01 source-only native four-action/four-outcome compatibility tests.

Mechanical public-shaped events only; no source owner action, original
protected first-use, scientific transfer claim or native model promotion.
"""
import hashlib
import struct
import unittest

from yggdrasil.public_causal_cells import PublicCausalCells
from yggdrasil.public_multiaction_cells import NativeMultiActionCells as Cells


def identity(index):
    return hashlib.sha256(
        f"ACT01-PUBLIC-MECHANICAL-OBSERVATION-{index}".encode("ascii")
    ).hexdigest()


class NativeMultiActionCellsEngineering(unittest.TestCase):
    def test_four_distinct_witnessed_actions_and_outcomes(self):
        c = Cells()
        self.assertIsNone(c.choose(0, 3))
        self.assertIsNone(c.probability(0, 3, 3))
        for action in range(4):
            for repeat in range(3):
                self.assertTrue(c.observe(
                    identity(100 + 10*action + repeat), 0, action, action))
        self.assertEqual(c.choose(0, 3), 3)
        self.assertEqual(c.choose(0, 2), 2)
        self.assertEqual(c.counts(0, 3), (0, 0, 0, 3))
        self.assertEqual(c.probability(0, 3, 3), (4, 7))
        self.assertEqual(c.probability(0, 3, 0), (1, 7))
        self.assertIsNone(c.probability(1, 3, 3))
        self.assertIsNone(c.choose(1, 0))

    def test_legacy_pyc1_binary_causal_memory_is_losslessly_retained(self):
        old = PublicCausalCells()
        for address in range(7):
            old.observe(address, 0, 1)
            old.observe(address, 1, 0)
        for address in range(9):
            old.observe(address, 0, 0, retained=True)
            old.observe(address, 1, 1, retained=True)
        before = old.snapshot()
        self.assertEqual(len(before), 164)
        new = Cells.migrate(before)
        self.assertEqual(new.original_binary_snapshot(), before)
        for addr in range(7):
            self.assertEqual(new.counts(addr, 0), (0, 1, 0, 0))
            self.assertEqual(new.counts(addr, 1), (1, 0, 0, 0))
        for addr in range(9):
            self.assertEqual(new.counts(addr, 0, retained=True),
                             (1, 0, 0, 0))
            self.assertEqual(new.counts(addr, 1, retained=True),
                             (0, 1, 0, 0))
        new.observe(identity(901), 0, 2, 3)
        new.observe(identity(902), 0, 3, 2, retained=True)
        self.assertEqual(new.original_binary_snapshot(), before)
        self.assertEqual(old.snapshot(), before)
        self.assertEqual(new.counts(0, 2), (0, 0, 0, 1))
        self.assertEqual(new.counts(0, 3, retained=True), (0, 0, 1, 0))
        restored = Cells.restore(new.snapshot())
        self.assertEqual(restored.original_binary_snapshot(), before)
        self.assertEqual(restored.snapshot(), new.snapshot())

    def test_cold_replay_and_cumulative_subsequent_public_observations(self):
        old = PublicCausalCells()
        old.observe(0, 0, 1)
        migrated = Cells.migrate(old.snapshot())
        for i in range(25):
            migrated.observe(identity(i), i % 7, i % 4, (i*3) % 4)
        exact = migrated.snapshot()
        self.assertEqual(len(exact), Cells.MIN_CHECKPOINT_BYTES +
                         25 * Cells.EVENT_BYTES)
        cold = Cells.restore(exact)
        self.assertEqual(cold.snapshot(), exact)
        for i in range(25, 42):
            for cells in (migrated, cold):
                cells.observe(identity(i), i % 7, i % 4, (i*3) % 4)
        self.assertEqual(migrated.snapshot(), cold.snapshot())
        self.assertEqual(old.snapshot(), cold.original_binary_snapshot())

    def test_sixteen_native_addresses_and_retained_memory_are_independent(self):
        c = Cells()
        for i in range(4):
            c.observe(identity(1000+i), 0, i, i)
            c.observe(identity(2000+i), 0, i, (i+1) % 4,
                      retained=True)
        self.assertEqual(c.choose(0, 0), 0)
        self.assertEqual(c.choose(0, 0, retained=True), 3)
        self.assertIsNone(c.choose(6, 0))
        self.assertIsNone(c.choose(8, 0, retained=True))
        self.assertEqual(len(c.snapshot()),
                         Cells.MIN_CHECKPOINT_BYTES + 8 * Cells.EVENT_BYTES)

    def test_exact_duplicates_idempotent_and_conflicts_fail_closed(self):
        c = Cells()
        ref = identity(3000)
        self.assertTrue(c.observe(ref, 1, 2, 3))
        prior = c.snapshot()
        self.assertFalse(c.observe(ref, 1, 2, 3))
        self.assertEqual(c.snapshot(), prior)
        for args in ((1, 2, 0, False), (1, 3, 3, False),
                     (2, 2, 3, False), (1, 2, 3, True)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                c.observe(ref, *args[:3], retained=args[3])
            self.assertEqual(c.snapshot(), prior)

    def test_invalid_new_source_action_state_or_address_cannot_mutate(self):
        c = Cells()
        old = c.snapshot()
        bad = [
            ("0"*64, True, 2, 3, False),
            ("0"*64, 7, 2, 3, False),
            ("0"*64, 0, True, 3, False),
            ("0"*64, 0, 4, 3, False),
            ("0"*64, 0, 0, 4, False),
            ("0"*64, 0, 0, True, False),
            ("0"*64, 9, 0, 0, True),
            ("0"*64, 0, 0, 0, 1),
            ("A"*64, 0, 0, 0, False),
            ("short", 0, 0, 0, False),
            (7, 0, 0, 0, False),
        ]
        for case in bad:
            with self.subTest(case=case), self.assertRaises(ValueError):
                c.observe(*case[:4], retained=case[4])
            self.assertEqual(c.snapshot(), old)
        with self.assertRaises(ValueError):
            c.counts(0, 4)
        with self.assertRaises(ValueError):
            c.probability(0, 0, 4)
        with self.assertRaises(ValueError):
            c.choose(0, -1)

    def test_rehashed_forged_count_or_source_tape_does_not_cold_restore(self):
        c = Cells()
        for i in range(3):
            c.observe(identity(i), 0, i, 3-i)
        genuine = c.snapshot()
        self.assertEqual(Cells.restore(genuine).snapshot(), genuine)
        forged_count = bytearray(genuine)
        count_slot = Cells.HEADER_BYTES + 2*2
        forged_count[count_slot] ^= 1
        forged_count[-32:] = hashlib.sha256(forged_count[:-32]).digest()
        forged_tape = bytearray(genuine)
        first_id = Cells.HEADER_BYTES + Cells.LEARNED_BYTES
        forged_tape[first_id] ^= 1
        forged_tape[-32:] = hashlib.sha256(forged_tape[:-32]).digest()
        forged_order = bytearray(genuine)
        start = Cells.HEADER_BYTES + Cells.LEARNED_BYTES
        next_pos = start + Cells.EVENT_BYTES
        x = bytes(forged_order[start:next_pos])
        forged_order[start:next_pos] = forged_order[
            next_pos:next_pos + Cells.EVENT_BYTES]
        forged_order[next_pos:next_pos + Cells.EVENT_BYTES] = x
        forged_order[-32:] = hashlib.sha256(forged_order[:-32]).digest()
        for altered in (forged_count, forged_tape, forged_order):
            with self.assertRaises(ValueError):
                Cells.restore(bytes(altered))
        self.assertEqual(c.snapshot(), genuine)

    def test_bad_checksum_length_magic_legacy_and_invalid_record_rejected(self):
        c = Cells()
        c.observe(identity(42), 1, 2, 3)
        good = c.snapshot()
        bad = bytearray(good)
        bad[0] ^= 1
        broken_checksum = bytearray(good)
        broken_checksum[-1] ^= 1
        illegal_origin = bytearray(good)
        illegal_origin[4] ^= 1
        illegal_origin[-32:] = hashlib.sha256(illegal_origin[:-32]).digest()
        illegal_retained = bytearray(good)
        j = Cells.HEADER_BYTES + Cells.LEARNED_BYTES + 35
        illegal_retained[j] = 2
        illegal_retained[-32:] = hashlib.sha256(
            illegal_retained[:-32]).digest()
        for data in (bytes(bad), good[:-1], good+b"!", bytes(broken_checksum),
                     bytes(illegal_origin), bytes(illegal_retained),
                     bytearray(good)):
            with self.subTest(shape=(type(data).__name__, len(data))):
                with self.assertRaises(ValueError):
                    Cells.restore(data)

    def test_source_budget_hard_and_saturating_counter_no_wrap(self):
        c = Cells()
        for i in range(Cells.MAX_EVENTS):
            c.observe(identity(10_000+i), 0, i % 4, i % 4)
        old = c.snapshot()
        self.assertEqual(len(old), Cells.MAX_CHECKPOINT_BYTES)
        with self.assertRaises(ValueError):
            c.observe(identity(99_999), 0, 2, 3)
        self.assertEqual(c.snapshot(), old)
        self.assertEqual(Cells.restore(old).snapshot(), old)
        # Local saturation negative only: do not serialize forged manual
        # data as authentic source evidence; the public source tape is source.
        throwaway = Cells()
        throwaway._counts[0][3][2] = 65535
        throwaway.observe(identity(77_777), 0, 3, 2)
        self.assertEqual(throwaway.counts(0, 3)[2], 65535)

    def test_unseen_action_abstains_and_conventional_dirichlet_is_explicit(self):
        c = Cells()
        c.observe(identity(8101), 0, 0, 0)
        c.observe(identity(8102), 0, 0, 1)
        c.observe(identity(8103), 0, 1, 0)
        self.assertIsNone(c.choose(0, 0))
        self.assertEqual(c.probability(0, 0, 0), (2, 6))
        self.assertEqual(c.probability(0, 1, 0), (2, 5))
        self.assertIsNone(c.probability(0, 2, 0))
        c.observe(identity(8104), 0, 2, 2)
        c.observe(identity(8105), 0, 3, 3)
        self.assertEqual(c.choose(0, 0), 1)
        self.assertEqual(c.probability(0, 3, 3), (2, 5))

    def test_original_pyc1_binary_learner_unchanged(self):
        c = PublicCausalCells()
        initial = c.snapshot()
        self.assertEqual(len(initial), 164)
        self.assertEqual(initial[:4], b"YPC1")
        c.observe(0, 0, 1)
        c.observe(0, 1, 0)
        self.assertEqual(c.choose(0), 0)
        old = c.snapshot()
        self.assertEqual(PublicCausalCells.restore(old).snapshot(), old)
        n = Cells.migrate(old)
        n.observe(identity(340), 0, 3, 2)
        self.assertEqual(c.snapshot(), old)
        self.assertEqual(n.original_binary_snapshot(), old)
        self.assertEqual(PublicCausalCells.restore(old).choose(0), 0)


if __name__ == "__main__":
    unittest.main()
