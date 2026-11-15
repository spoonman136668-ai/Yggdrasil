"""F30 independently verified source-locale preservation and numeric parity."""
import json
import unittest

from f26_semantic_association import NotAdmitted
from f27_versioned_entitydata import LiveEntityData
from f30_multilingual_associations import (
    SCHEMA, SEEDS, PREDICATES, preflight, exact_source_label,
    extract_seed_claims, endpoint_order, complete_source_labels,
    source_free_numeric_control, capture,
)


def source_entity(qid, text="source literal", lang="en", claims=None):
    return {
        "id": qid, "lastrevid": 12345,
        "labels": {lang: {"language": lang, "value": text}},
        "claims": claims if claims is not None else {},
    }


def statement(s, o, *, rank="normal", qualifiers=False, witness=True):
    obj = {
        "id": (s if witness else "Q99") + "$1",
        "rank": rank,
        "mainsnak": {
            "snaktype": "value",
            "datavalue": {"value": {"entity-type": "item", "id": o}},
        },
    }
    if qualifiers:
        obj["qualifiers"] = {"P580": []}
    return obj


class Response:
    status = 200
    headers = {}
    def __init__(self, raw):
        self.raw = raw
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def read(self, count):
        return self.raw[:count]


class Stub:
    def __init__(self, **opts):
        self.opts = opts
        self.urls = []
    def open(self, request, timeout):
        assert timeout == 15
        url = request.full_url
        qid = url.rsplit("/", 1)[-1].split(".json")[0]
        self.urls.append(url)
        if qid not in (*SEEDS, *PREDICATES, "Q2250224"):
            raise AssertionError("source scope expanded")
        labels = {
            "Q42": ("Douglas Adams", "fr"),
            "Q5": ("human", "en"),
            "Q2250224": ("persona", "es"),
            "P31": ("instance of", "en"),
            "P279": ("subclass of", "en"),
        }
        text, lang = labels.get(qid, ("relation", "en"))
        ent = source_entity(qid, text=text, lang=lang)
        if qid == "Q42":
            ent["claims"] = {"P31": [statement("Q42", "Q5")]}
        if qid == "Q5":
            ent["claims"] = {"P279": [statement(
                "Q5", "Q2250224",
                witness=not self.opts.get("unbound", False),
                qualifiers=self.opts.get("qualifier", False),
            )]}
        if self.opts.get("no_q42_lang") and qid == "Q42":
            ent["labels"] = {"eo": {"language": "eo", "value": "Douglas Adams"}}
        if self.opts.get("missing_endpoint") and qid == "Q2250224":
            ent["labels"] = {}
        if self.opts.get("wrong_revision") and "revision=" in url:
            ent["lastrevid"] = 12346
        if self.opts.get("changed_content") and "revision=" in url and qid == "Q42":
            ent["labels"]["fr"]["value"] = "tampered"
        return Response(json.dumps({"entities": {qid: ent}}).encode("utf-8"))


class F30(unittest.TestCase):
    def test_frozen_contract_and_source_order(self):
        p = preflight()
        self.assertEqual(p["schema"], SCHEMA)
        self.assertEqual(p["allowed_seed_qids"], list(SEEDS))
        self.assertEqual(p["allowed_properties"], list(PREDICATES))
        self.assertEqual(p["allow_label_languages_in_preference_order"][0], "en")

    def test_first_party_multilingual_selection_preserves_original_tag(self):
        obj = source_entity("Q42", "Douglas Adams", "fr")
        found = exact_source_label(obj)
        self.assertEqual(found, {"source_language": "fr", "label": "Douglas Adams"})
        obj["labels"]["en"] = {"language": "en", "value": "author"}
        self.assertEqual(exact_source_label(obj)["source_language"], "en")
        obj["labels"]["en"] = {"language": "fr", "value": "wrong"}
        self.assertEqual(exact_source_label(obj)["source_language"], "fr")
        self.assertIsNone(exact_source_label(source_entity("Q42", "name", "eo")))

    def test_typed_original_first_party_claim_and_language_2hop(self):
        reader = LiveEntityData(opener=Stub())
        result = capture(reader)
        self.assertEqual(len(result["source_rows"]), 2)
        self.assertEqual(result["numeric_equal_info_control"]["typed_integer_carrier_bytes"], 24)
        self.assertEqual(result["numeric_equal_info_control"]["actual_observed_twohop_queries"], 1)
        self.assertTrue(result["numeric_equal_info_control"]["numeric_vs_equal_info_symbolic_2hop_parity"])
        self.assertTrue(result["numeric_equal_info_control"]["canonical_cold_restore"])
        self.assertEqual(result["inventory"]["seed_source_label_languages"], {"Q42": "fr", "Q5": "en"})
        self.assertEqual(result["source_rows"][0]["s_language"], "fr")
        self.assertEqual({row["o_language"] for row in result["source_rows"]}, {"en", "es"})
        self.assertEqual(len(result["raw_first_party_source_receipts"]), 2 + 2 + 1 + 8)
        self.assertFalse(result["scientific_pass"])
        self.assertFalse(result["accepted_model_weights_modified"])

    def test_disallowed_qualifier_or_wrong_claim_witness_fails(self):
        for opts in ({"qualifier": True}, {"unbound": True}, {"missing_endpoint": True}):
            with self.subTest(opts=opts):
                out = capture(LiveEntityData(opener=Stub(**opts)))
                self.assertEqual(len(out["source_rows"]), 1)
                self.assertEqual(out["numeric_equal_info_control"]["actual_observed_twohop_queries"], 0)

    def test_altered_revision_and_torn_label_fail_closed(self):
        for opts in ({"wrong_revision": True}, {"changed_content": True}, {"no_q42_lang": True}):
            with self.subTest(opts=opts):
                with self.assertRaises(NotAdmitted):
                    capture(LiveEntityData(opener=Stub(**opts)))

    def test_source_bounded_endpoint_priority_and_empty_seed_rejected(self):
        raw = {
            "Q42": source_entity("Q42", "Douglas Adams", "fr",
                                 {"P31": [statement("Q42", "Q5")]}),
            "Q5": source_entity("Q5", "human", "en",
                                {"P279": [statement("Q5", "Q2250224")]}),
        }
        rows, info = extract_seed_claims(raw)
        self.assertEqual(len(rows), 2)
        self.assertEqual(endpoint_order(rows), ["Q2250224"])
        with self.assertRaises(NotAdmitted):
            extract_seed_claims({"Q42": raw["Q42"]})


if __name__ == "__main__":
    unittest.main()
