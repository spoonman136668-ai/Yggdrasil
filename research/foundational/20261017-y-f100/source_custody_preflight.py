"""F100 P2: read-only CKB source-custody preflight, NEVER first-use admission.

The input policy is externally fetched at a *pinned* immutable CKB commit and
verified as an exact Git blob. An R187 discovery policy is NOT an authenticated
content-birth witness or complete consumption ledger, even if its flags say yes.
No synthetic source generation, candidate ranking, experiment, queue or runner.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

CKB_MAIN_SNAPSHOT = "fab36e7c488f930505fcbaeb5f5bf04806e50c5b"
CKB_POLICY_PATH = ".github/research-audit/r187-source-pool.json"
CKB_POLICY_BLOB = "8a8afd6d7be7b8d5cd183519bb9e642b307ba168"
CKB_POLICY_SCHEMA = "ckb-plane.prospective-source-discovery-policy.r187"
CKB_POLICY_STATE = "PROSPECTIVELY_DECLARED_PREFREEZE_NOT_SCIENCE_ADMITTED"
CKB_EPOCH = "2026-10-08T22:06:37Z"
F100_FROZEN_R2_COMMIT = "17e27350e295a47fb224d69c237c802c9997861c"
F100_QUALIFIED_SOURCE_HEAD = "cdd5d904d8a6ebae4e3d1d2762cbd26217624866"
F100_QUALIFIER_RUN = 39015811146
F100_SOURCE_BLOB = "14066ad4f36e09e77134e7d5e192fcacf94b5810"
POLICY_BYTES_MAX = 16384
FLAGS = (
    "global_historical_source_ledger_complete",
    "prospective_input_independence_established",
    "frozen_experiment",
    "ready_research",
    "dispatch",
    "accepted_ref_mutation",
)
AUTH_REQUIRED = (
    "independent_content_birth_witness",
    "complete_cross_lane_exclusion_ledger",
    "independent_f100_train_validation_guard_admission",
    "ckb_first_use_exclusive_science_authorization",
)


class PreflightBlocked(ValueError):
    pass


def git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode()
                        + b"\0" + raw).hexdigest()


def policy_from_pinned_bytes(raw: bytes) -> dict:
    if type(raw) is not bytes or not 0 < len(raw) <= POLICY_BYTES_MAX:
        raise PreflightBlocked("F100_CKB_POLICY_SIZE_OR_TYPE")
    if git_blob_sha(raw) != CKB_POLICY_BLOB:
        raise PreflightBlocked("F100_CKB_POLICY_GIT_OBJECT_DRIFT")
    try:
        policy = json.loads(raw)
    except (UnicodeDecodeError, ValueError) as exc:
        raise PreflightBlocked("F100_CKB_POLICY_UNPARSEABLE") from exc
    return assess_policy(policy)


def assess_policy(policy: dict) -> dict:
    """Read-only triage, NEVER convert descriptive assertions to admission."""
    if type(policy) is not dict:
        raise PreflightBlocked("F100_CKB_POLICY_NOT_OBJECT")
    if policy.get("schema") != CKB_POLICY_SCHEMA or \
            policy.get("policy_state") != CKB_POLICY_STATE or \
            policy.get("birth_cutoff_utc") != CKB_EPOCH:
        raise PreflightBlocked("F100_CKB_POLICY_SCHEMA_OR_EPOCH_DRIFT")
    for key in FLAGS:
        if type(policy.get(key)) is not bool:
            raise PreflightBlocked("F100_CKB_POLICY_FLAG_MISSING_OR_BAD:" + key)
    if any(policy[key] is True for key in ("ready_research", "dispatch",
                                           "accepted_ref_mutation")):
        raise PreflightBlocked("F100_CKB_POLICY_AUTHORITY_CONTRADICTION")
    if policy.get("selection_excludes_unseen_outcomes") is not True or \
            policy.get("scope") != (
            "publicly-available immutable GitHub source-file discovery; "
            "new filename does not prove independently new content"):
        raise PreflightBlocked("F100_CKB_SOURCE_DISCOVERY_NOT_BIRTH")
    repos = policy.get("approved_public_repositories")
    budgets = policy.get("source_prefix_budgets")
    if type(repos) is not list or not repos or len(repos) != len(set(repos)) or \
            not all(isinstance(x, str) and re.fullmatch(
                r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", x) for x in repos) or \
            type(budgets) is not dict or budgets != {
                "code": 41453, "structured": 14365, "technical_prose": 1454
            }:
        raise PreflightBlocked("F100_CKB_SOURCE_POLICY_SCOPE_OR_BUDGET_DRIFT")
    unavailable = [
        "incomplete_cross_lane_historical_exclusion_ledger"
        if not policy["global_historical_source_ledger_complete"] else None,
        "prospective_content_origin_not_independent"
        if not policy["prospective_input_independence_established"] else None,
        "F100_FIRST_USE_WITNESS_ABSENT_FROM_CKB_SOURCE_DISCOVERY_POLICY",
        "NO_F100_CKB_SCIENTIFIC_ADMISSION_OR_ONESHOT_FIRST_USE",
    ]
    return dict(
        schema="yggdrasil.f100.ckb-source-custody-preflight.v1",
        stage="READ_ONLY_PINNED_POLICY_TRIAGE_NOT_SCIENTIFIC_ADMISSION",
        classification="F100_SOURCE_CUSTODY_NOT_QUALIFIED",
        source_repository="spoonman136668-ai/ckb-plane",
        frozen_ckb_main_snapshot=CKB_MAIN_SNAPSHOT,
        ckb_source_policy_path=CKB_POLICY_PATH,
        ckb_source_policy_git_blob=CKB_POLICY_BLOB,
        ckb_birth_cutoff=CKB_EPOCH,
        frozen_f100_r2_prereg_commit=F100_FROZEN_R2_COMMIT,
        frozen_f100_source_qualification_head=F100_QUALIFIED_SOURCE_HEAD,
        f100_source_qualification_run=F100_QUALIFIER_RUN,
        f100_source_blob=F100_SOURCE_BLOB,
        observed_source_policy_flags={k: policy[k] for k in FLAGS},
        missing_or_not_qualified=[x for x in unavailable if x],
        still_requires_independent_authority=list(AUTH_REQUIRED),
        approved_f100_train_graphs=0,
        approved_f100_validation_graphs=0,
        approved_f100_guard_graphs=0,
        source_first_use_allowed=False,
        prospective_experiment_dispatched=False,
        prospective_outcomes_accessed=False,
        protected_cohorts_accessed=False,
        scientifically_accepted=False,
        optimizer_promoted=False,
        CKB_controller_mutated=False,
        accepted_ref_mutated=False,
        Codex_invoked=False,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pinned-ckb-policy", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or not args.output.parent.is_dir():
        raise PreflightBlocked("F100_OUTPUT_EXISTS_OR_PARENT_MISSING")
    source = args.pinned_ckb_policy
    if not source.is_file() or source.stat().st_size > POLICY_BYTES_MAX:
        raise PreflightBlocked("F100_NO_PINNED_CKB_POLICY")
    result = policy_from_pinned_bytes(source.read_bytes())
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n",
                           encoding="utf-8")
    print("F100_P2_SOURCE_CUSTODY_CLASSIFICATION="
          + result["classification"])
    print("F100_P2_FIRST_USE_AUTHORIZED=FALSE")


if __name__ == "__main__":
    main()
