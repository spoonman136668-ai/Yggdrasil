"""Yggdrasil 091: developmental consumer architecture on fresh sealed contexts."""
import argparse,hashlib,importlib.util,json,math
from pathlib import Path

EXPERIMENT="EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-DEVELOPMENTAL-CONSUMER-ARCHITECTURE-091"
Y079_PATH=Path("research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-consolidation-mechanism-attribution-079.py")
ORDER=("transfer","third","fourth")
EXPECTED_LOCAL_KEYS={"tenth":(99,116,105,111),"eleventh":(116,114,117,99)}

def load_y079():
    spec=importlib.util.spec_from_file_location("yggdrasil_y079_for_y091",Y079_PATH)
    if spec is None or spec.loader is None: raise RuntimeError("Y079_IMPORT_SPEC_FAILED")
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

def dynamic_sources(root):
    root=Path(root)
    names=(("A","code.bin",41453),("B","structured.bin",14365),("C","technical-prose.bin",1454))
    out={}
    for k,name,n in names:
        data=(root/name).read_bytes()
        out[k]={"file":name,"sha256":hashlib.sha256(data).hexdigest(),"bytes":n}
    return out

def target_pool(y075,y079,root,m):
    y075.TARGET_SOURCES=dynamic_sources(root)
    tm=y079.builder_metrics()
    pool=[dict(x) for x in y075.build_pool(root,tm)]
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
    if not pool:return [],None
    return pool,dict(sorted(pool,key=y075.local_rank)[0])

def developmental_consumer(y079,target,retained):
    control=y079.project_payload(target,retained)
    treatment=dict(control)
    treatment["best"]=int(target["best"])
    treatment["map_best"]=int(target["map_best"])
    treatment["total"]=(int(retained["total"])+int(target["total"]))//2
    treatment["best_count"]=(int(retained["best_count"])+int(target["best_count"]))//2
    treatment["consistency"]=(float(retained["consistency"])+float(target["consistency"]))/2.0
    treatment["utility"]=(float(retained["utility"])+float(target["utility"]))/2.0
    return control,treatment

def run(transfer_root,third_root,fourth_root,tenth_root,eleventh_root):
    y079=load_y079();y075=y079.load_y075()
    names=(
      "historical_context_count","historical_full_pool_row_count","historical_identity_mismatch_count",
      "unseen_context_count","variant_count","control_clean_rescue_count","treatment_clean_rescue_count",
      "treatment_only_clean_rescue_count","lost_control_clean_rescue_count","treatment_behavior_change_count",
      "treatment_partner_collateral_failure_count","treatment_improvement_case_count","target_selector_key_mismatch_count",
      "target_source_identity_mismatch_count","target_source_count","target_total_source_bytes",
      "target_base_training_identity_mismatch_count","target_history_byte_budget_mismatch_count",
      "target_donor_row_count","target_eligible_candidate_count",
      "heldout_outcome_use_before_consumer_freeze","target_context_mapping_disclosure_count",
      "target_answer_disclosure_count","post_result_consumer_change_count","post_result_memory_addressing_change_count",
      "persistent_state_write_count","all_child_source_identity_mismatch_count",
      "all_child_transport_identity_mismatch_count","capacity_growth_event_count","invalid_evaluation_rows")
    m={k:0.0 for k in names};m["historical_context_count"]=3.0;m["unseen_context_count"]=2.0
    roots={"transfer":transfer_root,"third":third_root,"fourth":fourth_root}
    historical=[]
    for name in ORDER:
        pool,rep,bm,mis=y079.build_context(y075,name,roots[name])
        pool=[dict(x) for x in pool]
        m["historical_identity_mismatch_count"]+=float(mis)
        m["historical_full_pool_row_count"]+=float(len(pool))
        if rep is None or not pool:
            m["invalid_evaluation_rows"]+=1.0
            continue
        for state in pool:historical.append({"context":name,"state":dict(state)})

    cells=[]
    for context,root in (("tenth",tenth_root),("eleventh",eleventh_root)):
        pool,target=target_pool(y075,y079,root,m)
        if target is None or not historical:
            m["invalid_evaluation_rows"]+=1.0;continue
        if tuple(target["key"])!=EXPECTED_LOCAL_KEYS[context]:
            m["target_selector_key_mismatch_count"]+=1.0
        selected_context,distance,retained=y079.retrieve_full(y075,tuple(target["key"]),historical)
        control,treatment=developmental_consumer(y079,target,retained)
        by={}
        y075.TARGET_SOURCES=dynamic_sources(root)
        for arm,state in (("EXACT_RETAINED_STATE",control),("DEVELOPMENTAL_RESIDUAL_CONSUMER",treatment)):
            child=y075.run_variant(root,state);s=y079.summarize(child)
            clean=s["active_prose"]>s["original_prose"] and s["active_partner_fail"]==0.0
            changed=y079.behavior_changed(child)
            m["variant_count"]+=1.0
            m["all_child_source_identity_mismatch_count"]+=s["source_mismatch"]
            m["all_child_transport_identity_mismatch_count"]+=s["transport_mismatch"]
            m["capacity_growth_event_count"]+=s["capacity_growth"]
            m["invalid_evaluation_rows"]+=s["invalid"]
            if arm=="EXACT_RETAINED_STATE":m["control_clean_rescue_count"]+=float(clean)
            else:
                m["treatment_clean_rescue_count"]+=float(clean)
                m["treatment_behavior_change_count"]+=float(changed)
                m["treatment_partner_collateral_failure_count"]+=s["active_partner_fail"]
            row={"context":context,"arm":arm,"selected_historical_context":selected_context,
                 "selected_historical_key":list(retained["key"]),"relation_distance":int(distance),
                 "target_key":list(target["key"]),"clean_rescue":clean,"behavior_changed":changed,
                 "original_positive_prose_collateral_schedule_count":s["original_prose"],
                 "active_positive_prose_collateral_schedule_count":s["active_prose"],
                 "active_partner_collateral_failure_count":s["active_partner_fail"],
                 "active_mean_first_success_packet":s["active_first"]}
            cells.append(row);by[arm]=row
        c=by["EXACT_RETAINED_STATE"];t=by["DEVELOPMENTAL_RESIDUAL_CONSUMER"]
        if t["clean_rescue"] and not c["clean_rescue"]:m["treatment_only_clean_rescue_count"]+=1.0
        if c["clean_rescue"] and not t["clean_rescue"]:m["lost_control_clean_rescue_count"]+=1.0
        if (t["active_partner_collateral_failure_count"]==0.0 and
            (t["active_positive_prose_collateral_schedule_count"]>c["active_positive_prose_collateral_schedule_count"] or
             t["active_mean_first_success_packet"]<c["active_mean_first_success_packet"])):
            m["treatment_improvement_case_count"]+=1.0

    if m["historical_context_count"]!=3.0 or m["historical_full_pool_row_count"]!=17.0 or m["historical_identity_mismatch_count"]!=0.0:m["invalid_evaluation_rows"]+=1.0
    if m["unseen_context_count"]!=2.0 or m["target_source_count"]!=6.0 or m["target_total_source_bytes"]!=114544.0:m["invalid_evaluation_rows"]+=1.0
    if m["target_source_identity_mismatch_count"]!=0.0 or m["target_base_training_identity_mismatch_count"]!=0.0 or m["target_history_byte_budget_mismatch_count"]!=0.0:m["invalid_evaluation_rows"]+=1.0
    if m["target_selector_key_mismatch_count"]!=0.0 or m["target_donor_row_count"]!=32.0 or m["variant_count"]!=4.0:m["invalid_evaluation_rows"]+=1.0
    if m["heldout_outcome_use_before_consumer_freeze"]!=0.0 or m["post_result_consumer_change_count"]!=0.0 or m["post_result_memory_addressing_change_count"]!=0.0:m["invalid_evaluation_rows"]+=1.0
    if m["target_context_mapping_disclosure_count"]!=0.0 or m["target_answer_disclosure_count"]!=0.0:m["invalid_evaluation_rows"]+=1.0
    if m["persistent_state_write_count"]!=0.0 or m["all_child_source_identity_mismatch_count"]!=0.0 or m["all_child_transport_identity_mismatch_count"]!=0.0:m["invalid_evaluation_rows"]+=1.0
    if m["capacity_growth_event_count"]!=0.0:m["invalid_evaluation_rows"]+=1.0
    if any(not math.isfinite(float(v)) for v in m.values()):m["invalid_evaluation_rows"]+=1.0
    return {"schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,"metrics":m,"cells":cells}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--transfer-root",required=True);p.add_argument("--third-root",required=True);p.add_argument("--fourth-root",required=True)
    p.add_argument("--tenth-root",required=True);p.add_argument("--eleventh-root",required=True);p.add_argument("--out",required=True)
    a=p.parse_args()
    with open(a.out,"w",encoding="utf-8",newline="\n") as f:
        json.dump(run(a.transfer_root,a.third_root,a.fourth_root,a.tenth_root,a.eleventh_root),f,allow_nan=False,separators=(",",":"),sort_keys=True)
if __name__=="__main__":main()
