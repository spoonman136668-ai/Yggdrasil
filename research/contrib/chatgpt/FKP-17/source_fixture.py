"""FKP-17 public TRAIN/VALIDATION/FOUNDATION source fixture.

Research-only synthetic causal observation generator. It has deliberately NO
implementation or access path for original DEV, TRANSFER or owner-protected
worlds. This module does not create a learner, evaluate held science, confer
first-use authority or modify the native Yggdrasil model.

The learner-facing output consists only of actual public before/action/after,
public earned reward, done, and preceding (not future) public history. Private
training-law coefficients never occur in those returned records.

IMPORTANT: published fixture code is inspectable, hence it cannot be a
cryptographic substitute for a separately owned source-private held evaluator.
"""
from __future__ import annotations

from hashlib import sha256
import json
import random
from typing import NamedTuple

FOUNDATION = tuple(range(979100, 979228))
TRAIN = tuple(range(978100, 978164))
VALIDATION = tuple(range(978200, 978216))
HELD_DEV = tuple(range(978500, 978532))
HELD_TRANSFER = tuple(range(978600, 978664))
REGISTERS = 8
ACTIONS = 8
MAX_STEPS = 256
HISTORY = 16
FOUNDATION_RECORDS_PER_WORLD = 256
FOUNDATION_RECORDS = len(FOUNDATION) * FOUNDATION_RECORDS_PER_WORLD


class PublicTransition(NamedTuple):
    before: tuple[int, ...]
    action: int
    reward: float
    after: tuple[int, ...]
    done: bool


class PublicStep(NamedTuple):
    before: tuple[int, ...]
    action: int
    after: tuple[int, ...]
    reward: float
    done: bool
    history: tuple[PublicTransition, ...]


def cohort(seed: int) -> str:
    """Only source-safe foundation/TRAIN/VALIDATION can be instantiated.

    Denied even when a caller invents an allow_dev or other keyword. There is
    no held generator or bypass in this module: first use belongs elsewhere.
    """
    if type(seed) is not int:
        raise ValueError("FKP17_SEED_MUST_BE_INT")
    if seed in FOUNDATION:
        return "FOUNDATION"
    if seed in TRAIN:
        return "TRAIN"
    if seed in VALIDATION:
        return "VALIDATION"
    raise PermissionError("FKP17_HELD_OR_UNKNOWN_WORLD_REJECTED")


def _rng(seed: int, label: str) -> random.Random:
    material = f"FKP17/PUBLIC-TRAIN-FIXTURE/v1/{label}/{seed}".encode("ascii")
    return random.Random(int.from_bytes(sha256(material).digest()[:16], "big"))


class _TrainingWorld:
    """Evaluator-owned internal law; never hand this object to a learner."""
    __slots__ = ("state", "_edge", "_delta", "_sign", "_offset", "_mode")

    def __init__(self, seed: int, partition: str):
        rng = _rng(seed, "LAW")
        self.state = [rng.randrange(16) for _ in range(REGISTERS)]
        # A permutation with no self-loops yields an ordinary directed,
        # action-dependent relational graph. Not used in HELD families.
        shift = rng.randrange(1, REGISTERS)
        self._edge = tuple((i + shift) % REGISTERS for i in range(REGISTERS))
        self._delta = tuple(1 + rng.randrange(3) for _ in range(REGISTERS))
        self._sign = tuple(1 if rng.randrange(2) else -1 for _ in range(REGISTERS))
        self._offset = tuple(rng.randrange(4) for _ in range(REGISTERS))
        # Training/validation receive both known, separately sampled families.
        # Foundation has only ordinary relationships, not target-held families.
        self._mode = 0 if partition == "FOUNDATION" or seed % 2 == 0 else 1

    def step(self, action: int) -> tuple[tuple[int, ...], float, bool]:
        before = tuple(self.state)
        new_state = list(before)
        new_state[action] = (before[action] + self._delta[action]) % 16
        child = self._edge[action]
        strength = self._delta[action] + self._offset[action]
        if self._mode:
            # Bounded pairwise monotone mixing in the known TRAIN/VAL family.
            other = (action + 2) % REGISTERS
            strength += min(before[other], before[action]) // 4
        new_state[child] = (before[child] + self._sign[action] * strength) % 16
        old_cost = sum(abs(v - 8) for v in before)
        new_cost = sum(abs(v - 8) for v in new_state)
        earned = max(-1.0, min(1.0, (old_cost - new_cost) / 8.0))
        self.state = new_state
        # This initial public fixture guarantees fixed-length source records;
        # real held task success/termination requires separate qualification.
        return tuple(new_state), earned, False


def public_actions(seed: int, count: int) -> tuple[int, ...]:
    """Independent source-public exploration tape; same tape for every arm."""
    cohort(seed)
    if type(count) is not int or count < 0 or count > MAX_STEPS:
        raise ValueError("FKP17_PUBLIC_ACTION_BUDGET")
    rng = _rng(seed, "PUBLIC-ACTIONS")
    return tuple(rng.randrange(ACTIONS) for _ in range(count))


def collect_public(seed: int, actions: tuple[int, ...]) -> tuple[PublicStep, ...]:
    """Physically execute ONLY public training-family actions, then redact.

    Never emits a law parameter, RNG state, source family or any unchosen
    alternative outcome. No mutable environment object escapes the evaluator.
    """
    partition = cohort(seed)
    if type(actions) is not tuple or len(actions) > MAX_STEPS:
        raise ValueError("FKP17_PUBLIC_ACTION_TAPE_TYPE_OR_LENGTH")
    for action in actions:
        if type(action) is not int or not 0 <= action < ACTIONS:
            raise ValueError("FKP17_PUBLIC_ACTION_INVALID")
    world = _TrainingWorld(seed, partition)
    history: list[PublicTransition] = []
    observed: list[PublicStep] = []
    for action in actions:
        before = tuple(world.state)
        after, earned, done = world.step(action)
        observed.append(PublicStep(before, action, after, earned, done,
                                   tuple(history[-HISTORY:])))
        history.append(PublicTransition(before, action, earned, after, done))
        if done:
            break
    return tuple(observed)


def foundation_facts():
    """Yield exactly 128 * 256 source-observed records; no DEV instantiation."""
    for seed in FOUNDATION:
        tape = public_actions(seed, FOUNDATION_RECORDS_PER_WORLD)
        for index, record in enumerate(collect_public(seed, tape)):
            yield (seed, index, record)


def public_digest(records) -> str:
    """Stable SHA256 of public facts, identical regardless of receiving arm."""
    hash_state = sha256()
    for record in records:
        if type(record) is not PublicStep:
            raise ValueError("FKP17_ONLY_PUBLIC_RECORD_DIGEST_ALLOWED")
        raw = json.dumps(record, separators=(",", ":"), ensure_ascii=True)
        hash_state.update(len(raw).to_bytes(4, "big"))
        hash_state.update(raw.encode("ascii"))
    return hash_state.hexdigest()


# Source-safe observed action stream; original DEV/TRANSFER evaluator absent.
PUBLIC_EXPLORATION = 24
PUBLIC_SCORED = 16


class PublicSession:
    """Fresh TRAIN/VAL episode that reveals only public chosen consequences.

    Python-private __world is a convenience, NOT a security boundary. A real
    held evaluator must live in separately controlled code or process.
    The caller may read current_public and apply_public only. No alt-action,
    oracle, future-reward, law identity or source-private labels are returned.
    """

    __slots__ = ("__world", "__history", "__steps", "__done")

    def __init__(self, seed: int):
        partition = cohort(seed)  # protected and unknown seeds fail CLOSED
        if partition not in ("TRAIN", "VALIDATION"):
            raise PermissionError("FKP17_SESSION_TRAIN_VAL_ONLY")
        self.__world = _TrainingWorld(seed, partition)
        self.__history = []
        self.__steps = 0
        self.__done = False

    @property
    def current_public(self) -> tuple[int, ...]:
        return tuple(self.__world.state)

    @property
    def observed_steps(self) -> int:
        return self.__steps

    def apply_public(self, action: int) -> PublicStep:
        if type(action) is not int or not 0 <= action < ACTIONS:
            raise ValueError("FKP17_SESSION_INVALID_ACTION")
        if self.__done or self.__steps >= PUBLIC_EXPLORATION + PUBLIC_SCORED:
            raise ValueError("FKP17_SESSION_BUDGET_OR_TERMINATION")
        before = self.current_public
        after, reward, done = self.__world.step(action)
        row = PublicStep(before, action, after, reward, done,
                         tuple(self.__history[-HISTORY:]))
        self.__history.append(PublicTransition(before, action, reward, after, done))
        self.__steps += 1
        self.__done = done
        return row
