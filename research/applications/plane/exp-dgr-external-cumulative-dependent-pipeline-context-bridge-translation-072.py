"""EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-BRIDGE-TRANSLATION-072."""
import argparse
import importlib.util
import json
import math
from pathlib import Path

EXPERIMENT="EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-BRIDGE-TRANSLATION-072"
P071=Path("research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-context-local-key-induction-factorial-071.py")
P068=Path("research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-context-indexed-collateral-state-transport-attribution-068.py")
SOURCE_STATE={
    "key":(10,32,32,32),"best":32,"total":112,"best_count":112,
    "consistency":1.0,"utility":112.0,"cell_index":12,"map_best":32,
}
EXPECTED=[
    {"key":(32,116,104,101),"occ":8,"argmax":7,"consistency":0.8739495798319328},
    {"key":(32,97,110,100),"occ":3,"argmax":2,"consistency":0.9864864864864865},
]

def load_mod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    if s is None or s.loader is None:raise RuntimeError("IMPORT_SPEC_FAILED:"+name)
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def bridge_state(trigger):
    return {
      "key":tuple(trigger["key"]),
      "best":SOURCE_STATE["best"],
      "total":SOURCE_STATE["total"],
      "best_count":SOURCE_STATE["best_count"],
      "consistency":SOURCE_STATE["consistency"],
      "utility":SOURCE_STATE["utility"],
      "cell_index":SOURCE_STATE["cell_index"],
      "map_best":SOURCE_STATE["map_best"],
    }

def run_bridge(root,trigger):
    p68=load_mod("p068_bridge_"+str(trigger["rank"]),P068)
    p68.RETAINED_KEY=tuple(trigger["key"])
    p68.RETAINED_STATE=bridge_state(trigger)
    return p68.run(root)

def changed(child):
    m=child["metrics"]
    if m["active_positive_prose_collateral_schedule_count"]!=m["original_positive_prose_collateral_schedule_count"]:return True
    if m["active_mean_first_success_packet"]!=m["original_mean_first_success_packet"]:return True
    if m["active_partner_collateral_failure_count"]!=m["original_partner_collateral_failure_count"]:return True
    for d in child.get("diagnostics",[]):
        for p in d.get("packets",[]):
            if p["active"]!=p["original"]:return True
    return False

def run(root):
    m={
      "source_identity_mismatch_count":0.0,"induction_source_count":0.0,"induction_source_bytes":0.0,
      "base_training_identity_mismatch_count":0.0,"history_byte_budget_mismatch_count":0.0,
      "candidate_identity_mismatch_count":0.0,"candidate_count":0.0,"compatible_candidate_count":0.0,
      "heldout_compatibility_use_count":0.0,"selected_trigger_rank":0.0,"selected_compatibility_score":0.0,
      "alternate_trigger_rank":0.0,"alternate_compatibility_score":0.0,
      "source_payload_identity_mismatch_count":0.0,"bridge_payload_mutation_count":0.0,
      "bridge_translated_field_count":1.0,"bridge_row_synthesis_count":0.0,"persistent_state_write_count":0.0,
      "selected_bridge_behavior_change_count":0.0,"alternate_bridge_behavior_change_count":0.0,
      "original_positive_prose_collateral_schedule_count":0.0,
      "selected_positive_prose_collateral_schedule_count":0.0,"alternate_positive_prose_collateral_schedule_count":0.0,
      "selected_partner_collateral_failure_count":0.0,"alternate_partner_collateral_failure_count":0.0,
      "selected_mean_first_success_packet":0.0,"alternate_mean_first_success_packet":0.0,
      "capacity_growth_event_count":0.0,"invalid_evaluation_rows":0.0,
    }
    p71=load_mod("p071_bridge",P071)
    states=p71.candidate_states(root,m)
    m["candidate_count"]=float(len(states))
    if len(states)!=2:m["invalid_evaluation_rows"]+=1.0
    triggers=[]
    for i,state in enumerate(states[:2]):
        exp=EXPECTED[i]
        if tuple(state["key"])!=exp["key"] or state["train_occurrence_count"]!=exp["occ"] or state["train_argmax_count"]!=exp["argmax"] or abs(float(state["consistency"])-exp["consistency"])>1e-12:
            m["candidate_identity_mismatch_count"]+=1.0
        eligible=(
          state["train_occurrence_count"]>=1 and state["train_argmax_count"]>=1 and
          int(state["best"])==SOURCE_STATE["best"] and int(state["map_best"])==SOURCE_STATE["map_best"]
        )
        score=float(state["train_argmax_count"])*float(state["consistency"]) if eligible else -1.0
        if eligible:m["compatible_candidate_count"]+=1.0
        triggers.append({"rank":i+1,"key":tuple(state["key"]),"score":score,"eligible":eligible,"state":state})
    compatible=[x for x in triggers if x["eligible"]]
    if not compatible:
        return {"schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,"decision":"REJECT","metrics":m,"triggers":triggers,"selected":None,"alternate":None}
    compatible.sort(key=lambda x:(-x["score"],x["key"]))
    selected=compatible[0];alternate=compatible[1] if len(compatible)>1 else None
    m["selected_trigger_rank"]=float(selected["rank"]);m["selected_compatibility_score"]=float(selected["score"])
    if alternate is not None:
        m["alternate_trigger_rank"]=float(alternate["rank"]);m["alternate_compatibility_score"]=float(alternate["score"])
    for k in ("best","total","best_count","consistency","utility","cell_index","map_best"):
        if bridge_state(selected)[k]!=SOURCE_STATE[k]:m["bridge_payload_mutation_count"]+=1.0
    if tuple(SOURCE_STATE["key"])!=(10,32,32,32) or SOURCE_STATE["best"]!=32 or SOURCE_STATE["total"]!=112 or SOURCE_STATE["best_count"]!=112 or SOURCE_STATE["map_best"]!=32:
        m["source_payload_identity_mismatch_count"]+=1.0
    sel=run_bridge(root,selected);m["bridge_row_synthesis_count"]+=1.0
    sm=sel["metrics"]
    m["original_positive_prose_collateral_schedule_count"]=float(sm["original_positive_prose_collateral_schedule_count"])
    m["selected_positive_prose_collateral_schedule_count"]=float(sm["active_positive_prose_collateral_schedule_count"])
    m["selected_partner_collateral_failure_count"]=float(sm["active_partner_collateral_failure_count"])
    m["selected_mean_first_success_packet"]=float(sm["active_mean_first_success_packet"])
    if changed(sel):m["selected_bridge_behavior_change_count"]=1.0
    m["capacity_growth_event_count"]+=float(sm["capacity_growth_event_count"])
    m["invalid_evaluation_rows"]+=float(sm["invalid_evaluation_rows"]+sm["transported_state_identity_mismatch_count"])
    alt=None
    if alternate is not None:
        alt=run_bridge(root,alternate);m["bridge_row_synthesis_count"]+=1.0
        am=alt["metrics"]
        if float(am["original_positive_prose_collateral_schedule_count"])!=m["original_positive_prose_collateral_schedule_count"]:
            m["invalid_evaluation_rows"]+=1.0
        m["alternate_positive_prose_collateral_schedule_count"]=float(am["active_positive_prose_collateral_schedule_count"])
        m["alternate_partner_collateral_failure_count"]=float(am["active_partner_collateral_failure_count"])
        m["alternate_mean_first_success_packet"]=float(am["active_mean_first_success_packet"])
        if changed(alt):m["alternate_bridge_behavior_change_count"]=1.0
        m["capacity_growth_event_count"]+=float(am["capacity_growth_event_count"])
        m["invalid_evaluation_rows"]+=float(am["invalid_evaluation_rows"]+am["transported_state_identity_mismatch_count"])
    if m["candidate_identity_mismatch_count"]!=0 or m["source_payload_identity_mismatch_count"]!=0 or m["bridge_payload_mutation_count"]!=0:
        m["invalid_evaluation_rows"]+=1.0
    if m["bridge_row_synthesis_count"]!=float(len(compatible)):m["invalid_evaluation_rows"]+=1.0
    if m["capacity_growth_event_count"]!=0 or m["persistent_state_write_count"]!=0:m["invalid_evaluation_rows"]+=1.0
    assert all(math.isfinite(float(v)) for v in m.values())
    return {
      "schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,"decision":"BRIDGE",
      "metrics":m,
      "selected":{"rank":selected["rank"],"key":list(selected["key"]),"score":selected["score"],"source_payload":bridge_state(selected)},
      "alternate":None if alternate is None else {"rank":alternate["rank"],"key":list(alternate["key"]),"score":alternate["score"],"source_payload":bridge_state(alternate)},
      "selected_diagnostics":sel["diagnostics"],
      "alternate_diagnostics":[] if alt is None else alt["diagnostics"],
    }

def main():
    p=argparse.ArgumentParser();p.add_argument("--root",required=True);p.add_argument("--out",required=True);a=p.parse_args()
    with open(a.out,"w",encoding="utf-8",newline="\n") as f:json.dump(run(a.root),f,allow_nan=False,separators=(",",":"),sort_keys=True)

if __name__=="__main__":main()
