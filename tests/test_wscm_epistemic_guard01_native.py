"""Native integration negative controls for the optional WSCM epistemic guard.

This file is intended to run from the Yggdrasil repository at the candidate SHA.
It does not import/step an original environment or authorize new source first use.
"""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import hashlib
import unittest

from yggdrasil.native_grid5_evidence import NativeGrid5Evidence
from test_native_grid5_evidence_dev import receipt

SOURCE = (Path(__file__).resolve().parents[1] /
          "research/contrib/chatgpt/WSCM-EPISTEMIC-GUARD-01/guard.py")
SPEC = spec_from_file_location("wscm_epistemic_guard01", SOURCE)
GUARD = module_from_spec(SPEC)
SPEC.loader.exec_module(GUARD)

EPISODE = "a" * 64


class OriginalNativeGuardTests(unittest.TestCase):
    def test_fixed_family_unseen_confidence_is_not_action_authority(self):
        evidence = NativeGrid5Evidence().observe_public_receipt(
            *receipt(0, act=0, before=(0, 0), after=(1, 0)))
        fixed = evidence.public_role_forecast([1, 0], 0, episode_id=EPISODE)
        self.assertEqual(fixed["status"], "ENTAILED")
        self.assertEqual(fixed["predicted_next_state"], [2, 0])
        guard = GUARD.unfamiliar_family_readout(evidence, [1, 0], 0,
                                                episode_id=EPISODE)
        self.assertEqual(guard["status"], "ABSTAIN_UNVERIFIED_FAMILY")
        self.assertEqual(guard["role_family_status"], "ENTAILED")
        self.assertFalse(guard["action_admissible"])
        self.assertIsNone(guard["actionable_next_state"])
        self.assertIsNone(guard["historical_witness_next_state"])
        self.assertEqual(guard["role_survivors"], 24)

    def test_contradiction_after_second_public_witness_still_not_actionable(self):
        evidence = NativeGrid5Evidence().observe_public_receipt(
            *receipt(0, act=0, before=(0, 0), after=(1, 0)))
        evidence = evidence.observe_public_receipt(
            *receipt(1, act=0, before=(1, 0), after=(0, 0)))
        fixed = evidence.public_role_forecast([1, 0], 0, episode_id=EPISODE)
        self.assertEqual(fixed["status"], "CONTRADICTION")
        guard = GUARD.unfamiliar_family_readout(evidence, [1, 0], 0,
                                                episode_id=EPISODE)
        self.assertEqual(guard["role_family_status"], "CONTRADICTION")
        self.assertEqual(guard["historical_witness_next_state"], [0, 0])
        self.assertIsNone(guard["actionable_next_state"])
        self.assertFalse(guard["family_authenticated"])

    def test_cold_checkpoint_and_default_plan_are_unchanged(self):
        evidence = NativeGrid5Evidence().observe_public_receipt(
            *receipt(0, act=0, before=(0, 0), after=(1, 0)))
        raw_before = evidence.checkpoint()
        plan_before = evidence.public_plan([1, 0], episode_id=EPISODE)
        a = GUARD.unfamiliar_family_readout(evidence, [1, 0], 0,
                                           episode_id=EPISODE)
        self.assertEqual(evidence.checkpoint(), raw_before)
        self.assertEqual(evidence.public_plan([1, 0], episode_id=EPISODE),
                         plan_before)
        restored = NativeGrid5Evidence.restore(
            raw_before, hashlib.sha256(raw_before).hexdigest())
        b = GUARD.unfamiliar_family_readout(restored, [1, 0], 0,
                                           episode_id=EPISODE)
        self.assertEqual(a, b)

    def test_native_validation_not_bypassed(self):
        evidence = NativeGrid5Evidence().observe_public_receipt(
            *receipt(0, act=0, before=(0, 0), after=(1, 0)))
        for state, action, episode in (([10, 0], 0, EPISODE),
                                        ([1, 0], 5, EPISODE),
                                        ([1, 0], True, EPISODE),
                                        ([1, 0], 0, None)):
            with self.subTest(state=state, action=action, episode=episode):
                with self.assertRaises(ValueError):
                    GUARD.unfamiliar_family_readout(evidence, state,
                                                 action, episode_id=episode)


if __name__ == "__main__":
    unittest.main()
