"""Frozen source-free ambiguity/safety tests; zero protected world actions."""
import itertools
import unittest
import sys
from pathlib import Path

RESEARCH_DIR = Path(__file__).resolve().parents[1] / "research" / "contrib" / "chatgpt" / "WSCM-TRANSFER-02"
sys.path.insert(0, str(RESEARCH_DIR))

from unrestricted_safe_readout_dev import propose_unrestricted_safe_composition as safe
from composition_wire_dev import propose_two_step_composition as legacy

FIRST = (0, 1, 1, 0)
SECOND = (0, 0, 1, 1)


class NativeStub:
    def __init__(self, sigs):
        self.sigs = dict(sigs)
        self.lookups = 0

    def observed_external_fixture_value(self, state, action):
        self.lookups += 1
        signature = self.sigs.get(action)
        return None if signature is None else signature[2 * state[0] + state[1]]


def trace(source, start, second_signature=SECOND, middle=None):
    first = FIRST[2 * start[0] + start[1]]
    if middle is None:
        middle = (start[1], first)
    return {
        "source_id": f"{source:064x}", "public_view": list(start),
        "first_outcome": first, "second_public_view": list(middle),
        "second_outcome": second_signature[2 * middle[0] + middle[1]],
    }


class UnrestrictedSafeReadoutDev(unittest.TestCase):
    def setUp(self):
        self.native = NativeStub({1301: FIRST, 22007: SECOND})
        self.traces = (trace(1, (0, 1)), trace(2, (1, 0)))

    def call(self, native=None, rows=None, query=None):
        return safe(self.native if native is None else native, 1301, 22007,
                    self.traces if rows is None else rows,
                    [1, 1] if query is None else query)

    def test_nonconstant_does_not_promote_unseen_bit(self):
        self.assertEqual(legacy(self.native, 1301, 22007, self.traces, [1, 1])
                         ["predicted_next_bit"], 1)
        v = self.call()
        self.assertEqual((v["status"], v["reason"], v["predicted_next_bit"]),
                         ("ABSTAIN", "UNRESTRICTED_MAPPING_AMBIGUOUS", None))
        self.assertEqual(v["compatible_unrestricted_mapping_count"], 16)
        self.assertEqual(v["possible_next_bits"], [0, 1])
        self.assertFalse(v["robust_to_unrestricted_wiring"])

    def test_matched_set_valued_symbolic_control_exact(self):
        v = self.call()
        observed = {(0, 1), (1, 0)}
        states = ((0, 0), (0, 1), (1, 0), (1, 1))
        possible = set()
        matches = 0
        for row in itertools.product(states, repeat=4):
            if all(row[states.index(s)] == tuple(t["second_public_view"])
                   for s, t in ((tuple(t["public_view"]), t) for t in self.traces)):
                matches += 1
                middle = row[3]
                possible.add(SECOND[2 * middle[0] + middle[1]])
        self.assertEqual(matches, v["compatible_unrestricted_mapping_count"])
        self.assertEqual(sorted(possible), v["possible_next_bits"])
        self.assertNotIn((1, 1), observed)

    def test_constant_second_stage_conditional_invariant(self):
        constant = (0, 0, 0, 0)
        native = NativeStub({1301: FIRST, 22007: constant})
        rows = tuple(trace(i, start, constant) for i, start in
                     ((1, (0, 1)), (2, (1, 0))))
        v = self.call(native=native, rows=rows)
        self.assertEqual((v["status"], v["predicted_next_bit"],
                          v["possible_next_bits"]), ("INVARIANT", 0, [0]))
        self.assertTrue(v["robust_to_unrestricted_wiring"])
        self.assertEqual(v["reason"], "CONDITIONAL_CONSTANT_SECOND_STAGE_NOT_TRANSFER")

    def test_absent_source_and_action_permission_stay_false(self):
        for v in (self.call(), self.call(native=NativeStub({1301: FIRST}))):
            for flag in ("structural_chain_authenticated", "action_authorized",
                         "native_state_updated", "scientific_gain_verified",
                         "authenticated_structural_transition"):
                self.assertFalse(v[flag])
            self.assertEqual(v["source_mode"], "engineering_fixture_only")

    def test_non_grammar_witnesses_not_contradiction(self):
        rows = (trace(1, (0, 1), middle=(1, 1)),
                trace(2, (1, 0), middle=(1, 1)))
        self.assertEqual(legacy(self.native, 1301, 22007, rows, [1, 1])["reason"],
                         "NO_SUPPORTED_WIRING")
        v = self.call(rows=rows)
        self.assertEqual(v["status"], "ABSTAIN")
        self.assertEqual(v["reason"], "UNRESTRICTED_MAPPING_AMBIGUOUS")
        self.assertEqual(v["compatible_unrestricted_mapping_count"], 16)

    def test_conflicting_same_start_still_contradiction(self):
        rows = (trace(1, (0, 1)), trace(2, (0, 1), middle=(0, 0)))
        v = self.call(rows=rows)
        self.assertEqual((v["status"], v["reason"]),
                         ("CONTRADICTION", "CONFLICTING_STRUCTURAL_TRACES"))

    def test_missing_action_signature_abstains(self):
        self.assertEqual(self.call(native=NativeStub({1301: FIRST}))
                         ["reason"], "PRIMITIVE_NOT_FULLY_WITNESSED")

    def test_missing_or_one_trace_abstains(self):
        self.assertEqual(self.call(rows=())["reason"], "NO_STRUCTURAL_TRACES")
        self.assertEqual(self.call(rows=(self.traces[0],))["reason"],
                         "INSUFFICIENT_DISTINCT_STRUCTURAL_SUPPORT")

    def test_known_query_not_new_transfer(self):
        self.assertEqual(self.call(query=[0, 1])["reason"],
                         "EXACT_STRUCTURAL_TRACE_WITNESSED")

    def test_hidden_oracle_field_rejected(self):
        with self.assertRaisesRegex(ValueError, "WSCM_COMPOSE_TRACE_FIELDS"):
            self.call(rows=(self.traces[0] | {"law": "hidden"}, self.traces[1]))

    def test_repeated_cold_pure_readout_no_mutation(self):
        before = dict(self.native.sigs)
        self.assertEqual(self.call(), self.call())
        self.assertEqual(self.native.sigs, before)

    def test_invalid_action_and_boolean_input_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "WSCM_COMPOSE_ACTION"):
            safe(self.native, True, 22007, self.traces, [1, 1])
        with self.assertRaisesRegex(ValueError, "WSCM_COMPOSE_PUBLIC_VIEW"):
            self.call(query=[True, 0])


if __name__ == "__main__":
    unittest.main()
