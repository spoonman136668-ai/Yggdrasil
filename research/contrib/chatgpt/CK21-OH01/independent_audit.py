"""Independent CK21-OH01 trace recreation; never uses campaign planner."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"CKAD-20"))
from synthetic_world import make_episode,rollout

SOURCE_PIN="20cb67447988eb0deff287f4e42e5b61d46d4763a920db5c79852c9b07e163ef"
PARENT_PIN="c986dd9dc63ace08f4a0185f80258099971e22ff50884cf6a7ec58e9b1ad650e"
SEEDS=(101,202,303)
WORLD=(("invariant",0),("context_switch",1),("context_switch",0),
       ("invariant",0),("context_switch",1),("terminal_switch",1))
SCHEMA="yggdrasil.ck21oh01.oracle-headroom.result.v1"

def canonical(d):
    return json.dumps(d,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode("ascii")

def pin(d):
    return sha256(d).hexdigest()

def require(b,message):
    if not b:raise ValueError("CK21_OH01_AUDIT_"+message)

def replay_reference(episode,family,regime):
    # Independent simple public source-informed policy: no hidden/noise peeking
    def first(s1):
        return regime^(s1 if family=="context_switch" else 0)
    def second(s1,a1,s2):
        return s1^s2^(a1^regime if family=="terminal_switch" else 0)
    return rollout(episode,first,second)

def audit(d):
    require(d.get("schema")==SCHEMA,"SCHEMA")
    stable={k:v for k,v in d.items() if k not in ("stable_sha256","whole_wall_seconds")}
    require(pin(canonical(stable))==d.get("stable_sha256"),"STABLE_SHA")
    require(d.get("source_fixture_sha256")==SOURCE_PIN and
            d.get("historical_ckad21_result_sha256")==PARENT_PIN,"SOURCE")
    require((d.get("scientific_pass"),d.get("accepted_native"),d.get("deployment"))==
            (False,False,"NONE"),"AUTHORITY")
    require(all(d.get(k)==0 for k in
               ("new_training_updates","held_training_updates","original_source_actions","protected_first_use")),
            "SCOPE")
    require(d["exact_expectation"]==[113,128] and
            d["returning"]["expected_optimum_successes"]==[1017,2],"EXACT_THEORY")
    parent=json.loads((HERE.parent/"CKAD-21"/"result.json").read_bytes())
    require(parent["stable_sha256"]==PARENT_PIN,"ORIGINAL_PIN")
    require(pin((HERE.parent/"CKAD-20"/"synthetic_world.py").read_bytes())==SOURCE_PIN,
            "GENERATOR_PIN")
    require(len(d["by_seed"])==3 and len(d["by_session"])==6,"CASE_COUNT")
    combined=[]
    for item in d["by_seed"]:
        seed=item["seed"]
        require(seed in SEEDS and seed not in [v["seed"] for v in combined],"SEED_DUPLICATE")
        old=next(x for x in parent["seeds"] if x["seed"]==seed)
        require(len(item["sessions"])==6,"SESSION_COUNT")
        for index,(family,regime) in enumerate(WORLD):
            row=item["sessions"][index]
            require((row["session"],row["family"],row["regime"],row["episodes"])==
                    (index,family,regime,96),"COHORT")
            historical=old["sessions"][index]["evaluation"]
            require(row["active_reward"]==historical["context_active"]["reward_sum"] and
                    row["pooled_reward"]==historical["pooled_replay"]["reward_sum"] and
                    row["random_reward"]==historical["context_random"]["reward_sum"],
                    "HISTORICAL_REWARD")
            evidence=[]
            for episode_index in range(96):
                episode=make_episode(cohort=f"ckad21-held-{index}",seed=seed,
                                     index=episode_index,family=family,regime=regime)
                actual=replay_reference(episode,family,regime)
                evidence.append([actual[k] for k in ("s1","x1","s2","x2","y")])
            require(sum(e[-1] for e in evidence)==row["oracle_reward"],"EXECUTED_REFERENCE")
            require(pin(canonical(evidence))==row["oracle_trace_sha256"],"TRACE_SHA")
        combined.append(item)
    for i,(family,regime) in enumerate(WORLD):
        row=d["by_session"][i]
        require((row["session"],row["family"],row["regime"],row["episodes"])==
                (i,family,regime,288),"SESSION_TOTAL_SCOPE")
        for kind in ("oracle_reward","active_reward","pooled_reward","random_reward"):
            require(row[kind]==sum(s["sessions"][i][kind] for s in combined),"TOTAL_SCORE")
    returning=d["returning"]
    for kind in ("oracle_reward","active_reward","pooled_reward","random_reward"):
        require(returning[kind]==d["by_session"][0][kind]+d["by_session"][3][kind],"RETURNING_SCORE")
    require(returning["active_reward"]==497 and returning["pooled_reward"]==477,"CKAD21_BASE")
    require(returning["total_episodes"]==576 and returning["required_above_pooled"]==29 and
            returning["required_absolute_successes"]==506,"FROZEN_THRESHOLD")
    require(returning["oracle_minus_pooled"]==returning["oracle_reward"]-477 and
            returning["oracle_minus_active"]==returning["oracle_reward"]-497,
            "ORACLE_HEADROOM")
    met=returning["oracle_reward"]>=506
    require(returning["reference_oracle_meets_frozen_5pp_margin"] is met and
            d["classification"]==
            ("ORACLE_REFERENCE_ATTAINED_5PP" if met else "ORACLE_REFERENCE_BELOW_5PP"),
            "FROZEN_INTERPRETATION")
    return {"independent_audit":"PASS","episodes":1728,
            "stable_sha256":d["stable_sha256"],"returning":returning,
            "classification":d["classification"],"scientific_pass":False}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--result",type=Path,required=True)
    args=p.parse_args()
    print(json.dumps(audit(json.loads(args.result.read_text())),sort_keys=True))
