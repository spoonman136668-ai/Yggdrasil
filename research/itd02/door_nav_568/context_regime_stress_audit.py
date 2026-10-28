"""Source-free repeated-regime, context-collision and memory-pressure audit.

No hidden regime labels are provided to either agent: phases select public
interventions in the experiment harness only. Snapshot routes by public byte
and can misroute colliding contexts. This audit deliberately retains negatives.
"""
import json
from context_partitioned_three_step import ContextPartitionedThreeStep
from three_step_feature_cells import ThreeStepFeatureCells
from test_three_step_feature_cells import fit
from public_transition_planner import PublicTransitionPlanner

PROBE = b"zA-reversed"
COLLISION = b"xA-collision"
OLD = b"xA-retention"

def query(agent, frame):
    agent.observe(frame, [0, 1])
    return agent.choose(horizon=3)

def intervene(agent, frame, reverse, repeats=12):
    for _ in range(repeats):
        for action in (0, 1):
            good = (action == (0 if reverse else 1))
            agent.observe(frame, [0, 1])
            agent.learn(action, b"M1-intermediate" if good else b"D2-intermediate", 0, False)

def run(capacity=128):
    agents = {
        "single": ThreeStepFeatureCells(positions=2, capacity=capacity),
        "snapshot": ContextPartitionedThreeStep(positions=2, capacity=capacity),
    }
    controls = {}
    for name, agent in agents.items():
        fit(agent, PublicTransitionPlanner())
        controls[name] = {"A_initial": query(agent, OLD)}
    agents["snapshot"].freeze_boundary()
    for agent in agents.values():
        intervene(agent, PROBE, reverse=True)
        intervene(agent, COLLISION, reverse=True, repeats=2)
    for name, agent in agents.items():
        controls[name]["B_new_context"] = query(agent, PROBE)
        controls[name]["B_colliding_context"] = query(agent, COLLISION)
        controls[name]["B_old_retention"] = query(agent, OLD)
    for agent in agents.values():
        intervene(agent, PROBE, reverse=False)
    for name, agent in agents.items():
        controls[name]["A_return"] = query(agent, PROBE)
        controls[name]["A_old_retention"] = query(agent, OLD)
        controls[name]["examples"] = (agent.stored_examples() if
            isinstance(agent, ContextPartitionedThreeStep)
            else len(agent.model.examples))
        controls[name]["feature_position"] = agent.active.model.selected_position if (
            isinstance(agent, ContextPartitionedThreeStep)) else agent.model.selected_position
    return {
        "agents": controls,
        "expected": {"A_initial": 1, "B_new_context": 0, "B_colliding_context": 0,
                     "B_old_retention": 1, "A_return": 1, "A_old_retention": 1},
        "per_arm_new_context_interventions": 48,
        "per_arm_collision_interventions": 4,
        "snapshot_count": 1,
        "per_compartment_example_limit": capacity,
        "caveat": "Fixed public-byte routing; A/B phase changes are experiment interventions, not learned regime detection.",
    }

if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True))
