"""O22-W read-only true original matched physical pair action-value audit.

Uses exact authenticated C35 two-process original-world FIT and FIT_CHECK
archives. Every proposed choice's counterfactual *TWO* steps were REALLY
executed by pinned Farama MiniGrid C35 at the SAME authenticated anchor.
New native and conventional policies are NOT executed as full world agents.
"""
from __future__ import annotations
import argparse, hashlib,io,json,os,math
from pathlib import Path
import resource,subprocess,sys,time,zipfile
from collections import defaultdict

from research.optimizer_o22w.pair_models import (
    NativePairCells,FullNineRidgePairs,PAIRS,LEGAL,public,target,
    geometric_pair,select,canonical
)
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
P=json.loads((HERE/"PREREG.json").read_text())
C=P["source_C35"]


def original_c35(source):
    if hashlib.sha256(source).hexdigest()!=C["zip_sha256"]:
        raise ValueError("O22W_C35_ARCHIVE_WRONG")
    z=zipfile.ZipFile(io.BytesIO(source))
    if z.testzip() is not None or set(z.namelist())!={"comparison.json","process-a.json","process-a.log","process-b.json","process-b.log"}:
        raise ValueError("O22W_C35_ARCHIVE_MEMBERS")
    comparison=json.loads(z.read("comparison.json"))
    if comparison.get("science_identical") is not True or comparison.get("science_accepted") is not False:
        raise ValueError("O22W_C35_SCIENCE_CUSTODY")
    a,b=[json.loads(z.read(i)) for i in ("process-a.json","process-b.json")]
    for k,v in a.items():
        if k!="resources" and b[k]!=v:
            raise ValueError("O22W_C35_ORIGINAL_TWO_PROCESS_DRIFT")
    if a["result"]!="NO_C35_TWO_STEP_CAUSAL_SOURCE_EFFECT_PREDICTIVE_ADVANTAGE":
        raise ValueError("O22W_C35_ORIGINAL_NEGATIVE_DRIFT")
    fit=a["source_original_fit_real_two_action_forks"]
    check=a["source_independent_internal_fit_check_real_forks"]
    if (len(fit)!=C["fit_matched_anchors"] or
        len(check)!=C["fit_check_matched_anchors"] or
        a["FIT_source_original_fitted_intervention_pairs"]!=C["fit_physically_selected_pairs"] or
        a["new_protected_or_unknown_source_episodes"]!=0):
        raise ValueError("O22W_C35_ROLE_OR_PAIR_COUNT_DRIFT")
    seen=set()
    for phase,anchors in (("FIT",fit),("FIT_CHECK_ALREADY_EXPOSED",check)):
        for row in anchors:
            fam=row["family"]
            key=(fam,row["seed"],row["tick"])
            if key in seen or fam not in P["source_C35_families"]:
                raise ValueError("O22W_ORIGINAL_ANCHOR_OR_FAMILY")
            seen.add(key)
            s=row["public_initial"];public(s)
            for field in ("initial_source_sha256","anchor_source_sha256"):
                if type(row[field]) is not str or len(row[field])!=64:
                    raise ValueError("O22W_MISSING_REAL_SOURCE_GRID_PIN")
            branches=row["all_nine_original_physical_pairs"]
            if set(branches)!=set(PAIRS):
                raise ValueError("O22W_ALL_PHYSICAL_ALTERNATIVES_REQUIRED")
            for pair,r in branches.items():
                acts=r["actual_selected_source_actions"]
                if (type(acts) is not list or len(acts)!=2 or
                    [q["action"] for q in acts]!=[int(pair[0]),int(pair[1])] or
                    r["pair"]!=[int(pair[0]),int(pair[1])] or
                    r["completed_two_original_actions"] is not True or
                    r["physical_trace_sha256"]!=hashlib.sha256(canonical(acts)).hexdigest()
                    or acts[0]["before"]!=s or acts[1]["before"]!=acts[0]["after"] or
                    r["actually_observed_next_front_blocked"]!=acts[-1]["after"]["front_blocked"] or
                    any(type(q["reward"]) not in (float,int) or
                        type(q["term"]) is not bool or type(q["trunc"]) is not bool
                        for q in acts) or acts[0]["term"] or acts[0]["trunc"]):
                    raise ValueError("O22W_C35_ORIGINAL_PHYSICALLY_SELECTED_PAIR_INVALID")
                if (abs(sum(q["reward"] for q in acts)-r["actual_source_reward_sum"])>1e-9 or
                    r["real_two_step_goal_distance_improvement"]!=
                    (abs(s["x"]-s["goal_x"])+abs(s["y"]-s["goal_y"])-
                     abs(acts[-1]["after"]["x"]-s["goal_x"])-
                     abs(acts[-1]["after"]["y"]-s["goal_y"]))):
                    raise ValueError("O22W_C35_TRUE_SOURCE_RETURN_MISMATCH")
    return fit,check,{"source_result":a["result"],"two_process_science_identical":True,
       "FIT_anchors":len(fit),"FIT_CHECK_previously_exposed_anchors":len(check)}


def observed(row,pair):
    r=row["all_nine_original_physical_pairs"][pair]
    return {"progress":max(-1.,min(1.,r["real_two_step_goal_distance_improvement"]/2.)),
            "blocked":r["actually_observed_next_front_blocked"]}

def train_pair(model,fit,shuffle=False):
    start=time.process_time()
    for anchor in fit:
        state=anchor["public_initial"]
        for pair in PAIRS:
            # True original physics RETURN always belongs to this actually
            # executed physical pair, even in deliberately SHUFFLED negative.
            applied=(str(1-int(pair[0]))+pair[1]) if shuffle and pair[0] in "01" else pair
            model.learn(state,applied,observed(anchor,pair))
    if isinstance(model,FullNineRidgePairs):model.finalize()
    if model.n!=C["fit_physically_selected_pairs"] or any(v!=len(fit) for v in model.counts.values()):
        raise ValueError("O22W_EQUAL_SOURCE_PAIR_TRAINING_DRIFT")
    return round(time.process_time()-start,8)

def simple_fit_pair_mean(fit):
    totals={pair:0.0 for pair in PAIRS}
    for row in fit:
        for pair in PAIRS:totals[pair]+=observed(row,pair)["progress"]
    return max(LEGAL,key=lambda p:(totals[p],-int(p)))

def scored(check,models,fixed_pair):
    scores={}
    for name,model in models.items():
        by=defaultdict(lambda:{"n":0,"sum":0.,"front":0.})
        choices=defaultdict(lambda:{"n":0,"regret":0.,"real_progress":0.,
             "better_than_fixed22":0,"equal_oracle":0,"unsafe_unrestricted_inverse":0})
        for row in check:
            state=row["public_initial"];fam=row["family"]
            for p in PAIRS:
                obs=observed(row,p)
                pred=model.predict(state,p)
                if not(-1<=pred[0]<=1 and 0<=pred[1]<=1):
                    raise ValueError("O22W_PAIR_PREDICTION_RANGE")
                e=(pred[0]-obs["progress"])**2
                b=(pred[1]-float(obs["blocked"]))**2
                for key in ("all",fam,fam+"|"+p):
                    bucket=by[key];bucket["n"]+=1;bucket["sum"]+=e;bucket["front"]+=b
            chosen=select(model,state)
            unrestricted=select(model,state,PAIRS)
            truths={p:observed(row,p)["progress"] for p in LEGAL}
            true_progress=truths[chosen]
            oracle=max(truths.values())
            for key in ("all",fam):
                bucket=choices[key];bucket["n"]+=1
                bucket["regret"]+=oracle-true_progress
                bucket["real_progress"]+=true_progress
                bucket["better_than_fixed22"]+=int(true_progress>truths["22"])
                bucket["equal_oracle"]+=int(true_progress==oracle)
                bucket["unsafe_unrestricted_inverse"]+=int(unrestricted not in LEGAL)
        scores[name]={
          "per_family_and_original_physically_selected_action_pair":{
             key:{"n":v["n"],"progress_MSE":round(v["sum"]/v["n"],9),
                  "front_Brier":round(v["front"]/v["n"],9)}
             for key,v in by.items()},
          "matched_source_actually_executed_two_step_policy_choices":{
             key:{"anchors":v["n"],"mean_true_real_progress":round(v["real_progress"]/v["n"],9),
                  "mean_oracle_regret":round(v["regret"]/v["n"],9),
                  "strict_better_than_fixed_22":v["better_than_fixed22"],
                  "oracle_equal_count":v["equal_oracle"],
                  "unrestricted_inverse_turn_pair_proposals":v["unsafe_unrestricted_inverse"]}
             for key,v in choices.items()}
        }
    direct={}
    for name,chooser in (("fixed_forward22",lambda state:"22"),
                         ("source_public_optimistic_geometry",geometric_pair),
                         ("fitted_source_pair_mean",lambda state:fixed_pair)):
        d=defaultdict(lambda:{"n":0,"regret":0.,"progress":0.})
        for row in check:
            s=row["public_initial"];fam=row["family"];picked=chooser(s)
            real={p:observed(row,p)["progress"] for p in LEGAL}
            for key in ("all",fam):
                v=d[key];v["n"]+=1;v["regret"]+=max(real.values())-real[picked]
                v["progress"]+=real[picked]
        direct[name]={key:{"anchors":v["n"],"mean_true_real_progress":round(v["progress"]/v["n"],9),
                           "mean_oracle_regret":round(v["regret"]/v["n"],9)}
                      for key,v in d.items()}
    return scores,direct

def cold(model,s):
    cp=model.checkpoint()
    same=type(model).restore(cp)
    if same.checkpoint()!=cp or any(same.predict(s,p)!=model.predict(s,p) for p in PAIRS):
        raise ValueError("O22W_COLD_LOCAL_MODEL_MISMATCH")
    code=("import sys,json;"
        "from research.optimizer_o22w.pair_models import NativePairCells,FullNineRidgePairs,PAIRS,select;"
        "d=json.loads(sys.stdin.buffer.read());"
        "m=globals()[d['model']].restore(d['checkpoint'].encode());"
        "print(json.dumps({'n':m.n,'predict':[m.predict(d['state'],p) for p in PAIRS],"
        "'chosen':select(m,d['state'])}))")
    payload=canonical({"model":type(model).__name__,"checkpoint":cp.decode(),"state":s})
    env=dict(os.environ,PYTHONPATH=str(ROOT),PYTHONDONTWRITEBYTECODE="1")
    child=subprocess.run([sys.executable,"-B","-c",code],input=payload,
            capture_output=True,timeout=20,cwd=ROOT,env=env)
    if child.returncode:raise ValueError(child.stderr.decode())
    got=json.loads(child.stdout)
    if got!={"n":model.n,"predict":[list(model.predict(s,p)) for p in PAIRS],
             "chosen":select(model,s)}:
        raise ValueError("O22W_COLD_FRESH_PROCESS_ACTION_DRIFT")
    return len(cp)

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--source-zip",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True);arg=ap.parse_args()
    fit,check,custody=original_c35(arg.source_zip.read_bytes())
    model={"native_R1_local_cells":NativePairCells(),
           "independent_full9_pair_ridge":FullNineRidgePairs(),
           "shuffled_action_native_negative":NativePairCells()}
    cpu={name:train_pair(m,fit,name=="shuffled_action_native_negative")
         for name,m in model.items()}
    sizes={name:cold(m,check[0]["public_initial"]) for name,m in model.items()}
    fixed=simple_fit_pair_mean(fit)
    scores,simple=scored(check,model,fixed)
    native=scores["native_R1_local_cells"]
    ridge=scores["independent_full9_pair_ridge"]
    dynamic="MiniGrid-Dynamic-Obstacles-8x8-v0"
    static="MiniGrid-FourRooms-v0"
    true_native=native["matched_source_actually_executed_two_step_policy_choices"]
    true_ridge=ridge["matched_source_actually_executed_two_step_policy_choices"]
    mse_native=native["per_family_and_original_physically_selected_action_pair"]
    mse_ridge=ridge["per_family_and_original_physically_selected_action_pair"]
    dominates=(all(true_native[f]["mean_oracle_regret"]<true_ridge[f]["mean_oracle_regret"]
                   and mse_native[f]["progress_MSE"]<mse_ridge[f]["progress_MSE"]
                   for f in (dynamic,static)))
    verdict=("INTERNAL_FIT_ONLY_NATIVE_CAUSAL_PAIR_SELECTION_SIGNAL_UNCONFIRMED"
             if dominates else "NO_GO_NATIVE_MATCHED_TWO_ACTION_VALUE_VS_FULL9_CONVENTIONAL")
    result={
       "schema":P["schema"],"source_C35_original_run":C["original_run"],
       "source_C35_archived_zip_sha256":C["zip_sha256"],
       "verified_original_source":custody,
       "FIT_original_source_actual_pairs_fit":len(fit)*len(PAIRS),
       "FIT_CHECK_ALREADY_PUBLIC_real_matched_pair_outcomes":len(check)*len(PAIRS),
       "no_original_source_new_FIT_DEV_protected_steps":True,
       "learned_equal_source_FIT_model_counts":{name:m.n for name,m in model.items()},
       "family_and_pair_predictive_accuracy_and_actual_matched_action_regret":scores,
       "nonlearned_public_action_comparators":simple,
       "full_fresh_python_cold_checkpoint_bytes":sizes,
       "model_fit_CPU_seconds":cpu,
       "process_peak_RSS_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
       "previously_exposed_FIT_CHECK_cannot_be_called_blind":True,
       "learned_native_R3_integration":False,
       "physically_executed_entire_policy_episodes":False,
       "all_alternative_two_step_outcomes_were_original_physically_executed":True,
       "unfamiliar_world_and_protected_first_use":"NOT_PERFORMED",
       "scientific_gate":verdict
    }
    arg.out.write_bytes(canonical(result)+b"\n")
    print("O22W_ORIGINAL_REAL_TWO_STEP_MATCHED_SOURCE_AUTHENTICATED=PASS",flush=True)
    print("O22W_REAL_FIT_INTERVENTION_PAIRS="+str(len(fit)*9),flush=True)
    print("O22W_PREVIOUSLY_EXPOSED_FIT_CHECK_INTERVENTION_PAIRS="+str(len(check)*9),flush=True)
    for name,d in scores.items():
        print("O22W_"+name.upper()+"_PROGRESS_MSE="+
              str(d["per_family_and_original_physically_selected_action_pair"]["all"]["progress_MSE"]),flush=True)
        print("O22W_"+name.upper()+"_TRUE_MATCHED_ACTION_REGRET="+
              str(d["matched_source_actually_executed_two_step_policy_choices"]["all"]["mean_oracle_regret"]),flush=True)
    print("O22W_ALL_NATIVE_CONVENTIONAL_COLD_EXACT=PASS",flush=True)
    print("O22W_FIT_CHECK_PREVIOUSLY_EXPOSED=TRUE",flush=True)
    print("O22W_SCIENTIFIC_GATE="+verdict,flush=True)

if __name__=="__main__":main()
