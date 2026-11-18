"""Independent source-custody, matched-control, and frozen-gate CKAD23 audit.

This module reads previously executed native development receipts only.
It does not invoke a source generator, adapt a learner, or change checkpoints.
"""
import argparse
from collections import defaultdict
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys

if hasattr(sys,"set_int_max_str_digits"):sys.set_int_max_str_digits(0)
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
CK22=HERE.parent/"CKAD-22"
SOURCE_COMMIT="f04cfcac2aa07806a6b942d968119de87bfb6aaf"
SOURCE_STABLE="4b20ef3b9229eddfd509e5897e6aa8f8d5226288ab331c4a98f8a7bc46fbccc2"
SOURCE_FIXTURE="20cb67447988eb0deff287f4e42e5b61d46d4763a920db5c79852c9b07e163ef"
PREREG="43bf1854d0c12c3dc26a3010c3ee9d945bece28b"
PARENTS=(101,202,303)
ENVS=(1009,1013,1019,1021,1031,1033,1039,1049)
WORLDS=("conjunctive_terminal","interaction_gate")
ARMS=("novel_active","retrieval_only","novel_random",
      "full_beta","trailing_mle","pooled_replay","exact_mixture")
OS_NAMES=("ubuntu-latest","windows-2022")

def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode("ascii")

def digest(raw):
    return sha256(raw).hexdigest()

def need(condition,why):
    if not condition:raise ValueError("CKAD23_AUDIT_"+why)

def sha_check(s):
    return type(s) is str and len(s)==64 and all(c in "0123456789abcdef" for c in s)

def fpair(f):
    return [f.numerator,f.denominator]

def signflip(seq):
    need(len(seq)==3 and all(type(a) is int for a in seq),"SIGNFLIP_GROUPS")
    target=abs(sum(seq))
    count=sum(abs(sum(sign*v for sign,v in zip(sig,seq)))>=target
              for sig in product((-1,1),repeat=3))
    return fpair(Fraction(count,8))

def audit_shard(d):
    need(d.get("schema")=="yggdrasil.ckad23.compositional-disjoint-shard.v1","SHARD_SCHEMA")
    need(d.get("source_parent")==SOURCE_COMMIT and
         d.get("source_sha256")==SOURCE_FIXTURE and
         d.get("original_ckad22_result_sha256")==SOURCE_STABLE,"SHARD_SOURCE")
    need(d.get("scientific_pass") is False and d.get("accepted_native") is False
         and d.get("deployment")=="NONE","SHARD_NO_PROMOTION")
    need(d.get("original_source_actions")==0 and d.get("protected_first_use")==0,"SHARD_FIRST_USE")
    stable={k:v for k,v in d.items() if k not in ("stable_sha256","wall_seconds")}
    need(d.get("stable_sha256")==digest(canonical(stable)),"SHARD_SEMANTIC_PIN")
    parent,half=d["parent"],d["half"]
    need(type(parent) is int and parent in PARENTS and type(half) is int and half in (0,1),"SHARD_ID")
    subset=ENVS[:4] if half==0 else ENVS[4:]
    need(d["environment_seeds"]==list(subset) and len(d["cases"])==8
         and d["synthetic_probe_updates"]==128,"SHARD_SCOPE")
    return parent,half

def read_original():
    d=json.loads((CK22/"result.json").read_bytes())
    need(d["stable_sha256"]==SOURCE_STABLE and
         d["source_candidate_sha"]=="de1c3daac160c0ef24f352ce238558b1356c06dd",
         "CKAD22_ORIGINAL_SOURCE")
    return {z["seed"]:z["sha256"] for z in d["final_checkpoints"]}

def validate_case(row,parent,env,world,parent_pins):
    need((row["parent"],row["environment_seed"],row["world"])==(parent,env,world),
         "CASE_IDENTITY")
    need(row["composite_seed"]==parent*100000+env,"CASE_SOURCE_SEED")
    need(row["parent_checkpoint_sha256"]==parent_pins[parent],"CASE_PARENT_PIN")
    need(row["probes"]==16 and row["before_count"]==448 and
         row["after_count"]==464 and row["new_held_training_updates"]==0,
         "CASE_PROBES")
    need(row["novel_candidate_prior"]==[1,8],"NEW_PRIOR")
    mass=row["novel_candidate_final_weight"]
    need(type(mass) is list and len(mass)==2 and
         all(type(v) is int for v in mass) and
         mass[1]>0 and 0<=mass[0]<=mass[1],"POSTERIOR_MASS")
    need(sha_check(row["novel_checkpoint_sha256"]) and
         sha_check(row["active_receipt_sha256"]),"RECEIPT_PINS")
    need(set(row["evaluation"])=={world,"familiar"},"SCORED_SURFACES")
    for surface in (world,"familiar"):
        e=row["evaluation"][surface]
        need(e["denominator"]==48 and set(e["successes"])==set(ARMS)
             and set(e["trace_sha256"])==set(ARMS),"EVALUATION_PROTOCOL")
        for arm in ARMS:
            z=e["successes"][arm]
            need(type(z) is int and 0<=z<=48 and sha_check(e["trace_sha256"][arm]),
                 "SCORE_OR_TRACE")
        need(e["successes"]["novel_active"]==e["successes"]["exact_mixture"] and
             e["trace_sha256"]["novel_active"]==e["trace_sha256"]["exact_mixture"],
             "INDEPENDENT_MIXTURE_PARITY")

def combine(shards):
    original=read_original()
    need(len(shards)==6,"SIX_SHARDS_REQUIRED")
    keys=set()
    per_case=[]
    for d in shards:
        key=audit_shard(d)
        need(key not in keys,"DUPLICATE_SHARD")
        keys.add(key)
        subset=ENVS[:4] if key[1]==0 else ENVS[4:]
        expected=[(seed,world) for seed in subset for world in WORLDS]
        for row, (env,world) in zip(d["cases"],expected,strict=True):
            validate_case(row,key[0],env,world,original)
            per_case.append(row)
    need(keys==set(product(PARENTS,(0,1))) and len(per_case)==48,"ALL_SHARDS")
    by_world={}
    by_env={}
    group_diff={}
    for world in WORLDS:
        cells=[row for row in per_case if row["world"]==world]
        need(len(cells)==24,"WORLD_CASES")
        totals={}
        for surface in (world,"familiar"):
            totals[surface]={arm:sum(case["evaluation"][surface]["successes"][arm]
                                 for case in cells) for arm in ARMS}
        deltas={k:totals[world]["novel_active"]-totals[world][k]
                for k in ("retrieval_only","full_beta","trailing_mle",
                          "novel_random","pooled_replay")}
        by_world[world]={"held_episodes":1152,"familiar_held_episodes":1152,
                         "scores":totals,"novel_deltas":deltas}
        group_diff[world]={
          k:[sum(x["evaluation"][world]["successes"]["novel_active"]-
                 x["evaluation"][world]["successes"][k]
                 for x in cells if x["parent"]==parent) for parent in PARENTS]
          for k in ("retrieval_only","full_beta","trailing_mle","novel_random")
        }
        for env in ENVS:
            subset=[c for c in cells if c["environment_seed"]==env]
            need(len(subset)==3,"ENV_GROUP_SIZE")
            by_env.setdefault(str(env),{})[world]={
                "novel_minus_retrieval":sum(
                    x["evaluation"][world]["successes"]["novel_active"]-
                    x["evaluation"][world]["successes"]["retrieval_only"] for x in subset),
                "novel_minus_beta":sum(
                    x["evaluation"][world]["successes"]["novel_active"]-
                    x["evaluation"][world]["successes"]["full_beta"] for x in subset)
            }
    robust_counts={world:sum(by_env[str(seed)][world]["novel_minus_retrieval"]>0
                            for seed in ENVS) for world in WORLDS}
    gates={}
    for world in WORLDS:
        t=by_world[world]
        gates[f"{world}_vs_retrieval"]=(t["novel_deltas"]["retrieval_only"]>=35)
        gates[f"{world}_vs_full_beta"]=(t["novel_deltas"]["full_beta"]>=0)
        gates[f"{world}_seed_robustness"]=(robust_counts[world]>=6)
        familiar=t["scores"]["familiar"]
        gates[f"{world}_prior_retention"]=(familiar["novel_active"]>=864 and
             Fraction(familiar["novel_active"]-familiar["retrieval_only"],1152)>=-Fraction(1,20))
    outcome={
      "schema":"yggdrasil.ckad23.compositional-transfer.result.v1",
      "classification":"DEVELOPMENT_GO" if all(gates.values()) else "DEVELOPMENT_NO_GO",
      "parent_sha":SOURCE_COMMIT,"parent_stable_sha256":SOURCE_STABLE,
      "original_source_sha256":SOURCE_FIXTURE,
      "prereg_commit":PREREG,
      "previously_frozen_checkpoints":original,
      "independent_trained_parent_groups":3,
      "independent_exogenous_namespace_seeds":8,
      "contexts_trained":48,"new_probes":768,
      "new_world_held_episodes":2304,"familiar_held_episodes":2304,
      "unfamiliar_structures":list(WORLDS),
      "by_world":by_world,"by_environment_seed":by_env,
      "by_parent_group":group_diff,
      "seed_exact_two_sided_signflip_p":{
           world:{k:signflip(v) for k,v in group_diff[world].items()} for world in WORLDS},
      "seed_robustness_positive_counts":robust_counts,
      "frozen_gates":gates,
      "interpretation":"Development synthetic causal-family first exposure with only 3 independent retained-model parents; eight exogenous namespaces do not create eight independent trained replicas. Source rules were handcrafted by the evaluator, not inferred from arbitrary real worlds. Exact mixture matches a fully specified conventional control, not architecture superiority.",
      "synthetic_new_source_family_first_use":True,
      "protected_first_use":0,"original_source_actions":0,"held_training_updates":0,
      "accepted_native":False,"scientific_pass":False,"deployment":"NONE"
    }
    outcome["stable_sha256"]=digest(canonical(outcome))
    return outcome

def load_artifact_dir(root):
    records={}
    for p in root.rglob("result.json"):
        name=p.parent.name
        parts=name.split("-")
        # Expected ckad23-{linux|windows}-{parent}-{half}-proof, but GitHub artifact names use OS tokens.
        need(name.startswith("ckad23-") and name.endswith("-proof"),"ARTIFACT_NAME")
        if "ubuntu-latest" in name:os="ubuntu-latest"
        elif "windows-2022" in name:os="windows-2022"
        else:raise ValueError("CKAD23_AUDIT_ARTIFACT_OS")
        d=json.loads(p.read_text())
        key=(os,d["parent"],d["half"])
        need(key not in records,"ARTIFACT_DUPLICATE")
        records[key]=d
    need(len(records)==12,"TWELVE_OS_ARTIFACTS")
    for parent,half in product(PARENTS,(0,1)):
        a,b=records[("ubuntu-latest",parent,half)],records[("windows-2022",parent,half)]
        need(audit_shard(a)==audit_shard(b),"OS_SHARD_ID")
        need(a["stable_sha256"]==b["stable_sha256"],"OS_SEMANTIC_DRIFT")
        need({k:v for k,v in a.items() if k!="wall_seconds"}==
             {k:v for k,v in b.items() if k!="wall_seconds"},"OS_SHARD_DATA_DRIFT")
    return records

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--artifact-root",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    a=load_artifact_dir(args.artifact_root)
    records=[a[("ubuntu-latest",p,h)] for p,h in product(PARENTS,(0,1))]
    out=combine(records)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"classification":out["classification"],"frozen_gates":out["frozen_gates"],
                      "seed_robustness_positive_counts":out["seed_robustness_positive_counts"],
                      "by_world":out["by_world"],"stable_sha256":out["stable_sha256"]},sort_keys=True))

if __name__=="__main__":main()
