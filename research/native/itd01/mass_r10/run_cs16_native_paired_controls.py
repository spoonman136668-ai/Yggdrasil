#!/usr/bin/env python3
"""CS16: exact original R7 native retention vs equal-FIT conventional memory.

Prospective source-free PUBLIC development only. Frozen historical R7 remains
FAIL and blocks protected promotion. No external original-source claims.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import time
try:
    import resource
except ImportError:
    resource=None

HERE=Path(__file__).resolve().parent
NATIVE=HERE.parent/"r7"
sys.path.insert(0,str(NATIVE))
from native_cells import Colony,PublicDevGenerator,_examples,study,gates

FIRST="a3ab35bd541ed587059ddaf513350c9b5902325c"
NATIVE_SHA="4c492a494ac5b25d5e9c49b98185be6a2c966b2f"
TEST_SHA="5565929be0e91c679bfd3c6741d171b69d9a013f"
SEEDS=(131,157,181,197,223,251)
OLD=(17,31,47)
ARMS=("authentic_native_R7_Colony","trained_full_episodic_Laplace",
      "trained_contextual_logistic","trained_recurrent_EMA",
      "public_source_law_oracle","no_learning_constant_zero")
COHORTS=("valid_A","retained_A","extra_A","held_B","extra_B")
def need(ok,reason):
    if not ok:raise RuntimeError(reason)
def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),allow_nan=False)
def digest(x):
    return hashlib.sha256(canonical(x).encode()).hexdigest()
def file_blob(path):
    p=subprocess.run(["git","hash-object","--",str(path)],capture_output=True,
                     text=True,cwd=HERE.parents[4],timeout=20)
    need(p.returncode==0,"FROZEN_R7_GIT_NOT_AVAILABLE")
    return p.stdout.strip()
def verify_original():
    need(file_blob(NATIVE/"native_cells.py")==NATIVE_SHA,
         "ORIGINAL_R7_SOURCE_BLOB_DRIFT")
    need(file_blob(NATIVE/"test_native_cells.py")==TEST_SHA,
         "ORIGINAL_R7_TEST_BLOB_DRIFT")
    actual=Path(sys.modules[Colony.__module__].__file__).resolve()
    need(actual==(NATIVE/"native_cells.py").resolve(),
         "NATIVE_IMPORT_WRONG_SOURCE")
def source_cases(seed):
    g=PublicDevGenerator(seed+71)
    groups={
        "train_A":_examples(g,"A",320),
        "valid_A":_examples(g,"A",160),
        "train_B":_examples(g,"B",320),
        "retained_A":_examples(g,"A",160),
        "held_B":_examples(g,"B",160),
        "extra_A":_examples(g,"A",160),
        "extra_B":_examples(g,"B",160),
    }
    for k,rows in groups.items():
        expected=320 if k.startswith("train_") else 160
        ctx=k.split("_")[-1]
        need(len(rows)==expected and all(
            c==ctx and type(y) is bool and len(s)==4
            and all(type(v) is bool for v in s)
            for c,s,y in rows),"ORIGINAL_R7_GENERATOR_COHORT_INVALID:"+k)
    need(len({digest(groups[k]) for k in COHORTS})==5,
         "ORIGINAL_R7_DEV_COHORT_COLLISION")
    return groups
class Native:
    def __init__(self):self.c=Colony()
    def fit(self,c,s,y):
        self.c.predict(c,s)
        self.c.learn_completed_public_feedback(c,s,y,2)
    def predict(self,c,s):return bool(self.c.predict(c,s))
    def checkpoint(self):return self.c.checkpoint()
    @classmethod
    def restore(cls,raw):
        x=cls();x.c=Colony.restore(raw);return x
    def counts(self):
        return {"original_feedback_updates":self.c.feedback_updates,
                "original_local_cell_updates":sum(v.updates for l in self.c.cells.values() for v in l),
                "original_neighbor_messages":self.c.neighbor_messages,
                "context_A_cells":[(z.fast,z.slow,z.updates) for z in self.c.cells["A"]],
                "context_B_cells":[(z.fast,z.slow,z.updates) for z in self.c.cells["B"]]}
class Episodic:
    def __init__(self):self.events=[]
    def fit(self,c,s,y):self.events.append((c,tuple(s),bool(y)))
    def predict(self,c,s):
        pos=1;neg=1
        for ctx,x,y in self.events:
            if ctx==c and x==tuple(s):
                pos+=int(y);neg+=int(not y)
        return pos>neg
    def checkpoint(self):return canonical({"events":self.events}).encode()
    @classmethod
    def restore(cls,raw):
        x=cls();x.events=[(c,tuple(s),y) for c,s,y in json.loads(raw)["events"]];return x
    def counts(self):return {"fitted_public_events":len(self.events)}
class OnlineLogistic:
    def __init__(self):
        self.w={"A":[0.]*5,"B":[0.]*5}
        self.updates=0
    def features(self,s):return (1.,)+tuple(1. if b else -1. for b in s)
    def fit(self,c,s,y):
        f=self.features(s)
        z=sum(a*b for a,b in zip(self.w[c],f))
        p=1/(1+math.exp(-max(-30.,min(30.,z))))
        old=self.w[c][:]
        self.w[c]=[w+.08*((float(y)-p)*v-.003*w) for w,v in zip(old,f)]
        self.updates+=1
    def predict(self,c,s):
        return sum(w*v for w,v in zip(self.w[c],self.features(s)))>0.
    def checkpoint(self):return canonical({"weights":self.w,"updates":self.updates}).encode()
    @classmethod
    def restore(cls,raw):
        x=cls();v=json.loads(raw);x.w=v["weights"];x.updates=v["updates"];return x
    def counts(self):return {"FIT_updates":self.updates}
class RecurrentEMA:
    def __init__(self):
        self.w={"A":[0.]*6,"B":[0.]*6}
        self.ema={"A":0.,"B":0.}
        self.updates=0
    def features(self,c,s):
        return (1.,)+tuple(1. if b else -1. for b in s)+(self.ema[c],)
    def fit(self,c,s,y):
        f=self.features(c,s)
        z=sum(a*b for a,b in zip(self.w[c],f))
        p=1/(1+math.exp(-max(-30.,min(30.,z))))
        old=self.w[c][:]
        self.w[c]=[w+.08*((float(y)-p)*v-.003*w) for w,v in zip(old,f)]
        self.ema[c]=.9*self.ema[c]+.1*(2.*float(y)-1.)
        self.updates+=1
    def predict(self,c,s):
        return sum(w*v for w,v in zip(self.w[c],self.features(c,s)))>0.
    def checkpoint(self):
        return canonical({"weights":self.w,"EMA":self.ema,"updates":self.updates}).encode()
    @classmethod
    def restore(cls,raw):
        x=cls();v=json.loads(raw)
        x.w=v["weights"];x.ema=v["EMA"];x.updates=v["updates"];return x
    def counts(self):return {"FIT_updates":self.updates,"source_public_rolling_memory":self.ema}
class Oracle:
    def fit(self,c,s,y):pass
    def predict(self,c,s):return s[2] if c=="A" else not s[1]
    def checkpoint(self):return b'{"source_known_fixture_oracle":true}'
    @classmethod
    def restore(cls,raw):
        need(raw==cls().checkpoint(),"SOURCE_ORACLE_STATE_DRIFT")
        return cls()
    def counts(self):return {"FIT_updates":0,"source_rule_privileged":True}
class Constant:
    def fit(self,c,s,y):pass
    def predict(self,c,s):return False
    def checkpoint(self):return b'{"constant_zero":true}'
    @classmethod
    def restore(cls,raw):
        need(raw==cls().checkpoint(),"SOURCE_CONSTANT_STATE_DRIFT")
        return cls()
    def counts(self):return {"FIT_updates":0}
CONSTRUCTORS=(Native,Episodic,OnlineLogistic,RecurrentEMA,Oracle,Constant)
def classify(model,examples):
    bits=[bool(model.predict(c,s)) for c,s,y in examples]
    correct=sum(int(z==y) for z,(_,_,y) in zip(bits,examples))
    return {"correct":correct,"total":len(examples),
            "accuracy":correct/len(examples),
            "original_public_prediction_bits_SHA256":hashlib.sha256(
                bytes(int(b) for b in bits)).hexdigest()},bits
def model_case(model_type,groups):
    agent=model_type()
    fit_cpu=0
    def train(data):
        nonlocal fit_cpu
        t=time.process_time_ns()
        for c,s,y in data:
            agent.fit(c,s,y)
        fit_cpu+=time.process_time_ns()-t
    train(groups["train_A"])
    before_blob=agent.checkpoint()
    before=model_type.restore(before_blob)
    need(before.checkpoint()==before_blob,"BEFORE_COLD_MODEL_CHECKPOINT_NOT_EXACT")
    before_stats={name:classify(before,groups[name])
                  for name in COHORTS[:3]}
    before_A=before.counts().get("context_A_cells")
    train(groups["train_B"])
    after_blob=agent.checkpoint()
    after=model_type.restore(after_blob)
    need(after.checkpoint()==after_blob,"AFTER_COLD_MODEL_CHECKPOINT_NOT_EXACT")
    frozen_sha=hashlib.sha256(after_blob).hexdigest()
    t=time.process_time_ns()
    after_stats={name:classify(after,groups[name])
                 for name in COHORTS}
    infer_cpu=time.process_time_ns()-t
    need(after.checkpoint()==after_blob,"DEV_LEAK_OR_STATE_MUTATION")
    if model_type is Native:
        need(agent.c.feedback_updates==640 and agent.c.neighbor_messages==5120
             and sum(v.updates for l in agent.c.cells.values() for v in l)==2560,
             "ORIGINAL_NATIVE_640_TRUE_DELAYED_FEEDBACK_UPDATES_INVALID")
        need(before_A==after.counts()["context_A_cells"],
             "ORIGINAL_NATIVE_A_CELL_STATE_INTERFERENCE_DETECTED")
        need(before_blob!=after_blob,
             "ORIGINAL_NATIVE_B_LEARNING_CHECKPOINT_DID_NOT_CHANGE")
    result={"original_public_FIT_events":640 if model_type in (Native,Episodic,OnlineLogistic,RecurrentEMA) else 0,
            "before_A":{k:v[0] for k,v in before_stats.items()},
            "after_DEV":{k:v[0] for k,v in after_stats.items()},
            "paired_prediction_changed_per_160":{
                k:sum(int(p!=q) for p,q in zip(before_stats[k][1],after_stats[k][1]))
                for k in COHORTS[:3]},
            "paired_score_loss_per_160":{
                k:before_stats[k][0]["accuracy"]-after_stats[k][0]["accuracy"]
                for k in COHORTS[:3]},
            "source_free_recorded_model_state":after.counts(),
            "source_model_checkpoint_bytes":len(after_blob),
            "source_model_state_round12_SHA256":digest(rounded_state(after.counts(),after_blob,model_type)),
            "source_native_checkpoint_state_hash":frozen_sha if model_type is Native else None}
    info={"fit_CPU_ns":fit_cpu,"DEV_predict_CPU_ns":infer_cpu,
          "FIT_source_state_bytes":len(before_blob),
          "DEV_persistent_state_bytes":len(after_blob)}
    return result,info
def rounded_state(counts,checkpoint,kind):
    # Scientific identity of native original checkpoint must remain exact;
    # conventional float weights across OS use 11-place canonical snapshots.
    if kind is Native:return json.loads(checkpoint)
    if kind in (Oracle,Constant,Episodic):return json.loads(checkpoint)
    def convert(x):
        if isinstance(x,float):return round(x,11)
        if isinstance(x,dict):return {k:convert(v) for k,v in x.items()}
        if isinstance(x,list):return [convert(v) for v in x]
        return x
    return convert(json.loads(checkpoint))
def one_seed(seed):
    groups=source_cases(seed)
    results={};resources={}
    for cls,name in zip(CONSTRUCTORS,ARMS):
        r,meta=model_case(cls,groups);results[name]=r;resources[name]=meta
    native=results[ARMS[0]]
    need(sum(native["paired_prediction_changed_per_160"].values())==0 and
         all(loss==0 for loss in native["paired_score_loss_per_160"].values()),
         "PAIRED_ORIGINAL_NATIVE_SAME_EXAMPLE_RETENTION_CHANGED")
    old_pre=native["before_A"]["valid_A"]["accuracy"]
    old_post=native["after_DEV"]["retained_A"]["accuracy"]
    paired=old_pre-native["after_DEV"]["valid_A"]["accuracy"]
    sampling=native["after_DEV"]["valid_A"]["accuracy"]-old_post
    need(abs((old_pre-old_post)-(paired+sampling))<1e-12,
         "PUBLIC_UNPAIRED_LOSS_DECOMPOSITION_INVALID")
    return {"frozen_public_original_R7_seed":seed,
            "original_public_FIT_transcript_SHA256":digest(
                groups["train_A"]+groups["train_B"]),
            "original_public_DEV_cohort_SHA256":{
                name:digest(groups[name]) for name in COHORTS},
            "models":results,
            "native_unpaired_valid_before_minus_distinct_retained_after":old_pre-old_post,
            "native_same_valid_before_minus_after":paired,
            "native_distinct_test_composition_gap":sampling},resources,groups
def pooled(cases,name,cohorts,stage="after_DEV"):
    correct=sum(case["models"][name][stage][cohort]["correct"]
                for case in cases for cohort in cohorts)
    total=sum(case["models"][name][stage][cohort]["total"]
              for case in cases for cohort in cohorts)
    return correct/total
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    dest=Path(args.out);dest.mkdir(parents=True,exist_ok=True)
    receipt={"schema":"mass.cs16.paired_R7_vs_equal_fit_memory.v1",
             "FIRST_preregistered_commit":FIRST,
             "disposition":"PUBLIC_CS16_INVALID"}
    resources={"schema":"mass.cs16.process_resources.v1"}
    all_raw={"schema":"mass.cs16.original_public_generator_source_free_cohorts.v1","seeds":[]}
    t0=time.process_time_ns()
    try:
        verify_original()
        original_history=[study(s) for s in OLD]
        need(gates(original_history) is False and
             original_history[1]["a_before_b"]==.93125 and
             original_history[1]["a_after_b"]==.86875,
             "FROZEN_ORIGINAL_R7_HISTORY_OR_NEGATIVE_DRIFT")
        cases=[];per_resource=[]
        for seed in SEEDS:
            case,resource_row,groups=one_seed(seed)
            cases.append(case)
            per_resource.append({"seed":seed,"measured_CPU_resources":resource_row})
            all_raw["seeds"].append({"seed":seed,"groups":{
                k:groups[k] for k in ("train_A","train_B")+COHORTS}})
            print("CS16_PUBLIC_SEED="+str(seed)+" NATIVE_A="+str(
                case["models"][ARMS[0]]["after_DEV"]["valid_A"]["accuracy"])+
                " NATIVE_B="+str(case["models"][ARMS[0]]["after_DEV"]["held_B"]["accuracy"]),
                flush=True)
        a=("valid_A","retained_A","extra_A");b=("held_B","extra_B")
        pooled_quality={name:{
            "retained_A_same_original_cases":pooled(cases,name,a),
            "acquired_B_original_public_holdout":pooled(cases,name,b),
            "mean_fit_checkpoint_bytes":sum(case["models"][name]["source_model_checkpoint_bytes"]
                                             for case in cases)/len(cases)}
             for name in ARMS}
        native=pooled_quality[ARMS[0]]
        strong=[pooled_quality[n] for n in ARMS[1:4]]
        equal_baseline_A=max(z["retained_A_same_original_cases"] for z in strong)
        equal_baseline_B=max(z["acquired_B_original_public_holdout"] for z in strong)
        per_seed_min=all(
            all(case["models"][ARMS[0]]["after_DEV"][k]["accuracy"]>=.75
                for k in a+b) for case in cases)
        checks={
            "6_seeds_each_NATIVE_A_3_heldout_and_B_2_holdout_above_75_percent":per_seed_min,
            "native_pooled_A_gt_constant_by_at_least_15pp":
                native["retained_A_same_original_cases"]-
                pooled_quality[ARMS[5]]["retained_A_same_original_cases"]>=.15,
            "native_pooled_B_gt_constant_by_at_least_15pp":
                native["acquired_B_original_public_holdout"]-
                pooled_quality[ARMS[5]]["acquired_B_original_public_holdout"]>=.15,
            "native_pooled_A_within_5pp_of_strongest_fitted":
                native["retained_A_same_original_cases"]>=equal_baseline_A-.05,
            "native_pooled_B_within_5pp_of_strongest_fitted":
                native["acquired_B_original_public_holdout"]>=equal_baseline_B-.05,
            "native_2880_paired_A_case_predictions_unchanged":
                all(sum(c["models"][ARMS[0]]["paired_prediction_changed_per_160"].values())==0 for c in cases)}
        receipt.update({
            "schema":"mass.cs16.paired_R7_vs_equal_fit_memory.v1",
            "FIRST_preregistered_commit":FIRST,
            "original_native_R7_git_blob":NATIVE_SHA,
            "original_frozen_test_git_blob":TEST_SHA,
            "original_R7_historical_seeds_17_31_47_gate_pass":False,
            "original_historical_seed31_before_A":.93125,
            "original_historical_seed31_after_different_A":.86875,
            "historical_original_R7_legacy_integration":"FAIL_PRESERVED",
            "original_source_kind":"UNMODIFIED_PUBLICDEVGENERATOR_SOURCE_FREE",
            "original_source_owned_external_action_calls":0,
            "independent_unfamiliar_source_first_use":False,
            "strong_conventional_training_equal_FIT_examples_per_model":True,
            "source_known_oracle_is_privileged_not_equal_FIT":True,
            "prospective_sourcefree_6_seeds":list(SEEDS),
            "all_public_seed_scientific_receipts":cases,
            "pooled_scientific_quality_and_serialized_state":pooled_quality,
            "pooled_best_equal_fit_conventional_A":equal_baseline_A,
            "pooled_best_equal_fit_conventional_B":equal_baseline_B,
            "preregistered_gate_criteria":checks,
            "native_A_exact_paired_prediction_changes":0,
            "paired_native_original_A_holdout_cases":6*3*160,
            "native_B_original_public_heldout_cases":6*2*160,
            "sourcefree_all_public_generator_cohort_records_SHA256":digest(all_raw),
            "original_R7_frozen_test_waived_or_rewritten":False,
            "CS14_original_multi_action_production_promotion":False,
            "ELG_01_additive_language_mechanism_executed":False,
            "disposition":("PUBLIC_CS16_NATIVE_PAIRED_RETENTION_NONINFERIORITY_SUPPORTED_PUBLIC_ONLY"
                if all(checks.values()) else "PUBLIC_CS16_NATIVE_PAIRED_RETENTION_NONINFERIORITY_NOT_SHOWN")
        })
        resources["per_seed_CPU_and_checkpoint_bytes"]=per_resource
    except Exception as e:
        receipt["first_failure"]=type(e).__name__+":"+str(e)[:1000]
    finally:
        resources["full_process_CPU_ns_including_original_public_fixture"]=time.process_time_ns()-t0
        resources["peak_process_RSS_KiB"]=(
            resource.getrusage(resource.RUSAGE_SELF).ru_maxrss if resource else "NOT_MEASURED_WINDOWS")
        (dest/"cs16-logical-science-receipt.json").write_text(
            json.dumps(receipt,sort_keys=True,indent=2)+"\n")
        (dest/"cs16-original-R7-sourcefree-public-cohorts.json").write_text(
            canonical(all_raw)+"\n")
        resources["canonical_logical_science_SHA256"]=digest(receipt)
        (dest/"cs16-OS-process-resource-metadata.json").write_text(
            json.dumps(resources,sort_keys=True,indent=2)+"\n")
    print("CS16_DISPOSITION="+receipt["disposition"],flush=True)
    print("CS16_LOGICAL_RECEIPT_SHA256="+digest(receipt),flush=True)
    return 2 if receipt["disposition"]=="PUBLIC_CS16_INVALID" else 0
if __name__=="__main__":
    raise SystemExit(main())
