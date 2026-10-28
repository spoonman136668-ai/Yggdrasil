"""V18 source-public cell-receiving-gain candidate, engineering-only.

Eight original ring cells and seven named PUBLIC input tags. Reward-head
weights and intermediate receiving gains fit provided public reward feedback.
This is not the original native model, autonomous learned routing, or science.
"""
import hashlib
import json
import math

from .itd02_v17_neighbor_carried_learner_dev import (
    ACTIONS, ACTION_SITES, CELLS, CHANNELS, HOPS, PUBLIC_CUES,
    RING, canonical, fixed_original_identity, site_pulses,
)

SCHEMA = "ygg.itd02.v18.intermediate_gain.source_only.v1"
MAX_CHECKPOINT_BYTES = 8192
INITIAL_GAIN = 0.92
GAIN_LIMITS = (0.25, 1.50)
HEAD_LIMIT = 16.0
REWARD_LIMITS = (-5.0, 10.0)
HEAD_RATE = 0.6
GAIN_RATE = 0.015
HEAD_FEATURES = 1 + CHANNELS + 4 * 3
EDGES_PER_PASS = CELLS * 2 * CHANNELS * HOPS


def _valid_finite(x, low, high):
    return type(x) in (int, float) and math.isfinite(x) and low <= x <= high


def forward_local(pulse, gains, *, hops=HOPS):
    """Only reads previous hop's own/left/right sites, never global tuple."""
    if type(hops) is not int or not 0 <= hops <= HOPS:
        raise ValueError("INVALID_LOCAL_HOPS")
    if (type(pulse) is not list or len(pulse) != CELLS or
            any(type(row) is not list or len(row) != CHANNELS or
                any(not _valid_finite(x, 0.0, 1.0) for x in row) for row in pulse)):
        raise ValueError("INVALID_LOCAL_INPUT")
    if (type(gains) is not list or len(gains) != CELLS or
            any(type(row) is not list or len(row) != CHANNELS or
                any(not _valid_finite(x, *GAIN_LIMITS) for x in row) for row in gains)):
        raise ValueError("INVALID_RECEIVER_GAINS")
    state = [list(row) for row in pulse]
    eligible = [[0.0] * CHANNELS for _ in range(CELLS)]
    for _ in range(hops):
        previous = state
        next_state = []
        for cell in range(CELLS):
            left, right = RING[cell]
            row = []
            for channel in range(CHANNELS):
                incoming = max(previous[left][channel], previous[right][channel])
                eligible[cell][channel] += incoming / HOPS
                row.append(min(2.0, max(previous[cell][channel],
                                        gains[cell][channel] * incoming)))
            next_state.append(row)
        state = next_state
    return state, eligible, EDGES_PER_PASS * hops // HOPS


def reverse_local_reward_credit(selected_site):
    """Scalar reward-error reach through original neighbor links only."""
    if type(selected_site) is not int or selected_site not in ACTION_SITES:
        raise ValueError("INVALID_CREDIT_ORIGIN")
    credit = [0.0] * CELLS
    credit[selected_site] = 1.0
    for _ in range(HOPS):
        credit = [max(credit[cell], credit[RING[cell][0]],
                      credit[RING[cell][1]]) for cell in range(CELLS)]
    return credit, CELLS * 2 * HOPS


class IntermediatePlasticRingDev:
    def __init__(self, *, plastic_intermediate=True):
        if type(plastic_intermediate) is not bool:
            raise ValueError("INVALID_INTERMEDIATE_PLASTICITY_FLAG")
        self.native_ids = fixed_original_identity()
        self.gains = [[INITIAL_GAIN] * CHANNELS for _ in range(CELLS)]
        self.heads = [[0.0] * HEAD_FEATURES for _ in ACTION_SITES]
        self.plastic_intermediate = plastic_intermediate
        self.cue = None
        self.first = None
        self.delivered = None
        self.eligible = None
        self.transitions = 0
        self.learned_updates = 0
        self.forward_messages = 0
        self.credit_messages = 0
        self.frozen_sha = None

    def parameters_sha256(self):
        return hashlib.sha256(canonical({
            "gains": self.gains, "heads": self.heads,
            "plastic_intermediate": self.plastic_intermediate,
        })).hexdigest()

    def _check_frozen(self):
        if self.frozen_sha is not None and self.parameters_sha256() != self.frozen_sha:
            raise ValueError("FROZEN_V18_WEIGHTS_CHANGED")

    def start_observation(self, cue):
        self._check_frozen()
        if self.cue is not None or self.first is not None:
            raise ValueError("PUBLIC_EPISODE_PENDING")
        if type(cue) is not str or cue not in PUBLIC_CUES:
            raise ValueError("INVALID_FIRST_PUBLIC_CUE")
        self.cue = cue

    def accept_first(self, actual_first, next_observation="Nothing", reward=0):
        self._check_frozen()
        if self.cue is None or self.first is not None:
            raise ValueError("FIRST_PUBLIC_OBSERVATION_REQUIRED")
        if type(actual_first) is not str or actual_first not in ACTIONS:
            raise ValueError("INVALID_ACTUAL_FIRST_ACTION")
        if next_observation != "Nothing" or type(next_observation) is not str:
            raise ValueError("EXPECTED_SECOND_PUBLIC_NOTHING")
        if type(reward) is not int or reward != 0:
            raise ValueError("FIRST_PUBLIC_REWARD_MUST_BE_ZERO")
        pulse = site_pulses(self.cue, actual_first)
        delivered, eligible, messages = forward_local(pulse, self.gains)
        self.first = actual_first
        self.delivered = delivered
        self.eligible = eligible
        self.forward_messages += messages
        self.transitions += 1

    def _features(self, action, *, clamped_initial_gains=False):
        self._check_frozen()
        if self.cue is None or self.first is None or self.delivered is None:
            raise ValueError("MISSING_REAL_FIRST_PUBLIC_EVENT")
        if type(action) is not str or action not in ACTIONS:
            raise ValueError("INVALID_ACTUAL_SECOND_ACTION")
        site = ACTION_SITES[ACTIONS.index(action)]
        if clamped_initial_gains:
            gains = [[INITIAL_GAIN] * CHANNELS for _ in range(CELLS)]
            delivered, _, _ = forward_local(
                site_pulses(self.cue, self.first), gains)
            channel = delivered[site]
        else:
            channel = self.delivered[site]
        return [1.0] + list(channel) + [
            channel[cue] * channel[4 + first]
            for cue in range(4) for first in range(3)
        ]

    def scores(self, *, clamped_initial_gains=False):
        return [
            sum(w * x for w, x in zip(self.heads[i],
                self._features(action, clamped_initial_gains=clamped_initial_gains)))
            for i, action in enumerate(ACTIONS)
        ]

    def accept_second(self, selected, public_reward, *, learning=True, terminal=True):
        self._check_frozen()
        if type(selected) is not str or selected not in ACTIONS:
            raise ValueError("INVALID_SELECTED_SECOND_ACTION")
        if not _valid_finite(public_reward, *REWARD_LIMITS):
            raise ValueError("INVALID_PUBLIC_REWARD")
        if type(learning) is not bool or type(terminal) is not bool or not terminal:
            raise ValueError("SECOND_STEP_MUST_BE_TERMINAL")
        x = self._features(selected)
        if learning and self.frozen_sha is not None:
            raise ValueError("NO_TRAINING_DURING_FROZEN_READOUT")
        if learning:
            site_index = ACTIONS.index(selected)
            site = ACTION_SITES[site_index]
            row = self.heads[site_index]
            prediction = sum(w * v for w, v in zip(row, x))
            error = max(-13.0, min(13.0, float(public_reward) - prediction))
            step = HEAD_RATE * error / (1.0 + sum(v*v for v in x))
            self.heads[site_index] = [
                max(-HEAD_LIMIT, min(HEAD_LIMIT, w + step * v))
                for w, v in zip(row, x)
            ]
            if self.plastic_intermediate:
                credit, messages = reverse_local_reward_credit(site)
                for cell in range(CELLS):
                    eligible_row = self.eligible[cell]
                    denom = 1.0 + sum(eligible_row)
                    for channel in range(CHANNELS):
                        new = self.gains[cell][channel] + (
                            GAIN_RATE * error * credit[cell] *
                            eligible_row[channel] / denom)
                        self.gains[cell][channel] = max(
                            GAIN_LIMITS[0], min(GAIN_LIMITS[1], new))
                self.credit_messages += messages
            self.learned_updates += 1
        self.cue = None
        self.first = None
        self.delivered = None
        self.eligible = None
        self.transitions += 1
        self._check_frozen()

    def start_frozen_evaluation(self):
        self._check_frozen()
        if self.cue is not None or self.first is not None:
            raise ValueError("PUBLIC_EPISODE_PENDING")
        self.frozen_sha = self.parameters_sha256()

    def checkpoint(self):
        self._check_frozen()
        body = {
            "schema": SCHEMA, "native_ids": self.native_ids,
            "gains": self.gains, "heads": self.heads,
            "plastic_intermediate": self.plastic_intermediate,
            "cue": self.cue, "first": self.first, "delivered": self.delivered,
            "eligible": self.eligible, "transitions": self.transitions,
            "learned_updates": self.learned_updates,
            "forward_messages": self.forward_messages,
            "credit_messages": self.credit_messages, "frozen_sha": self.frozen_sha,
        }
        raw = canonical(body)
        if len(raw) > MAX_CHECKPOINT_BYTES:
            raise ValueError("CHECKPOINT_TOO_LARGE")
        return canonical({"body": body, "sha256": hashlib.sha256(raw).hexdigest()})

    @classmethod
    def restore(cls, raw):
        try:
            if type(raw) is not bytes or not 0 < len(raw) <= MAX_CHECKPOINT_BYTES:
                raise ValueError("INVALID_V18_CHECKPOINT_SIZE")
            envelope = json.loads(raw)
            if type(envelope) is not dict or set(envelope) != {"body", "sha256"}:
                raise ValueError("INVALID_V18_CHECKPOINT_ENVELOPE")
            b = envelope["body"]
            if hashlib.sha256(canonical(b)).hexdigest() != envelope["sha256"]:
                raise ValueError("INVALID_V18_CHECKPOINT_DIGEST")
            required = {
                "schema", "native_ids", "gains", "heads",
                "plastic_intermediate", "cue", "first", "delivered", "eligible",
                "transitions", "learned_updates", "forward_messages",
                "credit_messages", "frozen_sha",
            }
            if type(b) is not dict or set(b) != required or b["schema"] != SCHEMA:
                raise ValueError("INVALID_V18_CHECKPOINT_SCHEMA")
            if b["native_ids"] != fixed_original_identity():
                raise ValueError("ORIGINAL_NATIVE_SOURCE_DRIFT")
            if type(b["plastic_intermediate"]) is not bool:
                raise ValueError("INVALID_PLASTICITY_FLAG")
            gains, heads = b["gains"], b["heads"]
            if (type(gains) is not list or len(gains) != CELLS or
                any(type(row) is not list or len(row) != CHANNELS or
                    any(not _valid_finite(x, *GAIN_LIMITS) for x in row)
                    for row in gains)):
                raise ValueError("INVALID_RELAY_GAIN_CHECKPOINT")
            if (type(heads) is not list or len(heads) != len(ACTION_SITES) or
                any(type(row) is not list or len(row) != HEAD_FEATURES or
                    any(not _valid_finite(x, -HEAD_LIMIT, HEAD_LIMIT) for x in row)
                    for row in heads)):
                raise ValueError("INVALID_HEAD_CHECKPOINT")
            for key in ("transitions", "learned_updates", "forward_messages", "credit_messages"):
                if type(b[key]) is not int or not 0 <= b[key] <= 100000000:
                    raise ValueError("INVALID_MESSAGE_COUNTER")
            if b["forward_messages"] % EDGES_PER_PASS:
                raise ValueError("INVALID_FORWARD_MESSAGE_PROVENANCE")
            if b["credit_messages"] % (CELLS * 2 * HOPS):
                raise ValueError("INVALID_CREDIT_MESSAGE_PROVENANCE")
            cue, first = b["cue"], b["first"]
            if cue is None:
                if any(b[key] is not None for key in ("first", "delivered", "eligible")):
                    raise ValueError("ORPHANED_PUBLIC_EPISODE")
            else:
                if type(cue) is not str or cue not in PUBLIC_CUES:
                    raise ValueError("INVALID_FIRST_CUE_STATE")
                if first is None:
                    if b["delivered"] is not None or b["eligible"] is not None:
                        raise ValueError("ORPHANED_DELIVERED_STATE")
                else:
                    if type(first) is not str or first not in ACTIONS:
                        raise ValueError("INVALID_FIRST_ACTION_STATE")
                    expected, elig, _ = forward_local(site_pulses(cue, first), gains)
                    if b["delivered"] != expected or b["eligible"] != elig:
                        raise ValueError("UNTRUSTED_RECEIVED_OR_ELIGIBILITY_STATE")
            obj = cls.__new__(cls)
            obj.native_ids = b["native_ids"]
            obj.gains = [[float(x) for x in row] for row in gains]
            obj.heads = [[float(x) for x in row] for row in heads]
            obj.plastic_intermediate = b["plastic_intermediate"]
            obj.cue, obj.first = cue, first
            obj.delivered, obj.eligible = b["delivered"], b["eligible"]
            obj.transitions, obj.learned_updates = b["transitions"], b["learned_updates"]
            obj.forward_messages, obj.credit_messages = b["forward_messages"], b["credit_messages"]
            obj.frozen_sha = b["frozen_sha"]
            if obj.frozen_sha is not None and (
                type(obj.frozen_sha) is not str or len(obj.frozen_sha) != 64 or
                    obj.frozen_sha != obj.parameters_sha256()):
                raise ValueError("FROZEN_V18_PARAMETER_IDENTITY")
            return obj
        except (ValueError, TypeError, KeyError, OverflowError, AttributeError) as exc:
            raise ValueError("UNTRUSTED_V18_CHECKPOINT") from exc
