"""C34 original-source FIT-only Markov-sufficiency and real action-history gate.

Consumes the exact authenticated C28 full public event ledger, not MiniGrid.
The historical physical action pair is an *observed* chosen sequence; it does
NOT identify value/reward/causality of any other unchosen action sequence.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time

from research.native.itd02.r1.native_policy import canonical
from research.mass_r7c29.analysis import read_frozen_artifact
from research.mass_r7c29.effects import NativeCellEffect
from research.mass_r7c30.independent_logistic import IndependentPublicLogistic
from research.mass_r7c34.belief import (
    P,SourceBeliefBeta,source_sequences,all_records,split_fit_roles,
    shuffled_histories,sample_metrics,sequence_support
)

ROOT=Path(__file__).resolve().parents[2]


def train_equal_fit(train):
    arms={
       "current_cue_beta":SourceBeliefBeta(False),
       "prior_action_belief_beta":SourceBeliefBeta(True),
       "prior_history_shuffled_beta":SourceBeliefBeta(True),
       "full_nine_public_logistic":IndependentPublicLogistic(0.),
       "native_original_local_cells":NativeCellEffect()
    }
    altered=shuffled_histories(train)
    for item,shuf in zip(train,altered):
        s=item["before"];a=item["chosen_action"];y=item["returned_front"]
        arms["current_cue_beta"].observe(item)
        arms["prior_action_belief_beta"].observe(item)
        arms["prior_history_shuffled_beta"].observe(item,history_override=shuf)
        arms["full_nine_public_logistic"].observe(s,a,y)
        arms["native_original_local_cells"].observe(s,a,y)
    if any(m.updates!=len(train) for m in arms.values()):
        raise ValueError("C34_UNEQUAL_SOURCE_FIT_LEARNING_RIGHTS")
    return arms


def cold_history_parity(model,rows):
    checkpoint=model.checkpoint()
    sample=[{
        "before":item["before"].__dict__,
        "chosen_action":item["chosen_action"],
        "returned_front":item["returned_front"],
        "prior_history":item["prior_history"],
        "expected_probability":model.predict(item)
    } for item in rows[:12]]
    if not sample:raise ValueError("C34_NO_COLD_QUERIES")
    program="""import json,sys
from research.native.itd02.r1.native_policy import PublicGrid
from research.mass_r7c34.belief import SourceBeliefBeta
v=json.loads(sys.stdin.read())
m=SourceBeliefBeta.restore(v['checkpoint'].encode())
assert m.checkpoint().decode()==v['checkpoint']
for q in v['queries']:
    item={'before':PublicGrid(**q['before']),'chosen_action':q['chosen_action'],
          'returned_front':q['returned_front'],
          'prior_history':tuple(q['prior_history']) if q['prior_history'] is not None else None}
    assert abs(m.predict(item)-q['expected_probability'])<1e-13
print('C34_FRESH_OS_CAUSALLY_PRIOR_PUBLIC_MEMORY=PASS')
"""
    task=subprocess.run([sys.executable,"-B","-c",program],input=json.dumps({
       "checkpoint":checkpoint.decode(),"queries":sample}),text=True,
       capture_output=True,cwd=ROOT,timeout=25,
       env={**os.environ,"PYTHONDONTWRITEBYTECODE":"1"})
    if task.returncode or "PUBLIC_MEMORY=PASS" not in task.stdout:
        raise ValueError("C34_COLD_PRIOR_BELIEF_ERROR:"+task.stderr[-1300:])
    return len(checkpoint)


def audit(folder):
    original,source=read_frozen_artifact(folder)
    if len(original)!=805 or source.get("source_fit_event_ledger_sha256") is None:
        raise ValueError("C34_SOURCE_C28_NOT_ACCEPTED")
    episodes=source_sequences(original)
    records=all_records(episodes)
    training,check=split_fit_roles(records)
    arm=train_equal_fit(training)
    per_model={}
    for name,model in arm.items():
        overall=[];family={};action={}
        for r in check:
            s=r["before"];a=r["chosen_action"];y=r["returned_front"]
            p=(model.predict(r) if name.endswith("beta") else model.predict(s,a))
            if not 0<p<1:
                raise ValueError("C34_ILLEGAL_OR_UNCERTAIN_PROBABILITY")
            overall.append((p,y))
            family.setdefault(r["family"],[]).append((p,y))
            action.setdefault(str(a),[]).append((p,y))
        per_model[name]={"all":sample_metrics(overall),
           "by_original_source_family":{k:sample_metrics(v) for k,v in sorted(family.items())},
           "by_actual_selected_action":{k:sample_metrics(v) for k,v in sorted(action.items())},
           "trained_on_original_source_selected_events":model.updates}
    if sum(len(x) for x in episodes.values())!=805:
        raise ValueError("C34_ACTUAL_SELECTED_SOURCE_FIT_LOSS")
    support=sequence_support(episodes,records)
    for n in arm:
        if per_model[n]["all"]["n"]!=len(check):
            raise ValueError("C34_MISMATCHED_CONVENTIONAL_INFORMATION")
    exact=per_model
    history=exact["prior_action_belief_beta"]["all"]["brier"]
    current=exact["current_cue_beta"]["all"]["brier"]
    native=exact["native_original_local_cells"]["all"]["brier"]
    full=exact["full_nine_public_logistic"]["all"]["brier"]
    shuffle=exact["prior_history_shuffled_beta"]["all"]["brier"]
    if history<min(current,native,full,shuffle):
        decision="FIT_INTERNAL_HISTORY_PREDICTIVE_SIGNAL_VS_ALL_LISTED_CONTROLS_NOT_SCIENCE_GO"
    elif history<current and history<shuffle:
        decision="FIT_INTERNAL_HISTORY_SIGNAL_VS_CURRENT_AND_SHUFFLED_BUT_NOT_STRONG_FULL_PUBLIC_CONTROL"
    else:
        decision="NO_GO_FIT_INTERNAL_PRIOR_ACTION_HISTORY_NOT_USEFUL_AGAINST_CONTROLS"
    cold={name:cold_history_parity(arm[name],check)
          for name in ("current_cue_beta","prior_action_belief_beta","prior_history_shuffled_beta")}
    original_r3_stopped=True
    return {
      "schema":P["schema"],"classification":P["classification"],
      "immutable_original_farama_source":source["original_source"],
      "source_C28_original_two_producer_ledger_sha256":source["source_fit_event_ledger_sha256"],
      "frozen_original_selected_action_events":len(original),
      "source_FIT_training_only_events":len(training),
      "source_internal_FIT_check_only_events":len(check),
      "genuine_chronological_public_multi_step_support":support,
      "fitted_full_public_native_and_conventional_controls":per_model,
      "cold_restored_exact_public_history_checkpoint_bytes":cold,
      "source_public_history_brier_vs_current_cue":round(history-current,9),
      "source_public_history_brier_vs_full9_conventional":round(history-full,9),
      "fit_internal_history_identifiability":decision,
      "prior_C31_C32_myopic_alternative_turn_controller_still_STOPPED":original_r3_stopped,
      "selected_action_counterfactuals_or_goal_policy_effect":"UNIDENTIFIED_NOT_EXECUTED",
      "statistical_significance_or_unfamiliar_family_transfer":"NOT_DEMONSTRATED_CORRELATED_FIT_ONLY",
      "new_external_MiniGrid_environment_actions":0,
      "new_dev_valid_or_protected_episodes":0,
      "FORGE_FSA_first_use":"DENIED"
    }


def main():
    pa=argparse.ArgumentParser()
    pa.add_argument("--authentic-original-fit-dir",type=Path,required=True)
    pa.add_argument("--output",type=Path,required=True)
    ar=pa.parse_args()
    if ar.output.exists() or not ar.output.parent.is_dir():
        raise ValueError("C34_OUTPUT_ALREADY_EXISTS")
    r=audit(ar.authentic_original_fit_dir)
    blob=canonical(r)
    ar.output.write_bytes(blob+b"\n")
    z=r["fitted_full_public_native_and_conventional_controls"]
    print("C34_ORIGINAL_C28_TWICE_RECONCILED_SELECTED_ACTIONS=805_PASS",flush=True)
    print("C34_REAL_PUBLIC_MULTI_STEP_SUPPORT="+json.dumps(r["genuine_chronological_public_multi_step_support"],sort_keys=True),flush=True)
    print("C34_INTERNAL_FIT_HISTORY_AND_STRONG_CONVENTIONAL_BRIER="+json.dumps({k:v["all"] for k,v in z.items()},sort_keys=True),flush=True)
    print("C34_SCIENTIFIC_HISTORY_GATE="+r["fit_internal_history_identifiability"],flush=True)
    print("C34_FRESH_PROCESS_BELIEF_MEMORY_ALL_ARMS=PASS",flush=True)
    print("C34_NEW_SOURCE_ACTIONS_PROTECTED_FIRST_USE=ZERO",flush=True)
    print("C34_CANONICAL_REPORT_SHA256="+hashlib.sha256(blob).hexdigest(),flush=True)


if __name__=="__main__":
    main()
