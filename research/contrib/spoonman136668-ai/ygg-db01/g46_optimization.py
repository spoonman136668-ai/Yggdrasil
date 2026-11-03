"""G46: synthetic optimization symmetry and update-interference diagnostic.

No architectural changes, no primary task data, no tuning on held-out cohorts.
Frozen arms: exact G45 baseline, alternating-context order, lower learning
rate. Explicit synthetic supervised labels are used ONLY in this probe.
"""
from dataclasses import dataclass
import json

from native_dg1a import DG1APrototype, seeded_genome
from g38_native_learning import run_development, sensory
from g44_context import CUES, CONTEXTS, context_state, response
from g45_representation import (ROUNDS, UPDATES_PER_PAIR, MARGIN,
                                joint_accuracy, supervised_fit)

SCHEMA = "yggdrasil.g46.synthetic-optimization-diagnostic.v1"
ARMS = ("baseline", "alternating_context", "low_rate")
STARTS = ("seeded", "g38_pretrained")
MODES = ("visible", "masked")
INTERVALS = (0, 4, 8, 16)
PAIRS = tuple((ctx, cue) for ctx in CONTEXTS for cue in CUES)


def initial_genome(start):
    if type(start) is not str or start not in STARTS:
        raise ValueError("YGG_G46_START_INVALID")
    return seeded_genome(17) if start == "seeded" else run_development("mapped").genome


def target_for(ctx, cue):
    return MARGIN * ctx * (1 if cue > 0 else -1)


def supervised_mse(model, genome, visible):
    return sum((response(model, genome, cue, ctx, visible) - target_for(ctx, cue)) ** 2
               for ctx, cue in PAIRS) / len(PAIRS)


def schedule(arm, round_index):
    if arm == "alternating_context":
        # Mix contexts at each cue; every round still visits each pair once.
        pairs = ((-1, -1.0), (1, -1.0), (-1, 1.0), (1, 1.0))
    else:
        pairs = PAIRS
    return pairs if round_index % 2 == 0 else tuple(reversed(pairs))


@dataclass(frozen=True)
class Trace:
    arm: str
    start: str
    mode: str
    checkpoints: tuple
    genome: object
    updates: int


def fit(arm, start, mode):
    if type(arm) is not str or arm not in ARMS:
        raise ValueError("YGG_G46_ARM_INVALID")
    if type(mode) is not str or mode not in MODES:
        raise ValueError("YGG_G46_MODE_INVALID")
    model = DG1APrototype()
    genome = initial_genome(start)
    visible = mode == "visible"
    checkpoints = []
    rate = 0.1 if arm == "low_rate" else 0.5

    def record(round_index):
        checkpoints.append({
            "round": round_index,
            "accuracy": joint_accuracy(model, genome, visible),
            "interpolation": joint_accuracy(model, genome, visible, 0.5),
            "supervised_mse": round(supervised_mse(model, genome, visible), 15),
            "updates": round_index * len(PAIRS) * UPDATES_PER_PAIR
        })

    record(0)
    for r in range(ROUNDS):
        for ctx, cue in schedule(arm, r):
            state = context_state(model, ctx, visible)
            for _ in range(UPDATES_PER_PAIR):
                genome = model.fit_one_cell(
                    state, sensory(cue), genome, 1, 1,
                    target_for(ctx, cue), learning_rate=rate)
        if r + 1 in INTERVALS:
            record(r + 1)
    return Trace(arm, start, mode, tuple(checkpoints),
                 genome, ROUNDS * len(PAIRS) * UPDATES_PER_PAIR)


def cross_context_update_probe(start):
    """One-step signed response delta at target vs opposite context.

    Diagnostic only: a nonzero gradient is not proof of trainability.
    """
    model, genome = DG1APrototype(), initial_genome(start)
    rows = []
    for ctx, cue in PAIRS:
        before = response(model, genome, cue, ctx, True)
        opposing_before = response(model, genome, cue, -ctx, True)
        trained = model.fit_one_cell(
            context_state(model, ctx, True), sensory(cue), genome,
            1, 1, target_for(ctx, cue), learning_rate=0.5)
        after = response(model, trained, cue, ctx, True)
        opposing_after = response(model, trained, cue, -ctx, True)
        rows.append({
            "context": ctx, "cue": cue,
            "target_response_delta": round(after - before, 15),
            "opposing_context_response_delta": round(opposing_after - opposing_before, 15),
            "initial_error": round(before - target_for(ctx, cue), 15)
        })
    return rows


def build_report():
    rows = []
    for start in STARTS:
        for mode in MODES:
            for arm in ARMS:
                t = fit(arm, start, mode)
                rows.append({
                    "arm": arm, "start": start, "context_mode": mode,
                    "checkpoints": t.checkpoints,
                    "updates": t.updates,
                    "genome_parameters": t.genome.parameter_count
                })
    return {
        "schema": SCHEMA, "evidence": "SELF_AUTHORED_SYNTHETIC_DEV_ONLY",
        "frozen_arms": list(ARMS),
        "primary_execution_allowed": False,
        "scientific_acceptance": "NO_GO",
        "native_reward_learning": "UNVERIFIED",
        "genuine_transfer": "UNVERIFIED",
        "training_method": "EXPLICIT_SYNTHETIC_SUPERVISED_TARGETS",
        "gradient_probes": {start: cross_context_update_probe(start) for start in STARTS},
        "rows": rows,
    }


def report_json():
    return json.dumps(build_report(), sort_keys=True, separators=(",", ":"),
                      allow_nan=False)

if __name__ == "__main__":
    print("YGG_G46_DEV_OPTIMIZATION_JSON=" + report_json(), flush=True)
