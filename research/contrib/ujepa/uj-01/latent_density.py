"""UJ-01 DEV-only conditional latent density head. No encoder or scientific data.

One component is the deterministic-mean Gaussian control; two components
learn competing futures. Inputs are bounded continuous latent coordinates,
not token IDs. Both use the same proper likelihood and public target signal.
"""
import math
import random


def vector(values, size):
    if len(values) != size:
        raise ValueError("latent dimension mismatch")
    result = tuple(float(v) for v in values)
    if any(not math.isfinite(v) or abs(v) > 1 for v in result):
        raise ValueError("latent outside [-1, 1]")
    return result


def logsumexp(values):
    peak = max(values)
    return peak + math.log(sum(math.exp(v - peak) for v in values))


class LatentDensity:
    """Local online gradient updates; fixed variance, bounded coefficients."""
    def __init__(self, context_dim=4, target_dim=2, components=2, seed=0,
                 sigma=0.5, rate=0.02):
        if not all(type(d) is int and 1 <= d <= 64
                   for d in (context_dim, target_dim)):
            raise ValueError("invalid dimensions")
        if type(components) is not int or components not in (1, 2):
            raise ValueError("invalid component count")
        if not (0.25 <= sigma <= 1 and 0 < rate <= 0.05):
            raise ValueError("invalid learning configuration")
        self.context_dim, self.target_dim = context_dim, target_dim
        self.components, self.sigma, self.rate = components, sigma, rate
        rng = random.Random(seed)
        width = context_dim + 1
        self.means = [[[rng.uniform(-0.05, 0.05) for _ in range(width)]
                       for _ in range(target_dim)] for _ in range(components)]
        self.gates = [[0.0] * width for _ in range(components)]

    def _forward(self, context):
        x = (1.0,) + vector(context, self.context_dim)
        def dot(w):
            return sum(a*b for a, b in zip(w, x))
        logits = [dot(w) for w in self.gates]
        normalizer = logsumexp(logits)
        logs = [v-normalizer for v in logits]
        means = [tuple(math.tanh(dot(w)) for w in component)
                 for component in self.means]
        return x, logs, means

    def predict(self, context):
        _, logs, means = self._forward(context)
        return tuple((math.exp(p), mu) for p, mu in zip(logs, means))

    def _score(self, context, target):
        y = vector(target, self.target_dim)
        x, logs, means = self._forward(context)
        variance = self.sigma**2
        constant = self.target_dim * math.log(self.sigma * math.sqrt(2*math.pi))
        joints = [p - constant - sum((t-m)**2 for t,m in zip(y,mu))/(2*variance)
                  for p,mu in zip(logs,means)]
        evidence = logsumexp(joints)
        return x, y, logs, means, joints, evidence

    def nll(self, context, target):
        return -self._score(context, target)[-1]

    def observe(self, context, target):
        """Return pre-update NLL; prediction alone never changes memory."""
        x,y,logs,means,joints,evidence = self._score(context, target)
        def update(row, gradient):
            for i, v in enumerate(x):
                row[i] = max(-4.0, min(4.0, row[i]+self.rate*gradient*v))
        for k in range(self.components):
            responsibility = math.exp(joints[k]-evidence)
            update(self.gates[k], responsibility-math.exp(logs[k]))
            for d, mu in enumerate(means[k]):
                gradient = responsibility*(y[d]-mu)*(1-mu*mu)/(self.sigma**2)
                update(self.means[k][d], gradient)
        return -evidence
