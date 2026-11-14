"""AAI-11B grammar parity, real do-contrast, public custody, cold and disarm."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(HERE.parent/"AAI-11A"))
sys.path.insert(0,str(HERE.parent/"AAI-11P"))
import world,controls,learner as prior,contrast,dev


class FrozenContrastiveAssociation(unittest.TestCase):
    def test_prereg_and_frozen_original_sources(self):
        p=json.loads((HERE/"prereg.json").read_text("utf8"))
        self.assertEqual(p["id"],"AAI-11B")
        self.assertEqual(p["parent"]["sha"],
                         "c3e2601695579690bf3b3e83b93050018d88725f")
        self.assertEqual(p["source_development"]["historical_mean_reward"],
                         2.134027778)
        self.assertEqual(p["source_development"]["historical_comparison_source_run"],
                         43640947420)
        self.assertEqual(p["mechanism"]["selection"].split(" + ")[1][:1],"2")
        self.assertFalse(p["authority"]["scientific_first_use"])
        self.assertEqual(p["authority"]["cohort_consumption"],0)
        self.assertTrue(p["no_post_result_tuning"])

    def test_model_and_baseline_use_exact_same_public_graph_grammar(self):
        self.assertEqual(prior.GRAPH01,controls.PAIR_GRAMMAR)
        self.assertEqual(prior.SIZES,(45,45,84))
        new=contrast.InterventionTournament()
        old=prior.GraphWindow("graph_recent8")
        self.assertEqual(new.limit,8)
        self.assertEqual(new.name,old.name)
        self.assertEqual(new.stats["prior"],old.stats["prior"])
        for x in world.INPUTS:
            self.assertEqual(new.predict(x),old.predict(x))
        self.assertEqual(new.choose(world.start("A",world.INPUTS[0],
                                                world.GOALS[0])),
                         old.choose(world.start("A",world.INPUTS[0],
                                                world.GOALS[0])))

    def test_without_intervention_flips_prediction_matches_passive_control(self):
        new=contrast.InterventionTournament()
        old=prior.GraphWindow("graph_recent8")
        for i in range(7):
            row=world.start("A",world.INPUTS[i],world.GOALS[i%8])
            new.observe(row)
            old.observe(row)
        self.assertEqual(new.rows,old.rows)
        self.assertEqual(new.stats["mismatches"],old.stats["mismatches"])
        for x in world.INPUTS:
            self.assertEqual(new.predict(x),old.predict(x))

    def test_actual_intervention_changes_public_causal_contrast_weights(self):
        new=contrast.InterventionTournament()
        old=prior.GraphWindow("graph_recent8")
        before=world.start("C",(0,0,0,0,0,0),(1,0,1))
        after=world.do("C",before,(0,1))
        for row in (before,after):
            new.observe(world.copy_public(row))
            old.observe(world.copy_public(row))
        self.assertEqual(new.rows,old.rows)
        self.assertEqual(new.stats["mismatches"],old.stats["mismatches"])
        self.assertEqual(new.action_counts,[0,1])
        self.assertEqual(len(new._selection()),3)
        # Source cannot obtain causal effect labels; only observed endpoints.
        x0,m0=new.rows[0]
        x1,m1=new.rows[1]
        k0,k1=prior.x_key(x0),prior.x_key(x1)
        penalties=[
            2*int((prior.TRUTH01[k0][h]^prior.TRUTH01[k1][h])!=(m0[0]^m1[0]))
            for h in range(45)]
        self.assertTrue(any(penalties))
        self.assertTrue(all(p in (0,2) for p in penalties))

    def test_incomplete_or_stale_public_pair_is_not_used(self):
        new=contrast.InterventionTournament()
        old=prior.GraphWindow("graph_recent8")
        initial=world.start("D",world.INPUTS[2],world.GOALS[1])
        for row in (initial,world.do("D",initial,(3,1))):
            new.observe(row)
            old.observe(row)
        for i in range(10):
            row=world.start("B",world.INPUTS[i],world.GOALS[i%8])
            new.observe(row)
            old.observe(row)
        self.assertEqual(len(new.rows),8)
        self.assertEqual(len(new.action_counts),8)
        self.assertEqual(new.rows,old.rows)
        # Every row in the kept 8 is action_count=0: no action contrast.
        self.assertEqual(new.action_counts,[0]*8)
        for x in world.INPUTS:
            self.assertEqual(new.predict(x),old.predict(x))

    def test_cold_checkpoint_exact_and_no_cached_internal_rules(self):
        key="mechanical:alpha"
        snap,rows,seconds=dev.train(key)
        self.assertEqual(len(rows),64)
        self.assertGreaterEqual(seconds,0)
        actor=contrast.restore(snap)
        self.assertEqual(contrast.checkpoint(actor),snap)
        self.assertLessEqual(len(actor.rows),8)
        self.assertEqual(len(actor.rows),len(actor.action_counts))
        self.assertNotIn("_selected_rules",snap)
        self.assertNotIn("_pred_cache",snap)
        original=snap
        for law in ("A","B","C","D","E","F"):
            for n in (2,4):
                fork=dev.challenge(snap,law,key,n)
                self.assertEqual(contrast.checkpoint(contrast.restore(fork)),fork)
                for x,g in dev.admission.contexts(key,law,2):
                    out=dev.episode(fork,law,x,g)
                    self.assertGreaterEqual(out[0],-.1)
                    self.assertLessEqual(out[0],world.exact_oracle(law,x,g)+1e-9)
                self.assertEqual(snap,original)

    def test_no_oracle_or_hidden_causal_law_label_can_enter_model(self):
        example=world.start("C",world.INPUTS[7],world.GOALS[4])
        actor=contrast.InterventionTournament()
        for hidden in ("law","seed","oracle","simulator","future_action",
                       "regime","counterfactual","trainer_id"):
            initial=contrast.checkpoint(actor)
            with self.assertRaises(ValueError):
                actor.observe({**example,hidden:"C"})
            with self.assertRaises(ValueError):
                actor.choose({**example,hidden:"C"})
            self.assertEqual(contrast.checkpoint(actor),initial)
        for forbidden in (994000,995000,995063,996000,996031,"995000",
                          "mechanical:delta"):
            with self.assertRaises(PermissionError):
                world.fixture(forbidden)

    def test_corrupted_public_feedback_not_hidden_regime(self):
        key="mechanical:alpha"
        postB,_,_=dev.train(key)
        for law in ("C","F"):
            clean=dev.challenge(postB,law,key,4,corrupt=False)
            corrupted=dev.challenge(postB,law,key,4,corrupt=True)
            self.assertEqual(contrast.checkpoint(contrast.restore(clean)),clean)
            self.assertEqual(contrast.checkpoint(contrast.restore(corrupted)),corrupted)
            self.assertEqual(contrast.checkpoint(contrast.restore(postB)),postB)

    def test_canonical_checkpoint_fail_closed(self):
        model=contrast.InterventionTournament()
        state=contrast.checkpoint(model)
        with self.assertRaises(ValueError):
            contrast.restore(state+" ")
        doc=json.loads(state)
        doc["public_rows"].append([[0]*6,[0]*3,3])
        with self.assertRaises(ValueError):
            contrast.restore(controls.canonical(doc))
        with self.assertRaises(ValueError):
            contrast.restore(controls.canonical({"type":"wrong","public_rows":[]}))

    def test_firstuse_cli_disarmed(self):
        cmd=[sys.executable,"-B",str(HERE/"dev.py")]
        for tail in (["--primary"],["--fixture-admission","--primary"],
                     ["--world","995000"]):
            p=subprocess.run(cmd+tail,capture_output=True,text=True,timeout=8)
            self.assertNotEqual(p.returncode,0)
            self.assertTrue("DISARMED" in p.stderr or
                            "unrecognized arguments" in p.stderr)


if __name__=="__main__":
    unittest.main()
