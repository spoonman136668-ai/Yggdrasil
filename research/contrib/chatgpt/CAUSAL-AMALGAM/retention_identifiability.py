"""Expected-loss bound for a shared static transition readout under the frozen laws."""

from fractions import Fraction as F
from itertools import product
import json
from math import sqrt
from pathlib import Path
import sys

from selection_trial import restore

HERE = Path(__file__).resolve().parent
POSITIONS = tuple(product((0, 1), repeat=3))


def deterministic_outcome(context, action, phase):
    executed = action ^ phase["swap"]
    orientation = phase["regime"]
    if phase["family"] == "context_switch":
        orientation ^= context
    modulation = context & executed if phase["mask_by_context"] else 0
    return executed ^ orientation ^ modulation


def target(context, action, phase):
    """Marginalize the generator's hidden bit under the observed context."""
    one = (F(1, 4), F(3, 4))[context]
    flip = (1 - one) * F(1, 8) + one * F(1, 4)
    return 1 - flip if deterministic_outcome(context, action, phase) else flip


def mean(values):
    return sum(values) / len(values)


def bound(p_old, p_new, initial_readout, old_allowance):
    noise_old, noise_new = (mean([p * (1 - p) for p in projections])
                            for projections in (p_old, p_new))
    old_loss = noise_old + mean([(p - q)**2 for p, q in zip(p_old, initial_readout, strict=True)])
    separation = mean([(p - q)**2 for p, q in zip(p_old, p_new, strict=True)])
    # The feasible predictors occupy an L2 ball around the old Bayes predictor.
    # The nearest point to the new Bayes predictor lies on the connecting line.
    displacement = max(0.0, sqrt(separation) - sqrt(old_loss + old_allowance - noise_old))
    return {"conditional_mean_separation_squared": float(separation),
            "old_anchor_expected_brier": float(old_loss),
            "old_expected_brier_cap": float(old_loss + old_allowance),
            "old_oracle_expected_brier": float(noise_old),
            "new_oracle_expected_brier": float(noise_new),
            "static_new_expected_brier_minimum": float(noise_new + displacement**2),
            "independent_context_headroom": displacement**2}


def run(directory, plan_path):
    manifest = json.loads(plan_path.read_bytes())
    checkpoint = json.loads((HERE / manifest["checkpoint_contract"]).read_bytes())
    state = restore(directory, checkpoint)
    familiar, changed = manifest["familiar"], manifest["phases"][0]
    old, new = [], []
    keys = []
    for context, nuisance, action in POSITIONS:
        old.append(target(context, action, familiar))
        new.append(target(context, action, changed))
        keys.append(state.native.experience_context_forecast((context, nuisance), action))
    report = bound(old, new, keys, F(manifest["max_brier_drift"]))
    if bound(old, old, keys, F(0))["independent_context_headroom"] != 0:
        raise RuntimeError("Equal-law negative control failed")
    return dict(report, scope="Expected transition Brier under the frozen synthetic source",
                includes_outcomes_generated=0,
                common_inputs=["current public context bit", "nuisance bit", "public action"],
                old_transition_probability=[str(p) for p in old],
                new_transition_probability=[str(p) for p in new],
                shared_static_readout_only=True, equal_law_negative_control=True)


if __name__ == "__main__":
    directory, manifest = map(Path, sys.argv[1:])
    print(json.dumps(run(directory, manifest), indent=2, sort_keys=True))
