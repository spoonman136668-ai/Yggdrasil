"""C29 evaluate two learned public successor models on existing frozen C28 FIT.

This file does not import gym/minigrid or execute environmental episodes.
The only source of evidence is exact-provider-hash audited GitHub C28 archive.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

from research.mass_r7c29.effects import (
  P, NativeCellEffect, ConventionalBeta, canonical, data_event,
  event_split, exploratory_proxy, make_arms, prediction_metrics,
  query_impact, sealed, train, view
)


def read_frozen_artifact(folder):
    folder=Path(folder)
    expected={"original-fit-1.json","original-fit-2.json","comparison.json"}
    if {x.name for x in folder.iterdir() if x.is_file()}!=expected:
        raise ValueError("C28_PROVIDER_LEDGER_MEMBERS_MISMATCH")
    sources=[json.loads((folder/f"original-fit-{i}.json").read_text()) for i in (1,2)]
    if sources[0]!=sources[1]:
        # C28 CPU/RSS are the only nondeterministic measurements allowed.
        def science_only(x):
            return {k:v for k,v in x.items() if k not in (
                "cpu_bootstrap_seconds","cpu_whole_process_seconds","peak_process_rss_kib")}
        if science_only(sources[0])!=science_only(sources[1]):
            raise ValueError("C28_ORIGINAL_TWO_SOURCE_FIT_LEDGER_DRIFT")
    comparison=json.loads((folder/"comparison.json").read_text())
    if hashlib.sha256(canonical(comparison)).hexdigest()!=P["source_fit"]["reconciliation_sha256"]:
        raise ValueError("C28_ORIGINAL_RECONCILED_SOURCE_DIGEST_DRIFT")
    source=sources[0]
    expected_fit=P["source_fit"]
    if (source.get("schema")!="itd02.c28.authenticated-original-source-turn-inclusive-fit-ledger.v1" or
        source.get("original_source")!=expected_fit["source_original"] or
        source.get("source_fit_action_counts")!=expected_fit["selected_actions"] or
        source.get("source_fit_information_front_counts")!=expected_fit["info_returned"] or
        source.get("scientific_status")!="FIT_SOURCE_DATA_READY_FOR_SEPARATE_LEARNER_GATE" or
        source.get("original_new_dev_episodes")!=0 or
        source.get("protected_first_use_episodes")!=0 or
        source.get("learning_value_of_information_executed") is not False):
        raise ValueError("NOT_ORIGINAL_AUTHENTIC_FIT_ONLY_CORPUS")
    events=source.get("source_fit_events")
    if (type(events) is not list or len(events)!=805 or
        hashlib.sha256(canonical(events)).hexdigest()!=source.get("source_fit_event_ledger_sha256") or
        comparison.get("original_source_fit_event_sha256")!=source.get("source_fit_event_ledger_sha256")):
        raise ValueError("C28_ACTUAL_ACTION_EVENT_DIGEST_MISMATCH")
    expected_pairs={(e["family"],e["seed"]) for e in events}
    original_protocol=json.loads((Path(__file__).resolve().parent.parent/"mass_r7c28"/"PREREG.json").read_text())
    frozen_pairs={(fam,seed) for fam,seeds in original_protocol["new_fit_episodes"].items() for seed in seeds}
    if expected_pairs!=frozen_pairs:
        raise ValueError("C28_SOURCE_FIT_ROLE_IDENTITY_MISMATCH")
    # Fail closed if any selected event became duplicated/reordered or switched
    # to privileged and not the original source-public six-field event grammar.
    prior={}
    seen=Counter()
    for e in events:
        s,a,target=data_event(e)
        pair=(e["family"],e["seed"])
        if e["step"]!=prior.get(pair,-1)+1:
            raise ValueError("C28_DUPLICATE_OR_MISSING_ACTION_STEP")
        prior[pair]=e["step"]
        seen[str(a)]+=1
    if [seen[str(a)] for a in (0,1,2)]!=[236,143,426]:
        raise ValueError("ORIGINAL_SOURCE_SELECTED_ACTION_COVERAGE_DRIFT")
    return events,source


def fresh_os_cold_parity(model,queries):
    checkpoint=sealed(model)
    payload={"checkpoint":checkpoint.decode("utf-8"),
      "queries":[{"before":e["before"],"action":e["chosen_action"],
       "expected_probability":model.predict(view(e["before"]),e["chosen_action"]),
       "expected_probe":exploratory_proxy(model,view(e["before"]),e["chosen_action"])}
       for e in queries[:10]]}
    program="""import json,sys
from research.mass_r7c29.effects import unseal,view,exploratory_proxy
p=json.loads(sys.stdin.read())
m=unseal(p['checkpoint'].encode('utf-8'))
for item in p['queries']:
    s=view(item['before']);a=item['action']
    assert abs(m.predict(s,a)-item['expected_probability'])<1e-13
    assert exploratory_proxy(m,s,a)==item['expected_probe']
print('C29_FRESH_PROCESS_FULL_STATE_PREDICTION_AND_PROXY_PARITY=PASS')
"""
    r=subprocess.run([sys.executable,"-B","-c",program],input=json.dumps(payload),
        text=True,capture_output=True,cwd=Path(__file__).resolve().parents[2],
        env={**os.environ,"PYTHONDONTWRITEBYTECODE":"1"},timeout=25)
    if r.returncode!=0 or "PARITY=PASS" not in r.stdout:
        raise ValueError("C29_OS_COLD_PREDICTION_MISMATCH:"+r.stderr[-1000:])
    return len(checkpoint)


def run(folder):
    t0=time.process_time()
    events,source=read_frozen_artifact(folder)
    training,internal=event_split(events)
    arms=make_arms()
    train(arms,training)
    fit_scores={name:prediction_metrics(m,internal) for name,m in arms.items()}
    queries=query_impact(arms,internal)
    n=len(internal)
    choice_summary={}
    for name,responses in queries.items():
        choice_summary[name]={"probe":sum(r["would_probe"] for r in responses),
          "decline":n-sum(r["would_probe"] for r in responses)}
    differs={}
    for name in ("conventional","time_only","shuffled_action","frozen"):
        differs[name]={"probability":sum(abs(x["p"]-y["p"])>1e-7 for x,y in zip(queries["native"],queries[name])),
            "exploration_proxy_choice":sum(x["would_probe"]!=y["would_probe"] for x,y in zip(queries["native"],queries[name]))}
    before_full={name:m.updates for name,m in arms.items()}
    # Only AFTER reporting internal FIT scores, fit remaining FIT observations
    # to produce a complete final training checkpoint. No independent holdout.
    train(arms,internal)
    checkpoint_sizes={name:fresh_os_cold_parity(m,internal) for name,m in arms.items()}
    if any(arms[name].updates!=before_full[name]+len(internal) for name in
       ("native","conventional","time_only","shuffled_action")):
        raise ValueError("C29_FINALLY_TRAINED_SOURCE_EVENT_ACCOUNTING_DRIFT")
    report={
      "schema":P["schema"],
      "classification":P["status"],
      "original_fit_artifact_sha256":P["source_fit"]["artifact_zip_sha256"],
      "original_C28_source_reconciliation_sha256":P["source_fit"]["reconciliation_sha256"],
      "source_fit_original_selected_events":len(events),
      "source_fit_training_event_count":len(training),
      "source_fit_internal_check_event_count":len(internal),
      "never_original_dev_or_valid":True,"protected_first_use":False,
      "original_source_new_environment_actions":0,
      "models":{"native":"ORIGINAL_R1_LOCAL_CELL_SELECTED_EFFECT_OFFSPRING",
        "conventional":"INDEPENDENT_TEMPORAL_BAYES",
        "control_time_only":"INDEPENDENT_BAYES_WITHOUT_ACTION",
        "ablation_shuffled":"ACTION_LABEL_SHIFTED_NATIVE_CELLS",
        "ablation_frozen":"NO_UPDATES_CONSTANT_PRIOR"},
      "internal_fit_only_brier":fit_scores,
      "source_free_information_proxy_queries":choice_summary,
      "native_minus_other_fit_query_impacts":differs,
      "full_fit_final_updates":{name:m.updates for name,m in arms.items()},
      "complete_cold_checkpoint_bytes":checkpoint_sizes,
      "source_training_one_policy_observational_not_counterfactual":True,
      "predictive_outcome_is_observed_next_front_only":True,
      "learned_information_value_of_actions":"NOT_ESTABLISHED",
      "native_vs_bayesian_predictive_advantage":(
         "LOWER_INTERNAL_FIT_BRIER" if fit_scores["native"]["brier"]<fit_scores["conventional"]["brier"]
         else "NO_NATIVE_BRIER_ADVANTAGE"),
      "fit_native_cell_predictive_action_evidence":(
         "ACTION_SHUFFLING_CHANGES_FITTED_PUBLIC_PREDICTIONS" if differs["shuffled_action"]["probability"] else
         "NO_SEPARATION_FROM_SHUFFLED_ACTION_CONTROL"),
      "elapsed_cpu_seconds":round(time.process_time()-t0,6)
    }
    print("C29_AUTHENTIC_C28_FIT_BYTES=PASS",flush=True)
    print("C29_ORIGINAL_SOURCE_NEW_ACTIONS=0",flush=True)
    print("C29_FIT_PREQUENTIAL_BRIER="+json.dumps(fit_scores,sort_keys=True),flush=True)
    print("C29_MODEL_PROXY_CHOICES="+json.dumps(choice_summary,sort_keys=True),flush=True)
    print("C29_NATIVE_ACTION_ABLATIONS="+json.dumps(differs,sort_keys=True),flush=True)
    print("C29_NATIVE_VS_CONVENTIONAL_VERDICT="+report["native_vs_bayesian_predictive_advantage"],flush=True)
    print("C29_FRESH_OS_COLD_PARITY_ALL_MODELS=PASS",flush=True)
    print("C29_PROTECTED_FIRST_USE=DENIED",flush=True)
    return report


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--frozen-artifact-dir",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    report=run(args.frozen_artifact_dir)
    bytes_=canonical(report)
    Path(args.out).write_bytes(bytes_+b"\n")
    print("C29_FIT_CERTIFICATE_SHA256="+hashlib.sha256(bytes_).hexdigest())
