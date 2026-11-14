"""AAI-10C source-only causal sufficient-statistics and authority boundaries."""
import itertools
import json
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "AAI-10P"))
sys.path.insert(0, str(HERE.parent / "AAI-10A"))
import compact as c
import models as old
import benchmark as b


def examples(laws=("A","B"), reps=4):
    for law in laws:
        for rep in range(reps):
            for i,x in enumerate(b.INPUTS):
                init = b.public_initial(law,x,((rep+i)%2,rep%2))
                yield init
                yield b.public_step(law,init,b.ACTIONS[(rep+i)%6])


class CausalSufficientStats(unittest.TestCase):
    def test_frozen_prereg_prior_to_implementation(self):
        p=json.loads((HERE / "prereg.json").read_text(encoding="utf8"))
        self.assertEqual(p["id"],"AAI-10C")
        self.assertFalse(p["future_science"]["first_use_authorized"])
        self.assertTrue(p["no_post_result_tuning"])
        self.assertEqual(p["frozen_candidate"]["max_slots"],3)
        self.assertEqual(p["scientific_fresh_cohorts_used"] if "scientific_fresh_cohorts_used" in p else p["future_science"]["used"],0)
        self.assertEqual(p["lineage"]["base_sha"],"64a585010e13519c6290cc8c406154e1f23b9e78")

    def test_public_grammar_truth_table(self):
        self.assertEqual(len(c.TRUTH),8)
        self.assertEqual(c.N_HYPOTHESES,9)
        self.assertEqual(set(c.RULES),set(old.GRAMMAR))
        for bits in b.INPUTS:
            key=c.input_key(bits)
            self.assertEqual(c.TRUTH[key],
                             tuple(old.pattern(h,bits) for h in old.GRAMMAR))
        with self.assertRaises(ValueError):
            c.input_key((1,0,2))

    def test_sufficient_statistic_means_only_public_bitwise_counts(self):
        model=c.BoundedCausalSignatureBank(1)
        events=list(examples(laws=("A",),reps=2))
        for event in events:
            model.learn(event)
        self.assertEqual(len(events),32)
        slot=model.active()
        self.assertEqual(slot["rows"],32)
        expected=[[0]*9 for _ in range(2)]
        for row in events:
            x, mediator=old.visible(row)
            truth=c.TRUTH[c.input_key(x)]
            for out in range(2):
                for h in range(9):
                    expected[out][h] += (truth[h]!=mediator[out])
        self.assertEqual(slot["mismatches"],expected)
        self.assertEqual(len(slot["mismatches"]),2)
        self.assertEqual(len(slot["mismatches"][0]),9)
        self.assertEqual(len(model.slots),1)
        self.assertFalse(any("samples" in s for s in model.slots))

    def test_handcrafted_A_B_C_D_observations_and_closed_cold_forks(self):
        events=list(examples(laws=("A","B","C","D"),reps=1))
        self.assertEqual(len(events),64)
        for cap in (1,3):
            model=c.BoundedCausalSignatureBank(cap)
            for event in events:
                model.learn(event)
                self.assertLessEqual(len(model.slots),cap)
                self.assertTrue(all(0<=s["rows"]<=96 for s in model.slots))
                self.assertTrue(all(len(q)==9 for s in model.slots for q in s["mismatches"]))
            snap=c.checkpoint(model)
            restored=c.cold_restore(snap)
            self.assertEqual(c.checkpoint(restored),snap)
            for x, goal in itertools.product(b.INPUTS,b.GOALS):
                row=b.public_initial("A",x,goal)
                self.assertEqual(model.choose(row),restored.choose(row))
                self.assertEqual(model.predict(x),restored.predict(x))
                self.assertEqual(model.choose(row),old.plan(model,row))
                self.assertTrue(model.choose(row) in (None,*b.ACTIONS))

    def test_128_synthetic_public_events_not_scientific_cohorts(self):
        events=list(examples())
        self.assertEqual(len(events),128)
        model=c.BoundedCausalSignatureBank()
        for event in events:
            model.learn(event)
        self.assertEqual(model.scratch,[])
        self.assertLessEqual(len(model.slots),3)
        self.assertLessEqual(sum(s["rows"] for s in model.slots),128)
        self.assertEqual(c.checkpoint(c.cold_restore(c.checkpoint(model))),
                         c.checkpoint(model))

    def test_private_information_must_fail_atomically(self):
        model=c.BoundedCausalSignatureBank()
        valid=b.public_initial("A",(1,0,1),(0,1))
        for field in ("law","oracle","future_rewards","fork","seed"):
            snap=c.checkpoint(model)
            with self.assertRaises(ValueError):
                model.learn({**valid,field:"A"})
            with self.assertRaises(ValueError):
                model.choose({**valid,field:"A"})
            self.assertEqual(c.checkpoint(model),snap)

    def test_prior_is_public_and_protected_inactive_history(self):
        model=c.BoundedCausalSignatureBank()
        for event in examples(laws=("A","B"),reps=4):
            model.learn(event)
        frozen_snap=c.checkpoint(model)
        self.assertEqual(c.checkpoint(c.cold_restore(frozen_snap)),frozen_snap)
        seen=set(s["id"] for s in model.slots)
        self.assertEqual(len(seen),len(model.slots))
        self.assertIn(model.active_id,seen)
        self.assertTrue(all(v in (0,1) for s in model.slots
                            for row in s["prior"] for v in row))

    def test_cache_invalidated_on_update_and_not_in_checkpoint(self):
        model=c.BoundedCausalSignatureBank()
        start=b.public_initial("A",(0,1,0),(1,1))
        model.choose(start)
        self.assertGreater(len(model._plan_cache),0)
        model.learn(start)
        model.learn(b.public_step("A",start,(1,0)))
        self.assertEqual(model._plan_cache,{})
        self.assertEqual(model._signature_cache,{})
        snap=c.checkpoint(model)
        self.assertNotIn("_plan_cache",snap)
        self.assertNotIn("_signature_cache",snap)
        cold=c.cold_restore(snap)
        self.assertEqual(cold._plan_cache,{})

    def test_bad_cold_input_rejected(self):
        state=c.checkpoint(c.BoundedCausalSignatureBank())
        with self.assertRaises(ValueError):
            c.cold_restore(state+" ")
        d=json.loads(state)
        d["slots"][0]["rows"]=97
        with self.assertRaises(ValueError):
            c.cold_restore(old.canonical(d))
        d=json.loads(state)
        d["slots"][0]["prior"][0][1]=2
        with self.assertRaises(ValueError):
            c.cold_restore(old.canonical(d))

    def test_scientific_primary_cli_disarmed(self):
        done=subprocess.run([sys.executable,"-B",str(HERE/"profile_dev.py"),"--primary"],
                            capture_output=True,text=True,timeout=7)
        self.assertNotEqual(done.returncode,0)
        self.assertIn("DISARMED",done.stderr)


if __name__=="__main__":
    unittest.main()
