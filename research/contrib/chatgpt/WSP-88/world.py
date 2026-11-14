"""Synthetic English intervention source; learner never sees this vocabulary."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import random

OLD = (
    ("raise", "lift", "hoist"),
    ("lower", "drop", "sink"),
    ("hold", "freeze", "steady"),
)
NEW = ("elevate", "descend", "maintain")
TRAIN_FRAMES = (
    "Please {verb} the {object}.",
    "Could you {verb} the {object} now?",
    "{verb} the {object} safely.",
)
TEST_FRAMES = (
    "Kindly {verb} this {object} for me.",
    "Before the next step, {verb} the {object}.",
    "On my signal: {verb} the {object}.",
)
TRAIN_OBJECTS = ("panel", "lever", "gate", "dial")
TEST_OBJECTS = ("shutter", "slider", "cage", "switch")
UNKNOWN = (
    "Please illuminate the starboard window.",
    "Can you annotate the document?",
    "Synchronize the navigation displays.",
    "Schedule the opening ceremony.",
    "Archive all outstanding receipts.",
    "Move the vehicle toward the hangar.",
    "Reverse the conveyor direction.",
    "Paint the outside fence green.",
    "Rotate the beacon clockwise.",
    "Estimate the current temperature.",
    "Calculate the orbital period.",
    "Delete the unused configuration.",
    "Measure the liquid level.",
    "Calibrate the instrument now.",
    "Disconnect the backup generator.",
    "Record the full inspection.",
    "Refill the coolant reservoir.",
    "Translate the safety warning.",
    "Compare the new measurements.",
    "Describe the current conditions.",
)


def permutation(seed: int) -> tuple[int, int, int]:
    raw = hashlib.sha256(f"WSP88|permutation|{seed}|v1".encode("ascii")).digest()
    return tuple(random.Random(int.from_bytes(raw[:8], "big")).sample(range(3), 3))


def render(frame: str, verb: str, obj: str) -> str:
    return frame.format(verb=verb, object=obj)


@dataclass
class World:
    seed: int
    train_a: tuple[str, ...]
    train_b: tuple[str, ...]
    eval_a: tuple[str, ...]
    eval_b: tuple[str, ...]
    unknown: tuple[str, ...]
    _answers: dict[str, int]

    def probe(self, utterance: str, actuator: int) -> bool:
        """One paid, observable action-consequence trial; no class label returned."""
        if actuator not in (0, 1, 2):
            raise ValueError("invalid actuator")
        if utterance not in self.train_a and utterance not in self.train_b:
            raise ValueError("probe of unregistered utterance")
        return self._answers[utterance] == actuator

    def evaluator_truth(self, utterances: tuple[str, ...]) -> tuple[int, ...]:
        """Evaluator only: call AFTER all learner predictions are frozen."""
        return tuple(self._answers[x] for x in utterances)


def make_world(seed: int) -> World:
    if not isinstance(seed, int) or seed <= 0:
        raise ValueError("positive seed required")
    actions = permutation(seed)
    answers: dict[str, int] = {}
    train_a: list[str] = []
    train_b: list[str] = []
    eval_a: list[str] = []
    eval_b: list[str] = []

    def add(target: list[str], frame: str, verb: str, obj: str, intent: int) -> None:
        text = render(frame, verb, obj)
        if text in answers:
            raise ValueError("duplicate utterance")
        answers[text] = actions[intent]
        target.append(text)

    for intent, verbs in enumerate(OLD):
        for verb in verbs:
            for frame in TRAIN_FRAMES:
                for obj in TRAIN_OBJECTS:
                    add(train_a, frame, verb, obj, intent)
            for frame in TEST_FRAMES:
                for obj in TEST_OBJECTS:
                    add(eval_a, frame, verb, obj, intent)

    for intent, verb in enumerate(NEW):
        for i in range(3):
            add(train_b, TRAIN_FRAMES[i], verb, TRAIN_OBJECTS[i], intent)
        for frame in TEST_FRAMES:
            for obj in TEST_OBJECTS:
                add(eval_b, frame, verb, obj, intent)
    assert (len(train_a), len(train_b), len(eval_a), len(eval_b)) == (108, 9, 108, 36)
    return World(seed, tuple(train_a), tuple(train_b),
                 tuple(eval_a), tuple(eval_b), UNKNOWN, answers)
