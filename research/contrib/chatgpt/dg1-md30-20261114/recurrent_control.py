"""MD30 conventional fully fitted Elman recurrent world-model control.

Non-token continuous recurrent dynamics, *conventional control only*. Trained
with BPTT on the exact precharged synthetic sequences supplied to the Bayesian
control. Neither train/evaluation policy sees private graph objects.
"""
import json
import math
import time
from pathlib import Path

import numpy as np

from bayesian_control import ALL_ACTIONS, TRAIN_SEEDS, TOY_TRANSFER
from structural_catalog import TRAIN_MOTIFS, TRANSFER_MOTIFS, synthetic_world
from structural_rewire import canonical, digest

ROOT = Path(__file__).resolve().parent
LOCK = json.loads((ROOT / "conventional_controls_lock.json").read_text("utf-8"))
CFG = LOCK["recurrent"]
assert LOCK["schema"] == "yggdrasil.dg1-md30-recurrent-rl-controls-lock.v1"
assert LOCK["status"] == "FROZEN_BEFORE_NEW_CONVENTIONAL_CONTROL_SOURCE_OR_TRANSFER_OUTCOMES"
assert CFG["input_width"] == 16 and CFG["hidden_width"] == 32
assert CFG["trainable_parameters"] == 1766
ACTION_INDEX = {a: i for i, a in enumerate(ALL_ACTIONS)}


def encode(sensor, action, stage):
    if tuple(action.values()) == ():
        raise AssertionError("MD30_RNN_INVALID_ACTION")
    key = (action["node"], action["value"])
    index = ACTION_INDEX[key]
    x = np.zeros(16, dtype=np.float64)
    x[index] = 1.0
    x[8:14] = sensor
    x[14 + stage] = 1.0
    return x


def prepare(sessions):
    if len(sessions) != len(TRAIN_SEEDS):
        raise AssertionError("MD30_RNN_NOT_FROZEN_SHARED_CHARGED_DATA")
    inputs = np.empty((len(sessions), 8, 16), dtype=np.float64)
    targets = np.empty((len(sessions), 8, 6), dtype=np.float64)
    for i, pair in enumerate(sessions):
        idx = 0
        for stage, rows in enumerate(pair):
            if len(rows) != 4:
                raise AssertionError("MD30_RNN_UNPAID_OR_MISSING_STAGE")
            previous = (0,) * 6
            for row in rows:
                a = row["action"]
                if a["kind"] not in ("diagnostic", "actuator"):
                    raise AssertionError("MD30_RNN_INVALID_PAID_ACTION")
                inputs[i, idx] = encode(previous, a, stage)
                targets[i, idx] = row["sensor_vector"]
                previous = tuple(row["sensor_vector"])
                idx += 1
    return inputs, targets


class RecurrentWorldControl:
    """All recurrent/input/output weights are optimized, not a frozen reservoir."""

    def __init__(self, weights):
        self.weights = {k: np.array(v, dtype=np.float64, copy=True)
                        for k, v in weights.items()}
        self.h = np.zeros(CFG["hidden_width"], dtype=np.float64)
        self.model_calls = 0

    def reset(self):
        self.h[:] = 0.0
        self.model_calls = 0

    def simulate(self, obs, action):
        stage = obs["phase"]
        if stage not in (0, 1):
            raise AssertionError("MD30_RNN_BAD_PHASE")
        x = encode(obs["sensor_vector"], action, stage)
        w = self.weights
        hidden = np.tanh(x @ w["Wx"] + self.h @ w["Wh"] + w["bh"])
        logits = hidden @ w["Wy"] + w["by"]
        prob = 1.0 / (1.0 + np.exp(-np.clip(logits, -40.0, 40.0)))
        self.model_calls += 1
        return hidden, prob

    def choose(self, obs):
        if obs["phase"] not in (0, 1):
            raise AssertionError("MD30_RNN_DONE")
        options = []
        for node in (0, 1):
            if obs["actuator_availability"][node]:
                action = {"kind": "actuator", "node": node, "value": 1}
                options.append((float(self.simulate(obs, action)[1][5]), node))
        probability, winner = max(options, key=lambda v: (v[0], -v[1]))
        self._winner = winner
        if (obs["remaining_diagnostics"] > 0 and
                len([r for r in obs["charged_history"]
                     if r["phase"] == obs["phase"] and
                     r["action"]["kind"] == "diagnostic"]) <
                CFG["max_planned_diagnostics_per_stage"] and
                probability < 0.68):
            probes = []
            for node in obs["diagnostic_nodes"]:
                for value in (0, 1):
                    a = {"kind": "diagnostic", "node": node, "value": value}
                    p = self.simulate(obs, a)[1]
                    p = np.clip(p, 1e-10, 1 - 1e-10)
                    entropy = float(np.mean(-p * np.log2(p) -
                                             (1 - p) * np.log2(1 - p)))
                    probes.append((entropy, node, value))
            entropy, node, value = max(probes, key=lambda v: (v[0], -v[1], -v[2]))
            if entropy > 0.75:
                return {"kind": "diagnostic", "node": node, "value": value}
        return {"kind": "actuator", "node": winner, "value": 1}

    def consume(self, before, action, after):
        """State update on an actually charged action; no simulated world.step."""
        if not after["charged_history"]:
            raise AssertionError("MD30_RNN_UNCHARGED_UPDATE")
        row = after["charged_history"][-1]
        if row["action"] != action or row["phase"] != before["phase"]:
            raise AssertionError("MD30_RNN_RECEIPT_MISMATCH")
        self.h = self.simulate(before, action)[0]


class RecurrentTrainer:
    def __init__(self):
        rng = np.random.default_rng(CFG["seed"])
        h = CFG["hidden_width"]
        self.params = {
            "Wx": rng.normal(0, 0.07, (16, h)),
            "Wh": rng.normal(0, 0.07, (h, h)),
            "bh": np.zeros(h),
            "Wy": rng.normal(0, 0.07, (h, 6)),
            "by": np.zeros(6),
        }
        self.adam_m = {k: np.zeros_like(v) for k, v in self.params.items()}
        self.adam_v = {k: np.zeros_like(v) for k, v in self.params.items()}
        self.adam_steps = 0
        self.rng = rng
        self.report = None

    def _forward(self, x, w=None):
        p = self.params if w is None else w
        batch, steps, _ = x.shape
        h = np.zeros((batch, CFG["hidden_width"]), dtype=np.float64)
        states = [h]
        probs = []
        logits = []
        for t in range(steps):
            h = np.tanh(x[:, t, :] @ p["Wx"] + h @ p["Wh"] + p["bh"])
            z = h @ p["Wy"] + p["by"]
            states.append(h)
            logits.append(z)
            probs.append(1 / (1 + np.exp(-np.clip(z, -40, 40))))
        return np.stack(logits, 1), np.stack(probs, 1), states

    def _loss(self, x, y, weights=None):
        z, _, _ = self._forward(x, weights)
        return float(np.mean(np.logaddexp(0.0, z) - y * z))

    def _train_batch(self, x, y):
        p = self.params
        z, prob, states = self._forward(x)
        b, t, d = y.shape
        grad = {k: np.zeros_like(v) for k, v in p.items()}
        dh_next = np.zeros((b, CFG["hidden_width"]))
        for step in reversed(range(t)):
            dz = (prob[:, step, :] - y[:, step, :]) / (b * t * d)
            grad["Wy"] += states[step + 1].T @ dz
            grad["by"] += np.sum(dz, axis=0)
            dh = dz @ p["Wy"].T + dh_next
            da = dh * (1 - states[step + 1] ** 2)
            grad["Wx"] += x[:, step, :].T @ da
            grad["Wh"] += states[step].T @ da
            grad["bh"] += np.sum(da, axis=0)
            dh_next = da @ p["Wh"].T
        decay = CFG["l2_weight_decay"]
        for key in ("Wx", "Wh", "Wy"):
            grad[key] += decay * p[key]
        norm = math.sqrt(sum(float(np.sum(v ** 2)) for v in grad.values()))
        if not math.isfinite(norm):
            raise AssertionError("MD30_RNN_GRADIENT_NOT_FINITE")
        scale = min(1.0, CFG["gradient_clip_global_norm"] / max(norm, 1e-12))
        self.adam_steps += 1
        step = self.adam_steps
        beta1, beta2 = CFG["adam_betas"]
        for key in p:
            g = grad[key] * scale
            self.adam_m[key] = beta1 * self.adam_m[key] + (1 - beta1) * g
            self.adam_v[key] = beta2 * self.adam_v[key] + (1 - beta2) * (g * g)
            m = self.adam_m[key] / (1 - beta1 ** step)
            v = self.adam_v[key] / (1 - beta2 ** step)
            p[key] -= CFG["learning_rate"] * m / (np.sqrt(v) + CFG["adam_eps"])
        return float(np.mean(np.logaddexp(0, z) - y * z))

    def fit(self, sessions):
        x, y = prepare(sessions)
        n = LOCK["cohorts"]["fit_episodes"]
        xtr, ytr, xval, yval = x[:n], y[:n], x[n:], y[n:]
        best_loss = math.inf
        best_params = None
        best_epoch = 0
        patience = 0
        start = time.process_time()
        epochs = 0
        for epoch in range(1, CFG["max_epochs"] + 1):
            indices = self.rng.permutation(n)
            for ix in range(0, n, CFG["batch_episodes"]):
                batch = indices[ix:ix + CFG["batch_episodes"]]
                self._train_batch(xtr[batch], ytr[batch])
            val = self._loss(xval, yval)
            if not math.isfinite(val):
                raise AssertionError("MD30_RNN_VALIDATION_NAN")
            if val < best_loss - CFG["validation_min_delta"]:
                best_loss = val
                best_epoch = epoch
                best_params = {k: v.copy() for k, v in self.params.items()}
                patience = 0
            else:
                patience += 1
            epochs = epoch
            if epoch >= CFG["min_epochs"] and patience >= CFG["early_stop_patience"]:
                break
        self.params = best_params
        self.report = {
            "fit_episodes": n, "validation_episodes": len(xval),
            "epochs_executed": epochs, "validation_best_epoch": best_epoch,
            "train_bce": round(self._loss(xtr, ytr), 8),
            "validation_bce": round(best_loss, 8),
            "parameter_count": sum(v.size for v in self.params.values()),
            "stopped_by_patience": patience >= CFG["early_stop_patience"],
            "training_cpu_seconds": round(time.process_time() - start, 4),
        }
        if self.report["parameter_count"] != 1766:
            raise AssertionError("MD30_RNN_CAPACITY_DRIFT")
        return self

    def checkpoint(self):
        if self.report is None:
            raise AssertionError("MD30_RNN_UNTRAINED")
        data = {k: [[round(float(v), 8) for v in row] for row in val]
                if val.ndim == 2 else [round(float(v), 8) for v in val]
                for k, val in self.params.items()}
        return {"schema": "md30.recurrent-world-model.v1", "weights": data,
                "best_epoch": self.report["validation_best_epoch"],
                "architecture": [16, 32, 6],
                "validation_bce": self.report["validation_bce"]}


def recurrent_toy_control(sessions):
    trainer = RecurrentTrainer().fit(sessions)
    model = RecurrentWorldControl(trainer.params)
    rewards = []
    receipts = []
    charged = probes = 0
    inference_start = time.process_time()
    for seed in TOY_TRANSFER:
        motif = TRANSFER_MOTIFS[(seed - TOY_TRANSFER[0]) % len(TRANSFER_MOTIFS)]
        world = synthetic_world(seed, motif, rewire=(seed % 2 == 0))
        model.reset()
        while True:
            obs = world.observe()
            if obs["phase"] == "done":
                break
            action = model.choose(obs)
            later, reward, done = world.step(action)
            model.consume(obs, action, later)
            charged += 1
            probes += int(action["kind"] == "diagnostic")
            if done:
                break
        rec = world.receipt()
        rewards.append(rec["net_utility"])
        receipts.append(rec["physical_sha256"])
    return {
        "model": "trained_recurrent_world_model",
        "architecture": [16, 32, 6],
        "train": trainer.report,
        "checkpoint_sha256": digest(trainer.checkpoint()),
        "toy_episodes": len(rewards),
        "toy_mean_net_utility": round(math.fsum(rewards) / len(rewards), 6),
        "toy_charged_steps": charged, "toy_charged_probes": probes,
        "physical_receipts_sha256": digest(receipts),
        "inference_cpu_seconds": round(time.process_time() - inference_start, 4),
    }
