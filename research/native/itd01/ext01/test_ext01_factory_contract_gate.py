"""Mutation tests: static source analysis only; do not import Alchemy."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from ext01_factory_contract_gate import audit_source

SOURCE = """
class SymbolicAlchemy:
    def __init__(self, fix_obs_length=False): pass

def get_symbolic_alchemy_level(level_name, observe_used=True, end_trial_action=False,
    num_trials=10, num_stones_per_trial=3, num_potions_per_trial=12,
    see_chemistries=None, generate_events=False):
    if 'perceptual_mapping_randomized' in level_name:
        stone_map_gen = random_stone_map
        potion_map_gen = random_potion_map
    else:
        stone_map_gen = all_fixed_stone_map
        potion_map_gen = all_fixed_potion_map
    if 'random_bottleneck' in level_name:
        graph_gen = lambda: graph_distr(possible_constraints())
    else:
        graph_gen = None
    if 'rotation' in level_name:
        rotation_gen = random_rotation
    else:
        rotation_gen = lambda: np.eye(3)
    return SymbolicAlchemy()
"""

class FactorySourceTest(unittest.TestCase):
    def test_fixture_passes(self):
        r = audit_source(SOURCE.encode())
        self.assertEqual(r["episodes"], 0)
        self.assertTrue(r["mode_not_sealed"])

    def test_missing_random_graph_rejected(self):
        with self.assertRaisesRegex(ValueError, "RANDOM_BRANCH_random_bottleneck"):
            audit_source(SOURCE.replace("graph_distr(possible_constraints())", "None").encode())

    def test_hidden_rotation_rejected(self):
        with self.assertRaisesRegex(ValueError, "RANDOM_BRANCH_rotation"):
            audit_source(SOURCE.replace("random_rotation", "np.eye(3)").encode())

    def test_missing_fixed_mapping_rejected(self):
        with self.assertRaisesRegex(ValueError, "FIXED_BRANCH_perceptual_mapping_randomized"):
            audit_source(SOURCE.replace("all_fixed_potion_map", "random_potion_map").encode())

    def test_changed_trials_rejected(self):
        with self.assertRaisesRegex(ValueError, "FACTORY_DEFAULT_num_trials"):
            audit_source(SOURCE.replace("num_trials=10", "num_trials=11").encode())

    def test_changed_stone_slots_rejected(self):
        with self.assertRaisesRegex(ValueError, "FACTORY_DEFAULT_num_stones_per_trial"):
            audit_source(SOURCE.replace("num_stones_per_trial=3", "num_stones_per_trial=2").encode())

    def test_changed_potion_slots_rejected(self):
        with self.assertRaisesRegex(ValueError, "FACTORY_DEFAULT_num_potions_per_trial"):
            audit_source(SOURCE.replace("num_potions_per_trial=12", "num_potions_per_trial=13").encode())

    def test_changed_constructor_default_rejected(self):
        with self.assertRaisesRegex(ValueError, "CONSTRUCTOR_LENGTH_DEFAULT"):
            audit_source(SOURCE.replace("fix_obs_length=False", "fix_obs_length=True").encode())

    def test_changed_constructor_forwarding_rejected(self):
        with self.assertRaisesRegex(ValueError, "FACTORY_LENGTH_ARG"):
            audit_source(SOURCE.replace("return SymbolicAlchemy()", "return SymbolicAlchemy(fix_obs_length=True)").encode())

    def test_duplicate_factory_switch_rejected(self):
        with self.assertRaisesRegex(ValueError, "SWITCH_random_bottleneck"):
            audit_source(SOURCE.replace("    if 'random_bottleneck' in level_name:",
              "    if 'random_bottleneck' in level_name:\n        if 'random_bottleneck' in level_name: pass").encode())

    def test_changed_chemistry_default_rejected(self):
        with self.assertRaisesRegex(ValueError, "FACTORY_DEFAULT_see_chemistries"):
            audit_source(SOURCE.replace("see_chemistries=None", "see_chemistries={}").encode())


if __name__ == "__main__":
    unittest.main()
