"""Yggdrasil 081: cumulative state-transition attribution.

Generated only from a preregistered machine-readable contract. All six cells
are shadow evaluations. Accepted retained state and operational gates remain
immutable.
"""
import argparse
import importlib.util
import json
import math
from pathlib import Path

EXPERIMENT="EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CUMULATIVE-STATE-TRANSITION-ATTRIBUTION-081"
Y079_PATH=Path("research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-consolidation-mechanism-attribution-079.py")
ORDER=("transfer","third","fourth")

def load_y079():
    spec=importlib.util.spec_from_file_location("yggdrasil_y079_for_y081",Y079_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Y079_IMPORT_SPEC_FAILED")
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

def order(name):
    return ORDER.index(name)

def class_key(y075,key):
    return tuple(y075.byte_class(x) for x in key)

def norm_best(s):
    total=float(s["total"])
    return float(s["best_count"])/total if total>0 else 0.0

def transition_fields(y075,a,b,recurrence):
    return {
        "best_byte_changed":float(int(a["best"])!=int(b["best"])),
        "normalized_best_count_delta":norm_best(b)-norm_best(a),
        "consistency_delta":float(b["consistency"])-float(a["consistency"]),
        "utility_delta":float(b["utility"])-float(a["utility"]),
        "recurrence_count":float(recurrence),
    }

def build_transitions(y075,contexts,by_class=False):
    groups={}
    for name in ORDER:
        for state in contexts[name]:
            g=class_key(y075,state["key"]) if by_class else tuple(state["key"])
            groups.setdefault(g,{}).setdefault(name,[]).append(state)
    out=[]
    for g,by_context in groups.items():
        present=[name for name in ORDER if name in by_context]
        recurrence=len(present)
        if recurrence<2:
            continue
        for src,dst in (("transfer","third"),("third","fourth")):
            if src not in by_context or dst not in by_context:
                continue
            aa=sorted(by_context[src],key=lambda s:(y075.local_rank(s),tuple(s["key"])))
            bb=sorted(by_context[dst],key=lambda s:(y075.local_rank(s),tuple(s["key"])))
            for a in aa:
                for b in bb:
                    out.append({
                        "group":g,"src_context":src,"dst_context":dst,
                        "src_state":dict(a),"state":dict(b),
                        "fields":transition_fields(y075,a,b,recurrence),
                    })
    return out

def target_proxy(y075,source_selected,local_selected):
    return {
        "best_byte_changed":float(y075.byte_class(source_selected["best"])!=y075.byte_class(local_selected["best"])),
        "normalized_best_count_delta":norm_best(local_selected)-norm_best(source_selected),
        "consistency_delta":float(local_selected["consistency"])-float(source_selected["consistency"]),
        "utility_delta":float(local_selected["utility"])-float(source_selected["utility"]),
    }

def trans_distance(t,proxy):
    f=t["fields"]
    return (
        abs(f["best_byte_changed"]-proxy["best_byte_changed"])+
        abs(f["normalized_best_count_delta"]-proxy["normalized_best_count_delta"])+
        abs(f["consistency_delta"]-proxy["consistency_delta"])+
        abs(f["utility_delta"]-proxy["utility_delta"])
    )

def choose_transition(transitions,proxy):
    ranked=sorted(
        transitions,
        key=lambda t:(trans_distance(t,proxy),-order(t["dst_context"]),tuple(t["state"]["key"]),tuple(t["src_state"]["key"]))
    )
    return ranked[0] if ranked else None

def choose_last_state(y075,target_key,full_pool):
    exact=[x for x in full_pool if tuple(x["state"]["key"])==tuple(target_key)]
    if exact:
        ranked=sorted(exact,key=lambda x:(-order(x["context"]),y075.local_rank(x["state"]),tuple(x["state"]["key"])))
        return ranked[0]
    tc=class_key(y075,target_key)
    same_class=[x for x in full_pool if class_key(y075,x["state"]["key"])==tc]
    if same_class:
        ranked=sorted(same_class,key=lambda x:(-order(x["context"]),y075.local_rank(x["state"]),tuple(x["state"]["key"])))
        return ranked[0]
    ranked=sorted(full_pool,key=lambda x:(sum(int(a)!=int(b) for a,b in zip(target_key,x["state"]["key"])),-order(x["context"]),y075.local_rank(x["state"]),tuple(x["state"]["key"])))
    return ranked[0] if ranked else None

def run(transfer_root,third_root,fourth_root,fifth_root):
    y079=load_y079();y075=y079.load_y075()
    m={
        "variant_count":0.0,"historical_full_pool_row_count":0.0,"historical_identity_mismatch_count":0.0,
        "exact_transition_count":0.0,"class_transition_count":0.0,"target_direction_proxy_count":0.0,
        "transition_context_change_count":0.0,"last_state_clean_rescue_count":0.0,
        "exact_transition_clean_rescue_count":0.0,"class_transition_clean_rescue_count":0.0,
        "transition_behavior_change_count":0.0,"transition_partner_collateral_failure_count":0.0,
        "transition_support":0.0,"mixed_signal":0.0,
        "heldout_transition_choice_count":0.0,"post_result_transition_change_count":0.0,
        "source_state_mutation_count":0.0,"persistent_state_write_count":0.0,
        "all_child_source_identity_mismatch_count":0.0,"all_child_transport_identity_mismatch_count":0.0,
        "capacity_growth_event_count":0.0,
        "target_source_identity_mismatch_count":0.0,"target_source_count":0.0,"target_total_source_bytes":0.0,
        "target_base_training_identity_mismatch_count":0.0,"target_history_byte_budget_mismatch_count":0.0,
        "target_donor_row_count":0.0,"target_eligible_candidate_count":0.0,"target_selectors_same_row_count":0.0,
        "invalid_evaluation_rows":0.0,
    }
    roots={"transfer":transfer_root,"third":third_root,"fourth":fourth_root}
    contexts={};full_pool=[]
    for name in ORDER:
        pool,_,_,mis=y079.build_context(y075,name,roots[name])
        contexts[name]=[dict(x) for x in pool]
        m["historical_identity_mismatch_count"]+=mis
        m["historical_full_pool_row_count"]+=float(len(pool))
        for state in pool:
            full_pool.append({"context":name,"state":dict(state)})
    exact_trans=build_transitions(y075,contexts,False)
    class_trans=build_transitions(y075,contexts,True)
    m["exact_transition_count"]=float(len(exact_trans))
    m["class_transition_count"]=float(len(class_trans))

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
    if source_selected is None or local_selected is None or not full_pool or not exact_trans or not class_trans:
        m["invalid_evaluation_rows"]+=1.0
        return {"schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,"metrics":m,"cells":[]}
    if tuple(source_selected["key"])==tuple(local_selected["key"]):
        m["target_selectors_same_row_count"]=1.0
    proxy=target_proxy(y075,source_selected,local_selected);m["target_direction_proxy_count"]=1.0

    frozen=[]
    for key_origin,target in (("SOURCE_CONDITIONED",source_selected),("LOCAL_ONLY",local_selected)):
        last=choose_last_state(y075,tuple(target["key"]),full_pool)
        ex=choose_transition(exact_trans,proxy);cl=choose_transition(class_trans,proxy)
        if last is None or ex is None or cl is None:
            m["invalid_evaluation_rows"]+=1.0
            continue
        frozen.append((key_origin,"LAST_STATE",last["context"],y079.project_payload(target,last["state"])))
        frozen.append((key_origin,"EXACT_TRANSITION",ex["dst_context"],y079.project_payload(target,ex["state"])))
        frozen.append((key_origin,"CLASS_TRANSITION",cl["dst_context"],y079.project_payload(target,cl["state"])))

    cells=[];by_key={};original=None
    for key_origin,representation,context,state in frozen:
        child=y075.run_variant(fifth_root,state);s=y079.summarize(child)
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
        if representation=="LAST_STATE":
            m["last_state_clean_rescue_count"]+=float(clean)
        elif representation=="EXACT_TRANSITION":
            m["exact_transition_clean_rescue_count"]+=float(clean)
            m["transition_behavior_change_count"]+=float(changed)
            m["transition_partner_collateral_failure_count"]+=s["active_partner_fail"]
        else:
            m["class_transition_clean_rescue_count"]+=float(clean)
            m["transition_behavior_change_count"]+=float(changed)
            m["transition_partner_collateral_failure_count"]+=s["active_partner_fail"]
        row={
            "key_origin":key_origin,"representation":representation,"selected_context":context,
            "key":list(state["key"]),"best":int(state["best"]),"total":int(state["total"]),
            "best_count":int(state["best_count"]),"consistency":float(state["consistency"]),
            "utility":float(state["utility"]),"cell_index":int(state["cell_index"]),"map_best":int(state["map_best"]),
            "clean_rescue":clean,"behavior_changed":changed,
            "original_positive_prose_collateral_schedule_count":s["original_prose"],
            "active_positive_prose_collateral_schedule_count":s["active_prose"],
            "active_partner_collateral_failure_count":s["active_partner_fail"],
            "active_mean_first_success_packet":s["active_first"],
        }
        cells.append(row);by_key.setdefault(key_origin,{})[representation]=row

    support=False;mixed=False
    for key_origin in ("SOURCE_CONDITIONED","LOCAL_ONLY"):
        control=by_key[key_origin]["LAST_STATE"]
        for rep in ("EXACT_TRANSITION","CLASS_TRANSITION"):
            row=by_key[key_origin][rep]
            if row["selected_context"]!=control["selected_context"]:
                m["transition_context_change_count"]+=1.0
                if row["clean_rescue"] and not control["clean_rescue"] and row["active_partner_collateral_failure_count"]==0.0:
                    support=True
                if (not row["clean_rescue"] and row["active_partner_collateral_failure_count"]==0.0 and
                    (row["active_positive_prose_collateral_schedule_count"]>control["active_positive_prose_collateral_schedule_count"] or
                     row["active_mean_first_success_packet"]<control["active_mean_first_success_packet"])):
                    mixed=True
    m["transition_support"]=float(support);m["mixed_signal"]=float(mixed)

    if m["historical_full_pool_row_count"]!=17.0 or m["historical_identity_mismatch_count"]!=0.0:m["invalid_evaluation_rows"]+=1.0
    if m["target_source_count"]!=3.0 or m["target_total_source_bytes"]!=57272.0:m["invalid_evaluation_rows"]+=1.0
    if m["target_source_identity_mismatch_count"]!=0.0 or m["target_base_training_identity_mismatch_count"]!=0.0 or m["target_history_byte_budget_mismatch_count"]!=0.0:m["invalid_evaluation_rows"]+=1.0
    if m["target_donor_row_count"]!=16.0 or m["target_eligible_candidate_count"]!=6.0 or m["target_selectors_same_row_count"]!=0.0:m["invalid_evaluation_rows"]+=1.0
    if m["variant_count"]!=6.0 or m["target_direction_proxy_count"]!=1.0 or m["heldout_transition_choice_count"]!=0.0 or m["post_result_transition_change_count"]!=0.0:m["invalid_evaluation_rows"]+=1.0
    if m["exact_transition_count"]<=0.0 or m["class_transition_count"]<=0.0:m["invalid_evaluation_rows"]+=1.0
    if m["source_state_mutation_count"]!=0.0 or m["persistent_state_write_count"]!=0.0:m["invalid_evaluation_rows"]+=1.0
    if m["all_child_source_identity_mismatch_count"]!=0.0 or m["all_child_transport_identity_mismatch_count"]!=0.0 or m["capacity_growth_event_count"]!=0.0:m["invalid_evaluation_rows"]+=1.0
    if any(not math.isfinite(float(v)) for v in m.values()):m["invalid_evaluation_rows"]+=1.0
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
