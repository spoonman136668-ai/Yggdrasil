"""EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-LOCAL-KEY-INDUCTION-FACTORIAL-071."""
import argparse
import importlib.util
import json
import math
from pathlib import Path

EXPERIMENT="EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-LOCAL-KEY-INDUCTION-FACTORIAL-071"
P070=Path("research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-context-local-key-induction-070.py")
P068=Path("research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-context-indexed-collateral-state-transport-attribution-068.py")
NEEDLE='''        if RETAINED_KEY in original_guard:
            active_guard=original_guard;active_used=False
        else:
            active_guard=tuple(list(original_guard[:6])+[RETAINED_KEY]);active_used=True
            m["active_transport_use_schedule_count"]+=1.0
'''

def load_mod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    if s is None or s.loader is None:raise RuntimeError("IMPORT_SPEC_FAILED:"+name)
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def candidate_states(root,m):
    p70=load_mod("p070_y71",P070)
    rows,fm,prose_train=p70.canonical_donor(root,m)
    eligible=[]
    for r in rows:
        key=tuple(r["key"]);occ,obs,best,best_count=p70.scan_key(prose_train,key)
        map_best=fm.get(key)
        ok=(occ>=1 and obs>=1 and best==int(r["best"]) and map_best is not None and int(map_best)==int(r["best"]))
        if ok:
            state={
              "key":key,"best":int(r["best"]),"total":int(r["total"]),"best_count":int(r["best_count"]),
              "consistency":float(r["consistency"]),"utility":float(r["utility"]),"cell_index":int(r["cell_index"]),"map_best":int(map_best),
              "train_occurrence_count":int(occ),"train_argmax_count":int(best_count),
            }
            eligible.append(state)
    eligible.sort(key=lambda s:(-s["train_occurrence_count"],-s["train_argmax_count"],-s["utility"],s["key"]))
    return eligible

def run_variant(root,state,pos):
    base=P068.read_text(encoding="utf-8")
    if base.count(NEEDLE)!=1:raise RuntimeError("PRIOR_ACTIVATION_BLOCK_NOT_EXACT")
    repl=f'''        base_guard=[k for k in original_guard if k!=RETAINED_KEY]
        if RETAINED_KEY not in original_guard:
            if len(base_guard)!=7:m["invalid_evaluation_rows"]+=1.0
            elif {pos}>=len(base_guard):m["invalid_evaluation_rows"]+=1.0
            else:base_guard.pop({pos})
        if len(base_guard)!=6:m["invalid_evaluation_rows"]+=1.0
        active_list=list(base_guard);active_list.insert({pos},RETAINED_KEY)
        active_guard=tuple(active_list)
        active_used=(active_guard!=original_guard)
        if active_used:m["active_transport_use_schedule_count"]+=1.0
'''
    source=base.replace(NEEDLE,repl,1)
    ns={"__name__":"y68_y71_variant","__file__":str(P068)}
    exec(compile(source,str(P068),"exec"),ns)
    ns["RETAINED_KEY"]=tuple(state["key"])
    ns["RETAINED_STATE"]={k:state[k] for k in ("key","best","total","best_count","consistency","utility","cell_index","map_best")}
    return ns["run"](root)

def run(root):
    m={
      "source_identity_mismatch_count":0.0,"induction_source_count":0.0,"induction_source_bytes":0.0,
      "base_training_identity_mismatch_count":0.0,"history_byte_budget_mismatch_count":0.0,
      "expected_candidate_count":2.0,"candidate_count":0.0,"candidate_rank_count":2.0,"activation_position_count":7.0,"variant_count":0.0,
      "heldout_candidate_selection_count":0.0,"heldout_position_selection_count":0.0,"row_synthesis_count":0.0,
      "rank1_rescue_position_count":0.0,"rank2_rescue_position_count":0.0,"rank1_rank7_rescue_count":0.0,"rank2_rank7_rescue_count":0.0,
      "any_rescue_count":0.0,"behavior_change_cell_count":0.0,
      "all_variant_invalid_evaluation_rows":0.0,"all_variant_source_identity_mismatch_count":0.0,
      "all_variant_transport_identity_mismatch_count":0.0,"capacity_growth_event_count":0.0,
      "invalid_evaluation_rows":0.0,
    }
    states=candidate_states(root,m);m["candidate_count"]=float(len(states))
    variants=[];original_prose=None;original_first=None;original_partner=None
    if len(states)!=2:m["invalid_evaluation_rows"]+=1.0
    for ri,state in enumerate(states[:2],start=1):
        for pos in range(7):
            child=run_variant(root,state,pos);cm=child["metrics"];m["variant_count"]+=1.0
            op=float(cm["original_positive_prose_collateral_schedule_count"])
            ap=float(cm["active_positive_prose_collateral_schedule_count"])
            of=float(cm["original_mean_first_success_packet"]);af=float(cm["active_mean_first_success_packet"])
            opr=float(cm["original_partner_collateral_failure_count"]);apr=float(cm["active_partner_collateral_failure_count"])
            if original_prose is None:original_prose,original_first,original_partner=op,of,opr
            elif (op,of,opr)!=(original_prose,original_first,original_partner):m["invalid_evaluation_rows"]+=1.0
            rescue=(ap>op and apr==0)
            if rescue:
                m["any_rescue_count"]+=1.0
                m[f"rank{ri}_rescue_position_count"]+=1.0
                if pos==6:m[f"rank{ri}_rank7_rescue_count"]+=1.0
            if ap!=op or af!=of or apr!=opr:m["behavior_change_cell_count"]+=1.0
            m["all_variant_invalid_evaluation_rows"]+=float(cm["invalid_evaluation_rows"])
            m["all_variant_source_identity_mismatch_count"]+=float(cm["source_identity_mismatch_count"]+cm["transfer_manifest_identity_mismatch_count"])
            m["all_variant_transport_identity_mismatch_count"]+=float(cm["transported_state_identity_mismatch_count"])
            m["capacity_growth_event_count"]+=float(cm["capacity_growth_event_count"])
            variants.append({
              "candidate_rank":ri,"activation_position":pos+1,"candidate_key":list(state["key"]),
              "candidate_train_occurrence_count":state["train_occurrence_count"],
              "candidate_train_argmax_count":state["train_argmax_count"],
              "rescue":rescue,
              "active_positive_prose_collateral_schedule_count":ap,
              "active_partner_collateral_failure_count":apr,
              "active_mean_first_success_packet":af,
              "original_positive_prose_collateral_schedule_count":op,
              "original_mean_first_success_packet":of,
            })
    rank1_any=m["rank1_rescue_position_count"]>0
    rank2_any=m["rank2_rescue_position_count"]>0
    rank1_outside=(m["rank1_rescue_position_count"]-m["rank1_rank7_rescue_count"])>0
    rank2_outside=(m["rank2_rescue_position_count"]-m["rank2_rank7_rescue_count"])>0
    flags={
      "CANDIDATE_RANK":bool(rank2_any and not rank1_any),
      "ACTIVATION_POSITION":bool(rank1_outside),
      "CANDIDATE_POSITION_INTERACTION":bool(rank2_outside and m["rank2_rank7_rescue_count"]==0 and not rank1_any),
    }
    active=[k for k,v in flags.items() if v]
    if m["any_rescue_count"]==0:attribution="NO_RESCUE"
    elif len(active)==1:attribution=active[0]
    else:attribution="MULTIPLE"
    if m["all_variant_invalid_evaluation_rows"]!=0 or m["all_variant_source_identity_mismatch_count"]!=0 or m["all_variant_transport_identity_mismatch_count"]!=0:
        m["invalid_evaluation_rows"]+=1.0
    if m["variant_count"]!=14 or m["candidate_count"]!=2 or m["capacity_growth_event_count"]!=0:m["invalid_evaluation_rows"]+=1.0
    assert all(math.isfinite(float(v)) for v in m.values())
    return {"schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,"attribution":attribution,"metrics":m,"candidates":states[:2],"variants":variants}

def main():
    p=argparse.ArgumentParser();p.add_argument("--root",required=True);p.add_argument("--out",required=True);a=p.parse_args()
    with open(a.out,"w",encoding="utf-8",newline="\n") as f:json.dump(run(a.root),f,allow_nan=False,separators=(",",":"),sort_keys=True)

if __name__=="__main__":main()
