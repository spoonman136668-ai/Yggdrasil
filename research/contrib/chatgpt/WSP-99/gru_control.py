"""WSP99 fully trainable conventional GRU16 comparator, source-only, no oracle."""
from __future__ import annotations

import numpy as np

from controls import (
    N, STEPS, SEEDS, ORIGINAL_EPOCHS,
    _adam, _features, _sigmoid, _training_arrays, _valid_bits,
    validate_episodes,
)


class GradientGRU16:
    """GRU16 conventional gradient baseline (1398 parameters), full-batch BPTT."""
    def __init__(self, seed):
        if type(seed) is not int or seed not in SEEDS:
            raise ValueError("unregistered train seed")
        rng = np.random.Generator(np.random.PCG64(seed))
        w = {}
        for letter in ("z", "r", "n"):
            w["W"+letter] = rng.normal(0.0, .1, size=(16, 10))
            w["U"+letter] = rng.normal(0.0, .1, size=(16, 16))
            w["b"+letter] = np.zeros(16, dtype=np.float64)
        w["Wo"] = rng.normal(0.0, .1, size=(N, 16))
        w["bo"] = np.zeros(N, dtype=np.float64)
        if sum(v.size for v in w.values()) != 1398:
            raise AssertionError("GRU capacity drift")
        self.weights = w
        self.training_loss = None
        self.epochs_trained = 0
        self.reset()

    def reset(self):
        self._hidden = np.zeros(16, dtype=np.float64)

    def step_probability(self, visible, action):
        w = self.weights
        x = _features(visible, action)
        h = self._hidden
        z = _sigmoid(w["Wz"] @ x + w["Uz"] @ h + w["bz"])
        r = _sigmoid(w["Wr"] @ x + w["Ur"] @ h + w["br"])
        n = np.tanh(w["Wn"] @ x + w["Un"] @ (r * h) + w["bn"])
        self._hidden = z * h + (1.0 - z) * n
        return tuple(float(value) for value in
                     _sigmoid(w["Wo"] @ self._hidden + w["bo"]))

    def rollout(self, initial, actions):
        if not isinstance(actions, (list, tuple)) or len(actions) > STEPS:
            raise ValueError("maximum four actions")
        self.reset()
        x = _valid_bits(initial)
        output = []
        for action in actions:
            probabilities = self.step_probability(x, action)
            x = tuple(int(p > .5) for p in probabilities)
            output.append((x, probabilities))
        return tuple(output)

    def _forward(self, xs):
        w = self.weights
        h = [np.zeros((len(xs), 16), dtype=np.float64)]
        cache, logits = [], []
        for t in range(STEPS):
            u = xs[:, t]
            prev = h[-1]
            z = _sigmoid(u @ w["Wz"].T + prev @ w["Uz"].T + w["bz"])
            r = _sigmoid(u @ w["Wr"].T + prev @ w["Ur"].T + w["br"])
            n = np.tanh(u @ w["Wn"].T + (r * prev) @ w["Un"].T + w["bn"])
            new_h = z * prev + (1.0 - z) * n
            cache.append((z, r, n))
            h.append(new_h)
            logits.append(new_h @ w["Wo"].T + w["bo"])
        return h, cache, np.stack(logits, axis=1)

    def _grad(self, xs, ys):
        w = self.weights
        h, cache, logits = self._forward(xs)
        loss = float(np.mean(np.logaddexp(0, logits) - ys * logits))
        dl = (_sigmoid(logits) - ys) / float(ys.size)
        grad = {name: np.zeros_like(value) for name, value in w.items()}
        dh_next = np.zeros_like(h[-1])
        for t in reversed(range(STEPS)):
            u = xs[:, t]
            prev = h[t]
            z, r, n = cache[t]
            g = dl[:, t]
            grad["Wo"] += g.T @ h[t + 1]
            grad["bo"] += np.sum(g, axis=0)
            dh = g @ w["Wo"] + dh_next
            dn = dh * (1 - z)
            dz = dh * (prev - n)
            dh_previous = dh * z

            dn_pre = dn * (1 - n * n)
            grad["Wn"] += dn_pre.T @ u
            grad["Un"] += dn_pre.T @ (r * prev)
            grad["bn"] += np.sum(dn_pre, axis=0)
            dr_previous = dn_pre @ w["Un"]
            dr = dr_previous * prev
            dh_previous += dr_previous * r

            dr_pre = dr * r * (1 - r)
            grad["Wr"] += dr_pre.T @ u
            grad["Ur"] += dr_pre.T @ prev
            grad["br"] += np.sum(dr_pre, axis=0)
            dh_previous += dr_pre @ w["Ur"]

            dz_pre = dz * z * (1 - z)
            grad["Wz"] += dz_pre.T @ u
            grad["Uz"] += dz_pre.T @ prev
            grad["bz"] += np.sum(dz_pre, axis=0)
            dh_previous += dz_pre @ w["Uz"]
            dh_next = dh_previous
        return loss, grad

    def train(self, episodes, *, epochs=ORIGINAL_EPOCHS, development=False):
        if type(development) is not bool or type(epochs) is not int:
            raise ValueError("invalid regime")
        if development:
            if not 1 <= epochs <= 24:
                raise ValueError("DEV is limited to 24 epochs")
        elif epochs != ORIGINAL_EPOCHS:
            raise ValueError("exact original GRU training budget is 1800 epochs")
        _, xs, ys = _training_arrays(episodes)
        moments = {name: np.zeros_like(value)
                   for name, value in self.weights.items()}
        velocity = {name: np.zeros_like(value)
                    for name, value in self.weights.items()}
        for epoch in range(1, epochs + 1):
            _, grad = self._grad(xs, ys)
            _adam(self.weights, grad, moments, velocity, epoch)
        self.training_loss = self._grad(xs, ys)[0]
        self.epochs_trained = epochs
        return self.training_loss

    def source_fit(self, episodes):
        clean = validate_episodes(episodes)
        right = 0
        for episode in clean:
            self.reset()
            for x, action, y in episode:
                probs = self.step_probability(x, action)
                right += sum(int(int(p > .5) == truth) for p, truth in zip(probs, y))
        self.reset()
        return right / (len(clean) * STEPS * N)
