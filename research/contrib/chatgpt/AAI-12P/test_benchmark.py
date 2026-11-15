"""AAI-12P independent source-only causal-world mechanical and privacy tests."""
from __future__ import annotations
import json
import subprocess
import sys
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import world,controls,admit


class HeterogeneousCausalWorldQualification(unittest.TestCase):
    def test_prereg_must_precede_model_science_remains_disarmed(self):
        p=json.loads((HERE/"prereg.json").read_text("utf8"))
        self.assertEqual(p["id"],"AAI-12P")
        self.assertEqual(p["baseline_custody"]["main_sha"],
                         "5e74f8db85b2f5839c42148c0dfba69a88b1a2c9")
        self.assertEqual(p["world_design"]["controlled_bits"],8)
        self.assertEqual(p["world_design"]["observable_mediator_bits"],4)
        self.assertEqual(p["pre_registered_admission"]["controls_count"],8)
        self.assertTrue(p["safety"]["no_scientific_first_use"])
        self.assertEqual(p["safety"]["science_cohorts_used"],0)
        self.assertTrue(p["no_post_result_tuning"])

    def test_structurally_different_four_families_and_worlds_deterministic(self):
        self.assertEqual(len(world.FIT),4)
        self.assertEqual(len(world.TRANSFER),12)
        self.assertEqual(len(world.WORLDS),16)
        self.assertEqual(len(set(world.WORLDS)),16)
        self.assertEqual(len(world.FAMILIES),4)
        self.assertEqual(len(world.INPUTS),256)
        self.assertEqual(len(world.GOALS),16)
        self.assertEqual(len(world.ACTIONS),16)
        signatures=set()
        for law in world.TRANSFER:
            self.assertEqual(world.parameters(law),world.parameters(law))
            samples=tuple(world.intermediates(law,x) for x in world.PROBE_INPUTS)
            signatures.add(samples)
            self.assertEqual(len(samples),64)
        self.assertEqual(len(signatures),12)

    def test_no_world_identifiers_or_privileged_fields_in_public_data(self):
        for law in (world.FIT[0],world.TRANSFER[0],world.TRANSFER[-1]):
            x,g=world.INPUTS[11],world.GOALS[6]
            first=world.start(law,x,g)
            self.assertEqual(set(first),world.PUBLIC_KEYS)
            self.assertEqual(len(first["x"]),8)
            self.assertEqual(len(first["mediators"]),4)
            self.assertEqual(first["actions_taken"],0)
            self.assertEqual(world.visible(first),
                             (world.bits(x,8),world.intermediates(law,x)))
            for private in ("law","world_id","oracle","causal_parameters","seed"):
                with self.assertRaises(ValueError):
                    world.visible({**first,private:law})

    def test_actual_do_action_and_cost_and_max_two_interventions(self):
        law=world.TRANSFER[4];x=world.INPUTS[42];g=world.GOALS[7]
        first=world.start(law,x,g)
        self.assertEqual(world.COST,.08)
        for action in world.ACTIONS:
            changed=world.do(law,first,action)
            self.assertEqual(tuple(changed["x"]),world.setbit(x,action))
            self.assertEqual(tuple(changed["mediators"]),
                             world.intermediates(law,world.setbit(x,action)))
            self.assertEqual(changed["actions_taken"],1)
            self.assertEqual(changed["reward"],
                             world.reward(changed["mediators"],g,1))
            third=world.do(law,changed,world.ACTIONS[-1])
            self.assertEqual(third["actions_taken"],2)
            with self.assertRaises(ValueError):
                world.do(law,third,action)

    def test_oracle_two_action_success_and_terminal_reward_bound(self):
        for law in world.TRANSFER[::3]:
            for x in world.INPUTS[::41]:
                for goal in world.GOALS[::5]:
                    optimal,reachable=world.exact_oracle(law,x,goal)
                    initial=world.start(law,x,goal)
                    self.assertGreaterEqual(optimal,initial["reward"])
                    self.assertIn(reachable,(0,1))
                    for action in world.ACTIONS:
                        s=world.do(law,initial,action)
                        self.assertLessEqual(s["reward"],optimal+1e-10)
                        for action2 in world.ACTIONS:
                            t=world.do(law,s,action2)
                            self.assertLessEqual(t["reward"],optimal+1e-10)
                    if tuple(initial["mediators"])==goal:
                        self.assertEqual(reachable,1)

    def test_source_law_and_seed_first_use_disarm(self):
        for invalid in (994000,995000,995063,996000,996031,None,
                        "995000","mechanical:gamma","mechanical:bad"):
            with self.assertRaises(PermissionError):
                world.fixture(invalid)
            with self.assertRaises(PermissionError):
                world.law_name(invalid)
        for valid in world.FIXTURES:
            self.assertEqual(world.fixture(valid),valid)
        for valid in world.WORLDS:
            self.assertEqual(world.law_name(valid),valid)

    def test_strong_structural_grammar_can_express_source_truth(self):
        self.assertEqual(len(controls.METHODS),8)
        self.assertEqual(len(controls.GRAMMARS),4)
        # Full supervised source-law structural evidence is a diagnostic
        # oracle grammar expressiveness TEST, never used to train a control.
        for law in world.WORLDS:
            evidence=[(x,world.intermediates(law,x))
                      for x in world.INPUTS[::4]]
            selected=controls._grammatical_map(evidence)
            self.assertEqual(len(selected),4)
            for o,i in enumerate(selected):
                self.assertLess(i,len(controls.GRAMMARS[o]))
                rule=controls.GRAMMARS[o][i]
                self.assertTrue(all(controls._rule(rule,(*x,*m))==m[o]
                                    for x,m in evidence))

    def test_all_eight_controls_fit_public_data_cold_and_predict_bounded(self):
        samples=[world.pair(world.FIT[0],world.FIXTURES[0],"fit",j)[0]
                 for j in range(4)]
        for name in controls.METHODS:
            actor=controls.Control(name)
            for row in samples:actor.observe(world.copy_public(row))
            actor.fit_checkpoint()
            snap=controls.checkpoint(actor)
            frozen=controls.restore(name,snap)
            self.assertEqual(snap,controls.checkpoint(frozen))
            for x in world.INPUTS[::29]:
                p=frozen.predict(x)
                self.assertEqual(len(p),4)
                self.assertTrue(all(0<=z<=1 for z in p))
            self.assertEqual(controls.checkpoint(frozen),snap)

    def test_genuine_challenge_pair_shuffling_preserves_exact_public_marginals(self):
        key=world.FIXTURES[0]
        changed=False
        for law in world.TRANSFER:
            originals=[world.pair(law,key,"challenge",i) for i in range(4)]
            labels=[tuple(pair[1]["mediators"]) for pair in originals]
            rotate=labels[1:]+labels[:1]
            self.assertEqual(sorted(labels),sorted(rotate))
            if labels!=rotate:changed=True
            for (pre,post),m in zip(originals,rotate):
                corrupted={**post,"mediators":list(m),
                           "reward":world.reward(m,post["goal"],post["actions_taken"])}
                world.visible(corrupted)
                self.assertEqual(set(pre),world.PUBLIC_KEYS)
        self.assertTrue(changed)

    def test_cli_firstuse_and_unknown_scope_denied_before_a_single_science_world(self):
        cmd=[sys.executable,"-B",str(HERE/"admit.py")]
        for args in (["--primary"],["--source-admission","--primary"],
                     ["--world","995000"],[]):
            result=subprocess.run(cmd+args,capture_output=True,text=True,timeout=8)
            self.assertNotEqual(result.returncode,0)
            self.assertTrue("DISARMED" in result.stderr or
                            "unrecognized arguments" in result.stderr or
                            "only frozen source-only" in result.stderr)


if __name__=="__main__":
    unittest.main()
