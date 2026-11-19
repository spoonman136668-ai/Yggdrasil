"""YGG-CAP01 original trained Yggdrasil seven-head model capacity qualification.

The two already-trained JEPA2-05 native checkpoints (1022/997 original
episodes) stay byte-exact and read-only. On NEW synthetic development sources,
Yggdrasil continues learned native causal cells in bounded shards and all six
cloned specialist weight sets beyond the original 1024-episode cap.

This is actual source-bound native training with prospective action-consequence
data, NOT a scientific demonstration of new-world general intelligence, or
automatic evidence-based memory routing.
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

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from yggdrasil.native_context_basis import canonical,digest
from yggdrasil.native_jepa_future import (
    HORIZON,primary_truth,observed_features,primary_probabilities
)
from yggdrasil.native_segmented_continuation import SegmentedNativeJEPA
from yggdrasil.native_episode_experience import MAX_EPISODES

HERE=Path(__file__).resolve().parent
PRIOR=HERE.parent/"YGG-JEPA2-05"/"original"/"linux"
PREREG_COMMIT="d7107c0f63260684ed47fbf1e6baf32c34922fb4"
SOURCE_BLOB="9e34144de876778d8931b7dacce9b990bb36716a"
PARENT_SHA="7b0d9fd8c16b8e0433a632666cec88d8d008c19f"
PINS={
    14071:{"seed":99601,"n":1022,"blob":"33b648ef36e381a2eb753094f930a4722570b448",
           "sha":"646058e49adf75d2cf74b16b901e801b24ea38f017a717d68fe65a93ab4cad9e"},
    14072:{"seed":99603,"n":997,"blob":"5b9df452e45a1ebc3faadb265ceeffbc580ed7bf",
           "sha":"ef8e1b6daa9b0349d675aee6c30a79d759d6e21c460b5fc900461417c1970609"},
}
ARMS=("archive","active","one_jepa","temporal_jepa","beta_full","beta_window32")
FUTURE_ARMS=("continued_future","frozen_future")
CPU_LIMIT=180.0

def require(ok,tag):
    if not ok:
        raise ValueError("CAP01_CAMPAIGN_"+tag)

def blob(path):
    return subprocess.check_output(
        ["git","rev-parse","HEAD:"+path.relative_to(ROOT).as_posix()],
        cwd=ROOT,text=True,timeout=30).strip()

def source():
    spec=importlib.util.spec_from_file_location("cap01_fresh_source",HERE/"source.py")
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def pin_original(old_seed):
    config=PINS[old_seed]
    path=PRIOR/f"seed-{old_seed}-state.json"
    require(blob(path)==config["blob"],"ORIGINAL_TRAINED_BLOB")
    record=json.loads(path.read_bytes())
    raw=record["model_ascii"].encode("ascii")
    require(digest(raw)==record["model_sha256"]==config["sha"],
            "ORIGINAL_7_COMPONENT_SHA")
    model=SegmentedNativeJEPA.from_archive(raw,config["sha"])
    require(model.original_count==config["n"] and
            model._source.checkpoint()==raw,"ORIGINAL_COLD_MODEL")
    return model,raw

def brier(pred,true):
    p=np.asarray(pred,dtype=float)
    y=np.asarray(true,dtype=float)
    require(p.shape==y.shape and bool(np.isfinite(p).all()) and
            bool(((0<=p)&(p<=1)).all()),"PREQUENTIAL_METRIC")
    return float(np.mean((p-y)**2))

class Beta:
    """Fully fitted same public observations, plus bounded recency control."""
    def __init__(self,original):
        self.ledger=[]
        for _,views,a,s,b,y in original:
            self.observe(views,a,s,b,y)

    def observe(self,views,a,s,b,y):
        self.ledger.append((tuple(views[0]),a,s,b,y))

    def transition(self,view,a,window=None):
        rows=self.ledger if window is None else self.ledger[-window:]
        found=[s for v,x,s,_,_ in rows if v==tuple(view) and x==a]
        return (sum(found)+1)/(len(found)+2)

    def reward(self,view,a,s,b,window=None):
        rows=self.ledger if window is None else self.ledger[-window:]
        found=[y for v,x,z,b2,y in rows if v==tuple(view)
               and x==a and z==s and b2==b]
        return (sum(found)+1)/(len(found)+2)

def old_brier(state,ledger):
    errors=[]
    for _,views,a,s,b,y in ledger[-32:]:
        p=state.archived_forecast(views[0],a)
        q=state.archived_forecast(views[0],a,s,b)
        errors.append(brier([p,q],[s,y]))
    return sum(errors)/len(errors)

def one_seed(old_seed,mod):
    initial=time.perf_counter()
    initial_cpu=time.process_time()
    config=PINS[old_seed]
    seed=config["seed"]
    model,old_raw=pin_original(old_seed)
    original_native=model._source.original.base.native._ledger
    frozen_source_count=len(original_native)
    original_nsha=digest(model._source.original.base.native.checkpoint())
    initial_heads=digest(canonical({
        "one":[x.as_data() for x in model._one],
        "temporal":[x.data() for x in model._temporal],
        "future":[x.checkpoint() for x in model._future],
    }))
    legacy_before=old_brier(model,original_native)
    beta=Beta(original_native)
    events=mod.generate(seed)
    require(len(events)==mod.EVENTS==32,"REGISTERED_SOURCE_EPISODES")
    seen={e[0] for e in original_native}
    pending={}
    trace=[]
    future_trace=[]
    for i,public in enumerate(events):
        require(public["index"]==i and
                public["seed"]==seed and
                public["identifier"] not in seen and
                public["actions"]==mod.announced_plan(seed,i),
                "UNSEEN_PUBLIC_ACTION")
        seen.add(public["identifier"])
        views=public["views"]
        a,b=public["actions"]
        # Pre-first-stage forecasts: NONE may observe s2 or y.
        p_archive=model.archived_forecast(views[0],a)
        p_active=model.active_forecast(views[0],a)
        p_one,p_temporal=model.specialist_forecast(views,a)
        p_full=beta.transition(views[0],a)
        p_window=beta.transition(views[0],a,32)
        # The second stage is conditioned ONLY on now-witnessed s2.
        observed_s2=public["row"]["s2"]
        q_archive=model.archived_forecast(views[0],a,observed_s2,b)
        q_active=model.active_forecast(views[0],a,observed_s2,b)
        q_one,q_temporal=model.specialist_forecast(views,a,observed_s2,b)
        q_full=beta.reward(views[0],a,observed_s2,b)
        q_window=beta.reward(views[0],a,observed_s2,b,32)
        forecasts={
            "archive":(p_archive,q_archive),
            "active":(p_active,q_active),
            "one_jepa":(p_one,q_one),
            "temporal_jepa":(p_temporal,q_temporal),
            "beta_full":(p_full,q_full),
            "beta_window32":(p_window,q_window),
        }
        if i<=len(events)-HORIZON:
            plans=tuple(mod.announced_plan(seed,i+j) for j in range(3))
            require(plans[0]==public["actions"],"PUBLIC_FUTURE_PLANS")
            future=model.future_forecast(views,plans)
            # Control is SAME previously trained weights with no new learning
            # and the SAME history and plans, not a fresh random initializer.
            x=observed_features(views,plans,model._history())
            base=model._source
            frozen=primary_probabilities(
                base.sensory.predict(x),base.reward.predict(x))
            pending[i]={
                "plans":plans,
                "source_id":public["identifier"],
                "forecast":{
                    "continued_future":list(future),
                    "frozen_future":frozen.tolist(),
                }
            }
        # Score both public outcomes before training ANY learned module
        # on this event. The evaluation-only phase never enters any head.
        truth=(public["row"]["s2"],public["row"]["y"])
        trace.append({
            "index":i,"phase":public["phase"],
            "source_id":public["identifier"],
            "views":views,"actions":public["actions"],
            "truth":truth,
            "forecasts":{k:list(v) for k,v in forecasts.items()},
            "brier":{k:brier(v,truth) for k,v in forecasts.items()},
        })
        old_count=model.total_count
        model=model.observe(public["identifier"],views,
                            public["row"],public["post"])
        require(model.total_count==old_count+1,
                "ACTUAL_NEW_NATIVE_TRAINING_COUNT")
        beta.observe(views,a,observed_s2,b,public["row"]["y"])
        start=i-(HORIZON-1)
        if start in pending:
            pred=pending.pop(start)
            window=events[start:i+1]
            expected=primary_truth(tuple(
                {"post":e["post"],"row":e["row"]} for e in window)).tolist()
            f=pred["forecast"]
            future_trace.append({
                "start":start,"phase":window[0]["phase"],
                "source_id":pred["source_id"],
                "plans":[list(x) for x in pred["plans"]],
                "truth":expected,"forecasts":f,
                "brier":{k:brier(v,expected) for k,v in f.items()},
            })
    require(len(trace)==32 and len(future_trace)==30 and not pending,
            "ALL_PUBLIC_FUTURE_OUTCOMES_WITNESSED")
    require(model.original_count==frozen_source_count and
            model.new_count==32 and model.total_count>MAX_EPISODES and
            model._source.checkpoint()==old_raw and
            digest(model._source.original.base.native.checkpoint())==
                original_nsha,"FULL_ORIGINAL_NATIVE_READOUT_PRESERVED")
    require(model.future_windows==30 and
            all(x.steps==96 for x in (*model._one,*model._temporal)) and
            all(x.windows==orig.windows+30
                for x,orig in zip(model._future,
                    (model._source.sensory,model._source.reward))),
            "ACTUAL_SIX_HEADS_CONTINUE")
    after_heads=digest(canonical({
        "one":[x.as_data() for x in model._one],
        "temporal":[x.data() for x in model._temporal],
        "future":[x.checkpoint() for x in model._future],
    }))
    require(after_heads!=initial_heads,
            "TRAINED_SIX_HEAD_PARAMETERS_CHANGED")
    legacy_after=old_brier(model,original_native)
    require(legacy_before==legacy_after,
            "OLD_CAUSAL_READOUT_MUTATION")
    checkpoint=model.checkpoint()
    restored=SegmentedNativeJEPA.restore(checkpoint,digest(checkpoint))
    require(restored.checkpoint()==checkpoint and
            restored.archive_sha256==config["sha"],
            "FULL_TRAINED_COLD_REPLAY")
    report={
        "old_seed":old_seed,"seed":seed,
        "original_count":frozen_source_count,
        "new_count":model.new_count,"total_count":model.total_count,
        "old_source_sha256":config["sha"],
        "old_native_sha256":original_nsha,
        "original_six_head_sha256":initial_heads,
        "trained_six_head_sha256":after_heads,
        "final_segmented_sha256":digest(checkpoint),
        "final_checkpoint_bytes":len(checkpoint),
        "shard_counts":[len(s._ledger) for s in model._segments],
        "four_prior_head_epoch_updates":[x.steps for x in
                                        (*model._one,*model._temporal)],
        "future_new_windows":model.future_windows,
        "old_native_historical_brier_before":legacy_before,
        "old_native_historical_brier_after":legacy_after,
        "archived_original_model_byte_exact":True,
        "cold_forgery_checked":True,
        "old_replay_used_as_held_science":False,
        "development_trained":True,
        "science_pass":False,
        "late_step_brier":{
            arm:float(np.mean([z["brier"][arm] for z in trace[22:]]))
            for arm in ARMS
        },
        "late_future_brier":{
            arm:float(np.mean([z["brier"][arm]
                for z in future_trace if z["start"]>=22]))
            for arm in FUTURE_ARMS
        },
    }
    elapsed=time.process_time()-initial_cpu
    require(elapsed<=CPU_LIMIT,"CPU_PROCESS_BUDGET")
    times={"seed":seed,"cpu_seconds":elapsed,
           "wall_seconds":time.perf_counter()-initial}
    state={
        "old_seed":old_seed,"seed":seed,
        "old_model_sha256":config["sha"],
        "continued_sha256":digest(checkpoint),
        "continued_ascii":checkpoint.decode("ascii"),
    }
    return report,state,trace,future_trace,times

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    expected=subprocess.check_output([
        "git","rev-parse",PREREG_COMMIT+
        ":research/contrib/chatgpt/YGG-CAP01/prereg.json"],
        cwd=ROOT,text=True,timeout=30).strip()
    require(blob(HERE/"prereg.json")==expected,
            "ORIGINAL_FROZEN_PROTOCOL")
    require(blob(HERE/"source.py")==SOURCE_BLOB,
            "FROZEN_FIRST_USE_DEVELOPMENT_SOURCE")
    require(MAX_EPISODES==1024,"INHERITED_NATIVE_CONTRACT_UNCHANGED")
    args.output.mkdir(parents=True,exist_ok=True)
    src=source()
    reports=[]
    timings=[]
    for old_seed in sorted(PINS):
        report,state,trace,future,timing=one_seed(old_seed,src)
        reports.append(report)
        timings.append(timing)
        for name,item in (
            (f"seed-{old_seed}-state.json",state),
            (f"seed-{old_seed}-trace.json",trace),
            (f"seed-{old_seed}-future.json",future),
        ):
            (args.output/name).write_bytes(canonical(item))
        print("YGG_CAP01_ORIGINAL_7_COMPONENT_CONTINUES",
              report["original_count"],"to",report["total_count"],
              "new",report["new_count"],"heads",6,
              "archived_byte_exact",True,flush=True)
    result={
        "schema":"yggdrasil.cap01.original-native-capacity-development.v1",
        "frozen_protocol":PREREG_COMMIT,
        "parent_sha":PARENT_SHA,
        "new_source_blob":SOURCE_BLOB,
        "replicas":reports,
        "engineering_development_go":all(
            r["archived_original_model_byte_exact"] and
            r["old_native_historical_brier_before"]==
              r["old_native_historical_brier_after"] and
            r["total_count"]>1024 and r["future_new_windows"]==30
            for r in reports),
        "scientific_pass":False,
        "proven_native_causal_gain":False,
        "original_first_use":False,
        "deployment":"NONE",
    }
    (args.output/"result.json").write_bytes(canonical(result))
    (args.output/"timings.json").write_bytes(canonical(timings))
    print("YGG_CAP01_"+("ENGINEERING_DEVELOPMENT_GO" if
          result["engineering_development_go"] else
          "ENGINEERING_DEVELOPMENT_NO_GO")+
          " SCIENCE_UNVERIFIED",flush=True)

if __name__=="__main__":
    main()
