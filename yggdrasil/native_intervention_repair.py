"""NKR-11: source-pinned, non-token, exact-integer intervention-relation repair.

The learner never sees a hidden world phase, private causal mask or test
outcome. A FIRST PUBLIC contradiction to a frozen old mechanism gates a new
immutable intervention-effect signature. Prior memory remains frozen.

The ten-bit GF(2) hypothesis class is specified in advance. Inferring a
previously unseen action/context interaction is not free-form invention of
a fundamentally new reasoning grammar, nor is a source SHA authenticity.
"""
from __future__ import annotations

import hashlib
import json
import re

SCHEMA = "yggdrasil.nkr11.intervention-checkpoint.v1"
BUNDLE_SCHEMA = "yggdrasil.nkr11.public-action-bundle.v1"
SOURCE_MODE = "engineering_fixture_only"
SOURCE_KIND = "observed_intervention"
MAX_RECORDS = 32
MAX_BYTES = 65_536
FEATURE_COUNT = 10
MASK = (1 << FEATURE_COUNT) - 1


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def digest(value):
    return hashlib.sha256(value).hexdigest()


def _verify_pinned(raw, pin, code):
    if (not isinstance(raw, bytes) or type(pin) is not str
            or not re.fullmatch(r"[0-9a-f]{64}", pin)
            or digest(raw) != pin):
        raise ValueError(code + "_SHA_DRIFT")


def _parse(raw, *, max_size=MAX_BYTES):
    if not isinstance(raw, bytes) or len(raw) > max_size:
        raise ValueError("NKR11_JSON_SIZE_INVALID")
    try:
        doc = json.loads(raw.decode("ascii"))
    except (ValueError, UnicodeError) as exc:
        raise ValueError("NKR11_JSON_INVALID") from exc
    if raw != canonical(doc) or type(doc) is not dict:
        raise ValueError("NKR11_JSON_NOT_CANONICAL")
    return doc


def _records(rows, *, expected=None):
    if (type(rows) is not list or not 1 <= len(rows) <= MAX_RECORDS
            or (expected is not None and len(rows) != expected)):
        raise ValueError("NKR11_RECORDS_BUDGET_OR_COUNT")
    result, refs, pairs = [], set(), set()
    for item in rows:
        if type(item) is not list or len(item) != 4:
            raise ValueError("NKR11_RECORD_SHAPE")
        ref, context, action, outcome = item
        if (type(ref) is not str or re.fullmatch(
                r"[a-z][a-z0-9:_-]{4,79}", ref) is None):
            raise ValueError("NKR11_SOURCE_REF_INVALID")
        if type(context) is not int or not 0 <= context <= 15:
            raise ValueError("NKR11_CONTEXT_INVALID")
        if type(action) is not int or action not in (0, 1):
            raise ValueError("NKR11_ACTION_INVALID")
        if type(outcome) is not int or outcome not in (0, 1):
            raise ValueError("NKR11_OUTCOME_INVALID")
        if ref in refs or (context, action) in pairs:
            raise ValueError("NKR11_DUPLICATE_REF_OR_INTERVENTION")
        refs.add(ref)
        pairs.add((context, action))
        result.append((ref, context, action, outcome))
    return tuple(result)


def _bundle(raw, pin, *, expected=None):
    _verify_pinned(raw, pin, "NKR11_PUBLIC_BUNDLE")
    d = _parse(raw)
    if (set(d) != {"schema", "source_id", "source_kind",
                   "source_mode", "records"}
            or d["schema"] != BUNDLE_SCHEMA
            or d["source_kind"] != SOURCE_KIND
            or d["source_mode"] != SOURCE_MODE
            or type(d["source_id"]) is not str
            or re.fullmatch(r"[a-z][a-z0-9:_-]{4,79}",
                            d["source_id"]) is None):
        raise PermissionError("NKR11_SOURCE_NOT_QUALIFIED")
    return d["source_id"], _records(d["records"], expected=expected)


def features(context, action):
    """10-bit causal signature: intercept, x0..x3, a, a*x0..a*x3."""
    if type(context) is not int or not 0 <= context <= 15:
        raise ValueError("NKR11_CONTEXT_INVALID")
    if type(action) is not int or action not in (0, 1):
        raise ValueError("NKR11_ACTION_INVALID")
    return 1 | (context << 1) | (action << 5) | ((context * action) << 6)


class IntegerCausalSignature:
    """Integer-exact incremental GF(2) elimination with safe abstention.

    No parameter updates based on unknown test labels. Missing identifiable
    counterfactuals return None, rather than guessed boolean outcomes.
    """
    __slots__ = ("_rows", "_basis")

    def __init__(self, observations):
        rows = tuple(observations)
        if len(rows) > MAX_RECORDS:
            raise ValueError("NKR11_SIGNATURE_OBSERVATION_LIMIT")
        pivots = {}
        for _, context, action, outcome in rows:
            mask, result = features(context, action), outcome
            for pivot in sorted(pivots, reverse=True):
                left, rhs = pivots[pivot]
                if (mask >> pivot) & 1:
                    mask ^= left
                    result ^= rhs
            if mask:
                pivots[mask.bit_length() - 1] = (mask, result)
            elif result:
                raise ValueError("NKR11_CONTRADICTORY_SAME_EPOCH_EVIDENCE")
        self._rows = rows
        self._basis = pivots

    @property
    def rank(self):
        return len(self._basis)

    def predict(self, context, action):
        mask, result = features(context, action), 0
        for pivot in sorted(self._basis, reverse=True):
            left, rhs = self._basis[pivot]
            if (mask >> pivot) & 1:
                mask ^= left
                result ^= rhs
        return result if mask == 0 else None


class NativeInterventionRepair:
    """Frozen warm outcome model + contradiction-triggered repair checkpoint."""
    __slots__ = ("_raw", "_checkpoint", "_old", "_new")

    def __init__(self, checkpoint_raw, expected_sha256):
        _verify_pinned(checkpoint_raw, expected_sha256, "NKR11_CHECKPOINT")
        doc = _parse(checkpoint_raw)
        if (set(doc) != {"schema", "source_mode", "source_kind",
                         "warm_id", "warm_sha256", "warm_records",
                         "repair_id", "repair_sha256", "repair_records",
                         "contradiction_ref", "scientific_pass",
                         "accepted_native"}
                or doc["schema"] != SCHEMA
                or doc["source_mode"] != SOURCE_MODE
                or doc["source_kind"] != SOURCE_KIND
                or doc["scientific_pass"] is not False
                or doc["accepted_native"] is not False):
            raise ValueError("NKR11_CHECKPOINT_SCHEMA_OR_ACCEPTANCE")
        if (type(doc["warm_id"]) is not str
                or not re.fullmatch(r"[a-z][a-z0-9:_-]{4,79}", doc["warm_id"])
                or type(doc["warm_sha256"]) is not str
                or not re.fullmatch(r"[0-9a-f]{64}", doc["warm_sha256"])):
            raise ValueError("NKR11_WARM_ID_OR_SHA_INVALID")
        old_records = _records(doc["warm_records"], expected=32)
        if {(x, a) for _, x, a, _ in old_records} != {
                (x, a) for x in range(16) for a in (0, 1)}:
            raise ValueError("NKR11_WARM_COVERAGE_INCOMPLETE")
        old = IntegerCausalSignature(old_records)
        if old.rank != FEATURE_COUNT:
            raise ValueError("NKR11_WARM_SIGNATURE_NOT_IDENTIFIABLE")
        repair = doc["repair_records"]
        if repair:
            if (not isinstance(doc["repair_id"], str)
                    or not re.fullmatch(r"[a-z][a-z0-9:_-]{4,79}", doc["repair_id"])
                    or type(doc["repair_sha256"]) is not str
                    or not re.fullmatch(r"[0-9a-f]{64}", doc["repair_sha256"])):
                raise ValueError("NKR11_REPAIR_ID_OR_SHA_INVALID")
            records = _records(repair)
            if (records[0][0] != doc["contradiction_ref"]
                    or old.predict(records[0][1], records[0][2])
                    == records[0][3]):
                raise ValueError("NKR11_REPAIR_NOT_CONTRADICTION_GATED")
            if {r[0] for r in records} & {r[0] for r in old_records}:
                raise ValueError("NKR11_SOURCE_REF_REBOUND")
            new = IntegerCausalSignature(records)
        else:
            if (doc["repair_id"] is not None or doc["repair_sha256"] is not None
                    or doc["contradiction_ref"] is not None):
                raise ValueError("NKR11_PHANTOM_REPAIR_RECEIPT")
            new = None
        self._raw = checkpoint_raw
        self._checkpoint = doc
        self._old = old
        self._new = new

    @classmethod
    def from_warmup(cls, source_bundle, expected_sha256):
        ident, events = _bundle(source_bundle, expected_sha256, expected=32)
        model = IntegerCausalSignature(events)
        if model.rank != FEATURE_COUNT:
            raise ValueError("NKR11_WARMUP_INSUFFICIENT_FEATURE_COVERAGE")
        raw = canonical({
            "schema": SCHEMA, "source_mode": SOURCE_MODE,
            "source_kind": SOURCE_KIND,
            "warm_id": ident, "warm_sha256": expected_sha256,
            "warm_records": [list(x) for x in events],
            "repair_id": None, "repair_sha256": None,
            "repair_records": [], "contradiction_ref": None,
            "scientific_pass": False, "accepted_native": False,
        })
        return cls(raw, digest(raw))

    @property
    def checkpoint_sha256(self):
        return digest(self._raw)

    def checkpoint(self):
        return self._raw

    @property
    def change_detected(self):
        return self._new is not None

    @property
    def new_rank(self):
        return 0 if self._new is None else self._new.rank

    def prior(self, context, action):
        return self._old.predict(context, action)

    def predict(self, context, action):
        if self._new is None:
            return {"classification": "WARM_PRIOR_ONLY",
                    "public_outcome": self._old.predict(context, action),
                    "native_accepted": False, "scientific_pass": False}
        predicted = self._new.predict(context, action)
        return {"classification": (
                "UNVERIFIED_NEW_RELATION_OUTCOME" if predicted is not None
                else "UNKNOWN_ABSTAIN"),
                "public_outcome": predicted, "signature_rank": self._new.rank,
                "context_relation_family": "10_FEATURE_GF2_PARITY",
                "checkpoint_sha256": self.checkpoint_sha256,
                "verified_new_world_fact": False,
                "can_write_historical_facts": False,
                "can_write_causal_owner": False,
                "native_accepted": False, "scientific_pass": False}

    def stage_public_interventions(self, raw, expected_sha256):
        ident, events = _bundle(raw, expected_sha256)
        if self._new is not None:
            if ident == self._checkpoint["repair_id"]:
                if self._checkpoint["repair_sha256"] != expected_sha256:
                    raise ValueError("NKR11_SOURCE_ID_REBOUND")
                # Do not replay unknown-effect updates or mutate checkpoints.
                return self, {"classification": "DUPLICATE_NO_EFFECT",
                              "new_events": 0, "scientific_pass": False}
            raise PermissionError("NKR11_SINGLE_FROZEN_REPAIR_EPOCH_ONLY")
        if ident == self._checkpoint["warm_id"]:
            raise ValueError("NKR11_SOURCE_ID_REBOUND")
        if {x[0] for x in events} & {
                x[0] for x in self._checkpoint["warm_records"]}:
            raise ValueError("NKR11_PUBLIC_SOURCE_REF_REPLAY")
        first = events[0]
        if self._old.predict(first[1], first[2]) == first[3]:
            return self, {"classification": "NO_FIRST_PUBLIC_CONTRADICTION_NO_CHANGE",
                          "new_events": 0, "scientific_pass": False}
        # Conflicting or noisy followup evidence fails CLOSED for this
        # deterministic exact-mechanism fixture; not deployed as a noisy
        # real-world causal change detector.
        new = IntegerCausalSignature(events)
        candidate = dict(self._checkpoint)
        candidate["repair_id"] = ident
        candidate["repair_sha256"] = expected_sha256
        candidate["repair_records"] = [list(x) for x in events]
        candidate["contradiction_ref"] = first[0]
        packed = canonical(candidate)
        staged = NativeInterventionRepair(packed, digest(packed))
        return staged, {
            "classification": "FIXTURE_CONTRADICTION_GATED_NEW_RELATION_CANDIDATE",
            "new_events": len(events), "first_contradiction_ref": first[0],
            "old_checkpoint_sha256": self.checkpoint_sha256,
            "new_checkpoint_sha256": staged.checkpoint_sha256,
            "new_signature_rank": new.rank, "native_accepted": False,
            "scientific_pass": False,
        }
