"""SFI-02 controls use synthetic PUBLIC observation records only in unit tests.

Do not run actual SFI-01 source outcomes before candidate/code test source seal.
"""
import ast
from collections import namedtuple
from pathlib import Path
import unittest

import microfeedback as m

Old = namedtuple("Old", m.OLD_FIELDS)
Step = namedtuple("Step", m.STEP_FIELDS)
STATE = (0, 0, 8, 8, 8, 8, 8, 8)


def row(reward=-.25):
    history = (Old(STATE, 0, 0., STATE, False),
               Old(STATE, 1, 0., STATE, False),
               Old(STATE, 2, 0., STATE, False))
    return Step(STATE, 3, STATE, reward, False, history)


class SourceBlindMicrofeedbackTests(unittest.TestCase):
    def test_generic_grammar_is_bounded_and_nontrivial(self):
        self.assertEqual(m.PROGRAMS, 4096)
        self.assertEqual(len(set(m.CATALOG)), 4096)
        self.assertLess(m.DirectMicrofeedback.raw_parameter_bytes, m.CAPACITY)
        self.assertLess(m.ConventionalExactSymbolic.raw_parameter_bytes, m.CAPACITY)
        self.assertEqual(m._op(3, 3, 5), 6)
        self.assertEqual(m._op(2, 3, 5), 2)

    def test_two_independent_interpreters_agree_for_all_programs(self):
        for i, program in enumerate(m.CATALOG):
            p, q, c = (i * 3) & 7, (i * 5 + 1) & 7, i % 2
            self.assertEqual(m.execute_program(program, p, q, c),
                             m.ConventionalExactSymbolic._symbolic_eval(program, p, q, c))

    def test_real_delayed_earned_feedback_reduces_candidates(self):
        native, symbolic = m.DirectMicrofeedback(), m.ConventionalExactSymbolic()
        assert native.hypothesis_count == 4096
        negative = row()
        for agent in (native, symbolic):
            agent.observe_public(negative)
        self.assertEqual(native.hypothesis_count, symbolic.hypothesis_count)
        self.assertLess(native.hypothesis_count, 4096)
        self.assertGreater(native.hypothesis_count, 0)
        self.assertEqual(native.choose_public(STATE, negative.history),
                         symbolic.choose_public(STATE, negative.history))

    def test_no_oracle_or_private_input_and_atomic_receipt(self):
        native = m.DirectMicrofeedback()
        good = row()
        Extended = namedtuple("Extended", m.STEP_FIELDS + ("oracle_future_returns",))
        bad = Extended(*good, [0] * 8)
        saved = native.state_receipt()
        for case in (bad, good._replace(action=True), good._replace(reward=float("nan")),
                     good._replace(history=(good,)), good._replace(before=(0,) * 7)):
            with self.subTest(case=str(case)[:50]):
                with self.assertRaises(ValueError):
                    native.observe_public(case)
                self.assertEqual(native.state_receipt(), saved)

    def test_contradiction_rejected_without_partial_mutation(self):
        model = m.DirectMicrofeedback()
        positive = row(.25)
        # Force only a candidate that predicts the wrong credited action.
        credit, _ = m.public_row(positive)
        mask = bytearray(m.PROGRAMS)
        for i, program in enumerate(m.CATALOG):
            if m.execute_program(program, credit[0], credit[1], credit[2]) != credit[3]:
                mask[i] = 1
                break
        model.enabled = mask
        saved = model.state_receipt()
        with self.assertRaises(ValueError):
            model.observe_public(positive)
        self.assertEqual(saved, model.state_receipt())

    def test_frozen_max_observations_and_cold_replay(self):
        one, two = m.DirectMicrofeedback(), m.DirectMicrofeedback()
        for _ in range(m.MAX_OBSERVATIONS):
            one.observe_public(row())
            two.observe_public(row())
        self.assertEqual(one.state_receipt(), two.state_receipt())
        self.assertEqual(one.choose_public(STATE, row().history),
                         two.choose_public(STATE, row().history))
        previous = one.state_receipt()
        with self.assertRaises(ValueError):
            one.observe_public(row())
        self.assertEqual(previous, one.state_receipt())

    def test_model_source_cannot_import_generator_or_private_labels(self):
        source = Path(m.__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported.add(node.module)
        self.assertFalse(any("source_audit" in name for name in imported if name))
        self.assertNotIn("_target", source)
        self.assertNotIn("_SourceWorld", source)
        self.assertNotIn("_choose_oracle", source)
        self.assertNotIn("FAMILIES", source)

    def test_all_public_variants_select_preoutcome_without_mutation(self):
        for arm in (m.DirectMicrofeedback(), m.ConventionalExactSymbolic(),
                    m.ExactContextTable(), m.WrongCredit()):
            before = arm.received
            first = arm.choose_public(STATE, ())
            self.assertEqual(first, arm.choose_public(STATE, ()))
            self.assertIn(first, range(8))
            self.assertEqual(before, arm.received)
            arm.observe_public(row())
            self.assertEqual(arm.received, 1)


if __name__ == "__main__":
    unittest.main()
