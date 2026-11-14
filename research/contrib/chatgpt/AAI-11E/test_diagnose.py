"""AAI-11E frozen source-only posterior calibration/risk suppression tests."""
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
sys.path.insert(0,str(HERE.parent/"AAI-11D"))
import world,controls,admission
import calibration,dev
import diagnose


class FrozenRiskSuppression(unittest.TestCase):
    def test_prereg_before_model_diagnostic_and_science_unconsumed(self):
        p=json.loads((HERE/"prereg.json").read_text("utf8"))
        self.assertEqual(p["id"],"AAI-11E")
        self.assertEqual(p["source_custody"]["parent_sha"],
                         "56c6fd02d21a005708fa6998f2b3f2d056306f41")
        self.assertEqual(p["source_custody"]["model_blob"],
                         "49f7de063e3577ef8f0b4e42043a24581e6cd09c")
        self.assertEqual(p["science"]["used"],0)
        self.assertFalse(p["science"]["first_use_authorized"])
        self.assertTrue(p["no_post_result_tuning"])
        self.assertEqual(p["conditions"]["total_episodes_per_arm"],288)

    def test_only_original_synthetic_fixtures_and_original_methods(self):
        self.assertEqual(diagnose.ARMS,dev.ARMS)
        self.assertEqual(len(world.FIXTURES),3)
        self.assertEqual(len(world.TRANSFER),4)
        for invalid in (994000,995000,995063,996000,996031,
                        "995000","mechanical:delta",None):
            with self.assertRaises(PermissionError):
                world.fixture(invalid)

    def test_public_identical_cold_training_and_heldout_challenge(self):
        frozen,public,_=dev.train("mechanical:alpha")
        self.assertEqual(len(public),64)
        self.assertEqual(set(frozen),set(diagnose.ARMS))
        for event in public:
            self.assertEqual(set(event),world.PUBLIC_KEYS)
        for name in diagnose.ARMS:
            snap=dev.challenge(name,frozen[name],"D","mechanical:alpha",4)
            self.assertEqual(dev.frozen(name,dev.restored(name,snap)),snap)
        self.assertEqual(dev.restored("posterior_planner",frozen["posterior_planner"]).rows,
                         dev.restored("risk_calibrated_planner",frozen["risk_calibrated_planner"]).rows)

    def test_calibration_is_evaluator_only_and_checkpoint_unchanged(self):
        key="mechanical:alpha"
        frozen,_,_=dev.train(key)
        for name in diagnose.ARMS:
            snap=dev.challenge(name,frozen[name],"C",key,2)
            diag=diagnose.calibration_probe(name,snap,"C")
            self.assertEqual(len(diag["predictions"]),64)
            self.assertEqual(len(diag["brier"]),3)
            self.assertEqual(len(diag["logloss"]),3)
            for i in range(3):
                self.assertTrue(0<=diag["brier"][i]<=1)
                self.assertTrue(0<=diag["logloss"][i]<30)
                self.assertEqual(sum(item["n"] for item in diag["calibration_bins"][i]),64)
            self.assertEqual(dev.frozen(name,dev.restored(name,snap)),snap)

    def test_posterior_and_risk_calibration_bit_for_bit_equal(self):
        key="mechanical:alpha"
        frozen,_,_=dev.train(key)
        p=dev.challenge("posterior_planner",frozen["posterior_planner"],"D",key,4)
        r=dev.challenge("risk_calibrated_planner",frozen["risk_calibrated_planner"],"D",key,4)
        pm=diagnose.calibration_probe("posterior_planner",p,"D")
        rm=diagnose.calibration_probe("risk_calibrated_planner",r,"D")
        self.assertEqual(pm,rm)
        self.assertEqual(calibration.RISK_LAMBDA,.5)
        self.assertEqual(calibration.LIKELIHOOD_RATIO,9.)

    def test_no_private_regime_law_or_oracle_passed_to_models(self):
        key="mechanical:alpha"
        frozen,_,_=dev.train(key)
        row=world.start("F",world.INPUTS[5],world.GOALS[6])
        for name in diagnose.ARMS:
            actor=dev.restored(name,frozen[name])
            before=dev.frozen(name,actor)
            for field in ("law","oracle","world_id","counterfactual","future_action","regime"):
                with self.assertRaises(ValueError):
                    actor.observe({**row,field:"F"})
                with self.assertRaises(ValueError):
                    actor.choose({**row,field:"F"})
                self.assertEqual(dev.frozen(name,actor),before)

    def test_initial_choices_are_public_and_cold_independent(self):
        key="mechanical:alpha"
        frozen,_,_=dev.train(key)
        x,goal=admission.contexts(key,"F",1)[0]
        row=world.start("F",x,goal)
        for name in diagnose.ARMS:
            snap=dev.challenge(name,frozen[name],"F",key,2)
            a=diagnose.public_choice(name,snap,row)
            b=diagnose.public_choice(name,snap,row)
            self.assertEqual(a,b)
            self.assertGreaterEqual(a,-1)
            self.assertLess(a,12)
            self.assertEqual(dev.frozen(name,dev.restored(name,snap)),snap)

    def test_original_real_action_reward_and_privileged_oracle_only_evaluator(self):
        key="mechanical:alpha"
        frozen,_,_=dev.train(key)
        x,goal=admission.contexts(key,"C",1)[0]
        for name in diagnose.ARMS:
            snap=dev.challenge(name,frozen[name],"C",key,2)
            first=dev.episode(name,snap,"C",x,goal)
            second=dev.episode(name,snap,"C",x,goal)
            self.assertEqual(first,second)
            self.assertLessEqual(len(first[2]),2)
            self.assertLessEqual(first[0],world.exact_oracle("C",x,goal)+1e-10)

    def test_single_pair_records_correct_12_original_contexts(self):
        key="mechanical:alpha"
        frozen,_,_=dev.train(key)
        calibrated,episodes=diagnose.probe_pair(key,"F",2,frozen)
        self.assertEqual(set(calibrated),set(diagnose.ARMS))
        self.assertEqual(len(episodes),12)
        self.assertEqual(calibrated["posterior_planner"]["predictions"],
                         calibrated["risk_calibrated_planner"]["predictions"])
        for episode in episodes:
            self.assertEqual(len(episode["first_choices"]),3)
            self.assertEqual(len(episode["terminal_rewards"]),3)
            self.assertEqual(len(episode["terminal_goals"]),3)
            self.assertIn(episode["posterior_vs_risk_suppressed"],(0,1))
            if episode["posterior_vs_risk_suppressed"]:
                self.assertEqual(episode["first_choices"][2],-1)
                self.assertGreaterEqual(episode["first_choices"][1],0)
                self.assertIsNotNone(episode["one_step_gain_if_suppressed"])
                self.assertIsNotNone(episode["best_two_step_gain_if_suppressed"])
            else:
                self.assertIsNone(episode["one_step_gain_if_suppressed"])
            self.assertTrue(all(r<=episode["oracle_reward"]+1e-10
                                for r in episode["terminal_rewards"]))

    def test_science_first_use_cli_fail_closed(self):
        cmd=[sys.executable,"-B",str(HERE/"diagnose.py")]
        for args in (["--primary"],["--mechanical-diagnostic","--primary"],
                     ["--world","995000"]):
            process=subprocess.run(cmd+args,capture_output=True,text=True,timeout=8)
            self.assertNotEqual(process.returncode,0)
            self.assertTrue("DISARMED" in process.stderr or
                            "unrecognized arguments" in process.stderr)


if __name__=="__main__":
    unittest.main()
