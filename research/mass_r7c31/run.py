"""C31 source-original FIT-only R3 selected-action bridge certificate.

No MiniGrid original source environment is imported or executed. Model
predictions for UNCHOSEN actions are extrapolations from policy-collected FIT,
not physically witnessed action outcomes or proof of information value.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from research.native.itd02.r1.native_policy import canonical
from research.mass_r7c29.analysis import read_frozen_artifact
from research.mass_r7c29.effects import (
  data_event,event_split,make_arms,sealed,train,view
)
from research.mass_r7c30.independent_logistic import IndependentPublicLogistic
from research.mass_r7c31.action_bridge import (
  P,source_public_navigator,source_sensor_update,decision,
  learned_source_motors,replay_training_only_source_histories,qualified_disposition
)

ROOT=Path(__file__).resolve().parents[2]


def train_models(original):
    training,check=event_split(original)
    # Exactly C29 and C30 frozen first-8-per-family source FIT fit.
    original_arms=make_arms()
    train(original_arms,training)
    models={
     "native":original_arms["native"],
     "shuffled_action":original_arms["shuffled_action"],
     "frozen":original_arms["frozen"],
     "time_only":original_arms["time_only"],
     "temporal_bayes":original_arms["conventional"],
     "full9_conventional_sgd":IndependentPublicLogistic(0.0),
     "full9_conventional_momentum":IndependentPublicLogistic(.85)
    }
    for e in training:
        state,action,outcome=data_event(e)
        models["full9_conventional_sgd"].observe(state,action,outcome)
        models["full9_conventional_momentum"].observe(state,action,outcome)
    return models,training,check


def cold_check_at_real_episode_step3(models,motors,check):
    first_group=(check[0]["family"],check[0]["seed"])
    episode=[e for e in check if (e["family"],e["seed"])==first_group]
    if len(episode)<4:
        raise ValueError("NOT_ENOUGH_AUTHENTIC_FIT_STEPS_FOR_MID_EPISODE_COLD")
    nav=source_public_navigator(motors,first_group[0])
    for e in episode[:3]:
        before,a,y=data_event(e)
        after=view(e["returned_after"])
        source_sensor_update(nav,before)
        nav.observe(before,a,after,e["returned_reward"],e["terminated"],False)
        if e["terminated"] or e["truncated"]:
            raise ValueError("SOURCE_EPISODE_TERMINAL_BEFORE_COLD")
    state=view(episode[3]["before"])
    source_sensor_update(nav,state)
    payload={"public":episode[3]["before"],"navigator_checkpoint":nav.snapshot().decode("utf-8"),
      "checks":[]}
    sizes={"r3":len(nav.snapshot())}
    for name,model in models.items():
        kind="logistic" if name.startswith("full9_") else "native_or_beta"
        blob=(model.checkpoint() if kind=="logistic" else sealed(model))
        baseline,proposed,pred=decision(nav,state,model)
        payload["checks"].append({"name":name,"kind":kind,"checkpoint":blob.decode("utf-8"),
          "base":baseline,"proposed":proposed,"predict":pred})
        sizes[name]=len(blob)
    program="""import json,sys
from research.native.itd02.r1.native_policy import PublicGrid
from research.native.itd02.r3.navigator import Navigator
from research.mass_r7c29.effects import unseal
from research.mass_r7c30.independent_logistic import IndependentPublicLogistic
from research.mass_r7c31.action_bridge import decision
payload=json.loads(sys.stdin.read())
nav=Navigator.restore(payload['navigator_checkpoint'].encode('utf-8'))
state=PublicGrid(**payload['public'])
for c in payload['checks']:
    model=(IndependentPublicLogistic.restore(c['checkpoint'].encode('utf-8'))
           if c['kind']=='logistic' else unseal(c['checkpoint'].encode('utf-8')))
    b,a,p=decision(nav,state,model)
    assert b==c['base'] and a==c['proposed'] and p==c['predict'],c['name']
print('C31_AUTHENTIC_FIT_MID_EPISODE_FRESH_OS_R3_AND_ALL_PREDICTORS=PASS')
"""
    completed=subprocess.run([sys.executable,"-B","-c",program],
       input=json.dumps(payload),text=True,capture_output=True,
       cwd=ROOT,timeout=30,env={**os.environ,"PYTHONDONTWRITEBYTECODE":"1"})
    if completed.returncode!=0 or "PREDICTORS=PASS" not in completed.stdout:
        raise ValueError("C31_FRESH_OS_POLICY_RESTORE_FAILED:"+completed.stderr[-1000:])
    return sizes


def run(original_fit_dir):
    started=time.process_time()
    original,source=read_frozen_artifact(original_fit_dir)
    models,training,check=train_models(original)
    if len(original)!=805 or len(check)!=341:
        raise ValueError("C29_C30_FROZEN_FIT_SPLIT_MISMATCH")
    motors=learned_source_motors(training)
    results=replay_training_only_source_histories(models,check,motors)
    cold_sizes=cold_check_at_real_episode_step3(models,motors,check)
    disposition=qualified_disposition(results)
    # Keep the full original-state proposed-choice counterfactual record in
    # GitHub Actions, no private map, no hidden source physics.
    trace={"schema":P["schema"],"public_fit_only":True,
      "source_original_fit_sha256":source["source_fit_event_ledger_sha256"],
      "never_physically_executed_alternate_action":True,
      "all_models":results}
    summary={name:{k:v for k,v in result.items() if k!="decisions"}
             for name,result in results.items()}
    for name,r in results.items():
        if r["checked"]!=len(check):
            raise ValueError("MISSING_CHOICE_QUERY")
        if r["baseline_turns"]<1:
            raise ValueError("R3_BASELINE_NEVER_TURNS")
        if r["proposed_forward"]<0:
            raise ValueError("C31_IMPOSSIBLE_POLICY")
    report={
      "schema":P["schema"],"source_original":source["original_source"],
      "frozen_C28_real_original_fit_selected_action_records":len(original),
      "training_only_source_public_queries":len(check),
      "source_FIT_training_event_count":len(training),
      "original_source_new_actions":0,"original_source_dev_or_protected_first_use":0,
      "actual_returned_alternate_consequence_observed":False,
      "models_fully_fit_from_original_selected_effects":True,
      "source_original_r3_original_planner_modified":False,
      "full_original_fit_actor_motors_from_real_physical_returns":motors,
      "native_and_conventional_policy_source_free_choices":summary,
      "cold_restored_actual_episode_step3_checkpoint_bytes":cold_sizes,
      "decision_leverage_disposition":disposition,
      "learned_value_of_information_and_source_world_goal_improvement":"NOT_ESTABLISHED",
      "scientific_uncertainty":"Chosen-policy training confounds unselected effects; turn also advances moving-world time.",
      "elapsed_cpu_seconds":round(time.process_time()-started,6)
    }
    print("C31_REAL_C28_ORIGINAL_FIT_SOURCE_REAUTHENTICATED=PASS",flush=True)
    print("C31_ACTUAL_FIT_ONLY_CHOICE_QUERY_COUNTS="+json.dumps(summary,sort_keys=True),flush=True)
    print("C31_MID_EPISODE_FRESH_OS_ALL_POLICY_AND_CELL_PARITY=PASS",flush=True)
    print("C31_NATIVE_R3_ACTION_LEVERAGE="+disposition,flush=True)
    print("C31_NEW_ORIGINAL_SOURCE_ACTIONS=0",flush=True)
    print("C31_PROTECTED_FIRST_USE=DENIED",flush=True)
    return report,trace


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--original-fit-dir",required=True)
    ap.add_argument("--out-dir",required=True)
    a=ap.parse_args()
    report,trace=run(a.original_fit_dir)
    out=Path(a.out_dir)
    out.mkdir(parents=True,exist_ok=True)
    data=canonical(report)
    (out/"report.json").write_bytes(data+b"\n")
    (out/"public-fit-proposed-decisions.json").write_bytes(canonical(trace)+b"\n")
    print("C31_FIT_ONLY_REPORT_SHA256="+hashlib.sha256(data).hexdigest())
