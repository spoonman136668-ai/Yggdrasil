"""YGG-DB01 exploratory fixed-capacity local developmental substrate.

No trained parameters or scientific result; this is an executable interface fixture.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LocalDevelopment:
    width: int = 4
    height: int = 4
    channels: int = 2
    rate: float = 0.125

    def __post_init__(self):
        if self.width < 2 or self.height < 2 or self.channels != 2:
            raise ValueError("YGG_DB01_SHAPE_INVALID")
        if not 0.0 < self.rate <= 1.0:
            raise ValueError("YGG_DB01_RATE_INVALID")

    def step(self, state: tuple[tuple[tuple[float, float], ...], ...],
             sensory: tuple[tuple[float, ...], ...]):
        """Shared local residual update; sensory enters only the local cell.

        Channel 0 is immutable task/sensory input; channel 1 is mutable
        developmental state. All cells share exactly the same update rule.
        """
        if len(state) != self.height or len(sensory) != self.height:
            raise ValueError("YGG_DB01_GRID_INVALID")
        for row, signal in zip(state, sensory):
            if len(row) != self.width or len(signal) != self.width:
                raise ValueError("YGG_DB01_GRID_INVALID")
            if any(len(cell) != self.channels for cell in row):
                raise ValueError("YGG_DB01_CHANNELS_INVALID")
            if any(type(v) not in (int, float) or not -1 <= v <= 1 for v in signal):
                raise ValueError("YGG_DB01_SIGNAL_INVALID")
        out = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                neighbors = [
                    state[ny][nx][1]
                    for ny in range(max(0, y-1), min(self.height, y+2))
                    for nx in range(max(0, x-1), min(self.width, x+2))
                ]
                local_mean = sum(neighbors) / len(neighbors)
                old = state[y][x]
                delta = self.rate * (local_mean - old[1] + sensory[y][x])
                row.append((old[0], old[1] + delta))
            out.append(tuple(row))
        return tuple(out)


def feedback(outcome: int, length: int = 16, seed: int = 17) -> tuple[float, ...]:
    """Success: periodic pulses. Failure: reproducible irregular noise.

    Outcome is consumed by the environment-side encoder, not the learner.
    """
    if type(outcome) is not int or outcome not in (0, 1):
        raise ValueError("YGG_DB01_OUTCOME_INVALID")
    if type(length) is not int or not 4 <= length <= 1024:
        raise ValueError("YGG_DB01_LENGTH_INVALID")
    if type(seed) is not int or not 0 <= seed < 2**32:
        raise ValueError("YGG_DB01_SEED_INVALID")
    if outcome == 1:
        return tuple(1.0 if i % 4 == 0 else 0.0 for i in range(length))
    state = seed or 1
    samples = []
    for _ in range(length):
        state ^= (state << 13) & 0xFFFFFFFF
        state ^= state >> 17
        state ^= (state << 5) & 0xFFFFFFFF
        state &= 0xFFFFFFFF
        samples.append((state / 0xFFFFFFFF) * 2.0 - 1.0)
    return tuple(samples)

def feedback_control(outcome: int, condition: str = "mapped",
                     length: int = 16, seed: int = 17) -> tuple[float, ...]:
    """Environment-side negative controls; outcome never enters LocalDevelopment.

    Sham selection depends on the frozen seed parity, never on outcome. Pair
    identical seeds across outcomes so this is label independent. No-feedback
    keeps the same frame budget and a zero sensory signal.
    """
    if type(condition) is not str or condition not in (
            "mapped", "reversed", "sham", "no_feedback"):
        raise ValueError("YGG_DB01_CONTROL_INVALID")
    # Validate even controls that do not use the outcome or RNG.
    if type(outcome) is not int or outcome not in (0, 1):
        raise ValueError("YGG_DB01_OUTCOME_INVALID")
    if type(length) is not int or not 4 <= length <= 1024:
        raise ValueError("YGG_DB01_LENGTH_INVALID")
    if type(seed) is not int or not 0 <= seed < 2**32:
        raise ValueError("YGG_DB01_SEED_INVALID")
    if condition == "no_feedback":
        return (0.0,) * length
    if condition == "sham":
        # Half even/odd seeds select noise/beats, independent of outcomes.
        return feedback(seed & 1, length=length, seed=seed)
    if condition == "reversed":
        outcome = 1 - outcome
    return feedback(outcome, length=length, seed=seed)
