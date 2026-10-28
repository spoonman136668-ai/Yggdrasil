"""Prospective public two-hop evidence, with matched active/archive probes."""
import json
from two_hop_evidence_selector import TwoHopEvidenceSelector
from test_three_step_feature_cells import fit
from public_transition_planner import PublicTransitionPlanner

FIRST = ((b"xA-training", 1, b"M1-intermediate"),
         (b"xB-training", 1, b"D2-intermediate"))
SECOND = ((b"M1-intermediate", 2, b"R3-positive", b"X5-shift"),
          (b"D2-intermediate", 2, b"F4-negative", b"Y6-shift"))

def build():
    learner = TwoHopEvidenceSelector(positions=2, capacity=128)
    fit(learner, PublicTransitionPlanner())
    learner.freeze_boundary()
    # Both memories retain the same first hop. B changes only the second.
    for middle, action, original, shifted in SECOND:
        learner.observe(middle, [action])
        learner.learn(action, shifted, 0, False)
    return learner

def examine(world="A", corrupted=False):
    learner = build()
    learner.begin_chain_probe()
    for (start, action, middle), (_, second_action, original, shifted) in zip(FIRST, SECOND):
        learner.observe(start, [0, 1])
        learner.learn(action, middle, 0, False)
        learner.observe(middle, [second_action])
        successor = original if world == "A" else shifted
        if corrupted:
            successor = shifted if world == "A" else original
        learner.learn(second_action, successor, 0, False)
    selected = learner.resolve_chain_probe()
    return {
        "world": world,
        "corrupted_second_hop": corrupted,
        "admitted": selected,
        "selected": learner.selected,
        "expected": "snapshot" if world == "A" else "active",
        "first_hop_agrees": all(
            learner.active_links[(frame, action)] ==
            learner.archived_links[(frame, action)]
            for frame, action, _ in FIRST
        ),
        "probe_actions": 4,
        "active_transition_records": len(learner.active_links),
        "archive_transition_records": len(learner.archived_links),
        "stored_examples": learner.stored_examples(),
    }

def run():
    return {
        "A_return": examine("A"),
        "B_continues": examine("B"),
        "A_corrupted": examine("A", corrupted=True),
        "scope": "Synthetic, learned public two-stage action consequences",
        "caveat": "A shared falsified second-hop observation can select wrong memory; no original DoorKey episodes",
    }

if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True))
