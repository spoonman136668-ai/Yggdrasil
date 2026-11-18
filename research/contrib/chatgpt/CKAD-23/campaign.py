"""CKAD23: disjoint synthetic compositional action-consequence transfer.

The two new structural equations are evaluator-side only; native learners
receive public views, chosen actions, observed next state and reward. They do
not receive family names, regime, hidden state or counterfactual answers.
"""
import argparse
from fractions import Fraction
from hashlib import sha256
import importlib.util
import json
from itertools import product
from pathlib import Path
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
CK22=HERE.parent/"CKAD-22"
CK21=HERE.parent/"CKAD-21"
CK20=HERE.parent/"CKAD-20"
sys.path.insert(0,str(ROOT))
if hasattr(sys,"set_int_max_str_digits"):sys.set_int_max_str_digits(0)

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

BASE=load("ckad23_parent21",CK21/"campaign.py")
PARENT22=load("ckad23_parent22",CK22/"campaign.py")
GEN=BASE  # CKAD21 already imports pinned synthetic_world; avoid duplicate module state
REF=PARENT22.REFERENCE
LEGACY=BASE.LEGACY
from yggdrasil.native_context_basis import canonical,digest
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner, EXPERIENCE_SOURCE

SEEDS=(101,202,303)
ENV_SEEDS=(1009,1013,1019,1021,1031,1033,1039,1049)
WORLDS=("conjunctive_terminal","interaction_gate")
ARMS=("novel_active","retrieval_only","novel_random",
      "full_beta","trailing_mle","pooled_replay","exact_mixture")
SOURCE_PIN="20cb67447988eb0deff287f4e42e5b61d46d4763a920db5c79852c9b07e163ef"
PARENT_COMMIT="f04cfcac2aa07806a6b942d968119de87bfb6aaf"
PARENT_STABLE="4b20ef3b9229eddfd509e5897e6aa8f8d5226288ab331c4a98f8a7bc46fbccc2"
PROTOCOL_SHA="43bf1854d0c12c3dc26a3010c3ee9d945bece28b"

def require(b,msg):
    if not b:raise ValueError("CKAD23_"+msg)

def source_seed(parent,environment):
    return parent*100000+environment

def action_bits(tag,parent,environment,world,index):
    v=sha256(f"ckad23/v1/{tag}/{parent}/{environment}/{world}/{index}".encode()).digest()
    return v[0]&1,v[1]&1

class NewWorld:
    __slots__=("base","family","s1","nuisance_a","nuisance_b")
    def __init__(self,base,family):
        require(family in WORLDS,"WORLD")
        self.base=base; self.family=family
        self.s1=base.s1; self.nuisance_a=base.nuisance_a; self.nuisance_b=base.nuisance_b
    def transition(self,x1):
        require(type(x1) is int and x1 in (0,1),"FIRST_ACTION")
        if self.family=="conjunctive_terminal":
            return x1 ^ self.base.transition_noise
        return (x1 & self.s1) ^ 1 ^ self.base.transition_noise
    def _reward(self,x1,s2,x2):
        require(all(type(v) is int and v in (0,1) for v in (x1,s2,x2)),"SECOND_ACTION")
        if self.family=="conjunctive_terminal":
            target=(self.s1 & s2) ^ x1
            ready=(s2==0 or self.base.hidden==1)
        else:
            target=self.s1 ^ (x1 & s2)
            ready=(s2==1 or self.base.hidden==0)
        return int(ready and x2==target)^self.base.reward_noise

def episode(world, cohort, seed, index):
    b=GEN.make_episode(cohort=cohort,seed=seed,index=index,
                       family="invariant",regime=0)
    return NewWorld(b,world)

def parent_state(parent):
    row_path=CK22/f"seed-{parent}-expanded-native.json"
    raw=row_path.read_bytes()
    pin=digest(raw)
    report=json.loads((CK22/"result.json").read_bytes())
    require(report["stable_sha256"]==PARENT_STABLE
            and report["source_candidate_sha"]=="de1c3daac160c0ef24f352ce238558b1356c06dd",
            "PARENT_REPORT")
    target=next(z for z in report["final_checkpoints"] if z["seed"]==parent)
    require(target["sha256"]==pin and target["bytes"]==len(raw),"PARENT_RAW_PIN")
    model=NativeCumulativeLearner.restore(raw,pin)
    require(model.checkpoint()==raw,"COLD_PARENT")
    body=json.loads(raw)
    experience=json.loads(body["experience_ascii"])
    history=experience["episodes"]
    require(len(history)==448 and len({z[0] for z in history})==448,"PARENT_LEDGER")
    return raw,pin,history,model

def run_case(parent,environment,world,source):
    raw,parent_pin,old,foundation=source
    seed=source_seed(parent,environment)
    models={arm:NativeCumulativeLearner.restore(raw,parent_pin)
            for arm in ("novel_active","novel_random","retrieval_only","pooled_replay")}
    for arm in ("novel_active","novel_random","retrieval_only"):
        models[arm]=models[arm].begin_experience_context(novel=(arm!="retrieval_only"))
    mixture=REF.Mixture(old.copy(),novel=True)
    require(mixture.weights[-1]==Fraction(1,8),"FROZEN_NEW_PRIOR")
    retained=list(old)
    new_ids=[]
    confidence=[]
    for i in range(16):
        current=models["novel_active"]
        if i in (0,8):
            BASE.require_parity(current,mixture,{"forecasts":0,"decisions":0,"mismatches":0})
        e=episode(world,f"ckad23-probe-{world}",seed,i)
        views=GEN.public_views(e)
        view=views[0]
        observed=GEN.rollout(e,
             lambda _s1:current.experience_context_explore(view),
             lambda _s1,a1,s2:current.experience_context_explore(view,a1,s2))
        identifier=digest(canonical(["ckad23",SOURCE_PIN,world,seed,i,"active"]))
        for arm in ("novel_active","retrieval_only","pooled_replay"):
            models[arm]=BASE.admit(models[arm],identifier,views,observed)
        event=BASE.retain_event(identifier,views,observed)
        retained.append(event);new_ids.append(identifier);mixture.add(event)
        x1,x2=action_bits("probe-random",parent,environment,world,i)
        random_row=GEN.rollout(e,lambda _s1:x1,lambda *_:x2)
        random_id=digest(canonical(["ckad23",SOURCE_PIN,world,seed,i,"random"]))
        models["novel_random"]=BASE.admit(models["novel_random"],random_id,views,random_row)
    BASE.require_parity(models["novel_active"],mixture,
                        {"forecasts":0,"decisions":0,"mismatches":0})
    require(len(set(new_ids))==16 and len(retained)==464,"WITNESS_ACCOUNTING")
    native_info=models["novel_active"].info()["episode_experience"]["context"]
    final_weight=native_info["weights"][-1]
    require(Fraction(*final_weight)==mixture.weights[-1],"POSTERIOR")
    # Capacity and data access match the conventional controls exactly.
    readouts=PARENT22.readouts(models,mixture,foundation,retained)
    readouts["full_beta"]=readouts["beta"]
    plans={arm:{view:readouts[arm][0](view) for view in BASE.VIEWS} for arm in ARMS}
    require(plans["novel_active"]==plans["exact_mixture"],"EXACT_MIXTURE_PLAN")
    results={}
    for target in (world,"familiar"):
        wins={arm:0 for arm in ARMS}
        trace={arm:[] for arm in ARMS}
        for i in range(48):
            cohort=f"ckad23-held-{world}" if target==world else f"ckad23-familiar-{world}"
            e=(episode(world,cohort,seed,i) if target==world
               else GEN.make_episode(cohort=cohort,seed=seed,index=i,
                                     family="invariant",regime=0))
            view=GEN.public_views(e)[0]
            for arm in ARMS:
                row=LEGACY.planned_rollout(e,plans[arm][view])
                wins[arm]+=row["y"]
                trace[arm].append([row["x1"],row["s2"],row["x2"],row["y"]])
        require(wins["novel_active"]==wins["exact_mixture"],"EXACT_MIXTURE_REWARD")
        results[target]={"denominator":48,"successes":wins,
                         "trace_sha256":{arm:digest(canonical(rows)) for arm,rows in trace.items()}}
    frozen=models["novel_active"].checkpoint()
    require(foundation.checkpoint()==raw and
            len(json.loads(json.loads(frozen)["experience_ascii"])["episodes"])==464 and
            json.loads(json.loads(frozen)["experience_ascii"])["episodes"][:448]==old,
            "NO_HISTORY_DAMAGE")
    restored=NativeCumulativeLearner.restore(frozen,digest(frozen))
    require(restored.checkpoint()==frozen and
            BASE.context_readout_pin(restored)==BASE.context_readout_pin(models["novel_active"]),
            "COLD_CONTINUATION")
    return {"parent":parent,"parent_checkpoint_sha256":parent_pin,
            "environment_seed":environment,"composite_seed":seed,"world":world,
            "probes":16,"before_count":448,"after_count":464,
            "novel_candidate_prior":[1,8],"novel_candidate_final_weight":final_weight,
            "novel_checkpoint_sha256":digest(frozen),
            "active_receipt_sha256":digest(canonical(new_ids)),
            "new_held_training_updates":0,
            "evaluation":results}

def run(parent,half):
    start=time.monotonic()
    require(parent in SEEDS and half in (0,1),"CLI_BOUNDS")
    require(digest((CK20/"synthetic_world.py").read_bytes())==SOURCE_PIN==EXPERIENCE_SOURCE,
            "ORIGINAL_GENERATOR_PIN")
    protocol=json.loads((HERE/"prereg.json").read_bytes())
    require(protocol["parent_sha"]==PARENT_COMMIT and
            protocol["source_dependency"]["sha256"]==SOURCE_PIN and
            protocol["probe_budget_per_case"]==16 and
            protocol["held_per_case_per_world"]==48,"FROZEN_PROTOCOL")
    source=parent_state(parent)
    subset=ENV_SEEDS[:4] if half==0 else ENV_SEEDS[4:]
    cases=[run_case(parent,env,world,source)
           for env in subset for world in WORLDS]
    output={"schema":"yggdrasil.ckad23.compositional-disjoint-shard.v1",
            "parent":parent,"half":half,"environment_seeds":list(subset),
            "source_sha256":SOURCE_PIN,"source_parent":PARENT_COMMIT,
            "original_ckad22_result_sha256":PARENT_STABLE,
            "cases":cases,"synthetic_probe_updates":len(cases)*16,
            "original_source_actions":0,"protected_first_use":0,
            "scientific_pass":False,"accepted_native":False,"deployment":"NONE"}
    output["stable_sha256"]=digest(canonical(output))
    output["wall_seconds"]=time.monotonic()-start
    require(output["wall_seconds"]<900,"SHARD_WALL_BUDGET")
    return output

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--parent",type=int,required=True,choices=SEEDS)
    p.add_argument("--half",type=int,required=True,choices=(0,1))
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    output=run(args.parent,args.half)
    args.output.write_text(json.dumps(output,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"parent":args.parent,"half":args.half,
                      "cases":len(output["cases"]),"stable_sha256":output["stable_sha256"],
                      "wall_seconds":output["wall_seconds"],
                      "world_rewards":{w:sum(v["evaluation"][w]["successes"]["novel_active"]
                                            for v in output["cases"] if v["world"]==w)
                                       for w in WORLDS}},sort_keys=True))
