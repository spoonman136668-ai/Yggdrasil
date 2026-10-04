"""Yggdrasil 080: cumulative consolidation dynamics attribution.

Generated only from a preregistered machine-readable contract. All six cells
are shadow evaluations. Accepted retained state and operational gates remain
immutable.
"""
import argparse
import importlib.util
import json
import math
from pathlib import Path

EXPERIMENT="EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONSOLIDATION-DYNAMICS-ATTRIBUTION-080"
Y079_PATH=Path("research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-consolidation-mechanism-attribution-079.py")


def load_y079():
    spec=importlib.util.spec_from_file_location("yggdrasil_y079_for_y080",Y079_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Y079_IMPORT_SPEC_FAILED")
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def class_key(y075,key):
    return tuple(y075.byte_class(int(x)) for x in key)


def aggregate_groups(y075,full_pool,by_class=False):
    grouped={}
    for item in full_pool:
        state=item["state"]
        g=class_key(y075,state["key"]) if by_class else tuple(state["key"])
        grouped.setdefault(g,[]).append(item)
    out=[]
    multi=0
    for g,members in grouped.items():
        contexts=sorted({x["context"] for x in members},key=lambda x:y079_order(x))
        if len(contexts)<2:
            continue
        multi+=1
        totals=sum(int(x["state"]["total"]) for x in members)
        evidence={}
        for x in members:
            s=x["state"]
            evidence[int(s["best"])]=evidence.get(int(s["best"]),0)+int(s["best_count"])
        best=min(evidence,key=lambda b:(-evidence[b],b))
        best_count=evidence[best]
        consistency=(float(best_count)/float(totals)) if totals>0 else 0.0
        anchors=sorted(tuple(int(v) for v in x["state"]["key"]) for x in members)
        anchor=anchors[0]
        state={
            "key":anchor,
            "best":best,
            "total":totals,
            "best_count":best_count,
            "consistency":consistency,
            "utility":float(best_count)*consistency,
            "cell_index":min(int(x["state"]["cell_index"]) for x in members),
            "map_best":best,
        }
        out.append({"group":g,"contexts":contexts,"state":state})
    return out,multi


def y079_order(name):
    return ("transfer","third","fourth").index(name)


def retrieve_exact(y079,target_key,groups):
    ranked=sorted(groups,key=lambda x:(y079.hamming(target_key,x["state"]["key"]),tuple(x["state"]["key"])))
    return ranked[0] if ranked else None


def class_hamming(y075,a,b):
    aa=class_key(y075,a);bb=class_key(y075,b)
    return sum(int(x)!=int(y) for x,y in zip(aa,bb))


def retrieve_class(y075,target_key,groups):
    ranked=sorted(groups,key=lambda x:(class_hamming(y075,target_key,x["state"]["key"]),tuple(x["state"]["key"])))
    return ranked[0] if ranked else None


def run(transfer_root,third_root,fourth_root,fifth_root):
    y079=load_y079()
    y075=y079.load_y075()
    m={
        "variant_count":0.0,
        "historical_full_pool_row_count":0.0,
        "historical_identity_mismatch_count":0.0,
        "exact_key_group_count":0.0,
        "class_key_group_count":0.0,
        "multi_context_exact_group_count":0.0,
        "multi_context_class_group_count":0.0,
        "full_pool_clean_rescue_count":0.0,
        "exact_key_accumulation_clean_rescue_count":0.0,
        "class_key_accumulation_clean_rescue_count":0.0,
        "accumulation_behavior_change_count":0.0,
        "accumulation_partner_collateral_failure_count":0.0,
        "consolidation_support":0.0,
        "mixed_signal":0.0,
        "heldout_consolidation_choice_count":0.0,
        "post_result_consolidation_change_count":0.0,
        "source_state_mutation_count":0.0,
        "persistent_state_write_count":0.0,
        "all_child_source_identity_mismatch_count":0.0,
        "all_child_transport_identity_mismatch_count":0.0,
        "capacity_growth_event_count":0.0,
        "target_source_identity_mismatch_count":0.0,
        "target_source_count":0.0,
        "target_total_source_bytes":0.0,
        "target_base_training_identity_mismatch_count":0.0,
        "target_history_byte_budget_mismatch_count":0.0,
        "target_donor_row_count":0.0,
        "target_eligible_candidate_count":0.0,
        "target_selectors_same_row_count":0.0,
        "invalid_evaluation_rows":0.0,
    }
    roots={"transfer":transfer_root,"third":third_root,"fourth":fourth_root}
    full_pool=[]
    for name in y079.HISTORICAL_ORDER:
        pool,_,_,mis=y079.build_context(y075,name,roots[name])
        m["historical_identity_mismatch_count"]+=mis
        m["historical_full_pool_row_count"]+=float(len(pool))
        for state in pool:
            full_pool.append({"context":name,"state":dict(state)})
    exact_groups,exact_multi=aggregate_groups(y075,full_pool,False)
    class_groups,class_multi=aggregate_groups(y075,full_pool,True)
    m["exact_key_group_count"]=float(len(exact_groups))
    m["class_key_group_count"]=float(len(class_groups))
    m["multi_context_exact_group_count"]=float(exact_multi)
    m["multi_context_class_group_count"]=float(class_multi)

    y075.TARGET_SOURCES={k:dict(v) for k,v in y079.SOURCES["fifth"].items()}
    tm=y079.builder_metrics()
    target_pool=list(y075.build_pool(fifth_root,tm))
    source_selected=sorted(target_pool,key=y075.source_rank)[0] if target_pool else None
    local_selected=sorted(target_pool,key=y075.local_rank)[0] if target_pool else None
    m["target_source_identity_mismatch_count"]=tm["target_source_identity_mismatch_count"]
    m["target_source_count"]=tm["target_source_count"]
    m["target_total_source_bytes"]=tm["target_total_source_bytes"]
    m["target_base_training_identity_mismatch_count"]=tm["base_training_identity_mismatch_count"]
    m["target_history_byte_budget_mismatch_count"]=tm["history_byte_budget_mismatch_count"]
    m["target_donor_row_count"]=tm["donor_row_count"]
    m["target_eligible_candidate_count"]=tm["eligible_candidate_count"]
    m["invalid_evaluation_rows"]+=tm["invalid_evaluation_rows"]
    if source_selected is None or local_selected is None or not full_pool or not exact_groups or not class_groups:
        m["invalid_evaluation_rows"]+=1.0
        return {"schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,"metrics":m,"cells":[]}
    if tuple(source_selected["key"])==tuple(local_selected["key"]):
        m["target_selectors_same_row_count"]=1.0

    frozen=[]
    for key_origin,target in (("SOURCE_CONDITIONED",source_selected),("LOCAL_ONLY",local_selected)):
        _,dist,full_state=y079.retrieve_full(y075,tuple(target["key"]),full_pool)
        frozen.append((key_origin,"FULL_ELIGIBLE_POOL",y079.project_payload(target,full_state),dist))
        eg=retrieve_exact(y079,tuple(target["key"]),exact_groups)
        cg=retrieve_class(y075,tuple(target["key"]),class_groups)
        frozen.append((key_origin,"EXACT_KEY_ACCUMULATION",y079.project_payload(target,eg["state"]),y079.hamming(tuple(target["key"]),eg["state"]["key"])))
        frozen.append((key_origin,"CLASS_KEY_ACCUMULATION",y079.project_payload(target,cg["state"]),class_hamming(y075,tuple(target["key"]),cg["state"]["key"])))

    cells=[]
    by_key={}
    original=None
    for key_origin,representation,state,distance in frozen:
        child=y075.run_variant(fifth_root,state)
        s=y079.summarize(child)
        cur=(s["original_prose"],s["original_partner_fail"],s["original_first"])
        if original is None: original=cur
        elif cur!=original: m["invalid_evaluation_rows"]+=1.0
        clean=s["active_prose"]>s["original_prose"] and s["active_partner_fail"]==0.0
        changed=y079.behavior_changed(child)
        m["variant_count"]+=1.0
        m["all_child_source_identity_mismatch_count"]+=s["source_mismatch"]
        m["all_child_transport_identity_mismatch_count"]+=s["transport_mismatch"]
        m["capacity_growth_event_count"]+=s["capacity_growth"]
        m["invalid_evaluation_rows"]+=s["invalid"]
        if representation=="FULL_ELIGIBLE_POOL":
            m["full_pool_clean_rescue_count"]+=float(clean)
        elif representation=="EXACT_KEY_ACCUMULATION":
            m["exact_key_accumulation_clean_rescue_count"]+=float(clean)
            m["accumulation_behavior_change_count"]+=float(changed)
            m["accumulation_partner_collateral_failure_count"]+=s["active_partner_fail"]
        else:
            m["class_key_accumulation_clean_rescue_count"]+=float(clean)
            m["accumulation_behavior_change_count"]+=float(changed)
            m["accumulation_partner_collateral_failure_count"]+=s["active_partner_fail"]
        row={
            "key_origin":key_origin,"representation":representation,"key":list(state["key"]),
            "best":int(state["best"]),"total":int(state["total"]),"best_count":int(state["best_count"]),
            "consistency":float(state["consistency"]),"utility":float(state["utility"]),
            "cell_index":int(state["cell_index"]),"map_best":int(state["map_best"]),
            "distance":distance,"clean_rescue":clean,"behavior_changed":changed,
            "original_positive_prose_collateral_schedule_count":s["original_prose"],
            "active_positive_prose_collateral_schedule_count":s["active_prose"],
            "active_partner_collateral_failure_count":s["active_partner_fail"],
            "active_mean_first_success_packet":s["active_first"],
        }
        cells.append(row);by_key.setdefault(key_origin,{})[representation]=row

    support=False;mixed=False
    for key_origin in ("SOURCE_CONDITIONED","LOCAL_ONLY"):
        control=by_key[key_origin]["FULL_ELIGIBLE_POOL"]
        for rep in ("EXACT_KEY_ACCUMULATION","CLASS_KEY_ACCUMULATION"):
            row=by_key[key_origin][rep]
            if row["clean_rescue"] and not control["clean_rescue"]:
                support=True
            if (not row["clean_rescue"] and row["active_partner_collateral_failure_count"]==0.0 and
                (row["active_positive_prose_collateral_schedule_count"]>control["active_positive_prose_collateral_schedule_count"] or
                 row["active_mean_first_success_packet"]<control["active_mean_first_success_packet"])):
                mixed=True
    m["consolidation_support"]=float(support)
    m["mixed_signal"]=float(mixed)

    if m["historical_full_pool_row_count"]!=17.0 or m["historical_identity_mismatch_count"]!=0.0:
        m["invalid_evaluation_rows"]+=1.0
    if m["target_source_count"]!=3.0 or m["target_total_source_bytes"]!=57272.0:
        m["invalid_evaluation_rows"]+=1.0
    if m["target_source_identity_mismatch_count"]!=0.0 or m["target_base_training_identity_mismatch_count"]!=0.0 or m["target_history_byte_budget_mismatch_count"]!=0.0:
        m["invalid_evaluation_rows"]+=1.0
    if m["target_donor_row_count"]!=16.0 or m["target_eligible_candidate_count"]!=6.0 or m["target_selectors_same_row_count"]!=0.0:
        m["invalid_evaluation_rows"]+=1.0
    if m["variant_count"]!=6.0 or m["heldout_consolidation_choice_count"]!=0.0 or m["post_result_consolidation_change_count"]!=0.0:
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
    p.add_argument("--fourth-root",required=True);p.add_argument("--fifth-root",required=True)
    p.add_argument("--out",required=True);a=p.parse_args()
    r=run(a.transfer_root,a.third_root,a.fourth_root,a.fifth_root)
    with open(a.out,"w",encoding="utf-8",newline="\n") as f:
        json.dump(r,f,allow_nan=False,separators=(",",":"),sort_keys=True)


if __name__=="__main__":
    main()
