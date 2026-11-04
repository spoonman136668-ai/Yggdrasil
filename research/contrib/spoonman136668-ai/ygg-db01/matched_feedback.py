"""G34 matched-marginal feedback controls; environment-side DEV diagnostic only.

Periodic versus irregular sequences have the same signed-value histogram,
zero mean, absolute amplitude and L2 energy. This removes trivial marginal
energy and sign-imbalance differences in a diagnostic, NOT causal valence
confounds in learning tasks. The learner receives samples only; never labels.
"""
from __future__ import annotations


PATTERN = (1.0, 0.0, 0.0, -1.0)
CONDITIONS = frozenset(
    ("mapped", "reversed", "sham", "polarity_flip", "phase_shift", "no_feedback")
)


def _validated(outcome: int, condition: str, length: int, seed: int) -> None:
    if type(outcome) is not int or outcome not in (0, 1):
        raise ValueError("YGG_G34_OUTCOME_INVALID")
    if type(condition) is not str or condition not in CONDITIONS:
        raise ValueError("YGG_G34_CONDITION_INVALID")
    if type(length) is not int or not 16 <= length <= 1024 or length % 4:
        raise ValueError("YGG_G34_LENGTH_INVALID")
    if type(seed) is not int or not 0 <= seed < 2**32:
        raise ValueError("YGG_G34_SEED_INVALID")


def _shuffled_periodic(length: int, seed: int) -> tuple[float, ...]:
    """Explicit 32-bit xorshift/Fisher-Yates; independent of runtime RNG APIs.

    Deterministic rejection of an accidental period-4 permutation ensures
    that the chosen 'irregular' control is not identical to a regular beat.
    This does not guarantee uniform random permutations or statistical white
    noise; it is deliberately a reproducible negative-control generator.
    """
    regular = list(PATTERN * (length // 4))
    shuffled = regular[:]
    state = seed or 0x9E3779B9
    for i in range(length - 1, 0, -1):
        state ^= (state << 13) & 0xFFFFFFFF
        state ^= state >> 17
        state ^= (state << 5) & 0xFFFFFFFF
        state &= 0xFFFFFFFF
        j = state % (i + 1)
        shuffled[i], shuffled[j] = shuffled[j], shuffled[i]
    if all(shuffled[i] == shuffled[i + 4] for i in range(length - 4)):
        # Deterministic nonperiodic fallback preserving the multiset.
        shuffled = regular[:]
        shuffled[0], shuffled[1] = shuffled[1], shuffled[0]
    return tuple(shuffled)


def matched_feedback(outcome: int, condition: str = "mapped",
                     length: int = 16, seed: int = 17) -> tuple[float, ...]:
    """Return paired samples for a fixed seed and equal frame count.

    mapped: success periodic / failure shuffled, reversed: opposite mapping.
    sham: seed parity chooses a pattern independently of outcome.
    polarity_flip: sign-invert mapped waveform without changing its histogram.
    phase_shift: cyclic shift of mapped waveform by one sample.
    no_feedback: zero-energy ablation, NOT an energy-matched comparator.
    """
    _validated(outcome, condition, length, seed)
    if condition == "no_feedback":
        return (0.0,) * length
    if condition == "sham":
        periodic = bool(seed & 1)
    elif condition == "reversed":
        periodic = not bool(outcome)
    else:
        periodic = bool(outcome)
    waveform = (PATTERN * (length // 4) if periodic else
                _shuffled_periodic(length, seed))
    if condition == "polarity_flip":
        return tuple(-sample for sample in waveform)
    if condition == "phase_shift":
        return waveform[-1:] + waveform[:-1]
    return waveform
