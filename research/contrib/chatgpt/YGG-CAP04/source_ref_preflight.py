"""CAP04 source-reference custody preflight; read-only, zero secret access.

Verifies immutable Git refs, original CAP03 source and frozen CAP04 prereg.
This does NOT authorize real entropy generation or registered scientific first use.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
import json
from pathlib import Path
import re
import subprocess

SCHEMA = "yggdrasil.cap04.source-reference-preflight.v1"
REPO = "spoonman136668-ai/Yggdrasil"
SOURCE_PATH = "research/contrib/chatgpt/YGG-CAP04/prospective_source_v2.py"
PREREG_PATH = "research/contrib/chatgpt/YGG-CAP04/prereg.json"
CAP03_PATH = "research/contrib/chatgpt/YGG-CAP03/source.py"


@dataclass(frozen=True)
class FrozenRefs:
    candidate_sha: str = "5d6a04843c53507b316d94993faafcf08dc04afc"
    candidate_tree_sha: str = "571cdb44c17cedb0ef6aa35bac9c0a198ae4760a"
    source_blob_sha: str = "fd42459ba94210c97c94b6cf816ac38d7587c26f"
    prereg_blob_sha: str = "1d79e222685ea1a6889bff49e5bf405a9aed9580"
    cap03_source_blob_sha: str = "d5a3fc30846ebbb97eeb8817fc72d9cd5be8c181"
    prereg_freeze_commit: str = "1faf84d4a62f16da2ee4ef5f1c7464eb76bab39c"
    original_accepted_main: str = "5e74f8db85b2f5839c42148c0dfba69a88b1a2c9"


FROZEN = FrozenRefs()
EXPECTED_REGISTERED = (99917, 99931, 100017, 100031, 100117, 100131, 100151)


def _require(cond: bool, reason: str) -> None:
    if not cond:
        raise ValueError("CAP04_REFERENCE_" + reason)


def validate_sha(value: str) -> str:
    _require(type(value) is str and re.fullmatch("[0-9a-f]{40}", value) is not None,
             "INVALID_SHA")
    return value


def _git(root: Path, *args: str) -> str:
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), *args],
            check=False, capture_output=True, text=True, encoding="utf-8",
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ValueError("CAP04_REFERENCE_GIT_UNAVAILABLE") from exc
    _require(proc.returncode == 0, "GIT_OBJECT_OR_STATE_MISMATCH")
    return proc.stdout.strip()


def _immutable_ref(root: Path, commit: str, path: str) -> str:
    # All paths are trusted source constants, SHAs are strictly validated.
    return _git(root, "rev-parse", f"{validate_sha(commit)}:{path}")


def verify_source_references(root: Path, expected: FrozenRefs = FROZEN) -> dict:
    """Read-only immutable source audit; not a runtime/first-use approval."""
    _require(type(root) is Path and root.is_dir(), "REPOSITORY_ROOT")
    _require(type(expected) is FrozenRefs, "FROZEN_REFERENCE_TYPE")
    for sha in vars(expected).values():
        validate_sha(sha)
    _require(_git(root, "rev-parse", "--show-toplevel") ==
             str(root.resolve()), "WRONG_REPOSITORY_ROOT")
    commit = _git(root, "rev-parse", "--verify",
                  expected.candidate_sha + "^{commit}")
    _require(commit == expected.candidate_sha, "CANDIDATE_IDENTITY")
    _require(_git(root, "rev-parse", expected.candidate_sha + "^{tree}") ==
             expected.candidate_tree_sha, "CANDIDATE_TREE")
    # Git SHA content identity does not grant permission to execute.
    for path, blob in (
        (SOURCE_PATH, expected.source_blob_sha),
        (PREREG_PATH, expected.prereg_blob_sha),
        (CAP03_PATH, expected.cap03_source_blob_sha),
    ):
        _require(_immutable_ref(root, expected.candidate_sha, path) == blob,
                 "FROZEN_BLOB_" + path.rsplit("/", 1)[-1])
        _require(_git(root, "rev-parse", "HEAD:" + path) == blob,
                 "HEAD_BLOB_" + path.rsplit("/", 1)[-1])
        _require(_git(root, "hash-object", path) == blob,
                 "WORKTREE_BLOB_" + path.rsplit("/", 1)[-1])
    _require(_immutable_ref(root, expected.prereg_freeze_commit,
                            PREREG_PATH) == expected.prereg_blob_sha,
             "PREREG_FREEZE")
    _require(_git(root, "merge-base", "--is-ancestor",
                  expected.candidate_sha, "HEAD") == "", "SOURCE_ANCESTRY")
    source_text = _git(root, "show", expected.candidate_sha + ":" + PREREG_PATH)
    try:
        p = json.loads(source_text)
    except (ValueError, TypeError) as exc:
        raise ValueError("CAP04_REFERENCE_PREREG_INVALID_JSON") from exc
    _require(type(p) is dict and
             p.get("schema") ==
             "yggdrasil.cap04.native-predictive-state-splitting-prereg.v1" and
             p.get("id") == "YGG-CAP04", "PREREG_CONTRACT")
    parent = p.get("parent", {})
    _require(type(parent) is dict and
             parent.get("accepted_main") == expected.original_accepted_main,
             "ORIGINAL_MAIN_ANCHOR")
    s = p.get("source", {})
    _require(type(s) is dict and
             tuple(s.get("dev_seeds", [])) == EXPECTED_REGISTERED[:2] and
             tuple(s.get("reserved_pilot", [])) == EXPECTED_REGISTERED[2:4] and
             tuple(s.get("reserved_primary", [])) == EXPECTED_REGISTERED[4:] and
             s.get("new_episodes_per_seed") == 96 and
             s.get("phase_boundaries") == [0, 32, 72, 96],
             "REGISTERED_PROTOCOL")
    a = p.get("authority", {})
    _require(type(a) is dict and
             a.get("scientific_first_use_not_authorized") is True and
             a.get("no_merge") is True and
             a.get("no_deployment") is True,
             "FIRST_USE_FENCE")
    return {
        "schema": SCHEMA,
        "status": "PUBLIC_SOURCE_REF_VERIFIED_ONLY",
        "repo": REPO,
        "candidate_sha": expected.candidate_sha,
        "candidate_tree_sha": expected.candidate_tree_sha,
        "v2_source_blob_sha": expected.source_blob_sha,
        "prereg_blob_sha": expected.prereg_blob_sha,
        "cap03_source_blob_sha": expected.cap03_source_blob_sha,
        "registered_first_use_authorized": False,
        "private_entropy_custody_verified": False,
        "owner_source_key_uniqueness_verified": False,
        "scientific_effectiveness_verified": False,
    }


def prevent_public_receipt_promotion(receipt: dict) -> None:
    """Explicitly reject treating a public-only verification as first-use."""
    _require(type(receipt) is dict and
             receipt.get("schema") == SCHEMA and
             receipt.get("status") == "PUBLIC_SOURCE_REF_VERIFIED_ONLY" and
             receipt.get("registered_first_use_authorized") is False and
             receipt.get("private_entropy_custody_verified") is False,
             "INVALID_PUBLIC_RECEIPT")
    raise ValueError("CAP04_REFERENCE_FIRST_USE_NOT_AUTHORIZED")


if __name__ == "__main__":
    print(json.dumps(verify_source_references(Path(__file__).resolve().parents[4]),
                     sort_keys=True, separators=(",", ":")))
