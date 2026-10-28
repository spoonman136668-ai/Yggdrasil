"""V15 synthetic MECHANICAL ONLY diagnostic: no original-world science."""
import itertools
import json
import unittest

from research.itd02_v14_three_phase_context_capacity import (
    PUBLIC_CUES, ordered_local_word, phase_bits,
)
from yggdrasil.itd02_local_ring_memory_dev import ACTIONS, ACTION_SITES
from yggdrasil.itd02_native_task_bridge_dev import REWARDS
from yggdrasil.itd02_v15_three_phase_readout_dev import (
    FrozenNativeThreePhaseReadoutDev, HEAD_ENTRIES, RATE,
)


def fake_public_reward(cue, first, second):
    """Predeclared synthetic mechanical fixture, NOT a world/source reward law."""
    return REWARDS[(
        PUBLIC_CUES.index(cue) + ACTIONS.index(first) + ACTIONS.index(second)) % 3]


def begin_two_step(learner, cue, first):
    learner.start_observation(cue)
    learner.accept_public_transition(
        first, "Nothing", 0, learning=False, terminal=False)
    learner.start_observation("Nothing")


class V15FrozenNativeLocalReadoutTests(unittest.TestCase):
    def test_36_contexts_fit_only_supplied_public_feedback(self):
        model = FrozenNativeThreePhaseReadoutDev()
        original = dict(model.original_ids)
        prior = [list(x) for x in model.heads]
        cases = list(itertools.product(PUBLIC_CUES, ACTIONS, ACTIONS))
        self.assertEqual(len(cases), 36)
        for _ in range(4):
            for cue, first, second in cases:
                begin_two_step(model, cue, first)
                before = [list(x) for x in model.heads]
                idx = ACTIONS.index(second)
                localword = ordered_local_word(
                    [phase_bits(cue, first, second, p) for p in range(3)],
                    ACTION_SITES[idx])
                model.accept_public_transition(
                    second, "Nothing", fake_public_reward(cue, first, second),
                    learning=True, terminal=True)
                self.assertEqual(
                    [model.heads[i] for i in range(3) if i != idx],
                    [before[i] for i in range(3) if i != idx])
                for word in range(HEAD_ENTRIES):
                    if word != localword:
                        self.assertEqual(model.heads[idx][word], before[idx][word])
                self.assertEqual(model.bridge.model_identities(), original)
                model.reset_episode()
        self.assertEqual(model.local_updates, 4 * 36)
        self.assertNotEqual(model.heads, prior)
        initial_error = 0.0
        final_error = 0.0
        for cue, first, second in cases:
            begin_two_step(model, cue, first)
            idx = ACTIONS.index(second)
            expected = fake_public_reward(cue, first, second)
            actual = model.local_scores()[idx]
            initial_error += abs(expected)
            final_error += abs(expected - actual)
            self.assertAlmostEqual(actual, (1 - (1 - RATE) ** 4) * expected)
            self.assertEqual(len(model.readout_scores()), 3)
            model.accept_public_transition(
                second, "Nothing", expected, learning=False, terminal=True)
            model.reset_episode()
        self.assertGreater(initial_error, 0.)
        self.assertAlmostEqual(final_error / initial_error, (1 - RATE) ** 4)
        self.assertEqual(model.bridge.model_identities(), original)
        before_freeze = model.checkpoint()
        restored = FrozenNativeThreePhaseReadoutDev.restore(before_freeze)
        self.assertEqual(restored.checkpoint(), before_freeze)
        model.start_frozen_evaluation()
        restored.start_frozen_evaluation()
        self.assertEqual(restored.parameters_sha256(), model.parameters_sha256())
        for cue, first, second in cases:
            begin_two_step(model, cue, first)
            begin_two_step(restored, cue, first)
            self.assertEqual(model.readout_scores(), restored.readout_scores())
            selected = fake_public_reward(cue, first, second)
            model.accept_public_transition(
                second, "Nothing", selected, learning=False, terminal=True)
            restored.accept_public_transition(
                second, "Nothing", selected, learning=False, terminal=True)
            self.assertEqual(model.parameters_sha256(), restored.parameters_sha256())
            self.assertEqual(model.bridge.model_identities(), original)
        self.assertEqual(model.checkpoint(), restored.checkpoint())
        receipt = {
            "schema": "ygg.itd02.v15.source_public_engineering.v1",
            "classification": "V15_PUBLIC_FEEDBACK_LOCAL_READOUT_FITS_TOY__NO_SCIENCE",
            "contexts": len(cases),
            "synthetic_training_updates": 4 * len(cases),
            "original_native_parameters_modified": False,
            "original_memory_parameters_modified": False,
            "local_heads": len(model.heads),
            "entries_per_head": HEAD_ENTRIES,
            "local_learned_scalars": len(model.heads) * HEAD_ENTRIES,
            "toy_initial_absolute_error": initial_error,
            "toy_final_absolute_error": final_error,
            "toy_relative_absolute_error": final_error / initial_error,
            "native_cold_checkpoint_equal": True,
            "scientific_first_use": False,
            "original_world_training": False,
            "source_public_only": True,
            "input_fanout_native_admissibility": "NOT_PROVEN",
        }
        print("V15_ENGINEERING_DIAGNOSTIC=" + json.dumps(
            receipt, sort_keys=True, separators=(",", ":")))

    def test_negative_controls_freeze_transaction_and_corruption(self):
        m = FrozenNativeThreePhaseReadoutDev()
        with self.assertRaises(ValueError):
            m.start_observation("Nothing")
        with self.assertRaises(ValueError):
            m.accept_public_transition("GoForward", "Nothing", 0, terminal=False)
        m.start_observation("LRV")
        with self.assertRaises(ValueError):
            m.accept_public_transition("GoForward", "Nothing", 0, terminal=True)
        with self.assertRaises(ValueError):
            m.accept_public_transition("GoForward", "Nothing", 999, terminal=False)
        self.assertIsNone(m.first_context)
        m.accept_public_transition("Backup", "Nothing", 0, terminal=False)
        self.assertEqual(m.first_context, ("LRV", "Backup"))
        with self.assertRaises(ValueError):
            m.reset_episode()
        with self.assertRaises(ValueError):
            m.start_observation("MRV")
        m.start_observation("Nothing")
        before = m.checkpoint()
        with self.assertRaises(ValueError):
            m.accept_public_transition("GoForward", "Nothing", -2, terminal=True)
        self.assertEqual(before, m.checkpoint())
        self.assertEqual(m._candidate("GoForward")[2], ordered_local_word(
            [phase_bits("LRV", "Backup", "GoForward", p) for p in range(3)],
            ACTION_SITES[1]))
        with self.assertRaises(TypeError):
            m.accept_public_transition("GoForward", "Nothing", 0,
                                       terminal=True, private_world=8)
        self.assertEqual(before, m.checkpoint())
        m.accept_public_transition("GoForward", "Nothing", 10, terminal=True)
        m.start_frozen_evaluation()
        frozen = m.parameters_sha256()
        m.start_observation("MRV")
        with self.assertRaises(ValueError):
            m.accept_public_transition("TurnAround", "Nothing", 0,
                                       learning=True, terminal=False)
        m.accept_public_transition("TurnAround", "Nothing", 0,
                                   learning=False, terminal=False)
        m.start_observation("Nothing")
        with self.assertRaises(ValueError):
            m.accept_public_transition("GoForward", "Nothing", 10,
                                       learning=True, terminal=True)
        m.accept_public_transition("GoForward", "Nothing", 10,
                                   learning=False, terminal=True)
        self.assertEqual(frozen, m.parameters_sha256())
        raw = m.checkpoint()
        damaged = bytearray(raw)
        damaged[len(damaged) // 2] ^= 1
        with self.assertRaises(ValueError):
            FrozenNativeThreePhaseReadoutDev.restore(bytes(damaged))
        wrong = json.loads(raw)
        wrong["body"]["heads"][0][0] = 11.0
        with self.assertRaises(ValueError):
            FrozenNativeThreePhaseReadoutDev.restore(json.dumps(wrong).encode())
        restored = FrozenNativeThreePhaseReadoutDev.restore(raw)
        restored.heads[0][0] = 1.
        with self.assertRaises(ValueError):
            restored.readout_scores()


if __name__ == "__main__":
    unittest.main()
