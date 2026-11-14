"""WSP89 structural and adversarial controls use invented IDs only, not DEV sources."""
from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from weights import (VERIFIED, DECOY, CORRECTION, DirectEvidenceWeights,
                     SymbolicEvidenceControl, FullyTrainedSigmoidControl)
from experiment import FIXTURE, RESERVED, decoy_events, correction_events, classify, study
from source import DATA, read_frozen


def fake(sub="Q1", pid="P36", obj="Q101", sid="Q1$fixture-a", rev=123):
    return {
        "subject": sub, "predicate": pid, "object": obj,
        "source_type": VERIFIED, "statement_id": sid, "revision": rev,
        "source_url": ("https://www.wikidata.org/wiki/Special:EntityData/"
                       + sub + ".json?revision=" + str(rev)),
    }


class WSP89StructuralTests(unittest.TestCase):
    def test_sealed_source_split(self):
        self.assertTrue(set(FIXTURE).isdisjoint(RESERVED))
        self.assertEqual((len(FIXTURE), len(RESERVED)), (8, 16))

    def test_numerical_graph_citation_parity_and_cold_state(self):
        r = fake()
        num, graph = DirectEvidenceWeights(), SymbolicEvidenceControl()
        num.assert_evidence(r)
        graph.assert_evidence(r)
        self.assertEqual(num.answer("Q1","P36"), graph.answer("Q1","P36"))
        self.assertEqual(num.answer("Q1","P36")["values"], ("Q101",))
        self.assertIsNone(num.answer("Q2","P36"))
        self.assertEqual(DirectEvidenceWeights.restore(num.snapshot()).snapshot(),
                         num.snapshot())

        weak = {**r, "object":"Q102", "statement_id":"CF-weak",
                "source_type": DECOY, "revision":None,
                "source_url":"counterfactual:wsp89:fixture:weak"}
        num.assert_evidence(weak)
        graph.assert_evidence(weak)
        self.assertEqual(num.answer("Q1","P36"), graph.answer("Q1","P36"))
        self.assertEqual(num.answer("Q1","P36")["values"], ("Q101",))

        num.retract_evidence("Q1$fixture-a")
        graph.retract_evidence("Q1$fixture-a")
        self.assertIsNone(num.answer("Q1","P36"))
        replacement = {**r, "object":"Q103", "statement_id":"CF-strong",
                       "source_type": CORRECTION, "revision":None,
                       "source_url":"counterfactual:wsp89:fixture:correction"}
        num.assert_evidence(replacement)
        graph.assert_evidence(replacement)
        self.assertEqual(num.answer("Q1","P36"), graph.answer("Q1","P36"))
        self.assertEqual(num.answer("Q1","P36")["values"], ("Q103",))
        with self.assertRaises(ValueError):
            num.retract_evidence("Q1$fixture-a")

    def test_snapshot_semantic_and_checksum_tamper(self):
        mem = DirectEvidenceWeights()
        mem.assert_evidence(fake())
        snap = json.loads(mem.snapshot())
        snap["payload"]["weights"]["Q1/P36"]["Q101"] = 4.0
        with self.assertRaises(ValueError):
            DirectEvidenceWeights.restore(json.dumps(snap))
        bad = fake(obj="Q999", sid="")
        with self.assertRaises(ValueError):
            mem.assert_evidence(bad)
        with self.assertRaises(ValueError):
            mem.assert_evidence(fake())

    def test_converged_baseline_train_fit(self):
        rows = [fake(sub=f"Q{i}", obj=f"Q{100+i}",
                     sid=f"Q{i}$test", rev=100+i)
                for i in (1, 2, 3)]
        trained = FullyTrainedSigmoidControl()
        trained.fit(rows)
        self.assertEqual(trained.training_accuracy, 1.0)
        self.assertTrue(all(trained.answer(r["subject"], "P36") ==
                            (r["object"],) for r in rows))
        self.assertIsNone(trained.answer("Q100", "P36"))

    def test_no_live_api_in_model_evaluation(self):
        self.assertIn("--reserved-dev-first-use", Path(__file__).with_name(
            "experiment.py").read_text())
        self.assertNotIn("urlopen", Path(__file__).with_name(
            "experiment.py").read_text())


class WSP89CC0SourceFixtureTests(unittest.TestCase):
    def test_collected_real_data_public_fixture(self):
        if not DATA.exists():
            self.skipTest("One-shot CC0 snapshot has not yet been captured")
        dataset = read_frozen()
        self.assertEqual(dataset["license"], "CC0-1.0")
        self.assertGreaterEqual(len(dataset["claims"]), 32)
        self.assertTrue(set(r["subject"] for r in dataset["claims"]) >= set(FIXTURE))
        result = classify(study(dataset,dev=False),dev=False)
        print("WSP89_PUBLIC_FIXTURE=" + json.dumps({
            "classification": result["classification"],
            "checks": result["checks"], "claims": result["stageA_training_claims"],
            "queries": result["stageA_queries"],
            "decoys_rejected": result["decoys_rejected"],
            "decoys_total": result["decoys_total"],
            "corrections": result["counterfactual_corrections_correct"],
            "cpu_ns": result["whole_process_cpu_ns"],
        },sort_keys=True),flush=True)
        self.assertEqual(result["classification"], "FIXTURE_FEASIBLE")


if __name__ == "__main__":
    unittest.main()
