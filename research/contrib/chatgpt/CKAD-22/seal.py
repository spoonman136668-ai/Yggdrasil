"""Seal the matched experiment receipts and complete native checkpoints."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)
from campaign import stable

HERE = Path(__file__).resolve().parent


def unique(root, name):
    found = list(root.rglob(name))
    if len(found) != 1:
        raise ValueError(f"Expected exactly one artifact member named {name}.")
    return found[0]


def write_json(name, data):
    (HERE / name).write_bytes((json.dumps(data, indent=2, sort_keys=True) + "\n").encode())


lroot = Path(os.environ["CKAD22_LINUX_DIRECTORY"])
wroot = Path(os.environ["CKAD22_WINDOWS_DIRECTORY"])
linux = json.loads(unique(lroot, "campaign-result.json").read_bytes())
windows = json.loads(unique(wroot, "campaign-result.json").read_bytes())
source = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
tree = subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], text=True).strip()
signature = linux["stable_sha256"]
assert stable(linux) == stable(windows)
assert all(document["stable_sha256"] == signature and document["source_candidate_sha"] == source
           for document in (linux, windows))
for checkpoint in linux["final_checkpoints"]:
    name = checkpoint["name"]
    assert name == f"seed-{checkpoint['seed']}-expanded-native.json"
    artifact = unique(lroot, name)
    raw = artifact.read_bytes()
    assert len(raw) == checkpoint["bytes"] and hashlib.sha256(raw).hexdigest() == checkpoint["sha256"]
    shutil.copyfile(artifact, HERE / name)
write_json("result.json", linux)
write_json("replication-windows.json", windows)
write_json("provenance.json", {
    "schema": "yggdrasil.ckad22.provenance.v1",
    "source_sha": source,
    "source_tree": tree,
    "prereg_sha": os.environ["CKAD22_PREREG_SHA"],
    "run_id": int(os.environ["GITHUB_RUN_ID"]),
    "stable_sha256": signature,
    "original_source_actions": 0,
    "scientific_pass": False,
    "deployment": "NONE",
})
gates = linux["development_gates"]
report = f"""# CKAD22 learning a new context hypothesis

**{linux['classification']}**

The three qualified CKAD21 models continue from320 retained episodes through
four public sessions with32 actual probe episodes each. The retained-context
tournament allocates one eighth prior mass to an initially empty hypothesis,
which learns transition and terminal forecasts from new public receipts.
Old candidates remain fixed during a session. Every next session rebuilds its
candidates from the accumulated evidence in the same complete native checkpoint.

The source remains the frozen synthetic generator. Family and regime stay on
the source side. Scores are from96 held episodes after each probe budget.
Independent exact online-mixture forecasts and actions must match the native
model. Control metrics and exact rational development comparisons are in result.json.

Frozen gates are {gates}. The aggregate classification preserves every failed
threshold. CKAD20/21 outcomes and their original permissions remain historical.
This study uses32 probe episodes per session, differing from CKAD21's16.

Frozen source {source}.
Stable Linux/Windows result {signature}.
Linux campaign {linux['whole_wall_seconds']:.6f}s.
Windows campaign {windows['whole_wall_seconds']:.6f}s.
CI setup, qualification, independent audits and authoring are additional costs.

Reproduce with python -B research/contrib/chatgpt/CKAD-22/campaign.py
--output-directory /tmp/ckad22.
Audit with python -B research/contrib/chatgpt/CKAD-22/independent_audit.py.

Original-source actions and held training updates are zero.
Scientific pass remains false. Deployment status is NONE.
"""
(HERE / "SESSION_REPORT.md").write_text(report, encoding="utf-8")
