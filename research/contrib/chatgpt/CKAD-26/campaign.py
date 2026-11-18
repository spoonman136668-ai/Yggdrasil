"""CKAD26: independent action-conditioned Bayesian change detector.

Run exactly the unchanged native CKAD23 public-action learner on frozen new
synthetic draw namespaces. Give identical live public consequences to native,
causal-conditional Beta-Binomial, unconditional Beta-Binomial, and label-free
random alarms. Only the native learner chooses interventions. Candidate
detectors are SHADOW observers: no controller or model can adopt their scores.
"""
import argparse
from fractions import Fraction
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
import time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
CK25=HERE.parent/"CKAD-25"
CK23=HERE.parent/"CKAD-23"
CK22=HERE.parent/"CKAD-22"
SOURCE=HERE.parent/"CKAD-20"/"synthetic_world.py"
sys.path.insert(0,str(ROOT))
if hasattr(sys,"set_int_max_str_digits"):sys.set_int_max_str_digits(0)


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    obj=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

BASE=load("ckad26_parent_campaign",CK25/"campaign.py")
B=BASE.B
LEGACY=BASE.LEGACY
REFERENCE=BASE.BASE
from yggdrasil.native_context_basis import canonical,digest
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner,EXPERIENCE_SOURCE
from causal_evidence import ChangeEvidence

PARENT="a4c6d82727256306c06c20bf28d65bf888f7e671"
SOURCE_SHA="20cb67447988eb0deff287f4e42e5b61d46d4763a920db5c79852c9b07e163ef"
SEEDS=(101,202,303)
SCHEDULES=("transition_flip","reward_flip","no_change")
ARMS=("causal_bayes","unconditional_bayes","native_joint","random_alarm")


def need(ok,why):
    if not ok:raise ValueError("CKAD26_"+why)


def semantic(d):
    def norm(x):
        if isinstance(x,dict):
            return {k:norm(v) for k,v in x.items()
                    if k not in ("stable_sha256","wall_seconds","source_candidate_sha")}
        if isinstance(x,list):return [norm(z) for z in x]
        return x
    return digest(canonical(norm(d)))


def run_case(name,seed,out):
    start=time.monotonic()
    protocol=json.loads((HERE/"prereg.json").read_bytes())
    need(protocol["schema"]=="yggdrasil.ckad26.causal-change-bayes-prereg.v1" and
         protocol["parent_commit"]==PARENT and
         protocol["source_generator_sha256"]==SOURCE_SHA and
         protocol["source_cohort"]=="ckad26-causal-change" and
         protocol["seeds"]==list(SEEDS),"FROZEN_PROTOCOL")
    need(digest(SOURCE.read_bytes())==SOURCE_SHA==EXPERIENCE_SOURCE,
         "UNCHANGED_GENERATOR")
    need(seed in SEEDS and name in SCHEDULES,"SCOPED_CASE")
    family=protocol["schedules"][name]
    offset=family["offset"]
    phases=family["phases"]
    need(len(phases)==4 and
         (len({tuple(v) for v in phases})==1 if name=="no_change"
          else len({tuple(v) for v in phases})==2),
         "PHASES")
    parent_path=CK22/f"seed-{seed}-expanded-native.json"
    raw=parent_path.read_bytes()
    original_protocol=json.loads((CK23/"prereg.json").read_bytes())
    pinned=original_protocol["parent_pins"][str(seed)]
    need(digest(raw)==pinned,"PINNED_448_PARENT")
    ancestor=NativeCumulativeLearner.restore(raw,pinned)
    legacy,historical=B.legacy_and_experience(raw)
    initial=historical["episodes"]
    need(len(initial)==448,"HISTORICAL_SUPPORT")
    native=ancestor.begin_experience_stream()
    reference=REFERENCE.Monitor(initial)
    detectors={arm:ChangeEvidence(arm,f"{name}/{seed}") for arm in ARMS}
    records=[]
    source_seed=seed+offset
    for index in range(192):
        kind,regime=phases[index//48]
        world=B.make_episode(cohort=protocol["source_cohort"],
                             seed=source_seed,index=index,
                             family=kind,regime=regime)
        views=B.public_views(world)
        view=views[0]
        if index%4==3:
            decision=LEGACY.planned_rollout(world,native.experience_context_plan(view))
        else:
            pre=native
            decision=B.rollout(world,
                   lambda _state:pre.experience_context_explore(view),
                   lambda _state,first,state:pre.experience_context_explore(view,first,state))
        token=REFERENCE.event_id(protocol["source_cohort"],source_seed,index,"active")
        t=448+index+1
        x1,s2,x2,y=(decision[k] for k in ("x1","s2","x2","y"))
        row={"public_state":view[0],"first_action":x1,
             "next_state":s2,"second_action":x2,"reward":y}
        for detector in detectors.values():
            detector.observe(token,t,row)
        records.append({"event_id":token,"evidence_count":t,
                        "public_views":[list(views[0]),list(views[1])],**row})
        native=B.admit(native,token,views,decision)
        reference.add(B.retain_event(token,views,decision))
        reference.assert_native(native)
    detectors["native_joint"].alarms=[
        {"event_id":z["event_id"],"evidence_count":z["evidence_count"],
         "evidence":"joint","score":z["score"]} for z in reference.detections
    ]
    # Shadow detectors did not mutate source actions, native context, or prior memory.
    learned=native.consolidate_experience()
    bytes_=learned.checkpoint()
    pin=digest(bytes_)
    recovered=NativeCumulativeLearner.restore(bytes_,pin)
    need(recovered.checkpoint()==bytes_,"COLD_CHECKPOINT")
    new_legacy,new_experience=B.legacy_and_experience(bytes_)
    rows=new_experience["episodes"]
    need(new_legacy==legacy and rows[:448]==initial and len(rows)==640 and
         len({e[0] for e in rows})==640 and
         [e[0] for e in rows[448:]]==[r["event_id"] for r in records],
         "IMMUTABLE_WITNESSES")
    need(ancestor.checkpoint()==raw,"PARENT_BYTES_IMMUTABLE")
    out.mkdir(parents=True,exist_ok=True)
    filename=f"{name}-{seed}-native.json"
    (out/filename).write_bytes(bytes_)
    proof={
      "schema":"yggdrasil.ckad26.causal-change-bayes.case.v1",
      "schedule":name,"seed":seed,"source_seed":source_seed,
      "source_cohort":protocol["source_cohort"],
      "source_generator_sha256":SOURCE_SHA,"parent_commit":PARENT,
      "parent_checkpoint_sha256":pinned,"final_checkpoint_name":filename,
      "final_checkpoint_sha256":pin,"final_checkpoint_bytes":len(bytes_),
      "witnesses_before":448,"witnesses_after":640,
      "new_source_episodes":192,"chosen_intervention_actions":384,
      "trace":records,
      "alarms":{arm:detector.alarms for arm,detector in detectors.items()},
      "original_native_joint":reference.detections,
      "parent_immutable":True,"cold_restore_exact":True,
      "source_actions_original":0,"protected_first_use":0,"held_updates":0,
      "scientific_pass":False,"accepted_native":False,"deployment":"NONE"
    }
    proof["stable_sha256"]=semantic(proof)
    proof["wall_seconds"]=time.monotonic()-start
    need(proof["wall_seconds"]<protocol["budget"]["max_wall_seconds_per_case"],
         "FROZEN_WALL_BUDGET")
    (out/"case-result.json").write_text(json.dumps(proof,sort_keys=True,indent=2)+"\n")
    return proof


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--schedule",required=True,choices=SCHEDULES)
    p.add_argument("--seed",required=True,type=int,choices=SEEDS)
    p.add_argument("--output-directory",required=True,type=Path)
    a=p.parse_args()
    z=run_case(a.schedule,a.seed,a.output_directory)
    print(json.dumps({"schedule":a.schedule,"seed":a.seed,
        "alarms":{arm:[r["evidence_count"]-448 for r in items]
                  for arm,items in z["alarms"].items()},
        "stable_sha256":z["stable_sha256"],"wall_seconds":z["wall_seconds"]},
        sort_keys=True))
