"""CVH06 source-free, no-original-source, matched-action conventional control smoke.

One-shot CI process only; never instantiates or opens a genuine CausalGym world.
Pure toy transitions do not support scientific claims or first-use authority.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

from fourcell_control import (
    FourCellEarnedPolicy,PublicEarnedPolicy,
    independent_fourcell_public_batch,_canonical
)
from test_fourcell_control import toy_episode

HERE=Path(__file__).resolve().parent


def source_disarm_check():
    doc=json.loads((HERE/"source_first_use_NOT_AUTHORIZED.json").read_text())
    prereg=json.loads((HERE/"prereg.json").read_text())
    if (doc.get("schema")!="yggdrasil.cvh06.original-source-first-use-disabled.v1"
            or doc.get("state")!="NOT_AUTHORIZED_NO_ORIGINAL_SOURCE_ACTIONS"
            or prereg.get("parent",{}).get("head")!="0d0c0a4491c861d72aa0b2fe89a42be6f118b363"
            or prereg.get("phase")!="FROZEN_BEFORE_CVH06_CONTROL_IMPLEMENTATION; NO ORIGINAL FIRST_USE AUTHORIZATION"
            or prereg["authority"]["new_original_source_firstuse_approved"] is not False
            or prereg["source_admission"]["original_first_use_runnable"] is not False
            or doc["user_approval_current_study_ref"] is not None
            or doc["owner_signed_source_lease_ref"] is not None
            or doc["train_seed_ids"] != []
            or any(doc["held_seed_ids_by_arm"].values())
            or any(doc["transfer_seed_ids_by_arm"].values())
            or doc["actual_source_interventions_this_gate"]!=0
            or doc["consumed_previous_seed_ids"]!=[996100,996101,996102,996103]
            or doc["max_source_interventions"]!=13_312):
        raise PermissionError("CVH06_UNAPPROVED_NEW_SOURCE_FIRST_USE_IS_DISARMED")
    return doc,prereg


def qualify():
    disarm,prereg=source_disarm_check()
    controls={"native":PublicEarnedPolicy(min_support=2),
              "conventional":FourCellEarnedPolicy(min_support=2)}
    result_by_arm={}
    for name,policy in controls.items():
        events=[]
        per_episode=[]
        for toy_seed in (1,2,3,4,5,6):
            policy,rows=toy_episode(toy_seed,policy)
            events.extend(rows)
            per_episode.append({
                "mock_seed":toy_seed,"public_action_count":len(rows),
                "already_witnessed_reward_count":sum(r.reward for r in rows),
            })
        count=(policy.memory.seen if name=="native" else policy.seen)
        if count!=36 or sum(r["public_action_count"] for r in per_episode)!=36:
            raise AssertionError("CVH06_TWO_ARM_SOURCE_FREE_ACTION_BUDGET_MISMATCH")
        state=policy.snapshot()
        if type(policy).restore(state).snapshot()!=state:
            raise AssertionError("CVH06_MODEL_COLD_RESTORE_DRIFT")
        if name=="conventional":
            independent=independent_fourcell_public_batch(events)
            if policy.count!=independent[0] or policy.total!=independent[1]:
                raise AssertionError("CVH06_STRONG_PUBLIC_CONVENTIONAL_BATCH_MISMATCH")
        result_by_arm[name]={
            "mock_only":True,
            "source_original_reset_or_do_calls":0,
            "mock_episode_count":6,
            "mock_action_count":count,
            "model_checkpoint_sha256":sha256(state).hexdigest(),
            "model_checkpoint_bytes":len(state),
            "public_episode_action_counts":[r["public_action_count"] for r in per_episode],
            "public_episode_reward_counts":[r["already_witnessed_reward_count"] for r in per_episode],
        }
    result={
        "schema":"yggdrasil.cvh06.unapproved-source-boundary-strong-control-qualification.v1",
        "source":"PURE_SYNTHETIC_PUBLIC_RECORD_IO_ONLY",
        "preregistered_future_original_source_sha":disarm["source_sha"],
        "qualified_previous_source_provenance_fkp26":43930489602,
        "previous_qualified_native_source_sha":prereg["parent"]["head"],
        "original_upstream_import_calls":0,
        "original_env_constructor_calls":0,
        "original_env_reset_calls":0,
        "original_env_do_calls":0,
        "original_first_use_authorized":False,
        "source_seed_lists_reserved":False,
        "source_cohorts_touched":[],
        "owner_runtime_modified":False,
        "mock_only":True,
        "mock_action_budgets_equal_across_arms":True,
        "native_model_original_unchanged":True,
        "source_free_strong_conventional_exact_batch_parity":True,
        "cold_snapshot_both_arms_exact":True,
        "fully_trained_recurrent_science_control_ready":False,
        "scientific_pass":False,
        "native_accepted":False,
        "deployment":False,
        "classification":"SOURCE_FREE_FOURCELL_CONVENTIONAL_CONTROL_READY_BUT_SCIENCE_FIRST_USE_BLOCKED",
        "arms":result_by_arm,
    }
    result["receipt_sha256"]=sha256(_canonical(result)).hexdigest()
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-json",required=True)
    cfg=p.parse_args()
    report=qualify()
    path=Path(cfg.output_json)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print("CVH06_SOURCEFREE_CONTROL_QUALIFICATION="+json.dumps(
        {"classification":report["classification"],
         "mock_actions_per_arm":[report["arms"][k]["mock_action_count"]
             for k in ("native","conventional")],
         "actual_source_actions":0,
         "receipt_sha256":report["receipt_sha256"],
         "scientific_pass":False},sort_keys=True,separators=(",",":")),
         flush=True)


if __name__=="__main__":
    main()
