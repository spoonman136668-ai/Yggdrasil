"""Pure contract tests; original-native integration is a separate exact-SHA gate."""
import unittest
from guard import unfamiliar_family_readout, SCHEMA

EPISODE = "a" * 64


class DevEvidence:
    """Stub with the same query interfaces; not an original native implementation."""
    def __init__(self, *, historical=None, role_status="ENTAILED",
                 role_survivors=24, delta_status="HYPOTHESIS", delta_support=1):
        self.historical = historical
        self.role_status = role_status
        self.role_survivors = role_survivors
        self.delta_status = delta_status
        self.delta_support = delta_support
        self.reads = []

    def _validate(self, state, action, episode_id):
        if type(state) is not list or len(state) != 2 or not all(type(x) is int and 0 <= x <= 8 for x in state):
            raise ValueError("GRID5_STATE")
        if type(action) is not int or not 0 <= action < 5:
            raise ValueError("GRID5_ACTION")
        if episode_id != EPISODE:
            raise ValueError("GRID5_EPISODE_PIN")
        self.reads.append((tuple(state), action, episode_id))

    def public_forecast(self, state, action, *, episode_id):
        self._validate(state, action, episode_id)
        return self.historical

    def public_role_forecast(self, state, action, *, episode_id):
        self._validate(state, action, episode_id)
        return {"status": self.role_status, "surviving_permutations": self.role_survivors,
                "predicted_next_state": [2, 0] if self.role_status == "ENTAILED" else None}

    def public_learned_delta_forecast(self, state, action, *, episode_id):
        self._validate(state, action, episode_id)
        return {"status": self.delta_status, "support": self.delta_support,
                "predicted_next_state": [4, 2] if self.delta_status == "HYPOTHESIS" else None}


class EpistemicGuardContractTests(unittest.TestCase):
    def test_fixed_family_entailment_never_becomes_actionable(self):
        model = DevEvidence(role_status="ENTAILED", role_survivors=24)
        out = unfamiliar_family_readout(model, [1, 0], 0, episode_id=EPISODE)
        self.assertEqual(out["status"], "ABSTAIN_UNVERIFIED_FAMILY")
        self.assertEqual(out["schema"], SCHEMA)
        self.assertEqual(out["role_family_status"], "ENTAILED")
        self.assertEqual(out["role_survivors"], 24)
        self.assertIsNone(out["actionable_next_state"])
        self.assertFalse(out["action_admissible"])
        self.assertFalse(out["family_authenticated"])
        self.assertNotIn("conditional_next_state", out)
        self.assertEqual(len(model.reads), 3)

    def test_delta_provisional_forecast_not_promoted(self):
        out = unfamiliar_family_readout(DevEvidence(), [3, 2], 0, episode_id=EPISODE)
        self.assertEqual(out["delta_family_status"], "HYPOTHESIS")
        self.assertEqual(out["delta_support"], 1)
        self.assertIsNone(out["actionable_next_state"])
        self.assertNotIn("predicted_next_state", out)

    def test_historical_witness_kept_distinct_from_future_prediction(self):
        out = unfamiliar_family_readout(DevEvidence(historical=[0, 0]), [1, 0], 0, episode_id=EPISODE)
        self.assertEqual(out["historical_witness_next_state"], [0, 0])
        self.assertIsNone(out["actionable_next_state"])
        self.assertFalse(out["action_admissible"])

    def test_contradictory_model_families_still_abstain(self):
        out = unfamiliar_family_readout(DevEvidence(role_status="CONTRADICTION",
                            role_survivors=0, delta_status="CONTRADICTION", delta_support=2),
                             [1, 0], 0, episode_id=EPISODE)
        self.assertEqual(out["role_family_status"], "CONTRADICTION")
        self.assertEqual(out["delta_family_status"], "CONTRADICTION")
        self.assertIsNone(out["actionable_next_state"])

    def test_invalid_fields_fail_closed_through_native_contract(self):
        for state, action, ep in (([9, 0], 0, EPISODE), ([1, 0], 5, EPISODE),
                                  ([1, 0], True, EPISODE), ([1, 0], 0, "b" * 64)):
            with self.subTest(state=state, action=action, ep=ep):
                with self.assertRaises(ValueError):
                    unfamiliar_family_readout(DevEvidence(), state, action, episode_id=ep)

    def test_source_model_not_mutated(self):
        m = DevEvidence(historical=[0, 0])
        baseline = (m.historical[:], m.role_status, m.delta_status)
        one = unfamiliar_family_readout(m, [1, 0], 0, episode_id=EPISODE)
        two = unfamiliar_family_readout(m, [1, 0], 0, episode_id=EPISODE)
        self.assertEqual(one, two)
        self.assertEqual((m.historical, m.role_status, m.delta_status), baseline)


if __name__ == "__main__":
    unittest.main()
