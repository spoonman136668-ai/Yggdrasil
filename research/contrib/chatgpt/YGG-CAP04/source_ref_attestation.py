"""CAP04 v2 read-only Git source/protocol attestation — engineering-only.

This tool authenticates exact content against independently pinned, previously
qualified Git objects. It never accepts/loads source entropy or schedules a
registered first-use, and it is NOT owner acceptance or source-key custody.
Use only in a full source checkout with complete Git history available.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess

SCHEMA = "yggdrasil.cap04.v2-source-ref-preflight.v1"
ANCHOR_COMMIT = "5d6a04843c53507b316d94993faafcf08dc04afc"
ANCHOR_TREE = "571cdb44c17cedb0ef6aa35bac9c0a198ae4760a"
BLOBS = {
    "research/contrib/chatgpt/YGG-CAP04/prospective_source_v2.py":
        "fd42459ba94210c97c94b6cf816ac38d7587c26f",
    "tests/test_cap04_keyed_source_v2.py":
        "86259d4c964758f97bb256a84a3c392f1c1eb1be",
    "research/contrib/chatgpt/YGG-CAP04/prereg.json":
        "1d79e222685ea1a6889bff49e5bf405a9aed9580",
    "research/contrib/chatgpt/YGG-CAP03/source.py":
        "d5a3fc30846ebbb97eeb8817fc72d9cd5be8c181",
    "scripts/build_code_atlas.py":
        "cef1378fd3c47ebc74675bd9dde19a183775ceeb",
}
ALLOWED_DESCENDANT_CHANGES = frozenset({
    "research/contrib/chatgpt/YGG-CAP04/source_ref_attestation.py",
    "tests/test_cap04_v2_source_ref_attestation.py",
    ".github/workflows/ygg-cap04-v2-ref-attestation.yml",
    ".ice/code-atlas.json", ".ice/code-atlas.html", ".ice/code-atlas.ice",
})


def _require(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError("CAP04_REF_" + why)


def _git(repo: Path, *args: str) -> str:
    try:
        run = subprocess.run(
            ["git", "-C", str(repo), *args], capture_output=True,
            text=True, encoding="utf-8", errors="strict", check=False,
            timeout=20)
    except (OSError, subprocess.TimeoutExpired, UnicodeError) as exc:
        raise ValueError("CAP04_REF_GIT_UNAVAILABLE") from exc
    _require(run.returncode == 0, "GIT_COMMAND_FAILED")
    return run.stdout.strip()


def verify_source_refs(repo_root: Path) -> dict:
    """Verify the known 499/499 engineering source, no secret material involved.

    Rejects missing history, checkout drift, unknown file modifications,
    altered prereg, a different commit/tree, or a dirty source worktree.
    This verifies Git object identity relative to fixed trusted pins; it does
    not prove Git signature trust, entropy custody, owner approval or science.
    """
    _require(isinstance(repo_root, Path), "ROOT_TYPE")
    root = repo_root.resolve(strict=True)
    _require(Path(_git(root, "rev-parse", "--show-toplevel")).resolve() == root,
             "REPO_ROOT")
    _require(_git(root, "cat-file", "-t", ANCHOR_COMMIT) == "commit",
             "ANCHOR_TYPE")
    _require(_git(root, "rev-parse", ANCHOR_COMMIT + "^{tree}") == ANCHOR_TREE,
             "ANCHOR_TREE")
    head = _git(root, "rev-parse", "HEAD")
    _require(re.fullmatch(r"[0-9a-f]{40}", head) is not None, "HEAD_SHA")
    _git(root, "merge-base", "--is-ancestor", ANCHOR_COMMIT, head)
    for path, expected in BLOBS.items():
        pinned = _git(root, "rev-parse", ANCHOR_COMMIT + ":" + path)
        actual = _git(root, "rev-parse", "HEAD:" + path)
        _require(pinned == expected and actual == expected,
                 "SOURCE_BLOB_DRIFT")
    changed = frozenset(filter(None, _git(root, "diff", "--name-only",
                                           ANCHOR_COMMIT, head, "--").splitlines()))
    _require(changed.issubset(ALLOWED_DESCENDANT_CHANGES), "UNEXPECTED_DELTA")
    _require(_git(root, "status", "--porcelain", "--untracked-files=all") == "",
             "DIRTY_WORKTREE")

    # Read the immutable, old prereg directly from the Git object, never
    # trusting a mutable path or a newly supplied unverified source label.
    doc = json.loads(_git(root, "show",
                          ANCHOR_COMMIT +
                          ":research/contrib/chatgpt/YGG-CAP04/prereg.json"))
    _require(doc.get("schema") ==
             "yggdrasil.cap04.native-predictive-state-splitting-prereg.v1",
             "PREREG_SCHEMA")
    _require(doc.get("source", {}).get("dev_seeds") == [99917, 99931] and
             doc["source"].get("reserved_pilot") == [100017, 100031] and
             doc["source"].get("reserved_primary") ==
             [100117, 100131, 100151] and
             doc["source"].get("new_episodes_per_seed") == 96 and
             doc["source"].get("phase_boundaries") == [0, 32, 72, 96],
             "PREREG_COHORT")
    _require(doc.get("authority", {}).get("scientific_first_use_not_authorized")
             is True and doc["authority"].get("no_merge") is True,
             "FIRST_USE_FENCE")
    # Commit authority and secret-custody receipts deliberately unavailable.
    # Absence is not silently upgraded to PASS.
    return {
        "schema": SCHEMA, "classification": "ENGINEERING_SOURCE_REFS_ONLY",
        "anchor_commit": ANCHOR_COMMIT, "anchor_tree": ANCHOR_TREE,
        "verified_head": head, "verified_git_blobs": dict(sorted(BLOBS.items())),
        "changed_paths": sorted(changed),
        "protected_first_use": "LOCKED",
        "owner_entropy_custody": "UNVERIFIED",
        "owner_source_acceptance": "UNVERIFIED",
        "scientific_efficacy": "UNVERIFIED",
    }
