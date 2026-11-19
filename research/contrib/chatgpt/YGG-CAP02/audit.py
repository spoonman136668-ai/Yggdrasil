"""Independent CAP02 authentic source, readout and prequential score auditor.

Does NOT import campaign.py, issue new interventions, infer oracle regimes, or
re-score an untouched protected future cohort. Checks exact original source
bytes, all new public witnesses, both trained native/causal cold checkpoints,
frozen prereg verdict, and conventional counter fits on the same source.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT),str(HERE)]
from yggdrasil.native_context_basis import canonical,digest
from yggdrasil.native_causal_rule_memory import CausalMemory
from pinned_restore import load_pinned_cap01,restore_continued_from_pinned_parent

SOURCE_BLOB="bcae839c6f43ecf14fc1a1a2f3ce7ac813f501bf"
PINS={
 14071:{"seed":99811,"linux":("f4568f284605556f970d7f2cc4733577f09de244","6babc23f4baf30afde14db5f2ca8eb3e55e321169aa245482478ff9855b68f14"),
        "windows":("db50019c5ae9d8e8e16a24792f01fc50a0414b29","2d08c7e2d6d4d80acfc53727cdd0880d3f632c0f44bdb405b78feffba405938e")},
 14072:{"seed":99829,"linux":("371afb1e830d6790b948ceda06f8260e7070260b","c503ccf979f90d6d4954f0e8d42133fc177017d4b47de80ee64c9524b870d827"),
        "windows":("9e233e46a4fbc683c8a1388441791cad16b42f2a","e09b0cbbe47b95686f3ed3732baf080fe6b47301f0128c360437bf29bf9dfbfb")}
}
ARMS=("evidence","uniform","latest","action_masked",
      "full_rule","recent24_rule","beta_full","beta_window24",
      "beta_discount95","archive","active","one_jepa","temporal_jepa")
BENCH=("beta_full","beta_window24","beta_discount95",
       "full_rule","recent24_rule","archive","latest")

def require(ok,name):
    if not ok:
        raise ValueError("CAP02_INDEPENDENT_SOURCE_AUDIT_"+name)

def blob(path):
    return subprocess.check_output([
        "git","rev-parse","HEAD:"+path.relative_to(ROOT).as_posix()
    ],cwd=ROOT,text=True,timeout=25).strip()

def source():
    path=HERE/"source.py"
    require(blob(path)==SOURCE_BLOB,"FROZEN_PUBLIC_SOURCE_BLOB")
    spec=importlib.util.spec_from_file_location("cap02_source_audit",path)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def brier(forecasts,truth):
    require(type(forecasts) is list and len(forecasts)==2 and
            all(type(v) in (float,int) and math.isfinite(v)
                and 0<=v<=1 for v in forecasts),
            "PROBABILITY_RANGE")
    return sum((a-b)**2 for a,b in zip(forecasts,truth))/2

def match(a,b,tol=1e-9):
    return (type(a) in (int,float) and type(b) in (int,float) and
        math.isfinite(a) and math.isfinite(b) and abs(a-b)<=tol)

def conventional(rows,view,a,state=None,second=None,window=None,discount=None):
    if window is not None:
        rows=rows[-window:]
    total=0.
    success=0.
    for age,(v,first,s,b,y) in enumerate(reversed(rows)):
        found=(v==tuple(view) and first==a)
        if state is not None:
            found=found and s==state and b==second
        if found:
            weight=1. if discount is None else discount**age
            total+=weight
            success+=weight*(s if state is None else y)
    return (success+1)/(total+2)

def prior(oldseed,osname):
    prior_sha,expected=PINS[oldseed][osname]
    path=HERE.parent/"YGG-CAP01"/"original"/osname/f"seed-{oldseed}-state.json"
    require(blob(path)==prior_sha,"ORIGINAL_SEALED_ARTIFACT_GIT_BLOB")
    record=json.loads(path.read_bytes())
    raw=record["continued_ascii"].encode("ascii")
    require(digest(raw)==expected==record["continued_sha256"],
            "PLATFORM_ORIGINAL_COMPLETE_SHA")
    model,drift=load_pinned_cap01(raw,expected)
    require(drift["maximum_float_difference"]<=1e-12,
            "SOURCE_REPLAY_NUMERICAL_CUSTODY")
    return model,raw

def old_native_mean(model):
    return sum(brier([
        model.archived_forecast(views[0],a),
        model.archived_forecast(views[0],a,s2,b)
    ],[s2,y]) for _,views,a,s2,b,y in
        model._source.original.base.native._ledger[-32:])/32

def audit(directory):
    src=source()
    result=json.loads((directory/"result.json").read_bytes())
    require(result["schema"]==
            "yggdrasil.cap02.actual-native-and-causal-memory-development.v1"
            and result["source_blob"]==SOURCE_BLOB and
            result["prereg_first_sha"]==
            "d07b9ac4448b4c23288f4f9a76aec7f2c69faa55"
            and result["scientific_pass"] is False and
            result["accepted_native"] is False and
            result["deployment"]=="NONE" and len(result["replicas"])==2,
            "SEALED_SCIENTIFIC_BOUNDARY")
    examined=[]
    flags=[]
    for index,oldseed in enumerate(sorted(PINS)):
        r=result["replicas"][index]
        seed=PINS[oldseed]["seed"]
        osname=r["platform"]
        require(osname in ("linux","windows") and
                r["old_seed"]==oldseed and r["new_seed"]==seed,
                "CORRECT_SOURCE_AND_OS")
        original,old_raw=prior(oldseed,osname)
        original_future=original._events
        original_model_archive=original._source.checkpoint()
        state=json.loads((directory/f"seed-{oldseed}-state.json").read_bytes())
        native_raw=state["continued_native_ascii"].encode("ascii")
        memory_raw=state["causal_memory_ascii"].encode("ascii")
        require(state["old_seed"]==oldseed and state["seed"]==seed and
                state["original_sha256"]==r["old_training_checkpoint_sha256"]==
                    digest(old_raw) and
                state["continued_native_sha256"]==r["native_continued_sha256"]==
                    digest(native_raw) and
                state["causal_memory_sha256"]==r["causal_memory_sha256"]==
                    digest(memory_raw),
                "EVIDENCE_ACTUAL_COLD_SHA")
        model,drift=restore_continued_from_pinned_parent(
            native_raw,digest(native_raw),original)
        memory=CausalMemory.restore(memory_raw,digest(memory_raw),
                                     original_future)
        require(model.checkpoint()==native_raw and
                memory.checkpoint()==memory_raw and
                model._source.checkpoint()==original_model_archive and
                model._events[:32]==original_future and
                memory._prior==original_future and
                memory._events==model._events[32:] and
                model.archive_sha256==original.archive_sha256,
                "EXACT_OLDER_NATIVE_AND_NEW_CAUSAL_SOURCE")
        new=src.generate(seed)
        require(len(new)==48 and model.new_count==80 and
                memory.new_count==48 and memory.total==80 and
                model.total_count==original.total_count+48 and
                model.total_count==r["continued_total"] and
                [len(x._ledger) for x in model._segments]==[64,16] and
                list(memory.bank_sizes)==[16,16,16,16,16],
                "FULL_NATIVE_CONTINUATION_AND_BANK_ROLLOVER")
        for fresh,actual in zip(new,model._events[32:]):
            require(actual[0]==fresh["identifier"] and
                    actual[1]==fresh["views"] and
                    actual[2:6]==(fresh["row"]["x1"],
                        fresh["row"]["s2"],fresh["row"]["x2"],
                        fresh["row"]["y"]) and
                    actual[6]==fresh["post"],
                    "ALL_NEW_PUBLIC_ACTION_CONSEQUENCE_RECEIPTS")
        old_before=old_native_mean(original)
        old_after=old_native_mean(model)
        require(old_after==old_before==
                r["previous_old_native_brier"]==
                r["after_old_native_brier"],
                "OLD_CAUSAL_READER_PRESERVED_EXACT")
        require([v.steps for v in (*model._one,*model._temporal)]==
                [v.steps+144 for v in
                 (*original._one,*original._temporal)] and
                [v.windows for v in model._future]==[
                  v.windows+48 for v in original._future],
                "SIX_FITTED_NATIVE_SPECIALISTS_ACTUALLY_CONTINUED")
        trace=json.loads((directory/f"seed-{oldseed}-trace.json").read_bytes())
        require(len(trace)==48,"EXACT_FRESH_TAPE_LENGTH")
        beta_rows=[(tuple(e[1][0]),e[2],e[3],e[4],e[5])
                   for e in original._history()]
        summary={arm:[] for arm in ARMS}
        return_losses={arm:[] for arm in ARMS}
        for t,(record,event) in enumerate(zip(trace,new)):
            require(record["index"]==t and
                    record["source_id"]==event["identifier"] and
                    record["seed"]==seed and
                    record["phase"]==event["phase"] and
                    record["public_views"]==
                      [list(q) for q in event["views"]] and
                    record["announced_actions"]==list(event["actions"]) and
                    record["public_truth"]==
                      [event["row"]["s2"],event["row"]["y"]] and
                    set(record["prequential"])==set(ARMS) and
                    set(record["brier"])==set(ARMS),
                    "FIRST_USE_PUBLIC_EVENT_IDENTITY")
            expected_banks=[16]*(2+t//16)+(
                [t%16] if t%16 else [])
            require(record["bank_sizes_before"]==expected_banks,
                    "BANK_WITNESS_CHRONOLOGY")
            posterior=record["posterior_weights_before"]
            require(type(posterior) is list and
                    len(posterior)==len(expected_banks)+(
                        1 if t%16==0 else 0) and
                    all(math.isfinite(p) and 0<=p<=1
                        for p in posterior) and
                    abs(sum(posterior)-1)<=1e-9,
                    "PREQUENTIAL_EVIDENCE_WEIGHTS")
            views=event["views"]
            a,b=event["actions"]
            s2,y=record["public_truth"]
            for control,window,discount in (
                ("beta_full",None,None),
                ("beta_window24",24,None),
                ("beta_discount95",None,.95)):
                p=conventional(beta_rows,views[0],a,
                               window=window,discount=discount)
                q=conventional(beta_rows,views[0],a,s2,b,
                               window=window,discount=discount)
                require(match(p,record["prequential"][control][0]) and
                        match(q,record["prequential"][control][1]),
                        "INDEPENDENT_STRONG_BETA_CONTROL_FIT")
            archive=[original.archived_forecast(views[0],a),
                     original.archived_forecast(views[0],a,s2,b)]
            require(all(match(a,b,1e-12) for a,b in zip(
                archive,record["prequential"]["archive"])),
                "SOURCE_FROZEN_ARCHIVE_PREQUENTIAL")
            for arm in ARMS:
                score=brier(record["prequential"][arm],[s2,y])
                require(match(score,record["brier"][arm],1e-12),
                        "INDEPENDENT_PREQUENTIAL_BRIER")
                if t in range(24,32):
                    summary[arm].append(score)
                if t in range(40,48):
                    return_losses[arm].append(score)
            beta_rows.append((tuple(views[0]),a,s2,b,y))
        late_b={arm:sum(xs)/8 for arm,xs in summary.items()}
        late_return={arm:sum(xs)/8 for arm,xs in return_losses.items()}
        require(all(match(late_b[arm],r["late_B_brier"][arm])
                    for arm in ARMS) and
                all(match(late_return[arm],r["late_return_brier"][arm])
                    for arm in ARMS),
                "FINAL_SCORES_RECOMPUTED")
        best_return=min(late_return[x] for x in BENCH)
        best_b=min(late_b[x] for x in BENCH if x!="archive")
        require(match(best_return,r["best_return_matched_control"])
                and match(best_b,r["best_late_B_control"]),
                "FITTED_BENCHMARK_BEST")
        conditions={
            "return_beats_best_controls":
              late_return["evidence"]<=best_return-.010,
            "return_beats_action_mask":
              late_return["evidence"]<=late_return["action_masked"]-.010,
            "late_B_safe":late_b["evidence"]<=best_b+.005,
            "old_weights_immutable":True,
            "native_historic_read_exact":old_before==old_after,
            "source_and_six_heads_continued":True,
            "capacity_beyond_original_limit":model.total_count>1024,
        }
        require(conditions==r["frozen_conditions"] and
                all(conditions.values())==r["development_go"] and
                r["scientific_pass"] is False,
                "UNALTERED_FROZEN_DECISION")
        flags.append(all(conditions.values()))
        examined.append({
            "new_seed":seed,"os":osname,
            "original_checkpoint_sha256":digest(old_raw),
            "new_continued_sha256":digest(native_raw),
            "causal_memory_sha256":digest(memory_raw),
            "total_native_episodes":model.total_count,
            "late_B":late_b,"late_return":late_return,
            "conditions":conditions,
            "old_readout_brier":old_before,
            "model_source_replay_max_numeric_drift":
                drift["maximum_float_difference"],
            "development_go":all(conditions.values()),
        })
    require(result["development_go"]==all(flags) and
            result["scientific_pass"] is False and
            result["original_first_use"] is False,
            "COMPLETE_REPLICA_AND_SCIENCE_FENCE")
    return {
        "schema":"yggdrasil.cap02.independent-original-public-audit.v1",
        "source_blob":SOURCE_BLOB,
        "replicas":examined,
        "engineering_audit":True,
        "development_go":all(flags),
        "scientific_pass":False,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("data",type=Path)
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    result=audit(args.data)
    if args.output:
        args.output.write_bytes(canonical(result))
    print("YGG_CAP02_INDEPENDENT_CAUSAL_SOURCE_AUDIT_PASS",
          "DEV_"+("GO" if result["development_go"] else "NO_GO"),
          "SCIENTIFIC_NOT_PASS",flush=True)

if __name__=="__main__":
    main()
