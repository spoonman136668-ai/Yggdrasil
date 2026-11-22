"""Source-free contract negatives. No scoring seeds or protected actions."""
import importlib.util
from pathlib import Path
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "research/contrib/chatgpt/WSCM-TRANSFER-02/contract.py"
SPEC = importlib.util.spec_from_file_location("wscm02_contract", SOURCE)
CONTRACT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CONTRACT)


class StaticContractTests(unittest.TestCase):
    def test_illustrative_laws_are_not_identity_permutations(self):
        self.assertTrue(CONTRACT.audit_static_contract())
        self.assertEqual(len({CONTRACT.canonical_law(law) for law in ("A", "B", "C")}), 3)

    def test_four_roles_have_distinct_truth_functions(self):
        for law in ("A", "B", "C"):
            self.assertEqual(len({CONTRACT.signature(law, role) for role in CONTRACT.ROLES}), 4)

    def test_return_is_same_function_under_changed_public_ids(self):
        self.assertEqual(CONTRACT.PHASE_LAW["A_train"], CONTRACT.PHASE_LAW["A_return"])
        self.assertFalse(set(CONTRACT.ID_TO_ROLE["A_train"]) & set(CONTRACT.ID_TO_ROLE["A_return"]))
        for role in CONTRACT.ROLES:
            a = next(k for k, v in CONTRACT.ID_TO_ROLE["A_train"].items() if v == role)
            b = next(k for k, v in CONTRACT.ID_TO_ROLE["A_return"].items() if v == role)
            for state in CONTRACT.BITS:
                self.assertEqual(CONTRACT.engineering_only_outcome("A_train", state, a),
                                 CONTRACT.engineering_only_outcome("A_return", state, b))

    def test_model_visible_request_leaks_no_truth_role_or_phase(self):
        self.assertEqual(CONTRACT.public_request("C_composition", (1, 0), 5459),
                         {"public_view": [1, 0], "external_action_id": 5459})

    def test_invalid_or_forged_actions_and_states_refused(self):
        for phase, state, id_ in (("Z", (0, 0), 1301), ("A_train", (0, 0), 1029),
                                  ("A_train", (0, 2), 1301), ("A_train", [0, 1], 1301),
                                  ("A_train", (False, 0), 1301)):
            with self.subTest(phase=phase, state=state, id=id_):
                with self.assertRaises(ValueError):
                    CONTRACT.public_request(phase, state, id_)

    def test_one_observation_cannot_disambiguate_all_four_roles(self):
        for law in ("A", "B", "C"):
            for state in CONTRACT.BITS:
                outcomes = [CONTRACT.FUNCTIONS[law][r](*state) for r in CONTRACT.ROLES]
                self.assertLessEqual(len(set(outcomes)), 2)
                self.assertGreater(len(outcomes), len(set(outcomes)))

    def test_alias_or_false_novelty_guard_works(self):
        original = CONTRACT.FUNCTIONS["A"]
        try:
            CONTRACT.FUNCTIONS["A_PERMUTED"] = tuple(reversed(original))
            with self.assertRaisesRegex(ValueError, "LAWS_ISOMORPHIC"):
                CONTRACT.audit_static_contract()
        finally:
            del CONTRACT.FUNCTIONS["A_PERMUTED"]


if __name__ == "__main__":
    unittest.main()
