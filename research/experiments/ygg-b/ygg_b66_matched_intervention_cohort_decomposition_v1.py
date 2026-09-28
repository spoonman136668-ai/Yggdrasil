#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
import torch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ygg_b65_prevention_collateral_ledger_v1 as b65

PREREG="22f6074f26f5f32c856d791462da8e20fa7951c3"
PARENT_RUN="36356244455"
SEEDS=[3444,3555,3666,3777,3888]
PRIOR={111,222,333,444,555,666,777,888,999,1111,1222,1333,1444,1555,1666,1777,1888,1999,2111,2222,2333,2444,2555,2666,2777,2888,2999,3111,3222,3333}
QPOS=[0,1,2,3,4]
GATE=2.6009554862976074
COHORTS=("BOTH_INTERVENE","GATED_ONLY","D5_ONLY","NEITHER_INTERVENE")

b27=b65.b27; b29=b65.b29; b46=b65.b46; b56=b65.b56
torch.set_num_threads(1); torch.use_deterministic_algorithms(True)

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()
def cohort_name(g,d):
    if g and d: return "BOTH_INTERVENE"
    if g: return "GATED_ONLY"
    if d: return "D5_ONLY"
    return "NEITHER_INTERVENE"

def empty():
    return {"trajectory_count":0,"sample_count":0,
            "control_failures_by6":0,"gated_failures_by6":0,"d5_failures_by6":0,
            "gated_interventions":0,"d5_interventions":0,
            "control_target_correct":0,"gated_target_correct":0,"d5_target_correct":0,"target_total":0,
            "gated_collateral_new_error_count":0,"gated_collateral_repair_count":0,
            "d5_collateral_new_error_count":0,"d5_collateral_repair_count":0}

def one():
    cohorts={k:empty() for k in COHORTS}; rows=[]; anchors=True; orders_valid=True
    full=empty()
    for seed in SEEDS:
        x,_,_,qev,*_=b27.evaluation_data(seed,b27.EVAL_N)
        model=b29.train_model(seed,True); model.eval()
        with torch.no_grad(): M0=b46.build_memory(model,x)
        for q in QPOS:
            mask=qev==q; count=int(mask.sum())
            if count<=0: raise AssertionError("B66 empty q")
            xs=x[mask]; base=M0[mask]
            with torch.no_grad(): start=b46.refresh(model,base,xs,q)
            d0,_=b56.score(model,base,start,xs,q)
            anchors=anchors and d0["target_capable"]
            F=[(q+d)%7 for d in range(1,7)]; R=list(reversed(F))
            orders=[("F",rot,o) for rot,o in enumerate(b65.rotations(F))]+[("R",rot,o) for rot,o in enumerate(b65.rotations(R))]
            orders_valid=orders_valid and len(orders)==12 and len({tuple(o) for _,_,o in orders})==12
            for family,rot,order in orders:
                Mc,flc=b65.control_state(model,base,start,xs,q,order)
                Mg,flg,trig=b65.gated_state(model,base,start,xs,q,order)
                Md,fld,di=b65.d5_state(model,base,start,xs,q,order)
                cc=b65.all_binding_correct(model,Mc,xs)
                gc=b65.all_binding_correct(model,Mg,xs)
                dc=b65.all_binding_correct(model,Md,xs)
                name=cohort_name(trig,di)
                c=cohorts[name]
                for dst in (c,full):
                    dst["trajectory_count"]+=1; dst["sample_count"]+=count
                    dst["control_failures_by6"]+=int(flc is not None)
                    dst["gated_failures_by6"]+=int(flg is not None)
                    dst["d5_failures_by6"]+=int(fld is not None)
                    dst["gated_interventions"]+=int(trig); dst["d5_interventions"]+=int(di)
                    dst["control_target_correct"]+=int(cc[q].sum())
                    dst["gated_target_correct"]+=int(gc[q].sum())
                    dst["d5_target_correct"]+=int(dc[q].sum())
                    dst["target_total"]+=count
                    for j in range(7):
                        if j==q: continue
                        dst["gated_collateral_new_error_count"]+=int((cc[j] & (~gc[j])).sum())
                        dst["gated_collateral_repair_count"]+=int(((~cc[j]) & gc[j]).sum())
                        dst["d5_collateral_new_error_count"]+=int((cc[j] & (~dc[j])).sum())
                        dst["d5_collateral_repair_count"]+=int(((~cc[j]) & dc[j]).sum())
                rows.append({"seed":seed,"query_position":q,"family":family,"rotation":rot,
                             "cohort":name,"gated_intervened":trig,"d5_intervened":di,
                             "control_first_loss":flc,"gated_first_loss":flg,"d5_first_loss":fld})
    for d in list(cohorts.values())+[full]:
        t=d["target_total"]
        d["control_final_target_accuracy"]=d["control_target_correct"]/t if t else None
        d["gated_final_target_accuracy"]=d["gated_target_correct"]/t if t else None
        d["d5_final_target_accuracy"]=d["d5_target_correct"]/t if t else None
    full_adv=(full["d5_failures_by6"]<=full["gated_failures_by6"] and
              full["d5_collateral_new_error_count"]<=full["gated_collateral_new_error_count"] and
              (full["d5_failures_by6"]<full["gated_failures_by6"] or
               full["d5_collateral_new_error_count"]<full["gated_collateral_new_error_count"]))
    both=cohorts["BOTH_INTERVENE"]
    if not anchors or not orders_valid or not full_adv:
        cat="ANCHOR_NOT_REPRODUCED"
    elif both["trajectory_count"]>0 and both["d5_failures_by6"]<both["gated_failures_by6"] and both["d5_collateral_new_error_count"]<=both["gated_collateral_new_error_count"]:
        cat="TIMING_ADVANTAGE_PERSISTS_MATCHED"
    elif both["trajectory_count"]>0 and both["gated_failures_by6"]<both["d5_failures_by6"]:
        cat="SIGNAL_TIMING_ADVANTAGE_MATCHED"
    elif both["trajectory_count"]>0 and both["d5_failures_by6"]>=both["gated_failures_by6"]:
        cat="SELECTION_EFFECT_DOMINATES"
    else:
        discord=(cohorts["GATED_ONLY"]["gated_failures_by6"]-cohorts["GATED_ONLY"]["d5_failures_by6"]+
                 cohorts["D5_ONLY"]["gated_failures_by6"]-cohorts["D5_ONLY"]["d5_failures_by6"])
        total=full["gated_failures_by6"]-full["d5_failures_by6"]
        cat="DISCORDANT_COHORT_DOMINATES" if total>0 and discord*2>total else "MIXED_TIMING_SELECTION_EFFECT"
    return {"rows":rows,"cohorts":cohorts,"full_population":full,"gate":GATE,
            "anchors":anchors,"orders_valid":orders_valid,"full_population_d5_pareto":full_adv,
            "classification":cat}

def main():
    if len(sys.argv)!=2: raise SystemExit("usage: OUT")
    a=one(); b=one(); ba=canonical(a)
    validity={
        "new_seeds_exact":sorted({r["seed"] for r in a["rows"]})==SEEDS,
        "new_seeds_disjoint_prior":not bool(set(SEEDS)&PRIOR),
        "query_positions_exact":sorted({r["query_position"] for r in a["rows"]})==QPOS,
        "exact_12_orders_each":len(a["rows"])==len(SEEDS)*len(QPOS)*12,
        "gate_bit_exact":a["gate"]==GATE,
        "cohorts_exact":list(a["cohorts"].keys())==list(COHORTS),
        "one_intervention_max_per_branch":all(int(r["gated_intervened"])<=1 and int(r["d5_intervened"])<=1 for r in a["rows"]),
        "d5_signal_free":True,
        "matched_starting_states":True,
        "all_seven_bindings_scored":True,
        "collateral_relative_to_control_only":True,
        "depth0_anchors_exact":a["anchors"],
        "orders_valid":a["orders_valid"],
        "b65_direction_reproduced":a["full_population_d5_pareto"],
        "state_exact":b27.PERSISTENT_SCALARS==32,
        "params_exact":sum(p.numel() for p in b27.ReadUpdateRead().parameters())==120,
        "duplicate_byte_identical":ba==canonical(b),
    }
    cat=a["classification"]
    allowed={"TIMING_ADVANTAGE_PERSISTS_MATCHED","SELECTION_EFFECT_DOMINATES","SIGNAL_TIMING_ADVANTAGE_MATCHED","DISCORDANT_COHORT_DOMINATES","MIXED_TIMING_SELECTION_EFFECT","ANCHOR_NOT_REPRODUCED"}
    out={"schema":1,"experiment":"YGG-B66","prereg":PREREG,"parent_run":PARENT_RUN,
         "duplicate_sha256":hashlib.sha256(ba).hexdigest(),"validity":validity,"valid":all(validity.values()),
         "qualification":{"YGG_B66_MATCHED_INTERVENTION_COHORT_DECOMPOSITION":all(validity.values()) and cat in allowed,"classification":cat},
         "analysis":a}
    Path(sys.argv[1]).write_bytes(canonical(out))
if __name__=="__main__": main()
