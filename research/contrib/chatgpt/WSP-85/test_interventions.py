"""Zero-frozen-cohort WSP85 developer engineering controls.

No WSP85 World(10201..10206) is instantiated by tests. Synthetic rows are
generated from a separate fixed Random(20085) mechanism and only public
action history is available to the intervention selector.
"""
from pathlib import Path
from random import Random
from types import SimpleNamespace
import json
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
sys.path.append(str(HERE.parent/"WSP-84"))
sys.path.append(str(HERE.parent/"WSP-83"))

from active_policy import HypothesisInterventionPolicy,MAX_POLICY_MODELS,REFIT_EVERY
from operator_weights import PaidOperatorInducer
from independent_symbolic import IndependentTruthTableControl
from history_adam64 import INPUTS,HIDDEN,RESTARTS,MAX_STEPS,EndToEndAdamControl
from experiment import admit_frozen_source,classify,PRE_COMMIT,FROZEN,ARMS
import source


MASKS=((0,1,2),(1,3,5),(0,2,4))
TARGET=2


def fixture(n=384,novel=True):
    rng=Random(20085)
    state=(0,)*6
    actions=[]
    events=[]
    for _ in range(n):
        action=rng.randrange(6)
        bits=[int(v is not None and v in mask)
              for v,mask in zip((action,actions[-1] if actions else None,
                                  actions[-2] if len(actions)>=2 else None),MASKS)]
        after=list(state)
        after[action]^=1
        if novel and sum(bits)>=2:
            after[TARGET]^=1
        after=tuple(after)
        events.append(SimpleNamespace(before=state,action=action,
                                      after=after,action_cost=1))
        state=after
        actions.append(action)
    return tuple(events),tuple(actions)


class WSP85EngineeringTests(unittest.TestCase):
    def test_prereg_custody_and_no_scientific_admission(self):
        sha,p=admit_frozen_source()
        self.assertEqual(len(sha),40)
        self.assertEqual(PRE_COMMIT,"3683e76c5b12d3be41b96ccc5bcc5ee6950b79bf")
        self.assertEqual(len(FROZEN),9)
        self.assertEqual(p["source"]["physically_paid_actions"],6912)
        self.assertFalse(p["authority"]["registered_scientific_first_use"])
        self.assertEqual(len(ARMS),3)

    def test_protected_and_extra_source_seeds_refused(self):
        for seed in (5601,5616,10200,10207,10011,1):
            with self.assertRaises(PermissionError):
                source.World(seed)
        for bad in (-1,144,384):
            with self.assertRaises(PermissionError):
                source.stage_a_action(10201,bad)
        for bad in (143,384):
            with self.assertRaises(PermissionError):
                source.random_stage_b_action(10201,bad)
            with self.assertRaises(PermissionError):
                source.passive_stage_b_action(10201,bad)
        self.assertEqual(len(source.CONTEXTS),43)

    def test_selector_only_uses_charged_public_trajectory(self):
        paid,actions=fixture(n=160)
        selector=HypothesisInterventionPolicy()
        self.assertEqual(MAX_POLICY_MODELS,512)
        self.assertEqual(REFIT_EVERY,12)
        with self.assertRaises(PermissionError):
            selector.choose(143,paid[:143],actions[:143])
        with self.assertRaises(ValueError):
            selector.choose(144,paid[:144],tuple(reversed(actions[:144])))
        a=selector.choose(144,paid[:144],actions[:144])
        self.assertIn(a,range(6))
        self.assertEqual(selector.refits,1)
        # After 12 new public charges the selector updates its hypotheses
        # from observed outcomes, not from private target/physics.
        b=selector.choose(156,paid[:156],actions[:156])
        self.assertIn(b,range(6))
        self.assertEqual(selector.refits,2)
        self.assertEqual(selector.receipt()["paid_StageB_choices"],2)
        self.assertFalse(selector.receipt()["any_direct_private_source_lookups"])

    def test_multiple_source_blind_selectors_repeat_exact_results(self):
        paid,actions=fixture(n=144)
        first=HypothesisInterventionPolicy()
        second=HypothesisInterventionPolicy()
        x=first.choose(144,paid,actions)
        y=second.choose(144,paid,actions)
        self.assertEqual(x,y)
        self.assertEqual(first.receipt(),second.receipt())

    def test_original_full_neural_and_symbolic_control_on_synthetic_source(self):
        paid,actions=fixture()
        numeric=PaidOperatorInducer()
        for row in paid:
            numeric.charge(row.before,row.action,row.after,row.action_cost)
        trained=numeric.compile()
        self.assertEqual(trained["charged_public_actions"],384)
        cold=PaidOperatorInducer.restore(numeric.snapshot())
        symbolic=IndependentTruthTableControl(paid)
        self.assertTrue(all(
            cold.predict(state,action,history)==symbolic.predict(state,action,history)
            for history in ((),(1,2),(2,3),(3,3))
            for state in source.STATES for action in source.ACTIONS))
        self.assertEqual(INPUTS,25)
        self.assertEqual(HIDDEN,64)
        self.assertEqual(RESTARTS,3)
        self.assertEqual(MAX_STEPS,6000)
        with self.assertRaises(ValueError):
            EndToEndAdamControl(0).fit([])

    def test_cold_numeric_snapshots_are_rejected_if_corrupted(self):
        paid,_=fixture()
        numeric=PaidOperatorInducer()
        for row in paid:
            numeric.charge(row.before,row.action,row.after,row.action_cost)
        numeric.compile()
        cold=numeric.snapshot()
        for broken in (cold[:-1],
                       cold.replace('"charges":384','"charges":144',1),
                       cold.replace('"schema":"wsp84','"schema":"broken',1)):
            with self.assertRaises(ValueError):
                PaidOperatorInducer.restore(broken)

    def test_frozen_classification_is_negative_on_no_gain(self):
        p=json.loads((HERE/"prereg.json").read_text("utf8"))
        records=[]
        for spec in p["source"]["unregistered_worlds"]:
            for arm in ARMS:
                rows={
                    "seed":spec["seed"],"family":spec["family"],"arm":arm,
                    "stageA_144_digest":"same"+str(spec["seed"]),
                    "paid_actions":384,
                    "numeric_symbolic_full_parity":True,
                    "numeric_cold_exact_readout":True,
                    "scores":{"numeric":{
                        "correct":12000,"wrong_confident":0,
                        "never_paid_state_action_correct":4000,
                    }},
                    "operator_receipt":{"learned_operator_receipts":[
                        {"operator_candidates":1} for _ in range(6)]},
                    "Adam64":{"fully_trained":True},
                    "policy_receipt":{"any_direct_private_source_lookups":False}
                          if arm=="hypothesis_active" else None,
                    "stageB_action_choices":list(range(6))*40,
                }
                records.append(rows)
        outcome=classify(records,p)
        self.assertEqual(outcome["classification"],
                         "DEV_INTERVENTION_SELECTION_NEGATIVE")
        self.assertFalse(outcome["criteria"]["active_beats_random_correct"])
        self.assertFalse(outcome["criteria"]["active_beats_passive_correct"])
        self.assertFalse(outcome["criteria"]["active_reduced_ambiguity"])

    def test_no_private_oracle_import_in_action_selection_and_learner(self):
        for path in ("active_policy.py",):
            code=(HERE/path).read_text("utf8")
            for forbidden in ("import source","from source import",
                              "source.World","private_truth(",
                              "_secret_balanced_mask","private_receipt("):
                self.assertNotIn(forbidden,code)
        harness=(HERE/"experiment.py").read_text("utf8")
        self.assertEqual(harness.count("world.private_truth("),1)
        self.assertIn("all_frozen.append(",harness)
        self.assertIn("scores=score_only_after_all_frozen(world,arm,receipt)",harness)


if __name__=="__main__":
    unittest.main()
