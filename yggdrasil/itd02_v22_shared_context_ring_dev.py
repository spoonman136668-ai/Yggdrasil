"""ITD-02 V22 optional ring-local shared learning, PUBLIC synthetic engineering.

Native original learner and V18/V20 candidate sources are unchanged. Public
inputs enter at their original physical sites. Locally constructed scalar
predictions and reward credit travel only along original 8-cell ring edges.
Seven identity channels, cue/action products and linear update are PREDEFINED,
not learned neural communication or original-world scientific cognition.
"""
import hashlib
import json
import math

from .itd02_v17_neighbor_carried_learner_dev import (
    ACTIONS, ACTION_SITES, CELLS, CHANNELS, PUBLIC_CUES, RING,
    canonical, fixed_original_identity, site_pulses,
)
from .itd02_v18_intermediate_plasticity_dev import (
    HEAD_FEATURES, HOPS, INITIAL_GAIN, MAX_CHECKPOINT_BYTES,
    REWARD_LIMITS, _valid_finite, forward_local,
)

SCHEMA = "ygg.itd02.v22.edge_shared_context.source_only.v1"
MODES = ("shared", "action_partition")
LEARNING_RATE = 1.0
WEIGHT_BOUND = 16.0
EDGE_SIGNAL_PER_PASS = CELLS * 2 * HOPS
SOURCE_SIGNAL_PER_PASS = CELLS * 2 * CHANNELS * HOPS
LEARNED_SCALARS = CELLS * HEAD_FEATURES + len(ACTIONS)


def _mix_scalars(values, hops=HOPS):
    """One scalar per directed original neighbor edge, synchronous rounds."""
    if type(hops) is not int or not 0 <= hops <= HOPS:
        raise ValueError("INVALID_SCALAR_HOP_LIMIT")
    if (type(values) is not list or len(values) != CELLS or
            any(type(x) not in (int, float) or not math.isfinite(x)
                or abs(x) > 10000 for x in values)):
        raise ValueError("INVALID_SOURCE_LOCAL_SCALARS")
    state = list(map(float, values))
    for _ in range(hops):
        old = state
        state = [
            (old[cell] + old[RING[cell][0]] + old[RING[cell][1]]) / 3.0
            for cell in range(CELLS)
        ]
    return state, CELLS * 2 * hops


def _site_features(cue, first):
    """Seven input tags transported through the unchanged V18 neighbor rule."""
    pulse = site_pulses(cue, first)
    signal, _eligibility, messages = forward_local(
        pulse, [[INITIAL_GAIN] * CHANNELS for _ in range(CELLS)])
    if messages != SOURCE_SIGNAL_PER_PASS:
        raise ValueError("ORIGINAL_SOURCE_EDGE_TRANSPORT_DRIFT")
    features = []
    for cell in range(CELLS):
        local = signal[cell]
        row = [1.0] + list(local) + [
            local[cue_index] * local[4 + first_index]
            for cue_index in range(4) for first_index in range(3)
        ]
        if len(row) != HEAD_FEATURES:
            raise ValueError("LOCAL_REPRESENTATION_DRIFT")
        features.append(row)
    return features


class SharedContextRingDev:
    """163 learnable scalars; only public rewards update cell-local parameters."""

    def __init__(self, *, mode="shared"):
        if type(mode) is not str or mode not in MODES:
            raise ValueError("INVALID_SHARED_STATE_MODE")
        if CELLS != 8 or ACTION_SITES != (0, 2, 5):
            raise ValueError("ORIGINAL_EIGHT_CELL_RING_CHANGED")
        self.native_ids = fixed_original_identity()
        self.mode = mode
        self.cell_weights = [[0.0] * HEAD_FEATURES for _ in range(CELLS)]
        self.action_biases = [0.0] * len(ACTIONS)
        self.cue = None
        self.first = None
        self.transitions = 0
        self.updates = 0
        self.forward_input_messages = 0
        self.forward_output_messages = 0
        self.reverse_credit_messages = 0
        self.frozen_sha = None

    def parameters_sha256(self):
        return hashlib.sha256(canonical({
            "mode": self.mode, "cell_weights": self.cell_weights,
            "action_biases": self.action_biases,
        })).hexdigest()

    def _check_frozen(self):
        if (self.frozen_sha is not None and
                self.frozen_sha != self.parameters_sha256()):
            raise ValueError("FROZEN_SHARED_CELL_WEIGHTS_CHANGED")

    def start_observation(self, cue):
        self._check_frozen()
        if self.cue is not None or self.first is not None:
            raise ValueError("PREVIOUS_PUBLIC_EPISODE_NOT_FINALIZED")
        if type(cue) is not str or cue not in PUBLIC_CUES:
            raise ValueError("INVALID_FIRST_PUBLIC_CUE")
        self.cue = cue

    def accept_first(self, actual_first, next_observation="Nothing", reward=0):
        self._check_frozen()
        if self.cue is None or self.first is not None:
            raise ValueError("FIRST_PUBLIC_OBSERVATION_REQUIRED")
        if type(actual_first) is not str or actual_first not in ACTIONS:
            raise ValueError("INVALID_ACTUAL_FIRST_ACTION")
        if type(next_observation) is not str or next_observation != "Nothing":
            raise ValueError("FIRST_STEP_EXPECTED_PUBLIC_NOTHING")
        if type(reward) is not int or reward != 0:
            raise ValueError("FIRST_PUBLIC_REWARD_MUST_BE_ZERO")
        self.first = actual_first
        self.transitions += 1
        self.forward_input_messages += SOURCE_SIGNAL_PER_PASS

    def _features(self):
        self._check_frozen()
        if self.cue is None or self.first is None:
            raise ValueError("NO_ACTUAL_FIRST_PUBLIC_EVENT")
        return _site_features(self.cue, self.first)

    def _coefficients(self, action):
        """Reverse of 4-hop ring scalar averaging from actual reward site."""
        if type(action) is not str or action not in ACTIONS:
            raise ValueError("INVALID_SELECTED_SECOND_ACTION")
        selected = ACTIONS.index(action)
        origin = ACTION_SITES[selected]
        seed = [0.0] * CELLS
        seed[origin] = 1.0
        credit, message_count = _mix_scalars(seed)
        if message_count != EDGE_SIGNAL_PER_PASS:
            raise ValueError("REVERSE_NEIGHBOR_HOP_DRIFT")
        if self.mode == "action_partition":
            mask = [1.0 if i % len(ACTIONS) == selected else 0.0
                    for i in range(CELLS)]
            normalization = sum(mask[i] * credit[i] for i in range(CELLS))
            if normalization <= 0.0:
                raise ValueError("EMPTY_ACTION_PARTITION")
            return [
                credit[i] * mask[i] / normalization for i in range(CELLS)
            ]
        return credit

    def score(self, action):
        features = self._features()
        coeffs = self._coefficients(action)
        selected = ACTIONS.index(action)
        # Local cell emits one scalar. In the partition control an unowned
        # cell emits ZERO *before* any edge message is sent.
        values = [
            sum(a * b for a, b in zip(self.cell_weights[i], features[i])) *
            (1.0 if self.mode == "shared" or i % 3 == selected else 0.0)
            for i in range(CELLS)
        ]
        delivered, messages = _mix_scalars(values)
        self.forward_output_messages += messages
        if self.mode == "action_partition":
            seed_mask = [
                1.0 if i % 3 == selected else 0.0 for i in range(CELLS)]
            denominators, extra = _mix_scalars(seed_mask)
            self.forward_output_messages += extra
            if denominators[ACTION_SITES[selected]] <= 0.0:
                raise ValueError("ZERO_LOCAL_PARTITION_CONTRIBUTION")
            context_value = (delivered[ACTION_SITES[selected]] /
                             denominators[ACTION_SITES[selected]])
        else:
            context_value = delivered[ACTION_SITES[selected]]
        # A second independent exact algebraic reconstruction of the same
        # *neighbor-carried* result; reject any wrong edge/outgoing path.
        expected = sum(coeffs[i] * sum(
            a*b for a,b in zip(self.cell_weights[i],features[i]))
            for i in range(CELLS))
        if abs(context_value - expected) > 1e-9:
            raise ValueError("NEIGHBOR_SCALAR_ROUTE_MISMATCH")
        return context_value + self.action_biases[selected]

    def scores(self):
        return [self.score(action) for action in ACTIONS]

    def choose(self):
        values = self.scores()
        return ACTIONS[max(range(len(ACTIONS)), key=lambda j: values[j])]

    def accept_second(self, selected, public_reward, *,
                      learning=True, terminal=True):
        self._check_frozen()
        if type(selected) is not str or selected not in ACTIONS:
            raise ValueError("INVALID_SELECTED_SECOND_ACTION")
        if not _valid_finite(public_reward, *REWARD_LIMITS):
            raise ValueError("INVALID_PUBLIC_REWARD")
        if type(learning) is not bool or type(terminal) is not bool or not terminal:
            raise ValueError("SECOND_PUBLIC_STEP_MUST_TERMINATE")
        if self.cue is None or self.first is None:
            raise ValueError("SECOND_ACTION_BEFORE_ACTUAL_FIRST")
        if learning and self.frozen_sha is not None:
            raise ValueError("TRAINING_FORBIDDEN_IN_FROZEN_EVALUATION")
        features = self._features()
        coeffs = self._coefficients(selected)
        predicted = self.score(selected)
        if learning:
            err = max(-13.0, min(13.0, float(public_reward) - predicted))
            normalizer = 2.0 + sum(
                coeffs[cell]**2 * sum(v*v for v in features[cell])
                for cell in range(CELLS)
            )
            step = LEARNING_RATE * err / normalizer
            selected_idx = ACTIONS.index(selected)
            self.action_biases[selected_idx] = max(
                -WEIGHT_BOUND, min(WEIGHT_BOUND,
                                  self.action_biases[selected_idx] + step))
            for cell in range(CELLS):
                credit = coeffs[cell]
                if credit == 0.0:
                    continue
                current = self.cell_weights[cell]
                self.cell_weights[cell] = [
                    max(-WEIGHT_BOUND, min(WEIGHT_BOUND,
                        current[i] + step * credit * features[cell][i]))
                    for i in range(HEAD_FEATURES)
                ]
            self.reverse_credit_messages += EDGE_SIGNAL_PER_PASS
            self.updates += 1
        self.cue = None
        self.first = None
        self.transitions += 1
        self._check_frozen()

    def start_frozen_evaluation(self):
        self._check_frozen()
        if self.cue is not None or self.first is not None:
            raise ValueError("PUBLIC_EPISODE_IN_PROGRESS")
        self.frozen_sha = self.parameters_sha256()

    def checkpoint(self):
        self._check_frozen()
        body = {
            "schema": SCHEMA, "native_ids": self.native_ids,
            "mode": self.mode, "cell_weights": self.cell_weights,
            "action_biases": self.action_biases,
            "cue": self.cue, "first": self.first,
            "transitions": self.transitions, "updates": self.updates,
            "forward_input_messages": self.forward_input_messages,
            "forward_output_messages": self.forward_output_messages,
            "reverse_credit_messages": self.reverse_credit_messages,
            "frozen_sha": self.frozen_sha,
        }
        payload = canonical(body)
        if len(payload) > MAX_CHECKPOINT_BYTES:
            raise ValueError("SHARED_RING_CHECKPOINT_OVER_BUDGET")
        return canonical({
            "body": body, "sha256": hashlib.sha256(payload).hexdigest()})

    @classmethod
    def restore(cls, raw):
        try:
            if type(raw) is not bytes or not 0 < len(raw) <= MAX_CHECKPOINT_BYTES:
                raise ValueError("UNTRUSTED_V22_CHECKPOINT_SIZE")
            envelope = json.loads(raw)
            if type(envelope) is not dict or set(envelope) != {"body", "sha256"}:
                raise ValueError("UNTRUSTED_V22_CHECKPOINT_ENVELOPE")
            b = envelope["body"]
            if (type(b) is not dict or
                hashlib.sha256(canonical(b)).hexdigest() != envelope["sha256"]):
                raise ValueError("UNTRUSTED_V22_CHECKPOINT_DIGEST")
            required = {
                "schema", "native_ids", "mode", "cell_weights", "action_biases",
                "cue", "first", "transitions", "updates",
                "forward_input_messages", "forward_output_messages",
                "reverse_credit_messages", "frozen_sha",
            }
            if set(b) != required or b["schema"] != SCHEMA:
                raise ValueError("UNTRUSTED_V22_CHECKPOINT_SCHEMA")
            if type(b["mode"]) is not str or b["mode"] not in MODES:
                raise ValueError("UNTRUSTED_V22_MODE")
            native_ids = fixed_original_identity()
            if b["native_ids"] != native_ids:
                raise ValueError("UNTRUSTED_ORIGINAL_NATIVE_SOURCE_ID")
            if (type(b["cell_weights"]) is not list or
                len(b["cell_weights"]) != CELLS or
                any(type(row) is not list or len(row) != HEAD_FEATURES or
                    any(not _valid_finite(v, -WEIGHT_BOUND, WEIGHT_BOUND)
                        for v in row) for row in b["cell_weights"])):
                raise ValueError("UNTRUSTED_V22_CELL_WEIGHTS")
            if (type(b["action_biases"]) is not list or
                len(b["action_biases"]) != len(ACTIONS) or
                any(not _valid_finite(v,-WEIGHT_BOUND,WEIGHT_BOUND)
                    for v in b["action_biases"])):
                raise ValueError("UNTRUSTED_V22_ACTION_BIASES")
            cue, first = b["cue"], b["first"]
            if cue is not None and (type(cue) is not str or cue not in PUBLIC_CUES):
                raise ValueError("UNTRUSTED_PUBLIC_CUE")
            if first is not None and (type(first) is not str or first not in ACTIONS):
                raise ValueError("UNTRUSTED_FIRST_ACTION")
            if cue is None and first is not None:
                raise ValueError("UNTRUSTED_ORPHAN_PUBLIC_FIRST")
            for key in ("transitions", "updates", "forward_input_messages",
                        "forward_output_messages", "reverse_credit_messages"):
                if type(b[key]) is not int or not 0 <= b[key] <= 100000000:
                    raise ValueError("UNTRUSTED_V22_COUNTER")
            if b["forward_input_messages"] % SOURCE_SIGNAL_PER_PASS:
                raise ValueError("UNTRUSTED_V22_INPUT_PROVENANCE")
            if b["forward_output_messages"] % EDGE_SIGNAL_PER_PASS:
                raise ValueError("UNTRUSTED_V22_FORWARD_PROVENANCE")
            if b["reverse_credit_messages"] != b["updates"] * EDGE_SIGNAL_PER_PASS:
                raise ValueError("UNTRUSTED_V22_REVERSE_PROVENANCE")
            obj = cls.__new__(cls)
            obj.native_ids = native_ids
            obj.mode = b["mode"]
            obj.cell_weights = [
                [float(v) for v in row] for row in b["cell_weights"]]
            obj.action_biases = [float(v) for v in b["action_biases"]]
            obj.cue, obj.first = cue, first
            for key in ("transitions", "updates", "forward_input_messages",
                        "forward_output_messages", "reverse_credit_messages"):
                setattr(obj, key, b[key])
            obj.frozen_sha = b["frozen_sha"]
            if obj.frozen_sha is not None and (
                type(obj.frozen_sha) is not str or len(obj.frozen_sha) != 64 or
                obj.frozen_sha != obj.parameters_sha256()):
                raise ValueError("UNTRUSTED_V22_FROZEN_IDENTITY")
            if obj.checkpoint() != raw:
                raise ValueError("UNTRUSTED_V22_CHECKPOINT_REPLAY")
            return obj
        except (KeyError, ValueError, TypeError, OverflowError,
                AttributeError) as exc:
            raise ValueError("UNTRUSTED_V22_CHECKPOINT") from exc
