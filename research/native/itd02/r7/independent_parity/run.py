#!/usr/bin/env python3
"""Independent Yggdrasil R7 authored-development first-order causal experiment.

Parent alone knows original historic authored "truth"; subprocess learner
never receives it, its hidden parent triples, a seed, or evaluation labels.
No newly sourced scientific original-world experiment is authorized here.
"""
from __future__ import annotations
import argparse,hashlib,json,pathlib,random,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[5]
sys.path.insert(0,str(ROOT))
from research.native.itd02.r7.test_learner import truth
HERE=pathlib.Path(__file__).resolve().parent
CHILD=HERE/"model_child.py"
PREREG=HERE/"PREREG.json"
ARMS=("native","conventional","nearest")
SEQUENCES=([0],[1],[2],[0,1,2],[2,0,0,1,2])
def need(ok,s):
    if not ok:raise AssertionError("R7_PARITY_FAIL_CLOSED_"+s)
def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":")).encode()
def original_sha(path,expected):
    v=subprocess.run(["git","hash-object",path],cwd=ROOT,check=True,
                     capture_output=True,text=True).stdout.strip()
    need(v==expected,"PINNED_SOURCE_DRIFT_"+path.replace("/","_"))
    return v
def child(arm,mode,payload):
    done=subprocess.run([sys.executable,"-B",str(CHILD),"--arm",arm,"--mode",mode],
         input=json.dumps(payload),capture_output=True,text=True,cwd=ROOT,timeout=130)
    need(done.returncode==0,"CHILD_"+arm+"_"+mode+"_"+done.stderr[-1300:])
    return json.loads(done.stdout)
def run():
    frozen=json.loads(PREREG.read_text())
    need(frozen["status"]=="FROZEN_BEFORE_COMPARATOR_OR_EXECUTION","PREREG_DRIFT")
    source={p:original_sha(p,h) for p,h in frozen["exact_sources"].items()}
    public_fit=[];queries=[];answers=[]
    for seed in (11,12):
        fit=random.Random(seed).sample(range(256),192)
        unseen=sorted(set(range(256))-set(fit))
        need(len(unseen)==64,"UNSEEN_COUNT")
        for x in fit:
            for a in (0,1,2):
                public_fit.append([str(seed),a,x,truth(seed,a,x)])
        for x in unseen:
            for actions in SEQUENCES:
                state=x
                for a in actions:state=truth(seed,a,state)
                queries.append([str(seed),x,actions])
                answers.append(state)
    need(len(public_fit)==1152 and len(queries)==640,"FROZEN_ROSTER")
    table={};preds={}
    for arm in ARMS:
        trained=child(arm,"train",{"public_fit":public_fit})
        checkpoint=trained["checkpoint_b64"]
        current=child(arm,"score",{"checkpoint_b64":checkpoint,
            "checkpoint_sha256":trained["checkpoint_sha256"],"queries":queries})
        paired=child(arm,"ablate",{"checkpoint_b64":checkpoint,
            "checkpoint_sha256":trained["checkpoint_sha256"],"queries":queries})
        need(len(current["predictions"])==len(answers)
             and len(paired["predictions"])==len(answers),"ALL_OUTCOMES")
        pred=current["predictions"];preds[arm]=pred
        singles=[i for i,q in enumerate(queries) if len(q[2])==1]
        chains=[i for i,q in enumerate(queries) if len(q[2])>1]
        table[arm]={
           "single_step_correct":sum(pred[i]==answers[i] for i in singles),
           "single_step_total":len(singles),
           "multi_action_correct":sum(pred[i]==answers[i] for i in chains),
           "multi_action_total":len(chains),
           "composition_disabled_correct":sum(paired["predictions"][i]==answers[i] for i in chains),
           "native_only":arm=="native",
           "checkpoint_bytes":trained["checkpoint_bytes"],
           "checkpoint_sha256":trained["checkpoint_sha256"],
           "training_child_cpu_ns":trained["process_cpu_ns"],
           "scoring_child_cpu_ns":current["process_cpu_ns"],
           "training_whole_process_peak_rss_bytes":trained["whole_process_peak_rss_bytes"],
           "scoring_whole_process_peak_rss_bytes":current["whole_process_peak_rss_bytes"],
           "cold_process_recovery":current["cold_interpreter"],
        }
    by_action=[i for i,q in enumerate(queries) if len(q[2])>1]
    pair_diff=sum(preds["native"][i]!=preds["conventional"][i] for i in by_action)
    need(pair_diff==0,"NATIVE_CONVENTIONAL_HYPOTHESIS_PARITY_ABSENT")
    report={
        "schema":"yggdrasil.itd02.r7.authored-fixture-independent-controls.v1",
        "source_original_git_blobs":source,
        "original_r7_frozen_science_unchanged":True,
        "development_not_prospective_original_world":True,
        "source_seeds":[11,12],
        "previously_authored_source_fixture_truth":True,
        "original_external_world_resets_steps":0,
        "new_protected_cohort_cases_consumed":0,
        "FIT_public_observations":1152,
        "never_seen_single_step_queries":384,
        "never_seen_multi_action_queries":256,
        "per_model_results":table,
        "native_vs_equal_information_exhaustive_conventional_multi_action_disagreements":pair_diff,
        "all_outcome_digest_sha256":hashlib.sha256(canonical(
            {"queries":queries,"truth":answers,
             "native":preds["native"],"conventional":preds["conventional"],
             "nearest":preds["nearest"]})).hexdigest(),
        "scientific_native_superiority":False,
        "independent_unfamiliar_family_transfer":"NOT_EXECUTED",
        "FORGE_FSA_first_use":"DENIED",
        "optimizer_evidence_reuse":"CONTENT_ADDRESSED_ORIGINAL_AND_HYPOTHESIS_DISCRIMINATION",
        "full_optimizer_candidates_selected_protected":False,
    }
    return report
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=pathlib.Path,required=True)
    a=p.parse_args()
    res=run()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(res,indent=2,sort_keys=True)+"\n")
    print("R7_AUTHORED_HISTORIC_PUBLIC_EXPERIMENT=PASS")
    print("R7_FIT_EVENTS="+str(res["FIT_public_observations"]))
    print("R7_DEV_CHAIN_PREDICTIONS="+str(res["never_seen_multi_action_queries"]))
    for arm,v in res["per_model_results"].items():
        print(f"R7_{arm.upper()}_SINGLE={v['single_step_correct']}/{v['single_step_total']}")
        print(f"R7_{arm.upper()}_CHAIN={v['multi_action_correct']}/{v['multi_action_total']}")
        print(f"R7_{arm.upper()}_NO_COMPOSITION={v['composition_disabled_correct']}/{v['multi_action_total']}")
        print(f"R7_{arm.upper()}_BYTES={v['checkpoint_bytes']}")
    print("R7_NATIVE_VS_CONVENTIONAL_CHAIN_DISAGREEMENTS="+str(res["native_vs_equal_information_exhaustive_conventional_multi_action_disagreements"]))
    print("R7_ORIGINAL_EXTERNAL_WORLD_EPISODES=ZERO")
    print("R7_SCIENTIFIC_FIRSTUSE=DENIED")
    print("R7_DETERMINISTIC_OUTCOME_SHA="+res["all_outcome_digest_sha256"])
if __name__=="__main__":main()
