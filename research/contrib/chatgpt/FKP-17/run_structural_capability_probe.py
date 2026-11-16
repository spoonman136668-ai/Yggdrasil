"""Execute only public-FOUNDATION frozen STRUCTURED capability proof.

No protected-source evaluator, held seed, learning method update, native
Yggdrasil integration or scheduled job. Does not call original DEV/TRANSFER.
"""
from __future__ import annotations

import json
import os
import time

import public_policies
import source_fixture
import strong_controls
import structural_capability_probe as probe


def execute_public_constructive_proof():
    source_sha = os.environ.get("FKP17_SOURCE_SHA", "")
    if len(source_sha) != 40 or any(ch not in "0123456789abcdef" for ch in source_sha):
        raise ValueError("FKP17_CAPABILITY_SOURCE_NOT_PINNED")
    started = time.perf_counter()
    rows = tuple(record for _, _, record in source_fixture.foundation_facts())
    if len(rows) != 32768:
        raise AssertionError("FKP17_CAPABILITY_FOUNDATION_NOT_COMPLETE")
    structured = public_policies.PublicRelationArm(
        "STRUCTURED").fit_public_foundation(rows)
    symbolic = strong_controls.SymbolicBayes().fit_public_foundation(rows)
    result = probe.audit_frozen_public_arms(structured, symbolic)
    result["source_commit_original"] = source_sha
    result["source_safe_foundation_records"] = len(rows)
    result["model_parameter_bytes"] = {
        "STRUCTURED": structured.learned_bytes,
        "BAYES_SYMBOLIC": symbolic.memory_bytes,
    }
    result["development_falsification_wall_seconds"] = (
        time.perf_counter() - started)
    if not all((result["candidate_same_complete_state_after_distinct_conditional_laws"],
                result["candidate_same_complete_state_after_reordered_events"],
                result["independent_conditional_symbolic_control_distinguishes"])):
        raise AssertionError("FKP17_CAPABILITY_REQUIRED_COUNTEREXAMPLE_MISSING")
    try:
        probe.require_unfamiliar_law_representational_readiness(result)
    except ValueError as exc:
        if str(exc) != "FKP17_STRUCTURED_DELAYED_CONTEXT_REPRESENTATION_NO_GO":
            raise
        result["frozen_representation_readiness"] = "NO_GO"
    else:
        raise AssertionError("FKP17_CAPABILITY_FENCE_UNEXPECTEDLY_OPEN")
    return result


if __name__ == "__main__":
    record = execute_public_constructive_proof()
    print("FKP17_FROZEN_STRUCTURAL_REPRESENTATION_PROOF=" +
          json.dumps(record, sort_keys=True, separators=(",", ":")))
