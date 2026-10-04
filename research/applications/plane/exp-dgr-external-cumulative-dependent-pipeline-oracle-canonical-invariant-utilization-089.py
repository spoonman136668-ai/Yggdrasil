"""Yggdrasil 089: oracle-canonical invariant utilization on unseen contexts."""
import argparse,hashlib,importlib.util,json,math
from pathlib import Path

EXPERIMENT="EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-ORACLE-CANONICAL-INVARIANT-UTILIZATION-089"
Y079_PATH=Path("research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-consolidation-mechanism-attribution-079.py")
ORDER=("transfer","third","fourth")
FIELDS=("best_count","consistency","utility","cell_index")

def load_y079():
    spec=importlib.util.spec_from_file_location("yggdrasil_y079_for_y089",Y079_PATH)
    if spec is None or spec.loader is None: raise RuntimeError("Y079_IMPORT_SPEC_FAILED")
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

def cmp3(a,b):
    return -1 if a<b else 1 if a>b else 0

def ordinal(value,pool,field):
    vals=sorted(set(x[field] for x in pool))
    return vals.index(value)

def canonical_signature(state,representative,pool):
    key=tuple(state["key"]);anchor=tuple(representative["key"])
    out=[cmp3(key[i],anchor[i]) for i in range(4)]
    for i in range(4):
        for j in range(i+1,4): out.append(cmp3(key[i],key[j]))
    for field in FIELDS: out.append(ordinal(state[field],pool,field))
    out.append(cmp3(state["best"],state["map_best"]))
    return tuple(out)

def signature_distance(a,b):
    return sum(x!=y for x,y in zip(a,b))

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
    if not pool: return [],None,None,None
    rep=sorted(pool,key=y075.local_rank)[0]
    src=sorted(pool,key=y075.source_rank)[0]
    loc=sorted(pool,key=y075.local_rank)[0]
    return pool,dict(rep),dict(src),dict(loc)

def oracle_retrieve(y075,target_signature,historical):
    ranked=[]
    for item in historical:
        dist=signature_distance(target_signature,item["signature"])
        ranked.append((dist,ORDER.index(item["context"]),y075.local_rank(item["state"]),tuple(item["state"]["key"]),item))
    if not ranked: raise RuntimeError("ORACLE_RETRIEVAL_EMPTY")
    ranked.sort(key=lambda row:row[:4])
    return ranked[0][4],ranked[0][0]

def run(transfer_root,third_root,fourth_root,sixth_root,seventh_root):
    y079=load_y079();y075=y079.load_y075()
    names=(
      "historical_context_count","historical_full_pool_row_count","historical_identity_mismatch_count",
      "unseen_context_count","variant_count","control_clean_rescue_count","oracle_invariant_clean_rescue_count",
      "oracle_only_clean_rescue_count","lost_control_clean_rescue_count","oracle_selected_row_change_count",
      "oracle_changed_context_count","oracle_behavior_change_count","oracle_partner_collateral_failure_count",
      "oracle_improvement_case_count","canonical_relation_identity_mismatch_count",
      "target_source_identity_mismatch_count","target_source_count","target_total_source_bytes",
      "target_base_training_identity_mismatch_count","target_history_byte_budget_mismatch_count",
      "target_donor_row_count","target_eligible_candidate_count","target_selectors_same_row_count",
      "heldout_outcome_use_before_oracle_relation_freeze","target_context_mapping_disclosure_count",
      "target_answer_disclosure_count","post_result_relation_change_count","persistent_state_write_count",
      "all_child_source_identity_mismatch_count","all_child_transport_identity_mismatch_count",
      "capacity_growth_event_count","invalid_evaluation_rows")
    m={k:0.0 for k in names};m["historical_context_count"]=3.0;m["unseen_context_count"]=2.0
    roots={"transfer":transfer_root,"third":third_root,"fourth":fourth_root}
    historical=[];reps={}
    for name in ORDER:
        pool,rep,_,mis=y079.build_context(y075,name,roots[name])
        pool=[dict(x) for x in pool]
        m["historical_identity_mismatch_count"]+=float(mis)
        m["historical_full_pool_row_count"]+=float(len(pool))
        if rep is None or not pool:
            m["invalid_evaluation_rows"]+=1.0;continue
        reps[name]=dict(rep)
        for state in pool:
            sig=canonical_signature(state,rep,pool)
            if len(sig)!=15 or any((not isinstance(x,int)) for x in sig):
                m["canonical_relation_identity_mismatch_count"]+=1.0
            historical.append({"context":name,"state":dict(state),"signature":sig})

    cells=[]
    for context,root in (("sixth",sixth_root),("seventh",seventh_root)):
        pool,rep,src,loc=target_pool(y075,y079,root,m)
        if rep is None or src is None or loc is None:
            m["invalid_evaluation_rows"]+=1.0;continue
        if tuple(src["key"])==tuple(loc["key"]): m["target_selectors_same_row_count"]+=1.0
        changed_context=False
        context_oracle_only=0.0
        selectors={"SOURCE_CONDITIONED":src,"LOCAL_ONLY":loc}
        for origin,target in selectors.items():
            target_sig=canonical_signature(target,rep,pool)
            if len(target_sig)!=15 or any((not isinstance(x,int)) for x in target_sig):
                m["canonical_relation_identity_mismatch_count"]+=1.0
            cc,cd,control_state=y079.retrieve_full(y075,tuple(target["key"]),historical)
            oracle_item,od=oracle_retrieve(y075,target_sig,historical)
            oracle_state=oracle_item["state"];oc=oracle_item["context"]
            changed=(cc!=oc or tuple(control_state["key"])!=tuple(oracle_state["key"]))
            m["oracle_selected_row_change_count"]+=float(changed);changed_context=changed_context or changed
            by={}
            y075.TARGET_SOURCES=dynamic_sources(root)
            for repname,selected_context,state,dist in (
                ("EXACT_RETAINED_STATE",cc,control_state,cd),
                ("ORACLE_CANONICAL_INVARIANT",oc,oracle_state,od)):
                projected=y079.project_payload(target,state)
                child=y075.run_variant(root,projected);s=y079.summarize(child)
                clean=s["active_prose"]>s["original_prose"] and s["active_partner_fail"]==0.0
                behavior=y079.behavior_changed(child)
                m["variant_count"]+=1.0
                m["all_child_source_identity_mismatch_count"]+=s["source_mismatch"]
                m["all_child_transport_identity_mismatch_count"]+=s["transport_mismatch"]
                m["capacity_growth_event_count"]+=s["capacity_growth"]
                m["invalid_evaluation_rows"]+=s["invalid"]
                if repname=="EXACT_RETAINED_STATE": m["control_clean_rescue_count"]+=float(clean)
                else:
                    m["oracle_invariant_clean_rescue_count"]+=float(clean)
                    m["oracle_behavior_change_count"]+=float(behavior)
                    m["oracle_partner_collateral_failure_count"]+=s["active_partner_fail"]
                row={"context":context,"key_origin":origin,"representation":repname,
                     "selected_historical_context":selected_context,"selected_historical_key":list(state["key"]),
                     "relation_distance":int(dist),"clean_rescue":clean,"behavior_changed":behavior,
                     "original_positive_prose_collateral_schedule_count":s["original_prose"],
                     "active_positive_prose_collateral_schedule_count":s["active_prose"],
                     "active_partner_collateral_failure_count":s["active_partner_fail"],
                     "active_mean_first_success_packet":s["active_first"]}
                cells.append(row);by[repname]=row
            c=by["EXACT_RETAINED_STATE"];o=by["ORACLE_CANONICAL_INVARIANT"]
            if o["clean_rescue"] and not c["clean_rescue"]:
                m["oracle_only_clean_rescue_count"]+=1.0;context_oracle_only+=1.0
            if c["clean_rescue"] and not o["clean_rescue"]: m["lost_control_clean_rescue_count"]+=1.0
            if (changed and o["active_partner_collateral_failure_count"]==0.0 and
                (o["active_positive_prose_collateral_schedule_count"]>c["active_positive_prose_collateral_schedule_count"] or
                 o["active_mean_first_success_packet"]<c["active_mean_first_success_packet"])):
                m["oracle_improvement_case_count"]+=1.0
        if changed_context: m["oracle_changed_context_count"]+=1.0
        m[context+"_oracle_only_clean_rescue_count"]=context_oracle_only

    if m["historical_context_count"]!=3.0 or m["historical_full_pool_row_count"]!=17.0 or m["historical_identity_mismatch_count"]!=0.0:
        m["invalid_evaluation_rows"]+=1.0
    if m["unseen_context_count"]!=2.0 or m["target_source_count"]!=6.0 or m["target_total_source_bytes"]!=114544.0:
        m["invalid_evaluation_rows"]+=1.0
    if m["target_source_identity_mismatch_count"]!=0.0 or m["target_base_training_identity_mismatch_count"]!=0.0 or m["target_history_byte_budget_mismatch_count"]!=0.0:
        m["invalid_evaluation_rows"]+=1.0
    if m["target_donor_row_count"]!=32.0 or m["target_selectors_same_row_count"]!=0.0:
        m["invalid_evaluation_rows"]+=1.0
    if m["variant_count"]!=8.0 or m["heldout_outcome_use_before_oracle_relation_freeze"]!=0.0 or m["post_result_relation_change_count"]!=0.0:
        m["invalid_evaluation_rows"]+=1.0
    if m["target_context_mapping_disclosure_count"]!=0.0 or m["target_answer_disclosure_count"]!=0.0:
        m["invalid_evaluation_rows"]+=1.0
    if m["persistent_state_write_count"]!=0.0 or m["all_child_source_identity_mismatch_count"]!=0.0 or m["all_child_transport_identity_mismatch_count"]!=0.0:
        m["invalid_evaluation_rows"]+=1.0
    if m["capacity_growth_event_count"]!=0.0 or m["canonical_relation_identity_mismatch_count"]!=0.0:
        m["invalid_evaluation_rows"]+=1.0
    if any(not math.isfinite(float(v)) for v in m.values()): m["invalid_evaluation_rows"]+=1.0
    return {"schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,"metrics":m,"cells":cells}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--transfer-root",required=True);p.add_argument("--third-root",required=True);p.add_argument("--fourth-root",required=True)
    p.add_argument("--sixth-root",required=True);p.add_argument("--seventh-root",required=True);p.add_argument("--out",required=True)
    a=p.parse_args()
    with open(a.out,"w",encoding="utf-8",newline="\n") as f:
        json.dump(run(a.transfer_root,a.third_root,a.fourth_root,a.sixth_root,a.seventh_root),f,allow_nan=False,separators=(",",":"),sort_keys=True)
if __name__=="__main__":main()
