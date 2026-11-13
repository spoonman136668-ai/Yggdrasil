"""DG1 Sleep01: protected offline replay of *physical* causal observations.

No phase labels, evaluator answers or synthetic dream outputs enter learning.
This is synthetic DEV research, not a native runtime or a neural sleep model.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from itertools import combinations

SCHEMA = "ygg.dg1-sleep01.consolidated-causal-program.v1"
FULL = (1 << 40) - 1
TRIPLES = tuple(combinations(range(4), 3))
MAX_HISTORY = 64
BEAM_WIDTH = 48
SNAP_LIMIT = 8192


def valid_state(state):
    if type(state) is not int or not 0 <= state < 16:
        raise ValueError("SLEEP01_BAD_STATE")


def valid_action(action):
    if type(action) is not int or not 0 <= action < 4:
        raise ValueError("SLEEP01_BAD_ACTION")


def rule_effect(state, h, family):
    """Exact HC09 frozen 40-rule semantics (distinct control implementation)."""
    valid_state(state)
    if type(h) is not int or not 0 <= h < 40:
        raise ValueError("SLEEP01_BAD_RULE")
    if family == "native":
        if h < 32:
            return (((state & (h >> 1)).bit_count()) & 1) ^ (h & 1)
        return int(sum((state >> i) & 1 for i in TRIPLES[(h - 32) // 2]) >= 2) ^ (h & 1)
    if family == "conventional":
        if h < 32:
            bit = 0
            for i in range(4):
                if (h // 2) & (1 << i):
                    bit ^= (state >> i) & 1
            return bit ^ (h & 1)
        cols = TRIPLES[(h - 32) // 2]
        return (1 if sum((state >> i) & 1 for i in cols) >= 2 else 0) ^ (h & 1)
    raise ValueError("SLEEP01_BAD_FAMILY")


def surviving(mask, state, effect, family):
    return sum(1 << i for i in range(40) if mask & (1 << i) and rule_effect(state, i, family) == effect)


def unanimous(mask, state, family):
    zero = one = False
    for i in range(40):
        if mask & (1 << i):
            if rule_effect(state, i, family):
                one = True
            else:
                zero = True
            if one and zero:
                return None
    if one == zero:
        return None
    return int(one)


@dataclass(frozen=True)
class _Hypothesis:
    banks: tuple
    active: int
    switches: int
    unexplained: int
    path: tuple

    def rank(self):
        # Minimize unexplained observations FIRST; context changes cost complexity.
        return (self.unexplained, self.switches, len(self.banks), self.path,
                self.banks, self.active)


def replay(history, family, max_contexts):
    """Bounded offline search for two persistent latent causal contexts.

    No context labels. A hypothesis survives only if its frozen causal-program
    version space explains a *real* physical outcome. Unexplained observations
    are retained and penalized, not converted into convenient pseudolabels.
    """
    beam = [_Hypothesis(((FULL, FULL, FULL, FULL),), 0, 0, 0, ())]
    for state, action, after in history:
        eff = int(after != state)
        new = {}
        for h in beam:
            found = False
            for bank_idx in range(min(max_contexts, len(h.banks) + 1)):
                if bank_idx == len(h.banks):
                    banks = list(h.banks) + [(FULL, FULL, FULL, FULL)]
                else:
                    banks = list(h.banks)
                current = banks[bank_idx]
                mask = surviving(current[action], state, eff, family)
                if not mask:
                    continue
                found = True
                amended = list(current)
                amended[action] = mask
                banks[bank_idx] = tuple(amended)
                node = _Hypothesis(tuple(banks), bank_idx,
                                   h.switches + int(bank_idx != h.active),
                                   h.unexplained, h.path + (bank_idx,))
                key = (node.banks, node.active)
                if key not in new or node.rank() < new[key].rank():
                    new[key] = node
            if not found:
                # Fail closed: keep contradiction receipt, without learning from it.
                node = _Hypothesis(h.banks, h.active, h.switches,
                                   h.unexplained + 1, h.path + (-1,))
                key = (node.banks, node.active)
                if key not in new or node.rank() < new[key].rank():
                    new[key] = node
        beam = sorted(new.values(), key=lambda x: x.rank())[:BEAM_WIDTH]
        if not beam:
            raise AssertionError("SLEEP01_EMPTY_BEAM")
    return min(beam, key=lambda x: x.rank())


def _proofs(history, hypothesis, family):
    """Only predictions made *before* applying each real observation count.

    Assembles independently verifiable physical tests from the chronological
    source stream. Neither final fitted masks nor dreams produce evidence.
    """
    masks = [[FULL] * 4 for _ in hypothesis.banks]
    proofs = [[set() for _ in range(4)] for _ in hypothesis.banks]
    for (s, a, nxt), idx in zip(history, hypothesis.path):
        if idx < 0:
            continue
        pred = unanimous(masks[idx][a], s, family)
        eff = int(s != nxt)
        if pred == eff:
            proofs[idx][a].add(s)
        masks[idx][a] = surviving(masks[idx][a], s, eff, family)
        assert masks[idx][a]
    active = hypothesis.active
    active_streak = 0
    for idx in reversed(hypothesis.path):
        if idx != active:
            break
        active_streak += 1
    return tuple(tuple(tuple(sorted(x)) for x in bank) for bank in proofs), active_streak


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("ascii")


class SleepMemory:
    def __init__(self, family="native", max_contexts=2, dreams=True):
        if family not in ("native", "conventional") or type(max_contexts) is not int or max_contexts not in (1, 2) or type(dreams) is not bool:
            raise ValueError("SLEEP01_INVALID_CONFIGURATION")
        self.family = family
        self.max_contexts = max_contexts
        self.dreams_enabled = dreams
        self.history = []
        self.banks = ((FULL, FULL, FULL, FULL),)
        self.active = 0
        self.proofs = (((), (), (), ()),)
        self.active_streak = 0
        self.switches = 0
        self.unexplained = 0
        self.sleep_cycles = 0
        self.dream_proposals = ()

    def observe(self, before, action, after):
        valid_state(before)
        valid_action(action)
        valid_state(after)
        if after not in (before, before ^ (1 << action)):
            raise ValueError("SLEEP01_NONLOCAL_PHYSICAL_TRANSITION")
        self.history.append((before, action, after))
        if len(self.history) > MAX_HISTORY:
            self.history.pop(0)

    def sleep(self):
        if not self.history:
            raise ValueError("SLEEP01_EMPTY_SLEEP")
        h = replay(self.history, self.family, self.max_contexts)
        proofs, streak = _proofs(self.history, h, self.family)
        self.banks, self.active = h.banks, h.active
        self.proofs, self.active_streak = proofs, streak
        self.switches, self.unexplained = h.switches, h.unexplained
        self.sleep_cycles += 1
        # Dreams are *untrusted prediction proposals*, never synthetic labels.
        if self.dreams_enabled:
            visited = {(s, a) for s, a, _ in self.history}
            proposed = []
            for s in range(16):
                for a in range(4):
                    if (s, a) in visited:
                        continue
                    effect = unanimous(self.banks[self.active][a], s, self.family)
                    if effect is not None:
                        proposed.append((s, a, s ^ (effect << a)))
                    if len(proposed) == 8:
                        break
                if len(proposed) == 8:
                    break
            self.dream_proposals = tuple(proposed)
        else:
            self.dream_proposals = ()

    def predict(self, state, action):
        valid_state(state)
        valid_action(action)
        if not self.sleep_cycles or self.unexplained or self.active_streak < 3:
            return None
        if len(self.proofs[self.active][action]) < 2:
            return None
        effect = unanimous(self.banks[self.active][action], state, self.family)
        return None if effect is None else state ^ (effect << action)

    def snapshot(self):
        payload = {
            "schema": SCHEMA, "family": self.family,
            "max_contexts": self.max_contexts, "dreams_enabled": self.dreams_enabled,
            "history": self.history, "banks": self.banks, "active": self.active,
            "proofs": self.proofs, "active_streak": self.active_streak,
            "switches": self.switches, "unexplained": self.unexplained,
            "sleep_cycles": self.sleep_cycles, "dream_proposals": self.dream_proposals,
        }
        result = canonical({"payload": payload, "sha256": hashlib.sha256(canonical(payload)).hexdigest()})
        if len(result) > SNAP_LIMIT:
            raise ValueError("SLEEP01_TOO_LARGE")
        return result

    @classmethod
    def restore(cls, raw):
        if type(raw) is not bytes or not 0 < len(raw) <= SNAP_LIMIT:
            raise ValueError("SLEEP01_INVALID_SNAPSHOT")
        try:
            outer = json.loads(raw)
            if type(outer) is not dict or set(outer) != {"payload", "sha256"}:
                raise ValueError("SLEEP01_BAD_ENVELOPE")
            p = outer["payload"]
            fields = {"schema", "family", "max_contexts", "dreams_enabled", "history",
                      "banks", "active", "proofs", "active_streak", "switches",
                      "unexplained", "sleep_cycles", "dream_proposals"}
            if type(p) is not dict or set(p) != fields or p["schema"] != SCHEMA:
                raise ValueError("SLEEP01_BAD_SCHEMA")
            if hashlib.sha256(canonical(p)).hexdigest() != outer["sha256"]:
                raise ValueError("SLEEP01_BAD_DIGEST")
            m = cls(p["family"], p["max_contexts"], p["dreams_enabled"])
            if type(p["history"]) is not list or not 0 <= len(p["history"]) <= MAX_HISTORY:
                raise ValueError("SLEEP01_HISTORY_SIZE")
            for item in p["history"]:
                if type(item) is not list or len(item) != 3:
                    raise ValueError("SLEEP01_HISTORY_SHAPE")
                m.observe(*item)
            if type(p["sleep_cycles"]) is not int or not 0 <= p["sleep_cycles"] <= 100000:
                raise ValueError("SLEEP01_CYCLES")
            if p["sleep_cycles"]:
                m.sleep()
                # Internals are fully deterministic rederivations from physical data.
                for key, expected in (("banks", m.banks), ("active", m.active),
                                       ("proofs", m.proofs), ("active_streak", m.active_streak),
                                       ("switches", m.switches), ("unexplained", m.unexplained),
                                       ("dream_proposals", m.dream_proposals)):
                    if canonical(p[key]) != canonical(expected):
                        raise ValueError("SLEEP01_FORGED_DERIVATION_" + key)
                m.sleep_cycles = p["sleep_cycles"]
            else:
                if m.history:
                    # An awake-only pending log must never claim learned masks.
                    if canonical(p["banks"]) != canonical(m.banks):
                        raise ValueError("SLEEP01_PREMATURE_BANKS")
            if raw != m.snapshot():
                raise ValueError("SLEEP01_NONCANONICAL")
            return m
        except (ValueError, TypeError, KeyError, UnicodeError, OverflowError) as exc:
            raise ValueError("SLEEP01_INVALID_SNAPSHOT") from exc


class BayesianRunLength:
    """Independent empirical current-window baseline; no causal grammar."""
    def __init__(self, window=16):
        if type(window) is not int or window != 16:
            raise ValueError("SLEEP01_BAD_WINDOW")
        self.window = window
        self.events = []

    def observe(self, before, action, after):
        valid_state(before)
        valid_action(action)
        valid_state(after)
        if after not in (before, before ^ (1 << action)):
            raise ValueError("SLEEP01_NONLOCAL")
        self.events.append((before, action, after))
        self.events = self.events[-self.window:]

    def predict(self, state, action):
        valid_state(state)
        valid_action(action)
        obs = [int(s != aft) for s, a, aft in self.events if (s, a) == (state, action)]
        if len(obs) < 4:
            return None
        ones = sum(obs)
        # Beta(1,1): n=4 permits confidence only if all four agree.
        p = (ones + 1) / (len(obs) + 2)
        if p < 0.2:
            return state
        if p > 0.8:
            return state ^ (1 << action)
        return None

    def snapshot(self):
        payload = {"schema": "ygg.dg1-sleep01.bayesian-runlength.v1",
                   "window": self.window, "events": self.events}
        return canonical({"payload": payload, "sha256": hashlib.sha256(canonical(payload)).hexdigest()})

    @classmethod
    def restore(cls, raw):
        try:
            outer = json.loads(raw)
            payload = outer["payload"]
            if outer["sha256"] != hashlib.sha256(canonical(payload)).hexdigest() or payload["schema"] != "ygg.dg1-sleep01.bayesian-runlength.v1":
                raise ValueError("SLEEP01_BAYES_HASH")
            m = cls(payload["window"])
            for x in payload["events"]:
                m.observe(*x)
            if raw != m.snapshot():
                raise ValueError("SLEEP01_BAYES_CANONICAL")
            return m
        except (ValueError, TypeError, KeyError) as exc:
            raise ValueError("SLEEP01_BAYES_INVALID") from exc
