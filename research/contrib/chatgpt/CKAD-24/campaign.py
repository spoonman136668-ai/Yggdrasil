"""CKAD24: adversarial phase-permutation development using unchanged CKAD23.

One retained native learner per parent seed/schedule. Only evaluation-side
source phase ordering and synthetic exogenous draw seed are changed. No phase
labels, future source bits, or change notices are passed into the learner.
"""
import argparse
from copy import deepcopy
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
CK23=HERE.parent/"CKAD-23"
CK20=HERE.parent/"CKAD-20"
sys.path.insert(0,str(ROOT))
if hasattr(sys,"set_int_max_str_digits"):sys.set_int_max_str_digits(0)

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    obj=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

BASE=load("ckad24_qualified_ckad23",CK23/"campaign.py")
BASE_PROTOCOL=CK23/"prereg.json"
PROTOCOL_PATH=HERE/"prereg.json"
PARENT_COMMIT="08fbe556d7ac134d3662f7003af5bc4430013ac1"
PARENT_CAMPAIGN_BLOB="e5be78562e8087fd98e1540062de01f15dbc3797"
SEEDS=(101,202,303)
SCHEDULES=("middle_swap","double_flip")

def need(condition,why):
    if not condition:raise ValueError("CKAD24_"+why)

def git(*args):
    return subprocess.check_output(["git",*args],cwd=ROOT,text=True).strip()

def pin_source(prereg):
    need(prereg["schema"]=="yggdrasil.ckad24.permuted-causal-changes.prereg.v1"
         and prereg["base_commit"]==PARENT_COMMIT
         and prereg["parent_ckad23_campaign_git_blob"]==PARENT_CAMPAIGN_BLOB,
         "PARENT_PROTOCOL")
    need(git("hash-object",str(CK23/"campaign.py"))==PARENT_CAMPAIGN_BLOB,
         "UNCHANGED_PARENT_CAMPAIGN")
    need(git("hash-object",str(CK23/"prereg.json"))=="2809b5c565e0cef55c06aabaf43e08f0f453235b",
         "UNCHANGED_PARENT_PREREG")
    need(sha256((CK20/"synthetic_world.py").read_bytes()).hexdigest()==
         prereg["source_generator_sha256"]==BASE.EXPERIENCE_SOURCE,
         "UNCHANGED_ORIGINAL_GENERATOR")
    need(prereg["seeds"]==list(SEEDS) and
         list(prereg["schedules"])==list(SCHEDULES),"FROZEN_SEEDS_SCHEDULES")
    need(prereg["per_case"]["checkpoints"]==list(range(0,193,16)) and
         prereg["per_case"]["true_phase_boundaries"]==[48,96,144],
         "FROZEN_CHANGE_POSITIONS")
    git("merge-base","--is-ancestor",PARENT_COMMIT,"HEAD")

def run_case(schedule,seed,out_dir):
    start=time.monotonic()
    p=json.loads(PROTOCOL_PATH.read_bytes())
    pin_source(p)
    need(schedule in SCHEDULES and seed in SEEDS,"CASE_SELECTORS")
    parent=json.loads(BASE_PROTOCOL.read_bytes())
    spec=p["schedules"][schedule]
    adapted=deepcopy(parent)
    adapted["phases"]=deepcopy(spec["phase_worlds"])
    adapted["source_seed_offset"]=spec["source_seed_offset"]
    need(adapted["parent"]==parent["parent"],"NO_PARENT_RETARGET")
    need(adapted["parent_pins"]==parent["parent_pins"] and
         adapted["budgets"]==parent["budgets"],"NO_PARENT_BUDGET_CHANGE")
    need(adapted["budgets"]["stream_episodes_per_seed_per_acquisition_arm"]==192
         and adapted["budgets"]["held_episodes_per_checkpoint"]==96,
         "FIXED_SOURCE_BUDGET")
    out_dir.mkdir(parents=True,exist_ok=True)
    trained=BASE.run_seed(seed,adapted,out_dir)
    raw=(out_dir/trained["final_checkpoint_name"]).read_bytes()
    need(sha256(raw).hexdigest()==trained["final_checkpoint_sha256"] and
         len(raw)==trained["final_checkpoint_bytes"],"EXACT_SAVED_CHECKPOINT")
    wall=time.monotonic()-start
    need(wall<p["budgets"]["max_wall_seconds_per_case"],"WALL_BUDGET")
    output={
       "schema":"yggdrasil.ckad24.permuted-causal-changes.case.v1",
       "classification":"DEVELOPMENT_PROOF_ONLY",
       "schedule":schedule,"phase_worlds":spec["phase_worlds"],
       "seed":seed,"source_seed":seed+spec["source_seed_offset"],
       "source_parent_sha":PARENT_COMMIT,
       "original_generator_sha256":p["source_generator_sha256"],
       "unchanged_parent_campaign_git_blob":PARENT_CAMPAIGN_BLOB,
       "seed_result":trained,
       "scientific_pass":False,"accepted_native":False,
       "original_source_actions":0,"protected_first_use":0,
       "held_updates":0,"deployment":"NONE",
    }
    output["stable_sha256"]=stable_sha256(output)
    output["wall_seconds"]=wall
    (out_dir/"case-result.json").write_text(
       json.dumps(output,indent=2,sort_keys=True)+"\n")
    return output

def stable_sha256(value):
    def normalize(x):
        if isinstance(x,dict):
            return {k:normalize(v) for k,v in x.items() if k not in
                    ("stable_sha256","wall_seconds","cpu_seconds",
                     "source_candidate_sha","peak_rss_bytes")}
        if isinstance(x,list):return [normalize(v) for v in x]
        return x
    return sha256(json.dumps(normalize(value),sort_keys=True,separators=(",",":"),
                            ensure_ascii=True,allow_nan=False).encode("ascii")).hexdigest()

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--schedule",choices=SCHEDULES,required=True)
    parser.add_argument("--seed",type=int,choices=SEEDS,required=True)
    parser.add_argument("--output-directory",type=Path,required=True)
    args=parser.parse_args()
    result=run_case(args.schedule,args.seed,args.output_directory)
    training=result["seed_result"]
    print(json.dumps({
        "classification":result["classification"],
        "schedule":args.schedule,"seed":args.seed,
        "detected_stream_counts":[v["evidence_count"]-448 for v
                                  in training["active_detections"]],
        "checkpoint_sha256":training["final_checkpoint_sha256"],
        "stable_sha256":result["stable_sha256"],
        "wall_seconds":result["wall_seconds"],
    },sort_keys=True))

if __name__=="__main__":main()
