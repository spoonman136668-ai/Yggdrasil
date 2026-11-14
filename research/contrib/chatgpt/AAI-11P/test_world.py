"""AAI-11P finite causal task, strong controls and science-custody tests."""
from __future__ import annotations
import itertools
import json
import subprocess
import sys
import unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import world,controls,admission


class FrozenHardCausalTask(unittest.TestCase):
    def test_frozen_prereg_before_task_implementation(self):
        p=json.loads((HERE/"prereg.json").read_text("utf8"))
        self.assertEqual(p["id"],"AAI-11P")
        self.assertEqual(p["base_main_sha"],
                         "5e74f8db85b2f5839c42148c0dfba69a88b1a2c9")
        self.assertFalse(p["future_science"]["primary_authorized"])
        self.assertEqual(p["future_science"]["used"],0)
        self.assertTrue(p["no_post_result_tuning"])
        self.assertEqual(len(p["matched_controls"])-2,len(controls.METHODS))
        self.assertEqual(p["mechanical_admission"]["headroom"].split(">=")[1][:4],"0.25")

    def test_world_expand_and_finite_causal_graphs(self):
        self.assertEqual(len(world.INPUTS),64)
        self.assertEqual(len(world.GOALS),8)
        self.assertEqual(len(world.ACTIONS),12)
        self.assertEqual(len(world.LAWS),6)
        self.assertEqual(len(world.TRANSFER),4)
        signatures={}
        for law in world.LAWS:
            signatures[law]=tuple(world.intermediates(law,x) for x in world.INPUTS)
            self.assertEqual(len(set(signatures[law])),len(set(signatures[law])))
        self.assertEqual(len(set(signatures.values())),6)
        for l in world.LAWS:
            for x in world.INPUTS:
                self.assertEqual(len(world.intermediates(l,x)),3)

    def test_exhaustive_mechanical_identifiability_and_consequence(self):
        result=world.mechanics()
        self.assertTrue(all(result["checks"].values()),result["checks"])
        self.assertEqual(result["cases"],6*64*8*12)
        self.assertEqual(len(result["trace_sha256"]),64)
        self.assertEqual(len(result["unidentifiable_examples_per_pair"]),15)
        self.assertTrue(all(v==0 for v in result["unidentifiable_examples_per_pair"].values()))
        self.assertTrue(all(v>=.20 for v in result["consequential_fraction"].values()))
        self.assertEqual(result["science_cohorts_consumed"],0)

    def test_public_interventions_are_persistent_reward_and_private_fields_absent(self):
        for l in world.LAWS:
            initial=world.start(l,(0,1,0,0,1,0),(1,0,1))
            self.assertEqual(frozenset(initial),world.PUBLIC_KEYS)
            second=world.do(l,initial,(0,1))
            self.assertEqual(second["x"][0],1)
            self.assertEqual(second["actions_taken"],1)
            self.assertEqual(second["mediators"],list(world.intermediates(l,second["x"])))
            third=world.do(l,second,(5,1))
            self.assertEqual(third["x"][0],1)
            self.assertEqual(third["x"][5],1)
            self.assertEqual(third["actions_taken"],2)
            self.assertAlmostEqual(third["reward"],world.reward(third["mediators"],(1,0,1),2))
            with self.assertRaises(ValueError):world.do(l,third,(4,0))
            with self.assertRaises(ValueError):world.visible({**initial,"law":l})
            self.assertEqual(world.copy_public(initial),initial)

    def test_no_hidden_law_available_to_any_conventional_control(self):
        sample=world.start("A",(1,0,1,0,1,0),(0,0,1))
        for name in controls.ALL:
            model=controls.make(name)
            with self.assertRaises(ValueError):
                model.observe({**sample,"law":"A"})
            with self.assertRaises(ValueError):
                model.choose({**sample,"secret_oracle":"A"})
            self.assertEqual(model.rows,[])

    def test_shared_conventional_training_and_cold_restoration(self):
        key="mechanical:alpha"
        frozen,seen=admission.common_training(key)
        self.assertEqual(len(seen),64)
        self.assertEqual(set(frozen),set(controls.ALL))
        self.assertEqual(controls.restore(frozen["logistic_triple"],
                              "logistic_triple").trained,True)
        for name in controls.ALL:
            actor=controls.restore(frozen[name],name)
            self.assertEqual(controls.checkpoint(actor),frozen[name])
            for x in world.INPUTS[:8]:
                pred=actor.predict(x)
                self.assertEqual(len(pred),3)
                self.assertTrue(all(0<=q<=1 for q in pred))
            start=world.start("C",world.INPUTS[0],world.GOALS[0])
            self.assertIn(actor.choose(start),(None,*world.ACTIONS))
        self.assertEqual(len(controls.PAIR_GRAMMAR),45)
        self.assertEqual(len(controls.MONOMIALS),42)

    def test_common_public_challenge_and_cold_independent_episodes(self):
        key="mechanical:alpha"
        saved,_=admission.common_training(key)
        for name in ("tabular_all","knn_recent32","symbolic_pair_recent16",
                     "id3_depth4_all","logistic_triple"):
            snap=admission.common_challenge(name,saved[name],"C",key,4)
            sample=admission.contexts(key,"C",1)[0]
            first=admission.episode(name,snap,"C",*sample)
            second=admission.episode(name,snap,"C",*sample)
            self.assertEqual(first,second)
            self.assertEqual(controls.checkpoint(controls.restore(snap,name)),snap)
            self.assertIn(len(first["actions"]),(0,1,2))
            self.assertLessEqual(first["reward"],world.exact_oracle("C",*sample)+1e-9)
        self.assertEqual(len(set(admission.contexts(key,"C"))),12)

    def test_fixed_mechanical_fixture_not_science_seed(self):
        for invalid in (994000,995000,995063,996000,996031,
                        "995000","dev","mechanical:delta",None):
            with self.assertRaises(PermissionError):
                world.fixture(invalid)
            with self.assertRaises(PermissionError):
                world.fixture_trial(invalid,"train-initial",0)
        for valid in world.FIXTURES:
            self.assertEqual(world.fixture(valid),valid)

    def test_bad_control_checkpoint_and_scoring_fence(self):
        actor=controls.make("tabular_all")
        snap=controls.checkpoint(actor)
        for broken in (snap+" ","{}"):
            with self.assertRaises(ValueError):
                controls.restore(broken,"tabular_all")
        with self.assertRaises(ValueError):
            controls.restore(snap,"knn_all")
        with self.assertRaises(ValueError):
            controls.make("simulator_oracle")
        with self.assertRaises(ValueError):
            admission.score_condition("tabular_all",snap,"C","mechanical:alpha",8)

    def test_scientific_first_use_disarmed_in_both_entrypoints(self):
        for path in ("world.py","admission.py"):
            result=subprocess.run([sys.executable,"-B",str(HERE/path),"--primary"],
                                  capture_output=True,text=True,timeout=5)
            self.assertNotEqual(result.returncode,0)
            self.assertIn("DISARMED",result.stderr)


if __name__=="__main__":
    unittest.main()
