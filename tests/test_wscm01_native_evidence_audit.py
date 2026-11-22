"""Tests prove native episode provenance cannot be inflated into do-action evidence."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[1] /
          'research/contrib/chatgpt/CAUSAL-AMALGAM/wscm01_native_evidence_audit.py')
SPEC = spec_from_file_location('wscm01_native_evidence_audit', SOURCE)
MODULE = module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

ID1 = 'a' * 64
ID2 = 'b' * 64
VIEW = ((0, 1), (0, 1))
EVENT = (ID1, VIEW, 1, 0, 0, 1)


class FakeEpisodeReader:
    def __init__(self, ledger):
        self._ledger = ledger


class FakeNativeLearner:
    def __init__(self, ledger):
        self.reader = FakeEpisodeReader(ledger)

    def _episode_reader(self):
        return self.reader


class NativeEvidenceAuditTests(unittest.TestCase):
    def test_native_record_matches_real_contract_but_is_dev_only(self):
        original = FakeNativeLearner((EVENT,))
        result = MODULE.read_native_episode(original, ID1)
        self.assertEqual((result.first_action, result.next_state,
                          result.second_action, result.reward), (1, 0, 0, 1))
        self.assertEqual(result.source_class, 'engineering_fixture_only')
        self.assertFalse(result.charged_do_authenticated)
        self.assertFalse(result.basis_alignment_authenticated)
        with self.assertRaisesRegex(ValueError, 'WSCM_CHARGED_SOURCE_AUTHORITY_ABSENT'):
            MODULE.require_qualifying_probe(result)
        self.assertEqual(original.reader._ledger, (EVENT,))

    def test_forged_positive_flags_never_authenticate_native_ledger(self):
        record = MODULE.read_native_episode(FakeNativeLearner((EVENT,)), ID1)
        spoofed = record._replace(charged_do_authenticated=True,
                                  basis_alignment_authenticated=True)
        with self.assertRaisesRegex(ValueError, 'WSCM_CHARGED_SOURCE_AUTHORITY_ABSENT'):
            MODULE.require_qualifying_probe(spoofed)

    def test_missing_and_duplicate_id_are_rejected(self):
        with self.assertRaisesRegex(ValueError, 'WSCM_NATIVE_EPISODE_MISSING'):
            MODULE.read_native_episode(FakeNativeLearner((EVENT,)), ID2)
        with self.assertRaisesRegex(ValueError, 'WSCM_NATIVE_DUPLICATE_IDENTIFIER'):
            MODULE.read_native_episode(FakeNativeLearner((EVENT, EVENT)), ID1)

    def test_ledger_rejects_malformed_row_and_boolean_values(self):
        bad = (ID1, VIEW, True, 0, 0, 1)
        with self.assertRaisesRegex(ValueError, 'WSCM_NATIVE_LEDGER_CONTRACT'):
            MODULE.read_native_episode(FakeNativeLearner((bad,)), ID1)
        bad2 = (ID1, ((0, 1), (0, 2)), 1, 0, 0, 1)
        with self.assertRaisesRegex(ValueError, 'WSCM_NATIVE_LEDGER_CONTRACT'):
            MODULE.read_native_episode(FakeNativeLearner((bad2,)), ID1)

    def test_ledger_capacity_and_structure_fail_closed(self):
        with self.assertRaisesRegex(ValueError, 'WSCM_NATIVE_LEDGER_CAPACITY'):
            MODULE.read_native_episode(FakeNativeLearner([EVENT]), ID1)
        with self.assertRaisesRegex(ValueError, 'WSCM_NATIVE_LEDGER_CAPACITY'):
            MODULE.read_native_episode(FakeNativeLearner((EVENT,) * 1153), ID1)

    def test_unavailable_ledger_and_bad_identifiers_fail_closed(self):
        with self.assertRaisesRegex(ValueError, 'WSCM_NATIVE_IDENTIFIER'):
            MODULE.read_native_episode(FakeNativeLearner((EVENT,)), 'x')
        with self.assertRaisesRegex(ValueError, 'WSCM_NATIVE_LEDGER_UNAVAILABLE'):
            MODULE.read_native_episode(object(), ID1)


if __name__ == '__main__':
    unittest.main()
