"""Separate conventional exact four-bin two-feature symbolic fit control."""
from __future__ import annotations
from binding import _credit_public, _feature_bits, _state, _history, FEATURES, ROWS_LIMIT


class ExactTwoFeatureControl:
    """Same public observations/candidate features, independent fitting code."""

    def __init__(self):
        self.examples = []
        self.fitted = None

    def observe_public(self, row):
        if len(self.examples) >= ROWS_LIMIT:
            raise ValueError("CB1_CONTROL_BUDGET")
        credit, _ = _credit_public(row)
        if credit is not None:
            self.examples.append(credit)

    def seal(self):
        if self.fitted is not None:
            raise ValueError("CB1_CONTROL_FROZEN")
        n = len(self.examples)
        if not 32 <= n <= ROWS_LIMIT:
            raise ValueError("CB1_CONTROL_NO_EVIDENCE")
        winner = None
        for left in range(FEATURES):
            for right in range(left + 1, FEATURES):
                outcomes = [[0, 0] for _ in range(4)]
                for encoded, label in self.examples:
                    cell = (2 if encoded & (1 << left) else 0) + (1 if encoded & (1 << right) else 0)
                    outcomes[cell][label] += 1
                if any(not sum(observation) for observation in outcomes):
                    continue
                accurate = sum(max(observation) for observation in outcomes)
                symbol = sum((1 << bin_id) if observation[1] > observation[0] else 0
                             for bin_id, observation in enumerate(outcomes))
                if winner is None or accurate > winner[0]:
                    winner = (accurate, left, right, symbol)
        if winner is None or winner[0] * 10 < 9 * n:
            raise ValueError("CB1_CONTROL_UNSUPPORTED")
        self.fitted = winner
        self.examples = []
        return self

    def choose_public(self, state, history):
        if self.fitted is None:
            return None
        before = _state(state)
        past = _history(history, before)
        previous = past[-1].action if past else 0
        older = past[-2].action if len(past) >= 2 else 0
        encoded = _feature_bits(before, previous, older)
        _, a, b, table = self.fitted
        key = (2 if encoded & (1 << a) else 0) + (1 if encoded & (1 << b) else 0)
        return (table >> key) & 1
