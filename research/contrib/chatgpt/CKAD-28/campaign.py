"""CKAD28: matched action-consequence acquisition into separate native learners.

This experiment isolates *choice of intervention*. All three arms receive
equal counts of observations, identical initial native checkpoints and
the same deterministic synthetic world draws. Their chosen actions produce
their OWN actual consequences before learning. Held evaluation is read-only,
using disjoint seeded source episodes and no feedback to the learner.
"""
import argparse
from fractions import Fraction
from itertools import product
from pathlib import Path
from hashlib import sha256
import importlib.util
import json
import sys
import time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
CK23=HERE.parent/"CKAD-23"
CK22=HERE.parent/"CKAD-22"
SOURCE=HERE.parent/"CKAD-20"/"synthetic_world.py"
sys.path.insert(0,str(ROOT))
if hasattr(sys,"set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    x=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(x)
    return x


BASE=load("ckad28_qualified_23",CK23/"campaign.py")
B=BASE.B
LEGACY=BASE.LEGACY
import policy
from yggdrasil.native_context_basis import canonical,digest
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner,EXPERIENCE_SOURCE

ARMS=policy.ARMS
SEEDS=(101,202,303)
SCENARIOS=("reward_change","stationary_null")
CHECKPOINTS=(0,32,64,96,128)
PARENT="43a468dea22b19498329e386aa0af0abecc3100b"
SOURCE_SHA="20cb67447988eb0deff287f4e42e5b61d46d4763a920db5c79852c9b07e163ef"


def need(ok,why):
    if not ok:raise ValueError("CKAD28_"+why)


def ratio(f):
    return [f.numerator,f.denominator]


def stable(result):
    def strip(x):
        if isinstance(x,dict):
            return {key:strip(value) for key,value in x.items()
                    if key not in ("stable_sha256","wall_seconds",
                                   "cpu_seconds","source_candidate_sha")}
        if isinstance(x,list):
            return [strip(value) for value in x]
        return x
    return digest(canonical(strip(result)))


def source_protocol():
    p=json.loads((HERE/"prereg.json").read_bytes())
    need(p["schema"]=="yggdrasil.ckad28.decision-relevance.prereg.v1"
         and p["parent_commit"]==PARENT
         and p["original_source_sha256"]==SOURCE_SHA==EXPERIENCE_SOURCE
         and digest(SOURCE.read_bytes())==SOURCE_SHA,
         "FROZEN_SOURCE_PROTOCOL")
    need(p["seeds"]==list(SEEDS) and
         list(p["scenarios"])==list(SCENARIOS) and
         p["held_evaluations"]["checkpoints"]==list(CHECKPOINTS)
         and p["source_episodes_per_arm"]==128
         and p["held_evaluations"]["episodes_per_checkpoint"]==96,
         "PREDETERMINED_SOURCE_BUDGET")
    return p


def before_after(episode):
    return B.public_views(episode)[0]


def score(models,histories,seed,scenario,count,protocol):
    """Prospective held source, same exogenous draws for every arm/readout."""
    phase=protocol["scenarios"][scenario]["phases"][
        0 if count==0 else (count-1)//protocol["phase_episodes"]]
    family,regime=phase
    viewset=B.VIEWS
    tables={}
    models_before={arm:digest(model.checkpoint()) for arm,model in models.items()}
    for arm,model in models.items():
        conventional=LEGACY.ConventionalControl(B.receipts_from_events(histories[arm]),
                                                mle=True)
        tables[arm]={
          "plan":{view:model.experience_context_plan(view) for view in viewset},
          "conventional_plan":{view:conventional.plan(view) for view in viewset},
          "transition":{(view,first):model.experience_context_forecast(view,first)
                        for view in viewset for first in (0,1)},
          "terminal":{(view,first,state,second):
                      model.experience_context_forecast(view,first,state,second)
                      for view in viewset for first,state,second in
                      product((0,1),repeat=3)},
        }
    sums={arm:{"reward":0,"conventional_reward":0,
               "transition_error":Fraction(0),"reward_error":Fraction(0)}
          for arm in ARMS}
    cohort=protocol["held_cohort"]+"-"+scenario+"-"+str(count)
    n=protocol["held_evaluations"]["episodes_per_checkpoint"]
    source_seed=seed+protocol["scenarios"][scenario]["source_seed_offset"]
    for index in range(n):
        world=B.make_episode(cohort=cohort,seed=source_seed,
                             index=index,family=family,regime=regime)
        view=B.public_views(world)[0]
        actions=BASE.random_actions(cohort,"held-fixed",source_seed,index)
        sampled=LEGACY.fixed_rollout(world,actions)
        first,state,second,reward=(sampled[k] for k in ("x1","s2","x2","y"))
        for arm,tables_arm in tables.items():
            z=sums[arm]
            z["reward"]+=LEGACY.planned_rollout(world,tables_arm["plan"][view])["y"]
            z["conventional_reward"]+=LEGACY.planned_rollout(
                world,tables_arm["conventional_plan"][view])["y"]
            z["transition_error"]+=(tables_arm["transition"][(view,first)]-state)**2
            z["reward_error"]+=(tables_arm["terminal"][(view,first,state,second)]-reward)**2
    after={arm:digest(model.checkpoint()) for arm,model in models.items()}
    need(models_before==after,"HELD_SOURCE_MUTATED_TRAINING_STATE")
    return {
       "count":count,"evaluator_only_phase":phase,
       "held_episodes":n,
       "by_arm":{arm:{
            "reward_sum":v["reward"],
            "conventional_mle_reward_sum":v["conventional_reward"],
            "transition_brier":ratio(v["transition_error"]/n),
            "terminal_brier":ratio(v["reward_error"]/n),
            "checkpoint_sha256":after[arm]
        } for arm,v in sums.items()},
    }


def run_case(scenario,seed,out):
    started=time.monotonic()
    prereg=source_protocol()
    need(scenario in SCENARIOS and seed in SEEDS,"SEED_SCENARIO")
    frozen=json.loads((CK23/"prereg.json").read_bytes())
    old=(CK22/f"seed-{seed}-expanded-native.json").read_bytes()
    old_pin=frozen["parent_pins"][str(seed)]
    need(digest(old)==old_pin,"PINNED_PARENT")
    old_learner=NativeCumulativeLearner.restore(old,old_pin)
    old_other,old_experience=B.legacy_and_experience(old)
    prefix=old_experience["episodes"]
    need(len(prefix)==448,"QUALIFIED_HISTORY")
    models={arm:old_learner.begin_experience_stream() for arm in ARMS}
    histories={arm:list(prefix) for arm in ARMS}
    receipts={arm:[] for arm in ARMS}
    checkpoints=[]
    source_seed=seed+prereg["scenarios"][scenario]["source_seed_offset"]
    cohort=prereg["source_cohort"]+"-"+scenario
    for count in CHECKPOINTS:
        if count:
            for i in range(count-32,count):
                family,regime=prereg["scenarios"][scenario]["phases"][i//32]
                world=B.make_episode(cohort=cohort,seed=source_seed,
                                     index=i,family=family,regime=regime)
                views=B.public_views(world)
                view=views[0]
                for arm in ARMS:
                    model=models[arm]
                    checkpoint_before=digest(model.checkpoint()) if i in (0,32,64,96) else None
                    first,second=policy.choices(model,view,arm,
                                    f"{scenario}/{seed}/{arm}",i)
                    observed=B.rollout(world,first,second)
                    if checkpoint_before is not None:
                        need(digest(model.checkpoint())==checkpoint_before,
                             "POLICY_ALTERED_MODEL_BEFORE_CONSEQUENCE")
                    identity=digest(canonical(["ckad28",SOURCE_SHA,cohort,
                                               source_seed,i,arm]))
                    new=B.retain_event(identity,views,observed)
                    models[arm]=B.admit(model,identity,views,observed)
                    histories[arm].append(new)
                    receipts[arm].append({
                        "event_id":identity,"index":i,
                        "views":[list(x) for x in views],
                        "first_action":observed["x1"],
                        "next_state":observed["s2"],
                        "second_action":observed["x2"],"reward":observed["y"]
                    })
        checkpoints.append(score(models,histories,seed,scenario,count,prereg))
    need(len(checkpoints)==5 and all(len(z)==128 for z in receipts.values()),
         "COMPLETE_PUBLIC_SOURCE")
    new_models={}
    custody={}
    out.mkdir(parents=True,exist_ok=True)
    for arm in ARMS:
        learned=models[arm].consolidate_experience()
        source=learned.checkpoint()
        pin=digest(source)
        restored=NativeCumulativeLearner.restore(source,pin)
        need(restored.checkpoint()==source,"COLD_CHECKPOINT")
        other,experience=B.legacy_and_experience(source)
        actual=experience["episodes"]
        need(other==old_other and len(actual)==576
             and actual[:448]==prefix and actual[448:]==histories[arm][448:]
             and len({z[0] for z in actual})==576,
             "EXACT_CUMULATIVE_EVIDENCE")
        name=f"{scenario}-{seed}-{arm}-native.json"
        (out/name).write_bytes(source)
        new_models[arm]=pin
        custody[arm]={
          "filename":name,"checkpoint_sha256":pin,
          "checkpoint_bytes":len(source),
          "original_prefix_episodes":448,
          "appended_public_episodes":128,
          "cold_restore_exact":True
        }
    need(old_learner.checkpoint()==old,"PARENT_BYTES_CHANGED")
    result={
      "schema":"yggdrasil.ckad28.decision-relevance.case.v1",
      "scenario":scenario,"seed":seed,"source_seed":source_seed,
      "source_cohort":cohort,
      "source_generator_sha256":SOURCE_SHA,
      "parent_commit":PARENT,
      "parent_checkpoint_sha256":old_pin,
      "checkpoints":checkpoints,
      "source_receipts":receipts,
      "custody":custody,
      "source_public_episodes_per_arm":128,
      "held_updates":0,"original_source_actions":0,"protected_first_use":0,
      "scientific_pass":False,"accepted_native":False,"deployment":"NONE",
    }
    result["stable_sha256"]=stable(result)
    result["wall_seconds"]=time.monotonic()-started
    need(result["wall_seconds"]<prereg["budgets"]["max_runtime_seconds_per_case"],
         "SOURCE_CASE_WALL_BUDGET")
    (out/"case-result.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    return result


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--scenario",choices=SCENARIOS,required=True)
    p.add_argument("--seed",type=int,choices=SEEDS,required=True)
    p.add_argument("--output-directory",type=Path,required=True)
    args=p.parse_args()
    z=run_case(args.scenario,args.seed,args.output_directory)
    print(json.dumps({"scenario":z["scenario"],"seed":z["seed"],
                      "stable_sha256":z["stable_sha256"],
                      "wall_seconds":z["wall_seconds"],
                      "final_held":{arm:z["checkpoints"][-1]["by_arm"][arm]["reward_sum"]
                                    for arm in ARMS}},sort_keys=True))
