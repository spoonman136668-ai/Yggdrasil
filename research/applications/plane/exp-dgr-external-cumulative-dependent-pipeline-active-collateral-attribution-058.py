"""EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-ACTIVE-COLLATERAL-ATTRIBUTION-058."""
import argparse
import importlib.util
import json
import math
from pathlib import Path

EXPERIMENT="EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-ACTIVE-COLLATERAL-ATTRIBUTION-058"
PRIOR_PATH=Path("research/applications/plane/exp-dgr-external-interleaved-pipeline-020.py")
ACTIVE=7
PROSE="C"
SCHEDULES=(("A","C","B"),("B","C","A"),("C","A","B"),("C","B","A"))

def load_prior():
    s=importlib.util.spec_from_file_location("p020",PRIOR_PATH)
    if s is None or s.loader is None: raise RuntimeError("PRIOR_IMPORT_SPEC_FAILED")
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def mix(a,b):
    n=min(len(a),len(b))//32*32
    return b"".join(a[i:i+32]+b[i:i+32] for i in range(0,n,32))

def run(root):
    p20=load_prior();p17=p20.load_prior_experiment();p16=p17.load_prior_experiment()
    p15=p16.load_prior_experiment();p14=p15.load_prior_experiment();p13=p14.load_prior_experiment()
    ad=p13.load_prior_experiment();eg=ad.load_prior_experiment();wake=eg.load_wake();pressure=wake.load_pressure();learner=pressure.load_prior()
    m={
      "source_identity_mismatch_count":0.0,"source_count":0.0,"total_source_bytes":0.0,
      "base_training_identity_mismatch_count":0.0,"affected_schedule_count":4.0,
      "diagnostic_k_count":7.0,"diagnostic_record_count":0.0,"historical_positive_count":0.0,
      "minimum_positive_k_schedule_count":0.0,"post_injection_state_incompatibility_count":0.0,
      "attribution_accounting_error_count":0.0,"heldout_selection_use_count":0.0,
      "preserved_state_structure_count_min":16.0,"preserved_state_structure_count_max":0.0,
      "active_structure_count_min":16.0,"active_structure_count_max":0.0,
      "retained_structure_count_min":16.0,"retained_structure_count_max":0.0,
      "matched_assignment_failure_count":0.0,"history_byte_budget_mismatch_count":0.0,
      "capacity_growth_event_count":0.0,"row_mutation_event_count":0.0,
      "tokenizer_use_count":0.0,"external_model_call_count":0.0,"invalid_evaluation_rows":0.0,
    }
    d=p17.load_external(root,m)
    bt=[]
    for path,exp in learner.TRAIN_FILES:
        x,ok=learner.load_checked(path,exp);m["base_training_identity_mismatch_count"]+=float(not ok);bt.append(x)
    base=learner.baseline_train(bt)

    def build(cur,names):
        ind={}
        for n in names:
            cue,_=cur[n];st,o,iv=learner.candidate_stats(bt+[cue]);m["invalid_evaluation_rows"]+=float(o+iv)
            cells,rv=learner.develop(st);m["invalid_evaluation_rows"]+=float(rv)
            fm=learner.specialized_map(cells);rows=wake.known_rows(pressure,learner,cells,st)
            if len(fm)!=16 or len(rows)!=16:m["invalid_evaluation_rows"]+=1.0
            ind[n]=rows
        st,o,iv=learner.candidate_stats(bt+[cur[n][0] for n in names]);m["invalid_evaluation_rows"]+=float(o+iv)
        pooled,rv=learner.develop(st);m["invalid_evaluation_rows"]+=float(rv)
        cells,nsel,_,_=p16.build_matched_minimax_cells(learner,eg,base,st,pooled,ind,names,cur,p15)
        if nsel!=16:m["matched_assignment_failure_count"]+=1.0
        fm=learner.specialized_map(cells);rows=wake.known_rows(pressure,learner,cells,st)
        if len(fm)!=16 or len(rows)!=16:m["invalid_evaluation_rows"]+=1.0
        return rows,fm

    def rank(rows,fm,cue):
        keys={r["key"] for r in rows};sc=eg.contributions(learner,cue,base,keys,fm)
        return sorted(rows,key=lambda r:(-sc[r["key"]],-r["utility"],r["key"])),sc

    def part(rows,active):
        m["preserved_state_structure_count_min"]=min(m["preserved_state_structure_count_min"],float(len(rows)))
        m["preserved_state_structure_count_max"]=max(m["preserved_state_structure_count_max"],float(len(rows)))
        m["active_structure_count_min"]=min(m["active_structure_count_min"],float(len(active)))
        m["active_structure_count_max"]=max(m["active_structure_count_max"],float(len(active)))
        ret=len(rows)-len(active)
        m["retained_structure_count_min"]=min(m["retained_structure_count_min"],float(ret))
        m["retained_structure_count_max"]=max(m["retained_structure_count_max"],float(ret))
        if len(rows)!=16 or len(active)!=7 or ret!=9:m["invalid_evaluation_rows"]+=1.0

    def select(rows,fm,cue,reserved=()):
        rr,_=rank(rows,fm,cue);by={r["key"]:r for r in rows};out=[];seen=set()
        for k in reserved:
            r=by.get(k)
            if r is None:m["invalid_evaluation_rows"]+=1.0;continue
            if k not in seen:out.append(r);seen.add(k)
        if len(out)>7:m["invalid_evaluation_rows"]+=1.0
        for r in rr:
            if len(out)>=7:break
            if r["key"] in seen:continue
            out.append(r);seen.add(r["key"])
        if len(out)!=7:m["invalid_evaluation_rows"]+=1.0
        part(rows,out)
        return out,wake.active_map(out)

    def inject(rows,fm,hrows,hmap,carry,cue):
        out=list(rows);om=dict(fm);keys={r["key"] for r in out};hby={r["key"]:r for r in hrows}
        missing=[k for k in carry if k not in keys]
        if not missing:return out,om
        rr,sc=rank(out,om,cue);cs=set(carry)
        ev=sorted([r for r in rr if r["key"] not in cs],key=lambda r:(sc[r["key"]],r["utility"],tuple(-x for x in r["key"])))
        if len(ev)<len(missing):m["invalid_evaluation_rows"]+=1.0;return out,om
        ev=ev[:len(missing)];eks={r["key"] for r in ev};out=[r for r in out if r["key"] not in eks]
        for k in eks:om.pop(k,None)
        for k in missing:
            r=hby.get(k)
            if r is None or k not in hmap:m["invalid_evaluation_rows"]+=1.0;continue
            out.append(r);om[k]=hmap[k]
        if len(out)!=16 or len({r["key"] for r in out})!=16 or len(om)!=16:m["invalid_evaluation_rows"]+=1.0
        return out,om

    def score(ev,am):
        b,_,_=pressure.model_correct_counts(learner,ev,base,{})
        _,a,_=pressure.model_correct_counts(learner,ev,base,am)
        return a-b

    def rebalanced(a_name,b_name,a_cue,b_cue):
        aa=a_cue[:len(a_cue)//2];bb=b_cue[:len(b_cue)//2];total=len(aa)+len(bb)
        if a_name==PROSE:
            add=len(a_cue)-len(aa);aa=a_cue;bb=b_cue[:len(bb)-add]
        elif b_name==PROSE:
            add=len(b_cue)-len(bb);bb=b_cue;aa=a_cue[:len(aa)-add]
        if min(len(aa),len(bb))<=0 or len(aa)+len(bb)!=total:m["history_byte_budget_mismatch_count"]+=1.0
        return aa,bb

    diagnostics=[]
    for si,(an,bn,cn) in enumerate(SCHEDULES):
        ac,ae=d[an];bc,be=d[bn];cc,ce=d[cn]
        ah,bh=rebalanced(an,bn,ac,bc)
        hd={an:(ah,ae),bn:(bh,be)}
        hrows,hmap=build(hd,[an,bn]);derived=mix(ah,bh)
        if not derived:m["invalid_evaluation_rows"]+=1.0;continue
        rr,_=rank(hrows,hmap,derived)
        if len(rr)<6:m["invalid_evaluation_rows"]+=1.0;continue
        carry=tuple(r["key"] for r in rr[:6])

        prose_hist=ah if an==PROSE else bh
        prose_eval=ae if an==PROSE else be
        pr,_=rank(hrows,hmap,prose_hist)
        if len(pr)<7:m["invalid_evaluation_rows"]+=1.0;continue
        prose_order=tuple(r["key"] for r in pr[:7])
        _,hist_am=select(hrows,hmap,prose_hist,prose_order)
        hist_score=score(prose_eval,hist_am)
        if hist_score>0:m["historical_positive_count"]+=1.0

        cf=cc[len(cc)//2:]
        dep=mix(derived,cf)
        if not cf or not dep:m["invalid_evaluation_rows"]+=1.0;continue
        crows,cmap=build({cn:(cf,ce)},[cn]);rows,fmap=inject(crows,cmap,hrows,hmap,carry,dep)

        k_records=[];min_positive=None
        for k in range(1,8):
            reserved=prose_order[:k]
            _,am=select(rows,fmap,dep,reserved)
            ps=score(prose_eval,am)
            m["diagnostic_record_count"]+=1.0
            if ps>0 and min_positive is None:min_positive=k
            k_records.append({"k":k,"prose_collateral_score":ps,"reserved_keys":[list(x) for x in reserved]})
        if min_positive is None:
            category="post_injection_state_incompatibility"
            m["post_injection_state_incompatibility_count"]+=1.0
        else:
            category="minimum_positive_coalition"
            m["minimum_positive_k_schedule_count"]+=1.0
        diagnostics.append({
            "schedule_index":si,"schedule":[an,bn,cn],"historical_prose_score":hist_score,
            "historical_prose_active_order":[list(x) for x in prose_order],
            "minimum_positive_k":min_positive,"category":category,"records":k_records,
        })

    if len(diagnostics)!=4:m["attribution_accounting_error_count"]+=float(abs(4-len(diagnostics)))
    if m["diagnostic_record_count"]!=28:m["attribution_accounting_error_count"]+=1.0
    if m["historical_positive_count"]!=4:m["attribution_accounting_error_count"]+=1.0
    if m["minimum_positive_k_schedule_count"]+m["post_injection_state_incompatibility_count"]!=4:
        m["attribution_accounting_error_count"]+=1.0
    if m["preserved_state_structure_count_max"]==0:m["invalid_evaluation_rows"]+=1.0
    assert all(math.isfinite(float(v)) for v in m.values())
    return {"schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,"metrics":m,"diagnostics":diagnostics}

def main():
    p=argparse.ArgumentParser();p.add_argument("--root",required=True);p.add_argument("--out",required=True);a=p.parse_args()
    with open(a.out,"w",encoding="utf-8",newline="\n") as f:json.dump(run(a.root),f,allow_nan=False,separators=(",",":"))
if __name__=="__main__":main()
