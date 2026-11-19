"""Independent audit of fresh two-stage CAP02 cumulative native evidence.

No campaign import, no new training first-use. Independently recomputes score,
same-information conventional controls, source chronology, original model
provenance, continuation checkpoint cold replay and evidence-gate forecasts.
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
from yggdrasil.native_evidence_recall import EvidenceRecall

HERE=Path(__file__).resolve().parent
PRIOR=HERE.parent/"YGG-CAP01"/"original"/"linux"
SOURCE_BLOB="881df9ae85f3737a3ce2c8a83cd934ec0bde5cde"
PINS={
 14071:(99721,1054,"f4568f284605556f970d7f2cc4733577f09de244",
        "6babc23f4baf30afde14db5f2ca8eb3e55e321169aa245482478ff9855b68f14"),
 14072:(99739,1029,"371afb1e830d6790b948ceda06f8260e7070260b",
        "c503ccf979f90d6d4954f0e8d42133fc177017d4b47de80ee64c9524b870d827"),
}
ARMS=("gate","archive","active","mix50","beta_full","beta_recent32","sham_wrong_context")

def check(v,tag):
    if not v:
        raise ValueError("CAP02_INDEPENDENT_AUDIT_"+tag)

def close(a,b,tol=1e-9):
    return abs(a-b)<=tol

def blob(path):
    return subprocess.check_output([
        "git","rev-parse","HEAD:"+path.relative_to(ROOT).as_posix()],
        cwd=ROOT,text=True,timeout=20).strip()

def fresh():
    p=HERE/"source.py"
    check(blob(p)==SOURCE_BLOB,"SOURCE_BLOB")
    s=importlib.util.spec_from_file_location("cap02_audited_fresh",p)
    m=importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m

def beta(rows,stage,view,a,s=None,b=None,last=None):
    tape=rows if last is None else rows[-last:]
    if stage=="transition":
        val=[z for v,x,z,c,y in tape if v==tuple(view) and x==a]
    else:
        val=[y for v,x,z,c,y in tape if v==tuple(view)
             and x==a and z==s and c==b]
    return (sum(val)+1)/(len(val)+2)

def score(probs,truth):
    check(len(probs)==2 and all(type(x) in (float,int) and 0<=x<=1
                               for x in probs),"PROB_SHAPE")
    return sum((x-y)**2 for x,y in zip(probs,truth))/2

def audit(root):
    result=json.loads((root/"result.json").read_bytes())
    check(result["schema"]==
          "yggdrasil.cap02.native-evidence-recall-development.v1"
          and result["source_blob"]==SOURCE_BLOB and
          result["prereg_commit"]==
            "99ec70e48d09df724a32fa0384c3aa5ef18c0b2e" and
          result["scientific_pass"] is False and
          result["deployment"]=="NONE" and len(result["replicas"])==2,
          "SOURCE_AND_SCIENCE_DISPOSITION")
    source=fresh()
    receipts=[]
    for j,oldseed in enumerate(sorted(PINS)):
        seed,n,parent_blob,parent_sha=PINS[oldseed]
        prior_path=PRIOR/f"seed-{oldseed}-state.json"
        check(blob(prior_path)==parent_blob,"PRIOR_SOURCE_GIT")
        d=json.loads(prior_path.read_bytes())
        raw=d["continued_ascii"].encode("ascii")
        check(digest(raw)==parent_sha,"PRIOR_PARENT_SHA")
        prior=SegmentedNativeJEPA.restore(raw,parent_sha)
        check(prior.total_count==n,"TRAINED_PARENT_COUNT")
        r=result["replicas"][j]
        check((r["seed"],r["old_seed"],r["original_total"],
               r["new_witnesses"],r["total"],r["new_shard_witnesses"],
               r["future_windows"])==
              (seed,oldseed,n,32,n+32,64,62),
              "CUMULATIVE_CAPACITY_PROVENANCE")
        state=json.loads((root/f"seed-{oldseed}-state.json").read_bytes())
        learned=state["model_ascii"].encode("ascii")
        check(digest(learned)==state["model_sha256"]==
              r["continued_checkpoint_sha256"] and
              state["old_sha256"]==parent_sha,
              "TRAINED_MODEL_SHA")
        model=SegmentedNativeJEPA.restore(learned,digest(learned))
        check(model._events[:32]==prior._events and
              model._source.checkpoint()==prior._source.checkpoint() and
              model.total_count==n+32,"NO_PARENT_EVIDENCE_DELETION")
        gate_raw=state["gate_ascii"].encode("ascii")
        sham_raw=state["sham_ascii"].encode("ascii")
        gate=EvidenceRecall.restore(gate_raw,digest(gate_raw))
        sham=EvidenceRecall.restore(sham_raw,digest(sham_raw))
        check(digest(gate_raw)==r["gate_sha256"]==
              state["gate_sha256"] and
              digest(sham_raw)==r["sham_sha256"]==
              state["sham_sha256"] and
              len(gate._events)==len(sham._events)==64,
              "SOURCE_LOCKED_64_WITNESSES")
        original_tail=prior._events[-1][6]
        fresh_events=source.generate(seed,original_tail)
        for original,observed in zip(model._events[32:],fresh_events):
            check(original[0]==observed["id"] and
                  original[1]==observed["views"] and
                  original[2:6]==(
                    observed["row"]["x1"],observed["row"]["s2"],
                    observed["row"]["x2"],observed["row"]["y"]) and
                  original[6]==observed["post"],
                  "ACTUAL_NEW_PUBLIC_WITNESS")
        prior_history=prior._history()
        rows=[(tuple(v[0]),a,s,b,y)
              for _,v,a,s,b,y in prior_history]
        evidence=EvidenceRecall()
        negative=EvidenceRecall()
        trace=json.loads((root/f"seed-{oldseed}-trace.json").read_bytes())
        check(len(trace)==32,"ALL_PROSPECTIVE_EVENTS")
        late={name:[] for name in ARMS}
        for i,(rec,ev) in enumerate(zip(trace,fresh_events)):
            view=ev["views"][0]
            a,s,b,y=ev["row"]["x1"],ev["row"]["s2"],ev["row"]["x2"],ev["row"]["y"]
            check(rec["index"]==i and rec["id"]==ev["id"] and
                  rec["phase"]==ev["phase"] and
                  rec["views"]==[list(v) for v in ev["views"]] and
                  rec["actions"]==[a,b] and
                  rec["truth"]==[s,y] and
                  set(rec["forecasts"])=={"transition","terminal"} and
                  set(rec["brier"])==set(ARMS),
                  "INDEPENDENT_SOURCE_AND_CLOCK")
            for stage in ("transition","terminal"):
                t,c=(None,None) if stage=="transition" else (s,b)
                p=rec["forecasts"][stage]
                check(set(p)==set(ARMS),"MATCHED_FORECAST_ARMS")
                old=prior.archived_forecast(view,a,t,c)
                check(close(p["archive"],old,1e-12),
                      "READONLY_SOURCE_NATIVE_FORECAST")
                beta_full=beta(rows,stage,view,a,t,c)
                beta_recent=beta(rows,stage,view,a,t,c,32)
                check(close(p["beta_full"],beta_full,1e-12) and
                      close(p["beta_recent32"],beta_recent,1e-12),
                      "INDEPENDENT_FULLY_FITTED_BETA")
                check(close(p["mix50"],.5*(p["archive"]+p["active"])),
                      "UNGATED_SOURCE_CONTROL")
                expected=evidence.predict(stage,view,a,p["archive"],
                                         p["active"],t,c)
                wrong=negative.predict(stage,view,a,p["archive"],
                                       p["active"],t,c)
                check(close(p["gate"],expected["prob"],1e-12) and
                      close(p["sham_wrong_context"],wrong["prob"],1e-12),
                      "STRICT_PREQUENTIAL_RETRIEVAL")
            truth=(s,y)
            for arm in ARMS:
                measured=score([
                    rec["forecasts"]["transition"][arm],
                    rec["forecasts"]["terminal"][arm]],truth)
                check(close(measured,rec["brier"][arm],1e-12),
                      "INDEPENDENT_LOSS_CALC")
                if i>=22:
                    late[arm].append(measured)
            # Witness evidence ONLY AFTER both prequential predictions.
            for stage,label in (("transition",s),("terminal",y)):
                p=rec["forecasts"][stage]
                t,c=(None,None) if stage=="transition" else (s,b)
                evidence.witness(ev["id"],stage,view,a,label,
                                 p["archive"],p["active"],t,c)
                wrong_view=(1-view[0],view[1])
                negative.witness(ev["id"],stage,wrong_view,a,label,
                                 p["archive"],p["active"],t,c)
            rows.append((tuple(view),a,s,b,y))
        check(evidence.checkpoint()==gate_raw and
              negative.checkpoint()==sham_raw,
              "ALL_STORED_PUBLIC_EVIDENCE_RECONSTRUCTED")
        means={arm:sum(v)/len(v) for arm,v in late.items()}
        check(all(close(means[arm],r["late_brier"][arm]) for arm in ARMS),
              "FROZEN_LATE_METRICS_RECOMPUTED")
        conditions={arm:means["gate"]<=means[arm]-.005
                    for arm in ARMS if arm!="gate"}
        check(conditions==r["late_checks"] and
              all(conditions.values())==r["development_go"] and
              r["archive_unchanged"] is True and
              r["old_readout_unchanged"] is True,
              "FROZEN_DEVELOPMENT_VERDICT")
        receipts.append({
            "seed":seed,"prior_total":n,"new_total":model.total_count,
            "old_archive_sha256":digest(prior._archive_raw),
            "source_checkpoint_sha256":digest(learned),
            "original_source_unchanged":True,
            "public_witnesses":32,"matched_controls":True,
            "late_brier":means,"development_go":all(conditions.values()),
        })
    check(result["development_go"]==all(
        r["development_go"] for r in receipts),"OVERALL_QUALIFIER")
    return {
        "schema":"yggdrasil.cap02.independent-public-clock-audit.v1",
        "source_blob":SOURCE_BLOB,
        "replicas":receipts,
        "engineering_audit_pass":True,
        "development_go":result["development_go"],
        "scientific_pass":False,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("directory",type=Path)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    receipt=audit(a.directory)
    if a.output:
        a.output.write_bytes(canonical(receipt))
    print("CAP02_INDEPENDENT_NATIVE_RECALL_AUDIT_PASS",
          "DEVELOPMENT_"+("GO" if receipt["development_go"] else "NO_GO"),
          "SCIENCE_NOT_QUALIFIED",flush=True)

if __name__=="__main__":
    main()
