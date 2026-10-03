"""EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-COLLATERAL-STATE-COMPATIBILITY-ATTRIBUTION-063."""
import argparse
import hashlib
import importlib.util
import itertools
import json
import math
from pathlib import Path

EXPERIMENT="EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-COLLATERAL-STATE-COMPATIBILITY-ATTRIBUTION-063"
PRIOR_PATH=Path("research/applications/plane/exp-dgr-external-interleaved-pipeline-020.py")
PACKETS=12
PROSE="C"
TARGET_SCHEDULES=(("A","C","B"),("C","A","B"))
TRANSFER_SOURCES={
    "A":{"file":"code.bin","sha256":"66bb25b24a0316b4965c64798494de93a1d7332672b15b5f430ab6a2fb4b9d45","bytes":41453},
    "B":{"file":"structured.bin","sha256":"95ddbd0eaef29aad5ecfc74f9da21b795481f58b2c59380324a445fcd4d08932","bytes":14365},
    "C":{"file":"technical-prose.bin","sha256":"48c3d95b8b03864a4af41d892710675956cde85afd0d5d6c331594de9f17881b","bytes":1454},
}
SHARED5=(
    (118,101,108,111),
    (101,118,101,108),
    (100,101,118,101),
    (111,112,109,101),
    (32,32,32,32),
)
AC_SPEC=((32,110,111,116),(61,61,61,61))
BC_SPEC=((97,116,105,111),(10,32,32,32))
POOL=tuple(sorted(AC_SPEC+BC_SPEC))
VARIANT_PAIRS=tuple(itertools.combinations(POOL,2))
ORIGINAL_AC_PAIR=frozenset(AC_SPEC)
BC_KEYS=frozenset(BC_SPEC)

def load_transfer(root,m):
    root=Path(root);out={};total=0
    for name in ("A","B","C"):
        spec=TRANSFER_SOURCES[name];path=root/spec["file"]
        try:data=path.read_bytes()
        except OSError:
            data=b"";m["source_identity_mismatch_count"]+=1.0;m["transfer_manifest_identity_mismatch_count"]+=1.0
        actual=hashlib.sha256(data).hexdigest()
        if len(data)!=spec["bytes"] or actual!=spec["sha256"]:
            m["source_identity_mismatch_count"]+=1.0;m["transfer_manifest_identity_mismatch_count"]+=1.0
        total+=len(data)
        split=len(data)*60//100
        if split<=0 or split>=len(data):
            m["invalid_evaluation_rows"]+=1.0;out[name]=(b"",b"")
        else:out[name]=(data[:split],data[split:])
    m["source_count"]=3.0;m["total_source_bytes"]=float(total)
    return out

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
    n=max(1,len(data)*p//PACKETS)
    return data[:min(n,len(data))]

def run(root):
    p20=load_prior();p17=p20.load_prior_experiment();p16=p17.load_prior_experiment()
    p15=p16.load_prior_experiment();p14=p15.load_prior_experiment();p13=p14.load_prior_experiment()
    ad=p13.load_prior_experiment();eg=ad.load_prior_experiment();wake=eg.load_wake();pressure=wake.load_pressure();learner=pressure.load_prior()
    m={
      "source_identity_mismatch_count":0.0,"source_count":0.0,"total_source_bytes":0.0,
      "transfer_manifest_identity_mismatch_count":0.0,"base_training_identity_mismatch_count":0.0,
      "target_schedule_count":2.0,"variant_count":6.0,"packet_budget_per_schedule":12.0,
      "history_byte_budget_mismatch_count":0.0,"variant_selection_heldout_use_count":0.0,
      "original_ac_failure_schedule_count":0.0,"bc_containing_variant_rescue_both_count":0.0,
      "bc_containing_variant_rescue_one_count":0.0,"bc_containing_variant_prose_positive_both_count":0.0,
      "donor_missing_key_count":0.0,"variant_reserved_key_missing_count":0.0,
      "required_union_over_capacity_count":0.0,"state_capacity_failure_count":0.0,
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
            if r is None:
                m["variant_reserved_key_missing_count"]+=1.0;m["invalid_evaluation_rows"]+=1.0
            else:out.append(r)
        if len(out)!=7:m["invalid_evaluation_rows"]+=1.0
        part(rows,out)
        return wake.active_map(out)

    def inject(rows,fm,donor_rows,donor_map,required,cue):
        out=list(rows);om=dict(fm);keys={r["key"] for r in out};dby={r["key"]:r for r in donor_rows}
        missing=[k for k in required if k not in keys]
        if not missing:return out,om
        rr,sc=rank(out,om,cue);rs=set(required)
        ev=sorted([r for r in rr if r["key"] not in rs],key=lambda r:(sc[r["key"]],r["utility"],tuple(-x for x in r["key"])))
        if len(ev)<len(missing):
            m["state_capacity_failure_count"]+=1.0;m["invalid_evaluation_rows"]+=1.0;return out,om
        ev=ev[:len(missing)];eks={r["key"] for r in ev};out=[r for r in out if r["key"] not in eks]
        for k in eks:om.pop(k,None)
        for k in missing:
            r=dby.get(k)
            if r is None or k not in donor_map:
                m["donor_missing_key_count"]+=1.0;m["invalid_evaluation_rows"]+=1.0;continue
            out.append(r);om[k]=donor_map[k]
        if len(out)!=16 or len({r["key"] for r in out})!=16 or len(om)!=16:
            m["state_capacity_failure_count"]+=1.0;m["invalid_evaluation_rows"]+=1.0
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

    # Frozen B+C training-only donor state used only to source preregistered keys.
    bcue,beval=d["B"];ccue,ceval=d["C"]
    bhist,chist=rebalanced("B","C",bcue,ccue)
    bcrows,bcmap=build({"B":(bhist,beval),"C":(chist,ceval)},["B","C"])

    first={(si,vi):13 for si in range(2) for vi in range(6)}
    prose_positive={(si,vi):False for si in range(2) for vi in range(6)}
    diagnostics=[]
    for si,(an,bn,cn) in enumerate(TARGET_SCHEDULES):
        ac,ae=d[an];bc,be=d[bn];fc,fe=d[cn]
        ah,bh=rebalanced(an,bn,ac,bc)
        acrows,acmap=build({an:(ah,ae),bn:(bh,be)},[an,bn])
        derived=mix(ah,bh)
        if not derived:m["invalid_evaluation_rows"]+=1.0;continue
        rr,_=rank(acrows,acmap,derived)
        if len(rr)<6:m["invalid_evaluation_rows"]+=1.0;continue
        carry=tuple(r["key"] for r in rr[:6])

        donor_by={r["key"]:r for r in acrows};donor_map=dict(acmap)
        for r in bcrows:
            if r["key"] not in donor_by:
                donor_by[r["key"]]=r
                if r["key"] in bcmap:donor_map[r["key"]]=bcmap[r["key"]]
        donor_rows=list(donor_by.values())

        prose_eval=ae if an==PROSE else be
        partner_eval=be if an==PROSE else ae
        future_half=fc[len(fc)//2:]
        dep_eval=mix(mix(ae,be),fe)
        if not future_half or not dep_eval:m["invalid_evaluation_rows"]+=1.0;continue

        schedule_diag=[]
        for p in range(1,13):
            cp=packet_prefix(future_half,p);dep=mix(derived,cp)
            if not cp or not dep:m["invalid_evaluation_rows"]+=1.0;continue
            frows,fmap=build({cn:(cp,fe)},[cn])
            packet_variants=[]
            for vi,pair in enumerate(VARIANT_PAIRS):
                guard=SHARED5+pair
                required=tuple(dict.fromkeys(carry+guard))
                if len(required)>16:
                    m["required_union_over_capacity_count"]+=1.0;m["invalid_evaluation_rows"]+=1.0
                vrows,vmap=inject(frows,fmap,donor_rows,donor_map,required,dep)
                am=select_exact(vrows,vmap,guard)
                dd=score(dep_eval,am);pp=score(prose_eval,am);qq=score(partner_eval,am)
                ok=dd>0 and pp>0 and qq>0
                if pp>0:prose_positive[(si,vi)]=True
                if first[(si,vi)]==13 and ok:first[(si,vi)]=p
                packet_variants.append({"variant":vi,"pair":[list(k) for k in pair],"dependent":dd,"prose":pp,"partner":qq,"success":ok})
            schedule_diag.append({"packet":p,"variants":packet_variants})
        diagnostics.append({"schedule_index":si,"schedule":[an,bn,cn],"packets":schedule_diag})

    original_index=None
    for vi,pair in enumerate(VARIANT_PAIRS):
        if frozenset(pair)==ORIGINAL_AC_PAIR:original_index=vi
    if original_index is None:
        m["invalid_evaluation_rows"]+=1.0
    else:
        for si in range(2):
            if first[(si,original_index)]==13:m["original_ac_failure_schedule_count"]+=1.0

    variant_summary=[]
    for vi,pair in enumerate(VARIANT_PAIRS):
        successes=sum(1 for si in range(2) if first[(si,vi)]<=12)
        prose_both=all(prose_positive[(si,vi)] for si in range(2))
        bc_containing=bool(frozenset(pair)&BC_KEYS)
        if bc_containing and successes==2:m["bc_containing_variant_rescue_both_count"]+=1.0
        if bc_containing and successes==1:m["bc_containing_variant_rescue_one_count"]+=1.0
        if bc_containing and prose_both:m["bc_containing_variant_prose_positive_both_count"]+=1.0
        variant_summary.append({"variant":vi,"pair":[list(k) for k in pair],"bc_containing":bc_containing,"first_success_packets":[first[(0,vi)],first[(1,vi)]],"prose_positive_both":prose_both})

    if m["preserved_state_structure_count_max"]==0:m["invalid_evaluation_rows"]+=1.0
    assert len(VARIANT_PAIRS)==6
    assert all(math.isfinite(float(v)) for v in m.values())
    return {"schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,"metrics":m,"variant_summary":variant_summary,"diagnostics":diagnostics}

def main():
    p=argparse.ArgumentParser();p.add_argument("--root",required=True);p.add_argument("--out",required=True);a=p.parse_args()
    with open(a.out,"w",encoding="utf-8",newline="\n") as f:json.dump(run(a.root),f,allow_nan=False,separators=(",",":"))

if __name__=="__main__":main()
