"""NCI07 source-free parity/custody guard. Not a learner or world runner.

Pure engineering preflight: never produces actions, outcome labels, or hidden phase
identity. All arms are separately audited against the same public witness tape.
"""
from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence

SCHEMA = "yggdrasil.nci07.public-parity.v1"
PUBLIC_FIELDS = frozenset(("observation", "action", "outcome"))
PROHIBITED = frozenset(("phase", "source", "source_id", "regime", "reset", "oracle", "counterfactual"))


class AuditError(ValueError):
    """Fail-closed source-free engineering audit rejection."""


def canonical_public_tape(tape: Sequence[Mapping]) -> bytes:
    """Strict, phase-blind public witness serialization, with no hidden labels."""
    if type(tape) not in (list, tuple) or len(tape) == 0:
        raise AuditError("NCI07_PUBLIC_TAPE_EMPTY")
    rows = []
    for row in tape:
        if not isinstance(row, dict) or set(row) != PUBLIC_FIELDS:
            raise AuditError("NCI07_NONPUBLIC_FIELD_OR_MISSING_FIELD")
        obs, action, outcome = row["observation"], row["action"], row["outcome"]
        if type(obs) is not int or not 0 <= obs <= 255:
            raise AuditError("NCI07_OBSERVATION_INVALID")
        if type(action) is not int or action not in (0, 1):
            raise AuditError("NCI07_ACTION_INVALID")
        if type(outcome) is not int or outcome not in (0, 1):
            raise AuditError("NCI07_OUTCOME_INVALID")
        rows.append((obs, action, outcome))
    return json.dumps(rows, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def public_tape_digest(tape: Sequence[Mapping]) -> str:
    return hashlib.sha256(canonical_public_tape(tape)).hexdigest()


def assert_paired_evidence(arm_tapes: Mapping[str, Sequence[Mapping]],
                           expected_arms: Sequence[str],
                           *, max_witnesses: int) -> dict:
    """Confirm all models saw the same chronological public witnesses.

    Does not certify actions, truthful outcomes, source custody, training,
    or experimental equivalence beyond the supplied public tapes.
    """
    if (type(max_witnesses) is not int or max_witnesses <= 0 or
            type(expected_arms) not in (tuple, list) or
            len(expected_arms) == 0 or len(expected_arms) != len(set(expected_arms)) or
            any(type(x) is not str or not x for x in expected_arms) or
            not isinstance(arm_tapes, dict) or set(arm_tapes) != set(expected_arms)):
        raise AuditError("NCI07_ARM_CONTRACT_INVALID")
    digests = {}
    counts = {}
    for name in expected_arms:
        tape = arm_tapes[name]
        if len(tape) > max_witnesses:
            raise AuditError("NCI07_WITNESS_BUDGET_EXCEEDED")
        digests[name] = public_tape_digest(tape)
        counts[name] = len(tape)
    if len(set(digests.values())) != 1:
        raise AuditError("NCI07_UNMATCHED_PUBLIC_EVIDENCE")
    return {"schema": SCHEMA, "arms": list(expected_arms),
            "public_tape_sha256": next(iter(digests.values())),
            "witnesses_per_arm": next(iter(counts.values())),
            "source_custody_authenticated": False,
            "scientific_gain_verified": False}


def assert_cold_functional_retention(pre_b: Mapping[int, float],
                                     post_b_cold: Mapping[int, float],
                                     *, tolerance: float = 0.02) -> float:
    """Compare identical pre-return public queries across process restore.

    Snapshot byte integrity alone cannot demonstrate functional retention.
    This guard measures forecast drift, NOT verified true-law Brier.
    """
    if (type(tolerance) not in (float, int) or not 0 <= tolerance <= 1 or
            not isinstance(pre_b, dict) or not pre_b or
            not isinstance(post_b_cold, dict) or set(pre_b) != set(post_b_cold)):
        raise AuditError("NCI07_COLD_QUERY_SET_INVALID")
    diffs = []
    for k in pre_b:
        if type(k) is not int or not 0 <= k <= 255:
            raise AuditError("NCI07_COLD_CONTEXT_INVALID")
        a, b = pre_b[k], post_b_cold[k]
        if (type(a) not in (int, float) or type(b) not in (int, float) or
                not 0 <= a <= 1 or not 0 <= b <= 1):
            raise AuditError("NCI07_COLD_FORECAST_INVALID")
        diffs.append(abs(a - b))
    worst = max(diffs)
    if worst > tolerance:
        raise AuditError("NCI07_COLD_READOUT_DRIFT")
    return worst
