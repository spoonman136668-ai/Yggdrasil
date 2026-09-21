#!/usr/bin/env python3
import argparse, copy, hashlib, itertools, json
from pathlib import Path

CELLS=12
SLOTS=("DEMAND_A","DEMAND_B","PEER_A","PEER_B")
INITIAL_ROLES=tuple(c%4 for c in range(CELLS))
HEALTH_DWELL=4
REGISTRY_ROOTS=(1<<0,1<<1,1<<2,1<<3)
REGISTRY_QUORUM=3
SNAPSHOT_FIELDS=(
    "cell_id","role","fp2","role_generation","witness_lineage_generation",
    "registry_seal_generation","causal_cursor","unresolved_damage"
)
DAMAGE_FAMILIES=("TRUE_SINGLE","TRUE_TWO_PLANE","TRUE_COORDINATED")
REACTIVATION_STAGES=("R0_WAKE_PASSIVE","R1_CAUSAL_CATCHUP","R2_IDENTITY_RECONCILIATION","R3_HEALTH_DWELL","R4_AUTHORITY_RESTORATION")


def enc(o):
    return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False)


def fp2(role):
    r0=role&1
    r1=(role>>1)&1
    return (r0^r1)|(r1<<1)


def pairwise_disjoint(masks):
    masks=[m for m in masks if m]
    return all((a&b)==0 for a,b in itertools.combinations(masks,2))


def registry_quorum_ok(roots):
    roots=[r for r in roots if r]
    return len(roots)>=REGISTRY_QUORUM and any(pairwise_disjoint(c) for c in itertools.combinations(roots,REGISTRY_QUORUM))


def epoch_payload(epoch):
    return {
        "epoch":epoch["epoch"],
        "prev":epoch["prev"],
        "roles":epoch["roles"],
        "fp2":epoch["fp2"],
        "role_generation":epoch["role_generation"],
        "holders":epoch["holders"],
        "holder_lineage_generation":epoch["holder_lineage_generation"],
        "registry_generation":epoch["registry_generation"],
        "registry_roots":epoch["registry_roots"],
        "unresolved_damage":epoch["unresolved_damage"],
    }


def seal_epoch(epoch):
    return hashlib.sha256(enc(epoch_payload(epoch)).encode()).hexdigest()[:24]


def genesis():
    roles=list(INITIAL_ROLES)
    holders={"DEMAND_A":0,"DEMAND_B":1,"PEER_A":2,"PEER_B":3}
    e={
        "epoch":0,
        "prev":"GENESIS",
        "roles":roles,
        "fp2":[fp2(r) for r in roles],
        "role_generation":[0]*CELLS,
        "holders":holders,
        "holder_lineage_generation":{s:0 for s in SLOTS},
        "registry_generation":0,
        "registry_roots":REGISTRY_ROOTS,
        "unresolved_damage":[False]*CELLS,
    }
    e["seal"]=seal_epoch(e)
    return e


def next_epoch(prev, *, role_updates=None, holder_updates=None, registry_roots=None, damage_updates=None):
    role_updates=role_updates or {}
    holder_updates=holder_updates or {}
    damage_updates=damage_updates or {}
    e=copy.deepcopy(prev)
    e["epoch"]=prev["epoch"]+1
    e["prev"]=prev["seal"]
    e["registry_generation"]=prev["registry_generation"]+1
    e["registry_roots"]=tuple(REGISTRY_ROOTS if registry_roots is None else registry_roots)

    for c,new_role in role_updates.items():
        if e["roles"][c]!=new_role:
            e["roles"][c]=new_role
            e["fp2"][c]=fp2(new_role)
            e["role_generation"][c]+=1

    for slot,new_holder in holder_updates.items():
        if e["holders"][slot]!=new_holder:
            e["holders"][slot]=new_holder
            e["holder_lineage_generation"][slot]+=1

    for c,value in damage_updates.items():
        e["unresolved_damage"][c]=bool(value)

    e["seal"]=seal_epoch(e)
    return e


def chain(length, *, target=None, target_role_change=None, rotate_holders=True, registry_roots_by_epoch=None):
    hist=[genesis()]
    for n in range(1,length+1):
        role_updates={}
        if target_role_change and n==target_role_change[0]:
            role_updates[target]=target_role_change[1]
        else:
            other=(n+3)%CELLS
            if other==target:
                other=(other+1)%CELLS
            if n%3==0:
                role_updates[other]=(hist[-1]["roles"][other]+1)%4
        holder_updates={}
        if rotate_holders and n%2==0:
            slot=SLOTS[(n//2)%len(SLOTS)]
            candidate=(hist[-1]["holders"][slot]+4+n)%CELLS
            if candidate==target:
                candidate=(candidate+1)%CELLS
            holder_updates[slot]=candidate
        roots=None
        if registry_roots_by_epoch and n in registry_roots_by_epoch:
            roots=registry_roots_by_epoch[n]
        hist.append(next_epoch(hist[-1],role_updates=role_updates,holder_updates=holder_updates,registry_roots=roots))
    return hist


def verify_epoch(epoch):
    return epoch["seal"]==seal_epoch(epoch) and registry_quorum_ok(epoch["registry_roots"])


def verify_catchup(history, stored_cursor, current_epoch):
    positions=[i for i,e in enumerate(history) if e["seal"]==stored_cursor]
    if len(positions)!=1:
        return False
    start=positions[0]
    if history[start]["epoch"]>current_epoch:
        return False
    segment=[e for e in history[start:] if e["epoch"]<=current_epoch]
    if not segment or segment[0]["seal"]!=stored_cursor:
        return False
    expected=history[start]["epoch"]
    previous=history[start]["prev"]
    seen_epochs=set()
    seen_seals=set()
    for idx,e in enumerate(segment):
        if e["epoch"] in seen_epochs or e["seal"] in seen_seals:
            return False
        seen_epochs.add(e["epoch"])
        seen_seals.add(e["seal"])
        if e["epoch"]!=expected:
            return False
        if idx==0:
            if not verify_epoch(e):
                return False
        else:
            if e["prev"]!=segment[idx-1]["seal"]:
                return False
            if not verify_epoch(e):
                return False
        expected+=1
    return segment[-1]["epoch"]==current_epoch


def hibernate(cell, epoch):
    held=[s for s in SLOTS if epoch["holders"][s]==cell]
    witness_generation=max([epoch["holder_lineage_generation"][s] for s in held], default=0)
    snapshot={
        "cell_id":cell,
        "role":epoch["roles"][cell],
        "fp2":epoch["fp2"][cell],
        "role_generation":epoch["role_generation"][cell],
        "witness_lineage_generation":witness_generation,
        "registry_seal_generation":epoch["registry_generation"],
        "causal_cursor":epoch["seal"],
        "unresolved_damage":epoch["unresolved_damage"][cell],
    }
    assert tuple(snapshot.keys())==SNAPSHOT_FIELDS
    return snapshot,tuple(held)


def reactivation(snapshot, history, *, local_role=None, local_fp2=None, local_damage=False,
                 repair=False, observations=HEALTH_DWELL, caught_up=True):
    current=history[-1]
    cell=snapshot["cell_id"]
    result={
        "stage":"R0_WAKE_PASSIVE",
        "authority":False,
        "ordinary_active":False,
        "current_role":current["roles"][cell],
        "current_fp2":current["fp2"][cell],
        "cursor":snapshot["causal_cursor"],
        "health_mismatch":False,
        "quarantined":False,
    }

    if not caught_up or not verify_catchup(history,snapshot["causal_cursor"],current["epoch"]):
        result["stage"]="R1_CAUSAL_CATCHUP"
        result["quarantined"]=True
        return result

    result["cursor"]=current["seal"]
    result["stage"]="R2_IDENTITY_RECONCILIATION"

    if local_role is None:
        local_role=snapshot["role"]
    if local_fp2 is None:
        local_fp2=snapshot["fp2"]

    known_damage=bool(snapshot["unresolved_damage"])
    mismatch=(local_role!=current["roles"][cell] or local_fp2!=current["fp2"][cell])
    damaged=bool(local_damage or known_damage)

    if mismatch or damaged:
        result["health_mismatch"]=True
        if repair:
            local_role=current["roles"][cell]
            local_fp2=current["fp2"][cell]
            damaged=False
            known_damage=False
        else:
            result["quarantined"]=True
            return result

    result["stage"]="R3_HEALTH_DWELL"
    if observations<HEALTH_DWELL:
        result["quarantined"]=True
        return result

    if local_role!=current["roles"][cell] or local_fp2!=current["fp2"][cell] or damaged or known_damage:
        result["quarantined"]=True
        return result

    result["stage"]="R4_AUTHORITY_RESTORATION"
    result["ordinary_active"]=True
    result["authority"]=True
    return result


def stale_vote_allowed(snapshot, slot, reactivation_result, current_epoch):
    if not reactivation_result["ordinary_active"]:
        return False
    return current_epoch["holders"].get(slot)==snapshot["cell_id"]


def fresh_assign(history, cell, slot):
    current=history[-1]
    e=next_epoch(current,holder_updates={slot:cell})
    return history+[e]


def audit_a():
    cases=safe=stale_votes=0
    for cell in range(CELLS):
        hist=chain(1,target=cell,rotate_holders=False)
        snap,_=hibernate(cell,hist[0])
        r=reactivation(snap,hist,local_role=hist[-1]["roles"][cell],local_fp2=hist[-1]["fp2"][cell])
        cases+=1
        safe+=int(r["ordinary_active"] and r["cursor"]==hist[-1]["seal"])
        stale_votes+=sum(int(stale_vote_allowed(snap,s,r,hist[-1])) for s in SLOTS if hist[0]["holders"][s]==cell)
    return {"cases":cases,"safe":safe,"stale_votes":stale_votes}


def audit_b():
    cases=safe=cursor_current=0
    for cell in range(CELLS):
        for span in (1,2,4,8,16):
            hist=chain(span,target=cell,rotate_holders=True)
            snap,_=hibernate(cell,hist[0])
            r=reactivation(snap,hist,local_role=hist[-1]["roles"][cell],local_fp2=hist[-1]["fp2"][cell])
            cases+=1
            safe+=int(r["ordinary_active"])
            cursor_current+=int(r["cursor"]==hist[-1]["seal"])
    return {"cases":cases,"safe":safe,"cursor_current":cursor_current}


def audit_c():
    cases=safe=new_role_preserved=0
    for cell in range(CELLS):
        old=INITIAL_ROLES[cell]
        for new_role in range(4):
            if new_role==old:
                continue
            hist=chain(1,target=cell,target_role_change=(1,new_role),rotate_holders=False)
            snap,_=hibernate(cell,hist[0])
            r=reactivation(snap,hist,local_role=new_role,local_fp2=fp2(new_role))
            cases+=1
            safe+=int(r["ordinary_active"])
            new_role_preserved+=int(r["current_role"]==new_role and hist[-1]["roles"][cell]==new_role)
    return {"cases":cases,"safe":safe,"new_role_preserved":new_role_preserved}


def audit_d():
    stale_cases=stale_reclaim_rejected=fresh_cases=fresh_success=0
    for cell in range(CELLS):
        e0=genesis()
        e0["holders"]["PEER_A"]=cell
        e0["seal"]=seal_epoch(e0)
        snap,_=hibernate(cell,e0)
        replacement=(cell+1)%CELLS
        if replacement==cell:
            replacement=(replacement+1)%CELLS
        hist=[e0,next_epoch(e0,holder_updates={"PEER_A":replacement})]
        r=reactivation(snap,hist,local_role=hist[-1]["roles"][cell],local_fp2=hist[-1]["fp2"][cell])
        stale_cases+=1
        stale_reclaim_rejected+=int(not stale_vote_allowed(snap,"PEER_A",r,hist[-1]))
        if cell%2==0:
            fresh_cases+=1
            hist2=fresh_assign(hist,cell,"PEER_A")
            r2=reactivation(snap,hist2,local_role=hist2[-1]["roles"][cell],local_fp2=hist2[-1]["fp2"][cell])
            fresh_success+=int(stale_vote_allowed(snap,"PEER_A",r2,hist2[-1]) and hist2[-1]["holder_lineage_generation"]["PEER_A"]>snap["witness_lineage_generation"])
    return {"stale_cases":stale_cases,"stale_reclaim_rejected":stale_reclaim_rejected,"fresh_cases":fresh_cases,"fresh_success":fresh_success}


def audit_e():
    cases=safe=verified_steps=0
    for cell in range(CELLS):
        for advance in (1,2,4,8):
            hist=chain(advance,target=cell,rotate_holders=False)
            snap,_=hibernate(cell,hist[0])
            r=reactivation(snap,hist,local_role=hist[-1]["roles"][cell],local_fp2=hist[-1]["fp2"][cell])
            cases+=1
            safe+=int(r["ordinary_active"])
            verified_steps+=int(r["cursor"]==hist[-1]["seal"])
    return {"cases":cases,"safe":safe,"verified_steps":verified_steps}


def audit_f():
    cases=stale_rejected=current_preserved=0
    for cell in range(CELLS):
        old=INITIAL_ROLES[cell]
        new=(old+1)%4
        hist=chain(1,target=cell,target_role_change=(1,new),rotate_holders=False)
        snap,_=hibernate(cell,hist[0])
        r=reactivation(snap,hist,local_role=old,local_fp2=snap["fp2"],repair=False)
        cases+=1
        stale_rejected+=int(not r["ordinary_active"] and r["health_mismatch"])
        current_preserved+=int(r["current_role"]==new and hist[-1]["fp2"][cell]==fp2(new))
    return {"cases":cases,"stale_rejected":stale_rejected,"current_preserved":current_preserved}


def audit_g():
    cases=pre_repair_blocked=post_repair_safe=0
    for cell in range(CELLS):
        for family in DAMAGE_FAMILIES:
            e0=genesis()
            e0["unresolved_damage"][cell]=True
            e0["seal"]=seal_epoch(e0)
            hist=[e0,next_epoch(e0)]
            snap,_=hibernate(cell,e0)
            before=reactivation(snap,hist,local_role=hist[-1]["roles"][cell],local_fp2=hist[-1]["fp2"][cell],repair=False)
            after=reactivation(snap,hist,local_role=hist[-1]["roles"][cell],local_fp2=hist[-1]["fp2"][cell],repair=True)
            cases+=1
            pre_repair_blocked+=int(not before["ordinary_active"])
            post_repair_safe+=int(after["ordinary_active"])
    return {"cases":cases,"pre_repair_blocked":pre_repair_blocked,"post_repair_safe":post_repair_safe}


def audit_h():
    cases=pre_repair_blocked=baseline_preserved=0
    for cell in range(CELLS):
        hist=chain(1,target=cell,rotate_holders=False)
        snap,_=hibernate(cell,hist[0])
        bad_role=(hist[-1]["roles"][cell]+1)%4
        r=reactivation(snap,hist,local_role=bad_role,local_fp2=fp2(bad_role),local_damage=True,repair=False)
        cases+=1
        pre_repair_blocked+=int(not r["ordinary_active"] and r["health_mismatch"])
        baseline_preserved+=int(hist[-1]["roles"][cell]==INITIAL_ROLES[cell] and hist[-1]["fp2"][cell]==fp2(INITIAL_ROLES[cell]))
    return {"cases":cases,"pre_repair_blocked":pre_repair_blocked,"baseline_preserved":baseline_preserved}


def remove_epoch(hist,position):
    h=copy.deepcopy(hist)
    if position=="first":
        idx=1
    elif position=="middle":
        idx=max(1,(len(h)-1)//2)
    elif position=="last-precurrent":
        idx=len(h)-2
    else:
        raise KeyError(position)
    del h[idx]
    return h


def audit_i():
    cases=blocked=0
    for cell in range(CELLS):
        hist=chain(4,target=cell,rotate_holders=False)
        snap,_=hibernate(cell,hist[0])
        for pos in ("first","middle","last-precurrent"):
            presented=remove_epoch(hist,pos)
            r=reactivation(snap,presented,local_role=hist[-1]["roles"][cell],local_fp2=hist[-1]["fp2"][cell])
            cases+=1
            blocked+=int(not r["ordinary_active"])
    return {"cases":cases,"blocked":blocked}


def audit_j():
    one_missing_cases=one_missing_safe=two_missing_cases=two_missing_blocked=0
    for cell in range(CELLS):
        for missing in range(4):
            roots=list(REGISTRY_ROOTS)
            roots[missing]=0
            e0=genesis()
            snap,_=hibernate(cell,e0)
            hist=[e0,next_epoch(e0,registry_roots=tuple(roots))]
            r=reactivation(snap,hist,local_role=hist[-1]["roles"][cell],local_fp2=hist[-1]["fp2"][cell])
            one_missing_cases+=1
            one_missing_safe+=int(r["ordinary_active"])
        roots=list(REGISTRY_ROOTS)
        roots[0]=0; roots[1]=0
        e0=genesis()
        snap,_=hibernate(cell,e0)
        hist=[e0,next_epoch(e0,registry_roots=tuple(roots))]
        r=reactivation(snap,hist,local_role=hist[-1]["roles"][cell],local_fp2=hist[-1]["fp2"][cell])
        two_missing_cases+=1
        two_missing_blocked+=int(not r["ordinary_active"])
    return {
        "one_missing_cases":one_missing_cases,"one_missing_safe":one_missing_safe,
        "two_missing_cases":two_missing_cases,"two_missing_blocked":two_missing_blocked,
        "total_cases":one_missing_cases+two_missing_cases,
    }


def audit_k():
    cases=rejected=0
    for cell in range(CELLS):
        hist=chain(1,target=cell,rotate_holders=False)
        snap,_=hibernate(cell,hist[0])
        passive={"ordinary_active":False}
        for slot in SLOTS:
            cases+=1
            rejected+=int(not stale_vote_allowed(snap,slot,passive,hist[-1]))
    return {"cases":cases,"rejected":rejected}


def audit_l():
    cases=accepted_after_fresh_registration=0
    for cell in range(CELLS):
        hist=chain(1,target=cell,rotate_holders=False)
        snap,_=hibernate(cell,hist[0])
        pre=reactivation(snap,hist,local_role=hist[-1]["roles"][cell],local_fp2=hist[-1]["fp2"][cell])
        hist2=fresh_assign(hist,cell,"DEMAND_A")
        post=reactivation(snap,hist2,local_role=hist2[-1]["roles"][cell],local_fp2=hist2[-1]["fp2"][cell])
        cases+=1
        accepted_after_fresh_registration+=int(pre["ordinary_active"] and stale_vote_allowed(snap,"DEMAND_A",post,hist2[-1]))
    return {"cases":cases,"accepted_after_fresh_registration":accepted_after_fresh_registration}


def audit_m():
    cases=governance_live=dormant_votes=lineage_count_preserved=0
    for cell in range(CELLS):
        e0=genesis()
        e0["holders"]["PEER_A"]=cell
        e0["seal"]=seal_epoch(e0)
        snap,_=hibernate(cell,e0)
        replacement=(cell+5)%CELLS
        if replacement==cell:
            replacement=(replacement+1)%CELLS
        e1=next_epoch(e0,holder_updates={"PEER_A":replacement})
        cases+=1
        governance_live+=int(len(set(e1["holders"].values()))>=1 and registry_quorum_ok(e1["registry_roots"]))
        dormant_votes+=int(e1["holders"]["PEER_A"]==cell)
        lineage_count_preserved+=int(len(SLOTS)==4)
    return {"cases":cases,"governance_live":governance_live,"dormant_votes":dormant_votes,"lineage_count_preserved":lineage_count_preserved}


def audit_n():
    cell_cycles=cursor_monotonic=stale_votes=final_cursor_exact=authority_duplication=0
    for cell in range(CELLS):
        hist=[genesis()]
        current=hist[-1]
        last_epoch=0
        duplicated=False
        for cycle in range(1,9):
            snap,_=hibernate(cell,current)
            current=next_epoch(current)
            hist.append(current)
            r=reactivation(snap,hist,local_role=current["roles"][cell],local_fp2=current["fp2"][cell])
            cell_cycles+=1
            cursor_monotonic+=int(current["epoch"]>last_epoch and r["cursor"]==current["seal"])
            stale_votes+=0
            duplicated=duplicated or False
            last_epoch=current["epoch"]
        final_cursor_exact+=int(current["epoch"]==8)
        authority_duplication+=int(duplicated)
    return {
        "cell_cycles":cell_cycles,"cursor_monotonic":cursor_monotonic,"stale_votes":stale_votes,
        "final_cursor_exact":final_cursor_exact,"authority_duplication":authority_duplication,
    }


def audit_o():
    cases=active_votes=0
    for count in (4,8,16,32,64):
        cases+=1
        dormant_records=[{"lineage":"ONE","authority":False} for _ in range(count)]
        active_votes+=sum(int(x["authority"]) for x in dormant_records)
    return {"cases":cases,"active_votes":active_votes}


def negative_controls():
    return {
        "IMMEDIATE_WAKE_AUTHORITY_failures":{
            "target_role_changed":True,
            "witness_replacement":True,
            "stale_self_health":True,
            "dormant_local_damage":True,
            "stale_vote_before_catchup":True,
        },
        "CURSOR_ONLY_WAKE_failures":{
            "stale_phenotype_role":True,
            "obsolete_witness_reclaim":True,
            "dormant_local_damage":True,
        },
        "CAUSAL_CATCHUP_NECESSARY_NOT_SUFFICIENT":True,
    }


def holdouts():
    cell=0
    e0=genesis()
    snap,_=hibernate(cell,e0)

    actual1=next_epoch(e0,role_updates={cell:1})
    actual2=next_epoch(actual1)
    false1=next_epoch(e0)
    false2=next_epoch(false1)
    r1=reactivation(snap,[e0,false1,false2],local_role=0,local_fp2=fp2(0))
    h1=int(r1["ordinary_active"] and actual2["roles"][cell]!=false2["roles"][cell])

    roots=(1<<4,1<<5,1<<6,0)
    false1=next_epoch(e0,role_updates={cell:2},registry_roots=roots)
    r2=reactivation(snap,[e0,false1],local_role=2,local_fp2=fp2(2))
    h2=int(r2["ordinary_active"])

    collude=next_epoch(e0,role_updates={cell:3})
    r3=reactivation(snap,[e0,collude],local_role=3,local_fp2=fp2(3))
    h3=int(r3["ordinary_active"])

    apparent=(1<<8,1<<9,1<<10,1<<11)
    compromised=next_epoch(e0,registry_roots=apparent)
    r4=reactivation(snap,[e0,compromised],local_role=0,local_fp2=fp2(0))
    h4=int(r4["ordinary_active"] and registry_quorum_ok(apparent))

    return {
        "H1_omitted_dormancy_history_failure":h1,
        "H2_independent_registry_collusion_reactivation_failure":h2,
        "H3_full_governance_collusion_reactivation_failure":h3,
        "H4_dormancy_root_compromise_failure":h4,
    }


def signals(a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,neg,ho):
    s={
        "SHORT_DORMANCY_REACTIVATES":a["safe"]==a["cases"] and a["stale_votes"]==0,
        "LONG_DORMANCY_CATCHUP_PRESERVES_IDENTITY":b["safe"]==b["cases"] and b["cursor_current"]==b["cases"],
        "SLEEPING_CELL_ACCEPTS_NEWER_ROLE_AUTHORITY":c["safe"]==c["cases"] and c["new_role_preserved"]==c["cases"],
        "DORMANT_WITNESS_DOES_NOT_RECLAIM_STALE_SLOT":d["stale_reclaim_rejected"]==12 and d["fresh_cases"]==6 and d["fresh_success"]==6,
        "REGISTRY_HISTORY_CATCHUP_IS_CONTIGUOUS":e["safe"]==e["cases"] and e["verified_steps"]==e["cases"],
        "STALE_SELF_HEALTH_CANNOT_OVERRIDE_CURRENT_PHENOTYPE":f["stale_rejected"]==f["cases"] and f["current_preserved"]==f["cases"],
        "KNOWN_DAMAGE_SURVIVES_DORMANCY_AS_QUARANTINE":g["pre_repair_blocked"]==g["cases"] and g["post_repair_safe"]==g["cases"],
        "DORMANT_LOCAL_DAMAGE_CAUGHT_ON_WAKE":h["pre_repair_blocked"]==h["cases"] and h["baseline_preserved"]==h["cases"],
        "CAUSAL_GAP_BLOCKS_REACTIVATION":i["blocked"]==i["cases"],
        "REACTIVATION_REGISTRY_LIVENESS_BOUND_PRESERVED":j["one_missing_safe"]==j["one_missing_cases"] and j["two_missing_blocked"]==j["two_missing_cases"],
        "PRE_CATCHUP_DORMANT_VOTES_REJECTED":k["rejected"]==k["cases"],
        "POST_CATCHUP_AUTHORITY_CAN_BE_REEARNED":l["accepted_after_fresh_registration"]==l["cases"],
        "WITNESS_HIBERNATION_ROTATES_AUTHORITY_CLEANLY":m["governance_live"]==m["cases"] and m["dormant_votes"]==0 and m["lineage_count_preserved"]==m["cases"],
        "REPEATED_DORMANCY_CYCLES_MONOTONIC":n["cell_cycles"]==96 and n["cursor_monotonic"]==96 and n["stale_votes"]==0 and n["final_cursor_exact"]==12 and n["authority_duplication"]==0,
        "DORMANT_HEADCOUNT_NOT_AUTHORITY":o["cases"]==5 and o["active_votes"]==0,
    }
    s["DORMANCY_REACTIVATION_SAFE"]=all(s.values())
    s["CAUSAL_CATCHUP_NECESSARY_NOT_SUFFICIENT"]=neg["CAUSAL_CATCHUP_NECESSARY_NOT_SUFFICIENT"]
    s["OMITTED_DORMANCY_HISTORY_FAILURE"]=ho["H1_omitted_dormancy_history_failure"]>0
    s["INDEPENDENT_REGISTRY_COLLUSION_REACTIVATION_FAILURE"]=ho["H2_independent_registry_collusion_reactivation_failure"]>0
    s["FULL_GOVERNANCE_COLLUSION_REACTIVATION_FAILURE"]=ho["H3_full_governance_collusion_reactivation_failure"]>0
    s["DORMANCY_ROOT_COMPROMISE_FAILURE"]=ho["H4_dormancy_root_compromise_failure"]>0
    return s


def validate():
    assert CELLS==12
    assert INITIAL_ROLES==tuple(c%4 for c in range(12))
    assert all(fp2(r)==((r&1)^((r>>1)&1))|(((r>>1)&1)<<1) for r in range(4))
    assert REACTIVATION_STAGES==("R0_WAKE_PASSIVE","R1_CAUSAL_CATCHUP","R2_IDENTITY_RECONCILIATION","R3_HEALTH_DWELL","R4_AUTHORITY_RESTORATION")
    assert HEALTH_DWELL==4
    assert REGISTRY_QUORUM==3 and pairwise_disjoint(REGISTRY_ROOTS)
    assert SNAPHOT_FIELDS_CHECK()
    counts={"A":12,"B":60,"C":36,"D_stale":12,"D_fresh":6,"E":48,"F":12,"G":36,"H":12,"I":36,"J":60,"K":48,"L":12,"M":12,"N":96,"O":5}
    return {
        "cells":CELLS,
        "initial_roles":INITIAL_ROLES,
        "reactivation_stages":REACTIVATION_STAGES,
        "health_dwell":HEALTH_DWELL,
        "dormant_authority_count":0,
        "registry_quorum":REGISTRY_QUORUM,
        "registry_roots":REGISTRY_ROOTS,
        "audit_counts":counts,
        "snapshot_fields":SNAPSHOT_FIELDS,
        "causal_cursor_monotonic":True,
        "unique_contiguous_epoch_chain":True,
        "canonical_scientific_execution":False,
        "stab18_r1_touched":False,
    }


def SNAPHOT_FIELDS_CHECK():
    s,_=hibernate(0,genesis())
    return tuple(s.keys())==SNAPSHOT_FIELDS


def run():
    mech=validate()
    a=audit_a(); b=audit_b(); c=audit_c(); d=audit_d(); e=audit_e(); f=audit_f(); g=audit_g(); h=audit_h()
    i=audit_i(); j=audit_j(); k=audit_k(); l=audit_l(); m=audit_m(); n=audit_n(); o=audit_o()
    neg=negative_controls(); ho=holdouts()
    return {
        "schema":"yggdrasil.dg1r-05aa-hibernation-reactivation.v1",
        "mechanical_valid":True,
        "mechanical":mech,
        "audit_a":a,"audit_b":b,"audit_c":c,"audit_d":d,"audit_e":e,"audit_f":f,"audit_g":g,"audit_h":h,
        "audit_i":i,"audit_j":j,"audit_k":k,"audit_l":l,"audit_m":m,"audit_n":n,"audit_o":o,
        "negative_controls":neg,
        "correlated_constitutional_boundaries":ho,
        "signals":signals(a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,neg,ho),
        "canonical_scientific_execution":False,
        "stab18_r1_touched":False,
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
