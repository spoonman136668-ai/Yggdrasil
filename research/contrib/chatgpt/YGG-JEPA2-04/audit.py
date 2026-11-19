"""Independent YGG-JEPA2-04 source/metrics/retention/learned-weight refit audit.

Does not import the campaign module. Regenerates the disjoint public causal
source, authenticates original cumulative Yggdrasil cold checkpoint, recomputes
all scored future labels, prequential loss/thresholds, and independently fits
the new heads from BOTH old witnessed history and new observed consequences.
All facts here are engineering/development, never science first-use.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from yggdrasil.native_context_basis import canonical,digest
from yggdrasil.native_jepa_future import (
    FutureStateHead, NativeFutureStateLearner, targets, primary_truth,
    observed_features, public_observed, UPDATES,
)
from yggdrasil.native_jepa_temporal import NativeTemporalMultiLearner

HERE=Path(__file__).resolve().parent
OLD=HERE.parent/"YGG-JEPA2-03"
PAIRS=((14071,95413),(14072,95429))
PHASES=("stable_A","early_B","late_B","early_return_A","late_return_A")
ARMS=("native","future","direct","beta_full","beta_window24",
      "beta_window48","beta_discount95","mispaired",
      "no_history","no_action","sham")
FROZEN="6d113f776697a3709b46f1c616d2eb66c6e0e857"
PARENT="eee9ab7719f52c1c67ce30b142e8f07f36454dd1"


def check(cond,tag):
    if not cond:raise RuntimeError("YGG_JEPA2_04_AUDIT_"+tag)


def source():
    spec=importlib.util.spec_from_file_location("ygg_jepa4_audit_source",HERE/"source.py")
    d=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(d)
    return d


def gitblob(p):
    return subprocess.check_output(
        ["git","rev-parse","HEAD:"+p.relative_to(ROOT).as_posix()],
        cwd=ROOT,text=True,timeout=20).strip()


def read_old(seed):
    d=json.loads((OLD/f"seed-{seed}-state.json").read_bytes())
    raw=d["state_ascii"].encode("ascii")
    check(digest(raw)==d["state_sha256"],"ORIGINAL_CUSTODY")
    model=NativeTemporalMultiLearner.restore(raw,digest(raw))
    return model


def refit_futures(original,source_impl,newseed):
    """Relearn from original public ledger + new witnessed causal consequences.

    A checkpoint hash alone can be forged; numeric trained-head values MUST
    independently reproduce from the original public action/consequence source.
    """
    ledger=list(original.base.native._ledger)
    heads=(FutureStateHead("sensors"),FutureStateHead("reward"))
    for i in range(len(ledger)-2):
        origin=ledger[i][1]
        plans=tuple((e[2],e[4]) for e in ledger[i:i+3])
        x=observed_features(origin,plans,ledger[:i])
        sensors=[];rewards=[]
        for event in ledger[i:i+3]:
            _,v,first,state,second,reward=event
            u,_,w=public_observed(v)
            sensors.extend((u,state,w))
            rewards.append(reward)
        heads[0].learn(x,np.asarray(sensors,dtype=np.float64))
        heads[1].learn(x,np.asarray(rewards,dtype=np.float64))
    for world in source_impl.WORLDS:
        rows=source_impl.generate(newseed,world)
        pending={}
        for t,row in enumerate(rows):
            if t <= len(rows)-3:
                plans=tuple(source_impl.announced_plan(newseed,world,t+j)
                            for j in range(3))
                pending[t]=observed_features(row["views"],plans,ledger)
            item=(row["source_id"],row["views"],row["row"]["x1"],
                  row["row"]["s2"],row["row"]["x2"],row["row"]["y"])
            ledger.append(item)
            start=t-2
            if start in pending:
                x=pending.pop(start)
                s,r=targets(rows[start:t+1])
                heads[0].learn(x,s);heads[1].learn(x,r)
        check(not pending,"INCOMPLETE_REFIT_WINDOWS")
    return heads,ledger


def metric(rows):
    check(len(rows)>0,"PHASE_EMPTY")
    return {arm:{"brier":sum(t["brier"][arm] for t in rows)/len(rows),
                 "episodes":len(rows)} for arm in ARMS}


def audit(output):
    result=json.loads((output/"result.json").read_bytes())
    check(result["schema"]=="yggdrasil.jepa2-04.future-state-training-result.v1"
          and result["prereg_sha"]==FROZEN and result["parent"]==PARENT
          and result["source_blob"]==gitblob(HERE/"source.py")
          and result["science_pass"] is False
          and result["accepted_native"] is False
          and result["owner_first_use"] is False
          and result["deployment"]=="NONE"
          and len(result["replicas"])==2,"RESULT_SCHEMA_AND_SOURCE")
    check(gitblob(HERE/"prereg.json")==subprocess.check_output(
        ["git","rev-parse",f"{FROZEN}:research/contrib/chatgpt/YGG-JEPA2-04/prereg.json"],
        cwd=ROOT,text=True).strip(),"PREREG_EXACT")
    impl=source()
    verdicts=[]
    for oldseed,newseed in PAIRS:
        model_result=next(x for x in result["replicas"]
                          if x["old_seed"]==oldseed)
        check(model_result["new_seed"]==newseed,"SEED_CUSTODY")
        state=json.loads((output/f"seed-{oldseed}-state.json").read_bytes())
        trace=json.loads((output/f"seed-{oldseed}-trace.json").read_bytes())
        check(len(trace)==2*(impl.EVENTS_PER_WORLD-2)
              and len(set((t["world"],t["source_id"]) for t in trace))
              ==len(trace),"EXACT_WITNESSED_WINDOWS")
        original=read_old(oldseed)
        original_source=list(original.base.native._ledger)
        raw=state["checkpoint_ascii"].encode("ascii")
        check(digest(raw)==state["checkpoint_sha256"],"FULL_COLD_SOURCE_SHA")
        candidate=NativeFutureStateLearner.restore(raw,digest(raw))
        check(candidate.checkpoint()==raw,"EXACT_COLD_RESTORE")
        check(candidate.original.base.native._ledger[:len(original_source)]==
              tuple(original_source),"OLD_WITNESS_PREFIX")
        check(candidate.original.base.native.info()["count"]==
              len(original_source)+2*impl.EVENTS_PER_WORLD,
              "CUMULATIVE_NATIVE_EVENT_COUNT")
        check(model_result["old_native_sha256"]==
              digest(original.base.native.checkpoint()),"ORIGINAL_NATIVE_ID")
        check(model_result["old_five_head_sha256"]==
              digest(original.checkpoint()),"ORIGINAL_LEARNED_MODEL_PIN")
        for world in impl.WORLDS:
            events=impl.generate(newseed,world)
            sub=[row for row in trace if row["world"]==world]
            check(len(sub)==len(events)-2,"WORLD_TRACE_COUNT")
            for i,scored in enumerate(sub):
                row=events[i]
                nextthree=events[i:i+3]
                sens,rew=targets(nextthree)
                check(scored["index"]==i
                      and scored["seed"]==newseed
                      and scored["old_seed"]==oldseed
                      and scored["phase"]==row["phase"]
                      and scored["source_id"]==row["source_id"]
                      and scored["public_views"]==
                          [list(v) for v in row["views"]]
                      and scored["announced_plan"]==
                          [list(x["actions"]) for x in nextthree]
                      and scored["future_observed_public_sensors"]==
                          sens.astype(int).tolist()
                      and scored["future_observed_public_rewards"]==
                          rew.astype(int).tolist()
                      and scored["target_native_s2_and_reward"]==
                          primary_truth(nextthree).astype(int).tolist(),
                      "FUTURE_OBSERVED_SOURCE_RECONSTRUCTION")
                allpred=scored["full_future_forecast"]
                check(len(allpred)==12,"FULL_MULTIVARIATE_READOUT")
                compare=np.concatenate((sens,rew))
                full=float(np.mean((np.asarray(allpred)-compare)**2))
                check(abs(full-scored["full_future_brier"])<=1e-12,
                      "MULTIVARIATE_FUTURE_SCORE")
                truth=primary_truth(nextthree)
                for arm in ARMS:
                    p=np.asarray(scored["forecasts"][arm],dtype=float)
                    check(p.shape==(6,) and bool(np.isfinite(p).all())
                          and bool(((p>=0)&(p<=1)).all()),"FORECAST_SHAPE")
                    brier=float(np.mean((p-truth)**2))
                    check(abs(brier-scored["brier"][arm])<1e-12,
                          "FROZEN_PREQUENTIAL_SCORE")
                witness=candidate.original.base.native._ledger[
                    len(original_source)+world*len(events)+i]
                check(witness[0]==row["source_id"] and
                      witness[1]==row["views"] and
                      witness[2]==row["row"]["x1"] and
                      witness[3]==row["row"]["s2"] and
                      witness[4]==row["row"]["x2"] and
                      witness[5]==row["row"]["y"],
                      "NATIVE_MODEL_PUBLIC_SOURCE_WITNESS")
        metrics={phase:metric([x for x in trace if x["phase"]==phase])
                 for phase in PHASES}
        metrics["pooled_late"]=metric([x for x in trace
                                     if x["phase"] in ("late_B","late_return_A")])
        for phase,values in metrics.items():
            for arm,m in values.items():
                r=model_result["metrics"][phase][arm]
                check(r["episodes"]==m["episodes"]
                      and abs(r["brier"]-m["brier"])<=1e-12,
                      "INDEPENDENT_FROZEN_PHASE_AGGREGATION")
        p=metrics["pooled_late"]
        strong=min(p[k]["brier"] for k in ("direct","beta_full",
                                         "beta_window24","beta_window48",
                                         "beta_discount95"))
        checks={
            "vs_native":p["future"]["brier"]<=p["native"]["brier"]-0.005,
            "vs_conventional":p["future"]["brier"]<=strong-0.005,
            "vs_mispaired":p["future"]["brier"]<=p["mispaired"]["brier"]-0.010,
            "vs_no_history":p["future"]["brier"]<=p["no_history"]["brier"]-0.005,
            "vs_no_actions":p["future"]["brier"]<=p["no_action"]["brier"]-0.005,
            "old_knowledge":model_result["old_brier_after"]<=
                            model_result["old_brier_before"]+0.03,
            "learned_future_variance":
                model_result["target_latent_variance_sensory"]>=0.002
                and model_result["target_latent_variance_reward"]>=0.002,
        }
        check(checks==model_result["predicates"] and
              model_result["development_go"]==all(checks.values())
              and model_result["science_pass"] is False,
              "FROZEN_OBJECTIVE_DECISION")
        # Relearn the entire new future-state mechanism independently and
        # compare *every* trained parameter, not just the enclosing SHA.
        heads,expected_ledger=refit_futures(original,impl,newseed)
        check(tuple(expected_ledger)==
              candidate.original.base.native._ledger,
              "COMPLETE_NATIVE_SOURCE_LEDGER")
        for originalhead,refitted in zip(
                (candidate.sensory,candidate.reward),heads):
            a,b=originalhead.checkpoint(),refitted.checkpoint()
            check(a["kind"]==b["kind"] and
                  a["steps"]==b["steps"] and a["windows"]==b["windows"],
                  "TRAINED_EXPERT_STEP_COUNTS")
            for key in originalhead._fields():
                arr=np.asarray(a[key]);again=np.asarray(b[key])
                check(arr.shape==again.shape
                      and bool(np.isfinite(arr).all())
                      and bool(np.allclose(arr,again,atol=1e-7,rtol=0)),
                      "TRAINED_WEIGHTS_SOURCE_REDERIVATION_"+key)
        check(state["beta_windows"]==candidate.sensory.windows
              and state["direct"]["steps"]==UPDATES*candidate.sensory.windows,
              "SAME_INFORMATION_UPDATE_BUDGET")
        verdicts.append(model_result["development_go"])
    check(result["development_go"]==all(verdicts),"FINAL_BOUNDED_DEVELOPMENT_GATE")
    print("YGG_JEPA2_04_INDEPENDENT_SOURCE_WEIGHT_METRIC_AUDIT_PASS",
          "DEVELOPMENT_GO" if result["development_go"] else "DEVELOPMENT_NO_GO",
          "SCIENCE_NOT_PASS",flush=True)
    return result


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("directory",type=Path)
    args=p.parse_args()
    audit(args.directory)

