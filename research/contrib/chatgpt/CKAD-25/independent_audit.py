"""Independent, source-free CKAD25 final-model and alarm evidence audit.

Recompute all detector alarms and frozen gates from nine exact stored
public-probability traces. Restore each complete native checkpoint byte for
byte, verify the unchanged qualified 448-witness prefix and 192 fresh public
witnesses. Never execute another source episode or update a model.
"""
import gzip
from itertools import product
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
CK22=HERE.parent/"CKAD-22"
sys.path.insert(0,str(ROOT))
if hasattr(sys,"set_int_max_str_digits"):sys.set_int_max_str_digits(0)
import audit
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner


def require(condition,reason):
    if not condition:raise ValueError("CKAD25_INDEPENDENT_"+reason)


def unzip(name):
    p=HERE/name
    raw=p.read_bytes()
    require(raw[:3]==b"\x1f\x8b\x08" and raw[4:8]==b"\x00\x00\x00\x00",
            "DETERMINISTIC_GZIP")
    return gzip.decompress(raw)


def run():
    report=json.loads((HERE/"result.json").read_bytes())
    provenance=json.loads((HERE/"provenance.json").read_bytes())
    protocol=audit.protocols()
    cases=[]
    custody=[]
    for name,seed in product(audit.SCHEDULES,audit.SEEDS):
        stem=f"{name}-{seed}"
        proof=json.loads(unzip(stem+"-proof.json.gz"))
        raw=unzip(stem+"-native.json.gz")
        diagnosis=audit.validate_case(proof,protocol)
        sha=audit.sha(raw)
        require(sha==proof["final_checkpoint_sha256"] and
                len(raw)==proof["final_checkpoint_bytes"],"CHECKPOINT_BYTES")
        before=(CK22/f"seed-{seed}-expanded-native.json").read_bytes()
        require(audit.sha(before)==proof["parent_checkpoint_sha256"],
                "EXACT_PARENT")
        original=json.loads(before)
        original_memory=json.loads(original["experience_ascii"])
        state=json.loads(raw)
        episode_memory=json.loads(state["experience_ascii"])
        require(len(original_memory["episodes"])==448 and
                len(episode_memory["episodes"])==640 and
                episode_memory["episodes"][:448]==original_memory["episodes"] and
                len({row[0] for row in episode_memory["episodes"]})==640,
                "APPEND_ONLY_LEARNING")
        require({k:v for k,v in state.items() if k!="experience_ascii"}==
                {k:v for k,v in original.items() if k!="experience_ascii"},
                "LEGACY_SUBSTRATE_DRIFT")
        observed=episode_memory["episodes"][448:]
        require([row[0] for row in observed]==
                [row["event_id"] for row in proof["trace"]],
                "TRACE_TO_CHECKPOINT_WITNESSES")
        for row,record in zip(observed,proof["trace"]):
            require([row[2],row[3],row[4],row[5]]==
                    [record["first_action"],record["next_state"],
                     record["second_action"],record["reward"]],
                    "TRACE_ACTUAL_ACTION_CONSEQUENCE")
            require(list(row[1][0])==record["public_view"],"PUBLIC_VIEW_CUSTODY")
        model=NativeCumulativeLearner.restore(raw,sha)
        require(model.checkpoint()==raw,"EXACT_COLD_RESTORE")
        info=model.info()["episode_experience"]
        require(info["count"]==640 and
                info["stream"]["stream_start"]==448,
                "STORED_NATIVE_STREAM")
        require(info["stream"]["detections"]==
                proof["native_joint_detections"],"NATIVE_JOINT_DETECTIONS")
        cases.append(proof)
        custody.append({
            "schedule":name,"seed":seed,
            "sha256":sha,"bytes":len(raw),
            "old_witnesses":448,"new_witnesses":192,
            "unchanged_native_model":True,"cold_restore":True,
        })
    independent=audit.aggregate(cases)
    require(independent==report,"FROZEN_AGGREGATION")
    require(provenance["aggregate_semantic_sha256"]==report["stable_sha256"] and
            len(provenance["checkpoint_custody"])==9,
            "PROVENANCE")
    require(report["scientific_pass"] is False and
            report["accepted_native"] is False and
            report["deployment"]=="NONE" and
            report["shadow_only"] is True and
            report["policy_reward_claim"] is False,
            "SCIENCE_PROMOTION_BARRIER")
    return {
        "audit":"PASS",
        "classification":independent["classification"],
        "frozen_gates":independent["frozen_gates"],
        "stable_sha256":independent["stable_sha256"],
        "native_checkpoint_custody":custody,
        "scientific_pass":False,"accepted_native":False,"deployment":"NONE"
    }

if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True))
