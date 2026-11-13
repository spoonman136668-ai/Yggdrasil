"""Read-only WSP80 prospective source custody; NOT scientific first-use authority.

Does not import/execute the registered source generator, evaluate a frozen seed,
create world sessions, or look at private physics. A static source fingerprint
can prove Git identity/order but CANNOT prove prior first-use disjointness.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess

REPO = Path(__file__).resolve().parents[4]
PRE_COMMIT = "3f9aeafd4a040473d7f77c626e62e6f4b6db61f7"
PARENT = "ccb3672c709528d6b7322f138f135385aed5fc07"
PARENT_TREE = "5e7376cfea981c1d76d2e6c3b39b520940090acb"
PINNED = {
    "research/contrib/chatgpt/WSP-80/prereg.json":
        "0e96f4e0eff1ced7f87b754a2ad4fbb75c7b3d58",
    "research/contrib/chatgpt/WSP-80/source.py":
        "c5d0ab0dcf38b2f2dec1e60d7d8346eb2c2697d2",
    "research/contrib/chatgpt/WSP-77/fully_trained_mlp6.py":
        "90bca703948c71e482892d2be830682201342368",
}


def _git(*args, check=True):
    result = subprocess.run(("git",) + args, cwd=REPO, check=check,
                            text=True, capture_output=True)
    return result.stdout.strip() if check else result


def validate_frozen_protocol(data):
    if (type(data) is not dict or data.get("experiment") != "WSP80"
            or data.get("status") !=
                "FROZEN_PROSPECTIVE_BEFORE_NEW_SOURCE_LEARNER_HARNESS_OR_OUTCOMES"
            or data.get("schema") != "yggdrasil.external-research-prereg.v1"):
        raise ValueError("invalid frozen protocol")
    parent = data.get("parent", {})
    if parent.get("head_sha") != PARENT or parent.get("tree_sha") != PARENT_TREE:
        raise ValueError("parent baseline drift")
    src = data.get("source", {})
    if (src.get("seeds") != list(range(5601, 5617))
            or "SELFTEST" not in src.get("cohort", "")
            or "12288" not in src.get("paid_budget", "")
            or "384" not in src.get("paid_budget", "")):
        raise ValueError("frozen source/budget altered")
    t = data.get("frozen_thresholds", {})
    if (t.get("quartic_worlds_with_detected_paid_incompatible_action_min") != 4
            or t.get("degree2_3_controls_false_incompatible_action_max") != 0
            or t.get("candidate_minus_MLP_public_equal_coverage_correct_min") != 20
            or t.get("candidate_train_infer_CPU_over_MLP_train_infer_max") != 2
            or t.get("independent_symbolic_exact_parity_worlds") != 16):
        raise ValueError("frozen threshold drift")
    authority = data.get("authority", {})
    if (type(authority) is not dict or
            set(authority) != {"draft_unmerged", "protected_scientific_first_use",
                               "official_loop", "accepted_refs", "merges",
                               "controllers", "runners", "scheduled_tasks",
                               "deployment", "paid_apis"} or
            authority["draft_unmerged"] is not True or
            any(value is not False for key, value in authority.items()
                if key != "draft_unmerged")):
        raise PermissionError("protected or deployment authority changed")
    return True


def audit_static_readonly():
    sha = _git("rev-parse", "HEAD")
    expected = os.environ.get("GITHUB_SHA")
    if os.environ.get("GITHUB_EVENT_NAME") == "pull_request":
        expected = os.environ.get("WSP80_CHECKOUT_HEAD_SHA")
        if not expected:
            raise RuntimeError("explicit PR checkout head SHA missing")
    if len(sha) != 40 or (expected and sha != expected):
        raise RuntimeError("exact checkout SHA mismatch")
    if _git("status", "--porcelain"):
        raise RuntimeError("dirty source checkout")
    if _git("rev-parse", PARENT + "^{tree}") != PARENT_TREE:
        raise RuntimeError("parent tree mismatch")
    # Verify prospective prereg was committed alone immediately after frozen parent.
    if _git("rev-parse", PRE_COMMIT + "^") != PARENT:
        raise RuntimeError("prereg parent mismatch")
    prereg_path = "research/contrib/chatgpt/WSP-80/prereg.json"
    if _git("rev-parse", PRE_COMMIT + ":" + prereg_path) != PINNED[prereg_path]:
        raise RuntimeError("prereg original content mismatch")
    if _git("cat-file", "-e", PRE_COMMIT + ":research/contrib/chatgpt/WSP-80/source.py",
            check=False).returncode == 0:
        raise RuntimeError("registered source existed at prereg-first boundary")
    if _git("merge-base", "--is-ancestor", PRE_COMMIT, sha, check=False).returncode != 0:
        raise RuntimeError("prereg no longer ancestor of candidate")
    for path, expected in PINNED.items():
        if _git("rev-parse", "HEAD:" + path) != expected:
            raise RuntimeError("frozen source/blob changed: " + path)
    prereg = json.loads(_git("show", "HEAD:research/contrib/chatgpt/WSP-80/prereg.json"))
    validate_frozen_protocol(prereg)
    return {
        "schema": "wsp80.readonly-source-admission.v1",
        "head_sha": sha,
        "prereg_first_commit": PRE_COMMIT,
        "wsp79_parent_sha": PARENT,
        "wsp79_parent_tree": PARENT_TREE,
        "frozen_blob_ids": dict(PINNED),
        "prereg_frozen_seed_count": 16,
        "prereg_paid_budget_total_actions": 12288,
        "read_only_git_source_identity": "PASS",
        "historic_consumption_ledger_authenticated": False,
        "registered_source_first_use_executed": False,
        "registered_source_first_use_authorized": False,
        "scientific_admission": "BLOCKED_UNTIL_INDEPENDENT_SOURCE_CUSTODY_AND_AUTHORITY",
        "science": "UNVERIFIED",
    }


if __name__ == "__main__":
    if os.sys.argv[1:] != ["--readonly"]:
        raise PermissionError("not a first-use scientific executor")
    print("WSP80_SOURCE_ADMISSION=" +
          json.dumps(audit_static_readonly(), sort_keys=True,
                     separators=(",", ":")), flush=True)
