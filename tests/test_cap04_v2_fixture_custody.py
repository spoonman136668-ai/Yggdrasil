"""CAP04 v2 engineering-only, mock-key custody negative controls."""
import importlib.util
from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[1] /
          "research/contrib/chatgpt/YGG-CAP04/custody_fixture_contract.py")
spec = importlib.util.spec_from_file_location("cap04_mock_custody", SOURCE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

# These values are intentionally PUBLIC TOY KEYS — not scientific secrets.
AUDIT = bytes(range(32))
TOY_A = bytes(range(32, 64))
TOY_B = bytes(range(64, 96))


def make_ledger():
    return m.FixtureCustodyLedger(AUDIT)


def reserve(ledger, source, key, **overrides):
    kwargs = dict(source_sha=m.QUALIFIED_SOURCE_SHA,
                  source_tree=m.QUALIFIED_SOURCE_TREE,
                  prereg_blob=m.FROZEN_PREREG_BLOB)
    kwargs.update(overrides)
    return ledger.reserve_fixture(source, key, **kwargs)


class FixtureCustodyContractTests(unittest.TestCase):
    def test_distinct_sources_and_mock_keys_get_only_non_authorizing_receipts(self):
        ledger = make_ledger()
        for ix, (label, key) in enumerate(zip(sorted(m.ENGINEERING_IDENTITIES),
                                             (TOY_A, TOY_B)), start=1):
            rec = reserve(ledger, label, key)
            self.assertEqual(rec["mock_sources_seen"], ix)
            self.assertEqual(rec["classification"], "ENGINEERING_MOCK_ONLY")
            self.assertEqual(rec["registered_first_use"], "LOCKED")
            self.assertEqual(rec["source_entropy_quality"], "UNVERIFIED")
            self.assertEqual(rec["protected_key_custody"], "UNVERIFIED")
            self.assertEqual(rec["durable_uniqueness"], "UNVERIFIED")
            self.assertEqual(rec["owner_approval"], "UNVERIFIED")
            self.assertEqual(rec["scientific_efficacy"], "UNVERIFIED")
            self.assertEqual(rec["source_sha"], m.QUALIFIED_SOURCE_SHA)
            for sample in (AUDIT, TOY_A, TOY_B):
                self.assertNotIn(sample.hex(), repr(rec))
            self.assertNotIn("fingerprint", repr(rec).lower())
            self.assertNotIn("entropy_reuse_tag", repr(rec))
        self.assertEqual(len(ledger._seen_fingerprints), 2)

    def test_same_mock_entropy_across_two_different_source_ids_rejected(self):
        ledger = make_ledger()
        a, b = sorted(m.ENGINEERING_IDENTITIES)
        reserve(ledger, a, TOY_A)
        with self.assertRaisesRegex(ValueError, "CAP04_CUSTODY_ENTROPY_REUSE"):
            reserve(ledger, b, TOY_A)
        # The failed attempt must not consume b.
        self.assertEqual(reserve(ledger, b, TOY_B)["mock_sources_seen"], 2)

    def test_same_identity_with_different_mock_entropy_rejected(self):
        ledger = make_ledger()
        a = sorted(m.ENGINEERING_IDENTITIES)[0]
        reserve(ledger, a, TOY_A)
        with self.assertRaisesRegex(ValueError, "CAP04_CUSTODY_SOURCE_REUSE"):
            reserve(ledger, a, TOY_B)

    def test_unqualified_refs_and_reserved_cohort_ids_rejected_before_mutation(self):
        ledger = make_ledger()
        for label in ("99917", "99931", "100017", "100131", "", 99917,
                      "cap04-v2-engineering-unknown"):
            with self.subTest(label=label), self.assertRaisesRegex(
                    ValueError, "CAP04_CUSTODY_REGISTERED_FIRST_USE_FORBIDDEN"):
                reserve(ledger, label, TOY_A)
        for bad in (None, b"", bytes(31), bytes(33), bytearray(32),
                    "public-string", 1, True):
            with self.subTest(key=type(bad).__name__), self.assertRaisesRegex(
                    ValueError, "CAP04_CUSTODY_SOURCE_KEY_SHAPE"):
                reserve(ledger, sorted(m.ENGINEERING_IDENTITIES)[0], bad)
        for field in ("source_sha", "source_tree", "prereg_blob"):
            with self.subTest(field=field), self.assertRaisesRegex(
                    ValueError, "CAP04_CUSTODY_UNQUALIFIED_SOURCE_REFS"):
                reserve(ledger, sorted(m.ENGINEERING_IDENTITIES)[0],
                        TOY_A, **{field: "0" * 40})
        self.assertEqual(reserve(ledger, sorted(m.ENGINEERING_IDENTITIES)[0],
                                 TOY_A)["mock_sources_seen"], 1)

    def test_audit_key_input_and_no_key_raising_error_exposure(self):
        for invalid in (None, b"", bytes(31), bytes(33), "public", bytearray(32)):
            with self.assertRaisesRegex(ValueError, "CAP04_CUSTODY_AUDIT_KEY_SHAPE"):
                m.FixtureCustodyLedger(invalid)
        ledger = make_ledger()
        self.assertEqual(repr(ledger),
                         "FixtureCustodyLedger(mode=ENGINEERING_MOCK_ONLY,count=0)")
        with self.assertRaisesRegex(ValueError,
                                    "CAP04_CUSTODY_REGISTERED_FIRST_USE_FORBIDDEN"):
            ledger.authorize_registered_first_use(
                {"registered_first_use": "APPROVED"})
        with self.assertRaisesRegex(ValueError,
                                    "CAP04_CUSTODY_REGISTERED_FIRST_USE_FORBIDDEN"):
            ledger.authorize_registered_first_use(None)

    def test_ephemeral_ledger_cannot_prove_cross_process_uniqueness(self):
        # This MUST be reported as UNVERIFIED in all engineering receipts:
        # separate in-memory sessions cannot detect one another's key use.
        label = sorted(m.ENGINEERING_IDENTITIES)[0]
        first, second = make_ledger(), make_ledger()
        p = reserve(first, label, TOY_A)
        q = reserve(second, label, TOY_A)
        self.assertEqual(p["durable_uniqueness"], "UNVERIFIED")
        self.assertEqual(q["durable_uniqueness"], "UNVERIFIED")
        self.assertEqual(p, q)


if __name__ == "__main__":
    unittest.main()
