"""F31 source-language-agnostic first-party custody and matched symbolic controls."""
import json
import unittest

from f26_semantic_association import NotAdmitted
from f27_versioned_entitydata import LiveEntityData
from f31_all_language_associations import (
    SEEDS, PROPS, preflight, source_label, witnessed_rows, capture,
)


def entity(qid,lang="eo",label="source-language name",claims=None):
    return {"id":qid,"lastrevid":12345,
            "labels":{lang:{"language":lang,"value":label}},
            "claims":claims if claims is not None else {}}


def claim(subject,obj,qualified=False,wrong_witness=False):
    out={"id":("Q999" if wrong_witness else subject)+"$source-event",
         "rank":"normal","mainsnak":{"snaktype":"value","datavalue":
         {"value":{"entity-type":"item","id":obj}}}}
    if qualified:
        out["qualifiers"]={"P580":[]}
    return out


class Response:
    status=200
    headers={}
    def __init__(self,payload): self.payload=payload
    def __enter__(self): return self
    def __exit__(self,*args): return False
    def read(self,n): return self.payload[:n]


class Stub:
    def __init__(self,**options):
        self.options=options
        self.urls=[]
    def open(self,request,timeout):
        assert timeout==15
        url=request.full_url
        qid=url.rsplit("/",1)[-1].split(".json")[0]
        self.urls.append(url)
        assert qid in (*SEEDS,*PROPS,"Q2250224")
        item=entity(qid,lang="eo",label="native-source label")
        if qid=="Q42":
            item["labels"]={
                "eo":{"language":"eo","value":"Doug Adams in Esperanto"},
                "la":{"language":"la","value":"Source Latin name"},
            }
            item["claims"]={"P31":[claim("Q42","Q5")]}
        if qid=="Q5":
            item["labels"]={"en":{"language":"en","value":"human"}}
            item["claims"]={"P279":[claim(
                "Q5","Q2250224",
                qualified=self.options.get("qualified",False),
                wrong_witness=self.options.get("wrong_witness",False))]}
        if qid=="P31":
            item["labels"]={"en":{"language":"en","value":"instance of"}}
        if qid=="P279":
            item["labels"]={"en":{"language":"en","value":"subclass of"}}
        if qid=="Q2250224":
            item["labels"]={"zh-hans":{"language":"zh-hans","value":"原文对象"}}
        if self.options.get("no_source_label") and qid=="Q42":
            item["labels"]={"x":{"language":"x","value":"not qualified"}}
        if self.options.get("revision_drift") and qid=="Q42" and "?revision=" in url:
            item["lastrevid"]=12346
        if self.options.get("source_label_drift") and qid=="Q42" and "?revision=" in url:
            item["labels"]["eo"]["value"]="altered provenance"
        return Response(json.dumps({"entities":{qid:item}},ensure_ascii=True).encode("utf-8"))


class F31(unittest.TestCase):
    def test_frozen_protocol_and_no_scheduled_or_native_changes(self):
        rule=preflight()
        self.assertEqual(rule["schema"],"yggdrasil.qtr01.f31.first-party-all-language-fact-custody.v1")
        self.assertEqual(rule["seed_qids"],list(SEEDS))
        self.assertEqual(rule["endpoints_max"],24)
        self.assertTrue(rule["scope_fences"]["no_native_recipient_model_weights"])

    def test_first_party_original_language_selection_never_translates(self):
        obj=entity("Q42")
        obj["labels"]={"la":{"language":"la","value":"Latin source"},
                       "eo":{"language":"eo","value":"Esperanto source"}}
        self.assertEqual(source_label(obj),{"source_language":"eo","label":"Esperanto source"})
        obj["labels"]["en"]={"language":"en","value":"English direct source"}
        self.assertEqual(source_label(obj)["source_language"],"en")
        obj["labels"]["en"]["language"]="fr"
        self.assertEqual(source_label(obj)["source_language"],"eo")
        obj["labels"]["x"]={"language":"x","value":"unsupported"}
        self.assertNotEqual(source_label(obj)["source_language"],"x")

    def test_source_only_multilingual_numeric_and_strong_symbolic_parity(self):
        op=Stub()
        result=capture(LiveEntityData(opener=op))
        c=result["matched_symbolic_numeric_control"]
        self.assertEqual(c["source_labeled_rows"],2)
        self.assertEqual(c["typed_integer_carrier_bytes"],24)
        self.assertEqual(c["actual_observed_twohop_queries"],1)
        self.assertTrue(c["canonical_cold_restore"])
        self.assertTrue(c["numeric_vs_equal_info_symbolic_2hop_parity"])
        self.assertEqual(result["source_inventory"]["seed_source_languages"],{"Q42":"eo","Q5":"en"})
        self.assertEqual(next(row["s_language"] for row in result["typed_source_rows"] if row["s"]=="Q42"),"eo")
        self.assertEqual({row["o_language"] for row in result["typed_source_rows"]},{"en","zh-hans"})
        self.assertEqual(len(result["source_request_receipts"]),2+2+1+8)
        self.assertFalse(result["scientific_pass"])
        self.assertFalse(result["native_recipient_model_weights_edited"])

    def test_wrong_witness_and_qualifiers_are_excluded_not_accepted(self):
        for options in ({"wrong_witness":True},{"qualified":True}):
            with self.subTest(options=options):
                data=capture(LiveEntityData(opener=Stub(**options)))
                self.assertEqual(data["matched_symbolic_numeric_control"]["source_labeled_rows"],1)
                self.assertEqual(data["matched_symbolic_numeric_control"]["actual_observed_twohop_queries"],0)

    def test_first_party_revision_drift_and_missing_all_languages_fail_closed(self):
        for options in ({"revision_drift":True},{"source_label_drift":True},{"no_source_label":True}):
            with self.subTest(options=options):
                with self.assertRaises(NotAdmitted):
                    capture(LiveEntityData(opener=Stub(**options)))

    def test_source_does_not_admit_unknown_seed(self):
        data={"Q42":entity("Q42",lang="eo",claims={"P31":[claim("Q42","Q5")]})}
        with self.assertRaises(NotAdmitted):
            witnessed_rows(data)


if __name__=="__main__":
    unittest.main()
