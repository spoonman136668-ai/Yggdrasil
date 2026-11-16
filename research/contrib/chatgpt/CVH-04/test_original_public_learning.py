"""CVH04 source-free real-source receipt, cold and matched-learning negatives."""
from __future__ import annotations
import json
from pathlib import Path
import tempfile
import unittest

import real_public_retrospective as x


class AuthenticConsumedCausalMDPTests(unittest.TestCase):
    def test_all_four_original_fkp26_transcripts_from_exact_source_receipts(self):
        episodes=x.load_original_public()
        self.assertEqual(list(episodes),list(x.SEEDS))
        self.assertEqual([len(episodes[k]) for k in x.SEEDS],[31,31,31,31])
        self.assertEqual(sum(len(ep) for ep in episodes.values()),124)
        self.assertEqual([sum(r.reward for r in episodes[k]) for k in x.SEEDS],
                         [16,15,18,17])
        self.assertEqual(sum(r.reward for ep in episodes.values() for r in ep),66)
        self.assertTrue(all(ep[-1].truncated for ep in episodes.values()))
        self.assertEqual(x.ARTIFACT_SHA,
            "4c877a6df5685516cc7ba445b2b90c90afb3674537ab741fb67adb5453e5c9ef")
        self.assertEqual(x.TRAIN,(996100,996101))
        self.assertEqual(x.HELD,(996102,996103))

    def test_real_source_model_matches_independent_conventional_and_cold(self):
        r=x.run_retrospective()
        m=r["metrics"]
        self.assertEqual(r["fkp26_original_run"],43930489602)
        self.assertEqual(r["source_reset_or_do_calls"],0)
        self.assertFalse(r["original_source_first_use"])
        self.assertFalse(r["held_was_prospectively_blind"])
        self.assertFalse(r["scientific_pass"])
        self.assertFalse(r["native_accepted"])
        self.assertFalse(r["deployment"])
        self.assertEqual(m["source_physical_do_actions_reused"],124)
        self.assertEqual(m["source_new_do_actions"],0)
        self.assertEqual(m["train_original_source_actions"],62)
        self.assertEqual(m["retro_held_original_source_actions"],62)
        self.assertEqual(m["held_coverage_supported_n"]+m["held_unsupported_n"],62)
        self.assertEqual(m["independent_exact_batch_agreements"],
                         m["held_coverage_supported_n"])
        self.assertEqual(m["independent_exact_batch_disagreements"],0)
        self.assertTrue(m["train_original_rows_preserved_in_posteval_memory"])
        self.assertEqual(len(m["train_checkpoint_sha256"]),64)
        self.assertEqual(len(m["continual_checkpoint_sha256"]),64)
        self.assertEqual(x.hash_json({k:v for k,v in r.items()
                                      if k!="metric_receipt_sha256"}),
                         r["metric_receipt_sha256"])
        self.assertEqual(x.run_retrospective(),r)

    def test_missing_or_mutated_original_public_source_fails_closed(self):
        original=json.loads((x.HERE/"consumed_public_fixture.json").read_text())
        edits=(
          ("schema",lambda a:a.update(schema="fake")),
          ("source_sha",lambda a:a.update(source_sha="0"*40)),
          ("artifact_hash",lambda a:a["fkp26"].update(artifact_zip_sha256="0"*64)),
          ("episode_order",lambda a:a["episodes"].reverse()),
          ("source_rows",lambda a:a["episodes"][2].update(rows_hex="00"*31)),
          ("source_receipt",lambda a:a["episodes"][0].update(original_public_receipt_sha256="a"*64)),
          ("extra_held_world",lambda a:a["episodes"].append(a["episodes"][0].copy())),
          ("wrong_reward_count",lambda a:a["episodes"][1].update(earned_rewards=0)),
          ("source_seeds",lambda a:a["episodes"][3].update(seed=996500)),
        )
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"changed.json"
            for name,edit in edits:
                doc=json.loads(json.dumps(original))
                edit(doc)
                path.write_text(json.dumps(doc),encoding="utf-8")
                with self.subTest(name=name),self.assertRaises(ValueError):
                    x.load_original_public(path)

    def test_four_step_return_has_no_future_cross_episode(self):
        rows=x.load_original_public()[996100]
        rewards=[r.reward for r in rows]
        actual=x.four_step_targets(rows)
        self.assertEqual(len(actual),31)
        self.assertEqual(actual[-1],rewards[-1])
        self.assertEqual(actual[-2],rewards[-2]+rewards[-1]/2)
        self.assertEqual(actual[0],
                         rewards[0]+rewards[1]/2+rewards[2]/4+rewards[3]/8)
        self.assertEqual(len(x.context_keys(rows)),31)

    def test_candidate_native_model_is_inherited_not_reimplemented(self):
        import inspect
        source=(x.HERE/"real_public_retrospective.py").read_text()
        self.assertIn("from earned_memory import EarnedReturnMemory",source)
        self.assertIn("from strong_conventional import batch_public_returns",source)
        self.assertIn("native = EarnedReturnMemory()",source)
        self.assertIn("cold = EarnedReturnMemory.restore(snapshot)",source)
        self.assertIn("full_batch = batch_public_returns(training)",source)
        self.assertIn("prior = sum(train_return) / len(train_return)",source)
        self.assertNotIn("import causal_gym",source)
        self.assertNotIn("source_factory(",source)
        self.assertNotIn("env.reset(",source)
        self.assertNotIn("env.do(",source)
        self.assertNotIn("requests.get(",source)

    def test_full_source_retrospective_has_no_supported_new_actions(self):
        episodes=x.load_original_public()
        n=x.run_retrospective()
        self.assertEqual(n["candidate"],"unchanged CVH01 EarnedReturnMemory")
        self.assertTrue(n["not_a_causal_off_policy_estimate"])
        self.assertTrue(n["actual_source_original_but_previously_consumed"])
        self.assertIn(n["classification"],(
            "RETROSPECTIVE_SOURCE_PREDICTIVE_DEVELOPMENT_SIGNAL",
            "RETROSPECTIVE_SOURCE_PREDICTIVE_DEVELOPMENT_NO_GO"))
        # The output must never turn this weak retrospective retrospective
        # measurement into an independent novel-causality proof.
        self.assertEqual(n["source_sha"],x.SOURCE_SHA)
        self.assertEqual(sum(v for v in n["metrics"].values()
                             if type(v) is int and False),0)


if __name__=="__main__":
    unittest.main()
