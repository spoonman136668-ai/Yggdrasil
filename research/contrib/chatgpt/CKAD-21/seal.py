"""Seal the matched experiment receipts and complete native checkpoints."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
from campaign import stable

HERE = Path(__file__).resolve().parent


def unique(root, name):
    found = list(root.rglob(name))
    if len(found) != 1:
        raise ValueError(f"Expected exactly one artifact member named {name}.")
    return found[0]


def write_json(name, data):
    (HERE / name).write_bytes((json.dumps(data, indent=2, sort_keys=True) + "\n").encode())


lroot = Path(os.environ["CKAD21_LINUX_DIRECTORY"])
wroot = Path(os.environ["CKAD21_WINDOWS_DIRECTORY"])
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
    assert name == f"seed-{checkpoint['seed']}-context-native.json"
    artifact = unique(lroot, name)
    raw = artifact.read_bytes()
    assert len(raw) == checkpoint["bytes"] and hashlib.sha256(raw).hexdigest() == checkpoint["sha256"]
    shutil.copyfile(artifact, HERE / name)
write_json("result.json", linux)
write_json("replication-windows.json", windows)
write_json("provenance.json", {
    "schema": "yggdrasil.ckad21.provenance.v1",
    "source_sha": source,
    "source_tree": tree,
    "prereg_sha": os.environ["CKAD21_PREREG_SHA"],
    "run_id": int(os.environ["GITHUB_RUN_ID"]),
    "stable_sha256": signature,
    "original_source_actions": 0,
    "scientific_pass": False,
    "deployment": "NONE",
})
metrics = linux["development_metrics"]
gates = linux["development_gates"]
report = f"""# CKAD21 evidence-driven context retrieval

**{linux['classification']}**

The three complete CKAD20 models continue through six public sessions. Each
session receives sixteen probe episodes before held scoring. The model
reconstructs native candidate forecasts from contiguous witnessed experience
blocks and updates a persistent belief with actual public transition and
terminal outcomes. It conditions the second action on the first revealed
transition. Every subsequent session continues the retained full checkpoint.

Development metrics are exact rational values in result.json.
Frozen development gates are {gates}. The independent matched mixture has the
same evidence, candidate structures and action opportunities. Its exact
probabilities and actions must tie. The full-history Beta and fixed trailing64
MLE controls consume the active learner's actual probe outcomes.

The new probe permission differs from CKAD20's zero-adaptation held trial.
All CKAD20 negative results remain recorded. Scientific pass is false and
deployment status is NONE.

Source {source}.
Stable Linux/Windows result {signature}.
Linux campaign {linux['whole_wall_seconds']:.6f}s.
Windows campaign {windows['whole_wall_seconds']:.6f}s.
Setup, final regression, audits and authoring are additional costs.

Reproduce with python -B research/contrib/chatgpt/CKAD-21/campaign.py
--output-directory /tmp/ckad21.

Audit with python -B research/contrib/chatgpt/CKAD-21/independent_audit.py.
"""
(HERE / "SESSION_REPORT.md").write_text(report, encoding="utf-8")
