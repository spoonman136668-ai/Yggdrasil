"""Deterministic public-only interactive learning benchmark, not DoorKey.

Compares bounded native local learners to exact-state and shared-feature
controls on repeated action consequences and unseen observations.
"""
import json
from adaptive_feature_cells import AdaptiveFeatureCells
from eligibility_local_cells import EligibilityLocalCells
from feature_eligibility_cells import FeatureEligibilityCells

def run(episodes=16):
    if type(episodes) is not int or not 2 <= episodes <= 128:
        raise ValueError("EPISODE_COUNT_INVALID")
    learners = {
        "adaptive": AdaptiveFeatureCells(feature_bytes=2),
        "exact": EligibilityLocalCells(),
        "fixed_feature": FeatureEligibilityCells(feature_bytes=2),
    }
    counts = {name: {"train_success": 0, "transfer_success": 0, "train_actions": 0,
                     "transfer_actions": 0} for name in learners}
    for i in range(episodes):
        for name, learner in learners.items():
            frame = b"AB-train" if i % 2 == 0 else b"CD-train"
            goal_action = 1 if frame.startswith(b"AB") else 0
            learner.observe(frame, [0, 1])
            action = learner.choose()
            counts[name]["train_success"] += int(action == goal_action)
            counts[name]["train_actions"] += 1
            learner.learn(action, b"terminal", int(action == goal_action), True)
    for i in range(episodes):
        for name, learner in learners.items():
            frame = b"AB-unseen" if i % 2 == 0 else b"CD-unseen"
            goal_action = 1 if frame.startswith(b"AB") else 0
            learner.observe(frame, [0, 1])
            action = learner.choose()
            counts[name]["transfer_success"] += int(action == goal_action)
            counts[name]["transfer_actions"] += 1
    return {"episodes": episodes, "results": counts,
            "caveat": "Synthetic public-prefix regularity; fixed-feature prior supplied, not learned"}

if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True))
