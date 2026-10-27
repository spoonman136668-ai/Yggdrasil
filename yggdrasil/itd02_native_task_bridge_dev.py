"""Opt-in, PUBLIC-only bridge to Yggdrasil's existing native LocalTaskRuntime.

Engineering-only adapter. The evaluator/source owner supplies legal public
transitions; this module has no POMDP model, simulator, hidden-state access,
upstream imports, scientific acceptance or first-use authority.

Neither native runtime nor R7 is edited. Both original local cellular
predictor and the bounded ring-memory policy fit on the *same* public events.
"""
import hashlib
import json
import math

from .task_runtime import LocalTaskRuntime
from .itd02_local_ring_memory_dev import (
    ACTIONS, ACTION_SITES, CELLS, NativeRingMemoryDev, OBSERVATIONS, OBS_SITES,
    _canonical, _finite,
)

SCHEMA = "ygg.itd02.native_task_ring_bridge.source_only.v5"
REWARDS = (-3, 0, 10)  # source-declared observable labels; NOT source reward law
MAX_BYTES = 65536
RING = tuple(((i - 1) % CELLS, (i + 1) % CELLS) for i in range(CELLS))


def public_bits(observation, action):
    if type(observation) is not str or observation not in OBSERVATIONS:
        raise ValueError("INVALID_PUBLIC_OBSERVATION")
    if type(action) is not str or action not in ACTIONS:
        raise ValueError("INVALID_PUBLIC_ACTION")
    cells = [0] * CELLS
    cells[OBS_SITES[OBSERVATIONS.index(observation)]] = 1
    cells[ACTION_SITES[ACTIONS.index(action)]] = 1
    return cells


def _temporal_public_bits(observation, action, phase):
    """Two local temporal observations, never an action bit at reward sites.

    Site pairs neighboring the original reward heads jointly distinguish
    all 15 public observation-action contexts *across both phases*.
    This does not add a learnable model or a global message edge.
    """
    # Run the original public-interface validations before constructing codes.
    public_bits(observation, action)
    if type(phase) is not int or phase not in (0, 1):
        raise ValueError("INVALID_PUBLIC_ENCODING_PHASE")
    index = ACTIONS.index(action) * len(OBSERVATIONS) + OBSERVATIONS.index(observation)
    high, low = divmod(index, 4)
    cell_symbols = {1: high, 7: low, 3: low, 4: high, 6: low}
    result = [0] * CELLS
    for site, symbol in cell_symbols.items():
        result[site] = (symbol >> phase) & 1
    return result


def public_outcome(next_observation, reward):
    if type(next_observation) is not str or next_observation not in OBSERVATIONS:
        raise ValueError("INVALID_PUBLIC_SUCCESSOR")
    if type(reward) is not int or reward not in REWARDS:
        raise ValueError("INVALID_PUBLIC_REWARD_CATEGORY")
    cells = [0] * CELLS
    cells[OBS_SITES[OBSERVATIONS.index(next_observation)]] = 1
    cells[ACTION_SITES[REWARDS.index(reward)]] = 1
    return cells


class NativeTaskRingBridgeDev:
    """Existing 8-cell predictor plus opt-in locally retained reward memory.

    Candidate action evaluation is through the genuine LocalTaskRuntime.predict
    and fixed-category PUBLIC reward readout. The memory component supplies a
    second locally routed score. No global latent state is exposed to either
    learner; no fixed source transition or reward *rules* are installed.
    """
    def __init__(self, native=None, memory=None):
        self.native = LocalTaskRuntime() if native is None else native
        self.memory = NativeRingMemoryDev() if memory is None else memory
        if type(self.native) is not LocalTaskRuntime or self.native.neighbors != RING:
            raise ValueError("REQUIRES_ORIGINAL_EIGHT_CELL_RING")
        if type(self.memory) is not NativeRingMemoryDev:
            raise ValueError("REQUIRES_BOUNDED_MEMORY_MODEL")
        if self.native.damaged:
            raise ValueError("REQUIRES_INTACT_NATIVE_CELLS")
        self._observation = None
        self._frozen_native = None
        self.transitions = 0
        self.score_calls = 0
        # Eight deterministic bounded cell-local traces, not trained weights.
        self.cell_trace = [0.] * CELLS

    def start_observation(self, observation):
        if self._observation is not None or self.memory.pending:
            raise ValueError("PUBLIC_TRANSITION_PENDING")
        if self._frozen_native is not None and self._native_identity() != self._frozen_native:
            raise ValueError("NATIVE_FROZEN_PARAMETER_DRIFT")
        self.memory.advance(observation)
        self._observation = observation

    def _native_identity(self):
        # The original runtime snapshot includes event counters, so freeze
        # the *trained genome and roles*, not incidental accounting counters.
        return hashlib.sha256(_canonical({
            "genome": self.native.core.genome,
            "roles": self.native.core.roles,
            "neighbors": self.native.neighbors,
        })).hexdigest()

    def native_reward_scores(self):
        if self._observation is None or not self.memory.pending:
            raise ValueError("PUBLIC_OBSERVATION_REQUIRED")
        if self._frozen_native is not None and self._native_identity() != self._frozen_native:
            raise ValueError("NATIVE_FROZEN_PARAMETER_DRIFT")
        scores = []
        for action in ACTIONS:
            # Public action-conditioning through native own/neighbor cells.
            # Each candidate is scored twice, using two source-blind temporal
            # neighbor-only binary views. Original native core remains intact.
            phase_scores = []
            for phase in (0, 1):
                predictions = self.native.predict(
                    _temporal_public_bits(self._observation, action, phase))
                phase_scores.append(sum(
                    float(value) * predictions[ACTION_SITES[index]]
                    for index, value in enumerate(REWARDS)))
            scores.append(sum(phase_scores) / 2. + .10 * sum(
                float(value) * self.cell_trace[ACTION_SITES[index]]
                for index, value in enumerate(REWARDS)))
        self.score_calls += 1
        return scores

    def choose(self):
        native = self.native_reward_scores()
        memory = self.memory.q_values()
        # Source-blind fixed fusion, not hidden-state access or oracle planning.
        combined = [memory[i] + .15 * native[i] for i in range(len(ACTIONS))]
        self.memory.action_calls += 1
        return ACTIONS[max(range(len(ACTIONS)), key=lambda i: combined[i])]

    def accept_public_transition(self, action, next_observation, reward, *,
                                 learning=True, terminal=False):
        # Validate ALL public fields and authorizations before either learner
        # can mutate. Do not forward raw info or privileged environment object.
        before = (_temporal_public_bits(self._observation, action,
                                      self.transitions % 2)
                  if self._observation is not None else None)
        after = public_outcome(next_observation, reward)
        if before is None or not self.memory.pending:
            raise ValueError("NO_PENDING_PUBLIC_TRANSITION")
        if type(learning) is not bool or type(terminal) is not bool:
            raise ValueError("INVALID_PUBLIC_FLAGS")
        if self.native.damaged:
            raise ValueError("NATIVE_LESION_NOT_QUALIFIED_FOR_FIT")
        if learning:
            if self._frozen_native is not None or self.memory._frozen_hash is not None:
                raise ValueError("FITTING_FORBIDDEN_DURING_EVALUATION")
        else:
            if self._frozen_native is None or self.memory._frozen_hash is None:
                raise ValueError("BOTH_MODELS_MUST_BE_FROZEN")
            if self._native_identity() != self._frozen_native or (
                    self.memory.parameter_sha256() != self.memory._frozen_hash):
                raise ValueError("FROZEN_WEIGHT_IDENTITY_DRIFT")
        native_snap = self.native.snapshot()
        memory_snap = self.memory.checkpoint()
        trace_snap = list(self.cell_trace)
        try:
            if learning:
                self.native.observe(before, after)
            self.memory.feedback(action, reward, learning=learning, terminal=terminal)
            if learning:
                # Original public input bits only. Each cell updates its own
                # retained register; no oracle or other cell's state enters.
                self.cell_trace = [
                    max(-1., min(1., .75 * self.cell_trace[i]
                                 + .125 * (2 * before[RING[i][0]] - 1)
                                 + .125 * (2 * before[RING[i][1]] - 1)))
                    for i in range(CELLS)
                ]
            self.transitions += 1
            self._observation = None
        except Exception:
            self.native = LocalTaskRuntime.restore(native_snap)
            self.memory = NativeRingMemoryDev.restore(memory_snap)
            self.cell_trace = trace_snap
            raise

    def reset_episode(self):
        if self._observation is not None or self.memory.pending:
            raise ValueError("PENDING_PUBLIC_STEP")
        self.memory.reset_episode()

    def start_frozen_evaluation(self, native_sha, memory_sha):
        if self._observation is not None or self.memory.pending:
            raise ValueError("PENDING_PUBLIC_STEP")
        if type(native_sha) is not str or native_sha != self._native_identity():
            raise ValueError("NATIVE_WEIGHT_IDENTITY_MISMATCH")
        self.memory.start_frozen_evaluation(memory_sha)
        self._frozen_native = native_sha

    def model_identities(self):
        return {"native": self._native_identity(),
                "memory": self.memory.parameter_sha256()}

    def checkpoint(self):
        body = {"schema": SCHEMA, "native": json.loads(self.native.snapshot()),
                "memory": json.loads(self.memory.checkpoint()),
                "observation": self._observation,
                "transitions": self.transitions, "score_calls": self.score_calls,
                "frozen_native_sha256": self._frozen_native,
                "cell_trace": self.cell_trace}
        data = _canonical(body)
        if len(data) > MAX_BYTES:
            raise ValueError("BRIDGE_CHECKPOINT_OVER_BUDGET")
        return _canonical({"body": body, "sha256": hashlib.sha256(data).hexdigest()})

    @classmethod
    def restore(cls, raw):
        try:
            if type(raw) is not bytes or not 0 < len(raw) <= MAX_BYTES:
                raise ValueError("BRIDGE_CHECKPOINT_SIZE")
            envelope = json.loads(raw)
            if type(envelope) is not dict or set(envelope) != {"body", "sha256"}:
                raise ValueError("BRIDGE_CHECKPOINT_ENVELOPE")
            body = envelope["body"]
            if hashlib.sha256(_canonical(body)).hexdigest() != envelope["sha256"]:
                raise ValueError("BRIDGE_CHECKPOINT_DIGEST")
            if type(body) is not dict or set(body) != {
                    "schema", "native", "memory", "observation",
                    "transitions", "score_calls", "frozen_native_sha256",
                    "cell_trace"} or body["schema"] != SCHEMA:
                raise ValueError("BRIDGE_CHECKPOINT_SCHEMA")
            if (body["observation"] is not None and
                    (type(body["observation"]) is not str or
                     body["observation"] not in OBSERVATIONS)):
                raise ValueError("BRIDGE_CHECKPOINT_PUBLIC_OBS")
            if any(type(body[k]) is not int or not 0 <= body[k] <= 100000000
                   for k in ("transitions", "score_calls")):
                raise ValueError("BRIDGE_CHECKPOINT_COUNTS")
            native = LocalTaskRuntime.restore(json.dumps(body["native"]))
            memory = NativeRingMemoryDev.restore(_canonical(body["memory"]))
            if (body["observation"] is None) != (not memory.pending):
                raise ValueError("BRIDGE_CHECKPOINT_PENDING_IDENTITY")
            obj = cls(native, memory)
            obj._observation = body["observation"]
            obj.transitions = body["transitions"]
            obj.score_calls = body["score_calls"]
            trace = body["cell_trace"]
            if (type(trace) is not list or len(trace) != CELLS or
                    any(type(x) not in (int, float) or not math.isfinite(x)
                        or not -1. <= x <= 1. for x in trace)):
                raise ValueError("BRIDGE_CELL_TRACE_INVALID")
            obj.cell_trace = [float(x) for x in trace]
            frozen_native = body["frozen_native_sha256"]
            if (frozen_native is None) != (memory._frozen_hash is None):
                raise ValueError("BRIDGE_FROZEN_MODE_MISMATCH")
            if frozen_native is not None:
                if (type(frozen_native) is not str or len(frozen_native) != 64 or
                        any(c not in "0123456789abcdef" for c in frozen_native) or
                        frozen_native != obj._native_identity()):
                    raise ValueError("BRIDGE_FROZEN_NATIVE_IDENTITY_MISMATCH")
            obj._frozen_native = frozen_native
            return obj
        except (ValueError, TypeError, OverflowError, KeyError, AttributeError) as exc:
            raise ValueError("UNTRUSTED_NATIVE_BRIDGE_CHECKPOINT") from exc
