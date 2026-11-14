"""DG1-MD23 registered first-use study. NO registered-seed call on import.

Public partial observations and physical env.step actions only. Entry point is
guarded by the exact draft-PR opening GitHub Actions context. Sealed original
outcomes are emitted once to the workflow artifacts; no postresult tuning.
"""
import hashlib
import importlib.util
import json
import os
import statistics
from pathlib import Path

SOURCE = Path(__file__).with_name("md23.py")
spec = importlib.util.spec_from_file_location("md23_registered_core", str(SOURCE))
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)
m = d.m

SCHEMA = "yggdrasil.dg1-md23-original.v1"
TRAIN_DOOR = tuple(range(980001, 980025))
TRAIN_BOX = tuple(range(981001, 981025))
INTERFERENCE = tuple(range(982001, 982013))
COLD = tuple(range(983001, 983013))
SIZE = tuple(range(984001, 984013))
BOX = tuple(range(985001, 985013))
INTERFERENCE_ENV = "MiniGrid-Empty-6x6-v0"
SIZE_ENV = "MiniGrid-DoorKey-8x8-v0"
FIRSTUSE_CONTEXT = "MD23_PR_OPENED_FROZEN_SOURCE_ONCE"


def frozen_identity():
    d.verify_prereg()
    p = json.loads(Path(__file__).with_name("prereg.json").read_text())
    if (p["frozen_design"]["train_door"] !=
            "MiniGrid-DoorKey-6x6-v0 seeds 980001..980024 (24)"
            or p["frozen_design"]["train_box"] !=
            "MiniGrid-UnlockPickup-v0 seeds 981001..981024 (24)"
            or p["frozen_design"]["interference"] !=
            "MiniGrid-Empty-6x6-v0 seeds 982001..982012 (12)"
            or p["frozen_design"]["cold_before_and_after"] !=
            "MiniGrid-DoorKey-6x6-v0 seeds 983001..983012 (12 per arm each occasion)"
            or p["frozen_design"]["heldout_size"] !=
            "MiniGrid-DoorKey-8x8-v0 seeds 984001..984012 (12 per arm)"
            or p["frozen_design"]["heldout_box"] !=
            "MiniGrid-UnlockPickup-v0 seeds 985001..985012 (12 per arm)"
            or p["frozen_design"]["maximum_charged_env_steps"] != 89088):
        raise AssertionError("MD23_REGISTERED_PROTOCOL_DRIFT")
    cohorts = (TRAIN_DOOR, TRAIN_BOX, INTERFERENCE, COLD, SIZE, BOX)
    all_seeds = [seed for group in cohorts for seed in group]
    if len(all_seeds) != len(set(all_seeds)):
        raise AssertionError("MD23_COHORT_INTERSECTION")
    if len(TRAIN_DOOR) != 24 or len(TRAIN_BOX) != 24 or any(
            len(x) != 12 for x in (INTERFERENCE, COLD, SIZE, BOX)):
        raise AssertionError("MD23_COHORT_COUNTS")
    if set(all_seeds) & set(d.TOY_SEEDS):
        raise AssertionError("MD23_TOY_PRIMARY_OVERLAP")
    return p


def version_fence():
    import minigrid
    import gymnasium
    import numpy
    if (minigrid.__version__, gymnasium.__version__, numpy.__version__) != (
            "3.2.0", "1.4.0", "2.3.4"):
        raise AssertionError("MD23_LOCKED_DEPENDENCY_DRIFT")


def original_teacher(env_name, seed):
    """One real physical public-observation-only rewarded training episode."""
    model = d.GraphPolicy("fixed_scripted", probe_first=True)
    ep = m.make_trace(env_name, seed, model)
    if not 0 < len(ep["transitions"]) == ep["steps"] <= 256:
        raise AssertionError("MD23_UNCHARGED_TRAIN_ACTION")
    ep["no_key_probe"] = model.episode_failed_probes
    ep["with_key_unlock"] = model.episode_successful_unlocks
    ep["rewarded_box"] = int(model.episode_rewarded_box)
    return ep


def stripped(ep):
    return {key: value for key, value in ep.items()
            if key not in ("transitions", "cpu_ns")}


def teacher_train(agents, env_name, seeds, stage):
    records = []
    goals = paid = no_key = unlocks = boxes = 0
    for seed in seeds:
        ep = original_teacher(env_name, seed)
        d.train_shared(agents, ep)
        goals += ep["success"]
        paid += ep["steps"]
        no_key += ep["no_key_probe"]
        unlocks += ep["with_key_unlock"]
        boxes += ep["rewarded_box"]
        records.append(stripped(ep))
    return {"stage": stage, "environment": env_name, "episodes": records,
            "count": len(records), "goals": goals, "paid_actions": paid,
            "no_key_probes": no_key, "with_key_unlocks": unlocks,
            "rewarded_boxes": boxes}


def independent_scoring(agents, env_name, seeds, phase):
    """Evaluation trajectories are independent; no persistent training updates."""
    frozen = {name: d.save(model) for name, model in agents.items()}
    result = {}
    cpu = {}
    paid = 0
    for name, model in agents.items():
        events = []
        nanos = 0
        for seed in seeds:
            ep = m.make_trace(env_name, seed, model)
            if not 0 < ep["steps"] <= 256:
                raise AssertionError("MD23_UNCHARGED_EVAL_ACTION")
            paid += ep["steps"]
            nanos += ep["cpu_ns"]
            receipt = stripped(ep)
            receipt["learned_edges_used"] = int(getattr(model, "selected_learned_edge", False))
            receipt["edge_decisions"] = getattr(model, "edge_uses", 0)
            events.append(receipt)
        if d.save(model) != frozen[name]:
            raise AssertionError("MD23_HELDOUT_PERSISTENT_WEIGHT_UPDATE_" + name)
        cpu[name] = nanos
        result[name] = {"goal_count": sum(e["success"] for e in events),
                        "mean_discounted_reward": round(
                            statistics.mean(e["discounted_reward"] for e in events), 8),
                        "mean_paid_steps": round(statistics.mean(e["steps"] for e in events), 8),
                        "learned_edge_use_episodes": sum(
                            e["learned_edges_used"] for e in events),
                        "seeds": list(seeds),
                        "episodes": events,
                        "charged_actions": sum(e["steps"] for e in events),
                        "decision_cpu_ns": nanos}
    if paid != sum(x["charged_actions"] for x in result.values()):
        raise AssertionError("MD23_ACTION_LEDGER_DRIFT")
    return {"phase": phase, "environment": env_name, "count": len(seeds)*len(d.ARMS),
            "charged_actions": paid, "by_arm": result}


def seed_wins(result, challenger="causal_graph", control="shuffled_graph"):
    def seed_to_reward(name):
        return {x["seed"]: x["discounted_reward"]
                for x in result["by_arm"][name]["episodes"]}
    left, right = seed_to_reward(challenger), seed_to_reward(control)
    if left.keys() != right.keys():
        raise AssertionError("MD23_UNPAIRED_HELDOUT_REWARD")
    return sum(left[s] > right[s] + 1e-8 for s in left)


def return_delta(result, left, right):
    return (result["by_arm"][left]["mean_discounted_reward"] -
            result["by_arm"][right]["mean_discounted_reward"])


def scored_gates(receipt):
    p = frozen_identity()
    t = p["gates"]
    gates = {}
    tr = receipt["training"]
    phase_size = receipt["heldout_size"]
    phase_box = receipt["heldout_box"]
    co = phase_box["by_arm"]["causal_graph"]
    ss = phase_size["by_arm"]["causal_graph"]
    sh = phase_box["by_arm"]["shuffled_graph"]
    s_sh = phase_size["by_arm"]["shuffled_graph"]
    best_box = max(phase_box["by_arm"][k]["mean_discounted_reward"]
                   for k in ("tabular_q", "recurrent_imitation"))
    best_size = max(phase_size["by_arm"][k]["mean_discounted_reward"]
                    for k in ("tabular_q", "recurrent_imitation"))
    gate_cov = t["coverage"]
    gates["trainer_door_goals"] = tr["door"]["goals"] >= gate_cov["trainer_door_official_goals_min"]
    gates["trainer_box_goals"] = tr["box"]["goals"] >= gate_cov["trainer_box_official_goals_min"]
    probes = tr["door"]["no_key_probes"] + tr["box"]["no_key_probes"]
    unlocks = tr["door"]["with_key_unlocks"] + tr["box"]["with_key_unlocks"]
    boxes = tr["box"]["rewarded_boxes"]
    gates["physical_no_key"] = probes >= gate_cov["physical_no_key_door_failures_min"]
    gates["physical_with_key"] = unlocks >= gate_cov["physical_with_key_door_unlocks_min"]
    gates["physical_rewarded_box"] = boxes >= gate_cov["physical_rewarded_box_pickups_min"]
    gates["heldout_box_any_goal"] = sum(x["goal_count"] for x in phase_box["by_arm"].values()) >= gate_cov["heldout_box_goal_events_all_arms_min"]
    gates["heldout_size_any_goal"] = sum(x["goal_count"] for x in phase_size["by_arm"].values()) >= gate_cov["heldout_size_goal_events_all_arms_min"]
    valid_coverage = all(gates.values())
    primary = t["primary"]
    gates["box_causal_goals"] = co["goal_count"] >= primary["heldout_box_causal_goals_min"]
    gates["box_sham_margin"] = return_delta(phase_box, "causal_graph", "shuffled_graph") >= primary["heldout_box_mean_discounted_reward_advantage_over_sham_min"] - 1e-8
    gates["box_trained_margin"] = co["mean_discounted_reward"] - best_box >= primary["heldout_box_reward_advantage_over_best_trained_Q_or_RNN_min"] - 1e-8
    gates["box_strict_wins"] = seed_wins(phase_box) >= primary["heldout_box_strict_seed_wins_over_sham_min"]
    gates["size_causal_goals"] = ss["goal_count"] >= primary["heldout_size_causal_goals_min"]
    gates["size_sham_margin"] = return_delta(phase_size, "causal_graph", "shuffled_graph") >= primary["heldout_size_sham_reward_advantage_min"] - 1e-8
    gates["size_trained_nonregression"] = ss["mean_discounted_reward"] >= best_size - primary["heldout_size_vs_best_trained_return_allowed_deficit_max"] - 1e-8
    gates["size_seed_wins"] = seed_wins(phase_size) >= primary["heldout_size_strict_seed_wins_over_sham_min"]
    prior = receipt["cold_before"]["by_arm"]["causal_graph"]["goal_count"]
    post = receipt["cold_after"]["by_arm"]["causal_graph"]["goal_count"]
    gates["cold_retention"] = prior-post <= primary["cold_after_vs_before_causal_goal_loss_max"]
    gates["box_learned_edge_use"] = co["learned_edge_use_episodes"] >= primary["actual_learned_graph_edge_use_min_heldout_box"]
    gates["size_learned_edge_use"] = ss["learned_edge_use_episodes"] >= primary["actual_learned_graph_edge_use_min_heldout_size"]
    checkpoints = receipt["checkpoints"]
    gates["bounded_checkpoint"] = all(x["bytes"] <= primary["checkpoint_bytes_max"] for x in checkpoints.values())
    gates["trained_conventional"] = (
        receipt["trained_counts"]["tabular_q"] > 0 and
        receipt["trained_counts"]["recurrent_imitation"] > 0)
    gates["paid_action_budget"] = receipt["charged_actions"] <= 89088
    gates["episode_budget"] = receipt["episode_count"] == 348
    cpu = sum(x["by_arm"]["causal_graph"]["decision_cpu_ns"]
              for x in (phase_size, phase_box))
    conventional = sum(x["by_arm"]["recurrent_imitation"]["decision_cpu_ns"]
                       for x in (phase_size, phase_box))
    ratio = round(cpu / max(1, conventional), 6)
    gates["cpu_to_trained_recurrent"] = ratio <= primary["cpu_ratio_to_trained_recurrent_max"]
    required_primary = tuple(k for k in gates if k not in (
        "trainer_door_goals", "trainer_box_goals", "physical_no_key",
        "physical_with_key", "physical_rewarded_box", "heldout_box_any_goal",
        "heldout_size_any_goal"))
    accepted_dev = valid_coverage and all(gates[k] for k in required_primary)
    if not valid_coverage:
        classification = "INVALID_TASK_COVERAGE"
    elif accepted_dev:
        classification = "DEVELOPMENT_SIGNAL_ONLY"
    elif (co["goal_count"] >= 8 or return_delta(
            phase_box, "causal_graph", "shuffled_graph") >= 0.03 - 1e-8):
        classification = "MIXED_DEV"
    else:
        classification = "NEGATIVE_DEV"
    return classification, gates, ratio


def toy_scoring_preflight():
    """Exercises training, evaluation freeze, checkpoint and paid action ledger
    only on prereg toy seeds; never accesses registered cohorts.
    """
    d.verify_prereg()
    d.validate_toy_seeds((11, 17, 19))
    version_fence()
    agents = {name: d.make_agent(name) for name in d.ARMS}
    teacher_door = teacher_train(agents, d.DOOR_ENV, (11, 17), "toy_door")
    teacher_box = teacher_train(agents, d.BOX_ENV, (11, 17), "toy_box")
    before = {name: d.save(a) for name, a in agents.items()}
    phase = independent_scoring(agents, d.BOX_ENV, (19,), "toy_eval")
    if any(d.save(agent) != before[name] for name, agent in agents.items()):
        raise AssertionError("MD23_TOY_SCORING_CHECKPOINT_DRIFT")
    if not teacher_box["rewarded_boxes"] or not teacher_door["goals"]:
        raise AssertionError("MD23_TOY_SCORING_TRAIN_COVERAGE")
    return {"toy_only": True, "train_steps": teacher_box["paid_actions"] +
            teacher_door["paid_actions"], "charged_eval_steps": phase["charged_actions"],
            "actions": {k: {"goals": a["goal_count"],
                            "edge_used": a["learned_edge_use_episodes"]}
                        for k, a in phase["by_arm"].items()}}


def registered_firstuse():
    if os.environ.get("MD23_FIRST_USE") != FIRSTUSE_CONTEXT:
        raise PermissionError("MD23_REGISTERED_FIRST_USE_CONTEXT_REQUIRED")
    frozen_identity()
    version_fence()
    agents = {name: d.make_agent(name) for name in d.ARMS}
    train_door = teacher_train(agents, d.DOOR_ENV, TRAIN_DOOR, "door")
    train_box = teacher_train(agents, d.BOX_ENV, TRAIN_BOX, "box")
    cold_before = independent_scoring(agents, d.DOOR_ENV, COLD, "cold_before")
    interference = teacher_train(agents, INTERFERENCE_ENV, INTERFERENCE, "interference")
    cold_after = independent_scoring(agents, d.DOOR_ENV, COLD, "cold_after")
    size = independent_scoring(agents, SIZE_ENV, SIZE, "heldout_size")
    box = independent_scoring(agents, d.BOX_ENV, BOX, "heldout_box")
    checkpoints = {k: {"sha256": hashlib.sha256(d.save(v)).hexdigest(),
                       "bytes": len(d.save(v))}
                   for k, v in agents.items()}
    charged = sum(x["paid_actions"] for x in (train_door, train_box, interference))
    charged += sum(x["charged_actions"] for x in (cold_before, cold_after, size, box))
    count = 48 + 12 + sum(x["count"] for x in (cold_before, cold_after, size, box))
    if charged > 89088 or count != 348:
        raise AssertionError("MD23_REGISTERED_CHARGED_BUDGET_DRIFT")
    receipt = {"schema": SCHEMA, "exact_parent_sha": d.EXACT_PARENT,
               "frozen_prereg_sha": d.FROZEN_PREREG,
               "registered_first_use": True,
               "training": {"door": train_door, "box": train_box},
               "interference": interference,
               "cold_before": cold_before, "cold_after": cold_after,
               "heldout_size": size, "heldout_box": box,
               "checkpoints": checkpoints,
               "trained_counts": {
                   "tabular_q": agents["tabular_q"].count,
                   "recurrent_imitation": agents["recurrent_imitation"].count},
               "episode_count": count, "charged_actions": charged,
               "native_model_changed": False,
               "scientific_acceptance": "UNVERIFIED"}
    classification, gates, cpu_ratio = scored_gates(receipt)
    receipt.update(classification=classification,
                   primary_pass=(classification == "DEVELOPMENT_SIGNAL_ONLY"),
                   registered_gates=gates, cpu_ratio=cpu_ratio)
    return receipt


if __name__ == "__main__":
    print(m.canon(registered_firstuse()))
