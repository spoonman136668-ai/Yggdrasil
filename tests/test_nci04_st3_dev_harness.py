"""ST3 source-only development harness and frozen decision contract tests.

The source smoke uses already-consumed TRAINING law 3/seed 100 only.
All scored held law comparisons in this file are HANDWRITTEN FAKE fixtures,
not authentic reserved held development data or scientific results.
"""
import unittest

from research.nci04_st3.dev_compare import (
    NAMES, fresh_models, run_episode, score_results, load_checkpoint
)


def fabricated(law,seed,candidate,control=.17):
    scores={
        "candidate":candidate,
        "recurrent45":control,
        "action_count":control,
        "no_delay":control,
        "sham":control,
        "episode_erase":control,
    }
    return {
        "law_id_evaluator_only":law,
        "seed_evaluator_only":seed,
        "phase":"held_fixture_not_original_source",
        "original_source_steps":64,
        "actual_source_steps":64,
        "source_action_outcome_sha256":"handwritten-only",
        "preaction_brier":scores,
        "delayed_action2_followed_by_action3_steps":16,
        "delayed_action2_to_action3_brier":scores,
        "candidate_trained_observed_actions":100,
        "cold_model_restarts":len(NAMES),
        "per_model_wall_ns":{n:100 for n in NAMES},
        "source_wall_ns":100,
        "blind_actor_wall_ns":100,
        "shared_process_peak_rss_bytes":123456,
    }


class ST3MatchedHarnessSourceFree(unittest.TestCase):
    def test_single_already_consumed_training_source_episode(self):
        models=fresh_models()
        receipt=run_episode(3,100,models,"train",train=True,
                            per_step_hash=True)
        self.assertEqual(receipt["actual_source_steps"],64)
        self.assertEqual(receipt["cold_model_restarts"],len(NAMES))
        self.assertEqual(len(receipt["source_action_outcome_sha256"]),64)
        self.assertEqual(len(receipt["candidate_per_action_state_sha_chain"]),64)
        self.assertEqual(receipt["candidate_trained_observed_actions"],64)
        self.assertEqual(receipt["phase"],"train")
        self.assertTrue(receipt["independent_science_first_use"] is False)
        self.assertTrue(receipt["learner_received_private_law_or_mask"] is False)
        self.assertIsNone(receipt["preaction_brier"])
        self.assertEqual(models["candidate"].accounting()["extra_neural_weights"],0)
        self.assertTrue(models["action_count"].accounting()[
            "allocated_information_capacity_equal"
        ])

    def test_frozen_development_checks_cannot_be_overridden_by_one_win(self):
        laws=(29,31,37,41)
        seeds=(201,202,203,204,205,206,207,208)
        episodes=[
            fabricated(law,seed,.16) for law in laws for seed in seeds
        ]
        accounts={
            "candidate":{"binary_residual_uint8_counter_capacity_bytes":3456},
            "action_count":{"nine_profile_uint8_evidence_bytes":3456},
        }
        negative=score_results(episodes,{"pass":False},accounts)
        self.assertEqual(negative["pre_cross_os_disposition"],"DEV_NO_GO")
        self.assertFalse(negative["checks"][
            "pooled_0_02_better_than_strongest_trained_conventional_and_count"
        ])
        self.assertTrue(negative["checks"][
            "effective_conventional_integer_memory_capacity_matched"
        ])
        self.assertFalse(negative["checks"][
            "retains_95pct_of_chance_corrected_law_gain_after_8_laws"
        ])

    def test_fake_good_scores_only_allow_dev_signal_pending_portability(self):
        episodes=[
            fabricated(law,seed,.08,.18)
            for law in (29,31,37,41)
            for seed in (201,202,203,204,205,206,207,208)
        ]
        accounts={
            "candidate":{"binary_residual_uint8_counter_capacity_bytes":3456},
            "action_count":{"nine_profile_uint8_evidence_bytes":3456},
        }
        result=score_results(episodes,{"pass":True},accounts)
        self.assertEqual(result["pre_cross_os_disposition"],
                         "DEV_SIGNAL_PENDING_PORTABILITY_NOT_SCIENCE")
        self.assertTrue(all(result["checks"].values()))
        self.assertEqual(result["preaction_eval_source_steps"],2048)

    def test_refuse_fewer_than_frozen_2048_held_steps(self):
        accounts={
            "candidate":{"binary_residual_uint8_counter_capacity_bytes":3456},
            "action_count":{"nine_profile_uint8_evidence_bytes":3456},
        }
        with self.assertRaises(ValueError):
            score_results([fabricated(29,201,.01)],{"pass":True},accounts)

    def test_match_controls_all_have_observation_only_methods(self):
        models=fresh_models()
        self.assertEqual(set(models),set(NAMES))
        for name,m in models.items():
            before=m.snapshot()
            if name=="recurrent45":
                self.assertEqual(len(m.predict((0,)*8,0)),8)
            else:
                self.assertEqual(m.predict((0,)*8,0),[0.5]*8)
            self.assertEqual(before,m.snapshot())


if __name__=="__main__":
    unittest.main()
