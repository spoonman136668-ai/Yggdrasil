"""MR34J3C stage-only reward-trained memory policy candidates.

No original source access and no full scientific training. The only learning
signal passed into `update()` is the legitimate scalar terminal reward;
there is no ground-truth hidden branch or source-private label.
Both learners are explicitly provisional until authoritative preregistration.
"""
from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass

import numpy as np
from public_scaffold import KEY, BALL, NORTH, PublicView, ProtocolBlocked

EPS = 1e-12


def sigmoid(x):
    v = float(x)
    return 1. / (1. + np.exp(-np.clip(v, -36., 36.)))


def as_signal(view: PublicView, event: str) -> np.ndarray:
    """6 original-public-derived numbers: cue, fork, and two declared stage flags."""
    out = np.zeros(6, dtype=np.float64)
    if event in ("PUBLIC_CUE_EXPOSURE", "PUBLIC_FORK_OBJECT_EXPOSURE_AND_CHOICE") and view.direction != NORTH:
        raise ProtocolBlocked("STAGE_WITH_WRONG_PUBLIC_HEADING")
    if event == "PUBLIC_CUE_EXPOSURE":
        obj = view.front()
        if obj not in (KEY, BALL):
            raise ProtocolBlocked("LEARNER_CUE_NOT_VISIBLE")
        out[obj - KEY] = 1.
        out[4] = 1.
    elif event == "PUBLIC_FORK_OBJECT_EXPOSURE_AND_CHOICE":
        obj = view.obj(3, 4)
        if obj not in (KEY, BALL):
            raise ProtocolBlocked("LEARNER_FORK_NOT_VISIBLE")
        out[obj - KEY + 2] = 1.
        out[5] = 1.
    elif event == "":
        pass  # all-zero event, common public sensory band for scout navigation
    else:
        raise ProtocolBlocked("UNKNOWN_SHARED_STAGE_EVENT")
    return out


@dataclass(frozen=True)
class Episode:
    """Only public-view snapshots and preannounced stage tokens, no outcomes."""
    signals: tuple[tuple[float, ...], ...]

    @classmethod
    def from_public_events(cls, events: list[tuple[PublicView, str]]) -> "Episode":
        if not events:
            raise ProtocolBlocked("NO_PUBLIC_EPISODE_EVENTS")
        signals = tuple(tuple(float(x) for x in as_signal(view, event)) for view, event in events)
        a = [i for i, x in enumerate(signals) if x[4] == 1.]
        b = [i for i, x in enumerate(signals) if x[5] == 1.]
        if len(a) != 1 or len(b) != 1 or a[0] >= b[0]:
            raise ProtocolBlocked("INCOMPLETE_OR_UNORDERED_PUBLIC_EXPOSURE")
        return cls(signals)

    @property
    def cue(self):
        return np.asarray(next(x[:2] for x in self.signals if x[4] == 1.), dtype=np.float64)

    @property
    def fork(self):
        return np.asarray(next(x[2:4] for x in self.signals if x[5] == 1.), dtype=np.float64)

    @property
    def intervening(self):
        a = next(i for i, x in enumerate(self.signals) if x[4] == 1.)
        b = next(i for i, x in enumerate(self.signals) if x[5] == 1.)
        return b - a - 1


class ReinforceBase:
    def __init__(self, seed: int, lr: float):
        self.rng = np.random.default_rng(int(seed))
        self.lr = float(lr)
        self.episodes_fit = 0
        self.reward_baseline = 0.5  # immutable, avoids held-dependent baseline fit

    def action(self, ep: Episode, evaluation=False):
        p = sigmoid(self.logit_and_gradient(ep)[0])
        north = (p >= 0.5) if evaluation else bool(self.rng.random() < p)
        return ("north" if north else "south"), p

    def update(self, ep: Episode, selected: str, reward: float):
        if selected not in ("north", "south") or not np.isfinite(reward) or not 0. <= reward <= 1.:
            raise ProtocolBlocked("REWARD_ONLY_UPDATE_INVALID")
        logit, grads = self.logit_and_gradient(ep)
        p = sigmoid(logit)
        factor = (float(reward) - self.reward_baseline) * ((1. if selected == "north" else 0.) - p)
        for k in sorted(grads):
            self.weights[k] = self.weights[k] + self.lr * factor * grads[k]
            if not np.isfinite(self.weights[k]).all():
                raise ProtocolBlocked("NONFINITE_REWARD_UPDATE")
        self.episodes_fit += 1

    def snapshot(self):
        return json.dumps({"kind": type(self).__name__, "lr": self.lr,
                           "episodes_fit": self.episodes_fit,
                           "baseline": self.reward_baseline,
                           "weights": {k: self.weights[k].tolist() for k in sorted(self.weights)},
                           "rng": self.rng.bit_generator.state},
                          sort_keys=True, separators=(",", ":"), allow_nan=False)

    @classmethod
    def restore(cls, raw: str):
        obj = json.loads(raw)
        if obj["kind"] != cls.__name__:
            raise ProtocolBlocked("CHECKPOINT_KIND_MISMATCH")
        inst = cls(0, float(obj["lr"]))
        for k in inst.weights:
            inst.weights[k] = np.asarray(obj["weights"][k], dtype=np.float64)
            if inst.weights[k].shape != inst.expected_shapes[k]:
                raise ProtocolBlocked("CHECKPOINT_WEIGHT_SHAPE_MISMATCH")
        inst.episodes_fit = int(obj["episodes_fit"])
        inst.reward_baseline = float(obj["baseline"])
        inst.rng.bit_generator.state = obj["rng"]
        if inst.snapshot() != raw:
            raise ProtocolBlocked("CHECKPOINT_RESTORE_MISMATCH")
        return inst


class LearnedTrace17(ReinforceBase):
    """Two-dimensional *learned* cue encoder, learned persistence, bilinear readout.

    17 fitted scalars; no oracle cue matching. Learns only from rewarded branch
    choices. Stage events are public scaffold cues supplied identically to arms.
    """
    expected_shapes = {"W": (2, 2), "b": (2,), "d": (2,), "wm": (2,),
                       "wf": (2,), "X": (2, 2), "bo": ()}

    def __init__(self, seed: int, lr: float = 0.03):
        super().__init__(seed, lr)
        r = self.rng
        self.weights = {
            "W": r.normal(0, 0.05, (2,2)),
            "b": np.zeros(2, dtype=np.float64),
            "d": np.full(2, 4.59511985013459, dtype=np.float64), # 0.99 continuation
            "wm": r.normal(0, 0.05, 2),
            "wf": r.normal(0, 0.05, 2),
            "X": r.normal(0, 0.05, (2,2)),
            "bo": np.array(0., dtype=np.float64),
        }

    def logit_and_gradient(self, ep: Episode):
        x, f = ep.cue, ep.fork
        gap = ep.intervening
        w = self.weights
        q = np.tanh(w["W"] @ x + w["b"])
        s = np.asarray([sigmoid(v) for v in w["d"]])
        decay = s ** gap
        m = q * decay
        direct_m = w["wm"] + w["X"] @ f
        z = np.dot(w["wm"], m) + np.dot(w["wf"], f) + m @ w["X"] @ f + w["bo"].item()
        dq = direct_m * decay * (1. - q*q)
        grads = {
            "W": np.outer(dq, x),
            "b": dq,
            "d": direct_m * m * gap * (1.-s),
            "wm": m,
            "wf": f,
            "X": np.outer(m, f),
            "bo": np.array(1., dtype=np.float64)
        }
        return float(z), grads


class ConventionalRNN57(ReinforceBase):
    """Independently trained conventional tanh RNN plus bilinear readout, 57 weights.

    The bilinear feature is essential: deciding whether two 2-valued objects
    match is XOR-like and not generally linearly separable from two encodings.
    """
    expected_shapes = {"Wx": (4, 6), "Wh": (4, 4), "b": (4,), "v": (4,), "Y": (4, 2), "bo": ()}

    def __init__(self, seed: int, lr: float = 0.01):
        super().__init__(seed, lr)
        r = self.rng
        self.weights = {
            "Wx": r.normal(0, 0.05, (4, 6)),
            "Wh": np.eye(4, dtype=np.float64) * 0.97,
            "b": np.zeros(4, dtype=np.float64),
            "v": r.normal(0, 0.05, 4),
            "Y": r.normal(0, 0.05, (4, 2)),
            "bo": np.array(0., dtype=np.float64)
        }

    def logit_and_gradient(self, ep: Episode):
        w = self.weights
        x_list = [np.asarray(sig, dtype=np.float64) for sig in ep.signals]
        states = [np.zeros(4, dtype=np.float64)]
        for x in x_list:
            states.append(np.tanh(w["Wx"]@x + w["Wh"]@states[-1] + w["b"]))
        fork=ep.fork
        z = w["v"]@states[-1] + states[-1]@w["Y"]@fork + w["bo"].item()
        grad = {name: np.zeros_like(array) for name, array in w.items()}
        grad["v"] = states[-1].copy()
        grad["Y"] = np.outer(states[-1],fork)
        grad["bo"] = np.array(1., dtype=np.float64)
        dh = w["v"].copy() + w["Y"]@fork
        for t in range(len(x_list)-1, -1, -1):
            dh_pre = dh * (1. - states[t+1]**2)
            grad["Wx"] += np.outer(dh_pre, x_list[t])
            grad["Wh"] += np.outer(dh_pre, states[t])
            grad["b"] += dh_pre
            dh = w["Wh"].T @ dh_pre
        return float(z), grad


class ObservationOnly3(ReinforceBase):
    """Learned current-public-fork-only policy, exactly 3 parameters."""
    expected_shapes = {"wf": (2,), "bo": ()}
    def __init__(self, seed: int, lr: float = 0.03):
        super().__init__(seed, lr)
        self.weights = {"wf": self.rng.normal(0, 0.05, 2), "bo": np.array(0., dtype=np.float64)}
    def logit_and_gradient(self, ep: Episode):
        fork=ep.fork
        return float(self.weights["wf"]@fork+self.weights["bo"].item()), {"wf":fork,"bo":np.array(1.)}


def verify_capacity():
    return {c.__name__: int(sum(np.asarray(v).size for v in c(1).weights.values()))
            for c in (LearnedTrace17, ConventionalRNN57, ObservationOnly3)}


def fit_only_donor_cue(fit_public_cues: tuple[tuple[float, float], ...], evaluation_seed: int,
                       *, salt: int = 341303) -> tuple[float, float]:
    """Online-safe ablation: select a sealed FIT-only donor for DEV/HELD.

    The caller must freeze the donor array in ascending FIT source-seed order
    and its SHA before first DEV reset. No DEV/HELD observation or outcome
    can enter this lookup. A donor may equal the real cue; report this rate.
    """
    if len(fit_public_cues) != 768:
        raise ProtocolBlocked("FIT_ONLY_DONOR_POOL_NOT_COMPLETE")
    for pair in fit_public_cues:
        if tuple(pair) not in ((1.0, 0.0), (0.0, 1.0)):
            raise ProtocolBlocked("FIT_ONLY_DONOR_CUE_NOT_PUBLIC_BINARY")
    # One canonical index function; the evaluator cannot diverge from the
    # prospective attempt inventory or silently admit FIT/PREFLIGHT/OOV seeds.
    from source_attempt_intent import fit_only_donor_index
    try:
        donor_index = fit_only_donor_index(evaluation_seed, salt=salt)
    except ValueError as exc:
        raise ProtocolBlocked("EVALUATION_DONOR_SEED_OR_SALT_INVALID") from exc
    return tuple(fit_public_cues[donor_index])
