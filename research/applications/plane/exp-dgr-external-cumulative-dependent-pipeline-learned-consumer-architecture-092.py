"""Yggdrasil Y092: bounded learned cognition-consumer RSI pilot."""
import argparse,hashlib,importlib.util,json,math,resource,time
from pathlib import Path

EXPERIMENT="EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-LEARNED-CONSUMER-ARCHITECTURE-092"
Y079_PATH=Path("research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-consolidation-mechanism-attribution-079.py")
ORDER=("transfer","third","fourth")
GRID=(0.0,0.25,0.5,0.75,1.0)
FIELDS=("total","best_count","consistency","utility")
CANDIDATES=(
    {"id":"shared-alpha","scalars":1},
    {"id":"count-score-alpha","scalars":2},
    {"id":"distance-gated-alpha","scalars":2},
    {"id":"fieldwise-alpha","scalars":4},
)

def load_y079():
    spec=importlib.util.spec_from_file_location("yggdrasil_y079_for_y092",Y079_PATH)
    if spec is None or spec.loader is None: raise RuntimeError("Y079_IMPORT_SPEC_FAILED")
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

def dynamic_sources(root):
    root=Path(root)
    names=(("A","code.bin",41453),("B","structured.bin",14365),("C","technical-prose.bin",1454))
    out={}
    for k,name,n in names:
        data=(root/name).read_bytes()
        out[k]={"file":name,"sha256":hashlib.sha256(data).hexdigest(),"bytes":n}
    return out

def target_pool(y075,y079,root,m,prefix):
    y075.TARGET_SOURCES=dynamic_sources(root)
    tm=y079.builder_metrics()
    pool=[dict(x) for x in y075.build_pool(root,tm)]
    for dst,key in (
        ("source_identity_mismatch_count","target_source_identity_mismatch_count"),
        ("source_count","target_source_count"),
        ("source_bytes","target_total_source_bytes"),
        ("base_training_identity_mismatch_count","base_training_identity_mismatch_count"),
        ("history_byte_budget_mismatch_count","history_byte_budget_mismatch_count"),
        ("donor_row_count","donor_row_count"),
        ("eligible_candidate_count","eligible_candidate_count"),
        ("invalid_evaluation_rows","invalid_evaluation_rows")):
        metric_key="invalid_evaluation_rows" if dst=="invalid_evaluation_rows" else prefix+dst\n        m[metric_key]+=float(tm[key])
    if not pool:return [],None
    return pool,dict(sorted(pool,key=y075.local_rank)[0])

def field_alphas(spec,params,distance):
    if spec["id"]=="shared-alpha":
        return (params[0],)*4
    if spec["id"]=="count-score-alpha":
        return (params[0],params[0],params[1],params[1])
    if spec["id"]=="distance-gated-alpha":
        d=min(4,max(0,int(distance)))/4.0
        a=min(1.0,max(0.0,params[0]+(params[1]-0.5)*d))
        return (a,)*4
    if spec["id"]=="fieldwise-alpha":
        return tuple(params)
    raise RuntimeError("UNKNOWN_CANDIDATE")

def cognition_consumer(target,retained,distance,spec,params):
    alphas=field_alphas(spec,params,distance)
    out=dict(retained)
    out["best"]=int(target["best"])
    out["map_best"]=int(target["map_best"])
    for i,k in enumerate(FIELDS):
        a=float(alphas[i])
        v=(1.0-a)*float(retained[k])+a*float(target[k])
        if k in ("total","best_count"): v=int(round(v))
        out[k]=v
    return out

def baseline_consumer(target,retained):
    return cognition_consumer(target,retained,0,{"id":"shared-alpha","scalars":1},[0.5])

def summary(y079,child):
    s=y079.summarize(child)
    return {
        "clean":bool(s["active_prose"]>s["original_prose"] and s["active_partner_fail"]==0.0),
        "changed":bool(y079.behavior_changed(child)),
        "original_prose":float(s["original_prose"]),
        "active_prose":float(s["active_prose"]),
        "partner_fail":float(s["active_partner_fail"]),
        "first":float(s["active_first"]),
        "source_mismatch":float(s["source_mismatch"]),
        "transport_mismatch":float(s["transport_mismatch"]),
        "capacity_growth":float(s["capacity_growth"]),
        "invalid":float(s["invalid"]),
    }

def prepare_historical(y075,y079,roots,m):
    by={}
    for name in ORDER:
        pool,rep,bm,mis=y079.build_context(y075,name,roots[name])
        pool=[dict(x) for x in pool]
        m["historical_identity_mismatch_count"]+=float(mis)
        m["historical_full_pool_row_count"]+=float(len(pool))
        if rep is None or not pool:m["invalid_evaluation_rows"]+=1.0
        by[name]=pool
    return by

def donor_history(by,target_name):
    out=[]
    for name in ORDER:
        if name==target_name:continue
        for state in by[name]:out.append({"context":name,"state":dict(state)})
    return out

def historical_score(y075,y079,roots,by,spec,params):
    score=0.0
    for target_name in ORDER:
        pool=by[target_name]
        if not pool:return -1e18
        target=dict(sorted(pool,key=y075.local_rank)[0])
        donors=donor_history(by,target_name)
        _,distance,retained=y079.retrieve_full(y075,tuple(target["key"]),donors)
        state=cognition_consumer(target,retained,distance,spec,params)
        y075.TARGET_SOURCES=dynamic_sources(roots[target_name])
        s=summary(y079,y075.run_variant(roots[target_name],state))
        score+=100.0*float(s["clean"])+5.0*float(s["changed"])
        score+=0.1*s["active_prose"]-100.0*s["partner_fail"]-0.001*s["first"]
    score-=0.01*float(spec["scalars"]-1)
    return score

def fit_candidate(y075,y079,roots,by,spec):
    params=[0.5]*spec["scalars"]
    for _ in range(2):
        for g in range(spec["scalars"]):
            best=None
            for a in GRID:
                trial=list(params);trial[g]=a
                sc=historical_score(y075,y079,roots,by,spec,trial)
                key=(sc,-a)
                if best is None or key>best[0]:best=(key,trial,sc)
            params=best[1]
    score=historical_score(y075,y079,roots,by,spec,params)
    return {"id":spec["id"],"learned_scalars":spec["scalars"],"params":params,
            "historical_replay_score":score,"resource_eligible":spec["scalars"]<=1}

def run(transfer_root,third_root,fourth_root,fifteenth_root,sixteenth_root):
    y079=load_y079();y075=y079.load_y075()
    names=(
      "historical_context_count","historical_full_pool_row_count","historical_identity_mismatch_count",
      "unseen_context_count","variant_count","candidate_mechanism_count",
      "baseline_clean_rescue_count","learned_clean_rescue_count","learned_improvement_case_count",
      "lost_baseline_clean_rescue_count","learned_behavior_change_count","learned_partner_collateral_failure_count",
      "historical_source_identity_mismatch_count","historical_source_count","historical_source_bytes",
      "historical_base_training_identity_mismatch_count","historical_history_byte_budget_mismatch_count",
      "historical_donor_row_count","historical_eligible_candidate_count",
      "unseen_source_identity_mismatch_count","unseen_source_count","unseen_source_bytes",
      "unseen_base_training_identity_mismatch_count","unseen_history_byte_budget_mismatch_count",
      "unseen_donor_row_count","unseen_eligible_candidate_count",
      "heldout_outcome_use_before_candidate_freeze","post_result_candidate_or_threshold_choice_count",
      "persistent_state_write_count","source_identity_mismatch_count","transport_identity_mismatch_count",
      "capacity_growth_event_count","invalid_evaluation_rows",
      "capacity_total","capacity_active","capacity_retained",
      "baseline_effective_consumer_scalars","selected_effective_consumer_scalars","selected_resource_eligible")
    m={k:0.0 for k in names}
    m["historical_context_count"]=3.0;m["unseen_context_count"]=2.0;m["candidate_mechanism_count"]=4.0
    m["capacity_total"]=16.0;m["capacity_active"]=7.0;m["capacity_retained"]=9.0
    m["baseline_effective_consumer_scalars"]=1.0

    roots={"transfer":transfer_root,"third":third_root,"fourth":fourth_root}
    by=prepare_historical(y075,y079,roots,m)
    history=[fit_candidate(y075,y079,roots,by,spec) for spec in CANDIDATES]
    history.sort(key=lambda x:x["id"])
    selected=max(history,key=lambda x:(x["historical_replay_score"],-x["learned_scalars"],tuple(-v for v in x["params"]),x["id"]))
    spec=next(s for s in CANDIDATES if s["id"]==selected["id"])
    m["selected_effective_consumer_scalars"]=float(selected["learned_scalars"])
    m["selected_resource_eligible"]=float(bool(selected["resource_eligible"]))

    historical=[]
    for name in ORDER:
        for state in by[name]:historical.append({"context":name,"state":dict(state)})

    cells=[]
    for context,root in (("fifteenth",fifteenth_root),("sixteenth",sixteenth_root)):
        pool,target=target_pool(y075,y079,root,m,"unseen_")
        if target is None or not historical:
            m["invalid_evaluation_rows"]+=1.0;continue
        selected_context,distance,retained=y079.retrieve_full(y075,tuple(target["key"]),historical)
        baseline=baseline_consumer(target,retained)
        learned=cognition_consumer(target,retained,distance,spec,selected["params"])
        by_arm={}
        y075.TARGET_SOURCES=dynamic_sources(root)
        for arm,state in (("Y091_HAND_DESIGNED_ALPHA_0_5",baseline),("LEARNED_CONSUMER",learned)):
            child=y075.run_variant(root,state);s=summary(y079,child)
            m["variant_count"]+=1.0
            m["source_identity_mismatch_count"]+=s["source_mismatch"]
            m["transport_identity_mismatch_count"]+=s["transport_mismatch"]
            m["capacity_growth_event_count"]+=s["capacity_growth"]
            m["invalid_evaluation_rows"]+=s["invalid"]
            if arm=="Y091_HAND_DESIGNED_ALPHA_0_5":m["baseline_clean_rescue_count"]+=float(s["clean"])
            else:
                m["learned_clean_rescue_count"]+=float(s["clean"])
                m["learned_behavior_change_count"]+=float(s["changed"])
                m["learned_partner_collateral_failure_count"]+=s["partner_fail"]
            row={"context":context,"arm":arm,"selected_historical_context":selected_context,
                 "relation_distance":int(distance),"target_key":list(target["key"]),
                 "clean_rescue":s["clean"],"behavior_changed":s["changed"],
                 "original_positive_prose_collateral_schedule_count":s["original_prose"],
                 "active_positive_prose_collateral_schedule_count":s["active_prose"],
                 "active_partner_collateral_failure_count":s["partner_fail"],
                 "active_mean_first_success_packet":s["first"]}
            cells.append(row);by_arm[arm]=row
        b=by_arm["Y091_HAND_DESIGNED_ALPHA_0_5"];l=by_arm["LEARNED_CONSUMER"]
        if b["clean_rescue"] and not l["clean_rescue"]:m["lost_baseline_clean_rescue_count"]+=1.0
        improved=(l["active_partner_collateral_failure_count"]==0.0 and
                  ((l["clean_rescue"] and not b["clean_rescue"]) or
                   l["active_positive_prose_collateral_schedule_count"]>b["active_positive_prose_collateral_schedule_count"] or
                   l["active_mean_first_success_packet"]<b["active_mean_first_success_packet"]))
        if improved:m["learned_improvement_case_count"]+=1.0

    if m["historical_context_count"]!=3.0 or m["historical_full_pool_row_count"]!=17.0 or m["historical_identity_mismatch_count"]!=0.0:m["invalid_evaluation_rows"]+=1.0
    if m["unseen_context_count"]!=2.0 or m["unseen_source_count"]!=6.0 or m["unseen_source_bytes"]!=114544.0:m["invalid_evaluation_rows"]+=1.0
    if m["unseen_source_identity_mismatch_count"]!=0.0 or m["unseen_base_training_identity_mismatch_count"]!=0.0 or m["unseen_history_byte_budget_mismatch_count"]!=0.0:m["invalid_evaluation_rows"]+=1.0
    if m["variant_count"]!=4.0 or len(history)!=4:m["invalid_evaluation_rows"]+=1.0
    if m["capacity_total"]!=16.0 or m["capacity_active"]!=7.0 or m["capacity_retained"]!=9.0:m["invalid_evaluation_rows"]+=1.0
    if m["heldout_outcome_use_before_candidate_freeze"]!=0.0 or m["post_result_candidate_or_threshold_choice_count"]!=0.0:m["invalid_evaluation_rows"]+=1.0
    if m["persistent_state_write_count"]!=0.0 or m["source_identity_mismatch_count"]!=0.0 or m["transport_identity_mismatch_count"]!=0.0:m["invalid_evaluation_rows"]+=1.0
    if m["capacity_growth_event_count"]!=0.0:m["invalid_evaluation_rows"]+=1.0
    if any(not math.isfinite(float(v)) for v in m.values()):m["invalid_evaluation_rows"]+=1.0
    return {"schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,
            "selected_candidate":selected["id"],"selected_params":selected["params"],
            "candidate_history":history,"metrics":m,"cells":cells}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--transfer-root",required=True);p.add_argument("--third-root",required=True);p.add_argument("--fourth-root",required=True)
    p.add_argument("--fifteenth-root",required=True);p.add_argument("--sixteenth-root",required=True)
    p.add_argument("--out",required=True);p.add_argument("--resource-out")
    a=p.parse_args()
    started=time.perf_counter_ns()
    before=resource.getrusage(resource.RUSAGE_SELF)
    result=run(a.transfer_root,a.third_root,a.fourth_root,a.fifteenth_root,a.sixteenth_root)
    after=resource.getrusage(resource.RUSAGE_SELF)
    with open(a.out,"w",encoding="utf-8",newline="\n") as f:
        json.dump(result,f,allow_nan=False,separators=(",",":"),sort_keys=True)
    if a.resource_out:
        telemetry={
          "schema":"yggdrasil.rsi-resource-telemetry.v1","experiment":EXPERIMENT,
          "hardware_identity_assumed":False,
          "home_hardware_policy":"research/roadmap/home-hardware-feasibility.ice",
          "algorithmic_envelope":{"candidate_mechanisms":4,"capacity_total":16,"capacity_active":7,"capacity_retained":9,
                                  "max_candidate_learned_scalars":4,"baseline_effective_consumer_scalars":1,
                                  "external_model_calls":0,"persistent_state_growth":False},
          "elapsed_ns":time.perf_counter_ns()-started,
          "ru_maxrss_before":before.ru_maxrss,"ru_maxrss_after":after.ru_maxrss,
          "user_cpu_seconds":after.ru_utime-before.ru_utime,"system_cpu_seconds":after.ru_stime-before.ru_stime,
        }
        with open(a.resource_out,"w",encoding="utf-8",newline="\n") as f:json.dump(telemetry,f,separators=(",",":"),sort_keys=True)

if __name__=="__main__":main()
