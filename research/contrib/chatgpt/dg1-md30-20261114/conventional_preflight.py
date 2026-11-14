"""Execute MD30 conventional controls on frozen toy-only data in one process.

All comparison numbers are diagnostics, not original scientific first-use.
The identical physical training receipt is shared between controls.
"""
import json
from pathlib import Path

from bayesian_control import paid_training_episodes
from recurrent_control import recurrent_toy_control
from model_rl_control import empirical_rl_toy_control
from structural_rewire import canonical, digest


def control_comparison():
    lock = json.loads((Path(__file__).resolve().parent /
                       "conventional_controls_lock.json").read_text("utf-8"))
    assert lock["status"] == "FROZEN_BEFORE_NEW_CONVENTIONAL_CONTROL_SOURCE_OR_TRANSFER_OUTCOMES"
    sessions, physical = paid_training_episodes()
    assert physical["charged_steps"] == 1920 and len(sessions) == 240
    rnn = recurrent_toy_control(sessions)
    rl = empirical_rl_toy_control(sessions)
    assert rnn["train"]["fit_episodes"] == rl["train"]["fit_episodes"] == 192
    assert rnn["toy_episodes"] == rl["toy_episodes"] == 60
    assert rnn["train"]["validation_episodes"] == rl["train"]["validation_episodes"] == 48
    assert all(2 * 60 <= r["toy_charged_steps"] <= 8 * 60 for r in (rnn, rl))
    return {
        "schema": "md30.synthetic-conventional-controls-development.v1",
        "status": "TOY_ENGINEERING_DIAGNOSTIC_NO_SCIENTIFIC_PASS",
        "official_md30_science_first_use": False,
        "training_seed_range": [3301, 3540],
        "synthetic_transfer_seed_range": [5301, 5360],
        "physical_training": physical,
        "model_controls": {
            "recurrent_world_model": rnn,
            "empirical_model_based_rl": rl,
        },
        "limitations": "No best-of-run selection, candidate training, official DEV/cold/registered scores or matched-compute science; Bayesian stronger prior evaluated separately.",
    }


def portable_receipt(report):
    """Remove only hardware-dependent CPU seconds for exact trace comparison."""
    def clean(value):
        if isinstance(value, dict):
            return {key: clean(v) for key, v in value.items()
                    if key not in ("training_cpu_seconds", "inference_cpu_seconds")}
        if isinstance(value, list):
            return [clean(x) for x in value]
        return value
    return clean(report)


if __name__ == "__main__":
    print(canonical(control_comparison()))
