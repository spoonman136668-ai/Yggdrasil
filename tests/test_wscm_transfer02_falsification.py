"""Source-free falsification checks on illustrative WSCM-TRANSFER-02 fixtures."""
import unittest
import importlib.util
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "research/contrib/chatgpt/WSCM-TRANSFER-02/contract.py"
SPEC = importlib.util.spec_from_file_location("wscm02_falsification_contract", SOURCE)
CONTRACT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CONTRACT)
BITS = CONTRACT.BITS
FUNCTIONS = CONTRACT.FUNCTIONS
ID_TO_ROLE = CONTRACT.ID_TO_ROLE
PHASE_LAW = CONTRACT.PHASE_LAW
audit_static_contract = CONTRACT.audit_static_contract
canonical_law = CONTRACT.canonical_law
public_request = CONTRACT.public_request
validate_learner_request = CONTRACT.validate_learner_request


class WSCMTransfer02FalsificationTests(unittest.TestCase):
    def test_falsified_c_law_selection_cannot_pass_as_transfer(self):
        saved = PHASE_LAW["C_composition"]
        try:
            PHASE_LAW["C_composition"] = "A"
            with self.assertRaisesRegex(ValueError, "PHASE_LAW_CONTRACT"):
                audit_static_contract()
        finally:
            PHASE_LAW["C_composition"] = saved

    def test_falsified_b_law_selection_cannot_pass_as_regime_change(self):
        saved = PHASE_LAW["B_shift"]
        try:
            PHASE_LAW["B_shift"] = "A"
            with self.assertRaisesRegex(ValueError, "PHASE_LAW_CONTRACT"):
                audit_static_contract()
        finally:
            PHASE_LAW["B_shift"] = saved

    def test_all_public_requests_have_no_private_metadata(self):
        for phase, ids in ID_TO_ROLE.items():
            for external_id in ids:
                for state in BITS:
                    request = public_request(phase, state, external_id)
                    self.assertEqual(set(request), {"public_view", "external_action_id"})
                    self.assertEqual(request, validate_learner_request(request))

    def test_leaked_role_law_phase_mapping_or_future_outcome_rejected(self):
        request = public_request("C_composition", (1, 0), 5459)
        for field, private in (("phase", "C_composition"), ("role", 3), ("law", "C"),
                               ("id_to_role", {5459: 3}), ("future_outcome", 1)):
            with self.subTest(field=field):
                with self.assertRaisesRegex(ValueError, "LEARNER_REQUEST_LEAK_OR_INVALID"):
                    validate_learner_request({**request, field: private})

    def test_wrong_payload_shapes_and_int_aliases_rejected(self):
        request = public_request("A_train", (0, 1), 1301)
        for invalid in (None, [], {"public_view": [0, 1]},
                        {**request, "public_view": (0, 1)},
                        {**request, "public_view": [True, 0]},
                        {**request, "external_action_id": 1301.0},
                        {**request, "external_action_id": True}):
            with self.subTest(invalid=str(invalid)):
                with self.assertRaisesRegex(ValueError, "LEARNER_REQUEST_LEAK_OR_INVALID"):
                    validate_learner_request(invalid)
        for invalid_id in (1301.0, True, "1301", None):
            with self.subTest(id=invalid_id):
                with self.assertRaisesRegex(ValueError, "UNKNOWN_PUBLIC_ACTION"):
                    public_request("A_train", (0, 1), invalid_id)

    def test_nonbinary_function_is_not_valid_causal_law(self):
        prior = FUNCTIONS["C"]
        try:
            FUNCTIONS["C"] = (lambda p, q: 0.5, *prior[1:])
            with self.assertRaisesRegex(ValueError, "NONBINARY_CAUSAL_FUNCTION"):
                audit_static_contract()
        finally:
            FUNCTIONS["C"] = prior

    def test_renamed_a_is_not_unfamiliar_composition(self):
        prior = FUNCTIONS["C"]
        try:
            FUNCTIONS["C"] = tuple(reversed(FUNCTIONS["A"]))
            with self.assertRaisesRegex(ValueError, "LAWS_ISOMORPHIC"):
                audit_static_contract()
        finally:
            FUNCTIONS["C"] = prior
        self.assertNotEqual(canonical_law("A"), canonical_law("C"))


if __name__ == "__main__":
    unittest.main()
