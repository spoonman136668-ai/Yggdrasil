"""Developer-only WSP80 baseline/scorer API checks: no registered sources."""
from pathlib import Path
from types import SimpleNamespace
import importlib.util
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parent))
from controls import (
    paid_rows, SparsePublicControl, PaidMemorization, ConventionalAdam384
)
from frozen_scoring import PUBLIC, freeze_public_outputs, score_frozen, REQUIRED


def dev_ledger():
    """Synthetic no-physics fixture; 384 repeated paid identity observations."""
    zero = (0,) * 6
    return tuple(SimpleNamespace(before=zero, action=0, after=zero,
                                 action_cost=1) for _ in range(384))


class FrozenControlTests(unittest.TestCase):
    def test_public_paid_ledger_rejects_missing_charge_and_discontinuity(self):
        rows = dev_ledger()
        self.assertEqual(len(paid_rows(rows)), 384)
        with self.assertRaises(ValueError):
            paid_rows(rows[:-1])
        damaged = list(rows)
        damaged[20] = SimpleNamespace(before=(1,) * 6, action=0,
                                      after=(0,) * 6, action_cost=1)
        with self.assertRaises(ValueError):
            paid_rows(damaged)
        damaged = list(rows)
        damaged[20] = SimpleNamespace(before=(0,) * 6, action=0,
                                      after=(0,) * 6, action_cost=0)
        with self.assertRaises(ValueError):
            paid_rows(damaged)

    def test_fixed_always_sham_stageA_and_memory_controls(self):
        rows = dev_ledger()
        for mode in ("fixed_degree3", "always_degree4", "sham_novelty"):
            model = SparsePublicControl(rows, mode=mode)
            self.assertEqual(model.training_actions, 384)
            self.assertEqual(model.predict((0,) * 6, 0), (0,) * 6)
            self.assertIsNone(model.predict((0,) * 6, 1))
            self.assertEqual(model.flagged_actions, [])
        earlier = SparsePublicControl(rows, stage_a_only=True)
        self.assertEqual(earlier.training_actions, 144)
        memory = PaidMemorization(rows)
        self.assertEqual(memory.predict((0,) * 6, 0), (0,) * 6)
        self.assertIsNone(memory.predict((1,) * 6, 0))

    def test_conventional_wrapper_requires_three_restarts_and_384_paid(self):
        rows = dev_ledger()
        mlp = ConventionalAdam384(9001)
        called = []
        # Fake optimizer is ONLY a developer API fixture; not neural training.
        def fixture(seed, public_rows):
            called.append(seed)
            self.assertEqual(len(public_rows), 384)
            return object(), 0.96, 500
        mlp._train = fixture
        results = mlp.fit(rows)
        self.assertEqual(len(called), 3)
        self.assertEqual(len(set(called)), 3)
        self.assertEqual(results["gradient_updates_total"], 1500)
        self.assertTrue(results["fully_trained"])
        with self.assertRaises(ValueError):
            mlp.fit(rows)
        with self.assertRaises(ValueError):
            ConventionalAdam384(0).fit(rows[:-1])

    def test_prelabel_freeze_equal_coverage_and_private_score(self):
        rows = dev_ledger()
        zero = (0,) * 6
        def candidate(state, action):
            return state if action == 0 else None
        def forced(state, action):
            return state
        models = {name: candidate for name in REQUIRED}
        models["mlp_forced"] = forced
        frozen = freeze_public_outputs(
            rows, models,
            lambda state, action: (0.9,) * 6,
            {"candidate_train_cpu_ns": 100, "mlp_train_cpu_ns": 200},
        )
        # The private truth and composition lists never enter freeze.
        truth = {pair: pair[0] for pair in PUBLIC}
        tasks = tuple((zero, 0, 0, zero) for _ in range(32))
        result = score_frozen(frozen, truth, tasks)
        candidate_result = result["scores"]["candidate"]
        self.assertEqual(result["paid_action_count"], 384)
        self.assertEqual(result["unique_paid_count"], 1)
        self.assertEqual(result["equal_coverage_count"], 64)
        self.assertEqual(candidate_result["physical"]["correct"], 64)
        self.assertEqual(candidate_result["genuinely_unpaid"]["correct"], 63)
        self.assertEqual(candidate_result["genuinely_unpaid"]["total"], 383)
        self.assertEqual(candidate_result["two_action"]["correct"], 32)
        self.assertEqual(result["stageA_retention_fraction"], 1.0)
        self.assertEqual(result["scores"]["mlp_matched"]["physical"]["correct"], 64)
        with self.assertRaises(ValueError):
            score_frozen(frozen.replace('"candidate"', '"tampered"', 1), truth, tasks)
        with self.assertRaises(ValueError):
            score_frozen(frozen, dict(list(truth.items())[:-1]), tasks)
        with self.assertRaises(ValueError):
            freeze_public_outputs(rows, {"candidate": candidate},
                                  lambda state, action: (0.9,) * 6, {})

    def test_no_private_source_or_neural_writer_import_in_controls_and_scorer(self):
        root = Path(__file__).parent
        for name in ("controls.py", "frozen_scoring.py"):
            body = (root / name).read_text("utf-8")
            for forbidden in ("from source import", "import source",
                              "_step_oracle", "import structural_weights"):
                self.assertNotIn(forbidden, body)


if __name__ == "__main__":
    unittest.main()
