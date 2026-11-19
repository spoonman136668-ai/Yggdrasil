"""Source-frozen actual Yggdrasil continuation: three-step learned future states.

Two original JEPA2-03 native cumulative checkpoints remain the model.
No surrogate native learner or new controller. New public interventions from
a different multivariate causal source are scored before outcomes are revealed.
All 7 previously or newly trained components retain their parameter state.
This is development-only synthetic training, NOT scientific first-use.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys
import time
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_jepa_temporal import NativeTemporalMultiLearner
from yggdrasil.native_jepa_future import (
    FutureStateHead, NativeFutureStateLearner, DirectLogistic, UPDATES,
    HORIZON, DIM, _sigmoid, public_observed, observed_features,
    targets, primary_truth, primary_probabilities,
)
from yggdrasil.native_episode_experience import NativeEpisodeExperience

HERE = Path(__file__).resolve().parent
ORIGINAL = HERE.parent / "YGG-JEPA2-03"
PREREG_SHA = "6d113f776697a3709b46f1c616d2eb66c6e0e857"
PARENT_SHA = "eee9ab7719f52c1c67ce30b142e8f07f36454dd1"
PAIRS = ((14071, 95413), (14072, 95429))
PHASES = ("stable_A", "early_B", "late_B", "early_return_A", "late_return_A")
ARMS = ("native", "future", "direct", "beta_full", "beta_window24",
        "beta_window48", "beta_discount95", "mispaired",
        "no_history", "no_action", "sham")
LATE = ("late_B", "late_return_A")
MAX_CPU = 150.0


def check(cond, label):
    if not cond:
        raise RuntimeError("YGG_JEPA2_04_" + label)


def blob(path):
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD:" + path.relative_to(ROOT).as_posix()],
        cwd=ROOT, text=True, timeout=20).strip()


def load_source():
    spec = importlib.util.spec_from_file_location(
        "ygg_jepa2_04_frozen_source", HERE / "source.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def old_bootstrap(seed):
    path = ORIGINAL / f"seed-{seed}-state.json"
    record = json.loads(path.read_bytes())
    raw = record["state_ascii"].encode("ascii")
    check(digest(raw) == record["state_sha256"], "OLD_EXACT_CHECKPOINT_SHA")
    prior = NativeTemporalMultiLearner.restore(raw, digest(raw))
    check(prior.checkpoint() == raw, "OLD_FIVE_COMPONENT_COLD")
    return NativeFutureStateLearner(prior)


def old_window(ledger, i):
    """Retrospective already observed prior source, never evaluated as new."""
    out = []
    for e in ledger[i:i+HORIZON]:
        _, v, a, state, b, reward = e
        u, _, w = public_observed(v)
        out.append({"post": (u, state, w),
                    "row": {"s1":u,"x1":a,"s2":state,"x2":b,"y":reward}})
    return tuple(out)


def pack(w):
    s,r=targets(w)
    return np.concatenate((s,r))


def primary12(v):
    v=np.asarray(v,dtype=np.float64)
    check(v.shape==(12,), "PRIMARY_12")
    return primary_probabilities(v[:9],v[9:])


def mse(p,y):
    p,y=np.asarray(p,dtype=np.float64),np.asarray(y,dtype=np.float64)
    check(p.shape==y.shape==(6,) and bool(np.isfinite(p).all()),
          "PREQUENTIAL_SHAPE_FINITE")
    check(bool(((0<=p)&(p<=1)).all()),"PROBABILITY_RANGE")
    return float(np.mean((p-y)**2))


def full_mse(p,y):
    check(len(p)==len(y)==12,"FULL_FUTURE_TARGET_LENGTH")
    return float(np.mean((np.asarray(p)-np.asarray(y))**2))


class Counts:
    """History-window Beta controls, same announced plans/current public view."""
    def __init__(self):
        self.windows=[]

    def update(self, context, plans, y):
        c=tuple(context)
        bits=np.asarray(y,dtype=np.float64)
        check(bits.shape==(6,), "COUNT_LABEL")
        self.windows.append((c, tuple(tuple(v) for v in plans),
                             tuple(int(v) for v in bits)))

    def probabilities(self, context, plans, arm):
        context=tuple(context)
        check(arm in ("beta_full","beta_window24","beta_window48",
                      "beta_discount95"),"COUNT_ARM")
        source=self.windows
        if arm=="beta_window24":source=source[-24:]
        if arm=="beta_window48":source=source[-48:]
        pred=[]
        for h, action in enumerate(plans):
            for label in (0,1):
                numerator=1.0;denominator=2.0
                for i,(oldcontext,oldplans,outcomes) in enumerate(source):
                    if oldcontext==context and oldplans[h]==tuple(action):
                        weight=(0.95**(len(source)-i-1)
                                if arm=="beta_discount95" else 1.)
                        numerator+=weight*outcomes[2*h+label]
                        denominator+=weight
                pred.append(numerator/denominator)
        return np.asarray(pred,dtype=np.float64)


def native_forecast(native,views,plans):
    """No FUTURE labels: explicitly marginalize unobserved s2 before reward."""
    forecaster=native.base.native
    priorview=tuple(views[0])
    out=[]
    for a,b in plans:
        p=float(forecaster.context_forecast(priorview,a))
        reward0=float(forecaster.context_forecast(priorview,a,0,b))
        reward1=float(forecaster.context_forecast(priorview,a,1,b))
        r=(1-p)*reward0+p*reward1
        out.extend((p,r))
    out=np.asarray(out,dtype=np.float64)
    check(out.shape==(6,) and bool(((0<=out)&(out<=1)).all()),
          "NO_FUTURE_LEAK_NATIVE")
    return out


def build_model(seed):
    model=old_bootstrap(seed)
    ledger=model.original.base.native._ledger
    old_source=tuple(ledger)
    direct=DirectLogistic()
    counts=Counts()
    sham=(FutureStateHead("sensors"),FutureStateHead("reward"))
    no_history=(FutureStateHead("sensors"),FutureStateHead("reward"))
    no_action=(FutureStateHead("sensors"),FutureStateHead("reward"))
    prior_observed=[]
    for i in range(len(ledger)-HORIZON+1):
        window=old_window(ledger,i)
        y=pack(window)
        base=ledger[i]
        v=base[1]
        planned=tuple((e[2],e[4]) for e in ledger[i:i+HORIZON])
        x=observed_features(v,planned,ledger[:i])
        hist=observed_features(v,planned,ledger[:i],no_history=True)
        noact=observed_features(v,planned,ledger[:i],no_actions=True)
        model.learn_window(x,window)
        direct.learn(x,y)
        counts.update(public_observed(v),planned,primary12(y))
        sham_target=(prior_observed[i-23] if i>=23 else 1-y)
        sham[0].learn(x,sham_target[:9])
        sham[1].learn(x,sham_target[9:])
        for pair,feature in ((no_history,hist),(no_action,noact)):
            pair[0].learn(feature,y[:9]);pair[1].learn(feature,y[9:])
        prior_observed.append(y)
    check(model.sensory.windows==model.reward.windows==
          direct.steps//UPDATES and len(counts.windows)==len(prior_observed),
          "WARM_SOURCE_STEP_PARITY")
    return model,direct,counts,sham,no_history,no_action,prior_observed,old_source


def source_score(groups):
    return {arm:{"brier":sum(x["brier"][arm] for x in groups)/len(groups),
                 "episodes":len(groups)}
            for arm in ARMS}


def run_seed(oldseed,newseed,source):
    started=time.perf_counter()
    started_cpu=time.process_time()
    (model,direct,counts,sham,no_history,no_action,
     known_targets,old_source)=build_model(oldseed)
    old_count=len(old_source)
    check(600<old_count<750,"CUMULATIVE_PARENT")
    old_prefix_sha=digest(model.original.base.native.checkpoint())
    old_checkpoint_sha=digest(model.original.checkpoint())
    old_readouts=[]
    for item in old_source[-32:]:
        _,v,a,s,b,r=item
        p=model.original.base.predict(v,a,s,b,stream=True)["native"]
        old_readouts.append(((p[0]-s)**2+(p[1]-r)**2)/2)
    old_brier_before=sum(old_readouts)/len(old_readouts)
    reference=NativeEpisodeExperience.restore(
        model.original.base.native.checkpoint(),old_prefix_sha)
    seen={item[0] for item in old_source}
    trace=[]
    receipts=[]
    embeddings_s=[];embeddings_r=[]
    for world in source.WORLDS:
        events=source.generate(newseed,world)
        check(len(events)==source.EVENTS_PER_WORLD,"WORLD_COUNT")
        initial=len(model.original.base.native._ledger)
        before_sha=digest(model.checkpoint())
        pending={}
        for t,row in enumerate(events):
            views=row["views"]
            check(row["source_id"] not in seen, "SOURCE_DUPLICATE")
            seen.add(row["source_id"])
            # All three future ACTIONS were precommitted and publicly
            # announced; ONLY their actions (never future states) are read.
            if t<=len(events)-HORIZON:
                plan=tuple(source.announced_plan(newseed,world,t+i)
                           for i in range(HORIZON))
                check(plan[0]==row["actions"],"PUBLIC_PLAN_FIRST_ACTION")
                ledger=model.original.base.native._ledger
                x=observed_features(views,plan,ledger)
                sensor, reward=model.forecast(views,plan,ledger)
                combined=np.concatenate((sensor,reward))
                negative=np.concatenate(
                    (sham[0].predict(x),sham[1].predict(x)))
                nohist_x=observed_features(views,plan,ledger,no_history=True)
                noaction_x=observed_features(views,plan,ledger,no_actions=True)
                nohist=np.concatenate([a.predict(nohist_x) for a in no_history])
                noact=np.concatenate([a.predict(noaction_x) for a in no_action])
                ctx=public_observed(views)
                forecasts={
                    "native":native_forecast(model.original,views,plan),
                    "future":primary12(combined),
                    "direct":primary12(direct.predict(x)),
                    "mispaired":primary12(negative),
                    "no_history":primary12(nohist),
                    "no_action":primary12(noact),
                    "sham":np.full(6,.5),
                }
                for arm in ("beta_full","beta_window24","beta_window48",
                            "beta_discount95"):
                    forecasts[arm]=counts.probabilities(ctx,plan,arm)
                pending[t]={"index":t,"phase":row["phase"],
                            "source_id":row["source_id"],
                            "views":views,"plan":plan,"x":x,
                            "nohist_x":nohist_x,"noaction_x":noaction_x,
                            "forecast":forecasts,
                            "full_pred":combined}
            before=model.original.base.native._ledger
            model.observe_native(row["source_id"],views,row["row"])
            reference=reference.observe(row["source_id"],views,row["row"])
            # AFTER public consequence revelation of t, the oldest pending
            # 3-step forecast has become fully observable; score FIRST.
            start=t-(HORIZON-1)
            if start in pending:
                entry=pending.pop(start)
                window=events[start:t+1]
                expected=primary_truth(window)
                sensory,rewards=targets(window)
                y=np.concatenate((sensory,rewards))
                losses={arm:mse(p,expected)
                        for arm,p in entry["forecast"].items()}
                trace.append({
                    "old_seed":oldseed,"seed":newseed,"world":world,
                    "index":start,"phase":entry["phase"],
                    "source_id":entry["source_id"],
                    "announced_plan":entry["plan"],
                    "public_views":entry["views"],
                    "future_observed_public_sensors":sensory.astype(int).tolist(),
                    "future_observed_public_rewards":rewards.astype(int).tolist(),
                    "target_native_s2_and_reward":expected.astype(int).tolist(),
                    "forecasts":{k:v.tolist() for k,v in entry["forecast"].items()},
                    "brier":losses,
                    "full_future_brier":full_mse(entry["full_pred"],y),
                })
                embeddings_s.append(sensory)
                embeddings_r.append(rewards)
                # Model learning and ALL controls occur strictly AFTER scoring,
                # and after 3 real native witness outcomes have been revealed.
                model.learn_window(entry["x"],window)
                direct.learn(entry["x"],y)
                counts.update(public_observed(entry["views"]),entry["plan"],expected)
                previous=(known_targets[-23] if len(known_targets)>=23 else 1-y)
                sham[0].learn(entry["x"],previous[:9])
                sham[1].learn(entry["x"],previous[9:])
                for pair,feature in ((no_history,entry["nohist_x"]),
                                     (no_action,entry["noaction_x"])):
                    pair[0].learn(feature,sensory)
                    pair[1].learn(feature,rewards)
                known_targets.append(y)
        check(not pending, "UNRESOLVED_FUTURE_WINDOW")
        native_state=model.original.base.native
        check(native_state.checkpoint()==reference.checkpoint(),
              "EXISTING_NATIVE_SOURCE_REPLAY")
        check(tuple(native_state._ledger[:old_count])==old_source,
              "OLD_NATIVE_SOURCE_PREFIX_DAMAGE")
        check(native_state.info()["count"]==initial+len(events)<1000,
              "FULL_CUMULATIVE_CAPACITY")
        raw=model.checkpoint()
        restored=NativeFutureStateLearner.restore(raw,digest(raw))
        check(restored.checkpoint()==raw,"COLD_TRAINED_FUTURE")
        check(restored.original.checkpoint()==model.original.checkpoint(),
              "COLD_NATIVE_AND_FOUR_PRIOR_HEADS")
        receipts.append({
            "world":world,"source_episodes":len(events),
            "native_prior_count":initial,
            "native_after_count":native_state.info()["count"],
            "post_native_sha256":digest(native_state.checkpoint()),
            "post_five_component_sha256":digest(model.original.checkpoint()),
            "post_full_future_checkpoint_sha256":digest(raw),
            "post_full_future_checkpoint_bytes":len(raw),
            "checkpoint_cold_restore_pass":True,
            "old_native_prefix_retained":True,"no_hidden_phases_in_training":True,
        })
    sample_s=np.asarray(embeddings_s)
    sample_r=np.asarray(embeddings_r)
    var_s=model.sensory.variance(sample_s)
    var_r=model.reward.variance(sample_r)
    check(model.sensory.windows==model.reward.windows==
          sham[0].windows==sham[1].windows==
          no_history[0].windows==no_history[1].windows==
          no_action[0].windows==no_action[1].windows==
          len(counts.windows)==direct.steps//UPDATES,"ALL_WINDOWS_UPDATE_BUDGET")
    check(model.original.base.native._ledger[:old_count]==old_source,
          "FINAL_NATIVE_OLD_WITNESS_PROTECTION")
    old_readouts_after=[]
    for item in old_source[-32:]:
        _,v,a,s,b,r=item
        p=model.original.base.predict(v,a,s,b,stream=True)["native"]
        old_readouts_after.append(((p[0]-s)**2+(p[1]-r)**2)/2)
    old_brier_after=sum(old_readouts_after)/len(old_readouts_after)
    metrics={phase:source_score([x for x in trace if x["phase"]==phase])
             for phase in PHASES}
    pooled=[x for x in trace if x["phase"] in LATE]
    metrics["pooled_late"]=source_score(pooled)
    p=metrics["pooled_late"]
    champion=min(p[k]["brier"] for k in
                 ("direct","beta_full","beta_window24","beta_window48",
                  "beta_discount95"))
    preds={
        "vs_native":p["future"]["brier"]<=p["native"]["brier"]-0.005,
        "vs_conventional":p["future"]["brier"]<=champion-0.005,
        "vs_mispaired":p["future"]["brier"]<=p["mispaired"]["brier"]-0.010,
        "vs_no_history":p["future"]["brier"]<=p["no_history"]["brier"]-0.005,
        "vs_no_actions":p["future"]["brier"]<=p["no_action"]["brier"]-0.005,
        "old_knowledge":old_brier_after<=old_brier_before+0.03,
        "learned_future_variance":var_s>=0.002 and var_r>=0.002,
    }
    raw=model.checkpoint()
    cpu=time.process_time()-started_cpu
    check(cpu<=MAX_CPU,"FROZEN_CPU_BUDGET")
    report={
        "old_seed":oldseed,"new_seed":newseed,
        "old_retained_episodes":old_count,"new_observed_episodes":240,
        "old_native_sha256":old_prefix_sha,
        "old_five_head_sha256":old_checkpoint_sha,
        "world_receipts":receipts,
        "future_windows_train_count":model.sensory.windows,
        "old_brier_before":old_brier_before,"old_brier_after":old_brier_after,
        "target_latent_variance_sensory":var_s,
        "target_latent_variance_reward":var_r,
        "metrics":metrics,"strongest_control":champion,
        "predicates":preds,"development_go":all(preds.values()),
        "science_pass":False,"cpu_seconds":cpu,
        "wall_seconds":time.perf_counter()-started,
    }
    state={"old_seed":oldseed,"new_seed":newseed,
           "checkpoint_sha256":digest(raw),"checkpoint_ascii":raw.decode("ascii"),
           "direct":{"steps":direct.steps,"w":direct.w.tolist(),
                     "b":direct.b.tolist()},
           "negative":{"sensory":sham[0].checkpoint(),
                       "reward":sham[1].checkpoint()},
           "no_history":{"sensory":no_history[0].checkpoint(),
                         "reward":no_history[1].checkpoint()},
           "no_action":{"sensory":no_action[0].checkpoint(),
                       "reward":no_action[1].checkpoint()},
           "beta_windows":len(counts.windows)}
    return report,state,trace


def main():
    arg=argparse.ArgumentParser()
    arg.add_argument("--output",type=Path,required=True)
    a=arg.parse_args()
    a.output.mkdir(parents=True,exist_ok=True)
    check(blob(HERE/"prereg.json")==subprocess.check_output(
        ["git","rev-parse",f"{PREREG_SHA}:research/contrib/chatgpt/YGG-JEPA2-04/prereg.json"],
        cwd=ROOT,text=True).strip(),"FROZEN_PREREG_BLOB")
    source=load_source()
    cases=[]
    for oldseed,newseed in PAIRS:
        report,state,trace=run_seed(oldseed,newseed,source)
        cases.append(report)
        (a.output/f"seed-{oldseed}-state.json").write_bytes(canonical(state))
        (a.output/f"seed-{oldseed}-trace.json").write_bytes(canonical(trace))
        print("YGG_JEPA2_04_TRAINED",oldseed,newseed,
              "new_real_native_episodes",report["new_observed_episodes"],
              "development_go",report["development_go"],flush=True)
    result={"schema":"yggdrasil.jepa2-04.future-state-training-result.v1",
            "prereg_sha":PREREG_SHA,"parent":PARENT_SHA,
            "source_blob":blob(HERE/"source.py"),
            "architecture":"one cumulative original native + four old JEPA + two new independently trainable multi-step future-state EMA JEPA",
            "development_go":all(x["development_go"] for x in cases),
            "science_pass":False,"accepted_native":False,
            "owner_first_use":False,"deployment":"NONE",
            "replicas":cases,
            "note":"New disjoint SYNTHETIC causal DEVELOPMENT family with delayed 3-step action-conditioned PUBLIC future sensory/reward targets; not independent external scientific evidence."}
    (a.output/"result.json").write_bytes(canonical(result))
    print("YGG_JEPA2_04_DEVELOPMENT_"+("GO" if result["development_go"]
                                     else "NO_GO")+" SCIENCE_NOT_PASS",flush=True)


if __name__=="__main__":
    main()

