"""NKR-13 bounded native operator proposal from public interventions.

This is a separate research overlay, never a change to accepted DG-1 or YPC1.
Input-derived conjunction candidates extend NKR-11's fixed parity family,
but the proposed grammar is still prespecified, not de novo free-form thought.

Inputs are canonical SHA-pinned *synthetic* public observations. SHA-256
certifies byte integrity, not evidence authenticity.
"""
from __future__ import annotations

from yggdrasil.native_intervention_repair import (
    NativeInterventionRepair, _bundle, _parse, _verify_pinned,
    BUNDLE_SCHEMA, SOURCE_MODE, SOURCE_KIND, canonical, digest,
)

SCHEMA = "yggdrasil.nkr13.operator-proposal-checkpoint.v1"
TRAIN_CONTEXTS = (0, 1, 2, 4, 8, 3, 5, 10)
REPAIR_ACTIONS = ((0, 1), (0, 0)) + tuple(
    (x, a) for x in TRAIN_CONTEXTS[1:] for a in (0, 1))
OPERATOR_MASKS = tuple(range(1, 16))   # generated from 4 context bits
MIN_CHANGE_WITNESSES = 2
MAX_CHECKPOINT_BYTES = 65536


def _source_bundle(source_id, events):
    return canonical({
        "schema": BUNDLE_SCHEMA,
        "source_id": source_id,
        "source_mode": SOURCE_MODE,
        "source_kind": SOURCE_KIND,
        "records": [list(e) for e in events],
    })


def _fit_candidate(old, rows):
    """Learn parity baseline and propose conjunctions from PUBLIC evidence.

    Returns None when data are unsupported/unidentified. Does not ingest or
    query *any* source-hidden x/action test consequences. The prior is used
    only for public contradiction counts.
    """
    if len(rows) != 16 or tuple((x, a) for _, x, a, _ in rows) != REPAIR_ACTIONS:
        raise ValueError("NKR13_FROZEN_ACTION_SEQUENCE_CHANGED")
    disagreements = sum(old.prior(x, a) != outcome
                        for _, x, a, outcome in rows)
    if disagreements < MIN_CHANGE_WITNESSES:
        return None, "INSUFFICIENT_CHANGE_EVIDENCE"
    observed = {(x, a): value for _, x, a, value in rows}
    intercept = observed[(0, 0)]
    base_mask = sum(
        1 << bit for bit in range(4)
        if observed[(1 << bit, 0)] != intercept)
    if any(
        observed[(x, 0)] != (intercept ^ ((x & base_mask).bit_count() & 1))
        for x in TRAIN_CONTEXTS
    ):
        return None, "UNSUPPORTED_CONTEXT_BASE_ABSTAIN"
    # Derive candidate operators solely from the observed action effect;
    # do not transfer exact source-hidden AND masks from the environment.
    possible = [
        mask for mask in OPERATOR_MASKS
        if all(
            (observed[(x, 1)] ^ observed[(x, 0)])
            == int((x & mask) == mask)
            for x in TRAIN_CONTEXTS)
    ]
    if not possible:
        return None, "NO_SUPPORTED_NEW_OPERATOR_ABSTAIN"
    return {
        "intercept": intercept, "base_mask": base_mask,
        "candidate_masks": possible, "contradictions": disagreements,
    }, "SOURCE_SUPPORTED_OPERATOR_PROPOSAL"


class NativeOperatorDiscovery:
    """Immutable old checkpoint + distinct post-contradiction operator pool."""
    __slots__ = ("_old", "_raw", "_doc")

    def __init__(self, checkpoint, expected_sha256):
        _verify_pinned(checkpoint, expected_sha256, "NKR13_CHECKPOINT")
        data = _parse(checkpoint, max_size=MAX_CHECKPOINT_BYTES)
        required = {
            "schema", "warm_checkpoint", "warm_sha256", "repair",
            "scientific_pass", "accepted_native", "mode",
        }
        if (set(data) != required or data["schema"] != SCHEMA
                or data["scientific_pass"] is not False
                or data["accepted_native"] is not False
                or data["mode"] != "engineering_fixture_only"
                or type(data["warm_checkpoint"]) is not dict):
            raise ValueError("NKR13_CHECKPOINT_CONTRACT_DRIFT")
        old = NativeInterventionRepair(
            canonical(data["warm_checkpoint"]), data["warm_sha256"])
        if old.change_detected:
            raise ValueError("NKR13_WARM_CHECKPOINT_ALREADY_REPAIRED")
        if data["repair"] is not None:
            repair = data["repair"]
            if (type(repair) is not dict
                    or set(repair) != {"source_id", "sha256", "records",
                                      "proposal"}):
                raise ValueError("NKR13_REPAIR_CHECKPOINT_SCHEMA")
            source = _source_bundle(repair["source_id"], repair["records"])
            if digest(source) != repair["sha256"]:
                raise ValueError("NKR13_REPAIR_PUBLIC_SOURCE_DRIFT")
            ident, rows = _bundle(source, repair["sha256"], expected=16)
            if ident == data["warm_checkpoint"]["warm_id"]:
                raise ValueError("NKR13_WARM_REPAIR_SOURCE_REBOUND")
            warm_refs = {r[0] for r in data["warm_checkpoint"]["warm_records"]}
            if any(r[0] in warm_refs for r in rows):
                raise ValueError("NKR13_WARM_REPAIR_ROW_REPLAY")
            recalculated, _ = _fit_candidate(old, rows)
            if recalculated is None or recalculated != repair["proposal"]:
                raise ValueError("NKR13_REPAIR_PROPOSAL_RECONSTRUCTION_DRIFT")
        self._old = old
        self._doc = data
        self._raw = checkpoint

    @classmethod
    def from_warmup(cls, warm_public_source, sha256):
        old = NativeInterventionRepair.from_warmup(
            warm_public_source, sha256)
        return cls(canonical({
            "schema": SCHEMA,
            "warm_checkpoint": _parse(old.checkpoint()),
            "warm_sha256": old.checkpoint_sha256,
            "repair": None,
            "mode": "engineering_fixture_only",
            "accepted_native": False, "scientific_pass": False,
        }), digest(canonical({
            "schema": SCHEMA,
            "warm_checkpoint": _parse(old.checkpoint()),
            "warm_sha256": old.checkpoint_sha256,
            "repair": None,
            "mode": "engineering_fixture_only",
            "accepted_native": False, "scientific_pass": False,
        })))

    @property
    def checkpoint_sha256(self):
        return digest(self._raw)

    def checkpoint(self):
        return self._raw

    @property
    def operator_discovered(self):
        return self._doc["repair"] is not None

    @property
    def operator_masks(self):
        return () if not self.operator_discovered else tuple(
            self._doc["repair"]["proposal"]["candidate_masks"])

    def prior(self, x, action):
        return self._old.prior(x, action)

    def predict(self, x, action):
        # Input validated by existing native causal feature validator.
        self._old.prior(x, action)
        if not self.operator_discovered:
            return {
                "classification": "WARM_PRIOR_ONLY",
                "public_outcome": self._old.prior(x, action),
                "native_accepted": False,
                "scientific_pass": False,
                "can_write_causal_owner": False,
                "can_write_historical_facts": False,
            }
        proposal = self._doc["repair"]["proposal"]
        base = proposal["intercept"] ^ (
            (x & proposal["base_mask"]).bit_count() & 1)
        if action == 0:
            values = {base}
        else:
            values = {
                base ^ int((x & mask) == mask)
                for mask in proposal["candidate_masks"]
            }
        inferred = next(iter(values)) if len(values) == 1 else None
        return {
            "classification": (
                "UNVERIFIED_CONJUNCTION_OPERATOR_HYPOTHESIS"
                if inferred is not None else "UNKNOWN_ABSTAIN"),
            "public_outcome": inferred,
            "possible_operators": len(self.operator_masks),
            "operator_family": "CONJUNCTION_FROM_INPUT_BITS_GENERATOR_V1",
            "hypothesis_class_prespecified": True,
            "verified_new_world_fact": False,
            "native_accepted": False,
            "scientific_pass": False,
            "can_write_causal_owner": False,
            "can_write_historical_facts": False,
        }

    def stage_public_interventions(self, raw, sha256):
        ident, rows = _bundle(raw, sha256, expected=16)
        prior = self._doc["warm_checkpoint"]
        if ident == prior["warm_id"]:
            raise ValueError("NKR13_FEEDBACK_REUSES_WARM_SOURCE")
        warm_refs = {r[0] for r in prior["warm_records"]}
        if any(r[0] in warm_refs for r in rows):
            raise ValueError("NKR13_FEEDBACK_REF_REPLAY")
        if self.operator_discovered:
            existing = self._doc["repair"]
            if ident == existing["source_id"]:
                if sha256 != existing["sha256"]:
                    raise ValueError("NKR13_REPAIR_SOURCE_REBOUND")
                return self, {
                    "classification": "DUPLICATE_SOURCE_NO_EFFECT",
                    "new_events": 0, "scientific_pass": False}
            raise PermissionError("NKR13_SINGLE_REPAIR_EPOCH_ONLY")
        candidate, status = _fit_candidate(self._old, rows)
        if candidate is None:
            return self, {
                "classification": status, "new_events": 0,
                "repaired": False, "scientific_pass": False,
                "native_accepted": False,
            }
        updated = dict(self._doc)
        updated["repair"] = {
            "source_id": ident, "sha256": sha256,
            "records": [list(row) for row in rows],
            "proposal": candidate,
        }
        encoded = canonical(updated)
        successor = NativeOperatorDiscovery(encoded, digest(encoded))
        return successor, {
            "classification": status,
            "new_events": len(rows), "repaired": True,
            "candidate_operators": len(successor.operator_masks),
            "prior_checkpoint_sha256": self.checkpoint_sha256,
            "new_checkpoint_sha256": successor.checkpoint_sha256,
            "native_accepted": False, "scientific_pass": False,
        }
