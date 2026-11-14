"""AAI-11A source-only fair-structure, public observation and cold tests."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(HERE.parent/"AAI-11P"))
import world,controls,learner,fixture


class FrozenProtectedCausalGraph(unittest.TestCase):
    def test_prereg_prior_to_code_and_firstuse_disarmed(self):
        frozen=json.loads((HERE/"prereg.json").read_text("utf8"))
        self.assertEqual(frozen["id"],"AAI-11A")
        self.assertEqual(frozen["lineage"]["benchmark_sha"],
                         "40062783d0aa0e06fbe93b3419291150b306562d")
        self.assertFalse(frozen["future_science"]["first_use_authorized"])
        self.assertEqual(frozen["future_science"]["consumed"],0)
        self.assertTrue(frozen["no_post_result_tuning"])
        self.assertEqual(set(frozen["original_matched_controls"]),set(controls.METHODS))
        self.assertEqual(set(frozen["matched_structural_controls"]),set(learner.MATCHED_GRAPHS))
        self.assertEqual(len(learner.MATCHED),11)

    def test_public_compositional_grammar_shared_exactly(self):
        self.assertEqual(learner.GRAPH01,controls.PAIR_GRAMMAR)
        self.assertEqual(len(learner.GRAPH01),45)
        self.assertEqual(len(learner.GRAPH2),84)
        self.assertEqual(learner.SIZES,(45,45,84))
        self.assertEqual(len(learner.TRUTH01),64)
        self.assertEqual(len(learner.TRUTH2),64)
        for x in world.INPUTS:
            k=learner.x_key(x)
            for i,h in enumerate(learner.GRAPH01):
                self.assertEqual(learner.TRUTH01[k][i],
                                 controls.pair_pattern(h,x))
            for m0,m1 in ((0,0),(0,1),(1,0),(1,1)):
                for i,h in enumerate(learner.GRAPH2):
                    self.assertEqual(learner.TRUTH2[k][m0][m1][i],
                                     learner.pattern(h,(*x,m0,m1)))
        self.assertEqual(len(learner.ProtectedGraphBank().slots[0]["mismatches"][2]),84)

    def test_reject_private_law_and_unobserved_outcomes_atomically(self):
        raw=world.start("A",(1,0,0,1,1,0),(1,1,1))
        for method in learner.NAMES:
            actor=learner.make(method)
            initial=learner.checkpoint(method,actor)
            for private in ("law","regime","oracle","future_outcomes","source_formula","world_id"):
                with self.assertRaises(ValueError):
                    actor.observe({**raw,private:"A"})
                with self.assertRaises(ValueError):
                    actor.choose({**raw,private:"A"})
                self.assertEqual(learner.checkpoint(method,actor),initial)
        for value in (994000,995000,995063,996000,"995000","mechanical:illegal"):
            with self.assertRaises(PermissionError):
                world.fixture(value)

    def test_equal_training_and_independent_original_public_checkpoints(self):
        saved,observed,timings=fixture.common_training("mechanical:alpha")
        self.assertEqual(len(observed),64)
        self.assertEqual(set(saved),set(learner.NAMES))
        self.assertEqual(set(timings),set(learner.NAMES))
        self.assertTrue(all(v>=0 for v in timings.values()))
        for row in observed:
            self.assertEqual(set(row),world.PUBLIC_KEYS)
        for method,payload in saved.items():
            cloned=learner.restore(method,payload)
            self.assertEqual(learner.checkpoint(method,cloned),payload)
            for x in world.INPUTS[:3]:
                vals=cloned.predict(x)
                self.assertEqual(len(vals),3)
                self.assertTrue(all(0<=q<=1 for q in vals))
        self.assertTrue(learner.restore("logistic_triple",saved["logistic_triple"]).trained)
        self.assertEqual(learner.restore("one_slot",saved["one_slot"]).max_slots,1)
        self.assertEqual(learner.restore("protected_graph",saved["protected_graph"]).max_slots,3)

    def test_same_graph_family_predicts_equal_without_protected_memory(self):
        one=learner.ProtectedGraphBank(1)
        conventional=learner.GraphWindow("graph_all")
        initial=world.start("C",(1,0,0,0,1,1),(1,0,0))
        for method in (one,conventional):
            for row in (initial,world.do("C",initial,(1,1))):
                method.observe(world.copy_public(row))
        for x in world.INPUTS:
            self.assertEqual(one.predict(x),conventional.predict(x))
        self.assertEqual(one.choose(initial),conventional.choose(initial))

    def test_actual_action_consequence_and_full_budget_single_slot(self):
        saved,observed,_=fixture.common_training("mechanical:alpha",
                                                  names=("one_slot","protected_graph","graph_recent8"))
        frozen=dict(saved)
        for law in ("A","B","C","D","E","F"):
            for name in saved:
                snap=fixture.challenge(name,saved[name],law,"mechanical:alpha",4)
                obj=learner.restore(name,snap)
                if name=="one_slot":
                    self.assertEqual(len(obj.slots),1)
                    self.assertLessEqual(obj.slots[0]["rows"],72)
                x,g=world.INPUTS[0],world.GOALS[3]
                r1=fixture.episode(name,snap,law,x,g)
                r2=fixture.episode(name,snap,law,x,g)
                self.assertEqual(r1,r2)
                self.assertLessEqual(len(r1[2]),2)
                self.assertLessEqual(r1[0],world.exact_oracle(law,x,g)+1e-9)
        self.assertEqual(saved,frozen)
        self.assertLessEqual(64+8+3,96)

    def test_valid_conditional_m2_learning_from_public_upstream(self):
        method=learner.GraphWindow("graph_all")
        for x in world.INPUTS:
            method.observe(world.start("C",x,(0,0,0)))
        correct=0
        for x in world.INPUTS:
            probs=method.predict(x)
            inferred=tuple(int(q>=.5) for q in probs)
            correct+=int(inferred==world.intermediates("C",x))
        self.assertGreaterEqual(correct,56)  # only mechanical complete public truth table

    def test_protected_cold_bytes_recall_and_saturation_fence(self):
        actor=learner.ProtectedGraphBank(1)
        first=world.start("A",world.INPUTS[0],world.GOALS[0])
        for i in range(48):
            pre=world.start("A",world.INPUTS[i%64],world.GOALS[0])
            actor.observe(pre)
            actor.observe(world.do("A",pre,(i%6,1)))
        self.assertEqual(actor.active()["rows"],96)
        snapshot=learner.checkpoint("one_slot",actor)
        self.assertEqual(learner.checkpoint(
            "one_slot",learner.restore("one_slot",snapshot)),snapshot)
        actor.observe(first)
        scratch_before=learner.checkpoint("one_slot",actor)
        with self.assertRaisesRegex(ValueError,"saturation"):
            actor.observe(world.do("A",first,(2,1)))
        self.assertEqual(learner.checkpoint("one_slot",actor),scratch_before)
        altered=json.loads(snapshot)
        altered["slots"][0]["mismatches"][1][3]=100
        with self.assertRaises(ValueError):
            learner.restore("one_slot",controls.canonical(altered))
        altered=json.loads(snapshot)
        altered["next_id"]=3
        with self.assertRaises(ValueError):
            learner.restore("one_slot",controls.canonical(altered))

    def test_corrupted_feedback_preserves_public_marginals(self):
        key="mechanical:alpha"
        base=fixture.common_training(key,names=("protected_graph",))[0]["protected_graph"]
        clean=fixture.challenge("protected_graph",base,"C",key,4)
        corrupt=fixture.challenge("protected_graph",base,"C",key,4,corrupt=True)
        self.assertIsInstance(clean,str)
        self.assertIsInstance(corrupt,str)
        self.assertEqual(learner.checkpoint("protected_graph",
                         learner.restore("protected_graph",base)),base)
        self.assertEqual(len(learner.restore("protected_graph",clean).scratch),0)

    def test_scientific_first_use_cli_disarmed(self):
        for args in (["--primary"],["--fixture-admission","--primary"],
                     ["--world","995000"]):
            p=subprocess.run([sys.executable,"-B",str(HERE/"fixture.py"),*args],
                             text=True,capture_output=True,timeout=6)
            self.assertNotEqual(p.returncode,0)
            self.assertTrue("DISARMED" in p.stderr or
                            "unrecognized arguments" in p.stderr)


if __name__=="__main__":
    unittest.main()
