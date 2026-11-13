"""DG1-HC04: bounded uncertainty-aware causal hypothesis cells (DEV ONLY).

A fixed version space, not an open-ended program synthesizer. All updates come
from public physical before/action/after events; no evaluator imports.
"""
from __future__ import annotations
import hashlib
import json

SCHEMA = "ygg.dg1-hc04.version-space.v1"
ACTIONS = 4
SITES = 4
HYPOTHESES = 4
MAX_BANKS = 2
CHECKPOINT_LIMIT = 2048
FULL_MASK = (1 << HYPOTHESES) - 1


def require_state(state):
    if type(state) is not int or not 0 <= state < 16:
        raise ValueError("HC04_BAD_PUBLIC_STATE")
    return state


def require_action(action):
    if type(action) is not int or not 0 <= action < ACTIONS:
        raise ValueError("HC04_BAD_PUBLIC_ACTION")
    return action


def local_parity(state, action):
    require_state(state)
    require_action(action)
    return ((state >> ((action - 1) % SITES)) & 1) ^ (
        (state >> ((action + 1) % SITES)) & 1)


def hypothesis_effect(state, action, hypothesis):
    if type(hypothesis) is not int or not 0 <= hypothesis < HYPOTHESES:
        raise ValueError("HC04_BAD_HYPOTHESIS")
    own = (state >> action) & 1
    return local_parity(state, action) ^ ((hypothesis >> 1) & own) ^ (hypothesis & 1)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("ascii")


def filter_mask(mask, state, action, observed_effect):
    return sum(
        1 << h for h in range(HYPOTHESES)
        if mask & (1 << h) and hypothesis_effect(state, action, h) == observed_effect
    )


class VersionedCausalCells:
    """Two version-space memory banks with observable ambiguity and abstention."""

    def __init__(self, *, bank_limit=MAX_BANKS, reactivate=True):
        if type(bank_limit) is not int or not 1 <= bank_limit <= MAX_BANKS:
            raise ValueError("HC04_BAD_BANK_LIMIT")
        if type(reactivate) is not bool:
            raise ValueError("HC04_BAD_REACTIVATE")
        self.bank_limit = bank_limit
        self.reactivate = reactivate
        self.banks = [[FULL_MASK] * ACTIONS]
        self.active = 0
        self.plausible = [0]
        self.updates = 0
        self.splits = 0
        self.reactivations = 0
        self.ambiguous_events = 0
        self.unresolved = 0

    def observe(self, before, action, after):
        require_state(before)
        require_action(action)
        require_state(after)
        if after not in (before, before ^ (1 << action)):
            raise ValueError("HC04_NONLOCAL_DELTA")
        effect = int(before != after)
        possibilities = [
            (i, filter_mask(bank[action], before, action, effect))
            for i, bank in enumerate(self.banks)
        ]
        compatible = [(i, mask) for i, mask in possibilities if mask]
        current = next(((i, mask) for i, mask in compatible
                        if i == self.active), None)
        if current is not None:
            # Do not rewrite the inactive bank merely for fitting one event.
            self.banks[self.active][action] = current[1]
            self.plausible = sorted(i for i, _ in compatible)
            if len(self.plausible) > 1:
                self.ambiguous_events += 1
        else:
            previous = next(((i, mask) for i, mask in compatible
                             if i != self.active), None)
            if self.reactivate and previous is not None:
                self.active = previous[0]
                self.banks[self.active][action] = previous[1]
                self.plausible = [self.active]
                self.reactivations += 1
            elif len(self.banks) < self.bank_limit:
                newbank = [FULL_MASK] * ACTIONS
                newbank[action] = filter_mask(FULL_MASK, before, action, effect)
                self.banks.append(newbank)
                self.active = len(self.banks) - 1
                self.plausible = [self.active]
                self.splits += 1
            elif not self.reactivate:
                # A deliberate destructive control; same physical data budget.
                self.banks[self.active] = [FULL_MASK] * ACTIONS
                self.banks[self.active][action] = filter_mask(
                    FULL_MASK, before, action, effect)
                self.plausible = [self.active]
            else:
                # Full capacity and no compatible causal explanation.
                # Fail closed instead of confident extrapolation.
                self.plausible = []
                self.unresolved += 1
                self.updates += 1
                return False
        self.updates += 1
        return True

    def predict(self, before, action):
        require_state(before)
        require_action(action)
        if not self.plausible:
            return None
        effects = {
            hypothesis_effect(before, action, h)
            for bank_idx in self.plausible
            for h in range(HYPOTHESES)
            if self.banks[bank_idx][action] & (1 << h)
        }
        if len(effects) != 1:
            return None
        effect = next(iter(effects))
        return before ^ (effect << action)

    def predict_ungated(self, before, action):
        """Negative control: pick first compatible mechanism, ignore ambiguity."""
        require_state(before)
        require_action(action)
        candidates = self.banks[self.active][action]
        for h in range(HYPOTHESES):
            if candidates & (1 << h):
                return before ^ (hypothesis_effect(before, action, h) << action)
        return None

    @property
    def logical_hypothesis_bits(self):
        return MAX_BANKS * ACTIONS * HYPOTHESES

    def snapshot(self):
        payload = {
            "schema": SCHEMA, "bank_limit": self.bank_limit,
            "reactivate": self.reactivate, "banks": self.banks,
            "active": self.active, "plausible": self.plausible,
            "updates": self.updates, "splits": self.splits,
            "reactivations": self.reactivations,
            "ambiguous_events": self.ambiguous_events,
            "unresolved": self.unresolved,
        }
        plain = canonical(payload)
        packed = canonical({
            "payload": payload,
            "sha256": hashlib.sha256(plain).hexdigest()
        })
        if len(packed) > CHECKPOINT_LIMIT:
            raise OverflowError("HC04_CHECKPOINT_TOO_LARGE")
        return packed

    @classmethod
    def restore(cls, checkpoint):
        if type(checkpoint) is not bytes or not 0 < len(checkpoint) <= CHECKPOINT_LIMIT:
            raise ValueError("HC04_UNTRUSTED_CHECKPOINT")
        try:
            outer = json.loads(checkpoint)
            if type(outer) is not dict or set(outer) != {"payload", "sha256"}:
                raise ValueError("HC04_INVALID_ENVELOPE")
            p = outer["payload"]
            fields = {"schema", "bank_limit", "reactivate", "banks",
                      "active", "plausible", "updates", "splits",
                      "reactivations", "ambiguous_events", "unresolved"}
            if type(p) is not dict or set(p) != fields or p["schema"] != SCHEMA:
                raise ValueError("HC04_INVALID_SCHEMA")
            if hashlib.sha256(canonical(p)).hexdigest() != outer["sha256"]:
                raise ValueError("HC04_BAD_DIGEST")
            m = cls(bank_limit=p["bank_limit"], reactivate=p["reactivate"])
            banks = p["banks"]
            if (type(banks) is not list or not 1 <= len(banks) <= m.bank_limit or
                any(type(row) is not list or len(row) != ACTIONS or
                    any(type(mask) is not int or not 1 <= mask <= FULL_MASK
                        for mask in row) for row in banks)):
                raise ValueError("HC04_INVALID_BANKS")
            active, plausible = p["active"], p["plausible"]
            if type(active) is not int or not 0 <= active < len(banks):
                raise ValueError("HC04_BAD_ACTIVE")
            if type(plausible) is not list or plausible != sorted(set(plausible)) or any(
                type(i) is not int or not 0 <= i < len(banks) for i in plausible
            ):
                raise ValueError("HC04_BAD_PLAUSIBLE")
            if plausible and active not in plausible:
                raise ValueError("HC04_ACTIVE_NOT_PLAUSIBLE")
            for name in ("updates", "splits", "reactivations", "ambiguous_events", "unresolved"):
                if type(p[name]) is not int or not 0 <= p[name] <= 100000:
                    raise ValueError("HC04_BAD_COUNTER")
            if p["splits"] > len(banks) - 1 or p["reactivations"] > p["updates"]:
                raise ValueError("HC04_BAD_COUNTER_RELATION")
            m.banks = [list(row) for row in banks]
            m.active = active
            m.plausible = list(plausible)
            for name in ("updates", "splits", "reactivations", "ambiguous_events", "unresolved"):
                setattr(m, name, p[name])
            if m.snapshot() != checkpoint:
                raise ValueError("HC04_NONCANONICAL")
            return m
        except (UnicodeError, TypeError, ValueError, OverflowError, KeyError,
                json.JSONDecodeError) as exc:
            raise ValueError("HC04_UNTRUSTED_CHECKPOINT") from exc


class ConventionalConstraintControl(VersionedCausalCells):
    """Matched conventional equivalent: not independent or superior evidence."""
    pass
