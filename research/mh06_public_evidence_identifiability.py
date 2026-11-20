"""MH06: source-only identifiability and public-outcome gate, not a native learner.

No source episodes or rewarded trials are generated. This external shadow
mechanism never selects, switches, updates or mutates an actual V32E model.
The original V32E Rust explicitly labels itself a quarantined prototype.
"""
from __future__ import annotations

import math

# Immutable *engineering* constants frozen before implementation (MH06 prereg).
LOG_ODDS_GATE = math.log(19.0)
MIN_DISTINCT_PAIRS = 2
PROBABILITY_FLOOR = 0.05
PROBABILITY_CEILING = 0.95
ORIGINAL_V32E_GIT_BLOB = "85237dcc82905e05a273b11023b5be5db722726e"


def _cue(value: int) -> int:
    if type(value) is not int or value not in range(4):
        raise ValueError("MH06_PUBLIC_CUE_INVALID")
    return value


def _action(value: int) -> int:
    if type(value) is not int or value not in range(3):
        raise ValueError("MH06_PUBLIC_ACTION_INVALID")
    return value


def _reward(value: float) -> float:
    if type(value) not in (int, float) or value not in (-1, 1):
        raise ValueError("MH06_PUBLIC_REWARD_INVALID")
    return float(value)


def _bank_probability(score: float) -> float:
    if type(score) not in (float, int) or not math.isfinite(score):
        raise ValueError("MH06_BANK_FORECAST_INVALID")
    # Heuristic engineering likelihood, not a calibrated native score.
    p = (max(-1.0, min(1.0, float(score))) + 1.0) / 2.0
    return max(PROBABILITY_FLOOR, min(PROBABILITY_CEILING, p))


def expected_paired_accuracy(bank_choices: tuple[int | None, ...]) -> float:
    """Exact equal-prior bound for indistinguishable A-return and X-stay twins.

    In either hidden regime the *same public transcript* reaches the selector;
    a single bank choice is applied to both hypothetical labels. No outcomes
    are sampled, no world is run, and an abstention earns no correct guess.
    """
    if not isinstance(bank_choices, tuple) or not bank_choices:
        raise ValueError("MH06_CHOICES_REQUIRED")
    if any(type(x) is not int and x is not None or x not in (0, 1, None)
           for x in bank_choices):
        raise ValueError("MH06_ORACLE_OR_INVALID_CHOICE")
    return sum(x is not None for x in bank_choices) / (2 * len(bank_choices))


def expected_accuracy_with_prior(bank_choice: int | None, prior_bank0: float) -> float:
    """Paired hidden-regime calculation, independent of source rewards."""
    if bank_choice is not None and (type(bank_choice) is not int
                                    or bank_choice not in (0, 1)):
        raise ValueError("MH06_INVALID_CHOICE")
    if type(prior_bank0) not in (int, float) or not math.isfinite(prior_bank0) or not 0 <= prior_bank0 <= 1:
        raise ValueError("MH06_INVALID_PRIOR")
    if bank_choice is None:
        return 0.0
    return float(prior_bank0 if bank_choice == 0 else 1.0 - prior_bank0)


class MH06PublicEvidenceGate:
    """Read-only shadow bank-evidence selector, NOT actual native retrieval.

    This unit-test mechanism sees only public cue, then action/outcome, and
    two learned-bank *forecasts*. It cannot observe an environment regime ID,
    a true target mapping, or an evaluator-only known-correct-bank label.
    """
    def __init__(self):
        self._pending_cue: int | None = None
        self._log_odds = 0.0
        self._witnessed_pairs: set[tuple[int, int]] = set()

    def observe_public_cue(self, cue: int) -> None:
        cue = _cue(cue)
        if self._pending_cue is not None:
            raise ValueError("MH06_PENDING_OUTCOME_NOT_RESOLVED")
        self._pending_cue = cue

    def recommendation(self) -> int | None:
        # No evidential shortcut: a cue and bank0's known historical
        # competence are NOT evidence of which world now governs.
        if len(self._witnessed_pairs) < MIN_DISTINCT_PAIRS:
            return None
        if abs(self._log_odds) < LOG_ODDS_GATE:
            return None
        return 0 if self._log_odds > 0 else 1

    def record_public_feedback(self, action: int, reward: float,
                               bank0_score: float, bank1_score: float) -> int | None:
        if self._pending_cue is None:
            raise ValueError("MH06_FEEDBACK_BEFORE_OBSERVATION")
        action = _action(action)
        outcome = _reward(reward)
        p0 = _bank_probability(bank0_score)
        p1 = _bank_probability(bank1_score)
        pair = (self._pending_cue, action)
        if pair in self._witnessed_pairs:
            raise ValueError("MH06_DUPLICATE_PAIR_NOT_ADMITTED")
        p0_observed = p0 if outcome == 1.0 else 1.0 - p0
        p1_observed = p1 if outcome == 1.0 else 1.0 - p1
        delta = math.log(p0_observed) - math.log(p1_observed)
        # Atomic commit only after every input has passed validation.
        self._log_odds += delta
        self._witnessed_pairs.add(pair)
        self._pending_cue = None
        return self.recommendation()

    def inspect(self) -> dict:
        return {
            "pending_public_cue": self._pending_cue,
            "distinct_public_action_consequence_pairs": len(self._witnessed_pairs),
            "log_odds_bank0_over_bank1": self._log_odds,
            "shadow_recommendation": self.recommendation(),
            "native_bank_switched": False,
            "source_actions_executed": 0,
            "scientific_gain_verified": False,
        }
