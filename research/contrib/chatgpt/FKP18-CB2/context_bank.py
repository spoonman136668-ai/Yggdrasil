"""CB2 research-only four-relation bank with earned-contradiction repair.

Reuses the exact CB1 two-feature learner. The routing key is explicitly a
PUBLIC R7 low-two-bit feature; gate discovery is not claimed. No private law
or future outcome is available here. This is not a native Yggdrasil change.
"""
from __future__ import annotations
import hashlib
import json
from binding import ConditionalTemporalBinder, _credit_public, _feature_bits, _history, _state
from strong_control import ExactTwoFeatureControl

MODES = 4
MISMATCH_TRIGGER = 8
CREDITS_PER_RULE = 128
MAGIC = "FKP18_CB2_PUBLIC_RELATION_BANK_V1"
MAX_CHECKPOINT_BYTES = 1024


def _mode_from_credit(bits):
    return (bits >> 28) & 3


def _predict_rule(bits, rule):
    a, b, table = rule[:3]
    index = (((bits >> a) & 1) << 1) | ((bits >> b) & 1)
    return (table >> index) & 1


def _canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("ascii")


class GatedRelationBank:
    """Four sealed CB1 laws, repair one after 8 public contradictions.

    New evidence never silently updates other modes. Before repair the old
    prediction remains live; after 128 new observations one replacement is
    atomically installed, preserving three previously learned CB1 snapshots.
    """
    def __init__(self):
        self._models = [ConditionalTemporalBinder() for _ in range(MODES)]
        self._sealed = False
        self._mismatches = [0] * MODES
        self._shadows = {}
        self._versions = [1] * MODES
        self._earned = 0
        self._repairs = []

    def observe_public(self, row):
        credit, _ = _credit_public(row)  # validate private fields BEFORE mutation
        if credit is None:
            return
        bits, correct = credit
        mode = _mode_from_credit(bits)  # mode of action at t-2, not current mode
        if not self._sealed:
            self._models[mode].observe_public(row)
            self._earned += 1
            return
        if mode in self._shadows:
            shadow = self._shadows[mode]
            shadow.observe_public(row)
            if shadow._credited == CREDITS_PER_RULE:
                shadow.seal()  # failure leaves old model live
                self._models[mode] = shadow
                self._versions[mode] += 1
                self._repairs.append(mode)
                del self._shadows[mode]
                self._mismatches[mode] = 0
            self._earned += 1
            return
        old = self._models[mode].binding
        if _predict_rule(bits, old) == correct:
            self._mismatches[mode] = 0
        else:
            self._mismatches[mode] += 1
            if self._mismatches[mode] == MISMATCH_TRIGGER:
                self._shadows[mode] = ConditionalTemporalBinder()
        self._earned += 1

    def seal(self):
        if self._sealed:
            raise ValueError("CB2_ALREADY_SEALED")
        if any(m._credited != CREDITS_PER_RULE for m in self._models):
            raise ValueError("CB2_INCOMPLETE_MODE_EVIDENCE")
        # Stage all independent fit computations before changing state.
        new = [ConditionalTemporalBinder.restore(m.seal().snapshot()) for m in self._models]
        self._models = new
        self._sealed = True
        return self

    def choose_public(self, before, history):
        if not self._sealed:
            return None
        state = _state(before)
        _history(history, state)
        return self._models[state[7] & 3].choose_public(state, history)

    @property
    def repairs(self):
        return tuple(self._repairs)

    @property
    def versions(self):
        return tuple(self._versions)

    @property
    def credits(self):
        return self._earned

    @property
    def logical_persisted_relation_bytes(self):
        return MODES * ConditionalTemporalBinder.CHECKPOINT_BYTES

    def slot_receipts(self):
        if not self._sealed:
            raise ValueError("CB2_UNSEALED")
        return tuple(m.receipt() for m in self._models)

    def snapshot(self):
        if not self._sealed or self._shadows:
            raise ValueError("CB2_INCOMPLETE_SHADOW_OR_UNSEALED")
        body = {"magic": MAGIC, "versions": self._versions,
                "models": [m.snapshot().hex() for m in self._models]}
        payload = _canonical(body)
        raw = _canonical({"body": body, "sha256": hashlib.sha256(payload).hexdigest()})
        if len(raw) > MAX_CHECKPOINT_BYTES:
            raise ValueError("CB2_CHECKPOINT_CAPACITY")
        return raw

    @classmethod
    def restore(cls, checkpoint):
        if type(checkpoint) is not bytes or len(checkpoint) > MAX_CHECKPOINT_BYTES:
            raise ValueError("CB2_BAD_SNAPSHOT")
        try:
            outer = json.loads(checkpoint)
            if type(outer) is not dict or set(outer) != {"body", "sha256"}:
                raise ValueError("CB2_BAD_ENVELOPE")
            body = outer["body"]
            if type(body) is not dict or set(body) != {"magic", "versions", "models"}:
                raise ValueError("CB2_BAD_SCHEMA")
            if (body["magic"] != MAGIC or type(body["models"]) is not list or
                    len(body["models"]) != MODES or type(body["versions"]) is not list or
                    len(body["versions"]) != MODES or
                    any(type(v) is not int or v < 1 or v > 16 for v in body["versions"])):
                raise ValueError("CB2_BAD_FIELDS")
            if hashlib.sha256(_canonical(body)).hexdigest() != outer["sha256"]:
                raise ValueError("CB2_BAD_DIGEST")
            models = [ConditionalTemporalBinder.restore(bytes.fromhex(item))
                      for item in body["models"] if type(item) is str]
            if len(models) != MODES:
                raise ValueError("CB2_MISSING_MODEL")
            obj = cls()
            obj._models = models
            obj._versions = list(body["versions"])
            obj._sealed = True
            if obj.snapshot() != checkpoint:
                raise ValueError("CB2_NONCANONICAL")
            return obj
        except (ValueError, TypeError, KeyError, UnicodeError) as exc:
            raise ValueError("CB2_INVALID_SNAPSHOT") from exc


class ConventionalFourSlotBank:
    """Independent exact symbolic feature-pair fitting, equal public evidence.

    Uses CB1's existing independent comparator (not the direct binder).
    Routing/repair trigger is shared by design and is therefore not a claim
    of unique native inference.
    """
    def __init__(self):
        self._models = [ExactTwoFeatureControl() for _ in range(MODES)]
        self._sealed = False
        self._mismatches = [0] * MODES
        self._shadows = {}
        self._versions = [1] * MODES
        self._repairs = []

    def observe_public(self, row):
        credit, _ = _credit_public(row)
        if credit is None:
            return
        bits, correct = credit
        mode = _mode_from_credit(bits)
        if not self._sealed:
            self._models[mode].observe_public(row)
            return
        if mode in self._shadows:
            shadow = self._shadows[mode]
            shadow.observe_public(row)
            if len(shadow.examples) == CREDITS_PER_RULE:
                shadow.seal()
                self._models[mode] = shadow
                self._versions[mode] += 1
                self._repairs.append(mode)
                del self._shadows[mode]
                self._mismatches[mode] = 0
            return
        fitted = self._models[mode].fitted
        if _predict_rule(bits, fitted[1:]) == correct:
            self._mismatches[mode] = 0
        else:
            self._mismatches[mode] += 1
            if self._mismatches[mode] == MISMATCH_TRIGGER:
                self._shadows[mode] = ExactTwoFeatureControl()

    def seal(self):
        if self._sealed:
            raise ValueError("CB2_CONTROL_FROZEN")
        if any(len(m.examples) != CREDITS_PER_RULE for m in self._models):
            raise ValueError("CB2_CONTROL_INCOMPLETE")
        for m in self._models:
            m.seal()
        self._sealed = True
        return self

    def choose_public(self, before, history):
        state = _state(before)
        _history(history, state)
        if not self._sealed:
            return None
        return self._models[state[7] & 3].choose_public(state, history)

    @property
    def repairs(self):
        return tuple(self._repairs)

    @property
    def versions(self):
        return tuple(self._versions)
