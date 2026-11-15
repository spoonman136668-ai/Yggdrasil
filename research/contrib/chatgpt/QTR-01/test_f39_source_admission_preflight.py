"""F39 source-free safety tests; these Q-IDs are synthetic, not facts."""
import hashlib
import json
import unittest

from f39_source_admission_preflight import OLD, EXT, Rejected, scan, MINIMA


def fixture():
    rows = []
    receipts = []
    for w in range(2):
        a = 900000000 + 100*w + 1
        b = a + 1
        c = a + 2
        for s, p, o in [(a, 400001, b), (b, 400002, c)]:
            rows.append({
                "s": f"Q{s}", "p": f"P{p}", "o": f"Q{o}",
                "source_claim": f"Q{s}$SYNTHETIC-{w}-{p}",
                "source_revision": 11, "rank": "normal", "qualifier_count": 0,
                "world": f"world_{w}", "domain": f"domain_{w}"
            })
        for q in (a, b):
            receipts.append({"qid": f"Q{q}", "revision": 11,
                             "raw_sha256": "a"*64})
    return {
        "schema": "yggdrasil.qtr01.f39.dev-claims-source-candidate.v1",
        "stage": "DEVELOPMENT_SOURCE_ONLY_NOT_SEALED",
        "source": "Wikidata structured claims",
        "license": "CC0",
        "license_reference": "https://www.wikidata.org/wiki/Wikidata:Licensing",
        "immutable_source_revision": "SYNTHETIC_TEST_ONLY",
        "rows": rows, "subject_receipts": receipts
    }


def evaluate(obj, old=None, ext=None):
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    digest = hashlib.sha256(raw).hexdigest()
    return scan(raw, digest,
                OLD.read_bytes() if old is None else old,
                EXT.read_bytes() if ext is None else ext)


class F39OfflinePreflight(unittest.TestCase):
    def test_development_graph_is_not_admitted_as_science(self):
        result = evaluate(fixture())
        self.assertEqual(result["counts"]["verified_claims"], 4)
        self.assertEqual(result["counts"]["independent_root_groups"], 2)
        self.assertEqual(result["counts"]["witnessed_positive_queries"], 2)
        self.assertEqual(result["world_count"], 2)
        self.assertFalse(result["proposed_minima_met"])
        for field in ("source_admitted", "scientific_first_use",
                      "scientific_pass", "heldout_families_sealed",
                      "upstream_receipt_bytes_independently_authenticated",
                      "complete_historical_consumed_source_ledger_verified"):
            self.assertFalse(result[field])

    def test_full_minima_cannot_be_silently_raised_or_lowered(self):
        self.assertEqual(MINIMA, {
            "verified_claims": 1024, "independent_root_groups": 64,
            "semantic_domains": 4, "distinct_predicate_ids": 16,
            "distinct_predicate_chains": 8, "witnessed_positive_queries": 128
        })

    def test_prior_bytes_must_be_exact(self):
        with self.assertRaisesRegex(Rejected, "PRIOR_SOURCE_HASH_MISMATCH"):
            evaluate(fixture(), old=OLD.read_bytes()+b" ")
        with self.assertRaisesRegex(Rejected, "PRIOR_SOURCE_HASH_MISMATCH"):
            evaluate(fixture(), ext=EXT.read_bytes()+b" ")

    def test_development_candidate_bytes_must_be_exact(self):
        obj = fixture()
        raw = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
        with self.assertRaisesRegex(Rejected, "CANDIDATE_DIGEST_MISMATCH"):
            scan(raw+b" ", hashlib.sha256(raw).hexdigest(),
                 OLD.read_bytes(), EXT.read_bytes())

    def test_prior_entity_leak_is_rejected(self):
        obj = fixture()
        obj["rows"][0]["o"] = "Q42"
        with self.assertRaisesRegex(Rejected, "REUSED_PRIOR_SOURCE_ENTITY"):
            evaluate(obj)

    def test_cross_world_node_leak_is_rejected(self):
        obj = fixture()
        obj["rows"][1]["world"] = "world_1"
        with self.assertRaisesRegex(Rejected, "CROSS_WORLD_ENTITY_LEAK"):
            evaluate(obj)

    def test_missing_subject_receipt_is_rejected(self):
        obj = fixture()
        obj["subject_receipts"].pop()
        with self.assertRaisesRegex(Rejected, "MALFORMED_OR_UNWITNESSED"):
            evaluate(obj)

    def test_qualifier_claim_and_rank_fences(self):
        for field, bad in (("qualifier_count", 1),
                           ("rank", "deprecated"),
                           ("source_claim", "Q111$FAKE")):
            with self.subTest(field=field):
                obj = fixture()
                obj["rows"][0][field] = bad
                with self.assertRaisesRegex(Rejected, "MALFORMED_OR_UNWITNESSED"):
                    evaluate(obj)

    def test_duplicate_fact_and_receipt_rejected(self):
        obj = fixture()
        obj["rows"].append(dict(obj["rows"][0]))
        with self.assertRaisesRegex(Rejected, "DUPLICATE_CANDIDATE_FACT"):
            evaluate(obj)
        obj = fixture()
        obj["subject_receipts"].append(dict(obj["subject_receipts"][0]))
        with self.assertRaisesRegex(Rejected, "DUPLICATE_RECEIPT"):
            evaluate(obj)

    def test_license_and_revision_identifiers_required(self):
        for key, bad in (("license", "unknown"),
                         ("immutable_source_revision", "")):
            with self.subTest(key=key):
                obj = fixture()
                obj[key] = bad
                with self.assertRaisesRegex(Rejected, "SOURCE_IDENTITY_OR_LICENSE"):
                    evaluate(obj)


if __name__ == "__main__":
    unittest.main()
