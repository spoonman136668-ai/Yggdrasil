"""QTR-01 F27: offline source and negative tests; never contacts Wikidata."""
import hashlib
import json
import unittest

from f27_versioned_entitydata import (
    LiveEntityData, NotAdmitted, capture, good_path, preflight,
    SOURCE_ITEMS, PROPS, SCHEMA,
)
from test_f26_semantic_association import entity, item_claim


class Response:
    status = 200
    headers = {}
    def __init__(self, blob):
        self.blob = blob
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def read(self, size):
        return self.blob[:size]


class Stub:
    def __init__(self, *, tamper=False, missing_label=False, wrong_revision=False):
        self.calls = []
        self.tamper = tamper
        self.missing_label = missing_label
        self.wrong_revision = wrong_revision
    def open(self, request, timeout):
        self.calls.append(request.full_url)
        assert timeout == 15
        url = request.full_url
        entity_id = url.rsplit("/", 1)[-1].split(".json")[0]
        if entity_id not in SOURCE_ITEMS + PROPS:
            raise AssertionError("unexpected source identifier")
        x = entity(entity_id, "Semantic label " + entity_id)
        if entity_id == "Q42":
            x["claims"] = {"P31": [item_claim("Q42", "P31", "Q5")]}
        if self.missing_label and entity_id == "Q5":
            x["labels"] = {}
        if self.wrong_revision and "revision=" in url:
            x["lastrevid"] = 12346
        if self.tamper and entity_id == "Q42" and "revision=" in url:
            x["labels"]["en"]["value"] = "altered source label"
        return Response(json.dumps({"entities": {entity_id: x}}).encode())


class F27(unittest.TestCase):
    def test_frozen_protocol_no_hidden_source_scope(self):
        self.assertEqual(preflight()["schema"], SCHEMA)
        self.assertEqual(len(SOURCE_ITEMS), 14)
        self.assertEqual(len(PROPS), 15)

    def test_source_url_rejects_non_whitelisted_urls(self):
        self.assertTrue(good_path("https://www.wikidata.org/wiki/Special:EntityData/Q42.json", "Q42"))
        self.assertTrue(good_path("https://www.wikidata.org/wiki/Special:EntityData/Q42.json?revision=12345", "Q42", 12345))
        self.assertFalse(good_path("https://evil.example/wiki/Special:EntityData/Q42.json", "Q42"))
        self.assertFalse(good_path("https://www.wikidata.org/wiki/Special:EntityData/Q42.json?not=revision", "Q42", 12345))
        self.assertFalse(good_path("http://www.wikidata.org/wiki/Special:EntityData/Q42.json", "Q42"))

    def test_offline_versioned_capture_real_schema_and_symbolic_parity(self):
        mock = Stub()
        reader = LiveEntityData(opener=mock)
        obj = capture(reader)
        self.assertEqual(obj["schema"], SCHEMA)
        self.assertEqual(obj["classification"],
                         "DEV_FIRST_PARTY_VERSIONED_SEMANTIC_ASSOCIATION_SOURCE_ONLY")
        self.assertEqual(obj["association_carrier"]["admitted_semantic_edges"], 1)
        self.assertEqual(obj["association_carrier"]["numeric_carrier_bytes"], 12)
        self.assertTrue(obj["association_carrier"]["cold_restore_exact"])
        self.assertTrue(obj["association_carrier"]["equal_info_symbolic_control_parity"])
        self.assertFalse(obj["actual_recipient_weights_edited"])
        self.assertFalse(obj["scientific_pass"])
        self.assertEqual(len(obj["source_read_receipts"]), 14 + 14 + 15)
        self.assertEqual(sum(z["revision_pinned_read"] for z in obj["source_read_receipts"]), 14)
        self.assertEqual(obj["admitted_rows"][0]["o_label"], "Semantic label Q5")
        self.assertTrue(all(z["raw_sha256"] == hashlib.sha256(
            json.dumps({"entities": {z["entity"]: (
                entity(z["entity"], "Semantic label " + z["entity"],
                       {"P31": [item_claim("Q42","P31","Q5")]}
                       if z["entity"] == "Q42" else {})
            )}}).encode()).hexdigest() for z in obj["source_read_receipts"]))

    def test_revision_tamper_and_wrong_revisions_fail_closed(self):
        for opts in ({"tamper": True}, {"wrong_revision": True}):
            with self.subTest(opts=opts):
                with self.assertRaises(NotAdmitted):
                    capture(LiveEntityData(opener=Stub(**opts)))

    def test_missing_english_object_label_abstains_without_fiction(self):
        with self.assertRaises(NotAdmitted):
            capture(LiveEntityData(opener=Stub(missing_label=True)))

    def test_duplicate_url_rejected(self):
        reader = LiveEntityData(opener=Stub())
        reader.fetch("Q42")
        with self.assertRaises(NotAdmitted):
            reader.fetch("Q42")
        with self.assertRaises(NotAdmitted):
            reader.fetch("Q42", revision=0)


if __name__ == "__main__":
    unittest.main()
