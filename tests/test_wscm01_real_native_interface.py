"""WSCM-01 integration contract against the REAL NativeEpisodeExperience.

Source-free regression only. No native Genome writes or real do-intervention
admission. These tests run only after the WSCM contributor branch includes
its Amalgam parent, not against accepted main alone.
"""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest

from yggdrasil.native_episode_experience import NativeEpisodeExperience

SOURCE = (Path(__file__).resolve().parents[1] /
          "research/contrib/chatgpt/CAUSAL-AMALGAM/wscm01_native_evidence_audit.py")
SPEC = spec_from_file_location("wscm01_native_evidence_audit_real", SOURCE)
AUDIT = module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)

FIRST_ID = "a" * 64
VIEWS = ((0, 1), (0, 1))
PUBLIC = {"s1": 0, "x1": 1, "s2": 0, "x2": 0, "y": 1}


class LearnerReadOnlyAdapter:
    """Expose the genuine, immutable native episode instance for audit only."""
    def __init__(self, episode):
        self.episode = episode

    def _episode_reader(self):
        return self.episode


class NativeEvidenceRealInterfaceTests(unittest.TestCase):
    def test_exact_native_episode_event_is_readable_and_nonpromotable(self):
        original = NativeEpisodeExperience()
        updated = original.observe(FIRST_ID, VIEWS, dict(PUBLIC))
        self.assertEqual(original._ledger, ())
        self.assertEqual(len(updated._ledger), 1)
        witness = AUDIT.read_native_episode(LearnerReadOnlyAdapter(updated), FIRST_ID)
        self.assertEqual((witness.identifier, witness.views), (FIRST_ID, VIEWS))
        self.assertEqual((witness.first_action, witness.next_state,
                          witness.second_action, witness.reward), (1, 0, 0, 1))
        self.assertEqual(witness.source_class, "engineering_fixture_only")
        self.assertFalse(witness.charged_do_authenticated)
        self.assertFalse(witness.basis_alignment_authenticated)
        with self.assertRaisesRegex(ValueError, "WSCM_CHARGED_SOURCE_AUTHORITY_ABSENT"):
            AUDIT.require_qualifying_probe(witness)
        self.assertEqual(len(updated._ledger), 1)

    def test_replayed_real_native_event_remains_idempotent(self):
        original = NativeEpisodeExperience()
        once = original.observe(FIRST_ID, VIEWS, dict(PUBLIC))
        twice = once.observe(FIRST_ID, VIEWS, dict(PUBLIC))
        self.assertIs(once, twice)
        witness = AUDIT.read_native_episode(LearnerReadOnlyAdapter(twice), FIRST_ID)
        self.assertEqual(witness.identifier, FIRST_ID)

    def test_native_interface_rejects_action_id_shift_not_binary(self):
        episode = NativeEpisodeExperience()
        changed = dict(PUBLIC)
        changed["x1"] = 90017
        with self.assertRaises(ValueError):
            episode.observe(FIRST_ID, VIEWS, changed)
        self.assertEqual(episode._ledger, ())

    def test_native_source_requires_distinct_authentication(self):
        episode = NativeEpisodeExperience().observe(FIRST_ID, VIEWS, dict(PUBLIC))
        record = AUDIT.read_native_episode(LearnerReadOnlyAdapter(episode), FIRST_ID)
        forged = record._replace(charged_do_authenticated=True,
                                 basis_alignment_authenticated=True)
        with self.assertRaisesRegex(ValueError, "WSCM_CHARGED_SOURCE_AUTHORITY_ABSENT"):
            AUDIT.require_qualifying_probe(forged)


if __name__ == "__main__":
    unittest.main()
