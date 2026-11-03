"""G48: synthetic native-feedback learning and checkpoint controls.

G38's engineered periodicity decoder is retained; no native reward-learning
claim, held-out transfer, or scientific acceptance follows from this test.
"""
import json
import unittest

from native_dg1a import DG1APrototype, GENOME_PARAMETER_COUNT
from g38_native_learning import (CUES, NOVEL_CUES, ROUNDS, FRAMES,
                                 GRADIENT_CALLS, MARGIN, action, sensory,
                                 perceived_valence, run_development, value)
from matched_feedback import matched_feedback
from g40_adaptation import accuracy
from test_g39_retention_transfer import freeze_genome, restore_genome

ARMS = ("matched", "antithetic", "no_feedback", "frozen")
CHECKPOINTS = (0, 4, 8, 16)


def run(arm):
    if type(arm) is not str or arm not in ARMS:
        raise ValueError("YGG_G48_ARM")
    model = DG1APrototype()
    genome = run_development("mapped").genome
    initial = model.initial_state()
    checkpoints = []

    def record(rounds):
        blob = freeze_genome(genome)
        restored = restore_genome(blob)
        checkpoints.append({
            "rounds": rounds,
            "source": accuracy(model, restored, NOVEL_CUES, 1),
            "reversed": accuracy(model, restored, NOVEL_CUES, -1),
            "interpolation": accuracy(model, restored, (-0.25, 0.25), -1),
            "checkpoint_size": len(blob),
            "restored_equal": restored == genome
        })

    record(0)
    for rnd in range(ROUNDS):
        for cue in CUES:
            chosen = action(model, genome, cue)
            if rnd % 4 == 0:
                chosen = -chosen
            # The world owns the reversed answer. The learner only receives
            # chosen action, local cue and the returned waveform.
            correct = int(chosen == -(1 if cue > 0 else -1))
            if arm == "antithetic":
                correct = 1 - correct
            condition = "no_feedback" if arm == "no_feedback" else "mapped"
            waveform = matched_feedback(correct, condition,
                                        length=FRAMES, seed=100 + rnd)
            valence = perceived_valence(model, genome, waveform)
            target = chosen * valence * MARGIN if valence else value(
                model, genome, cue)
            for _ in range(GRADIENT_CALLS):
                candidate = model.fit_one_cell(
                    initial, sensory(cue), genome, 1, 1,
                    target, learning_rate=0.5)
                if arm != "frozen":
                    genome = candidate
        if rnd + 1 in CHECKPOINTS:
            record(rnd + 1)
    interactions = ROUNDS * len(CUES)
    return {
        "arm": arm, "checkpoints": checkpoints,
        "interactions": interactions,
        "feedback_frames": interactions * FRAMES,
        "gradient_calls": interactions * GRADIENT_CALLS,
        "genome_parameters": genome.parameter_count,
        "genome": genome
    }


def build_report():
    rows = []
    for arm in ARMS:
        row = run(arm)
        row.pop("genome")
        rows.append(row)
    return {
        "schema": "yggdrasil.g48.synthetic-native-feedback-retention.v1",
        "evidence": "SELF_AUTHORED_SYNTHETIC_DEV_ONLY",
        "fixed_engineered_feedback_decoder": True,
        "antithetic_control_is_not_random_shuffling": True,
        "scientific_acceptance": "NO_GO",
        "genuine_transfer": "UNVERIFIED",
        "primary_execution_allowed": False,
        "rows": rows
    }


class G48NativeFeedbackDiagnostics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results = {arm: run(arm) for arm in ARMS}

    def test_budgets_and_capacity(self):
        for arm, row in self.results.items():
            with self.subTest(arm=arm):
                self.assertEqual(row["interactions"], ROUNDS * len(CUES))
                self.assertEqual(row["feedback_frames"],
                                 ROUNDS * len(CUES) * FRAMES)
                self.assertEqual(row["gradient_calls"],
                                 ROUNDS * len(CUES) * GRADIENT_CALLS)
                self.assertEqual(row["genome_parameters"],
                                 GENOME_PARAMETER_COUNT)

    def test_checkpoint_roundtrip_and_frozen_control(self):
        source = run_development("mapped").genome
        self.assertEqual(self.results["frozen"]["genome"], source)
        self.assertEqual(self.results["no_feedback"]["genome"], source)
        for arm, row in self.results.items():
            with self.subTest(arm=arm):
                self.assertEqual(tuple(x["rounds"] for x in row["checkpoints"]),
                                 CHECKPOINTS)
                self.assertTrue(all(x["restored_equal"]
                                    for x in row["checkpoints"]))
                self.assertEqual(row["checkpoints"][0]["source"], 1.0)
                for x in row["checkpoints"]:
                    self.assertEqual(x["source"] + x["reversed"], 1.0)

    def test_report_does_not_assert_positive_learning(self):
        report = build_report()
        self.assertEqual(report["scientific_acceptance"], "NO_GO")
        self.assertEqual(report["genuine_transfer"], "UNVERIFIED")
        self.assertEqual([r["arm"] for r in report["rows"]], list(ARMS))
        self.assertEqual(json.loads(json.dumps(report)), report)

    def test_fail_closed(self):
        for invalid in (None, "", "protected", "heldout", 7):
            with self.assertRaises(ValueError):
                run(invalid)


if __name__ == "__main__":
    print("YGG_G48_DEV_FEEDBACK_JSON=" +
          json.dumps(build_report(), sort_keys=True,
                     separators=(",", ":"), allow_nan=False), flush=True)
    unittest.main()
