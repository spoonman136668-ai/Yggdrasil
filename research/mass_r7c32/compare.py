"""C32 science repeat: actual original-world actions, no hypothetical benefits."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from research.native.itd02.r1.native_policy import canonical
from research.mass_r7c32.run import P

def strip_nondeterministic(x):
    return {k:v for k,v in x.items() if k!="resources"}

def compare(a,b):
    if canonical(strip_nondeterministic(a))!=canonical(strip_nondeterministic(b)):
        raise ValueError("C32_TWO_INDEPENDENT_ORIGINAL_RUNS_DIVERGED")
    proto=P
    for x in (a,b):
        if(x.get("schema")!=proto["schema"] or x.get("gate")!="ITD02-C32"
           or x.get("source_DEV_or_protected_episodes")!=0
           or x.get("scientific_first_use") is not False
           or x.get("scientific_accepted") is not False
           or x.get("all_actor_actions_physically_executed") is not True
           or x.get("prior_original_native_R3_modified") is not False):
            raise ValueError("C32_UNQUALIFIED_ORIGINAL_SOURCE_RESULT")
        records=x["original_world_episode_records"]
        expected=len(proto["actors"])*sum(len(s) for s in proto["prospectivePublicFIT"]["families"].values())
        if len(records)!=expected:raise ValueError("C32_MISSING_REAL_SOURCE_EPISODE")
        found=set()
        for r in records:
            key=(r["arm"],r["family"],r["seed"])
            if (key in found or r["arm"] not in proto["actors"]
                or r["seed"] not in proto["prospectivePublicFIT"]["families"].get(r["family"],[])
                or r["steps"]!=len(r["source_actual_actions"])
                or r["steps"]>proto["prospectivePublicFIT"]["maxActionsPerEpisode"]
                or not r["cold_step_three"]["restored_in_fresh_process"]):
                raise ValueError("C32_INVALID_PHYSICAL_EPISODE_CUSTODY")
            found.add(key)
            from hashlib import sha256
            if sha256(canonical(r["source_actual_actions"])).hexdigest()!=r["source_trace_sha256"]:
                raise ValueError("C32_INVALID_PHYSICAL_ACTION_TRACE_DIGEST")
            for t,event in enumerate(r["source_actual_actions"]):
                if(event["t"]!=t or event["executed"] not in (0,1,2)
                   or event["original_r3_proposed"] not in (0,1,2)
                   or set(event["before"])!=set(proto["prospectivePublicFIT"]["observationFields"])
                   or set(event["after"])!=set(proto["prospectivePublicFIT"]["observationFields"])):
                    raise ValueError("C32_INVALID_ACTUAL_SOURCE_SELECTED_EVENT")
                if t and event["before"]!=r["source_actual_actions"][t-1]["after"]:
                    raise ValueError("C32_DISCONTIGUOUS_SOURCE_ACTION_CHAIN")
                if event["executed"]!=event["original_r3_proposed"] and (
                    event["executed"] not in (0,1) or
                    event["original_r3_proposed"] not in (0,1)):
                    raise ValueError("C32_ORIGINAL_R3_FORWARD_WAS_CHANGED")
    positive=(a["verdict"]==proto["acceptance"]["positive"])
    return {"schema":"itd02.c32.original-source-independent-repeat-v1",
        "science_identical":True,
        "source_A":a["verdict"],"source_B":b["verdict"],
        "result":("REPEATED_BOUNDED_C32_SOURCE_ACTION_GAIN_NOT_TRANSFER"
                  if positive else "NO_REPEATABLE_C32_REAL_SOURCE_NATIVE_EFFECT_DECISION_ADVANTAGE"),
        "original_physical_actions_actually_executed":True,
        "scientific_first_use":False,"scientific_accepted":False}

def main():
    parser=argparse.ArgumentParser()
    for name in ("first","second","output"):
        parser.add_argument("--"+name,type=Path,required=True)
    a=parser.parse_args()
    out=a.output
    if out.exists() or not out.parent.is_dir():raise ValueError("C32_COMPARISON_NOT_FRESH")
    v=compare(json.loads(a.first.read_text()),json.loads(a.second.read_text()))
    out.write_bytes(canonical(v)+b"\n")
    print("C32_INDEPENDENT_PHYSICAL_SOURCE_RESULT="+v["result"])
    print("C32_ORIGINAL_SOURCE_TWO_PROCESS_PARITY=PASS")

if __name__=="__main__":main()
