"""Matched repeated-switch and corrupted-evidence audit for active/archive selection.

Harness changes public consequences only. Neither candidate receives phase
labels; each switch incurs two independently owned probe actions. Keep wrong
answers and abstentions as primary results rather than selecting favorable
trials. All four regimes use a common training and memory budget.
"""
import json
from evidence_selected_three_step import EvidenceSelectedThreeStep
from context_regime_stress_audit import intervene
from test_three_step_feature_cells import fit
from public_transition_planner import PublicTransitionPlanner

def run():
    agent = EvidenceSelectedThreeStep(positions=2, capacity=128)
    fit(agent, PublicTransitionPlanner())
    agent.freeze_boundary()
    intervene(agent, b"zA-reversed", reverse=True, repeats=12)
    cases = []
    # Retained, reversed, retained, reversed; same public frame means memory
    # identity cannot be inferred from a fixed first-byte context partition.
    trials = (
        ("A_prior", b"xA-retention", False, False),
        ("B_changed", b"zA-reversed", True, False),
        ("A_return", b"xA-retention", False, False),
        ("B_return", b"zA-reversed", True, False),
        ("B_reward_corrupted", b"zA-reversed", True, True),
        ("B_public_collision", b"xA-collision", True, False),
        ("unknown_family", b"qQ-unseen", False, False),
    )
    for name, frame, reverse, corrupt in trials:
        agent.begin_probe()
        for action in (0, 1):
            good = action == (0 if reverse else 1)
            successor = b"M1-intermediate" if good else b"D2-intermediate"
            agent.observe(frame, [0, 1])
            agent.learn(action, successor, int(not good) if corrupt else 0, False)
        evidence = list(agent.evidence)
        diagnostics = {
            "active_prediction": [sample[3][0] for sample in evidence],
            "archive_prediction": [sample[3][1] for sample in evidence],
            "observed_successor": [sample[2] for sample in evidence],
            "active_matches": sum(sample[3][0] == sample[2] for sample in evidence),
            "archive_matches": sum(sample[3][1] == sample[2] for sample in evidence),
        }
        admitted = agent.resolve_probe()
        agent.observe(frame, [0, 1])
        decision = agent.choose(3)
        cases.append({
            "case": name,
            "admitted": admitted,
            "selected": agent.selected,
            "decision": decision,
            "expected": 0 if reverse else 1,
            "correct": decision == (0 if reverse else 1),
            "abstained": decision is None,
            "probe_actions": 2,
            "reward_corrupted": corrupt,
            "stored_examples": agent.stored_examples(),
            "diagnostics": diagnostics,
        })
        agent.current = None
        agent.active.current = None
        agent.snapshot.current = None
    return {
        "cases": cases,
        "correct": sum(c["correct"] for c in cases),
        "abstentions": sum(c["abstained"] for c in cases),
        "wrong_decisions": sum(c["decision"] is not None and not c["correct"] for c in cases),
        "extra_probe_actions": sum(c["probe_actions"] for c in cases),
        "memory_cap": 2 * agent.capacity,
        "scope": "Source-free public-action interventions, not original DoorKey episodes",
        "limitation": "A fixed two-compartment model may fail after repeated adaptation, and a shared manipulated successor channel remains undetectable",
    }

if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True))
