"""AAI-12Q causal contrastive representation integrity and negative tests."""
from __future__ import annotations
import json
from pathlib import Path
import subprocess
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"AAI-12P"))
sys.path.insert(0,str(HERE))
import world,controls,admit
import invariants,dev


class CausalInvariantMechanism(unittest.TestCase):
    def test_prereg_before_source_and_original_strong_baseline_frozen(self):
        p=json.loads((HERE/"prereg.json").read_text("utf8"))
        self.assertEqual(p["id"],"AAI-12Q")
        self.assertEqual(p["source_custody"]["parent_sha"],
                         "abd374e7dc433981df991e103d8ebdff0b5eb093")
        self.assertEqual(p["source_custody"]["source_controls_blob"],
                         "042b36f66fa14e0c7c7f39fe709ed58df9776eed")
        self.assertEqual(p["evaluation"]["source_baseline"]["reward"],2.673541667)
        self.assertEqual(p["evaluation"]["prespecified_go_no_go"]["minimum_integer_reachable_hits"],48)
        self.assertEqual(p["safety"]["science_cohorts_used"],0)
        self.assertTrue(p["no_post_result_tuning"])
        self.assertFalse(p["safety"]["no_native_yggdrasil"] is False)

    def test_original_four_causal_grammars_and_frozen_weight(self):
        self.assertEqual(len(controls.GRAMMARS),4)
        self.assertEqual(invariants.EFFECT_WEIGHT,2)
        self.assertEqual(invariants.MAX_PUBLIC_EVENTS,8)
        self.assertEqual(len(invariants.ARMS),2)
        self.assertEqual(len(world.FIT),4)
        self.assertEqual(len(world.TRANSFER),12)
        self.assertEqual(len(controls.METHODS),8)

    def test_actual_do_pair_recognition_and_false_cross_world_exclusion(self):
        law=world.TRANSFER[0]
        first=world.start(law,world.INPUTS[37],world.GOALS[5])
        second=world.do(law,first,world.ACTIONS[8])
        self.assertEqual(len(invariants.public_do_pairs([first,second])),1)
        invalid={**second,"goal":world.GOALS[2]}
        invalid["reward"]=world.reward(invalid["mediators"],invalid["goal"],1)
        self.assertEqual(invariants.public_do_pairs([first,invalid]),())
        old={**second,"actions_taken":0,
             "reward":world.reward(second["mediators"],second["goal"],0)}
        self.assertEqual(invariants.public_do_pairs([first,old]),())

    def test_effect_constraint_uses_real_bit_changes_not_hidden_law(self):
        law=world.TRANSFER[1]
        before,after=world.pair(law,"mechanical:alpha","challenge",0)
        pairs=invariants.public_do_pairs([before,after])
        self.assertEqual(len(pairs),1)
        p0,p1,m0,m1=pairs[0]
        self.assertEqual(tuple(p0[:8]),tuple(before["x"]))
        self.assertEqual(tuple(p1[:8]),tuple(after["x"]))
        self.assertEqual(tuple(m0),tuple(before["mediators"]))
        self.assertEqual(tuple(m1),tuple(after["mediators"]))
        for out in range(4):
            self.assertIn(m0[out]^m1[out],(0,1))
        with self.assertRaises(ValueError):
            invariants.contrastive_rule_indices([before,after],None)
        with self.assertRaises(ValueError):
            invariants.contrastive_rule_indices([before]*9,True)

    def test_pointwise_equal_state_ablation_exactly_matches_original_MAP(self):
        rows=[]
        for law in (world.FIT[-1],world.TRANSFER[1]):
            for i in range(4):
                rows.extend(world.pair(law,"mechanical:beta",
                                       "fit" if law in world.FIT else "challenge",i))
        rows=rows[-8:]
        equal=invariants.CausalInvariantModel(invariants.ABLATION)
        original=controls.Control("causal_structure_recent8")
        for row in rows:
            equal.observe(row)
            original.observe(row)
        self.assertEqual(equal.rows,original.rows)
        self.assertEqual(invariants.contrastive_rule_indices(equal.events,False),
                         controls._grammatical_map(original.rows))
        for x in world.INPUTS[::13]:
            self.assertEqual(equal.predict(x),original.predict(x))
        self.assertEqual(equal._best_rules,original._best_rules)

    def test_exact_shared_action_choice_and_limited_one_step_program(self):
        for arm in invariants.ARMS:
            actor=invariants.CausalInvariantModel(arm)
            for i in range(4):
                for row in world.pair(world.FIT[1],"mechanical:alpha","fit",i):
                    actor.observe(row)
            row=world.start(world.TRANSFER[3],world.INPUTS[33],world.GOALS[7])
            self.assertEqual(actor.choose(row),controls.choose(actor,row))
            self.assertIn(actor.choose(row),(None,*world.ACTIONS))
            self.assertEqual(len(actor.rows),8)
            self.assertEqual(actor.events[-1]["actions_taken"],1)

    def test_equal_public_memory_cold_restore_no_hypothesis_leak(self):
        for arm in invariants.ARMS:
            actor=invariants.CausalInvariantModel(arm)
            for i in range(12):
                actor.observe(world.pair(world.FIT[0],"mechanical:alpha","fit",i)[0])
            snap=invariants.checkpoint(actor)
            self.assertEqual(len(json.loads(snap)["rows"]),8)
            for x in world.INPUTS[::11]:
                actor.predict(x)
            self.assertEqual(invariants.checkpoint(actor),snap)
            self.assertEqual(invariants.checkpoint(invariants.restore(arm,snap)),snap)
            self.assertEqual(set(json.loads(snap)),{"type","arm","rows"})
            self.assertNotIn("oracle",snap)
            self.assertNotIn("rules",snap)
            with self.assertRaises(ValueError):
                invariants.restore(arm,snap+" ")
            other=next(a for a in invariants.ARMS if a!=arm)
            with self.assertRaises(ValueError):
                invariants.restore(other,snap)

    def test_same_data_training_and_challenge_cold_forks(self):
        key="mechanical:alpha"
        saved,public,elapsed=dev.train(key)
        self.assertEqual(len(public),64)
        self.assertEqual(set(saved),set(dev.ARMS))
        self.assertTrue(all(name in elapsed for name in dev.ARMS))
        ab=invariants.restore(invariants.ABLATION,saved[invariants.ABLATION])
        iv=invariants.restore(invariants.CANDIDATE,saved[invariants.CANDIDATE])
        self.assertEqual(ab.events,iv.events)
        self.assertEqual(ab.rows,iv.rows)
        original=controls.restore(dev.BEST,saved[dev.BEST])
        self.assertEqual(original.rows,ab.rows)
        ab_new,_=dev.challenge(invariants.ABLATION,saved[invariants.ABLATION],
                               world.TRANSFER[0],key)
        iv_new,_=dev.challenge(invariants.CANDIDATE,saved[invariants.CANDIDATE],
                               world.TRANSFER[0],key)
        self.assertEqual(invariants.restore(invariants.ABLATION,ab_new).events,
                         invariants.restore(invariants.CANDIDATE,iv_new).events)

    def test_real_two_action_causal_episode_never_privileged_overfit(self):
        key="mechanical:alpha"
        saved,_,_=dev.train(key)
        for name in dev.ARMS:
            snap,_=dev.challenge(name,saved[name],world.TRANSFER[2],key)
            x,goal=world.contexts(key,world.TRANSFER[2],1)[0]
            a=dev.episode(name,snap,world.TRANSFER[2],x,goal)
            b=dev.episode(name,snap,world.TRANSFER[2],x,goal)
            self.assertEqual(a,b)
            self.assertLessEqual(len(a[2]),2)
            exact,_=world.exact_oracle(world.TRANSFER[2],x,goal)
            self.assertLessEqual(a[0],exact+1e-9)
            self.assertEqual(dev.checkpoint(name,dev.restore(name,snap)),snap)

    def test_public_schema_and_first_science_use_remains_disarmed(self):
        actor=invariants.CausalInvariantModel(invariants.CANDIDATE)
        row=world.start(world.TRANSFER[1],world.INPUTS[29],world.GOALS[3])
        for field in ("law","world_id","oracle","seed","counterfactual","phase"):
            with self.assertRaises(ValueError):
                actor.observe({**row,field:"secret"})
            with self.assertRaises(ValueError):
                actor.choose({**row,field:"secret"})
        for forbidden in (994000,995000,995063,996000,996031,"995000",
                          "mechanical:gamma",None):
            with self.assertRaises(PermissionError):
                world.fixture(forbidden)
            with self.assertRaises(PermissionError):
                world.law_name(forbidden)
        cli=[sys.executable,"-B",str(HERE/"dev.py")]
        for extras in (["--primary"],["--source-dev","--primary"],
                       ["--world","995000"],[]):
            p=subprocess.run(cli+extras,text=True,capture_output=True,timeout=8)
            self.assertNotEqual(p.returncode,0)
            self.assertTrue("DISARMED" in p.stderr or
                            "unrecognized arguments" in p.stderr or
                            "only frozen source-only" in p.stderr)


if __name__=="__main__":
    unittest.main()
