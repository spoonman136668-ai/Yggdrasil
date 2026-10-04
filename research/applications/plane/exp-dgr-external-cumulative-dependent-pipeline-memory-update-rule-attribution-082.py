"""Yggdrasil 082: cumulative memory update-rule attribution."""
import argparse,importlib.util,json,math
from pathlib import Path
EXPERIMENT="EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-MEMORY-UPDATE-RULE-ATTRIBUTION-082"
Y080_PATH=Path("research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-consolidation-dynamics-attribution-080.py")
ORDER=("transfer","third","fourth")

def load_y080():
    spec=importlib.util.spec_from_file_location("yggdrasil_y080_for_y082",Y080_PATH)
    if spec is None or spec.loader is None: raise RuntimeError("Y080_IMPORT_SPEC_FAILED")
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

def recency_class_groups(y080,y075,full_pool):
    acc={}
    for ci,context in enumerate(ORDER):
        if ci>0:
            for a in acc.values():
                a["total"]*=0.5
                for b in list(a["evidence"]): a["evidence"][b]*=0.5
        for item in full_pool:
            if item["context"]!=context: continue
            s=item["state"];g=y080.class_key(y075,s["key"])
            a=acc.setdefault(g,{"total":0.0,"evidence":{},"contexts":set(),"anchors":[],"cell_index":int(s["cell_index"])})
            a["contexts"].add(context);a["anchors"].append(tuple(int(v) for v in s["key"]))
            a["cell_index"]=min(a["cell_index"],int(s["cell_index"]))
            a["total"]+=float(s["total"]);best=int(s["best"])
            a["evidence"][best]=a["evidence"].get(best,0.0)+float(s["best_count"])
    out=[]
    for g,a in acc.items():
        contexts=sorted(a["contexts"],key=lambda x:ORDER.index(x))
        if len(contexts)<2 or not a["evidence"] or a["total"]<=0: continue
        best=min(a["evidence"],key=lambda b:(-a["evidence"][b],b))
        bc=float(a["evidence"][best]);total=float(a["total"]);cons=bc/total
        out.append({"group":g,"contexts":contexts,"state":{"key":sorted(a["anchors"])[0],"best":best,"total":total,
            "best_count":bc,"consistency":cons,"utility":bc*cons,"cell_index":a["cell_index"],"map_best":best}})
    return out

def payload_changed(a,b):
    if int(a["best"])!=int(b["best"]) or int(a["cell_index"])!=int(b["cell_index"]) or int(a["map_best"])!=int(b["map_best"]): return True
    return any(abs(float(a[k])-float(b[k]))>1e-12 for k in ("total","best_count","consistency","utility"))

def run(transfer_root,third_root,fourth_root,fifth_root):
    y080=load_y080();y079=y080.load_y079();y075=y079.load_y075()
    names=("variant_count","historical_full_pool_row_count","historical_identity_mismatch_count","class_group_count",
      "multi_context_class_group_count","uniform_clean_rescue_count","recency_half_clean_rescue_count",
      "recency_half_behavior_change_count","recency_half_partner_collateral_failure_count",
      "recency_half_selected_payload_change_count","update_support","mixed_signal","heldout_update_choice_count",
      "post_result_update_change_count","source_state_mutation_count","persistent_state_write_count",
      "all_child_source_identity_mismatch_count","all_child_transport_identity_mismatch_count",
      "capacity_growth_event_count","target_source_identity_mismatch_count","target_source_count","target_total_source_bytes",
      "target_base_training_identity_mismatch_count","target_history_byte_budget_mismatch_count","target_donor_row_count",
      "target_eligible_candidate_count","target_selectors_same_row_count","invalid_evaluation_rows")
    m={k:0.0 for k in names}
    roots={"transfer":transfer_root,"third":third_root,"fourth":fourth_root};full_pool=[]
    for name in ORDER:
        pool,_,_,mis=y079.build_context(y075,name,roots[name]);m["historical_identity_mismatch_count"]+=mis
        m["historical_full_pool_row_count"]+=float(len(pool));full_pool.extend({"context":name,"state":dict(s)} for s in pool)
    ugroups,umulti=y080.aggregate_groups(y075,full_pool,True);rgroups=recency_class_groups(y080,y075,full_pool)
    m["class_group_count"]=float(len(ugroups));m["multi_context_class_group_count"]=float(umulti)
    if {tuple(x["group"]) for x in ugroups}!={tuple(x["group"]) for x in rgroups}: m["invalid_evaluation_rows"]+=1.0

    y075.TARGET_SOURCES={k:dict(v) for k,v in y079.SOURCES["fifth"].items()}
    tm=y079.builder_metrics();target_pool=list(y075.build_pool(fifth_root,tm))
    src=sorted(target_pool,key=y075.source_rank)[0] if target_pool else None;loc=sorted(target_pool,key=y075.local_rank)[0] if target_pool else None
    m["target_source_identity_mismatch_count"]=tm["target_source_identity_mismatch_count"];m["target_source_count"]=tm["target_source_count"]
    m["target_total_source_bytes"]=tm["target_total_source_bytes"];m["target_base_training_identity_mismatch_count"]=tm["base_training_identity_mismatch_count"]
    m["target_history_byte_budget_mismatch_count"]=tm["history_byte_budget_mismatch_count"];m["target_donor_row_count"]=tm["donor_row_count"]
    m["target_eligible_candidate_count"]=tm["eligible_candidate_count"];m["invalid_evaluation_rows"]+=tm["invalid_evaluation_rows"]
    if src is None or loc is None or not ugroups or not rgroups:
        m["invalid_evaluation_rows"]+=1.0;return {"schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,"metrics":m,"cells":[]}
    if tuple(src["key"])==tuple(loc["key"]): m["target_selectors_same_row_count"]=1.0

    frozen=[]
    for ko,target in (("SOURCE_CONDITIONED",src),("LOCAL_ONLY",loc)):
        u=y080.retrieve_class(y075,tuple(target["key"]),ugroups);r=y080.retrieve_class(y075,tuple(target["key"]),rgroups)
        if u is None or r is None or tuple(u["group"])!=tuple(r["group"]): m["invalid_evaluation_rows"]+=1.0;continue
        if payload_changed(u["state"],r["state"]): m["recency_half_selected_payload_change_count"]+=1.0
        frozen.append((ko,"CLASS_UNIFORM_ACCUMULATION",y079.project_payload(target,u["state"]),y080.class_hamming(y075,tuple(target["key"]),u["state"]["key"])))
        frozen.append((ko,"CLASS_RECENCY_HALF_UPDATE",y079.project_payload(target,r["state"]),y080.class_hamming(y075,tuple(target["key"]),r["state"]["key"])))

    cells=[];by={};original=None
    for ko,rep,state,distance in frozen:
        child=y075.run_variant(fifth_root,state);s=y079.summarize(child);cur=(s["original_prose"],s["original_partner_fail"],s["original_first"])
        if original is None: original=cur
        elif cur!=original: m["invalid_evaluation_rows"]+=1.0
        clean=s["active_prose"]>s["original_prose"] and s["active_partner_fail"]==0.0;changed=y079.behavior_changed(child)
        m["variant_count"]+=1.0;m["all_child_source_identity_mismatch_count"]+=s["source_mismatch"]
        m["all_child_transport_identity_mismatch_count"]+=s["transport_mismatch"];m["capacity_growth_event_count"]+=s["capacity_growth"];m["invalid_evaluation_rows"]+=s["invalid"]
        if rep=="CLASS_UNIFORM_ACCUMULATION": m["uniform_clean_rescue_count"]+=float(clean)
        else:
            m["recency_half_clean_rescue_count"]+=float(clean);m["recency_half_behavior_change_count"]+=float(changed)
            m["recency_half_partner_collateral_failure_count"]+=s["active_partner_fail"]
        row={"key_origin":ko,"representation":rep,"key":list(state["key"]),"best":int(state["best"]),"total":float(state["total"]),
          "best_count":float(state["best_count"]),"consistency":float(state["consistency"]),"utility":float(state["utility"]),
          "cell_index":int(state["cell_index"]),"map_best":int(state["map_best"]),"distance":int(distance),"clean_rescue":clean,
          "behavior_changed":changed,"original_positive_prose_collateral_schedule_count":s["original_prose"],
          "active_positive_prose_collateral_schedule_count":s["active_prose"],"active_partner_collateral_failure_count":s["active_partner_fail"],
          "active_mean_first_success_packet":s["active_first"]}
        cells.append(row);by.setdefault(ko,{})[rep]=row
    support=False;mixed=False
    for ko in ("SOURCE_CONDITIONED","LOCAL_ONLY"):
        c=by.get(ko,{}).get("CLASS_UNIFORM_ACCUMULATION");r=by.get(ko,{}).get("CLASS_RECENCY_HALF_UPDATE")
        if c is None or r is None: m["invalid_evaluation_rows"]+=1.0;continue
        if r["clean_rescue"] and not c["clean_rescue"] and r["active_partner_collateral_failure_count"]==0.0: support=True
        if (not r["clean_rescue"] and r["active_partner_collateral_failure_count"]==0.0 and
            (r["active_positive_prose_collateral_schedule_count"]>c["active_positive_prose_collateral_schedule_count"] or
             r["active_mean_first_success_packet"]<c["active_mean_first_success_packet"])): mixed=True
    m["update_support"]=float(support);m["mixed_signal"]=float(mixed)
    if m["historical_full_pool_row_count"]!=17.0 or m["historical_identity_mismatch_count"]!=0.0: m["invalid_evaluation_rows"]+=1.0
    if m["target_source_count"]!=3.0 or m["target_total_source_bytes"]!=57272.0: m["invalid_evaluation_rows"]+=1.0
    if m["target_source_identity_mismatch_count"]!=0.0 or m["target_base_training_identity_mismatch_count"]!=0.0 or m["target_history_byte_budget_mismatch_count"]!=0.0: m["invalid_evaluation_rows"]+=1.0
    if m["target_donor_row_count"]!=16.0 or m["target_eligible_candidate_count"]!=6.0 or m["target_selectors_same_row_count"]!=0.0: m["invalid_evaluation_rows"]+=1.0
    if m["variant_count"]!=4.0 or m["heldout_update_choice_count"]!=0.0 or m["post_result_update_change_count"]!=0.0: m["invalid_evaluation_rows"]+=1.0
    if m["source_state_mutation_count"]!=0.0 or m["persistent_state_write_count"]!=0.0: m["invalid_evaluation_rows"]+=1.0
    if m["all_child_source_identity_mismatch_count"]!=0.0 or m["all_child_transport_identity_mismatch_count"]!=0.0 or m["capacity_growth_event_count"]!=0.0: m["invalid_evaluation_rows"]+=1.0
    if any(not math.isfinite(float(v)) for v in m.values()): m["invalid_evaluation_rows"]+=1.0
    return {"schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,"metrics":m,"cells":cells}

def main():
    p=argparse.ArgumentParser();p.add_argument("--transfer-root",required=True);p.add_argument("--third-root",required=True)
    p.add_argument("--fourth-root",required=True);p.add_argument("--fifth-root",required=True);p.add_argument("--out",required=True);a=p.parse_args()
    with open(a.out,"w",encoding="utf-8",newline="\n") as f: json.dump(run(a.transfer_root,a.third_root,a.fourth_root,a.fifth_root),f,allow_nan=False,separators=(",",":"),sort_keys=True)
if __name__=="__main__": main()
