"""V17 bounded neighbor-carried public-input learner, development only.

Separate opt-in ring-local diagnostic; does NOT fit the original native genome,
learn message-routing rules, or prove autonomous distributed cognition.
No global (cue, first, second) key, hidden world field or reward oracle.
"""
import hashlib
import json
import math

from .itd02_local_ring_memory_dev import (
    ACTIONS, ACTION_SITES, CELLS, OBSERVATIONS, OBS_SITES,
)
from .itd02_native_task_bridge_dev import RING, NativeTaskRingBridgeDev

SCHEMA = "ygg.itd02.v17.neighbor_carried_heads.source_only.v1"
PUBLIC_CUES = ("LRV", "MRV", "docked_LRV", "docked_MRV")
CHANNELS = len(PUBLIC_CUES) + len(ACTIONS)
HOPS = 4
RATE = 0.27
MAX_BYTES = 8192
BOUNDS = (-3.0, 10.0)
WEIGHT_LIMIT = 16.0


def canonical(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def fixed_original_identity():
    """Identity of the unchanged native objects (not learner training)."""
    frozen = NativeTaskRingBridgeDev()
    return frozen.model_identities()


def site_pulses(cue, actual_first):
    """Inject each event independently at its original physical input site."""
    if type(cue) is not str or cue not in PUBLIC_CUES:
        raise ValueError("INVALID_FIRST_PUBLIC_CUE")
    if type(actual_first) is not str or actual_first not in ACTIONS:
        raise ValueError("INVALID_ACTUAL_FIRST_ACTION")
    pulse = [[0.0] * CHANNELS for _ in range(CELLS)]
    cue_site = OBS_SITES[OBSERVATIONS.index(cue)]
    first_site = ACTION_SITES[ACTIONS.index(actual_first)]
    pulse[cue_site][PUBLIC_CUES.index(cue)] = 1.0
    pulse[first_site][len(PUBLIC_CUES) + ACTIONS.index(actual_first)] = 1.0
    return pulse


def neighbor_transport(pulses, hops=HOPS):
    """Synchronous *edge-only* propagation; each hop reads own/left/right."""
    if type(hops) is not int or not 0 <= hops <= HOPS:
        raise ValueError("INVALID_NEIGHBOR_HOP_BUDGET")
    if (type(pulses) is not list or len(pulses) != CELLS or
            any(type(row) is not list or len(row) != CHANNELS or
                any(type(x) not in (int, float) or
                    not math.isfinite(x) or not 0.0 <= x <= 1.0
                    for x in row) for row in pulses)):
        raise ValueError("INVALID_SITE_LOCAL_PULSES")
    state = [list(row) for row in pulses]
    for _ in range(hops):
        prior = state
        state = [[max(prior[site][channel],
                      prior[RING[site][0]][channel],
                      prior[RING[site][1]][channel])
                  for channel in range(CHANNELS)] for site in range(CELLS)]
    # Two real original edges per cell, one bounded scalar per channel/hop.
    return state, CELLS * 2 * CHANNELS * hops


class NeighborCarriedPublicLearnerDev:
    """Exactly 3 cell-local plastic heads, fed only by ring-neighbor messages."""

    def __init__(self):
        if CELLS != 8 or ACTION_SITES != (0, 2, 5):
            raise ValueError("ORIGINAL_NATIVE_EIGHT_CELL_BOUNDARY_DRIFT")
        self.native_ids = fixed_original_identity()
        self.weights = [[0.0] * (CHANNELS + 1) for _ in ACTION_SITES]
        self.cue = None
        self.first = None
        self.delivered = None
        self.transitions = 0
        self.learned_updates = 0
        self.edge_scalar_messages = 0
        self.frozen_sha = None

    def parameters_sha256(self):
        return hashlib.sha256(canonical(self.weights)).hexdigest()

    def _check_frozen(self):
        if self.frozen_sha is not None and self.parameters_sha256() != self.frozen_sha:
            raise ValueError("FROZEN_LOCAL_HEAD_PARAMETER_DRIFT")

    def start_observation(self, cue):
        self._check_frozen()
        if self.cue is not None or self.first is not None:
            raise ValueError("PREVIOUS_PUBLIC_EPISODE_PENDING")
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
            raise ValueError("FIRST_STEP_MUST_CONTINUE_TO_NOTHING")
        if type(reward) is not int or reward != 0:
            raise ValueError("UNSUPPORTED_FIRST_STEP_PUBLIC_REWARD")
        delivered, messages = neighbor_transport(site_pulses(self.cue, actual_first))
        self.first = actual_first
        self.delivered = delivered
        self.transitions += 1
        self.edge_scalar_messages += messages

    def _features(self, second, *, no_messages=False):
        self._check_frozen()
        if self.first is None or self.cue is None or self.delivered is None:
            raise ValueError("SECOND_ACTION_BEFORE_REAL_FIRST_EVENT")
        if type(second) is not str or second not in ACTIONS:
            raise ValueError("INVALID_SECOND_ACTION")
        site = ACTION_SITES[ACTIONS.index(second)]
        # No context-tuple index. A head sees only its own delivered message row.
        local = (site_pulses(self.cue, self.first)[site] if no_messages
                 else self.delivered[site])
        return [1.0] + list(local)

    def local_scores(self):
        return [sum(w * x for w, x in zip(self.weights[i], self._features(action)))
                for i, action in enumerate(ACTIONS)]

    def diagnostic_zero_message_scores(self):
        """Causal ablation using SAME trained weights but no edge transport."""
        return [sum(w * x for w, x in zip(self.weights[i],
                                         self._features(action, no_messages=True)))
                for i, action in enumerate(ACTIONS)]

    def choose(self):
        scores = self.local_scores()
        return ACTIONS[max(range(len(ACTIONS)), key=lambda i: scores[i])]

    def accept_second(self, actually_selected, public_reward, *,
                      learning=True, terminal=True):
        self._check_frozen()
        if type(actually_selected) is not str or actually_selected not in ACTIONS:
            raise ValueError("INVALID_ACTUAL_SECOND_ACTION")
        if (type(public_reward) not in (int, float) or
                not math.isfinite(public_reward) or
                not BOUNDS[0] <= public_reward <= BOUNDS[1]):
            raise ValueError("INVALID_PUBLIC_REWARD")
        if type(learning) is not bool or type(terminal) is not bool or not terminal:
            raise ValueError("SECOND_PUBLIC_STEP_MUST_TERMINATE")
        features = self._features(actually_selected)
        if learning and self.frozen_sha is not None:
            raise ValueError("FITTING_FORBIDDEN_DURING_FROZEN_EVALUATION")
        if learning:
            idx = ACTIONS.index(actually_selected)
            row = self.weights[idx]
            pred = sum(w * x for w, x in zip(row, features))
            error = max(-13.0, min(13.0, float(public_reward) - pred))
            # All weights are owned by THIS action head, not a global table.
            updated = [max(-WEIGHT_LIMIT, min(WEIGHT_LIMIT,
                           w + RATE * error * x / 3.0))
                       for w, x in zip(row, features)]
            self.weights[idx] = updated
            self.learned_updates += 1
        self.cue = None
        self.first = None
        self.delivered = None
        self.transitions += 1
        self._check_frozen()

    def start_frozen_evaluation(self):
        self._check_frozen()
        if self.cue is not None or self.first is not None:
            raise ValueError("PENDING_PUBLIC_EPISODE")
        self.frozen_sha = self.parameters_sha256()

    def checkpoint(self):
        self._check_frozen()
        body = {
            "schema": SCHEMA, "native_ids": self.native_ids,
            "weights": self.weights, "cue": self.cue, "first": self.first,
            "delivered": self.delivered, "transitions": self.transitions,
            "learned_updates": self.learned_updates,
            "edge_scalar_messages": self.edge_scalar_messages,
            "frozen_sha": self.frozen_sha,
        }
        raw = canonical(body)
        if len(raw) > MAX_BYTES:
            raise ValueError("CHECKPOINT_BUDGET_EXCEEDED")
        return canonical({"body": body, "sha256": hashlib.sha256(raw).hexdigest()})

    @classmethod
    def restore(cls, data):
        try:
            if type(data) is not bytes or not 0 < len(data) <= MAX_BYTES:
                raise ValueError("BAD_CHECKPOINT_SIZE")
            envelope = json.loads(data)
            if type(envelope) is not dict or set(envelope) != {"body", "sha256"}:
                raise ValueError("BAD_CHECKPOINT_ENVELOPE")
            body = envelope["body"]
            if hashlib.sha256(canonical(body)).hexdigest() != envelope["sha256"]:
                raise ValueError("BAD_CHECKPOINT_DIGEST")
            required = {"schema", "native_ids", "weights", "cue", "first",
                        "delivered", "transitions", "learned_updates",
                        "edge_scalar_messages", "frozen_sha"}
            if type(body) is not dict or set(body) != required or body["schema"] != SCHEMA:
                raise ValueError("BAD_CHECKPOINT_SCHEMA")
            original = fixed_original_identity()
            if body["native_ids"] != original:
                raise ValueError("ORIGINAL_NATIVE_IDENTITY_MISMATCH")
            weights = body["weights"]
            if (type(weights) is not list or len(weights) != len(ACTION_SITES) or
                    any(type(row) is not list or len(row) != CHANNELS + 1 or
                        any(type(x) not in (int, float) or not math.isfinite(x) or
                            abs(x) > WEIGHT_LIMIT for x in row) for row in weights)):
                raise ValueError("INVALID_CELL_LOCAL_PARAMETERS")
            cue, first, delivered = body["cue"], body["first"], body["delivered"]
            if cue is None:
                if first is not None or delivered is not None:
                    raise ValueError("ORPHANED_PUBLIC_HISTORY")
            elif type(cue) is not str or cue not in PUBLIC_CUES:
                raise ValueError("INVALID_PUBLIC_CUE_STATE")
            elif first is None:
                if delivered is not None:
                    raise ValueError("ORPHANED_DELIVERY")
            else:
                if type(first) is not str or first not in ACTIONS:
                    raise ValueError("INVALID_PUBLIC_FIRST_STATE")
                expected, _ = neighbor_transport(site_pulses(cue, first))
                if delivered != expected:
                    raise ValueError("UNTRUSTED_EDGE_DELIVERY")
            for field in ("transitions", "learned_updates", "edge_scalar_messages"):
                if type(body[field]) is not int or not 0 <= body[field] <= 100000000:
                    raise ValueError("INVALID_COUNTER")
            if body["edge_scalar_messages"] % (CELLS * 2 * CHANNELS * HOPS):
                raise ValueError("INVALID_MESSAGE_PROVENANCE")
            obj = cls.__new__(cls)
            obj.native_ids = original
            obj.weights = [[float(x) for x in row] for row in weights]
            obj.cue, obj.first, obj.delivered = cue, first, delivered
            obj.transitions = body["transitions"]
            obj.learned_updates = body["learned_updates"]
            obj.edge_scalar_messages = body["edge_scalar_messages"]
            obj.frozen_sha = body["frozen_sha"]
            if obj.frozen_sha is not None:
                if (type(obj.frozen_sha) is not str or len(obj.frozen_sha) != 64
                        or obj.frozen_sha != obj.parameters_sha256()):
                    raise ValueError("FROZEN_PARAMETER_IDENTITY_MISMATCH")
            return obj
        except (TypeError, ValueError, KeyError, OverflowError, AttributeError) as exc:
            raise ValueError("UNTRUSTED_V17_CHECKPOINT") from exc
