"""V20 source-only engineered, neighbor-routed causal eligibility credit.

Distinct opt-in descendant of V18's *engineering candidate*, not the
protected original native learner. The fixed public tags, max relay and
reverse-mode local adjoints are designed (not learned). No original-world
data or target formula is imported here.
"""
import hashlib
import json
import math

from .itd02_v17_neighbor_carried_learner_dev import (
    ACTIONS, ACTION_SITES, CELLS, CHANNELS, HOPS, RING, canonical, site_pulses,
)
from .itd02_v18_intermediate_plasticity_dev import (
    IntermediatePlasticRingDev, SCHEMA as V18_SCHEMA, EDGES_PER_PASS,
    INITIAL_GAIN, GAIN_LIMITS, GAIN_RATE, HEAD_RATE, HEAD_LIMIT,
    MAX_CHECKPOINT_BYTES, REWARD_LIMITS, _valid_finite, forward_local,
)

SCHEMA = "ygg.itd02.v20.locally_routed_responsibility.source_only.v1"
CAUSAL_EPS = 1e-10


class ResponsibilityGatedRingDev(IntermediatePlasticRingDev):
    """Local max-branch adjoints, 56 receiver gains + 60 local head weights."""

    def __init__(self):
        super().__init__(plastic_intermediate=True)

    def local_gain_responsibilities(self, selected):
        """Source-matched forward trace plus reverse traversal of *ring* edges.

        Each adjoint passes only across the exact left/right edge that won
        during the corresponding forward hop; no central tuple or all-pairs
        feedback connection. Same frozen 8-cell physical ring as V18.
        """
        self._check_frozen()
        if self.cue is None or self.first is None or self.delivered is None:
            raise ValueError("PUBLIC_FIRST_ACTION_REQUIRED")
        if type(selected) is not str or selected not in ACTIONS:
            raise ValueError("INVALID_SECOND_SELECTED_ACTION")
        pulses = site_pulses(self.cue, self.first)
        states = [pulses]
        for _ in range(HOPS):
            prior = states[-1]
            following = []
            for cell in range(CELLS):
                left, right = RING[cell]
                following.append([
                    min(2.0, max(prior[cell][tag],
                                  self.gains[cell][tag] *
                                  max(prior[left][tag], prior[right][tag])))
                    for tag in range(CHANNELS)
                ])
            states.append(following)
        if states[-1] != self.delivered:
            raise ValueError("LOCAL_FORWARD_TRACE_DRIFT")
        idx = ACTIONS.index(selected)
        cell = ACTION_SITES[idx]
        final_channels = states[-1][cell]
        head = self.heads[idx]
        # Selected head receives only 7 delivered public channels, not
        # the (cue,first,second) tuple or an evaluator reward table.
        channels = [head[1 + j] for j in range(CHANNELS)]
        for cue_index in range(4):
            for first_index in range(3):
                interaction = head[8 + 3*cue_index + first_index]
                channels[cue_index] += (
                    interaction * final_channels[4 + first_index])
                channels[4 + first_index] += (
                    interaction * final_channels[cue_index])
        downstream = [[0.0] * CHANNELS for _ in range(CELLS)]
        downstream[cell] = channels
        derivatives = [[0.0] * CHANNELS for _ in range(CELLS)]
        for depth in reversed(range(HOPS)):
            prior = states[depth]
            before = [[0.0] * CHANNELS for _ in range(CELLS)]
            for receiver in range(CELLS):
                left, right = RING[receiver]
                for tag in range(CHANNELS):
                    credit = downstream[receiver][tag]
                    if credit == 0.0:
                        continue
                    own = prior[receiver][tag]
                    lval, rval = prior[left][tag], prior[right][tag]
                    neighbor = left if lval >= rval else right
                    signal = max(lval, rval)
                    gained = self.gains[receiver][tag] * signal
                    if gained > own:
                        if gained < 2.0:
                            derivatives[receiver][tag] += credit * signal
                            before[neighbor][tag] += (
                                credit * self.gains[receiver][tag])
                        # At the cap there is zero derivative.
                    else:
                        # Exact ties choose own retention, not a nonexistent edge.
                        before[receiver][tag] += credit
            downstream = before
        if any(not math.isfinite(v) for row in derivatives for v in row):
            raise ValueError("NONFINITE_LOCAL_ELIGIBILITY")
        return derivatives, EDGES_PER_PASS

    def accept_second(self, selected, public_reward, *, learning=True,
                      terminal=True):
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
            idx = ACTIONS.index(selected)
            row = self.heads[idx]
            prediction = sum(w * v for w, v in zip(row, x))
            error = max(-13.0, min(13.0, float(public_reward) - prediction))
            # Crucially calculate responsibility using PRE-UPDATE head
            # weights and PRE-UPDATE receiver gains.
            responsible, messages = self.local_gain_responsibilities(selected)
            step = HEAD_RATE * error / (1.0 + sum(v*v for v in x))
            self.heads[idx] = [
                max(-HEAD_LIMIT, min(HEAD_LIMIT, w + step * v))
                for w, v in zip(row, x)
            ]
            for cell in range(CELLS):
                grad = responsible[cell]
                scale = 1.0 + sum(abs(v) for v in grad)
                for channel in range(CHANNELS):
                    derivative = grad[channel]
                    if abs(derivative) <= CAUSAL_EPS:
                        continue
                    updated = (self.gains[cell][channel] +
                               GAIN_RATE * error * derivative / scale)
                    self.gains[cell][channel] = max(
                        GAIN_LIMITS[0], min(GAIN_LIMITS[1], updated))
            self.credit_messages += messages
            self.learned_updates += 1
        self.cue = None
        self.first = None
        self.delivered = None
        self.eligible = None
        self.transitions += 1
        self._check_frozen()

    def checkpoint(self):
        raw = json.loads(super().checkpoint())
        body = raw["body"]
        if body["schema"] != V18_SCHEMA:
            raise ValueError("V18_CHECKPOINT_SCHEMA_DRIFT")
        body["schema"] = SCHEMA
        serialized = canonical(body)
        if len(serialized) > MAX_CHECKPOINT_BYTES:
            raise ValueError("V20_CHECKPOINT_BUDGET")
        return canonical({
            "body": body, "sha256": hashlib.sha256(serialized).hexdigest()
        })

    @classmethod
    def restore(cls, raw):
        try:
            if type(raw) is not bytes or not 0 < len(raw) <= MAX_CHECKPOINT_BYTES:
                raise ValueError("V20_CHECKPOINT_SIZE")
            packet = json.loads(raw)
            if type(packet) is not dict or set(packet) != {"body", "sha256"}:
                raise ValueError("V20_CHECKPOINT_ENVELOPE")
            body = packet["body"]
            if (type(body) is not dict or body.get("schema") != SCHEMA or
                hashlib.sha256(canonical(body)).hexdigest() != packet["sha256"]):
                raise ValueError("V20_CHECKPOINT_INTEGRITY")
            # Delegate ALL native identity, public history, parameter bounds,
            # receiver state and frozen-readout validation to unchanged V18.
            body["schema"] = V18_SCHEMA
            original = canonical(body)
            parent_envelope = canonical({
                "body": body, "sha256": hashlib.sha256(original).hexdigest(),
            })
            value = IntermediatePlasticRingDev.restore(parent_envelope)
            if not value.plastic_intermediate:
                raise ValueError("V20_REQUIRES_ENABLED_CAUSAL_GAINS")
            value.__class__ = cls
            if value.checkpoint() != raw:
                raise ValueError("V20_CHECKPOINT_ROUNDTRIP")
            return value
        except (ValueError, KeyError, TypeError, OverflowError,
                AttributeError) as exc:
            raise ValueError("UNTRUSTED_V20_CHECKPOINT") from exc
