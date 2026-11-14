"""AAI-10C independent bounded tokenless causal signature learner.

Nine public hypotheses per output; fixed-sized integer sufficient statistics.
AAI-10P benchmark and AAI-10A/10B original models are NEVER changed.
No science first-use or hidden simulator-law inputs exist in this module.
"""
from __future__ import annotations

import base64
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "AAI-10A"))
import models as conventional

# Frozen *public* operator grammar. Never imports hidden simulator law formulas.
RULES = conventional.GRAMMAR
TRUTH = tuple(
    tuple(conventional.pattern(rule, ((key >> 2) & 1, (key >> 1) & 1, key & 1))
          for rule in RULES)
    for key in range(8)
)
N_HYPOTHESES = len(RULES)
MAX_ROWS = 96
PREDICTION_CONFIDENCE = (0.05, 0.95)


def input_key(x):
    a, b, c = conventional.require_bits(x, 3)
    return (a << 2) | (b << 1) | c


def blank_slot(number, prior=None):
    prior = prior or ((0,) * N_HYPOTHESES, (0,) * N_HYPOTHESES)
    return {"id": number, "rows": 0,
            "mismatches": [[0] * N_HYPOTHESES for _ in range(2)],
            "prior": [list(prior[0]), list(prior[1])]}


def best_rule(slot, out):
    errors = slot["mismatches"][out]
    penalty = slot["prior"][out]
    best = 0
    value = errors[0] + penalty[0]
    for i in range(1, N_HYPOTHESES):
        trial = errors[i] + penalty[i]
        if trial < value:
            best, value = i, trial
    return best


def _check_slot(slot):
    if type(slot) is not dict or set(slot) != {"id", "rows", "mismatches", "prior"}:
        raise ValueError("invalid slot keys")
    if type(slot["id"]) is not int or slot["id"] < 0:
        raise ValueError("invalid slot ID")
    n = slot["rows"]
    if type(n) is not int or not 0 <= n <= MAX_ROWS:
        raise ValueError("invalid slot row count")
    for key, upper in (("mismatches", n), ("prior", 1)):
        arrays = slot[key]
        if type(arrays) is not list or len(arrays) != 2:
            raise ValueError("invalid hypothesis matrix")
        for a in arrays:
            if type(a) is not list or len(a) != N_HYPOTHESES:
                raise ValueError("invalid hypothesis length")
            if any(type(v) is not int or not 0 <= v <= upper for v in a):
                raise ValueError("out-of-range hypothesis count")


class BoundedCausalSignatureBank:
    """Sufficient-statistic update, protected prior association and cold restore."""

    def __init__(self, max_slots=3):
        if type(max_slots) is not int or max_slots not in (1, 3):
            raise ValueError("only frozen 1-slot and 3-slot capacities supported")
        self.max_slots = max_slots
        self.slots = [blank_slot(0)]
        self.active_id = 0
        self.next_id = 1
        self.scratch = []
        self.retrievals = 0
        self._invalidate()

    def _invalidate(self):
        self._signature_cache = {}
        self._plan_cache = {}

    def active(self):
        for slot in self.slots:
            if slot["id"] == self.active_id:
                return slot
        raise ValueError("missing active slot")

    def _selection(self, slot):
        key = slot["id"]
        if key not in self._signature_cache:
            self._signature_cache[key] = (best_rule(slot, 0), best_rule(slot, 1))
        return self._signature_cache[key]

    def _mismatches(self, slot, batch):
        a, b = self._selection(slot)
        missing = 0
        for key, m0, m1 in batch:
            truth = TRUTH[key]
            missing += (truth[a] != m0) + (truth[b] != m1)
        return missing

    def _reuse_prior(self):
        if self.max_slots == 1:
            return None
        protected = [s for s in self.slots
                     if s["id"] != self.active_id and s["rows"] >= 8]
        if not protected:
            return None
        old = min(protected, key=lambda s: s["id"])
        op0, op1 = (RULES[i][0] for i in self._selection(old))
        return (
            tuple(0 if rule[0] == op0 else 1 for rule in RULES),
            tuple(0 if rule[0] == op1 else 1 for rule in RULES),
        )

    def learn(self, row):
        # Validation occurs BEFORE mutation; cannot accept privileged fields.
        x, mediator = conventional.visible(row)
        key = input_key(x)
        self.scratch.append((key, mediator[0], mediator[1]))
        if len(self.scratch) < 2:
            return
        batch = self.scratch
        active = self.active()
        own_errors = self._mismatches(active, batch)
        others = [s for s in self.slots if s["id"] != self.active_id]
        if others:
            closest = min(others, key=lambda s: (self._mismatches(s, batch), s["id"]))
            other_err = self._mismatches(closest, batch)
        else:
            closest, other_err = None, 5
        if closest is not None and other_err <= own_errors - 1:
            target = closest
            self.retrievals += 1
        elif (self.max_slots > len(self.slots) and active["rows"] >= 8
              and own_errors >= 2):
            prior = self._reuse_prior()
            target = blank_slot(self.next_id, prior)
            self.next_id += 1
            self.slots.append(target)
        else:
            target = active
        # Fail closed on saturation; never silently truncate or overwrite memory.
        if target["rows"] + 2 > MAX_ROWS:
            # Preserve all prior durable state. The second input row is refused.
            self.scratch.pop()
            raise ValueError("frozen 96-row slot saturation")
        self.active_id = target["id"]
        for key, m0, m1 in batch:
            patterns = TRUTH[key]
            mismatches = target["mismatches"]
            for i in range(N_HYPOTHESES):
                if patterns[i] != m0:
                    mismatches[0][i] += 1
                if patterns[i] != m1:
                    mismatches[1][i] += 1
        target["rows"] += 2
        self.scratch = []
        self._invalidate()

    def predict(self, x):
        key = input_key(x)
        slot = self.active()
        h0, h1 = self._selection(slot)
        truth = TRUTH[key]
        return (PREDICTION_CONFIDENCE[truth[h0]], PREDICTION_CONFIDENCE[truth[h1]])

    def choose(self, row):
        # Same frozen AAI-10A common planner (including STOP/ties).
        conventional.visible(row)
        key = (input_key(row["x"]), tuple(row["goal"]), row["actions_taken"])
        if key not in self._plan_cache:
            self._plan_cache[key] = conventional.plan(self, row)
        return self._plan_cache[key]

    def state(self):
        return {
            "type": "bounded_causal_signature",
            "version": 1,
            "max_slots": self.max_slots,
            "slots": self.slots,
            "active_id": self.active_id,
            "next_id": self.next_id,
            "scratch": [[k, m0, m1] for k, m0, m1 in self.scratch],
            "retrievals": self.retrievals,
        }


def _pack_slot(slot):
    """Compact 23-byte fixed signature; no event history or label storage."""
    _check_slot(slot)
    bits = sum(v << i for i, v in enumerate(slot["prior"][0] + slot["prior"][1]))
    data = bytes([slot["id"], slot["rows"],
                  *slot["mismatches"][0], *slot["mismatches"][1],
                  bits & 255, (bits >> 8) & 255, (bits >> 16) & 255])
    if len(data) != 23:
        raise ValueError("bad packed slot size")
    return base64.b64encode(data).decode("ascii")


def _unpack_slot(encoded):
    if type(encoded) is not str or len(encoded) != 32:
        raise ValueError("bad base64 slot")
    try:
        raw = base64.b64decode(encoded, validate=True)
    except (ValueError, base64.binascii.Error) as exc:
        raise ValueError("invalid slot base64") from exc
    if len(raw) != 23 or base64.b64encode(raw).decode("ascii") != encoded:
        raise ValueError("noncanonical slot encoding")
    mask = raw[20] | (raw[21] << 8) | (raw[22] << 16)
    if mask >> 18:
        raise ValueError("slot prior unused bits nonzero")
    slot = {
        "id": raw[0], "rows": raw[1],
        "mismatches": [list(raw[2:11]), list(raw[11:20])],
        "prior": [[(mask >> i) & 1 for i in range(9)],
                  [(mask >> (i + 9)) & 1 for i in range(9)]],
    }
    _check_slot(slot)
    return slot


def checkpoint(model):
    state = model.state()
    state["slots"] = [_pack_slot(slot) for slot in state["slots"]]
    return conventional.canonical(state)


def cold_restore(payload):
    state = json.loads(payload)
    if conventional.canonical(state) != payload:
        raise ValueError("non-canonical checkpoint")
    if type(state) is not dict or set(state) != {
        "type", "version", "max_slots", "slots", "active_id", "next_id",
        "scratch", "retrievals"
    }:
        raise ValueError("invalid checkpoint")
    if state["type"] != "bounded_causal_signature" or state["version"] != 1:
        raise ValueError("wrong checkpoint type/version")
    model = BoundedCausalSignatureBank(state["max_slots"])
    slots = state["slots"]
    if type(slots) is not list or not 1 <= len(slots) <= model.max_slots:
        raise ValueError("bad slot count")
    slots = [_unpack_slot(s) for s in slots]
    ids = [s["id"] for s in slots]
    if sorted(ids) != list(range(len(ids))):
        raise ValueError("slot IDs must be dense and durable")
    if state["next_id"] != len(ids) or type(state["next_id"]) is not int:
        raise ValueError("invalid next slot ID")
    if type(state["active_id"]) is not int or state["active_id"] not in ids:
        raise ValueError("invalid active slot")
    rows = state["scratch"]
    if type(rows) is not list or len(rows) > 1:
        raise ValueError("invalid scratch size")
    for row in rows:
        if type(row) is not list or len(row) != 3 or any(
            type(v) is not int for v in row):
            raise ValueError("invalid scratch row")
        if not 0 <= row[0] < 8 or any(x not in (0, 1) for x in row[1:]):
            raise ValueError("bad scratch content")
    if type(state["retrievals"]) is not int or state["retrievals"] < 0:
        raise ValueError("invalid retrieval count")
    model.slots = slots
    model.active_id = state["active_id"]
    model.next_id = state["next_id"]
    model.scratch = [tuple(x) for x in rows]
    model.retrievals = state["retrievals"]
    model._invalidate()
    if checkpoint(model) != payload:
        raise ValueError("cold restore not byte identical")
    return model
