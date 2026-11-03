"""G45 development-only: separate representability from gradient learnability.

Explicit bounded XOR-like witness is NOT learned and is NOT scientific
evidence. The second, separately reported arm uses synthetic supervised
answers solely to diagnose the G33 training interface; G44 reward-driven
learning is unchanged and remains unproven. No protected labels are read.
"""
from dataclasses import dataclass
import json
from native_dg1a import (DG1APrototype, SharedGenome, seeded_genome,
                          INPUTS, HIDDEN, OUTPUTS, GENOME_PARAMETER_COUNT)
from g38_native_learning import run_development, sensory
from g44_context import context_state, chosen_action, CONTEXTS, CUES

SCHEMA = "yggdrasil.g45.synthetic-representation.v1"
ROUNDS = 16
UPDATES_PER_PAIR = 8
MARGIN = 0.09
CUE_MAGNITUDES = (1.0, 0.5)


def witness_genome():
    """Hand-constructed four-unit context/cue conjunctions; not a learner."""
    first = [0.0] * (INPUTS * HIDDEN)
    b1 = [0.0] * HIDDEN
    second = [0.0] * (HIDDEN * OUTPUTS)
    b2 = [0.0] * OUTPUTS
    # Own context at feature 0; sensory at feature INPUTS-1.
    for j, (ctx, cue) in enumerate(((1, 1), (-1, -1), (1, -1), (-1, 1))):
        first[j * INPUTS] = 2.0 * ctx
        first[j * INPUTS + INPUTS - 1] = 2.0 * cue
        b1[j] = -2.0
        second[j] = 1.0 if j < 2 else -1.0
    return SharedGenome(tuple(first), tuple(b1), tuple(second), tuple(b2))


def joint_accuracy(model, genome, visible, magnitude=1.0):
    if type(visible) is not bool or magnitude not in CUE_MAGNITUDES:
        raise ValueError("YGG_G45_EVAL_ARGUMENT")
    return sum(chosen_action(model, genome, cue * magnitude, ctx, visible) ==
               ctx * (1 if cue > 0 else -1)
               for ctx in CONTEXTS for cue in CUES) / (len(CONTEXTS) * len(CUES))


@dataclass(frozen=True)
class Result:
    start: str
    context_mode: str
    before: float
    after: float
    interpolation: float
    updates: int
    genome: object


def supervised_fit(start, context_mode):
    if type(start) is not str or start not in ("seeded", "g38_pretrained"):
        raise ValueError("YGG_G45_START")
    if type(context_mode) is not str or context_mode not in ("visible", "masked"):
        raise ValueError("YGG_G45_CONTEXT_MODE")
    model = DG1APrototype()
    genome = seeded_genome(17) if start == "seeded" else run_development("mapped").genome
    visible = context_mode == "visible"
    before = joint_accuracy(model, genome, visible)
    pairs = [(ctx, cue) for ctx in CONTEXTS for cue in CUES]
    for r in range(ROUNDS):
        # Equal deterministic balance; alternate pair order to limit order bias.
        schedule = pairs if r % 2 == 0 else list(reversed(pairs))
        for ctx, cue in schedule:
            state = context_state(model, ctx, visible)
            # Synthetic answer is supplied ONLY here, in the explicit
            # supervised representation probe, never in G44 or step().
            target = MARGIN * ctx * (1 if cue > 0 else -1)
            for _ in range(UPDATES_PER_PAIR):
                genome = model.fit_one_cell(state, sensory(cue), genome,
                                            1, 1, target, learning_rate=0.5)
    return Result(start, context_mode, before,
                  joint_accuracy(model, genome, visible),
                  joint_accuracy(model, genome, visible, 0.5),
                  ROUNDS * len(pairs) * UPDATES_PER_PAIR, genome)


def build_report():
    model = DG1APrototype()
    witness = witness_genome()
    rows = []
    for start in ("seeded", "g38_pretrained"):
        for mode in ("visible", "masked"):
            r = supervised_fit(start, mode)
            rows.append({"start": start, "context_mode": mode,
                         "before": r.before, "after": r.after,
                         "interpolation": r.interpolation, "updates": r.updates,
                         "genome_parameters": r.genome.parameter_count})
    return {
        "schema": SCHEMA,
        "evidence": "SELF_AUTHORED_SYNTHETIC_DEV_ONLY",
        "witness_is_hardcoded_not_learned": True,
        "witness_visible_accuracy": joint_accuracy(model, witness, True),
        "witness_masked_accuracy": joint_accuracy(model, witness, False),
        "witness_visible_interpolation": joint_accuracy(model, witness, True, 0.5),
        "training_method": "EXPLICIT_SYNTHETIC_SUPERVISED_TARGETS",
        "reward_driven_learning": "UNVERIFIED",
        "genuine_transfer": "UNVERIFIED",
        "scientific_acceptance": "NO_GO",
        "primary_execution_allowed": False,
        "rows": rows
    }


def report_json():
    return json.dumps(build_report(), sort_keys=True, separators=(",", ":"),
                      allow_nan=False)

if __name__ == "__main__":
    print("YGG_G45_DEV_REPRESENTATION_JSON=" + report_json(), flush=True)
