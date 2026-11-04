"""G42 synthetic reversal-interference trajectory and parameter-drift audit.

Only locally authored G38/G40 toy tasks. No primary cohorts, no external
evaluation, no scientific acceptance. Feedback interpretation remains the
fixed engineered periodicity detector from G38, not a learned native reward.
"""
from dataclasses import dataclass
import json
import math

from native_dg1a import DG1APrototype, seeded_genome
from matched_feedback import matched_feedback
from g38_native_learning import (CUES, NOVEL_CUES, ROUNDS, FRAMES,
                                 GRADIENT_CALLS, MARGIN, action, sensory,
                                 perceived_valence, value, run_development)
from g40_adaptation import CONDITIONS, accuracy

CHECKPOINTS = (0, 1, 2, 4, 8, 12, 16)
SCHEMA = "yggdrasil.g42.synthetic-interference-trace.v1"


def genome_delta(start, current):
    """Euclidean parameter distance from pre-adaptation checkpoint, not memory."""
    parts = ("first", "first_bias", "second", "second_bias")
    return math.sqrt(sum((a - b) ** 2 for part in parts
                         for a, b in zip(getattr(start, part), getattr(current, part))))


@dataclass(frozen=True)
class Trace:
    condition: str
    pretrained: bool
    checkpoints: tuple
    final_genome: object
    interactions: int
    feedback_frames: int
    gradient_calls: int
    evidence_class: str = "SYNTHETIC_DEV_DIAGNOSTIC_NOT_TRANSFER"


def trace(condition, pretrained=True):
    if type(condition) is not str or condition not in CONDITIONS:
        raise ValueError("YGG_G42_INVALID_CONDITION")
    if type(pretrained) is not bool:
        raise ValueError("YGG_G42_INVALID_PRETRAINED")
    model = DG1APrototype()
    genome = run_development("mapped").genome if pretrained else seeded_genome(17)
    starting = genome
    initial = model.initial_state()
    entries = []

    def record(rounds):
        source = accuracy(model, genome, NOVEL_CUES, 1)
        target = accuracy(model, genome, NOVEL_CUES, -1)
        entries.append({
            "rounds": rounds,
            "source_accuracy": source,
            "target_accuracy": target,
            "weight_distance": round(genome_delta(starting, genome), 12),
            "interactions": rounds * len(CUES),
            "feedback_frames": rounds * len(CUES) * FRAMES,
            "gradient_calls": rounds * len(CUES) * GRADIENT_CALLS
        })

    record(0)
    for i in range(ROUNDS):
        for cue in CUES:
            chosen = action(model, genome, cue)
            if i % 4 == 0:
                chosen = -chosen
            # Reversed target rule is private to synthetic environment.
            correct = -(1 if cue > 0 else -1)
            waveform = matched_feedback(
                int(chosen == correct),
                "no_feedback" if condition == "decoder_ablation" else condition,
                length=FRAMES, seed=100 + i)
            decoded = (0 if condition == "decoder_ablation"
                       else perceived_valence(model, genome, waveform))
            target = (chosen * decoded * MARGIN if decoded
                      else value(model, genome, cue))
            for _ in range(GRADIENT_CALLS):
                genome = model.fit_one_cell(initial, sensory(cue), genome,
                                            1, 1, target, learning_rate=0.5)
        if i + 1 in CHECKPOINTS:
            record(i + 1)
    count = ROUNDS * len(CUES)
    return Trace(condition, pretrained, tuple(entries), genome,
                 count, count * FRAMES, count * GRADIENT_CALLS)


def build_report():
    rows = []
    for pretrained in (False, True):
        for condition in CONDITIONS:
            t = trace(condition, pretrained)
            rows.append({
                "condition": condition, "pretrained": pretrained,
                "checkpoints": t.checkpoints, "interactions": t.interactions,
                "feedback_frames": t.feedback_frames,
                "gradient_calls": t.gradient_calls
            })
    return {
        "schema": SCHEMA,
        "evidence": "SELF_AUTHORED_SYNTHETIC_DEV_ONLY",
        "primary_execution_allowed": False,
        "scientific_acceptance": "NO_GO",
        "genuine_transfer": "UNVERIFIED",
        "reward_decoder": "FIXED_ENGINEERED_PERIODICITY_DETECTOR",
        "comparison_caveat": "warm-start includes unmatched earlier G38 source training",
        "rows": rows
    }


def report_json():
    return json.dumps(build_report(), sort_keys=True, separators=(",", ":"),
                      allow_nan=False)


if __name__ == "__main__":
    print("YGG_G42_DEV_TRACE_JSON=" + report_json(), flush=True)
