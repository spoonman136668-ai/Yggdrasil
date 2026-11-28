"""Prospective self-selected probes on synthetic public two-hop environments.

The probe planner receives only previously learned maps and public legal
starting actions. A separate deterministic environment produces outcomes
AFTER the selected interventions. Distractor starting frames prevent assuming
the original fixed probe sequence. Training history, actions and memory are
accounted. The all-corrupted successor case remains a visible scientific
negative, rather than being filtered out.
"""
import json
from causal_probe_planner import CausalProbePlanner
from two_hop_evidence_audit import build, FIRST, SECOND

def trial(world="A", corrupted=False, reverse_starts=False):
    agent = build()
    starts = [
        (b"uQ-unrelated", (0, 1)),
        (b"xB-training", (0, 1)),
        (b"xA-training", (0, 1)),
    ]
    if reverse_starts:
        starts.reverse()
    planner = CausalProbePlanner(max_candidates=32)
    proposals = planner.rank(agent.active_links, agent.archived_links, starts)
    chosen = planner.select_pair(agent.active_links, agent.archived_links, starts)
    if chosen is None:
        raise AssertionError("NO_DISTINGUISHING_PAIR")
    # Environment is not queried until the planner has committed its probes.
    # Independent deterministic physical first-hop fixture supports EVERY
    # legal action, including candidates chosen by the planner rather than
    # the earlier manually selected FIRST sequence.
    public_first = {
        (frame, action): (b"M1-intermediate" if
                          action == (1 if frame[1:2] == b"A" else 0)
                          else b"D2-intermediate")
        for frame in (b"xA-training", b"xB-training")
        for action in (0, 1)
    }
    public_second = {
        (middle, action): (old if world == "A" else new)
        for middle, action, old, new in SECOND
    }
    if corrupted:
        public_second = {
            (middle, action): (new if world == "A" else old)
            for middle, action, old, new in SECOND
        }
    agent.begin_chain_probe()
    for first, intermediate, second in chosen:
        actual_middle = public_first[first]
        agent.observe(first[0], [0, 1])
        agent.learn(first[1], actual_middle, 0, False)
        agent.observe(actual_middle, [second[1]])
        agent.learn(second[1], public_second[second], 0, False)
    admitted = agent.resolve_chain_probe()
    return {
        "world": world,
        "corrupted": corrupted,
        "admitted": admitted,
        "selected": agent.selected,
        "expected": "snapshot" if world == "A" else "active",
        "candidate_count": len(proposals),
        "chosen_first_frames": [first[0].decode() for first, _, _ in chosen],
        "two_action_probes": len(chosen),
        "physical_interventions": 2 * len(chosen),
        "extra_successor_records": (len(agent.active_links) +
                                    len(agent.archived_links)),
        "stored_fit_examples": agent.stored_examples(),
    }

def run():
    return {
        "A_return": trial("A"),
        "B_continues": trial("B"),
        "A_with_corrupted_successors": trial("A", corrupted=True),
        "permuted_start_order": trial("A", reverse_starts=True),
        "scope": "Source-free public FIT; probes ranked before outcomes are observed",
        "caveat": "A fully corrupted successor channel can still falsely corroborate an obsolete model",
    }

if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True))
