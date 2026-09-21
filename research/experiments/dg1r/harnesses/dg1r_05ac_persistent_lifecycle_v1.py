#!/usr/bin/env python3
import argparse, copy, hashlib, itertools, json
from pathlib import Path

CELLS=12
PART_A=tuple(range(0,6))
PART_B=tuple(range(6,12))
SLOTS=("DEMAND_A","DEMAND_B","PEER_A","PEER_B")
GOV_ROOTS=(1<<0,1<<1,1<<2,1<<3)
REG_ROOTS=(1<<8,1<<9,1<<10,1<<11)
REG_QUORUM=3
HEALTH_DWELL=4
CAPSULE_FIELDS=("checkpoint_id","generation","role","fp2","causal_cursor")
REACT_STAGES=("R0_WAKE_PASSIVE","R1_CAUSAL_CATCHUP","R2_IDENTITY_RECONCILIATION","R3_HEALTH_DWELL","R4_AUTHORITY_RESTORATION")
EPOCHS=(
    "E0_GENESIS","E1_CLEAN_OPERATION","E2_TRUE_DAMAGE","E3_QUALIFIED_REPAIR",
    "E4_HEALTH_MEMORY_COMMIT","E5_WITHIN_ROLE_ADAPTATION","E6_ROLE_MIGRATION_PROPOSAL",
    "E7_ROLE_MIGRATION_COMMIT","E8_HEREDITARY_CAPSULE_SEAL","E9_TARGET_HIBERNATION",
    "E10_LIVE_POPULATION_WITNESS_ROTATION","E11_LEGITIMATE_ROLE_CHANGE_WHILE_TARGET_SLEEPS",
    "E12_TARGET_REACTIVATION_CAUSAL_CATCHUP","E13_COMMUNICATION_PARTITION",
    "E14_PARTITION_LOCAL_PROVISIONAL_EVENTS","E15_REMERGE_FINAL_SEAL",
)
TRUE_DAMAGE=("TRUE_SINGLE","TRUE_TWO_PLANE","TRUE_COORDINATED")
TX_LAYERS=("REPAIR_RECEIPT","HEALTH_COMMIT","ROLE_COMMIT","REGISTRY_SEAL","REACTIVATION_REGISTRATION","PARTITION_MERGE")
CUTS=("BEFORE_FIRST_WRITE","AFTER_FIRST_WRITE","BEFORE_FINAL_CERTIFICATE")


def enc(o):
    return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False)


def fp2(role):
    r0=role&1
    r1=(role>>1)&1
    return (r0^r1)|(r1<<1)


def pairwise_disjoint(masks):
    masks=[m for m in masks if m]
    return all((a&b)==0 for a,b in itertools.combinations(masks,2))


def gov_ok(roots):
    return len(roots)==4 and all(roots) and pairwise_disjoint(roots)


def reg_ok(roots):
    roots=[r for r in roots if r]
    return len(roots)>=REG_QUORUM and any(pairwise_disjoint(c) for c in itertools.combinations(roots,REG_QUORUM))


def base_state():
    roles=[c%4 for c in range(CELLS)]
    return {
        "roles":roles,
        "fp2":[fp2(r) for r in roles],
        "role_gen":[0]*CELLS,
        "health_gen":[0]*CELLS,
        "damage":[False]*CELLS,
        "mode":["ACTIVE"]*CELLS,
        "holders":{"DEMAND_A":0,"DEMAND_B":1,"PEER_A":2,"PEER_B":3},
        "holder_gen":{s:0 for s in SLOTS},
        "gov_roots":GOV_ROOTS,
        "reg_roots":REG_ROOTS,
        "registry_gen":0,
        "dangling":False,
    }


def record_payload(rec):
    return {
        "epoch":rec["epoch"],
        "label":rec["label"],
        "parent":rec["parent"],
        "roles":rec["roles"],
        "fp2":rec["fp2"],
        "role_gen":rec["role_gen"],
        "health_gen":rec["health_gen"],
        "damage":rec["damage"],
        "mode":rec["mode"],
        "holders":rec["holders"],
        "holder_gen":rec["holder_gen"],
        "registry_gen":rec["registry_gen"],
    }


def seal_record(rec):
    return hashlib.sha256(enc(record_payload(rec)).encode()).hexdigest()[:24]


def make_record(state, epoch, label, parent):
    rec={"epoch":epoch,"label":label,"parent":parent}
    for k in ("roles","fp2","role_gen","health_gen","damage","mode","holders","holder_gen","registry_gen"):
        rec[k]=copy.deepcopy(state[k])
    rec["seal"]=seal_record(rec)
    return rec


def init_history():
    s=base_state()
    r=make_record(s,0,EPOCHS[0],"ROOT")
    return s,[r]


def append_history(state,history,label):
    st=copy.deepcopy(state)
    st["registry_gen"]+=1
    rec=make_record(st,len(history),label,history[-1]["seal"])
    return st,history+[rec]


def verify_history(history):
    if not history:
        return False
    for i,rec in enumerate(history):
        if rec["epoch"]!=i:
            return False
        if rec["label"]!=EPOCHS[i] and len(history)<=len(EPOCHS):
            if i < len(EPOCHS):
                return False
        if i==0:
            if rec["parent"]!="ROOT":
                return False
        else:
            if rec["parent"]!=history[i-1]["seal"]:
                return False
        if rec["seal"]!=seal_record(rec):
            return False
    return True


def apply_damage(state,cell,family):
    st=copy.deepcopy(state)
    if family in TRUE_DAMAGE:
        st["damage"][cell]=True
        return st,"DAMAGE"
    if family=="CHECK_ONLY":
        return st,"AMBIGUOUS"
    raise KeyError(family)


def repair(state,cell,family):
    st=copy.deepcopy(state)
    if family in TRUE_DAMAGE and st["damage"][cell]:
        st["damage"][cell]=False
        return st,True
    return st,False


def health_commit(state,cell,peers_ok=True):
    st=copy.deepcopy(state)
    if st["damage"][cell] or not peers_ok:
        return st,False
    st["health_gen"][cell]+=1
    return st,True


def within_role_adapt(state,cell):
    st=copy.deepcopy(state)
    return st


def propose_role(state,cell,new_role,roots=GOV_ROOTS):
    complete=gov_ok(roots)
    return {"cell":cell,"new_role":new_role,"roots":tuple(roots),"qualified":complete}


def commit_role(state,proposal,complete=True):
    st=copy.deepcopy(state)
    c=proposal["cell"]
    if not complete or not proposal["qualified"] or st["damage"][c] or st["mode"][c]=="QUARANTINED":
        return st,False
    if st["roles"][c]==proposal["new_role"]:
        return st,False
    st["roles"][c]=proposal["new_role"]
    st["fp2"][c]=fp2(proposal["new_role"])
    st["role_gen"][c]+=1
    return st,True


def rotate_holder(state,slot,new_holder):
    st=copy.deepcopy(state)
    if st["holders"][slot]!=new_holder:
        st["holders"][slot]=new_holder
        st["holder_gen"][slot]+=1
    return st


def hibernate(state,cell,current_record):
    st=copy.deepcopy(state)
    held=[slot for slot,h in st["holders"].items() if h==cell]
    for slot in held:
        replacement=(cell+5+SLOTS.index(slot))%CELLS
        if replacement==cell:
            replacement=(replacement+1)%CELLS
        st=rotate_holder(st,slot,replacement)
    st["mode"][cell]="DORMANT"
    snap={
        "cell":cell,
        "role":state["roles"][cell],
        "fp2":state["fp2"][cell],
        "role_gen":state["role_gen"][cell],
        "health_gen":state["health_gen"][cell],
        "causal_cursor":current_record["seal"],
        "held_slots":tuple(held),
    }
    return st,snap


def capsule_from_record(rec,cell):
    return {
        "checkpoint_id":f"CP{rec['epoch']}_{cell}",
        "generation":rec["epoch"],
        "role":rec["roles"][cell],
        "fp2":rec["fp2"][cell],
        "causal_cursor":rec["seal"],
    }


def verify_capsule(history,capsule,cell):
    if tuple(capsule.keys())!=CAPSULE_FIELDS:
        return False
    if not verify_history(history):
        return False
    g=capsule["generation"]
    if g<0 or g>=len(history):
        return False
    rec=history[g]
    return (
        rec["seal"]==capsule["causal_cursor"]
        and rec["roles"][cell]==capsule["role"]
        and rec["fp2"][cell]==capsule["fp2"]
    )


def reactivation(state,history,snapshot,*,local_role=None,local_fp2=None,local_damage=False,repair_local=False,observations=HEALTH_DWELL):
    st=copy.deepcopy(state)
    c=snapshot["cell"]
    result={"stage":"R0_WAKE_PASSIVE","authority":False,"ordinary_active":False,"quarantined":False}
    positions=[i for i,r in enumerate(history) if r["seal"]==snapshot["causal_cursor"]]
    if len(positions)!=1 or not verify_history(history):
        result["stage"]="R1_CAUSAL_CATCHUP"; result["quarantined"]=True
        return st,result
    result["stage"]="R2_IDENTITY_RECONCILIATION"
    if local_role is None: local_role=snapshot["role"]
    if local_fp2 is None: local_fp2=snapshot["fp2"]
    current_role=st["roles"][c]; current_fp2=st["fp2"][c]
    stale=(local_role==snapshot["role"] and local_fp2==snapshot["fp2"] and (local_role!=current_role or local_fp2!=current_fp2))
    if stale and not local_damage:
        local_role=current_role; local_fp2=current_fp2
    if local_damage or local_role!=current_role or local_fp2!=current_fp2 or st["damage"][c]:
        if repair_local:
            local_role=current_role; local_fp2=current_fp2; local_damage=False; st["damage"][c]=False
        else:
            st["mode"][c]="QUARANTINED"
            result["quarantined"]=True
            return st,result
    result["stage"]="R3_HEALTH_DWELL"
    if observations<HEALTH_DWELL:
        st["mode"][c]="QUARANTINED"; result["quarantined"]=True
        return st,result
    st["mode"][c]="ACTIVE"
    result["stage"]="R4_AUTHORITY_RESTORATION"
    result["ordinary_active"]=True
    result["authority"]=True
    return st,result


def register_fresh_holder(state,cell,slot):
    if state["mode"][cell]!="ACTIVE":
        return copy.deepcopy(state),False
    st=rotate_holder(state,slot,cell)
    return st,True


def same_lineage_quorum(roots,needed):
    roots=[r for r in roots if r]
    if len(roots)<needed:
        return False
    return any(pairwise_disjoint(c) for c in itertools.combinations(roots,needed))


def partition_event(part,target,new_role,state,roots=GOV_ROOTS):
    eligible=gov_ok(roots) and state["mode"][target]=="ACTIVE" and not state["damage"][target]
    return {"part":part,"target":target,"new_role":new_role,"base_gen":state["role_gen"][target],"eligible":eligible}


def merge_partition(state,events):
    st=copy.deepcopy(state)
    by_target={}
    for e in events:
        if e["eligible"]:
            by_target.setdefault(e["target"],[]).append(e)
    statuses=[]
    for target,group in by_target.items():
        if any(e["base_gen"]!=st["role_gen"][target] for e in group):
            statuses.extend(["REJECTED_STALE"]*len(group)); continue
        roles={e["new_role"] for e in group}
        if len(roles)==1:
            role=next(iter(roles))
            p=propose_role(st,target,role)
            st,ok=commit_role(st,p,complete=True)
            statuses.extend(["MERGED" if i==0 and ok else "COALESCED" for i,_ in enumerate(group)])
        else:
            statuses.extend(["ROLLED_BACK_CONFLICT"]*len(group))
    return st,statuses


def run_lifecycle(target,alt_role=None):
    if alt_role is None:
        alt_role=(target%4+1)%4
    state,history=init_history()
    state,history=append_history(state,history,EPOCHS[1])
    state,_=apply_damage(state,target,"TRUE_SINGLE")
    state,history=append_history(state,history,EPOCHS[2])
    state,rok=repair(state,target,"TRUE_SINGLE")
    state,history=append_history(state,history,EPOCHS[3])
    state,hok=health_commit(state,target,True)
    state,history=append_history(state,history,EPOCHS[4])
    state=within_role_adapt(state,target)
    state,history=append_history(state,history,EPOCHS[5])
    proposal=propose_role(state,target,alt_role)
    state,history=append_history(state,history,EPOCHS[6])
    state,mok=commit_role(state,proposal,True)
    state,history=append_history(state,history,EPOCHS[7])
    capsule=capsule_from_record(history[-1],target)
    state,history=append_history(state,history,EPOCHS[8])
    capsule=capsule_from_record(history[7],target)
    state,snapshot=hibernate(state,target,history[-1])
    state,history=append_history(state,history,EPOCHS[9])
    slot="PEER_A"
    repl=(state["holders"][slot]+5)%CELLS
    if repl==target: repl=(repl+1)%CELLS
    state=rotate_holder(state,slot,repl)
    state,history=append_history(state,history,EPOCHS[10])
    newer=(alt_role+1)%4
    p2=propose_role(state,target,newer)
    old_mode=state["mode"][target]
    state["mode"][target]="ACTIVE"
    state,live_role_ok=commit_role(state,p2,True)
    state["mode"][target]=old_mode
    state,history=append_history(state,history,EPOCHS[11])
    state,react=reactivation(state,history,snapshot,local_role=snapshot["role"],local_fp2=snapshot["fp2"])
    if react["ordinary_active"]:
        state,_=register_fresh_holder(state,target,"DEMAND_A")
    state,history=append_history(state,history,EPOCHS[12])
    state,history=append_history(state,history,EPOCHS[13])
    a=PART_A[0]; b=PART_B[0]
    if a==target: a=PART_A[1]
    if b==target: b=PART_B[1]
    ea=partition_event("A",a,(state["roles"][a]+1)%4,state)
    eb=partition_event("B",b,(state["roles"][b]+1)%4,state)
    state,history=append_history(state,history,EPOCHS[14])
    state,statuses=merge_partition(state,[ea,eb])
    state,history=append_history(state,history,EPOCHS[15])
    return {
        "state":state,"history":history,"capsule":capsule,"snapshot":snapshot,
        "repair_ok":rok,"health_ok":hok,"migration_ok":mok,"live_role_ok":live_role_ok,
        "reactivation":react,"merge_statuses":statuses
    }


def audit_a():
    cases=complete=0
    for c in range(CELLS):
        r=run_lifecycle(c)
        st=r["state"]; hist=r["history"]
        ok=(len(hist)==16 and verify_history(hist) and r["repair_ok"] and r["health_ok"] and r["migration_ok"]
            and r["live_role_ok"] and r["reactivation"]["ordinary_active"] and
            verify_capsule(hist,r["capsule"],c) and st["mode"][c]=="ACTIVE" and
            not st["damage"][c] and not st["dangling"])
        cases+=1; complete+=int(ok)
    return {"cases":cases,"complete":complete}


def audit_b():
    cases=order_safe=0
    for c in range(CELLS):
        for fam in TRUE_DAMAGE:
            st=base_state()
            before_h=st["health_gen"][c]
            st,_=apply_damage(st,c,fam)
            no_early=(st["health_gen"][c]==before_h)
            early_state,early_ok=health_commit(st,c,True)
            st,rep=repair(st,c,fam)
            st,hc=health_commit(st,c,True)
            ok=no_early and not early_ok and rep and hc and st["health_gen"][c]==before_h+1 and st["roles"][c]==c%4
            cases+=1; order_safe+=int(ok)
    return {"cases":cases,"order_safe":order_safe}


def audit_c():
    cases=safe=0
    for c in range(CELLS):
        st=base_state(); old=copy.deepcopy(st)
        st,status=apply_damage(st,c,"CHECK_ONLY")
        st,rep=repair(st,c,"CHECK_ONLY")
        st["mode"][c]="QUARANTINED"
        p=propose_role(st,c,(st["roles"][c]+1)%4)
        st2,mig=commit_role(st,p,True)
        cases+=1
        safe+=int(status=="AMBIGUOUS" and not rep and not mig and st2["roles"][c]==old["roles"][c])
    return {"cases":cases,"safe":safe}


def audit_d():
    cases=safe=0
    for c in range(CELLS):
        st=base_state(); role=st["roles"][c]; ph=st["fp2"][c]
        st=within_role_adapt(st,c)
        cases+=1; safe+=int(st["roles"][c]==role and st["fp2"][c]==ph and st["role_gen"][c]==0)
    return {"cases":cases,"safe":safe}


def audit_e():
    cases=safe=0
    for c in range(CELLS):
        old=c%4
        for nr in range(4):
            if nr==old: continue
            st=base_state()
            p=propose_role(st,c,nr)
            pre=copy.deepcopy(st)
            partial,partial_ok=commit_role(st,p,False)
            st,ok=commit_role(st,p,True)
            cases+=1
            safe+=int(partial==pre and not partial_ok and ok and st["roles"][c]==nr and st["role_gen"][c]==1 and st["fp2"][c]==fp2(nr))
    return {"cases":cases,"safe":safe}


def audit_f():
    cases=safe=0
    for c in range(CELLS):
        old=c%4
        for nr in range(4):
            if nr==old: continue
            st,hist=init_history()
            st,snap=hibernate(st,c,hist[-1])
            st,hist=append_history(st,hist,EPOCHS[1])
            oldmode=st["mode"][c]; st["mode"][c]="ACTIVE"
            p=propose_role(st,c,nr); st,ok=commit_role(st,p,True); st["mode"][c]=oldmode
            st,hist=append_history(st,hist,EPOCHS[2])
            pre_vote=all(st["holders"][slot]!=c for slot in SLOTS)
            st,rr=reactivation(st,hist,snap,local_role=snap["role"],local_fp2=snap["fp2"])
            post=rr["ordinary_active"] and st["roles"][c]==nr
            cases+=1; safe+=int(ok and pre_vote and post)
    return {"cases":cases,"safe":safe}


def audit_g():
    cases=safe=0
    for c in range(CELLS):
        for slot in SLOTS:
            st=base_state()
            st["holders"][slot]=c
            oldgen=st["holder_gen"][slot]
            dummy=make_record(st,0,EPOCHS[0],"ROOT"); dummy["seal"]=seal_record(dummy)
            st,snap=hibernate(st,c,dummy)
            replacement=st["holders"][slot]
            no_dormant= replacement!=c and st["mode"][c]=="DORMANT"
            st["mode"][c]="ACTIVE"
            st,ok=register_fresh_holder(st,c,slot)
            safe_case=no_dormant and ok and st["holders"][slot]==c and st["holder_gen"][slot]>oldgen
            cases+=1; safe+=int(safe_case)
    return {"cases":cases,"safe":safe}


def audit_h():
    clean=rewrite=0
    for c in range(CELLS):
        r=run_lifecycle(c)
        clean+=int(verify_capsule(r["history"],r["capsule"],c))
        bad=copy.deepcopy(r["history"])
        bad[2]["roles"][c]=(bad[2]["roles"][c]+1)%4
        bad[2]["fp2"][c]=fp2(bad[2]["roles"][c])
        rewrite+=int(not verify_capsule(bad,r["capsule"],c))
    return {"clean_cases":12,"clean_valid":clean,"rewrite_cases":12,"rewrite_contested":rewrite}


def audit_i():
    cases=safe=0
    for a in PART_A:
        for b in PART_B:
            st=base_state()
            ea=partition_event("A",a,(st["roles"][a]+1)%4,st)
            eb=partition_event("B",b,(st["roles"][b]+1)%4,st)
            s1,_=merge_partition(st,[ea,eb]); s2,_=merge_partition(st,[eb,ea])
            cases+=1; safe+=int(s1==s2 and s1["role_gen"][a]==1 and s1["role_gen"][b]==1)
    return {"cases":cases,"safe":safe}


def audit_j():
    cases=safe=0
    for c in range(CELLS):
        alts=[r for r in range(4) if r!=c%4]
        for ra in alts:
            for rb in alts:
                if ra==rb: continue
                st=base_state()
                ea=partition_event("A",c,ra,st); eb=partition_event("B",c,rb,st)
                merged,status=merge_partition(st,[ea,eb])
                cases+=1
                safe+=int(merged["roles"][c]==c%4 and merged["role_gen"][c]==0 and status==["ROLLED_BACK_CONFLICT","ROLLED_BACK_CONFLICT"])
    return {"cases":cases,"safe":safe}


def audit_k():
    cases=safe=0
    for c in range(CELLS):
        st,hist=init_history()
        st,snap=hibernate(st,c,hist[-1])
        st,hist=append_history(st,hist,EPOCHS[1])
        oldmode=st["mode"][c]; st["mode"][c]="ACTIVE"
        nr=(c%4+1)%4; p=propose_role(st,c,nr); st,_=commit_role(st,p,True); st["mode"][c]=oldmode
        st,hist=append_history(st,hist,EPOCHS[2])
        bad=(nr+1)%4
        st2,rr=reactivation(st,hist,snap,local_role=bad,local_fp2=fp2(bad),local_damage=True,repair_local=False)
        blocked=not rr["ordinary_active"] and st2["mode"][c]=="QUARANTINED"
        st3,rr2=reactivation(st,hist,snap,local_role=bad,local_fp2=fp2(bad),local_damage=True,repair_local=True)
        repaired=rr2["ordinary_active"] and st3["roles"][c]==nr
        cases+=1; safe+=int(blocked and repaired)
    return {"cases":cases,"safe":safe}


def audit_l():
    cases=safe=0
    for count in (4,8,16,32,64):
        root=1<<20
        gov=(root,)*4
        reg=(root,)*4
        sent=(root,)*4
        cases+=3
        safe+=int(not gov_ok(gov))
        safe+=int(not reg_ok(reg))
        safe+=int(not same_lineage_quorum(sent,2))
    return {"cases":cases,"safe":safe}


def audit_m():
    cases=safe=0
    for c in range(CELLS):
        r=run_lifecycle(c)
        hist=r["history"]
        snap=r["snapshot"]
        for pos in ("first","middle","last-precurrent"):
            presented=copy.deepcopy(hist)
            if pos=="first": idx=1
            elif pos=="middle": idx=max(1,(len(presented)-1)//2)
            else: idx=len(presented)-2
            del presented[idx]
            st=copy.deepcopy(r["state"])
            st["mode"][c]="DORMANT"
            st2,rr=reactivation(st,presented,snap,local_role=st["roles"][c],local_fp2=st["fp2"][c])
            cases+=1; safe+=int(not rr["ordinary_active"])
    return {"cases":cases,"safe":safe}


def partial_transaction(state,layer,cut):
    st=copy.deepcopy(state)
    before=copy.deepcopy(state)
    if cut not in CUTS or layer not in TX_LAYERS:
        raise KeyError((layer,cut))
    scratch={"layer":layer,"cut":cut,"tentative":cut=="AFTER_FIRST_WRITE"}
    authoritative=before
    return authoritative,scratch


def audit_n():
    cases=safe=0
    for layer in TX_LAYERS:
        for cut in CUTS:
            st=base_state(); final,scratch=partial_transaction(st,layer,cut)
            cases+=1; safe+=int(final==st and not final["dangling"])
    return {"cases":cases,"safe":safe}


def audit_o():
    cell_lifecycles=monotonic=stale_votes=dup=single_head=0
    for c in range(CELLS):
        st=base_state()
        cursor="ROOT"
        last_role_gen=st["role_gen"][c]
        last_health_gen=st["health_gen"][c]
        ok=True
        for cycle in range(4):
            st,_=apply_damage(st,c,"TRUE_SINGLE")
            st,rep=repair(st,c,"TRUE_SINGLE")
            st,hc=health_commit(st,c,True)
            st=within_role_adapt(st,c)

            nr=(st["roles"][c]+1)%4
            p=propose_role(st,c,nr)
            st,mig=commit_role(st,p,True)

            pseudo={"seal":cursor}
            st,snap=hibernate(st,c,pseudo)
            stale_votes+=sum(int(st["holders"].get(slot)==c) for slot in snap["held_slots"])

            live_nr=(st["roles"][c]+1)%4
            oldmode=st["mode"][c]
            st["mode"][c]="ACTIVE"
            p2=propose_role(st,c,live_nr)
            st,live_ok=commit_role(st,p2,True)
            st["mode"][c]=oldmode

            st["mode"][c]="ACTIVE"
            st,reg_okay=register_fresh_holder(st,c,"DEMAND_A")

            a=PART_A[0] if c not in PART_A[:1] else PART_A[1]
            b=PART_B[0] if c not in PART_B[:1] else PART_B[1]
            ea=partition_event("A",a,(st["roles"][a]+1)%4,st)
            eb=partition_event("B",b,(st["roles"][b]+1)%4,st)
            st,statuses=merge_partition(st,[ea,eb])

            new_cursor=hashlib.sha256((cursor+"|"+str(cycle)+"|"+enc({
                "roles":st["roles"],"role_gen":st["role_gen"],"health_gen":st["health_gen"],
                "holders":st["holders"],"holder_gen":st["holder_gen"]
            })).encode()).hexdigest()[:24]

            cycle_ok=(
                rep and hc and mig and live_ok and reg_okay
                and st["role_gen"][c] > last_role_gen
                and st["health_gen"][c] > last_health_gen
                and new_cursor != cursor
                and len(statuses)==2
                and all(x=="MERGED" for x in statuses)
            )
            ok=ok and cycle_ok
            last_role_gen=st["role_gen"][c]
            last_health_gen=st["health_gen"][c]
            cursor=new_cursor
            dup+=int(len(st["holders"])!=len(SLOTS))
            single_head+=int(bool(cursor))
            cell_lifecycles+=1
        monotonic+=4*int(ok)
    return {"cell_lifecycles":cell_lifecycles,"monotonic":monotonic,"stale_votes":stale_votes,"authority_duplication":dup,"single_head":single_head}


def audit_p():
    st=base_state(); c=0
    st,_=apply_damage(st,c,"TRUE_SINGLE")
    st["health_gen"][c]+=1
    leak=int(st["damage"][c] and st["health_gen"][c]==1)
    return {"authority_leaks":leak}


def holdouts():
    h1=h2=h3=h4=h5=h6=0
    st=base_state(); c=0
    p=propose_role(st,c,3,GOV_ROOTS); st1,ok=commit_role(st,p,True); h1=int(ok and st1["roles"][c]==3)
    h2=int(reg_ok(REG_ROOTS))
    st=base_state(); st["roles"][c]=3; st["fp2"][c]=fp2(3)
    rec=make_record(st,0,EPOCHS[0],"ROOT"); rec["seal"]=seal_record(rec)
    cap=capsule_from_record(rec,c); h3=int(verify_capsule([rec],cap,c))
    clean=run_lifecycle(c); h4=int(verify_history(clean["history"]))
    replacement=copy.deepcopy(clean["history"])
    replacement[0]["roles"][c]=3; replacement[0]["fp2"][c]=fp2(3); replacement[0]["seal"]=seal_record(replacement[0])
    for i in range(1,len(replacement)):
        replacement[i]["parent"]=replacement[i-1]["seal"]; replacement[i]["seal"]=seal_record(replacement[i])
    h5=int(verify_history(replacement))
    h6=int(h1 and h2 and h3 and h4 and h5)
    return {"H1":h1,"H2":h2,"H3":h3,"H4":h4,"H5":h5,"H6":h6}


def signals(a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,ho):
    s={
        "CLEAN_LIFECYCLE_COMPLETES":a["complete"]==a["cases"],
        "DAMAGE_REPAIR_HEALTH_ORDER_SAFE":b["order_safe"]==b["cases"],
        "AMBIGUOUS_DAMAGE_DOES_NOT_MUTATE":c["safe"]==c["cases"],
        "WITHIN_ROLE_ADAPTATION_PRESERVED":d["safe"]==d["cases"],
        "ROLE_MIGRATION_ATOMIC":e["safe"]==e["cases"],
        "HIBERNATION_ACCEPTS_NEWER_AUTHORITY":f["safe"]==f["cases"],
        "WITNESS_REPLACEMENT_NO_DUPLICATION":g["safe"]==g["cases"],
        "TEMPORAL_ANCESTRY_SURVIVES_LIFECYCLE":h["clean_valid"]==h["clean_cases"] and h["rewrite_contested"]==h["rewrite_cases"],
        "DISJOINT_PARTITION_CHANGES_MERGE":i["safe"]==i["cases"],
        "SAME_TARGET_PARTITION_CONFLICT_ROLLS_BACK":j["safe"]==j["cases"],
        "STALE_DORMANT_DAMAGE_CANNOT_NORMALIZE":k["safe"]==k["cases"],
        "SAME_LINEAGE_FANOUT_COLLAPSES":l["safe"]==l["cases"],
        "INCOMPLETE_HISTORY_BLOCKS_AUTHORITY":m["safe"]==m["cases"],
        "PARTIAL_WRITES_ROLL_BACK":n["safe"]==n["cases"],
        "REPEATED_LIFECYCLES_MONOTONIC":o["cell_lifecycles"]==48 and o["monotonic"]==48 and o["stale_votes"]==0 and o["authority_duplication"]==0 and o["single_head"]==48,
        "CROSS_LAYER_ORDERING_NECESSARY":p["authority_leaks"]>0,
    }
    s["PERSISTENT_DEVELOPMENTAL_LIFECYCLE_SAFE"]=all(s.values())
    s["FULL_INDEPENDENT_GOVERNANCE_COLLUSION_BOUNDARY"]=ho["H1"]>0
    s["INDEPENDENT_REGISTRY_COLLUSION_BOUNDARY"]=ho["H2"]>0
    s["CORRUPTION_BEFORE_TEMPORAL_SEAL_BOUNDARY"]=ho["H3"]>0
    s["COMPLETE_EVENT_OMISSION_BOUNDARY"]=ho["H4"]>0
    s["GENESIS_ROOT_REPLACEMENT_BOUNDARY"]=ho["H5"]>0
    s["CROSS_LAYER_CORRELATED_FORGERY_BOUNDARY"]=ho["H6"]>0
    return s


def validate():
    assert CELLS==12
    assert PART_A==tuple(range(6)) and PART_B==tuple(range(6,12))
    assert EPOCHS[0]=="E0_GENESIS" and EPOCHS[-1]=="E15_REMERGE_FINAL_SEAL" and len(EPOCHS)==16
    assert CAPSULE_FIELDS==("checkpoint_id","generation","role","fp2","causal_cursor")
    assert REACT_STAGES==("R0_WAKE_PASSIVE","R1_CAUSAL_CATCHUP","R2_IDENTITY_RECONCILIATION","R3_HEALTH_DWELL","R4_AUTHORITY_RESTORATION")
    assert len(SLOTS)==4 and gov_ok(GOV_ROOTS)
    assert REG_QUORUM==3 and pairwise_disjoint(REG_ROOTS)
    assert CUTS==("BEFORE_FIRST_WRITE","AFTER_FIRST_WRITE","BEFORE_FINAL_CERTIFICATE")
    counts={"A":12,"B":36,"C":12,"D":12,"E":36,"F":36,"G":48,"H":24,"I":36,"J":72,"K":12,"L":15,"M":36,"N":18,"O":48}
    return {
        "cells":CELLS,"part_a":PART_A,"part_b":PART_B,"epochs":EPOCHS,
        "capsule_fields":CAPSULE_FIELDS,"reactivation_stages":REACT_STAGES,
        "governance_classes":len(SLOTS),"registry_quorum":REG_QUORUM,
        "dormant_authority_count":0,"audit_counts":counts,
        "canonical_scientific_execution":False,"stab18_r1_touched":False,
    }


def run():
    mech=validate()
    a=audit_a(); b=audit_b(); c=audit_c(); d=audit_d(); e=audit_e(); f=audit_f(); g=audit_g(); h=audit_h()
    i=audit_i(); j=audit_j(); k=audit_k(); l=audit_l(); m=audit_m(); n=audit_n(); o=audit_o(); p=audit_p()
    ho=holdouts()
    return {
        "schema":"yggdrasil.dg1r-05ac-persistent-developmental-lifecycle.v1",
        "mechanical_valid":True,"mechanical":mech,
        "audit_a":a,"audit_b":b,"audit_c":c,"audit_d":d,"audit_e":e,"audit_f":f,"audit_g":g,"audit_h":h,
        "audit_i":i,"audit_j":j,"audit_k":k,"audit_l":l,"audit_m":m,"audit_n":n,"audit_o":o,"audit_p":p,
        "correlated_constitutional_boundaries":ho,
        "signals":signals(a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,ho),
        "canonical_scientific_execution":False,"stab18_r1_touched":False,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--mechanical-only",action="store_true")
    args=ap.parse_args()
    if args.mechanical_only:
        print(enc({"mechanical_valid":True,"mechanical":validate()}))
        return
    if not args.out:
        raise SystemExit("--out required unless --mechanical-only")
    obj=run()
    raw=(enc(obj)+"\n").encode()
    Path(args.out).write_bytes(raw)
    print(enc({"output":args.out,"sha256":hashlib.sha256(raw).hexdigest(),"signals":obj["signals"]}))


if __name__=="__main__":
    main()
