"""ST11 optional native-model-owned, public-witness-trained probe-value head.

No world simulator, evaluator truth, reward oracle, source actor, or new
causal substrate. The existing ST9 NativeRepair8 model remains the only
causal memory. This small preference head learns which admitted public
action-feature groups previously increased native causal identifiability.
ST11 is source-only engineering, NOT original-world scientific first use.
"""
from hashlib import sha256
import json
import re

from research.nci04_st9.native_repair import NativeRepair8, features
from research.nci04_st10.adaptive_actor import _rank, choose_intervention

SCHEMA = "yggdrasil.nci04.st11.public-probe-preference.v1"
MAX_EVENTS = 8
SHA_PATTERN = re.compile(r"[0-9a-f]{64}\Z")


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _validated_model(raw):
    if type(raw) is not str:
        raise ValueError("ST11_NATIVE_CHECKPOINT_TYPE")
    model = NativeRepair8.restore(raw)
    if model.variant != "repair" or model.snapshot() != raw:
        raise ValueError("ST11_NATIVE_REPAIR_CHECKPOINT_REQUIRED")
    return model


def _core_identity(model):
    record = json.loads(model.snapshot())
    record.pop("phase")
    record.pop("rotation")
    return sha256(canonical(record).encode("utf-8")).hexdigest()


def _counts(events):
    trials = [0] * 16
    positive = [0] * 16
    for ref, before_id, after_id, action, mode, gain in events:
        if (type(ref) is not str or SHA_PATTERN.fullmatch(ref) is None or
                type(before_id) is not str or SHA_PATTERN.fullmatch(before_id) is None or
                type(after_id) is not str or SHA_PATTERN.fullmatch(after_id) is None or
                type(action) is not int or action not in range(2, 17) or
                type(mode) is not int or mode not in (1, 2) or
                type(gain) is not int or gain not in (0, 1)):
            raise ValueError("ST11_EVENT_LEDGER_MALFORMED")
        public_feature = features(action - 1, 2)
        offset = 0 if mode == 1 else 8
        for index in range(8):
            if public_feature & (1 << index):
                trials[offset + index] += 1
                positive[offset + index] += gain
    return trials, positive


class NativeProbePreference:
    """One opt-in preference head bound to an unchanged native learner."""

    def __init__(self, native):
        if type(native) is not NativeRepair8 or native.variant != "repair":
            raise ValueError("ST11_ORIGINAL_NATIVE_MODEL_REQUIRED")
        _validated_model(native.snapshot())
        if type(native.updates) is not int or not 0 <= native.updates <= MAX_EVENTS:
            raise ValueError("ST11_NATIVE_INTERVENTION_LIMIT")
        self.origin_count = native.updates
        self.origin_identity = _core_identity(native)
        self.current_identity = self.origin_identity
        self.events = []
        self.trials = [0] * 16
        self.positive = [0] * 16

    def posterior(self, native, action):
        self._check_bound(native)
        if type(action) is not int or not 2 <= action <= 16:
            raise ValueError("ST11_ACTION_CODE_INVALID")
        feat = features(action - 1, 2)
        offset = 0 if native.degree == 1 else 8
        active = [i + offset for i in range(8) if feat & (1 << i)]
        if not active:
            return (1, 2)
        # Beta-smoothed empirical value. Rational arithmetic avoids platform
        # floating drift and gives the independent Beta-count control parity.
        from fractions import Fraction
        mean = sum((Fraction(self.positive[i] + 1, self.trials[i] + 2)
                    for i in active), Fraction()) / len(active)
        return mean.numerator, mean.denominator

    def _check_bound(self, native):
        if type(native) is not NativeRepair8 or native.variant != "repair":
            raise ValueError("ST11_ORIGINAL_NATIVE_MODEL_REQUIRED")
        if _core_identity(native) != self.current_identity:
            raise ValueError("ST11_NATIVE_CORE_CUSTODY_DRIFT")
        if native.updates != self.origin_count + len(self.events):
            raise ValueError("ST11_UNRECONCILED_NATIVE_UPDATES")
        if len(self.events) > MAX_EVENTS:
            raise ValueError("ST11_LEARNING_BUDGET_EXCEEDED")

    def propose(self, native):
        """Pure read. Never executes an action or updates native weights."""
        self._check_bound(native)
        fallback = choose_intervention(native)  # includes calibration, conflicts, budget
        if fallback is None or len(self.events) < 2:
            return fallback
        used = [b for b, _ in native.experiences]
        degree = native.degree
        if degree == 1:
            current = _rank([features(b, 1) for b in used], 4)
            candidates = [b for b in range(1, 16) if b not in used and
                          _rank([features(k, 1) for k in used] +
                                [features(b, 1)], 4) > current]
            if not candidates:
                current = _rank([features(b, 2) for b in used], 8)
                candidates = [b for b in range(1, 16) if b not in used and
                              features(b, 2) >> 4 and
                              _rank([features(k, 2) for k in used] +
                                    [features(b, 2)], 8) > current]
        else:
            current = _rank([features(b, 2) for b in used], 8)
            candidates = [b for b in range(1, 16) if b not in used and
                          _rank([features(k, 2) for k in used] +
                                [features(b, 2)], 8) > current]
        if not candidates:
            return None
        scores = {b: self.posterior(native, b + 1) for b in candidates}
        from fractions import Fraction
        # No empirical feature evidence: defer to ST10 rather than
        # represent a prior as successfully learned intervention value.
        offset = 0 if degree == 1 else 8
        if not any(self.trials[offset + i] for b in candidates
                   for i in range(8) if features(b, 2) & (1 << i)):
            return fallback
        # Equal posterior: preserve the already qualified ST10 action if
        # admissible. A data-learned preference may override only on a
        # strict rational-valued difference.
        best = max(Fraction(*x) for x in scores.values())
        tied = [b for b in candidates if Fraction(*scores[b]) == best]
        if fallback - 1 in tied:
            return fallback
        return min(tied) + 1

    def observe_revealed(self, before_raw, after_raw, public_before, action,
                        public_after, evidence_sha256):
        """Transactional opt-in learning only after native observation.

        Public-shaped receipts prove deterministic consistency with the
        native learner, NOT independent source-owner authenticity.
        """
        before = _validated_model(before_raw)
        after = _validated_model(after_raw)
        if (type(evidence_sha256) is not str or
                SHA_PATTERN.fullmatch(evidence_sha256) is None or
                type(action) is not int or action not in range(2, 17) or
                before.phase != 1 or before.rotation not in (1, 2, 3) or
                after.phase != 2 or
                before.updates + 1 != after.updates or
                after.updates > MAX_EVENTS or
                len(after.experiences) != len(before.experiences) + 1 or
                after.experiences[:-1] != before.experiences or
                after.experiences[-1][0] != action - 1):
            raise ValueError("ST11_UNQUALIFIED_OR_MISSING_NATIVE_TRANSITION")
        before_id, after_id = _core_identity(before), _core_identity(after)
        # The exact original native observation is replayed on a disposable
        # native clone; no hidden source rule or invented target is passed.
        if (type(public_before) not in (list, tuple) or
                type(public_after) not in (list, tuple) or
                len(public_before) != 8 or len(public_after) != 8 or
                any(type(z) is not int or z not in (0, 1)
                    for z in (*public_before, *public_after))):
            raise ValueError("ST11_PUBLIC_REVEAL_INVALID")
        cloned = NativeRepair8.restore(before_raw)
        x = [u ^ v for u, v in zip(public_before, public_after)]
        cloned.observe(public_before, action, x, public_after, train=True)
        if cloned.snapshot() != after_raw:
            raise ValueError("ST11_UNREPRODUCIBLE_NATIVE_PUBLIC_OUTCOME")
        gain = int(after.rank > before.rank or
                   after.growth_events > before.growth_events)
        event = [evidence_sha256, before_id, after_id, action, before.degree, gain]
        for prior in self.events:
            if prior[0] == evidence_sha256:
                if prior != event:
                    raise ValueError("ST11_DUPLICATE_SOURCE_REF_CONFLICT")
                return self  # Idempotent; no additional fitted credit.
        if (before_id != self.current_identity or
                self.origin_count + len(self.events) != before.updates or
                len(self.events) >= MAX_EVENTS - self.origin_count):
            raise ValueError("ST11_UNAUTHORIZED_OR_STALE_NATIVE_UPDATE")
        result = object.__new__(NativeProbePreference)
        result.origin_count = self.origin_count
        result.origin_identity = self.origin_identity
        result.current_identity = after_id
        result.events = self.events + [event]
        result.trials, result.positive = _counts(result.events)
        if result.trials != _counts(result.events)[0]:
            raise ValueError("ST11_CREDIT_NOT_RECONCILABLE")
        return result

    def snapshot(self):
        return canonical({
            "schema": SCHEMA, "origin_count": self.origin_count,
            "origin_identity": self.origin_identity,
            "current_identity": self.current_identity,
            "events": self.events, "trials": self.trials,
            "positive": self.positive, "scientific_pass": False,
            "accepted_native": False,
        })

    @classmethod
    def restore(cls, raw, native):
        if type(raw) is not str or len(raw) > 4096:
            raise ValueError("ST11_CHECKPOINT_CAP")
        try:
            d = json.loads(raw)
            required = {"schema", "origin_count", "origin_identity",
                        "current_identity", "events", "trials", "positive",
                        "scientific_pass", "accepted_native"}
            if (type(d) is not dict or set(d) != required or
                    d["schema"] != SCHEMA or d["scientific_pass"] is not False or
                    d["accepted_native"] is not False or
                    type(d["origin_count"]) is not int or
                    not 0 <= d["origin_count"] <= MAX_EVENTS or
                    any(type(d[k]) is not str or
                        SHA_PATTERN.fullmatch(d[k]) is None
                        for k in ("origin_identity", "current_identity")) or
                    type(d["events"]) is not list or
                    len(d["events"]) > MAX_EVENTS - d["origin_count"] or
                    any(type(e) is not list or len(e) != 6
                        for e in d["events"]) or
                    len({e[0] for e in d["events"]}) != len(d["events"]) or
                    (d["events"] and
                     (d["events"][0][1] != d["origin_identity"] or
                      d["events"][-1][2] != d["current_identity"] or
                      any(prev[2] != nxt[1] for prev, nxt in
                          zip(d["events"], d["events"][1:])))) or
                    (not d["events"] and
                     d["origin_identity"] != d["current_identity"]) or
                    _counts(d["events"]) != (d["trials"], d["positive"])):
                raise ValueError("ST11_MALFORMED_COLD_STATE")
            instance = object.__new__(cls)
            instance.origin_count = d["origin_count"]
            instance.origin_identity = d["origin_identity"]
            instance.current_identity = d["current_identity"]
            instance.events = d["events"]
            instance.trials = d["trials"]
            instance.positive = d["positive"]
            if instance.snapshot() != raw:
                raise ValueError("ST11_NONCANONICAL_COLD_STATE")
            instance._check_bound(native)
            return instance
        except (TypeError, KeyError, IndexError, OverflowError) as exc:
            raise ValueError("ST11_BAD_COLD_STRUCTURE") from exc
