"""Exact native evidence-component development checks, NOT NativeEpisodeExperience.

The adapter only maps NativeExternalActionIdentity's fully witnessed public
signature into the existing NativeEpisodeExperience readout method shape.
No source-authorized causal chain or protected scientific first use is claimed.
"""
import hashlib
import json
import unittest
import sys
from pathlib import Path

RESEARCH_DIR = Path(__file__).resolve().parents[1] / "research" / "contrib" / "chatgpt" / "WSCM-TRANSFER-02"
sys.path.insert(0, str(RESEARCH_DIR))


from composition_wire_dev import propose_two_step_composition
from yggdrasil.native_external_action_identity import (
    NativeExternalActionIdentity, RECEIPT_SCHEMA, SOURCE_MODE, STATES, _canonical,
)

FIRST = (0, 1, 1, 0)
SECOND = (0, 0, 1, 1)


def make_receipt(action, state, outcome, serial):
    payload = {"schema": RECEIPT_SCHEMA, "source_mode": SOURCE_MODE,
               "source_id": f"{serial:064x}", "public_view": list(state),
               "external_action_id": action, "outcome": outcome}
    raw = _canonical(payload)
    return raw, hashlib.sha256(raw).hexdigest()


def add(native, action, values, start=1, limit=4):
    for i, state in enumerate(STATES[:limit]):
        raw, pin = make_receipt(action, state, values[i], start + i)
        native = native.observe_public_receipt(
            {"public_view": list(state), "external_action_id": action}, raw, pin)
    return native


def trace(serial, state, wire="y_then_output"):
    x, y = state
    out = FIRST[2 * x + y]
    intermediate = {
        "output_then_x": (out, x), "output_then_y": (out, y),
        "x_then_output": (x, out), "y_then_output": (y, out),
    }[wire]
    return {"source_id": f"{serial:064x}", "public_view": list(state),
            "first_outcome": out, "second_public_view": list(intermediate),
            "second_outcome": SECOND[2 * intermediate[0] + intermediate[1]]}


class NativeComponentReadout:
    """Pass-through of *observed*, not inferred, real native evidence rows."""
    def __init__(self, native):
        self.native = native

    def observed_external_fixture_value(self, view, action):
        signature = self.native.observed_signature(action)
        return None if signature is None else signature[2 * view[0] + view[1]]


class ActualNativeEvidenceComposition(unittest.TestCase):
    def setUp(self):
        self.identity = add(NativeExternalActionIdentity(), 1301, FIRST)
        self.identity = add(self.identity, 22007, SECOND, 10)
        self.rows = (trace(100, (0, 1)), trace(101, (1, 0)))

    def call(self, identity=None, rows=None, query=None):
        native = self.identity if identity is None else identity
        return propose_two_step_composition(
            NativeComponentReadout(native), 1301, 22007,
            self.rows if rows is None else rows,
            [1, 1] if query is None else query)

    def test_genuine_native_receipts_two_action_composition(self):
        self.assertEqual(self.identity.observed_signature(1301), FIRST)
        self.assertEqual(self.identity.observed_signature(22007), SECOND)
        result = self.call()
        self.assertEqual((result["status"], result["compatible_wirings"],
                          result["predicted_next_bit"]),
                         ("HYPOTHESIS", ["y_then_output"], 1))
        self.assertFalse(result["structural_chain_authenticated"])
        self.assertFalse(result["action_authorized"])
        self.assertFalse(result["scientific_gain_verified"])

    def test_original_native_component_cold_restore_same_result(self):
        raw = self.identity.checkpoint()
        cold = NativeExternalActionIdentity.restore(
            raw, NativeExternalActionIdentity.sha256(raw))
        self.assertEqual(raw, cold.checkpoint())
        self.assertEqual(self.call(), self.call(cold))

    def test_native_component_underfilled_signature_must_abstain(self):
        underfilled = add(NativeExternalActionIdentity(), 1301, FIRST, 100)
        underfilled = add(underfilled, 22007, SECOND, 200, 3)
        self.assertEqual(self.call(underfilled)["reason"],
                         "PRIMITIVE_NOT_FULLY_WITNESSED")

    def test_no_transfer_to_new_external_action_id_without_observations(self):
        self.assertIsNone(self.identity.observed_signature(90017))
        partial = add(self.identity, 90017, SECOND, 300, 3)
        self.assertIsNone(partial.observed_signature(90017))
        raw, pin = make_receipt(90017, STATES[3], SECOND[3], 303)
        complete = partial.observe_public_receipt(
            {"public_view": list(STATES[3]), "external_action_id": 90017}, raw, pin)
        self.assertTrue(complete.observed_equivalent(22007, 90017))

    def test_conflicting_original_receipt_id_rejected(self):
        raw, pin = make_receipt(1301, STATES[0], 1, 1)
        with self.assertRaisesRegex(ValueError, "WSCM_SOURCE_REPLAY_CONFLICT"):
            self.identity.observe_public_receipt(
                {"public_view": list(STATES[0]), "external_action_id": 1301}, raw, pin)

    def test_forged_phase_and_role_rejected_by_original_ingress(self):
        raw, _ = make_receipt(1301, STATES[0], 0, 1000)
        for private in ("phase", "law", "role", "future_outcome"):
            data = json.loads(raw)
            data[private] = "hidden"
            forged = _canonical(data)
            with self.subTest(private=private), self.assertRaises(ValueError):
                self.identity.observe_public_receipt(
                    {"public_view": list(STATES[0]), "external_action_id": 1301},
                    forged, hashlib.sha256(forged).hexdigest())

    def test_unseen_context_exception_falsifies_unrestricted_transfer(self):
        # Alternative physical wiring agrees on both public training traces but
        # feeds (0, 0) instead of (1, 0) at the unseen query (1, 1).
        # It is outside the fixed four-wiring grammar, hence cannot be ruled out.
        result = self.call()
        self.assertEqual(result["predicted_next_bit"], 1)
        alternative_intermediate = (0, 0)
        alternative_outcome = SECOND[0]
        self.assertEqual(alternative_outcome, 0)
        self.assertNotEqual(result["predicted_next_bit"], alternative_outcome)
        self.assertEqual(result["status"], "HYPOTHESIS")
        self.assertFalse(result["structural_chain_authenticated"])

    def test_no_native_mutation_on_prediction_or_ambiguous_traces(self):
        original = self.identity.checkpoint()
        self.call()
        ambiguous = (trace(200, (0, 0)), trace(201, (0, 1)))
        self.assertEqual(self.call(rows=ambiguous)["reason"], "AMBIGUOUS_WIRING")
        self.assertEqual(original, self.identity.checkpoint())


if __name__ == "__main__":
    unittest.main()
