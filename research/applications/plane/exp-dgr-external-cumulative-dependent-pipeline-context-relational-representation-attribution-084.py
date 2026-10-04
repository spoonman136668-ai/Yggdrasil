"""Yggdrasil 084: context-relational representation attribution."""
import argparse,importlib.util,json,math
from pathlib import Path
EXPERIMENT="EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-RELATIONAL-REPRESENTATION-ATTRIBUTION-084"
Y080_PATH=Path("research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-consolidation-dynamics-attribution-080.py")
ORDER=("transfer","third","fourth")

def load_y080():
    spec=importlib.util.spec_from_file_location("yggdrasil_y080_for_y084",Y080_PATH)
    if spec is None or spec.loader is None: raise RuntimeError("Y080_IMPORT_SPEC_FAILED")
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

def exact_hamming(a,b):
    aa=tuple(int(v) for v in a);bb=tuple(int(v) for v in b)
    if len(aa)!=4 or len(bb)!=4: raise ValueError("EXACT_KEY_LENGTH_MISMATCH")
    return sum(x!=y for x,y in zip(aa,bb))

def relational_retrieve(y080,y075,target_key,groups,full_pool,m):
    target=tuple(int(v) for v in target_key);scored=[]
    for g in groups:
        group=tuple(g["group"]);distances=[]
        for context in ORDER:
            members=[item for item in full_pool if item["context"]==context and tuple(y080.class_key(y075,item["state"]["key"]))==group]
            if not members: continue
            distances.append(min(exact_hamming(target,item["state"]["key"]) for item in members))
        if len(distances)<2:
            m["invalid_evaluation_rows"]+=1.0
            continue
        scored.append((max(distances),sum(distances),group,g))
    if not scored: return None
    scored.sort(key=lambda row:(row[0],row[1],row[2]))
    return scored[0][3]

def run(transfer_root,third_root,fourth_root,fifth_root):
    y080=load_y080();y079=y080.load_y079();y075=y079.load_y075()
    names=("variant_count","historical_full_pool_row_count","historical_identity_mismatch_count","class_group_count",
      "multi_context_class_group_count","relational_candidate_class_count","relational_selected_class_change_count",
      "control_clean_rescue_count","relational_clean_rescue_count","relational_behavior_change_count",
      "relational_partner_collateral_failure_count","lost_control_clean_rescue_count","relational_support","mixed_signal",
      "heldout_relation_choice_count","post_result_relation_change_count","source_state_mutation_count",
      "persistent_state_write_count","all_child_source_identity_mismatch_count","all_child_transport_identity_mismatch_count",
      "capacity_growth_event_count","target_source_identity_mismatch_count","target_source_count","target_total_source_bytes",
      "target_base_training_identity_mismatch_count","target_history_byte_budget_mismatch_count","target_donor_row_count",
      "target_eligible_candidate_count","target_selectors_same_row_count","invalid_evaluation_rows")
    m={k:0.0 for k in names}
    roots={"transfer":transfer_root,"third":third_root,"fourth":fourth_root};full_pool=[]
    for name in ORDER:
        pool,_,_,mis=y079.build_context(y075,name,roots[name]);m["historical_identity_mismatch_count"]+=mis
        m["historical_full_pool_row_count"]+=float(len(pool));full_pool.extend({"context":name,"state":dict(s)} for s in pool)
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
      ("invalid_evaluation_rows","invalid_evaluation_rows")): m[dst]+=float(tm[key])
    if src is None or loc is None or not groups:
        m["invalid_evaluation_rows"]+=1.0
        return {"schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,"metrics":m,"cells":[]}
    if tuple(src["key"])==tuple(loc["key"]): m["target_selectors_same_row_count"]=1.0

    cells=[];by={}
    for ko,target in (("SOURCE_CONDITIONED",src),("LOCAL_ONLY",loc)):
        control=y080.retrieve_class(y075,tuple(target["key"]),groups)
        relation=relational_retrieve(y080,y075,tuple(target["key"]),groups,full_pool,m)
        if control is None or relation is None:
            m["invalid_evaluation_rows"]+=1.0;continue
        changed=tuple(control["group"])!=tuple(relation["group"])
        m["relational_selected_class_change_count"]+=float(changed)
        for rep,chosen in (("REPRESENTATIVE_CLASS_HAMMING",control),("CONTEXT_MINIMAX_RELATION",relation)):
            state=y079.project_payload(target,chosen["state"])
            child=y075.run_variant(fifth_root,state);s=y079.summarize(child)
            clean=s["active_prose"]>s["original_prose"] and s["active_partner_fail"]==0.0
            behavior=y079.behavior_changed(child)
            m["variant_count"]+=1.0;m["all_child_source_identity_mismatch_count"]+=s["source_mismatch"]
            m["all_child_transport_identity_mismatch_count"]+=s["transport_mismatch"]
            m["capacity_growth_event_count"]+=s["capacity_growth"];m["invalid_evaluation_rows"]+=s["invalid"]
            if rep=="REPRESENTATIVE_CLASS_HAMMING": m["control_clean_rescue_count"]+=float(clean)
            else:
                m["relational_clean_rescue_count"]+=float(clean);m["relational_behavior_change_count"]+=float(behavior)
                m["relational_partner_collateral_failure_count"]+=s["active_partner_fail"]
            row={"key_origin":ko,"representation":rep,"selected_group":list(chosen["group"]),
              "key":list(state["key"]),"best":int(state["best"]),"clean_rescue":clean,"behavior_changed":behavior,
              "original_positive_prose_collateral_schedule_count":s["original_prose"],
              "active_positive_prose_collateral_schedule_count":s["active_prose"],
              "active_partner_collateral_failure_count":s["active_partner_fail"],
              "active_mean_first_success_packet":s["active_first"]}
            cells.append(row);by.setdefault(ko,{})[rep]=row

    support=False;mixed=False
    for ko in ("SOURCE_CONDITIONED","LOCAL_ONLY"):
        c=by.get(ko,{}).get("REPRESENTATIVE_CLASS_HAMMING");r=by.get(ko,{}).get("CONTEXT_MINIMAX_RELATION")
        if c is None or r is None: m["invalid_evaluation_rows"]+=1.0;continue
        changed=c["selected_group"]!=r["selected_group"]
        if c["clean_rescue"] and not r["clean_rescue"]: m["lost_control_clean_rescue_count"]+=1.0
        if changed and r["clean_rescue"] and not c["clean_rescue"] and r["active_partner_collateral_failure_count"]==0.0: support=True
        if (changed and not r["clean_rescue"] and r["active_partner_collateral_failure_count"]==0.0 and
            (r["active_positive_prose_collateral_schedule_count"]>c["active_positive_prose_collateral_schedule_count"] or
             r["active_mean_first_success_packet"]<c["active_mean_first_success_packet"])): mixed=True
    if m["lost_control_clean_rescue_count"]>0 or m["relational_partner_collateral_failure_count"]>0: support=False
    m["relational_support"]=float(support);m["mixed_signal"]=float(mixed and not support)

    if m["historical_full_pool_row_count"]!=17.0 or m["historical_identity_mismatch_count"]!=0.0: m["invalid_evaluation_rows"]+=1.0
    if m["class_group_count"]!=2.0 or m["multi_context_class_group_count"]!=2.0 or m["relational_candidate_class_count"]!=2.0: m["invalid_evaluation_rows"]+=1.0
    if m["target_source_count"]!=3.0 or m["target_total_source_bytes"]!=57272.0: m["invalid_evaluation_rows"]+=1.0
    if m["target_source_identity_mismatch_count"]!=0.0 or m["target_base_training_identity_mismatch_count"]!=0.0 or m["target_history_byte_budget_mismatch_count"]!=0.0: m["invalid_evaluation_rows"]+=1.0
    if m["target_donor_row_count"]!=16.0 or m["target_eligible_candidate_count"]!=6.0 or m["target_selectors_same_row_count"]!=0.0: m["invalid_evaluation_rows"]+=1.0
    if m["variant_count"]!=4.0 or m["heldout_relation_choice_count"]!=0.0 or m["post_result_relation_change_count"]!=0.0: m["invalid_evaluation_rows"]+=1.0
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
