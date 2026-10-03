"""EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-INDEXED-COLLATERAL-COALITION-064."""
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path

EXPERIMENT="EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-INDEXED-COLLATERAL-COALITION-064"
PRIOR_PATH=Path("research/applications/plane/exp-dgr-external-interleaved-pipeline-020.py")
PACKETS=12
PROSE="C"
SCHEDULES=(("A","C","B"),("B","C","A"),("C","A","B"),("C","B","A"))
TRANSFER_SOURCES={
    "A":{"file":"code.bin","sha256":"66bb25b24a0316b4965c64798494de93a1d7332672b15b5f430ab6a2fb4b9d45","bytes":41453},
    "B":{"file":"structured.bin","sha256":"95ddbd0eaef29aad5ecfc74f9da21b795481f58b2c59380324a445fcd4d08932","bytes":14365},
    "C":{"file":"technical-prose.bin","sha256":"48c3d95b8b03864a4af41d892710675956cde85afd0d5d6c331594de9f17881b","bytes":1454},
}
RETAINED_KEY=(10,32,32,32)
SHARED5=(
    (118,101,108,111),
    (101,118,101,108),
    (100,101,118,101),
    (111,112,109,101),
    (32,32,32,32),
)

def load_transfer(root,m):
    root=Path(root);out={};total=0
    for name in ("A","B","C"):
        spec=TRANSFER_SOURCES[name];path=root/spec["file"]
        try:data=path.read_bytes()
        except OSError:
            data=b"";m["source_identity_mismatch_count"]+=1.0;m["transfer_manifest_identity_mismatch_count"]+=1.0
        if len(data)!=spec["bytes"] or hashlib.sha256(data).hexdigest()!=spec["sha256"]:
            m["source_identity_mismatch_count"]+=1.0;m["transfer_manifest_identity_mismatch_count"]+=1.0
        total+=len(data);split=len(data)*60//100
        if split<=0 or split>=len(data):m["invalid_evaluation_rows"]+=1.0;out[name]=(b"",b"")
        else:out[name]=(data[:split],data[split:])
    m["source_count"]=3.0;m["total_source_bytes"]=float(total);return out

def load_prior():
    s=importlib.util.spec_from_file_location("p020",PRIOR_PATH)
    if s is None or s.loader is None:raise RuntimeError("PRIOR_IMPORT_SPEC_FAILED")
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def mix(a,b):
    n=min(len(a),len(b))//32*32
    return b"".join(a[i:i+32]+b[i:i+32] for i in range(0,n,32))

def packet_prefix(data,p):
    if not data:return data
    if p>=PACKETS:return data
    n=max(1,len(data)*p//PACKETS);return data[:min(n,len(data))]

def run(root):
    p20=load_prior();p17=p20.load_prior_experiment();p16=p17.load_prior_experiment()
    p15=p16.load_prior_experiment();p14=p15.load_prior_experiment();p13=p14.load_prior_experiment()
    ad=p13.load_prior_experiment();eg=ad.load_prior_experiment();wake=eg.load_wake();pressure=wake.load_pressure();learner=pressure.load_prior()
    m={
      "source_identity_mismatch_count":0.0,"source_count":0.0,"total_source_bytes":0.0,
      "transfer_manifest_identity_mismatch_count":0.0,"base_training_identity_mismatch_count":0.0,
      "affected_schedule_count":4.0,"packet_budget_per_schedule":12.0,"history_byte_budget_mismatch_count":0.0,
      "candidate_selection_heldout_use_count":0.0,"gate_use_schedule_count":0.0,"gate_noop_schedule_count":0.0,
      "retained_memory_donor_missing_count":0.0,"candidate_reserved_key_missing_count":0.0,
      "candidate_required_union_over_capacity_count":0.0,"candidate_state_capacity_failure_count":0.0,
      "baseline_mean_first_success_packet":0.0,"candidate_mean_first_success_packet":0.0,
      "candidate_mean_packet_reduction":0.0,"candidate_positive_reduction_schedule_count":0.0,
      "candidate_schedule_slower_than_baseline_count":0.0,"candidate_positive_prose_collateral_schedule_count":0.0,
      "candidate_partner_collateral_failure_count":0.0,
      "preserved_state_structure_count_min":16.0,"preserved_state_structure_count_max":0.0,
      "active_structure_count_min":16.0,"active_structure_count_max":0.0,
      "retained_structure_count_min":16.0,"retained_structure_count_max":0.0,
      "matched_assignment_failure_count":0.0,"capacity_growth_event_count":0.0,"row_mutation_event_count":0.0,
      "tokenizer_use_count":0.0,"external_model_call_count":0.0,"invalid_evaluation_rows":0.0,
    }
    d=load_transfer(root,m)
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

    def select_exact(rows,fm,guard):
        by={r["key"]:r for r in rows};out=[]
        for k in guard:
            r=by.get(k)
            if r is None:m["candidate_reserved_key_missing_count"]+=1.0;m["invalid_evaluation_rows"]+=1.0
            else:out.append(r)
        if len(out)!=7:m["invalid_evaluation_rows"]+=1.0
        part(rows,out);return wake.active_map(out)

    def select_baseline(rows,fm,cue,carry):
        rr,_=rank(rows,fm,cue);by={r["key"]:r for r in rows};out=[];seen=set()
        for k in carry:
            r=by.get(k)
            if r is None:m["invalid_evaluation_rows"]+=1.0;continue
            if k not in seen:out.append(r);seen.add(k)
        for r in rr:
            if len(out)>=7:break
            if r["key"] not in seen:out.append(r);seen.add(r["key"])
        if len(out)!=7:m["invalid_evaluation_rows"]+=1.0
        part(rows,out);return wake.active_map(out)

    def inject(rows,fm,donor_rows,donor_map,required,cue):
        out=list(rows);om=dict(fm);keys={r["key"] for r in out};dby={r["key"]:r for r in donor_rows}
        missing=[k for k in required if k not in keys]
        if not missing:return out,om
        rr,sc=rank(out,om,cue);rs=set(required)
        ev=sorted([r for r in rr if r["key"] not in rs],key=lambda r:(sc[r["key"]],r["utility"],tuple(-x for x in r["key"])))
        if len(ev)<len(missing):m["candidate_state_capacity_failure_count"]+=1.0;m["invalid_evaluation_rows"]+=1.0;return out,om
        ev=ev[:len(missing)];eks={r["key"] for r in ev};out=[r for r in out if r["key"] not in eks]
        for k in eks:om.pop(k,None)
        for k in missing:
            r=dby.get(k)
            if r is None or k not in donor_map:m["retained_memory_donor_missing_count"]+=1.0;m["invalid_evaluation_rows"]+=1.0;continue
            out.append(r);om[k]=donor_map[k]
        if len(out)!=16 or len({r["key"] for r in out})!=16 or len(om)!=16:
            m["candidate_state_capacity_failure_count"]+=1.0;m["invalid_evaluation_rows"]+=1.0
        return out,om

    def score(ev,am):
        b,_,_=pressure.model_correct_counts(learner,ev,base,{})
        _,a,_=pressure.model_correct_counts(learner,ev,base,am);return a-b

    def rebalanced(a_name,b_name,a_cue,b_cue):
        aa=a_cue[:len(a_cue)//2];bb=b_cue[:len(b_cue)//2];total=len(aa)+len(bb)
        if a_name==PROSE:
            add=len(a_cue)-len(aa);aa=a_cue;bb=b_cue[:len(bb)-add]
        elif b_name==PROSE:
            add=len(b_cue)-len(bb);bb=b_cue;aa=a_cue[:len(aa)-add]
        if min(len(aa),len(bb))<=0 or len(aa)+len(bb)!=total:m["history_byte_budget_mismatch_count"]+=1.0
        return aa,bb

    # Frozen retained-row donor: B+C training-only historical state.
    bcue,beval=d["B"];ccue,ceval=d["C"]
    bhist,chist=rebalanced("B","C",bcue,ccue)
    donor_rows,donor_map=build({"B":(bhist,beval),"C":(chist,ceval)},["B","C"])
    if RETAINED_KEY not in {r["key"] for r in donor_rows} or RETAINED_KEY not in donor_map:
        m["retained_memory_donor_missing_count"]+=1.0;m["invalid_evaluation_rows"]+=1.0

    bfirst=[];cfirst=[];diagnostics=[]
    for si,(an,bn,cn) in enumerate(SCHEDULES):
        ac,ae=d[an];bc,be=d[bn];fc,fe=d[cn]
        ah,bh=rebalanced(an,bn,ac,bc)
        hrows,hmap=build({an:(ah,ae),bn:(bh,be)},[an,bn]);derived=mix(ah,bh)
        if not derived:m["invalid_evaluation_rows"]+=1.0;continue
        rr,_=rank(hrows,hmap,derived)
        if len(rr)<6:m["invalid_evaluation_rows"]+=1.0;continue
        carry=tuple(r["key"] for r in rr[:6])
        prose_hist=ah if an==PROSE else bh
        prose_eval=ae if an==PROSE else be
        partner_eval=be if an==PROSE else ae
        pr,_=rank(hrows,hmap,prose_hist)
        if len(pr)<7:m["invalid_evaluation_rows"]+=1.0;continue
        original_guard=tuple(r["key"] for r in pr[:7])

        combined_by={r["key"]:r for r in hrows};combined_map=dict(hmap)
        for r in donor_rows:
            if r["key"] not in combined_by:
                combined_by[r["key"]]=r
                if r["key"] in donor_map:combined_map[r["key"]]=donor_map[r["key"]]
        combined_rows=list(combined_by.values())

        if RETAINED_KEY in original_guard:
            gated_guard=original_guard;m["gate_noop_schedule_count"]+=1.0;gate_used=False
        else:
            context_rows=[k for k in original_guard if k not in set(SHARED5)]
            if len(context_rows)!=2 or not all(k in original_guard for k in SHARED5):
                m["invalid_evaluation_rows"]+=1.0;gated_guard=original_guard
            else:
                gated_guard=SHARED5+(context_rows[0],RETAINED_KEY)
            m["gate_use_schedule_count"]+=1.0;gate_used=True
        if len(gated_guard)!=7 or len(set(gated_guard))!=7:m["invalid_evaluation_rows"]+=1.0

        future_half=fc[len(fc)//2:];dep_eval=mix(mix(ae,be),fe)
        if not future_half or not dep_eval:m["invalid_evaluation_rows"]+=1.0;continue
        first={"baseline":13,"candidate":13};candidate_prose_positive=False;candidate_partner_bad=False;packets=[]
        for p in range(1,13):
            cp=packet_prefix(future_half,p);dep=mix(derived,cp)
            if not cp or not dep:m["invalid_evaluation_rows"]+=1.0;continue
            frows,fmap=build({cn:(cp,fe)},[cn])
            brows,bmap=inject(frows,fmap,hrows,hmap,carry,dep)
            bam=select_baseline(brows,bmap,dep,carry)
            bd=score(dep_eval,bam);bp=score(prose_eval,bam);bq=score(partner_eval,bam);bok=bd>0 and bp>0 and bq>0
            if first["baseline"]==13 and bok:first["baseline"]=p

            required=tuple(dict.fromkeys(carry+gated_guard))
            if len(required)>16:m["candidate_required_union_over_capacity_count"]+=1.0;m["invalid_evaluation_rows"]+=1.0
            crows,cmap=inject(frows,fmap,combined_rows,combined_map,required,dep)
            cam=select_exact(crows,cmap,gated_guard)
            cd=score(dep_eval,cam);cpv=score(prose_eval,cam);cq=score(partner_eval,cam);cok=cd>0 and cpv>0 and cq>0
            if cpv>0:candidate_prose_positive=True
            if cd>0 and cq<=0:candidate_partner_bad=True
            if first["candidate"]==13 and cok:first["candidate"]=p
            packets.append({"packet":p,"baseline":{"dependent":bd,"prose":bp,"partner":bq,"success":bok},"candidate":{"dependent":cd,"prose":cpv,"partner":cq,"success":cok}})

        bfirst.append(first["baseline"]);cfirst.append(first["candidate"])
        if first["candidate"]<first["baseline"]:m["candidate_positive_reduction_schedule_count"]+=1.0
        if first["candidate"]>first["baseline"]:m["candidate_schedule_slower_than_baseline_count"]+=1.0
        if candidate_prose_positive:m["candidate_positive_prose_collateral_schedule_count"]+=1.0
        if candidate_partner_bad and first["candidate"]==13:m["candidate_partner_collateral_failure_count"]+=1.0
        diagnostics.append({"schedule_index":si,"schedule":[an,bn,cn],"gate_used":gate_used,"original_guard":[list(k) for k in original_guard],"gated_guard":[list(k) for k in gated_guard],"first_success_packet":first,"packets":packets})

    if len(bfirst)!=4 or len(cfirst)!=4:m["invalid_evaluation_rows"]+=1.0
    mean=lambda xs:sum(xs)/len(xs) if xs else 0.0
    m["baseline_mean_first_success_packet"]=mean(bfirst);m["candidate_mean_first_success_packet"]=mean(cfirst)
    m["candidate_mean_packet_reduction"]=mean([float(x-y) for x,y in zip(bfirst,cfirst)])
    if m["preserved_state_structure_count_max"]==0:m["invalid_evaluation_rows"]+=1.0
    assert all(math.isfinite(float(v)) for v in m.values())
    return {"schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,"metrics":m,"diagnostics":diagnostics}

def main():
    p=argparse.ArgumentParser();p.add_argument("--root",required=True);p.add_argument("--out",required=True);a=p.parse_args()
    with open(a.out,"w",encoding="utf-8",newline="\n") as f:json.dump(run(a.root),f,allow_nan=False,separators=(",",":"))

if __name__=="__main__":main()
