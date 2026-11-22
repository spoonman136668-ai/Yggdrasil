"""OBS-01: retrospective source-free Bayes observability bound for frozen Yggdrasil laws.

Uses only PUBLIC, already-scored conditional probabilities from the pinned
staged-retention identifiability artifact. No source calls or native learning.
The two-law oracle is an upper bound WITHIN the declared fixed-context,
conditionally-independent Bernoulli measurement model. Correlated hidden-state
noise, changing contexts, unmodeled sensors or costs could change the result.
Not a deployable predictor, new experiment, or evidence of learning gain.
"""
from functools import lru_cache
from fractions import Fraction as F
import json
from pathlib import Path

INPUT_GIT_BLOB = "40fdcca22297d90022a72aeb407467ecd9707b2e"
PROTOCOL_GIT_BLOB = "1bbc1672ccd80f248c86c5ec7482f6ade8a0d76a"
MAX_PROBES = 8
NOISE_LEVELS = (F(0), F(1, 10))
CONTEXTS = (0, 1)
# Literal public conditional probabilities from the SHA-pinned old/new law
# analysis. This diagnostic intentionally cannot accept alternative sources.
EXPECTED_OLD = tuple(F(x) for x in
    ("5/32", "27/32", "5/32", "27/32", "7/32", "25/32", "7/32", "25/32"))
EXPECTED_NEW = tuple(F(x) for x in
    ("27/32", "5/32", "27/32", "5/32", "7/32", "7/32", "7/32", "7/32"))


def _check_laws(data):
    if data.get("shared_static_readout_only") is not True or data.get("includes_outcomes_generated") != 0:
        raise ValueError("OBS01_NOT_PINNED_ANALYTIC_INPUT")
    old = tuple(F(x) for x in data["old_transition_probability"])
    new = tuple(F(x) for x in data["new_transition_probability"])
    if len(old) != 8 or len(new) != 8 or any(not 0 < p < 1 for p in old + new):
        raise ValueError("OBS01_INVALID_PROBABILITIES")
    if old != EXPECTED_OLD or new != EXPECTED_NEW:
        raise ValueError("OBS01_PINNED_SOURCE_MISMATCH")
    return old, new


def posterior_optimum(pairs, n, noise=F(0)):
    """Exact Bayes balanced-prior MAP success; optimal adaptive action choice.

    Each pair is P(outcome=1 | old law), P(outcome=1 | new law).
    The controller sees only its chosen binary action and subsequent outcome,
    not the regime. The oracle knows the frozen probabilities: optimistic floor.
    """
    if type(n) is not int or not 0 <= n <= MAX_PROBES or noise not in NOISE_LEVELS:
        raise ValueError("OBS01_BUDGET")
    if not pairs or any(not 0 < a < 1 or not 0 < b < 1 for a, b in pairs):
        raise ValueError("OBS01_PAIRS")
    choices = tuple((noise + (1 - 2 * noise) * a,
                     noise + (1 - 2 * noise) * b) for a, b in pairs)

    @lru_cache(None)
    def expected_correct(remaining, mass_old, mass_new):
        if remaining == 0:
            return max(mass_old, mass_new)
        return max(
            expected_correct(remaining - 1, mass_old * (1 - a), mass_new * (1 - b))
            + expected_correct(remaining - 1, mass_old * a, mass_new * b)
            for a, b in choices
        )

    return expected_correct(n, F(1, 2), F(1, 2))


def run(data):
    old, new = _check_laws(data)
    cases = []
    for context in CONTEXTS:
        # The nuisance bit is not a regime label; it is fixed at zero here.
        pair_a0 = (old[context * 4], new[context * 4])
        pair_a1 = (old[context * 4 + 1], new[context * 4 + 1])
        for noise in NOISE_LEVELS:
            optimum = [posterior_optimum((pair_a0, pair_a1), n, noise)
                       for n in range(MAX_PROBES + 1)]
            a0 = [posterior_optimum((pair_a0,), n, noise)
                  for n in range(MAX_PROBES + 1)]
            a1 = [posterior_optimum((pair_a1,), n, noise)
                  for n in range(MAX_PROBES + 1)]
            threshold = F(19, 20)  # 95% detection probability target
            first = next((i for i, score in enumerate(optimum) if score >= threshold), None)
            cases.append({
                "public_context": context,
                "independent_outcome_flip_noise": str(noise),
                "old_new_p1_action0": [str(p) for p in pair_a0],
                "old_new_p1_action1": [str(p) for p in pair_a1],
                "best_adaptive_map_accuracy": [str(x) for x in optimum],
                "fixed_action0_accuracy": [str(x) for x in a0],
                "fixed_action1_accuracy": [str(x) for x in a1],
                "first_95pct_probes_up_to_8": first,
                "no_information_action0": pair_a0[0] == pair_a0[1],
            })
    return {
        "id": "OBS-01",
        "status": "RETROSPECTIVE_ANALYTIC_DIAGNOSTIC_NOT_SCIENTIFIC_FIRST_USE",
        "input_git_blob": INPUT_GIT_BLOB,
        "protocol_git_blob": PROTOCOL_GIT_BLOB,
        "source_world_actions": 0,
        "real_native_learning": False,
        "conditional_independence_assumed": True,
        "fixed_observed_context_assumed": True,
        "balanced_old_new_prior_assumed": True,
        "scientific_gain_verified": False,
        "max_charged_actions_in_bound": MAX_PROBES,
        "cases": cases,
    }


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--output", required=True)
    a = ap.parse_args()
    result = run(json.loads(Path(a.input).read_text()))
    Path(a.output).write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print("OBS01_RETROSPECTIVE: 4 analytic cases; no first-use; no model gain")
