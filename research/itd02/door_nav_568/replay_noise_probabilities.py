"""Exact probabilistic-noise audit over exhaustive replay counterexamples.

No random seeds, sampling claims, or original DoorKey episodes. Mask outcomes
are measured by the source-free replay harness; probabilities are weighted
analytically for independent errors and for an all-probe correlated inversion.
A mixture parameter q is probability of a shared inversion of *every* reward,
followed by independent per-reward flips with probability p.
"""
import json
from replay_corruption_comparison import run as exhaustive

SCENARIOS = (
    ("clean", 0.0, 0.0),
    ("independent_10pct", 0.1, 0.0),
    ("independent_25pct", 0.25, 0.0),
    ("correlated_10pct", 0.1, 0.1),
    ("correlated_25pct", 0.25, 0.25),
)

def probability(mask, n, p, q):
    flips = mask.bit_count()
    independent = p ** flips * (1.0 - p) ** (n - flips)
    shared_inverted = p ** (n - flips) * (1.0 - p) ** flips
    return (1.0 - q) * independent + q * shared_inverted

def run():
    policies = exhaustive()["policies"]
    records = []
    for label, p, q in SCENARIOS:
        for n in (2, 3):
            cases = policies[str(n)]["cases"]
            weighted = lambda predicate, regime: sum(
                probability(c["flip_mask"], n, p, q)
                for c in cases if c["regime"] == regime and predicate(c)
            )
            records.append({
                "scenario": label,
                "independent_flip_probability": p,
                "shared_inversion_probability": q,
                "probe_count": n,
                "false_restore_probability_given_B": weighted(lambda c: c["false_restore"], "B"),
                "correct_restore_probability_given_A": weighted(lambda c: c["correct_restore"], "A"),
                "false_refusal_probability_given_A": weighted(lambda c: c["false_refusal"], "A"),
                "probe_interactions_per_decision": n,
                "archived_feedback_examples": policies[str(n)]["archived_feedback_examples_per_case"],
                "archive_snapshots": policies[str(n)]["archive_snapshots_per_case"],
                "probability_mass_B": weighted(lambda c: True, "B"),
                "probability_mass_A": weighted(lambda c: True, "A"),
            })
    return {
        "records": records,
        "source": "Exact weighting of exhaustively executed 2- and 3-probe outcomes",
        "scope": "Specified independent and common-mode inversion mixture, not calibrated real-world noise",
        "warning": "Correlated inversion can defeat all probes; more feedback costs interaction time",
    }

if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True))
