"""YGG-CAP02 original cumulative native + six JEPA, prospective causal recall screen.

One authentic original trained CAP01 model on each OS per replica. All parent
witnessed interventions and learned weights remain intact; 48 new actions
continue native/shard/six-head training, while a separate structural
evidence-selected bank learns from those same source observations. No source
actor actions, hidden oracle phase labels, or external scientific first-use.
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

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from yggdrasil.native_context_basis import canonical,digest
from yggdrasil.native_segmented_continuation import SegmentedNativeJEPA
from yggdrasil.native_causal_rule_memory import CausalMemory,CausalPosterior,_features

HERE=Path(__file__).resolve().parent
PREREG_SHA="d07b9ac4448b4c23288f4f9a76aec7f2c69faa55"
SOURCE_BLOB="bcae839c6f43ecf14fc1a1a2f3ce7ac813f501bf"
PARENT_SHA="3770e660bc8b908218e6fe82e176bd4bf91158d9"
OLD={
 14071:{"seed":99811,"prior_seed":99601,"full_count":1054,
        "linux":{"blob":"f4568f284605556f970d7f2cc4733577f09de244",
                 "sha":"6babc23f4baf30afde14db5f2ca8eb3e55e321169aa245482478ff9855b68f14"},
        "windows":{"blob":"db50019c5ae9d8e8e16a24792f01fc50a0414b29",
                   "sha":"2d08c7e2d6d4d80acfc53727cdd0880d3f632c0f44bdb405b78feffba405938e"}},
 14072:{"seed":99829,"prior_seed":99603,"full_count":1029,
        "linux":{"blob":"371afb1e830d6790b948ceda06f8260e7070260b",
                 "sha":"c503ccf979f90d6d4954f0e8d42133fc177017d4b47de80ee64c9524b870d827"},
        "windows":{"blob":"9e233e46a4fbc683c8a1388441791cad16b42f2a",
                   "sha":"e09b0cbbe47b95686f3ed3732baf080fe6b47301f0128c360437bf29bf9dfbfb"}}
}
PARENT_RESULT_BLOB="f0d0542f61ecfabfa10c5d4344fa7f5178540cac"
ARMS=("evidence","uniform","latest","action_masked",
      "full_rule","recent24_rule","beta_full","beta_window24",
      "beta_discount95","archive","active","one_jepa","temporal_jepa")
CPU_LIMIT=300
LATE_B=tuple(range(24,32))
LATE_RETURN=tuple(range(40,48))

def require(cond,name):
    if not cond:
        raise ValueError("CAP02_CAMPAIGN_"+name)

def blob(path):
    return subprocess.check_output(
        ["git","rev-parse","HEAD:"+path.relative_to(ROOT).as_posix()],
        cwd=ROOT,text=True,timeout=30).strip()

def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    obj=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

def platform():
    return "windows" if sys.platform=="win32" else "linux"

def pin_old(old_seed):
    pin=OLD[old_seed][platform()]
    path=HERE.parent/"YGG-CAP01"/"original"/platform()/f"seed-{old_seed}-state.json"
    require(blob(path)==pin["blob"],"PLATFORM_ORIGINAL_BLOB")
    original=json.loads(path.read_bytes())
    raw=original["continued_ascii"].encode("ascii")
    require(digest(raw)==original["continued_sha256"]==pin["sha"],
            "PLATFORM_ORIGINAL_SOURCE")
    model=SegmentedNativeJEPA.restore(raw,pin["sha"])
    require(model.total_count==OLD[old_seed]["full_count"] and
            model.new_count==32 and model.checkpoint()==raw,
            "PLATFORM_COLD_MODEL_ORIGINAL")
    return model,raw

def rule_predict(pair,views,a,s2=None,b=None):
    return (pair[0].predict(_features(views,a)) if s2 is None else
            pair[1].predict(_features(views,a,s2,b)))

def new_rule_pair():
    return CausalPosterior(4),CausalPosterior(6)

def rule_learn(pair,views,a,s2,b,y):
    pair[0].learn(_features(views,a),s2)
    pair[1].learn(_features(views,a,s2,b),y)

def prior_view(event):
    # Tuple native six-stage and CAP01 seven-stage source records supported.
    identifier,views,a,s2,b,y=event[:6]
    return views,a,s2,b,y

def fit_rule_rows(rows):
    pair=new_rule_pair()
    for event in rows:
        views,a,s2,b,y=prior_view(event)
        rule_learn(pair,views,a,s2,b,y)
    return pair

def probability_discount(beta,view,a,s2=None,b=None):
    weights=[]
    targets=[]
    history=beta.ledger
    for age,(v,x,s,x2,y) in enumerate(reversed(history)):
        match=(v==tuple(view) and x==a)
        if s2 is not None:
            match=match and s==s2 and x2==b
        if match:
            weights.append(.95**age)
            targets.append(s if s2 is None else y)
    count=sum(weights)
    return (1+sum(w*y for w,y in zip(weights,targets)))/(2+count)

def brier(pred,true):
    require(len(pred)==len(true)==2 and
            all(math.isfinite(p) and 0<=p<=1 for p in pred),
            "PREQUENTIAL_BOUNDS")
    return sum((p-y)**2 for p,y in zip(pred,true))/2

def historical_brier(model):
    rows=model._source.original.base.native._ledger[-32:]
    return sum(brier(
        [model.archived_forecast(views[0],a),
         model.archived_forecast(views[0],a,s2,b)],
        (s2,y))
        for _,views,a,s2,b,y in rows)/len(rows)

def run_seed(old_seed,src,cap01):
    clock=time.perf_counter()
    cpu=time.process_time()
    pin=OLD[old_seed]
    seed=pin["seed"]
    model,old_raw=pin_old(old_seed)
    old_prefix=model._events
    memory=CausalMemory.from_native(model)
    original_bank_sha=memory.prior_sha256
    original_native_archive_sha=model.archive_sha256
    history_prefix=model._history()
    historic_before=historical_brier(model)
    # Full fitted rule posterior includes ALL previous 1,000+ witnessed
    # native actions, not just 32 source-specific CAP01 development episodes.
    full=fit_rule_rows(history_prefix)
    beta=cap01.Beta(history_prefix)
    future=src.generate(seed)
    require(len(future)==48 and memory.total==32 and
            memory.bank_sizes==(16,16) and model.new_count==32,
            "NEW_DISJOINT_INITIAL_CONDITION")
    seen={e[0] for e in history_prefix}
    rows=[]
    history=list(history_prefix)
    initial_head_steps=[x.steps for x in (*model._one,*model._temporal)]
    initial_future_windows=[x.windows for x in model._future]
    for i,event in enumerate(future):
        views=event["views"]
        a,b=event["actions"]
        require(event["index"]==i and
                event["identifier"] not in seen and
                event["actions"]==src.announced_plan(seed,i),
                "SOURCE_AND_PREANNOUNCED_ACTION")
        seen.add(event["identifier"])
        # First stage: neither s2 nor reward enters any forecaster.
        start={}
        for arm in ("evidence","uniform","latest","action_masked"):
            start[arm]=memory.forecast(views,a,variant=arm)
        start["full_rule"]=rule_predict(full,views,a)
        recent=fit_rule_rows(history[-24:])
        start["recent24_rule"]=rule_predict(recent,views,a)
        start["beta_full"]=beta.transition(views[0],a)
        start["beta_window24"]=beta.transition(views[0],a,24)
        start["beta_discount95"]=probability_discount(beta,views[0],a)
        start["archive"]=model.archived_forecast(views[0],a)
        start["active"]=model.active_forecast(views[0],a)
        one,temporal=model.specialist_forecast(views,a)
        start["one_jepa"],start["temporal_jepa"]=one,temporal
        # Witness s2 only. Second-stage prediction is PRE-reward.
        s2=event["row"]["s2"]
        finish={}
        for arm in ("evidence","uniform","latest","action_masked"):
            finish[arm]=memory.forecast(views,a,s2,b,variant=arm)
        finish["full_rule"]=rule_predict(full,views,a,s2,b)
        finish["recent24_rule"]=rule_predict(recent,views,a,s2,b)
        finish["beta_full"]=beta.reward(views[0],a,s2,b)
        finish["beta_window24"]=beta.reward(views[0],a,s2,b,24)
        finish["beta_discount95"]=probability_discount(beta,views[0],a,s2,b)
        finish["archive"]=model.archived_forecast(views[0],a,s2,b)
        finish["active"]=model.active_forecast(views[0],a,s2,b)
        one,temporal=model.specialist_forecast(views,a,s2,b)
        finish["one_jepa"],finish["temporal_jepa"]=one,temporal
        require(set(start)==set(finish)==set(ARMS),
                "CONTROL_COMPLETE")
        # All arm forecasts are frozen BEFORE the second-stage outcome.
        forecasts={arm:[float(start[arm]),float(finish[arm])]
                   for arm in ARMS}
        truth=[s2,event["row"]["y"]]
        rows.append({
            "index":i,"source_id":event["identifier"],
            "phase":event["phase"],   # Evaluator never passed to any model
            "seed":seed,              # Evaluator never passed to any model
            "public_views":views,"announced_actions":event["actions"],
            "public_truth":truth,
            "prequential":forecasts,
            "brier":{arm:brier(pred,truth)
                     for arm,pred in forecasts.items()},
            "bank_sizes_before":list(memory.bank_sizes),
            "posterior_weights_before":list(memory._weights()),
        })
        # ONLY NOW update all native and causal learners with the actually
        # witnessed action-consequence row, no rewind/restart.
        memory.observe(event["identifier"],views,event["row"],event["post"])
        model=model.observe(event["identifier"],views,event["row"],event["post"])
        rule_learn(full,views,a,s2,b,event["row"]["y"])
        beta.observe(views,a,s2,b,event["row"]["y"])
        history.append((
            event["identifier"],views,a,s2,b,event["row"]["y"]))
    require(len(rows)==48 and model._events[:32]==old_prefix and
            model.new_count==80 and memory.new_count==48 and
            memory.total==80 and memory.bank_sizes==(16,16,16,16,16) and
            model.total_count==pin["full_count"]+48 and
            [len(shard._ledger) for shard in model._segments]==[64,16],
            "ACTUAL_CUMULATIVE_TRAINING_AND_SHARD_ROLLOVER")
    require([x.steps for x in (*model._one,*model._temporal)]==
            [i+144 for i in initial_head_steps] and
            [x.windows for x in model._future]==
            [i+48 for i in initial_future_windows],
            "ALL_SIX_PREVIOUSLY_FITTED_HEADS_CONTINUED")
    hist_after=historical_brier(model)
    require(hist_after==historic_before and
            model._source.checkpoint()==json.loads(old_raw)["archive_ascii"].encode("ascii") and
            model.archive_sha256==original_native_archive_sha,
            "IMMUTABLE_OLDER_SEVEN_COMPONENT_ARCHIVE")
    model_raw=model.checkpoint()
    memory_raw=memory.checkpoint()
    require(SegmentedNativeJEPA.restore(model_raw,digest(model_raw)).checkpoint()==
            model_raw,"COLD_NATIVE_EXACT")
    require(CausalMemory.restore(memory_raw,digest(memory_raw),old_prefix).checkpoint()==
            memory_raw,"COLD_CAUSAL_MEMORY_EXACT")
    late_b={arm:sum(rows[i]["brier"][arm] for i in LATE_B)/len(LATE_B)
            for arm in ARMS}
    late_return={
        arm:sum(rows[i]["brier"][arm] for i in LATE_RETURN)/len(LATE_RETURN)
        for arm in ARMS
    }
    benchmark=("beta_full","beta_window24","beta_discount95",
               "full_rule","recent24_rule","archive","latest")
    best_return=min(late_return[x] for x in benchmark)
    best_b=min(late_b[x] for x in benchmark if x!="archive")
    conditions={
        "return_beats_best_controls":late_return["evidence"]<=
                                     best_return-.010,
        "return_beats_action_mask":late_return["evidence"]<=
                                    late_return["action_masked"]-.010,
        "late_B_safe":late_b["evidence"]<=best_b+.005,
        "old_weights_immutable":True,
        "native_historic_read_exact":hist_after==historic_before,
        "source_and_six_heads_continued":True,
        "capacity_beyond_original_limit":model.total_count>1024,
    }
    source_cpu=time.process_time()-cpu
    require(source_cpu<CPU_LIMIT,"SOURCE_CPU_BUDGET")
    report={
        "old_seed":old_seed,"new_seed":seed,"platform":platform(),
        "old_training_checkpoint_sha256":digest(old_raw),
        "original_native_archive_sha256":original_native_archive_sha,
        "original_source_history_sha256":digest(canonical(history_prefix)),
        "original_bank_source_sha256":original_bank_sha,
        "new_interventions":48,
        "old_plus_parent_total":pin["full_count"],
        "continued_total":model.total_count,
        "cap01_new_prefix":len(old_prefix),
        "cap02_new_evidence":memory.new_count,
        "native_shard_sizes":[len(s._ledger) for s in model._segments],
        "causal_bank_sizes":list(memory.bank_sizes),
        "native_continued_sha256":digest(model_raw),
        "causal_memory_sha256":digest(memory_raw),
        "native_checkpoint_bytes":len(model_raw),
        "memory_checkpoint_bytes":len(memory_raw),
        "previous_old_native_brier":historic_before,
        "after_old_native_brier":hist_after,
        "six_heads_new_one_step_updates":[144]*4,
        "six_heads_new_multistep_updates":[48]*2,
        "late_B_brier":late_b,"late_return_brier":late_return,
        "best_return_matched_control":best_return,
        "best_late_B_control":best_b,
        "frozen_conditions":conditions,
        "development_go":all(conditions.values()),
        "scientific_pass":False,
        "automatic_deployment":False,
    }
    artifacts={
        "old_seed":old_seed,"seed":seed,
        "original_sha256":digest(old_raw),
        "continued_native_sha256":digest(model_raw),
        "continued_native_ascii":model_raw.decode("ascii"),
        "causal_memory_sha256":digest(memory_raw),
        "causal_memory_ascii":memory_raw.decode("ascii"),
    }
    timing={"seed":seed,"cpu_seconds":source_cpu,
            "wall_seconds":time.perf_counter()-clock}
    return report,artifacts,rows,timing

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    require(blob(HERE/"source.py")==SOURCE_BLOB,"FROZEN_SOURCE_BLOB")
    protocol=subprocess.check_output([
        "git","rev-parse",PREREG_SHA+
        ":research/contrib/chatgpt/YGG-CAP02/prereg.json"],
        cwd=ROOT,text=True,timeout=30).strip()
    require(blob(HERE/"prereg.json")==protocol,
            "FROZEN_PREREG_BEFORE_SCORED_TRAINING")
    parent_result=HERE.parent/"YGG-CAP01"/"result.json"
    require(blob(parent_result)==PARENT_RESULT_BLOB,
            "ORIGINAL_CAP01_QUALIFIED_RESULT")
    src=load(HERE/"source.py","cap02_source_first_use")
    cap01=load(HERE.parent/"YGG-CAP01"/"campaign.py","cap02_prior_beta")
    args.output.mkdir(parents=True,exist_ok=True)
    results,times=[],[]
    for seed in sorted(OLD):
        report,state,trace,timing=run_seed(seed,src,cap01)
        results.append(report)
        times.append(timing)
        for name,value in (
            (f"seed-{seed}-state.json",state),
            (f"seed-{seed}-trace.json",trace)):
            (args.output/name).write_bytes(canonical(value))
        print("YGG_CAP02_REAL_CONTINUED_NATIVE_AND_CAUSAL_RULE_MEMORY",
              report["old_plus_parent_total"],"to",report["continued_total"],
              "bank_sizes",report["causal_bank_sizes"],
              "development_go",report["development_go"],flush=True)
    result={
        "schema":"yggdrasil.cap02.actual-native-and-causal-memory-development.v1",
        "source_blob":SOURCE_BLOB,
        "prereg_first_sha":PREREG_SHA,
        "parent_exact_sha":PARENT_SHA,
        "replicas":results,
        "development_go":all(v["development_go"] for v in results),
        "scientific_pass":False,
        "original_first_use":False,
        "accepted_native":False,
        "deployment":"NONE",
    }
    (args.output/"result.json").write_bytes(canonical(result))
    (args.output/"timings.json").write_bytes(canonical(times))
    print("YGG_CAP02_"+("DEVELOPMENT_GO" if result["development_go"]
                           else "DEVELOPMENT_NO_GO")+
          " SCIENTIFIC_NOT_PASS",flush=True)

if __name__=="__main__":
    main()
