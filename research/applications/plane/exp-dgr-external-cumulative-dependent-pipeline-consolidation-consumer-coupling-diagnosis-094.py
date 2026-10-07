"""Yggdrasil Y094: consolidation/consumer coupling diagnosis."""
import argparse,importlib.util,json,math,resource,time
from pathlib import Path

EXPERIMENT="EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONSOLIDATION-CONSUMER-COUPLING-DIAGNOSIS-094"
Y093_PATH=Path("research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-learned-consumer-component-attribution-093.py")
FIELDS=("total","best_count","consistency","utility")
ARMS=(
 {"id":"retained-continuous_target-discrete","continuous":"retained","discrete":"target"},
 {"id":"target-continuous_target-discrete","continuous":"target","discrete":"target"},
 {"id":"target-continuous_retained-discrete","continuous":"target","discrete":"retained"},
 {"id":"retained-continuous_retained-discrete","continuous":"retained","discrete":"retained"},
)

def load_y093():
    spec=importlib.util.spec_from_file_location("yggdrasil_y093_for_y094",Y093_PATH)
    if spec is None or spec.loader is None: raise RuntimeError("Y093_IMPORT_SPEC_FAILED")
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

def coupled(target,retained,arm):
    out=dict(retained)
    src=target if arm["continuous"]=="target" else retained
    for k in FIELDS: out[k]=src[k]
    dsrc=target if arm["discrete"]=="target" else retained
    out["best"]=int(dsrc["best"]);out["map_best"]=int(dsrc["map_best"])
    return out

def run(transfer_root,third_root,fourth_root,fifteenth_root,sixteenth_root):
    y093=load_y093();y092=y093.load_y092();y079=y092.load_y079();y075=y079.load_y075()
    names=("historical_context_count","historical_full_pool_row_count","historical_identity_mismatch_count","historical_source_identity_mismatch_count","historical_source_count","historical_source_bytes","historical_base_training_identity_mismatch_count","historical_history_byte_budget_mismatch_count","historical_donor_row_count","historical_eligible_candidate_count","unseen_context_count","variant_count","coupling_arm_count","unseen_source_identity_mismatch_count","unseen_source_count","unseen_source_bytes","unseen_base_training_identity_mismatch_count","unseen_history_byte_budget_mismatch_count","unseen_donor_row_count","unseen_eligible_candidate_count","heldout_outcome_use_before_arm_freeze","post_result_arm_or_threshold_choice_count","persistent_state_write_count","source_identity_mismatch_count","transport_identity_mismatch_count","capacity_growth_event_count","addressing_change_count","invalid_evaluation_rows","capacity_total","capacity_active","capacity_retained","external_model_call_count")
    m={k:0.0 for k in names};m["historical_context_count"]=3.0;m["unseen_context_count"]=2.0;m["coupling_arm_count"]=4.0;m["capacity_total"]=16.0;m["capacity_active"]=7.0;m["capacity_retained"]=9.0
    roots={"transfer":transfer_root,"third":third_root,"fourth":fourth_root};by=y092.prepare_historical(y075,y079,roots,m);history=[]
    for name in y092.ORDER:
        for state in by[name]:history.append({"context":name,"state":dict(state)})
    summaries={a["id"]:{"id":a["id"],"improved_context_count":0,"lost_y091_clean_rescue_count":0,"partner_collateral_failure_count":0.0,"behavior_change_count":0,"cells":[]} for a in ARMS};cells=[]
    for context,root in (("fifteenth",fifteenth_root),("sixteenth",sixteenth_root)):
        pool,target=y092.target_pool(y075,y079,root,m,"unseen_")
        if target is None or not history:m["invalid_evaluation_rows"]+=1.0;continue
        selected_context,distance,retained=y079.retrieve_full(y075,tuple(target["key"]),history);y091=y092.baseline_consumer(target,retained);y075.TARGET_SOURCES=y092.dynamic_sources(root)
        rows={}
        evals=[("y091-alpha-0.5",y091)]+[(a["id"],coupled(target,retained,a)) for a in ARMS]
        for arm_id,state in evals:
            if tuple(state["key"])!=tuple(retained["key"]):m["addressing_change_count"]+=1.0
            child=y075.run_variant(root,state);ss=y092.summary(y079,child);m["variant_count"]+=1.0;m["source_identity_mismatch_count"]+=ss["source_mismatch"];m["transport_identity_mismatch_count"]+=ss["transport_mismatch"];m["capacity_growth_event_count"]+=ss["capacity_growth"];m["invalid_evaluation_rows"]+=ss["invalid"]
            row={"context":context,"arm":arm_id,"selected_historical_context":selected_context,"relation_distance":int(distance),"target_key":list(target["key"]),"clean_rescue":ss["clean"],"behavior_changed":ss["changed"],"original_positive_prose_collateral_schedule_count":ss["original_prose"],"active_positive_prose_collateral_schedule_count":ss["active_prose"],"active_partner_collateral_failure_count":ss["partner_fail"],"active_mean_first_success_packet":ss["first"]};cells.append(row);rows[arm_id]=row
            if arm_id in summaries:summaries[arm_id]["partner_collateral_failure_count"]+=ss["partner_fail"];summaries[arm_id]["behavior_change_count"]+=int(bool(ss["changed"]));summaries[arm_id]["cells"].append(row)
        base=rows["retained-continuous_target-discrete"];ref=rows["y091-alpha-0.5"]
        for a in ARMS:
            row=rows[a["id"]];ss=summaries[a["id"]]
            if y093.improved(base,row):ss["improved_context_count"]+=1
            if ref["clean_rescue"] and not row["clean_rescue"]:ss["lost_y091_clean_rescue_count"]+=1
    if m["historical_full_pool_row_count"]!=17.0 or m["historical_identity_mismatch_count"]!=0.0:m["invalid_evaluation_rows"]+=1.0
    if m["unseen_source_count"]!=6.0 or m["unseen_source_bytes"]!=114544.0 or m["unseen_source_identity_mismatch_count"]!=0.0 or m["unseen_base_training_identity_mismatch_count"]!=0.0 or m["unseen_history_byte_budget_mismatch_count"]!=0.0:m["invalid_evaluation_rows"]+=1.0
    if m["variant_count"]!=10.0 or m["capacity_total"]!=16.0 or m["capacity_active"]!=7.0 or m["capacity_retained"]!=9.0:m["invalid_evaluation_rows"]+=1.0
    if m["heldout_outcome_use_before_arm_freeze"]!=0.0 or m["post_result_arm_or_threshold_choice_count"]!=0.0 or m["persistent_state_write_count"]!=0.0 or m["source_identity_mismatch_count"]!=0.0 or m["transport_identity_mismatch_count"]!=0.0 or m["capacity_growth_event_count"]!=0.0 or m["addressing_change_count"]!=0.0:m["invalid_evaluation_rows"]+=1.0
    if any(not math.isfinite(float(v)) for v in m.values()):m["invalid_evaluation_rows"]+=1.0
    return {"schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,"arms":[summaries[a["id"]] for a in ARMS],"metrics":m,"cells":cells}

def main():
    p=argparse.ArgumentParser();p.add_argument("--transfer-root",required=True);p.add_argument("--third-root",required=True);p.add_argument("--fourth-root",required=True);p.add_argument("--fifteenth-root",required=True);p.add_argument("--sixteenth-root",required=True);p.add_argument("--out",required=True);p.add_argument("--resource-out");a=p.parse_args()
    started=time.perf_counter_ns();before=resource.getrusage(resource.RUSAGE_SELF);result=run(a.transfer_root,a.third_root,a.fourth_root,a.fifteenth_root,a.sixteenth_root);after=resource.getrusage(resource.RUSAGE_SELF)
    Path(a.out).write_text(json.dumps(result,allow_nan=False,separators=(",",":"),sort_keys=True),encoding="utf-8")
    if a.resource_out:Path(a.resource_out).write_text(json.dumps({"schema":"yggdrasil.rsi-resource-telemetry.v1","experiment":EXPERIMENT,"algorithmic_envelope":{"coupling_arms":4,"capacity_total":16,"capacity_active":7,"capacity_retained":9,"learned_scalars":0,"external_model_calls":0,"persistent_state_growth":False},"elapsed_ns":time.perf_counter_ns()-started,"ru_maxrss_before":before.ru_maxrss,"ru_maxrss_after":after.ru_maxrss},separators=(",",":"),sort_keys=True),encoding="utf-8")
    print(json.dumps(result,separators=(",",":"),sort_keys=True))
if __name__=="__main__":main()
