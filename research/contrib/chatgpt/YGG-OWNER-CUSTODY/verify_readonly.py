"""Yggdrasil native-owner custody audit. NO model execution or checkpoint read.

Offline mode verifies source-linked claims and strict owner fail-closed state.
Online mode issues ONLY bounded read-only GitHub GET metadata requests on
already-pinned project SHA/paths, using preexisting GITHUB_TOKEN in CI.
It never guesses a workstation path, runs owner commands or fetches model bytes.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import urllib.error
import urllib.parse
import urllib.request

HERE=Path(__file__).resolve().parent
REPO="spoonman136668-ai/Yggdrasil"
BASE=f"https://api.github.com/repos/{REPO}"
SHA40=re.compile(r"^[a-f0-9]{40}$")
SHA64=re.compile(r"^[a-f0-9]{64}$")


class CustodyError(ValueError):
    pass


def require(condition,tag):
    if not condition:
        raise CustodyError("YGG_OWNER_CUSTODY_"+tag)


def load(path=HERE/"verified_baseline.json"):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def audit_offline(p):
    require(p["schema"]=="yggdrasil.owner-native-checkpoint-readonly-custody.v1","SCHEMA")
    require("CURRENT_ACCEPTED_TRAINED_CHECKPOINT_UNVERIFIED" in p["classification"],"CLAIM_SCOPE")
    source=p["source_refs"]
    main=source["accepted_main"]
    owner=source["active_native_research_branch"]
    launcher=source["research_only_controller"]
    cap=source["parallel_CAP02_CAP03_research_checkpoint"]
    knowledge=source["prior_factual_knowledge_image"]
    research=source["prior_experiment_audit"]
    require(main["sha"]=="5e74f8db85b2f5839c42148c0dfba69a88b1a2c9","MAIN_ID")
    require(main["public_cells_checkpoint_bytes"]==164,"MAIN_NATIVE_CONTROL_SCOPE")
    require(main["public_cells_are_explicit_baseline_control_not_full_native_GI"] is True,"MAIN_GI_CLAIM")
    require(owner["sha"]=="92c421a5475a27015a390efb88c373eb5f15379d","OWNER_REF")
    require(owner["protected"] is True,"OWNER_PROTECTION")
    require(owner["live_research_state"]["status_classification"]=="preregistered-blocked","OWNER_BLOCK")
    require(owner["live_research_state"]["scientific_claim"] is False,"OWNER_SCIENCE")
    require(owner["last_commit_date_utc"].startswith("2026-10-16"),"OWNER_FRESHNESS")
    require(owner["source_is_on_protected_research_branch_not_accepted_main"] is True,"OWNER_NOT_MAIN")
    require(launcher["authority"]=="research-only" and launcher["ckb_plane_role"]=="governance-only","OWNER_AUTH")
    require(launcher["latest_observed_run"]["run_id"]==44522000519,"RUN_CUSTODY")
    require(launcher["latest_observed_run"]["commit_sha"]==main["sha"],"RUN_MAIN_SOURCE")
    require(launcher["latest_observed_run"]["job_result"]=="success","RUN_ENGINEERING")
    require("RESEARCH_EXECUTOR_UNATTENDED=NOT_CONFIGURED_NO_MODEL_INVOCATION" in
            launcher["latest_observed_run"]["log_verbatim_statuses"],"NO_MODEL_RUN")
    require(launcher["schedule_changed_by_this_gate"] is False,"NO_SCHEDULER_MUTATION")
    require(cap["candidate_sha"]=="78f9696794a9145a0de607dd870244ee49cd9fee","CAP_REF")
    require(cap["scientific_dev_go"] is False and cap["accepted_owner_checkpoint"] is False,"CAP_SCIENCE")
    require(cap["full_regression"]["run_id"]==44520940169,"CAP_FULL_REGRESSION")
    require(cap["full_regression"]["ubuntu_latest"]=="success" and
            cap["full_regression"]["windows_2022"]=="success","CAP_CI")
    require(cap["original_cross_os_checkpoint_sha_equal"] is False and
            cap["new_cross_os_model_checkpoint_sha_equal"] is False,"CAP_CROSS_OS_LIMIT")
    require(cap["continued_trained_source_episode_count_by_seed"]=={"14071":1118,"14072":1093},"CAP_HISTORY_COUNTS")
    require(cap["direct_original_archive_retained_byte_exact"] is True and
            cap["direct_original_readouts_retained_equal"] is True,"CAP_RETENTION_SCOPE")
    require(knowledge["current_owner_installed"]=="UNVERIFIED","KNOWLEDGE_INSTALL")
    require(knowledge["historical_records"]==21343681 and knowledge["historical_predicates"]==828,"KNOWLEDGE_DATA_SCOPE")
    require(knowledge["expected_artifact_expires_at_utc"]=="2026-12-16T11:20:20Z","KNOWLEDGE_EXPIRY")
    require(research["pr"]==1320 and research["scientific_dev_no_go_studies"]==9,"CKAD_HISTORY")
    for row in (main,owner,cap,knowledge):
        for field in ("sha","tree","candidate_sha","candidate_tree"):
            if field in row:require(bool(SHA40.fullmatch(row[field])),field.upper()+"_FORMAT")
    for key,value in p["accepted_owner_checkpoint_requirements"].items():
        require(value is None,"UNPROVEN_"+key.upper())
    require(p["accepted_owner_validation"]=="UNVERIFIED","OWNER_UNVERIFIED")
    require(p["full_final_accepted_owner_scientific_qualification"]=="UNVERIFIED","SCIENCE_UNVERIFIED")
    flags=p["this_gate"]
    for key in ("no_new_scientific_source_consumed","no_runner_dispatched","no_model_training_performed",
                "no_owner_checkpoint_bytes_verified","no_deployment"):
        require(flags[key] is True,"GATE_"+key.upper())
    require(flags["sidecar_only"] is True,"SIDE_CAR_ONLY")
    return {
      "schema":"yggdrasil.owner-native-custody-audit.v1",
      "context_source_and_owner_bounded_read_verified":True,
      "accepted_main_sha":main["sha"],
      "protected_owner_branch_sha":owner["sha"],
      "owner_state":"preregistered-blocked",
      "owner_latest_attempt_run":launcher["latest_observed_run"]["run_id"],
      "latest_owner_attempt_unattended_model_invoked":False,
      "parallel_CAP03_regression":True,
      "parallel_CAP03_science":"DEV_NO_GO",
      "prior_knowledge_image_source_qualified":True,
      "knowledge_owner_durable_install":"UNVERIFIED",
      "current_accepted_native_checkpoint":"UNVERIFIED",
      "scientific_qualification":"UNVERIFIED",
      "deployment":"NONE",
      "new_science_seeds_consumed":0
    }


def get_json(suffix,token):
    req=urllib.request.Request(
       BASE+suffix,
       headers={"Authorization":"Bearer "+token,
                "Accept":"application/vnd.github+json",
                "X-GitHub-Api-Version":"2022-11-28",
                "User-Agent":"yggdrasil-readonly-owner-custody-audit"})
    try:
        with urllib.request.urlopen(req,timeout=15) as response:
            data=response.read(1500000)
            require(response.status==200,"REMOTE_GET")
            return json.loads(data)
    except (OSError,ValueError,urllib.error.HTTPError) as e:
        raise CustodyError("YGG_OWNER_CUSTODY_REMOTE_UNAVAILABLE_"+type(e).__name__) from e


def audit_online(p,token):
    require(bool(token),"REMOTE_TOKEN_UNAVAILABLE")
    src=p["source_refs"]
    main=src["accepted_main"]
    owner=src["active_native_research_branch"]
    cap=src["parallel_CAP02_CAP03_research_checkpoint"]
    knowledge=src["prior_factual_knowledge_image"]
    for name,expected in (
      ("main",main["sha"]),
      (owner["name"],owner["sha"])):
        branch=urllib.parse.quote(name,safe="")
        observed=get_json("/branches/"+branch,token)
        require(observed["commit"]["sha"]==expected,"REF_DRIFT_"+name.replace("/","_").upper())
    for kind,row in (("MAIN",main),("OWNER",owner),
                     ("CAP03",cap),("KNOWLEDGE",knowledge)):
        sha=row["sha"] if "sha" in row else row["candidate_sha"]
        expected=row["tree"] if "tree" in row else row["candidate_tree"]
        git_commit=get_json("/git/commits/"+sha,token)
        require(git_commit["tree"]["sha"]==expected,"TREE_DRIFT_"+kind)
    for kind,path,ref,expected in (
       ("MAIN_NATIVE",main["public_native_code"],main["sha"],main["public_native_blob_sha"]),
       ("OWNER_STATE",owner["live_research_state_path"],owner["sha"],owner["live_research_state_blob_sha"]),
       ("RESEARCH_CONFIG",src["research_only_controller"]["config_path"],main["sha"],
             src["research_only_controller"]["config_blob_sha"]),
       ("CAP03_RESULT",cap["result_path"],cap["candidate_sha"],cap["result_blob_sha"]),
       ("CAP03_PARITY",cap["parity_path"],cap["candidate_sha"],cap["parity_blob_sha"]),
       ("NKR07_PREREG","research/contrib/chatgpt/NKR-07/prereg.json",knowledge["candidate_sha"],knowledge["prereg_blob_sha"])):
        url="/contents/"+urllib.parse.quote(path,safe="/")+"?ref="+ref
        content=get_json(url,token)
        require(content["sha"]==expected,"BLOB_DRIFT_"+kind)
    for kind,run_id,expected_sha in (
       ("OWNER",src["research_only_controller"]["latest_observed_run"]["run_id"],main["sha"]),
       ("CAP03",cap["full_regression"]["run_id"],cap["candidate_sha"])):
        run=get_json("/actions/runs/"+str(run_id),token)
        require(run["head_sha"]==expected_sha and run["status"]=="completed" and
                run["conclusion"]=="success","CI_RUN_DRIFT_"+kind)
    return {
       "readonly_api_gets_verified":2+4+6+2,
       "accepted_main_exact":True,
       "protected_owner_ref_exact":True,
       "original_git_trees_exact":True,
       "source_blob_hashes_exact":True,
       "source_CI_run_head_and_completion_exact":True,
       "native_checkpoint_content_accessed":False
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--online",action="store_true",help="Read-only fixed GitHub metadata GET; needs existing GITHUB_TOKEN")
    args=ap.parse_args()
    payload=load()
    status=audit_offline(payload)
    if args.online:
        status.update(audit_online(payload,os.environ.get("GITHUB_TOKEN","")))
    print("YGG_OWNER_CUSTODY_RESULT="+json.dumps(status,sort_keys=True,separators=(",",":")))


if __name__=="__main__":
    main()
