"""MD35 CPU-only trained 64-unit gated recurrent physical world model.

GRU forward/backward, clipped Adam, and 3 independent frozen seeds are built
from NumPy. The targets are only charged diagnostic *bits* and terminal
success/failure; a failed terminal guess never reveals its correct target.
No private law, source motif, cohort seed, graph or privileged teacher enters.
"""
import copy
import math
import time
import numpy as np
from public_actions import PublicEpisode, require_public_blocks

HIDDEN = 64
QUERY = 22
WIDTH = 26
SEEDS = (35035, 35036, 35037)
LEARNING_RATE = 0.001
WEIGHT_DECAY = 0.0001
BATCH_BLOCKS = 16
EPOCHS_MAX = 120
EPOCHS_MIN = 20
PATIENCE = 20
CLIP_NORM = 1.0
CPU_CAP = 900.0

KINDS = {"actuator": 0, "route": 1, "diagnostic": 2, "terminal": 3}
PARAMETER_SHAPES = {
    "Wz": (WIDTH, HIDDEN), "Uz": (HIDDEN, HIDDEN), "bz": (HIDDEN,),
    "Wr": (WIDTH, HIDDEN), "Ur": (HIDDEN, HIDDEN), "br": (HIDDEN,),
    "Wn": (WIDTH, HIDDEN), "Un": (HIDDEN, HIDDEN), "bn": (HIDDEN,),
    "Wo": (HIDDEN + QUERY, 2), "bo": (2,),
}


def sigmoid(value):
    value = np.clip(value, -40.0, 40.0)
    return 1.0 / (1.0 + np.exp(-value))


def query_vector(context, event):
    if (type(context) is not int or context not in range(4) or
            type(event) is not tuple or len(event) != 5):
        raise AssertionError("MD35_GRU_BAD_PUBLIC_EVENT")
    phase, kind, arg, reward, bit = event
    if kind not in KINDS or type(phase) is not int or phase not in range(3):
        raise AssertionError("MD35_GRU_UNSUPPORTED_PUBLIC_ACTION")
    out = np.zeros(QUERY, dtype=np.float64)
    out[context] = 1
    out[4 + phase] = 1
    out[7 + KINDS[kind]] = 1
    if kind == "route":
        if arg not in (0, 1):
            raise AssertionError("MD35_GRU_BAD_ROUTE_CHOICE")
        out[11 + arg] = 1
    if kind == "terminal":
        if type(arg) is not int or arg not in range(4):
            raise AssertionError("MD35_GRU_BAD_TERMINAL_GUESS")
        out[13 + arg] = 1
    if kind == "diagnostic":
        out[17 + phase] = 1
        if phase == 1:
            if arg not in (0, 1):
                raise AssertionError("MD35_GRU_BAD_PAID_ROUTE_CHANNEL")
            out[20 + arg] = 1
    return out


def observed_vector(query, event):
    _, kind, _, reward, bit = event
    if kind == "diagnostic":
        if bit not in (0, 1) or reward != -0.09:
            raise AssertionError("MD35_GRU_DIAGNOSTIC_MUST_BE_PAID")
    elif bit != -1:
        raise AssertionError("MD35_GRU_UNPAID_SENSOR")
    extra = np.array([
        float(kind == "diagnostic" and bit == 0),
        float(kind == "diagnostic" and bit == 1),
        float(reward),
        float(kind == "terminal"),
    ], dtype=np.float64)
    return np.concatenate((query, extra))


def training_arrays(blocks, expected):
    source = require_public_blocks(blocks, expected_count=expected)
    queries = np.zeros((expected, 16, QUERY), dtype=np.float64)
    updates = np.zeros((expected, 16, WIDTH), dtype=np.float64)
    targets = np.zeros((expected, 16, 2), dtype=np.float64)
    masks = np.zeros((expected, 16, 2), dtype=np.float64)
    for b, block in enumerate(source):
        step = 0
        for ep in block:
            if len(ep.events) != 4 or ep.diagnostic() is None:
                raise AssertionError("MD35_GRU_SHARED_TRAINING_MUST_PAY_6144")
            for event in ep.events:
                if step >= 16:
                    raise AssertionError("MD35_GRU_TRAIN_SEQUENCE_OVERFLOW")
                q = query_vector(ep.context, event)
                queries[b, step] = q
                updates[b, step] = observed_vector(q, event)
                if event[1] == "terminal":
                    masks[b, step, 0] = 1.0
                    targets[b, step, 0] = float(event[3] == 0.98)
                if event[1] == "diagnostic":
                    masks[b, step, 1] = 1.0
                    targets[b, step, 1] = event[4]
                step += 1
        if step != 16 or masks[b].sum() != 8:
            raise AssertionError("MD35_GRU_SHARED_PUBLIC_SUPERVISION_DRIFT")
    return queries, updates, targets, masks


class GatedRecurrentControl:
    def __init__(self, seed=35035, weights=None):
        if seed not in SEEDS:
            raise AssertionError("MD35_GRU_UNREGISTERED_SEED")
        self.seed = seed
        if weights is None:
            rng = np.random.default_rng(seed)
            self.w = {
                name: (np.zeros(shape) if name.startswith("b") else
                       rng.normal(0.0, 0.06, shape))
                for name, shape in PARAMETER_SHAPES.items()
            }
        else:
            self.w = {name: np.asarray(value, dtype=np.float64)
                      for name, value in weights.items()}
        if {name: v.shape for name, v in self.w.items()} != PARAMETER_SHAPES:
            raise AssertionError("MD35_GRU_CAPACITY_DRIFT")
        if any(not np.isfinite(v).all() for v in self.w.values()):
            raise AssertionError("MD35_GRU_NONFINITE_INITIALIZATION")
        self.h = np.zeros(HIDDEN, dtype=np.float64)
        self._block_episodes = None
        self.fitted = False
        self.all_seed_reports = None
        self.fit_report = None

    def _step(self, h, x):
        w = self.w
        z = sigmoid(x @ w["Wz"] + h @ w["Uz"] + w["bz"])
        r = sigmoid(x @ w["Wr"] + h @ w["Ur"] + w["br"])
        n = np.tanh(x @ w["Wn"] + (r * h) @ w["Un"] + w["bn"])
        following = (1.0 - z) * h + z * n
        return following, (h, x, z, r, n)

    def _forward(self, array):
        queries, updates, _, _ = array
        b, length, _ = queries.shape
        h = np.zeros((b, HIDDEN), dtype=np.float64)
        preds, cache = [], []
        for t in range(length):
            q, x = queries[:, t], updates[:, t]
            p = sigmoid(np.concatenate((h, q), axis=1) @ self.w["Wo"] +
                        self.w["bo"])
            new_h, partial = self._step(h, x)
            preds.append(p)
            cache.append((q, p, partial))
            h = new_h
        return np.stack(preds, axis=1), cache

    def _loss(self, array):
        p, _ = self._forward(array)
        _, _, y, mask = array
        p = np.clip(p, 1e-9, 1 - 1e-9)
        return float(-(mask * (y * np.log(p) +
                     (1 - y) * np.log(1 - p))).sum() / mask.sum())

    def _fit_batch(self, array, moments, iteration):
        predictions, cache = self._forward(array)
        _, _, y, mask = array
        b, length, _ = predictions.shape
        gradients = {name: np.zeros_like(val) for name, val in self.w.items()}
        dh = np.zeros((b, HIDDEN), dtype=np.float64)
        w = self.w
        for t in range(length - 1, -1, -1):
            q, p, (previous, x, z, r, n) = cache[t]
            dy = (p - y[:, t]) * mask[:, t] / max(1.0, float(mask.sum()))
            gradients["Wo"] += np.concatenate((previous, q), axis=1).T @ dy
            gradients["bo"] += dy.sum(axis=0)
            dn = dh * z
            dz = dh * (n - previous)
            dprev = dh * (1.0 - z)
            dnpre = dn * (1.0 - n * n)
            gradients["Wn"] += x.T @ dnpre
            gradients["Un"] += (r * previous).T @ dnpre
            gradients["bn"] += dnpre.sum(axis=0)
            dmod = dnpre @ w["Un"].T
            dprev += dmod * r
            drpre = dmod * previous * r * (1.0 - r)
            gradients["Wr"] += x.T @ drpre
            gradients["Ur"] += previous.T @ drpre
            gradients["br"] += drpre.sum(axis=0)
            dprev += drpre @ w["Ur"].T
            dzpre = dz * z * (1.0 - z)
            gradients["Wz"] += x.T @ dzpre
            gradients["Uz"] += previous.T @ dzpre
            gradients["bz"] += dzpre.sum(axis=0)
            dprev += dzpre @ w["Uz"].T
            dh = dprev + dy @ w["Wo"][:HIDDEN].T
        for name in w:
            if name.startswith("W") or name.startswith("U"):
                gradients[name] += WEIGHT_DECAY * w[name]
        norm = math.sqrt(sum(float((g * g).sum()) for g in gradients.values()))
        if not math.isfinite(norm):
            raise AssertionError("MD35_GRU_NONFINITE_GRADIENTS")
        scale = min(1.0, CLIP_NORM / max(norm, 1e-12))
        for name, value in w.items():
            grad = gradients[name] * scale
            m, v = moments[name]
            m *= 0.9
            m += 0.1 * grad
            v *= 0.999
            v += 0.001 * grad * grad
            value -= LEARNING_RATE * (m / (1 - 0.9 ** iteration)) / (
                np.sqrt(v / (1 - 0.999 ** iteration)) + 1e-8)
        if any(not np.isfinite(v).all() for v in w.values()):
            raise AssertionError("MD35_GRU_NONFINITE_TRAINING")

    def _fit_one(self, train, valid, start_cpu):
        moments = {k: [np.zeros_like(v), np.zeros_like(v)]
                   for k, v in self.w.items()}
        rng = np.random.default_rng(self.seed + 1000)
        best_loss, best_weights, best_epoch = float("inf"), None, 0
        stale, iterations = 0, 0
        initial_loss = self._loss(train)
        for epoch in range(1, EPOCHS_MAX + 1):
            permutation = rng.permutation(len(train[0]))
            for begin in range(0, len(permutation), BATCH_BLOCKS):
                selected = permutation[begin:begin + BATCH_BLOCKS]
                iterations += 1
                self._fit_batch(tuple(a[selected] for a in train),
                                moments, iterations)
                if time.process_time() - start_cpu >= CPU_CAP:
                    raise TimeoutError("MD35_GRU_THREE_SEED_CPU_CAP")
            current_loss = self._loss(valid)
            if current_loss < best_loss - 1e-12:
                best_loss = current_loss
                best_epoch = epoch
                best_weights = {k: v.copy() for k, v in self.w.items()}
                stale = 0
            else:
                stale += 1
            if epoch >= EPOCHS_MIN and stale >= PATIENCE:
                break
        if best_weights is None:
            raise AssertionError("MD35_GRU_NO_VALIDATION_CHECKPOINT")
        self.w = best_weights
        report = {
            "seed": self.seed, "epochs": epoch,
            "best_epoch": best_epoch,
            "initial_training_bce": initial_loss,
            "selected_validation_bce": best_loss,
            "trained_public_actions": len(train[0]) * 16,
            "validation_public_actions": len(valid[0]) * 16,
            "trainable_parameters": sum(v.size for v in self.w.values()),
        }
        if (report["trained_public_actions"] != 6144 or
                report["validation_public_actions"] != 1536 or
                report["epochs"] < EPOCHS_MIN or
                report["epochs"] > EPOCHS_MAX or
                not math.isfinite(best_loss)):
            raise AssertionError("MD35_GRU_FROZEN_TRAIN_CONTRACT_FAILED")
        self.fit_report = report
        return self

    @classmethod
    def train(cls, train_blocks, validation_blocks):
        train = training_arrays(train_blocks, 384)
        valid = training_arrays(validation_blocks, 96)
        started = time.process_time()
        trained = []
        for seed in SEEDS:
            model = cls(seed)._fit_one(train, valid, started)
            trained.append(model)
        chosen = min(trained, key=lambda model: (
            model.fit_report["selected_validation_bce"], model.seed))
        chosen.all_seed_reports = [copy.deepcopy(model.fit_report)
                                   for model in trained]
        chosen.fitted = True
        chosen.fit_report["all_three_seed_cpu_seconds"] = time.process_time() - started
        if chosen.fit_report["all_three_seed_cpu_seconds"] > CPU_CAP:
            raise TimeoutError("MD35_GRU_CPU_CAP")
        return chosen

    def begin_block(self):
        self.h.fill(0.0)
        self._block_episodes = 0

    def update(self, episode):
        if self._block_episodes is None or self._block_episodes >= 4:
            raise AssertionError("MD35_GRU_PUBLIC_BLOCK_REQUIRED")
        if type(episode) is not PublicEpisode or episode.context != self._block_episodes:
            raise AssertionError("MD35_GRU_PUBLIC_CONTEXT_DRIFT")
        for event in episode.events:
            q = query_vector(episode.context, event)
            x = observed_vector(q, event)
            self.h = self._step(self.h[None, :], x[None, :])[0][0]
        self._block_episodes += 1

    def predict_target(self, context, route):
        """Estimate terminal-class distribution from model-predicted success.

        The simulated updates are *internal GRU predictions* of publicly
        known action costs, not calls to an environment/world or oracle.
        """
        if self._block_episodes is None:
            raise AssertionError("MD35_GRU_BLOCK_BOUNDARY_REQUIRED")
        local = self.h[None, :].copy()
        for event in ((0, "actuator", context, -0.02, -1),
                      (1, "route", route, -0.02 if route == 0 else -0.05, -1)):
            q = query_vector(context, event)
            x = observed_vector(q, event)
            local = self._step(local, x[None, :])[0]
        scores = []
        for guess in range(4):
            e = (2, "terminal", guess, 0.0, -1)
            q = query_vector(context, e)
            scores.append(float(sigmoid(
                np.concatenate((local[0], q)) @ self.w["Wo"][:, 0] +
                self.w["bo"][0])))
        p = np.asarray(scores) + 1e-12
        return tuple(float(x) for x in p / p.sum())

    def checkpoint(self):
        if not self.fitted or self.all_seed_reports is None:
            raise AssertionError("MD35_GRU_UNTRAINED_CHECKPOINT")
        return {
            "schema": "md35.gated-public-gru64.v1",
            "hidden": HIDDEN, "seeds": list(SEEDS),
            "selected_seed": self.seed,
            "all_seed_reports": self.all_seed_reports,
            "fit_report": self.fit_report,
            "weights": {k: v.tolist() for k, v in sorted(self.w.items())},
        }

    @classmethod
    def restore(cls, data):
        if (type(data) is not dict or data.get("schema") != "md35.gated-public-gru64.v1"
                or data.get("hidden") != HIDDEN or data.get("seeds") != list(SEEDS)
                or data.get("selected_seed") not in SEEDS
                or type(data.get("all_seed_reports")) is not list
                or [r.get("seed") for r in data["all_seed_reports"]] != list(SEEDS)):
            raise AssertionError("MD35_GRU_INVALID_COLD_CHECKPOINT")
        obj = cls(data["selected_seed"], data["weights"])
        obj.fit_report = copy.deepcopy(data["fit_report"])
        obj.all_seed_reports = copy.deepcopy(data["all_seed_reports"])
        obj.fitted = True
        if obj.checkpoint() != data:
            raise AssertionError("MD35_GRU_COLD_BYTES_DIFFER")
        return obj
