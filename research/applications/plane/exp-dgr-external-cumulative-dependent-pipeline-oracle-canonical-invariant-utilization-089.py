"""Yggdrasil 089: oracle-canonical invariant utilization on unseen contexts."""
import argparse,hashlib,importlib.util,json,math
from pathlib import Path

EXPERIMENT="EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-ORACLE-CANONICAL-INVARIANT-UTILIZATION-089"
Y079_PATH=Path("research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-consolidation-mechanism-attribution-079.py")
ORDER=("transfer","third","fourth")

def load_y079():
    spec=importlib.util.spec_from_file_location("yggdrasil_y079_for_y089",Y079_PATH)
    if spec is None or spec.loader is None: raise RuntimeError("Y079_IMPORT_SPEC_FAILED")
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

def cmpv(a,b):
    return -1 if a<b else (1 if a>b else 0)

def ordinal_rank(pool,field,value):
    vals=sorted({float(x[field]) for x in pool})
    return vals.index(float(value))

def canonical_signature(state,rep,pool):
    key=tuple(int(x) for x in state["key"]);anchor=tuple(int(x) for x in rep["key"])
    anchor_rel=tuple(cmpv(key[i],anchor[i]) for i in range(4))
    within=tuple(cmpv(key[i],key[j]) for i in range(4) for j in range(i+1,4))
    payload_rel=(cmpv(int(state["best"]),int(state["map_best"])),)
    ranks=tuple(ordinal_rank(pool,f,state[f]) for f in ("best_count","consistency","utility","cell_index"))
    return anchor_rel+within+payload_rel+ranks

def sig_distance(a,b):
    return sum(int(x)!=int(y) for x,y in zip(a,b))

def dyn_sources(code,structured,prose):
    return {
      "A":{"file":"code.bin","sha256":hashlib.sha256(code).hexdigest(),"bytes":41453},
      "B":{"file":"structured.bin","sha256":hashlib.sha256(structured).hexdigest(),"bytes":14365},
      "C":{"file":"technical-prose.bin","sha256":hashlib.sha256(prose).hexdigest(),"bytes":1454},
    }

def build_target(y075,root,sources):
    y075.TARGET_SOURCES={k:dict(v) for k,v in sources.items()}
    m={
      "target_source_identity_mismatch_count":0.0,"target_source_count":0.0,"target_total_source_bytes":0.0,
      "base_training_identity_mismatch_count":0.0,"history_byte_budget_mismatch_count":0.0,
      "donor_row_count":0.0,"induction_source_bytes":0.0,"eligible_candidate_count":0.0,"invalid_evaluation_rows":0.0,
    }
    pool=[dict(x) for x in y075.build_pool(root,m)]
    src=sorted(pool,key=y075.source_rank)[0] if pool else None
    loc=sorted(pool,key=y075.local_rank)[0] if pool else None
    return pool,src,loc,m

def canonical_retrieve(y075,target,target_rep,target_pool,full_pool,pools,reps):
    ts=canonical_signature(target,target_rep,target_pool)
    ranked=[]
    for item in full_pool:
        c=item["context"];state=item["state"]
        hs=canonical_signature(state,reps[c],pools[c])
        ranked.append((sig_distance(ts,hs),ORDER.index(c),y075.local_rank(state),tuple(state["key"]),item,hs))
    if not ranked: raise RuntimeError("CANONICAL_RETRIEVAL_EMPTY")
    ranked.sort(key=lambda x:x[:4]);row=ranked[0]
    return row[4]["context"],row[0],row[4]["state"],ts,row[5]

def run(transfer_root,third_root,fourth_root,sixth_root,seventh_root):
    y079=load_y079();y075=y079.load_y075()
    names=(
      "historical_context_count","historical_full_pool_row_count","historical_identity_mismatch_count",
      "variant_count","unseen_context_count","target_case_count","control_clean_rescue_count",
      "oracle_invariant_clean_rescue_count","oracle_only_clean_rescue_count","lost_control_clean_rescue_count",
      "oracle_selected_row_change_count","oracle_behavior_change_count","oracle_partner_collateral_failure_count",
      "contexts_with_selection_change","contexts_with_oracle_only_rescue","mixed_improvement_case_count",
      "canonical_relation_identity_mismatch_count","target_source_identity_mismatch_count",
      "heldout_outcome_use_before_oracle_relation_freeze","target_context_mapping_disclosure_count",
      "target_answer_disclosure_count","post_result_relation_change_count","persistent_state_write_count",
      "capacity_growth_event_count","all_child_source_identity_mismatch_count","all_child_transport_identity_mismatch_count",
      "invalid_evaluation_rows")
    m={k:0.0 for k in names};m["historical_context_count"]=3.0;m["unseen_context_count"]=2.0
    roots={"transfer":transfer_root,"third":third_root,"fourth":fourth_root}
    pools={};reps={};full=[]
    for name in ORDER:
        pool,rep,_,mis=y079.build_context(y075,name,roots[name])
        pools[name]=[dict(x) for x in pool]
        if rep is not None: reps[name]=dict(rep)
        m["historical_full_pool_row_count"]+=float(len(pool));m["historical_identity_mismatch_count"]+=float(mis)
        full.extend({"context":name,"state":dict(x)} for x in pool)
    if len(reps)!=3: m["invalid_evaluation_rows"]+=1.0

    targets=[
      ("sixth",sixth_root),
      ("seventh",seventh_root),
    ]
    cells=[]
    for context,root in targets:
        code=Path(root,"code.bin").read_bytes();structured=Path(root,"structured.bin").read_bytes();prose=Path(root,"technical-prose.bin").read_bytes()
        pool,src,loc,tm=build_target(y075,root,dyn_sources(code,structured,prose))
        m["target_source_identity_mismatch_count"]+=float(tm["target_source_identity_mismatch_count"]+tm["base_training_identity_mismatch_count"]+tm["history_byte_budget_mismatch_count"])
        m["invalid_evaluation_rows"]+=float(tm["invalid_evaluation_rows"])
        if tm["target_source_count"]!=3.0 or tm["target_total_source_bytes"]!=57272.0 or tm["donor_row_count"]!=16.0:
            m["invalid_evaluation_rows"]+=1.0
        if src is None or loc is None or not pool:
            m["invalid_evaluation_rows"]+=1.0;continue
        if tuple(src["key"])==tuple(loc["key"]): m["invalid_evaluation_rows"]+=1.0
        changed_context=False;rescue_context=False
        by={}
        for origin,target in (("SOURCE_CONDITIONED",src),("LOCAL_ONLY",loc)):
            cc,cd,cstate=y079.retrieve_full(y075,tuple(target["key"]),full)
            oc,od,ostate,ts,hs=canonical_retrieve(y075,target,loc,pool,full,pools,reps)
            changed=(cc!=oc or tuple(cstate["key"])!=tuple(ostate["key"]))
            changed_context=changed_context or changed
            m["oracle_selected_row_change_count"]+=float(changed);m["target_case_count"]+=1.0
            if len(ts)!=15 or len(hs)!=15: m["canonical_relation_identity_mismatch_count"]+=1.0
            for rep,selctx,state,dist in (
              ("EXACT_RETAINED_STATE",cc,cstate,cd),
              ("ORACLE_CANONICAL_INVARIANT",oc,ostate,od)):
                projected=y079.project_payload(target,state)
                child=y075.run_variant(root,projected);summ=y079.summarize(child)
                clean=summ["active_prose"]>summ["original_prose"] and summ["active_partner_fail"]==0.0
                behavior=y079.behavior_changed(child)
                m["variant_count"]+=1.0
                m["all_child_source_identity_mismatch_count"]+=summ["source_mismatch"]
                m["all_child_transport_identity_mismatch_count"]+=summ["transport_mismatch"]
                m["capacity_growth_event_count"]+=summ["capacity_growth"]
                m["invalid_evaluation_rows"]+=summ["invalid"]
                if rep=="EXACT_RETAINED_STATE": m["control_clean_rescue_count"]+=float(clean)
                else:
                    m["oracle_invariant_clean_rescue_count"]+=float(clean)
                    m["oracle_behavior_change_count"]+=float(behavior)
                    m["oracle_partner_collateral_failure_count"]+=summ["active_partner_fail"]
                row={"context":context,"key_origin":origin,"representation":rep,"selected_historical_context":selctx,
                     "selected_historical_key":list(state["key"]),"relation_distance":int(dist),"clean_rescue":clean,
                     "behavior_changed":behavior,"original_positive_prose_collateral_schedule_count":summ["original_prose"],
                     "active_positive_prose_collateral_schedule_count":summ["active_prose"],
                     "active_partner_collateral_failure_count":summ["active_partner_fail"],
                     "active_mean_first_success_packet":summ["active_first"]}
                cells.append(row);by.setdefault(origin,{})[rep]=row
        if changed_context: m["contexts_with_selection_change"]+=1.0
        for origin in ("SOURCE_CONDITIONED","LOCAL_ONLY"):
            c=by.get(origin,{}).get("EXACT_RETAINED_STATE");o=by.get(origin,{}).get("ORACLE_CANONICAL_INVARIANT")
            if c is None or o is None: m["invalid_evaluation_rows"]+=1.0;continue
            if o["clean_rescue"] and not c["clean_rescue"]:
                m["oracle_only_clean_rescue_count"]+=1.0;rescue_context=True
            if c["clean_rescue"] and not o["clean_rescue"]: m["lost_control_clean_rescue_count"]+=1.0
            if (not o["clean_rescue"] and o["active_partner_collateral_failure_count"]==0.0 and
                (o["active_positive_prose_collateral_schedule_count"]>c["active_positive_prose_collateral_schedule_count"] or
                 o["active_mean_first_success_packet"]<c["active_mean_first_success_packet"])):
                m["mixed_improvement_case_count"]+=1.0
        if rescue_context: m["contexts_with_oracle_only_rescue"]+=1.0

    if m["historical_full_pool_row_count"]!=17.0 or m["historical_identity_mismatch_count"]!=0.0: m["invalid_evaluation_rows"]+=1.0
    if m["variant_count"]!=8.0 or m["target_case_count"]!=4.0: m["invalid_evaluation_rows"]+=1.0
    for k in ("heldout_outcome_use_before_oracle_relation_freeze","target_context_mapping_disclosure_count","target_answer_disclosure_count",
              "post_result_relation_change_count","persistent_state_write_count","capacity_growth_event_count",
              "all_child_source_identity_mismatch_count","all_child_transport_identity_mismatch_count","canonical_relation_identity_mismatch_count",
              "target_source_identity_mismatch_count"):
        if m[k]!=0.0: m["invalid_evaluation_rows"]+=1.0
    if any(not math.isfinite(float(v)) for v in m.values()): m["invalid_evaluation_rows"]+=1.0
    return {"schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,"metrics":m,"cells":cells}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--transfer-root",required=True);p.add_argument("--third-root",required=True);p.add_argument("--fourth-root",required=True)
    p.add_argument("--sixth-root",required=True);p.add_argument("--seventh-root",required=True);p.add_argument("--out",required=True)
    a=p.parse_args()
    with open(a.out,"w",encoding="utf-8",newline="\n") as f:
        json.dump(run(a.transfer_root,a.third_root,a.fourth_root,a.sixth_root,a.seventh_root),f,allow_nan=False,separators=(",",":"),sort_keys=True)
if __name__=="__main__": main()
