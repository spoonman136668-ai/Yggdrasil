"""FKP-18 source-safe capacity and microfeedback negative controls.

No protected original FKP17 cohort, no private law generator, no acceptance.
"""
from __future__ import annotations

from collections import namedtuple
from hashlib import sha256
import json
import unittest

import source_safe_witness as witness
from temporal_trace import SparseTemporalTrace, PublicStep, MAX_LOGICAL_BYTES


def run_case(case, *, context=True, order=True, budget=512):
    model = SparseTemporalTrace(context_forks=context,
                                temporal_order=order,slot_budget=budget)
    responses = []
    for index, row in enumerate(case):
        responses.append(model.observe_public(row, event_id=index))
    return model, responses


class IndependentExactPublicConditionalReference:
    """A separately written exact lookup, deliberately stronger than marginal."""

    def __init__(self):
        self._public = {}

    def observe_public(self, row):
        if tuple(row._fields) != PublicStep._fields:
            raise ValueError("FKP18_REFERENCE_ONLY_PUBLIC")
        for target in range(8):
            diff = (row.after[target] - row.before[target]) % 16
            delta = diff if diff <= 7 else diff - 16
            key = (row.action, target, row.before[target])
            self._public.setdefault(key, set()).add(delta)

    def predict_delta(self, state, action, target):
        outcomes = self._public.get((action, target, state[target]), set())
        return next(iter(outcomes)) if len(outcomes) == 1 else None


class TemporalEvidenceTests(unittest.TestCase):
    def test_frozen_two_step_witnesses_are_physical_public_actions(self):
        for name, steps in witness.safe_fixed_witnesses().items():
            with self.subTest(case=name):
                self.assertEqual(len(steps), 2)
                self.assertEqual(steps[0].after, steps[1].before)
                self.assertEqual(steps[0].before, steps[1].after)
                self.assertEqual(steps[0].history, ())
                self.assertEqual(steps[1].history[-1].after, steps[1].before)
                self.assertTrue(all(step._fields == PublicStep._fields for step in steps))
                self.assertEqual(sum(step.reward for step in steps), 0.0)
        self.assertEqual([r.action for r in witness.conditional_cycle("A")], [3, 3])
        self.assertEqual([r.action for r in witness.conditional_cycle("B")], [3, 3])
        self.assertEqual([r.action for r in witness.temporal_cycle("AB")], [2, 5])
        self.assertEqual([r.action for r in witness.temporal_cycle("BA")], [5, 2])

    def test_actual_outcome_contradiction_allocates_sparse_fork(self):
        model, feedback = run_case(witness.conditional_cycle("A"))
        self.assertEqual(feedback[0], ())
        self.assertIn(("CONTEXT_FORK", 3, 3), feedback[1])
        self.assertEqual(model.discovered_conditional_forks, 1)
        self.assertEqual(model.public_observations, 2)
        self.assertLess(model.learned_relation_slots, 512)
        self.assertLess(model.logical_learned_bytes, MAX_LOGICAL_BYTES)
        self.assertNotEqual(model.semantic_receipt(), "0" * 64)

    def test_same_present_public_state_requires_opposite_public_effect(self):
        a, _ = run_case(witness.conditional_cycle("A"))
        b, _ = run_case(witness.conditional_cycle("B"))
        self.assertNotEqual(a.semantic_receipt(), b.semantic_receipt())
        self.assertEqual(a.predict_delta(witness.STATE, 3, 3), 1)
        self.assertEqual(b.predict_delta(witness.STATE, 3, 3), -1)
        self.assertIsNone(a.predict_delta(witness.STATE, 7, 3))
        self.assertEqual(witness.conditional_cycle("A")[0].reward, +0.125)
        self.assertEqual(witness.conditional_cycle("B")[0].reward, -0.125)

    def test_unconditioned_matched_observation_ablation_collapses(self):
        a, _ = run_case(witness.conditional_cycle("A"), context=False, order=False)
        b, _ = run_case(witness.conditional_cycle("B"), context=False, order=False)
        self.assertEqual(a.semantic_receipt(), b.semantic_receipt())
        self.assertEqual(a.public_observations, b.public_observations)
        self.assertIsNone(a.predict_delta(witness.STATE, 3, 3))
        self.assertIsNone(b.predict_delta(witness.STATE, 3, 3))
        self.assertEqual(a.discovered_conditional_forks, 0)

    def test_order_trace_distinguishes_reversed_real_events(self):
        ab, _ = run_case(witness.temporal_cycle("AB"))
        ba, _ = run_case(witness.temporal_cycle("BA"))
        self.assertNotEqual(ab.semantic_receipt(), ba.semantic_receipt())
        self.assertNotEqual(ab.observed_order_trace(), ba.observed_order_trace())
        self.assertEqual(ab.discovered_conditional_forks, 0)
        self.assertEqual(ba.discovered_conditional_forks, 0)
        self.assertEqual(ab.public_observations, ba.public_observations)
        # An observed order trace is not a proof of delayed causal effect.
        self.assertIsNone(ab.predict_delta(witness.STATE, 3, 3))

    def test_no_temporal_order_ablation_erases_order(self):
        ab, _ = run_case(witness.temporal_cycle("AB"), order=False)
        ba, _ = run_case(witness.temporal_cycle("BA"), order=False)
        self.assertEqual(ab.semantic_receipt(), ba.semantic_receipt())
        self.assertEqual(ab.observed_order_trace(), ())
        self.assertEqual(ba.observed_order_trace(), ())

    def test_independent_exact_conditional_reference_ties_on_toy(self):
        observations = witness.safe_fixed_witnesses()
        for name, expected in (("conditional_A", 1), ("conditional_B", -1)):
            reference = IndependentExactPublicConditionalReference()
            for row in observations[name]:
                reference.observe_public(row)
            self.assertEqual(reference.predict_delta(witness.STATE, 3, 3), expected)
        # This is *representation capacity*, not unique superiority
        # over a competent traditional exact-lookup learner.

    def test_bitwise_cold_identity_after_public_two_action_learning(self):
        for name, rows in witness.safe_fixed_witnesses().items():
            with self.subTest(case=name):
                model, _ = run_case(rows)
                before = model.semantic_receipt()
                raw = model.checkpoint()
                fresh = SparseTemporalTrace.restore(raw)
                self.assertEqual(fresh.semantic_receipt(), before)
                self.assertEqual(fresh.checkpoint(), raw)
                self.assertEqual(fresh.public_observations, 2)
                self.assertLess(len(raw), MAX_LOGICAL_BYTES)
                self.assertEqual(fresh.predict_delta(witness.STATE, 3, 3),
                                 model.predict_delta(witness.STATE, 3, 3))

    def test_changed_future_or_private_field_refused_atomically(self):
        model = SparseTemporalTrace()
        row = witness.conditional_cycle("A")[0]
        bad_schema = namedtuple("PrivateStep", (*row._fields, "oracle"))
        bad = bad_schema(*row, (1,) * 8)
        for tamper in (bad, tuple(row), row._replace(reward=float("nan")),
                       row._replace(before=(True,) * 8), row._replace(after=(16,) * 8),
                       row._replace(action=8), row._replace(done=0)):
            before = model.semantic_receipt()
            with self.assertRaises(ValueError):
                model.observe_public(tamper, event_id=0)
            self.assertEqual(model.semantic_receipt(), before)
        self.assertEqual(model.public_observations, 0)

    def test_duplicate_misordered_or_forged_history_refused(self):
        original = witness.conditional_cycle("A")
        m = SparseTemporalTrace()
        m.observe_public(original[0], event_id=0)
        before = m.semantic_receipt()
        for row, idx in ((original[0], 0), (original[1], 0),
                         (original[1]._replace(history=()), 1),
                         (original[1]._replace(before=(8,) * 8), 1)):
            with self.assertRaises(ValueError):
                m.observe_public(row, event_id=idx)
            self.assertEqual(m.semantic_receipt(), before)
        m.observe_public(original[1], event_id=1)
        self.assertEqual(m.public_observations, 2)

    def test_allocation_limit_failure_is_atomic(self):
        a = witness.conditional_cycle("A")
        memory = SparseTemporalTrace(slot_budget=1)
        memory.observe_public(a[0], event_id=0)
        before = memory.semantic_receipt()
        with self.assertRaisesRegex(ValueError, "CAPACITY"):
            memory.observe_public(a[1], event_id=1)
        self.assertEqual(memory.semantic_receipt(), before)
        self.assertEqual(memory.public_observations, 1)

    def test_checkpoint_tamper_fails_and_no_pickle(self):
        m, _ = run_case(witness.conditional_cycle("A"))
        raw = m.checkpoint()
        corrupted = raw.replace(b'"sha256":', b'"sha256":"bad","ignored":')
        with self.assertRaises(ValueError):
            SparseTemporalTrace.restore(corrupted)
        data = json.loads(raw)
        data["body"]["count"] = 3
        with self.assertRaisesRegex(ValueError, "CHECKPOINT_SHA_MISMATCH"):
            SparseTemporalTrace.restore(json.dumps(data).encode("ascii"))
        with self.assertRaises(ValueError):
            SparseTemporalTrace.restore(b"\x80\x04pickle")
        self.assertEqual(m.public_observations, 2)

    def test_no_source_private_imports_or_accepted_native_changes(self):
        from pathlib import Path
        import ast
        code = Path(__import__("temporal_trace").__file__).read_text("utf-8")
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.assertNotIn(alias.name,
                                     ("source_safe_witness","source_fixture","torch",
                                      "tensorflow","yggdrasil"))
            if isinstance(node, ast.ImportFrom):
                self.assertNotIn(node.module,
                                 ("source_safe_witness","source_fixture","yggdrasil"))
        self.assertNotIn("allow_dev=True", code)
        self.assertNotIn("978500", code)
        self.assertNotIn("978600", code)


if __name__ == "__main__":
    unittest.main()
