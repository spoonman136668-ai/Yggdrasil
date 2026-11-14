"""Conventional MD30 Bayesian causal-response control. Toy engineering only.

The controller never reads graph objects or source seed. Hypotheses are drawn
from a universal small-DAG grammar independent of the six heldout motifs.
Training only consumes paid World.step public traces, and stage-boundary
change-point uncertainty is carried as a probabilistic posterior mixture.
No official MD30 seeds or original cohorts are accepted in this module.
"""
import hashlib
import itertools
import json
import math
import random
import time
from pathlib import Path

from structural_rewire import Graph, Node, canonical, digest
from structural_catalog import TRAIN_MOTIFS, TRANSFER_MOTIFS, synthetic_world

ROOT = Path(__file__).resolve().parent
LOCK = json.loads((ROOT / "control_preflight_lock.json").read_text("utf-8"))
assert LOCK["schema"] == "yggdrasil.dg1-md30-bayes-control-toy-lock.v1"
assert LOCK["status"] == "PREREGISTERED_SYNTHETIC_DEVELOPMENT_ONLY__NO_OFFICIAL_COHORT"
COUNT = 768
TRAIN_SEEDS = tuple(range(3301, 3541))
TOY_TRANSFER = tuple(range(5301, 5361))
ALL_ACTIONS = ((0, 1), (1, 1)) + tuple(
    (n, v) for n in (2, 3, 4) for v in (0, 1))
ACTUATOR_INDEX = (0, 1)
PROBE_INDICES = tuple(range(2, 8))
ERROR = 0.12
EM_ROUNDS = 3
SMOOTH = 0.05
CHANGE = 0.5
SIGNATURE_SEED = 31030
MAX_DRAW = 60000


def build_hypotheses():
    rng = random.Random(SIGNATURE_SEED)
    unique = {}
    for _ in range(MAX_DRAW):
        nodes = []
        for idx in range(2, 6):
            arity = 1 if rng.randrange(3) == 0 else 2
            parents = tuple(sorted(rng.sample(range(idx), arity)))
            gate = "PASS" if arity == 1 else ("AND", "OR", "XOR")[rng.randrange(3)]
            invert = tuple(rng.randrange(2) for _ in range(arity))
            nodes.append(Node(parents, gate, invert))
        graph = Graph(tuple(nodes))
        if graph.respond((0, 0)) != (0,) * 6:
            continue
        signature = tuple(graph.respond((0, 0), action) for action in ALL_ACTIONS)
        if (signature[0][5], signature[1][5]) not in ((0, 1), (1, 0)):
            continue
        unique.setdefault(signature, None)
        if len(unique) == COUNT:
            break
    if len(unique) != COUNT:
        raise AssertionError("MD30_HYPOTHESIS_CAPACITY_NOT_MET")
    return tuple(unique)


def paid_training_episodes():
    """Trainer's access to synthetic_world is restricted to creating new runs.

    Returned rows contain only charged public action/response traces; this
    function never returns private Graph objects or hidden future state.
    """
    sessions = []
    physical = hashlib.sha256()
    steps = 0
    for seed in TRAIN_SEEDS:
        motif = TRAIN_MOTIFS[(seed - TRAIN_SEEDS[0]) % len(TRAIN_MOTIFS)]
        env = synthetic_world(seed, motif, rewire=(seed % 2 == 0))
        stages = []
        for stage in range(2):
            one = []
            for node, value in (
                (2, (seed + stage) % 2),
                (3, (seed // 2 + stage) % 2),
                (4, (seed // 4 + stage) % 2),
            ):
                action = {"kind": "diagnostic", "node": node, "value": value}
                obs, reward, done = env.step(action)
                if done or reward != -0.05:
                    raise AssertionError("MD30_TRAIN_UNCHARGED_PROBE")
                one.append(obs["charged_history"][-1])
            action = {"kind": "actuator", "node": (seed + stage) % 2, "value": 1}
            obs, reward, done = env.step(action)
            if done != (stage == 1) or reward not in (0.98, -0.52):
                raise AssertionError("MD30_TRAIN_ACTUATOR_CUSTODY")
            one.append(obs["charged_history"][-1])
            stages.append(tuple(one))
        receipt = env.receipt()
        if receipt["paid_steps"] != 8:
            raise AssertionError("MD30_TRAIN_STEPS_MISMATCH")
        physical.update((receipt["physical_sha256"] + "\n").encode("ascii"))
        steps += receipt["paid_steps"]
        sessions.append(tuple(stages))
    if steps != 1920 or len(sessions) != 240:
        raise AssertionError("MD30_TRAIN_BUDGET_MISMATCH")
    return tuple(sessions), {"charged_episodes": len(sessions),
                             "charged_steps": steps, "physical_sha256": physical.hexdigest()}


def _log_likelihood(signature, rows):
    mismatches = 0
    for row in rows:
        action = row["action"]
        key = (action["node"], action["value"])
        idx = ALL_ACTIONS.index(key)
        pred = signature[idx]
        got = row["sensor_vector"]
        mismatches += sum(a != b for a, b in zip(pred, got))
    return mismatches * math.log(ERROR / (1.0 - ERROR))


def normalize(scores):
    if not scores:
        raise AssertionError("MD30_EMPTY_POSTERIOR")
    m = max(scores)
    vals = [math.exp(x - m) for x in scores]
    total = math.fsum(vals)
    if not total or not math.isfinite(total):
        raise AssertionError("MD30_BAYES_POSTERIOR_NAN")
    return tuple(x / total for x in vals)


class BayesianGraphControl:
    def __init__(self, hypotheses, prior=None):
        if len(hypotheses) != COUNT:
            raise AssertionError("MD30_BAYES_INVALID_CAPACITY")
        self.hypotheses = hypotheses
        self.prior = tuple(prior) if prior is not None else (1 / COUNT,) * COUNT
        self.weights = self.prior
        self.phase = 0
        self.probes = 0
        self.model_calls = 0
        self._verify_weights(self.prior)

    @staticmethod
    def _verify_weights(values):
        if any((not math.isfinite(x)) or x < 0 for x in values):
            raise AssertionError("MD30_INVALID_BAYES_WEIGHTS")
        if abs(math.fsum(values) - 1) > 1e-9:
            raise AssertionError("MD30_UNNORMALIZED_POSTERIOR")

    def set_prior(self, new):
        self.prior = tuple(new)
        self.weights = self.prior
        self._verify_weights(self.prior)

    def fit(self, sessions):
        if len(sessions) != len(TRAIN_SEEDS):
            raise AssertionError("MD30_TRAIN_SESSIONS_NOT_FROZEN")
        # EM-like empirical Bayes: each charged stage segment offers
        # exactly four publicly observed actions and sensor consequences.
        stage_rows = [rows for episode in sessions for rows in episode]
        prior = self.prior
        for _ in range(EM_ROUNDS):
            sums = [0.0] * COUNT
            for rows in stage_rows:
                scores = [math.log(max(w, 1e-300)) +
                          _log_likelihood(signature, rows)
                          for w, signature in zip(prior, self.hypotheses)]
                posterior = normalize(scores)
                for i, p in enumerate(posterior):
                    sums[i] += p
            raw = [x / len(stage_rows) for x in sums]
            prior = tuple(round((1 - SMOOTH) * p + SMOOTH / COUNT, 13)
                          for p in raw)
            total = math.fsum(prior)
            prior = tuple(x / total for x in prior)
        self.set_prior(prior)
        return self

    def posterior_step(self, action, public_receipt):
        if not isinstance(public_receipt, dict) or set(public_receipt) != {
            "phase", "action", "sensor_vector", "reward"}:
            raise AssertionError("MD30_BAYES_REQUIRE_CHARGED_PUBLIC_RECEIPT")
        if public_receipt["action"] != action or public_receipt["phase"] != self.phase:
            raise AssertionError("MD30_BAYES_ACTION_RECEIPT_MISMATCH")
        idx = ALL_ACTIONS.index((action["node"], action["value"]))
        values = public_receipt["sensor_vector"]
        scores = [
            math.log(max(p, 1e-300)) +
            sum(a != b for a, b in zip(sig[idx], values)) *
            math.log(ERROR / (1 - ERROR))
            for p, sig in zip(self.weights, self.hypotheses)
        ]
        self.weights = normalize(scores)
        self._verify_weights(self.weights)
        if action["kind"] == "actuator":
            if self.phase == 0:
                self.weights = tuple(
                    CHANGE * old + (1 - CHANGE) * new
                    for old, new in zip(self.weights, self.prior))
            self.phase += 1
            self.probes = 0
        else:
            self.probes += 1

    def _actuator_probability(self, posterior):
        return [math.fsum(w for w, sig in zip(posterior, self.hypotheses)
                          if sig[act][5] == 1) for act in ACTUATOR_INDEX]

    def choose(self, obs):
        """Public observation only; no graph, generator or seed input."""
        if obs["phase"] != self.phase or obs["phase"] == "done":
            raise AssertionError("MD30_BAYES_PHASE_DRIFT")
        p = self._actuator_probability(self.weights)
        available = obs["actuator_availability"]
        baseline = max(p[i] for i in (0, 1) if available[i])
        best_action = None
        best_gain = 0.0
        self.model_calls += 1
        if self.probes < min(3, obs["remaining_diagnostics"]):
            for idx in PROBE_INDICES:
                node, value = ALL_ACTIONS[idx]
                if node not in obs["diagnostic_nodes"]:
                    continue
                # Predicted observations are INTERNAL model simulations, never
                # uncharged physical world steps or environment clones.
                outcomes = {}
                for w, sig in zip(self.weights, self.hypotheses):
                    key = sig[idx]
                    row = outcomes.setdefault(key, [0.0, 0.0])
                    row[0] += w if sig[0][5] else 0.0
                    row[1] += w if sig[1][5] else 0.0
                after = math.fsum(max(row) for row in outcomes.values())
                gain = 1.5 * (after - baseline) - 0.05
                if gain > best_gain + 1e-12:
                    best_action = {"kind": "diagnostic", "node": node,
                                   "value": value}
                    best_gain = gain
        if best_action is not None:
            return best_action
        action = max((i for i in (0, 1) if available[i]),
                     key=lambda i: (p[i], -i))
        return {"kind": "actuator", "node": action, "value": 1}

    def checkpoint(self):
        return {"schema": "md30.bayesian-causal-response.v1",
                "hypothesis_count": len(self.hypotheses),
                "signature_sha256": digest(self.hypotheses),
                "prior": [round(x, 13) for x in self.prior],
                "change": CHANGE, "em_rounds": EM_ROUNDS}


def synthetic_control_preflight():
    begin = time.process_time()
    hypotheses = build_hypotheses()
    data, training_custody = paid_training_episodes()
    control = BayesianGraphControl(hypotheses).fit(data)
    uniform = (1.0 / COUNT,) * COUNT
    if max(abs(a - b) for a, b in zip(control.prior, uniform)) < 1e-8:
        raise AssertionError("MD30_BAYES_LEARNING_NO_UPDATE")
    checkpoint = control.checkpoint()
    checkpoint_sha = digest(checkpoint)
    fit_cpu = time.process_time() - begin
    toy_rewards = []
    blind_rewards = []
    toy_receipts = []
    charged = probes = 0
    for seed in TOY_TRANSFER:
        motif = TRANSFER_MOTIFS[(seed - TOY_TRANSFER[0]) % 3]
        world = synthetic_world(seed, motif, rewire=(seed % 2 == 0))
        learner = BayesianGraphControl(hypotheses, control.prior)
        while True:
            obs = world.observe()
            if obs["phase"] == "done":
                break
            action = learner.choose(obs)
            new, reward, done = world.step(action)
            learner.posterior_step(action, new["charged_history"][-1])
            charged += 1
            probes += int(action["kind"] == "diagnostic")
            if done:
                break
        rec = world.receipt()
        toy_rewards.append(rec["net_utility"])
        toy_receipts.append(rec["physical_sha256"])
        baseline = synthetic_world(seed, motif, rewire=(seed % 2 == 0))
        baseline.step({"kind": "actuator", "node": 0, "value": 1})
        baseline.step({"kind": "actuator", "node": 0, "value": 1})
        blind_rewards.append(baseline.receipt()["net_utility"])
    return {
        "schema": "md30.synthetic-bayes-control-preflight.v1",
        "status": "TOY_CONTROL_DEVELOPMENT_ONLY__NOT_SCIENTIFIC_PASS",
        "official_first_use": False,
        "synthetic_training_seed_range": [TRAIN_SEEDS[0], TRAIN_SEEDS[-1]],
        "synthetic_transfer_seed_range": [TOY_TRANSFER[0], TOY_TRANSFER[-1]],
        "physical_training": training_custody,
        "checkpoint_sha256": checkpoint_sha,
        "hypothesis_count": COUNT,
        "prior_max_deviation_uniform": round(
            max(abs(a - b) for a, b in zip(control.prior, uniform)), 10),
        "toy_episodes": len(toy_rewards),
        "toy_mean_net_utility": round(math.fsum(toy_rewards) / len(toy_rewards), 6),
        "blind_mean_net_utility": round(math.fsum(blind_rewards) / len(blind_rewards), 6),
        "toy_charged_steps": charged,
        "toy_charged_probes": probes,
        "toy_receipts_sha256": digest(toy_receipts),
        "whole_process_fit_cpu_seconds": round(fit_cpu, 4),
        "limits": "Only one conventional control; no recurrent/RL convergence or matched-compute scientific claim."
    }


if __name__ == "__main__":
    print(canonical(synthetic_control_preflight()))
