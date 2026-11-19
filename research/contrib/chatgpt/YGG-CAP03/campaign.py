"""CAP03: train cumulative Yggdrasil and native paired causal contrasts once.

Prequential forecasts on four reset-interventions from the same synthetic
state are scored BEFORE any of the four consequences updates the trained
contrast or fully fitted conventional controls. Only ONE precommitted primary
branch advances the sequential 7-component Yggdrasil native ledger. All
old trained native and six JEPA weights are continued, never restarted.
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
from yggdrasil.native_evidence_recall import restore_original_sealed_native
from yggdrasil.native_paired_causal_contrast import (
    ARMS,PairedCausalContrast,state as public_state,
)

HERE=Path(__file__).resolve().parent
PLATFORM="windows" if sys.platform=="win32" else "linux"
PRIOR=HERE.parent/"YGG-CAP02"/"original"/PLATFORM
PREREG="f9c5e6d69827e76df27239c421aed01d4229d51b"
SOURCE_BLOB="d5a3fc30846ebbb97eeb8817fc72d9cd5be8c181"
PARENT="23429ef8145e88ce3005d5c5df6e87443a3c7dec"
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
}[PLATFORM]
ARMS_OF_COMPARISON=("contrast","sham","beta_exact","beta_pooled",
                    "ridge","native_archive","native_active")
MATCHED=("sham","beta_exact","beta_pooled","ridge")
FEATURES=16

def require(ok,tag):
    if not ok:
        raise ValueError("CAP03_CAMPAIGN_"+tag)

def git_blob(path):
    return subprocess.check_output([
        "git","rev-parse","HEAD:"+path.relative_to(ROOT).as_posix()],
        cwd=ROOT,text=True,timeout=20).strip()

def fresh_source():
    path=HERE/"source.py"
    require(git_blob(path)==SOURCE_BLOB,"NEW_SOURCE_FROZEN_BLOB")
    spec=importlib.util.spec_from_file_location("cap03_new_development",path)
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def features(st,action):
    u,v,w=st
    a,b=action
    return np.asarray((1.,u,v,w,a,b,u*a,v*a,w*a,
                       u*b,v*b,w*b,a*b,u*v,u*w,v*w),dtype=np.float64)

class FittedRidge:
    """Fully refit L2 linear 16-feature control, matched on every fork label."""
    def __init__(self,prior_ledger):
        self.gram=4.*np.eye(FEATURES,dtype=np.float64)
        self.rhs=np.zeros((FEATURES,2),dtype=np.float64)
        self.examples=0
        for _,views,a,s,b,y in prior_ledger:
            self.learn(public_state(views),(a,b),s,y)
    def learn(self,st,action,s2,y):
        x=features(st,action)
        self.gram+=np.outer(x,x)
        self.rhs+=np.outer(x,(float(s2),float(y^s2)))
        self.examples+=1
    def forecast(self,st,action,stage,s2=None):
        weights=np.linalg.solve(self.gram,self.rhs)
        j=0 if stage=="transition" else 1
        p=float(np.clip(features(st,action)@weights[:,j],.02,.98))
        return p if stage=="transition" or s2==0 else 1.-p

class FullBeta:
    """Fully fitted exact-state/action and action-pooled matched-information arms."""
    def __init__(self,prior):
        self.rows=[]
        for _,views,a,s,b,y in prior:
            self.learn(public_state(views),(a,b),s,y)
    def learn(self,st,action,s2,y):
        self.rows.append((st,action,s2,y))
    def forecast(self,st,action,stage,s2=None,pooled=False):
        j=2 if stage=="transition" else 3
        selected=[row[j] if j==2 else row[3]^row[2]
                  for row in self.rows
                  if row[1]==action and (pooled or row[0]==st)]
        p=(sum(selected)+1.)/(len(selected)+2.)
        return float(p if stage=="transition" or s2==0 else 1.-p)

def error(v,truth):
    return ((v[0]-truth[0])**2+(v[1]-truth[1])**2)/2

def one_seed(oldseed,source):
    start_wall=time.perf_counter();start_cpu=time.process_time()
    newseed,old_count,pinblob,pinsha=PINS[oldseed]
    path=PRIOR/f"seed-{oldseed}-state.json"
    require(git_blob(path)==pinblob,"REAL_ORIGINAL_TRAINED_SOURCE")
    data=json.loads(path.read_bytes())
    raw=data["model_ascii"].encode("ascii")
    require(digest(raw)==pinsha==data["model_sha256"],"ORIGINAL_TRAINED_SHA")
    model=restore_original_sealed_native(raw,pinsha)
    require(model.total_count==old_count and
            model.new_count==64,"REAL_NATIVE_CONTINUATION_COUNT")
    archive=bytes(model._archive_raw)
    prior_ledger=model._history()
    prefix=tuple(model._events)
    prior_old=model._source.original.base.native._ledger[-32:]
    preserved=tuple((
        model.archived_forecast(v[0],a),
        model.archived_forecast(v[0],a,s,b),
    ) for _,v,a,s,b,y in prior_old)
    initial_six=digest(canonical({
        "one":[h.as_data() for h in model._one],
        "temporal":[h.data() for h in model._temporal],
        "future":[h.checkpoint() for h in model._future],
    }))
    prior_post=model._events[-1][6]
    events=source.generate(newseed,prior_post)
    require(len(events)==32 and len({e["id"] for e in events})==32,
            "DISJOINT_NEW_SYNTHETIC_SOURCE")
    contrast=PairedCausalContrast()
    sham=PairedCausalContrast(mispair=True)
    beta=FullBeta(prior_ledger)
    ridge=FittedRidge(prior_ledger)
    seen={row[0] for row in prior_ledger}
    trace=[]
    for t,event in enumerate(events):
        views=event["views"];st=public_state(views)
        require(event["id"] not in seen and
                event["chosen"]==source.chosen(newseed,t) and
                event["forks"][source.ARMS.index(event["chosen"])]["post"]==
                  event["post"],"PUBLIC_PLAN_AND_FORK")
        seen.add(event["id"])
        forecasts={name:[] for name in ARMS_OF_COMPARISON}
        for fork in event["forks"]:
            action=fork["action"]
            s2=fork["s2"]
            # stage 1 forecast does not receive s2; stage 2 does, but
            # NEVER receives unobserved reward y.
            for name in ARMS_OF_COMPARISON:
                if name=="contrast":
                    p=contrast.forecast(views,action,"transition")
                    q=contrast.forecast(views,action,"terminal",s2)
                elif name=="sham":
                    p=sham.forecast(views,action,"transition")
                    q=sham.forecast(views,action,"terminal",s2)
                elif name=="beta_exact":
                    p=beta.forecast(st,action,"transition")
                    q=beta.forecast(st,action,"terminal",s2)
                elif name=="beta_pooled":
                    p=beta.forecast(st,action,"transition",pooled=True)
                    q=beta.forecast(st,action,"terminal",s2,pooled=True)
                elif name=="ridge":
                    p=ridge.forecast(st,action,"transition")
                    q=ridge.forecast(st,action,"terminal",s2)
                elif name=="native_archive":
                    p=model.archived_forecast(views[0],action[0])
                    q=model.archived_forecast(
                        views[0],action[0],s2,action[1])
                elif name=="native_active":
                    p=model.active_forecast(views[0],action[0])
                    q=model.active_forecast(
                        views[0],action[0],s2,action[1])
                require(0<=p<=1 and 0<=q<=1,"COLD_PREQUENTIAL_PROB")
                forecasts[name].append([float(p),float(q)])
        true=[(f["s2"],f["y"]) for f in event["forks"]]
        scores={name:float(np.mean([
            error(pred,label) for pred,label in zip(forecasts[name],true)
        ])) for name in ARMS_OF_COMPARISON}
        trace.append({
            "index":t,"source_id":event["id"],"views":views,
            "chosen":event["chosen"],"phase":event["phase"],
            "witnessed_forks":event["forks"],
            "forecasts":forecasts,"scores":scores,
        })
        # All 4 fork consequences are NOW revealed, after all forecasts.
        contrast.observe(event["id"],views,event["forks"])
        sham.observe(event["id"],views,event["forks"])
        for fork in event["forks"]:
            beta.learn(st,fork["action"],fork["s2"],fork["y"])
            ridge.learn(st,fork["action"],fork["s2"],fork["y"])
        # Only the ONE preannounced branch advances the original native
        # chronology; reset forks must not masquerade as sequential events.
        before=model.total_count
        model=model.observe(event["id"],views,event["selected"],event["post"])
        require(model.total_count==before+1,"ONE_ACTUAL_PRIMARY_EPISODE")
    require(model.total_count==old_count+32 and model.new_count==96 and
            model._events[:64]==prefix and model._archive_raw==archive and
            model._source.checkpoint()==archive and
            [h.steps for h in (*model._one,*model._temporal)]==[288]*4 and
            model.future_windows==94,"CUMULATIVE_SEVEN_COMPONENT_TRAINING")
    check_old=tuple((
        model.archived_forecast(v[0],a),
        model.archived_forecast(v[0],a,s,b),
    ) for _,v,a,s,b,y in prior_old)
    require(check_old==preserved,"PREVIOUSLY_LEARNED_NATIVE_READOUT")
    final_six=digest(canonical({
        "one":[h.as_data() for h in model._one],
        "temporal":[h.data() for h in model._temporal],
        "future":[h.checkpoint() for h in model._future],
    }))
    require(final_six!=initial_six,"REAL_SIX_HEAD_UPDATE")
    checkpoint=model.checkpoint()
    require(restore_original_sealed_native(checkpoint,digest(checkpoint))
            .checkpoint()==checkpoint,"EXACT_NEW_NATIVE_COLD_SOURCE")
    cont_raw=contrast.checkpoint()
    sham_raw=sham.checkpoint()
    require(PairedCausalContrast.restore(cont_raw,digest(cont_raw))
             .checkpoint()==cont_raw and
            PairedCausalContrast.restore(sham_raw,digest(sham_raw))
             .checkpoint()==sham_raw,"CAUSAL_REPRESENTATION_COLD")
    late=trace[22:]
    scores={name:sum(r["scores"][name] for r in late)/len(late)
            for name in ARMS_OF_COMPARISON}
    qualifiers={
        name:scores["contrast"]<=scores[name]-.005
        for name in MATCHED
    }
    outcome=all(qualifiers.values())
    cpu=time.process_time()-start_cpu
    require(cpu<=180.,"EXPERIMENT_CPU_BUDGET")
    return ({
        "old_seed":oldseed,"seed":newseed,"old_total":old_count,
        "new_primary_episodes":32,"new_matched_fork_outcomes":128,
        "total":model.total_count,"new_native_count":model.new_count,
        "final_future_windows":model.future_windows,
        "four_head_epoch_steps":[h.steps for h in
                                 (*model._one,*model._temporal)],
        "original_checkpoint_sha256":pinsha,
        "original_six_head_sha256":initial_six,
        "continued_six_head_sha256":final_six,
        "continued_native_sha256":digest(checkpoint),
        "contrast_sha256":digest(cont_raw),
        "sham_sha256":digest(sham_raw),
        "old_archive_byte_exact":True,
        "old_readouts_equal":True,
        "late_brier":scores,
        "control_qualifiers":qualifiers,
        "development_go":outcome,"science_pass":False,
    },{
        "seed":newseed,"old_seed":oldseed,"original_sha256":pinsha,
        "model_sha256":digest(checkpoint),
        "model_ascii":checkpoint.decode("ascii"),
        "contrast_sha256":digest(cont_raw),
        "contrast_ascii":cont_raw.decode("ascii"),
        "sham_sha256":digest(sham_raw),
        "sham_ascii":sham_raw.decode("ascii"),
    },trace,{
        "seed":newseed,"cpu_seconds":cpu,
        "wall_seconds":time.perf_counter()-start_wall,
        "prior_fitted_conventional_examples":len(prior_ledger),
        "new_paired_fork_witnesses":128,
    })

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True,type=Path)
    args=p.parse_args()
    frozen=subprocess.check_output([
        "git","rev-parse",
        PREREG+":research/contrib/chatgpt/YGG-CAP03/prereg.json"],
        cwd=ROOT,text=True).strip()
    require(git_blob(HERE/"prereg.json")==frozen,
            "ORIGINAL_PREREG_FROZEN")
    source=fresh_source()
    args.output.mkdir(parents=True,exist_ok=True)
    reports=[];times=[]
    for oldseed in sorted(PINS):
        rep,weights,trace,t=one_seed(oldseed,source)
        reports.append(rep);times.append(t)
        for name,body in (
            (f"seed-{oldseed}-state.json",weights),
            (f"seed-{oldseed}-trace.json",trace),
        ):
            (args.output/name).write_bytes(canonical(body))
        print("CAP03_REAL_NATIVE_CONTINUES",oldseed,rep["old_total"],
              rep["total"],"paired",rep["new_matched_fork_outcomes"],
              "development_go",rep["development_go"],flush=True)
    outcome=all(rep["development_go"] for rep in reports)
    result={
        "schema":"yggdrasil.cap03.paired-native-causal-contrast.v1",
        "parent_sha":PARENT,
        "prereg_commit":PREREG,
        "source_git_blob":SOURCE_BLOB,
        "replicas":reports,
        "development_go":outcome,"scientific_pass":False,
        "original_first_use":False,"deployment":"NONE",
    }
    (args.output/"result.json").write_bytes(canonical(result))
    (args.output/"timings.json").write_bytes(canonical(times))
    print("CAP03_FROZEN_DEVELOPMENT_"+("GO" if outcome else "NO_GO"),
          "SCIENTIFIC_PASS_FALSE",flush=True)

if __name__=="__main__":
    main()
