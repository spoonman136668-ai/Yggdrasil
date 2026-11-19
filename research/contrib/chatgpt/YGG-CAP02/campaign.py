"""Prospective native evidence-recall development on ACTUAL cumulative CAP01 models.

Restores the 1054/1029 episode learned native Yggdrasil models and six learned
heads. Continues with new source-bound interventions, scores before observing
outcomes, fits independent conventional controls, and preserves original-model
immutable cold readout and evidence-only selection checkpoint.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time
import numpy as np

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from yggdrasil.native_context_basis import canonical,digest
from yggdrasil.native_segmented_continuation import SegmentedNativeJEPA
from yggdrasil.native_evidence_recall import EvidenceRecall,restore_original_sealed_native
HERE=Path(__file__).resolve().parent
PLATFORM="windows" if sys.platform=="win32" else "linux"
PRIOR=HERE.parent/"YGG-CAP01"/"original"/PLATFORM
PREREG="99ec70e48d09df724a32fa0384c3aa5ef18c0b2e"
SOURCE_BLOB="881df9ae85f3737a3ce2c8a83cd934ec0bde5cde"
PARENT_SHA="3770e660bc8b908218e6fe82e176bd4bf91158d9"
PINS={
 "linux":{
  14071:(99721,1054,"f4568f284605556f970d7f2cc4733577f09de244",
         "6babc23f4baf30afde14db5f2ca8eb3e55e321169aa245482478ff9855b68f14"),
  14072:(99739,1029,"371afb1e830d6790b948ceda06f8260e7070260b",
         "c503ccf979f90d6d4954f0e8d42133fc177017d4b47de80ee64c9524b870d827"),
 },
 "windows":{
  14071:(99721,1054,"db50019c5ae9d8e8e16a24792f01fc50a0414b29",
         "2d08c7e2d6d4d80acfc53727cdd0880d3f632c0f44bdb405b78feffba405938e"),
  14072:(99739,1029,"9e233e46a4fbc683c8a1388441791cad16b42f2a",
         "e09b0cbbe47b95686f3ed3732baf080fe6b47301f0128c360437bf29bf9dfbfb"),
 }
}[PLATFORM]
ARMS=("gate","archive","active","mix50","beta_full","beta_recent32",
      "sham_wrong_context")
CPU_LIMIT=220.
def check(x,s):
    if not x:
        raise ValueError("CAP02_CAMPAIGN_"+s)

def git_blob(path):
    return subprocess.check_output(
        ["git","rev-parse","HEAD:"+path.relative_to(ROOT).as_posix()],
        cwd=ROOT,text=True,timeout=20).strip()

def load_source():
    p=HERE/"source.py"
    check(git_blob(p)==SOURCE_BLOB,"SOURCE_GIT_BLOB")
    spec=importlib.util.spec_from_file_location("cap02_fresh_source",p)
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

class Beta:
    def __init__(self,history):
        self.rows=[(tuple(views[0]),a,s,b,y)
                   for _,views,a,s,b,y in history]
    def probability(self,stage,view,a,s=None,b=None,last=None):
        rows=self.rows if last is None else self.rows[-last:]
        if stage=="transition":
            ys=[z for v,x,z,_,_ in rows if v==tuple(view) and x==a]
        else:
            ys=[y for v,x,z,c,y in rows if v==tuple(view) and
                x==a and z==s and c==b]
        return (sum(ys)+1)/(len(ys)+2)
    def observe(self,views,a,s,b,y):
        self.rows.append((tuple(views[0]),a,s,b,y))

def brier(values):
    return float(np.mean(values))

def run_seed(old_seed,source):
    t0=time.perf_counter()
    cpu0=time.process_time()
    seed,n,blob,sha=PINS[old_seed]
    p=PRIOR/f"seed-{old_seed}-state.json"
    check(git_blob(p)==blob,"TRAINED_SOURCE_BLOB")
    d=json.loads(p.read_bytes())
    root=d["continued_ascii"].encode("ascii")
    check(digest(root)==sha==d["continued_sha256"],"TRAINED_CAP01_PIN")
    model=restore_original_sealed_native(root,sha)
    check(model.total_count==n and model._source.checkpoint()==
          model._archive_raw,"ORIGINAL_CUMULATIVE_MODEL")
    parent_ledger=model._history()
    parent_prefix=tuple(model._events)
    initial_archive=bytes(model._archive_raw)
    frozen_native=tuple(model._source.original.base.native._ledger[-32:])
    base_readouts=[
        (model.archived_forecast(v[0],a),
         model.archived_forecast(v[0],a,s,b))
        for _,v,a,s,b,y in frozen_native
    ]
    first_state=model._events[-1][6]
    events=source.generate(seed,first_state)
    check(len(events)==32 and events[0]["views"]==
          ((first_state[0],first_state[1]),(first_state[1],first_state[2])),
          "GENUINE_PUBLIC_CONTINUITY")
    beta=Beta(parent_ledger)
    gate=EvidenceRecall()
    sham=EvidenceRecall()
    trace=[]
    seen={row[0] for row in parent_ledger}
    for i,evt in enumerate(events):
        id=evt["id"]
        views=evt["views"]
        view=views[0]
        row=evt["row"]
        a,s,b,y=row["x1"],row["s2"],row["x2"],row["y"]
        check(id not in seen and (a,b)==source.announced(seed,i),
              "NEW_PUBLIC_ACTION_ID")
        seen.add(id)
        forecasts={}
        stage_receipts=[]
        for stage in ("transition","terminal"):
            state,second=(None,None) if stage=="transition" else (s,b)
            # Reward y is hidden until ALL conditional predictions have
            # been recorded, even though the test source tape is complete.
            pa=model.archived_forecast(view,a,state,second)
            pn=model.active_forecast(view,a,state,second)
            lookup=gate.predict(stage,view,a,pa,pn,state,second)
            # Negative: evidence is stored on a deliberately WRONG public
            # context using the complement of the first public view bit.
            wrong_view=(1-view[0],view[1])
            wrong=sham.predict(stage,view,a,pa,pn,state,second)
            pb=beta.probability(stage,view,a,state,second)
            pr=beta.probability(stage,view,a,state,second,32)
            values={"gate":lookup["prob"],"archive":pa,
                    "active":pn,"mix50":.5*(pa+pn),
                    "beta_full":pb,"beta_recent32":pr,
                    "sham_wrong_context":wrong["prob"]}
            check(set(values)==set(ARMS) and
                  all(0<=p<=1 for p in values.values()),"PROB_RANGE")
            forecasts[stage]=values
            stage_receipts.append({
                "stage":stage,"context":list(lookup["public_key"]),
                "support_before":lookup["support"],
                "archive_weight_before":lookup["archive_weight"],
                "sham_support_before":wrong["support"],
            })
        truth={"transition":s,"terminal":y}
        scores={arm:sum((forecasts[stage][arm]-truth[stage])**2
                        for stage in ("transition","terminal"))/2
                for arm in ARMS}
        trace.append({
            "index":i,"id":id,"phase":evt["phase"],
            "views":[list(x) for x in views],
            "actions":[a,b],"truth":[s,y],
            "forecasts":forecasts,"brier":scores,
            "stage_receipts":stage_receipts
        })
        # Scoring is finished; update posterior only now, using witnessed
        # public s2 and y, and then update the cumulative native model once.
        for stage,label in (("transition",s),("terminal",y)):
            gate.witness(id,stage,view,a,label,
                         forecasts[stage]["archive"],
                         forecasts[stage]["active"],
                         None if stage=="transition" else s,
                         None if stage=="transition" else b)
            wrong_view=(1-view[0],view[1])
            sham.witness(id,stage,wrong_view,a,label,
                         forecasts[stage]["archive"],
                         forecasts[stage]["active"],
                         None if stage=="transition" else s,
                         None if stage=="transition" else b)
        beta.observe(views,a,s,b,y)
        prev=model.total_count
        model=model.observe(id,views,row,evt["post"])
        check(model.total_count==prev+1,"CUMULATIVE_NATIVE_LEARNING")
    check(model.total_count==n+32 and model.new_count==64 and
          model._events[:len(parent_prefix)]==parent_prefix and
          model._archive_raw==initial_archive and
          model._source.checkpoint()==initial_archive,
          "IMMUTABLE_OLD_NATIVE_AND_NEW_CAPACITY")
    check([x.steps for x in (*model._one,*model._temporal)]==[192]*4 and
          model.future_windows==62,"ALL_SIX_CONTINUED_TRAINING")
    for (a,b),(_,views,first,state,second,reward) in zip(base_readouts,frozen_native):
        check((a,b)==(model.archived_forecast(views[0],first),
                      model.archived_forecast(views[0],first,state,second)),
              "OLD_READOUT_EXACT")
    gate_raw=gate.checkpoint()
    sham_raw=sham.checkpoint()
    check(EvidenceRecall.restore(gate_raw,digest(gate_raw)).checkpoint()==
          gate_raw and
          EvidenceRecall.restore(sham_raw,digest(sham_raw)).checkpoint()==
          sham_raw,"GATE_COLD_EVIDENCE_PROVENANCE")
    model_raw=model.checkpoint()
    check(restore_original_sealed_native(model_raw,digest(model_raw)).checkpoint()
          ==model_raw,"MODEL_COLD_SOURCE_PROVENANCE")
    late=trace[22:]
    means={arm:brier([r["brier"][arm] for r in late])
           for arm in ARMS}
    gate_late=means["gate"]
    late_checks={k:gate_late<=means[k]-.005 for k in ARMS
                 if k!="gate"}
    success=all(late_checks.values())
    cpu=time.process_time()-cpu0
    check(cpu<=CPU_LIMIT,"CPU_LIMIT")
    return ({
        "old_seed":old_seed,"seed":seed,
        "original_total":n,"new_witnesses":32,"total":model.total_count,
        "new_shard_witnesses":model.new_count,
        "future_windows":model.future_windows,
        "four_head_epoch_steps":[x.steps for x in
                                 (*model._one,*model._temporal)],
        "original_checkpoint_sha256":sha,
        "continued_checkpoint_sha256":digest(model_raw),
        "gate_sha256":digest(gate_raw),"sham_sha256":digest(sham_raw),
        "archive_unchanged":True,
        "old_readout_unchanged":True,
        "late_brier":means,
        "late_checks":late_checks,
        "development_go":success,
        "scientific_pass":False,
    },{
        "old_seed":old_seed,"seed":seed,"old_sha256":sha,
        "model_ascii":model_raw.decode("ascii"),
        "model_sha256":digest(model_raw),
        "gate_ascii":gate_raw.decode("ascii"),"gate_sha256":digest(gate_raw),
        "sham_ascii":sham_raw.decode("ascii"),"sham_sha256":digest(sham_raw),
    },trace,{"seed":seed,"wall_seconds":time.perf_counter()-t0,
             "cpu_seconds":cpu})

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True,type=Path)
    a=p.parse_args()
    frozen=subprocess.check_output([
        "git","rev-parse",PREREG+
        ":research/contrib/chatgpt/YGG-CAP02/prereg.json"],
        cwd=ROOT,text=True).strip()
    check(git_blob(HERE/"prereg.json")==frozen,"PREREG_FROZEN")
    src=load_source()
    a.output.mkdir(parents=True,exist_ok=True)
    reports,timing=[],[]
    for old_seed in sorted(PINS):
        report,state,trace,t=run_seed(old_seed,src)
        reports.append(report);timing.append(t)
        for fname,obj in ((f"seed-{old_seed}-state.json",state),
                          (f"seed-{old_seed}-trace.json",trace)):
            (a.output/fname).write_bytes(canonical(obj))
        print("CAP02_SOURCE_BOUND_NATIVE_CONTINUATION",old_seed,
              report["original_total"],report["total"],"development_go",
              report["development_go"],flush=True)
    result={"schema":"yggdrasil.cap02.native-evidence-recall-development.v1",
            "parent_sha":PARENT_SHA,
            "prereg_commit":PREREG,
            "source_blob":SOURCE_BLOB,
            "replicas":reports,
            "development_go":all(r["development_go"] for r in reports),
            "scientific_pass":False,"deployment":"NONE"}
    (a.output/"result.json").write_bytes(canonical(result))
    (a.output/"timings.json").write_bytes(canonical(timing))
    print("CAP02_DEVELOPMENT_"+("GO" if result["development_go"] else "NO_GO"),
          "SCIENCE_NOT_QUALIFIED",flush=True)
if __name__=="__main__":
    main()
