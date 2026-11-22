"""Source-side two-stage Boolean fixtures for development experiments.

Keep episodes, hidden draws and logging rules on the evaluator side. An
intervention policy receives only the public history supplied by ``rollout``.
Hold out both family/phase combinations and episode cohorts before scoring.
"""

from dataclasses import dataclass
from hashlib import sha256


FAMILIES = ("invariant", "context_switch", "terminal_switch")


def _bit(value):
    if type(value) is not int or value not in (0, 1):
        raise ValueError("expected a public binary value")
    return value


@dataclass(frozen=True, slots=True)
class _Episode:
    family: str
    regime: int
    s1: int
    hidden: int
    transition_noise: int
    reward_noise: int
    logging_noise: int
    logging_second: int
    nuisance_a: int
    nuisance_b: int

    def transition(self, x1):
        orientation = self.regime
        if self.family == "context_switch":
            orientation ^= self.s1
        return _bit(x1) ^ orientation ^ self.transition_noise

    def _reward(self, x1, s2, x2):
        target = self.s1 ^ s2
        if self.family == "terminal_switch":
            target ^= x1 ^ self.regime
        ready = s2 == 0 or self.hidden == 1
        return int(ready and _bit(x2) == target) ^ self.reward_noise


def make_episode(*, cohort, seed, index, family, regime):
    """Create a reproducible episode in an explicit draw namespace.

    Independent action arms can share a key for paired evaluation. Family and
    regime affect structural equations while the key controls exogenous draws.
    """
    if (type(cohort) is not str or not cohort or not cohort.isascii()
            or any(not (item.isalnum() or item in "-_") for item in cohort)):
        raise ValueError("expected a nonempty ASCII cohort name")
    if any(type(value) is not int or value < 0 for value in (seed, index)):
        raise ValueError("expected nonnegative integer seed and index")
    if type(family) is not str or family not in FAMILIES:
        raise ValueError("unknown synthetic family")
    _bit(regime)
    key = f"ckad20/episode-v1/{cohort}/{seed}/{index}".encode("ascii")
    draws = sha256(key).digest()
    hidden = draws[0] & 1
    return _Episode(
        family=family,
        regime=regime,
        s1=hidden ^ int(draws[1] < 64),
        hidden=hidden,
        transition_noise=int(draws[2] < 32 + 32 * hidden),
        reward_noise=int(draws[3] < 16),
        logging_noise=int(draws[4] < 16),
        logging_second=draws[5] & 1,
        nuisance_a=draws[6] & 1,
        nuisance_b=draws[7] & 1,
    )


def public_views(episode):
    """Return two observations of the same initial state and unrelated cues."""
    return (episode.s1, episode.nuisance_a), (episode.s1, episode.nuisance_b)


def rollout(episode, choose_first, choose_second):
    """Reveal one trajectory using public sequential policy calls."""
    s1 = episode.s1
    x1 = _bit(choose_first(s1))
    s2 = episode.transition(x1)
    x2 = _bit(choose_second(s1, x1, s2))
    return {"s1": s1, "x1": x1, "s2": s2, "x2": x2, "y": episode._reward(x1, s2, x2)}


def logged(episode):
    """Generate observational evidence under an unrevealed logging rule.

    The first action follows the hidden reward cause with probability 15/16.
    This can favor the wrong first action in a marginal observational analysis.
    The caller must tag the result as logged evidence outside the public row.
    """
    return rollout(
        episode,
        lambda _s1: episode.hidden ^ episode.logging_noise,
        lambda _s1, _x1, _s2: episode.logging_second,
    )
