"""Read-only pinned provenance check for accepted Yggdrasil state vs draft models.

Does NOT load/run synthetic scientific experiments or modify any branch.
Accepted main is source acceptance; this check cannot inspect owner workstation
disk or private non-Git checkpoints. That remains explicitly UNVERIFIED.
"""
from __future__ import annotations
import argparse
import json
import pathlib
import subprocess
import hashlib

ROOT=pathlib.Path(__file__).resolve().parents[4]
HERE=pathlib.Path(__file__).resolve().parent
MAIN="5e74f8db85b2f5839c42148c0dfba69a88b1a2c9"
OWNER="92c421a5475a27015a390efb88c373eb5f15379d"
CAP03="a594a6c5273345687544ddc31e698498bda41d2c"
ACCEPTED_MODULE="yggdrasil/public_causal_cells.py"

def git(*args):
    return subprocess.check_output(["git",*args],cwd=ROOT,
                                   stderr=subprocess.PIPE,
                                   timeout=30).decode("utf-8").strip()

def require(ok,code):
    if not ok:
        raise ValueError("YGG_LINEAGE01_"+code)

def ls(sha):
    return git("ls-tree","-r","--name-only",sha).splitlines()

def check(manifest):
    require(manifest["schema"]==
            "yggdrasil.lineage01.accepted-native-checkpoint-custody.v1",
            "MANIFEST_SCHEMA")
    snapshots=manifest["snapshots"]
    require(snapshots["accepted_main"]["sha"]==MAIN and
            snapshots["owner_research_branch"]["observed_sha"]==OWNER and
            snapshots["research_candidate"]["sha"]==CAP03,
            "PINNED_REFS")
    paths=ls(MAIN)
    native=sorted(path for path in paths
                  if path.startswith("yggdrasil/") and path.endswith(".py"))
    require(native==[ACCEPTED_MODULE],"ACCEPTED_MODULE_SCOPE")
    require(git("rev-parse",MAIN+":"+ACCEPTED_MODULE)==
            snapshots["accepted_main"]["blob"],
            "ACCEPTED_SOURCE_BLOB")
    trusted_checkpoint_formats=(
        ".pt",".pth",".ckpt",".safetensors",".onnx",".pkl",".npz"
    )
    learned_checkpoint_paths=[
        p for p in paths if p.endswith(trusted_checkpoint_formats)]
    require(not learned_checkpoint_paths,
            "UNEXPECTED_ACCEPTED_CHECKPOINT_PATH")
    accepted=git("show",MAIN+":"+ACCEPTED_MODULE)
    require("class PublicCausalCells:" in accepted and
            "self._counts = [[[0, 0]" in accepted and
            "def observe(" in accepted and
            "def restore(" in accepted,
            "ACCEPTED_NATIVE_SOURCE_BEHAVIOR")
    cfg=json.loads(git("show",MAIN+":.research-autonomy/config.json"))
    require(cfg["program"]=="Yggdrasil" and
            cfg["authority"]=="research-only" and
            cfg["ckb_plane_role"]=="governance-only" and
            cfg["active_branch"]==
                snapshots["owner_controller"]["configured_branch"] and
            cfg["mode"]=="repo-local-self-chain",
            "OWNER_CONFIG_AUTHORITY")
    state=json.loads(
        subprocess.check_output([
            "git","show",OWNER+":.research-autonomy/state.json"],
            cwd=ROOT,timeout=30).decode("utf-8-sig"))
    require(state["schema"]=="research.repo-local-state.v1" and
            state["classification"]=="preregistered-blocked" and
            state["scientific_claim"] is False and
            state["authority"]=="research-only" and
            state["experiment"]==
                snapshots["owner_research_branch"]["state_experiment"] and
            state["last_completed_utc"]==
                snapshots["owner_research_branch"]["state_last_completed_utc"],
            "OWNER_BLOCKED_STATE")
    cap03=ls(CAP03)
    require("research/contrib/chatgpt/YGG-CAP03/result.json" in cap03 and
            "research/contrib/chatgpt/YGG-CAP03/provenance.json" in cap03 and
            "yggdrasil/public_causal_cells.py" in cap03,
            "DRAFT_RESEARCH_RECEIPT")
    outcome=json.loads(git(
        "show",CAP03+":research/contrib/chatgpt/YGG-CAP03/result.json"))
    require(outcome.get("scientific_pass",False) is False,
            "NO_UNFOUNDED_SCIENCE_PROMOTION")
    return {
        "schema":"yggdrasil.lineage01.readonly-main-owner-audit.v1",
        "snapshot_only":True,
        "accepted_main_sha":MAIN,
        "active_owner_branch_observed_sha":OWNER,
        "research_candidate_sha":CAP03,
        "accepted_native_modules":native,
        "accepted_checkpoint_paths_by_known_weight_extensions":
            learned_checkpoint_paths,
        "main_native_source_is_initial_zero_count_control":True,
        "owner_state_classification":state["classification"],
        "owner_state_scientific_claim":state["scientific_claim"],
        "owner_configuration_authority":cfg["authority"],
        "cap03_external_research_evidence_verified":True,
        "canonical_accepted_continually_trained_checkpoint":"UNVERIFIED",
        "private_host_local_owner_checkpoint_custody":"UNVERIFIED",
        "source_tree_and_archived_research_receipts":"PASS",
        "new_scientific_first_use":False,
        "accepted_model_promotion":False,
        "controller_or_runner_changed":False,
        "deployment":"NONE"
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--manifest",type=pathlib.Path,
                        default=HERE/"manifest.json")
    parser.add_argument("--output",type=pathlib.Path)
    opts=parser.parse_args()
    receipt=check(json.loads(opts.manifest.read_text(encoding="utf-8")))
    raw=(json.dumps(receipt,sort_keys=True,indent=2)+"\n").encode()
    if opts.output:
        opts.output.write_bytes(raw)
    print("YGG_LINEAGE01_READONLY_SOURCE_CUSTODY_PASS",
          "accepted_checkpoint",receipt[
              "canonical_accepted_continually_trained_checkpoint"],
          "owner_host_custody",receipt[
              "private_host_local_owner_checkpoint_custody"],
          "digest",hashlib.sha256(raw).hexdigest(),flush=True)

if __name__=="__main__":
    main()
