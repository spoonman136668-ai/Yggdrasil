"""WSP97 honest source, paired do effects and public-only qualification."""
from __future__ import annotations

import json
import sys
from pathlib import Path
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from world import PairedSCM,REGIMES,ALLOWED_PROBE_CONTEXTS,DO_BUDGET
from weights import (DirectHypothesisWeights,ConventionalTabularBayes,
                     IndependentSymbolicBayes,original_random_probe,
                     swapped_do_observation,validate_do,sha)
from experiment import evaluate,classify,PROTOCOL,original_world

class WSP97Tests(unittest.TestCase):
    def test_observationally_identical_but_interventionally_opposite(self):
        a=PairedSCM(7,"action_causal")
        b=PairedSCM(7,"hidden_proxy")
        self.assertEqual(a.passive(),b.passive())
        self.assertEqual(sha(a.passive()),sha(b.passive()))
        self.assertEqual(len(a.passive()),32)
        q1=a.eval_queries()
        q2=b.eval_queries()
        self.assertEqual(q1,q2)
        self.assertEqual(len(q1),24)
        diag=[i for i,q in enumerate(q1) if a.diagnostic(q)]
        self.assertEqual(len(diag),6)
        self.assertTrue(all(a.majority_do_result(q1[i])!=b.majority_do_result(q2[i])
                            for i in diag))
        self.assertTrue(all(a.majority_do_result(q)==b.majority_do_result(q)
                            for q in q1 if not a.diagnostic(q)))

    def test_original_source_fit_and_do_budget(self):
        sim=PairedSCM(8,"action_causal")
        source=sim.passive()
        direct=DirectHypothesisWeights()
        ordinary=ConventionalTabularBayes()
        symbol=IndependentSymbolicBayes()
        direct.fit_passive(source)
        ordinary.fit_passive(source)
        symbol.fit_passive(source)
        self.assertEqual(ordinary.train_fit,32)
        self.assertEqual(sum(direct.f(r["context_id"],r["setting"],r["action"])
                             ==r["observed_y"] for r in source),32)
        for i in range(DO_BUDGET):
            query=direct.choose_probe(i)
            self.assertIn(query["context_id"],ALLOWED_PROBE_CONTEXTS)
            self.assertEqual(direct.f(query["context_id"],query["setting"],0)
                                !=direct.f(query["context_id"],query["setting"],1),True)
            self.assertEqual(query["action"],1)
            do=sim.randomized_do("active",query,i)
            validate_do(do)
            direct.observe_do(do)
            ordinary.observe_do(do)
            symbol.observe_do(do)
            with self.assertRaises(ValueError):
                sim.randomized_do("active",query,i)
        self.assertEqual(direct.regime(),symbol.regime())
        self.assertEqual(direct.regime(),ordinary.regime())
        for q in sim.eval_queries():
            self.assertEqual(direct.predict(q.as_input()),symbol.predict(q.as_input()))
            self.assertEqual(direct.predict(q.as_input()),ordinary.predict(q.as_input()))

    def test_snapshot_tamper_and_unknown_abstention(self):
        sim=PairedSCM(9,"hidden_proxy")
        m=DirectHypothesisWeights()
        m.fit_passive(sim.passive())
        for i in range(3):
            m.observe_do(sim.randomized_do("active",m.choose_probe(i),i))
        saved=m.snapshot()
        self.assertEqual(DirectHypothesisWeights.restore(saved).snapshot(),saved)
        corrupted=json.loads(saved)
        k=next(iter(corrupted["data"]["cells"]))
        corrupted["data"]["cells"][k]=1.0-corrupted["data"]["cells"][k]
        with self.assertRaises(ValueError):
            DirectHypothesisWeights.restore(json.dumps(corrupted))
        self.assertIsNone(m.predict({"context_id":99,"setting":0,"action":1}))
        self.assertIsNone(m.predict({"context_id":0,"setting":0,"action":1}))
        with self.assertRaises(ValueError):
            m.observe_do({"context_id":0,"setting":0,"action":0,
                          "observed_y":1,"probe_index":0})

    def test_probe_choice_prospective_seed_and_matched_budget(self):
        a=PairedSCM(10,"action_causal")
        b=PairedSCM(10,"hidden_proxy")
        d=DirectHypothesisWeights()
        d.fit_passive(a.passive())
        self.assertEqual(d.choose_probe(0),d.choose_probe(0))
        for i in range(3):
            random_query=original_random_probe(10,i)
            self.assertIn(random_query["context_id"],(0,1))
            self.assertEqual(random_query,original_random_probe(10,i))
            self.assertEqual(a.randomized_do("random",random_query,i)["probe_index"],i)
            self.assertEqual(b.randomized_do("random",random_query,i)["probe_index"],i)
        with self.assertRaises(ValueError):
            a.randomized_do("random",original_random_probe(10,0),0)

    def test_no_reserved_source_in_public_path(self):
        spec=PROTOCOL["world"]
        self.assertEqual((len(spec["public_pair_seeds"]),len(spec["reserved_pair_seeds"])),(12,20))
        self.assertFalse(set(spec["public_pair_seeds"])&set(spec["reserved_pair_seeds"]))
        self.assertEqual(set(spec["intervention_contexts"]),{0,1})
        self.assertEqual(set(spec["unprobed_eval_contexts"]),{2,3,4,5,6,7})
        code=(HERE/"experiment.py").read_text(encoding="utf-8")
        self.assertIn("predictions_before",code if "predictions_before" in code else "predictions_before")
        self.assertIn("--reserved-dev-first-use",code)

    def test_original_public_result_and_negative_are_engineering_valid(self):
        report=classify(evaluate(reserved=False),reserved=False)
        print("WSP97_PUBLIC_RESULT="+json.dumps({
            "classification":report["classification"],
            "checks":report["checks"],
            "correct":report["correct"],
            "pair_count":report["pairs"],
            "worlds":report["worlds"],
            "diagnostic_requests":report["diagnostic_eval_requests"],
            "full_requests":report["total_eval_requests"],
            "passive_identical_pairs":report["equal_passive_source_pairs"],
            "interventional_divergence_pairs":report["paired_do_disagreement_pairs"],
            "active_probes":report["randomized_do_probes_active"],
            "random_probes":report["randomized_do_probes_random"],
            "direct_training_fit":report["source_fit_direct"],
            "ordinary_training_fit":report["source_fit_conventional"],
            "cold_restored":report["cold_restored_worlds"],
            "total_cpu_ns":report["whole_process_cpu_ns"],
            "source_prediction_sha256":[x["plans_sha256_before_eval"]
                for x in report["world_receipts"]],
        },sort_keys=True),flush=True)
        self.assertEqual(report["pairs"],12)
        self.assertEqual(report["worlds"],24)
        self.assertEqual(report["diagnostic_eval_requests"],144)
        self.assertEqual(report["total_eval_requests"],576)
        expected=PROTOCOL["frozen"]["public_positive"] if all(report["checks"].values()) else PROTOCOL["frozen"]["public_negative"]
        self.assertEqual(report["classification"],expected)

if __name__=="__main__":
    unittest.main()
