"""Deterministic source-free matched-feedback interactive learning benchmark.

All candidates receive exactly the same public frames, actions, and rewards
during FIT; transfer is evaluated without feedback. Synthetic prefix structure
is specified by the experimenter, not autonomously discovered.
"""
import json
from adaptive_feature_cells import AdaptiveFeatureCells
from eligibility_local_cells import EligibilityLocalCells
from feature_eligibility_cells import FeatureEligibilityCells
from public_transition_planner import PublicTransitionPlanner

def run(episodes=16):
    if type(episodes) is not int or not 2 <= episodes <= 128:
        raise ValueError("EPISODE_COUNT_INVALID")
    learners = {
        "adaptive": AdaptiveFeatureCells(feature_bytes=2),
        "exact": EligibilityLocalCells(),
        "fixed_feature": FeatureEligibilityCells(feature_bytes=2),
        "conventional_tabular": PublicTransitionPlanner(),
    }
    counts = {name: {"train_success": 0, "transfer_success": 0,
                     "train_actions": 0, "transfer_actions": 0}
              for name in learners}
    # Interleaved fixed action coverage: both actions sampled equally within
    # each public training state. This is identical evidence for every learner,
    # and does not use candidates' action choices to generate FIT data.
    for i in range(episodes):
        frame = b"AB-train" if (i // 2) % 2 == 0 else b"CD-train"
        action = i % 2
        goal_action = 1 if frame.startswith(b"AB") else 0
        reward = int(action == goal_action)
        for name, learner in learners.items():
            learner.observe(frame, [0, 1])
            learner.learn(action, b"terminal", reward, True)
            counts[name]["train_success"] += reward
            counts[name]["train_actions"] += 1
    for i in range(episodes):
        frame = b"AB-unseen" if i % 2 == 0 else b"CD-unseen"
        goal_action = 1 if frame.startswith(b"AB") else 0
        for name, learner in learners.items():
            learner.observe(frame, [0, 1])
            action = learner.choose(horizon=1) if name == "conventional_tabular" else learner.choose()
            counts[name]["transfer_success"] += int(action == goal_action)
            counts[name]["transfer_actions"] += 1
    return {"episodes": episodes, "results": counts,
            "fit_policy": "paired balanced actions; same feedback per learner",
            "caveat": "Synthetic fixed-prefix regularity; supplied feature prior, not native discovery; no DoorKey acceptance"}

if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True))
