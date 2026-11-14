"""WSP91 structural and public-only source fixtures. Reserved DEV untouched."""
from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
from source import DATA,read_frozen,expected_titles
from weights import (spans,raw_context,learning_examples,DirectSpanWriter,
                     TrainedSpanLogistic,SymbolicParser,LexicalCue,WIDTH)
from experiment import TRAIN,PUBLIC,DEV,RELATIONS,evaluate,classify,proof

FAKE_DOC={
    "requested_title":"Inventium",
    "text":"Inventium is a fictional chemical element; it has symbol Iv and atomic number 52. "
           "It was observed under controlled laboratory conditions.",
    "page_id":1234,"reported_revision_id":123456,
    "source_page_url":"https://en.wikipedia.org/wiki/Inventium",
    "text_sha256":"fixture_fake_hash","license":"CC BY-SA 4.0",
}

class WSP91StructuralTests(unittest.TestCase):
    def test_fixed_disjoint_cohorts(self):
        self.assertEqual((len(TRAIN),len(PUBLIC),len(DEV)),(12,8,16))
        sets=[{x["title"] for x in pool} for pool in (TRAIN,PUBLIC,DEV)]
        self.assertEqual(len(expected_titles()),36)
        self.assertFalse(sets[0]&sets[1] or sets[0]&sets[2] or sets[1]&sets[2])

    def test_raw_character_candidates_and_actual_offsets(self):
        text=FAKE_DOC["text"]
        symbols=spans(text,"symbol")
        numbers=spans(text,"atomic_number")
        self.assertTrue(any(text[i:j]=="Iv" for i,j,_ in symbols))
        self.assertTrue(any(text[i:j]=="52" for i,j,_ in numbers))
        self.assertEqual(spans(text,"unregistered_relation"),())
        self.assertTrue(all(0<=idx<WIDTH for _,_,_,vec in
            tuple((i,j,v,raw_context(text,"symbol",i,j)) for i,j,v in symbols)
            for idx,_ in vec))
        with self.assertRaises(ValueError):
            learning_examples(text,"atomic_number","900")

    def test_direct_context_learning_and_span_source_custody(self):
        direct=DirectSpanWriter()
        direct.observe(FAKE_DOC["text"],"symbol","Iv")
        direct.observe(FAKE_DOC["text"],"atomic_number","52")
        self.assertEqual(direct.observed_fields,2)
        self.assertTrue(direct.occupied_weights()>0)
        for relation in RELATIONS:
            pred=direct.extract(FAKE_DOC,relation)
            if pred is not None:
                self.assertTrue(proof(pred,FAKE_DOC))
                self.assertEqual(FAKE_DOC["text"][pred["start"]:pred["end"]],
                                 pred["value"])
        self.assertIsNone(direct.extract(FAKE_DOC,"unknown"))
        self.assertIsNone(direct.extract({"text":""},"symbol"))

    def test_snapshot_recovery_tamper_and_no_gradient_candidate(self):
        model=DirectSpanWriter()
        model.observe(FAKE_DOC["text"],"symbol","Iv")
        snapshot=model.snapshot()
        self.assertEqual(DirectSpanWriter.restore(snapshot).snapshot(),snapshot)
        tampered=json.loads(snapshot)
        tampered["payload"]["observed_fields"]+=1
        with self.assertRaises(ValueError):
            DirectSpanWriter.restore(json.dumps(tampered))

    def test_fully_trained_and_independent_symbolic_control(self):
        rows=((FAKE_DOC["text"],"symbol","Iv"),
              (FAKE_DOC["text"],"atomic_number","52"))
        ordinary=TrainedSpanLogistic()
        ordinary.fit(rows)
        self.assertEqual(ordinary.extract(FAKE_DOC,"symbol")["value"],"Iv")
        self.assertEqual(ordinary.extract(FAKE_DOC,"atomic_number")["value"],"52")
        symbolic=SymbolicParser()
        lexical=LexicalCue()
        for relation,expected in (("symbol","Iv"),("atomic_number","52")):
            self.assertEqual(symbolic.extract(FAKE_DOC,relation)["value"],expected)
            self.assertIsNotNone(lexical.extract(FAKE_DOC,relation))

    def test_public_fixture_source_and_strict_scoring(self):
        if not DATA.exists():
            self.skipTest("Exact original Wikipedia source is not yet frozen")
        corpus=read_frozen()
        self.assertTrue(all("symbol" not in page and "atomic_number" not in page
                            for page in corpus["documents"]))
        report=classify(evaluate(corpus,reserved=False),reserved=False)
        print("WSP91_PUBLIC_FIXTURE="+json.dumps({
            "classification":report["classification"],
            "checks":report["checks"],
            "scores":report["correct_counts"],
            "initial_fit":report["first_training_exact"],
            "final_fit":report["final_training_exact"],
            "ordinary_train_fit":report["trained_conventional_train_exact"],
            "retained":report["first_16_fields_retained_exact"],
            "source_sha":report["source_documents_sha256"],
            "cpu_ns":report["whole_process_CPU_ns"],
            "fixture_errors":[x for x in report["per_question"]
                              if x["predicted"]["direct_numeric"]!=x["expected"]],
            "training_fields_not_present":[],
        },sort_keys=True),flush=True)
        self.assertEqual(report["classification"],"PUBLIC_FIXTURE_FEASIBLE")

if __name__=="__main__":
    unittest.main()
