"""WSP92 negative and source custody tests; PUBLIC fixture only, never DEV."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from source import CORPUS,LABELS,verify
from weights import (span_candidates,features,supervision,
                     DirectQuestionSpanWriter,FullyTrainedLogistic,
                     RetrievalCharControl,SymbolicCueControl,RandomSpanControl)
from experiment import classify,evaluate,proof

CTX="The source states that the mineral was discovered by Ada in 1852. It is a useful example of attributed information."
QUESTION="Who discovered the mineral?"
START=CTX.index("Ada")
ITEM={"cohort":"training","qa_id":"fixture-01",
      "article_title":"Mineral Test","context":CTX,
      "context_sha256":hashlib.sha256(CTX.encode("utf-8")).hexdigest(),
      "question":QUESTION,"article_url":"https://en.wikipedia.org/wiki/Mineral",
      "wikipedia_contributors_url":"https://en.wikipedia.org/w/index.php?title=Mineral&action=history",
      "license":"CC BY-SA 4.0"}
GOLD={"answer_start":START,"answer_text":"Ada","qa_id":"fixture-01","cohort":"training"}

class WSP92StructuralTests(unittest.TestCase):
    def test_raw_span_coverage_and_real_offsets(self):
        all_candidates=span_candidates(CTX)
        self.assertTrue(any(a==START and x=="Ada" for a,b,x in all_candidates))
        self.assertTrue(all(CTX[a:b]==v for a,b,v in all_candidates))
        self.assertTrue(len(features(QUESTION,CTX,START,START+3))>10)
        with self.assertRaises(ValueError):
            supervision(QUESTION,CTX,"fixture-01",START,"Nonexistent")

    def test_direct_weight_programming_and_source_proof(self):
        m=DirectQuestionSpanWriter()
        self.assertIsNone(m.answer(ITEM))
        m.observe(ITEM,GOLD)
        self.assertEqual(m.observed,1)
        self.assertGreater(len(m.weights),5)
        p=m.answer(ITEM)
        if p:
            self.assertTrue(proof(p,ITEM))
            self.assertEqual(p["answer"],CTX[p["start"]:p["end"]])
        self.assertIsNone(m.answer({**ITEM,"context":"unauthorized text"}))
        self.assertIsNone(m.answer({**ITEM,"question":""}))

    def test_exact_state_restore_and_tamper(self):
        m=DirectQuestionSpanWriter()
        m.observe(ITEM,GOLD)
        snap=m.snapshot()
        self.assertEqual(DirectQuestionSpanWriter.restore(snap).snapshot(),snap)
        changed=json.loads(snap)
        changed["payload"]["observed"]+=1
        with self.assertRaises(ValueError):
            DirectQuestionSpanWriter.restore(json.dumps(changed))

    def test_ordinary_comparator_and_baselines(self):
        model=FullyTrainedLogistic()
        model.fit([(ITEM,GOLD)])
        p=model.answer(ITEM)
        self.assertIsNotNone(p)
        self.assertTrue(proof(p,ITEM))
        for control in (RetrievalCharControl(),SymbolicCueControl(),
                        RandomSpanControl()):
            x=control.answer(ITEM)
            self.assertTrue(proof(x,ITEM))

    def test_data_separation_and_public_only_mode(self):
        if not CORPUS.exists() or not LABELS.exists():
            self.skipTest("one-shot SQuAD snapshot not yet captured")
        receipt=verify()
        d=json.loads(CORPUS.read_text(encoding="utf-8"))
        self.assertEqual(len(d["records"]),202)
        self.assertFalse(any("answer_start" in q or "answer_text" in q
                             for q in d["records"]))
        self.assertEqual(receipt["rows"],202)

    def test_original_public_fixture(self):
        if not CORPUS.exists() or not LABELS.exists():
            self.skipTest("one-shot SQuAD snapshot not yet captured")
        receipt=classify(evaluate(reserved=False),reserved=False)
        print("WSP92_PUBLIC_FIXTURE="+json.dumps({
            "classification":receipt["classification"],
            "checks":receipt["checks"],"training_correct":receipt["final_train_exact"],
            "ordinary_train_correct":receipt["conventional_train_exact"],
            "retention":receipt["retained_old_exact"],"scores":receipt["correct_exact"],
            "coverage":receipt["oracle_candidate_reachable"],
            "source_sha":receipt["source_sha256"],
            "whole_cpu":receipt["whole_process_cpu_ns"],
        },sort_keys=True),flush=True)
        # A scientifically negative public result is a qualified outcome,
        # not a failing engineering harness. Do not change thresholds.
        self.assertIn(receipt["classification"],
                      ("PUBLIC_FIXTURE_FEASIBLE","PUBLIC_FIXTURE_NEGATIVE"))
        self.assertEqual(receipt["classification"],
                         "PUBLIC_FIXTURE_FEASIBLE" if all(receipt["checks"].values())
                         else "PUBLIC_FIXTURE_NEGATIVE")
        self.assertEqual(receipt["questions"],24)
        self.assertEqual(receipt["checks"]["public_fixture_nontrivial"],
                         receipt["correct_exact"]["direct_numeric"]>=
                         json.loads((HERE/"prereg.json").read_text())["frozen"]["min_candidate_public_exact"])

if __name__=="__main__":
    unittest.main()
