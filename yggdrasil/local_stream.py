"""NCI04 maintained-native, bounded one-hop developmental experience stream.

Every cell updates its own predictor from observed next-state local evidence.
The only communication edges are the ring's two immediate neighbors; no
global winner lookup, predetermined entity ID, or task-indexed memory.
This does not by itself prove functional regeneration or learned causality.
"""
import json
import math

CELLS = 8
FEATURES = 4

def _signal(values):
    if not isinstance(values, (tuple, list)) or len(values) != CELLS:
        raise ValueError("eight sensor values required")
    if any(type(v) not in (int, float) or not math.isfinite(v) or not -1 <= v <= 1 for v in values):
        raise ValueError("invalid bounded sensor")
    return [float(v) for v in values]

def _squash(value):
    return 1 / (1 + math.exp(-max(-30.0, min(30.0, value))))

class LocalStream:
    """Eight fixed-degree cells with untied *locally* learned predictors.

    Damage deletes a cell's state and parameters. Reopening a cell restores
    only the ability to learn from NEW observations, not its old weights.
    """

    def __init__(self):
        self.weights = [[0.0] * FEATURES for _ in range(CELLS)]
        self.state = [0.0] * CELLS
        self.alive = [True] * CELLS
        self.updates = 0

    def _features(self, signals, cell):
        left, right = (cell - 1) % CELLS, (cell + 1) % CELLS
        return (1.0, signals[cell],
                self.state[left] if self.alive[left] else 0.0,
                self.state[right] if self.alive[right] else 0.0)

    def predict_local(self, stimulus):
        x = _signal(stimulus)
        return tuple(_squash(sum(w * v for w, v in zip(self.weights[i], self._features(x, i))))
                     if self.alive[i] else 0.5 for i in range(CELLS))

    def observe_local(self, stimulus, observed_next, rate=0.1):
        x = _signal(stimulus)
        y = _signal(observed_next)
        if type(rate) not in (int, float) or not math.isfinite(rate) or not 0 < rate <= .25:
            raise ValueError("invalid plasticity rate")
        if self.updates >= 1_000_000:
            raise ValueError("local stream update budget exhausted")
        # Predict with the OLD synchronous neighborhood before any local writes.
        guesses = self.predict_local(x)
        next_weights = [row[:] for row in self.weights]
        for cell in range(CELLS):
            if not self.alive[cell]:
                continue
            delta = rate * (y[cell] - guesses[cell])
            for j, value in enumerate(self._features(x, cell)):
                next_weights[cell][j] = max(-8.0, min(8.0, next_weights[cell][j] + delta * value))
        next_state = [x[i] if self.alive[i] else 0.0 for i in range(CELLS)]
        self.weights = next_weights
        self.state = next_state
        self.updates += 1

    def lesion_local(self, cell):
        if type(cell) is not int or not 0 <= cell < CELLS:
            raise ValueError("invalid cell")
        self.weights[cell] = [0.0] * FEATURES
        self.state[cell] = 0.0
        self.alive[cell] = False

    def rehabilitate_local(self, cell):
        if type(cell) is not int or not 0 <= cell < CELLS or self.alive[cell]:
            raise ValueError("cell not available for rehabilitation")
        # Zeroed cell is now plastic again; no former phenotype is reintroduced.
        self.alive[cell] = True
        self.weights[cell] = [0.0] * FEATURES
        self.state[cell] = 0.0

    def snapshot_local(self):
        return json.dumps({"schema": "yggdrasil.nci04.localstream.v1",
                           "weights": self.weights, "state": self.state,
                           "alive": self.alive, "updates": self.updates},
                          sort_keys=True, separators=(",", ":"))

    def restore_local(self, raw):
        if not isinstance(raw, str) or not 0 < len(raw) <= 8192:
            raise ValueError("invalid local snapshot size")
        data = json.loads(raw)
        if not isinstance(data, dict) or set(data) != {"schema", "weights", "state", "alive", "updates"}:
            raise ValueError("invalid snapshot fields")
        if data["schema"] != "yggdrasil.nci04.localstream.v1":
            raise ValueError("unexpected source identity")
        w, state, alive, updates = data["weights"], data["state"], data["alive"], data["updates"]
        if not isinstance(w, list) or len(w) != CELLS or any(
                not isinstance(row, list) or len(row) != FEATURES or any(
                    type(value) not in (int, float) or not math.isfinite(value) or abs(value) > 8
                    for value in row) for row in w):
            raise ValueError("invalid local weights")
        _signal(state)
        if not isinstance(alive, list) or len(alive) != CELLS or any(type(v) is not bool for v in alive):
            raise ValueError("invalid local cell availability")
        if type(updates) is not int or not 0 <= updates <= 1_000_000:
            raise ValueError("invalid local update count")
        # Commit only after all checks; never alias caller-owned arrays.
        self.weights = [[float(v) for v in row] for row in w]
        self.state = list(map(float, state))
        self.alive = alive.copy()
        self.updates = updates
