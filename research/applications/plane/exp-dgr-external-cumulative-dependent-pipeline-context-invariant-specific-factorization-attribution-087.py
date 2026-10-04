"""Yggdrasil 087: context-invariant/specific key factorization attribution."""
import argparse,hashlib,importlib.util,json,math
from pathlib import Path

EXPERIMENT="EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-INVARIANT-SPECIFIC-FACTORIZATION-ATTRIBUTION-087"
Y079_PATH=Path("research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-consolidation-mechanism-attribution-079.py")
ORDER=("transfer","third","fourth")

def load_y079():
    spec=importlib.util.spec_from_file_location("yggdrasil_y079_for_y087",Y079_PATH)
    if spec is None or spec.loader is None: raise RuntimeError("Y079_IMPORT_SPEC_FAILED")
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

def factor_positions(full_pool):
    if not full_pool: return (0,1),(2,3),[0,0,0,0]
    counts=[]
    for i in range(4):
        counts.append(len({int(item["state"]["key"][i]) for item in full_pool}))
    ranked=sorted(range(4),key=lambda i:(counts[i],i))
    inv=tuple(sorted(ranked[:2]));spec=tuple(sorted(ranked[2:]))
    return inv,spec,counts

def factorized_retrieve(y075,y079,target_key,full_pool,inv_pos,spec_pos):
    ranked=[]
    for item in full_pool:
        state=item["state"];context=item["context"];key=tuple(state["key"])
        inv=sum(int(target_key[i])!=int(key[i]) for i in inv_pos)
        spec=sum(int(target_key[i])!=int(key[i]) for i in spec_pos)
        total=y079.hamming(target_key,key)
        ranked.append((inv,spec,total,ORDER.index(context),y075.local_rank(state),key,item))
    ranked.sort(key=lambda row:row[:-1]);row=ranked[0]
    return row[-1]["context"],row[0],row[1],row[2],row[-1]["state"]

def run(transfer_root,third_root,fourth_root,fifth_root):
    y079=load_y079();y075=y079.load_y075()
    names=(
      "variant_count","historical_context_count","historical_full_pool_row_count","historical_identity_mismatch_count",
      "factorization_position_count","factorization_identity_mismatch_count",
      "factorized_selected_row_change_count","control_clean_rescue_count","factorized_clean_rescue_count",
      "factorized_behavior_change_count","factorized_partner_collateral_failure_count","lost_control_clean_rescue_count",
      "factorization_support","mixed_signal","heldout_outcome_use_before_factorization_freeze",
      "post_result_factorization_change_count","source_state_mutation_count","persistent_state_write_count",
      "all_child_source_identity_mismatch_count","all_child_transport_identity_mismatch_count","capacity_growth_event_count",
      "target_source_identity_mismatch_count","target_source_count","target_total_source_bytes",
      "target_base_training_identity_mismatch_count","target_history_byte_budget_mismatch_count",
      "target_donor_row_count","target_eligible_candidate_count","target_selectors_same_row_count",
      "invalid_evaluation_rows")
    m={k:0.0 for k in names};m["historical_context_count"]=3.0
    roots={"transfer":transfer_root,"third":third_root,"fourth":fourth_root}
    full_pool=[]
    for name in ORDER:
        pool,_,_,mis=y079.build_context(y075,name,roots[name])
        m["historical_identity_mismatch_count"]+=mis
        m["historical_full_pool_row_count"]+=float(len(pool))
        full_pool.extend({"context":name,"state":dict(s)} for s in pool)
    inv_pos,spec_pos,distinct=factor_positions(full_pool)
    m["factorization_position_count"]=float(len(inv_pos)+len(spec_pos))
    if len(inv_pos)!=2 or len(spec_pos)!=2 or set(inv_pos).intersection(spec_pos) or set(inv_pos+spec_pos)!={0,1,2,3}:
        m["factorization_identity_mismatch_count"]+=1.0

    y075.TARGET_SOURCES={k:dict(v) for k,v in y079.SOURCES["fifth"].items()}
    tm=y079.builder_metrics();target_pool=list(y075.build_pool(fifth_root,tm))
    src=sorted(target_pool,key=y075.source_rank)[0] if target_pool else None
    loc=sorted(target_pool,key=y075.local_rank)[0] if target_pool else None
    for dst,key in (
      ("target_source_identity_mismatch_count","target_source_identity_mismatch_count"),
      ("target_source_count","target_source_count"),
      ("target_total_source_bytes","target_total_source_bytes"),
      ("target_base_training_identity_mismatch_count","base_training_identity_mismatch_count"),
      ("target_history_byte_budget_mismatch_count","history_byte_budget_mismatch_count"),
      ("target_donor_row_count","donor_row_count"),
      ("target_eligible_candidate_count","eligible_candidate_count"),
      ("invalid_evaluation_rows","invalid_evaluation_rows")): m[dst]+=float(tm[key])
    if src is None or loc is None or not full_pool:
        m["invalid_evaluation_rows"]+=1.0
        return {"schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,"metrics":m,"cells":[],
                "invariant_positions":list(inv_pos),"specific_positions":list(spec_pos),"distinct_counts":distinct}
    if tuple(src["key"])==tuple(loc["key"]): m["target_selectors_same_row_count"]=1.0

    cells=[];by={}
    for key_origin,target in (("SOURCE_CONDITIONED",src),("LOCAL_ONLY",loc)):
        cc,cd,control_state=y079.retrieve_full(y075,tuple(target["key"]),full_pool)
        fc,fi,fs,ft,factor_state=factorized_retrieve(y075,y079,tuple(target["key"]),full_pool,inv_pos,spec_pos)
        changed=(cc!=fc or tuple(control_state["key"])!=tuple(factor_state["key"]))
        m["factorized_selected_row_change_count"]+=float(changed)
        for rep,context,state,total_dist,inv_dist,spec_dist in (
          ("EXACT_KEY_ONLY",cc,control_state,cd,cd,0),
          ("INVARIANT_SPECIFIC_FACTORIZED_KEY",fc,factor_state,ft,fi,fs)):
            projected=y079.project_payload(target,state)
            child=y075.run_variant(fifth_root,projected);s=y079.summarize(child)
            clean=s["active_prose"]>s["original_prose"] and s["active_partner_fail"]==0.0
            behavior=y079.behavior_changed(child)
            m["variant_count"]+=1.0
            m["all_child_source_identity_mismatch_count"]+=s["source_mismatch"]
            m["all_child_transport_identity_mismatch_count"]+=s["transport_mismatch"]
            m["capacity_growth_event_count"]+=s["capacity_growth"]
            m["invalid_evaluation_rows"]+=s["invalid"]
            if rep=="EXACT_KEY_ONLY": m["control_clean_rescue_count"]+=float(clean)
            else:
                m["factorized_clean_rescue_count"]+=float(clean)
                m["factorized_behavior_change_count"]+=float(behavior)
                m["factorized_partner_collateral_failure_count"]+=s["active_partner_fail"]
            row={"key_origin":key_origin,"representation":rep,"selected_context":context,
                 "selected_historical_key":list(state["key"]),"total_distance":int(total_dist),
                 "invariant_distance":int(inv_dist),"specific_distance":int(spec_dist),
                 "clean_rescue":clean,"behavior_changed":behavior,
                 "original_positive_prose_collateral_schedule_count":s["original_prose"],
                 "active_positive_prose_collateral_schedule_count":s["active_prose"],
                 "active_partner_collateral_failure_count":s["active_partner_fail"],
                 "active_mean_first_success_packet":s["active_first"]}
            cells.append(row);by.setdefault(key_origin,{})[rep]=row

    support=False;mixed=False
    for ko in ("SOURCE_CONDITIONED","LOCAL_ONLY"):
        c=by.get(ko,{}).get("EXACT_KEY_ONLY");f=by.get(ko,{}).get("INVARIANT_SPECIFIC_FACTORIZED_KEY")
        if c is None or f is None: m["invalid_evaluation_rows"]+=1.0;continue
        changed=(c["selected_context"]!=f["selected_context"] or c["selected_historical_key"]!=f["selected_historical_key"])
        if c["clean_rescue"] and not f["clean_rescue"]: m["lost_control_clean_rescue_count"]+=1.0
        if changed and f["clean_rescue"] and not c["clean_rescue"] and f["active_partner_collateral_failure_count"]==0.0:
            support=True
        if (changed and not f["clean_rescue"] and f["active_partner_collateral_failure_count"]==0.0 and
            (f["active_positive_prose_collateral_schedule_count"]>c["active_positive_prose_collateral_schedule_count"] or
             f["active_mean_first_success_packet"]<c["active_mean_first_success_packet"])):
            mixed=True
    if m["lost_control_clean_rescue_count"]>0 or m["factorized_partner_collateral_failure_count"]>0: support=False
    m["factorization_support"]=float(support);m["mixed_signal"]=float(mixed and not support)

    if m["historical_context_count"]!=3.0 or m["historical_full_pool_row_count"]!=17.0 or m["historical_identity_mismatch_count"]!=0.0: m["invalid_evaluation_rows"]+=1.0
    if m["factorization_position_count"]!=4.0 or m["factorization_identity_mismatch_count"]!=0.0: m["invalid_evaluation_rows"]+=1.0
    if m["target_source_count"]!=3.0 or m["target_total_source_bytes"]!=57272.0: m["invalid_evaluation_rows"]+=1.0
    if m["target_source_identity_mismatch_count"]!=0.0 or m["target_base_training_identity_mismatch_count"]!=0.0 or m["target_history_byte_budget_mismatch_count"]!=0.0: m["invalid_evaluation_rows"]+=1.0
    if m["target_donor_row_count"]!=16.0 or m["target_eligible_candidate_count"]!=6.0 or m["target_selectors_same_row_count"]!=0.0: m["invalid_evaluation_rows"]+=1.0
    if m["variant_count"]!=4.0 or m["heldout_outcome_use_before_factorization_freeze"]!=0.0 or m["post_result_factorization_change_count"]!=0.0: m["invalid_evaluation_rows"]+=1.0
    if m["source_state_mutation_count"]!=0.0 or m["persistent_state_write_count"]!=0.0: m["invalid_evaluation_rows"]+=1.0
    if m["all_child_source_identity_mismatch_count"]!=0.0 or m["all_child_transport_identity_mismatch_count"]!=0.0 or m["capacity_growth_event_count"]!=0.0: m["invalid_evaluation_rows"]+=1.0
    if any(not math.isfinite(float(v)) for v in m.values()): m["invalid_evaluation_rows"]+=1.0
    return {"schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,"metrics":m,"cells":cells,
            "invariant_positions":list(inv_pos),"specific_positions":list(spec_pos),"distinct_counts":distinct}

def main():
    p=argparse.ArgumentParser();p.add_argument("--transfer-root",required=True);p.add_argument("--third-root",required=True)
    p.add_argument("--fourth-root",required=True);p.add_argument("--fifth-root",required=True);p.add_argument("--out",required=True);a=p.parse_args()
    with open(a.out,"w",encoding="utf-8",newline="\n") as f:
        json.dump(run(a.transfer_root,a.third_root,a.fourth_root,a.fifth_root),f,allow_nan=False,separators=(",",":"),sort_keys=True)
if __name__=="__main__": main()
