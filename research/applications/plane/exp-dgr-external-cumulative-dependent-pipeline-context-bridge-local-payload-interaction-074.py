"""EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-BRIDGE-LOCAL-PAYLOAD-INTERACTION-074."""
import argparse
import importlib.util
import json
import math
from pathlib import Path

EXPERIMENT="EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-BRIDGE-LOCAL-PAYLOAD-INTERACTION-074"
P070=Path("research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-context-local-key-induction-070.py")
P071=Path("research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-context-local-key-induction-factorial-071.py")
P072=Path("research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-context-bridge-translation-072.py")
SOURCE_STATE={"key":(10,32,32,32),"best":32,"total":112,"best_count":112,"consistency":1.0,"utility":112.0,"cell_index":12,"map_best":32}

def load_mod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    if s is None or s.loader is None:raise RuntimeError("IMPORT_SPEC_FAILED:"+name)
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def byte_class(x):
    x=int(x)
    if x in (9,10,13,32):return 0
    if 65<=x<=90 or 97<=x<=122:return 1
    if 48<=x<=57:return 2
    return 3

def build_pool(root,m):
    p70=load_mod("p070_y74",P070)
    rows,fm,prose_train=p70.canonical_donor(root,m)
    m["donor_row_count"]=float(len(rows))
    pool=[]
    for r in rows:
        key=tuple(r["key"]);occ,obs,argmax,argmax_count=p70.scan_key(prose_train,key)
        if occ<1 or obs<1:continue
        state={
          "key":key,"best":int(r["best"]),"total":int(r["total"]),"best_count":int(r["best_count"]),
          "consistency":float(r["consistency"]),"utility":float(r["utility"]),
          "cell_index":int(r["cell_index"]),"map_best":int(fm[key]),
          "train_occurrence_count":int(occ),"train_argmax_count":int(argmax_count),
          "train_argmax":int(argmax),
        }
        pool.append(state)
    m["eligible_candidate_count"]=float(len(pool))
    return pool

def source_rank(s):
    best_match=int(byte_class(s["best"])==byte_class(SOURCE_STATE["best"]))
    key_matches=sum(byte_class(a)==byte_class(b) for a,b in zip(s["key"],SOURCE_STATE["key"]))
    return (-best_match,-key_matches,-s["train_occurrence_count"],-s["train_argmax_count"],-s["utility"],s["key"])

def local_rank(s):
    return (-s["train_occurrence_count"],-s["train_argmax_count"],-s["utility"],s["key"])

def summarize(child):
    m=child["metrics"]
    return {
      "positive_prose":float(m["active_positive_prose_collateral_schedule_count"]),
      "partner_fail":float(m["active_partner_collateral_failure_count"]),
      "mean_first":float(m["active_mean_first_success_packet"]),
      "original_positive_prose":float(m["original_positive_prose_collateral_schedule_count"]),
      "original_partner_fail":float(m["original_partner_collateral_failure_count"]),
      "original_mean_first":float(m["original_mean_first_success_packet"]),
      "capacity_growth":float(m["capacity_growth_event_count"]),
      "invalid":float(m["invalid_evaluation_rows"]),
      "source_mismatch":float(m["source_identity_mismatch_count"]+m["transfer_manifest_identity_mismatch_count"]),
      "transport_mismatch":float(m["transported_state_identity_mismatch_count"]),
    }

def run(root):
    m={
      "source_identity_mismatch_count":0.0,"base_training_identity_mismatch_count":0.0,
      "history_byte_budget_mismatch_count":0.0,"donor_row_count":0.0,"eligible_candidate_count":0.0,
      "source_state_identity_mismatch_count":0.0,"source_state_mutation_count":0.0,
      "heldout_selection_count":0.0,"selectors_same_row_count":0.0,
      "source_selected_best_class_match":0.0,"source_selected_key_class_match_count":0.0,
      "source_selected_train_occurrence_count":0.0,"local_selected_train_occurrence_count":0.0,
      "original_positive_prose_collateral_schedule_count":0.0,
      "source_positive_prose_collateral_schedule_count":0.0,"local_positive_prose_collateral_schedule_count":0.0,
      "source_partner_collateral_failure_count":0.0,"local_partner_collateral_failure_count":0.0,
      "source_mean_first_success_packet":0.0,"local_mean_first_success_packet":0.0,
      "source_behavior_change_count":0.0,"local_behavior_change_count":0.0,
      "all_child_source_identity_mismatch_count":0.0,"all_child_transport_identity_mismatch_count":0.0,
      "capacity_growth_event_count":0.0,"persistent_state_write_count":0.0,
      "invalid_evaluation_rows":0.0,
    }
    if SOURCE_STATE!={"key":(10,32,32,32),"best":32,"total":112,"best_count":112,"consistency":1.0,"utility":112.0,"cell_index":12,"map_best":32}:
        m["source_state_identity_mismatch_count"]+=1.0
    pool=build_pool(root,m)
    if m["donor_row_count"]!=16 or not pool:
        m["invalid_evaluation_rows"]+=1.0
        return {"schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,"metrics":m,"source_selected":None,"local_selected":None}
    sr=sorted(pool,key=source_rank);lr=sorted(pool,key=local_rank)
    source_selected=sr[0];local_selected=lr[0]
    if tuple(source_selected["key"])==tuple(local_selected["key"]):m["selectors_same_row_count"]=1.0
    m["source_selected_best_class_match"]=float(byte_class(source_selected["best"])==byte_class(SOURCE_STATE["best"]))
    m["source_selected_key_class_match_count"]=float(sum(byte_class(a)==byte_class(b) for a,b in zip(source_selected["key"],SOURCE_STATE["key"])))
    m["source_selected_train_occurrence_count"]=float(source_selected["train_occurrence_count"])
    m["local_selected_train_occurrence_count"]=float(local_selected["train_occurrence_count"])
    p71=load_mod("p071_y74",P071);p72=load_mod("p072_y74",P072)
    source_child=p71.run_variant(root,source_selected,6)
    local_child=p71.run_variant(root,local_selected,6)
    ss=summarize(source_child);ls=summarize(local_child)
    if ss["original_positive_prose"]!=ls["original_positive_prose"] or ss["original_partner_fail"]!=ls["original_partner_fail"] or ss["original_mean_first"]!=ls["original_mean_first"]:
        m["invalid_evaluation_rows"]+=1.0
    m["original_positive_prose_collateral_schedule_count"]=ss["original_positive_prose"]
    m["source_positive_prose_collateral_schedule_count"]=ss["positive_prose"]
    m["local_positive_prose_collateral_schedule_count"]=ls["positive_prose"]
    m["source_partner_collateral_failure_count"]=ss["partner_fail"];m["local_partner_collateral_failure_count"]=ls["partner_fail"]
    m["source_mean_first_success_packet"]=ss["mean_first"];m["local_mean_first_success_packet"]=ls["mean_first"]
    if p72.changed(source_child):m["source_behavior_change_count"]=1.0
    if p72.changed(local_child):m["local_behavior_change_count"]=1.0
    m["capacity_growth_event_count"]=ss["capacity_growth"]+ls["capacity_growth"]
    m["all_child_source_identity_mismatch_count"]=ss["source_mismatch"]+ls["source_mismatch"]
    m["all_child_transport_identity_mismatch_count"]=ss["transport_mismatch"]+ls["transport_mismatch"]
    m["invalid_evaluation_rows"]+=ss["invalid"]+ls["invalid"]
    if m["source_state_identity_mismatch_count"]!=0 or m["source_state_mutation_count"]!=0:m["invalid_evaluation_rows"]+=1.0
    if m["all_child_source_identity_mismatch_count"]!=0 or m["all_child_transport_identity_mismatch_count"]!=0:m["invalid_evaluation_rows"]+=1.0
    if m["capacity_growth_event_count"]!=0 or m["persistent_state_write_count"]!=0:m["invalid_evaluation_rows"]+=1.0
    assert all(math.isfinite(float(v)) for v in m.values())
    return {
      "schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,"metrics":m,
      "source_selected":source_selected,"local_selected":local_selected,
      "source_diagnostics":source_child["diagnostics"],"local_diagnostics":local_child["diagnostics"],
    }

def main():
    p=argparse.ArgumentParser();p.add_argument("--root",required=True);p.add_argument("--out",required=True);a=p.parse_args()
    with open(a.out,"w",encoding="utf-8",newline="\n") as f:json.dump(run(a.root),f,allow_nan=False,separators=(",",":"),sort_keys=True)

if __name__=="__main__":main()
