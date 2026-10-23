#!/usr/bin/env python3
"""CS14: real original Causal-Gymnasium MDP actions into new action-owned R7 cells.

PUBLIC DEVELOPMENT source, not sealed unfamiliar scientific first use.
"""
from __future__ import annotations
import argparse
import hashlib
import inspect
import json
from pathlib import Path
import resource
import subprocess
import sys
import time

from run_cs02_public_mdp_learning import (
    FittedLogistic,TabularRewards,BlindRewards,
    source_episode,pinned_source,bit,canon,sha,need
)
from isolated_original_mdp_import import original_mdp_classes
from cs14_action_owned_native_cells import (
    ActionOwnedNativeCells,LocalCell,ORIGINAL_LOCAL_CELL_SOURCE_GIT_BLOB
)

FIRST="8e6f13e1c2dc8b86017eda62e17ab727dd9baab5"
REPS=(0,1,2)
FIT_N,VALID_N,DEV_N,HORIZON=192,48,128,30
ARMS=("native_action_owned_R7_LocalCells",
      "trained_contextual_tabular_reward",
      "trained_contextual_logistic_reward",
      "trained_context_blind_reward",
      "native_action_permuted",
      "native_cold_untrained",
      "original_source_known_oracle")
def seed(role,rep,i):
    return {"FIT":3100000,"VALID":3200000,"DEV":3300000}[role]+10000*rep+i
def enforce_original_r7():
    filename=Path(inspect.getfile(LocalCell)).resolve()
    expected=Path(__file__).resolve().parents[1]/"r7"/"native_cells.py"
    need(filename==expected.resolve(),"CS14_ACTUAL_LOCALCELL_SOURCE_NOT_YGG_R7")
    p=subprocess.run(["git","hash-object",str(filename)],text=True,capture_output=True,
                     cwd=Path(__file__).resolve().parents[4],timeout=30)
    need(p.returncode==0 and p.stdout.strip()==ORIGINAL_LOCAL_CELL_SOURCE_GIT_BLOB,
         "CS14_LOCALCELL_ORIGINAL_GIT_BLOB_DRIFT")
    return {"source_original_native_file":str(filename.relative_to(
                Path(__file__).resolve().parents[4])),
            "original_Git_blob":ORIGINAL_LOCAL_CELL_SOURCE_GIT_BLOB}
class Explore:
    def __init__(self,i):
        self.i=i;self.t=0
    def choose(self,s):
        bit(s)
        a=(self.t+self.i)%2;self.t+=1
        return a
class ActionPermuted:
    def __init__(self,native):self.native=native
    def choose(self,s):return 1-self.native.choose(bit(s))
    def state(self):return {"kind":"frozen_native_action_address_inverted",
                             "original_fitted_model_SHA":hashlib.sha256(
                                 self.native.checkpoint()).hexdigest()}
class Cold:
    def __init__(self):self.model=ActionOwnedNativeCells()
    def choose(self,s):return self.model.choose(bit(s))
    def state(self):return {"kind":"frozen_original_native_action_cells_no_FIT",
                             "checkpoint_sha":hashlib.sha256(
                                 self.model.checkpoint()).hexdigest()}
class Oracle:
    def choose(self,s):return bit(s)
    def state(self):return {"kind":"original_source_CS01_oracle_public_state_feedback",
                             "privileged_original_published_source_law":True}
def train_original(fit):
    begin=time.process_time_ns()
    native=ActionOwnedNativeCells()
    for s,a,y,ns,final in fit:
        native.learn_completed_public_consequence(s,a,y,ns,2)
    native_fit_ns=time.process_time_ns()-begin
    original_bytes=native.checkpoint()
    need(len(original_bytes)<=32768 and
         native.completed_feedback_updates==len(fit),
         "CS14_ACTUAL_NATIVE_FIT_ACTION_CONSEQUENCES_INCOMPLETE")
    cold=ActionOwnedNativeCells.restore(original_bytes)
    need(cold.checkpoint()==original_bytes,
         "CS14_REAL_NATIVE_COLD_CHECKPOINT_NOT_BYTE_IDENTICAL")
    for s in (0,1):
        for a in (0,1):
            need(native.predict_reward(s,a)==cold.predict_reward(s,a) and
                 native.predict_next(s,a)==cold.predict_next(s,a),
                 "CS14_NATIVE_COLD_REWARD_OR_TRANSITION_PREDICTION_DRIFT")
        need(native.choose(s)==cold.choose(s),
             "CS14_NATIVE_COLD_SOURCE_ACTION_POLICY_CHANGED")
    table=TabularRewards();t=time.process_time_ns();table.fit(fit)
    table_fit=time.process_time_ns()-t
    log=FittedLogistic();t=time.process_time_ns();log.fit(fit)
    log_fit=time.process_time_ns()-t
    blind=BlindRewards();t=time.process_time_ns();blind.fit(fit)
    blind_fit=time.process_time_ns()-t
    models={ARMS[0]:cold,ARMS[1]:table,ARMS[2]:log,ARMS[3]:blind,
            ARMS[4]:ActionPermuted(cold),ARMS[5]:Cold(),ARMS[6]:Oracle()}
    owned={(s,a):native.buckets[(s,a)]["count"] for s in (0,1) for a in (0,1)}
    support={(s,a):sum(int(z[0]==s and z[1]==a) for z in fit)
             for s in (0,1) for a in (0,1)}
    need(owned==support and all(c>=100 for c in support.values()),
         "CS14_EACH_ACTUAL_SOURCE_STATE_ACTION_FIT_SUPPORT_INVALID")
    for s in (0,1):
        for a in (0,1):
            cell=cold.buckets[(s,a)]
            need(cell["reward"].updates==support[(s,a)] and
                 cell["next_state"].updates==support[(s,a)],
                 "CS14_NATIVE_BOTH_CONSEQUENCE_CHANNELS_NOT_UPDATED")
    receipt={"original_FIT_source_transition_count":len(fit),
             "source_original_fitted_state_action_visits":{
                 str(s)+":"+str(a):support[(s,a)] for s in (0,1) for a in (0,1)},
             "native_actual_cold_checkpoint_bytes":len(original_bytes),
             "native_actual_cold_checkpoint_SHA256":hashlib.sha256(original_bytes).hexdigest(),
             "native_genuine_completed_action_feedback":cold.completed_feedback_updates,
             "native_reward_and_transition_cells_updated_exactly_once_per_real_action":True,
             "real_native_fit_cpu_ns":native_fit_ns,
             "conventional_fitted_train_CPU_ns":{
                 ARMS[1]:table_fit,ARMS[2]:log_fit,ARMS[3]:blind_fit},
             "serialized_model_states":{
                 name:{"size_bytes":len(canon(m.state()).encode()),
                       "source_free_state_SHA256":sha(m.state())}
                 for name,m in models.items()},
             "learned_genuine_source_policy_by_original_public_state":{
                 name:[models[name].choose(0),models[name].choose(1)]
                 for name in ARMS},
             "real_native_transition_probabilities_by_state_action":{
                 str(s)+":"+str(a):cold.predict_next(s,a)
                 for s in (0,1) for a in (0,1)},
             "real_native_reward_probabilities_by_state_action":{
                 str(s)+":"+str(a):cold.predict_reward(s,a)
                 for s in (0,1) for a in (0,1)},
    }
    return models,receipt
def check_original_source_episode(Source,original_seed,policy):
    raw=source_episode(Source,original_seed,policy)
    need(len(raw)==HORIZON and all(z[0] in (0,1) and z[1] in (0,1) and
         z[2] in (0,1) and z[3] in (0,1) for z in raw),
         "CS14_REAL_ORIGINAL_SOURCE_ACTION_RETURNS_INVALID")
    return raw
def score_role(Source,role,rep,models):
    n=VALID_N if role=="VALID" else DEV_N
    frozen={name:sha(m.state()) for name,m in models.items()}
    result={}
    for name in ARMS:
        evidence=[]
        cpu=0
        for i in range(n):
            st=time.process_time_ns()
            original=check_original_source_episode(Source,seed(role,rep,i),models[name])
            elapsed=time.process_time_ns()-st
            cpu+=elapsed
            evidence.append({"original_source_episode_seed":seed(role,rep,i),
                             "original_30_step_source_native_S_action_Y_nextS":original})
        rows=[tuple(step) for ep in evidence for step in
              ep["original_30_step_source_native_S_action_Y_nextS"]]
        observed_reward=sum(r[2] for r in rows)
        n_actions=len(rows)
        need(len(evidence)==n and n_actions==n*HORIZON,"CS14_ROLE_OBSERVED_ACTION_BUDGET_INVALID")
        item={"episodes":n,"source_owned_real_actions":n_actions,
              "total_original_source_reward":observed_reward,
              "original_source_reward_per_decision":observed_reward/n_actions,
              "original_source_mean_30_step_reward":observed_reward/n,
              "original_source_plus_policy_CPU_ns":cpu,
              "original_public_development_trace_SHA256":sha(evidence),
              "original_source_public_episode_traces":evidence,
              "actual_original_source_action_by_state":[
                  [sum(int(s==ss and a==aa) for s,a,y,ns,last in rows)
                   for aa in (0,1)] for ss in (0,1)]}
        if name==ARMS[0]:
            model=models[name];tab=models[ARMS[1]]
            n_brier=sum((model.predict_next(s,a)-ns)**2
                        for s,a,y,ns,last in rows)/n_actions
            # Report only genuinely FIT-native next-state predictions.
            # The prior CS02 tabular comparator was trained on rewards, not
            # source transitions; do not mislabel it a transition estimator.
            item["native_real_next_state_Brier_score"]=n_brier
            item["public_next_state_uninformative_half_Brier"]=.25
        result[name]=item
    need(frozen=={name:sha(m.state()) for name,m in models.items()},
         "CS14_SCIENCE_ROLE_FITTED_MODEL_MUTATED")
    return result
def main():
    p=argparse.ArgumentParser();p.add_argument("--upstream",required=True)
    p.add_argument("--out",required=True);args=p.parse_args()
    root=Path(args.upstream).resolve();out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    receipt={"schema":"mass.cs14.action_owned_genuine_ygg_r7_localcells_source_MDP.v1",
             "frozen_FIRST_prereg":FIRST,"source_role":"PUBLIC_ORIGINAL_CAUSALGYM_DEV_ONLY",
             "native_R7_Colony_original_source_edited":False,
             "new_action_owned_wrapper_is_original_R7_Colony":False,
             "full_action_and_next_state_consequence_native_model":True,
             "independent_unfamiliar_original_source_family":False,
             "partially_observed_persistent_memory_required":False,
             "scientific_CKB_plane_admission":False,
             "protected_source_first_use":False,
             "model_isolated_resource_nonregression":False,
             "disposition":"PUBLIC_CS14_ORIGINAL_SOURCE_OR_NATIVE_PROTOCOL_INVALID",
             "replicas":[]}
    histories={"schema":"mass.cs14.original_MDP_shared_public_FIT.v1","replicas":[]}
    t0=time.process_time_ns()
    try:
        receipt["original_external_git_source_identity"]=pinned_source(root)
        receipt["original_Ygg_native_local_cell_identity"]=enforce_original_r7()
        MDPSCM,Source=original_mdp_classes(root)
        need(MDPSCM.__name__=="MDPSCM" and Source.__name__=="MDPPCH",
             "CS14_WRONG_ORIGINAL_SOURCE_CLASSES")
        all_valid_traces=[]
        for rep in REPS:
            start=time.process_time_ns()
            fit=[]
            for i in range(FIT_N):
                fit.extend(check_original_source_episode(Source,seed("FIT",rep,i),Explore(i)))
            source_fit_cpu=time.process_time_ns()-start
            need(len(fit)==FIT_N*HORIZON and
                 all(a==(i+t)%2 for i in range(FIT_N)
                     for t,(s,a,y,ns,last) in enumerate(
                         fit[i*HORIZON:(i+1)*HORIZON])),
                 "CS14_ORIGINAL_SOURCE_FIT_ACTION_EXPLORATION_CHANGED")
            histories["replicas"].append({"replica":rep,"real_original_source_FIT_rows":fit})
            models,training=train_original(fit)
            before={name:sha(m.state()) for name,m in models.items()}
            valid=score_role(Source,"VALID",rep,models)
            dev=score_role(Source,"DEV",rep,models)
            need(before=={name:sha(m.state()) for name,m in models.items()},
                 "CS14_ORIGINAL_SOURCE_DEV_CHANGED_FITTED_NATIVE_MODEL")
            r=lambda k:dev[k]["original_source_reward_per_decision"]
            best=max(r(ARMS[1]),r(ARMS[2]))
            native=r(ARMS[0])
            brier=dev[ARMS[0]]["native_real_next_state_Brier_score"]
            yes=(native-r(ARMS[3])>=.15 and native-r(ARMS[5])>=.15
                 and native-r(ARMS[4])>=.25
                 and native>=best-.03 and native>=r(ARMS[6])-.05
                 and brier<.25)
            receipt["replicas"].append({
                 "replica":rep,"fit_original_source_episodes":FIT_N,
                 "fit_original_source_action_count":len(fit),
                 "original_source_FIT_CPU_ns":source_fit_cpu,
                 "shared_original_source_FIT_transcript_SHA256":sha(fit),
                 "native_and_conventional_FIT_receipts":training,
                 "valid":valid,"dev":dev,
                 "native_DEV_minus_blind":native-r(ARMS[3]),
                 "native_DEV_minus_cold":native-r(ARMS[5]),
                 "native_DEV_minus_permuted":native-r(ARMS[4]),
                 "native_DEV_minus_best_trained_contextual":native-best,
                 "native_DEV_minus_privileged_source_oracle":native-r(ARMS[6]),
                 "native_real_original_next_state_Brier":brier,
                 "prospective_native_source_consequence_gate_passed":yes})
            print("CS14_REPLICA="+str(rep)+" ORIGINAL_DEV_SOURCE_REWARDS="+
                  canon({name:round(r(name),5) for name in ARMS})+
                  " ACTUAL_NATIVE_NEXT_STATE_BRIER="+str(round(brier,5)),flush=True)
        receipt["original_source_FIT_episodes"]=len(REPS)*FIT_N
        receipt["original_source_VALID_episodes"]=len(REPS)*len(ARMS)*VALID_N
        receipt["original_source_DEV_episodes"]=len(REPS)*len(ARMS)*DEV_N
        receipt["all_original_source_reset_episode_calls"]=sum(
            receipt[k] for k in ("original_source_FIT_episodes",
                                 "original_source_VALID_episodes",
                                 "original_source_DEV_episodes"))
        receipt["all_original_source_native_action_calls"]=receipt[
            "all_original_source_reset_episode_calls"]*HORIZON
        need(receipt["all_original_source_native_action_calls"]==128160 and
             receipt["all_original_source_reset_episode_calls"]==4272,
             "CS14_FROZEN_ORIGINAL_SOURCE_EPISODE_COUNTS_DRIFT")
        receipt["all_original_FIT_history_SHA256"]=sha(histories)
        receipt["disposition"]=(
            "PUBLIC_CS14_NATIVE_MULTIACTION_SOURCE_CONSEQUENCE_SUPPORTED_NOT_TRANSFER"
            if all(x["prospective_native_source_consequence_gate_passed"]
                   for x in receipt["replicas"])
            else "PUBLIC_CS14_ACTION_OWNED_NATIVE_NO_ADVANTAGE")
        receipt["native_vs_conventional_superiority"]="NOT_ESTABLISHED_UNLESS_OUTPERFORMED_MATCHED_CONTROLS"
        receipt["native_novel_source_family_transfer"]="NOT_TESTED_ORIGINAL_SOURCE_PUBLICLY_INSPECTED"
    except Exception as exc:
        receipt["first_failure"]=type(exc).__name__+":"+str(exc)[:1000]
    finally:
        receipt["full_CPU_ns_including_source_native_and_models"]=time.process_time_ns()-t0
        receipt["process_inclusive_peak_RSS_KiB"]=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        (out/"cs14-original-MDP-action-owned-receipt.json").write_text(
            json.dumps(receipt,sort_keys=True,indent=2)+"\n")
        (out/"cs14-original-MDP-public-FIT.json").write_text(canon(histories)+"\n")
    print("CS14_DISPOSITION="+receipt["disposition"],flush=True)
    return 2 if receipt["disposition"]=="PUBLIC_CS14_ORIGINAL_SOURCE_OR_NATIVE_PROTOCOL_INVALID" else 0
if __name__=="__main__":
    sys.exit(main())
