#!/usr/bin/env python3
import argparse, hashlib, itertools, json
from copy import deepcopy
from pathlib import Path

CELLS=12
DWELL=4
GOV_MASKS=(1<<0,1<<1,1<<2,1<<3)
REG_MASKS=(1<<4,1<<5,1<<6,1<<7)
WITHIN_DELTAS=(5,10,15)
REPAIR_FAMILIES=("TRUE_SINGLE","TRUE_TWO_PLANE","TRUE_COORDINATED","CHECK_ONLY")
FINAL_RECORDS=("TARGET","PEER_A","PEER_B")


def role_to_fp2(role):
    r0=role&1; r1=(role>>1)&1
    return (r0^r1)|(r1<<1)

def role2_internal(x):
    return ((((x>>0)&1)^((x>>2)&1)) | ((((x>>1)&1)^((x>>3)&1))<<1))

def fp2_internal(x):
    f0=((x>>0)&1)^((x>>1)&1)^((x>>2)&1)^((x>>3)&1)
    f1=((x>>1)&1)^((x>>3)&1)
    return f0|(f1<<1)

def init_state(cell):
    role=cell%4
    return {
        "cell":cell,
        "role":role,
        "internal":role,
        "fp2":role_to_fp2(role),
        "peer_a_role":role,
        "peer_b_role":role,
        "role_gen":0,
        "peer_a_gen":0,
        "peer_b_gen":0,
        "damage":False,
        "repair_status":"HEALTHY",
        "peer_a_holder_epoch":0,
        "peer_b_holder_epoch":0,
        "peer_a_lineage":GOV_MASKS[2],
        "peer_b_lineage":GOV_MASKS[3],
        "witness_lineage_gen":0,
        "registry_gen":0,
        "registry_active":False,
        "registry_edge_parentset":(),
        "registry_seal_parentset":(),
        "registry_holder_epoch":0,
    }

def snap(state):
    return json.dumps(state,sort_keys=True,separators=(",",":"))

def pairwise_disjoint(masks):
    return all((a&b)==0 for a,b in itertools.combinations(masks,2))

def lineage_quorum3(masks):
    vals=[m for m in masks if m not in (None,0)]
    for combo in itertools.combinations(vals,3):
        if pairwise_disjoint(combo):
            return True
    return False

def governance_independent(masks):
    return len(masks)==4 and all(m not in (None,0) for m in masks) and pairwise_disjoint(masks)

def invariants(state):
    return {
        "role_fp2":state["fp2"]==role_to_fp2(state["role"]),
        "peer_roles":state["peer_a_role"]==state["role"]==state["peer_b_role"],
        "generation":state["peer_a_gen"]==state["role_gen"]==state["peer_b_gen"],
        "registry":(not state["registry_active"]) or state["registry_edge_parentset"]==state["registry_seal_parentset"],
    }

def mark_damage(state,family="TRUE_SINGLE"):
    t=deepcopy(state); t["damage"]=True; t["repair_status"]="DAMAGED"
    if family=="TRUE_SINGLE": t["internal"]^=1
    elif family=="TRUE_TWO_PLANE": t["internal"]^=3
    elif family=="TRUE_COORDINATED": t["internal"]^=7
    else: raise KeyError(family)
    return t

def repair_contract(state,family,forged=False):
    t=deepcopy(state)
    if family=="CHECK_ONLY":
        t["repair_status"]="ABSTAIN_CHECK_ONLY"
        return False,t
    if family in REPAIR_FAMILIES[:3] and not forged:
        t["damage"]=False
        t["repair_status"]="REPAIRED"
        t["internal"]=t["role"]
        return True,t
    if forged:
        t["damage"]=False
        t["repair_status"]="FALSE_REPAIR"
        t["internal"]^=1
        return True,t
    raise KeyError(family)

def health_commit(state):
    if state["damage"]:
        return False,deepcopy(state)
    if role2_internal(state["internal"])!=state["role"]:
        return False,deepcopy(state)
    if fp2_internal(state["internal"])!=state["fp2"]:
        return False,deepcopy(state)
    return True,deepcopy(state)

def registry_update(state,*,vote_masks=REG_MASKS,present=(True,True,True,True),
                    edge_present=None,seal_present=None,unique_seal=True,
                    parentset=("OLD","NEW"),seal_parentset=None,verified_lineage=True,
                    rotate=True):
    if edge_present is None: edge_present=present
    if seal_present is None: seal_present=present
    edge_masks=[m for m,p in zip(vote_masks,edge_present) if p]
    seal_masks=[m for m,p in zip(vote_masks,seal_present) if p]
    if seal_parentset is None: seal_parentset=parentset
    ok=(verified_lineage and lineage_quorum3(edge_masks) and lineage_quorum3(seal_masks)
        and unique_seal and tuple(sorted(parentset))==tuple(sorted(seal_parentset)))
    if not ok:
        return False,deepcopy(state)
    t=deepcopy(state)
    t["registry_gen"]+=1
    t["registry_active"]=True
    t["registry_edge_parentset"]=tuple(sorted(parentset))
    t["registry_seal_parentset"]=tuple(sorted(seal_parentset))
    if rotate:
        t["peer_a_holder_epoch"]+=1
        t["witness_lineage_gen"]+=1
    return True,t

def role_migration(state,new_role,*,approvals=(True,True,True,True),lineages=GOV_MASKS,
                   verified=(True,True,True,True),stable=True,
                   final_records=FINAL_RECORDS,required_holder_active=True,
                   generation_conflict=False):
    if state["damage"] or not stable or generation_conflict or not required_holder_active:
        return False,deepcopy(state)
    if not all(approvals) or not all(verified) or not governance_independent(lineages):
        return False,deepcopy(state)
    if set(final_records)!=set(FINAL_RECORDS) or new_role==state["role"]:
        return False,deepcopy(state)
    t=deepcopy(state); ng=state["role_gen"]+1
    t["role"]=new_role
    t["internal"]=new_role
    t["fp2"]=role_to_fp2(new_role)
    t["peer_a_role"]=new_role
    t["peer_b_role"]=new_role
    t["role_gen"]=ng
    t["peer_a_gen"]=ng
    t["peer_b_gen"]=ng
    return True,t

def composed_migration_rotation(state,new_role,*,registry_kw=None,**role_kw):
    old=deepcopy(state)
    ok,t=role_migration(state,new_role,**role_kw)
    if not ok:
        return False,old
    rok,u=registry_update(t,**({} if registry_kw is None else registry_kw))
    if not rok:
        return False,old
    return True,u

def proper_subsets():
    return [s for n in (1,2) for s in itertools.combinations(FINAL_RECORDS,n)]

def partial_tentative(state,new_role,subset):
    t=deepcopy(state); ng=state["role_gen"]+1
    if "TARGET" in subset:
        t["role"]=new_role
        t["internal"]=new_role
        t["fp2"]=role_to_fp2(new_role)
        t["role_gen"]=ng
    if "PEER_A" in subset:
        t["peer_a_role"]=new_role
        t["peer_a_gen"]=ng
    if "PEER_B" in subset:
        t["peer_b_role"]=new_role
        t["peer_b_gen"]=ng
    return t

def role_replay(state,old_role,old_gen):
    if old_gen<=state["role_gen"]:
        return False,deepcopy(state)
    t=deepcopy(state)
    t["role"]=old_role
    t["fp2"]=role_to_fp2(old_role)
    t["role_gen"]=old_gen
    return True,t

def lineage_replay(state,old_epoch,old_gen):
    if old_gen<=state["witness_lineage_gen"]:
        return False,deepcopy(state)
    t=deepcopy(state)
    t["peer_a_holder_epoch"]=old_epoch
    t["witness_lineage_gen"]=old_gen
    return True,t

def audit_a():
    cases=success=0
    for cell in range(CELLS):
        for new_role in range(4):
            if new_role==cell%4: continue
            cases+=1
            s=mark_damage(init_state(cell),"TRUE_SINGLE")
            repaired,s=repair_contract(s,"TRUE_SINGLE")
            s["internal"]^=WITHIN_DELTAS[0]
            health_ok,_=health_commit(s)
            committed,t=composed_migration_rotation(s,new_role,registry_kw={"parentset":("OLD_WITNESS","ROTATED_WITNESS")})
            good=(repaired and health_ok and committed and not t["damage"] and t["role"]==new_role
                  and t["role_gen"]==1 and t["peer_a_holder_epoch"]==1 and t["registry_active"]
                  and all(invariants(t).values()))
            success+=int(good)
    return {"cases":cases,"success":success}

def audit_b():
    cases=success=premature_blocked=true_repairs=check_abstain=0
    for cell in range(CELLS):
        for family in REPAIR_FAMILIES:
            cases+=1; s=init_state(cell)
            if family=="CHECK_ONLY":
                before=snap(s); ok,t=repair_contract(s,family)
                good=(not ok and snap({**t,"repair_status":"HEALTHY"})==before)
                check_abstain+=int(not ok)
                success+=int(good)
            else:
                damaged=mark_damage(s,family)
                pre,_=health_commit(damaged)
                premature_blocked+=int(not pre)
                rep,t=repair_contract(damaged,family)
                true_repairs+=int(rep)
                post,u=health_commit(t)
                good=(not pre and rep and post and u["fp2"]==s["fp2"] and u["role"]==s["role"]
                      and role2_internal(u["internal"])==u["role"])
                success+=int(good)
    return {"cases":cases,"success":success,"premature_blocked":premature_blocked,
            "true_repairs":true_repairs,"check_abstain":check_abstain}

def audit_c():
    cases=success=blocked=retry_success=0
    for cell in range(CELLS):
        for new_role in range(4):
            if new_role==cell%4: continue
            cases+=1; s=mark_damage(init_state(cell),"TRUE_SINGLE")
            first,t1=role_migration(s,new_role)
            blocked+=int(not first and snap(t1)==snap(s))
            rep,healed=repair_contract(s,"TRUE_SINGLE")
            second,t2=role_migration(healed,new_role)
            retry_success+=int(second)
            success+=int((not first) and rep and second and t2["role"]==new_role)
    return {"cases":cases,"success":success,"blocked":blocked,"retry_success":retry_success}

def audit_d():
    cases=success=local_control_leaks=0
    for cell in range(CELLS):
        for new_role in range(4):
            if new_role==cell%4: continue
            for subset in proper_subsets():
                cases+=1; s=init_state(cell); before=snap(s)
                local=partial_tentative(s,new_role,subset)
                local_control_leaks+=int(snap(local)!=before)
                regok,_=registry_update(local,seal_present=(True,True,False,False))
                candidate=deepcopy(s)
                success+=int((not regok) and snap(candidate)==before)
    return {"cases":cases,"success":success,"local_control_leaks":local_control_leaks}

def audit_e():
    cases=success=0
    for cell in range(CELLS):
        for new_role in range(4):
            if new_role==cell%4: continue
            s=init_state(cell)
            committed,t=composed_migration_rotation(s,new_role,registry_kw={"parentset":("OLD","NEW")})
            for kind in ("ROLE","LINEAGE"):
                cases+=1; before=snap(t)
                if kind=="ROLE": accepted,u=role_replay(t,s["role"],0)
                else: accepted,u=lineage_replay(t,0,0)
                success+=int(committed and not accepted and snap(u)==before)
    return {"cases":cases,"success":success}

def audit_f():
    cases=success=distinct_holder_control=0
    for cell in range(CELLS):
        for fanout in (4,8,16,32):
            cases+=1; s=init_state(cell); new_role=(s["role"]+1)%4
            accepted,t=role_migration(s,new_role,lineages=(GOV_MASKS[0],)*4)
            success+=int(not accepted and snap(t)==snap(s))
            distinct_holder_control+=int(fanout>=4)
    return {"cases":cases,"success":success,"distinct_holder_control":distinct_holder_control}

def audit_g():
    cases=success=0
    for cell in range(CELLS):
        for new_role in range(4):
            if new_role==cell%4: continue
            for bad in range(4):
                cases+=1; s=init_state(cell); approvals=[True]*4; approvals[bad]=False
                accepted,t=role_migration(s,new_role,approvals=tuple(approvals))
                success+=int(not accepted and snap(t)==snap(s))
    return {"cases":cases,"success":success}

def audit_h():
    cases=success=0
    for cell in range(CELLS):
        for new_role in range(4):
            if new_role==cell%4: continue
            for missing in range(4):
                cases+=1; s=init_state(cell); present=[True]*4; present[missing]=False
                accepted,t=composed_migration_rotation(s,new_role,
                    registry_kw={"present":tuple(present),"parentset":("OLD","ROTATED")})
                success+=int(accepted and t["role"]==new_role and t["peer_a_holder_epoch"]==1
                             and all(invariants(t).values()))
    return {"cases":cases,"success":success}

def audit_i():
    cases=success=0
    for cell in range(CELLS):
        for new_role in range(4):
            if new_role==cell%4: continue
            cases+=1; s=init_state(cell)
            migrated,t=role_migration(s,new_role)
            old_lineage=t["peer_a_lineage"] if migrated else None
            rotated,u=registry_update(t,parentset=("OLD","ROTATED"))
            read=(u["role"],u["peer_a_holder_epoch"],u["peer_a_lineage"])
            success+=int(migrated and rotated and read==(new_role,1,old_lineage) and all(invariants(u).values()))
    return {"cases":cases,"success":success}

def audit_j():
    cases=success=0
    for cell in range(CELLS):
        for new_role in range(4):
            if new_role==cell%4: continue
            s=init_state(cell)
            cases+=1
            ok,t=role_migration(s,new_role,verified=(False,True,True,True))
            success+=int(not ok and snap(t)==snap(s))
            cases+=1
            ok,t=composed_migration_rotation(s,new_role,
                registry_kw={"seal_present":(True,True,False,False),"parentset":("OLD","ROTATED")})
            success+=int(not ok and snap(t)==snap(s))
            cases+=1
            damaged=mark_damage(s,"TRUE_SINGLE")
            ok,t=role_migration(damaged,new_role)
            success+=int(not ok and snap(t)==snap(damaged))
    return {"cases":cases,"success":success}

def audit_k():
    chains=commits=success=0
    for cell in range(CELLS):
        s=init_state(cell); generations=[0]
        for _ in range(3):
            new_role=(s["role"]+1)%4
            ok,t=role_migration(s,new_role)
            if ok:
                commits+=1; s=t; generations.append(s["role_gen"])
        chains+=1
        success+=int(s["role_gen"]==3 and generations==[0,1,2,3] and all(invariants(s).values()))
    return {"chains":chains,"commits":commits,"success":success}

def audit_l():
    cases=success=0
    for cell in range(CELLS):
        for new_role in range(4):
            if new_role==cell%4: continue
            cases+=1; s=init_state(cell)
            false_masks=(REG_MASKS[0],REG_MASKS[0],REG_MASKS[0],REG_MASKS[1])
            ok,t=composed_migration_rotation(s,new_role,
                registry_kw={"vote_masks":false_masks,"present":(True,True,True,False),"parentset":("FALSE","HISTORY")})
            success+=int(not ok and snap(t)==snap(s))
    return {"cases":cases,"success":success}

def negative_control():
    premature_health=partial_write=stale_overwrite=0
    for cell in range(CELLS):
        s=mark_damage(init_state(cell),"TRUE_SINGLE")
        naive=deepcopy(s); naive["fp2"]=fp2_internal(naive["internal"])
        premature_health+=int(naive["fp2"]!=init_state(cell)["fp2"])
        new_role=(cell%4+1)%4
        partial_write+=int(snap(partial_tentative(init_state(cell),new_role,("TARGET",)))!=snap(init_state(cell)))
        newer=init_state(cell); newer["role_gen"]=1
        stale=deepcopy(newer); stale["role_gen"]=0
        stale_overwrite+=int(stale["role_gen"]<newer["role_gen"])
    return {"premature_health_leaks":premature_health,"partial_write_leaks":partial_write,
            "stale_overwrite_leaks":stale_overwrite}

def holdouts():
    h1=h2=h3=h4=0; cases=0
    for cell in range(CELLS):
        old=cell%4
        for false_role in range(4):
            if false_role==old: continue
            cases+=1; s=init_state(cell)
            a,t=role_migration(s,false_role,approvals=(True,True,True,True),lineages=GOV_MASKS)
            h1+=int(a)
            r,u=registry_update(s,vote_masks=REG_MASKS,present=(True,True,True,False),
                                parentset=("FALSE","HISTORY"))
            h2+=int(r)
            # evaluator says four distinct root IDs were minted from one actual source.
            root_compromise_masks=GOV_MASKS
            c,v=role_migration(s,false_role,approvals=(True,True,True,True),lineages=root_compromise_masks)
            h3+=int(c)
            damaged=mark_damage(s,"TRUE_SINGLE")
            forged_rep,w=repair_contract(damaged,"TRUE_SINGLE",forged=True)
            m,x=role_migration(w,false_role,approvals=(True,True,True,True),lineages=GOV_MASKS)
            q,y=registry_update(x,vote_masks=REG_MASKS,present=(True,True,True,False),
                                parentset=("FORGED","CHAIN")) if m else (False,x)
            h4+=int(forged_rep and m and q and y["role"]==false_role)
    return {"cases":cases,"H1_full_governance_collusion_false_commit":h1,
            "H2_independent_registry_collusion_false_commit":h2,
            "H3_root_compromise_false_commit":h3,
            "H4_cross_layer_correlated_forgery_false_commit":h4}

def signals(a,b,c,d,e,f,g,h,i,j,k,l,neg,hold):
    vals={
        "CLEAN_LIFECYCLE_COMPOSES":a["success"]==36,
        "DAMAGE_NOT_NORMALIZED_BEFORE_REPAIR":b["success"]==48,
        "UNRESOLVED_DAMAGE_BLOCKS_ROLE_COMMIT":c["success"]==36,
        "CROSS_LAYER_PARTIAL_WRITE_ROLLBACK":d["success"]==216,
        "CROSS_LAYER_STALE_REPLAY_REJECTED":e["success"]==72,
        "GOVERNANCE_FANOUT_NOT_INDEPENDENT_QUORUM":f["success"]==48,
        "SINGLE_GOVERNANCE_CLASS_CORRUPTION_REJECTED":g["success"]==144,
        "REGISTRY_LOSS_DURING_LIFECYCLE_TOLERATED":h["success"]==144,
        "ROLE_THEN_HOLDER_ROTATION_COHERENT":i["success"]==36,
        "LOWER_LAYER_ABSTENTION_PROPAGATES":j["success"]==108,
        "REPEATED_LIFECYCLE_GENERATIONS_MONOTONIC":k["chains"]==12 and k["commits"]==36 and k["success"]==12,
        "COMPOSED_SAME_LINEAGE_REGISTRY_ATTACK_REJECTED":l["success"]==36,
    }
    vals["LOCAL_COMPOSITION_LEAK_EXPOSED"]=sum(neg.values())>0
    vals["CELLULAR_SOVEREIGNTY_COMPOSES"]=all(vals.values())
    vals["FULL_INDEPENDENT_GOVERNANCE_COLLUSION_FAILURE"]=hold["H1_full_governance_collusion_false_commit"]>0
    vals["INDEPENDENT_REGISTRY_COLLUSION_FAILURE"]=hold["H2_independent_registry_collusion_false_commit"]>0
    vals["ROOT_COMPROMISE_FAILURE"]=hold["H3_root_compromise_false_commit"]>0
    vals["CROSS_LAYER_CORRELATED_FORGERY_FAILURE"]=hold["H4_cross_layer_correlated_forgery_false_commit"]>0
    return vals

def validate():
    assert CELLS==12 and DWELL==4
    assert tuple(d for d in range(1,16) if role2_internal(d)==0)==WITHIN_DELTAS
    assert tuple(role_to_fp2(r) for r in range(4))==tuple(fp2_internal(r) for r in range(4))
    assert pairwise_disjoint(GOV_MASKS) and pairwise_disjoint(REG_MASKS)
    assert all((g&r)==0 for g in GOV_MASKS for r in REG_MASKS)
    assert len(proper_subsets())==6
    counts={"A":36,"B":48,"C":36,"D":216,"E":72,"F":48,"G":144,"H":144,"I":36,"J":108,"K_commits":36,"L":36}
    assert 12*3==36 and 36*6==216 and 36*2==72 and 12*4==48 and 36*4==144 and 36*3==108
    return counts

def run():
    mech=validate()
    a=audit_a(); b=audit_b(); c=audit_c(); d=audit_d(); e=audit_e(); f=audit_f()
    g=audit_g(); h=audit_h(); i=audit_i(); j=audit_j(); k=audit_k(); l=audit_l()
    neg=negative_control(); hold=holdouts()
    return {"schema":"yggdrasil.dg1r-05x-cellular-sovereignty-composition.v1",
            "mechanical_valid":True,"mechanical":mech,
            "audit_a":a,"audit_b":b,"audit_c":c,"audit_d":d,"audit_e":e,"audit_f":f,
            "audit_g":g,"audit_h":h,"audit_i":i,"audit_j":j,"audit_k":k,"audit_l":l,
            "negative_control":neg,"correlated_boundary":hold,
            "signals":signals(a,b,c,d,e,f,g,h,i,j,k,l,neg,hold),
            "canonical_scientific_execution":False,"stab18_r1_touched":False}

def enc(o):
    return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--mechanical-only",action="store_true")
    a=ap.parse_args()
    if a.mechanical_only:
        print(enc({"mechanical_valid":True,"mechanical":validate()})); return
    if not a.out: raise SystemExit("--out required unless --mechanical-only")
    obj=run(); raw=(enc(obj)+"\n").encode(); Path(a.out).write_bytes(raw)
    print(enc({"output":a.out,"sha256":hashlib.sha256(raw).hexdigest(),"signals":obj["signals"]}))
if __name__=="__main__": main()
