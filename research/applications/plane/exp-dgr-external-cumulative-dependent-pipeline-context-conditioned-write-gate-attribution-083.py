"""Yggdrasil 083: context-conditioned write-gate attribution."""
import argparse,importlib.util,json,math
from pathlib import Path
EXPERIMENT="EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-CONDITIONED-WRITE-GATE-ATTRIBUTION-083"
Y080_PATH=Path("research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-consolidation-dynamics-attribution-080.py")
ORDER=("transfer","third","fourth")

def load_y080():
    spec=importlib.util.spec_from_file_location("yggdrasil_y080_for_y083",Y080_PATH)
    if spec is None or spec.loader is None: raise RuntimeError("Y080_IMPORT_SPEC_FAILED")
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

def context_stable_groups(y080,y075,full_pool,control_groups):
    by_group={}
    for item in full_pool:
        s=item["state"];g=y080.class_key(y075,s["key"])
        a=by_group.setdefault(g,{})
        c=a.setdefault(item["context"],{})
        b=int(s["best"]);c[b]=c.get(b,0.0)+float(s["best_count"])
    controls={tuple(x["group"]):x for x in control_groups}
    out=[];rejected=0;disagree=0
    for g,control in controls.items():
        ctx=by_group.get(g,{})
        if len(ctx)<2:
            rejected+=1;continue
        winners=[]
        for name in ORDER:
            ev=ctx.get(name)
            if not ev: continue
            winners.append(min(ev,key=lambda b:(-ev[b],b)))
        if len(winners)<2 or len(set(winners))!=1:
            rejected+=1;disagree+=1;continue
        out.append(control)
    return out,rejected,disagree

def payload_changed(a,b):
    if a is None or b is None: return True
    if int(a["best"])!=int(b["best"]) or int(a["cell_index"])!=int(b["cell_index"]) or int(a["map_best"])!=int(b["map_best"]): return True
    return any(abs(float(a[k])-float(b[k]))>1e-12 for k in ("total","best_count","consistency","utility"))

def run(transfer_root,third_root,fourth_root,fifth_root):
    y080=load_y080();y079=y080.load_y079();y075=y079.load_y075()
    names=("variant_count","historical_full_pool_row_count","historical_identity_mismatch_count","class_group_count",
      "multi_context_class_group_count","writable_class_group_count","rejected_class_group_count","gate_context_disagreement_count",
      "ungated_clean_rescue_count","gated_clean_rescue_count","gated_rejection_count","gated_behavior_change_count",
      "gated_partner_collateral_failure_count","gate_selected_payload_change_count","useful_rejection_count",
      "missed_control_clean_rescue_count","write_gate_support","mixed_signal","heldout_gate_choice_count",
      "post_result_gate_change_count","source_state_mutation_count","persistent_state_write_count",
      "all_child_source_identity_mismatch_count","all_child_transport_identity_mismatch_count",
      "capacity_growth_event_count","target_source_identity_mismatch_count","target_source_count","target_total_source_bytes",
      "target_base_training_identity_mismatch_count","target_history_byte_budget_mismatch_count","target_donor_row_count",
      "target_eligible_candidate_count","target_selectors_same_row_count","invalid_evaluation_rows")
    m={k:0.0 for k in names}
    roots={"transfer":transfer_root,"third":third_root,"fourth":fourth_root};full_pool=[]
    for name in ORDER:
        pool,_,_,mis=y079.build_context(y075,name,roots[name]);m["historical_identity_mismatch_count"]+=mis
        m["historical_full_pool_row_count"]+=float(len(pool));full_pool.extend({"context":name,"state":dict(s)} for s in pool)

    ugroups,umulti=y080.aggregate_groups(y075,full_pool,True)
    ggroups,rejected,disagree=context_stable_groups(y080,y075,full_pool,ugroups)
    m["class_group_count"]=float(len(ugroups));m["multi_context_class_group_count"]=float(umulti)
    m["writable_class_group_count"]=float(len(ggroups));m["rejected_class_group_count"]=float(rejected)
    m["gate_context_disagreement_count"]=float(disagree)
    if len(ggroups)+rejected!=len(ugroups): m["invalid_evaluation_rows"]+=1.0

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
    if src is None or loc is None or not ugroups:
        m["invalid_evaluation_rows"]+=1.0
        return {"schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,"metrics":m,"cells":[]}
    if tuple(src["key"])==tuple(loc["key"]): m["target_selectors_same_row_count"]=1.0

    cells=[];by={}
    for ko,target in (("SOURCE_CONDITIONED",src),("LOCAL_ONLY",loc)):
        u=y080.retrieve_class(y075,tuple(target["key"]),ugroups)
        if u is None:
            m["invalid_evaluation_rows"]+=1.0;continue
        g=y080.retrieve_class(y075,tuple(target["key"]),ggroups) if ggroups else None
        control_state=y079.project_payload(target,u["state"])
        control_child=y075.run_variant(fifth_root,control_state);cs=y079.summarize(control_child)
        control_clean=cs["active_prose"]>cs["original_prose"] and cs["active_partner_fail"]==0.0
        control_changed=y079.behavior_changed(control_child)
        m["variant_count"]+=1.0;m["ungated_clean_rescue_count"]+=float(control_clean)
        m["all_child_source_identity_mismatch_count"]+=cs["source_mismatch"]
        m["all_child_transport_identity_mismatch_count"]+=cs["transport_mismatch"];m["capacity_growth_event_count"]+=cs["capacity_growth"];m["invalid_evaluation_rows"]+=cs["invalid"]
        crow={"key_origin":ko,"representation":"UNGATED_CLASS_WRITE","rejected":False,"key":list(control_state["key"]),
          "best":int(control_state["best"]),"distance":int(y080.class_hamming(y075,tuple(target["key"]),u["state"]["key"])),
          "clean_rescue":control_clean,"behavior_changed":control_changed,
          "original_positive_prose_collateral_schedule_count":cs["original_prose"],
          "active_positive_prose_collateral_schedule_count":cs["active_prose"],
          "active_partner_collateral_failure_count":cs["active_partner_fail"],
          "active_mean_first_success_packet":cs["active_first"]}
        cells.append(crow);by.setdefault(ko,{})["UNGATED_CLASS_WRITE"]=crow

        m["variant_count"]+=1.0
        if g is None:
            m["gated_rejection_count"]+=1.0
            useful=control_changed and cs["active_prose"]<=cs["original_prose"] and not control_clean
            if useful: m["useful_rejection_count"]+=1.0
            if control_clean: m["missed_control_clean_rescue_count"]+=1.0
            grow={"key_origin":ko,"representation":"CONTEXT_STABLE_WRITE_GATE","rejected":True,"key":None,"best":None,"distance":None,
              "clean_rescue":False,"behavior_changed":False,
              "original_positive_prose_collateral_schedule_count":cs["original_prose"],
              "active_positive_prose_collateral_schedule_count":cs["original_prose"],
              "active_partner_collateral_failure_count":cs["original_partner_fail"],
              "active_mean_first_success_packet":cs["original_first"]}
        else:
            gate_state=y079.project_payload(target,g["state"])
            if tuple(g["group"])!=tuple(u["group"]) or payload_changed(u["state"],g["state"]): m["gate_selected_payload_change_count"]+=1.0
            gate_child=y075.run_variant(fifth_root,gate_state);gs=y079.summarize(gate_child)
            gate_clean=gs["active_prose"]>gs["original_prose"] and gs["active_partner_fail"]==0.0
            gate_changed=y079.behavior_changed(gate_child)
            m["gated_clean_rescue_count"]+=float(gate_clean);m["gated_behavior_change_count"]+=float(gate_changed)
            m["gated_partner_collateral_failure_count"]+=gs["active_partner_fail"]
            m["all_child_source_identity_mismatch_count"]+=gs["source_mismatch"]
            m["all_child_transport_identity_mismatch_count"]+=gs["transport_mismatch"];m["capacity_growth_event_count"]+=gs["capacity_growth"];m["invalid_evaluation_rows"]+=gs["invalid"]
            grow={"key_origin":ko,"representation":"CONTEXT_STABLE_WRITE_GATE","rejected":False,"key":list(gate_state["key"]),
              "best":int(gate_state["best"]),"distance":int(y080.class_hamming(y075,tuple(target["key"]),g["state"]["key"])),
              "clean_rescue":gate_clean,"behavior_changed":gate_changed,
              "original_positive_prose_collateral_schedule_count":gs["original_prose"],
              "active_positive_prose_collateral_schedule_count":gs["active_prose"],
              "active_partner_collateral_failure_count":gs["active_partner_fail"],
              "active_mean_first_success_packet":gs["active_first"]}
        cells.append(grow);by.setdefault(ko,{})["CONTEXT_STABLE_WRITE_GATE"]=grow

    support=m["useful_rejection_count"]>0
    mixed=False
    for ko in ("SOURCE_CONDITIONED","LOCAL_ONLY"):
        c=by.get(ko,{}).get("UNGATED_CLASS_WRITE");g=by.get(ko,{}).get("CONTEXT_STABLE_WRITE_GATE")
        if c is None or g is None: m["invalid_evaluation_rows"]+=1.0;continue
        if g["clean_rescue"] and not c["clean_rescue"]: support=True
        if (not g["rejected"] and not g["clean_rescue"] and g["active_partner_collateral_failure_count"]==0.0 and
            (g["active_positive_prose_collateral_schedule_count"]>c["active_positive_prose_collateral_schedule_count"] or
             g["active_mean_first_success_packet"]<c["active_mean_first_success_packet"])): mixed=True
    if m["missed_control_clean_rescue_count"]>0 or m["gated_partner_collateral_failure_count"]>0: support=False
    m["write_gate_support"]=float(support);m["mixed_signal"]=float(mixed and not support)

    if m["historical_full_pool_row_count"]!=17.0 or m["historical_identity_mismatch_count"]!=0.0: m["invalid_evaluation_rows"]+=1.0
    if m["target_source_count"]!=3.0 or m["target_total_source_bytes"]!=57272.0: m["invalid_evaluation_rows"]+=1.0
    if m["target_source_identity_mismatch_count"]!=0.0 or m["target_base_training_identity_mismatch_count"]!=0.0 or m["target_history_byte_budget_mismatch_count"]!=0.0: m["invalid_evaluation_rows"]+=1.0
    if m["target_donor_row_count"]!=16.0 or m["target_eligible_candidate_count"]!=6.0 or m["target_selectors_same_row_count"]!=0.0: m["invalid_evaluation_rows"]+=1.0
    if m["variant_count"]!=4.0 or m["heldout_gate_choice_count"]!=0.0 or m["post_result_gate_change_count"]!=0.0: m["invalid_evaluation_rows"]+=1.0
    if m["source_state_mutation_count"]!=0.0 or m["persistent_state_write_count"]!=0.0: m["invalid_evaluation_rows"]+=1.0
    if m["all_child_source_identity_mismatch_count"]!=0.0 or m["all_child_transport_identity_mismatch_count"]!=0.0 or m["capacity_growth_event_count"]!=0.0: m["invalid_evaluation_rows"]+=1.0
    if any(not math.isfinite(float(v)) for v in m.values()): m["invalid_evaluation_rows"]+=1.0
    return {"schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,"metrics":m,"cells":cells}

def main():
    p=argparse.ArgumentParser();p.add_argument("--transfer-root",required=True);p.add_argument("--third-root",required=True)
    p.add_argument("--fourth-root",required=True);p.add_argument("--fifth-root",required=True);p.add_argument("--out",required=True);a=p.parse_args()
    with open(a.out,"w",encoding="utf-8",newline="\n") as f:
        json.dump(run(a.transfer_root,a.third_root,a.fourth_root,a.fifth_root),f,allow_nan=False,separators=(",",":"),sort_keys=True)
if __name__=="__main__": main()
