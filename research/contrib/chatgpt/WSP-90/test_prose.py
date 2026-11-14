"""WSP90 public-only tests: no reserved DEV first-use and no live network."""
from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from source import DATA, read_frozen, expected_titles
from weights import (DirectWriter, TrainedLogistic, LexicalParserControl,
                     RetrievalControl, features, WIDTH)
from experiment import FIXTURE, RESERVED, evaluate, classify

CAPITAL=("Seabridge is the national capital of Northland. "
         "It serves as the seat of government and the largest city in Northland.")
OTHER=("Westbank is a coastal town in Northland known for its fishermen. "
       "It is the capital of Westbank District, one of the provinces of Northland.")

class WSP90ProseTests(unittest.TestCase):
    def test_source_split_and_no_heldout_leak(self):
        self.assertEqual(len(FIXTURE),8)
        self.assertEqual(len(RESERVED),12)
        self.assertEqual(len(expected_titles()),40)
        titles=lambda g:{r[k] for r in g for k in ("capital","control")}
        self.assertFalse(titles(FIXTURE)&titles(RESERVED))
        self.assertEqual(len(titles(FIXTURE)),16)
        self.assertEqual(len(titles(RESERVED)),24)

    def test_direct_numeric_evidence_and_unknown_abstention(self):
        mem=DirectWriter()
        mem.observe(CAPITAL,"Seabridge","Northland",True)
        mem.observe(OTHER,"Westbank","Northland",False)
        a=mem.score(CAPITAL,"Seabridge","Northland")
        b=mem.score(OTHER,"Westbank","Northland")
        self.assertGreater(a,b)
        self.assertIsNone(mem.score(OTHER,"Westbank","Unknown Country"))
        self.assertTrue(all(0<=i<WIDTH for i,_ in features(CAPITAL,"Seabridge","Northland")))
        with self.assertRaises(ValueError):
            mem.observe(CAPITAL,"Seabridge","Northland","yes")

    def test_checksum_cold_restore_and_tamper(self):
        writer=DirectWriter()
        writer.observe(CAPITAL,"Seabridge","Northland",True)
        original=writer.snapshot()
        self.assertEqual(DirectWriter.restore(original).snapshot(),original)
        bad=json.loads(original)
        key=next(iter(bad["payload"]["weights"]))
        bad["payload"]["weights"][key]=123.0
        with self.assertRaises(ValueError):
            DirectWriter.restore(json.dumps(bad))

    def test_conventional_trained_control_and_independent_baselines(self):
        train=[
            (CAPITAL,"Seabridge","Northland",True),
            (OTHER,"Westbank","Northland",False),
        ]
        sgd=TrainedLogistic()
        sgd.fit(train)
        self.assertGreaterEqual(sgd.train_accuracy,0.95)
        self.assertGreater(LexicalParserControl().score(CAPITAL,"Seabridge","Northland"),
                           LexicalParserControl().score(OTHER,"Westbank","Northland"))
        self.assertGreaterEqual(RetrievalControl().score(CAPITAL,"Seabridge","Northland"),0)

    def test_no_live_fetch_or_reserved_score_in_normal_tests(self):
        source=Path(__file__).with_name("experiment.py").read_text(encoding="utf-8")
        self.assertNotIn("urlopen",source)
        self.assertIn("prediction_hash_before_labels_sha256",source)
        self.assertIn("--reserved-dev-first-use",source)

    def test_wikipedia_public_fixture_only(self):
        if not DATA.exists():
            self.skipTest("WSP90 real source not yet captured")
        corpus=read_frozen()
        self.assertTrue(all(not any(k in d for k in
                            ("capital","control","is_capital","label"))
                            for d in corpus["documents"]))
        result=classify(evaluate(corpus,reserved=False),reserved=False)
        print("WSP90_PUBLIC_FIXTURE="+json.dumps({
            "classification":result["classification"],"checks":result["checks"],
            "scores":result["scores"],
            "initial_fixture_correct":result["first_six_train_label_correct"],
            "final_fixture_correct":result["final_train_label_correct"],
            "retention":result["old_training_pair_answers_retained"],
            "source_hash":result["source_file_documents_sha256"],
            "cpu_ns":result["whole_process_cpu_ns"]
        },sort_keys=True),flush=True)
        self.assertEqual(result["classification"],"PUBLIC_FIXTURE_FEASIBLE")

if __name__=="__main__":
    unittest.main()
