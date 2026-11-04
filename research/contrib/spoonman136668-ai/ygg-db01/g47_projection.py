"""G47 fixed-budget synthetic opposing-context gradient projection.

One shared G33 genome, unchanged parameter count and supervised targets.
The context-conditioned projection is an externally engineered update
mechanism, NOT learned memory, native reward or genuine task transfer.
"""
from dataclasses import dataclass
import json
import math

from native_dg1a import DG1APrototype, SharedGenome
from g38_native_learning import sensory
from g44_context import context_state
from g45_representation import joint_accuracy
from g46_optimization import (PAIRS, STARTS, MODES, UPDATES_PER_PAIR,
                              initial_genome, target_for, supervised_mse,
                              schedule)

SCHEMA = "yggdrasil.g47.synthetic-context-gradient-projection.v1"
ARMS = ("baseline", "opposing_projection")
ROUNDS = 4
PARTS = ("first", "first_bias", "second", "second_bias")
RATE = 0.5

def flatten(genome):
    return tuple(value for name in PARTS for value in getattr(genome, name))

def from_flat(values, template):
    pos, parts = 0, []
    for name in PARTS:
        count = len(getattr(template, name))
        parts.append(tuple(values[pos:pos + count]))
        pos += count
    return SharedGenome(*parts)

def gradient_step(model, genome, ctx, cue, visible):
    return model.fit_one_cell(context_state(model, ctx, visible),
                              sensory(cue), genome, 1, 1,
                              target_for(ctx, cue), learning_rate=RATE)

def projected_step(model, genome, ctx, cue, visible, arm):
    """Evaluate both contexts at the SAME frozen starting genome.

    If updates conflict, remove the opposing-gradient component of the
    current update. No label is inferred: both targets are explicitly
    supplied synthetic supervised labels. Masked context is a negative control.
    """
    if arm not in ARMS:
        raise ValueError("YGG_G47_ARM")
    first = gradient_step(model, genome, ctx, cue, visible)
    other = gradient_step(model, genome, -ctx, cue, visible)
    start, changed, alternate = map(flatten, (genome, first, other))
    g = tuple(b - a for a, b in zip(start, changed))
    h = tuple(b - a for a, b in zip(start, alternate))
    dot = sum(a * b for a, b in zip(g, h))
    norm = sum(b * b for b in h)
    active = arm == "opposing_projection" and dot < 0.0 and norm > 0.0
    coeff = dot / norm if active else 0.0
    corrected = tuple(a + (u - coeff * v) for a, u, v in zip(start, g, h))
    # Projection is non-expansive in euclidean norm in exact arithmetic;
    # explicit error checks still reject malformed/overflowing parameters.
    return (from_flat(corrected, genome) if active else first), active, dot

@dataclass(frozen=True)
class Trace:
    start: str
    mode: str
    arm: str
    initial_accuracy: float
    final_accuracy: float
    interpolation: float
    initial_mse: float
    final_mse: float
    projection_count: int
    negative_dot_count: int
    updates: int
    gradient_evaluations: int
    genome: object

def run(arm, start, mode):
    if type(arm) is not str or arm not in ARMS:
        raise ValueError("YGG_G47_ARM")
    if type(start) is not str or start not in STARTS:
        raise ValueError("YGG_G47_START")
    if type(mode) is not str or mode not in MODES:
        raise ValueError("YGG_G47_MODE")
    model = DG1APrototype()
    genome = initial_genome(start)
    visible = mode == "visible"
    start_score = joint_accuracy(model, genome, visible)
    start_mse = supervised_mse(model, genome, visible)
    projected = negative = 0
    for rnd in range(ROUNDS):
        for ctx, cue in schedule("baseline", rnd):
            for _ in range(UPDATES_PER_PAIR):
                genome, active, dot = projected_step(model, genome, ctx, cue, visible, arm)
                projected += int(active)
                negative += int(dot < 0.0)
    updates = ROUNDS * len(PAIRS) * UPDATES_PER_PAIR
    return Trace(start, mode, arm, start_score,
                 joint_accuracy(model, genome, visible),
                 joint_accuracy(model, genome, visible, 0.5),
                 round(start_mse, 15),
                 round(supervised_mse(model, genome, visible), 15),
                 projected, negative, updates, 2 * updates, genome)

def build_report():
    rows = []
    for start in STARTS:
        for mode in MODES:
            for arm in ARMS:
                r = run(arm, start, mode)
                rows.append({
                    "start": start, "context_mode": mode, "arm": arm,
                    "before_accuracy": r.initial_accuracy,
                    "after_accuracy": r.final_accuracy,
                    "interpolation": r.interpolation,
                    "before_mse": r.initial_mse, "after_mse": r.final_mse,
                    "projection_count": r.projection_count,
                    "negative_dot_count": r.negative_dot_count,
                    "updates": r.updates,
                    "gradient_evaluations": r.gradient_evaluations,
                    "genome_parameters": r.genome.parameter_count
                })
    return {
        "schema": SCHEMA,
        "evidence": "SELF_AUTHORED_SYNTHETIC_DEV_ONLY",
        "training_method": "EXPLICIT_SYNTHETIC_SUPERVISION",
        "frozen_arms": list(ARMS),
        "primary_execution_allowed": False,
        "scientific_acceptance": "NO_GO",
        "genuine_transfer": "UNVERIFIED",
        "native_reward_learning": "UNVERIFIED",
        "shared_parameter_capacity": 398,
        "counterfactual_gradient_labels_are_explicit_synthetic_targets": True,
        "rows": rows
    }

def report_json():
    return json.dumps(build_report(), sort_keys=True,
                      separators=(",", ":"), allow_nan=False)

if __name__ == "__main__":
    print("YGG_G47_DEV_PROJECTION_JSON=" + report_json(), flush=True)
