"""AAI-10D synthetic fixtures ONLY; no primary or science cohort execution."""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import protocol as p
import models as old


def run_fixture(key, context_count=1):
    p.ensure_fixture(key)
    models, observed = p.common_training(key)
    if len(observed) != 64 or set(models) != set(p.LEARNERS):
        raise AssertionError("unequal common training")
    baseline_sha = hashlib.sha256(old.canonical(models).encode()).hexdigest()
    result = []
    for law in ("A", "B", "C", "D"):
        for n in p.PRIMARY_BUDGETS:
            for name in p.LEARNERS:
                outcome = p.evaluate_branch(
                    name, models[name], law, key, n, n_contexts=context_count
                )
                result.append({
                    "phase": law, "challenge_trials": n, "learner": name,
                    "mean_reward": outcome["mean_reward"],
                    "goal_correct": outcome["goal_correct"],
                    "mean_interventions": outcome["mean_interventions"],
                    "actions_sha256": outcome["actions_sha256"],
                })
    # Artifacts do not contain unchosen action rewards or law IDs in model
    # checkpoints. Phase labels in DIAGNOSTIC report are external to actors.
    after_sha = hashlib.sha256(old.canonical(models).encode()).hexdigest()
    if baseline_sha != after_sha:
        raise AssertionError("B checkpoint changed after independent forks")
    sample_clean = p.challenge_pairs("C", key, 8)
    sample_corrupt = p.challenge_pairs("C", key, 8, corrupt=True)
    clean_outputs = sorted(tuple(q[1]["mediators"]) for q in sample_clean)
    corrupt_outputs = sorted(tuple(q[1]["mediators"]) for q in sample_corrupt)
    if clean_outputs != corrupt_outputs:
        raise AssertionError("negative shuffled challenge changed marginals")
    if not any(a[1]["mediators"] != b[1]["mediators"]
               for a, b in zip(sample_clean, sample_corrupt)):
        raise AssertionError("negative fixture does not perturb associations")
    before_negative = p.challenge_checkpoint(
        "aai10c", models["aai10c"], "C", key, 8, corrupt=False
    )
    after_negative = p.challenge_checkpoint(
        "aai10c", models["aai10c"], "C", key, 8, corrupt=True
    )
    # Two negative controls need not force different final model states;
    # only mutated public causal associations and identical observation
    # budgets/marginals are required at this source-prep stage.
    if not before_negative or not after_negative:
        raise AssertionError("negative continuation invalid")
    full_trace_sha = hashlib.sha256(old.canonical(result).encode()).hexdigest()
    return {
        "schema": "yggdrasil.contrib.aai10d.fixture.v1",
        "status": "SOURCE_FIXTURE_ONLY_NOT_A_SCIENTIFIC_RESULT",
        "fixture": key,
        "public_training_rows": len(observed),
        "matched_methods": list(p.MATCHED),
        "candidate": "aai10c",
        "full_budget_single_slot": True,
        "evaluated_laws": ["A", "B", "C", "D"],
        "challenge_trial_counts": list(p.PRIMARY_BUDGETS),
        "contexts_per_branch": context_count,
        "method_condition_results": len(result),
        "checkpoint_preserved": True,
        "negative_feedback_marginals_preserved": True,
        "negative_feedback_causal_pairing_perturbed": True,
        "phase_independent_action_trace_sha256": full_trace_sha,
        "scored_science_cohorts": 0,
        "native_model_changed": False,
        "first_use_authorized": False,
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--fixture", choices=p.FIXTURES)
    parser.add_argument("--primary", action="store_true")
    args=parser.parse_args()
    if args.primary:
        parser.error("AAI-10D SCIENTIFIC FIRST USE DISARMED")
    if args.fixture is None:
        parser.error("AAI-10D fixture-only synthetic qualification")
    print(json.dumps(run_fixture(args.fixture), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
