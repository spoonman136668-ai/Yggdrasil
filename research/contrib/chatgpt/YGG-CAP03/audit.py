"""Independent CAP03 evidence auditor: public interventional clock and controls.

Never imports campaign.py. Recovers exact frozen prior trained native and
six JEPA weights, reconstructs the original matched four-fork source,
refits independent conventional controls on ALL previously witnessed public
events, audits every stored prequential prediction and primary-branch native
continuation, and confirms cold source/contrast receipts.
"""
from __future__ import annotations
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
from yggdrasil.native_evidence_recall import restore_original_sealed_native
from yggdrasil.native_paired_causal_contrast import (
    PairedCausalContrast,ARMS,state as state_of,
)

HERE=Path(__file__).resolve().parent
OS="windows" if sys.platform=="win32" else "linux"
PRIOR=HERE.parent/"YGG-CAP02"/"original"/OS
SOURCE_SHA="d5a3fc30846ebbb97eeb8817fc72d9cd5be8c181"
PINS={
 "linux":{
  14071:(99811,1086,"2a4113370100093437dba4dc56094e737ab9d9b1",
   "94ba6cd5a7771cb15f69920ac8ee03a1277bd41b9b2ab5dc98fda514f7292481"),
  14072:(99829,1061,"db526dd0bbec3f6afe179d4d7e8812c55ce92075",
   "e1469b3477b69560ecac2c1b41a26e12055d11e2a1203b112fde1f6910e19cbd"),
 },
 "windows":{
  14071:(99811,1086,"89b5c2857c6c393a09fc8b373a13e39f3e0f7816",
   "abc78822a3fc8c30297738338a48199b31addcc1590f71850c9c529bb8b62bd0"),
  14072:(99829,1061,"579649a025bbd5c49562001d5c73fe6e0deb788d",
   "3fc0c2ab1bdcc798d4d10fb02225d6394331bacd434906a881a9596d5f629dac"),
 }
}[OS]
MODEL_NAMES=("contrast","sham","beta_exact","beta_pooled","ridge",
             "native_archive","native_active")
MATCHED=("sham","beta_exact","beta_pooled","ridge")

def check(value,label):
    if not value:
        raise ValueError("CAP03_INDEPENDENT_AUDIT_"+label)

def eq(a,b):
    return abs(float(a)-float(b))<=1e-9

def git_blob(path):
    return subprocess.check_output([
        "git","rev-parse","HEAD:"+path.relative_to(ROOT).as_posix()],
        cwd=ROOT,text=True,timeout=20).strip()

def source():
    p=HERE/"source.py"
    check(git_blob(p)==SOURCE_SHA,"SOURCE_BLOB")
    s=importlib.util.spec_from_file_location("cap03_independent_source",p)
    mod=importlib.util.module_from_spec(s)
    s.loader.exec_module(mod)
    return mod

def xvector(state,arm):
    u,v,w=state
    a,b=arm
    return np.array([1.,u,v,w,a,b,u*a,v*a,w*a,
                     u*b,v*b,w*b,a*b,u*v,u*w,v*w],dtype=float)

class IndependentLinear:
    def __init__(self,history):
        self.G=np.eye(16,dtype=float)*4.
        self.H=np.zeros((16,2),dtype=float)
        for _,views,a,s,b,y in history:
            self.observe((views[0][0],views[0][1],views[1][1]),(a,b),s,y)
    def observe(self,st,arm,s,y):
        z=xvector(st,arm)
        self.G=self.G+np.outer(z,z)
        self.H=self.H+np.outer(z,[s,y^s])
    def forecast(self,st,arm,stage,s2=None):
        coeff=np.linalg.solve(self.G,self.H)
        idx=0 if stage=="transition" else 1
        pred=float(np.clip(np.dot(xvector(st,arm),coeff[:,idx]),.02,.98))
        return pred if stage=="transition" or s2==0 else 1.-pred

class IndependentExactCounts:
    def __init__(self,history):
        self.rows=[]
        for _,views,a,s,b,y in history:
            self.observe((views[0][0],views[0][1],views[1][1]),(a,b),s,y)
    def observe(self,st,arm,s,y):
        self.rows.append((st,arm,s,y))
    def forecast(self,st,arm,stage,s2=None,pooled=False):
        values=[]
        for prev,old_arm,ns,reward in self.rows:
            if old_arm==arm and (pooled or prev==st):
                values.append(ns if stage=="transition" else reward^ns)
        p=(sum(values)+1.)/(len(values)+2.)
        return p if stage=="transition" or s2==0 else 1.-p

def audit(path):
    source_module=source()
    result=json.loads((path/"result.json").read_bytes())
    check(result["schema"]=="yggdrasil.cap03.paired-native-causal-contrast.v1"
          and result["source_git_blob"]==SOURCE_SHA and
          result["prereg_commit"]==
              "f9c5e6d69827e76df27239c421aed01d4229d51b" and
          result["scientific_pass"] is False and
          result["deployment"]=="NONE" and
          len(result["replicas"])==2,"FROZEN_RESULT")
    receipts=[]
    for position,oldseed in enumerate(sorted(PINS)):
        seed,n,git_sha,parentsha=PINS[oldseed]
        previous=PRIOR/f"seed-{oldseed}-state.json"
        check(git_blob(previous)==git_sha,"PINNED_ORIGINAL_MODEL_BLOB")
        init=json.loads(previous.read_bytes())
        original=init["model_ascii"].encode("ascii")
        check(digest(original)==init["model_sha256"]==parentsha,
              "REAL_PARENT_LEARNED_WEIGHTS")
        native=restore_original_sealed_native(original,parentsha)
        check(native.total_count==n and native.new_count==64,
              "PREVIOUS_SEVEN_COMPONENT_CAPACITY")
        intact=tuple(native._events)
        archive=bytes(native._archive_raw)
        observations=source_module.generate(seed,intact[-1][6])
        by_model=PairedCausalContrast()
        wrong=PairedCausalContrast(mispair=True)
        base=IndependentExactCounts(native._history())
        linear=IndependentLinear(native._history())
        states=json.loads((path/f"seed-{oldseed}-state.json").read_bytes())
        trace=json.loads((path/f"seed-{oldseed}-trace.json").read_bytes())
        check(len(trace)==32 and len(observations)==32,
              "ORIGINAL_WITNESS_COUNT")
        metrics={name:[] for name in MODEL_NAMES}
        for i,(rec,evt) in enumerate(zip(trace,observations)):
            check(rec["index"]==i and rec["source_id"]==evt["id"]
                  and rec["phase"]==evt["phase"]
                  and rec["views"]==[list(v) for v in evt["views"]]
                  and rec["chosen"]==list(evt["chosen"])
                  and rec["witnessed_forks"]==[
                      {"action":list(f["action"]),"s2":f["s2"],
                       "y":f["y"],"post":list(f["post"])}
                      for f in evt["forks"]]
                  and set(rec["forecasts"])==set(MODEL_NAMES)
                  and set(rec["scores"])==set(MODEL_NAMES),
                  "PUBLIC_FORK_SOURCE_TIMELINE")
            st=state_of(evt["views"])
            true=[(fork["s2"],fork["y"]) for fork in evt["forks"]]
            for name in MODEL_NAMES:
                predictions=rec["forecasts"][name]
                check(len(predictions)==4,"FOUR_PREQUENTIAL_ARMS")
                total=0.
                for pair,(fork,pair_pred) in enumerate(zip(evt["forks"],predictions)):
                    arm=fork["action"];s2=fork["s2"]
                    if name=="contrast":
                        p=by_model.forecast(evt["views"],arm,"transition")
                        q=by_model.forecast(evt["views"],arm,"terminal",s2)
                    elif name=="sham":
                        p=wrong.forecast(evt["views"],arm,"transition")
                        q=wrong.forecast(evt["views"],arm,"terminal",s2)
                    elif name=="beta_exact":
                        p=base.forecast(st,arm,"transition")
                        q=base.forecast(st,arm,"terminal",s2)
                    elif name=="beta_pooled":
                        p=base.forecast(st,arm,"transition",pooled=True)
                        q=base.forecast(st,arm,"terminal",s2,pooled=True)
                    elif name=="ridge":
                        p=linear.forecast(st,arm,"transition")
                        q=linear.forecast(st,arm,"terminal",s2)
                    elif name=="native_archive":
                        p=native.archived_forecast(evt["views"][0],arm[0])
                        q=native.archived_forecast(
                            evt["views"][0],arm[0],s2,arm[1])
                    else:
                        p=native.active_forecast(evt["views"][0],arm[0])
                        q=native.active_forecast(
                            evt["views"][0],arm[0],s2,arm[1])
                    check(eq(p,pair_pred[0]) and eq(q,pair_pred[1]),
                          "INDEPENDENT_PREQUENTIAL_"+name)
                    total+=((pair_pred[0]-s2)**2+
                            (pair_pred[1]-fork["y"])**2)/8.
                check(eq(total,rec["scores"][name]),
                      "INDEPENDENT_BRIER_"+name)
                if i>=22:
                    metrics[name].append(total)
            # All fork labels enter learners only AFTER scoring all 4 arms.
            by_model.observe(evt["id"],evt["views"],evt["forks"])
            wrong.observe(evt["id"],evt["views"],evt["forks"])
            for fork in evt["forks"]:
                base.observe(st,fork["action"],fork["s2"],fork["y"])
                linear.observe(st,fork["action"],fork["s2"],fork["y"])
            oldcount=native.total_count
            native=native.observe(evt["id"],evt["views"],
                                  evt["selected"],evt["post"])
            check(native.total_count==oldcount+1,
                  "FORKS_NOT_FAKE_SEQUENTIAL_EPISODES")
        rep=result["replicas"][position]
        check((rep["seed"],rep["old_seed"],rep["old_total"],
               rep["new_primary_episodes"],rep["new_matched_fork_outcomes"],
               rep["total"],rep["new_native_count"],
               rep["final_future_windows"])==
              (seed,oldseed,n,32,128,n+32,96,94),
              "CUMULATIVE_SIX_HEADS_AND_FORK_COUNTS")
        check(native._events[:64]==intact and
              native._archive_raw==archive and
              native._source.checkpoint()==archive and
              rep["old_archive_byte_exact"] is True and
              rep["old_readouts_equal"] is True,
              "ALL_OLD_NATIVE_WITNESSES_PRESERVED")
        raw=states["model_ascii"].encode("ascii")
        check(digest(raw)==states["model_sha256"]==
              rep["continued_native_sha256"] and
              native.checkpoint()==raw,
              "ORIGINAL_TRAINED_FINAL_COLD_REPLAY")
        contrasts={
            "contrast":by_model.checkpoint(),
            "sham":wrong.checkpoint(),
        }
        for name,content in contrasts.items():
            check(content==states[name+"_ascii"].encode("ascii")
                  and digest(content)==states[name+"_sha256"]==
                  rep[name+"_sha256"] and
                  PairedCausalContrast.restore(
                      content,digest(content)).checkpoint()==content,
                  "REAL_WITNESSED_EFFECT_COLD_"+name)
        measured={name:sum(v)/len(v) for name,v in metrics.items()}
        check(all(eq(measured[name],rep["late_brier"][name])
                  for name in MODEL_NAMES),"ORIGINAL_BRIER_RECEIPTS")
        checks={n:measured["contrast"]<=measured[n]-.005 for n in MATCHED}
        check(checks==rep["control_qualifiers"] and
              rep["development_go"]==all(checks.values())
              and rep["science_pass"] is False,
              "FROZEN_DEVELOPMENT_VERDICT")
        receipts.append({
            "seed":seed,"old_count":n,"new_count":n+32,
            "original_sha256":parentsha,
            "new_sha256":digest(raw),
            "matched_fork_training":128,
            "late_brier":measured,
            "development_go":rep["development_go"],
            "audit_pass":True,
        })
    check(result["development_go"]==
          all(x["development_go"] for x in receipts),
          "OVERALL_FROZEN_DECISION")
    return {
        "schema":"yggdrasil.cap03.independent-native-causal-clock.v1",
        "source_blob":SOURCE_SHA,
        "replicas":receipts,
        "audit_pass":True,
        "development_go":result["development_go"],
        "scientific_pass":False,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("directory",type=Path)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    output=audit(a.directory)
    if a.output:
        a.output.write_bytes(canonical(output))
    print("CAP03_INDEPENDENT_PAIRED_CAUSAL_CLOCK_PASS",
          "DEVELOPMENT_"+("GO" if output["development_go"] else "NO_GO"),
          "SCIENTIFIC_PASS_FALSE",flush=True)

if __name__=="__main__":
    main()
