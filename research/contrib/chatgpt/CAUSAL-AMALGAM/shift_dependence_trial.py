"""Fit cross-cell change dependence from anonymous synthetic observations."""

from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
from random import Random
from statistics import mean
from time import monotonic


HERE = Path(__file__).resolve().parent
PLAN = HERE / "shift-dependence-dev-01" / "prereg.json"
DONOR = (5 / 32, 27 / 32)
TARGET = (25 / 32, 7 / 32)


def worlds(scope, seed, agreement, split, count, probes, target_probes):
    key = f"{scope}:{seed}:{agreement}:{split}".encode("ascii")
    generator = Random(int.from_bytes(sha256(key).digest(), "big"))
    rows = []
    for index in range(count):
        donor = generator.randrange(2)
        target = donor if generator.random() < agreement else 1 - donor
        a = sum(generator.random() < DONOR[donor] for _ in range(probes))
        b = sum(generator.random() < TARGET[target] for _ in range(target_probes))
        rows.append((index, a, b))
    return rows


def likelihood(ones, total, probability):
    return probability**ones * (1 - probability)**(total - ones)


def observe_fit(receipts, hypotheses, probes):
    """Integrate over each unknown pair of local shift states."""
    masses = [1 / len(hypotheses)] * len(hypotheses)
    for _, a, b in receipts:
        donor = [likelihood(a, probes, p) for p in DONOR]
        target = [likelihood(b, probes, p) for p in TARGET]
        same = sum(u * v for u, v in zip(donor, target, strict=True))
        different = sum(u * v for u, v in zip(donor, reversed(target), strict=True))
        masses = [weight * (same * h + different * (1 - h))
                  for weight, h in zip(masses, hypotheses, strict=True)]
        total = sum(masses)
        masses = [weight / total for weight in masses]
    return masses


def prediction(ones, probes, agreement):
    unchanged, changed = (likelihood(ones, probes, p) for p in DONOR)
    shift = (unchanged * (1 - agreement) + changed * agreement) / (unchanged + changed)
    return TARGET[0] * (1 - shift) + TARGET[1] * shift


def run():
    started = monotonic()
    raw = PLAN.read_bytes()
    plan = json.loads(raw)
    hypotheses = [float(Fraction(value)) for value in plan["hypotheses"]]
    rows = []
    for seed in plan["seeds"]:
        for truth in hypotheses:
            fit = worlds(plan["id"], seed, truth, "fit", plan["fit_worlds"],
                         plan["fit_probes_per_cell"], plan["fit_probes_per_cell"])
            held = worlds(plan["id"], seed, truth, "held", plan["held_worlds"],
                          plan["held_donor_probes"], 1)
            posterior = observe_fit(fit, hypotheses, plan["fit_probes_per_cell"])
            fitted = sum(h * w for h, w in zip(hypotheses, posterior, strict=True))
            scores = {name: mean((prediction(a, plan["held_donor_probes"], agreement) - b)**2
                                 for _, a, b in held)
                      for name, agreement in (("independent", .5), ("coupled", 1.0),
                                              ("fitted", fitted), ("oracle", truth))}
            trace = json.dumps([fit, held], separators=(",", ":")).encode("ascii")
            rows.append(dict(seed=seed, agreement=truth, posterior=posterior, fitted=fitted,
                             brier=scores, trace_sha256=sha256(trace).hexdigest(),
                             actions=len(fit) * 2 * plan["fit_probes_per_cell"]
                             + len(held) * (plan["held_donor_probes"] + 1)))
    correlated = [r for r in rows if r["agreement"] != .5]
    null = [r for r in rows if r["agreement"] == .5]
    gain = mean(r["brier"]["independent"] - r["brier"]["fitted"] for r in correlated)
    drift = max(r["brier"]["fitted"] - r["brier"]["independent"] for r in null)
    signal = gain >= plan["min_correlated_gain"] and drift <= plan["max_null_drift"]
    actions = sum(r["actions"] for r in rows)
    if actions != plan["budget_actions"]:
        raise ValueError("Trial action budget differs from preregistration")
    return dict(verdict="DEV_SIGNAL" if signal else "DEV_NO_GO", rows=rows,
                correlated_brier_gain=gain, worst_independent_drift=drift,
                source_actions=actions, witnesses_admitted=0,
                protocol_sha256=sha256(raw).hexdigest(), wall_seconds=monotonic() - started)


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
