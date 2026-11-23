"""Y2-CCE02: bounded action-grounded signature ecology, DEV ONLY.

Learner sees only public (probe, observation, terminal action, reward).
It never receives hidden mechanism labels, world type or counterfactual
outcomes. No tokens, gradients, teacher weights or external model calls.
A single central selection gate remains an explicitly disclosed limitation.
"""

from __future__ import annotations

import hashlib
import json
import math

SCHEMA = "yggdrasil.y2.cce02.v1"
TRAIN_LIMIT = 512
MIN_COVERAGE = 12
MIN_VALUE = 0.08


def bit(x: int) -> bool:
    return type(x) is int and x in (0, 1)


def validate(probe: int, observation: int, terminal: int,
             reward: int) -> None:
    if not all(bit(v) for v in (probe, observation, terminal, reward)):
        raise ValueError("CCE02_PUBLIC_EVENT_INVALID")


def posterior(pair: list[int]) -> float:
    return (pair[1] + 1) / (pair[0] + pair[1] + 2)


class IdentityEcology:
    """Two probes x two public outcomes x two terminal actions.

    A contract is a learned action-effect *signature*, not a supplied world
    identity. Causality here is backed by randomized interventions in the
    synthetic environment; this class cannot establish identifiability.
    """

    def __init__(self) -> None:
        self.pooled = [[0, 0] for _ in range(2)]
        self.signatures = [[[[0, 0] for _ in range(2)]
                            for _ in range(2)] for _ in range(2)]
        self.observations = [[0, 0] for _ in range(2)]
        self.probe_n = [0, 0]
        self.gains = [0.0, 0.0]
        self.events = 0
        self.selected_probe: int | None = None
        self.frozen = False

    def p_reward(self, terminal: int, *, probe: int | None = None,
                 observation: int | None = None) -> float:
        if not bit(terminal) or (probe is None) != (observation is None):
            raise ValueError("CCE02_PREDICTION_INVALID")
        if probe is None:
            return posterior(self.pooled[terminal])
        if not bit(probe) or not bit(observation):
            raise ValueError("CCE02_PREDICTION_INVALID")
        return posterior(self.signatures[probe][observation][terminal])

    def observe(self, probe: int, observation: int,
                terminal: int, reward: int) -> None:
        validate(probe, observation, terminal, reward)
        if self.frozen or self.events >= TRAIN_LIMIT:
            raise ValueError("CCE02_TRAINING_FROZEN_OR_OVER_BUDGET")
        p0 = self.p_reward(terminal)
        p1 = self.p_reward(terminal, probe=probe,
                           observation=observation)
        self.gains[probe] += (p0 - reward) ** 2 - (p1 - reward) ** 2
        self.pooled[terminal][reward] += 1
        self.signatures[probe][observation][terminal][reward] += 1
        self.observations[probe][observation] += 1
        self.probe_n[probe] += 1
        self.events += 1

    def value(self, probe: int) -> float:
        if not bit(probe):
            raise ValueError("CCE02_PROBE_INVALID")
        total = self.probe_n[probe]
        return sum(
            (self.observations[probe][signal] + 1) / (total + 2)
            * max(self.p_reward(t, probe=probe, observation=signal)
                  for t in (0, 1))
            for signal in (0, 1)
        )

    def pooled_value(self) -> float:
        return max(self.p_reward(t) for t in (0, 1))

    def freeze(self) -> int | None:
        if self.frozen or self.events != TRAIN_LIMIT:
            raise ValueError("CCE02_FREEZE_REQUIRES_EXACT_TRAINING_BUDGET")
        qualified = []
        pooled = self.pooled_value()
        for probe in (0, 1):
            covered = all(
                sum(self.signatures[probe][z][t]) >= MIN_COVERAGE
                for z in (0, 1) for t in (0, 1)
            )
            val = self.value(probe)
            if (covered and val >= pooled + MIN_VALUE
                    and self.gains[probe] >= max(2.0, 0.01 * self.probe_n[probe])):
                qualified.append((val, probe))
        if qualified:
            self.selected_probe = sorted(qualified,
                                         key=lambda item: (-item[0], item[1]))[0][1]
        self.frozen = True
        return self.selected_probe

    def choose_probe(self) -> int:
        if not self.frozen:
            raise ValueError("CCE02_NOT_FROZEN")
        return 1 if self.selected_probe is None else self.selected_probe

    def choose_terminal(self, probe: int, observation: int,
                        *, conditional: bool = True) -> int:
        if not self.frozen or not bit(probe) or not bit(observation):
            raise ValueError("CCE02_DECISION_INVALID")
        options = [
            (self.p_reward(t, probe=probe, observation=observation)
             if conditional else self.p_reward(t)) for t in (0, 1)
        ]
        return 1 if options[1] > options[0] else 0

    def choose(self, observation: int) -> int:
        probe = self.choose_probe()
        return self.choose_terminal(probe, observation,
                                    conditional=self.selected_probe is not None)

    def snapshot(self) -> bytes:
        state = {
            "schema": SCHEMA, "events": self.events, "pooled": self.pooled,
            "signatures": self.signatures, "observations": self.observations,
            "probe_n": self.probe_n, "gains": self.gains,
            "selected_probe": self.selected_probe, "frozen": self.frozen,
        }
        raw = json.dumps(state, sort_keys=True, separators=(",", ":"),
                         allow_nan=False).encode("ascii")
        return b"CCE02." + hashlib.sha256(raw).hexdigest().encode("ascii") + b"." + raw

    @classmethod
    def restore(cls, value: bytes) -> "IdentityEcology":
        if type(value) is not bytes:
            raise ValueError("CCE02_CHECKPOINT_REJECTED")
        parts = value.split(b".", 2)
        if (len(parts) != 3 or parts[0] != b"CCE02"
                or len(parts[1]) != 64
                or hashlib.sha256(parts[2]).hexdigest().encode("ascii") != parts[1]):
            raise ValueError("CCE02_CHECKPOINT_REJECTED")
        try:
            state = json.loads(parts[2])
            if type(state) is not dict or set(state) != {
                "schema", "events", "pooled", "signatures", "observations",
                "probe_n", "gains", "selected_probe", "frozen"
            } or state["schema"] != SCHEMA:
                raise ValueError("CCE02_CHECKPOINT_SCHEMA_INVALID")
            obj = cls()
            if (type(state["events"]) is not int
                    or not 0 <= state["events"] <= TRAIN_LIMIT
                    or type(state["frozen"]) is not bool
                    or (state["frozen"] and state["events"] != TRAIN_LIMIT)
                    or (not state["frozen"] and state["selected_probe"] is not None)
                    or (state["selected_probe"] is not None
                        and not bit(state["selected_probe"]))):
                raise ValueError("CCE02_CHECKPOINT_METADATA_INVALID")
            for array, shape in ((state["pooled"], (2, 2)),
                                 (state["signatures"], (2, 2, 2, 2)),
                                 (state["observations"], (2, 2)),
                                 (state["probe_n"], (2,))):
                def check(item, dims):
                    if dims:
                        if type(item) is not list or len(item) != dims[0]:
                            raise ValueError("CCE02_CHECKPOINT_SHAPE_INVALID")
                        for part in item:
                            check(part, dims[1:])
                    elif type(item) is not int or item < 0 or item > TRAIN_LIMIT:
                        raise ValueError("CCE02_CHECKPOINT_COUNT_INVALID")
                check(array, shape)
            if (type(state["gains"]) is not list
                    or len(state["gains"]) != 2
                    or any(type(g) not in (float, int) or not math.isfinite(g)
                           or abs(g) > TRAIN_LIMIT for g in state["gains"])):
                raise ValueError("CCE02_CHECKPOINT_GAIN_INVALID")
            obj.events = state["events"]
            obj.pooled = state["pooled"]
            obj.signatures = state["signatures"]
            obj.observations = state["observations"]
            obj.probe_n = state["probe_n"]
            obj.gains = state["gains"]
            obj.selected_probe = state["selected_probe"]
            obj.frozen = state["frozen"]
            if (sum(sum(x) for x in obj.pooled) != obj.events
                    or sum(obj.probe_n) != obj.events
                    or any(sum(obj.observations[p]) != obj.probe_n[p]
                           for p in (0, 1))
                    or any(sum(sum(sum(t) for t in z) for z in obj.signatures[p])
                           != obj.probe_n[p] for p in (0, 1))
                    or any(
                        sum(obj.signatures[p][z][t][reward]
                            for p in (0, 1) for z in (0, 1)) != obj.pooled[t][reward]
                        for t in (0, 1) for reward in (0, 1))
                    or any(
                        sum(sum(obj.signatures[p][z][t]) for t in (0, 1))
                        != obj.observations[p][z]
                        for p in (0, 1) for z in (0, 1))):
                raise ValueError("CCE02_CHECKPOINT_COUNTS_INCONSISTENT")
            return obj
        except (UnicodeError, ValueError, TypeError, KeyError) as exc:
            raise ValueError("CCE02_CHECKPOINT_REJECTED") from exc
