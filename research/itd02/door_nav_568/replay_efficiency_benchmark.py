"""Matched-feedback return-to-regime experiment; no original DoorKey episodes.

The replay learner sees exactly the same two post-switch intervention outcomes
as a fresh baseline. Reports held-out decisions, evidence use, and retained
history; never assumes replay must outperform scratch.
"""
import json
from evidence_gated_replay import EvidenceGatedReplay
from learned_byte_cells import LearnedByteCells
from sequential_regimes import evaluate, training_phase

PROBE_A = ((b"xB-train", 1, 0), (b"yA-train", 1, 1))
PROBE_B = ((b"xB-train", 1, 1), (b"yA-train", 1, 0))

def feed(agent, observations):
    for frame, action, reward in observations:
        agent.observe(frame, [0, 1])
        agent.learn(action, b"terminal", reward, True)

def run(probe=PROBE_A):
    replay = EvidenceGatedReplay(feature_positions=2, max_examples=8)
    training_phase(replay, "A")
    replay.archive()
    training_phase(replay, "B")
    before = {"A": evaluate(replay, "A"), "B": evaluate(replay, "B")}
    replay.start_probe()
    fresh = LearnedByteCells(feature_positions=2, max_examples=8)
    feed(replay, probe)
    feed(fresh, probe)
    restored = replay.restore_with_evidence()
    return {
        "probe_observations_per_candidate": len(probe),
        "pre_switch_scores": before,
        "replay_restored": restored,
        "replay_scores": {"A": evaluate(replay, "A"), "B": evaluate(replay, "B")},
        "fresh_scores": {"A": evaluate(fresh, "A"), "B": evaluate(fresh, "B")},
        "replay_history": len(replay.active.examples),
        "fresh_history": len(fresh.examples),
        "archive_count": len(replay.archives),
        "caveat": "Synthetic matched public FIT; archived prior eight samples are additional historical information, not free compute",
    }

if __name__ == "__main__":
    print(json.dumps({"A_return": run(PROBE_A), "B_continues": run(PROBE_B)}, sort_keys=True))
