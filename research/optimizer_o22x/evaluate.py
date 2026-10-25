"""O22-X — authentic physically executed C35 pair transitions used as a
READ-ONLY source to evaluate TWO-step learned belief composition.

No new MiniGrid reset/step, no protected first-use, no actual intermediate
returned world state supplied to model rollout. Original C35 FIT_CHECK exposed.
"""
from __future__ import annotations
import argparse,hashlib,json,os,resource,subprocess,sys,time
from collections import defaultdict
from pathlib import Path
from research.native.itd02.r1.native_policy import canonical
from research.optimizer_o22w.evaluate import original_c35,observed
from research.optimizer_o22x.transition_belief import (
    NativeCausalCells,ConventionalNineRidge,
    ACTIONS,PAIRS,SAFE,two_step_belief,choose,check_transition
)

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
P=json.loads((HERE/"PREREG.json").read_text())
SOURCE=P["original_C35_actions"]

def train(model,anchors,action_shift=False):
    start=time.process_time()
    for anchor in anchors:
        for pair in PAIRS:
            branch=anchor["all_nine_original_physical_pairs"][pair]
            for e in branch["actual_selected_source_actions"]:
                a=e["action"]
                if action_shift and a in (0,1):
                    a=1-a
                # Label-shuffled negative only, not source physics proof.
                if action_shift:
                    b=dict(e["before"]);aft=dict(e["after"])
                    # A shuffled legal TURN must have a correspondingly
                    # consistent public heading to retain grammar.
                    if e["action"] in (0,1):
                        aft["direction"]=(b["direction"]-1)%4 if a==0 else (b["direction"]+1)%4
                    model.learn(b,a,aft)
                else:
                    model.learn(e["before"],a,e["after"])
    if isinstance(model,ConventionalNineRidge):model.finalize()
    total=len(anchors)*len(PAIRS)*2
    if model.events!=total or any(n!=total//3 for n in model.action_counts.values()):
        raise ValueError("O22X_SOURCE_TRAIN_COUNT_DRIFT")
    return round(time.process_time()-start,8)

def scores(anchors,models):
    results={}
    fams=("MiniGrid-FourRooms-v0","MiniGrid-Dynamic-Obstacles-8x8-v0")
    for name,model in models.items():
        preds=defaultdict(lambda:{"n":0,"progress":0.,"front":0.})
        decisions=defaultdict(lambda:{"n":0,"true_progress":0.,"regret":0.,"oracle_equal":0,
                   "beat_forward22":0,"unsafe_unrestricted_pairs":0})
        for anchor in anchors:
            s=anchor["public_initial"];fam=anchor["family"]
            truth={p:observed(anchor,p) for p in PAIRS}
            for pair in PAIRS:
                expected=two_step_belief(model,s,pair)
                actual=truth[pair]
                for key in ("all",fam,fam+"|"+pair):
                    ref=preds[key];ref["n"]+=1
                    ref["progress"]+=(expected[0]-actual["progress"])**2
                    ref["front"]+=(expected[1]-float(actual["blocked"]))**2
            choice=choose(model,s)
            unrestricted=choose(model,s,PAIRS)
            legal={p:truth[p]["progress"] for p in SAFE}
            value=legal[choice];best=max(legal.values())
            for key in ("all",fam):
                d=decisions[key];d["n"]+=1
                d["true_progress"]+=value
                d["regret"]+=best-value
                d["oracle_equal"]+=int(value==best)
                d["beat_forward22"]+=int(value>legal["22"])
                d["unsafe_unrestricted_pairs"]+=int(unrestricted not in SAFE)
        results[name]={
          "public_consequence_forecast":{
            k:{"source_physical_pairs":v["n"],
               "progress_MSE":round(v["progress"]/v["n"],9),
               "next_front_Brier":round(v["front"]/v["n"],9)}
               for k,v in preds.items()},
          "source_matched_realized_two_step_choices":{
            k:{"source_anchors":v["n"],
               "mean_real_physical_progress":round(v["true_progress"]/v["n"],9),
               "mean_oracle_regret":round(v["regret"]/v["n"],9),
               "oracle_equal_anchors":v["oracle_equal"],
               "strictly_better_than_forward22_anchors":v["beat_forward22"],
               "unrestricted_inverse_pair_suggestions":v["unsafe_unrestricted_pairs"]}
            for k,v in decisions.items()}
        }
    simple={}
    for fam in ("all",)+fams:
        rows=[r for r in anchors if fam=="all" or r["family"]==fam]
        regrets=[];val=[]
        for r in rows:
            possible={p:observed(r,p)["progress"] for p in SAFE}
            regrets.append(max(possible.values())-possible["22"])
            val.append(possible["22"])
        simple[fam]={"source_anchors":len(rows),"fixed_forward22_mean_true_physical_progress":round(sum(val)/len(val),9),
                     "fixed_forward22_mean_oracle_regret":round(sum(regrets)/len(regrets),9)}
    return results,simple

def cold(model,source_before):
    wire=model.checkpoint()
    restored=type(model).restore(wire)
    if restored.checkpoint()!=wire:
        raise ValueError("O22X_LOCALLY_CORRUPT_LEARNED_COLD")
    childscript=(
     "import json,sys;"
     "from research.optimizer_o22x.transition_belief import NativeCausalCells,ConventionalNineRidge,PAIRS,two_step_belief,choose;"
     "d=json.loads(sys.stdin.buffer.read());"
     "m=globals()[d['name']].restore(d['wire'].encode());"
     "print(json.dumps({'n':m.events,'out':[two_step_belief(m,d['before'],p) for p in PAIRS],"
     "'choice':choose(m,d['before'])}))"
    )
    payload=canonical({"name":type(model).__name__,
                       "wire":wire.decode(),"before":source_before})
    result=subprocess.run([sys.executable,"-B","-c",childscript],
             input=payload,capture_output=True,timeout=25,cwd=ROOT,
             env=dict(os.environ,PYTHONPATH=str(ROOT),PYTHONDONTWRITEBYTECODE="1"))
    if result.returncode:
        raise ValueError("O22X_FRESH_PYTHON_COLD_FAIL:"+result.stderr.decode())
    actual=json.loads(result.stdout)
    expected={"n":model.events,
              "out":[list(two_step_belief(model,source_before,p)) for p in PAIRS],
              "choice":choose(model,source_before)}
    if actual!=expected:
        raise ValueError("O22X_FRESH_PYTHON_COLD_COMPOSITION_MISMATCH")
    return len(wire)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-zip",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    if (P["source_Farama"]!="Farama-Foundation/Minigrid@7f5853792ea7f04f75614661006d87fcf949f26d"
       or SOURCE["artifact"]!=12603145885
       or P["governance"]["source_original_new_reset_or_step_count"]!=0):
        raise ValueError("O22X_SOURCE_FIRST_CONTRACT_DRIFT")
    fit,check,record=original_c35(args.source_zip.read_bytes())
    if len(fit)!=SOURCE["FIT_anchor_count"] or len(check)!=SOURCE["FIT_CHECK_already_public_anchor_count"]:
        raise ValueError("O22X_ORIGINAL_C35_ROLE_DRIFT")
    models={"native_original_R1_compositional":NativeCausalCells(),
            "independent_full9_ridge_compositional":ConventionalNineRidge(),
            "native_left_right_action_shuffled_negative":NativeCausalCells(),
            "untrained_original_R1_cells":NativeCausalCells()}
    costs={key:train(m,fit,action_shift=(key=="native_left_right_action_shuffled_negative"))
           for key,m in models.items() if key!="untrained_original_R1_cells"}
    if any(models[x].events!=SOURCE["FIT_anchor_count"]*18
           for x in costs):
        raise ValueError("O22X_EQUAL_SOURCE_SELECTED_FIT_ROWS")
    cold_bytes={key:cold(m,check[0]["public_initial"]) for key,m in models.items()}
    result,simple=scores(check,models)
    native=result["native_original_R1_compositional"]
    ridge=result["independent_full9_ridge_compositional"]
    passed=True
    for family in ("MiniGrid-FourRooms-v0","MiniGrid-Dynamic-Obstacles-8x8-v0"):
        n=native["source_matched_realized_two_step_choices"][family]
        c=ridge["source_matched_realized_two_step_choices"][family]
        p=native["public_consequence_forecast"][family]
        r=ridge["public_consequence_forecast"][family]
        if not (n["mean_oracle_regret"]<c["mean_oracle_regret"] and
                n["mean_oracle_regret"]<simple[family]["fixed_forward22_mean_oracle_regret"]
                and p["next_front_Brier"]<=r["next_front_Brier"]):
            passed=False
    decision=("RETROSPECTIVE_INTERNAL_FIT_SOURCE_BELIEF_SIGNAL_NOT_SCIENTIFIC_FIRST_USE"
              if passed else "NO_GO_COMPOSITIONAL_NATIVE_POLICY_PARETO_VS_STRONG_CONTROLS")
    body={
      "schema":P["schema"],"source_original_C35_run":SOURCE["run"],
      "source_C35_immutable_original_zip_sha256":SOURCE["zip_sha256"],
      "source_original_producer_record":record,
      "actual_physical_original_FIT_action_transition_rows":len(fit)*18,
      "actual_physical_original_FIT_CHECK_action_transition_rows_PREVIOUSLY_EXPOSED":len(check)*18,
      "all_nine_actual_original_source_two_step_branches_per_anchor":True,
      "forecast_rollout_reads_original_first_source_after":False,
      "model_conditioning_only_six_public_fields":True,
      "source_original_step_count_new":0,
      "original_native_R1_R3_untouched":True,
      "source_matched_model_composition":result,
      "simple_baseline_fixed_forward22":simple,
      "full_fresh_os_model_cold_bytes":cold_bytes,
      "source_FIT_training_CPU_seconds":costs,
      "process_peak_RSS_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
      "original_fresh_full_episode_goal_reward":"NOT_TESTED",
      "protected_FSA_83_first_use":"DENIED",
      "scientific_decision":decision
    }
    args.out.write_bytes(canonical(body)+b"\n")
    print("O22X_AUTHENTIC_C35_TWO_PROCESS_NINE_MATCHED_PHYSICAL_PAIRS=PASS")
    print("O22X_EQUAL_SOURCE_FIT_TRANSITIONS="+str(len(fit)*18))
    print("O22X_INTERNAL_FIT_CHECK_PREVIOUSLY_EXPOSED=TRUE")
    for name,r in result.items():
        print("O22X_"+name.upper()+"_PROGRESS_MSE="+str(r["public_consequence_forecast"]["all"]["progress_MSE"]))
        print("O22X_"+name.upper()+"_REAL_PHYSICAL_CHOICE_REGRET="+str(r["source_matched_realized_two_step_choices"]["all"]["mean_oracle_regret"]))
    print("O22X_TRUE_COLD_FULL_COMPOSITIONAL_BELIEF=PASS")
    print("O22X_SCIENTIFIC_GATE="+decision)
    print("O22X_NO_ORIGINAL_WORLD_DEV_PROTECTED_ACTIONS=TRUE")

if __name__=="__main__":main()
