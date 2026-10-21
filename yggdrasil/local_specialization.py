"""NCI-04C developmental candidate: experience-induced local specialization.
Self-supervised next-cell-state prediction; no target-function labels,
local role assignments, previous lesion state, or global cell lookup.
Recovery uses learned neighbor messages, never copied parameters.
"""
import json
import math
COUNT = 8
PARAMS = 4
def check_view(view):
    if not isinstance(view, (tuple, list)) or len(view) != COUNT:
        raise ValueError("eight local signals required")
    if any(type(v) not in (int, float) or not math.isfinite(v) or not 0 <= v <= 1 for v in view):
        raise ValueError("invalid bounded local observation")
    return [float(v) for v in view]
def logistic(value):
    return 1 / (1 + math.exp(-max(-30.0, min(30.0, value))))
class LocalSpecialization:
    def __init__(self, rate=0.15, teach=0.3):
        if (type(rate) not in (int, float) or not math.isfinite(rate)
                or not 0 <= rate <= .25):
            raise ValueError("invalid learning rate")
        if (type(teach) not in (int, float) or not math.isfinite(teach)
                or not 0 <= teach <= .5):
            raise ValueError("invalid local teaching rate")
        self.rate = float(rate)
        self.teach = float(teach)
        self.weights = [[0.0] * PARAMS for _ in range(COUNT)]
        self.trace = [0.5] * COUNT
        self.alive = [True] * COUNT
        self.recovering = [False] * COUNT
        self.steps = 0
    def local_features(self, current, i):
        left, right = (i-1) % COUNT, (i+1) % COUNT
        return (1.0, current[i],
                self.trace[left] if self.alive[left] else .5,
                self.trace[right] if self.alive[right] else .5)
    def predict(self, current):
        view = check_view(current)
        result = []
        for i in range(COUNT):
            if not self.alive[i]:
                result.append(.5)
            else:
                result.append(logistic(sum(w*f for w, f in zip(
                    self.weights[i], self.local_features(view, i)))))
        return tuple(result)
    def learn(self, current, observed_next):
        x, y = check_view(current), check_view(observed_next)
        if self.steps >= 1_000_000:
            raise ValueError("local step budget exhausted")
        old = self.predict(x)
        new_weights = [w.copy() for w in self.weights]
        new_trace = self.trace.copy()
        for i in range(COUNT):
            if not self.alive[i]:
                continue
            left, right = (i-1) % COUNT, (i+1) % COUNT
            predicted = old[i]
            target = y[i]
            if (self.recovering[i] and self.alive[left] and self.alive[right]
                    and abs(old[left] - old[right]) < .15):
                target = (1 - self.teach) * target + self.teach * (old[left] + old[right])/2
            deviation = target-predicted
            for k, feature in enumerate(self.local_features(x, i)):
                value = new_weights[i][k] + self.rate * deviation * feature
                new_weights[i][k] = max(-5., min(5., value))
            new_trace[i] = .8 * self.trace[i] + .2 * y[i]
        self.weights, self.trace = new_weights, new_trace
        self.steps += 1
    def lesion(self, i):
        if type(i) is not int or not 0 <= i < COUNT:
            raise ValueError("invalid lesion location")
        self.weights[i] = [0.0] * PARAMS
        self.trace[i] = .5
        self.alive[i] = False
        self.recovering[i] = False
    def regrow(self, i):
        if type(i) is not int or not 0 <= i < COUNT or self.alive[i]:
            raise ValueError("invalid regeneration request")
        self.alive[i] = True
        self.recovering[i] = True
        self.weights[i] = [0.0] * PARAMS
        self.trace[i] = .5
    def snapshot(self):
        return json.dumps({"schema": "yggdrasil.nci04c.local.v1", "weights": self.weights,
                           "trace": self.trace, "alive": self.alive,
                           "recovering": self.recovering, "steps": self.steps},
                          sort_keys=True, separators=(",", ":"))
    def restore(self, raw):
        if not isinstance(raw, str) or not 0 < len(raw) <= 16000:
            raise ValueError("invalid checkpoint length")
        d = json.loads(raw)
        if (not isinstance(d, dict) or set(d) !=
                {"schema", "weights", "trace", "alive", "recovering", "steps"}
                or d["schema"] != "yggdrasil.nci04c.local.v1"):
            raise ValueError("source identity drift")
        w, traces, alive, recover, steps = (d[name] for name in
                            ("weights", "trace", "alive", "recovering", "steps"))
        if (not isinstance(w, list) or len(w) != COUNT or any(
              not isinstance(row, list) or len(row) != PARAMS or any(
                  type(v) not in (int, float) or not math.isfinite(v) or abs(v)>5
                  for v in row) for row in w)):
            raise ValueError("invalid learned parameters")
        check_view(traces)
        if (not isinstance(alive, list) or not isinstance(recover, list)
                or len(alive) != COUNT or len(recover) != COUNT
                or any(type(v) is not bool for v in alive+recover)):
            raise ValueError("invalid cell activation")
        if type(steps) is not int or not 0 <= steps <= 1_000_000:
            raise ValueError("invalid developmental age")
        self.weights = [row.copy() for row in w]
        self.trace = traces.copy()
        self.alive = alive.copy()
        self.recovering = recover.copy()
        self.steps = steps
