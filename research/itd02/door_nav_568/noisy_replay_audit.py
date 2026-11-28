"""Enumerated noisy-probe replay audit with action-owned public feedback.

Two observations cannot disambiguate a genuine environment change from two
adversarial label flips. Enumerate zero, one, and two flips; report both
false-restoration and correct-restoration counts without hiding negatives.
"""
import json
from evidence_gated_replay import EvidenceGatedReplay
from sequential_regimes import training_phase

PROBES = ((b"xB-train", 1), (b"yA-train", 1))
CORRECT = {
    "A": (0, 1),
    "B": (1, 0),
}

def run():
    cases = []
    for actual in ("A", "B"):
        for flip_mask in range(4):
            agent = EvidenceGatedReplay(feature_positions=2, max_examples=8)
            training_phase(agent, "A")
            agent.archive()
            training_phase(agent, "B")
            agent.start_probe()
            for index, (frame, action) in enumerate(PROBES):
                reward = CORRECT[actual][index] ^ ((flip_mask >> index) & 1)
                agent.observe(frame, [0, 1])
                agent.learn(action, b"terminal", reward, True)
            restored = agent.restore_with_evidence()
            cases.append({
                "actual": actual,
                "flip_mask": flip_mask,
                "flips": flip_mask.bit_count(),
                "restored": restored,
                "false_restoration": actual == "B" and restored,
                "correct_restoration": actual == "A" and restored,
                "probe_closed": not agent.probe_active,
            })
    return {
        "cases": cases,
        "total_cases": len(cases),
        "false_restorations": sum(case["false_restoration"] for case in cases),
        "correct_restorations": sum(case["correct_restoration"] for case in cases),
        "warning": "Two label flips make B feedback indistinguishable from A; no two-observation rule can resolve this",
    }

if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True))
