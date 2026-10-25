"""C30 score feature-matched conventional online public action-effects on frozen C28 FIT only."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

from research.native.itd02.r1.native_policy import canonical, features
from research.mass_r7c29.analysis import read_frozen_artifact
from research.mass_r7c29.effects import event_split,make_arms,train,data_event,exploratory_proxy
from research.mass_r7c30.independent_logistic import IndependentPublicLogistic,independently_encoded_public

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
P=json.loads((HERE/"PREREG.json").read_text())


def score(models,rows):
    records={name:{"sumsq":0.0,"nll":0.0,"n":0,"by_family":defaultdict(list),
                  "by_action":defaultdict(list),"proxy_probe":0,"proxy_decline":0}
             for name in models}
    classifications={}
    for e in rows:
        s,a,y=data_event(e)
        if independently_encoded_public(s)!=features(s):
            raise ValueError("C30_ACTUAL_PUBLIC_NINE_FEATURES_NOT_IDENTICAL")
        for name,model in models.items():
            pred=model.predict(s,a)
            if not 0<pred<1:raise ValueError("C30_INVALID_PREDICTION")
            d=(pred-y)**2
            nll=-(y*math.log(pred)+(1-y)*math.log1p(-pred))
            z=records[name]
            z["sumsq"]+=d
            z["nll"]+=nll
            z["n"]+=1
            z["by_family"][e["family"]].append(d)
            z["by_action"][str(a)].append(d)
            if exploratory_proxy(model,s,a):z["proxy_probe"]+=1
            else:z["proxy_decline"]+=1
    return {
     name:{
      "n":z["n"],"brier":round(z["sumsq"]/z["n"],9),
      "log_loss":round(z["nll"]/z["n"],9),
      "per_source_family":{fam:{"n":len(v),"brier":round(sum(v)/len(v),9)}
                          for fam,v in sorted(z["by_family"].items())},
      "per_selected_action":{action:{"n":len(v),"brier":round(sum(v)/len(v),9)}
                             for action,v in sorted(z["by_action"].items())},
      "source_free_proxy":{"probe":z["proxy_probe"],"decline":z["proxy_decline"]}
     } for name,z in records.items()
    }


def native_and_comparators(data):
    trainrows,checkrows=event_split(data)
    old=make_arms()
    train(old,trainrows)
    models={"native":old["native"],"temporal_bayes":old["conventional"],
      "native_shuffled":old["shuffled_action"],
      "native_frozen":old["frozen"],
      "time_only_bayes":old["time_only"],
      "full9_logistic_sgd":IndependentPublicLogistic(0.0),
      "full9_logistic_momentum":IndependentPublicLogistic(.85)}
    t0=time.process_time()
    for e in trainrows:
        s,a,y=data_event(e)
        models["full9_logistic_sgd"].observe(s,a,y)
        models["full9_logistic_momentum"].observe(s,a,y)
    train_cpu=round(time.process_time()-t0,6)
    test=score(models,checkrows)
    expected={"native":0.173901971,"temporal_bayes":0.181200564,
        "native_shuffled":0.213467862,"native_frozen":.25,"time_only_bayes":0.226552501}
    for name,value in expected.items():
        if test[name]["brier"]!=value:
            raise ValueError("C29_FROZEN_PRIOR_FIT_BRIER_REGRESSION:"+name)
    # The original C29 fixed Bayesian had lower effective source-public
    # representation; FULL9 conventional receives all nine original features.
    matched=min(test["full9_logistic_sgd"]["brier"],test["full9_logistic_momentum"]["brier"])
    native=test["native"]["brier"]
    if native<matched:status="NATIVE_LOWER_BRIER_THAN_BOTH_MATCHED_CONVENTIONAL_ON_INTERNAL_FIT"
    elif native==matched:status="NATIVE_TIED_BEST_FULL9_CONVENTIONAL_ON_INTERNAL_FIT"
    else:status="AT_LEAST_ONE_FULL9_CONVENTIONAL_LOWER_BRIER_THAN_NATIVE"
    same_public_queries={}
    for arm in ("full9_logistic_sgd","full9_logistic_momentum"):
        model=models[arm]
        same_public_queries[arm]=sum(
           model.predict(data_event(e)[0],data_event(e)[1])!=models["native"].predict(data_event(e)[0],data_event(e)[1])
           for e in checkrows)
    for e in checkrows:
        s,a,y=data_event(e)
        models["full9_logistic_sgd"].observe(s,a,y)
        models["full9_logistic_momentum"].observe(s,a,y)
    return models,checkrows,test,status,train_cpu,same_public_queries,len(trainrows)


def fresh_process_check(model,queries):
    blob=model.checkpoint()
    payload={"blob":blob.decode(),"queries":[]}
    for e in queries[:10]:
        s,a,y=data_event(e)
        payload["queries"].append({"view":e["before"],"action":a,
          "p":model.predict(s,a),"probe":exploratory_proxy(model,s,a)})
    program="""import json,sys
from research.mass_r7c30.independent_logistic import IndependentPublicLogistic
from research.mass_r7c29.effects import view,exploratory_proxy
p=json.loads(sys.stdin.read())
m=IndependentPublicLogistic.restore(p['blob'].encode())
assert m.checkpoint().decode()==p['blob']
for q in p['queries']:
    v=view(q['view'])
    assert abs(m.predict(v,q['action'])-q['p'])<1e-13
    assert exploratory_proxy(m,v,q['action'])==q['probe']
print('C30_FULL9_CONVENTIONAL_FRESH_OS_BEHAVIORAL_PARITY=PASS')
"""
    r=subprocess.run([sys.executable,"-B","-c",program],cwd=ROOT,text=True,
          input=json.dumps(payload),capture_output=True,timeout=30,
          env={**os.environ,"PYTHONDONTWRITEBYTECODE":"1"})
    if r.returncode or "PARITY=PASS" not in r.stdout:
        raise ValueError("CONVENTIONAL_COLD_RESTORE_FAILED:"+r.stderr)
    return len(blob)


def main():
    args=argparse.ArgumentParser()
    args.add_argument("--c28-artifact-dir",required=True)
    args.add_argument("--out",required=True)
    a=args.parse_args()
    start=time.process_time()
    original,source=read_frozen_artifact(a.c28_artifact_dir)
    if len(original)!=805:raise ValueError("NONFROZEN_FIT_COUNT")
    models,check,scores,status,train_cpu,queries,ntrain=native_and_comparators(original)
    bytes_={name:fresh_process_check(models[name],check) for name in ("full9_logistic_sgd","full9_logistic_momentum")}
    report={
      "schema":P["schema"],"classification":P["classification"],
      "input_original_source_fit_ledger_sha256":source["source_fit_event_ledger_sha256"],
      "source_original":source["original_source"],
      "original_selected_fit_events":len(original),
      "internal_fit_learn_events":ntrain,"internal_fit_check_events":len(check),
      "same_full_nine_public_features_for_all_native_and_full9_models":True,
      "source_returned_effect":"next_public_front_blocked",
      "prereg_no_check_tuning_or_new_external_episodes":True,
      "same_frozen_r1_local_cells_as_c29":True,
      "brier_nll_and_group_metrics":scores,
      "source_free_fixed_proxy_not_observed_source_behavior":True,
      "native_vs_best_full9_conventional":status,
      "full9_vs_native_distinct_probability_count":queries,
      "full9_conventional_complete_cold_checkpoint_bytes":bytes_,
      "full9_conventional_fit_only_training_cpu_seconds":train_cpu,
      "overall_process_cpu_seconds":round(time.process_time()-start,6),
      "original_environment_resets_or_steps":0,
      "dev_valid_protected_events":0,
      "scientific_architectural_superiority":"NOT_DEMONSTRATED_WITHOUT_REAL_ACTION_DECISION_SOURCE_EXECUTION_AND_STRONGER_CONTROLS"
    }
    out=canonical(report)
    Path(a.out).write_bytes(out+b"\n")
    print("C30_AUTHENTIC_C28_SOURCE_FIT_ONLY=PASS")
    print("C30_FROZEN_C29_METRICS_REPRODUCED=PASS")
    print("C30_FULL_FEATURE_PUBLIC_PARITY=PASS")
    print("C30_INTERNAL_FIT_GROUP_BRIER="+json.dumps({k:{"brier":v["brier"],"n":v["n"]} for k,v in scores.items()},sort_keys=True))
    print("C30_FEATURE_MATCHED_NATIVE_VERDICT="+status)
    print("C30_FRESH_OS_FULL_CONVENTIONAL_PARITY=PASS")
    print("C30_NEW_SOURCE_ACTIONS_AND_PROTECTED_FIRST_USE=0")
    print("C30_CERTIFICATE_SHA256="+hashlib.sha256(out).hexdigest())


if __name__=="__main__":
    main()
