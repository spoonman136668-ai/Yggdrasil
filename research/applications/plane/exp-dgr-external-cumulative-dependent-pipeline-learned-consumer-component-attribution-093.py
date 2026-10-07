"""Yggdrasil Y093: bounded cognition-consumer component attribution."""
import argparse,importlib.util,json,math,resource,time
from pathlib import Path

EXPERIMENT="EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-LEARNED-CONSUMER-COMPONENT-ATTRIBUTION-093"
Y092_PATH=Path("research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-learned-consumer-architecture-092.py")
FIELDS=("total","best_count","consistency","utility")
ARMS=(
    {"id":"y092-selected","best":"target","map_best":"target"},
    {"id":"retain-best","best":"retained","map_best":"target"},
    {"id":"retain-map-best","best":"target","map_best":"retained"},
    {"id":"retain-both","best":"retained","map_best":"retained"},
)

def load_y092():
    spec=importlib.util.spec_from_file_location("yggdrasil_y092_for_y093",Y092_PATH)
    if spec is None or spec.loader is None: raise RuntimeError("Y092_IMPORT_SPEC_FAILED")
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

def component_consumer(target,retained,arm):
    out=dict(retained)
    out["best"]=int(target["best"] if arm["best"]=="target" else retained["best"])
    out["map_best"]=int(target["map_best"] if arm["map_best"]=="target" else retained["map_best"])
    for k in FIELDS: out[k]=retained[k]
    return out

def improved(base,row):
    return (row["active_partner_collateral_failure_count"]==0.0 and
            ((row["clean_rescue"] and not base["clean_rescue"]) or
             row["active_positive_prose_collateral_schedule_count"]>base["active_positive_prose_collateral_schedule_count"] or
             row["active_mean_first_success_packet"]<base["active_mean_first_success_packet"]))

def run(transfer_root,third_root,fourth_root,fifteenth_root,sixteenth_root):
    y092=load_y092();y079=y092.load_y079();y075=y079.load_y075()
    names=(
      "historical_context_count","historical_full_pool_row_count","historical_identity_mismatch_count",
      "unseen_context_count","variant_count","attribution_arm_count",
      "historical_source_identity_mismatch_count","historical_source_count","historical_source_bytes",
      "historical_base_training_identity_mismatch_count","historical_history_byte_budget_mismatch_count",
      "historical_donor_row_count","historical_eligible_candidate_count",
      "unseen_source_identity_mismatch_count","unseen_source_count","unseen_source_bytes",
      "unseen_base_training_identity_mismatch_count","unseen_history_byte_budget_mismatch_count",
      "unseen_donor_row_count","unseen_eligible_candidate_count",
      "heldout_outcome_use_before_arm_freeze","post_result_arm_or_threshold_choice_count",
      "persistent_state_write_count","source_identity_mismatch_count","transport_identity_mismatch_count",
      "capacity_growth_event_count","addressing_change_count","continuous_field_change_count","invalid_evaluation_rows",
      "capacity_total","capacity_active","capacity_retained","external_model_call_count")
    m={k:0.0 for k in names}
    m["historical_context_count"]=3.0;m["unseen_context_count"]=2.0;m["attribution_arm_count"]=4.0
    m["capacity_total"]=16.0;m["capacity_active"]=7.0;m["capacity_retained"]=9.0

    roots={"transfer":transfer_root,"third":third_root,"fourth":fourth_root}
    by=y092.prepare_historical(y075,y079,roots,m)
    historical=[]
    for name in y092.ORDER:
        for state in by[name]: historical.append({"context":name,"state":dict(state)})

    summaries={a["id"]:{
        "id":a["id"],"improved_context_count":0,"lost_y091_clean_rescue_count":0,
        "partner_collateral_failure_count":0.0,"behavior_change_count":0,"cells":[]} for a in ARMS}
    cells=[]
    for context,root in (("fifteenth",fifteenth_root),("sixteenth",sixteenth_root)):
        pool,target=y092.target_pool(y075,y079,root,m,"unseen_")
        if target is None or not historical:
            m["invalid_evaluation_rows"]+=1.0;continue
        selected_context,distance,retained=y079.retrieve_full(y075,tuple(target["key"]),historical)
        y091=y092.baseline_consumer(target,retained)
        y075.TARGET_SOURCES=y092.dynamic_sources(root)

        states=[("y091-alpha-0.5",y091)]
        for arm in ARMS: states.append((arm["id"],component_consumer(target,retained,arm)))
        rows={}
        for arm_id,state in states:
            if tuple(state["key"])!=tuple(retained["key"]):m["addressing_change_count"]+=1.0
            if arm_id!="y091-alpha-0.5" and any(state[k]!=retained[k] for k in FIELDS):m["continuous_field_change_count"]+=1.0
            child=y075.run_variant(root,state);s=y092.summary(y079,child);m["variant_count"]+=1.0
            m["source_identity_mismatch_count"]+=s["source_mismatch"]
            m["transport_identity_mismatch_count"]+=s["transport_mismatch"]
            m["capacity_growth_event_count"]+=s["capacity_growth"]
            m["invalid_evaluation_rows"]+=s["invalid"]
            row={"context":context,"arm":arm_id,"selected_historical_context":selected_context,
                 "relation_distance":int(distance),"target_key":list(target["key"]),
                 "clean_rescue":s["clean"],"behavior_changed":s["changed"],
                 "original_positive_prose_collateral_schedule_count":s["original_prose"],
                 "active_positive_prose_collateral_schedule_count":s["active_prose"],
                 "active_partner_collateral_failure_count":s["partner_fail"],
                 "active_mean_first_success_packet":s["first"]}
            cells.append(row);rows[arm_id]=row
            if arm_id in summaries:
                summaries[arm_id]["partner_collateral_failure_count"]+=s["partner_fail"]
                summaries[arm_id]["behavior_change_count"]+=int(bool(s["changed"]))
                summaries[arm_id]["cells"].append(row)

        base=rows["y092-selected"];ref=rows["y091-alpha-0.5"]
        for arm in ARMS:
            row=rows[arm["id"]];s=summaries[arm["id"]]
            if improved(base,row):s["improved_context_count"]+=1
            if ref["clean_rescue"] and not row["clean_rescue"]:s["lost_y091_clean_rescue_count"]+=1

    if m["historical_context_count"]!=3.0 or m["historical_full_pool_row_count"]!=17.0 or m["historical_identity_mismatch_count"]!=0.0:m["invalid_evaluation_rows"]+=1.0
    if m["unseen_context_count"]!=2.0 or m["unseen_source_count"]!=6.0 or m["unseen_source_bytes"]!=114544.0:m["invalid_evaluation_rows"]+=1.0
    if m["unseen_source_identity_mismatch_count"]!=0.0 or m["unseen_base_training_identity_mismatch_count"]!=0.0 or m["unseen_history_byte_budget_mismatch_count"]!=0.0:m["invalid_evaluation_rows"]+=1.0
    if m["variant_count"]!=10.0 or len(summaries)!=4:m["invalid_evaluation_rows"]+=1.0
    if m["capacity_total"]!=16.0 or m["capacity_active"]!=7.0 or m["capacity_retained"]!=9.0:m["invalid_evaluation_rows"]+=1.0
    if m["heldout_outcome_use_before_arm_freeze"]!=0.0 or m["post_result_arm_or_threshold_choice_count"]!=0.0:m["invalid_evaluation_rows"]+=1.0
    if m["persistent_state_write_count"]!=0.0 or m["source_identity_mismatch_count"]!=0.0 or m["transport_identity_mismatch_count"]!=0.0:m["invalid_evaluation_rows"]+=1.0
    if m["capacity_growth_event_count"]!=0.0 or m["addressing_change_count"]!=0.0 or m["continuous_field_change_count"]!=0.0:m["invalid_evaluation_rows"]+=1.0
    if any(not math.isfinite(float(v)) for v in m.values()):m["invalid_evaluation_rows"]+=1.0
    ordered=[summaries[a["id"]] for a in ARMS]
    return {"schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,
            "arms":ordered,"metrics":m,"cells":cells}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--transfer-root",required=True);p.add_argument("--third-root",required=True);p.add_argument("--fourth-root",required=True)
    p.add_argument("--fifteenth-root",required=True);p.add_argument("--sixteenth-root",required=True)
    p.add_argument("--out",required=True);p.add_argument("--resource-out")
    a=p.parse_args();started=time.perf_counter_ns();before=resource.getrusage(resource.RUSAGE_SELF)
    result=run(a.transfer_root,a.third_root,a.fourth_root,a.fifteenth_root,a.sixteenth_root)
    after=resource.getrusage(resource.RUSAGE_SELF)
    with open(a.out,"w",encoding="utf-8",newline="\n") as f:json.dump(result,f,allow_nan=False,separators=(",",":"),sort_keys=True)
    if a.resource_out:
        telemetry={"schema":"yggdrasil.rsi-resource-telemetry.v1","experiment":EXPERIMENT,
          "hardware_identity_assumed":False,"home_hardware_policy":"research/roadmap/home-hardware-feasibility.ice",
          "algorithmic_envelope":{"attribution_arms":4,"capacity_total":16,"capacity_active":7,"capacity_retained":9,
                                  "learned_scalars":0,"external_model_calls":0,"persistent_state_growth":False},
          "elapsed_ns":time.perf_counter_ns()-started,"ru_maxrss_before":before.ru_maxrss,"ru_maxrss_after":after.ru_maxrss,
          "user_cpu_seconds":after.ru_utime-before.ru_utime,"system_cpu_seconds":after.ru_stime-before.ru_stime}
        with open(a.resource_out,"w",encoding="utf-8",newline="\n") as f:json.dump(telemetry,f,separators=(",",":"),sort_keys=True)
    print(json.dumps(result,separators=(",",":"),sort_keys=True))

if __name__=="__main__":main()
