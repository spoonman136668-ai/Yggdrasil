"""WSP84 operator-induction unit tests: ZERO frozen cohort consumption.

Synthetic fixtures are generated from a separate unit-only Random(4782)
with different target rule families. The WSP84 developer source.World is
NEVER instantiated for 10011..10014 by these unit tests.
"""
from pathlib import Path
from random import Random
from types import SimpleNamespace
import json
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
sys.path.append(str(HERE.parent/"WSP-83"))
sys.path.append(str(HERE.parent/"WSP-82"))

from operator_weights import PaidOperatorInducer,FEATURES
from independent_symbolic import IndependentTruthTableControl
from xor_weights import PaidXorComposer
from history_adam64 import HIDDEN,INPUTS,RESTARTS,MAX_STEPS,EndToEndAdamControl
from experiment import readonly_admission,classify,PRE_COMMIT,FROZEN
import source


MASKS=((0,1,2),(1,3,5),(0,2,4))
TARGET=5


def synthetic_effect(action,history,operator="parity"):
    slots=(action,history[-1] if history else None,
           history[-2] if len(history)>=2 else None)
    bits=[int(val is not None and val in allowed)
          for val,allowed in zip(slots,MASKS)]
    if operator=="parity":
        return bits[0]^bits[1]^bits[2]
    if operator=="majority":
        return int(sum(bits)>=2)
    if operator=="none":
        return 0
    raise ValueError("unit-only unsupported operator")


def transition(state,action,history,operator):
    out=list(state)
    out[action]^=1
    if synthetic_effect(action,history,operator):
        out[TARGET]^=1
    return tuple(out)


def fixture(operator):
    rng=Random(4782)
    state=(0,)*6
    actions=[]
    rows=[]
    for _ in range(384):
        a=rng.randrange(6)
        after=transition(state,a,actions,operator)
        rows.append(SimpleNamespace(before=state,action=a,
                                    after=after,action_cost=1))
        actions.append(a)
        state=after
    return tuple(rows)


class FrozenOperatorDevelopmentTests(unittest.TestCase):
    def test_preregistered_before_code_and_source_custody(self):
        head,protocol=readonly_admission()
        self.assertEqual(len(head),40)
        self.assertEqual(PRE_COMMIT,"5f6cef2e6d39f14cb411c2b046557fb6415fe776")
        self.assertEqual(len(FROZEN),9)
        self.assertEqual(protocol["source_private"]["total_paid_actions"],1536)
        self.assertEqual(protocol["source_private"]["query_count_total"],66048)
        self.assertFalse(protocol["authority"]["registered_scientific_first_use"])

    def test_source_does_not_admit_protected_or_out_of_cohort(self):
        for seed in (5601,5616,10010,10015,9901,0):
            with self.assertRaises(PermissionError):
                source.World(seed)
        for step in (-1,384):
            with self.assertRaises(PermissionError):
                source.fixed_action(10011,step)
        self.assertEqual(len(source.CONTEXTS),43)

    def test_new_operator_learned_with_no_named_operator_in_model(self):
        self.assertEqual(len(FEATURES),60)
        for operator in ("parity","majority","none"):
            rows=fixture(operator)
            learned=PaidOperatorInducer()
            old=PaidXorComposer()
            for row in rows:
                learned.charge(row.before,row.action,row.after,row.action_cost)
                old.charge(row.before,row.action,row.after,row.action_cost)
            info=learned.compile()
            cold=PaidOperatorInducer.restore(learned.snapshot())
            symbolic=IndependentTruthTableControl(rows)
            self.assertEqual(info["charged_public_actions"],384)
            self.assertTrue(info["all_selected_table_cells_physically_observed"])
            if operator in ("parity","majority"):
                self.assertGreaterEqual(info["three_input_operator_output_count"],1)
                with self.assertRaises(ValueError):
                    old.compile()
            else:
                self.assertEqual(info["three_input_operator_output_count"],0)
                old.compile()
            self.assertIsNone(cold._rows)
            for history in source.CONTEXTS:
                for state in source.STATES:
                    for action in source.ACTIONS:
                        expected=transition(state,action,history,operator)
                        self.assertEqual(cold.predict(state,action,history),expected)
                        self.assertEqual(symbolic.predict(state,action,history),expected)
            self.assertEqual(cold.snapshot(),learned.snapshot())

    def test_public_charge_continuity_overbudget_and_cold_tamper_refused(self):
        rows=fixture("parity")
        learner=PaidOperatorInducer()
        with self.assertRaises(ValueError):
            learner.charge((1,)*6,0,(0,)*6)
        with self.assertRaises(ValueError):
            learner.compile()
        for row in rows:
            learner.charge(row.before,row.action,row.after,row.action_cost)
        learner.compile()
        with self.assertRaises(ValueError):
            learner.charge(rows[-1].after,0,rows[-1].after)
        snapshot=learner.snapshot()
        for corrupt in (snapshot[:-1],
                        snapshot.replace('"charges":384','"charges":144',1),
                        snapshot.replace('"schema":"wsp84','"schema":"invalid',1),
                        snapshot.replace('"mask_weights"','"secret_masks"',1)):
            with self.assertRaises(ValueError):
                PaidOperatorInducer.restore(corrupt)
        restored=PaidOperatorInducer.restore(snapshot)
        with self.assertRaises(ValueError):
            restored.charge((0,)*6,0,(0,)*6)

    def test_stronger_true_history_Adam_frozen_training_config(self):
        self.assertEqual(INPUTS,25)
        self.assertEqual(HIDDEN,64)
        self.assertEqual(RESTARTS,3)
        self.assertEqual(MAX_STEPS,6000)
        with self.assertRaises(ValueError):
            EndToEndAdamControl(0).fit([])

    def test_frozen_threshold_negative_really_fails(self):
        p=json.loads((HERE/"prereg.json").read_text("utf8"))
        data=[]
        for spec in p["source_private"]["new_unregistered_cohort"]:
            data.append({
                "family":spec["family"],"old_WSP83_rejected":False,
                "paid_actions":384,"cold_equal":True,"symbolic_parity":True,
                "operator":{
                    "three_input_operator_output_count":0,
                    "all_selected_table_cells_physically_observed":True,
                },
                "Adam64":{"fully_trained":True},
                "scores":{
                    "numeric":{"correct":1000,"wrong_confident":300,
                               "never_paid_state_action_correct":0},
                    "memoryless":{"correct":16512},
                },
            })
        got=classify(data,p)
        self.assertEqual(got["classification"],
                         "DEV_LEARNED_OPERATOR_DIAGNOSTICS_NEGATIVE")
        self.assertFalse(got["checks"]["old_WSP83_incompatible_new"])
        self.assertFalse(got["checks"]["new_operator_support_3"])
        self.assertFalse(got["checks"]["no_confident_wrong_novel"])

    def test_numeric_and_symbolic_learners_never_import_evaluator_private_rule(self):
        for name in ("operator_weights.py","independent_symbolic.py",
                     "history_adam64.py"):
            content=(HERE/name).read_text("utf8")
            for forbidden in ("import source","from source import",
                              "source.World","source._transition",
                              "private_truth(","_secret_balanced_mask"):
                self.assertNotIn(forbidden,content)
        harness=(HERE/"experiment.py").read_text("utf8")
        self.assertEqual(harness.count("world.private_truth("),1)
        self.assertIn("evaluate_private_postfreeze(world,frozen)",harness)


if __name__=="__main__":
    unittest.main()
