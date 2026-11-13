"""WSP82 independent temporal-symbolic comparator, same frozen basis size.

This source-blind solver does not import, call, or invoke the numerical model.
It independently builds primitive Boolean signatures from paid public rows,
finds minimum structural complexity exact matches, and abstains if distinct
minimum-complexity solutions disagree on a novel query.
"""
from itertools import product

STATES = frozenset(product((0, 1), repeat=6))
ACTIONS = tuple(range(6))
_BASIS = (
    (("zero", -1, -1), ("one", -1, -1))
    + tuple(("action", i, -1) for i in ACTIONS)
    + tuple(("prior", i, -1) for i in ACTIONS)
    + tuple(("second_prior", i, -1) for i in ACTIONS)
    + (("prior_equal", -1, -1),)
    + tuple(("action_prior", a, p) for a in ACTIONS for p in ACTIONS)
    + tuple(("action_second_prior", a, p) for a in ACTIONS for p in ACTIONS)
    + tuple(("prior_pair", p, q) for p in ACTIONS for q in ACTIONS)
    + tuple(("prior_equal_action", a, -1) for a in ACTIONS)
)
_PRIORITY = {
    "zero": 0, "one": 1, "action": 1, "prior": 1,
    "second_prior": 1, "prior_equal": 2, "action_prior": 3,
    "action_second_prior": 3, "prior_pair": 3,
    "prior_equal_action": 4,
}


def _eval(desc, action, history):
    typ, x, y = desc
    p = history[-1] if history else None
    q = history[-2] if len(history) >= 2 else None
    values = {
        "zero": False,
        "one": True,
        "action": action == x,
        "prior": p == x,
        "second_prior": q == x,
        "prior_equal": p is not None and q is not None and p == q,
        "action_prior": action == x and p == y,
        "action_second_prior": action == x and q == y,
        "prior_pair": p == x and q == y,
        "prior_equal_action":
            p is not None and q is not None and p == q and action == x,
    }
    return values[typ]


class IndependentTemporalSymbolic:
    def __init__(self, ledger):
        rows = tuple(ledger)
        if len(rows) != 384:
            raise ValueError("384 separately charged observations required")
        s = (0,) * 6
        history = []
        train = []
        for row in rows:
            try:
                before, a, after, cost = (
                    row.before, row.action, row.after, row.action_cost)
            except AttributeError as exc:
                raise ValueError("incomplete paid public observation") from exc
            if (type(before) is not tuple or before not in STATES
                    or type(after) is not tuple or after not in STATES
                    or type(a) is not int or a not in ACTIONS
                    or type(cost) is not int or cost != 1 or before != s):
                raise ValueError("invalid or discontinuous public evidence")
            train.append((before, a, after, tuple(history)))
            history.append(a)
            s = after

        self.accepted = []
        for bit in range(6):
            consistent = []
            for desc in _BASIS:
                if all(
                    (int(_eval(desc, action, hist)) ==
                     (before[bit] ^ after[bit] ^ int(action == bit)))
                    for before, action, after, hist in train):
                    consistent.append(desc)
            if not consistent:
                raise ValueError("symbolic basis cannot represent paid data")
            score = min(_PRIORITY[d[0]] for d in consistent)
            self.accepted.append(tuple(
                desc for desc in consistent if _PRIORITY[desc[0]] == score))
        self.charged_actions = len(rows)

    def predict(self, state, action, history=()):
        if (type(state) is not tuple or state not in STATES
                or type(action) is not int or action not in ACTIONS
                or type(history) not in (tuple, list)
                or any(type(i) is not int or i not in ACTIONS for i in history)):
            raise ValueError("invalid symbolic public query")
        output = []
        for bit, choices in enumerate(self.accepted):
            answers = {
                state[bit] ^ int(action == bit) ^
                    int(_eval(desc, action, history))
                for desc in choices
            }
            if len(answers) != 1:
                return None
            output.append(next(iter(answers)))
        return tuple(output)
