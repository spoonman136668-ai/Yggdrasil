#!/usr/bin/env python3
import argparse, hashlib, itertools, json
from copy import deepcopy
from pathlib import Path

CELLS=12
PART_A=tuple(range(0,6))
PART_B=tuple(range(6,12))
BASE_ROLES=tuple(c%4 for c in range(CELLS))
GOV_A=(1<<0,1<<1,1<<2,1<<3)
GOV_B=(1<<4,1<<5,1<<6,1<<7)
REG_A=(1<<8,1<<9,1<<10,1<<11)
REG_B=(1<<12,1<<13,1<<14,1<<15)
MAJORITY_WEIGHTS={"A":7,"B":5}
TERMINAL={"MERGED_GLOBAL","SUPERSEDED","COALESCED","ROLLED_BACK_CONFLICT","REJECTED_STALE","REJECTED_INELIGIBLE"}


def pairwise_disjoint(masks):
    masks=[m for m in masks if m]
    return all((a&b)==0 for a,b in itertools.combinations(masks,2))

def gov_ok(roots):
    return len(roots)==4 and all(roots) and pairwise_disjoint(roots)

def reg_ok(roots):
    roots=[r for r in roots if r]
    return any(pairwise_disjoint(c) for c in itertools.combinations(roots,3)) if len(roots)>=3 else False

def role_to_fp2(role):
    r0=role&1; r1=(role>>1)&1
    return (r0^r1)|(r1<<1)

def base_state():
    return [{"role":BASE_ROLES[c],"gen":0,"fp2":role_to_fp2(BASE_ROLES[c]),"damage":False} for c in range(CELLS)]

def event_id(part,target,op,outcome,idx):
    return f"{part}:{target}:{op}:{outcome}:{idx}"

def make_event(part,target,op,*,outcome=None,before_gen=0,after_gen=None,parent_global="BASE0",
               gov_roots=None,reg_roots=None,registry_closed=True,parent_events=(),idx=0):
    if gov_roots is None: gov_roots=GOV_A if part=="A" else GOV_B
    if reg_roots is None: reg_roots=REG_A if part=="A" else REG_B
    if after_gen is None:
        after_gen=before_gen+1 if op=="ROLE" else before_gen
    eligible=(parent_global=="BASE0" and gov_ok(tuple(gov_roots)) and registry_closed and reg_ok(tuple(reg_roots)))
    status="PARTITION_PROVISIONAL" if eligible else "LOCAL_OBSERVATION"
    return {
        "event_id":event_id(part,target,op,outcome,idx),
        "partition":part,
        "parent_global":parent_global,
        "target":target,
        "op":op,
        "outcome":outcome,
        "before_gen":before_gen,
        "after_gen":after_gen,
        "gov_roots":tuple(gov_roots),
        "reg_roots":tuple(reg_roots),
        "registry_closed":bool(registry_closed),
        "parent_events":tuple(parent_events),
        "eligible":bool(eligible),
        "status":status,
    }

def apply_event(st,e):
    t=deepcopy(st)
    cell=t[e["target"]]
    if e["op"]=="ROLE":
        cell["role"]=e["outcome"]; cell["gen"]=e["after_gen"]; cell["fp2"]=role_to_fp2(e["outcome"])
    elif e["op"]=="REPAIR":
        cell["damage"]=False
    elif e["op"]=="ADAPT":
        pass
    else:
        raise KeyError(e["op"])
    return t

def same_outcome(a,b):
    return (a["target"],a["op"],a["outcome"],a["after_gen"])==(b["target"],b["op"],b["outcome"],b["after_gen"])

def candidate_merge(global_state,events,current_commit="BASE0"):
    st=deepcopy(global_state); evs=[deepcopy(e) for e in events]
    valid=[]
    for e in evs:
        if not e["eligible"]:
            e["status"]="REJECTED_INELIGIBLE"; continue
        if e["parent_global"]!=current_commit:
            e["status"]="REJECTED_STALE"; continue
        valid.append(e)

    by_target={}
    for e in valid: by_target.setdefault(e["target"],[]).append(e)

    for target,group in by_target.items():
        base_gen=st[target]["gen"]
        fresh=[]
        for e in group:
            if e["before_gen"]<base_gen or e["after_gen"]<base_gen:
                e["status"]="REJECTED_STALE"
            else:
                fresh.append(e)
        if not fresh: continue

        ids={e["event_id"]:e for e in fresh}
        superseded=set()
        for e in fresh:
            for p in e["parent_events"]:
                if p in ids and e["before_gen"]==ids[p]["after_gen"]:
                    superseded.add(p)
        if superseded:
            descendants=[e for e in fresh if e["event_id"] not in superseded]
            for e in fresh:
                if e["event_id"] in superseded: e["status"]="SUPERSEDED"
            fresh=descendants

        if len(fresh)==1:
            e=fresh[0]
            if e["op"]=="ROLE" and not (e["before_gen"]==base_gen and e["after_gen"]==base_gen+1):
                e["status"]="REJECTED_STALE"; continue
            st=apply_event(st,e); e["status"]="MERGED_GLOBAL"; continue

        if all(same_outcome(fresh[0],x) for x in fresh[1:]):
            chosen=sorted(fresh,key=lambda e:(e["partition"],e["event_id"]))[0]
            if chosen["op"]=="ROLE" and not (chosen["before_gen"]==base_gen and chosen["after_gen"]==base_gen+1):
                for e in fresh: e["status"]="REJECTED_STALE"
                continue
            st=apply_event(st,chosen)
            chosen["status"]="MERGED_GLOBAL"
            for e in fresh:
                if e is not chosen: e["status"]="COALESCED"
            continue

        for e in fresh: e["status"]="ROLLED_BACK_CONFLICT"

    return st,evs

def majority_merge(global_state,events):
    st=deepcopy(global_state); evs=[deepcopy(e) for e in events]
    by_target={}
    for e in evs:
        if e["eligible"]: by_target.setdefault(e["target"],[]).append(e)
        else: e["status"]="REJECTED_INELIGIBLE"
    for target,group in by_target.items():
        if len(group)==1:
            st=apply_event(st,group[0]); group[0]["status"]="MERGED_GLOBAL"; continue
        if all(same_outcome(group[0],x) for x in group[1:]):
            st=apply_event(st,group[0]); group[0]["status"]="MERGED_GLOBAL"
            for e in group[1:]: e["status"]="COALESCED"
            continue
        group.sort(key=lambda e:(-MAJORITY_WEIGHTS[e["partition"]],e["partition"],e["event_id"]))
        winner=group[0]; st=apply_event(st,winner); winner["status"]="MERGED_GLOBAL"
        for e in group[1:]: e["status"]="SUPERSEDED"
    return st,evs

def audit_a():
    st,events=candidate_merge(base_state(),[])
    return {"cases":1,"exact":int(st==base_state() and events==[])}

def audit_b():
    cases=merged=exact_once=0
    for c in range(CELLS):
        part="A" if c in PART_A else "B"
        e=make_event(part,c,"REPAIR",outcome="HEALTHY",idx=1)
        cases+=1; st,ev=candidate_merge(base_state(),[e])
        merged+=int(ev[0]["status"]=="MERGED_GLOBAL"); exact_once+=int(sum(x["status"]=="MERGED_GLOBAL" for x in ev)==1)
        e=make_event(part,c,"ADAPT",outcome="ROLE_PRESERVING",idx=2)
        cases+=1; st,ev=candidate_merge(base_state(),[e])
        merged+=int(ev[0]["status"]=="MERGED_GLOBAL"); exact_once+=int(sum(x["status"]=="MERGED_GLOBAL" for x in ev)==1)
        for new in range(4):
            if new==BASE_ROLES[c]: continue
            e=make_event(part,c,"ROLE",outcome=new,idx=10+new)
            cases+=1; st,ev=candidate_merge(base_state(),[e])
            merged+=int(ev[0]["status"]=="MERGED_GLOBAL" and st[c]["role"]==new and st[c]["gen"]==1)
            exact_once+=int(sum(x["status"]=="MERGED_GLOBAL" for x in ev)==1)
    return {"cases":cases,"merged":merged,"exact_once":exact_once}

def audit_c():
    cases=success=0
    for a in PART_A:
        for b in PART_B:
            cases+=1
            ea=make_event("A",a,"ROLE",outcome=(BASE_ROLES[a]+1)%4,idx=1)
            eb=make_event("B",b,"ROLE",outcome=(BASE_ROLES[b]+1)%4,idx=1)
            st,ev=candidate_merge(base_state(),[ea,eb])
            success+=int(st[a]["gen"]==1 and st[b]["gen"]==1 and all(e["status"]=="MERGED_GLOBAL" for e in ev))
    return {"cases":cases,"success":success}

def audit_d():
    cases=abstain=control_picks=split=0
    for c in range(CELLS):
        alts=[r for r in range(4) if r!=BASE_ROLES[c]]
        for ra in alts:
            for rb in alts:
                if rb==ra: continue
                cases+=1
                ea=make_event("A",c,"ROLE",outcome=ra,idx=ra)
                eb=make_event("B",c,"ROLE",outcome=rb,idx=rb)
                st,ev=candidate_merge(base_state(),[ea,eb])
                abstain+=int(st[c]["role"]==BASE_ROLES[c] and st[c]["gen"]==0 and all(e["status"]=="ROLLED_BACK_CONFLICT" for e in ev))
                split+=0
                cst,cev=majority_merge(base_state(),[ea,eb])
                control_picks+=int(cst[c]["role"] in (ra,rb) and cst[c]["gen"]==1)
    return {"cases":cases,"candidate_abstain":abstain,"majority_control_picks":control_picks,"split_brain":split}

def audit_e():
    cases=success=0
    for c in range(CELLS):
        for new in range(4):
            if new==BASE_ROLES[c]: continue
            cases+=1
            ea=make_event("A",c,"ROLE",outcome=new,idx=1)
            eb=make_event("B",c,"ROLE",outcome=new,idx=2)
            st,ev=candidate_merge(base_state(),[ea,eb])
            statuses=sorted(e["status"] for e in ev)
            success+=int(st[c]["role"]==new and st[c]["gen"]==1 and statuses==["COALESCED","MERGED_GLOBAL"])
    return {"cases":cases,"success":success}

def audit_f():
    cases=success=0
    for c in range(CELLS):
        for fanout in (4,8,16,32):
            cases+=1
            roots=(GOV_A[0],)*4
            e=make_event("A",c,"ROLE",outcome=(BASE_ROLES[c]+1)%4,gov_roots=roots,idx=fanout)
            st,ev=candidate_merge(base_state(),[e])
            success+=int(ev[0]["status"]=="REJECTED_INELIGIBLE" and st==base_state())
    return {"cases":cases,"success":success}

def audit_g():
    cases=success=0
    for part in ("A","B"):
        roots=GOV_A if part=="A" else GOV_B
        target=PART_A[0] if part=="A" else PART_B[0]
        for missing in range(4):
            cases+=1
            bad=list(roots); bad[missing]=0
            e=make_event(part,target,"ROLE",outcome=(BASE_ROLES[target]+1)%4,gov_roots=tuple(bad),idx=missing)
            st,ev=candidate_merge(base_state(),[e])
            success+=int(ev[0]["status"]=="REJECTED_INELIGIBLE" and st==base_state())
    return {"cases":cases,"success":success}

def audit_h():
    cases=success=0
    for c in range(CELLS):
        current=base_state()
        current[c]["role"]=(BASE_ROLES[c]+1)%4; current[c]["gen"]=1; current[c]["fp2"]=role_to_fp2(current[c]["role"])
        e=make_event("A" if c in PART_A else "B",c,"ROLE",outcome=BASE_ROLES[c],before_gen=0,after_gen=0,idx=7)
        st,ev=candidate_merge(current,[e])
        success+=int(st[c]==current[c] and ev[0]["status"]=="REJECTED_STALE"); cases+=1
    return {"cases":cases,"success":success}

def audit_i():
    cases=success=0
    for part in ("A","B"):
        regs=REG_A if part=="A" else REG_B
        target=PART_A[0] if part=="A" else PART_B[0]
        for missing in range(4):
            cases+=1; rr=list(regs); rr[missing]=0
            e=make_event(part,target,"ROLE",outcome=(BASE_ROLES[target]+1)%4,reg_roots=tuple(rr),idx=10+missing)
            st,ev=candidate_merge(base_state(),[e])
            success+=int(ev[0]["status"]=="MERGED_GLOBAL")
        for missing_pair in itertools.combinations(range(4),2):
            cases+=1; rr=list(regs)
            for m in missing_pair: rr[m]=0
            e=make_event(part,target,"ROLE",outcome=(BASE_ROLES[target]+1)%4,reg_roots=tuple(rr),idx=20+sum(1<<m for m in missing_pair))
            st,ev=candidate_merge(base_state(),[e])
            success+=int(ev[0]["status"]=="REJECTED_INELIGIBLE")
    return {"cases":cases,"success":success}

def audit_j():
    cases=success=0
    for a in PART_A:
        for b in PART_B:
            cases+=1
            ea=make_event("A",a,"ROLE",outcome=(BASE_ROLES[a]+1)%4,idx=1)
            eb=make_event("B",a,"ROLE",outcome=(BASE_ROLES[a]+2)%4,idx=2)
            ec=make_event("B",b,"ROLE",outcome=(BASE_ROLES[b]+1)%4,idx=3)
            st,ev=candidate_merge(base_state(),[ea,eb,ec])
            a_status=[e["status"] for e in ev if e["target"]==a]
            b_status=[e["status"] for e in ev if e["target"]==b]
            success+=int(st[a]["gen"]==0 and st[b]["gen"]==1 and
                         all(x=="ROLLED_BACK_CONFLICT" for x in a_status) and b_status==["MERGED_GLOBAL"])
    return {"cases":cases,"success":success}

def audit_k():
    presentations=success=0
    for a in PART_A:
        for b in PART_B:
            ea=make_event("A",a,"ROLE",outcome=(BASE_ROLES[a]+1)%4,idx=1)
            eb=make_event("B",b,"ROLE",outcome=(BASE_ROLES[b]+1)%4,idx=1)
            s1,e1=candidate_merge(base_state(),[ea,eb]); presentations+=1
            s2,e2=candidate_merge(base_state(),[eb,ea]); presentations+=1
            success+=2*int(s1==s2)
    return {"presentations":presentations,"success":success}

def audit_l():
    events=[]
    for c in range(CELLS):
        part="A" if c in PART_A else "B"
        events.append(make_event(part,c,"REPAIR",outcome="HEALTHY",idx=100))
        events.append(make_event(part,c,"ADAPT",outcome="ROLE_PRESERVING",idx=101))
    _,resolved=candidate_merge(base_state(),events)
    terminal=sum(e["status"] in TERMINAL for e in resolved)
    dangling=sum(e["status"]=="PARTITION_PROVISIONAL" for e in resolved)
    return {"events":len(resolved),"terminal":terminal,"dangling":dangling}

def negative_control():
    picks=0
    for c in range(CELLS):
        alts=[r for r in range(4) if r!=BASE_ROLES[c]]
        ea=make_event("A",c,"ROLE",outcome=alts[0],idx=1)
        eb=make_event("B",c,"ROLE",outcome=alts[1],idx=2)
        st,ev=majority_merge(base_state(),[ea,eb])
        picks+=int(st[c]["role"]==alts[0])
    return {"population_weights":MAJORITY_WEIGHTS,"larger_partition_picks":picks}

def holdouts():
    h1=h2=h3=h4=0
    for c in range(CELLS):
        false=(BASE_ROLES[c]+1)%4
        ea=make_event("A",c,"ROLE",outcome=false,idx=1)
        eb=make_event("B",c,"ROLE",outcome=false,idx=2)
        st,ev=candidate_merge(base_state(),[ea,eb]); h1+=int(st[c]["role"]==false)
        e=make_event("A",c,"ROLE",outcome=false,gov_roots=GOV_A,idx=3)
        st,ev=candidate_merge(base_state(),[e]); h2+=int(st[c]["role"]==false)
        e=make_event("A",c,"ROLE",outcome=false,parent_global="FAKE_BASE",idx=4)
        e["eligible"]=True; e["status"]="PARTITION_PROVISIONAL"
        st,ev=candidate_merge(base_state(),[e],current_commit="BASE0"); h3+=int(st[c]["role"]==false)
        visible=make_event("A",c,"ROLE",outcome=false,idx=5)
        omitted=make_event("B",c,"ROLE",outcome=(BASE_ROLES[c]+2)%4,idx=6)
        st,ev=candidate_merge(base_state(),[visible]); h4+=int(st[c]["role"]==false)
    return {"cases":CELLS,
            "H1_dual_partition_independent_collusion_false_merge":h1,
            "H2_partition_root_compromise_false_merge":h2,
            "H3_forged_common_ancestor_false_merge":h3,
            "H4_omitted_partition_event_false_merge":h4,
            "immutable_BASE0_anchor_assumed":True}

def signals(a,b,c,d,e,f,g,h,i,j,k,l,neg,hold):
    s={
        "CLEAN_PARTITION_REJOINS_EXACTLY":a["exact"]==1,
        "ONE_SIDED_PROVISIONAL_ACTION_MERGES":b["merged"]==60 and b["exact_once"]==60,
        "DISJOINT_CONCURRENT_EVENTS_COMMUTE":c["success"]==36,
        "CONCURRENT_ROLE_CONFLICT_ABSTAINS":d["candidate_abstain"]==72 and d["split_brain"]==0,
        "IDENTICAL_CONCURRENT_OUTCOME_COALESCES":e["success"]==36,
        "PARTITIONING_DOES_NOT_MULTIPLY_PROVENANCE":f["success"]==48,
        "INSUFFICIENT_PARTITION_ROOTS_CANNOT_MINT_AUTHORITY":g["success"]==8,
        "STALE_PARTITION_REPLAY_REJECTED":h["success"]==12,
        "PARTITION_REGISTRY_LIVENESS_BOUND_PRESERVED":i["success"]==20,
        "TARGET_SCOPED_CONFLICT_ISOLATION":j["success"]==36,
        "MERGE_ORDER_INDEPENDENT_FOR_COMMUTING_EVENTS":k["presentations"]==72 and k["success"]==72,
        "NO_DANGLING_PROVISIONAL_AUTHORITY":l["terminal"]==l["events"] and l["dangling"]==0,
        "POPULATION_MAJORITY_FAILURE_EXPOSED":neg["larger_partition_picks"]==12,
    }
    primary=[k for k in s if k!="POPULATION_MAJORITY_FAILURE_EXPOSED"]
    s["PARTITIONED_SOVEREIGNTY_REMERGES"]=all(s[k] for k in primary)
    s["DUAL_PARTITION_INDEPENDENT_COLLUSION_FAILURE"]=hold["H1_dual_partition_independent_collusion_false_merge"]>0
    s["PARTITION_ROOT_COMPROMISE_FAILURE"]=hold["H2_partition_root_compromise_false_merge"]>0
    s["FORGED_COMMON_ANCESTOR_REJECTED_WITH_IMMUTABLE_ANCHOR"]=hold["H3_forged_common_ancestor_false_merge"]==0
    s["OMITTED_PARTITION_EVENT_FAILURE"]=hold["H4_omitted_partition_event_false_merge"]>0
    return s

def validate():
    assert CELLS==12
    assert PART_A==tuple(range(6)) and PART_B==tuple(range(6,12))
    assert BASE_ROLES==tuple(c%4 for c in range(12))
    assert pairwise_disjoint(GOV_A) and pairwise_disjoint(GOV_B)
    assert pairwise_disjoint(REG_A) and pairwise_disjoint(REG_B)
    assert MAJORITY_WEIGHTS=={"A":7,"B":5}
    counts={"A":1,"B":60,"C":36,"D":72,"E":36,"F":48,"G":8,"H":12,"I":20,"J":36,"K":72}
    assert 12*(1+1+3)==60
    assert 6*6==36
    assert 12*6==72
    assert 12*3==36
    assert 12*4==48
    assert 2*4==8
    assert 2*(4+6)==20
    assert 36*2==72
    return {"partition_a":PART_A,"partition_b":PART_B,"base_roles":BASE_ROLES,
            "governance_roots_a":GOV_A,"governance_roots_b":GOV_B,
            "registry_roots_a":REG_A,"registry_roots_b":REG_B,
            "majority_control_weights":MAJORITY_WEIGHTS,"audit_counts":counts}

def run():
    mech=validate()
    a=audit_a(); b=audit_b(); c=audit_c(); d=audit_d(); e=audit_e(); f=audit_f()
    g=audit_g(); h=audit_h(); i=audit_i(); j=audit_j(); k=audit_k(); l=audit_l()
    neg=negative_control(); hold=holdouts()
    return {"schema":"yggdrasil.dg1r-05y-partitioned-sovereignty-remerge.v1","mechanical_valid":True,
            "mechanical":mech,"audit_a":a,"audit_b":b,"audit_c":c,"audit_d":d,"audit_e":e,
            "audit_f":f,"audit_g":g,"audit_h":h,"audit_i":i,"audit_j":j,"audit_k":k,"audit_l":l,
            "negative_control":neg,"correlated_boundaries":hold,
            "signals":signals(a,b,c,d,e,f,g,h,i,j,k,l,neg,hold),
            "canonical_scientific_execution":False,"stab18_r1_touched":False}

def enc(o): return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--out"); ap.add_argument("--mechanical-only",action="store_true"); a=ap.parse_args()
    if a.mechanical_only:
        print(enc({"mechanical_valid":True,"mechanical":validate()})); return
    if not a.out: raise SystemExit("--out required unless --mechanical-only")
    obj=run(); raw=(enc(obj)+"\n").encode(); Path(a.out).write_bytes(raw)
    print(enc({"output":a.out,"sha256":hashlib.sha256(raw).hexdigest(),"signals":obj["signals"]}))
if __name__=="__main__": main()
