"""ITD-02 bounded eight-cell local-memory *engineering candidate*.

Consumes only public observations/actions/rewards. All runtime information
travels through the existing eight-site ring via neighbor-only scalar messages.
No Shuttle/world import, privileged state, original episodes or science claim.
Frozen LocalTaskRuntime and R7 remain unchanged. This does not yet integrate
with LocalTaskRuntime's learned genome/roles; it tests a bounded new mechanism.
"""
import hashlib
import json
import math

SCHEMA = "ygg.itd02.local_ring_memory.source_only.v2"
OBSERVATIONS = ("LRV", "MRV", "docked_MRV", "Nothing", "docked_LRV")
ACTIONS = ("TurnAround", "GoForward", "Backup")
# Interleave input/output cell sites on the unchanged eight-site ring.
OBS_SITES = (1, 3, 4, 6, 7)
ACTION_SITES = (0, 2, 5)
CELLS = 8
ROUNDS = 2  # bounded two-hop neighborhood; not full ring visibility
MAX_CHECKPOINT_BYTES = 8192


def _sigmoid(x):
    return 1.0 / (1.0 + math.exp(-max(-20., min(20., x))))


def _finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def _local_exchange(values, rounds=ROUNDS):
    """One scalar per directed neighbor link per hop; no global skip edge."""
    if type(values) is not list or len(values) != CELLS or any(not _finite(v) for v in values):
        raise ValueError("INVALID_LOCAL_SIGNAL")
    if type(rounds) is not int or not 0 <= rounds <= ROUNDS:
        raise ValueError("INVALID_HOP_LIMIT")
    result = list(values)
    for _ in range(rounds):
        previous = result
        result = [(previous[i] * .5 + previous[(i - 1) % CELLS] * .25
                   + previous[(i + 1) % CELLS] * .25)
                  for i in range(CELLS)]
    return result



def _local_credit(site, signal, rounds=ROUNDS):
    """Propagate scalar reward credit only through bounded neighbor hops."""
    if type(site) is not int or not 0 <= site < CELLS or not _finite(signal):
        raise ValueError("INVALID_LOCAL_CREDIT")
    seed = [0.] * CELLS
    seed[site] = float(signal)
    return _local_exchange(seed, rounds=rounds)

def _public_pulse(observation):
    if type(observation) is not str or observation not in OBSERVATIONS:
        raise ValueError("INVALID_PUBLIC_OBSERVATION")
    pulse = [0.] * CELLS
    pulse[OBS_SITES[OBSERVATIONS.index(observation)]] = 1.
    return pulse


class NativeRingMemoryDev:
    """Locally gated episodic state and three learned neighbor-routed heads.

    Eight retained scalar cell states. Each cell has exactly one reward-trained
    retention logit; each action head reads its locally delivered two signals.
    The readout sees no raw observation array, hidden POMDP state or oracle.
    """

    def __init__(self):
        self.gates = [1.] * CELLS
        self.heads = [[0., 0., 0.] for _ in ACTIONS]  # bias, local-now, local-memory
        self.memory = [0.] * CELLS
        self._pulse = [0.] * CELLS
        self._before = [0.] * CELLS
        self.pending = False
        self.updates = 0
        self.action_calls = 0
        self.messages = 0
        self._frozen_hash = None

    def reset_episode(self):
        if self.pending:
            raise ValueError("PENDING_ACTION_NOT_FINALIZED")
        self.memory = [0.] * CELLS
        self._pulse = [0.] * CELLS
        self._before = [0.] * CELLS

    def advance(self, observation):
        if self.pending:
            raise ValueError("PREVIOUS_ACTION_NOT_FINALIZED")
        if self._frozen_hash is not None and self.parameter_sha256() != self._frozen_hash:
            raise ValueError("FROZEN_WEIGHTS_CHANGED")
        pulse = _public_pulse(observation)
        self._before = self.memory[:]
        self._pulse = pulse
        self.memory = [g * old + (1. - g) * now
                       for g, old, now in zip(map(_sigmoid, self.gates), self._before, pulse)]
        self.pending = True

    def _signals(self):
        now = _local_exchange(self._pulse)
        retained = _local_exchange(self.memory)
        self.messages += 2 * CELLS * 2 * ROUNDS  # signals x cells x neighbor directions x hops
        return now, retained

    def q_values(self):
        if not self.pending:
            raise ValueError("PUBLIC_OBSERVATION_REQUIRED")
        if self._frozen_hash is not None and self.parameter_sha256() != self._frozen_hash:
            raise ValueError("FROZEN_WEIGHTS_CHANGED")
        now, retained = self._signals()
        return [self.heads[i][0] + self.heads[i][1] * now[site]
                + self.heads[i][2] * (16. * retained[site])
                for i, site in enumerate(ACTION_SITES)]

    def choose(self):
        q = self.q_values()
        self.action_calls += 1
        return ACTIONS[max(range(3), key=lambda i: q[i])]

    def feedback(self, action, reward, *, learning=True, terminal=False):
        if not self.pending:
            raise ValueError("NO_PENDING_PUBLIC_ACTION")
        if type(action) is not str or action not in ACTIONS:
            raise ValueError("INVALID_PUBLIC_ACTION")
        if not _finite(reward) or abs(reward) > 10000 or type(learning) is not bool or type(terminal) is not bool:
            raise ValueError("INVALID_PUBLIC_REWARD_OR_FLAGS")
        if self._frozen_hash is not None:
            if learning:
                raise ValueError("FITTING_FORBIDDEN_DURING_EVALUATION")
            if self.parameter_sha256() != self._frozen_hash:
                raise ValueError("FROZEN_WEIGHTS_CHANGED")
        elif not learning:
            raise ValueError("FROZEN_EVALUATION_REQUIRED")
        if learning:
            idx = ACTIONS.index(action)
            site = ACTION_SITES[idx]
            # The response gradient is computed only from messages arriving
            # at the chosen action cell; no oracle target or central state copy.
            now, hist = self._signals()
            x = (1., now[site], 16. * hist[site])
            weights = self.heads[idx]
            prediction = sum(a * b for a, b in zip(weights, x))
            # A bounded, locally normalized recency update. Only this
            # action cell's public reward prediction is corrected; intact
            # neighbor-only routing, trainable parameter count and the native
            # LocalTaskRuntime remain unchanged. Compete against the original
            # rule and independently acting recency controls before admission.
            error = max(-13., min(13., float(reward) - prediction))
            recency_step = .7 * error / (1. + sum(v * v for v in x))
            old_mem_weight = weights[2]
            # Reward credit originates at the chosen action site and travels
            # through the same bounded neighbor-only ring, in the reverse
            # direction. Cells outside the two-hop support receive exactly 0.
            credit = _local_credit(site, max(-2., min(2., error)) * old_mem_weight)
            for cell in range(CELLS):
                if credit[cell] == 0.:
                    continue
                gate = _sigmoid(self.gates[cell])
                grad = (self._before[cell] - self._pulse[cell]) * gate * (1. - gate)
                self.gates[cell] = max(-4., min(4., self.gates[cell]
                                        + .12 * credit[cell] * grad * 16.))
            for j in range(3):
                weights[j] = max(-16., min(16., weights[j] + recency_step * x[j]))
            self.updates += 1
        self.pending = False
        if terminal:
            self.reset_episode()

    def parameter_sha256(self):
        return hashlib.sha256(_canonical({"schema": SCHEMA,
                                          "gates": self.gates, "heads": self.heads})).hexdigest()

    def start_frozen_evaluation(self, expected_sha):
        if type(expected_sha) is not str or expected_sha != self.parameter_sha256():
            raise ValueError("FITTED_PARAMETER_IDENTITY_MISMATCH")
        if self.pending:
            raise ValueError("PENDING_TRAINING_EVENT")
        self.reset_episode()
        self._frozen_hash = expected_sha

    def checkpoint(self):
        body = {"schema": SCHEMA, "gates": self.gates, "heads": self.heads,
                "memory": self.memory, "pulse": self._pulse,
                "before": self._before, "pending": self.pending,
                "updates": self.updates, "action_calls": self.action_calls,
                "messages": self.messages,
                "frozen_sha256": self._frozen_hash}
        payload = _canonical(body)
        if len(payload) > MAX_CHECKPOINT_BYTES:
            raise ValueError("CHECKPOINT_OVER_BUDGET")
        return _canonical({"body": body, "sha256": hashlib.sha256(payload).hexdigest()})

    @classmethod
    def restore(cls, raw):
        try:
            if type(raw) is not bytes or not 0 < len(raw) <= MAX_CHECKPOINT_BYTES:
                raise ValueError("BAD_CHECKPOINT_SIZE")
            data = json.loads(raw)
            if type(data) is not dict or set(data) != {"body", "sha256"}:
                raise ValueError("BAD_CHECKPOINT_ENVELOPE")
            body = data["body"]
            if hashlib.sha256(_canonical(body)).hexdigest() != data["sha256"]:
                raise ValueError("BAD_CHECKPOINT_DIGEST")
            if type(body) is not dict or set(body) != {"schema", "gates", "heads", "memory",
                                                     "pulse", "before", "pending", "updates",
                                                     "action_calls", "messages",
                                                     "frozen_sha256"} or body["schema"] != SCHEMA:
                raise ValueError("BAD_CHECKPOINT_SCHEMA")
            fields = ("gates", "memory", "pulse", "before")
            if any(type(body[k]) is not list or len(body[k]) != CELLS or
                   any(not _finite(x) or abs(x) > 16 for x in body[k]) for k in fields):
                raise ValueError("BAD_CHECKPOINT_CELLS")
            if (type(body["heads"]) is not list or len(body["heads"]) != 3 or
                    any(type(row) is not list or len(row) != 3 or
                        any(not _finite(x) or abs(x) > 16 for x in row)
                        for row in body["heads"])):
                raise ValueError("BAD_CHECKPOINT_HEADS")
            if type(body["pending"]) is not bool or any(type(body[k]) is not int or
                body[k] < 0 or body[k] > 100000000 for k in ("updates", "action_calls", "messages")):
                raise ValueError("BAD_CHECKPOINT_COUNTERS")
            obj = cls()
            obj.gates = [float(v) for v in body["gates"]]
            obj.heads = [[float(v) for v in row] for row in body["heads"]]
            obj.memory = [float(v) for v in body["memory"]]
            obj._pulse = [float(v) for v in body["pulse"]]
            obj._before = [float(v) for v in body["before"]]
            obj.pending = body["pending"]
            frozen = body["frozen_sha256"]
            if frozen is not None:
                if (type(frozen) is not str or len(frozen) != 64 or
                        any(c not in "0123456789abcdef" for c in frozen) or
                        frozen != obj.parameter_sha256()):
                    raise ValueError("BAD_FROZEN_PARAMETER_IDENTITY")
            obj._frozen_hash = frozen
            for name in ("updates", "action_calls", "messages"):
                setattr(obj, name, body[name])
            return obj
        except (ValueError, TypeError, KeyError, OverflowError) as exc:
            raise ValueError("UNTRUSTED_DEVELOPMENT_CHECKPOINT") from exc
