"""ST1 candidate native cellular structural learning: two-hop graph selection.

Frozen original S1 45 neural coefficients plus eight existing state scalars.
Receiver-local structural scores are learned only from *actual subsequent*
public outcomes. Four alternatives require additional training message reads;
they are neither free information nor proof of a physically routed network.
No hidden-world oracle, scientific first-use or controller authority.
"""
import hashlib
import json
import math

from research.nci04_s1.local_messages import LocalPredictiveMessages45
from research.mr18.native_public_learning import validate
from yggdrasil.developmental import sig, valid

N, D, WINDOW, MAX_SWITCHES = 8, 7, 32, 2
MARGIN = 0.10
SCHEMA = "yggdrasil.nci04.st1.adaptive-topology.v1"


def options(cell):
    if type(cell) is not int or not 0 <= cell < N:
        raise ValueError("NCI04_ST1_INVALID_CELL")
    return tuple(((cell - l) % N, (cell + r) % N)
                 for l, r in ((1, 1), (2, 1), (1, 2), (2, 2)))


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False)


class NativeAdaptiveTopology45:
    """Opt-in reversible developmental connection choice at fixed edge count."""

    def __init__(self, original_s1_snapshot):
        self.native = LocalPredictiveMessages45.restore(original_s1_snapshot)
        if self.native.runtime.neighbors != tuple(options(i)[0] for i in range(N)):
            raise ValueError("NCI04_ST1_NOT_ORIGINAL_RING")
        self.weights_sha256 = self._weight_digest()
        self.choices = [0] * N
        self.losses = [[0.0] * 4 for _ in range(N)]
        self.window_seen = 0
        self.switches = [0] * N
        self.total_windows = 0

    def _weight_digest(self):
        return hashlib.sha256(
            self.native.runtime.core.snapshot().encode("utf-8")).hexdigest()

    def _weights_frozen(self):
        if self._weight_digest() != self.weights_sha256:
            raise ValueError("NCI04_ST1_NATIVE_COEFFICIENT_DRIFT")

    def graph(self):
        return tuple(options(i)[self.choices[i]] for i in range(N))

    def _predictions(self, raw, bits, action, all_choices):
        validate(raw, bits, action)
        self._weights_frozen()
        f = self.native.features(raw, bits, action)
        g = self.native.runtime.core.genome
        roles = self.native.runtime.core.roles
        state = self.native.state
        rows = []
        for i in range(N):
            base = (sum(g[0][j] * f[i][j] for j in range(D))
                    + roles[i][0]
                    + state[i] *
                    sum(g[1][j] * f[i][j] for j in range(D)))
            selection = range(4) if all_choices else (self.choices[i],)
            rows.append(tuple(sig(
                base + roles[i][1] * (state[left] + state[right]) / 2.0)
                for q in selection
                for left, right in (options(i)[q],)))
        return rows

    def predict(self, raw, bits, action):
        # Exactly sixteen selected messages read across the eight cells.
        return [row[0] for row in self._predictions(raw, bits, action, False)]

    def _finish_window(self):
        if self.window_seen != WINDOW:
            raise ValueError("NCI04_ST1_WINDOW_NOT_COMPLETE")
        for i in range(N):
            if self.switches[i] >= MAX_SWITCHES:
                continue
            best = min(range(4), key=lambda q: (self.losses[i][q], q))
            old = self.choices[i]
            if (best != old and
                    self.losses[i][best] + MARGIN < self.losses[i][old]):
                self.choices[i] = best
                self.switches[i] += 1
        self.losses = [[0.0] * 4 for _ in range(N)]
        self.window_seen = 0
        self.total_windows += 1

    def observe(self, raw, bits, action, public_outcomes, *, train=True):
        """Scores alternatives after true public outcomes; no neural retraining.

        An owner must separately authenticate the original source and its
        actual event. Merely calling this API cannot admit a science result.
        """
        validate(raw, bits, action)
        valid(public_outcomes)
        if type(train) is not bool:
            raise ValueError("NCI04_ST1_INVALID_MODE")
        prior = self.snapshot()
        try:
            predicted = self.predict(raw, bits, action)
            variants = (self._predictions(raw, bits, action, True)
                        if train else None)
            # S1 train=False updates its local public-history state ONLY.
            self.native.observe(raw, bits, action, public_outcomes, train=False)
            self._weights_frozen()
            if train:
                for i in range(N):
                    for q in range(4):
                        d = public_outcomes[i] - variants[i][q]
                        self.losses[i][q] += d * d
                self.window_seen += 1
                if self.window_seen == WINDOW:
                    self._finish_window()
            if self.restore(self.snapshot()).snapshot() != self.snapshot():
                raise ValueError("NCI04_ST1_RESTORE_DRIFT")
            return predicted
        except Exception:
            self.__dict__.update(self.restore(prior).__dict__)
            raise

    def reset_episode(self):
        # Keep learned routing across episodes; reset only episodic memory.
        self._weights_frozen()
        self.native.reset_episode()

    def accounting(self):
        return {
            "original_neural_coefficients": 45,
            "original_inference_state_scalars": 8,
            "inference_neighbor_scalar_reads": 16,
            "extra_training_candidate_scalar_reads": 64,
            "extra_persistent_score_scalars": 32,
            "extra_score_float64_equivalent_bytes": 256,
            "structural_choice_registers": 8,
            "edge_reconfigurations": sum(self.switches),
            "checkpoint_bytes": len(self.snapshot().encode("utf-8")),
            "physical_distributed_messages_qualified": False,
            "scientific_first_use_qualified": False,
        }

    def snapshot(self):
        self._weights_frozen()
        return canonical({
            "schema": SCHEMA, "native": json.loads(self.native.snapshot()),
            "weights_sha256": self.weights_sha256,
            "choices": self.choices, "losses": self.losses,
            "window_seen": self.window_seen, "switches": self.switches,
            "total_windows": self.total_windows,
        })

    @classmethod
    def restore(cls, payload):
        if type(payload) is not str or len(payload) > 65536:
            raise ValueError("NCI04_ST1_BAD_SNAPSHOT_SIZE")
        try:
            d = json.loads(payload)
            if (type(d) is not dict or set(d) != {
                "schema", "native", "weights_sha256", "choices",
                "losses", "window_seen", "switches", "total_windows"
            } or d["schema"] != SCHEMA or
                type(d["choices"]) is not list or
                len(d["choices"]) != N or
                any(type(v) is not int or v not in range(4)
                    for v in d["choices"]) or
                type(d["switches"]) is not list or
                len(d["switches"]) != N or
                any(type(v) is not int or not 0 <= v <= MAX_SWITCHES
                    for v in d["switches"]) or
                type(d["losses"]) is not list or
                len(d["losses"]) != N or
                any(type(row) is not list or len(row) != 4
                    for row in d["losses"]) or
                any(type(v) is not float or
                    not math.isfinite(v) or not 0 <= v <= WINDOW
                    for row in d["losses"] for v in row) or
                type(d["window_seen"]) is not int or
                not 0 <= d["window_seen"] < WINDOW or
                type(d["total_windows"]) is not int or
                not 0 <= d["total_windows"] <= 100000000 or
                (d["window_seen"] == 0 and
                 any(v != 0 for row in d["losses"] for v in row))):
                raise ValueError("NCI04_ST1_BAD_SNAPSHOT_SHAPE")
            obj = cls(canonical(d["native"]))
            obj.choices = list(d["choices"])
            obj.losses = [list(row) for row in d["losses"]]
            obj.window_seen = d["window_seen"]
            obj.switches = list(d["switches"])
            obj.total_windows = d["total_windows"]
            if (obj.weights_sha256 != d["weights_sha256"] or
                    obj.snapshot() != payload):
                raise ValueError("NCI04_ST1_BAD_SNAPSHOT_IDENTITY")
            return obj
        except (TypeError, KeyError, OverflowError) as err:
            raise ValueError("NCI04_ST1_BAD_SNAPSHOT") from err
