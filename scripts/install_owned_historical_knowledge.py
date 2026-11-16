"""NKR-07: explicit owner-scoped durable install of existing historical knowledge.

No default owner path, no controller, acceptance, scheduler or automatic run.
Requires existing GitHub CLI authentication and a caller-selected destination.
Only the already-built, pinned GitHub research artifact can be installed.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

from yggdrasil.native_knowledge_activation import (
    PINNED_ARTIFACT_ID, PINNED_SOURCE_RUN, PINNED_ROWS,
    PINNED_PACKED_SHA, PINNED_MANIFEST_SHA,
    install_offline_image, open_installed_session,
)

REPO = "spoonman136668-ai/Yggdrasil"
SOURCE_COMMIT = "c4b4e97726f6541197913ad405a47d4c4019a3cf"
ARTIFACT_NAME = "NKR05-21M-full-historical-TRAIN-native-factual-weights"
ZIP_SHA256 = "c7265cabac91b8762fb5d65209eef44fa79a8fbf3d9a6f61300ef60ded0a5275"
EXPECTED_ZIP_BYTES = 256126168
REQUIRED_FILES = frozenset(("facts.uint32le", "manifest.json", "receipt.json"))


def verify_source_metadata(meta, *, now=None):
    """Check immutability and expiry before any artifact content is requested.

    Metadata digest reports the ZIP hash, while the separate NKR-06 installer
    re-hashes the *actual* unpacked 256 MB image. Both checks are mandatory.
    """
    if type(meta) is not dict:
        raise ValueError("NKR07_ARTIFACT_METADATA_INVALID")
    run = meta.get("workflow_run")
    if (type(meta.get("id")) is not int
            or meta["id"] != PINNED_ARTIFACT_ID
            or meta.get("name") != ARTIFACT_NAME
            or meta.get("expired") is not False
            or meta.get("digest") != "sha256:" + ZIP_SHA256
            or type(meta.get("size_in_bytes")) is not int
            or meta["size_in_bytes"] != EXPECTED_ZIP_BYTES
            or type(run) is not dict
            or run.get("id") != PINNED_SOURCE_RUN
            or run.get("head_sha") != SOURCE_COMMIT):
        raise ValueError("NKR07_ORIGINAL_ARTIFACT_IDENTITY_DRIFT")
    expires = meta.get("expires_at")
    if type(expires) is not str:
        raise ValueError("NKR07_EXPIRY_INVALID")
    try:
        parsed = datetime.fromisoformat(expires.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("NKR07_EXPIRY_INVALID") from exc
    if parsed.tzinfo is None:
        raise ValueError("NKR07_EXPIRY_INVALID")
    instant = now if now is not None else datetime.now(timezone.utc)
    if instant.tzinfo is None:
        raise ValueError("NKR07_CLOCK_INVALID")
    if instant >= parsed:
        raise ValueError("NKR07_ORIGINAL_ARTIFACT_EXPIRED")
    return True


def _gh(args, *, timeout):
    """No shell, no token interpolation and no credential output."""
    output = subprocess.run(
        ["gh", *args], check=True, capture_output=True, text=True,
        timeout=timeout)
    return output.stdout


def stage_owner_knowledge(parent, name="yggdrasil-historical-facts",
                          *, now=None, gh_runner=None):
    """Explicit installer; does nothing without a verified caller-owned parent.

    gh_runner is only an injected subprocess boundary for source-free tests.
    It must obey _gh(args, timeout=...) and is never persisted.
    """
    parent = Path(parent)
    if not parent.is_dir() or parent.is_symlink():
        raise ValueError("NKR07_OWNER_PARENT_MISSING_OR_SYMLINK")
    if (type(name) is not str
            or re.fullmatch(r"[a-z][a-z0-9_-]{2,63}", name) is None):
        raise ValueError("NKR07_INSTALL_NAME_INVALID")
    target = parent / name
    if target.exists() or target.is_symlink():
        raise FileExistsError("NKR07_EXISTING_TARGET_NO_REPLAY")
    run = gh_runner if gh_runner is not None else _gh
    metadata = run(
        ["api", f"repos/{REPO}/actions/artifacts/{PINNED_ARTIFACT_ID}"],
        timeout=30)
    try:
        parsed = json.loads(metadata)
    except (TypeError, ValueError) as exc:
        raise ValueError("NKR07_METADATA_NOT_JSON") from exc
    verify_source_metadata(parsed, now=now)
    # Neither temporary bits nor image bytes are written to the user's model
    # until the source has been staged into an isolated, checked directory.
    with tempfile.TemporaryDirectory(prefix="nkr07-owned-source-") as temp:
        staging = Path(temp)
        run(["run", "download", str(PINNED_SOURCE_RUN),
             "-R", REPO, "-n", ARTIFACT_NAME,
             "-D", str(staging)], timeout=360)
        actual = frozenset(x.name for x in staging.iterdir())
        if (actual != REQUIRED_FILES
                or any(not x.is_file() or x.is_symlink() for x in staging.iterdir())):
            raise ValueError("NKR07_ARTIFACT_MEMBER_MISMATCH")
        outcome = install_offline_image(staging, parent, name)
    # Verify persisted activation receipt and *full cold image*, not just copy.
    with open_installed_session(target) as knowledge:
        first = knowledge._weights.row_at(0)
        last = knowledge._weights.row_at(PINNED_ROWS - 1)
        if (not knowledge.fact(*first)["witnessed"]
                or not knowledge.fact(*last)["witnessed"]
                or knowledge.fact(0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF)["witnessed"]):
            raise AssertionError("NKR07_OWNER_COLD_RETRIEVAL_FAIL")
    return {
        **outcome,
        "schema": "yggdrasil.nkr07.owner-persistent-research-install.v1",
        "classification": "OWNER_LOCAL_RESEARCH_IMAGE_READY",
        "accepted_native": False,
        "native_owner_activated": False,
        "scientific_pass": False,
        "source_origin_artifact_id": PINNED_ARTIFACT_ID,
        "source_original_run_id": PINNED_SOURCE_RUN,
        "source_image_sha256": PINNED_PACKED_SHA,
        "source_manifest_sha256": PINNED_MANIFEST_SHA,
        "owner_selected_destination": str(target),
        "no_controller_mutation": True,
        "no_original_science_replay": True,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--owner-persistent-parent", required=True,
                        help="Existing owned directory; NO default and no overwrite")
    parser.add_argument("--name", default="yggdrasil-historical-facts")
    args = parser.parse_args()
    result = stage_owner_knowledge(args.owner_persistent_parent, args.name)
    print("NKR07_OWNER_INSTALL=" + json.dumps(
        result, sort_keys=True, separators=(",", ":")), flush=True)


if __name__ == "__main__":
    main()
