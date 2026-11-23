"""CCE04: locally scored finite causal-belief contracts for hidden binary states.

Synthetic development only. Neither the true hidden bit nor the generator's
action/noise parameters are supplied to this learner. The 36 fixed candidate
structures and central evidence competition are explicitly *not* proof of
autonomous discovery, generalization or AGI.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import math

TRAIN_EPISODES = 128
TRAIN_ACTIONS = 12
NULL_PENALTY_MULTIPLIER = 2.0
COARSE_NOISE = (0.1, 0.2, 0.3)
COARSE_DRIFT = (0.03, 0.10, 0.20)
FINE_NOISE = tuple(i * 0.05 for i in range(1, 10))
FINE_DRIFT = tuple(i * 0.02 for i in range(1, 13))
ACTION_FAMILIES = tuple(itertools.product((0, 1), repeat=2))
SCHEMA = "yggdrasil.y2.cce04.v1"


def check_history(observations: tuple[int, ...], actions: tuple[int, ...]) -> None:
    if (type(observations) is not tuple or type(actions) is not tuple
            or len(observations) != len(actions) + 1 or not observations
            or any(type(x) is not int or x not in (0, 1)
                   for x in observations + actions)):
        raise ValueError("CCE04_PUBLIC_HISTORY_INVALID")


def templates(coarse: bool = True, no_action: bool = False) -> tuple:
    noise = COARSE_NOISE if coarse else FINE_NOISE
    drift = COARSE_DRIFT if coarse else FINE_DRIFT
    families = ((0, 0),) if no_action else ACTION_FAMILIES
    return tuple((flip, eps, rate)
                 for flip in families for eps in noise for rate in drift)


def observe_posterior(p: float, o: int, noise: float) -> tuple[float, float]:
    likelihood_one = 1.0 - noise if o else noise
    likelihood_zero = noise if o else 1.0 - noise
    mass_one = p * likelihood_one
    mass_zero = (1.0 - p) * likelihood_zero
    probability = mass_one + mass_zero
    return mass_one / probability, math.log(probability)


def move(p: float, action: int, flip: tuple[int, int], drift: float) -> float:
    effective = drift if flip[action] == 0 else 1.0 - drift
    return p * (1.0 - effective) + (1.0 - p) * effective


def filter_history(observations: tuple[int, ...], actions: tuple[int, ...],
                   params: tuple) -> tuple[float, float]:
    check_history(observations, actions)
    flips, noise, drift = params
    p, score = observe_posterior(0.5, observations[0], noise)
    for action, observation in zip(actions, observations[1:]):
        p, likelihood = observe_posterior(move(p, action, flips, drift),
                                          observation, noise)
        score += likelihood
    return p, score


def predict_future(observations: tuple[int, ...], actions: tuple[int, ...],
                   future_actions: tuple[int, ...], params: tuple | None) -> tuple[float, ...]:
    check_history(observations, actions)
    if type(future_actions) is not tuple or any(type(a) is not int or a not in (0, 1)
                                                 for a in future_actions):
        raise ValueError("CCE04_FUTURE_ACTIONS_INVALID")
    if params is None:
        return (0.5,) * len(future_actions)
    p, _ = filter_history(observations, actions, params)
    flips, noise, drift = params
    forecasts = []
    for action in future_actions:
        p = move(p, action, flips, drift)
        forecasts.append(noise + (1.0 - 2.0 * noise) * p)
    return tuple(forecasts)


def validate_episodes(episodes: tuple) -> None:
    if type(episodes) is not tuple or len(episodes) != TRAIN_EPISODES:
        raise ValueError("CCE04_TRAINING_EPISODES_INVALID")
    for obs, actions in episodes:
        check_history(obs, actions)
        if len(actions) != TRAIN_ACTIONS:
            raise ValueError("CCE04_TRAINING_HORIZON_INVALID")


def fit_grid(episodes: tuple, grid: tuple) -> tuple[tuple | None, float, float]:
    """Select using public prequential likelihood; iid penalizes complexity."""
    validate_episodes(episodes)
    nobs = TRAIN_EPISODES * (TRAIN_ACTIONS + 1)
    null_ll = -nobs * math.log(2.0)
    best_ll = float("-inf")
    best = None
    for params in grid:
        score = sum(filter_history(obs, actions, params)[1] for obs, actions in episodes)
        if score > best_ll:
            best_ll, best = score, params
    if best_ll - null_ll <= NULL_PENALTY_MULTIPLIER * math.log(nobs):
        return None, null_ll, best_ll
    return best, best_ll, best_ll


class CausalBeliefEcology:
    def __init__(self) -> None:
        self.selected: tuple | None = None
        self.score: float | None = None
        self.best_stateful_score: float | None = None
        self.trained = False

    def fit(self, episodes: tuple) -> None:
        if self.trained:
            raise ValueError("CCE04_ALREADY_FROZEN")
        params, score, best = fit_grid(episodes, templates(coarse=True))
        self.selected = params
        self.score = score
        self.best_stateful_score = best
        self.trained = True

    def predict(self, observations: tuple[int, ...], actions: tuple[int, ...],
                future_actions: tuple[int, ...]) -> tuple[float, ...]:
        if not self.trained:
            raise ValueError("CCE04_UNTRAINED")
        return predict_future(observations, actions, future_actions, self.selected)

    def snapshot(self) -> bytes:
        state = {"schema": SCHEMA, "trained": self.trained,
                 "selected": None if self.selected is None else
                 [list(self.selected[0]), self.selected[1], self.selected[2]],
                 "score": self.score, "best_stateful_score": self.best_stateful_score}
        raw = json.dumps(state, separators=(",", ":"), sort_keys=True,
                         allow_nan=False).encode("ascii")
        return b"CCE04." + hashlib.sha256(raw).hexdigest().encode("ascii") + b"." + raw

    @classmethod
    def restore(cls, packed: bytes) -> "CausalBeliefEcology":
        if type(packed) is not bytes:
            raise ValueError("CCE04_SNAPSHOT_REJECTED")
        parts = packed.split(b".", 2)
        if (len(parts) != 3 or parts[0] != b"CCE04" or len(parts[1]) != 64
                or hashlib.sha256(parts[2]).hexdigest().encode("ascii") != parts[1]):
            raise ValueError("CCE04_SNAPSHOT_REJECTED")
        try:
            data = json.loads(parts[2])
            if (type(data) is not dict or set(data) !=
                    {"schema", "trained", "selected", "score", "best_stateful_score"}
                    or data["schema"] != SCHEMA or type(data["trained"]) is not bool):
                raise ValueError("CCE04_STATE_INVALID")
            obj = cls()
            if data["trained"]:
                params = data["selected"]
                if params is not None:
                    if (type(params) is not list or len(params) != 3
                            or type(params[0]) is not list):
                        raise ValueError("CCE04_PARAMS_INVALID")
                    params = (tuple(params[0]), params[1], params[2])
                    if params not in templates(coarse=True):
                        raise ValueError("CCE04_PARAMS_INVALID")
                for key in ("score", "best_stateful_score"):
                    value = data[key]
                    if type(value) not in (float, int) or not math.isfinite(value):
                        raise ValueError("CCE04_SCORES_INVALID")
                nobs = TRAIN_EPISODES * (TRAIN_ACTIONS + 1)
                null_ll = -nobs * math.log(2.0)
                if (data["best_stateful_score"] < null_ll - 10 * nobs
                        or data["best_stateful_score"] > 0
                        or (params is None and abs(data["score"] - null_ll) > 1e-8)
                        or (params is not None and
                            abs(data["score"] - data["best_stateful_score"]) > 1e-8)
                        or (params is None and data["best_stateful_score"] - null_ll
                            > NULL_PENALTY_MULTIPLIER * math.log(nobs) + 1e-8)
                        or (params is not None and data["best_stateful_score"] - null_ll
                            <= NULL_PENALTY_MULTIPLIER * math.log(nobs))):
                    raise ValueError("CCE04_EVIDENCE_INCONSISTENT")
                obj.selected, obj.score = params, data["score"]
                obj.best_stateful_score = data["best_stateful_score"]
                obj.trained = True
            elif any(data[k] is not None for k in
                     ("selected", "score", "best_stateful_score")):
                raise ValueError("CCE04_UNTRAINED_STATE_INVALID")
            return obj
        except (ValueError, KeyError, UnicodeError, TypeError) as exc:
            raise ValueError("CCE04_SNAPSHOT_REJECTED") from exc
