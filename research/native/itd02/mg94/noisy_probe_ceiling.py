#!/usr/bin/env python3
"""MG94-B: exhaustive source-free noisy-probe Bayes ceiling. No native science."""
import json
from fractions import Fraction
from pathlib import Path

reliabilities = [Fraction(n, 8) for n in range(4, 9)]
costs = [Fraction(n, 8) for n in range(5)]
rows = []
for reliability in reliabilities:
    for cost in costs:
        blind = Fraction(1, 2)
        probe = reliability - cost
        optimal = max(blind, probe)
        decision = "probe" if probe > blind else "blind_or_tie"
        # Direct enumeration of both hidden states and both public signals.
        total = Fraction(0)
        for h in (0, 1):
            for signal in (0, 1):
                probability = reliability if signal == h else (1 - reliability)
                correct = int(signal == h)
                total += Fraction(1, 2) * probability * (correct - cost)
        assert total == probe
        assert optimal >= blind and optimal >= probe
        rows.append({
            "reliability": str(reliability), "cost": str(cost),
            "blind_value": str(blind), "probe_value": str(total),
            "bayes_optimum": str(optimal), "bayes_choice": decision
        })
assert len(rows) == 25
assert sum(x["bayes_choice"] == "probe" for x in rows) == 10
report = {
  "schema": "mg94.source_free.noisy_probe_ceiling.v1",
  "classification": "ANALYTIC_DEVELOPMENT_ONLY_NOT_NATIVE_SCIENCE",
  "comparison": "Bayes-optimal decision with identical public signal",
  "parameter_grid": "reliability 4/8..8/8 and cost 0/8..4/8",
  "case_count": len(rows), "probe_optimal_cases": 10,
  "native_advantage": "NOT_TESTED",
  "source_world_executed": False,
  "claim": "On this stipulated two-world decision model, no equally informed actor can exceed the Bayes optimum in expected return.",
  "rows": rows
}
path = Path(__file__).with_suffix(".json")
path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print("MG94_B_ANALYTIC_PASS", len(rows), report["probe_optimal_cases"])
