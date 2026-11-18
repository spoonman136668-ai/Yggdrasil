"""Seal independently reproduced CKAD23 synthetic training receipts into the existing draft."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)
from campaign import LEGACY
from yggdrasil.native_context_basis import digest

def check(value, label):
    if not value:
        raise RuntimeError("CKAD23_SEAL_" + label)

def unique(root, name):
    matches = list(root.rglob(name))
    check(len(matches) == 1, "UNIQUE_" + name)
    return matches[0]

def store(name, body):
    (HERE / name).write_bytes((json.dumps(body, indent=2, sort_keys=True) + "\n").encode("ascii"))

linux_root = Path(os.environ["CKAD23_LINUX_DIRECTORY"])
windows_root = Path(os.environ["CKAD23_WINDOWS_DIRECTORY"])
source = os.environ["CKAD23_SOURCE_COMMIT"]
run_id = int(os.environ["CKAD23_EVIDENCE_RUN"])
git_source = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
check(git_source != source, "SEAL_RUN_MUST_NOT_MUTATE_FROZEN_SOURCE")
linux = json.loads(unique(linux_root, "campaign-result.json").read_bytes())
windows = json.loads(unique(windows_root, "campaign-result.json").read_bytes())
stable_l = digest(LEGACY.stable(linux))
stable_w = digest(LEGACY.stable(windows))
check(stable_l == stable_w == linux["stable_sha256"] == windows["stable_sha256"],
      "CROSS_PLATFORM_SEMANTIC_DIFFERENCE")
check(linux["source_candidate_sha"] == windows["source_candidate_sha"] == source,
      "SOURCE_CANDIDATE")
check([s["seed"] for s in linux["seeds"]] == [101, 202, 303], "FROZEN_SEEDS")
check(linux["development_gates"] == windows["development_gates"]
      and linux["classification"] == windows["classification"], "FROZEN_DECISION")
check(linux["scientific_pass"] is False and windows["scientific_pass"] is False
      and linux["accepted_native"] is False and windows["accepted_native"] is False
      and linux["deployment"] == windows["deployment"] == "NONE", "SAFETY_FENCES")
for case in linux["seeds"]:
    filename = case["final_checkpoint_name"]
    check(filename == f"seed-{case['seed']}-stream-native.json", "CHECKPOINT_NAME")
    primary = unique(linux_root, filename).read_bytes()
    replica = unique(windows_root, filename).read_bytes()
    check(primary == replica, "PLATFORM_CHECKPOINT_BYTES")
    check(len(primary) == case["final_checkpoint_bytes"]
          and hashlib.sha256(primary).hexdigest() == case["final_checkpoint_sha256"],
          "CHECKPOINT_CUSTODY")
    (HERE / filename).write_bytes(primary)
store("campaign-result.json", linux)
store("replication-windows.json", windows)
store("provenance.json", {
    "schema": "yggdrasil.ckad23.unsignaled-development.provenance.v1",
    "training_source_sha": source,
    "training_run_id": run_id,
    "sealing_source_sha": git_source,
    "stable_sha256": stable_l,
    "synthetic_original_source_actions": 0,
    "protected_first_use": 0,
    "scientific_pass": False,
    "deployment": "NONE",
})
summary = linux["development_metrics"]
gates = linux["development_gates"]
report = f"""# CKAD23 consequence-driven unsignaled context changes

**{linux['classification']}** — engineering evidence from the frozen synthetic
development source only. Scientific superiority remains **UNVERIFIED** and
no deployment or accepted-model promotion is authorized.

Three cumulative native learner states begin with448 witnessed episodes,
continue with192 actual synthetic causal interventions each and preserve all
640 episodes at completion. Four unseen evaluator-side phases change at48,
96 and144. The learner is never given phase labels or a regime switch notice.
It uses the preregistered prequential joint likelihood monitor and native
novel-context mixture. Same-receipt conventional exact-mixture predictions
remain a mandatory parity control.

Frozen gates: {json.dumps(gates, sort_keys=True)}.
Frozen metrics: {json.dumps(summary, sort_keys=True)}.
Negative outcomes remain negative; no post-score threshold is changed.

Exact qualified training source: {source}.
CI training and replication run: {run_id}.
Linux/Windows semantic SHA256: {stable_l}.
Original-source actions and held training updates:0.

Linux campaign wall seconds: {linux['whole_wall_seconds']:.6f}.
Windows campaign wall seconds: {windows['whole_wall_seconds']:.6f}.
These exclude setup, authoring and independent acceptance costs.

Reproduce from the pinned source with:
python -B research/contrib/chatgpt/CKAD-23/campaign.py
--output-directory /tmp/ckad23
Independent raw replay:
python -B research/contrib/chatgpt/CKAD-23/independent_audit.py
research/contrib/chatgpt/CKAD-23
"""
(HERE / "SESSION_REPORT.md").write_text(report, encoding="utf-8")
subprocess.check_call([sys.executable, "-B",
                       str(HERE / "independent_audit.py"), str(HERE)], cwd=ROOT)
print(json.dumps({"sealed": True, "stable": stable_l, "training_run_id": run_id}))
