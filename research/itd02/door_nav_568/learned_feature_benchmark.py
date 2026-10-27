"""Matched-feedback held-out public-feature discovery benchmark.

Synthetic 2-byte signals only; no original DoorKey episodes.
Every learner receives the same eight action/reward observations; evaluation
withholds reward and uses unseen nuisance bytes.
"""
import json
from learned_byte_cells import LearnedByteCells
from feature_eligibility_cells import FeatureEligibilityCells
from public_transition_planner import PublicTransitionPlanner

def run():
    learners = {
        "learned_byte": LearnedByteCells(feature_positions=2),
        "fixed_prefix": FeatureEligibilityCells(feature_bytes=1),
        "tabular": PublicTransitionPlanner(),
    }
    training = []
    for nuisance in (b"x", b"y"):
        for signal, correct in ((b"A", 1), (b"B", 0)):
            for action in (0, 1):
                training.append((nuisance+signal+b"-train", action, int(action == correct)))
    for frame, action, reward in training:
        for learner in learners.values():
            learner.observe(frame, [0, 1])
            learner.learn(action, b"terminal", reward, True)
    holdout = [(b"zA-unseen", 1), (b"zB-unseen", 0),
               (b"wA-unseen", 1), (b"wB-unseen", 0)]
    results = {}
    for name, learner in learners.items():
        decisions = []
        for frame, expected in holdout:
            learner.observe(frame, [0, 1])
            action = learner.choose(horizon=1) if name == "tabular" else learner.choose()
            decisions.append({"action": action, "correct": int(action == expected)})
        results[name] = {"fit_observations": len(training), "holdout_successes":
                         sum(d["correct"] for d in decisions), "holdout_total": len(decisions),
                         "decisions": decisions}
    return {"selected_position": learners["learned_byte"].feature_position,
            "results": results,
            "limitations": "Synthetic two-position representation; balanced matched FIT; no independent-world transfer"}

if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True))
