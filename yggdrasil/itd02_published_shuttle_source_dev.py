"""Published original Shuttle POMDP source adapter — isolated PUBLIC development.

This is a *source-side* adapter to Chrisman's original published benchmark
text served at https://www.pomdp.org/examples/shuttle.95.POMDP.
It reads transition/observation/reward tables from the verified publisher's
2281-byte file; never implements an invented dynamics/reward/goal oracle.
Only the five public observations and source rewards reach the native model.
The actual hidden state and seeded RNG remain exclusively in source owner.

NOT an FSA protected first-use permit, independent science result, or accepted
source/holdout. Loading and validating the text is source discovery. Stepping
the source requires separate, existing owner-approved public-development role.
"""
from __future__ import annotations

import hashlib
import math
import random
import re
from pathlib import Path
from typing import Mapping

ORIGINAL_PUBLISHER_URL = "https://www.pomdp.org/examples/shuttle.95.POMDP"
ORIGINAL_PUBLISHER_SHA256 = "a69baec2d6e83e239bafa4c6b74faead794e7c91400bf69c7d3813ed114cea94"
ORIGINAL_PUBLISHER_BYTES = 2281
ACTIONS = ("TurnAround", "GoForward", "Backup")
OBSERVATIONS = ("LRV", "MRV", "docked_MRV", "Nothing", "docked_LRV")
MAX_EPISODE_STEPS = 512


class SourcePreflightDenied(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SourcePreflightDenied("ITD02_PUBLISHED_SHUTTLE_" + message)


def _row(line: str, count: int) -> tuple[float, ...]:
    parts = line.split()
    _require(len(parts) == count, "MATRIX_SHAPE")
    try:
        numbers = tuple(float(x) for x in parts)
    except ValueError as exc:
        raise SourcePreflightDenied("ITD02_PUBLISHED_SHUTTLE_NON_NUMERIC") from exc
    _require(all(math.isfinite(x) and 0 <= x <= 1 for x in numbers),
             "MATRIX_RANGE")
    _require(abs(sum(numbers) - 1.0) < 1e-10, "MATRIX_NOT_PROBABILITY")
    return numbers


def read_original_published_model(raw: bytes) -> dict:
    """Parse EXACT published source content, without taking any world action."""
    _require(type(raw) is bytes and len(raw) == ORIGINAL_PUBLISHER_BYTES,
             "FILE_SIZE")
    _require(hashlib.sha256(raw).hexdigest() == ORIGINAL_PUBLISHER_SHA256,
             "PUBLISHER_IDENTITY")
    try:
        source = raw.decode("ascii")
    except UnicodeDecodeError as exc:
        raise SourcePreflightDenied("ITD02_PUBLISHED_SHUTTLE_ENCODING") from exc
    # Original source comments contain background/source ambiguities; the
    # machine-readable tables, never comments, define original task dynamics.
    lines = [x.partition("#")[0].strip() for x in source.splitlines()]
    lines = [x for x in lines if x]
    expected_header = (
        "discount: 0.95", "values: reward", "states:  8",
        "actions: TurnAround GoForward Backup", "observations: 5",
    )
    _require(len(lines) >= 41 and lines[:5] == list(expected_header),
             "UNEXPECTED_HEADER")
    cursor = 5
    _require(lines[cursor] == "start:", "START_NOT_DECLARED")
    cursor += 1
    initial = _row(lines[cursor], 8)
    cursor += 1
    transitions = {}
    for action in ACTIONS:
        _require(lines[cursor] == "T: " + action, "ACTION_BLOCK_ORDER")
        cursor += 1
        rows = []
        for _ in range(8):
            rows.append(_row(lines[cursor], 8))
            cursor += 1
        transitions[action] = tuple(rows)
    _require(lines[cursor] == "O: *", "PUBLIC_OBSERVATION_BLOCK")
    cursor += 1
    observations = []
    for _ in range(8):
        observations.append(_row(lines[cursor], 5))
        cursor += 1
    reward = {}
    for line in lines[cursor:]:
        match = re.fullmatch(
            r"R:\s*(TurnAround|GoForward|Backup)\s*:\s*([0-7])"
            r"\s*:\s*([0-7])\s*:\s*\*\s+(-?\d+)", line)
        _require(match is not None, "REWARD_DIRECTIVE_INVALID")
        a, before, after, amount = match.groups()
        key = (a, int(before), int(after))
        _require(key not in reward and int(amount) in (-3, 10),
                 "REWARD_DUPLICATE_OR_CLASS")
        reward[key] = int(amount)
    _require(set(reward) == {
        ("GoForward", 1, 1),
        ("GoForward", 6, 6),
        ("Backup", 3, 0),
    }, "REWARD_RULE_IDENTITY")
    _require(reward[("Backup", 3, 0)] == 10 and
             reward[("GoForward", 1, 1)] == -3 and
             reward[("GoForward", 6, 6)] == -3,
             "REWARD_AMOUNT_IDENTITY")
    return {
        "source_sha256": ORIGINAL_PUBLISHER_SHA256,
        "initial": initial,
        "transitions": transitions,
        "observations": tuple(observations),
        "rewards": reward,
        "authority": "PUBLISHED_PUBLIC_DEVELOPMENT_SOURCE_ONLY",
        "scientific_first_use": False,
    }


def _draw(rng: random.Random, probabilities: tuple[float, ...]) -> int:
    position = rng.random()
    total = 0.0
    for i, p in enumerate(probabilities):
        total += p
        if position < total:
            return i
    return len(probabilities) - 1


class PublishedShuttleOwnerDev:
    """External source owner's role-scoped adapter, not a trained policy.

    Loading is harmless. To perform a source reset/step, an independently
    granted public FIT role and finite episode budget must be bound here by
    the source owner. This class does not authenticate that grant itself.
    It intentionally never presents the model with RNG/seed, source state,
    probability tables, state IDs or a privileged info dictionary.
    """

    def __init__(self, raw: bytes, *, seed: int, episode_steps: int,
                 development_role: str):
        self.model = read_original_published_model(raw)
        _require(type(seed) is int and 0 <= seed <= 2**63-1,
                 "SOURCE_SEED_INVALID")
        _require(type(episode_steps) is int and
                 1 <= episode_steps <= MAX_EPISODE_STEPS,
                 "FIT_INTERACTION_BUDGET_INVALID")
        _require(development_role == "OWNER_AUTHORIZED_PUBLIC_FIT_ONLY",
                 "MISSING_SOURCE_OWNER_FIT_ROLE")
        self._rng = random.Random(seed)
        self._limit = episode_steps
        self._step_count = 0
        self._hidden = None
        self._uncertain = False
        self._completed = False

    def _observe(self) -> str:
        return OBSERVATIONS[_draw(
            self._rng, self.model["observations"][self._hidden])]

    def reset_public(self) -> str:
        if self._hidden is not None or self._uncertain:
            raise SourcePreflightDenied(
                "ITD02_PUBLISHED_SHUTTLE_SOURCE_RESET_NOT_AT_BOUNDARY")
        self._uncertain = True
        self._hidden = _draw(self._rng, self.model["initial"])
        self._step_count = 0
        self._completed = False
        public = self._observe()
        self._uncertain = False
        return public

    def step_public(self, action: str) -> tuple[str, int, bool, bool]:
        if (type(action) is not str or action not in ACTIONS or
                self._hidden is None or self._completed or self._uncertain):
            raise SourcePreflightDenied(
                "ITD02_PUBLISHED_SHUTTLE_PUBLIC_STEP_INVALID")
        self._uncertain = True
        before = self._hidden
        self._hidden = _draw(
            self._rng, self.model["transitions"][action][before])
        reward = self.model["rewards"].get((action, before, self._hidden), 0)
        observation = self._observe()
        self._step_count += 1
        self._completed = self._step_count >= self._limit
        self._uncertain = False
        # The original published Shuttle is CONTINUING: it has no terminal.
        # Source-owner episode ceilings are honest truncations, not goals.
        return observation, reward, False, self._completed

    @property
    def source_receipt(self) -> Mapping[str, object]:
        """Outside-model audit only. This is NOT a science-acceptance receipt."""
        return {
            "source_sha256": ORIGINAL_PUBLISHER_SHA256,
            "source_url": ORIGINAL_PUBLISHER_URL,
            "role": "PUBLIC_FIT_ONLY_NOT_INDEPENDENT_SCIENCE",
            "steps": self._step_count,
            "completed_truncation": self._completed,
            "protected_first_use": False,
        }
