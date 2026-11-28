"""Exhaustive, source-free replay feedback-corruption comparison.

No stochastic sampling: every bit-flip pattern is enumerated separately for
returning A and continuing B. The hardened policy uses a third *distinct*
public frame/action probe. Baseline and hardened outcomes are reported with
their different interaction counts and historical archive costs.
"""
import json
from evidence_gated_replay import EvidenceGatedReplay
from sequential_regimes import training_phase

PROBES = (
    (b"xB-train", 1, {"A": 0, "B": 1}),
    (b"yA-train", 1, {"A": 1, "B": 0}),
    (b"xB-train", 0, {"A": 1, "B": 0}),
)

def run():
    report = {}
    for required in (2, 3):
        cases = []
        for regime in ("A", "B"):
            for mask in range(1 << required):
                agent = EvidenceGatedReplay(
                    feature_positions=2, max_examples=8,
                    max_archives=2, min_probe_samples=required,
                )
                training_phase(agent, "A")
                agent.archive()
                training_phase(agent, "B")
                agent.start_probe()
                for index, (frame, action, outcomes) in enumerate(PROBES[:required]):
                    reward = outcomes[regime] ^ ((mask >> index) & 1)
                    agent.observe(frame, [0, 1])
                    agent.learn(action, b"terminal", reward, True)
                restored = agent.restore_with_evidence()
                cases.append({
                    "regime": regime,
                    "flip_mask": mask,
                    "flipped_feedback": mask.bit_count(),
                    "restored": restored,
                    "false_restore": regime == "B" and restored,
                    "correct_restore": regime == "A" and restored,
                    "false_refusal": regime == "A" and not restored,
                    "probe_closed": not agent.probe_active,
                })
        report[str(required)] = {
            "cases": cases,
            "total_cases": len(cases),
            "probe_interactions_per_case": required,
            "archive_snapshots_per_case": 1,
            "archived_feedback_examples_per_case": 8,
            "false_restorations": sum(x["false_restore"] for x in cases),
            "correct_restorations": sum(x["correct_restore"] for x in cases),
            "false_refusals": sum(x["false_refusal"] for x in cases),
            "continuing_regime_cases": sum(x["regime"] == "B" for x in cases),
        }
    return {
        "policies": report,
        "scope": "Exhaustive Boolean corruptions of fixed public probes, not an environmental noise model",
        "warning": "All-flipped evidence remains indistinguishable from an actual regime switch",
    }

if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True))
