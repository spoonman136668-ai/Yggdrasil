"""DG1-HC05: bounded causal-program uncertainty and two-step intervention choice.

No tokens, gradient, hidden physics, oracle, or model calls. All beliefs are
eliminated by *actual* public before/action/after observations. This is a
fixed six-hypothesis, four-action mechanistic source-only DEV control.
"""
from __future__ import annotations

from fractions import Fraction
import hashlib
import json

SCHEMA = "yggdrasil.dg1-hc05.causal-interventions.dev.v1"
ACTIONS = 4
STATES = 16
HYPOTHESES = 6
FULL_MASK = (1 << HYPOTHESES) - 1
MAX_CHECKPOINT_BYTES = 1024
LOOKAHEAD_DISCOUNT = Fraction(9, 10)


def checked_state(s):
    if type(s) is not int or not 0 <= s < STATES:
        raise ValueError("HC05_INVALID_PUBLIC_STATE")
    return s


def checked_action(a):
    if type(a) is not int or not 0 <= a < ACTIONS:
        raise ValueError("HC05_INVALID_PUBLIC_ACTION")
    return a


def local_effect(state, action, hypothesis):
    checked_state(state)
    checked_action(action)
    if type(hypothesis) is not int or not 0 <= hypothesis < HYPOTHESES:
        raise ValueError("HC05_INVALID_CAUSAL_HYPOTHESIS")
    left = (state >> ((action - 1) % 4)) & 1
    own = (state >> action) & 1
    right = (state >> ((action + 1) % 4)) & 1
    family = hypothesis // 2
    sign = hypothesis % 2
    if family == 0:
        base = left ^ right
    elif family == 1:
        base = left ^ right ^ own
    else:
        base = left & right
    return base ^ sign


def filtered(mask, state, action, effect):
    """Return surviving hypotheses; does not add a new hypothesis."""
    return sum(
        1 << h for h in range(HYPOTHESES)
        if mask & (1 << h) and local_effect(state, action, h) == effect
    )


def outcomes(mask, state, action):
    """Counts of predicted 0/1 effects under uniform surviving hypotheses."""
    counts = [0, 0]
    for h in range(HYPOTHESES):
        if mask & (1 << h):
            counts[local_effect(state, action, h)] += 1
    return tuple(counts)


def gini(mask, state, action):
    zero, one = outcomes(mask, state, action)
    n = zero + one
    return Fraction(2 * zero * one, n * n) if n else Fraction(0)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("ascii")


class CausalProbeCells:
    __slots__ = ("masks", "observations", "contradictions")

    def __init__(self):
        self.masks = [FULL_MASK] * ACTIONS
        self.observations = 0
        self.contradictions = 0

    @property
    def logical_mask_bits(self):
        return ACTIONS * HYPOTHESES

    def observe(self, before, action, after):
        checked_state(before)
        checked_action(action)
        checked_state(after)
        if after not in (before, before ^ (1 << action)):
            raise ValueError("HC05_NONLOCAL_PUBLIC_OUTCOME")
        effect = int(before != after)
        new_mask = filtered(self.masks[action], before, action, effect)
        if not new_mask and self.masks[action]:
            self.contradictions += 1
        self.masks[action] = new_mask
        self.observations += 1

    def predict(self, before, action):
        checked_state(before)
        checked_action(action)
        zero, one = outcomes(self.masks[action], before, action)
        if zero == one == 0 or zero and one:
            return None
        return before ^ ((1 if one else 0) << action)

    def choose_greedy(self, state):
        checked_state(state)
        scores = [gini(mask, state, a)
                  for a, mask in enumerate(self.masks)]
        return max(range(ACTIONS), key=lambda a: (scores[a], -a))

    def choose_lookahead(self, state):
        """Expectimax information value over real-first / hypothetical-second action.

        A future action is scored solely against the belief masks. It is
        never executed, and no hidden physics is queried at planning time.
        """
        checked_state(state)
        scores = []
        for action, mask in enumerate(self.masks):
            zero, one = outcomes(mask, state, action)
            total = zero + one
            score = gini(mask, state, action)
            if total:
                expected = Fraction(0)
                for effect, support in ((0, zero), (1, one)):
                    if not support:
                        continue
                    after = state ^ (effect << action)
                    posterior = filtered(mask, state, action, effect)
                    future_masks = self.masks[:]
                    future_masks[action] = posterior
                    best_followup = max(
                        gini(future_masks[a], after, a) for a in range(ACTIONS)
                    )
                    expected += Fraction(support, total) * best_followup
                score += LOOKAHEAD_DISCOUNT * expected
            scores.append(score)
        return max(range(ACTIONS), key=lambda a: (scores[a], -a))

    def snapshot(self):
        payload = {
            "schema": SCHEMA,
            "masks": self.masks,
            "observations": self.observations,
            "contradictions": self.contradictions,
        }
        raw = canonical(payload)
        packet = canonical({
            "payload": payload,
            "sha256": hashlib.sha256(raw).hexdigest()
        })
        if len(packet) > MAX_CHECKPOINT_BYTES:
            raise ValueError("HC05_SNAPSHOT_BUDGET_EXCEEDED")
        return packet

    @classmethod
    def restore(cls, snapshot):
        if type(snapshot) is not bytes or not 0 < len(snapshot) <= MAX_CHECKPOINT_BYTES:
            raise ValueError("HC05_CHECKPOINT_REJECTED")
        try:
            packet = json.loads(snapshot)
            if type(packet) is not dict or set(packet) != {"payload", "sha256"}:
                raise ValueError("HC05_CHECKPOINT_ENVELOPE")
            payload = packet["payload"]
            fields = {"schema", "masks", "observations", "contradictions"}
            if type(payload) is not dict or set(payload) != fields or payload["schema"] != SCHEMA:
                raise ValueError("HC05_CHECKPOINT_SCHEMA")
            if hashlib.sha256(canonical(payload)).hexdigest() != packet["sha256"]:
                raise ValueError("HC05_CHECKPOINT_HASH")
            masks = payload["masks"]
            if type(masks) is not list or len(masks) != ACTIONS or any(
                type(mask) is not int or not 0 <= mask <= FULL_MASK for mask in masks
            ):
                raise ValueError("HC05_CHECKPOINT_MASKS")
            n = payload["observations"]
            c = payload["contradictions"]
            if type(n) is not int or type(c) is not int or not 0 <= c <= n <= 100000:
                raise ValueError("HC05_CHECKPOINT_COUNTERS")
            obj = cls()
            obj.masks = masks[:]
            obj.observations = n
            obj.contradictions = c
            if obj.snapshot() != snapshot:
                raise ValueError("HC05_CHECKPOINT_CANONICAL")
            return obj
        except (UnicodeError, TypeError, ValueError, KeyError, OverflowError) as error:
            raise ValueError("HC05_CHECKPOINT_REJECTED") from error


class ConventionalEquivalentPlanner(CausalProbeCells):
    """Algorithmically identical conventional version space, not a novelty claim."""
    pass
