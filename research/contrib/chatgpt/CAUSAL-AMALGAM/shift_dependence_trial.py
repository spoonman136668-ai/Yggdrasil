"""Fit cross-cell change dependence from anonymous synthetic observations."""

from fractions import Fraction
from hashlib import sha256
import json
from math import sqrt
from pathlib import Path
from random import Random
from statistics import mean
import sys
from time import monotonic


HERE = Path(__file__).resolve().parent
PLAN = HERE / "shift-dependence-dev-01" / "prereg.json"
DONOR = (5 / 32, 27 / 32)
TARGET = (25 / 32, 7 / 32)


def worlds(scope, seed, agreement, split, count, probes, target_probes,
           laws=(DONOR, TARGET)):
    key = f"{scope}:{seed}:{agreement}:{split}".encode("ascii")
    generator = Random(int.from_bytes(sha256(key).digest(), "big"))
    rows = []
    for index in range(count):
        donor = generator.randrange(2)
        target = donor if generator.random() < agreement else 1 - donor
        a = sum(generator.random() < laws[0][donor] for _ in range(probes))
        b = sum(generator.random() < laws[1][target] for _ in range(target_probes))
        rows.append((index, a, b))
    return rows


def likelihood(ones, total, probability):
    return probability**ones * (1 - probability)**(total - ones)


def observe_fit(receipts, hypotheses, probes, laws=(DONOR, TARGET)):
    """Integrate over each unknown pair of local shift states."""
    masses = [1 / len(hypotheses)] * len(hypotheses)
    for _, a, b in receipts:
        donor = [likelihood(a, probes, p) for p in laws[0]]
        target = [likelihood(b, probes, p) for p in laws[1]]
        same = sum(u * v for u, v in zip(donor, target, strict=True))
        different = sum(u * v for u, v in zip(donor, reversed(target), strict=True))
        masses = [weight * (same * h + different * (1 - h))
                  for weight, h in zip(masses, hypotheses, strict=True)]
        total = sum(masses)
        masses = [weight / total for weight in masses]
    return masses


def fit_marginal_contrast(receipts, probes):
    """Use the second factorial moment of a balanced symmetric mixture."""
    cap = 0.5 - 1 / (2 * (len(receipts) + 1))
    margins = []
    for i in (1, 2):
        second = mean(row[i] * (row[i] - 1) for row in receipts) / (probes * (probes - 1))
        contrast = min(cap, sqrt(max(0, second - .25)))
        margins.append((.5 - contrast, .5 + contrast))
    return margins[0], margins[1][::-1]


def prediction(ones, probes, agreement, laws=(DONOR, TARGET)):
    unchanged, changed = (likelihood(ones, probes, p) for p in laws[0])
    shift = (unchanged * (1 - agreement) + changed * agreement) / (unchanged + changed)
    return laws[1][0] * (1 - shift) + laws[1][1] * shift


def run(protocol=PLAN):
    started = monotonic()
    raw = protocol.read_bytes()
    plan = json.loads(raw)
    hypotheses = [float(Fraction(value)) for value in plan["hypotheses"]]
    rows = []
    families = plan.get("families", {"": (DONOR, TARGET)})
    for family, laws in families.items():
        for seed in plan["seeds"]:
            for truth in hypotheses:
                scope = f"{plan['id']}-{family}" if family else plan["id"]
                fit = worlds(scope, seed, truth, "fit", plan["fit_worlds"],
                             plan["fit_probes_per_cell"], plan["fit_probes_per_cell"], laws)
                held = worlds(scope, seed, truth, "held", plan["held_worlds"],
                              plan["held_donor_probes"], 1, laws)
                posterior = observe_fit(fit, hypotheses, plan["fit_probes_per_cell"])
                fitted = sum(h * w for h, w in zip(hypotheses, posterior, strict=True))
                scores = {name: mean((prediction(a, plan["held_donor_probes"], agreement) - b)**2
                                     for _, a, b in held)
                          for name, agreement in (("independent", .5), ("coupled", 1.0),
                                                  ("fitted", fitted))}
                scores["oracle"] = mean((prediction(a, plan["held_donor_probes"], truth, laws)
                                         - b)**2 for _, a, b in held)
                trace = json.dumps([fit, held], separators=(",", ":")).encode("ascii")
                rows.append(dict(seed=seed, agreement=truth, posterior=posterior, fitted=fitted,
                                 brier=scores, trace_sha256=sha256(trace).hexdigest(),
                                 actions=len(fit) * 2 * plan["fit_probes_per_cell"]
                                 + len(held) * (plan["held_donor_probes"] + 1)))
                if family:
                    rows[-1]["family"] = family
                if plan.get("calibrate_marginals"):
                    learned = fit_marginal_contrast(fit, plan["fit_probes_per_cell"])
                    learned_weights = observe_fit(fit, hypotheses, plan["fit_probes_per_cell"],
                                                  learned)
                    known_weights = observe_fit(fit, hypotheses, plan["fit_probes_per_cell"], laws)
                    for name, weights, margins in (("calibrated", learned_weights, learned),
                                                    ("law_matched_fit", known_weights, laws)):
                        fitted_agreement = sum(h * w for h, w in zip(hypotheses, weights, strict=True))
                        scores[name] = mean((prediction(a, plan["held_donor_probes"],
                                                        fitted_agreement, margins) - b)**2
                                            for _, a, b in held)
                    rows[-1]["learned_margins"] = learned
    correlated = [r for r in rows if r["agreement"] != .5]
    null = [r for r in rows if r["agreement"] == .5]
    candidate = "calibrated" if plan.get("calibrate_marginals") else "fitted"
    gain = mean(r["brier"]["independent"] - r["brier"][candidate] for r in correlated)
    drift = max(r["brier"][candidate] - r["brier"]["independent"] for r in null)
    signal = gain >= plan["min_correlated_gain"] and drift <= plan["max_null_drift"]
    actions = sum(r["actions"] for r in rows)
    if actions != plan["budget_actions"]:
        raise ValueError("Trial action budget differs from preregistration")
    return dict(verdict="DEV_SIGNAL" if signal else "DEV_NO_GO", rows=rows,
                correlated_brier_gain=gain, worst_independent_drift=drift,
                source_actions=actions, witnesses_admitted=0,
                protocol_sha256=sha256(raw).hexdigest(), wall_seconds=monotonic() - started)


if __name__ == "__main__":
    protocol = Path(sys.argv[1]) if len(sys.argv) == 2 else PLAN
    print(json.dumps(run(protocol), indent=2, sort_keys=True))
