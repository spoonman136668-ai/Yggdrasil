"""Measure equal-budget probe allocations using shared simulator trajectories."""

from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
from random import Random
from statistics import mean
import sys
from time import monotonic

from joint_probe_model import JointProbeModel
from matched_probe_bound import gain
from shift_dependence_trial import fit_marginal_contrast, likelihood, observe_fit, worlds


PLAN = Path(__file__).resolve().parent / "probe-allocation-dev-01" / "prereg.json"


def allocation(laws, agreement, budget):
    donor, target = [tuple(Fraction(str(p)) for p in values) for values in laws]
    model = Fraction(str(agreement))
    return max(range(budget + 1), key=lambda n: gain(donor, target, model, n, budget - n))


def receive(donor_rows, target_rows, laws, agreement):
    first = [likelihood(sum(donor_rows), len(donor_rows), p) for p in laws[0]]
    second = [likelihood(sum(target_rows), len(target_rows), p) for p in laws[1]]
    masses = [second[t] * sum(first[d] * (agreement if d == t else 1 - agreement)
                              for d in range(2)) for t in range(2)]
    return sum(w * p for w, p in zip(masses, laws[1], strict=True)) / sum(masses)


def replicate(plan, family, true_laws, seed, truth):
    scope = f"{plan['id']}-{family}"
    n = plan["probes"]
    fit = worlds(scope, seed, truth, "calibration", plan["fit_worlds"],
                 plan["fit_probes_per_cell"], plan["fit_probes_per_cell"], true_laws)
    hypotheses = [.1, .5, .9]
    laws = fit_marginal_contrast(fit, plan["fit_probes_per_cell"])
    weights = observe_fit(fit, hypotheses, plan["fit_probes_per_cell"], laws)
    agreement = sum(h * w for h, w in zip(hypotheses, weights, strict=True))
    choices = dict(target=0, balanced=n // 2, donor=n, learned=allocation(laws, agreement, n),
                   oracle=allocation(true_laws, truth, n))
    joint = None
    if "joint_margins" in plan:
        joint = JointProbeModel(fit, plan["fit_probes_per_cell"], plan["joint_margins"], hypotheses)
        choices["joint"] = joint.allocation(n)
    digest = sha256()
    digest.update(json.dumps(fit, separators=(",", ":")).encode("ascii"))
    square = dict.fromkeys(choices, 0.)
    key = f"{scope}:{seed}:{truth}:held".encode("ascii")
    generator = Random(int.from_bytes(sha256(key).digest(), "big"))
    for _ in range(plan["held_worlds"]):
        first = generator.randrange(2)
        second = first if generator.random() < truth else 1 - first
        source_d = [int(generator.random() < true_laws[0][first]) for _ in range(n)]
        source_t = [int(generator.random() < true_laws[1][second]) for _ in range(n)]
        held = int(generator.random() < true_laws[1][second])
        observations = {}
        for name, count in choices.items():
            pair = source_d[:count], source_t[:n - count]
            observations[name] = pair
            if name == "oracle":
                forecast = receive(*pair, true_laws, truth)
            elif joint is not None:
                forecast = joint.predict(*pair)
            else:
                forecast = receive(*pair, laws, agreement)
            square[name] += (forecast - held)**2
        digest.update(json.dumps([observations, held], separators=(",", ":")).encode("ascii"))
    return dict(family=family, agreement=truth, seed=seed, donor_probes=choices,
                brier={name: value / plan["held_worlds"] for name, value in square.items()},
                actions=2 * len(fit) * plan["fit_probes_per_cell"]
                + plan["held_worlds"] * (len(choices) * n + 1),
                trace_sha256=digest.hexdigest())


def run(protocol=PLAN):
    started = monotonic()
    raw = protocol.read_bytes()
    plan = json.loads(raw)
    rows = [replicate(plan, family, laws, seed, truth)
            for family, laws in plan["families"].items()
            for seed in plan["seeds"] for truth in (.1, .5, .9)]
    comparisons = ("target", "balanced", "donor")
    selected = "joint" if "joint_margins" in plan else "learned"
    delta = mean(min(r["brier"][n] for n in comparisons) - r["brier"][selected]
                 for r in rows if r["agreement"] != .5)
    drift = max(r["brier"][selected] - r["brier"]["target"]
                for r in rows if r["agreement"] == .5)
    actions = sum(r["actions"] for r in rows)
    if actions != plan["budget_actions"]:
        raise ValueError("Action count exceeds frozen scope")
    signal = delta >= plan["min_correlated_gain"] and drift <= plan["max_null_drift"]
    return dict(verdict="DEV_SIGNAL" if signal else "DEV_NO_GO", rows=rows,
                gain_vs_best_fixed=delta, worst_independent_drift=drift,
                simulated_probes=actions, native_witnesses=0, wall_seconds=monotonic() - started,
                protocol_sha256=sha256(raw).hexdigest())


if __name__ == "__main__":
    protocol = Path(sys.argv[1]) if len(sys.argv) == 2 else PLAN
    print(json.dumps(run(protocol), indent=2, sort_keys=True))
