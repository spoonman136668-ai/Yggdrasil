"""EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-LOCAL-MULTIROW-COALITION-072."""
import argparse
import importlib.util
import json
import math
from pathlib import Path

EXPERIMENT="EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-LOCAL-MULTIROW-COALITION-072"
P071=Path("research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-context-local-key-induction-factorial-071.py")
P068=Path("research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-context-indexed-collateral-state-transport-attribution-068.py")

TRANSPORT='''    transported_row={"key":RETAINED_KEY,"best":RETAINED_STATE["best"],"total":RETAINED_STATE["total"],"best_count":RETAINED_STATE["best_count"],"consistency":RETAINED_STATE["consistency"],"utility":RETAINED_STATE["utility"],"cell_index":RETAINED_STATE["cell_index"]}
    transported_map={RETAINED_KEY:RETAINED_STATE["map_best"]}
    if transported_row["best"]!=transported_map[RETAINED_KEY] or tuple(RETAINED_STATE["key"])!=RETAINED_KEY:
        m["transported_state_identity_mismatch_count"]+=1.0;m["invalid_evaluation_rows"]+=1.0
'''
COMBINED='''        combined_by={r["key"]:r for r in hrows};combined_map=dict(hmap)
        if RETAINED_KEY not in combined_by:
            combined_by[RETAINED_KEY]=transported_row;combined_map[RETAINED_KEY]=transported_map[RETAINED_KEY]
        combined_rows=list(combined_by.values())
'''
ACTIVE='''        if RETAINED_KEY in original_guard:
            active_guard=original_guard;active_used=False
        else:
            active_guard=tuple(list(original_guard[:6])+[RETAINED_KEY]);active_used=True
            m["active_transport_use_schedule_count"]+=1.0
        if len(active_guard)!=7 or len(set(active_guard))!=7:m["invalid_evaluation_rows"]+=1.0
'''
PASSIVE='''            passive_required=tuple(dict.fromkeys(carry+original_guard+(RETAINED_KEY,)))
'''

def load_mod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    if s is None or s.loader is None:raise RuntimeError("IMPORT_SPEC_FAILED:"+name)
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def run(root):
    m={
      "source_identity_mismatch_count":0.0,"induction_source_count":0.0,"induction_source_bytes":0.0,
      "base_training_identity_mismatch_count":0.0,"history_byte_budget_mismatch_count":0.0,
      "invalid_evaluation_rows":0.0,"coalition_candidate_count":0.0,
      "passive_coalition_state_schedule_count":0.0,"active_coalition_use_schedule_count":0.0,
      "original_positive_prose_collateral_schedule_count":0.0,"passive_positive_prose_collateral_schedule_count":0.0,
      "active_positive_prose_collateral_schedule_count":0.0,"active_partner_collateral_failure_count":0.0,
      "original_mean_first_success_packet":0.0,"passive_mean_first_success_packet":0.0,"active_mean_first_success_packet":0.0,
      "behavior_change_flag":0.0,"row_synthesis_count":0.0,"heldout_candidate_selection_count":0.0,
      "heldout_position_selection_count":0.0,"capacity_growth_event_count":0.0,
      "transported_state_identity_mismatch_count":0.0,
    }
    y71=load_mod("y71_y72",P071)
    states=y71.candidate_states(root,m)
    m["coalition_candidate_count"]=float(len(states))
    if len(states)!=2:
        m["invalid_evaluation_rows"]+=1.0
        return {"schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,"metrics":m,"coalition":states}
    keys=tuple(tuple(s["key"]) for s in states)
    base=P068.read_text(encoding="utf-8")
    for needle,name in ((TRANSPORT,"TRANSPORT"),(COMBINED,"COMBINED"),(ACTIVE,"ACTIVE"),(PASSIVE,"PASSIVE")):
        if base.count(needle)!=1:raise RuntimeError("P068_"+name+"_BLOCK_NOT_EXACT")
    transport='''    transported_rows={};transported_map={}
    for state in COALITION_STATES:
        key=tuple(state["key"])
        row={"key":key,"best":state["best"],"total":state["total"],"best_count":state["best_count"],"consistency":state["consistency"],"utility":state["utility"],"cell_index":state["cell_index"]}
        transported_rows[key]=row;transported_map[key]=state["map_best"]
        if row["best"]!=transported_map[key]:
            m["transported_state_identity_mismatch_count"]+=1.0;m["invalid_evaluation_rows"]+=1.0
'''
    combined='''        combined_by={r["key"]:r for r in hrows};combined_map=dict(hmap)
        for key,row in transported_rows.items():
            if key not in combined_by:
                combined_by[key]=row;combined_map[key]=transported_map[key]
        combined_rows=list(combined_by.values())
'''
    active='''        coalition_set=set(COALITION_KEYS)
        base_guard=[k for k in original_guard if k not in coalition_set]
        if len(base_guard)<5:m["invalid_evaluation_rows"]+=1.0
        active_guard=tuple(base_guard[:5]+list(COALITION_KEYS))
        active_used=(active_guard!=original_guard)
        if active_used:m["active_transport_use_schedule_count"]+=1.0
        if len(active_guard)!=7 or len(set(active_guard))!=7:m["invalid_evaluation_rows"]+=1.0
'''
    passive='''            passive_required=tuple(dict.fromkeys(carry+original_guard+COALITION_KEYS))
'''
    source=base.replace(TRANSPORT,transport,1).replace(COMBINED,combined,1).replace(ACTIVE,active,1).replace(PASSIVE,passive,1)
    ns={"__name__":"y68_y72_coalition","__file__":str(P068),"COALITION_STATES":states,"COALITION_KEYS":keys}
    exec(compile(source,str(P068),"exec"),ns)
    child=ns["run"](root);cm=child["metrics"]
    m["passive_coalition_state_schedule_count"]=float(cm["passive_transport_state_schedule_count"])
    m["active_coalition_use_schedule_count"]=float(cm["active_transport_use_schedule_count"])
    m["original_positive_prose_collateral_schedule_count"]=float(cm["original_positive_prose_collateral_schedule_count"])
    m["passive_positive_prose_collateral_schedule_count"]=float(cm["passive_positive_prose_collateral_schedule_count"])
    m["active_positive_prose_collateral_schedule_count"]=float(cm["active_positive_prose_collateral_schedule_count"])
    m["active_partner_collateral_failure_count"]=float(cm["active_partner_collateral_failure_count"])
    m["original_mean_first_success_packet"]=float(cm["original_mean_first_success_packet"])
    m["passive_mean_first_success_packet"]=float(cm["passive_mean_first_success_packet"])
    m["active_mean_first_success_packet"]=float(cm["active_mean_first_success_packet"])
    m["capacity_growth_event_count"]=float(cm["capacity_growth_event_count"])
    m["transported_state_identity_mismatch_count"]=float(cm["transported_state_identity_mismatch_count"])
    m["invalid_evaluation_rows"]+=float(cm["invalid_evaluation_rows"])
    if cm["candidate_selection_heldout_use_count"]!=0:m["invalid_evaluation_rows"]+=float(cm["candidate_selection_heldout_use_count"])
    changed=(m["active_positive_prose_collateral_schedule_count"]!=m["original_positive_prose_collateral_schedule_count"] or
             m["active_mean_first_success_packet"]!=m["original_mean_first_success_packet"] or
             m["active_partner_collateral_failure_count"]!=float(cm["original_partner_collateral_failure_count"]))
    if not changed:
        for d in child.get("diagnostics",[]):
            for p in d.get("packets",[]):
                if p["active"]["dependent"]!=p["original"]["dependent"] or p["active"]["partner"]!=p["original"]["partner"]:
                    changed=True;break
            if changed:break
    m["behavior_change_flag"]=float(changed)
    if cm["preserved_state_structure_count_min"]!=16 or cm["active_structure_count_min"]!=7 or cm["retained_structure_count_min"]!=9:
        m["invalid_evaluation_rows"]+=1.0
    assert all(math.isfinite(float(v)) for v in m.values())
    return {"schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,"metrics":m,"coalition":states,"diagnostics":child["diagnostics"]}

def main():
    p=argparse.ArgumentParser();p.add_argument("--root",required=True);p.add_argument("--out",required=True);a=p.parse_args()
    with open(a.out,"w",encoding="utf-8",newline="\n") as f:json.dump(run(a.root),f,allow_nan=False,separators=(",",":"),sort_keys=True)

if __name__=="__main__":main()
