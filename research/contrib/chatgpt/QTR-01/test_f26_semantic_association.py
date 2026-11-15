"""QTR F26 semantic factual association source custody, purely source-free fixtures."""
import hashlib
import struct
import unittest

from f26_semantic_association import (
    NotAdmitted, PackedAssociationWeights, SOURCE_ITEMS, PROPS,
    safe_label, validate_rows, complete_labels, extract_seed_edges,
    parse_entity_batch, dryrun, symbolic_twohop, stable_json, qnum,
)


def entity(qid, label, statements=None):
    return {
        "id": qid, "lastrevid": 12345,
        "labels": {"en": {"language": "en", "value": label}},
        "claims": statements if statements is not None else {},
    }


def item_claim(s, p, o, idx=1, *, qualifier=False):
    d = {
        "id": s + "$" + str(idx),
        "rank": "normal",
        "mainsnak": {"snaktype": "value",
                     "datavalue": {"value": {"entity-type": "item", "id": o}}}
    }
    if qualifier:
        d["qualifiers"] = {"P580": [{"snaktype": "value"}]}
    return d


def sample_rows():
    return [
        {"s": "Q42", "p": "P31", "o": "Q5", "s_label": "Douglas Adams",
         "p_label": "instance of", "o_label": "human",
         "source_claim": "Q42$1", "source_revision": 12345},
        {"s": "Q5", "p": "P279", "o": "Q2", "s_label": "human",
         "p_label": "subclass of", "o_label": "Earth",
         "source_claim": "Q5$2", "source_revision": 12345}
    ]


class F26(unittest.TestCase):
    def test_typed_semantic_rows_cold_numeric_not_neural_weights(self):
        rows = sample_rows()
        self.assertTrue(validate_rows(rows))
        summary = dryrun(rows)
        self.assertEqual(summary["admitted_semantic_edges"], 2)
        self.assertEqual(summary["numeric_carrier_bytes"], 24)
        self.assertEqual(summary["twohop_compositions_checked"], 1)
        self.assertTrue(summary["equal_info_symbolic_control_parity"])
        self.assertTrue(summary["cold_restore_exact"])
        self.assertFalse(summary["architecture_native_weights_edited"])
        x = PackedAssociationWeights.from_rows(rows)
        self.assertEqual(x.twohop(42, 31, 279), {2})
        self.assertEqual(symbolic_twohop(rows, 42, 31, 279), {2})
        self.assertEqual(PackedAssociationWeights.restore(x.blob).blob, x.blob)

    def test_malformed_label_claim_and_source_membership_fail_closed(self):
        for label in ("", "Q5", "P31", "bad\ninjection", "x" * 400):
            with self.assertRaises(NotAdmitted):
                safe_label(label)
        for field, value in (("s", "Q9999"), ("p", "P777777"),
                             ("source_claim", "Q5$bad"),
                             ("source_revision", True),
                             ("o_label", "Q5")):
            rows = sample_rows()
            rows[0][field] = value
            with self.assertRaises(NotAdmitted):
                validate_rows(rows)
        with self.assertRaises(NotAdmitted):
            qnum("42", "Q")

    def test_unqualified_source_claims_only_and_full_seed_scope(self):
        seeds = {q: entity(q, "Name " + q) for q in SOURCE_ITEMS}
        seeds["Q42"]["claims"]["P31"] = [
            item_claim("Q42", "P31", "Q5", idx=1),
            item_claim("Q42", "P31", "Q2", idx=2, qualifier=True),
        ]
        rows, info = extract_seed_edges(seeds)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["o"], "Q5")
        self.assertEqual(info["claim_rows_inspected"], 2)
        seeds["Q42"]["claims"]["P31"].append(
            item_claim("Q99", "P31", "Q17", idx=3)
        )
        verified, audit = extract_seed_edges(seeds)
        self.assertEqual(len(verified), 1)
        self.assertEqual(audit["excluded_unbound_claim_witnesses"], 1)
        with self.assertRaises(NotAdmitted):
            extract_seed_edges({"Q42": seeds["Q42"]})

    def test_label_completion_abstains_not_invents(self):
        seeds = {q: entity(q, "Seed " + q) for q in SOURCE_ITEMS}
        props = {"P31": entity("P31", "instance of")}
        rows = [
            {"s": "Q42", "p": "P31", "o": "Q5", "s_label": "Seed Q42",
             "claim": "Q42$1", "source_revision": 12345},
            {"s": "Q42", "p": "P31", "o": "Q12345", "s_label": "Seed Q42",
             "claim": "Q42$2", "source_revision": 12345}
        ]
        accepted, missing = complete_labels(rows, seeds, props, {})
        self.assertEqual((len(accepted), missing), (1, 1))
        self.assertEqual(accepted[0]["o_label"], "Seed Q5")
        self.assertEqual(accepted[0]["p_label"], "instance of")

    def test_noncanonical_snapshot_and_duplicate_relations_rejected(self):
        rows = sample_rows()
        with self.assertRaises(NotAdmitted):
            validate_rows(rows + rows)
        x = PackedAssociationWeights.from_rows(rows)
        for bad in (b"", b"abc", x.blob[::-1], x.blob + x.blob):
            with self.assertRaises(NotAdmitted):
                PackedAssociationWeights.restore(bad)
        self.assertEqual(hashlib.sha256(x.blob).hexdigest(),
                         dryrun(rows)["numeric_snapshot_sha256"])

    def test_seed_source_request_includes_revision_info_without_network(self):
        import json
        from f26_semantic_association import CustodyHTTP
        class Response:
            status = 200
            headers = {}
            def __init__(self, raw): self.raw = raw
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self, count): return self.raw[:count]
        class StubOpener:
            def open(self, request, timeout):
                self.last_url = request.full_url
                assert timeout == 18
                return Response(json.dumps({"entities": {
                    "Q42": entity("Q42", "Douglas Adams")
                }}).encode())
        http = CustodyHTTP()
        http.opener = StubOpener()
        got = http.get(("Q42",), "info|claims|labels")
        self.assertEqual(got["Q42"]["lastrevid"], 12345)
        self.assertIn("props=info%7Cclaims%7Clabels", http.opener.last_url)
        self.assertEqual(len(http.receipts), 1)
        with self.assertRaises(NotAdmitted):
            http.get(("Q42",), "claims|labels")

    def test_source_json_endpoint_and_api_shape_negative(self):
        obj = {"entities": {"Q42": entity("Q42", "Douglas Adams")}}
        import json
        blob = json.dumps(obj).encode()
        self.assertEqual(parse_entity_batch(blob, ("Q42",))["Q42"]["id"], "Q42")
        for bad in ({"entities": {"Q99": entity("Q99", "unknown")}},
                    {"error": {"code": "rate_limit"}, "entities": obj["entities"]},
                    {"entities": {"Q42": {"id": "Q64", "missing": ""}}}):
            with self.assertRaises(NotAdmitted):
                parse_entity_batch(json.dumps(bad).encode(), ("Q42",))

    def test_shuffled_relation_negative_breaks_composition(self):
        x = PackedAssociationWeights.from_rows(sample_rows())
        different = PackedAssociationWeights([(5, 31, 2), (42, 279, 5)])
        self.assertEqual(x.twohop(42, 31, 279), {2})
        self.assertEqual(different.twohop(42, 31, 279), set())
        self.assertNotEqual(x.blob, different.blob)


if __name__ == "__main__":
    unittest.main()
