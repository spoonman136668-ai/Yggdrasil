"""CCE06 trainable compact recurrent neural comparator: public data only.

Standard-library tanh RNN trained with truncated BPTT and Adam; output is a
4-class next-observation distribution. No evaluator/oracle, teacher, teacher
weights, fixed reservoir, suffix table, or protected CAL/PRIMARY dependency.
The bounded truncation is a declared engineering limitation, not proof of
full convergence or a strongest neural baseline.
"""
from __future__ import annotations

import math
import random
from calibration_controls import code, validated, multichannel_brier


def _softmax(logits):
    hi = max(logits)
    e = [math.exp(v - hi) for v in logits]
    total = sum(e)
    return tuple(v / total for v in e)


def _features(observed, action):
    if type(action) is not int or action not in (0, 1, 2):
        raise ValueError('CCE06_RNN_INVALID_ACTION')
    code(observed)
    return [float(observed[0]), float(observed[1])] + [float(action == a) for a in range(3)]


class TrainableRecurrentEstimator:
    """One-layer tanh recurrent state, trained by gradients through time.

    The recurrent matrix is fitted and updated; unlike a random reservoir it
    contributes gradients on every training block. 4-way softmax prediction,
    with optional TRAIN-only early stopping on public selection streams.
    """
    def __init__(self, hidden=8, seed=60806):
        if type(hidden) is not int or hidden not in (4, 8, 12, 16) or type(seed) is not int or seed < 0:
            raise ValueError('CCE06_RNN_INVALID_CAPACITY')
        rng = random.Random(seed)
        self.hidden = hidden
        self.seed = seed
        k = 1 / math.sqrt(hidden)
        self.wx = [[rng.uniform(-k, k) for _ in range(5)] for _ in range(hidden)]
        self.wh = [[rng.uniform(-k, k) for _ in range(hidden)] for _ in range(hidden)]
        self.bh = [0.] * hidden
        self.wo = [[rng.uniform(-k, k) for _ in range(hidden)] for _ in range(4)]
        self.bo = [0.] * 4
        self.fitted = False
        self.train_events = 0
        self.trace = []
        self.best_epoch = None
        self.early_stopped = False

    def _params(self):
        return self.wx + self.wh + [self.bh] + self.wo + [self.bo]

    def _copy(self):
        return [row[:] for row in self._params()]

    def _restore(self, copy):
        for row, saved in zip(self._params(), copy):
            row[:] = saved[:]

    def new_state(self):
        if not self.fitted:
            raise ValueError('CCE06_RNN_NOT_FITTED')
        return (0.,) * self.hidden

    def _step(self, state, observed, action):
        if type(state) not in (tuple, list) or len(state) != self.hidden or any(
                type(v) not in (int, float) or not math.isfinite(v) for v in state):
            raise ValueError('CCE06_RNN_INVALID_STATE')
        x = _features(observed, action)
        h = [math.tanh(self.bh[i] + sum(w * xi for w, xi in zip(self.wx[i], x))
                       + sum(w * hi for w, hi in zip(self.wh[i], state)))
             for i in range(self.hidden)]
        p = _softmax([self.bo[o] + sum(w * hi for w, hi in zip(self.wo[o], h))
                      for o in range(4)])
        return tuple(h), p

    def forecast(self, state, observed, action):
        if not self.fitted:
            raise ValueError('CCE06_RNN_NOT_FITTED')
        return self._step(state, observed, action)

    def predict(self, history, action):
        if not self.fitted:
            raise ValueError('CCE06_RNN_NOT_FITTED')
        state = self.new_state()
        if history:
            validated(history)
            for event in history:
                state, _ = self._step(state, event['observation'], event['action'])
            observed = history[-1]['next_observation']
        else:
            observed = [0, 0]  # Without a public first observation, no context exists.
        return self._step(state, observed, action)[1]

    def score(self, datasets):
        if not self.fitted:
            raise ValueError('CCE06_RNN_NOT_FITTED')
        loss, n = 0., 0
        for events in datasets:
            validated(events)
            state = self.new_state()
            for event in events:
                state, probs = self.forecast(state, event['observation'], event['action'])
                loss += multichannel_brier(probs, event['next_observation'])
                n += 1
        return loss / n

    def fit(self, train, *, epochs=30, lr=0.02, truncate=12,
            validation=None, patience=5, clip=1.0):
        if (self.fitted or type(train) not in (list, tuple) or not train or
                type(epochs) is not int or not 1 <= epochs <= 120 or
                type(truncate) is not int or not 2 <= truncate <= 64 or
                type(lr) not in (int, float) or not 0 < lr <= 0.1 or
                type(patience) is not int or not 2 <= patience <= 30 or
                type(clip) not in (int, float) or not 0 < clip <= 10):
            raise ValueError('CCE06_RNN_INVALID_FIT')
        for seq in train:
            validated(seq)
        if validation is not None:
            if type(validation) not in (tuple, list) or not validation:
                raise ValueError('CCE06_RNN_BAD_SELECTION')
            for seq in validation:
                validated(seq)
        self.train_events = sum(len(seq) for seq in train)
        params = self._params()
        m = [[0.] * len(row) for row in params]
        v = [[0.] * len(row) for row in params]
        step_num, best, waiting, snapshot = 0, math.inf, 0, None
        self.fitted = True  # enables frozen public-only scoring in early-stop
        for epoch in range(1, epochs + 1):
            loss, seen = 0., 0
            for seq in train:
                state = (0.,) * self.hidden
                for start in range(0, len(seq), truncate):
                    block = seq[start:start + truncate]
                    tape = []
                    for event in block:
                        following, prob = self._step(state, event['observation'], event['action'])
                        tape.append((state, _features(event['observation'], event['action']),
                                     following, prob, code(event['next_observation'])))
                        loss -= math.log(max(1e-12, prob[code(event['next_observation'])]))
                        seen += 1
                        state = following
                    grads = [[0.] * len(row) for row in params]
                    dh_next = [0.] * self.hidden
                    H = self.hidden
                    for prev, x, h, prob, target in reversed(tape):
                        logits = [prob[o] - float(o == target) for o in range(4)]
                        for o in range(4):
                            for j in range(H):
                                grads[2*H+1+o][j] += logits[o] * h[j]
                            grads[-1][o] += logits[o]
                        dh = [dh_next[j] + sum(self.wo[o][j] * logits[o] for o in range(4))
                              for j in range(H)]
                        dz = [dh[j] * (1 - h[j] ** 2) for j in range(H)]
                        next_back = [0.] * H
                        for j in range(H):
                            for k in range(5):
                                grads[j][k] += dz[j] * x[k]
                            for k in range(H):
                                grads[H+j][k] += dz[j] * prev[k]
                                next_back[k] += self.wh[j][k] * dz[j]
                            grads[2*H][j] += dz[j]
                        dh_next = next_back
                    # Clip *full block* gradient, rather than clipping each event.
                    norm = math.sqrt(sum(g*g for row in grads for g in row))
                    scale = min(1.0, float(clip) / max(1e-12, norm))
                    step_num += 1
                    b1, b2 = 0.9, 0.999
                    for row, grad, mr, vr in zip(params, grads, m, v):
                        for k in range(len(row)):
                            g = grad[k] * scale
                            mr[k] = b1 * mr[k] + (1-b1) * g
                            vr[k] = b2 * vr[k] + (1-b2) * (g*g)
                            mh = mr[k] / (1 - b1 ** step_num)
                            vh = vr[k] / (1 - b2 ** step_num)
                            row[k] -= float(lr) * mh / (math.sqrt(vh) + 1e-8)
            metric = self.score(validation) if validation is not None else loss / seen
            if not math.isfinite(metric):
                raise ValueError('CCE06_RNN_NONFINITE_TRAIN')
            self.trace.append(dict(epoch=epoch, train_cross_entropy=loss / seen,
                                   train_only_select_brier=(metric if validation is not None else None)))
            if validation is not None:
                if metric < best - 1e-6:
                    best, waiting, snapshot = metric, 0, self._copy()
                    self.best_epoch = epoch
                else:
                    waiting += 1
                    if waiting >= patience:
                        self.early_stopped = True
                        break
        if snapshot is not None:
            self._restore(snapshot)
        elif validation is None:
            self.best_epoch = len(self.trace)
        return self
