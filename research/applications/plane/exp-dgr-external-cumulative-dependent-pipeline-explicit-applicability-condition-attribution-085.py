"""Yggdrasil 085: explicit applicability-condition attribution."""
import argparse,importlib.util,json,math
from pathlib import Path

EXPERIMENT="EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-EXPLICIT-APPLICABILITY-CONDITION-ATTRIBUTION-085"
Y084_PATH=Path("research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-context-relational-representation-attribution-084.py")
ORDER=("transfer","third","fourth")

def load_y084():
    spec=importlib.util.spec_from_file_location("yggdrasil_y084_for_y085",Y084_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Y084_IMPORT_SPEC_FAILED")
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

def relational_rank(y084,y080,y075,target_key,groups,full_pool,m):
    target=tuple(int(v) for v in target_key);scored=[]
    for g in groups:
        group=tuple(g["group"]);distances=[]
        for context in ORDER:
            members=[item for item in full_pool if item["context"]==context and tuple(y080.class_key(y075,item["state"]["key"]))==group]
            if not members:
                continue
            distances.append(min(y084.exact_hamming(target,item["state"]["key"]) for item in members))
        if len(distances)<2:
            m["invalid_evaluation_rows"]+=1.0
            continue
        scored.append((max(distances),sum(distances),group,g))
    scored.sort(key=lambda row:(row[0],row[1],row[2]))
    return scored

def run(transfer_root,third_root,fourth_root,fifth_root):
    y084=load_y084();y080=y084.load_y080();y079=y080.load_y079();y075=y079.load_y075()
    names=("variant_count","historical_full_pool_row_count","historical_identity_mismatch_count","class_group_count",
      "multi_context_class_group_count","relational_candidate_class_count","primary_minimax_tie_count",
      "dominance_approved_count","dominance_rejected_count","control_clean_rescue_count","gated_clean_rescue_count",
      "control_behavior_change_count","gated_behavior_change_count","gated_partner_collateral_failure_count",
      "useful_rejection_count","missed_control_clean_rescue_count","applicability_support","mixed_signal",
      "heldout_applicability_choice_count","post_result_applicability_change_count","source_state_mutation_count",
      "persistent_state_write_count","all_child_source_identity_mismatch_count","all_child_transport_identity_mismatch_count",
      "capacity_growth_event_count","target_source_identity_mismatch_count","target_source_count","target_total_source_bytes",
      "target_base_training_identity_mismatch_count","target_history_byte_budget_mismatch_count","target_donor_row_count",
      "target_eligible_candidate_count","target_selectors_same_row_count","invalid_evaluation_rows")
    m={k:0.0 for k in names}

    roots={"transfer":transfer_root,"third":third_root,"fourth":fourth_root};full_pool=[]
    for name in ORDER:
        pool,_,_,mis=y079.build_context(y075,name,roots[name])
        m["historical_identity_mismatch_count"]+=mis
        m["historical_full_pool_row_count"]+=float(len(pool))
        full_pool.extend({"context":name,"state":dict(s)} for s in pool)

    groups,multi=y080.aggregate_groups(y075,full_pool,True)
    m["class_group_count"]=float(len(groups));m["multi_context_class_group_count"]=float(multi)
    m["relational_candidate_class_count"]=float(len(groups))

    y075.TARGET_SOURCES={k:dict(v) for k,v in y079.SOURCES["fifth"].items()}
    tm=y079.builder_metrics();target_pool=list(y075.build_pool(fifth_root,tm))
    src=sorted(target_pool,key=y075.source_rank)[0] if target_pool else None
    loc=sorted(target_pool,key=y075.local_rank)[0] if target_pool else None
    for dst,key in (
      ("target_source_identity_mismatch_count","target_source_identity_mismatch_count"),
      ("target_source_count","target_source_count"),("target_total_source_bytes","target_total_source_bytes"),
      ("target_base_training_identity_mismatch_count","base_training_identity_mismatch_count"),
      ("target_history_byte_budget_mismatch_count","history_byte_budget_mismatch_count"),
      ("target_donor_row_count","donor_row_count"),("target_eligible_candidate_count","eligible_candidate_count"),
      ("invalid_evaluation_rows","invalid_evaluation_rows")):
        m[dst]+=float(tm[key])

    if src is None or loc is None or len(groups)<2:
        m["invalid_evaluation_rows"]+=1.0
        return {"schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,"metrics":m,"cells":[]}
    if tuple(src["key"])==tuple(loc["key"]):
        m["target_selectors_same_row_count"]=1.0

    cells=[];support=False;mixed=False
    for ko,target in (("SOURCE_CONDITIONED",src),("LOCAL_ONLY",loc)):
        ranked=relational_rank(y084,y080,y075,tuple(target["key"]),groups,full_pool,m)
        donor=y084.relational_retrieve(y080,y075,tuple(target["key"]),groups,full_pool,m)
        if len(ranked)<2 or donor is None:
            m["invalid_evaluation_rows"]+=1.0
            continue
        winner=ranked[0][3]
        if tuple(winner["group"])!=tuple(donor["group"]):
            m["invalid_evaluation_rows"]+=1.0
        best_primary=ranked[0][0]
        other_primary=[row[0] for row in ranked[1:]]
        primary_tie=any(v==best_primary for v in other_primary)
        approved=(len(other_primary)>0 and best_primary<min(other_primary))
        m["primary_minimax_tie_count"]+=float(primary_tie)
        m["dominance_approved_count"]+=float(approved)
        m["dominance_rejected_count"]+=float(not approved)

        state=y079.project_payload(target,winner["state"])
        child=y075.run_variant(fifth_root,state);s=y079.summarize(child)
        control_clean=s["active_prose"]>s["original_prose"] and s["active_partner_fail"]==0.0
        control_behavior=y079.behavior_changed(child)
        m["variant_count"]+=1.0;m["control_clean_rescue_count"]+=float(control_clean)
        m["control_behavior_change_count"]+=float(control_behavior)
        m["all_child_source_identity_mismatch_count"]+=s["source_mismatch"]
        m["all_child_transport_identity_mismatch_count"]+=s["transport_mismatch"]
        m["capacity_growth_event_count"]+=s["capacity_growth"];m["invalid_evaluation_rows"]+=s["invalid"]
        control={"key_origin":ko,"representation":"UNCONDITIONAL_RELATIONAL_ACTIVATION","rejected":False,
          "selected_group":list(winner["group"]),"primary_minimax_distance":best_primary,
          "secondary_sum_distance":ranked[0][1],"key":list(state["key"]),"best":int(state["best"]),
          "clean_rescue":control_clean,"behavior_changed":control_behavior,
          "original_positive_prose_collateral_schedule_count":s["original_prose"],
          "active_positive_prose_collateral_schedule_count":s["active_prose"],
          "active_partner_collateral_failure_count":s["active_partner_fail"],
          "active_mean_first_success_packet":s["active_first"]}
        cells.append(control)

        m["variant_count"]+=1.0
        if approved:
            # Gate changes eligibility only; an approved cell must be byte-identical to the control activation.
            gated_clean=control_clean;gated_behavior=control_behavior
            gated_partner=s["active_partner_fail"]
            gated_prose=s["active_prose"];gated_first=s["active_first"]
            m["gated_clean_rescue_count"]+=float(gated_clean)
            m["gated_behavior_change_count"]+=float(gated_behavior)
            m["gated_partner_collateral_failure_count"]+=gated_partner
            gated={"key_origin":ko,"representation":"STRICT_MINIMAX_DOMINANCE_GATE","rejected":False,
              "selected_group":list(winner["group"]),"primary_minimax_distance":best_primary,
              "secondary_sum_distance":ranked[0][1],"key":list(state["key"]),"best":int(state["best"]),
              "clean_rescue":gated_clean,"behavior_changed":gated_behavior,
              "original_positive_prose_collateral_schedule_count":s["original_prose"],
              "active_positive_prose_collateral_schedule_count":gated_prose,
              "active_partner_collateral_failure_count":gated_partner,
              "active_mean_first_success_packet":gated_first}
        else:
            gated_clean=False;gated_behavior=False
            gated_partner=s["original_partner_fail"]
            gated_prose=s["original_prose"];gated_first=s["original_first"]
            useful=(control_behavior and not control_clean and
                    s["active_prose"]<=s["original_prose"] and s["original_partner_fail"]==0.0)
            if useful:
                m["useful_rejection_count"]+=1.0;support=True
            if control_clean:
                m["missed_control_clean_rescue_count"]+=1.0
            if (not useful and s["original_partner_fail"]==0.0 and
                (s["original_prose"]>s["active_prose"] or s["original_first"]<s["active_first"])):
                mixed=True
            m["gated_partner_collateral_failure_count"]+=gated_partner
            gated={"key_origin":ko,"representation":"STRICT_MINIMAX_DOMINANCE_GATE","rejected":True,
              "selected_group":None,"primary_minimax_distance":best_primary,
              "secondary_sum_distance":ranked[0][1],"key":None,"best":None,
              "clean_rescue":False,"behavior_changed":False,
              "original_positive_prose_collateral_schedule_count":s["original_prose"],
              "active_positive_prose_collateral_schedule_count":gated_prose,
              "active_partner_collateral_failure_count":gated_partner,
              "active_mean_first_success_packet":gated_first}
        cells.append(gated)

    if m["missed_control_clean_rescue_count"]>0 or m["gated_partner_collateral_failure_count"]>0:
        support=False
    m["applicability_support"]=float(support);m["mixed_signal"]=float(mixed and not support)

    if m["historical_full_pool_row_count"]!=17.0 or m["historical_identity_mismatch_count"]!=0.0:
        m["invalid_evaluation_rows"]+=1.0
    if m["class_group_count"]!=2.0 or m["multi_context_class_group_count"]!=2.0 or m["relational_candidate_class_count"]!=2.0:
        m["invalid_evaluation_rows"]+=1.0
    if m["target_source_count"]!=3.0 or m["target_total_source_bytes"]!=57272.0:
        m["invalid_evaluation_rows"]+=1.0
    if m["target_source_identity_mismatch_count"]!=0.0 or m["target_base_training_identity_mismatch_count"]!=0.0 or m["target_history_byte_budget_mismatch_count"]!=0.0:
        m["invalid_evaluation_rows"]+=1.0
    if m["target_donor_row_count"]!=16.0 or m["target_eligible_candidate_count"]!=6.0 or m["target_selectors_same_row_count"]!=0.0:
        m["invalid_evaluation_rows"]+=1.0
    if m["variant_count"]!=4.0 or m["dominance_approved_count"]+m["dominance_rejected_count"]!=2.0:
        m["invalid_evaluation_rows"]+=1.0
    if m["heldout_applicability_choice_count"]!=0.0 or m["post_result_applicability_change_count"]!=0.0:
        m["invalid_evaluation_rows"]+=1.0
    if m["source_state_mutation_count"]!=0.0 or m["persistent_state_write_count"]!=0.0:
        m["invalid_evaluation_rows"]+=1.0
    if m["all_child_source_identity_mismatch_count"]!=0.0 or m["all_child_transport_identity_mismatch_count"]!=0.0 or m["capacity_growth_event_count"]!=0.0:
        m["invalid_evaluation_rows"]+=1.0
    if any(not math.isfinite(float(v)) for v in m.values()):
        m["invalid_evaluation_rows"]+=1.0
    return {"schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,"metrics":m,"cells":cells}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--transfer-root",required=True);p.add_argument("--third-root",required=True)
    p.add_argument("--fourth-root",required=True);p.add_argument("--fifth-root",required=True);p.add_argument("--out",required=True)
    a=p.parse_args()
    with open(a.out,"w",encoding="utf-8",newline="\n") as f:
        json.dump(run(a.transfer_root,a.third_root,a.fourth_root,a.fifth_root),f,allow_nan=False,separators=(",",":"),sort_keys=True)

if __name__=="__main__":
    main()
