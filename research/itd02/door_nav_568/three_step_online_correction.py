"""Online correction trial: detect and repair a wrong three-step prediction.

FIT intervention changes the causal first-hop mapping only for one unfamiliar
public subfamily. The agent sees its own action -> next-public observation.
No regime ID, hidden outcome, scripted corrective action, or original episodes.
"""
import json
from three_step_feature_cells import ThreeStepFeatureCells
from public_transition_planner import PublicTransitionPlanner
from test_three_step_feature_cells import fit

def run():
    native = ThreeStepFeatureCells(positions=2, capacity=128)
    exact = PublicTransitionPlanner()
    fit(native, exact)
    probe = b"zA-reversed"
    native.observe(probe, [0, 1])
    before = native.choose(horizon=3)
    # Environment actually reversed only this public subfamily; learn from
    # both physical action interventions with successor observations.
    for _ in range(12):
        for action, successor in ((1, b"D2-intermediate"),
                                  (0, b"M1-intermediate")):
            native.observe(probe, [0, 1])
            native.learn(action, successor, 0, False)
    native.observe(probe, [0, 1])
    after = native.choose(horizon=3)
    native.observe(b"xA-retention", [0, 1])
    retained = native.choose(horizon=3)
    exact.observe(probe, [0, 1])
    baseline = exact.choose(horizon=3)
    return {
        "before": before,
        "after": after,
        "expected_repaired_action": 0,
        "other_family_action": retained,
        "expected_other_family_action": 1,
        "conventional_exact_state_action": baseline,
        "intervention_actions": 24,
        "retained_fit_examples": len(native.model.examples),
        "max_examples": native.model.capacity,
        "feature_position": native.model.selected_position,
        "scope": "Source-free synthetic reversal on held-out public subfamily",
    }

if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True))
