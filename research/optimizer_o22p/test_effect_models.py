"""O22-P strictly public selected-event local learner and independent controls."""
import json
import subprocess
import sys
import unittest

from research.optimizer_o22p.effect_models import (
    NativePlasticCells, ConventionalBayesianEffects, _public
)


def event(b, action, moved, blocked_after):
    after = list(b)
    if moved: after[0] += 1
    if action == 0: after[2] = (b[2] - 1) % 4
    if action == 1: after[2] = (b[2] + 1) % 4
    after[5] = int(blocked_after)
    return after


class TestSourcePublicEffectLearning(unittest.TestCase):
    def setUp(self):
        self.before = [2, 3, 1, 6, 6, 0]

    def test_original_selected_legal_action_effect(self):
        self.assertEqual(_public(self.before, 0, event(self.before, 0, False, True)),
                         (1, 0))
        with self.assertRaises(ValueError):
            _public(self.before, 5, event(self.before, 0, False, True))
        with self.assertRaises(ValueError):
            _public(self.before + [123], 0, event(self.before, 0, False, True))
        with self.assertRaises(ValueError):
            _public(self.before, 0, event(self.before, 0, False, True) + [888])

    def test_all_action_families_update_selected_consequences(self):
        for cls in (NativePlasticCells, ConventionalBayesianEffects):
            model = cls()
            for a in (0, 1, 2):
                model.learn(self.before, a, event(self.before, a, a == 2, a == 1))
            self.assertEqual(model.actions, {"0": 1, "1": 1, "2": 1})
            self.assertEqual(model.events, 3)
            self.assertTrue(all(0 <= p <= 1 for a in (0, 1, 2)
                                for p in model.predict(self.before, a)))

    def test_native_selected_event_changes_predicted_public_effect(self):
        m = NativePlasticCells()
        before = m.predict(self.before, 1)[0]
        for i in range(5):
            m.learn(self.before, 1, event(self.before, 1, False, True))
        self.assertGreater(m.predict(self.before, 1)[0], before)
        prior = m.predict(self.before, 1)[0]
        for i in range(8):
            m.learn(self.before, 1, event(self.before, 1, False, False))
        self.assertLess(m.predict(self.before, 1)[0], prior)
        self.assertGreater(m.events, 0)

    def test_independent_conventional_revises_after_contradiction(self):
        m = ConventionalBayesianEffects()
        old = m.predict(self.before, 0)[0]
        for _ in range(7):
            m.learn(self.before, 0, event(self.before, 0, False, True))
        self.assertGreater(m.predict(self.before, 0)[0], old)
        prior = m.predict(self.before, 0)[0]
        for _ in range(11):
            m.learn(self.before, 0, event(self.before, 0, False, False))
        self.assertLess(m.predict(self.before, 0)[0], prior)

    def test_source_public_hypothetical_local_turn_ablation(self):
        m = NativePlasticCells()
        self.assertIsNone(m.proposal(self.before))
        for i in range(8):
            m.learn(self.before, 0, event(self.before, 0, False, True))
            m.learn(self.before, 1, event(self.before, 1, False, False))
        self.assertEqual(m.proposal(self.before), 1)
        # This is a source-FREE hypothetical turn preference only.
        self.assertIsNone(NativePlasticCells().proposal(self.before))

    def test_native_and_conventional_cold_exact_and_tamper_rejection(self):
        for cls in (NativePlasticCells, ConventionalBayesianEffects):
            m = cls()
            for a in (0, 1, 2):
                m.learn(self.before, a, event(self.before, a, a == 2, a == 1))
            wire = m.checkpoint()
            new = cls.restore(wire)
            self.assertEqual(new.checkpoint(), wire)
            for a in (0, 1, 2):
                self.assertEqual(new.predict(self.before, a),
                                 m.predict(self.before, a))
            script = (
              "import json,sys;"
              "from research.optimizer_o22p.effect_models import "
              "NativePlasticCells,ConventionalBayesianEffects;"
              "m=globals()[sys.argv[1]].restore(sys.stdin.buffer.read());"
              "b=[2,3,1,6,6,0];"
              "print(json.dumps({'prediction':m.predict(b,1),'actions':m.actions}))"
            )
            c = subprocess.run([sys.executable, "-B", "-c", script, cls.__name__],
                               input=wire, capture_output=True, timeout=20)
            self.assertEqual(c.returncode, 0, c.stderr.decode())
            out = json.loads(c.stdout)
            self.assertEqual(out["prediction"], list(m.predict(self.before, 1)))
            self.assertEqual(out["actions"], {"0": 1, "1": 1, "2": 1})
            bad = json.loads(wire)
            bad["body"]["events"] = 100
            with self.assertRaises(ValueError):
                cls.restore(json.dumps(bad).encode())

    def test_action_shuffling_not_assumed_to_be_causal_source_return(self):
        original = NativePlasticCells()
        shuffled = NativePlasticCells()
        for _ in range(10):
            original.learn(self.before, 0, event(self.before, 0, False, True))
            original.learn(self.before, 1, event(self.before, 1, False, False))
            shuffled.learn(self.before, 1, event(self.before, 0, False, True))
            shuffled.learn(self.before, 0, event(self.before, 1, False, False))
        self.assertNotEqual(original.proposal(self.before), shuffled.proposal(self.before))


if __name__ == "__main__":
    unittest.main(verbosity=2)
