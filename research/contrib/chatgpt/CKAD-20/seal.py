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


lroot = Path(os.environ["CKAD20_LINUX_DIRECTORY"])
wroot = Path(os.environ["CKAD20_WINDOWS_DIRECTORY"])
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
    assert name == f"seed-{checkpoint['seed']}-unified-native.json"
    artifact = unique(lroot, name)
    raw = artifact.read_bytes()
    assert len(raw) == checkpoint["bytes"] and hashlib.sha256(raw).hexdigest() == checkpoint["sha256"]
    shutil.copyfile(artifact, HERE / name)
write_json("result.json", linux)
write_json("replication-windows.json", windows)
write_json("provenance.json", {
    "schema": "yggdrasil.ckad20.provenance.v1",
    "source_sha": source,
    "source_tree": tree,
    "prereg_sha": os.environ["CKAD20_PREREG_SHA"],
    "run_id": int(os.environ["GITHUB_RUN_ID"]),
    "stable_sha256": signature,
    "original_source_actions": 0,
    "scientific_pass": False,
    "deployment": "NONE",
})
(HERE / "SESSION_REPORT.md").write_text(f"""# CKAD20 unified synthetic continuation

**{linux['classification']}**

The full CKAD18 learner received new public synthetic trajectories in a single
episode ledger. During acquisition, hypothesis disagreement or composed
two-stage predictions selected the actual interventions. The source returned
the resulting next state and terminal reward. The same witnessed ledger drives
paired-view projection learning, the fitted forecast structures, targeted
counter repair, and replay on restore. Model forecasts never enter that ledger.

Every stage measured reward by executing policies in paired held synthetic
episodes. Both native and fully fitted conventional controls are recorded in
result.json. The checkpoint embeds its verified episode history and keeps the
historical properties, hypotheses, quarantine, MDP and DTR state.

Frozen source {source}. Stable Linux/Windows result {signature}.
The qualification workflow records complete campaign and CI timing.

Reproduce with python -B research/contrib/chatgpt/CKAD-20/campaign.py
--output-directory /tmp/ckad20. The independent audit checks the retained
legacy state and regenerates each acquired public outcome at its chosen actions.

Scientific pass remains false. Deployment status is NONE.
""", encoding="utf-8")
