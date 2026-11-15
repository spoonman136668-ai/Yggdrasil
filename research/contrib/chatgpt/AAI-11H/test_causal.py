"""AAI-11H new causal substrate, original public evidence and science boundary."""
from __future__ import annotations
import json
import math
from pathlib import Path
import subprocess
import sys
import unittest

HERE=Path(__file__).resolve().parent
for folder in ("AAI-11P","AAI-11A","AAI-11D","AAI-11G"):
    sys.path.insert(0,str(HERE.parent/folder))
sys.path.insert(0,str(HERE))
import world, controls, admission
import learner as original
import calibration as prior
import causal, dev


class FrozenCausalRunlength(unittest.TestCase):
    def test_prereg_first_exact_source_and_no_scientific_authority(self):
        p=json.loads((HERE/"prereg.json").read_text(encoding="utf8"))
        self.assertEqual(p["id"],"AAI-11H")
        self.assertEqual(p["parent"]["head"],
                         "2f1a0d8e73465081d24c8d7364883d9836ba69d1")
        self.assertEqual(p["parent"]["G_prereg_blob"],
                         "260c815900cc7f12aeab9a41a2caa6627482b6e9")
        self.assertEqual(p["frozen_mechanism"]["runlength_candidates"],[4,8,16])
        self.assertEqual(p["frozen_mechanism"]["arms"],list(causal.ARMS))
        self.assertEqual(p["science"]["used"],0)
        self.assertFalse(p["science"]["first_use_authorized"])
        self.assertTrue(p["no_post_result_tuning"])

    def test_original_public_operator_grammar_and_fixed_likelihood(self):
        self.assertEqual(len(original.GRAPH01),45)
        self.assertEqual(len(original.GRAPH2),84)
        self.assertEqual(causal.HORIZONS,(4,8,16))
        self.assertEqual(causal.ODDS,9.)
        self.assertEqual(causal.hypothesis_posterior([0,0]),(.5,.5))
        post=causal.hypothesis_posterior([0,1,2])
        self.assertAlmostEqual(post[0]/post[1],9.)
        self.assertAlmostEqual(sum(post),1.)
        for bad in ([],[-1,0],[0,17],[0,True],[1.0,1]):
            with self.assertRaises(ValueError):
                causal.hypothesis_posterior(bad)

    def test_per_horizon_evidence_is_finite_and_normalized(self):
        history=[]
        for i in range(16):
            event=world.start("C",world.INPUTS[i],world.GOALS[i%8])
            history.append(world.visible(event))
        for r in causal.HORIZONS:
            weights,log_evidence=causal.per_horizon(history,r)
            self.assertEqual(tuple(len(w) for w in weights),(45,45,84))
            self.assertTrue(math.isfinite(log_evidence))
            self.assertTrue(all(abs(sum(w)-1.)<1e-10 for w in weights))
        with self.assertRaises(ValueError):
            causal.per_horizon(history,6)
        with self.assertRaises(ValueError):
            causal.per_horizon(history+history,16)

    def test_exact_same_latest16_public_evidence_but_distinct_runlength_models(self):
        actors=[causal.RunLengthCausalPosterior(arm) for arm in causal.ARMS]
        p8=prior.PosteriorCausalModel("posterior_planner")
        for i in range(28):
            law="C" if i>=20 else "A"
            row=world.copy_public(world.start(law,world.INPUTS[i],world.GOALS[i%8]))
            for actor in (*actors,p8):
                actor.observe(row)
        self.assertEqual(actors[0].rows,actors[1].rows)
        self.assertEqual(len(actors[0].rows),16)
        self.assertEqual(len(p8.rows),8)
        a=actors[0]._active_horizons()
        b=actors[1]._active_horizons()
        self.assertEqual(len(a),1)
        self.assertEqual(len(b),3)
        self.assertEqual([entry[2] for entry in b],[4,8,16])
        self.assertAlmostEqual(sum(entry[0] for entry in b),1.,places=12)
        self.assertEqual(a[0][2],16)

    def test_all_public_causal_predictions_and_unmodified_shared_action_planner(self):
        for arm in causal.ARMS:
            actor=causal.RunLengthCausalPosterior(arm)
            for x in world.INPUTS:
                result=actor.predict(x)
                self.assertEqual(len(result),3)
                self.assertTrue(all(0<=p<=1 and math.isfinite(p) for p in result))
            for law in ("C","E"):
                row=world.start(law,world.INPUTS[23],world.GOALS[5])
                self.assertEqual(actor.choose(row),controls.plan(actor,row))
                self.assertIn(actor.choose(row),(None,*world.ACTIONS))
                self.assertEqual(len(actor.rows),0)
            self.assertEqual(causal.checkpoint(actor),
                             causal.checkpoint(causal.restore(
                                 arm,causal.checkpoint(actor))))

    def test_exact_cold_restore_no_hidden_derived_weights_or_secret_state(self):
        for arm in causal.ARMS:
            actor=causal.RunLengthCausalPosterior(arm)
            for i in range(20):
                actor.observe(world.start("C",world.INPUTS[i],world.GOALS[0]))
            frozen=causal.checkpoint(actor)
            for x in world.INPUTS:
                actor.predict(x)
            self.assertEqual(causal.checkpoint(actor),frozen)
            self.assertEqual(causal.checkpoint(causal.restore(arm,frozen)),frozen)
            self.assertEqual(set(json.loads(frozen)),{"type","arm","rows"})
            self.assertNotIn("posterior",frozen)
            self.assertNotIn("oracle",frozen)
            self.assertNotIn("law",frozen)

    def test_public_training_and_eight_control_rows_are_equal_original(self):
        saved,public,spent=dev.train("mechanical:alpha")
        self.assertEqual(set(saved),set(dev.ARMS))
        self.assertEqual(len(public),64)
        self.assertEqual(set(spent),set(dev.ARMS))
        self.assertTrue(all(set(row)==world.PUBLIC_KEYS for row in public))
        self.assertEqual(dev.restored(dev.NEW,saved[dev.NEW]).rows,
                         dev.restored(dev.ABLATION,saved[dev.ABLATION]).rows)
        self.assertEqual(len(dev.restored(dev.NEW,saved[dev.NEW]).rows),16)
        self.assertEqual(len(dev.restored(dev.OLD_POSTERIOR,saved[dev.OLD_POSTERIOR]).rows),8)

    def test_actual_consequences_cold_forks_and_legal_at_most_two_actions(self):
        key="mechanical:alpha"
        saved,_,_=dev.train(key)
        for name in dev.ARMS:
            snap=dev.challenge(name,saved[name],"F",key,4)
            x,goal=admission.contexts(key,"F",1)[0]
            got=dev.episode(name,snap,"F",x,goal)
            again=dev.episode(name,snap,"F",x,goal)
            self.assertEqual(got,again)
            self.assertLessEqual(len(got[2]),2)
            self.assertLessEqual(got[0],world.exact_oracle("F",x,goal)+1e-9)
            self.assertEqual(dev.frozen(name,dev.restored(name,saved[name])),saved[name])

    def test_reject_private_source_fields_and_noncanonical_or_wrong_arm_checkpoints(self):
        for arm in causal.ARMS:
            actor=causal.RunLengthCausalPosterior(arm)
            row=world.start("C",world.INPUTS[5],world.GOALS[6])
            before=causal.checkpoint(actor)
            for private in ("law","oracle","regime","counterfactual","phase","world_id","seed"):
                with self.assertRaises(ValueError):
                    actor.observe({**row,private:"C"})
                with self.assertRaises(ValueError):
                    actor.choose({**row,private:"C"})
                self.assertEqual(causal.checkpoint(actor),before)
            with self.assertRaises(ValueError):
                causal.restore(arm,before+" ")
            other=next(x for x in causal.ARMS if x!=arm)
            with self.assertRaises(ValueError):
                causal.restore(other,before)
            malformed=json.loads(before)
            malformed["rows"]=[[[0]*6,[0]*3]]*17
            with self.assertRaises(ValueError):
                causal.restore(arm,controls.canonical(malformed))

    def test_first_use_reserved_worlds_and_unapproved_cli_fenced(self):
        for seed in (994000,995000,995063,996000,996031,"995000",
                     "mechanical:delta",None):
            with self.assertRaises(PermissionError):
                world.fixture(seed)
        cmd=[sys.executable,"-B",str(HERE/"dev.py")]
        for args in (["--primary"],["--fixture-admission","--primary"],
                     ["--world","995000"],[]):
            p=subprocess.run(cmd+args,text=True,capture_output=True,timeout=8)
            self.assertNotEqual(p.returncode,0)
            self.assertTrue("DISARMED" in p.stderr or
                            "unrecognized arguments" in p.stderr or
                            "only original three" in p.stderr)


if __name__=="__main__":
    unittest.main()
