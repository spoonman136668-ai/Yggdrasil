"""AAI-11I source-only causal feedback planner tests and science boundaries."""
from __future__ import annotations
import json
import math
import subprocess
import sys
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
for name in ("AAI-11P","AAI-11A","AAI-11D"):
    sys.path.insert(0,str(HERE.parent/name))
sys.path.insert(0,str(HERE))
import world,controls
import calibration,learner
import policy,dev


class OriginalCausalFeedbackGate(unittest.TestCase):
    def test_preregistered_source_custody_and_unconsumed_first_use(self):
        p=json.loads((HERE/"prereg.json").read_text("utf8"))
        self.assertEqual(p["id"],"AAI-11I")
        self.assertEqual(p["parent"]["source_sha"],
                         "90e04193a50055b2154a1782ed5da21f0132a8ba")
        self.assertEqual(p["parent"]["qualified_11G_prereg"],
                         "260c815900cc7f12aeab9a41a2caa6627482b6e9")
        self.assertEqual(p["frozen_algorithm"]["name"],policy.ARM)
        self.assertEqual(p["science"]["used"],0)
        self.assertFalse(p["science"]["first_use_authorized"])
        self.assertTrue(p["no_post_result_tuning"])
        self.assertEqual(p["frozen_comparison"]["all_required_dev_gates"]["candidate_reward_min"],
                         2.214027778)

    def test_same_eight_row_public_memory_and_frozen_grammar(self):
        self.assertEqual(len(learner.GRAPH01),45)
        self.assertEqual(len(learner.GRAPH2),84)
        self.assertEqual(calibration.LIKELIHOOD_RATIO,9.)
        old=calibration.PosteriorCausalModel("posterior_planner")
        new=policy.CausalFeedbackPlanner()
        for i in range(12):
            public=world.copy_public(world.start("A",world.INPUTS[i],world.GOALS[i%8]))
            old.observe(public)
            new.observe(public)
        self.assertEqual(old.rows,new.rows)
        self.assertEqual(len(new.rows),8)
        self.assertEqual(old.stats,new.stats)
        self.assertEqual(old._weights(),new._weights())
        for x in world.INPUTS:
            self.assertEqual(old.predict(x),new.predict(x))

    def test_structural_joint_predictive_is_nonnegative_and_normalized(self):
        actor=policy.CausalFeedbackPlanner()
        for i in range(8):
            actor.observe(world.start("C",world.INPUTS[i],world.GOALS[i%8]))
        for x in world.INPUTS[:16]:
            joint=policy._predict_joint(actor._weights(),learner.x_key(x))
            self.assertEqual(set(joint),set(policy.OUTCOMES))
            self.assertAlmostEqual(sum(joint.values()),1.,places=10)
            self.assertTrue(all(math.isfinite(v) and 0<=v<=1 for v in joint.values()))
            forecasts=actor.predict(x)
            for m in (0,1,2):
                self.assertAlmostEqual(sum(prob for bits,prob in joint.items()
                                           if bits[m]),forecasts[m],places=9)

    def test_hypothetical_one_row_bayes_update_matches_actual_public_update(self):
        actor=policy.CausalFeedbackPlanner()
        for i in range(8):
            actor.observe(world.start("A",world.INPUTS[i],world.GOALS[i%8]))
        start=policy.checkpoint(actor)
        x=world.INPUTS[19]
        for observed in ((0,0,0),(1,1,1),(1,0,1)):
            hypothesis=policy._hypothetical_weights(actor,learner.x_key(x),observed)
            actual=policy.restore(start)
            # Publicly well-formed hypothetical event; NOT actual simulator truth.
            row={"x":list(x),"mediators":list(observed),"goal":[0,1,1],
                 "reward":world.reward(observed,(0,1,1),1),"actions_taken":1}
            actual.observe(row)
            target=actual._weights()
            for a,b in zip(hypothesis,target):
                self.assertEqual(len(a),len(b))
                self.assertTrue(all(abs(y-z)<1e-12 for y,z in zip(a,b)))
            self.assertEqual(policy.checkpoint(actor),start)

    def test_actual_next_step_uses_original_identical_shared_planner(self):
        actor=policy.CausalFeedbackPlanner()
        for i in range(8):
            actor.observe(world.start("C",world.INPUTS[i],world.GOALS[i%8]))
        row=world.start("C",world.INPUTS[31],world.GOALS[3])
        first=world.do("C",row,(1,0))
        actor.observe(first)
        self.assertEqual(actor.choose(first),controls.plan(actor,first))
        second=world.do("C",first,(5,0))
        self.assertIsNone(actor.choose(second))
        self.assertIn(actor.choose(first),(None,*world.ACTIONS))

    def test_first_action_is_legal_deterministic_and_imagination_not_persistent(self):
        actor=policy.CausalFeedbackPlanner()
        for i in range(8):
            actor.observe(world.start("A",world.INPUTS[i],world.GOALS[2]))
        row=world.start("C",world.INPUTS[31],world.GOALS[5])
        actor.observe(row)
        snap=policy.checkpoint(actor)
        first=actor.choose(row)
        second=actor.choose(row)
        self.assertEqual(first,second)
        self.assertIn(first,(None,*world.ACTIONS))
        self.assertEqual(policy.checkpoint(actor),snap)
        self.assertEqual(actor.rows,policy.restore(snap).rows)

    def test_public_train_matches_original_posterior_and_strongest_conventional(self):
        original,events,timing=dev.train("mechanical:alpha")
        self.assertEqual(len(events),64)
        self.assertEqual(set(original),set(dev.ARMS))
        self.assertEqual(set(timing),set(dev.ARMS))
        for row in events:
            self.assertEqual(set(row),world.PUBLIC_KEYS)
        old=dev.restored(dev.POSTERIOR,original[dev.POSTERIOR])
        new=dev.restored(dev.CANDIDATE,original[dev.CANDIDATE])
        self.assertEqual(old.rows,new.rows)
        self.assertEqual(old._weights(),new._weights())
        self.assertEqual(len(new.rows),8)

    def test_independent_real_interventions_no_privileged_teacher_to_model(self):
        key="mechanical:alpha"
        saved,_,_=dev.train(key)
        for name in dev.ARMS:
            after=dev.challenge(name,saved[name],"F",key,2)
            x,goal=world.INPUTS[15],world.GOALS[3]
            first=dev.episode(name,after,"F",x,goal)
            next_run=dev.episode(name,after,"F",x,goal)
            self.assertEqual(first,next_run)
            self.assertLessEqual(len(first[2]),2)
            self.assertLessEqual(first[0],world.exact_oracle("F",x,goal)+1e-9)
            self.assertEqual(dev.frozen(name,dev.restored(name,after)),after)

    def test_private_data_refused_and_cold_checkpoint_no_derived_memory(self):
        actor=policy.CausalFeedbackPlanner()
        row=world.start("C",world.INPUTS[1],world.GOALS[0])
        snap=policy.checkpoint(actor)
        for field in ("law","oracle","counterfactual","regime","world_id","future_action","seed"):
            with self.assertRaises(ValueError):
                actor.observe({**row,field:"C"})
            with self.assertRaises(ValueError):
                actor.choose({**row,field:"C"})
            self.assertEqual(policy.checkpoint(actor),snap)
        with self.assertRaises(ValueError):
            policy.restore(snap+" ")
        corrupt=json.loads(snap)
        corrupt["rows"]=[[[0]*6,[0]*3]]*9
        with self.assertRaises(ValueError):
            policy.restore(controls.canonical(corrupt))
        self.assertEqual(set(json.loads(snap)),{"arm","rows","type"})

    def test_science_firstuse_id_and_cli_rejected(self):
        for key in (994000,995000,995063,996000,996031,"995000",
                    "mechanical:delta",None):
            with self.assertRaises(PermissionError):
                world.fixture(key)
        cmd=[sys.executable,"-B",str(HERE/"dev.py")]
        for extra in (["--primary"],["--fixture-admission","--primary"],
                      ["--world","995000"],[]):
            process=subprocess.run(cmd+extra,capture_output=True,text=True,timeout=8)
            self.assertNotEqual(process.returncode,0)
            self.assertTrue("DISARMED" in process.stderr or
                            "unrecognized arguments" in process.stderr or
                            "only the original" in process.stderr)


if __name__=="__main__":
    unittest.main()
