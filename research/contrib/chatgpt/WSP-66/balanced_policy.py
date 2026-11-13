"""WSP66 preregistered balanced ordered-pair physical experiment design.

This is a deterministic source-blind DE BRUIJN cycle, *not* a feedback-
adaptive information-gain algorithm. It guarantees action-pair coverage
under a 48-action no-reset physical training budget; it does not guarantee
coverage of physical sensor states or identify the unknown hidden mode.
Learner/physics/evaluator code is never imported here.
"""
from __future__ import annotations

CHANNELS = (0, 1, 2, 3)
TRAIN_ACTIONS = 48


def debruijn_order2(k=4):
    """FKM de Bruijn B(k,2), cyclic length k², every ordered pair once."""
    if type(k) is not int or k != 4:
        raise ValueError("frozen four-channel action alphabet only")
    n = 2
    a = [0] * (k*n+1)
    seq = []

    def db(t, p):
        if t > n:
            if n % p == 0:
                seq.extend(a[1:p+1])
        else:
            a[t] = a[t-p]
            db(t+1, p)
            for j in range(a[t-p]+1, k):
                a[t] = j
                db(t+1, t)

    db(1, 1)
    result = tuple(seq)
    assert len(result) == 16
    assert set((result[i], result[(i+1) % 16]) for i in range(16)) == {
        (x,y) for x in CHANNELS for y in CHANNELS
    }
    return result


CYCLE = debruijn_order2()


class BalancedPairPolicy:
    def __init__(self):
        self.ledger = []
        self.state = None

    def select(self, current):
        if type(current) is not tuple or len(current) not in (3,4):
            raise ValueError("invalid current physical sensor tuple")
        if self.state is None and current != (0,) * len(current):
            raise ValueError("single initial physical state violated")
        if self.state is not None and current != self.state:
            raise ValueError("illegal source state discontinuity")
        if len(self.ledger) >= TRAIN_ACTIONS:
            raise ValueError("48 charged physical actions exhausted")
        return CYCLE[len(self.ledger) % len(CYCLE)]

    def observe(self, experience):
        expected = CYCLE[len(self.ledger) % len(CYCLE)]
        if len(self.ledger) >= TRAIN_ACTIONS:
            raise ValueError("observation budget exceeded")
        if (experience.action != expected or
                experience.action_cost != 1 or
                experience.before != (self.state if self.state is not None
                                      else (0,) * len(experience.before))):
            raise ValueError("noncompliant charged action receipt")
        self.ledger.append((experience.before, experience.action, experience.after))
        self.state = experience.after

    def ordered_pairs(self):
        actions = [a for b,a,y in self.ledger]
        return tuple(zip(actions[:-1], actions[1:]))

    def charged_count(self):
        return len(self.ledger)
