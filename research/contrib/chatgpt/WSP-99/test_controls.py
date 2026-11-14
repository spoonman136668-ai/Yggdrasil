"""WSP99 source-blind control implementation tests; fixture IDs only."""
from __future__ import annotations
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from task import FixtureWorld, bits
from controls import (
    GradientTanhRNN, GradientMemoryless, SymbolicFiniteState,
    validate_episodes, SEEDS, ORIGINAL_EPOCHS,
)


def fixture_episodes(fixture_id=0, count=12):
    world = FixtureWorld(fixture_id)
    episodes = []
    for i in range(count):
        x = world.reset(bits((7*i + 3) % 64))
        episode = []
        for t in range(4):
            action = (i + t) % 4
            y = world.step(action)["observation"]
            episode.append((x, action, y))
            x = y
        episodes.append(tuple(episode))
    return tuple(episodes)


class ControlFixtureTests(unittest.TestCase):
    def test_symbolic_source_consistency_and_delay(self):
        for fixture_id in (0, 1, 2):
            model = SymbolicFiniteState(fixture_episodes(fixture_id))
            self.assertEqual(model.source_accuracy, 1.0)
            self.assertEqual(len(model.candidate_counts), 2)
            self.assertTrue(all(0 < n <= 120 for n in model.candidate_counts))
            prediction = model.rollout(bits(5), (0, 1, 2))
            self.assertEqual(len(prediction), 3)
            self.assertEqual(prediction, model.rollout(bits(5), (0, 1, 2)))

    def test_strong_baselines_train_and_are_deterministic(self):
        rows = fixture_episodes(count=5)
        a, b = GradientTanhRNN(11), GradientTanhRNN(11)
        self.assertEqual(a.train(rows, epochs=12, development=True),
                         b.train(rows, epochs=12, development=True))
        self.assertEqual(a.rollout(bits(1), (0, 2)),
                         b.rollout(bits(1), (0, 2)))
        self.assertTrue(0 <= a.source_fit(rows) <= 1)
        self.assertTrue(a.training_loss >= 0)
        memoryless = GradientMemoryless(11)
        self.assertTrue(memoryless.train(rows, epochs=12, development=True) >= 0)
        self.assertEqual(len(memoryless.probability(bits(3), 1)), 6)

    def test_source_training_loss_decreases_on_fixture(self):
        rows = fixture_episodes(count=5)
        model = GradientTanhRNN(17)
        xs_loss = model.train(rows, epochs=24, development=True)
        self.assertLess(xs_loss, .6932)
        nohistory = GradientMemoryless(17)
        self.assertLess(nohistory.train(rows, epochs=24, development=True), .6932)

    def test_original_epochs_are_immutable(self):
        rows = fixture_episodes(count=2)
        for model in (GradientTanhRNN(11), GradientMemoryless(11)):
            for epochs in (0, 17, 1799, 1801):
                with self.assertRaises(ValueError):
                    model.train(rows, epochs=epochs)
            with self.assertRaises(ValueError):
                model.train(rows, epochs=25, development=True)
        with self.assertRaises(ValueError):
            GradientTanhRNN(99)
        self.assertEqual(SEEDS, (11, 17, 23))
        self.assertEqual(ORIGINAL_EPOCHS, 1800)

    def test_history_and_action_provenance_validated(self):
        rows = list(fixture_episodes(count=2))
        self.assertEqual(len(validate_episodes(rows)), 2)
        bad = list(rows[0])
        first = list(bad[1])
        first[0] = bits(63)
        bad[1] = tuple(first)
        with self.assertRaises(ValueError):
            validate_episodes((tuple(bad),))
        with self.assertRaises(ValueError):
            validate_episodes((((bits(0), True, bits(0)),)*4,))


if __name__ == "__main__":
    unittest.main()
