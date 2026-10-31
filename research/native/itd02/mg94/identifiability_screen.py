#!/usr/bin/env python3
"""Source-free analytic screen. NOT original-world native qualification."""
import json
import hashlib
from pathlib import Path

# Hidden mechanism H in {0,1}, equiprobable. Pre-probe observation identical.
# Terminal choice matching H earns 1; probe costs 1/8 reward and reveals H.
# This is a mathematical example, NOT measured native research.
worlds = (0, 1)
policies = ("blind_fixed_0", "blind_fixed_1", "uniform_random_expected", "bayes_probe", "oracle_forbidden")

def outcome(h, policy):
    if policy == "blind_fixed_0":
        return 1.0 if h == 0 else 0.0
    if policy == "blind_fixed_1":
        return 1.0 if h == 1 else 0.0
    if policy == "uniform_random_expected":
        return 0.5
    if policy == "bayes_probe":
        return 1.0 - 0.125
    if policy == "oracle_forbidden":
        return 1.0
    raise ValueError(policy)

results = {p: sum(outcome(h, p) for h in worlds) / len(worlds) for p in policies}
assert results["blind_fixed_0"] == results["blind_fixed_1"] == 0.5
assert results["bayes_probe"] == 0.875
assert results["oracle_forbidden"] == 1.0

report = {
    "schema": "mg94.source_free.identifiability.v1",
    "classification": "ANALYTIC_DEVELOPMENT_ONLY_NOT_NATIVE_SCIENCE",
    "worlds": 2,
    "observation_before_probe": "identical",
    "probe_public_effect": "reveals causal regime",
    "probe_reward_cost": 0.125,
    "information_gain_bits": 1,
    "expected_net_reward": results,
    "causal_probe_uplift_over_uninformed": results["bayes_probe"] - 0.5,
    "native_unique_gain": "UNTESTED",
    "limitations": [
        "not original Farama source",
        "no trained native code",
        "Bayesian control already exploits entire information advantage",
        "oracle is forbidden comparator",
    ],
}
p = Path(__file__).with_suffix(".json")
payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
p.write_text(payload, encoding="utf-8")
print(payload, end="")
print("REPORT_SHA256", hashlib.sha256(p.read_bytes()).hexdigest())
