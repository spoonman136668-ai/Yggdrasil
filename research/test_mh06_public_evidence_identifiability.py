"""MH06 frozen source-only mechanical controls; no reward world or native runs."""
import hashlib
import math
from pathlib import Path
import unittest

from research import mh06_public_evidence_identifiability as mh


class MH06ReadOnlyIdentifiabilityTests(unittest.TestCase):
    def test_unchanged_original_quarantined_rust_blob(self):
        root = Path(__file__).resolve().parents[1]
        raw = (root / "research" / "itd02_v32e_pair_consensus.rs").read_bytes()
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        self.assertEqual(blob, mh.ORIGINAL_V32E_GIT_BLOB)
        self.assertIn(b"Quarantined source-only", raw)
        self.assertIn(b"Not original native learner", raw)

    def test_no_feedback_paired_twin_identifiability(self):
        # The same public sequence is presented in both hypothetical regimes.
        for choices in ((0,), (1,), (0, 1, 0, 1),
                        (1, 1, 1, 0, 0, 1), (0,)*24):
            self.assertEqual(mh.expected_paired_accuracy(choices), 0.5)
        self.assertEqual(mh.expected_paired_accuracy((None,)*8), 0.0)
        self.assertEqual(mh.expected_paired_accuracy((0,None,1,None)), .25)
        with self.assertRaises(ValueError):
            mh.expected_paired_accuracy((0, 2))
        with self.assertRaises(ValueError):
            mh.expected_paired_accuracy((True,))
        with self.assertRaises(ValueError):
            mh.expected_paired_accuracy(())

    def test_unequal_prior_bound(self):
        for p in (0.01, 0.1, 0.5, 0.9, 0.99):
            self.assertLessEqual(mh.expected_accuracy_with_prior(0,p), max(p,1-p))
            self.assertLessEqual(mh.expected_accuracy_with_prior(1,p), max(p,1-p))
        self.assertEqual(mh.expected_accuracy_with_prior(None,.5), 0.)
        for bad in (-.01,1.01,float("nan"),True):
            with self.assertRaises(ValueError):
                mh.expected_accuracy_with_prior(0,bad)

    def test_no_public_reward_no_selection(self):
        g=mh.MH06PublicEvidenceGate()
        self.assertIsNone(g.recommendation())
        g.observe_public_cue(0)
        self.assertIsNone(g.recommendation())
        self.assertEqual(g.inspect()["distinct_public_action_consequence_pairs"],0)
        self.assertIsNone(g.inspect()["shadow_recommendation"])
        self.assertFalse(g.inspect()["native_bank_switched"])
        self.assertEqual(g.inspect()["source_actions_executed"],0)
        self.assertFalse(g.inspect()["scientific_gain_verified"])

    def test_public_feedback_favors_each_bank_only_after_two_distinct_pairs(self):
        for reward,winner in ((1.0,0),(-1.0,1)):
            g=mh.MH06PublicEvidenceGate()
            g.observe_public_cue(1)
            self.assertIsNone(g.record_public_feedback(0,reward,1.0,-1.0))
            self.assertIsNone(g.recommendation())
            g.observe_public_cue(2)
            self.assertEqual(g.record_public_feedback(1,reward,1.0,-1.0), winner)
            self.assertEqual(g.inspect()["distinct_public_action_consequence_pairs"],2)
            self.assertGreaterEqual(abs(g.inspect()["log_odds_bank0_over_bank1"]),
                                    mh.LOG_ODDS_GATE)

    def test_ambiguous_and_contradictory_public_feedback_stays_abstained(self):
        g=mh.MH06PublicEvidenceGate()
        for cue,action in ((0,0),(1,1)):
            g.observe_public_cue(cue)
            self.assertIsNone(g.record_public_feedback(action,1.0,.8,.8))
        self.assertIsNone(g.recommendation())
        h=mh.MH06PublicEvidenceGate()
        h.observe_public_cue(0)
        h.record_public_feedback(0,1.0,1.,-1.)
        h.observe_public_cue(1)
        self.assertIsNone(h.record_public_feedback(1,-1.0,1.,-1.))
        self.assertAlmostEqual(h.inspect()["log_odds_bank0_over_bank1"],0.,places=12)

    def test_invalid_outcome_does_not_commit_partial_state(self):
        g=mh.MH06PublicEvidenceGate()
        with self.assertRaises(ValueError):
            g.record_public_feedback(0,1.,1.,-1.)
        for cue in (-1,4,True,"0"):
            with self.assertRaises(ValueError):
                g.observe_public_cue(cue)
        g.observe_public_cue(0)
        for action,reward,s0,s1 in ((3,1.,1.,-1.),(0,0.,1.,-1.),
                                    (0,True,1.,-1.),(0,1.,math.nan,-1.),
                                    (0,1.,1.,math.inf),(False,1.,1.,-1.)):
            with self.assertRaises(ValueError):
                g.record_public_feedback(action,reward,s0,s1)
            self.assertEqual(g.inspect()["pending_public_cue"],0)
            self.assertEqual(g.inspect()["distinct_public_action_consequence_pairs"],0)
        with self.assertRaises(ValueError):
            g.observe_public_cue(1)
        self.assertIsNone(g.record_public_feedback(0,1.,1.,-1.))
        g.observe_public_cue(0)
        with self.assertRaises(ValueError):
            g.record_public_feedback(0,1.,1.,-1.)
        self.assertEqual(g.inspect()["pending_public_cue"],0)
        self.assertEqual(g.inspect()["distinct_public_action_consequence_pairs"],1)


if __name__ == "__main__":
    unittest.main()
