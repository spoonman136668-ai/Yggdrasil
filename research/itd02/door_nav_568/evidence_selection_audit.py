"""Prospective native model selection by public, owned successor evidence.

An identical two-action probe is used for each candidate. This explicitly
accounts for extra training feedback and exposes abstentions, not just wins.
"""
import json
from evidence_selected_three_step import EvidenceSelectedThreeStep
from test_three_step_feature_cells import fit
from context_regime_stress_audit import intervene
from public_transition_planner import PublicTransitionPlanner

def experiment(frame, reverse):
    agent = EvidenceSelectedThreeStep(positions=2, capacity=128)
    fit(agent, PublicTransitionPlanner())
    agent.freeze_boundary()
    intervene(agent, b"zA-reversed", reverse=True, repeats=12)
    agent.begin_probe()
    for action in (0, 1):
        correct = action == (0 if reverse else 1)
        successor = b"M1-intermediate" if correct else b"D2-intermediate"
        agent.observe(frame, [0, 1])
        agent.learn(action, successor, 0, False)
    admitted = agent.resolve_probe()
    agent.observe(frame, [0, 1])
    decision = agent.choose(3)
    return {
        "admitted": admitted,
        "selected": agent.selected,
        "decision": decision,
        "expected": 0 if reverse else 1,
        "extra_probe_interactions": 2,
        "stored_examples": agent.stored_examples(),
        "max_examples": 2 * agent.capacity,
    }

def run():
    return {
        "B_changed": experiment(b"zA-reversed", True),
        "A_prior_context": experiment(b"xA-retention", False),
        "scope": "Synthetic public successor feedback; two owned interventions per case",
        "caveat": "No guaranteed selection when features alias or both models lack coverage",
    }

if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True))
