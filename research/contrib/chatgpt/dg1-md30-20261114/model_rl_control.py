"""MD30 conventional empirical model-based RL control, synthetic only.

Learns a categorical transition/reward model from physically charged public
actions. A finite-horizon Bellman one-probe backup selects information-gathering
actions; it never clones the physical world or reads hidden causal structure.
"""
from collections import Counter, defaultdict
import json
import math
import time
from pathlib import Path

from bayesian_control import ALL_ACTIONS, TOY_TRANSFER, TRAIN_SEEDS
from structural_catalog import TRANSFER_MOTIFS, synthetic_world
from structural_rewire import digest

ROOT = Path(__file__).resolve().parent
LOCK = json.loads((ROOT / "conventional_controls_lock.json").read_text("utf-8"))
CFG = LOCK["model_based_rl"]
assert LOCK["schema"] == "yggdrasil.dg1-md30-recurrent-rl-controls-lock.v1"
ACTION_INDEX = {action: i for i, action in enumerate(ALL_ACTIONS)}
PRIOR = CFG["smoothing_strength"]
TOP_K = CFG["top_outcomes_per_probe"]


def state_key(sensor):
    if len(sensor) != 6:
        raise AssertionError("MD30_RL_BAD_PUBLIC_SENSOR")
    return tuple(int(v) for v in sensor[2:6])


class EmpiricalModelBasedRL:
    def __init__(self):
        self.cells = defaultdict(Counter)
        self.global_cells = defaultdict(Counter)
        self.fitted_steps = 0
        self.inference_calls = 0
        self.metrics = None

    def fit(self, sessions):
        n = LOCK["cohorts"]["fit_episodes"]
        if len(sessions) != len(TRAIN_SEEDS) or self.fitted_steps:
            raise AssertionError("MD30_RL_TRAIN_COHORT_OR_REUSE_DRIFT")
        for episode in sessions[:n]:
            for phase, rows in enumerate(episode):
                sensor = (0,) * 6
                for row in rows:
                    action = row["action"]
                    key = ACTION_INDEX[(action["node"], action["value"])]
                    response = tuple(row["sensor_vector"])
                    local = (phase, state_key(sensor), key)
                    global_key = (phase, key)
                    self.cells[local][response] += 1
                    self.global_cells[global_key][response] += 1
                    self.fitted_steps += 1
                    sensor = response
        if self.fitted_steps != LOCK["cohorts"]["fit_charged_actions"]:
            raise AssertionError("MD30_RL_PHYSICAL_TRAIN_BUDGET_DRIFT")
        logloss = []
        for episode in sessions[n:]:
            for phase, rows in enumerate(episode):
                sensor = (0,) * 6
                for row in rows:
                    action = row["action"]
                    key = ACTION_INDEX[(action["node"], action["value"])]
                    pred = dict(self.predict(phase, sensor, key))
                    got = tuple(row["sensor_vector"])
                    # The model is finite-table and may assign zero probability
                    # to a never-observed vector. Explicit fixed floor reported.
                    logloss.append(-math.log(max(pred.get(got, 0.0), 1e-8)))
                    sensor = got
        val = math.fsum(logloss) / len(logloss)
        self.metrics = {
            "fit_episodes": n,
            "validation_episodes": LOCK["cohorts"]["validation_episodes"],
            "fitted_charged_actions": self.fitted_steps,
            "fitted_local_state_action_cells": len(self.cells),
            "fitted_backoff_action_cells": len(self.global_cells),
            "validation_categorical_logloss": round(val, 8),
        }
        if not math.isfinite(val) or not self.global_cells:
            raise AssertionError("MD30_RL_MODEL_NO_FIT")
        return self

    def predict(self, phase, sensor, key):
        self.inference_calls += 1
        state = state_key(sensor)
        local = self.cells.get((phase, state, key), Counter())
        global_counts = self.global_cells.get((phase, key), Counter())
        if not global_counts:
            global_counts = Counter({(0, 0, 0, 0, 0, 0): 1,
                                     (0, 0, 0, 0, 0, 1): 1})
        n = sum(local.values())
        ng = sum(global_counts.values())
        w = n / (n + PRIOR) if n else 0.0
        outcomes = set(local) | set(global_counts)
        table = []
        for response in sorted(outcomes):
            p = (w * local[response] / n if n else 0.0)
            p += (1 - w) * global_counts[response] / ng
            if p > 0:
                table.append((response, p))
        total = math.fsum(p for _, p in table)
        if abs(total - 1.0) > 1e-9:
            raise AssertionError("MD30_RL_TRANSITIONS_NOT_NORMALIZED")
        return tuple(table)

    def expected_reward(self, phase, sensor, node):
        distribution = self.predict(phase, sensor, ACTION_INDEX[(node, 1)])
        return math.fsum(p * (0.98 if obs[5] == 1 else -0.52)
                         for obs, p in distribution)

    def choose(self, obs):
        if obs["phase"] not in (0, 1):
            raise AssertionError("MD30_RL_FINISHED")
        phase = obs["phase"]
        sensor = tuple(obs["sensor_vector"])
        available = tuple(i for i in (0, 1) if obs["actuator_availability"][i])
        values = {a: self.expected_reward(phase, sensor, a) for a in available}
        choice = max(available, key=lambda a: (values[a], -a))
        base = values[choice]
        probes_spent = sum(
            row["phase"] == phase and row["action"]["kind"] == "diagnostic"
            for row in obs["charged_history"])
        if (probes_spent < CFG["max_planned_diagnostics_per_stage"] and
                obs["remaining_diagnostics"] > 0):
            best_gain, best_probe = 0.0, None
            for node in obs["diagnostic_nodes"]:
                for value in (0, 1):
                    dist = sorted(self.predict(phase, sensor,
                        ACTION_INDEX[(node, value)]),
                        key=lambda pair: (-pair[1], pair[0]))[:TOP_K]
                    total = math.fsum(p for _, p in dist)
                    # Truncated empirical branching is an approximation,
                    # never an uncharged query against physical world.
                    expected = math.fsum(
                        (p / total) *
                        max(self.expected_reward(phase, downstream, a)
                            for a in available)
                        for downstream, p in dist)
                    gain = expected - base - 0.05
                    if gain > best_gain + 1e-12:
                        best_gain, best_probe = gain, (node, value)
            if best_probe is not None:
                return {"kind": "diagnostic", "node": best_probe[0],
                        "value": best_probe[1]}
        return {"kind": "actuator", "node": choice, "value": 1}

    def checkpoint(self):
        if self.metrics is None:
            raise AssertionError("MD30_RL_UNTRAINED")
        return {"schema": "md30.empirical-model-based-rl.v1",
                "local": [[phase, list(state), action,
                           [[list(response), count]
                            for response, count in sorted(counter.items())]]
                          for (phase, state, action), counter
                          in sorted(self.cells.items())],
                "backoff": [[phase, action,
                             [[list(response), count]
                              for response, count in sorted(counter.items())]]
                            for (phase, action), counter
                            in sorted(self.global_cells.items())],
                "validation_logloss": self.metrics["validation_categorical_logloss"]}


def empirical_rl_toy_control(sessions):
    start = time.process_time()
    learner = EmpiricalModelBasedRL().fit(sessions)
    fit_cpu = time.process_time() - start
    rewards, receipts = [], []
    charged = probes = 0
    begin = time.process_time()
    for seed in TOY_TRANSFER:
        motif = TRANSFER_MOTIFS[(seed - TOY_TRANSFER[0]) % 3]
        world = synthetic_world(seed, motif, rewire=(seed % 2 == 0))
        while True:
            obs = world.observe()
            if obs["phase"] == "done":
                break
            action = learner.choose(obs)
            later, reward, done = world.step(action)
            if later["charged_history"][-1]["action"] != action:
                raise AssertionError("MD30_RL_UNPAID_PUBLIC_ACTION")
            charged += 1
            probes += int(action["kind"] == "diagnostic")
            if done:
                break
        rec = world.receipt()
        rewards.append(rec["net_utility"])
        receipts.append(rec["physical_sha256"])
    return {
        "model": "empirical_model_based_rl",
        "train": dict(learner.metrics, training_cpu_seconds=round(fit_cpu, 4)),
        "checkpoint_sha256": digest(learner.checkpoint()),
        "toy_episodes": len(rewards),
        "toy_mean_net_utility": round(math.fsum(rewards) / len(rewards), 6),
        "toy_charged_steps": charged, "toy_charged_probes": probes,
        "physical_receipts_sha256": digest(receipts),
        "inference_cpu_seconds": round(time.process_time() - begin, 4),
    }
