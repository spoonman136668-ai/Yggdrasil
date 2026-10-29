"""V36 selected-feedback information/decision mismatch regression tests."""
import itertools
import unittest

from research.itd02_v23_unfamiliar_mapping_audit import train_source
from research.itd02_v29_observational_equivalence_audit import selected_map
from research.itd02_v36_public_identifiability_rank_audit import (
    finite_family_information, observed_completions, frozen_rank_utilization,
)
from research.itd02_v35_action_conditioned_local_basis_audit import run
from yggdrasil.itd02_v17_neighbor_carried_learner_dev import ACTIONS,PUBLIC_CUES


class V36PublicInformationTests(unittest.TestCase):
    def test_finite_world_identification_uses_only_selected_events(self):
        observed,_=selected_map()
        self.assertEqual(len(observed),12)
        result=finite_family_information(observed)
        self.assertEqual(len(result["original_base_feedback"]),3)
        self.assertTrue(all(len(x)==12 for x in result["original_base_feedback"].values()))
        self.assertEqual(len(result["observed_reward_history_sha"]),3)

    def test_two_legal_completion_laws_observation_identical_optima_different(self):
        first=ACTIONS[0]
        second=ACTIONS[1]
        events=[{"selected_public":[cue,action,first],"reward":1.0}
                for cue,action in itertools.product(PUBLIC_CUES,ACTIONS)]
        events.extend({"selected_public":[PUBLIC_CUES[i],ACTIONS[i],second],
                       "reward":1.0} for i in range(3))
        assert len(events)==15
        result=observed_completions(events)
        self.assertEqual(result["selected_feedback_unique_count"],15)
        self.assertEqual(result["never_selected_actions"],21)
        self.assertEqual(len(result["low"]["optimal_actions"]),12)
        self.assertEqual(len(result["high"]["optimal_actions"]),12)
        self.assertEqual(result["different_optimal_context_count"],12)
        self.assertTrue(result["information_witness_at_least_6"])
        bad=[dict(x) for x in events]
        bad[-1]={"selected_public":list(events[0]["selected_public"]),"reward":10.0}
        with self.assertRaises(AssertionError):
            observed_completions(bad)

    def test_frozen_rank_readout_has_exact_36_score_dimensions(self):
        source=train_source()["pretrained_shared"]
        observed,_=selected_map()
        # Reuse the actual preregistered V35 learner and one D-family; no
        # original V22/V35 changes, no hidden law seen by the model.
        result=run("v22_shared_novelty","D1",source,observed)
        rank=frozen_rank_utilization(result)
        self.assertEqual(len(rank["policy_before"]),12)
        self.assertEqual(len(rank["policy_after"]),12)
        self.assertEqual(len(rank["margins_before"]),12)
        self.assertEqual(len(rank["margins_after"]),12)
        self.assertGreaterEqual(rank["frozen_36_score_changed_count"],0)
        self.assertLessEqual(rank["frozen_36_score_changed_count"],36)
        self.assertTrue(rank["native_parameters_changed"])
        self.assertEqual(len(rank["selected_probe_feedback"]),3)
        self.assertEqual(result["model_updates"],15)


if __name__=="__main__":
    unittest.main()
