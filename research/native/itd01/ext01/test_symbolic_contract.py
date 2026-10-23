"""EXT01 native symbolic source-contract adversarial tests. No benchmark imports."""
import ast
from pathlib import Path
import subprocess
import tempfile
import unittest

from check_symbolic_contract import (
    FILES, UPSTREAM_SHA, audit, git_blob_sha, inspect_symbolic_ast,
)

FAKE = '''
MAX_STONES = 3
MAX_POTIONS = 12
DEFAULT_MAX_STEPS_PER_TRIAL = 20
class SymbolicAlchemy:
    def __init__(self, chemistry_gen, reward_weights, items_gen, num_trials,
                 end_trial_action=False,
                 max_steps_per_trial=DEFAULT_MAX_STEPS_PER_TRIAL,
                 see_chemistries=None, generate_events=False,
                 fix_obs_length=False, observe_used=True):
        pass
    def reset(self):
        return self.reset_no_observation()
    def step(self, action):
        return self.step_slot_based_action(self._int_to_slot_based_action(action))
    def step_slot_based_action(self, action):
        return self._internal_step(action)
    def observation(self):
        return self.result
    def observation_spec(self):
        obs_features = 4
        return {"symbolic_obs":obs_features}
    def action_spec(self):
        num_special_actions = 2 if self._end_trial_action else 1
        num_actions = MAX_STONES * (MAX_POTIONS + 1) + num_special_actions
        return BoundedArray(minimum=0, maximum=num_actions - 1)
'''


class SourceContractTests(unittest.TestCase):
    def test_unmodified_source_layout(self):
        x = inspect_symbolic_ast(FAKE.encode())
        self.assertEqual(x["integer_action_count_default_no_end_trial"], 40)
        self.assertEqual(x["integer_action_count_optional_end_trial"], 41)
        self.assertEqual(x["native_stone_slots"], 3)
        self.assertEqual(x["native_potion_slots"], 12)

    def test_stone_limit_must_not_drift(self):
        with self.assertRaisesRegex(ValueError, "stone-slot limit"):
            inspect_symbolic_ast(FAKE.replace("MAX_STONES = 3", "MAX_STONES = 4").encode())

    def test_potion_limit_must_not_drift(self):
        with self.assertRaisesRegex(ValueError, "potion-slot limit"):
            inspect_symbolic_ast(FAKE.replace("MAX_POTIONS = 12", "MAX_POTIONS = 6").encode())

    def test_feedback_time_contract_not_invented(self):
        x = inspect_symbolic_ast(FAKE.encode())
        self.assertEqual(x["source_default_trial_step_limit"], 20)
        self.assertNotIn("artificial_delayed_feedback", x)

    def test_no_chemistry_observation_override(self):
        with self.assertRaisesRegex(ValueError, "see_chemistries"):
            inspect_symbolic_ast(FAKE.replace("see_chemistries=None",
                                             "see_chemistries={}").encode())

    def test_end_trial_mode_not_changed(self):
        with self.assertRaisesRegex(ValueError, "end_trial_action"):
            inspect_symbolic_ast(FAKE.replace("end_trial_action=False",
                                             "end_trial_action=True").encode())

    def test_original_step_must_remain_native(self):
        with self.assertRaisesRegex(ValueError, "integer step"):
            inspect_symbolic_ast(FAKE.replace("return self.step_slot_based_action(self._int_to_slot_based_action(action))",
                                             "return self.result").encode())

    def test_hidden_observation_vector_not_inferred(self):
        with self.assertRaisesRegex(ValueError, "symbolic observation"):
            inspect_symbolic_ast(FAKE.replace('"symbolic_obs"', '"private_chemistry"').encode())

    def test_blob_integrity_is_content_bound(self):
        raw = b"binary\0native\r\n"
        self.assertEqual(len(git_blob_sha(raw)), 40)
        self.assertNotEqual(git_blob_sha(raw), git_blob_sha(raw + b"!"))
        self.assertEqual(len(FILES), 4)
        self.assertEqual(len(UPSTREAM_SHA), 40)

    def test_unauthorized_lookalike_checkout_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            subprocess.run(("git","init","-q",str(repo)),check=True)
            with self.assertRaisesRegex(ValueError, "upstream source commit drift"):
                audit(repo)

    def test_source_parse_is_readonly_and_unsampled(self):
        x = inspect_symbolic_ast(FAKE.encode())
        self.assertNotIn("scientific_first_use", x)
        self.assertNotIn("generated_episodes", x)
        self.assertNotIn("pretrained_model", x)
        self.assertTrue(ast.parse(FAKE))


if __name__ == "__main__":
    unittest.main()
