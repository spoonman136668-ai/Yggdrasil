"""WSP93 structure and source qualification, public-only—not reserved first-use."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from source import CORPUS,LABELS,verify
from weights import (DirectBinding,ConventionalLogistic,AnchorRetrieval,
                     SymbolicTypeControl,RandomCandidate,features,
                     anchors,intent,shape,spans)
from experiment import evaluate,classify,validated_proof

CONTEXT=("In the year 1967, the astronomer Mira discovered the object near the "
         "lake. In 1973, the discovery was published by the institute. "
         "Mira conducted several other careful experiments.")
QUESTION="Who discovered the object?"
START=CONTEXT.index("Mira")
FAKE={
    "cohort":"training","qa_id":"wsp93-fixture-001",
    "article_title":"Fixture astronomy","question":QUESTION,
    "context":CONTEXT,
    "context_sha256":hashlib.sha256(CONTEXT.encode("utf-8")).hexdigest(),
    "article_url":"https://en.wikipedia.org/wiki/Fixture_astronomy",
    "wikipedia_contributors_url":"https://en.wikipedia.org/w/index.php?title=Fixture_astronomy&action=history",
    "license":"CC BY-SA 4.0",
}
GOLD={"qa_id":FAKE["qa_id"],"cohort":"training","answer_text":"Mira","answer_start":START}

class WSP93Tests(unittest.TestCase):
    def test_raw_evidence_binding_and_article_custody(self):
        self.assertEqual(intent("Who discovered an object?"),"who")
        self.assertEqual(intent("How many were discovered?"),"how_many")
        self.assertEqual(shape("Mira"),"proper")
        self.assertTrue(anchors(QUESTION,CONTEXT))
        self.assertTrue(any(a==START and v=="Mira" for a,b,v in spans(CONTEXT)))
        f=features(QUESTION,CONTEXT,START,START+4)
        g=features("When discovered the object?",CONTEXT,START,START+4)
        self.assertNotEqual(f,g)
        self.assertGreater(len(f),8)
        self.assertLess(len(features(QUESTION,CONTEXT,START,START+4,True)),len(f))

    def test_program_edits_cold_restore_unknown_source(self):
        m=DirectBinding();self.assertIsNone(m.answer(FAKE))
        m.observe(FAKE,GOLD)
        self.assertGreater(len(m.weights),5)
        snap=m.snapshot()
        self.assertEqual(DirectBinding.restore(snap).snapshot(),snap)
        p=m.answer(FAKE)
        if p is not None:
            self.assertTrue(validated_proof(p,FAKE))
        self.assertIsNone(m.answer({**FAKE,"context":"unverified altered source"}))
        self.assertIsNone(m.answer({**FAKE,"question":""}))
        altered=json.loads(snap)
        altered["payload"]["observed"]+=1
        with self.assertRaises(ValueError):
            DirectBinding.restore(json.dumps(altered))

    def test_controls_receive_same_article_and_no_answer_choice(self):
        logistic=ConventionalLogistic()
        logistic.fit([(FAKE,GOLD)])
        for method in (logistic,AnchorRetrieval(),
                       SymbolicTypeControl(),RandomCandidate()):
            output=method.answer(FAKE)
            self.assertIsNotNone(output)
            self.assertTrue(validated_proof(output,FAKE))

    def test_experiment_does_not_fetch_live_source(self):
        body=(HERE/"experiment.py").read_text(encoding="utf-8")
        self.assertNotIn("urlopen",body)
        self.assertIn("prediction_sha256_before_scoring",body)
        self.assertIn("--reserved-dev-first-use",body)

    def test_frozen_label_separation_and_counts(self):
        if not CORPUS.exists() or not LABELS.exists():
            self.skipTest("SQuAD source not yet captured")
        receipt=verify()
        self.assertEqual(receipt["rows"],128)
        self.assertEqual(receipt["cohorts"],{"training":72,"public":24,"reserved":32})
        dataset=json.loads(CORPUS.read_text(encoding="utf-8"))
        self.assertFalse(any("answer_start" in r or "answer_text" in r
                             for r in dataset["records"]))
        self.assertEqual(len({r["article_title"] for r in dataset["records"]}),26)

    def test_authentic_public_outcome_positive_or_negative(self):
        if not CORPUS.exists() or not LABELS.exists():
            self.skipTest("SQuAD source not yet captured")
        report=classify(evaluate(reserved=False),reserved=False)
        print("WSP93_PUBLIC_FIXTURE="+json.dumps({
            "classification":report["classification"],
            "checks":report["checks"],
            "scores":report["exact"],
            "train":report["final_fit"],
            "conventional_train":report["ordinary_training_exact"],
            "retained":report["old_exact_retained"],
            "gold_span_coverage":report["source_answer_reachable"],
            "cpu_ns":report["whole_cpu_ns"],
            "source_sha":report["source_sha256"],
        },sort_keys=True),flush=True)
        frozen=json.loads((HERE/"prereg.json").read_text(encoding="utf-8"))
        threshold=frozen["criteria"]["public_min_exact"]
        self.assertEqual(report["checks"]["public_positive_transfer"],
                         report["exact"]["direct_binding"]>=threshold)
        expected=("PUBLIC_BINDING_FEASIBLE" if all(report["checks"].values())
                  else "PUBLIC_BINDING_NEGATIVE")
        self.assertEqual(report["classification"],expected)
        self.assertEqual(report["questions"],24)

if __name__=="__main__":unittest.main()
