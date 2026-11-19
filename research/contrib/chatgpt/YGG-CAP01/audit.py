"""Independent source-tape, causal-clock, controls, metrics and custody auditor.

Uses the sealed original trained native states and fresh source, but does not
import/re-execute the campaign scoring module or issue new interventions.
Restored learned checkpoints independently replay each witnessed event to
reject forged/rehashed internal weights.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from yggdrasil.native_context_basis import canonical,digest
from yggdrasil.native_segmented_continuation import SegmentedNativeJEPA
from yggdrasil.native_episode_experience import MAX_EPISODES

HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/"YGG-JEPA2-05"/"original"/"linux"
PINS={
 14071:(99601,1022,"33b648ef36e381a2eb753094f930a4722570b448",
        "646058e49adf75d2cf74b16b901e801b24ea38f017a717d68fe65a93ab4cad9e"),
 14072:(99603,997,"5b9df452e45a1ebc3faadb265ceeffbc580ed7bf",
        "ef8e1b6daa9b0349d675aee6c30a79d759d6e21c460b5fc900461417c1970609"),
}
SOURCE_BLOB="9e34144de876778d8931b7dacce9b990bb36716a"
ARMS=("archive","active","one_jepa","temporal_jepa","beta_full","beta_window32")

def require(ok,tag):
    if not ok:
        raise ValueError("CAP01_INDEPENDENT_AUDIT_"+tag)

def blob(path):
    return subprocess.check_output(
        ["git","rev-parse","HEAD:"+path.relative_to(ROOT).as_posix()],
        cwd=ROOT,text=True,timeout=30).strip()

def fresh():
    path=HERE/"source.py"
    require(blob(path)==SOURCE_BLOB,"SOURCE_PIN")
    spec=importlib.util.spec_from_file_location("cap01_auditor_source",path)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def score(pred,truth):
    require(type(pred) is list and len(pred)==len(truth) and
            all(type(x) in (int,float) and 0<=x<=1 for x in pred),
            "STAGE_FORECAST_BOUND")
    return sum((p-y)**2 for p,y in zip(pred,truth))/len(truth)

def close(a,b,tolerance=1e-9):
    return abs(a-b)<=tolerance

def beta(rows,view,a,state=None,second=None,window=None):
    prior=rows if window is None else rows[-window:]
    if state is None:
        bits=[s for v,x,s,b,y in prior if v==tuple(view) and x==a]
    else:
        bits=[y for v,x,s,b,y in prior if
              v==tuple(view) and x==a and s==state and b==second]
    return (sum(bits)+1)/(len(bits)+2)

def audit(input_dir):
    source=fresh()
    report=json.loads((input_dir/"result.json").read_bytes())
    require(report["schema"]==
            "yggdrasil.cap01.original-native-capacity-development.v1"
            and report["new_source_blob"]==SOURCE_BLOB and
            report["scientific_pass"] is False and
            report["proven_native_causal_gain"] is False and
            report["deployment"]=="NONE" and len(report["replicas"])==2,
            "REPORT_DISPOSITION")
    evidence=[]
    for j,old_seed in enumerate(sorted(PINS)):
        seed,n,source_blob,source_sha=PINS[old_seed]
        r=report["replicas"][j]
        require((r["old_seed"],r["seed"],r["original_count"],
                 r["new_count"],r["total_count"],r["future_new_windows"])==
                (old_seed,seed,n,32,n+32,30) and n+32>1024 and
                MAX_EPISODES==1024 and
                r["old_source_sha256"]==source_sha,
                "PRECOMMITTED_CAPACITY_BOUNDARY")
        original_path=PARENT/f"seed-{old_seed}-state.json"
        require(blob(original_path)==source_blob,
                "OLD_SOURCE_GIT_BLOB")
        olddoc=json.loads(original_path.read_bytes())
        original_raw=olddoc["model_ascii"].encode("ascii")
        require(digest(original_raw)==olddoc["model_sha256"]==source_sha,
                "OLD_MODEL_STABLE")
        archived=SegmentedNativeJEPA.from_archive(original_raw,source_sha)
        old=archived._source.original.base.native._ledger
        before=sum(
            score([archived.archived_forecast(v[0],a),
                   archived.archived_forecast(v[0],a,s,b)],[s,y])
            for _,v,a,s,b,y in old[-32:])/32
        require(close(before,r["old_native_historical_brier_before"],1e-12),
                "ORIGINAL_NATIVE_HISTORIC_READOUT")
        state=json.loads((input_dir/f"seed-{old_seed}-state.json").read_bytes())
        raw=state["continued_ascii"].encode("ascii")
        require(digest(raw)==state["continued_sha256"]==
                r["final_segmented_sha256"] and
                state["old_model_sha256"]==source_sha and
                state["old_seed"]==old_seed and state["seed"]==seed,
                "CONTINUED_SIX_HEAD_SOURCE_PIN")
        model=SegmentedNativeJEPA.restore(raw,digest(raw))
        require(model.checkpoint()==raw and
                model._source.checkpoint()==original_raw and
                model.archive_sha256==source_sha and
                model.original_count==n and model.new_count==32,
                "INDEPENDENT_7_COMPONENT_COLD_REPLAY")
        actual=source.generate(seed)
        require(len(actual)==32 and len(model._events)==32,
                "FRESH_WITNESS_COUNT")
        for event,expected in zip(model._events,actual):
            require(event[0]==expected["identifier"] and
                    event[1]==expected["views"] and
                    event[2:6]==(
                        expected["row"]["x1"],expected["row"]["s2"],
                        expected["row"]["x2"],expected["row"]["y"]) and
                    event[6]==expected["post"],
                    "PUBLIC_ACTION_CONSEQUENCE_PROVENANCE")
        require(r["shard_counts"]==[len(shard._ledger)
                 for shard in model._segments] and
                r["four_prior_head_epoch_updates"]==[96]*4 and
                [h.steps for h in
                 (*model._one,*model._temporal)]==[96]*4 and
                model.future_windows==30 and
                all(head.windows==oldhead.windows+30 for
                    head,oldhead in zip(model._future,
                        (model._source.sensory,model._source.reward))),
                "NATIVE_AND_SIX_LEARNER_TRAINING_PROVENANCE")
        after=sum(
            score([model.archived_forecast(v[0],a),
                   model.archived_forecast(v[0],a,s,b)],[s,y])
            for _,v,a,s,b,y in old[-32:])/32
        require(before==after==
                r["old_native_historical_brier_after"]==
                r["old_native_historical_brier_before"],
                "OLD_READOUT_EXACT_RETENTION")
        tr=json.loads((input_dir/f"seed-{old_seed}-trace.json").read_bytes())
        ft=json.loads((input_dir/f"seed-{old_seed}-future.json").read_bytes())
        require(len(tr)==32 and len(ft)==30,"COMPLETE_NEW_PREQUENTIAL_TAPE")
        # Independent conventional refit on EXACT same old and new
        # interventions, score BEFORE current evidence is appended.
        beta_rows=[(tuple(v[0]),a,s,b,y) for _,v,a,s,b,y in old]
        scores={arm:[] for arm in ARMS}
        for i,(record,e) in enumerate(zip(tr,actual)):
            truth=[e["row"]["s2"],e["row"]["y"]]
            require(record["index"]==i and
                    record["source_id"]==e["identifier"] and
                    record["phase"]==e["phase"] and
                    record["views"]==[list(q) for q in e["views"]] and
                    record["actions"]==list(e["actions"]) and
                    record["truth"]==truth and
                    set(record["forecasts"])==set(ARMS) and
                    set(record["brier"])==set(ARMS),
                    "PREQUENTIAL_PUBLIC_RECORD")
            view=e["views"][0]
            a,b=e["actions"]
            s=truth[0]
            for arm,window in (("beta_full",None),("beta_window32",32)):
                p=beta(beta_rows,view,a,window=window)
                q=beta(beta_rows,view,a,s,b,window=window)
                require(close(record["forecasts"][arm][0],p) and
                        close(record["forecasts"][arm][1],q),
                        "INDEPENDENT_BETA_EXPOSURE")
            archive=[archived.archived_forecast(view,a),
                     archived.archived_forecast(view,a,s,b)]
            require(all(close(p,q,1e-12)
                        for p,q in zip(record["forecasts"]["archive"],archive)),
                    "EXACT_ARCHIVE_PREQUENTIAL_READ")
            for arm in ARMS:
                require(close(score(record["forecasts"][arm],truth),
                              record["brier"][arm],1e-12),
                        "INDEPENDENT_BRIER_CALC")
                if i>=22:
                    scores[arm].append(record["brier"][arm])
            beta_rows.append((tuple(view),a,s,b,truth[1]))
        future_scores={"continued_future":[],"frozen_future":[]}
        for i,record in enumerate(ft):
            windows=actual[i:i+3]
            required_truth=[]
            for event in windows:
                required_truth.extend((event["post"][1],event["row"]["y"]))
            require(record["start"]==i and
                    record["source_id"]==windows[0]["identifier"] and
                    record["phase"]==windows[0]["phase"] and
                    record["plans"]==[list(source.announced_plan(seed,k))
                                     for k in range(i,i+3)] and
                    record["truth"]==required_truth and
                    set(record["forecasts"])==set(future_scores) and
                    set(record["brier"])==set(future_scores),
                    "THREE_STEP_CAUSAL_CLOCK")
            for arm in future_scores:
                require(close(score(record["forecasts"][arm],
                                    required_truth),record["brier"][arm],1e-12),
                        "FUTURE_PREQUENTIAL_SCORE")
                if i>=22:
                    future_scores[arm].append(record["brier"][arm])
        means={arm:sum(x)/len(x) for arm,x in scores.items()}
        late_future={arm:sum(x)/len(x) for arm,x in future_scores.items()}
        require(all(close(means[arm],r["late_step_brier"][arm]) for arm
                    in ARMS) and
                all(close(late_future[arm],r["late_future_brier"][arm])
                    for arm in future_scores),
                "SOURCE_BASED_METRIC_RECOMPUTATION")
        trained=r["trained_six_head_sha256"]
        require(type(trained) is str and len(trained)==64 and
                trained !=r["original_six_head_sha256"] and
                r["final_checkpoint_bytes"]==len(raw) and
                r["archived_original_model_byte_exact"] is True and
                r["science_pass"] is False,"HEAD_CONTINUATION_RECEIPTS")
        evidence.append({
            "seed":seed,"original":n,"total":n+32,
            "legacy_before":before,"legacy_after":after,
            "late_brier":means,"late_future":late_future,
            "cold_replay":True,
            "old_7_component_sha256":source_sha,
            "continued_sha256":digest(raw),
        })
    require(report["engineering_development_go"] is True and
            report["scientific_pass"] is False,
            "FROZEN_ENGINEERING_GO_SCIENCE_HOLD")
    return {
        "schema":"yggdrasil.cap01.independent-native-capacity-audit.v1",
        "source_git_blob":SOURCE_BLOB,
        "replicas":evidence,
        "engineering_audit_pass":True,
        "scientific_pass":False,
        "original_first_use":False,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("directory",type=Path)
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    report=audit(args.directory)
    if args.output:
        args.output.write_bytes(canonical(report))
    print("YGG_CAP01_INDEPENDENT_CAUSAL_CLOCK_AND_COLD_REPLAY_PASS",
          "two_genuine_models",len(report["replicas"]),
          "scientific_pass",False,flush=True)

if __name__=="__main__":
    main()
