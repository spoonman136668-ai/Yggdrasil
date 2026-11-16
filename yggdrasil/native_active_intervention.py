"""NKR-16: immutable, source-bound selection of informative interventions.

A bounded research-only information-acquisition substrate. Neither the
policies nor this module can access a simulator's hidden operator or any
source-hidden counterfactual. All sources are synthetic fixture observations.

IMPORTANT: a directly measured action result is NOT a generalized cold
prediction. Four unrestricted probes reveal four bits, no more.
"""
from __future__ import annotations

import hashlib
import math

from yggdrasil.native_intervention_repair import (
    _bundle, _parse, _verify_pinned, canonical, digest,
    BUNDLE_SCHEMA, SOURCE_KIND, SOURCE_MODE,
)
from yggdrasil.native_operator_discovery import REPAIR_ACTIONS

SCHEMA = "yggdrasil.nkr16.source-bound-active-intervention.v1"
COLD = (6, 7, 9, 11, 12, 13, 14, 15)
TRAIN = (0, 1, 2, 4, 8, 3, 5, 10)
MASKS = tuple(range(1, 16))
BUDGETS = {"unrestricted": 4, "structured": 2}
POLICIES = ("active", "random")
SEED = b"nkr16:random:seed=20261116"
MAX_SIZE = 65536


def source_bundle(source_id, rows):
    """Canonically attest fixture-source bytes, not external authenticity."""
    return canonical({
        "schema": BUNDLE_SCHEMA, "source_id": source_id,
        "source_kind": SOURCE_KIND, "source_mode": SOURCE_MODE,
        "records": [list(row) for row in rows],
    })


def _fit(initial, acquired, mode):
    """Return public baseline and candidate effects, never source-hidden data."""
    if tuple((x, a) for _, x, a, _ in initial) != REPAIR_ACTIONS:
        raise ValueError("NKR16_INITIAL_ACTION_SEQUENCE_DRIFT")
    seen = {(x, a): y for _, x, a, y in initial}
    baseline = seen[(0, 0)]
    mask = 0
    for bit in range(4):
        if seen[(1 << bit, 0)] ^ baseline:
            mask |= 1 << bit
    if any(seen[(x, 0)] !=
           (baseline ^ ((x & mask).bit_count() & 1)) for x in TRAIN):
        raise ValueError("NKR16_SOURCE_PARITY_BASELINE_DRIFT")
    initial_effects = {
        x: seen[(x, 1)] ^ seen[(x, 0)] for x in TRAIN
    }
    observed = dict(initial_effects)
    for _, x, action, y in acquired:
        if x not in COLD or action != 1 or x in observed:
            raise ValueError("NKR16_NEW_SOURCE_NOT_A_FRESH_INTERVENTION")
        inferred_baseline = baseline ^ ((x & mask).bit_count() & 1)
        observed[x] = y ^ inferred_baseline
    if mode == "unrestricted":
        candidates = ()
        versions = 1 << (16 - len(observed))
    elif mode == "structured":
        candidates = tuple(m for m in MASKS if all(
            int((x & m) == m) == effect
            for x, effect in observed.items()))
        if not candidates:
            raise ValueError("NKR16_CONJUNCTION_CANDIDATES_EXHAUSTED")
        versions = len(candidates)
    else:
        raise ValueError("NKR16_UNKNOWN_HYPOTHESIS_FAMILY")
    return baseline, mask, observed, candidates, versions


def _select(mode, policy, original_sha, acquired, candidates):
    used = {x for _, x, _, _ in acquired}
    remaining = [x for x in COLD if x not in used]
    if not remaining or len(acquired) >= BUDGETS[mode]:
        return None
    if policy == "random":
        seed = hashlib.sha256(
            SEED + b":" + original_sha.encode("ascii") +
            b":" + str(len(acquired)).encode("ascii")
        ).digest()
        return remaining[int.from_bytes(seed[:8], "big") % len(remaining)]
    if mode == "unrestricted":
        # Every unmeasured effect bit has identical entropy, H=1.
        return remaining[0]
    # With N equally likely explicit candidate operators, maximizing
    # n0*n1 is equivalent to maximizing exact binary entropy; no floating
    # point ordering or world IDs enter the selection decision.
    return min(remaining, key=lambda x: (
        -(sum(int((x & m) == m) for m in candidates) *
          sum(int((x & m) != m) for m in candidates)),
        x))


def _entropy(mode, candidates, context):
    if context is None:
        return 0.0
    if mode == "unrestricted":
        return 1.0
    p = sum(int((context & m) == m) for m in candidates) / len(candidates)
    if p in (0.0, 1.0):
        return 0.0
    return -p * math.log2(p) - (1 - p) * math.log2(1 - p)


class NativeActiveIntervention:
    """One immutable plan + pinned selected outcomes, no accepted model edits."""
    __slots__ = ("_raw", "_doc", "_initial", "_acquired",
                 "_baseline", "_mask", "_observed", "_candidates", "_versions")

    def __init__(self, raw, expected_sha256):
        _verify_pinned(raw, expected_sha256, "NKR16_CHECKPOINT")
        doc = _parse(raw, max_size=MAX_SIZE)
        if (set(doc) != {"schema", "source_id", "source_sha256",
                         "initial_records", "mode", "policy", "receipts",
                         "source_mode", "scientific_pass", "native_accepted"}
                or doc["schema"] != SCHEMA
                or doc["source_mode"] != SOURCE_MODE
                or doc["scientific_pass"] is not False
                or doc["native_accepted"] is not False
                or doc["mode"] not in BUDGETS
                or doc["policy"] not in POLICIES):
            raise ValueError("NKR16_CHECKPOINT_CONTRACT_INVALID")
        base_source = source_bundle(doc["source_id"], doc["initial_records"])
        ident, initial = _bundle(base_source, doc["source_sha256"], expected=16)
        if ident != doc["source_id"] or type(doc["receipts"]) is not list:
            raise ValueError("NKR16_BASE_SOURCE_ID_OR_RECEIPTS_INVALID")
        if len(doc["receipts"]) > BUDGETS[doc["mode"]]:
            raise ValueError("NKR16_ACTION_BUDGET_EXCEEDED")
        _, _, _, candidates, _ = _fit(initial, (), doc["mode"])
        gathered = []
        seen_ids = {ident}
        seen_refs = {ref for ref, _, _, _ in initial}
        for receipt in doc["receipts"]:
            if type(receipt) is not dict or set(receipt) != {
                    "source_id", "source_sha256", "records"}:
                raise ValueError("NKR16_RECEIPT_SCHEMA")
            body = source_bundle(receipt["source_id"], receipt["records"])
            sample_id, rows = _bundle(body, receipt["source_sha256"], expected=1)
            if sample_id in seen_ids:
                raise ValueError("NKR16_DUPLICATE_PUBLIC_SOURCE")
            seen_ids.add(sample_id)
            if any(ref in seen_refs for ref, _, _, _ in rows):
                raise ValueError("NKR16_PUBLIC_EVENT_REPLAY")
            seen_refs.update(ref for ref, _, _, _ in rows)
            expected_x = _select(doc["mode"], doc["policy"],
                                 doc["source_sha256"], gathered, candidates)
            if (expected_x is None or rows[0][1] != expected_x
                    or rows[0][2] != 1):
                raise ValueError("NKR16_SELECTED_ACTION_MISMATCH")
            gathered.extend(rows)
            _, _, _, candidates, _ = _fit(initial, gathered, doc["mode"])
        self._baseline, self._mask, self._observed, self._candidates, self._versions = (
            _fit(initial, gathered, doc["mode"]))
        self._raw, self._doc = raw, doc
        self._initial, self._acquired = initial, tuple(gathered)

    @classmethod
    def from_initial_public_source(cls, raw, expected_sha256, *,
                                   mode, policy):
        source_id, records = _bundle(raw, expected_sha256, expected=16)
        doc = {
            "schema": SCHEMA, "source_id": source_id,
            "source_sha256": expected_sha256,
            "initial_records": [list(x) for x in records],
            "mode": mode, "policy": policy,
            "receipts": [], "source_mode": SOURCE_MODE,
            "scientific_pass": False, "native_accepted": False,
        }
        packed = canonical(doc)
        return cls(packed, digest(packed))

    @property
    def checkpoint_sha256(self):
        return digest(self._raw)

    def checkpoint(self):
        return self._raw

    @property
    def candidate_count(self):
        return self._versions

    @property
    def additional_public_actions(self):
        return len(self._acquired)

    @property
    def operator_candidates(self):
        return self._candidates

    def select_next_action(self):
        context = _select(self._doc["mode"], self._doc["policy"],
                          self._doc["source_sha256"],
                          self._acquired, self._candidates)
        if context is None:
            return None
        return {
            "context": context, "action": 1,
            "expected_information_gain_bits": _entropy(
                self._doc["mode"], self._candidates, context),
            "hypothesis_family": self._doc["mode"],
            "policy": self._doc["policy"],
            "current_hypotheses": self._versions,
            "observations_used": len(self._acquired),
            "verified_new_world_fact": False,
            "native_accepted": False, "scientific_pass": False,
        }

    def observe_selected_public_action(self, source_raw, source_sha256):
        ident, rows = _bundle(source_raw, source_sha256, expected=1)
        choice = self.select_next_action()
        if choice is None:
            raise PermissionError("NKR16_NO_ADDITIONAL_ACTION_AUTHORIZED")
        if (rows[0][1], rows[0][2]) != (
                choice["context"], choice["action"]):
            raise ValueError("NKR16_FEEDBACK_NOT_SELECTED_ACTION")
        if ident == self._doc["source_id"] or any(
                r["source_id"] == ident for r in self._doc["receipts"]):
            raise ValueError("NKR16_REPLAYED_SOURCE_ID")
        if rows[0][0] in {x[0] for x in self._initial + self._acquired}:
            raise ValueError("NKR16_REPLAYED_PUBLIC_REF")
        doc = dict(self._doc)
        doc["receipts"] = self._doc["receipts"] + [{
            "source_id": ident, "source_sha256": source_sha256,
            "records": [list(r) for r in rows],
        }]
        packed = canonical(doc)
        new = NativeActiveIntervention(packed, digest(packed))
        return new, {
            "classification": "SOURCE_PINNED_SELECTED_PUBLIC_ACTION",
            "observed_outcome": rows[0][3],
            "choice": [choice["context"], 1],
            "source_sha256": source_sha256,
            "old_checkpoint_sha256": self.checkpoint_sha256,
            "new_checkpoint_sha256": new.checkpoint_sha256,
            "remaining_hypotheses": new.candidate_count,
            "scientific_pass": False, "native_accepted": False,
        }

    def predict(self, context, action):
        if type(context) is not int or not 0 <= context < 16:
            raise ValueError("NKR16_CONTEXT_OUT_OF_DOMAIN")
        if type(action) is not int or action not in (0, 1):
            raise ValueError("NKR16_ACTION_OUT_OF_DOMAIN")
        baseline = self._baseline ^ ((context & self._mask).bit_count() & 1)
        if action == 0:
            value = baseline
            kind = "UNVERIFIED_ACTION_ZERO_PARITY_PRIOR"
        elif context in self._observed:
            value = baseline ^ self._observed[context]
            kind = "DIRECTLY_OBSERVED_ACTION_OUTCOME"
        elif self._doc["mode"] == "structured":
            possible = {
                baseline ^ int((context & m) == m)
                for m in self._candidates
            }
            value = next(iter(possible)) if len(possible) == 1 else None
            kind = ("UNVERIFIED_CONJUNCTION_FAMILY_PREDICTION"
                    if value is not None else "UNKNOWN_ABSTAIN")
        else:
            value = None
            kind = "UNKNOWN_ARBITRARY_BOOLEAN_EFFECT"
        return {
            "classification": kind, "public_outcome": value,
            "hypothesis_family": self._doc["mode"],
            "family_is_prespecified": True,
            "verified_new_world_fact": False,
            "can_write_causal_owner": False,
            "can_write_historical_facts": False,
            "scientific_pass": False, "native_accepted": False,
        }
