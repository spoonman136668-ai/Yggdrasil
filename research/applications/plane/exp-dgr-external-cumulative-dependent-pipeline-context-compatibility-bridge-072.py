"""EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-COMPATIBILITY-BRIDGE-072."""
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path

EXPERIMENT="EXP-DGR-EXTERNAL-CUMULATIVE-DEPENDENT-PIPELINE-CONTEXT-COMPATIBILITY-BRIDGE-072"
PRIOR_PATH=Path("research/applications/plane/exp-dgr-external-interleaved-pipeline-020.py")
P070_PATH=Path("research/applications/plane/exp-dgr-external-cumulative-dependent-pipeline-context-local-key-induction-070.py")
PACKETS=12
PROSE="C"
SCHEDULES=(("A","C","B"),("B","C","A"),("C","A","B"),("C","B","A"))
TRANSFER_SOURCES={
    "A":{"file":"code.bin","sha256":"50744a9e70d67d62c97f3f434f4f05788b6b8514c6bce46cf7dafbaf49e2abff","bytes":41453},
    "B":{"file":"structured.bin","sha256":"2a97ba02bc5e479b1738f6f0c3e09318bb5a255350c84de014ddbcebea46af56","bytes":14365},
    "C":{"file":"technical-prose.bin","sha256":"23c002a1984ed065abfdbafa82100ed54d6bf6276a947676e710a30c75d96017","bytes":1454},
}
RETAINED_KEY=(10,32,32,32)
RETAINED_STATE={"key":RETAINED_KEY,"best":32,"total":112,"best_count":112,"consistency":1.0,"utility":112.0,"cell_index":12,"map_best":32}

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

def load_p070():
    s=importlib.util.spec_from_file_location("p070_y72",P070_PATH)
    if s is None or s.loader is None:raise RuntimeError("P070_IMPORT_SPEC_FAILED")
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def compatibility_decision(root,m):
    p70=load_p070()
    rows,fm,prose_train=p70.canonical_donor(root,m)
    occ,obs,best,_=p70.scan_key(prose_train,RETAINED_KEY)
    direct=(occ>=1 and obs>=1 and best==RETAINED_STATE["best"])
    eligible=[]
    for row in rows:
        key=tuple(row["key"])
        rocc,robs,rbest,rarg=p70.scan_key(prose_train,key)
        map_best=fm.get(key)
        if rocc>=1 and robs>=1 and rbest==RETAINED_STATE["best"] and int(row["best"])==RETAINED_STATE["best"] and map_best is not None and int(map_best)==RETAINED_STATE["best"]:
            score=float(rocc)*float(row["consistency"])*(float(row["best_count"])/float(row["total"]))
            eligible.append({
                "key":key,"best":int(row["best"]),"total":int(row["total"]),
                "best_count":int(row["best_count"]),"consistency":float(row["consistency"]),
                "utility":float(row["utility"]),"cell_index":int(row["cell_index"]),
                "map_best":int(map_best),"train_occurrence_count":int(rocc),
                "train_argmax_count":int(rarg),"compatibility_score":score,
            })
    eligible.sort(key=lambda x:(-x["compatibility_score"],x["key"]))
    if direct: decision="DIRECT"
    elif len(eligible)>=2: decision="BRIDGE"
    else: decision="REJECT"
    return decision,eligible,{"occurrence_count":occ,"successor_observation_count":obs,"training_argmax":best}

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
      "candidate_selection_heldout_use_count":0.0,"transported_state_identity_mismatch_count":0.0,
      "candidate_reserved_key_missing_count":0.0,"candidate_required_union_over_capacity_count":0.0,"candidate_state_capacity_failure_count":0.0,
      "original_positive_prose_collateral_schedule_count":0.0,"passive_positive_prose_collateral_schedule_count":0.0,"active_positive_prose_collateral_schedule_count":0.0,
      "original_partner_collateral_failure_count":0.0,"passive_partner_collateral_failure_count":0.0,"active_partner_collateral_failure_count":0.0,
      "active_transport_use_schedule_count":0.0,"passive_transport_state_schedule_count":0.0,
      "original_mean_first_success_packet":0.0,"passive_mean_first_success_packet":0.0,"active_mean_first_success_packet":0.0,
      "preserved_state_structure_count_min":16.0,"preserved_state_structure_count_max":0.0,
      "active_structure_count_min":16.0,"active_structure_count_max":0.0,
      "retained_structure_count_min":16.0,"retained_structure_count_max":0.0,
      "matched_assignment_failure_count":0.0,"capacity_growth_event_count":0.0,"row_mutation_event_count":0.0,
      "tokenizer_use_count":0.0,"external_model_call_count":0.0,"invalid_evaluation_rows":0.0,
      "induction_source_count":0.0,"induction_source_bytes":0.0,
      "compatibility_decision_count":0.0,"heldout_compatibility_access_count":0.0,"post_result_decision_change_count":0.0,
      "direct_source_key_occurrence_count":0.0,"direct_source_successor_observation_count":0.0,"direct_source_argmax_match_count":0.0,
      "eligible_bridge_row_count":0.0,"bridge_width":0.0,"bridge_score_sum":0.0,
      "source_state_rewrite_count":0.0,"row_synthesis_count":0.0,
      "policy_positive_prose_collateral_schedule_count":0.0,"policy_partner_collateral_failure_count":0.0,
      "policy_nonprose_regression_schedule_count":0.0,
    }
    d=load_transfer(root,m)
    bt=[]
    for path,exp in learner.TRAIN_FILES:
        x,ok=learner.load_checked(path,exp);m["base_training_identity_mismatch_count"]+=float(not ok);bt.append(x)
    base=learner.baseline_train(bt)
    decision,eligible,direct_diag=compatibility_decision(root,m)
    bridge_states=eligible[:2] if decision=="BRIDGE" else []
    bridge_keys=tuple(tuple(x["key"]) for x in bridge_states)
    m["compatibility_decision_count"]=1.0
    m["direct_source_key_occurrence_count"]=float(direct_diag["occurrence_count"])
    m["direct_source_successor_observation_count"]=float(direct_diag["successor_observation_count"])
    m["direct_source_argmax_match_count"]=float(direct_diag["successor_observation_count"]>0 and direct_diag["training_argmax"]==RETAINED_STATE["best"])
    m["eligible_bridge_row_count"]=float(len(eligible))
    m["bridge_width"]=float(len(bridge_states))
    m["bridge_score_sum"]=sum(x["compatibility_score"] for x in bridge_states)

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

    transported_row={"key":RETAINED_KEY,"best":RETAINED_STATE["best"],"total":RETAINED_STATE["total"],"best_count":RETAINED_STATE["best_count"],"consistency":RETAINED_STATE["consistency"],"utility":RETAINED_STATE["utility"],"cell_index":RETAINED_STATE["cell_index"]}
    transported_map={RETAINED_KEY:RETAINED_STATE["map_best"]}
    if transported_row["best"]!=transported_map[RETAINED_KEY] or tuple(RETAINED_STATE["key"])!=RETAINED_KEY:
        m["transported_state_identity_mismatch_count"]+=1.0;m["invalid_evaluation_rows"]+=1.0
    bridge_rows=[]
    bridge_map={}
    for state in bridge_states:
        key=tuple(state["key"])
        bridge_rows.append({"key":key,"best":state["best"],"total":state["total"],"best_count":state["best_count"],"consistency":state["consistency"],"utility":state["utility"],"cell_index":state["cell_index"]})
        bridge_map[key]=state["map_best"]

    ofirst=[];pfirst=[];afirst=[];diagnostics=[]
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

        direct_by={r["key"]:r for r in hrows};direct_map=dict(hmap)
        if RETAINED_KEY not in direct_by:
            direct_by[RETAINED_KEY]=transported_row;direct_map[RETAINED_KEY]=transported_map[RETAINED_KEY]
        direct_rows=list(direct_by.values())
        direct_guard=original_guard if RETAINED_KEY in original_guard else tuple(list(original_guard[:6])+[RETAINED_KEY])

        policy_by={r["key"]:r for r in hrows};policy_map=dict(hmap)
        if decision=="DIRECT":
            policy_by=dict(direct_by);policy_map=dict(direct_map);policy_guard=direct_guard
        elif decision=="BRIDGE":
            for row in bridge_rows:
                key=row["key"]
                if key not in policy_by:
                    policy_by[key]=row;policy_map[key]=bridge_map[key]
            remain=[k for k in original_guard if k not in set(bridge_keys)]
            if len(remain)<5:m["invalid_evaluation_rows"]+=1.0
            policy_guard=tuple(remain[:5]+list(bridge_keys))
        else:
            policy_guard=original_guard
        policy_rows=list(policy_by.values())
        active_used=(policy_guard!=original_guard)
        if active_used:m["active_transport_use_schedule_count"]+=1.0
        if len(direct_guard)!=7 or len(set(direct_guard))!=7:m["invalid_evaluation_rows"]+=1.0
        if len(policy_guard)!=7 or len(set(policy_guard))!=7:m["invalid_evaluation_rows"]+=1.0
        m["passive_transport_state_schedule_count"]+=1.0

        future_half=fc[len(fc)//2:];dep_eval=mix(mix(ae,be),fe)
        if not future_half or not dep_eval:m["invalid_evaluation_rows"]+=1.0;continue
        first={"original":13,"passive":13,"active":13}
        original_prose_positive=False;passive_prose_positive=False;active_prose_positive=False
        original_partner_bad=False;passive_partner_bad=False;active_partner_bad=False;policy_nonprose_bad=False;packets=[]
        for p in range(1,13):
            cp=packet_prefix(future_half,p);dep=mix(derived,cp)
            if not cp or not dep:m["invalid_evaluation_rows"]+=1.0;continue
            frows,fmap=build({cn:(cp,fe)},[cn])

            original_required=tuple(dict.fromkeys(carry+original_guard))
            if len(original_required)>16:m["candidate_required_union_over_capacity_count"]+=1.0;m["invalid_evaluation_rows"]+=1.0
            orows,omap=inject(frows,fmap,hrows,hmap,original_required,dep)
            oam=select_exact(orows,omap,original_guard)
            od=score(dep_eval,oam);op=score(prose_eval,oam);oq=score(partner_eval,oam);ook=od>0 and op>0 and oq>0
            if op>0:original_prose_positive=True
            if od>0 and oq<=0:original_partner_bad=True
            if first["original"]==13 and ook:first["original"]=p

            passive_required=tuple(dict.fromkeys(carry+direct_guard))
            if len(passive_required)>16:m["candidate_required_union_over_capacity_count"]+=1.0;m["invalid_evaluation_rows"]+=1.0
            prows,pmap=inject(frows,fmap,direct_rows,direct_map,passive_required,dep)
            pam=select_exact(prows,pmap,direct_guard)
            pd=score(dep_eval,pam);pp=score(prose_eval,pam);pq=score(partner_eval,pam);pok=pd>0 and pp>0 and pq>0
            if pp>0:passive_prose_positive=True
            if pd>0 and pq<=0:passive_partner_bad=True
            if first["passive"]==13 and pok:first["passive"]=p

            active_required=tuple(dict.fromkeys(carry+policy_guard))
            if len(active_required)>16:m["candidate_required_union_over_capacity_count"]+=1.0;m["invalid_evaluation_rows"]+=1.0
            arows,amap=inject(frows,fmap,policy_rows,policy_map,active_required,dep)
            aam=select_exact(arows,amap,policy_guard)
            adp=score(dep_eval,aam);ap=score(prose_eval,aam);aq=score(partner_eval,aam);aok=adp>0 and ap>0 and aq>0
            if ap>0:active_prose_positive=True
            if adp>0 and aq<=0:active_partner_bad=True
            if first["active"]==13 and aok:first["active"]=p
            if adp<od or aq<oq:policy_nonprose_bad=True

            packets.append({"packet":p,
                "original":{"dependent":od,"prose":op,"partner":oq,"success":ook},
                "passive":{"dependent":pd,"prose":pp,"partner":pq,"success":pok},
                "active":{"dependent":adp,"prose":ap,"partner":aq,"success":aok}})

        ofirst.append(first["original"]);pfirst.append(first["passive"]);afirst.append(first["active"])
        if original_prose_positive:m["original_positive_prose_collateral_schedule_count"]+=1.0
        if passive_prose_positive:m["passive_positive_prose_collateral_schedule_count"]+=1.0
        if active_prose_positive:m["active_positive_prose_collateral_schedule_count"]+=1.0
        if original_partner_bad and first["original"]==13:m["original_partner_collateral_failure_count"]+=1.0
        if passive_partner_bad and first["passive"]==13:m["passive_partner_collateral_failure_count"]+=1.0
        if active_partner_bad and first["active"]==13:m["active_partner_collateral_failure_count"]+=1.0
        if policy_nonprose_bad:m["policy_nonprose_regression_schedule_count"]+=1.0
        diagnostics.append({"schedule_index":si,"schedule":[an,bn,cn],"active_transport_used":active_used,
            "original_guard":[list(k) for k in original_guard],"direct_guard":[list(k) for k in direct_guard],"active_guard":[list(k) for k in policy_guard],
            "first_success_packet":first,"packets":packets})

    if len(ofirst)!=4 or len(pfirst)!=4 or len(afirst)!=4:m["invalid_evaluation_rows"]+=1.0
    mean=lambda xs:sum(xs)/len(xs) if xs else 0.0
    m["original_mean_first_success_packet"]=mean(ofirst)
    m["passive_mean_first_success_packet"]=mean(pfirst)
    m["active_mean_first_success_packet"]=mean(afirst)
    m["policy_positive_prose_collateral_schedule_count"]=m["active_positive_prose_collateral_schedule_count"]
    m["policy_partner_collateral_failure_count"]=m["active_partner_collateral_failure_count"]
    if RETAINED_KEY!=(10,32,32,32) or RETAINED_STATE!={"key":RETAINED_KEY,"best":32,"total":112,"best_count":112,"consistency":1.0,"utility":112.0,"cell_index":12,"map_best":32}:
        m["source_state_rewrite_count"]+=1.0;m["invalid_evaluation_rows"]+=1.0
    if m["preserved_state_structure_count_max"]==0:m["invalid_evaluation_rows"]+=1.0
    assert all(math.isfinite(float(v)) for v in m.values())
    return {"schema":"yggdrasil.research-scientific-result.v1","experiment":EXPERIMENT,"compatibility_decision":decision,
        "metrics":m,"source_retained_state":RETAINED_STATE,"eligible_bridge_rows":eligible,
        "selected_bridge_rows":bridge_states,"diagnostics":diagnostics}

def main():
    p=argparse.ArgumentParser();p.add_argument("--root",required=True);p.add_argument("--out",required=True);a=p.parse_args()
    with open(a.out,"w",encoding="utf-8",newline="\n") as f:json.dump(run(a.root),f,allow_nan=False,separators=(",",":"))

if __name__=="__main__":main()
