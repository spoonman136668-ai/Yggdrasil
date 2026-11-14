"""AAI-11C immutable-model causal identification vs decision diagnostic tests."""
from __future__ import annotations
import json
from pathlib import Path
import subprocess
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(HERE.parent/"AAI-11P"))
sys.path.insert(0,str(HERE.parent/"AAI-11A"))
sys.path.insert(0,str(HERE.parent/"AAI-11B"))
import world,controls,admission,learner as graph,contrast,dev as prior_dev
import diagnose as d


class FrozenNoTuningDiagnosis(unittest.TestCase):
    def test_prereg_before_diagnostic_and_untouched_primary_cohorts(self):
        p=json.loads((HERE/"prereg.json").read_text(encoding="utf8"))
        self.assertEqual(p["id"],"AAI-11C")
        self.assertEqual(p["source"]["original_AAI11B_final_sha"],
                         "425747038824324c161c4de5e960117c6be31145")
        self.assertEqual(p["source"]["AAI11B_model_blob"],
                         "69ff21daf627feeaaca6661f8f3c8096efbe4de8")
        self.assertFalse(p["science"]["science_first_use_authorized"])
        self.assertEqual(p["science"]["cohorts_consumed"],0)
        self.assertTrue(p["no_post_result_tuning"])
        self.assertEqual(d.METHODS,
                         ("aai11b_intervention_tournament","graph_recent8"))
        self.assertEqual((d.EXPECTED_CANDIDATE,d.EXPECTED_CONTROL),
                         (2.084722222,2.134027778))

    def test_exact_source_models_have_identical_grammar_and_shared_planner(self):
        original=graph.GraphWindow("graph_recent8")
        candidate=contrast.InterventionTournament()
        self.assertEqual(original.limit,candidate.limit)
        self.assertEqual(original.stats,candidate.stats)
        self.assertEqual(len(graph.GRAPH01),45)
        self.assertEqual(len(graph.GRAPH2),84)
        for x in world.INPUTS:
            self.assertEqual(original.predict(x),candidate.predict(x))
        for row in (world.start("A",world.INPUTS[3],world.GOALS[2]),
                    world.start("C",world.INPUTS[9],world.GOALS[7])):
            self.assertEqual(original.choose(row),candidate.choose(row))

    def test_public_state_privacy_fail_closed(self):
        row=world.start("C",world.INPUTS[5],world.GOALS[2])
        for actor,method in ((contrast.InterventionTournament(),"candidate"),
                             (graph.GraphWindow("graph_recent8"),"control")):
            initial=(contrast.checkpoint(actor) if method=="candidate"
                     else graph.checkpoint("graph_recent8",actor))
            for key in ("law","oracle","regime","counterfactuals","world_id","seed"):
                with self.assertRaises(ValueError):
                    actor.observe({**row,key:"C"})
                with self.assertRaises(ValueError):
                    actor.choose({**row,key:"C"})
            final=(contrast.checkpoint(actor) if method=="candidate"
                   else graph.checkpoint("graph_recent8",actor))
            self.assertEqual(initial,final)

    def test_no_reserved_science_world_generator_or_cli_firstuse(self):
        for seed in (994000,995000,995063,996000,996031,"995000","mechanical:delta"):
            with self.assertRaises(PermissionError):
                world.fixture(seed)
        cmd=[sys.executable,"-B",str(HERE/"diagnose.py")]
        for args in (["--primary"],["--primary","--mechanical-diagnostic"],
                     ["--world","995000"]):
            p=subprocess.run(cmd+args,capture_output=True,text=True,timeout=8)
            self.assertNotEqual(p.returncode,0)
            self.assertTrue("DISARMED" in p.stderr or
                            "unrecognized arguments" in p.stderr)

    def test_private_perfect_predictor_is_exact_law_not_a_learnable_model(self):
        for law in world.LAWS:
            gold=d.PerfectPredictorDiagnostic(law)
            for x in world.INPUTS:
                self.assertEqual(gold.predict(x),
                                 tuple(float(v) for v in world.intermediates(law,x)))
        with self.assertRaises(ValueError):
            d.PerfectPredictorDiagnostic("invalid")
        self.assertFalse(hasattr(d.PerfectPredictorDiagnostic("C"),"observe"))

    def test_perfect_forecast_shared_planner_never_exceeds_two_step_oracle(self):
        for law in world.TRANSFER:
            for x,g in admission.contexts("mechanical:alpha",law,4):
                achieved,actions=d.perfect_planner_rollout(law,x,g)
                self.assertLessEqual(len(actions),2)
                self.assertLessEqual(achieved,world.exact_oracle(law,x,g)+1e-10)
                self.assertGreaterEqual(achieved,-.10)

    def test_probe_is_read_only_and_counterfactuals_never_train(self):
        key="mechanical:alpha"
        frozen,_,_=prior_dev.train(key)
        actor=contrast.restore(frozen)
        before=contrast.checkpoint(actor)
        result=d.probe(actor,"C")
        self.assertEqual(result["evaluated_inputs"],64)
        self.assertEqual(result["evaluated_do_actions"],768)
        self.assertEqual(result["changed_do_actions"],384)
        self.assertEqual(len(result["factual_each_mediator"]),3)
        self.assertTrue(all(0<=x<=1 for x in result["factual_each_mediator"]))
        self.assertTrue(0<=result["changed_input_flip_bit_accuracy"]<=1)
        self.assertEqual(contrast.checkpoint(actor),before)
        self.assertEqual(len(actor.rows),8)

    def test_same_public_training_states_and_independent_challenge_probes(self):
        key="mechanical:alpha"
        a,rows,_=prior_dev.train(key)
        original=graph.GraphWindow("graph_recent8")
        copied=[]
        for law,phase in (("A","train-initial"),("B","train-next")):
            for i in range(16):
                for row in world.pair(law,key,phase,i):
                    original.observe(world.copy_public(row))
                    copied.append(row)
        self.assertEqual(rows,tuple(copied))
        baseline=graph.checkpoint("graph_recent8",original)
        one=d.compare_condition(key,"D",2,a,baseline)
        two=d.compare_condition(key,"D",2,a,baseline)
        self.assertEqual(one,two)
        self.assertEqual(len(one["episodes"]),12)
        self.assertIn(one["selected_rules_different"],(0,1,2,3))
        self.assertLessEqual(one["retained_public_do_pairs"],4)
        self.assertEqual(contrast.checkpoint(contrast.restore(a)),a)
        self.assertEqual(graph.checkpoint("graph_recent8",
                         graph.restore("graph_recent8",baseline)),baseline)

    def test_classification_rules_are_frozen_and_mutually_exclusive(self):
        baseline={"factual_bit_accuracy":.80,
                  "intervention_flip_bit_accuracy":.80}
        worse={"factual_bit_accuracy":.78,
               "intervention_flip_bit_accuracy":.80}
        equal={"factual_bit_accuracy":.81,
               "intervention_flip_bit_accuracy":.80}
        self.assertEqual(d.classification(worse,baseline,.0,-.05),
                         "HYPOTHESIS_SELECTION_LIMIT_DIAGNOSTIC")
        self.assertEqual(d.classification(equal,baseline,.0,-.05),
                         "POLICY_OR_CALIBRATION_MISMATCH_DIAGNOSTIC")
        self.assertEqual(d.classification(equal,baseline,.06,-.05),
                         "PLANNER_LIMITATION_DETECTED")
        self.assertEqual(d.classification(equal,baseline,.0,.01),
                         "MIXED_OR_INCONCLUSIVE_DIAGNOSTIC")

    def test_original_checkpoint_readback_and_no_extra_actions(self):
        key="mechanical:alpha"
        start,_,_=prior_dev.train(key)
        snap=prior_dev.challenge(start,"F",key,4)
        actor=contrast.restore(snap)
        self.assertLessEqual(len(actor.rows),8)
        self.assertEqual(d.retained_contrasts(actor),
                         sum(actor.action_counts[i]==actor.action_counts[i-1]+1
                             and actor.rows[i][0]!=actor.rows[i-1][0]
                             for i in range(1,len(actor.rows))))
        x,g=admission.contexts(key,"F",1)[0]
        got=prior_dev.episode(snap,"F",x,g)
        self.assertLessEqual(len(got[2]),2)
        self.assertLessEqual(got[0],world.exact_oracle("F",x,g)+1e-10)


if __name__=="__main__":
    unittest.main()
