"""Fully fitted conventional Elman recurrent public-mechanism world model.

Training sequences contain ONLY real paid encoder/decoder probes in the
source MD32 world; six public request features predict a four-way response.
The recurrent state changes only after an observed public paid response.
No motif/offset/rewire/seed/hidden graph enters the model or policy.
"""
import json
import math
from pathlib import Path

import numpy as np

from synthetic import LOCK
from compositional_relay import canonical, digest

CFG = LOCK["controls"]["recurrent"]
assert CFG["trainable_parameters"] == 964
HIDDEN = CFG["hidden_width"]
KINDS = ("encoder", "decoder")
assert CFG["input_width"] == 10 and CFG["output_width"] == 4
THRESHOLD = LOCK["controls"]["bayesian"]["probe_vs_actuator_threshold"]


def request_vector(kind, channel):
    if kind not in KINDS or type(channel) is not int or channel not in range(4):
        raise AssertionError("MD33_RNN_BAD_PUBLIC_PROBE_REQUEST")
    out = np.zeros(6, dtype=np.float64)
    out[KINDS.index(kind)] = 1.0
    out[2 + channel] = 1.0
    return out


def response_vector(request, response):
    if type(response) is not int or response not in range(4):
        raise AssertionError("MD33_RNN_NOT_PUBLIC_RESPONSE")
    x = np.zeros(10, dtype=np.float64)
    x[:6] = request
    x[6 + response] = 1.0
    return x


def training_arrays(blocks):
    if len(blocks) not in (192, 48):
        raise AssertionError("MD33_RNN_TRAIN_VALIDATION_ALLOCATION_DRIFT")
    req = np.zeros((len(blocks), 8, 6), dtype=np.float64)
    updates = np.zeros((len(blocks), 8, 10), dtype=np.float64)
    targets = np.zeros((len(blocks), 8), dtype=np.int64)
    for b, block in enumerate(blocks):
        if len(block) != 4:
            raise AssertionError("MD33_RNN_BLOCK_LENGTH")
        index = 0
        for episode in block:
            if len(episode) != 2:
                raise AssertionError("MD33_RNN_EXPECTS_PAID_TWO_PROBES")
            for kind, channel, observed in episode:
                q = request_vector(kind, channel)
                req[b, index] = q
                updates[b, index] = response_vector(q, observed)
                targets[b, index] = observed
                index += 1
    return req, updates, targets


def softmax(logits):
    adjusted = logits - np.max(logits, axis=-1, keepdims=True)
    p = np.exp(adjusted)
    return p / np.sum(p, axis=-1, keepdims=True)


class RecurrentWorldModel:
    """Conventional trainable recurrent world model, not native Yggdrasil."""

    def __init__(self, weights=None):
        if weights is None:
            rng = np.random.default_rng(CFG["initialization_seed"])
            w = {
                "Wx": rng.normal(0, 0.09, (10, HIDDEN)),
                "Wh": rng.normal(0, 0.09, (HIDDEN, HIDDEN)),
                "bh": np.zeros(HIDDEN, dtype=np.float64),
                "Wo": rng.normal(0, 0.09, (HIDDEN + 6, 4)),
                "bo": np.zeros(4, dtype=np.float64),
            }
        else:
            w = {k: np.asarray(v, dtype=np.float64)
                 for k, v in weights.items()}
        if ({k: value.shape for k, value in w.items()} !=
                {"Wx": (10, HIDDEN), "Wh": (HIDDEN, HIDDEN),
                 "bh": (HIDDEN,), "Wo": (HIDDEN + 6, 4), "bo": (4,)}):
            raise AssertionError("MD33_RNN_WEIGHT_CAPACITY_DRIFT")
        self.weights = w
        self.training_report = None
        self.h = np.zeros(HIDDEN, dtype=np.float64)
        self.paid_memory = {}
        self.model_calls = 0
        self.epochs = 0

    def begin_block(self):
        self.h[:] = 0.0
        self.paid_memory.clear()

    def predict(self, kind, channel):
        key = (kind, channel)
        self.model_calls += 1
        if key in self.paid_memory:
            observed = self.paid_memory[key]
            return tuple(float(i == observed) for i in range(4))
        req = request_vector(kind, channel)
        w = self.weights
        raw = np.concatenate((self.h, req)) @ w["Wo"] + w["bo"]
        probs = softmax(raw)
        return tuple(float(x) for x in probs)

    def observe(self, kind, channel, result):
        """Call only after verification of a physically paid public receipt."""
        req = request_vector(kind, channel)
        x = response_vector(req, result)
        w = self.weights
        self.h = np.tanh(x @ w["Wx"] + self.h @ w["Wh"] + w["bh"])
        self.paid_memory[(kind, channel)] = result

    def should_probe(self, probabilities):
        return max(probabilities) < THRESHOLD

    def _forward(self, requests, updates):
        batch, length, _ = requests.shape
        state = np.zeros((batch, HIDDEN), dtype=np.float64)
        states = [state]
        probabilities = []
        for t in range(length):
            features = np.concatenate([state, requests[:, t, :]], axis=1)
            logits = features @ self.weights["Wo"] + self.weights["bo"]
            probabilities.append(softmax(logits))
            state = np.tanh(updates[:, t, :] @ self.weights["Wx"] +
                            state @ self.weights["Wh"] + self.weights["bh"])
            states.append(state)
        return np.stack(probabilities, axis=1), states

    def _loss(self, requests, updates, targets):
        probs, _ = self._forward(requests, updates)
        rows = np.arange(len(requests))[:, None]
        times = np.arange(requests.shape[1])[None, :]
        chosen = probs[rows, times, targets]
        return float(-np.mean(np.log(np.maximum(chosen, 1e-15))))

    def _fit_batch(self, requests, updates, targets, moments, step):
        w = self.weights
        probs, states = self._forward(requests, updates)
        batch, length, categories = probs.shape
        gradients = {key: np.zeros_like(val) for key, val in w.items()}
        downstream = np.zeros((batch, HIDDEN), dtype=np.float64)
        for t in reversed(range(length)):
            dz = probs[:, t, :].copy()
            dz[np.arange(batch), targets[:, t]] -= 1.0
            dz /= (batch * length)
            inp = np.concatenate([states[t], requests[:, t, :]], axis=1)
            gradients["Wo"] += inp.T @ dz
            gradients["bo"] += dz.sum(axis=0)
            da = downstream * (1.0 - states[t + 1] ** 2)
            gradients["Wx"] += updates[:, t, :].T @ da
            gradients["Wh"] += states[t].T @ da
            gradients["bh"] += da.sum(axis=0)
            downstream = dz @ w["Wo"][:HIDDEN, :].T + da @ w["Wh"].T
        for key in ("Wx", "Wh", "Wo"):
            gradients[key] += CFG["weight_decay"] * w[key]
        norm = math.sqrt(sum(float(np.sum(g * g))
                             for g in gradients.values()))
        if not math.isfinite(norm):
            raise AssertionError("MD33_RNN_NONFINITE_GRADIENTS")
        multiplier = min(1.0, CFG["clip_grad_norm"] / max(norm, 1e-12))
        beta1, beta2 = CFG["adam_betas"]
        for name in w:
            g = gradients[name] * multiplier
            first, second = moments[name]
            first *= beta1
            first += (1.0 - beta1) * g
            second *= beta2
            second += (1.0 - beta2) * (g * g)
            w[name] -= CFG["learning_rate"] * (
                first / (1 - beta1 ** step)) / (
                np.sqrt(second / (1 - beta2 ** step)) + CFG["adam_eps"])

    def fit(self, train_blocks, validation_blocks):
        if len(train_blocks) != 192 or len(validation_blocks) != 48:
            raise AssertionError("MD33_RNN_FROZEN_FIT_SPLIT")
        train = training_arrays(train_blocks)
        valid = training_arrays(validation_blocks)
        begin_train_loss = self._loss(*train)
        rng = np.random.default_rng(CFG["training_shuffle_seed"])
        moments = {key: [np.zeros_like(val), np.zeros_like(val)]
                   for key, val in self.weights.items()}
        best_loss, best_epoch, best_weights = float("inf"), 0, None
        patience = 0
        batch = CFG["batch_blocks"]
        optim_step = 0
        for epoch in range(1, CFG["epochs_max"] + 1):
            for start in range(0, 192, batch):
                indices = permutation[start:start + batch] if start else None
                if start == 0:
                    permutation = rng.permutation(192)
                    indices = permutation[:batch]
                optim_step += 1
                self._fit_batch(
                    *(x[indices] for x in train),
                    moments, optim_step)
            valid_loss = self._loss(*valid)
            if not math.isfinite(valid_loss):
                raise AssertionError("MD33_RNN_NONFINITE_VALIDATION")
            if valid_loss < best_loss - CFG["validation_improvement_epsilon"]:
                best_loss, best_epoch = valid_loss, epoch
                best_weights = {k: v.copy()
                                for k, v in self.weights.items()}
                patience = 0
            else:
                patience += 1
            self.epochs = epoch
            if epoch >= CFG["epochs_min"] and patience >= CFG["patience"]:
                break
        if best_weights is None:
            raise AssertionError("MD33_RNN_UNTRAINED")
        self.weights = best_weights
        parameter_count = sum(w.size for w in self.weights.values())
        self.training_report = {
            "fit_blocks": 192, "validation_blocks": 48,
            "fit_public_probes": 1536,
            "validation_public_probes": 384,
            "trainable_parameters": parameter_count,
            "initial_train_cross_entropy": round(begin_train_loss, 7),
            "final_train_cross_entropy": round(self._loss(*train), 7),
            "validation_best_cross_entropy": round(best_loss, 7),
            "epochs_completed": self.epochs, "validation_best_epoch": best_epoch,
            "stopped_by_patience": patience >= CFG["patience"],
        }
        if parameter_count != 964 or not (
                self.training_report["final_train_cross_entropy"] <
                self.training_report["initial_train_cross_entropy"]):
            raise AssertionError("MD33_RNN_NOT_TRAINED_OR_CAPACITY_DRIFT")
        return self

    def checkpoint(self):
        if self.training_report is None:
            raise AssertionError("MD33_RNN_NOT_FITTED")
        return {
            "schema": "md33.fully-trained-elman-probe-world-model.v1",
            "architecture": [10, HIDDEN, 4],
            "weights": {key: np.round(value, 9).tolist()
                        for key, value in sorted(self.weights.items())},
            "training_report": self.training_report,
        }

    @classmethod
    def from_checkpoint(cls, checkpoint):
        if checkpoint.get("schema") != "md33.fully-trained-elman-probe-world-model.v1":
            raise AssertionError("MD33_RNN_BAD_COLD_CHECKPOINT")
        model = cls(checkpoint["weights"])
        model.training_report = checkpoint["training_report"]
        if model.training_report["trainable_parameters"] != 964:
            raise AssertionError("MD33_RNN_COLD_CAPACITY_DRIFT")
        if canonical(model.checkpoint()) != canonical(checkpoint):
            raise AssertionError("MD33_RNN_COLD_CHECKPOINT_BYTES_DIFFER")
        return model
