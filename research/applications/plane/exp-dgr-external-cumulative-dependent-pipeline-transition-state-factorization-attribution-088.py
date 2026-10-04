"""Yggdrasil 088: transition-state factorization attribution."""
import argparse,importlib.util,json,math
from pathlib import Path

EXPERIMENT="EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-TRANSITION-STATE-FACTORIZATION-ATTRIBUTION-088"
Y079_PATH=Path("research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-consolidation-mechanism-attribution-079.py")
ORDER=("transfer","third","fourth")

def load_y079():
    spec=importlib.util.spec_from_file_location("yggdrasil_y079_for_y088",Y079_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Y079_IMPORT_SPEC_FAILED")
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def transition_mask(key,anchor):
    return tuple(int(int(key[i])!=int(anchor[i])) for i in range(4))

def mask_hamming(a,b):
    return sum(int(x)!=int(y) for x,y in zip(a,b))

def transition_retrieve(y075,y079,target_key,target_mask,full_pool,reps):
    ranked=[]
    for item in full_pool:
        context=item["context"];state=item["state"];key=tuple(state["key"])
        if context not in reps:
            continue
        hmask=transition_mask(key,tuple(reps[context]["key"]))
        mdist=mask_hamming(target_mask,hmask)
        kdist=y079.hamming(target_key,key)
        ranked.append((mdist,kdist,ORDER.index(context),y075.local_rank(state),key,item,hmask))
    if not ranked:
        raise RuntimeError("TRANSITION_RETRIEVAL_EMPTY")
    ranked.sort(key=lambda row:row[:5])
    row=ranked[0]
    return row[5]["context"],row[0],row[1],row[5]["state"],row[6]

def run(transfer_root,third_root,fourth_root,fifth_root):
    y079=load_y079();y075=y079.load_y075()
    names=(
      "variant_count","historical_context_count","historical_full_pool_row_count","historical_identity_mismatch_count",
      "historical_representative_count","transition_mask_length_mismatch_count",
      "transition_selected_row_change_count","control_clean_rescue_count","transition_clean_rescue_count",
      "transition_behavior_change_count","transition_partner_collateral_failure_count","lost_control_clean_rescue_count",
      "transition_factorization_support","mixed_signal","heldout_outcome_use_before_transition_factorization_freeze",
      "post_result_transition_factorization_change_count","source_state_mutation_count","persistent_state_write_count",
      "all_child_source_identity_mismatch_count","all_child_transport_identity_mismatch_count","capacity_growth_event_count",
      "target_source_identity_mismatch_count","target_source_count","target_total_source_bytes",
      "target_base_training_identity_mismatch_count","target_history_byte_budget_mismatch_count",
      "target_donor_row_count","target_eligible_candidate_count","target_selectors_same_row_count",
      "invalid_evaluation_rows")
    m={k:0.0 for k in names};m["historical_context_count"]=3.0
    roots={"transfer":transfer_root,"third":third_root,"fourth":fourth_root}
    full_pool=[];reps={}
    for name in ORDER:
        pool,selected,_,mis=y079.build_context(y075,name,roots[name])
        m["historical_identity_mismatch_count"]+=mis
        m["historical_full_pool_row_count"]+=float(len(pool))
        if selected is not None:
            reps[name]=dict(selected)
            m["historical_representative_count"]+=1.0
        full_pool.extend({"context":name,"state":dict(s)} for s in pool)

    for item in full_pool:
        context=item["context"]
        if context not in reps:
            m["transition_mask_length_mismatch_count"]+=1.0
            continue
        hm=transition_mask(tuple(item["state"]["key"]),tuple(reps[context]["key"]))
        if len(hm)!=4 or any(x not in (0,1) for x in hm):
            m["transition_mask_length_mismatch_count"]+=1.0

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
      ("invalid_evaluation_rows","invalid_evaluation_rows")):
        m[dst]+=float(tm[key])

    if src is None or loc is None or not full_pool or len(reps)!=3:
        m["invalid_evaluation_rows"]+=1.0
        return {"schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,"metrics":m,"cells":[]}

    if tuple(src["key"])==tuple(loc["key"]):
        m["target_selectors_same_row_count"]=1.0

    cells=[];by={}
    selectors={"SOURCE_CONDITIONED":src,"LOCAL_ONLY":loc}
    others={"SOURCE_CONDITIONED":loc,"LOCAL_ONLY":src}
    for key_origin,target in selectors.items():
        other=others[key_origin]
        tmask=transition_mask(tuple(target["key"]),tuple(other["key"]))
        if len(tmask)!=4 or any(x not in (0,1) for x in tmask):
            m["transition_mask_length_mismatch_count"]+=1.0
        cc,cd,control_state=y079.retrieve_full(y075,tuple(target["key"]),full_pool)
        tc,tmd,tkd,transition_state,hmask=transition_retrieve(
            y075,y079,tuple(target["key"]),tmask,full_pool,reps)
        changed=(cc!=tc or tuple(control_state["key"])!=tuple(transition_state["key"]))
        m["transition_selected_row_change_count"]+=float(changed)

        for rep,context,state,key_dist,mask_dist,selected_mask in (
          ("EXACT_KEY_ONLY",cc,control_state,cd,None,None),
          ("TRANSITION_MASK_FACTORIZED_KEY",tc,transition_state,tkd,tmd,hmask)):
            projected=y079.project_payload(target,state)
            child=y075.run_variant(fifth_root,projected);s=y079.summarize(child)
            clean=s["active_prose"]>s["original_prose"] and s["active_partner_fail"]==0.0
            behavior=y079.behavior_changed(child)
            m["variant_count"]+=1.0
            m["all_child_source_identity_mismatch_count"]+=s["source_mismatch"]
            m["all_child_transport_identity_mismatch_count"]+=s["transport_mismatch"]
            m["capacity_growth_event_count"]+=s["capacity_growth"]
            m["invalid_evaluation_rows"]+=s["invalid"]
            if rep=="EXACT_KEY_ONLY":
                m["control_clean_rescue_count"]+=float(clean)
            else:
                m["transition_clean_rescue_count"]+=float(clean)
                m["transition_behavior_change_count"]+=float(behavior)
                m["transition_partner_collateral_failure_count"]+=s["active_partner_fail"]
            row={
              "key_origin":key_origin,"representation":rep,"selected_context":context,
              "selected_historical_key":list(state["key"]),"key_hamming_distance":int(key_dist),
              "target_transition_mask":list(tmask),
              "selected_transition_mask":list(selected_mask) if selected_mask is not None else None,
              "transition_mask_distance":int(mask_dist) if mask_dist is not None else None,
              "clean_rescue":clean,"behavior_changed":behavior,
              "original_positive_prose_collateral_schedule_count":s["original_prose"],
              "active_positive_prose_collateral_schedule_count":s["active_prose"],
              "active_partner_collateral_failure_count":s["active_partner_fail"],
              "active_mean_first_success_packet":s["active_first"]}
            cells.append(row);by.setdefault(key_origin,{})[rep]=row

    support=False;mixed=False
    for ko in ("SOURCE_CONDITIONED","LOCAL_ONLY"):
        c=by.get(ko,{}).get("EXACT_KEY_ONLY")
        t=by.get(ko,{}).get("TRANSITION_MASK_FACTORIZED_KEY")
        if c is None or t is None:
            m["invalid_evaluation_rows"]+=1.0
            continue
        changed=(c["selected_context"]!=t["selected_context"] or c["selected_historical_key"]!=t["selected_historical_key"])
        if c["clean_rescue"] and not t["clean_rescue"]:
            m["lost_control_clean_rescue_count"]+=1.0
        if changed and t["clean_rescue"] and not c["clean_rescue"] and t["active_partner_collateral_failure_count"]==0.0:
            support=True
        if (changed and not t["clean_rescue"] and t["active_partner_collateral_failure_count"]==0.0 and
            (t["active_positive_prose_collateral_schedule_count"]>c["active_positive_prose_collateral_schedule_count"] or
             t["active_mean_first_success_packet"]<c["active_mean_first_success_packet"])):
            mixed=True
    if m["lost_control_clean_rescue_count"]>0 or m["transition_partner_collateral_failure_count"]>0:
        support=False
    m["transition_factorization_support"]=float(support)
    m["mixed_signal"]=float(mixed and not support)

    if m["historical_context_count"]!=3.0 or m["historical_full_pool_row_count"]!=17.0 or m["historical_identity_mismatch_count"]!=0.0:
        m["invalid_evaluation_rows"]+=1.0
    if m["historical_representative_count"]!=3.0 or m["transition_mask_length_mismatch_count"]!=0.0:
        m["invalid_evaluation_rows"]+=1.0
    if m["target_source_count"]!=3.0 or m["target_total_source_bytes"]!=57272.0:
        m["invalid_evaluation_rows"]+=1.0
    if m["target_source_identity_mismatch_count"]!=0.0 or m["target_base_training_identity_mismatch_count"]!=0.0 or m["target_history_byte_budget_mismatch_count"]!=0.0:
        m["invalid_evaluation_rows"]+=1.0
    if m["target_donor_row_count"]!=16.0 or m["target_eligible_candidate_count"]!=6.0 or m["target_selectors_same_row_count"]!=0.0:
        m["invalid_evaluation_rows"]+=1.0
    if m["variant_count"]!=4.0 or m["heldout_outcome_use_before_transition_factorization_freeze"]!=0.0 or m["post_result_transition_factorization_change_count"]!=0.0:
        m["invalid_evaluation_rows"]+=1.0
    if m["source_state_mutation_count"]!=0.0 or m["persistent_state_write_count"]!=0.0:
        m["invalid_evaluation_rows"]+=1.0
    if m["all_child_source_identity_mismatch_count"]!=0.0 or m["all_child_transport_identity_mismatch_count"]!=0.0 or m["capacity_growth_event_count"]!=0.0:
        m["invalid_evaluation_rows"]+=1.0
    if any(not math.isfinite(float(v)) for v in m.values()):
        m["invalid_evaluation_rows"]+=1.0

    return {
      "schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,
      "metrics":m,"cells":cells}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--transfer-root",required=True)
    p.add_argument("--third-root",required=True)
    p.add_argument("--fourth-root",required=True)
    p.add_argument("--fifth-root",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    with open(a.out,"w",encoding="utf-8",newline="\n") as f:
        json.dump(run(a.transfer_root,a.third_root,a.fourth_root,a.fifth_root),f,allow_nan=False,separators=(",",":"),sort_keys=True)
if __name__=="__main__":
    main()
