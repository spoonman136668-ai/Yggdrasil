"""F29 exact first-party source schema diagnostic, no live source reads."""
import hashlib
import unittest

from f29_schema_diagnostic import (
    IDS, SCHEMA, diagnose, preflight, inspect, NotAdmitted,
)


def receipt(qid):
    return {"entity": qid, "revision": 12345, "bytes": 730,
            "raw_sha256": "a" * 64}


def entity(qid, labels):
    return {"id": qid, "lastrevid": 12345, "labels": labels,
            "claims": {"P31": []}}


class StubReader:
    def __init__(self, overrides=None):
        self.overrides = overrides or {}
        self.receipts = []
        self.total_bytes = 0
    def fetch(self, qid):
        if qid not in IDS or any(r["entity"] == qid for r in self.receipts):
            raise NotAdmitted("DUPLICATE_OR_UNKNOWN_SOURCE")
        labels = self.overrides.get(qid, {
            "en": {"language": "en", "value": "Semantic name"}
        })
        got = entity(qid, labels)
        self.receipts.append(receipt(qid))
        self.total_bytes += 730
        return got, hashlib.sha256(qid.encode()).hexdigest()


class F29(unittest.TestCase):
    def test_prereg_and_exact_cohort(self):
        self.assertEqual(preflight()["schema"], SCHEMA)
        self.assertEqual(IDS, ("Q42", "Q5"))
    def test_two_first_party_metadata_reads_do_not_admit_source(self):
        reader = StubReader()
        result = inspect(reader)
        self.assertEqual(result["request_count"], 2)
        self.assertEqual(result["source_en_label_usable_count"], 2)
        self.assertFalse(result["source_data_admitted"])
        self.assertFalse(result["model_weights_modified"])
        self.assertFalse(result["scientific_pass"])
        self.assertTrue(all(row["raw_sha256"] == "a"*64 for row in result["records"]))
        self.assertEqual(result["source_bytes"], 1460)
    def test_missing_label_is_recorded_not_guessed(self):
        reader = StubReader({"Q5": {}})
        result = inspect(reader)
        self.assertEqual(result["source_en_label_usable_count"], 1)
        self.assertFalse(result["records"][1]["en_present"])
        self.assertEqual(result["records"][1]["en_field_type"], "NoneType")
    def test_schema_mismatch_is_visible_without_source_text(self):
        for bad in ([], {"en": []},
                    {"en": {"language": "en-gb", "value": "Hello"}},
                    {"en": {"language": "en", "value": "bad\nlabel"}},
                    {"en": {"language": "en", "value": "Q5"}}):
            with self.subTest(bad=bad):
                row = diagnose("Q42", entity("Q42", bad), receipt("Q42"))
                self.assertFalse(row["source_en_label_usable"])
    def test_bad_source_receipts_fail_closed(self):
        with self.assertRaises(NotAdmitted):
            diagnose("Q99", entity("Q99", {}), receipt("Q99"))
        with self.assertRaises(NotAdmitted):
            diagnose("Q42", entity("Q42", {}), receipt("Q5"))
        with self.assertRaises(NotAdmitted):
            diagnose("Q42", entity("Q42", {}), {"entity": "Q42", "revision": 10})
    def test_missing_record_or_byte_budget_fails_closed(self):
        class TooMuch(StubReader):
            def fetch(self, qid):
                out = super().fetch(qid)
                self.total_bytes += 8388608
                return out
        with self.assertRaises(NotAdmitted):
            inspect(TooMuch())


if __name__ == "__main__":
    unittest.main()
