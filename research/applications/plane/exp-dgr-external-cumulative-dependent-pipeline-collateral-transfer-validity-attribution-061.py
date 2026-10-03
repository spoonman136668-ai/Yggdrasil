"""EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-COLLATERAL-TRANSFER-VALIDITY-ATTRIBUTION-061."""
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path

EXPERIMENT="EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-COLLATERAL-TRANSFER-VALIDITY-ATTRIBUTION-061"
PRIOR_PATH=Path("research/applications/plane/exp-dgr-external-interleaved-pipeline-020.py")
ACTIVE=7
PACKETS=12
PROSE="C"
SCHEDULES=(("A","C","B"),("B","C","A"),("C","A","B"),("C","B","A"))

TRANSFER_MANIFEST_SHA256="c79f09eb3841309b38827ceffee6a14eb87973c8aa2cf817908ed05f10e5c250"
TRANSFER_SOURCES={
    "A":("code.bin",41453,"66bb25b24a0316b4965c64798494de93a1d7332672b15b5f430ab6a2fb4b9d45"),
    "B":("structured.bin",14365,"95ddbd0eaef29aad5ecfc74f9da21b795481f58b2c59380324a445fcd4d08932"),
    "C":("technical-prose.bin",1454,"48c3d95b8b03864a4af41d892710675956cde85afd0d5d6c331594de9f17881b"),
}

def load_transfer(root,m,invalid):
    root=Path(root);demands={};total=0
    if TRANSFER_MANIFEST_SHA256!="c79f09eb3841309b38827ceffee6a14eb87973c8aa2cf817908ed05f10e5c250":
        m["transfer_manifest_identity_mismatch_count"]+=1.0
    for name in ("A","B","C"):
        fn,n,h=TRANSFER_SOURCES[name]
        try:data=(root/fn).read_bytes()
        except OSError:
            data=b"";m["source_identity_mismatch_count"]+=1.0
        if len(data)!=n or hashlib.sha256(data).hexdigest()!=h:
            m["source_identity_mismatch_count"]+=1.0
        total+=len(data)
        split=len(data)*60//100
        if split<=0 or split>=len(data):
            invalid("derived_or_guard",1);demands[name]=(b"",b"")
        else:demands[name]=(data[:split],data[split:])
    m["source_count"]=3.0;m["total_source_bytes"]=float(total)
    return demands

def load_prior():
    s=importlib.util.spec_from_file_location("p020",PRIOR_PATH)
    if s is None or s.loader is None: raise RuntimeError("PRIOR_IMPORT_SPEC_FAILED")
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def mix(a,b):
    n=min(len(a),len(b))//32*32
    return b"".join(a[i:i+32]+b[i:i+32] for i in range(0,n,32))

def packet_prefix(data,p):
    if not data:return data
    if p>=PACKETS:return data
    n=max(1,len(data)*p//PACKETS)
    return data[:min(n,len(data))]

def run(root):
    p20=load_prior();p17=p20.load_prior_experiment();p16=p17.load_prior_experiment()
    p15=p16.load_prior_experiment();p14=p15.load_prior_experiment();p13=p14.load_prior_experiment()
    ad=p13.load_prior_experiment();eg=ad.load_prior_experiment();wake=eg.load_wake();pressure=wake.load_pressure();learner=pressure.load_prior()
    m={
      "source_identity_mismatch_count":0.0,"transfer_manifest_identity_mismatch_count":0.0,"source_count":0.0,"total_source_bytes":0.0,
      "base_training_identity_mismatch_count":0.0,"affected_schedule_count":4.0,"packet_budget_per_schedule":12.0,
      "history_byte_budget_mismatch_count":0.0,"candidate_selection_heldout_use_count":0.0,"candidate_k":7.0,
      "baseline_mean_first_success_packet":0.0,"candidate_mean_first_success_packet":0.0,
      "candidate_mean_packet_reduction":0.0,"candidate_positive_reduction_schedule_count":0.0,
      "candidate_positive_prose_collateral_schedule_count":0.0,"candidate_partner_collateral_failure_count":0.0,
      "preserved_state_structure_count_min":16.0,"preserved_state_structure_count_max":0.0,
      "active_structure_count_min":16.0,"active_structure_count_max":0.0,
      "retained_structure_count_min":16.0,"retained_structure_count_max":0.0,
      "matched_assignment_failure_count":0.0,"capacity_growth_event_count":0.0,"row_mutation_event_count":0.0,
      "tokenizer_use_count":0.0,"external_model_call_count":0.0,"invalid_evaluation_rows":0.0,
    }
    attribution_categories=("candidate_stats_overflow","candidate_stats_invalid","develop_radius_violation","state_shape","selection_or_rebuild","derived_or_guard","final_coverage")
    for cat in attribution_categories:m["attribution_"+cat+"_count"]=0.0
    def invalid(cat,n=1):
        v=float(n);m["invalid_evaluation_rows"]+=v;m["attribution_"+cat+"_count"]+=v
    d=load_transfer(root,m,invalid)
    bt=[]
    for path,exp in learner.TRAIN_FILES:
        x,ok=learner.load_checked(path,exp);m["base_training_identity_mismatch_count"]+=float(not ok);bt.append(x)
    base=learner.baseline_train(bt)

    def build(cur,names):
        ind={}
        for n in names:
            cue,_=cur[n];st,o,iv=learner.candidate_stats(bt+[cue]);invalid("candidate_stats_overflow",o);invalid("candidate_stats_invalid",iv)
            cells,rv=learner.develop(st);invalid("develop_radius_violation",rv)
            fm=learner.specialized_map(cells);rows=wake.known_rows(pressure,learner,cells,st)
            if len(fm)!=16 or len(rows)!=16:invalid("state_shape",1)
            ind[n]=rows
        st,o,iv=learner.candidate_stats(bt+[cur[n][0] for n in names]);invalid("candidate_stats_overflow",o);invalid("candidate_stats_invalid",iv)
        pooled,rv=learner.develop(st);invalid("develop_radius_violation",rv)
        cells,nsel,_,_=p16.build_matched_minimax_cells(learner,eg,base,st,pooled,ind,names,cur,p15)
        if nsel!=16:m["matched_assignment_failure_count"]+=1.0
        fm=learner.specialized_map(cells);rows=wake.known_rows(pressure,learner,cells,st)
        if len(fm)!=16 or len(rows)!=16:invalid("state_shape",1)
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
        if len(rows)!=16 or len(active)!=7 or ret!=9:invalid("state_shape",1)

    def select(rows,fm,cue,reserved=()):
        rr,_=rank(rows,fm,cue);by={r["key"]:r for r in rows};out=[];seen=set()
        for k in reserved:
            r=by.get(k)
            if r is None:invalid("selection_or_rebuild",1);continue
            if k not in seen:out.append(r);seen.add(k)
        if len(out)>7:invalid("selection_or_rebuild",1)
        for r in rr:
            if len(out)>=7:break
            if r["key"] in seen:continue
            out.append(r);seen.add(r["key"])
        if len(out)!=7:invalid("selection_or_rebuild",1)
        part(rows,out)
        return out,wake.active_map(out)

    def inject(rows,fm,hrows,hmap,carry,cue):
        out=list(rows);om=dict(fm);keys={r["key"] for r in out};hby={r["key"]:r for r in hrows}
        missing=[k for k in carry if k not in keys]
        if not missing:return out,om
        rr,sc=rank(out,om,cue);cs=set(carry)
        ev=sorted([r for r in rr if r["key"] not in cs],key=lambda r:(sc[r["key"]],r["utility"],tuple(-x for x in r["key"])))
        if len(ev)<len(missing):invalid("selection_or_rebuild",1);return out,om
        ev=ev[:len(missing)];eks={r["key"] for r in ev};out=[r for r in out if r["key"] not in eks]
        for k in eks:om.pop(k,None)
        for k in missing:
            r=hby.get(k)
            if r is None or k not in hmap:invalid("selection_or_rebuild",1);continue
            out.append(r);om[k]=hmap[k]
        if len(out)!=16 or len({r["key"] for r in out})!=16 or len(om)!=16:invalid("selection_or_rebuild",1)
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

    bfirst=[];cfirst=[];diagnostics=[]
    for si,(an,bn,cn) in enumerate(SCHEDULES):
        ac,ae=d[an];bc,be=d[bn];cc,ce=d[cn]
        ah,bh=rebalanced(an,bn,ac,bc)
        hd={an:(ah,ae),bn:(bh,be)}
        hrows,hmap=build(hd,[an,bn]);derived=mix(ah,bh)
        if not derived:invalid("derived_or_guard",1);continue
        rr,_=rank(hrows,hmap,derived)
        if len(rr)<6:invalid("derived_or_guard",1);continue
        carry=tuple(r["key"] for r in rr[:6])
        prose_hist=ah if an==PROSE else bh
        prose_eval=ae if an==PROSE else be
        partner_eval=be if an==PROSE else ae
        pr,_=rank(hrows,hmap,prose_hist)
        coalition_k=7
        if len(pr)<coalition_k:invalid("derived_or_guard",1);continue
        prose_guard=tuple(r["key"] for r in pr[:coalition_k])

        cf=cc[len(cc)//2:];dep_eval=mix(mix(ae,be),ce)
        if not cf or not dep_eval:invalid("derived_or_guard",1);continue
        first={"baseline":13,"candidate":13};candidate_partner_bad=False;candidate_prose_positive=False
        packets=[]
        for p in range(1,13):
            cp=packet_prefix(cf,p);dep=mix(derived,cp)
            if not cp or not dep:invalid("derived_or_guard",1);continue
            crows,cmap=build({cn:(cp,ce)},[cn]);rows,fmap=inject(crows,cmap,hrows,hmap,carry,dep)
            rec={"packet":p}
            _,bam=select(rows,fmap,dep,carry)
            bd=score(dep_eval,bam);bp=score(prose_eval,bam);bq=score(partner_eval,bam)
            bok=bd>0 and bp>0 and bq>0
            if first["baseline"]==13 and bok:first["baseline"]=p
            _,cam=select(rows,fmap,dep,prose_guard)
            cd=score(dep_eval,cam);cpv=score(prose_eval,cam);cq=score(partner_eval,cam)
            cok=cd>0 and cpv>0 and cq>0
            if cpv>0:candidate_prose_positive=True
            if cd>0 and cq<=0:candidate_partner_bad=True
            if first["candidate"]==13 and cok:first["candidate"]=p
            rec["baseline"]={"dependent":bd,"prose":bp,"partner":bq,"success":bok}
            rec["candidate"]={"dependent":cd,"prose":cpv,"partner":cq,"success":cok}
            packets.append(rec)
        bfirst.append(first["baseline"]);cfirst.append(first["candidate"])
        if first["candidate"]<first["baseline"]:m["candidate_positive_reduction_schedule_count"]+=1.0
        if candidate_prose_positive:m["candidate_positive_prose_collateral_schedule_count"]+=1.0
        if candidate_partner_bad and first["candidate"]==13:m["candidate_partner_collateral_failure_count"]+=1.0
        diagnostics.append({"schedule_index":si,"schedule":[an,bn,cn],"coalition_k":coalition_k,"prose_guard_keys":[list(k) for k in prose_guard],"first_success_packet":first,"packets":packets})

    if len(bfirst)!=4 or len(cfirst)!=4:invalid("final_coverage",1)
    mean=lambda xs:sum(xs)/len(xs) if xs else 0.0
    m["baseline_mean_first_success_packet"]=mean(bfirst);m["candidate_mean_first_success_packet"]=mean(cfirst)
    m["candidate_mean_packet_reduction"]=mean([float(x-y) for x,y in zip(bfirst,cfirst)])
    if m["preserved_state_structure_count_max"]==0:invalid("final_coverage",1)
    m["attribution_total_count"]=sum(m["attribution_"+cat+"_count"] for cat in attribution_categories)
    assert all(math.isfinite(float(v)) for v in m.values())
    return {"schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,"metrics":m,"diagnostics":diagnostics}

def main():
    p=argparse.ArgumentParser();p.add_argument("--root",required=True);p.add_argument("--out",required=True);a=p.parse_args()
    with open(a.out,"w",encoding="utf-8",newline="\n") as f:json.dump(run(a.root),f,allow_nan=False,separators=(",",":"))
if __name__=="__main__":main()
