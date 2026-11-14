"""WSP-99 independent fixture comparators. No original-world oracle imported.

This source is a proposed control implementation, not a scientific result.
The original PUBLIC/RESERVE world factory is unavailable to this module.
"""
from __future__ import annotations
from itertools import combinations, product
import math
import numpy as np

N = 6
ACTIONS = 4
STEPS = 4
SEEDS = (11, 17, 23)
ORIGINAL_EPOCHS = 1800
GATES = ("AND", "OR", "XOR", "XNOR", "NAND", "NOR")


def _valid_bits(bits):
    if not isinstance(bits, (tuple, list)) or len(bits) != N or any(
        type(b) is not int or b not in (0, 1) for b in bits
    ):
        raise ValueError("six binary visible values expected")
    return tuple(bits)


def _valid_action(action):
    if type(action) is not int or not 0 <= action < ACTIONS:
        raise ValueError("action must be 0..3")
    return action


def validate_episodes(episodes):
    if not isinstance(episodes, (list, tuple)) or not episodes:
        raise ValueError("at least one training episode required")
    clean = []
    for episode in episodes:
        if not isinstance(episode, (list, tuple)) or len(episode) != STEPS:
            raise ValueError("four steps per reset episode required")
        rows = []
        for index, row in enumerate(episode):
            if not isinstance(row, (list, tuple)) or len(row) != 3:
                raise ValueError("episode row must be (visible, action, next-visible)")
            x, action, y = _valid_bits(row[0]), _valid_action(row[1]), _valid_bits(row[2])
            if index and x != rows[-1][2]:
                raise ValueError("invalid episode transition continuity")
            rows.append((x, action, y))
        clean.append(tuple(rows))
    return tuple(clean)


def clause_value(x, clause):
    p, q, flip_p, flip_q, law = clause
    a, b = x[p] ^ flip_p, x[q] ^ flip_q
    if law == "AND": return a & b
    if law == "OR": return a | b
    if law == "XOR": return a ^ b
    if law == "XNOR": return 1 ^ a ^ b
    if law == "NAND": return 1 ^ (a & b)
    if law == "NOR": return 1 ^ (a | b)
    raise ValueError("unknown clause")


def _catalogue():
    return tuple((p, q, flip_p, flip_q, law)
                 for p, q in combinations(range(N), 2)
                 for flip_p, flip_q in product((0, 1), repeat=2)
                 for law in GATES)


class SymbolicFiniteState:
    """Enumerates observable-consistent programs and latent two-latch rules.

    This method is independent of the simulator implementation. It receives
    only visible source rows, actions, and next-visible consequences.
    """
    def __init__(self, episodes):
        self.episodes = validate_episodes(episodes)
        rows = tuple(row for ep in self.episodes for row in ep)
        clauses = _catalogue()
        assert len(clauses) == 360
        signatures = {}
        for clause in clauses:
            signature = sum(clause_value(row[0], clause) << i for i, row in enumerate(rows))
            signatures.setdefault(signature, []).append(clause)
        target_signatures = [
            sum(row[2][output] << i for i, row in enumerate(rows))
            for output in range(N)
        ]
        self._plain = []
        for output in (4, 5):
            options = signatures.get(target_signatures[output], ())
            if not options:
                raise ValueError("symbolic output has no source-consistent clause")
            self._plain.append(tuple(options))
        self._latches = []
        for latch in range(2):
            viable = []
            for trigger in range(ACTIONS):
                for p, q in combinations(range(N), 2):
                    for flip in (0, 1):
                        hidden_sig = 0
                        position = 0
                        for episode in self.episodes:
                            h = 0
                            for x, action, _ in episode:
                                hidden_sig |= h << position
                                h ^= int(action == trigger and (x[p] ^ x[q] ^ flip) == 1)
                                position += 1
                        per_output = []
                        for output in (latch, latch + 2):
                            options = signatures.get(target_signatures[output] ^ hidden_sig, ())
                            if not options:
                                break
                            per_output.append(tuple(options))
                        if len(per_output) == 2:
                            viable.append((trigger, p, q, flip, tuple(per_output)))
            if not viable:
                raise ValueError("no consistent hidden-latch program")
            self._latches.append(tuple(viable))
        filtered = []
        for j in range(2):
            opposite = {c[0] for c in self._latches[1 - j]}
            candidates = tuple(c for c in self._latches[j] if any(t != c[0] for t in opposite))
            if not candidates:
                raise ValueError("distinct-trigger causal program impossible")
            filtered.append(candidates)
        self._latches = tuple(filtered)
        self.candidate_counts = tuple(len(x) for x in self._latches)
        self.reset()
        self.source_accuracy = self.source_fit()

    def reset(self):
        self._hidden = [[0] * len(latch_candidates)
                        for latch_candidates in self._latches]

    def step(self, visible, action):
        x, action = _valid_bits(visible), _valid_action(action)
        predicted = [0] * N
        for j in range(2):
            scores = [0, 0]
            for index, (trigger, p, q, flip, options) in enumerate(self._latches[j]):
                h = self._hidden[j][index]
                for local_output in range(2):
                    for clause in options[local_output]:
                        bit = clause_value(x, clause) ^ h
                        scores[local_output] += (2 * bit - 1)
                self._hidden[j][index] = h ^ int(
                    action == trigger and (x[p] ^ x[q] ^ flip) == 1
                )
            predicted[j] = int(scores[0] > 0)
            predicted[j + 2] = int(scores[1] > 0)
        for index, options in enumerate(self._plain):
            score = sum(2 * clause_value(x, clause) - 1 for clause in options)
            predicted[4 + index] = int(score > 0)
        return tuple(predicted)

    def rollout(self, initial, actions):
        if len(actions) > STEPS:
            raise ValueError("episode length exceeded")
        self.reset()
        x = _valid_bits(initial)
        output = []
        for action in actions:
            x = self.step(x, action)
            output.append(x)
        return tuple(output)

    def source_fit(self):
        correct, total = 0, 0
        for episode in self.episodes:
            self.reset()
            for x, action, y in episode:
                predicted = self.step(x, action)
                correct += sum(int(a == b) for a, b in zip(predicted, y))
                total += N
        self.reset()
        return correct / total


def _features(x, action):
    _valid_bits(x)
    _valid_action(action)
    return np.asarray([2 * b - 1 for b in x] +
                      [int(action == k) for k in range(ACTIONS)], dtype=np.float64)


def _training_arrays(episodes):
    clean = validate_episodes(episodes)
    x = np.asarray([[_features(row[0], row[1]) for row in ep]
                    for ep in clean], dtype=np.float64)
    y = np.asarray([[row[2] for row in ep] for ep in clean], dtype=np.float64)
    return clean, x, y


def _sigmoid(z):
    return np.exp(-np.logaddexp(0.0, -z))


def _adam(weights, grads, moments, velocity, epoch, *, decay=1.e-4):
    norm = math.sqrt(sum(float(np.sum(g * g)) for g in grads.values()))
    scale = min(1.0, 5.0 / max(norm, 1e-300))
    for name, weight in weights.items():
        grad = scale * grads[name]
        if name.startswith("W"):
            grad = grad + decay * weight
        moments[name] = .9 * moments[name] + .1 * grad
        velocity[name] = .999 * velocity[name] + .001 * (grad * grad)
        mhat = moments[name] / (1.0 - .9 ** epoch)
        vhat = velocity[name] / (1.0 - .999 ** epoch)
        weight -= .01 * mhat / (np.sqrt(vhat) + 1.e-8)
        if not np.all(np.isfinite(weight)):
            raise ValueError("unstable conventional learner")


class GradientTanhRNN:
    """Conventional 16-unit tanh RNN, exact full-batch BPTT + Adam.

    Full original budget is fixed to 1800 epochs/seed; dev fixtures may run
    up to 24 diagnostic steps and are never confirmatory scientific evidence.
    """
    def __init__(self, seed):
        if seed not in SEEDS or type(seed) is not int:
            raise ValueError("unregistered source training seed")
        rng = np.random.Generator(np.random.PCG64(seed))
        self.weights = {
            "Wx": rng.normal(0.0, .1, size=(16, 10)),
            "Wh": rng.normal(0.0, .1, size=(16, 16)),
            "bh": np.zeros(16, dtype=np.float64),
            "Wo": rng.normal(0.0, .1, size=(N, 16)),
            "bo": np.zeros(N, dtype=np.float64),
        }
        assert sum(v.size for v in self.weights.values()) == 534
        self.training_loss = None
        self.epochs_trained = 0
        self.reset()

    def reset(self):
        self._h = np.zeros(16, dtype=np.float64)

    def step_probability(self, visible, action):
        w = self.weights
        self._h = np.tanh(w["Wx"] @ _features(visible, action) +
                          w["Wh"] @ self._h + w["bh"])
        return tuple(float(z) for z in _sigmoid(w["Wo"] @ self._h + w["bo"]))

    def rollout(self, initial, actions):
        if len(actions) > STEPS:
            raise ValueError("episode budget exceeded")
        self.reset()
        x = _valid_bits(initial)
        predictions = []
        for action in actions:
            p = self.step_probability(x, action)
            x = tuple(int(z > .5) for z in p)
            predictions.append((x, p))
        return tuple(predictions)

    def _forward(self, xs):
        w = self.weights
        hidden = [np.zeros((len(xs), 16), dtype=np.float64)]
        logits = []
        for t in range(STEPS):
            h = np.tanh(xs[:, t] @ w["Wx"].T + hidden[-1] @ w["Wh"].T + w["bh"])
            hidden.append(h)
            logits.append(h @ w["Wo"].T + w["bo"])
        return hidden, np.stack(logits, axis=1)

    def _grad(self, xs, ys):
        w = self.weights
        hidden, logits = self._forward(xs)
        loss = float(np.mean(np.logaddexp(0.0, logits) - ys * logits))
        dl = (_sigmoid(logits) - ys) / float(ys.size)
        grads = {name: np.zeros_like(value) for name, value in w.items()}
        dh_next = np.zeros_like(hidden[-1])
        for t in reversed(range(STEPS)):
            g = dl[:, t]
            grads["Wo"] += g.T @ hidden[t + 1]
            grads["bo"] += np.sum(g, axis=0)
            dh = g @ w["Wo"] + dh_next
            dz = dh * (1.0 - hidden[t + 1] ** 2)
            grads["Wx"] += dz.T @ xs[:, t]
            grads["Wh"] += dz.T @ hidden[t]
            grads["bh"] += np.sum(dz, axis=0)
            dh_next = dz @ w["Wh"]
        return loss, grads

    def train(self, episodes, *, epochs=ORIGINAL_EPOCHS, development=False):
        if type(development) is not bool or type(epochs) is not int:
            raise ValueError("invalid training regime")
        if development:
            if not 1 <= epochs <= 24:
                raise ValueError("DEV can use only 1..24 steps")
        elif epochs != ORIGINAL_EPOCHS:
            raise ValueError("original source training budget frozen at 1800 epochs")
        _, xs, ys = _training_arrays(episodes)
        moments = {name: np.zeros_like(value) for name, value in self.weights.items()}
        velocity = {name: np.zeros_like(value) for name, value in self.weights.items()}
        for epoch in range(1, epochs + 1):
            _, grad = self._grad(xs, ys)
            _adam(self.weights, grad, moments, velocity, epoch)
        self.training_loss = self._grad(xs, ys)[0]
        self.epochs_trained = epochs
        return self.training_loss

    def source_fit(self, episodes):
        clean = validate_episodes(episodes)
        correct = 0
        for episode in clean:
            self.reset()
            for x, action, y in episode:
                p = self.step_probability(x, action)
                correct += sum(int(int(z > .5) == label) for z, label in zip(p, y))
        self.reset()
        return correct / (len(clean) * STEPS * N)


class GradientMemoryless:
    """History-erased 10->16->6 tanh network, same optimizer and fixed epochs."""
    def __init__(self, seed):
        if seed not in SEEDS or type(seed) is not int:
            raise ValueError("unregistered control seed")
        rng = np.random.Generator(np.random.PCG64(seed))
        self.weights = {
            "Wx": rng.normal(0.0, .1, size=(16, 10)),
            "bh": np.zeros(16, dtype=np.float64),
            "Wo": rng.normal(0.0, .1, size=(N, 16)),
            "bo": np.zeros(N, dtype=np.float64)
        }
        self.training_loss = None
        self.epochs_trained = 0

    def probability(self, visible, action):
        w = self.weights
        h = np.tanh(w["Wx"] @ _features(visible, action) + w["bh"])
        return tuple(float(z) for z in _sigmoid(w["Wo"] @ h + w["bo"]))

    def train(self, episodes, *, epochs=ORIGINAL_EPOCHS, development=False):
        if type(development) is not bool or type(epochs) is not int:
            raise ValueError("invalid regime")
        if development:
            if not 1 <= epochs <= 24: raise ValueError("DEV budget exceeded")
        elif epochs != ORIGINAL_EPOCHS:
            raise ValueError("original budget frozen")
        _, xs, ys = _training_arrays(episodes)
        xs = xs.reshape((-1, 10))
        ys = ys.reshape((-1, N))
        w = self.weights
        moments = {name: np.zeros_like(value) for name, value in w.items()}
        velocity = {name: np.zeros_like(value) for name, value in w.items()}
        def loss_grad():
            h = np.tanh(xs @ w["Wx"].T + w["bh"])
            z = h @ w["Wo"].T + w["bo"]
            loss = float(np.mean(np.logaddexp(0.0, z) - ys * z))
            dz = (_sigmoid(z) - ys) / ys.size
            dh = dz @ w["Wo"] * (1 - h * h)
            return loss, {
                "Wx": dh.T @ xs,
                "bh": np.sum(dh, axis=0),
                "Wo": dz.T @ h,
                "bo": np.sum(dz, axis=0)
            }
        for epoch in range(1, epochs + 1):
            _, grads = loss_grad()
            _adam(w, grads, moments, velocity, epoch)
        self.training_loss = loss_grad()[0]
        self.epochs_trained = epochs
        return self.training_loss
