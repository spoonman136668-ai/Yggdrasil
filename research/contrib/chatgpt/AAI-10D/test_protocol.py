"""AAI-10D information, matching, causal action, cold, bootstrap and fail-closed tests."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "AAI-10P"))
sys.path.insert(0, str(HERE.parent / "AAI-10A"))
sys.path.insert(0, str(HERE.parent / "AAI-10C"))
import protocol as p
import fixture_only
import benchmark as b
import models as old
import compact


class FrozenTransferProtocol(unittest.TestCase):
    def test_preregistration_and_source_only_firstuse(self):
        d=json.loads((HERE/"prereg.json").read_text("utf8"))
        self.assertEqual(d["id"],"AAI-10D")
        self.assertEqual(d["basis"]["head_sha"],
                         "58c0a3744e08e7547a85acdf88190decb6797584")
        self.assertEqual(d["train"]["total_rows"],64)
        self.assertEqual(d["fork"]["maximum_rows_per_method_before_evaluation"],80)
        self.assertEqual(d["fork"]["model_slot_cap"],96)
        self.assertFalse(d["seeds"]["primary_authorized"])
        self.assertEqual(d["seeds"]["science_seed_usage"],0)
        self.assertTrue(d["no_post_result_tuning"])
        self.assertEqual(set(d["controls"]["eligible_matched"]),set(p.MATCHED))
        self.assertEqual(p.LEARNERS,(p.CANDIDATE,p.ABLATION,*p.MATCHED,p.DIAGNOSTIC))
        self.assertNotIn("oracle",p.LEARNERS)

    def test_world_id_permissions_reject_all_science_and_unlisted(self):
        for value in (991000,992000,992063,993000,993031,990000,"992000",
                      "fixture-unregistered",None,0,""):
            with self.assertRaises(PermissionError):
                p.ensure_fixture(value)
            with self.assertRaises(PermissionError):
                p.design_trial(value,"training-alpha",0)
        for good in p.FIXTURES:
            self.assertEqual(p.ensure_fixture(good),good)

    def test_common_training_identical_public_data_budget_and_cold_forks(self):
        snap, evidence=p.common_training("handcrafted:one")
        self.assertEqual(len(evidence),64)
        self.assertEqual(set(snap),set(p.LEARNERS))
        self.assertEqual({frozenset(row) for row in evidence},{p.PUBLIC_KEYS})
        for name in p.LEARNERS:
            restored=p.restore_actor(name,snap[name])
            self.assertEqual(p.freeze_actor(name,restored),snap[name])
        self.assertEqual(p.restore_actor("one_slot",snap["one_slot"]).max_slots,1)
        self.assertEqual(p.restore_actor("aai10c",snap["aai10c"]).max_slots,3)
        for key in ("law","oracle","world_id","regime","counterfactual","seed"):
            bad={**evidence[0],key:"secret"}
            with self.assertRaises(ValueError):
                p.public_copy(bad)
            for name in p.LEARNERS:
                model=p.make_actor(name)
                with self.assertRaises(ValueError):
                    model.learn(bad)

    def test_fair_single_slot_full_challenge_budget_and_independent_retention(self):
        snap,_=p.common_training("handcrafted:one",
                                 labels=("aai10c","one_slot","tabular_recent16"))
        initial=dict(snap)
        for law in ("A","B","C","D"):
            for n in p.CHALLENGE_TRIALS:
                for name in initial:
                    after=p.challenge_checkpoint(name,initial[name],law,
                                                 "handcrafted:one",n)
                    restored=p.restore_actor(name,after)
                    self.assertEqual(p.freeze_actor(name,restored),after)
                    if name=="one_slot":
                        self.assertLessEqual(restored.slots[0]["rows"],80)
                        self.assertLessEqual(len(restored.slots),1)
                self.assertEqual(snap,initial)
        # At N=8, A/B evidence + challenge + one full 3-public-row episode
        # would be <=83 rows in a one-slot bank, below its immutable cap 96.
        self.assertLessEqual(64 + 2 * 8 + 3,96)

    def test_independent_episode_actual_actions_only_without_leakage(self):
        snap,_=p.common_training("handcrafted:one",labels=("aai10c","one_slot","tabular_recent16"))
        for name in snap:
            challenger=p.challenge_checkpoint(name,snap[name],"C","handcrafted:one",4)
            before=challenger
            x,g=p.heldout_contexts("handcrafted:one","C",count=1)[0]
            result=p.episode(name,challenger,"C",x,g)
            self.assertIn(result["actions"],(0,1,2))
            self.assertTrue(-.1 <= result["terminal_reward"] <=2)
            self.assertEqual(len(result["actual_action_indices"]),result["actions"])
            self.assertEqual(challenger,before)
            again=p.episode(name,challenger,"C",x,g)
            self.assertEqual(result,again)
            oracle=p.oracle_diagnostic("C",x,g)
            self.assertGreaterEqual(oracle,result["terminal_reward"])
        self.assertEqual(len(p.heldout_contexts("handcrafted:one","C")),16)
        self.assertEqual(len(set(p.heldout_contexts("handcrafted:one","D"))),16)

    def test_corrupted_public_feedback_marginals_and_equal_interventions(self):
        for fixture in p.FIXTURES:
            originals=p.challenge_pairs("C",fixture,8)
            corrupted=p.challenge_pairs("C",fixture,8,corrupt=True)
            self.assertEqual(len(originals),len(corrupted))
            orig_post=sorted(tuple(pair[1]["mediators"]) for pair in originals)
            bad_post=sorted(tuple(pair[1]["mediators"]) for pair in corrupted)
            self.assertEqual(orig_post,bad_post)
            self.assertEqual([pair[1]["x"] for pair in originals],
                             [pair[1]["x"] for pair in corrupted])
            self.assertEqual([pair[0] for pair in originals],
                             [pair[0] for pair in corrupted])
            self.assertTrue(any(x[1]["mediators"] != y[1]["mediators"]
                                for x,y in zip(originals,corrupted)))
            for pair in corrupted:
                self.assertEqual(pair[1]["reward"],
                                 b.reward(pair[1]["mediators"],pair[1]["goal"],1))
        with self.assertRaises(ValueError):
            p.challenge_pairs("C","handcrafted:one",0,True)

    def test_full_fixture_all_controls_and_return_A_hold_B_unfamiliar_C_D(self):
        r=fixture_only.run_fixture("handcrafted:two",context_count=1)
        self.assertEqual(r["method_condition_results"],4*2*len(p.LEARNERS))
        self.assertEqual(r["public_training_rows"],64)
        self.assertEqual(r["scored_science_cohorts"],0)
        self.assertTrue(r["checkpoint_preserved"])
        self.assertTrue(r["negative_feedback_marginals_preserved"])
        self.assertTrue(r["negative_feedback_causal_pairing_perturbed"])
        self.assertEqual(len(r["phase_independent_action_trace_sha256"]),64)

    def test_paired_whole_world_bootstrap_fixed_and_invalid_input_fence(self):
        data=[-0.10,0.00,0.15,0.30]
        one=p.paired_bootstrap(data)
        self.assertEqual(one,p.paired_bootstrap(data))
        self.assertEqual(one["cluster_count"],4)
        self.assertAlmostEqual(one["mean"],.0875)
        self.assertLessEqual(one["lower95"],one["mean"])
        self.assertGreaterEqual(one["upper95"],one["mean"])
        for bad in ([],[float("nan")],[1.0,float("inf")]):
            with self.assertRaises(ValueError):
                p.paired_bootstrap(bad)
        with self.assertRaises(ValueError):
            p.paired_bootstrap(data,n_draws=32)
        with self.assertRaises(ValueError):
            p.classify_primary([])

    def test_explicit_firstuse_and_world_generation_fail_closed(self):
        cmd=[sys.executable,"-B",str(HERE/"fixture_only.py")]
        for tail in (["--primary"],["--fixture","handcrafted:one","--primary"],
                     ["--fixture","992000"],["--world","992000"]):
            run=subprocess.run(cmd+tail,capture_output=True,text=True,timeout=6)
            self.assertNotEqual(run.returncode,0)
            self.assertTrue("DISARMED" in run.stderr or "invalid choice" in run.stderr or
                            "unrecognized arguments" in run.stderr)


if __name__=="__main__":
    unittest.main()
