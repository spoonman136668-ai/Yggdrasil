"""WSP82 never first-uses registered/held-out developer cohorts in unit tests.

All 384-step training fixtures below are generated locally from an unrelated
explicit synthetic unit seed, without source.World creation or private oracle.
"""
from pathlib import Path
from random import Random
from types import SimpleNamespace
import json
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.append(str(HERE.parent / "WSP-81"))
from temporal_weights import PaidTemporalFeatureEditor
from independent_symbolic import IndependentTemporalSymbolic
from history_adam import _inputs, EndToEndAdamControl, RESTARTS, MAX_STEPS
from history_weights import PaidHistoryNumeric
from experiment import (validate_readonly_custody, classify, PRE_COMMIT,
                        FROZEN, CONTEXTS)
import source


def synthetic_fixture(extra=True, offset=2):
    rng = Random(202611)
    current = (0,) * 6
    history = []
    rows = []
    for index in range(384):
        action = rng.randrange(6)
        next_state = list(current)
        next_state[action] ^= 1
        if extra and len(history) >= 2 and history[-2] == history[-1]:
            next_state[(action + offset) % 6] ^= 1
        next_state = tuple(next_state)
        rows.append(SimpleNamespace(
            before=current, action=action, after=next_state, action_cost=1))
        current = next_state
        history.append(action)
    return rows


def expected_transition(state, a, history, extra=True, offset=2):
    out = list(state)
    out[a] ^= 1
    if extra and len(history) >= 2 and history[-1] == history[-2]:
        out[(a + offset) % 6] ^= 1
    return tuple(out)


class TemporalFeatureDeveloperTests(unittest.TestCase):
    def test_frozen_preregistered_before_implementation_and_no_science(self):
        sha, protocol = validate_readonly_custody()
        self.assertEqual(len(sha), 40)
        self.assertEqual(PRE_COMMIT, "4bff9a0d576e04d8123a902545680d2b78e176da")
        self.assertEqual(len(FROZEN), 9)
        self.assertEqual([x["seed"] for x in protocol["source"]["cohort"]],
                         [9701,9702,9703,9704])
        self.assertFalse(protocol["authority"]["registered_first_use"])
        self.assertTrue(protocol["source"]["no_reset"])

    def test_out_of_cohort_and_budget_are_rejected(self):
        for bad in (5601,5616,9401,9699,9705,9001):
            with self.assertRaises(PermissionError):
                source.World(bad)
        for step in (-1,384):
            with self.assertRaises(PermissionError):
                source.fixed_action(9701,step)

    def test_direct_weights_fit_lag_relation_then_cold_predict(self):
        for extra in (True,False):
            rows=synthetic_fixture(extra=extra)
            m=PaidTemporalFeatureEditor()
            with self.assertRaises(ValueError):
                m.compile()
            for row in rows:
                m.charge(row.before,row.action,row.after,row.action_cost)
            diag=m.compile()
            self.assertEqual(diag["paid_actions"],384)
            cold=PaidTemporalFeatureEditor.restore(m.snapshot())
            self.assertIsNone(cold._rows)
            independently=IndependentTemporalSymbolic(rows)
            for hist in CONTEXTS:
                for state in source.STATES:
                    for action in source.ACTIONS:
                        truth=expected_transition(state,action,hist,extra)
                        self.assertEqual(cold.predict(state,action,hist),truth)
                        self.assertEqual(independently.predict(state,action,hist),truth)
            self.assertEqual(cold.snapshot(),m.snapshot())

    def test_old_predefined_WSP81_parity_trigger_model_is_out_of_class(self):
        rows=synthetic_fixture(extra=True)
        old=PaidHistoryNumeric()
        for row in rows:
            old.charge(row.before,row.action,row.after,row.action_cost)
        with self.assertRaises(ValueError):
            old.compile()

    def test_corrupted_numeric_weight_refused_even_when_forged(self):
        rows=synthetic_fixture(extra=True)
        m=PaidTemporalFeatureEditor()
        for row in rows:
            m.charge(row.before,row.action,row.after)
        m.compile()
        snapshot=m.snapshot()
        for bad in (snapshot[:-1],
                    snapshot.replace('"charges":384','"charges":144',1),
                    snapshot.replace('"feature_count":135','"feature_count":42',1)):
            with self.assertRaises(ValueError):
                PaidTemporalFeatureEditor.restore(bad)
        cold=PaidTemporalFeatureEditor.restore(snapshot)
        with self.assertRaises(ValueError):
            cold.charge((0,)*6,0,(0,)*6)
        with self.assertRaises(ValueError):
            m.charge(m.current,0,m.current)

    def test_public_history_neural_shape_and_frozen_real_training_budget(self):
        x=_inputs((0,)*6,2,(3,3))
        self.assertEqual(len(x),25)
        self.assertEqual(x[-1],1.0)
        self.assertEqual(_inputs((1,)*6,2,())[24],0.0)
        self.assertEqual(RESTARTS,3)
        self.assertEqual(MAX_STEPS,6000)
        with self.assertRaises(ValueError):
            EndToEndAdamControl(9701).fit([])

    def test_frozen_negative_classification_does_not_self_pass(self):
        p=json.loads((HERE/"prereg.json").read_text())
        r=[]
        for spec in p["source"]["cohort"]:
            score={"numeric":{"correct":768,"wrong_confident":768,"unpaid_correct":0},
                   "memoryless":{"correct":1536}}
            r.append({
                "seed":spec["seed"],"family":spec["family"],
                "old_WSP81_model_rejected":False,
                "scores":score,
                "numeric_info":{"nonconstant_temporal_weight_selected":False},
                "symbolic_exact_parity":True,
                "numeric_cold_readout_match":True,
                "paid_actions":384,
                "Adam_receipt":{"fully_trained":True},
            })
        got=classify(r,p)
        self.assertEqual(got["classification"],
                         "DEV_TEMPORAL_FEATURE_DIAGNOSTICS_NEGATIVE")
        self.assertFalse(got["checks"]["old_WSP81_misspecified"])
        self.assertFalse(got["checks"]["novel_no_confident_errors"])

    def test_learners_cannot_import_private_evaluator(self):
        for path in ("temporal_weights.py","independent_symbolic.py",
                     "history_adam.py"):
            c=(HERE/path).read_text("utf8")
            self.assertNotIn("import source",c)
            self.assertNotIn("from source import",c)
            self.assertNotIn("source.World",c)
            self.assertNotIn("_truth(",c)
        program=(HERE/"experiment.py").read_text()
        self.assertEqual(program.count("world._truth("),1)
        self.assertIn("score_only_after_freeze(world, freeze)",program)


if __name__ == "__main__":
    unittest.main()
