"""G44: fixed-capacity context discrimination fixture, development-only.

A public task-context signal is placed in immutable local channel 0;
the binary cue enters local sensory separately. No correct action is
encoded in the context alone. The world's target stays private and
only matched temporal feedback is delivered to supervised toy plasticity.
The periodicity decoder remains externally engineered; NOT native reward.
"""
from dataclasses import dataclass
import json

from native_dg1a import DG1APrototype, GENOME_PARAMETER_COUNT
from g38_native_learning import (run_development, sensory, perceived_valence,
                                 MARGIN, FRAMES, GRADIENT_CALLS)
from matched_feedback import matched_feedback

CONDITIONS = ("mapped", "sham", "no_feedback")
CONTEXT_MODES = ("visible", "masked")
CUES = (-1.0, 1.0)
CONTEXTS = (-1, 1)
ROUNDS = 16
CENTER = (1, 1)
SCHEMA = "yggdrasil.g44.synthetic-context-discrimination.v1"


def context_state(model, context, visible):
    if type(context) is not int or context not in CONTEXTS:
        raise ValueError("YGG_G44_CONTEXT_INVALID")
    if type(visible) is not bool:
        raise ValueError("YGG_G44_VISIBLE_INVALID")
    state = [list(row) for row in model.initial_state()]
    y, x = CENTER
    old = state[y][x]
    state[y][x] = ((float(context) if visible else 0.0),) + old[1:]
    return tuple(tuple(row) for row in state)


def response(model, genome, cue, context, visible):
    return model.step(context_state(model, context, visible),
                      sensory(cue), genome)[CENTER[0]][CENTER[1]][2]


def chosen_action(model, genome, cue, context, visible):
    return 1 if response(model, genome, cue, context, visible) >= 0 else -1


def accuracy(model, genome, context, visible):
    return sum(chosen_action(model, genome, cue, context, visible) ==
               context * (1 if cue > 0 else -1) for cue in CUES) / len(CUES)


@dataclass(frozen=True)
class Result:
    condition: str
    context_mode: str
    positive_before: float
    negative_before: float
    positive_after: float
    negative_after: float
    interactions: int
    feedback_frames: int
    gradient_calls: int
    genome: object
    evidence: str = "SYNTHETIC_DEV_ONLY_NO_TRANSFER_CLAIM"


def run(condition, context_mode):
    if type(condition) is not str or condition not in CONDITIONS:
        raise ValueError("YGG_G44_CONDITION_INVALID")
    if type(context_mode) is not str or context_mode not in CONTEXT_MODES:
        raise ValueError("YGG_G44_MODE_INVALID")
    visible = context_mode == "visible"
    model = DG1APrototype()
    genome = run_development("mapped").genome
    before = tuple(accuracy(model, genome, ctx, visible) for ctx in CONTEXTS)
    for i in range(ROUNDS):
        # Paired signs and contexts: no outcome/correct-action bit enters learner.
        for ctx in CONTEXTS:
            state = context_state(model, ctx, visible)
            for cue in CUES:
                chosen = chosen_action(model, genome, cue, ctx, visible)
                if i % 4 == 0:
                    chosen = -chosen
                # Only world adapter knows the target, which depends on BOTH
                # cue sign and context, not context by itself.
                correct = ctx * (1 if cue > 0 else -1)
                wave = matched_feedback(int(chosen == correct), condition,
                                        length=FRAMES, seed=100 + i)
                decoded = perceived_valence(model, genome, wave)
                current = response(model, genome, cue, ctx, visible)
                target = (chosen * decoded * MARGIN if decoded else current)
                for _ in range(GRADIENT_CALLS):
                    genome = model.fit_one_cell(state, sensory(cue), genome,
                                                CENTER[0], CENTER[1],
                                                target, learning_rate=0.5)
    after = tuple(accuracy(model, genome, ctx, visible) for ctx in CONTEXTS)
    n = ROUNDS * len(CUES) * len(CONTEXTS)
    return Result(condition, context_mode, before[1], before[0],
                  after[1], after[0], n, n * FRAMES, n * GRADIENT_CALLS,
                  genome)


def build_report():
    rows = []
    for condition in CONDITIONS:
        for mode in CONTEXT_MODES:
            result = run(condition, mode)
            rows.append({
                "condition": condition, "context_mode": mode,
                "positive_before": result.positive_before,
                "negative_before": result.negative_before,
                "positive_after": result.positive_after,
                "negative_after": result.negative_after,
                "joint_accuracy_after": (result.positive_after + result.negative_after) / 2,
                "interactions": result.interactions,
                "feedback_frames": result.feedback_frames,
                "gradient_calls": result.gradient_calls,
                "genome_parameters": result.genome.parameter_count
            })
    return {
        "schema": SCHEMA, "evidence": "SELF_AUTHORED_SYNTHETIC_DEV_ONLY",
        "primary_execution_allowed": False,
        "scientific_acceptance": "NO_GO",
        "genuine_transfer": "UNVERIFIED",
        "decoder": "FIXED_ENGINEERED_PERIODICITY",
        "context_input": "IMMUTABLE_LOCAL_CHANNEL_ZERO",
        "no_hidden_answer_input": True,
        "source_pretraining_cost_unmatched_to_new_SEEDED_CONTROL": True,
        "rows": rows
    }


def report_json():
    return json.dumps(build_report(), sort_keys=True,
                      separators=(",", ":"), allow_nan=False)


if __name__ == "__main__":
    print("YGG_G44_DEV_CONTEXT_JSON=" + report_json(), flush=True)
