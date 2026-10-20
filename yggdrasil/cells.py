"""Candidate-only Yggdrasil local developmental learning; no acceptance authority.

Each cell predicts its own next state using its prior state and immediate
neighbors. Local error updates cause untied parameters to differentiate.
Neighbor parameter copying is a conventional redundancy control and MUST NOT
be reported as genuine developmental regeneration.
"""
import json
import math

CELLS = 8
CHANNELS = 7

def _bits(values):
    if not isinstance(values, (list, tuple)) or len(values) != CELLS or any(type(v) is not int or v not in (0, 1) for v in values):
        raise ValueError("expected eight binary cell values")

def _sigmoid(z):
    z = max(-40.0, min(40.0, z))
    return 1.0 / (1.0 + math.exp(-z))

def local_features(bits, i):
    _bits(bits)
    x = 2 * bits[i] - 1
    a = 2 * bits[(i - 1) % CELLS] - 1
    b = 2 * bits[(i + 1) % CELLS] - 1
    return (1.0, float(x), float(a), float(b), float(a*b), float(x*a), float(x*b))

class DevelopmentalCells:
    """Eight fixed-budget cells with independently updated local parameters."""
    def __init__(self):
        self.weights = [[0.0] * CHANNELS for _ in range(CELLS)]
        self.updates = 0

    def predict(self, bits):
        _bits(bits)
        return [_sigmoid(sum(w*f for w, f in zip(self.weights[i], local_features(bits, i)))) for i in range(CELLS)]

    def observe(self, bits, consequences, rate=0.038):
        _bits(bits)
        _bits(consequences)
        if not isinstance(rate, (int, float)) or not math.isfinite(rate) or not 0 < rate <= 1:
            raise ValueError("invalid local learning rate")
        forecast = self.predict(bits)
        next_weights = [row[:] for row in self.weights]
        for i in range(CELLS):
            delta = rate * (consequences[i] - forecast[i])
            for k, feature in enumerate(local_features(bits, i)):
                next_weights[i][k] += delta * feature
                if not math.isfinite(next_weights[i][k]):
                    raise ValueError("nonfinite update")
        self.weights = next_weights
        self.updates += 1

    def lesion(self, i):
        if type(i) is not int or not 0 <= i < CELLS:
            raise ValueError("invalid cell")
        self.weights[i] = [0.0] * CHANNELS

    def neighbor_copy_baseline(self, i):
        if type(i) is not int or not 0 <= i < CELLS:
            raise ValueError("invalid cell")
        self.weights[i] = [(a+b)/2 for a, b in zip(self.weights[(i-1)%CELLS], self.weights[(i+1)%CELLS])]

    def snapshot(self):
        return json.dumps({"schema":"yggdrasil.t45o.cells.v1","weights":self.weights,"updates":self.updates}, sort_keys=True, separators=(",",":"))

    def restore(self, text):
        if not isinstance(text, str) or len(text)>4096:
            raise ValueError("invalid snapshot")
        value=json.loads(text)
        if set(value)!={"schema","weights","updates"} or value["schema"]!="yggdrasil.t45o.cells.v1":
            raise ValueError("invalid schema")
        weights=value["weights"]
        if not isinstance(weights,list) or len(weights)!=CELLS or any(not isinstance(row,list) or len(row)!=CHANNELS for row in weights):
            raise ValueError("invalid weight shape")
        for row in weights:
            for v in row:
                if type(v) not in (int,float) or not math.isfinite(v):
                    raise ValueError("invalid weights")
        updates=value["updates"]
        if type(updates) is not int or not 0<=updates<=1_000_000_000:
            raise ValueError("invalid update count")
        self.weights=[[float(v) for v in row] for row in weights]
        self.updates=updates
