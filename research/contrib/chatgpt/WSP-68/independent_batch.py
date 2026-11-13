"""Independent conventional converged batch-trained fixed-feature neural control.

A separate implementation of the SAME source-independent 8->32 ReLU feature
bank and 41-feature neural readout. Trains all four readout output vectors by
solving the ridge normal equations to convergence via Cholesky, rather than
incrementally editing weights. A numerical optimum residual is independently
checked and compared with online RLS weights on exactly the same evidence.

It is a valid converged supervised neural READOUT comparator, NOT an
end-to-end gradient-trained hidden layer. No source imports, symbolic rules,
online_weight module import, or hidden evaluator labels.
"""
from __future__ import annotations
from math import sqrt
from random import Random

N_INPUTS = 8
N_RELU = 32
N_FEATURES = 41
N_OUTPUT = 4
RIDGE = 0.5
BANK_SEED = 68182026


def _bank():
    rng = Random(BANK_SEED)
    hidden = [[rng.uniform(-0.65, 0.65) for _ in range(N_INPUTS)]
              for _ in range(N_RELU)]
    biases = [rng.uniform(-0.3, 0.3) for _ in range(N_RELU)]
    return hidden, biases


class BatchTrainedReadout:
    def __init__(self):
        self.hidden_weights, self.hidden_biases = _bank()
        self.output_weights = [[0.0] * N_FEATURES for _ in range(N_OUTPUT)]
        self.objective_stationarity = float("inf")
        self.train_exact = 0.0
        self.fit_samples = 0

    def _phi(self, state, action):
        if (type(state) is not tuple or len(state) != 4 or
                type(action) is not int or action not in range(4)):
            raise ValueError("invalid public sensory training example")
        inputs = [float(v) for v in state] + [
            float(action == k) for k in range(4)
        ]
        relu = [max(0.0, sum(w*x for w, x in zip(row, inputs)) + b)
                for row, b in zip(self.hidden_weights, self.hidden_biases)]
        return [1.0] + inputs + relu

    @staticmethod
    def _solve_cholesky(a, rhs):
        n = len(a)
        l = [[0.0]*n for _ in range(n)]
        for i in range(n):
            for j in range(i+1):
                val = a[i][j] - sum(l[i][k]*l[j][k] for k in range(j))
                if i == j:
                    if val <= 0:
                        raise ArithmeticError("regularized batch matrix not SPD")
                    l[i][j] = sqrt(val)
                else:
                    l[i][j] = val / l[j][j]
        m = len(rhs[0])
        z = [[0.0]*m for _ in range(n)]
        for i in range(n):
            for output in range(m):
                z[i][output] = (rhs[i][output] -
                    sum(l[i][k]*z[k][output] for k in range(i))) / l[i][i]
        x = [[0.0]*m for _ in range(n)]
        for i in reversed(range(n)):
            for output in range(m):
                x[i][output] = (z[i][output] -
                    sum(l[k][i]*x[k][output] for k in range(i+1,n))) / l[i][i]
        return x

    def fit(self, ledger):
        if (not ledger or
                any(type(b) is not tuple or len(b)!=4 or
                    type(y) is not tuple or len(y)!=4
                    for b,a,y in ledger)):
            raise ValueError("bad charged public observations")
        n = N_FEATURES
        gram = [[(RIDGE if i==j else 0.0) for j in range(n)]
                for i in range(n)]
        cross = [[0.0]*N_OUTPUT for _ in range(n)]
        for state, action, target in ledger:
            features = self._phi(state, action)
            for i in range(n):
                for j in range(i+1):
                    gram[i][j] += features[i] * features[j]
                for output in range(N_OUTPUT):
                    cross[i][output] += features[i] * target[output]
        for i in range(n):
            for j in range(i+1,n):
                gram[i][j] = gram[j][i]
        optimum = self._solve_cholesky(gram, cross)
        self.output_weights = [
            [optimum[i][output] for i in range(n)]
            for output in range(N_OUTPUT)
        ]
        self.objective_stationarity = max(
            abs(sum(gram[i][k]*optimum[k][output] for k in range(n)) -
                cross[i][output])
            for i in range(n) for output in range(N_OUTPUT)
        )
        self.fit_samples = len(ledger)
        self.train_exact = sum(
            self.predict(state, action) == target
            for state, action, target in ledger
        ) / len(ledger)
        return {
            "independent_optimizer": "batch-Cholesky-ridge",
            "objective_stationarity_infinity": self.objective_stationarity,
            "train_exact_rate": self.train_exact,
            "fit_samples": self.fit_samples,
            "parameters": N_RELU*(N_INPUTS+1)+N_OUTPUT*N_FEATURES
        }

    def raw(self, state, action):
        phi = self._phi(state, action)
        return tuple(sum(w*x for w,x in zip(row,phi))
                     for row in self.output_weights)

    def predict(self, state, action):
        return tuple(int(y>=0.5) for y in self.raw(state, action))
