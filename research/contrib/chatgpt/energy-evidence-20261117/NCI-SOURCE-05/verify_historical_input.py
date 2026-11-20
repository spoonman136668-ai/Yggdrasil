#!/usr/bin/env python3
"""Read-only audit of pinned Amalgam historical traces against NCI-SOURCE-03 guard.
No Yggdrasil imports, checkpoints, training, source resets, or model actions.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def blob_sha1(data):
    header = b"blob " + str(len(data)).encode("ascii") + b"\0"
    return hashlib.sha1(header + data).hexdigest()


def is_bit(v):
    return type(v) is int and v in (0, 1)


def rows(value):
    if type(value) is list:
        groups = [("array", value)]
    elif type(value) is dict:
        groups = [(k, v) for k, v in value.items()]
        if any(type(v) is not list for _, v in groups):
            raise ValueError("unexpected non-array group")
    else:
        raise ValueError("trace is neither object nor array")
    for group, events in groups:
        for index, event in enumerate(events):
            if type(event) is list and len(event) == 3:
                identifier, views, row = event
            elif type(event) is dict:
                identifier = event.get("id", event.get("identifier"))
                views, row = event.get("views"), event.get("row")
            else:
                raise ValueError("unexpected event shape")
            yield group, index, identifier, views, row


def verify_event(identifier, views, row):
    if type(identifier) is not str or len(identifier) != 64 or any(c not in "0123456789abcdef" for c in identifier):
        raise ValueError("invalid witness identifier")
    if not (type(views) is list and len(views) == 2
            and all(type(v) is list and len(v) == 2 and all(is_bit(b) for b in v) for v in views)):
        raise ValueError("invalid public paired views")
    if not (type(row) is dict and set(row) == {"s1", "x1", "s2", "x2", "y"}
            and all(is_bit(v) for v in row.values())):
        raise ValueError("invalid public row")
    if row["s1"] != views[0][0] or views[0][0] != views[1][0]:
        raise ValueError("initial state conflicts with public views")


def exact_git_head(source, expected):
    completed = subprocess.run(
        ["git", "-C", str(source), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True)
    if completed.stdout.strip() != expected:
        raise ValueError("incorrect Amalgam source SHA")
    dirty = subprocess.run(
        ["git", "-C", str(source), "status", "--porcelain", "--untracked-files=normal"],
        capture_output=True, text=True, check=True)
    if dirty.stdout.strip():
        raise ValueError("source checkout is dirty")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-tree", type=Path, required=True)
    args = parser.parse_args()
    root = args.source_tree.resolve()
    manifest = json.loads(Path(__file__).with_name("manifest.json").read_text("utf-8"))
    if manifest["schema"] != "nci-source05.historical-public-input-audit.v1":
        raise ValueError("incorrect manifest schema")
    exact_git_head(root, manifest["research_source"]["commit"])
    for component in ("original_entrypoint", "original_episode"):
        f = manifest[component]
        raw = (root / f["path"]).read_bytes()
        if blob_sha1(raw) != f["git_blob_sha1"]:
            raise ValueError("native source drift: " + f["path"])
    report = []
    total = 0
    for f in manifest["files"]:
        raw = (root / f["path"]).read_bytes()
        if blob_sha1(raw) != f["git_blob_sha1"]:
            raise ValueError("trace blob mismatch: " + f["path"])
        parsed = json.loads(raw)
        n = 0
        for group, ix, identifier, views, row in rows(parsed):
            try:
                verify_event(identifier, views, row)
            except ValueError as exc:
                raise ValueError(f["path"] + ":" + group + ":" + str(ix) + ": " + str(exc)) from exc
            n += 1
        if n != f["records"]:
            raise ValueError("unexpected row count: " + f["path"])
        total += n
        report.append({"path": f["path"], "git_blob_sha1": f["git_blob_sha1"],
                       "records": n, "initial_state_conflicts": 0})
    if len(report) != manifest["totals"]["files"] or total != manifest["totals"]["records"]:
        raise ValueError("manifest totals mismatch")
    print(json.dumps({"status": "READ_ONLY_HISTORICAL_COMPATIBILITY_PASS",
                      "research_commit": manifest["research_source"]["commit"],
                      "files": report, "records": total,
                      "native_model_restored": False, "scientific_pass": False},
                     sort_keys=True, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as e:
        print("AUDIT_FAIL: " + str(e), file=sys.stderr)
        sys.exit(1)
