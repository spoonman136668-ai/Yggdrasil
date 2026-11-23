"""CCE06 public-data controls. Training never imports calibration_worlds.

Engineering-only implementations: suffix table and EM-fitted action HMM.
Not a complete or independently qualified strongest-comparator portfolio.
"""
from __future__ import annotations

import math
import random


def code(bits) -> int:
    if type(bits) is not list or len(bits) != 2 or any(type(x) is not int or x not in (0, 1) for x in bits):
        raise ValueError("CCE06_BAD_PUBLIC_OBSERVATION")
    return bits[0] * 2 + bits[1]


def validated(events):
    if type(events) not in (list, tuple) or len(events) < 1:
        raise ValueError("CCE06_EMPTY_EVENTS")
    obs = []
    actions = []
    for idx, e in enumerate(events):
        if type(e) is not dict or set(e) != {"observation", "action", "next_observation"}:
            raise ValueError("CCE06_BAD_EVENT_SCHEMA")
        a = e["action"]
        if type(a) is not int or a not in (0, 1, 2):
            raise ValueError("CCE06_BAD_ACTION")
        o, n = code(e["observation"]), code(e["next_observation"])
        if idx == 0:
            obs.append(o)
        elif obs[-1] != o:
            raise ValueError("CCE06_DISCONTINUOUS_EVENT")
        obs.append(n)
        actions.append(a)
    return obs, actions


def normalize(values):
    z = sum(values)
    if not math.isfinite(z) or z <= 0:
        raise ValueError("CCE06_NONFINITE_PROBABILITY")
    return tuple(v / z for v in values)


class FullSuffixTable:
    """Counts full public contexts; depth selection must use TRAIN only."""
    def __init__(self, depth: int):
        if type(depth) is not int or not 1 <= depth <= 8:
            raise ValueError("CCE06_BAD_DEPTH")
        self.depth = depth
        self.counts = {}
        self.samples = 0

    def fit(self, datasets):
        if self.samples:
            raise ValueError("CCE06_ALREADY_FIT")
        for events in datasets:
            obs, actions = validated(events)
            history = []
            for t, action in enumerate(actions):
                # Fit all backoff contexts, never from calibration eval.
                for length in range(min(self.depth, len(history)) + 1):
                    k = (action, tuple(history[-length:]) if length else ())
                    self.counts.setdefault(k, [0, 0, 0, 0])[obs[t + 1]] += 1
                history.append((obs[t], action))
                self.samples += 1
        if not self.samples:
            raise ValueError("CCE06_NO_TRAIN_DATA")
        return self

    def predict(self, past_events, action):
        if not self.samples or type(action) is not int or action not in (0, 1, 2):
            raise ValueError("CCE06_UNTRAINED_OR_BAD_ACTION")
        history = []
        if past_events:
            observations, actions = validated(past_events)
            history = list(zip(observations[:-1], actions))
        for length in range(min(self.depth, len(history)), -1, -1):
            k = (action, tuple(history[-length:]) if length else ())
            if k in self.counts:
                counts = self.counts[k]
                return normalize([c + 1 for c in counts])
        return (0.25, 0.25, 0.25, 0.25)


class ActionHMM:
    """Discrete action-conditioned HMM, fitted by public-sequence Baum-Welch.

    No latent-truth seeding. This is a candidate control implementation;
    convergence, dimensional selection, CPU and robustness need qualification.
    """
    def __init__(self, hidden: int, seed: int):
        if type(hidden) is not int or not 2 <= hidden <= 8:
            raise ValueError("CCE06_BAD_HIDDEN_CAPACITY")
        rng = random.Random(seed)
        self.hidden = hidden
        self.pi = normalize([rng.random() + .1 for _ in range(hidden)])
        self.emit = [normalize([rng.random() + .1 for _ in range(4)]) for _ in range(hidden)]
        self.trans = [[normalize([rng.random() + .1 for _ in range(hidden)])
                       for _ in range(hidden)] for _ in range(3)]
        self.trace = []
        self.fitted = False
        self.samples = 0

    def _forward(self, obs, acts):
        h = self.hidden
        first = [self.pi[i] * self.emit[i][obs[0]] for i in range(h)]
        scale = [sum(first)]
        if scale[0] <= 0:
            raise ValueError("CCE06_ZERO_LIKELIHOOD")
        alpha = [tuple(x / scale[0] for x in first)]
        for t, action in enumerate(acts):
            row = [self.emit[j][obs[t + 1]] *
                   sum(alpha[t][i] * self.trans[action][i][j] for i in range(h))
                   for j in range(h)]
            z = sum(row)
            if z <= 0:
                raise ValueError("CCE06_ZERO_LIKELIHOOD")
            alpha.append(tuple(x / z for x in row))
            scale.append(z)
        return alpha, scale

    def likelihood(self, datasets):
        total = 0.0
        for events in datasets:
            o, a = validated(events)
            _, scales = self._forward(o, a)
            total += sum(math.log(v) for v in scales)
        return total

    def fit(self, datasets, max_iters=50, min_iters=3, tol=1e-6):
        if self.fitted or type(max_iters) is not int or not 3 <= max_iters <= 100:
            raise ValueError("CCE06_INVALID_FIT")
        if type(datasets) not in (tuple, list) or not datasets:
            raise ValueError("CCE06_NO_TRAIN_DATA")
        sequences = [validated(e) for e in datasets]
        self.samples = sum(len(a) for _, a in sequences)
        h = self.hidden
        for iteration in range(max_iters):
            init = [0.01] * h
            emissions = [[0.01] * 4 for _ in range(h)]
            transitions = [[[0.01] * h for _ in range(h)] for _ in range(3)]
            for obs, acts in sequences:
                alpha, scales = self._forward(obs, acts)
                beta = [[1.0] * h for _ in range(len(obs))]
                for t in range(len(acts) - 1, -1, -1):
                    action = acts[t]
                    beta[t] = [sum(self.trans[action][i][j] * self.emit[j][obs[t + 1]] *
                                   beta[t + 1][j] for j in range(h)) / scales[t + 1]
                               for i in range(h)]
                gamma = [normalize([alpha[t][i] * beta[t][i] for i in range(h)])
                         for t in range(len(obs))]
                for i in range(h):
                    init[i] += gamma[0][i]
                for t, symbol in enumerate(obs):
                    for i in range(h):
                        emissions[i][symbol] += gamma[t][i]
                for t, action in enumerate(acts):
                    xi = [[alpha[t][i] * self.trans[action][i][j] *
                           self.emit[j][obs[t + 1]] * beta[t + 1][j]
                           for j in range(h)] for i in range(h)]
                    z = sum(map(sum, xi))
                    if z <= 0:
                        raise ValueError("CCE06_ZERO_XI")
                    for i in range(h):
                        for j in range(h):
                            transitions[action][i][j] += xi[i][j] / z
            self.pi = normalize(init)
            self.emit = [normalize(row) for row in emissions]
            self.trans = [[normalize(row) for row in matrix] for matrix in transitions]
            current = self.likelihood(datasets)
            self.trace.append(current)
            if len(self.trace) >= min_iters and abs(current - self.trace[-2]) <= tol * max(1.0, abs(self.trace[-2])):
                break
        self.fitted = True
        return self

    def predict(self, past_events, action):
        if not self.fitted or type(action) is not int or action not in (0, 1, 2):
            raise ValueError("CCE06_UNTRAINED_OR_BAD_ACTION")
        if past_events:
            obs, acts = validated(past_events)
            alpha, _ = self._forward(obs, acts)
            belief = alpha[-1]
        else:
            belief = self.pi
        state = [sum(belief[i] * self.trans[action][i][j] for i in range(self.hidden))
                 for j in range(self.hidden)]
        return normalize([sum(state[j] * self.emit[j][out] for j in range(self.hidden))
                          for out in range(4)])


def multichannel_brier(probs, observed):
    """Mean binary Brier across two channels; never score test data during fit."""
    if len(probs) != 4 or any(not math.isfinite(p) or p < 0 for p in probs) or abs(sum(probs) - 1) > 1e-8:
        raise ValueError("CCE06_INVALID_DISTRIBUTION")
    outcome = code(observed)
    p0 = probs[2] + probs[3]
    p1 = probs[1] + probs[3]
    return 0.5 * ((p0 - (outcome // 2)) ** 2 + (p1 - (outcome % 2)) ** 2)
