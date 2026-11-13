"""HC03 source-only engineering, no protected science or owner execution."""
import json
import unittest

from model import (
    CausalProgramSociety, MAX_CHECKPOINT_BYTES,
    check_state, parity_context,
)
from eval_dev import EvaluatorOnlyWorld, one_world


class HypothesisCellTests(unittest.TestCase):
    def test_public_action_consequence_program_infers_new_state(self):
        m = CausalProgramSociety()
        source = EvaluatorOnlyWorld(12101)
        first = 0
        m.observe(first, 2, source.step(first, 2))
        self.assertEqual(m.predict(15, 2), source.step(15, 2))
        self.assertIsNone(m.predict(15, 1))
        self.assertEqual(m.logical_rule_bits, 16)

    def test_no_regime_label_but_reactivates_old_program(self):
        world = EvaluatorOnlyWorld(12102)
        m = CausalProgramSociety()
        state = 5
        for phase in (0, 1, 2):
            prev = state
            state = world.step(state, 0, phase)
            m.observe(prev, 0, state)
        self.assertEqual(m.splits, 1)
        self.assertEqual(m.reactivations, 1)
        self.assertEqual(m.active, 0)
        self.assertEqual(m.predict(7, 0), world.step(7, 0, 0))

    def test_reactivation_ablation_destroys_old_program(self):
        world = EvaluatorOnlyWorld(12102)
        m = CausalProgramSociety(reactivate=False)
        state = 5
        for phase in (0, 1, 2):
            prev = state
            state = world.step(state, 0, phase)
            m.observe(prev, 0, state)
        self.assertEqual(m.reactivations, 0)
        self.assertEqual(m.active, 1)
        self.assertEqual(m.banks[1][1], None)

    def test_continuous_source_actions_and_zero_reset(self):
        r = one_world(12101)
        self.assertEqual(r["source_actions"], 25)
        self.assertEqual(r["bank_count"], 2)
        self.assertEqual(r["reactivations"], 1)
        self.assertEqual(r["candidate"]["correct"], 64)
        self.assertEqual(r["candidate"]["wrong_confident"], 0)
        self.assertEqual(r["single_reset"]["correct"], 16)
        self.assertEqual(r["labelled_upper_bound"]["correct"], 64)
        self.assertTrue(r["cold_parity"])

    def test_incompatible_public_delta_is_atomic(self):
        m = CausalProgramSociety()
        baseline = m.snapshot()
        for bad in [(0, 0, 2), (0, 4, 0), (-1, 0, 0),
                    (False, 0, 0), (0, True, 0), (0, 0, 16)]:
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    m.observe(*bad)
                self.assertEqual(m.snapshot(), baseline)
        with self.assertRaises(TypeError):
            m.observe(0, 0, 0, hidden_rule="oracle")

    def test_bank_capacity_fail_closed_when_all_known_incompatible(self):
        m = CausalProgramSociety()
        # Learn a0 sign=0; contradict a1 to create bank 1.
        m.observe(0, 0, 0)
        m.observe(0, 1, 0)
        m.observe(0, 1, 2)
        self.assertEqual(len(m.banks), 2)
        # Fill a0 in bank 1 with sign=0, then present sign=1.
        m.observe(0, 0, 0)
        old = [row[:] for row in m.banks]
        assert m.banks[0][0] == m.banks[1][0] == 0
        self.assertFalse(m.observe(0, 0, 1))
        self.assertEqual(m.banks, old)
        self.assertEqual(m.unresolved, 1)

    def test_cross_cold_restore_parity_and_byte_budget(self):
        world = EvaluatorOnlyWorld(12103)
        m = CausalProgramSociety()
        s = 9
        for t in range(25):
            p = t // 16 if t < 24 else 2
            a = t % 4
            successor = world.step(s, a, p)
            m.observe(s, a, successor)
            s = successor
        raw = m.snapshot()
        self.assertLessEqual(len(raw), MAX_CHECKPOINT_BYTES)
        clone = CausalProgramSociety.restore(raw)
        self.assertEqual(clone.snapshot(), raw)
        for state in range(16):
            for a in range(4):
                self.assertEqual(clone.predict(state, a), m.predict(state, a))

    def test_snapshot_corruption_bad_shapes_and_oversize_rejected(self):
        m = CausalProgramSociety()
        cp = m.snapshot()
        edited = bytearray(cp)
        edited[len(cp) // 2] ^= 1
        for bad in (bytes(edited), cp[:-4], cp+b"!", bytearray(cp),
                    b"X"*1025):
            with self.subTest(length=len(bad), typ=type(bad)):
                with self.assertRaises(ValueError):
                    CausalProgramSociety.restore(bad)
        tampered = json.loads(cp)
        tampered["payload"]["bank_limit"] = 99
        with self.assertRaises(ValueError):
            CausalProgramSociety.restore(
                json.dumps(tampered).encode("utf-8"))

    def test_memory_budget_and_strict_input_types(self):
        for invalid in (-1, 16, 3.4, True, "1", None):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    check_state(invalid)
        for invalid_limit in (0, 3, True, 1.5):
            with self.subTest(limit=invalid_limit):
                with self.assertRaises(ValueError):
                    CausalProgramSociety(bank_limit=invalid_limit)

    def test_out_of_family_is_reported_not_reclassified(self):
        r = one_world(12109, negative=True)
        self.assertEqual(r["source_actions"], 16)
        self.assertEqual(r["family"], "out_of_family")
        self.assertEqual(sum(r["candidate"][k] for k in
                             ("correct", "wrong_confident", "abstained")), 64)


if __name__ == "__main__":
    unittest.main()
