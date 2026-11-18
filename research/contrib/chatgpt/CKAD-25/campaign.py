"""CKAD25: frozen factorized prequential surprise, shadow-only.

All policy actions, source public observations and checkpoint updates are
performed by the unchanged CKAD23 native learner. Four independent alarm
streams see the exact same evidence, before each model update. Their alarms
do not change the model, so reward gains are NOT claimed by this experiment.
"""
import argparse
from fractions import Fraction
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
CK22=HERE.parent/"CKAD-22"
SOURCE=HERE.parent/"CKAD-20"/"synthetic_world.py"
sys.path.insert(0,str(ROOT))
if hasattr(sys,"set_int_max_str_digits"):sys.set_int_max_str_digits(0)

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

BASE=load("ckad25_qualified_ckad23",CK23/"campaign.py")
B=BASE.B
LEGACY=BASE.LEGACY
from yggdrasil.native_context_basis import canonical,digest
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner,EXPERIENCE_SOURCE
SCHEDULES=("transition_only","reward_only","stationary_null")
SEEDS=(101,202,303)
PARENT="4ecc1144b1c2a3af388734fbd11a619c2cd50498"
SOURCE_SHA="20cb67447988eb0deff287f4e42e5b61d46d4763a920db5c79852c9b07e163ef"
ARMS=("joint","transition","reward","factorized_or")
STREAM_LENGTH=192
ORIGIN=448


def require(cond,code):
    if not cond:
        raise ValueError("CKAD25_"+code)


def ratio(value):
    return [value.numerator,value.denominator]


def semantic(data):
    def normalize(value):
        if isinstance(value,dict):
            return {k:normalize(v) for k,v in value.items()
                    if k not in ("stable_sha256","wall_seconds","runtime_host",
                                 "source_candidate_sha")}
        if isinstance(value,list):
            return [normalize(x) for x in value]
        return value
    return digest(canonical(normalize(data)))


class SurpriseAlarm:
    """Fully specified, independent prequential monitor, no retraining."""

    def __init__(self,kind):
        require(kind in ARMS,"ALARM_KIND")
        self.kind=kind
        self.t=Fraction(1)
        self.y=Fraction(1)
        self.joint=Fraction(1)
        self.last=ORIGIN
        self.alarms=[]

    def observe(self,event_id,count,p_transition,p_reward):
        require(type(count) is int and ORIGIN<count<=ORIGIN+STREAM_LENGTH,
                "ALARM_COUNT")
        require(0<p_transition<=1 and 0<p_reward<=1,
                "OBSERVED_EVENT_PROBABILITY")
        self.joint=max(Fraction(1),self.joint/(4*p_transition*p_reward))
        self.t=max(Fraction(1),self.t/(2*p_transition))
        self.y=max(Fraction(1),self.y/(2*p_reward))
        if count-self.last<8:
            return
        if self.kind=="joint":
            flag=self.joint>=16
            score=self.joint
            causes=["joint"] if flag else []
        elif self.kind=="transition":
            flag=self.t>=16
            score=self.t
            causes=["transition"] if flag else []
        elif self.kind=="reward":
            flag=self.y>=16
            score=self.y
            causes=["reward"] if flag else []
        else:
            flag=self.t>=16 or self.y>=16
            score=max(self.t,self.y)
            causes=([s for s,trigger in (("transition",self.t>=16),
                                          ("reward",self.y>=16)) if trigger]
                    if flag else [])
        if flag:
            self.alarms.append({"event_id":event_id,"evidence_count":count,
                                "score":ratio(score),"causes":causes})
            self.joint=Fraction(1)
            self.t=Fraction(1)
            self.y=Fraction(1)
            self.last=count


def native_joint(normal):
    return [{"event_id":z["event_id"],"evidence_count":z["evidence_count"]}
            for z in normal]


def run_case(schedule,seed,out):
    started=time.monotonic()
    protocol=json.loads((HERE/"prereg.json").read_bytes())
    require(protocol["schema"]=="yggdrasil.ckad25.factorized-surprise-development.prereg.v1"
            and protocol["parent_commit"]==PARENT and
            protocol["generator_sha256"]==SOURCE_SHA==EXPERIENCE_SOURCE,
            "FROZEN_SOURCE")
    require(digest(SOURCE.read_bytes())==SOURCE_SHA,"SOURCE_FIXTURE_HASH")
    require(schedule in SCHEDULES and seed in SEEDS,"SOURCE_SCOPE")
    require(protocol["checkpoint_parent_group_seeds"]==list(SEEDS) and
            protocol["budgets"]["per_case_public_episodes"]==STREAM_LENGTH,
            "SOURCE_PROTOCOL")
    phases=protocol["source_schedules"][schedule]
    require(len(phases)==4 and len(set(map(tuple,phases)))>1
            if schedule!="stationary_null" else len(set(map(tuple,phases)))==1,
            "PHASE_STRUCTURE")
    namespace_seed=seed+protocol["source_seed_offsets"][schedule]
    source_cohort=protocol["source_namespace"]
    parent_bytes=(CK22/f"seed-{seed}-expanded-native.json").read_bytes()
    baseline=json.loads((CK23/"prereg.json").read_bytes())
    pin=baseline["parent_pins"][str(seed)]
    require(digest(parent_bytes)==pin,"PARENT_CHECKPOINT")
    parent=NativeCumulativeLearner.restore(parent_bytes,pin)
    legacy,history=B.legacy_and_experience(parent_bytes)
    require(len(history["episodes"])==ORIGIN,"PARENT_448_WITNESSES")
    model=parent.begin_experience_stream()
    monitor=BASE.Monitor(history["episodes"])
    observers={key:SurpriseAlarm(key) for key in ARMS}
    trace=[]
    for index in range(STREAM_LENGTH):
        family,regime=phases[index//48]
        episode=B.make_episode(cohort=source_cohort,seed=namespace_seed,index=index,
                               family=family,regime=regime)
        views=B.public_views(episode)
        view=views[0]
        if index%4==3:
            row=LEGACY.planned_rollout(episode,model.experience_context_plan(view))
        else:
            current=model
            row=B.rollout(episode,
                 lambda _state:current.experience_context_explore(view),
                 lambda _state,first,s2:current.experience_context_explore(view,first,s2))
        identifier=BASE.event_id(source_cohort,namespace_seed,index,"active")
        first,state,second,reward=(row[k] for k in ("x1","s2","x2","y"))
        p=model.experience_context_forecast(view,first)
        q=model.experience_context_forecast(view,first,state,second)
        pt=p if state else 1-p
        py=q if reward else 1-q
        require(0<pt<=1 and 0<py<=1,"PREQUENTIAL_POSITIVE_PROBABILITY")
        absolute=ORIGIN+index+1
        for observer in observers.values():
            observer.observe(identifier,absolute,pt,py)
        trace.append({
            "event_id":identifier,"evidence_count":absolute,
            "public_view":list(view),"first_action":first,"next_state":state,
            "second_action":second,"reward":reward,
            "p_transition_observed":ratio(pt),
            "p_reward_observed":ratio(py)
        })
        model=B.admit(model,identifier,views,row)
        monitor.add(B.retain_event(identifier,views,row))
        monitor.assert_native(model)
        require(native_joint(observers["joint"].alarms)==native_joint(monitor.detections),
                "JOINT_ALARM_PARITY")
    native=model.consolidate_experience()
    raw=native.checkpoint()
    restored=NativeCumulativeLearner.restore(raw,digest(raw))
    require(restored.checkpoint()==raw,"FINAL_COLD_RESTORE")
    new_legacy,new_experience=B.legacy_and_experience(raw)
    episodes=new_experience["episodes"]
    require(new_legacy==legacy and len(episodes)==640 and
            episodes[:ORIGIN]==history["episodes"] and
            len({row[0] for row in episodes})==640,"IMMUTABLE_640_WITNESSES")
    require(parent.checkpoint()==parent_bytes,"ORIGINAL_BYTES_UNCHANGED")
    require(restored.info()["episode_experience"]["stream"]["detections"]==
            monitor.detections,"NATIVE_ALARM_RESTORED")
    name=f"{schedule}-{seed}-native.json"
    out.mkdir(parents=True,exist_ok=True)
    (out/name).write_bytes(raw)
    result={
        "schema":"yggdrasil.ckad25.factorized-surprise.case.v1",
        "schedule":schedule,"seed":seed,"source_seed":namespace_seed,
        "source_cohort":source_cohort,
        "source_generator_sha256":SOURCE_SHA,
        "unchanged_native_parent_commit":PARENT,
        "parent_checkpoint_sha256":pin,
        "final_checkpoint_name":name,
        "final_checkpoint_sha256":digest(raw),
        "final_checkpoint_bytes":len(raw),
        "case_episodes":STREAM_LENGTH,
        "source_actions":STREAM_LENGTH*2,
        "new_public_episodes":STREAM_LENGTH,
        "old_public_episodes":ORIGIN,
        "trace":trace,
        "alarms":{key:observer.alarms for key,observer in observers.items()},
        "native_joint_detections":monitor.detections,
        "scientific_pass":False,"accepted_native":False,"deployment":"NONE",
        "original_source_actions":0,"protected_first_use":0,"held_updates":0,
    }
    result["stable_sha256"]=semantic(result)
    result["wall_seconds"]=time.monotonic()-started
    require(result["wall_seconds"]<protocol["budgets"]["per_case_max_wall_seconds"],
            "FROZEN_WALL_BUDGET")
    (out/"case-result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--schedule",required=True,choices=SCHEDULES)
    parser.add_argument("--seed",type=int,required=True,choices=SEEDS)
    parser.add_argument("--output-directory",required=True,type=Path)
    args=parser.parse_args()
    result=run_case(args.schedule,args.seed,args.output_directory)
    print(json.dumps({
        "seed":args.seed,"schedule":args.schedule,
        "alarms":{k:[z["evidence_count"]-ORIGIN for z in v]
                  for k,v in result["alarms"].items()},
        "case_sha256":result["stable_sha256"],
        "wall_seconds":result["wall_seconds"],
    },sort_keys=True))


if __name__=="__main__":main()
