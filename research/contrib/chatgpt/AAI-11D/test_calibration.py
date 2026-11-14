"""AAI-11D frozen posterior/risk uncertainty, fairness and first-use tests."""
from __future__ import annotations
import json
import math
from pathlib import Path
import subprocess
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(HERE.parent/"AAI-11P"))
sys.path.insert(0,str(HERE.parent/"AAI-11A"))
import world,controls
import learner as graph
import calibration,dev


class FrozenUncertaintyCausalPolicy(unittest.TestCase):
    def test_prereg_immutable_baseline_and_science_fence(self):
        p=json.loads((HERE/"prereg.json").read_text(encoding="utf8"))
        self.assertEqual(p["id"],"AAI-11D")
        self.assertEqual(p["base"]["head"],
                         "44729734a17a658873b344024913587a596239b2")
        self.assertEqual(p["base"]["historical"]["best_graph_recent8_reward"],2.134027778)
        self.assertFalse(p["science"]["first_use_authorized"])
        self.assertEqual(p["science"]["used"],0)
        self.assertTrue(p["no_post_result_tuning"])
        self.assertEqual(p["arms"]["risk_calibrated_planner"].count("0.5"),1)
        self.assertEqual(calibration.RISK_LAMBDA,.5)
        self.assertEqual(calibration.LIKELIHOOD_RATIO,9.)

    def test_same_operator_grammar_and_eight_recent_public_states(self):
        self.assertEqual(len(graph.GRAPH01),45)
        self.assertEqual(len(graph.GRAPH2),84)
        arms=[graph.GraphWindow("graph_recent8")]+[
            calibration.PosteriorCausalModel(name) for name in calibration.ARMS]
        for i in range(18):
            row=world.start("C",world.INPUTS[i],world.GOALS[i%8])
            for model in arms:
                model.observe(world.copy_public(row))
        self.assertTrue(all(len(model.rows)==8 for model in arms))
        self.assertEqual(arms[0].rows,arms[1].rows)
        self.assertEqual(arms[1].rows,arms[2].rows)
        self.assertEqual(arms[0].stats,arms[1].stats)
        self.assertEqual(arms[1].stats,arms[2].stats)
        self.assertEqual(arms[1].state()["rows"],arms[2].state()["rows"])

    def test_posterior_likelihood_normalization_uniform_and_finite(self):
        u=calibration.posterior([0]*45)
        self.assertEqual(len(u),45)
        self.assertAlmostEqual(sum(u),1.0)
        self.assertAlmostEqual(u[0],1/45)
        known=calibration.posterior([0,1,2])
        self.assertAlmostEqual(known[0]/known[1],9)
        self.assertAlmostEqual(known[1]/known[2],9)
        self.assertAlmostEqual(sum(known),1)
        for invalid in ([],[-1,0],[0,9],[1.0,1],["0",0]):
            with self.assertRaises(ValueError):
                calibration.posterior(invalid)

    def test_public_causal_marginal_forecast_composes_downstream(self):
        for name in calibration.ARMS:
            actor=calibration.PosteriorCausalModel(name)
            for x in world.INPUTS:
                p=actor.predict(x)
                self.assertEqual(len(p),3)
                self.assertTrue(all(math.isfinite(v) and 0<=v<=1 for v in p))
            self.assertEqual(calibration.checkpoint(actor),
                             calibration.checkpoint(calibration.restore(
                                 name,calibration.checkpoint(actor))))
        a=calibration.PosteriorCausalModel("posterior_planner")
        b=calibration.PosteriorCausalModel("risk_calibrated_planner")
        for x in world.INPUTS[:15]:
            pair=world.start("D",x,world.GOALS[0])
            for m in (a,b):m.observe(pair)
        for x in world.INPUTS:
            self.assertEqual(a.predict(x),b.predict(x))

    def test_uncertainty_risk_is_pessimistic_and_no_more_actions(self):
        row=world.start("D",world.INPUTS[3],world.GOALS[2])
        actor=calibration.PosteriorCausalModel("risk_calibrated_planner")
        p=actor.predict(row["x"])
        expected=controls.expected(p,row["goal"],1)
        risk=actor._risk_value(p,row["goal"],1)
        self.assertLessEqual(risk,expected)
        self.assertAlmostEqual(expected-risk,
                               .5*math.sqrt(sum(q*(1-q) for q in p)))
        self.assertIn(actor.choose(row),(None,*world.ACTIONS))
        at_two=world.do("D",world.do("D",row,(3,1)),(1,0))
        self.assertIsNone(actor.choose(at_two))

    def test_cold_restoration_all_methods_no_derived_cached_weights(self):
        key="mechanical:alpha"
        saved,rows,cost=dev.train(key)
        self.assertEqual(len(rows),64)
        self.assertEqual(set(saved),set(dev.ARMS))
        self.assertEqual(set(cost),set(dev.ARMS))
        for name in dev.ARMS:
            model=dev.restored(name,saved[name])
            self.assertEqual(dev.frozen(name,model),saved[name])
            for x in world.INPUTS[:4]:
                model.predict(x)
            self.assertEqual(dev.frozen(name,model),saved[name])
            if name!="graph_recent8":
                self.assertNotIn("posterior_cache",saved[name])
                self.assertNotIn("pred_cache",saved[name])

    def test_real_actions_independent_forks_and_original_control_replay(self):
        key="mechanical:alpha"
        saved,_,_=dev.train(key)
        for name in dev.ARMS:
            for law in ("C","F"):
                snap=dev.challenge(name,saved[name],law,key,4)
                self.assertEqual(dev.frozen(name,dev.restored(name,snap)),snap)
                x,g=world.INPUTS[3],world.GOALS[6]
                a=dev.episode(name,snap,law,x,g)
                b=dev.episode(name,snap,law,x,g)
                self.assertEqual(a,b)
                self.assertLessEqual(len(a[2]),2)
                self.assertLessEqual(a[0],world.exact_oracle(law,x,g)+1e-9)
                self.assertEqual(dev.frozen(name,dev.restored(name,saved[name])),
                                 saved[name])

    def test_secret_law_and_future_action_data_rejected_atomically(self):
        row=world.start("C",world.INPUTS[7],world.GOALS[5])
        for name in calibration.ARMS:
            model=calibration.PosteriorCausalModel(name)
            state=calibration.checkpoint(model)
            for forbidden in ("law","world","counterfactual","oracle","regime","future_actions"):
                with self.assertRaises(ValueError):
                    model.observe({**row,forbidden:"C"})
                with self.assertRaises(ValueError):
                    model.choose({**row,forbidden:"C"})
                self.assertEqual(calibration.checkpoint(model),state)

    def test_corrupt_checkpoint_and_forbidden_science_ids(self):
        name="risk_calibrated_planner"
        s=calibration.checkpoint(calibration.PosteriorCausalModel(name))
        with self.assertRaises(ValueError):
            calibration.restore(name,s+" ")
        with self.assertRaises(ValueError):
            calibration.restore("posterior_planner",s)
        broken=json.loads(s)
        broken["rows"]=[[[0]*6,[0]*3]]*9
        with self.assertRaises(ValueError):
            calibration.restore(name,controls.canonical(broken))
        for bad in (994000,995000,995063,996000,996031,"995000",
                    "mechanical:delta"):
            with self.assertRaises(PermissionError):
                world.fixture(bad)

    def test_primary_disarmed_in_source_and_no_extra_execution_route(self):
        cmd=[sys.executable,"-B",str(HERE/"dev.py")]
        for tail in (["--primary"],["--primary","--fixture-admission"],
                     ["--world","995000"]):
            p=subprocess.run(cmd+tail,capture_output=True,text=True,timeout=8)
            self.assertNotEqual(p.returncode,0)
            self.assertTrue("DISARMED" in p.stderr or
                            "unrecognized arguments" in p.stderr)


if __name__=="__main__":
    unittest.main()
