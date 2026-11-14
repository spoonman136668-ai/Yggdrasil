"""Independent source-matched WSP98 controls; no evaluator oracle imported."""
from __future__ import annotations

import math
from itertools import combinations, product
from core import ACTIONS, D, GATES, N, PASSIVE_ROWS, phi, rank, state


def clause_output(x, clause):
    p, q, flip_a, flip_b, gate = clause
    a, b = x[p] ^ flip_a, x[q] ^ flip_b
    if gate == 'AND': return int(a == 1 and b == 1)
    if gate == 'OR': return int(a == 1 or b == 1)
    if gate == 'XOR': return int(a != b)
    if gate == 'XNOR': return int(a == b)
    if gate == 'NAND': return int(not (a == 1 and b == 1))
    if gate == 'NOR': return int(not (a == 1 or b == 1))
    raise ValueError('unknown source-grammar gate')


class SymbolicInducer:
    """Enumerates all source-consistent clauses for each output independently."""
    def __init__(self, rows):
        if len(rows) not in (PASSIVE_ROWS, PASSIVE_ROWS + ACTIONS):
            raise ValueError('unregistered source count')
        self.rows = tuple((state(x), state(y)) for x, y in rows)
        catalogue = tuple((p, q, na, nb, gate)
                          for p, q in combinations(range(N), 2)
                          for na, nb in product((0, 1), repeat=2)
                          for gate in GATES)
        self.consistent = tuple(tuple(clause for clause in catalogue
                                      if all(clause_output(x, clause) == y[node]
                                             for x, y in self.rows))
                                for node in range(N))
        if any(not options for options in self.consistent):
            raise ValueError('source inconsistent with registered grammar')

    def votes(self, x):
        x = state(x)
        return tuple(tuple(clause_output(x, clause) for clause in opts)
                     for opts in self.consistent)

    def predict(self, x):
        # Posterior majority over equally likely surviving clauses; tie -> 0.
        return tuple(int(sum(v) > len(v) / 2) for v in self.votes(x))

    def identifiable(self, x):
        return tuple(len(set(v)) == 1 for v in self.votes(x))

    def ambiguity(self):
        return tuple(len(v) for v in self.consistent)


class PolynomialGradient:
    """Separate fully trained six-output polynomial MSE learner, fixed 2000 epochs.

    Full-batch gradients, learning rate 0.03 and L2 weight decay 0.125.
    No closed-form/no-gradient write; this is a gradient trained control.
    """
    epochs = 2000
    lr = .03
    decay = .125

    def __init__(self, rows):
        if len(rows) != PASSIVE_ROWS + ACTIONS: raise ValueError('missing controlled source')
        samples = tuple((phi(x), tuple(2 * b - 1 for b in state(y))) for x, y in rows)
        self.w = [[0.0] * D for _ in range(N)]
        step = self.lr / len(samples)
        for _ in range(self.epochs):
            grad = [[0.0] * D for _ in range(N)]
            for f, y in samples:
                for k in range(N):
                    delta = sum(self.w[k][j] * f[j] for j in range(D)) - y[k]
                    for j in range(D):
                        grad[k][j] += delta * f[j]
            for k in range(N):
                for j in range(D):
                    self.w[k][j] -= step * grad[k][j] + self.lr * self.decay * self.w[k][j]
        self.train_fit = sum(self.predict(x) == state(y) for x, y in rows)

    def predict(self, x):
        f = phi(x)
        return tuple(int(sum(self.w[k][j] * f[j] for j in range(D)) > 0) for k in range(N))


class TanhGradient:
    """Independent 6->32->6 tanh model, trained 2500 full-batch gradient epochs."""
    epochs = 2500
    lr = .01
    hidden = 32

    def __init__(self, rows, world_id):
        if len(rows) != PASSIVE_ROWS + ACTIONS: raise ValueError('missing controlled source')
        self.a = [[((rank(world_id, 'WORLD', j*6+i) % 2001)-1000)/10000.0 for i in range(N)]
                  for j in range(self.hidden)]
        self.b = [0.0] * self.hidden
        self.c = [[((rank(world_id, 'WORLD', 192+k*32+j) % 2001)-1000)/10000.0 for j in range(self.hidden)]
                  for k in range(N)]
        self.d = [0.0] * N
        source = tuple((tuple(2*b-1 for b in state(x)), tuple(2*b-1 for b in state(y))) for x,y in rows)
        for _ in range(self.epochs):
            da = [[0.0] * N for _ in range(self.hidden)]; db = [0.0]*self.hidden
            dc = [[0.0] * self.hidden for _ in range(N)]; dd = [0.0]*N
            for x,y in source:
                hidden = [math.tanh(self.b[j]+sum(self.a[j][i]*x[i] for i in range(N))) for j in range(self.hidden)]
                output = [math.tanh(self.d[k]+sum(self.c[k][j]*hidden[j] for j in range(self.hidden))) for k in range(N)]
                out_grad = [(output[k]-y[k])*(1-output[k]**2) for k in range(N)]
                hid_grad = [(1-hidden[j]**2)*sum(out_grad[k]*self.c[k][j] for k in range(N)) for j in range(self.hidden)]
                for k in range(N):
                    dd[k] += out_grad[k]
                    for j in range(self.hidden): dc[k][j] += out_grad[k]*hidden[j]
                for j in range(self.hidden):
                    db[j] += hid_grad[j]
                    for i in range(N): da[j][i] += hid_grad[j]*x[i]
            step = self.lr / len(source)
            for k in range(N):
                self.d[k] -= step*dd[k]
                for j in range(self.hidden): self.c[k][j] -= step*dc[k][j]
            for j in range(self.hidden):
                self.b[j] -= step*db[j]
                for i in range(N): self.a[j][i] -= step*da[j][i]
        self.train_fit = sum(self.predict(x)==state(y) for x,y in rows)

    def predict(self, x):
        x = tuple(2*b-1 for b in state(x))
        h = [math.tanh(self.b[j]+sum(self.a[j][i]*x[i] for i in range(N))) for j in range(self.hidden)]
        return tuple(int(self.d[k]+sum(self.c[k][j]*h[j] for j in range(self.hidden)) > 0) for k in range(N))
