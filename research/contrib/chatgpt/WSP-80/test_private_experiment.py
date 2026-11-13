"""WSP80 private orchestrator custody checks: unregistered developer source only."""
import sys
import unittest
from pathlib import Path
from hashlib import sha256

sys.path.insert(0, str(Path(__file__).parent))
from private_experiment import (
    collect_developer_sessions, freeze_developer_models,
    score_after_prelabel_freeze,
)
from source import World


class PrivateOrchestratorDevelopmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.world = World(9001, "quartic_positive",
                          tuple(range(6)), tuple(range(6)))
        cls.paid = collect_developer_sessions(cls.world)

    def test_independent_real_charges_and_common_stageA(self):
        candidate = self.paid["candidate_ledger"]
        random = self.paid["random_ledger"]
        self.assertIsNot(candidate, random)
        self.assertEqual(len(candidate), 384)
        self.assertEqual(len(random), 384)
        self.assertEqual(candidate[:144], random[:144])
        self.assertNotEqual(
            tuple(x.action for x in candidate[144:]),
            tuple(x.action for x in random[144:]))
        for ledger in (candidate, random):
            self.assertEqual(ledger[0].before, (0,) * 6)
            self.assertTrue(all(x.action_cost == 1 for x in ledger))
            self.assertTrue(all(ledger[i].after == ledger[i + 1].before
                                for i in range(383)))
        self.assertIn('"charges":144', self.paid["stage_a_snapshot"])

    def test_registered_world_rejected_without_physics_use(self):
        registered = World(5601, "degree2_control",
                           tuple(range(6)), tuple(range(6)))
        with self.assertRaises(PermissionError):
            collect_developer_sessions(registered, seed=5601)

    def test_neural_training_cannot_be_faked_or_silently_skipped(self):
        with self.assertRaises(ValueError):
            freeze_developer_models(self.paid, train_conventional=False)

    def test_private_scoring_rejects_unfrozen_receipt(self):
        fake = {"prelabel": "not a real frozen receipt",
                "prelabel_sha256": sha256(b"bad").hexdigest(),
                "source_private_receipt": self.world.receipt()}
        with self.assertRaises(ValueError):
            score_after_prelabel_freeze(self.world, fake)
        with self.assertRaises(PermissionError):
            score_after_prelabel_freeze(
                World(5601, "degree2_control", tuple(range(6)),
                      tuple(range(6))), fake, seed=5601)

    def test_no_private_import_in_frozen_controls(self):
        root = Path(__file__).parent
        for name in ("numerical_controls.py", "controls.py",
                     "independent_symbolic.py", "frozen_scoring.py"):
            code = (root / name).read_text("utf-8")
            self.assertNotIn("from private_experiment import", code)
            self.assertNotIn("import private_experiment", code)


if __name__ == "__main__":
    unittest.main()
