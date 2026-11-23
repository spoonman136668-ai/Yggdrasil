"""Offline unit gates for WSCM provisional composition; no protected worlds."""
import unittest
import sys
from pathlib import Path

RESEARCH_DIR = Path(__file__).resolve().parents[1] / "research" / "contrib" / "chatgpt" / "WSCM-TRANSFER-02"
sys.path.insert(0, str(RESEARCH_DIR))

from composition_wire_dev import propose_two_step_composition as propose, STATES

FIRST = (0, 1, 1, 0)  # XOR, existing fully witnessed primitive
SECOND = (0, 0, 1, 1)  # first-coordinate, independently witnessed primitive


class NativeReadoutStub:
    """Only the exact public interface of NativeEpisodeExperience is used."""
    def __init__(self, signatures):
        self.signatures = dict(signatures)
        self.reads = 0

    def observed_external_fixture_value(self, view, action):
        self.reads += 1
        values = self.signatures.get(action)
        return None if values is None else values[2 * view[0] + view[1]]


def trace(source, start, wire="y_then_output"):
    x, y = start
    z = FIRST[2*x+y]
    middle = {"output_then_x": (z, x), "output_then_y": (z, y),
              "x_then_output": (x, z), "y_then_output": (y, z)}[wire]
    return {"source_id": f"{source:064x}", "public_view": list(start),
            "first_outcome": z, "second_public_view": list(middle),
            "second_outcome": SECOND[2*middle[0]+middle[1]]}


class CompositionWireDev(unittest.TestCase):
    def setUp(self):
        self.native = NativeReadoutStub({1301: FIRST, 22007: SECOND})
        self.rows = (trace(1, (0, 1)), trace(2, (1, 0)))

    def call(self, rows=None, query=None, native=None):
        return propose(self.native if native is None else native, 1301, 22007,
                       self.rows if rows is None else rows,
                       [1, 1] if query is None else query)

    def test_two_public_traces_identify_one_wire_and_predict_new_composition(self):
        v = self.call()
        self.assertEqual((v["status"], v["compatible_wirings"],
                          v["predicted_next_bit"]),
                         ("HYPOTHESIS", ["y_then_output"], 1))
        self.assertEqual(v["structural_witnesses"], 2)
        for field in ("structural_chain_authenticated", "action_authorized",
                      "native_state_updated", "scientific_gain_verified"):
            self.assertFalse(v[field])
        # Matched conventional symbolic fixed-grammar control: exact parity.
        first = FIRST[3]
        conventional = SECOND[2*1 + first]
        self.assertEqual(v["predicted_next_bit"], conventional)

    def test_no_structural_witnesses_abstains(self):
        self.assertEqual(self.call(())["reason"], "NO_STRUCTURAL_TRACES")

    def test_one_distinct_witness_abstains(self):
        self.assertEqual(self.call((self.rows[0],))["status"], "ABSTAIN")
        self.assertEqual(self.call((self.rows[0], self.rows[0] | {"source_id": "f"*64}))["reason"],
                         "INSUFFICIENT_DISTINCT_STRUCTURAL_SUPPORT")

    def test_ambiguous_wiring_abstains(self):
        rows = (trace(1, (0, 0)), trace(2, (0, 1)))
        self.assertEqual(self.call(rows)["reason"], "AMBIGUOUS_WIRING")

    def test_inconsistent_structural_trace_rejected(self):
        rows = (trace(1, (0, 1)), trace(2, (1, 0), "output_then_x"))
        self.assertEqual(self.call(rows)["reason"], "NO_SUPPORTED_WIRING")

    def test_conflicting_repeated_start_rejected(self):
        row = trace(1, (0, 1))
        different = trace(2, (0, 1), "x_then_output")
        self.assertEqual(self.call((row, different))["reason"], "CONFLICTING_STRUCTURAL_TRACES")

    def test_missing_primitive_signature_abstains(self):
        stub = NativeReadoutStub({1301: FIRST})
        self.assertEqual(self.call(native=stub)["reason"], "PRIMITIVE_NOT_FULLY_WITNESSED")

    def test_exact_witness_query_does_not_claim_generalization(self):
        self.assertEqual(self.call(query=[0, 1])["reason"], "EXACT_STRUCTURAL_TRACE_WITNESSED")

    def test_primitive_trace_mismatch_rejected(self):
        row = self.rows[0] | {"first_outcome": 0}
        with self.assertRaisesRegex(ValueError, "WSCM_COMPOSE_PRIMITIVE_MISMATCH"):
            self.call((row, self.rows[1]))

    def test_harness_private_metadata_rejected(self):
        for key in ("law", "role", "phase", "future_outcome", "id_to_role"):
            with self.subTest(key=key):
                with self.assertRaisesRegex(ValueError, "WSCM_COMPOSE_TRACE_FIELDS"):
                    self.call((self.rows[0] | {key: "oracle"}, self.rows[1]))

    def test_aliases_and_invalid_receipt_refused(self):
        with self.assertRaisesRegex(ValueError, "WSCM_COMPOSE_ACTION"):
            propose(self.native, True, 22007, self.rows, [1, 1])
        with self.assertRaisesRegex(ValueError, "WSCM_COMPOSE_PUBLIC_VIEW"):
            self.call(query=[True, 0])
        with self.assertRaisesRegex(ValueError, "WSCM_COMPOSE_TRACE_ID"):
            self.call((self.rows[0], self.rows[0]))
        with self.assertRaisesRegex(ValueError, "WSCM_COMPOSE_TRACE_CAPACITY"):
            self.call(self.rows * 9)

    def test_determinism_and_no_state_mutation(self):
        before = dict(self.native.signatures)
        self.assertEqual(self.call(), self.call())
        self.assertEqual(before, self.native.signatures)
        self.assertEqual(tuple(STATES), ((0, 0), (0, 1), (1, 0), (1, 1)))

if __name__ == "__main__":
    unittest.main()
