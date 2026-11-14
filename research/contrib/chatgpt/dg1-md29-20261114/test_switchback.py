"""DG1-MD29 frozen toy tests: physical action consequences and interference."""

import importlib.util
import json
from pathlib import Path
import unittest

SOURCE=Path(__file__).with_name("switchback.py")
spec=importlib.util.spec_from_file_location("dg1_md29",SOURCE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class NonstationaryCausalInterference(unittest.TestCase):
    def test_frozen_protocol_parent_cohort_custody(self):
        x=m.protocol()
        self.assertEqual(m.PREREG_SHA,
                         "401a70dd89f5989c8a32943804d856705c06e7f8")
        self.assertEqual(x["parent_sha"],m.PARENT)
        self.assertEqual(x["world"]["context_holdout"],[0,1])
        self.assertEqual(len(m.TRAIN_NORMAL),240)
        self.assertEqual(len(m.TRAIN_INTERFERENCE),240)
        self.assertEqual(len(m.TOY),32)
        self.assertEqual(len(m.COLD),16)
        self.assertEqual(len(m.RESERVED),96)
        for seed in (1070001,1070027,1070096):
            for role in ("normal","interference","toy","cold","registered"):
                with self.assertRaisesRegex(
                        AssertionError,"REGISTERED_SEED_USE_FORBIDDEN"):
                    m.guard(seed,role)
        self.assertFalse(set(m.TRAIN_NORMAL)&set(m.TRAIN_INTERFERENCE))
        self.assertFalse(set(m.TOY)&set(m.COLD))

    def test_hidden_polarity_alias_and_action_consequence(self):
        plus=m.Switchback(201,m.UNSEEN,0,latent_override=1,
                          flip_override=False)
        minus=m.Switchback(201,m.UNSEEN,0,latent_override=-1,
                           flip_override=False)
        self.assertEqual(plus.observe(),minus.observe())
        for forbidden in ("_polarity","_flip","seed","internal_state"):
            self.assertNotIn(forbidden,plus.observe())
        a=plus.step("probe")
        b=minus.step("probe")
        self.assertEqual(a[0]["stage1_probe_effect"],
                         -b[0]["stage1_probe_effect"])
        self.assertEqual(a[1],-0.04)
        self.assertEqual(b[1],-0.04)
        plus.step("apply_A")
        minus.step("apply_A")
        self.assertNotEqual(
            plus.observe()["stage1_actuator_effect"],
            minus.observe()["stage1_actuator_effect"])
        for world in (plus,minus):
            self.assertEqual(world.observe()["stage"],"s2")
            with self.assertRaisesRegex(
                    AssertionError,"REPEAT_OR_INVALID_PHYSICAL_PROBE"):
                # Once stage2 paid probe is consumed, repetition is forbidden.
                world.step("probe")
                world.step("probe")

    def test_same_visible_stage2_opposite_flip_requires_new_information(self):
        changed=m.Switchback(205,m.UNSEEN,1,latent_override=1,
                             flip_override=True)
        still=m.Switchback(205,m.UNSEEN,1,latent_override=1,
                           flip_override=False)
        self.assertEqual(changed.observe(),still.observe())
        for w in (changed,still):
            w.step("probe")
            w.step("apply_A")
        self.assertEqual(changed.observe(),still.observe())
        c=changed.step("probe")[0]
        d=still.step("probe")[0]
        self.assertEqual(c["stage2_probe_effect"],
                         -d["stage2_probe_effect"])
        self.assertEqual(c["stage"],"s2_probed")
        self.assertEqual(d["stage"],"s2_probed")
        for w in (changed,still):
            w.step("apply_B")
            self.assertEqual(w.phase,"done")
            self.assertEqual(w.receipt()["paid_steps"],4)

    def test_shared_paid_training_normal_then_interference_not_leak(self):
        rows,coverage,digest=m.dataset()
        self.assertEqual(len(rows),480)
        self.assertEqual(set(coverage.values()),{80})
        # Each mode/context pair includes 40 real physical episodes per
        # hazard, while frozen min=70 applies to pair total=80.
        for mode in (0,1):
            for context in m.TRAIN_CONTEXTS:
                for hazard in (0,1):
                    self.assertEqual(sum(row["mode"]==mode and
                                         row["context"]==context and
                                         row["hazard"]==hazard for row in rows),40)
        self.assertEqual(sum(r["paid_steps"] for r in rows),1920)
        self.assertEqual(len(digest),64)
        self.assertTrue(all(tuple(row["context"])!=m.UNSEEN for row in rows))
        self.assertTrue(all(len(row["raw_public_trace"])==4 for row in rows))
        self.assertEqual({r["mode"] for r in rows[:240]},{0})
        self.assertEqual({r["mode"] for r in rows[240:]},{1})
        self.assertTrue(all(set(row["signed_observations"]).issubset({-1,1})
                            for row in rows))
        self.assertTrue(all("_polarity" not in m.canon(r["raw_public_trace"])
                            for r in rows))

    def test_gated_memory_protects_first_law_and_strong_bayes_fitted(self):
        rows,_,_=m.dataset()
        models=m.fit(rows)
        self.assertEqual(set(models),set(m.ARMS))
        self.assertTrue(all(v.trained_rows==480 for v in models.values()))
        c=models["regime_gated_memory"]
        strong=models["trained_factorized_bayes"]
        bad=models["nongated_global_memory"]
        for mode in (0,1):
            self.assertEqual(c.relative(mode,0,1),
                             m.relative_physics(0,1,mode))
            self.assertEqual(strong.relative(mode,0,1),
                             m.relative_physics(0,1,mode))
        self.assertNotEqual(bad.relative(0,0,1),
                            m.relative_physics(0,1,0))
        self.assertEqual(c.normal_before_interference,
                         {"00":1,"10":-1,"11":1})
        self.assertEqual(c.relative(0,0,1),-1)
        self.assertEqual(strong.strong,{"base":1,"probe":-1,
                                      "act":-1,"mode":-1})
        for key,v in models.items():
            snap=v.checkpoint()
            self.assertEqual(m.Memory.restore(snap).checkpoint(),snap,key)

    def test_real_paid_probe_action_is_hazard_sensitive_and_limited(self):
        rows,_,_=m.dataset()
        c=m.Memory("regime_gated_memory")
        c.train(rows)
        low=m.Switchback(202,m.UNSEEN,0)
        high=m.Switchback(201,m.UNSEEN,1)
        for w in (low,high):
            self.assertEqual(c.act(w.observe()),"probe")
            w.step("probe")
            act=c.act(w.observe())
            self.assertIn(act,("apply_A","apply_B"))
            w.step(act)
            self.assertEqual(w.phase,"s2")
        self.assertFalse(c.requires_stage2_probe(low.observe()))
        self.assertTrue(c.requires_stage2_probe(high.observe()))
        self.assertIn(c.act(low.observe()),("apply_A","apply_B"))
        self.assertEqual(c.act(high.observe()),"probe")
        high.step(c.act(high.observe()))
        self.assertIn(c.act(high.observe()),("apply_A","apply_B"))
        with self.assertRaisesRegex(AssertionError,"ILLEGAL_OR_UNPAID_ACTION"):
            finished=m.Switchback(207,m.UNSEEN,0)
            finished.step("apply_A")
            finished.step("apply_B")
            finished.step("probe")

    def test_toy_frozen_gates_cold_retention_and_physical_ledger(self):
        r=m.toy_study()
        self.assertEqual(r["schema"],"yggdrasil.dg1-md29-toy.v1")
        self.assertFalse(r["registered_firstuse_executed"])
        self.assertTrue(r["cold_trace_parity"])
        self.assertEqual(r["training"]["paid_steps"],1920)
        self.assertEqual(len(r["scores"]),8)
        for name,episodes in r["physical_toy_episodes"].items():
            self.assertEqual(len(episodes),32,name)
            for row in episodes:
                self.assertEqual(len(row["actions"]),row["paid_steps"])
                self.assertEqual(len(row["trace"]),row["paid_steps"])
                self.assertLessEqual(row["paid_steps"],4)
                self.assertEqual(len(row["physical_sha256"]),64)
        self.assertEqual(r["classification"]==
                         "TOY_NOVELTY_CANDIDATE_PENDING_INDEPENDENT_QUALIFICATION",
                         all(r["frozen_task_gates"].values()) and
                         all(r["frozen_novelty_gates"].values()))
        print("MD29_TOY_CLASSIFICATION:"+r["classification"],flush=True)
        print("MD29_TOY_TASK_GATES:"+json.dumps(
            r["frozen_task_gates"],sort_keys=True),flush=True)
        print("MD29_TOY_NOVELTY_GATES:"+json.dumps(
            r["frozen_novelty_gates"],sort_keys=True),flush=True)
        print("MD29_TOY_METRICS:"+json.dumps({
            "training":r["training"],"scores":r["scores"],
            "strong_gain":r["strong_baseline_mean_gain"],
            "nongated_gain":r["nongated_ablation_mean_gain"],
            "always_gain":r["always_reprobe_mean_gain"],
            "never_gain":r["never_reprobe_mean_gain"],
            "paired_ablation_wins":r["paired_nongated_strict_wins"],
            "cold":r["cold_trace_parity"]},
            sort_keys=True),flush=True)


if __name__=="__main__":
    unittest.main()
