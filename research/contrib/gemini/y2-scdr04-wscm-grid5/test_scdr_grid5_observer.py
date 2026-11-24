"""Native compatibility & partial-contradiction tests for SCDRGrid5Observer against real NativeGrid5Evidence and WSCM guard.py."""

from __future__ import annotations

import hashlib
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from yggdrasil.native_grid5_evidence import NativeGrid5Evidence
from test_native_grid5_evidence_dev import receipt
from scdr_grid5_observer import SCDRGrid5Observer

EPISODE = "a" * 64


class TestSCDRGrid5ObserverNative(unittest.TestCase):
    def test_preserves_wscm_safety_and_native_checkpoint_byte_exact(self) -> None:
        evidence = NativeGrid5Evidence().observe_public_receipt(*receipt(0, act=0, before=(0, 0), after=(1, 0)))
        obs = SCDRGrid5Observer()
        obs.observe_transition((0, 0), 0, (1, 0))

        raw_before = evidence.checkpoint()
        plan_before = evidence.public_plan([1, 0], episode_id=EPISODE)
        out = obs.guarded_diagnostic_readout(evidence, [1, 0], 0, episode_id=EPISODE)

        self.assertEqual(evidence.checkpoint(), raw_before)
        self.assertEqual(evidence.public_plan([1, 0], episode_id=EPISODE), plan_before)
        self.assertEqual(out["status"], "ABSTAIN_UNVERIFIED_FAMILY")
        self.assertFalse(out["action_admissible"])
        self.assertIsNone(out["actionable_next_state"])
        self.assertFalse(out["family_authenticated"])
        self.assertEqual(out["scdr_action_role_map"], "PLUS_X")

        # Fail-closed validation from NativeGrid5Evidence is never bypassed
        for bad_state, bad_act, bad_ep in (([10, 0], 0, EPISODE), ([1, 0], 5, EPISODE), ([1, 0], 0, None)):
            with self.assertRaises(ValueError):
                obs.guarded_diagnostic_readout(evidence, bad_state, bad_act, episode_id=bad_ep)

    def test_isolates_single_contradicting_action_while_preserving_other_four(self) -> None:
        """
        When action 0 contradicts fixed Grid5 translation ((0,0)->(1,0) then (1,0)->(0,0)),
        NativeGrid5Evidence.public_role_forecast collapses to CONTRADICTION globally for ALL 5 actions.
        SCDRGrid5Observer selectively isolates action 0 as NOVEL_OR_CONTRADICTED while keeping
        actions 1..4 cleanly identified via Sub-Stochastic Sinkhorn!
        """
        # Continuous valid 1-step Manhattan Grid5 trajectory starting at (0, 0)
        transitions = [
            (0, (0, 0), (1, 0)),  # action 0 moves +x
            (0, (1, 0), (0, 0)),  # action 0 moves -x (contradiction!)
            (0, (0, 0), (0, 1)),  # action 0 moves +y (contradiction!)
            (0, (0, 1), (0, 0)),  # action 0 moves -y (contradicts all 5 fixed roles!)
            (1, (0, 0), (0, 1)),  # action 1 consistently +y
            (1, (0, 1), (0, 2)),  # action 1 consistently +y
            (0, (0, 2), (1, 2)),  # action 0 moves +x
            (2, (1, 2), (0, 2)),  # action 2 consistently -x
            (0, (0, 2), (1, 2)),  # action 0 moves +x
            (2, (1, 2), (0, 2)),  # action 2 consistently -x
            (3, (0, 2), (0, 1)),  # action 3 consistently -y
            (3, (0, 1), (0, 0)),  # action 3 consistently -y
            (4, (0, 0), (0, 0)),  # action 4 consistently STAY
            (4, (0, 0), (0, 0)),  # action 4 consistently STAY
        ]
        evidence = NativeGrid5Evidence()
        obs = SCDRGrid5Observer()
        for idx, (act, bef, aft) in enumerate(transitions):
            evidence = evidence.observe_public_receipt(*receipt(idx, act=act, before=bef, after=aft))
            obs.observe_transition(bef, act, aft)

        # Native global 120-permutation role forecast collapses to CONTRADICTION even on consistent action 1!
        r0 = obs.guarded_diagnostic_readout(evidence, [2, 2], 0, episode_id=EPISODE)
        r1 = obs.guarded_diagnostic_readout(evidence, [2, 2], 1, episode_id=EPISODE)
        r2 = obs.guarded_diagnostic_readout(evidence, [2, 2], 2, episode_id=EPISODE)
        r3 = obs.guarded_diagnostic_readout(evidence, [2, 2], 3, episode_id=EPISODE)
        r4 = obs.guarded_diagnostic_readout(evidence, [2, 2], 4, episode_id=EPISODE)

        self.assertEqual(r1["role_family_status"], "CONTRADICTION")
        # SCDR isolates action 0 as NOVEL_OR_CONTRADICTED (abstain > 0.85)
        self.assertEqual(r0["scdr_action_role_map"], "NOVEL_OR_CONTRADICTED")
        self.assertGreater(r0["scdr_action_novel_abstain"], 0.85)
        # While preserving all 4 consistent actions (abstain < 0.05)!
        self.assertEqual(r1["scdr_action_role_map"], "PLUS_Y")
        self.assertEqual(r2["scdr_action_role_map"], "MINUS_X")
        self.assertEqual(r3["scdr_action_role_map"], "MINUS_Y")
        self.assertEqual(r4["scdr_action_role_map"], "STAY")
        for r in (r1, r2, r3, r4):
            self.assertLess(r["scdr_action_novel_abstain"], 0.05)
            self.assertFalse(r["action_admissible"])


if __name__ == "__main__":
    unittest.main()
