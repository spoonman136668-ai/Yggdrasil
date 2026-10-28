"""Controlled public intervention fixture for causal action discrimination.

A/B comparisons are paired by public starting state and exogenous trial index.
No original DoorKey source or hidden-state learner inputs.
"""
from eligibility_local_cells import EligibilityLocalCells

def paired_interventions(n=8):
    if type(n) is not int or n < 2 or n > 64:
        raise ValueError("INVALID_TRIAL_COUNT")
    results = []
    for trial in range(n):
        for action in (0, 1):
            # Fixed synthetic intervention: only action 0 unlocks a later
            # positive outcome. Same trial index gives matched nuisance.
            reward = int(action == 0)
            results.append((trial, action, reward))
    return results

def compare():
    learner = EligibilityLocalCells()
    observations = paired_interventions()
    for trial, action, reward in observations:
        learner.observe(b"start", [0, 1])
        learner.learn(action, b"middle", 0, False)
        learner.observe(b"middle", [2])
        learner.learn(2, b"goal" if reward else b"dead_end", reward, True)
    learner.observe(b"start", [0, 1])
    selected = learner.choose()
    arm0 = sum(r for _, a, r in observations if a == 0)
    arm1 = sum(r for _, a, r in observations if a == 1)
    return {"trials_per_arm": len(observations)//2,
            "arm0_successes": arm0, "arm1_successes": arm1,
            "selected_action": selected,
            "intervention_effect": (arm0-arm1)/(len(observations)//2)}
