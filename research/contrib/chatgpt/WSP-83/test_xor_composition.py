"""WSP83 unregistered-only zero-source-creation development unit fixtures.

Unit tests NEVER instantiate any WSP83 frozen 9901..9904 real world;
synthetic public rows use separate temporary Random(81723) source only.
"""
import json
from pathlib import Path
from random import Random
from types import SimpleNamespace
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
sys.path.append(str(HERE.parent/"WSP-82"))
from xor_weights import PaidXorComposer, FEATURES
from independent_symbolic import IndependentSymbolicXorComposer
from temporal_weights import PaidTemporalFeatureEditor
from history_adam import INPUTS, RESTARTS, MAX_STEPS, EndToEndAdamControl
from experiment import readonly_source_admission, classify, PINNED, PRE_COMMIT
import source


def synthetic_paid(extra=True,offset=2,marker=4):
    rng=Random(81723)
    history=[]
    state=(0,)*6
    events=[]
    for _ in range(384):
        action=rng.randrange(6)
        next_state=list(state)
        next_state[action]^=1
        equal=len(history)>=2 and history[-2]==history[-1]
        hit=bool(history) and history[-1]==marker
        if extra and equal!=hit:
            next_state[(action+offset)%6]^=1
        next_state=tuple(next_state)
        events.append(SimpleNamespace(
            before=state,action=action,after=next_state,action_cost=1))
        state=next_state
        history.append(action)
    return tuple(events)


def synthetic_expected(s,a,history,extra=True,offset=2,marker=4):
    next_state=list(s)
    next_state[a]^=1
    equal=len(history)>=2 and history[-1]==history[-2]
    match=bool(history) and history[-1]==marker
    if extra and equal!=match:
        next_state[(a+offset)%6]^=1
    return tuple(next_state)


class WSP83DeveloperUnitTests(unittest.TestCase):
    def test_exact_prereg_first_and_protected_worlds_separate(self):
        sha,protocol=readonly_source_admission()
        self.assertEqual(len(sha),40)
        self.assertEqual(PRE_COMMIT,"3339fdb449c37e686668b959fbb1700ffeca35fe")
        self.assertEqual(len(PINNED),8)
        self.assertEqual(len(protocol["new_unregistered_cohort"]),4)
        self.assertTrue(protocol["budgets_and_fence"]["no_protected_science_first_use"])
        self.assertEqual(protocol["source_private"]["public_query_count_total"],18432)

    def test_registered_and_other_seeds_refused_without_source_generation(self):
        for seed in (5601,5616,9701,9899,9905,12345):
            with self.assertRaises(PermissionError):
                source.World(seed)
        for step in (-1,384):
            with self.assertRaises(PermissionError):
                source.fixed_action(9901,step)

    def test_compose_missing_XOR_cold_restore_and_independent_symbolic(self):
        self.assertEqual(len(FEATURES),135)
        for extra in (True,False):
            events=synthetic_paid(extra)
            numeric=PaidXorComposer()
            old=PaidTemporalFeatureEditor()
            with self.assertRaises(ValueError):
                numeric.compile()
            for event in events:
                numeric.charge(event.before,event.action,event.after,event.action_cost)
                old.charge(event.before,event.action,event.after,event.action_cost)
            info=numeric.compile()
            self.assertEqual(info["paid_actions"],384)
            if extra:
                self.assertGreater(info["composed_two_atom_XOR_outputs"],0)
                with self.assertRaises(ValueError):
                    old.compile()
            else:
                self.assertEqual(info["composed_two_atom_XOR_outputs"],0)
                old.compile()
            cold=PaidXorComposer.restore(numeric.snapshot())
            symbolic=IndependentSymbolicXorComposer(events)
            self.assertIsNone(cold._rows)
            histories=((),(0,1),(1,0),(2,2),(4,4),(1,4),(4,0))
            for past in histories:
                for state in source.STATES:
                    for a in source.ACTIONS:
                        truth=synthetic_expected(state,a,past,extra)
                        self.assertEqual(cold.predict(state,a,past),truth)
                        self.assertEqual(symbolic.predict(state,a,past),truth)
            self.assertEqual(cold.snapshot(),numeric.snapshot())

    def test_public_charges_and_tampered_snapshot_refusal(self):
        writer=PaidXorComposer()
        with self.assertRaises(ValueError):
            writer.charge((1,)*6,0,(0,)*6)
        events=synthetic_paid()
        for e in events:
            writer.charge(e.before,e.action,e.after,e.action_cost)
        writer.compile()
        with self.assertRaises(ValueError):
            writer.charge(events[-1].after,0,(0,)*6)
        serialized=writer.snapshot()
        for bad in (serialized[:-1],
                    serialized.replace('"charges":384','"charges":144',1),
                    serialized.replace('"basis_count":135','"basis_count":34',1)):
            with self.assertRaises(ValueError):
                PaidXorComposer.restore(bad)
        cold=PaidXorComposer.restore(serialized)
        with self.assertRaises(ValueError):
            cold.charge((0,)*6,0,(0,)*6)

    def test_frozen_25_input_real_Adam_baseline_cannot_be_stubbed(self):
        self.assertEqual(INPUTS,25)
        self.assertEqual(RESTARTS,3)
        self.assertEqual(MAX_STEPS,6000)
        with self.assertRaises(ValueError):
            EndToEndAdamControl(9911).fit([])

    def test_negative_frozen_diagnostics_not_success_by_construction(self):
        prereg=json.loads((HERE/"prereg.json").read_text())
        records=[]
        for item in prereg["new_unregistered_cohort"]:
            records.append({
                "seed":item["seed"],"family":item["family"],
                "old_WSP82_singleton_rejected":False,
                "scores":{"numeric":{"correct":2304,"wrong_confident":2304,
                                     "genuinely_unpaid_correct":0},
                          "memoryless":{"correct":4608}},
                "composer":{"composed_two_atom_XOR_outputs":0},
                "symbolic_exact_parity":True,
                "numeric_cold_full_parity":True,
                "history_Adam":{"fully_trained":True},
                "paid_actions":384,
            })
        v=classify(records,prereg)
        self.assertEqual(v["classification"],"DEV_XOR_COMPOSITION_DIAGNOSTICS_NEGATIVE")
        self.assertFalse(v["checks"]["old_singleton_rejected_both_novel"])
        self.assertFalse(v["checks"]["composed_necessary"])
        self.assertFalse(v["checks"]["new_numerical_no_wrong"])

    def test_private_evaluator_never_imported_by_learners(self):
        for name in ("xor_weights.py","independent_symbolic.py"):
            text=(HERE/name).read_text("utf8")
            for forbidden in ("import source","from source import",
                              "source.World","private_truth","_private_int"):
                self.assertNotIn(forbidden,text)
        harness=(HERE/"experiment.py").read_text("utf8")
        self.assertEqual(harness.count("world.private_truth("),1)
        self.assertIn("score_after_freeze(world,frozen)",harness)


if __name__=="__main__":
    unittest.main()
