"""Matched public intervention benchmark for reward-only vs successor-corroborated replay.

Both arms get identical A then B historical experience and two public probes.
The successor arm also stores historical public next-state observations.
Reward and next-state channels are manipulated independently in this synthetic
fixture; joint corruption remains indistinguishable from genuine reversal.
"""
import json
from evidence_gated_replay import EvidenceGatedReplay
from successor_corroborated_replay import SuccessorCorroboratedReplay
from sequential_regimes import training_phase, evaluate
from test_successor_corroborated_replay import fit, PROBES, reward_for

def run():
    cases = []
    for reward_regime in ("A", "B"):
        for successor_regime in ("A", "B"):
            plain = EvidenceGatedReplay(feature_positions=2, max_examples=8)
            training_phase(plain, "A")
            plain.archive()
            training_phase(plain, "B")
            corroborated = SuccessorCorroboratedReplay()
            fit(corroborated, "A")
            corroborated.archive()
            fit(corroborated, "B")
            plain.start_probe()
            corroborated.start_probe()
            for frame, action in PROBES:
                reward = reward_for(reward_regime, frame, action)
                next_frame = successor_regime.encode() + b":" + frame
                for learner in (plain, corroborated):
                    learner.observe(frame, [0, 1])
                    learner.learn(action, next_frame, reward, True)
            plain_restored = plain.restore_with_evidence()
            corroborated_restored = corroborated.restore_with_corrob()
            cases.append({
                "reward_channel": reward_regime,
                "successor_channel": successor_regime,
                "reward_only_restored": plain_restored,
                "corroborated_restored": corroborated_restored,
                "reward_only_A_success": evaluate(plain, "A"),
                "corroborated_A_success": evaluate(corroborated, "A"),
                "probe_actions_per_arm": len(PROBES),
                "historical_reward_examples_per_arm": 16,
                "additional_successor_transition_examples": 16,
                "public_successor_key_count": len(corroborated.archived_successors) +
                                              len(corroborated.current_successors),
            })
    return {
        "cases": cases,
        "scope": "Source-free matched synthetic reward/successor interventions",
        "qualification_limit": "Next-state observations are a second public signal, not an independently verified sensor",
    }

if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True))
