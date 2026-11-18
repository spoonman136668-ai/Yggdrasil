"""CKAD26 source-free independent replay, original-causal-checkpoint custody.

Reopen nine full persisted native models and action-consequence receipts.
Verify all exact source identities, original 448 witness prefixes, 192 new
interventions, original source-free cold restoration and frozen detection
scores, without generating any additional source episode.
"""
import gzip
from itertools import product
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
PARENT=HERE.parent/"CKAD-22"
sys.path.insert(0,str(ROOT))
if hasattr(sys,"set_int_max_str_digits"):sys.set_int_max_str_digits(0)
import audit
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner


def need(b,reason):
    if not b:raise ValueError("CKAD26_INDEPENDENT_"+reason)


def unpack(name):
    raw=(HERE/name).read_bytes()
    need(raw[:3]==b"\x1f\x8b\x08" and raw[4:8]==b"\x00\x00\x00\x00",
         "DETERMINISTIC_GZIP")
    return gzip.decompress(raw)


def run():
    record=json.loads((HERE/"result.json").read_bytes())
    provenance=json.loads((HERE/"provenance.json").read_bytes())
    policy=audit.protocol()
    cases=[]
    custody=[]
    for name,seed in product(audit.SCHEDULES,audit.SEEDS):
        stem=f"{name}-{seed}"
        proof=json.loads(unpack(stem+"-proof.json.gz"))
        raw=unpack(stem+"-native.json.gz")
        evidence=audit.validate_case(proof,policy)
        digest=audit.sha(raw)
        need(digest==proof["final_checkpoint_sha256"] and
             len(raw)==proof["final_checkpoint_bytes"],"EXACT_CHECKPOINT_SHA")
        previous=(PARENT/f"seed-{seed}-expanded-native.json").read_bytes()
        need(audit.sha(previous)==proof["parent_checkpoint_sha256"],
             "ORIGINAL_PINNED_PARENT")
        old=json.loads(previous)
        new=json.loads(raw)
        old_episodes=json.loads(old["experience_ascii"])["episodes"]
        new_episodes=json.loads(new["experience_ascii"])["episodes"]
        need(len(old_episodes)==448 and
             len(new_episodes)==640 and
             new_episodes[:448]==old_episodes and
             len({event[0] for event in new_episodes})==640,
             "RETAINED_WITNESS_PREFIX")
        need({k:v for k,v in old.items() if k!="experience_ascii"}==
             {k:v for k,v in new.items() if k!="experience_ascii"},
             "UNRELATED_NATIVE_SUBSTRATE")
        for native,public in zip(new_episodes[448:],proof["trace"]):
            need(native[0]==public["event_id"] and
                 [native[2],native[3],native[4],native[5]]==
                 [public["first_action"],public["next_state"],
                  public["second_action"],public["reward"]] and
                 native[1]==public["public_views"],
                 "ACTUAL_PUBLIC_CAUSAL_RECEIPT")
        recovered=NativeCumulativeLearner.restore(raw,digest)
        need(recovered.checkpoint()==raw,"COLD_NATIVE_CHECKPOINT")
        info=recovered.info()["episode_experience"]
        need(info["count"]==640 and
             info["stream"]["stream_start"]==448 and
             info["stream"]["detections"]==proof["original_native_joint"],
             "ACTUAL_ORIGINAL_NATIVE_DETECTOR")
        cases.append(proof)
        custody.append({"schedule":name,"seed":seed,"checkpoint_sha256":digest,
                        "old_witnesses":448,"new_witnesses":192,
                        "cold_restored":True})
    independently=audit.aggregate(cases)
    need(independently==record and
         provenance["stable_result_sha256"]==record["stable_sha256"] and
         len(provenance["checkpoint_custody"])==9,
         "INDEPENDENT_REPRODUCTION")
    need(independently["scientific_pass"] is False and
         independently["accepted_native"] is False and
         independently["deployment"]=="NONE" and
         independently["shadow_only"] is True and
         independently["policy_reward_claim"] is False,
         "SCIENTIFIC_NONPROMOTION")
    return {"independent_audit":"PASS",
            "classification":record["classification"],
            "stable_sha256":record["stable_sha256"],
            "frozen_gates":record["frozen_gates"],
            "checkpoint_receipts":custody,
            "scientific_pass":False,"deployment":"NONE"}

if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True))
