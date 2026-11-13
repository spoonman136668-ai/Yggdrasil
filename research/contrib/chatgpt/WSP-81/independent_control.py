"""Independent symbolic WSP81 control, without numeric editor or source import.

Exactly the same frozen 31-member finite hypothesis class; separately
implemented parity and visible transition. A numeric tie proves no
advantage over an equally expressive symbolic state machine.
"""
from itertools import product

_STATES = frozenset(product((0, 1), repeat=6))
_ACTIONS = tuple(range(6))
_ALL = ((None, None),) + tuple(
    (trigger, offset) for trigger in _ACTIONS for offset in range(1, 6))


def _transition(state, action, action_history, hypothesis):
    trigger, offset = hypothesis
    mode = 0
    if trigger is not None:
        for previous in action_history:
            if previous == trigger:
                mode = 1 - mode
    out = list(state)
    out[action] = 1 - out[action]
    if trigger is not None and mode and action != trigger:
        target = (action + offset) % 6
        out[target] = 1 - out[target]
    return tuple(out)


class IndependentHistorySymbolic:
    def __init__(self, experiences):
        records = tuple(experiences)
        if len(records) != 384:
            raise ValueError("incomplete paid 384-step history")
        self.paid_actions = 384
        current = (0,) * 6
        history = []
        rows = []
        for e in records:
            try:
                before, action, after, cost = (
                    e.before, e.action, e.after, e.action_cost)
            except AttributeError as exc:
                raise ValueError("missing charged observation") from exc
            if (type(before) is not tuple or before not in _STATES
                    or type(after) is not tuple or after not in _STATES
                    or type(action) is not int or action not in _ACTIONS
                    or type(cost) is not int or cost != 1
                    or before != current):
                raise ValueError("unpaid or noncontinuous public history")
            rows.append((before, action, after, tuple(history)))
            history.append(action)
            current = after
        self.survivors = tuple(
            candidate for candidate in _ALL
            if all(_transition(state, action, hist, candidate) == after
                   for state, action, after, hist in rows))
        if not self.survivors:
            raise ValueError("no consistent model in independently defined class")

    def predict(self, state, action, history=()):
        if (type(state) is not tuple or state not in _STATES
                or type(action) is not int or action not in _ACTIONS
                or type(history) not in (list, tuple)
                or any(type(a) is not int or a not in _ACTIONS for a in history)):
            raise ValueError("invalid public history query")
        predictions = {
            _transition(state, action, history, candidate)
            for candidate in self.survivors
        }
        return next(iter(predictions)) if len(predictions) == 1 else None
