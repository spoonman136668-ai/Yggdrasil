"""CKAD23: unsignaled causal change detection in one cumulative native learner.

Frozen source phases are evaluator-side only. On every episode, learner
action a1 precedes observed S2; action a2 follows S2 and precedes Y.
Online detector sees only the prequential public S2,Y likelihood.
No hidden phase, family, change point, future answer or oracle readout is fed
to the native system or the independent replay monitor.
"""
import argparse
from fractions import Fraction
from itertools import product
import importlib.util
import json
from pathlib import Path
from hashlib import sha256
import os
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
PARENT22=HERE.parent/"CKAD-22"
PARENT21=HERE.parent/"CKAD-21"
SOURCE=HERE.parent/"CKAD-20"/"synthetic_world.py"
sys.path.insert(0,str(ROOT))
if hasattr(sys,"set_int_max_str_digits"):sys.set_int_max_str_digits(0)

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    item=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(item)
    return item

CK22=module("ckad23_parent22_campaign",PARENT22/"campaign.py")
CK21=CK22.BASE
GEN=CK21
LEGACY=CK22.LEGACY
REF=CK22.REFERENCE
from yggdrasil.native_context_basis import canonical,digest
from yggdrasil.native_cumulative_learner import EXPERIENCE_SOURCE,NativeCumulativeLearner
BITS=(0,1)
VIEWS=tuple(product(BITS,repeat=2))
HISTORIES=tuple(product(BITS,repeat=3))
SEEDS=(101,202,303)
PHASES=(("invariant",0),("terminal_switch",1),
        ("invariant",1),("invariant",0))
BOUNDARIES=(48,96,144)
CHECKPOINTS=tuple(range(0,193,16))
ARMS=("detector_active","detector_random","no_reset","periodic32",
      "pooled_replay","trailing_mle","frozen_ckad22","exact_monitor")
SOURCE_SHA="20cb67447988eb0deff287f4e42e5b61d46d4763a920db5c79852c9b07e163ef"
PARENT_SHA="f04cfcac2aa07806a6b942d968119de87bfb6aaf"
PREREG_PARENT_PINS={
 101:"852d9eede37c6e749c2b90eefd358826cbf1f61321d58dcfa0e26348927111f9",
 202:"63754801ea27ed0950f4ce27ab247621c7881cb18b1fd818f3261acc2b07eacd",
 303:"d8132cd5c1dac818812e3a9f63c3a9ff0de16dff090c801804206cfb0f1441f9",
}


def need(ok,message):
    if not ok:raise RuntimeError("CKAD23_"+message)


def current_phase(count):
    need(type(count) is int and 0<=count<=192,"CHECKPOINT_COUNT")
    return PHASES[0 if count==0 else (count-1)//48]


def event_id(seed,index,arm):
    return digest(canonical(["ckad23",SOURCE_SHA,"ckad23-stream",seed,index,arm]))


def random_actions(seed,index):
    raw=sha256(f"ckad23/actions-v1/ckad23-stream/random/{seed}/{index}".encode("ascii")).digest()
    return raw[0]&1,raw[1]&1


class IndependentMonitor:
    """Previously qualified exact rational mixture with a separate change monitor.

    Uses reference replay, not the native detector or its hidden state.
    """
    __slots__=("history","mixture","score","detections","start")

    def __init__(self,history):
        self.history=list(history)
        self.mixture=REF.Mixture(self.history,novel=True)
        self.score=Fraction(1)
        self.detections=[]
        self.start=len(self.history)

    def observe(self,event):
        identifier,views,first,state,second,reward=event
        view=tuple(views[0])
        transition=self.mixture.forecast(view,first)
        terminal=self.mixture.forecast(view,first,state,second)
        likelihood=(transition if state else 1-transition)*(terminal if reward else 1-terminal)
        need(0<likelihood<=1,"INDEPENDENT_LIKELIHOOD")
        self.history.append(event)
        self.mixture.add(event)
        self.score=max(Fraction(1),self.score/(4*likelihood))
        if self.score>=16 and len(self.history)-self.start>=8:
            self.detections.append({
                "identifier":identifier,"count":len(self.history),
                "score":LEGACY.ratio(self.score)
            })
            self.mixture=REF.Mixture(self.history,novel=True)
            self.start=len(self.history)
            self.score=Fraction(1)

    def parity(self,model):
        native=model.info()["episode_experience"]
        observed=native["stream"]
        need(observed["stream_start"]==448 and observed["detections"]==self.detections,
             "INDEPENDENT_BOUNDARY_PARITY")
        need(Fraction(*observed["score"])==self.score,"INDEPENDENT_SCORE_PARITY")
        need(native["context"]==self.mixture.info(),"INDEPENDENT_MODEL_WEIGHT_PARITY")
        for view in VIEWS:
            native_plan=model.experience_context_plan(view)
            independent_plan=self.mixture.plan(view)
            need(canonical(native_plan)==canonical(independent_plan),
                 "INDEPENDENT_ACTION_PARITY")
            for first in BITS:
                need(model.experience_context_forecast(view,first)==
                     self.mixture.forecast(view,first),
                     "INDEPENDENT_TRANSITION_PARITY")
                for state,second in product(BITS,repeat=2):
                    need(model.experience_context_forecast(view,first,state,second)==
                         self.mixture.forecast(view,first,state,second),
                         "INDEPENDENT_TERMINAL_PARITY")
        return 4*2+4*8+4


def load_parent(seed,protocol):
    name=f"seed-{seed}-expanded-native.json"
    raw=(PARENT22/name).read_bytes()
    pin=protocol["parent_pins"][str(seed)]
    need(pin==PREREG_PARENT_PINS[seed] and digest(raw)==pin,"PINNED_PARENT_CHECKPOINT")
    model=NativeCumulativeLearner.restore(raw,pin)
    need(model.checkpoint()==raw,"PARENT_COLD_RESTORE")
    body=json.loads(raw)
    experience=json.loads(body["experience_ascii"])
    history=experience["episodes"]
    need(len(history)==448 and len({v[0] for v in history})==448,
         "PINNED_448_HISTORY")
    legacy={k:v for k,v in body.items() if k!="experience_ascii"}
    return raw,pin,model,history,legacy


def score(models,monitor,parent,retained,source_seed,count,world):
    cohort=f"ckad23-held-{count}"
    conventional=LEGACY.ConventionalControl(CK21.receipts_from_events(retained),mle=True)
    methods={
       "detector_active":(models["detector_active"].experience_context_plan,
                          models["detector_active"].experience_context_forecast),
       "detector_random":(models["detector_random"].experience_context_plan,
                          models["detector_random"].experience_context_forecast),
       "no_reset":(models["no_reset"].experience_context_plan,
                   models["no_reset"].experience_context_forecast),
       "periodic32":(models["periodic32"].experience_context_plan,
                     models["periodic32"].experience_context_forecast),
       "pooled_replay":(models["pooled_replay"].experience_plan,
                       models["pooled_replay"].experience_forecast),
       "trailing_mle":(conventional.plan,conventional.forecast),
       "frozen_ckad22":(parent.experience_context_plan,parent.experience_context_forecast),
       "exact_monitor":(monitor.mixture.plan,monitor.mixture.forecast),
    }
    pinned={}
    for arm,(plan,forecast) in methods.items():
        pinned[arm]=(
            {view:plan(view) for view in VIEWS},
            {(view,a1):forecast(view,a1) for view in VIEWS for a1 in BITS},
            {(view,*h):forecast(view,*h) for view in VIEWS for h in HISTORIES},
        )
    need(pinned["detector_active"]==pinned["exact_monitor"],"EXACT_MONITOR_READOUT")
    totals={arm:[0,Fraction(),Fraction()] for arm in ARMS}
    traces={arm:[] for arm in ARMS}
    for index in range(96):
        episode=GEN.make_episode(cohort=cohort,seed=source_seed,index=index,
                                 family=world[0],regime=world[1])
        view=GEN.public_views(episode)[0]
        a1,a2=random_actions(source_seed,index+100000+count)
        observed=LEGACY.fixed_rollout(episode,(a1,a2))
        for arm,(plans,transitions,terminals) in pinned.items():
            decision=LEGACY.planned_rollout(episode,plans[view])
            totals[arm][0]+=decision["y"]
            s2=observed["s2"]
            y=observed["y"]
            totals[arm][1]+=(transitions[(view,a1)]-s2)**2
            totals[arm][2]+=(terminals[(view,a1,s2,a2)]-y)**2
            traces[arm].append([decision["x1"],decision["s2"],
                                decision["x2"],decision["y"]])
    scores={arm:{
        "episodes":96,"reward_sum":values[0],
        "transition_brier":LEGACY.ratio(values[1]/96),
        "terminal_brier":LEGACY.ratio(values[2]/96),
        "pooled_brier":LEGACY.ratio((values[1]+values[2])/192),
        "trace_sha256":digest(canonical(traces[arm]))
    } for arm,values in totals.items()}
    need(scores["detector_active"]==scores["exact_monitor"],
         "EXACT_MONITOR_SCORE")
    return scores


def run_seed(seed,protocol,output):
    started=time.monotonic()
    raw,pin,parent,original,legacy=load_parent(seed,protocol)
    source_seed=seed+protocol["source_seed_offset"]
    models={
        "detector_active":parent.begin_experience_stream(),
        "detector_random":parent.begin_experience_stream(),
        "no_reset":parent.begin_experience_context(novel=True),
        "periodic32":parent.begin_experience_context(novel=True),
        "pooled_replay":parent,
    }
    monitor=IndependentMonitor(original)
    retained=list(original)
    active_ids=[]
    random_ids=[]
    previous={arm:original for arm in models}
    parity={"forecast_queries":0,"source_outcomes":0,
            "detector_boundaries_checked":0,"readout_checks":0}
    checkpoints=[]
    acquire_reward={"detector_active":0,"detector_random":0}
    for count in CHECKPOINTS:
        # Every count is checked BEFORE acquiring the next 16 episodes.
        if count:
            for index in range(count-16,count):
                if index>0 and index%32==0:
                    models["periodic32"]=models["periodic32"].begin_experience_context(novel=True)
                phase=PHASES[index//48]
                cohort="ckad23-stream"
                episode=GEN.make_episode(cohort=cohort,seed=source_seed,index=index,
                                         family=phase[0],regime=phase[1])
                views=GEN.public_views(episode)
                view=views[0]
                active=models["detector_active"]
                reference=monitor.mixture
                if index%4==3:
                    plan=active.experience_context_plan(view)
                    need(canonical(plan)==canonical(reference.plan(view)),
                         "PREACTION_POLICY_PARITY")
                    row=LEGACY.planned_rollout(episode,plan)
                else:
                    need(active.experience_context_explore(view)==reference.explore(view),
                         "PREACTION_EXPLORE_PARITY")
                    row=GEN.rollout(episode,
                        lambda _initial:active.experience_context_explore(view),
                        lambda _initial,first,state:active.experience_context_explore(view,first,state))
                identifier=event_id(source_seed,index,"active")
                for arm in ("detector_active","no_reset","periodic32","pooled_replay"):
                    models[arm]=CK21.admit(models[arm],identifier,views,row)
                event=CK21.retain_event(identifier,views,row)
                retained.append(event)
                monitor.observe(event)
                active_ids.append(identifier)
                parity["source_outcomes"]+=1
                acquire_reward["detector_active"]+=row["y"]
                ra1,ra2=random_actions(source_seed,index)
                random_row=LEGACY.fixed_rollout(episode,(ra1,ra2))
                rand_id=event_id(source_seed,index,"random")
                models["detector_random"]=CK21.admit(models["detector_random"],
                                                     rand_id,views,random_row)
                random_ids.append(rand_id)
                acquire_reward["detector_random"]+=random_row["y"]
                info=models["detector_active"].info()["episode_experience"]["stream"]
                need(info["detections"]==monitor.detections and
                     Fraction(*info["score"])==monitor.score,
                     "PREQUENTIAL_BOUNDARY_SCORE")
                parity["detector_boundaries_checked"]+=1
        # Verify the model and its conventional comparator on public values.
        parity["forecast_queries"]+=monitor.parity(models["detector_active"])
        parity["readout_checks"]+=1
        world=current_phase(count)
        before={arm:digest(model.checkpoint()) for arm,model in models.items()}
        scores=score(models,monitor,parent,retained,source_seed,count,world)
        need(all(digest(model.checkpoint())==before[arm] for arm,model in models.items()),
             "HELD_MODEL_MUTATED")
        # Exact checkpoint continuation replays the causally inferred boundaries.
        if count in (0,64,112,160,192):
            for arm in ("detector_active","detector_random","no_reset","periodic32"):
                checkpoint=models[arm].checkpoint()
                restored=NativeCumulativeLearner.restore(checkpoint,digest(checkpoint))
                need(restored.checkpoint()==checkpoint,"COLD_BOUNDARY_STATE")
                if arm=="detector_active":
                    need(restored.info()["episode_experience"]["stream"]==
                         models[arm].info()["episode_experience"]["stream"],
                         "COLD_DETECTION_STATE")
                models[arm]=restored
        active=models["detector_active"]
        state=active.info()["episode_experience"]
        checkpoints.append({
           "count":count,"held_cohort":f"ckad23-held-{count}",
           "evaluation":scores,
           "active_stream":state["stream"],
           "context_candidates":state["context"]["candidate_count"],
           "checkpoint_sha256":digest(active.checkpoint()),
           "checkpoint_bytes":len(active.checkpoint()),
           "source_phase_evaluator_only":list(world),
        })
        if count and count%48==0:
            need(len(retained)==448+count,"STREAM_LEDGER_COUNT")
    need(len(retained)==640 and len(set(active_ids))==192 and
         len(set(random_ids))==192 and not set(active_ids).intersection(random_ids),
         "PUBLIC_192_WITNESS_CUSTODY")
    for arm,model in models.items():
        state=json.loads(model.checkpoint())
        experience=json.loads(state["experience_ascii"])
        need(experience["episodes"][:448]==original and len(experience["episodes"])==640,
             "HISTORICAL_PREFIX_OR_APPEND")
        if arm!="detector_random":
            need(experience["episodes"]==retained,"MATCHED_PUBLIC_RECEIPTS")
        need({k:v for k,v in state.items() if k!="experience_ascii"}==legacy,
             "LEGACY_NATIVE_MUTATION")
    need(parent.checkpoint()==raw,"PARENT_SOURCE_CHANGED")
    final=models["detector_active"].checkpoint()
    name=f"seed-{seed}-stream-native.json"
    (output/name).write_bytes(final)
    need(digest((output/name).read_bytes())==digest(final),"SAVED_CUSTODY")
    elapsed=time.monotonic()-started
    need(elapsed<protocol["budgets"]["max_wall_seconds"],
         "SOURCE_WALL_BUDGET")
    detector=models["detector_active"].info()["episode_experience"]["stream"]["detections"]
    alarms=sum(not any(change+1<=event["count"]<=change+16 for change in BOUNDARIES)
               for event in detector)
    return {
      "seed":seed,"source_seed":source_seed,
      "original_checkpoint_sha256":pin,
      "final_checkpoint_name":name,"final_checkpoint_sha256":digest(final),
      "final_checkpoint_bytes":len(final),
      "checkpoints":checkpoints,"parity":parity,
      "detected_boundaries":detector,"false_alarms":alarms,
      "first_public_actions":192,"second_public_actions":192,
      "random_first_public_actions":192,"random_second_public_actions":192,
      "acquired_reward":acquire_reward,
      "legacy_checkpoint_retained":True,
      "held_updates":0,"wall_seconds":elapsed
    }


def metrics(seeds):
    def avg(checkpoints,arm):
        rows=[checkpoint["evaluation"][arm]
              for seed in seeds for checkpoint in seed["checkpoints"]
              if checkpoint["count"] in checkpoints]
        return Fraction(sum(z["reward_sum"] for z in rows),
                        sum(z["episodes"] for z in rows))
    targeted=(64,112,160)
    active=avg(targeted,"detector_active")
    no_reset=avg(targeted,"no_reset")
    periodic=avg(targeted,"periodic32")
    trailing=avg(targeted,"trailing_mle")
    final=avg((192,),"detector_active")
    gates={
       "gain_vs_no_reset":active-no_reset>=Fraction(1,20),
       "at_least_periodic32":active>=periodic,
       "at_least_trailing64_mle":active>=trailing,
       "returning_invariant_reward":final>=Fraction(4,5),
       "per_seed_false_alarms":all(s["false_alarms"]<=3 for s in seeds),
    }
    rates={
      "target_held_reward":LEGACY.ratio(active),
      "target_gain_vs_no_reset":LEGACY.ratio(active-no_reset),
      "target_gain_vs_periodic32":LEGACY.ratio(active-periodic),
      "target_gain_vs_trailing64_mle":LEGACY.ratio(active-trailing),
      "final_invariant_reward":LEGACY.ratio(final),
    }
    return gates,rates


def semantic(d):
    # Stable platform-independent evidence excludes only runtime/metadata.
    if isinstance(d,dict):
        return {k:semantic(v) for k,v in d.items()
                if k not in ("source_candidate_sha","stable_sha256",
                             "whole_wall_seconds","wall_seconds",
                             "cpu_seconds","peak_rss_bytes")}
    if isinstance(d,list):return [semantic(v) for v in d]
    return d


def run(args):
    started=time.monotonic()
    protocol=json.loads((HERE/"prereg.json").read_bytes())
    need(protocol["schema"]=="yggdrasil.ckad23.unsignaled-context-development.prereg.v1" and
         protocol["parent"]==PARENT_SHA and
         protocol["parent_pins"]=={str(k):v for k,v in PREREG_PARENT_PINS.items()},
         "FROZEN_PROTOCOL")
    need(digest(SOURCE.read_bytes())==SOURCE_SHA==EXPERIENCE_SOURCE,
         "FROZEN_GENERATOR_SOURCE")
    need(protocol["budgets"]["stream_episodes_per_seed_per_acquisition_arm"]==192 and
         protocol["budgets"]["held_episodes_per_checkpoint"]==96 and
         protocol["budgets"]["checkpoints"]==list(CHECKPOINTS),
         "FROZEN_BUDGET")
    seeds=[run_seed(seed,protocol,args.output_directory) for seed in args.seeds]
    result={
      "schema":"yggdrasil.ckad23.unsignaled-context-development.result.v1",
      "classification":"PARTIAL_SOURCE_PROOF" if len(args.seeds)<3 else None,
      "source_parent":PARENT_SHA,
      "source_sha256":SOURCE_SHA,
      "source_candidate_sha":subprocess.check_output(
          ["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
      "seeds":seeds,"science_pass":False,"accepted_native":False,
      "deployment":"NONE","scope":{
        "original_source_actions":0,"protected_first_use":0,"held_updates":0,
        "stream_episodes":192*len(seeds),
        "held_episodes":96*13*len(seeds),
        "held_policy_rollouts":96*13*len(seeds)*len(ARMS),
      },
    }
    if len(args.seeds)==3:
        gates,rates=metrics(seeds)
        result.update({
          "classification":"DEVELOPMENT_GO" if all(gates.values()) else "DEVELOPMENT_NO_GO",
          "development_gates":gates,"development_metrics":rates,
        })
    result["stable_sha256"]=digest(canonical(semantic(result)))
    result["whole_wall_seconds"]=time.monotonic()-started
    return result


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output-directory",required=True,type=Path)
    p.add_argument("--seed",type=int,choices=SEEDS,action="append",dest="seeds")
    args=p.parse_args()
    if args.seeds is None:args.seeds=list(SEEDS)
    args.output_directory.mkdir(parents=True,exist_ok=True)
    d=run(args)
    (args.output_directory/"result.json").write_text(json.dumps(d,sort_keys=True,indent=2)+"\n")
    print(json.dumps({
      "classification":d["classification"],"seeds":args.seeds,
      "stable_sha256":d["stable_sha256"],
      "summary":[{"seed":s["seed"],"detections":len(s["detected_boundaries"]),
                  "false_alarms":s["false_alarms"],
                  "acquired_reward":s["acquired_reward"]}
                 for s in d["seeds"]],
      "wall_seconds":d["whole_wall_seconds"]
    },sort_keys=True))
