"""EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-TECHNICAL-PROSE-SUPPORT-ATTRIBUTION-056."""
import argparse
import importlib.util
import json
import math
from pathlib import Path

EXPERIMENT = "EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-TECHNICAL-PROSE-SUPPORT-ATTRIBUTION-056"
PRIOR_PATH = Path("research/applications/plane/exp-dgr-external-interleaved-pipeline-020.py")
ACTIVE_CEILING = 7
PACKETS = 12
PROSE = "C"
AFFECTED = (
    ("A","C","B"),
    ("B","C","A"),
    ("C","A","B"),
    ("C","B","A"),
)

def load_prior_experiment():
    spec=importlib.util.spec_from_file_location("dgr_external_020",PRIOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("PRIOR_IMPORT_SPEC_FAILED")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def mix(a,b):
    n=min(len(a),len(b))//32*32
    return b"".join(a[i:i+32]+b[i:i+32] for i in range(0,n,32))

def run(root):
    prior020=load_prior_experiment()
    prior017=prior020.load_prior_experiment()
    prior016=prior017.load_prior_experiment()
    prior015=prior016.load_prior_experiment()
    prior014=prior015.load_prior_experiment()
    prior013=prior014.load_prior_experiment()
    adaptation=prior013.load_prior_experiment()
    error_guided=adaptation.load_prior_experiment()
    wake=error_guided.load_wake()
    pressure=wake.load_pressure()
    learner=pressure.load_prior()

    m={
        "source_identity_mismatch_count":0.0,
        "source_count":0.0,
        "total_source_bytes":0.0,
        "base_training_identity_mismatch_count":0.0,
        "affected_schedule_count":4.0,
        "attribution_record_count":0.0,
        "historical_positive_count":0.0,
        "failed_final_packet_count":0.0,
        "historical_not_positive_count":0.0,
        "row_not_carried_count":0.0,
        "injection_loss_count":0.0,
        "reservation_selection_loss_count":0.0,
        "active_score_loss_count":0.0,
        "preserved_but_dependent_failure_count":0.0,
        "attribution_accounting_error_count":0.0,
        "heldout_selection_use_count":0.0,
        "preserved_state_structure_count_min":16.0,
        "preserved_state_structure_count_max":0.0,
        "active_structure_count_min":16.0,
        "active_structure_count_max":0.0,
        "retained_structure_count_min":16.0,
        "retained_structure_count_max":0.0,
        "matched_assignment_failure_count":0.0,
        "capacity_growth_event_count":0.0,
        "row_mutation_event_count":0.0,
        "tokenizer_use_count":0.0,
        "external_model_call_count":0.0,
        "invalid_evaluation_rows":0.0,
    }

    demands=prior017.load_external(root,m)
    base_train=[]
    for path,expected in learner.TRAIN_FILES:
        data,ok=learner.load_checked(path,expected)
        m["base_training_identity_mismatch_count"]+=float(not ok)
        base_train.append(data)
    baseline=learner.baseline_train(base_train)

    def build_state(current_demands,ordered_names):
        independent_rows={}
        for name in ordered_names:
            cue,_=current_demands[name]
            stats,overflow,invalid=learner.candidate_stats(base_train+[cue])
            m["invalid_evaluation_rows"]+=float(overflow+invalid)
            cells,rv=learner.develop(stats)
            m["invalid_evaluation_rows"]+=float(rv)
            full=learner.specialized_map(cells)
            rows=wake.known_rows(pressure,learner,cells,stats)
            if len(full)!=16 or len(rows)!=16:
                m["invalid_evaluation_rows"]+=1.0
            independent_rows[name]=rows
        shared_stats,overflow,invalid=learner.candidate_stats(
            base_train+[current_demands[name][0] for name in ordered_names]
        )
        m["invalid_evaluation_rows"]+=float(overflow+invalid)
        pooled_cells,rv=learner.develop(shared_stats)
        m["invalid_evaluation_rows"]+=float(rv)
        cells,selected_count,_,_=prior016.build_matched_minimax_cells(
            learner,error_guided,baseline,shared_stats,pooled_cells,
            independent_rows,ordered_names,current_demands,prior015,
        )
        if selected_count!=16:
            m["matched_assignment_failure_count"]+=1.0
        full_map=learner.specialized_map(cells)
        rows=wake.known_rows(pressure,learner,cells,shared_stats)
        if len(full_map)!=16 or len(rows)!=16:
            m["matched_assignment_failure_count"]+=1.0
            m["invalid_evaluation_rows"]+=1.0
        return rows,full_map

    def contribution_rank(rows,full_map,cue):
        keys={row["key"] for row in rows}
        scores=error_guided.contributions(learner,cue,baseline,keys,full_map)
        ranked=sorted(rows,key=lambda row:(-scores[row["key"]],-row["utility"],row["key"]))
        return ranked,scores

    def record_partition(rows,active):
        m["preserved_state_structure_count_min"]=min(m["preserved_state_structure_count_min"],float(len(rows)))
        m["preserved_state_structure_count_max"]=max(m["preserved_state_structure_count_max"],float(len(rows)))
        m["active_structure_count_min"]=min(m["active_structure_count_min"],float(len(active)))
        m["active_structure_count_max"]=max(m["active_structure_count_max"],float(len(active)))
        retained=len(rows)-len(active)
        m["retained_structure_count_min"]=min(m["retained_structure_count_min"],float(retained))
        m["retained_structure_count_max"]=max(m["retained_structure_count_max"],float(retained))
        if len(rows)!=16 or len(active)!=7 or retained!=9:
            m["invalid_evaluation_rows"]+=1.0

    def select_active(rows,full_map,cue,reserved_keys=()):
        ranked,_=contribution_rank(rows,full_map,cue)
        by_key={row["key"]:row for row in rows}
        selected=[]
        selected_keys=set()
        for key in reserved_keys:
            row=by_key.get(key)
            if row is None:
                m["invalid_evaluation_rows"]+=1.0
                continue
            if key not in selected_keys:
                selected.append(row)
                selected_keys.add(key)
        if len(selected)>ACTIVE_CEILING:
            m["invalid_evaluation_rows"]+=1.0
        for row in ranked:
            if len(selected)>=ACTIVE_CEILING:
                break
            if row["key"] in selected_keys:
                continue
            selected.append(row)
            selected_keys.add(row["key"])
        if len(selected)!=ACTIVE_CEILING:
            m["invalid_evaluation_rows"]+=1.0
        record_partition(rows,selected)
        return selected,wake.active_map(selected)

    def inject_retained(current_rows,current_map,historical_rows,historical_map,carry_keys,cue):
        rows=list(current_rows)
        fmap=dict(current_map)
        current_keys={row["key"] for row in rows}
        hist_by_key={row["key"]:row for row in historical_rows}
        missing=[key for key in carry_keys if key not in current_keys]
        if not missing:
            return rows,fmap
        ranked,scores=contribution_rank(rows,fmap,cue)
        carry_set=set(carry_keys)
        evictable=sorted(
            [row for row in ranked if row["key"] not in carry_set],
            key=lambda row:(scores[row["key"]],row["utility"],tuple(-x for x in row["key"])),
        )
        if len(evictable)<len(missing):
            m["invalid_evaluation_rows"]+=1.0
            return rows,fmap
        evicted=evictable[:len(missing)]
        evicted_keys={row["key"] for row in evicted}
        rows=[row for row in rows if row["key"] not in evicted_keys]
        for key in evicted_keys:
            fmap.pop(key,None)
        for key in missing:
            row=hist_by_key.get(key)
            if row is None or key not in historical_map:
                m["invalid_evaluation_rows"]+=1.0
                continue
            rows.append(row)
            fmap[key]=historical_map[key]
        if len(rows)!=16 or len({row["key"] for row in rows})!=16 or len(fmap)!=16:
            m["invalid_evaluation_rows"]+=1.0
        return rows,fmap

    def score(evaluation,active_map):
        base_correct,_,_=pressure.model_correct_counts(learner,evaluation,baseline,{})
        _,active_correct,_=pressure.model_correct_counts(learner,evaluation,baseline,active_map)
        return active_correct-base_correct

    def rebalanced_history(a_name,b_name,a_cue,b_cue):
        a_base=a_cue[:len(a_cue)//2]
        b_base=b_cue[:len(b_cue)//2]
        total=len(a_base)+len(b_base)
        a_re,b_re=a_base,b_base
        if a_name==PROSE:
            added=len(a_cue)-len(a_base)
            a_re=a_cue
            b_re=b_cue[:len(b_base)-added]
        elif b_name==PROSE:
            added=len(b_cue)-len(b_base)
            b_re=b_cue
            a_re=a_cue[:len(a_base)-added]
        if min(len(a_re),len(b_re))<=0 or len(a_re)+len(b_re)!=total:
            m["invalid_evaluation_rows"]+=1.0
        return a_re,b_re

    records=[]
    for schedule_index,(a_name,b_name,c_name) in enumerate(AFFECTED):
        a_cue,a_eval=demands[a_name]
        b_cue,b_eval=demands[b_name]
        c_cue,c_eval=demands[c_name]
        a_hist,b_hist=rebalanced_history(a_name,b_name,a_cue,b_cue)
        historical={
            a_name:(a_hist,a_eval),
            b_name:(b_hist,b_eval),
        }
        hist_rows,hist_map=build_state(historical,[a_name,b_name])
        derived_ab=mix(a_hist,b_hist)
        if not derived_ab:
            m["invalid_evaluation_rows"]+=1.0
            continue
        ranked,_=contribution_rank(hist_rows,hist_map,derived_ab)
        if len(ranked)<6:
            m["invalid_evaluation_rows"]+=1.0
            continue
        carry6=tuple(row["key"] for row in ranked[:6])

        prose_hist=a_hist if a_name==PROSE else b_hist
        prose_eval=a_eval if a_name==PROSE else b_eval
        partner_eval=b_eval if a_name==PROSE else a_eval
        prose_ranked,_=contribution_rank(hist_rows,hist_map,prose_hist)
        if not prose_ranked:
            m["invalid_evaluation_rows"]+=1.0
            continue
        protected_key=prose_ranked[0]["key"]
        _,hist_prose_map=select_active(hist_rows,hist_map,prose_hist)
        historical_score=score(prose_eval,hist_prose_map)
        if historical_score>0:
            m["historical_positive_count"]+=1.0

        c_future=c_cue[len(c_cue)//2:]
        if not c_future:
            m["invalid_evaluation_rows"]+=1.0
            continue
        c_rows,c_map=build_state({c_name:(c_future,c_eval)},[c_name])
        dep_cue=mix(derived_ab,c_future)
        if not dep_cue:
            m["invalid_evaluation_rows"]+=1.0
            continue
        injected_rows,injected_map=inject_retained(
            c_rows,c_map,hist_rows,hist_map,carry6,dep_cue
        )
        injected_keys={row["key"] for row in injected_rows}
        _,injected_prose_map=select_active(injected_rows,injected_map,prose_hist)
        injected_score=score(prose_eval,injected_prose_map)

        reserved_active,reserved_map=select_active(
            injected_rows,injected_map,dep_cue,carry6
        )
        reserved_keys={row["key"] for row in reserved_active}
        reserved_prose_score=score(prose_eval,reserved_map)
        partner_score=score(partner_eval,reserved_map)
        dependent_eval=mix(mix(a_eval,b_eval),c_eval)
        dependent_score=score(dependent_eval,reserved_map) if dependent_eval else 0
        if not dependent_eval:
            m["invalid_evaluation_rows"]+=1.0

        success=(dependent_score>0 and reserved_prose_score>0 and partner_score>0)
        if not success:
            m["failed_final_packet_count"]+=1.0

        if historical_score<=0:
            category="historical_not_positive"
        elif protected_key not in set(carry6):
            category="row_not_carried"
        elif protected_key not in injected_keys:
            category="injection_loss"
        elif protected_key not in reserved_keys:
            category="reservation_selection_loss"
        elif reserved_prose_score<=0:
            category="active_score_loss"
        else:
            category="preserved_but_dependent_failure"

        key=category+"_count"
        if key not in m:
            m["invalid_evaluation_rows"]+=1.0
        else:
            m[key]+=1.0
        m["attribution_record_count"]+=1.0

        records.append({
            "schedule_index":schedule_index,
            "schedule":[a_name,b_name,c_name],
            "historical_prose_score":historical_score,
            "protected_key":list(protected_key),
            "protected_key_carried":protected_key in set(carry6),
            "protected_key_survived_injection":protected_key in injected_keys,
            "post_injection_prose_score":injected_score,
            "protected_key_active_reserved":protected_key in reserved_keys,
            "reserved_prose_score":reserved_prose_score,
            "partner_collateral_score":partner_score,
            "dependent_score":dependent_score,
            "final_success":success,
            "category":category,
        })

    total=sum(m[k] for k in (
        "historical_not_positive_count",
        "row_not_carried_count",
        "injection_loss_count",
        "reservation_selection_loss_count",
        "active_score_loss_count",
        "preserved_but_dependent_failure_count",
    ))
    if total!=m["attribution_record_count"] or m["attribution_record_count"]!=4:
        m["attribution_accounting_error_count"]+=1.0
    if m["preserved_state_structure_count_max"]==0:
        m["invalid_evaluation_rows"]+=1.0
    assert all(math.isfinite(float(v)) for v in m.values())
    return {
        "schema":"yggdrasil.research-scientific-result.v1",
        "experiment":EXPERIMENT,
        "metrics":m,
        "attribution_records":records,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    with open(a.out,"w",encoding="utf-8",newline="\n") as f:
        json.dump(run(a.root),f,allow_nan=False,separators=(",",":"))

if __name__=="__main__":
    main()
