"""Mechanical-only checks; MUST NOT run preregistered primary seed cohorts."""
import importlib.util
import unittest
from pathlib import Path

path = Path(__file__).with_name("synthetic_replication.py")
spec = importlib.util.spec_from_file_location("y_syn01_mechanics", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class SyntheticMechanics(unittest.TestCase):
    def test_frozen_envelope(self):
        self.assertEqual(module.CAPACITY, (16, 7, 9))
        self.assertEqual(module.SEEDS, (809, 811, 821, 823))
        self.assertEqual(module.TOTAL_PROJECTIONS, 9216)
        self.assertEqual(module.TOTAL_CASES, 3072)

    def test_generator_smoke_non_study_seed(self):
        a = module.Generator(1, 0)
        b = module.Generator(1, 0)
        for _ in range(10):
            av, bv = a.uniform(), b.uniform()
            self.assertEqual(av, bv)
            self.assertTrue(0.0 <= av < 1.0)

    def test_projector_mechanical_control_no_primary_labels(self):
        project = module._load_qualified_mechanism()
        target = dict(total=9, best_count=5, consistency=0.0, utility=0.0, key=(99,), best=0, map_best=0)
        retained = dict(target, best_count=7, best=1, map_best=1)
        self.assertEqual(project(target, retained, "A0")["best"], 0)
        self.assertEqual(project(target, retained, "A1")["best"], 1)
        self.assertEqual(project(target, retained, "A2")["best"], 1)
        retained["map_best"] = 0
        self.assertEqual(project(target, retained, "A2")["best"], 0)

if __name__ == "__main__":
    unittest.main()
