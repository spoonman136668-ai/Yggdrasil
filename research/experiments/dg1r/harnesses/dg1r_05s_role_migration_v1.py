#!/usr/bin/env python3
import argparse, hashlib, itertools, json
from collections import Counter
from pathlib import Path

CELLS=12
ROLES=4
DWELL=4
FP2_ROWS=((1,1,1,1),(0,1,0,1))
ROLE_ROWS=((1,0,1,0),(0,1,0,1))
METHODS=("TARGET_SELF_MIGRATION","TARGET_PLUS_STRUCTURE","SINGLE_PEER_MIGRATION","INDEPENDENT_ROLE_MIGRATION")
INITIAL_ROLES=tuple(c % 4 for c in range(CELLS))


def linear_map(x, rows):
    out=0
    for i,row in enumerate(rows):
        v=0
        for p,c in enumerate(row):
            if c and ((x>>p)&1): v ^= 1
        out |= v<<i
    return out

def fp2(x): return linear_map(x,FP2_ROWS)
def role2(x): return linear_map(x,ROLE_ROWS)
def role_to_fp2(r):
    r0=r&1; r1=(r>>1)&1
    return (r0^r1) | (r1<<1)
def peer_a(c): return (c+4)%CELLS
def peer_b(c): return (c+8)%CELLS

def longest_run(seq, value):
    best=cur=0
    for x in seq:
        if x==value:
            cur+=1; best=max(best,cur)
        else:
            cur=0
    return best

def method_authorizes(method, *, shadow_seq, old_role, new_role, structural_clean=True,
                      target_fp_start_matches=True, peer_a_old=True, peer_b_old=True,
                      demand_a=True, demand_b=True, peer_a_observed=True, peer_b_observed=True,
                      generation_conflict=False, unavailable_slots=(), cancel_before_commit=False):
    stable = longest_run(shadow_seq,new_role) >= DWELL
    if method=="TARGET_SELF_MIGRATION":
        ok=stable
    elif method=="TARGET_PLUS_STRUCTURE":
        ok=stable and structural_clean
    elif method=="SINGLE_PEER_MIGRATION":
        ok=(stable and structural_clean and target_fp_start_matches and peer_a_old and demand_a and peer_a_observed
            and not generation_conflict and "DEMAND_A" not in unavailable_slots and "PEER_A" not in unavailable_slots)
    elif method=="INDEPENDENT_ROLE_MIGRATION":
        ok=(stable and structural_clean and target_fp_start_matches and peer_a_old and peer_b_old
            and demand_a and demand_b and peer_a_observed and peer_b_observed and not generation_conflict
            and not set(unavailable_slots).intersection({"DEMAND_A","DEMAND_B","PEER_A","PEER_B"}))
    else:
        raise KeyError(method)
    if cancel_before_commit: return False
    return bool(ok)

def full_commit(authorize, target, old_role, new_role, generation, partial_records=None):
    if not authorize:
        return {"authority":old_role,"generation":generation,"split_brain":False,"rollback":False,
                "committed":False,"records":()}
    new_gen=generation+1
    records=("TARGET","PEER_A","PEER_B") if partial_records is None else tuple(sorted(partial_records))
    all3=set(records)=={"TARGET","PEER_A","PEER_B"}
    if all3:
        return {"authority":new_role,"generation":new_gen,"split_brain":False,"rollback":False,
                "committed":True,"records":records}
    return {"authority":old_role,"generation":generation,"split_brain":False,"rollback":True,
            "committed":False,"records":records}

def audit_a():
    out={m:Counter() for m in METHODS}; rows=[]
    for c in range(CELLS):
        old=INITIAL_ROLES[c]
        for new in range(ROLES):
            if new==old: continue
            for m in METHODS:
                auth=method_authorizes(m,shadow_seq=(new,)*DWELL,old_role=old,new_role=new)
                tx=full_commit(auth,c,old,new,0)
                if tx["committed"] and tx["authority"]==new: out[m]["LEGITIMATE_MIGRATION_COMMIT"]+=1
                else: out[m]["SAFE_ABORT"]+=1
                if tx["split_brain"]: out[m]["SPLIT_BRAIN"]+=1
            rows.append({"cell":c,"old_role":old,"new_role":new,"peer_a":peer_a(c),"peer_b":peer_b(c)})
    return {"cases":len(rows),"methods":{m:dict(sorted(c.items())) for m,c in out.items()},"examples":rows[:8]}

def audit_b():
    coalitions=list(itertools.combinations(range(CELLS),2))+list(itertools.combinations(range(CELLS),3))+[tuple(range(CELLS))]
    targets=0; commits=0; false=0; split=0; interference=0; samples=[]
    for co in coalitions:
        before=list(INITIAL_ROLES); after=list(before)
        for c in co:
            targets+=1; old=before[c]; new=(old+1)%ROLES
            auth=method_authorizes("INDEPENDENT_ROLE_MIGRATION",shadow_seq=(new,)*DWELL,old_role=old,new_role=new)
            tx=full_commit(auth,c,old,new,0)
            if tx["committed"] and tx["authority"]==new: commits+=1; after[c]=new
            else: false+=1
            split += int(tx["split_brain"])
        for c in range(CELLS):
            if c not in co and after[c]!=before[c]: interference+=1
        if len(samples)<8: samples.append({"coalition":co,"commits":sum(after[c]!=before[c] for c in co)})
    return {"coalitions":len(coalitions),"target_transactions":targets,"successful_commits":commits,
            "false_or_missed":false,"split_brain":split,"non_target_changes":interference,"examples":samples}

def audit_c():
    out=Counter(); rows=[]
    for c in range(CELLS):
        old=INITIAL_ROLES[c]
        for new in range(ROLES):
            if new==old: continue
            wrong=next(r for r in range(ROLES) if r not in (old,new))
            seq1=(wrong,new,new,new,new)
            auth1=method_authorizes("INDEPENDENT_ROLE_MIGRATION",shadow_seq=seq1,old_role=old,new_role=new)
            tx1=full_commit(auth1,c,old,new,0)
            if tx1["committed"] and longest_run(seq1,new)>=DWELL: out["C1_COMMIT_AFTER_FINAL_DWELL"]+=1
            else: out["C1_FAIL"]+=1
            early=any(method_authorizes("INDEPENDENT_ROLE_MIGRATION",shadow_seq=seq1[:k],old_role=old,new_role=new) for k in range(1,len(seq1)))
            out["C1_EARLY_COMMIT"] += int(early)
            seq2=tuple(old if i%2==0 else new for i in range(8))
            a2=method_authorizes("INDEPENDENT_ROLE_MIGRATION",shadow_seq=seq2,old_role=old,new_role=new)
            out["C2_ALTERNATING_ABORT"] += int(not a2)
            seq3=(new,new,new)
            a3=method_authorizes("INDEPENDENT_ROLE_MIGRATION",shadow_seq=seq3,old_role=old,new_role=new)
            out["C3_THREE_STEP_ABORT"] += int(not a3)
            if len(rows)<6: rows.append({"cell":c,"old":old,"new":new,"c1":seq1,"c2":seq2,"c3":seq3})
    return {"cases_each":36,"counts":dict(sorted(out.items())),"examples":rows}

def audit_d():
    conds=("D1_DEMAND_A_ABSENT","D2_DEMAND_B_ABSENT","D3_PEER_A_UNAVAILABLE","D4_PEER_B_UNAVAILABLE","D5_DEMAND_DISAGREE","D6_PEER_DISAGREE")
    commits=Counter(); cases=0
    for c in range(CELLS):
        old=INITIAL_ROLES[c]
        for new in range(ROLES):
            if new==old: continue
            cases+=1
            tests={
                conds[0]:dict(unavailable_slots=("DEMAND_A",)),
                conds[1]:dict(unavailable_slots=("DEMAND_B",)),
                conds[2]:dict(unavailable_slots=("PEER_A",)),
                conds[3]:dict(unavailable_slots=("PEER_B",)),
                conds[4]:dict(demand_b=False),
                conds[5]:dict(peer_b_observed=False),
            }
            for name,kw in tests.items():
                if method_authorizes("INDEPENDENT_ROLE_MIGRATION",shadow_seq=(new,)*DWELL,old_role=old,new_role=new,**kw): commits[name]+=1
    return {"cases_per_condition":cases,"commits":{k:commits[k] for k in conds}}

def audit_e():
    subsets=[s for r in (1,2) for s in itertools.combinations(("TARGET","PEER_A","PEER_B"),r)]
    cases=0; rollback=0; new_authority=0; split=0
    for c in range(CELLS):
        old=INITIAL_ROLES[c]
        for new in range(ROLES):
            if new==old: continue
            for sub in subsets:
                cases+=1
                tx=full_commit(True,c,old,new,0,sub)
                rollback+=int(tx["rollback"] and tx["authority"]==old)
                new_authority+=int(tx["authority"]==new)
                split+=int(tx["split_brain"])
    return {"partial_subsets":len(subsets),"cases":cases,"rollback_to_old":rollback,
            "new_role_authority":new_authority,"split_brain":split,"subsets":subsets}

def audit_f():
    conds=("F1_PEER_A_DAMAGED","F2_PEER_B_DAMAGED","F3_DEMAND_COHORT_DAMAGED")
    commits=Counter(); cases=0
    for c in range(CELLS):
        old=INITIAL_ROLES[c]
        for new in range(ROLES):
            if new==old: continue
            cases+=1
            tests={conds[0]:("PEER_A",),conds[1]:("PEER_B",),conds[2]:("DEMAND_A",)}
            for name,unavail in tests.items():
                commits[name]+=int(method_authorizes("INDEPENDENT_ROLE_MIGRATION",shadow_seq=(new,)*DWELL,old_role=old,new_role=new,unavailable_slots=unavail))
    return {"cases_per_condition":cases,"commits":{k:commits[k] for k in conds}}

def audit_g():
    cases=0; commits=0; metadata_changes=0
    for c in range(CELLS):
        old=INITIAL_ROLES[c]
        for new in range(ROLES):
            if new==old: continue
            cases+=1
            a=method_authorizes("INDEPENDENT_ROLE_MIGRATION",shadow_seq=(new,)*DWELL,old_role=old,new_role=new,cancel_before_commit=True)
            tx=full_commit(a,c,old,new,0)
            commits+=int(tx["committed"])
            metadata_changes+=int(tx["authority"]!=old or tx["generation"]!=0)
    return {"cases":cases,"commits":commits,"metadata_changes":metadata_changes}

def negative_controls():
    out={m:0 for m in METHODS}; cases=0
    for c in range(CELLS):
        old=INITIAL_ROLES[c]
        for new in range(ROLES):
            if new==old: continue
            cases+=1
            out["TARGET_SELF_MIGRATION"]+=int(method_authorizes("TARGET_SELF_MIGRATION",shadow_seq=(new,)*DWELL,old_role=old,new_role=new))
            out["TARGET_PLUS_STRUCTURE"]+=int(method_authorizes("TARGET_PLUS_STRUCTURE",shadow_seq=(new,)*DWELL,old_role=old,new_role=new))
            out["SINGLE_PEER_MIGRATION"]+=int(method_authorizes("SINGLE_PEER_MIGRATION",shadow_seq=(new,)*DWELL,old_role=old,new_role=new,demand_a=True,peer_a_observed=True))
            out["INDEPENDENT_ROLE_MIGRATION"]+=int(method_authorizes("INDEPENDENT_ROLE_MIGRATION",shadow_seq=(new,)*DWELL,old_role=old,new_role=new,demand_a=False,demand_b=False,peer_a_observed=False,peer_b_observed=False))
    return {"false_role_cases":cases,"authorizations":out}

def correlated_holdouts():
    h=Counter(); cases=0
    for c in range(CELLS):
        old=INITIAL_ROLES[c]
        for new in range(ROLES):
            if new==old: continue
            cases+=1
            a1=method_authorizes("INDEPENDENT_ROLE_MIGRATION",shadow_seq=(new,)*DWELL,old_role=old,new_role=new,
                                demand_a=True,demand_b=True,peer_a_observed=False,peer_b_observed=False)
            h["H1_BOTH_DEMAND_FORGED_FALSE_COMMIT"]+=int(a1)
            a2=method_authorizes("INDEPENDENT_ROLE_MIGRATION",shadow_seq=(new,)*DWELL,old_role=old,new_role=new,
                                demand_a=False,demand_b=False,peer_a_observed=True,peer_b_observed=True)
            h["H2_BOTH_PEERS_FORGED_FALSE_COMMIT"]+=int(a2)
            a3=method_authorizes("INDEPENDENT_ROLE_MIGRATION",shadow_seq=(new,)*DWELL,old_role=old,new_role=new,
                                demand_a=True,demand_b=True,peer_a_observed=True,peer_b_observed=True)
            h["H3_FULL_FORGERY_FALSE_COMMIT"]+=int(a3)
            one_cases=(
                dict(demand_a=True,demand_b=False,peer_a_observed=False,peer_b_observed=False),
                dict(demand_a=False,demand_b=True,peer_a_observed=False,peer_b_observed=False),
                dict(demand_a=False,demand_b=False,peer_a_observed=True,peer_b_observed=False),
                dict(demand_a=False,demand_b=False,peer_a_observed=False,peer_b_observed=True),
            )
            for kw in one_cases:
                h["H4_ONE_OF_FOUR_FALSE_COMMIT"]+=int(method_authorizes("INDEPENDENT_ROLE_MIGRATION",shadow_seq=(new,)*DWELL,old_role=old,new_role=new,**kw))
    return {"base_cases":cases,"counts":dict(sorted(h.items()))}

def signals(a,b,c,d,e,f,g,corr):
    am=a["methods"]["INDEPENDENT_ROLE_MIGRATION"]
    single=(am.get("LEGITIMATE_MIGRATION_COMMIT",0)==36 and am.get("SPLIT_BRAIN",0)==0)
    coordinated=(b["successful_commits"]==b["target_transactions"] and b["false_or_missed"]==0 and b["split_brain"]==0 and b["non_target_changes"]==0)
    dwell=(c["counts"].get("C1_COMMIT_AFTER_FINAL_DWELL",0)==36 and c["counts"].get("C1_EARLY_COMMIT",0)==0 and c["counts"].get("C2_ALTERNATING_ABORT",0)==36 and c["counts"].get("C3_THREE_STEP_ABORT",0)==36)
    partial=all(v==0 for v in d["commits"].values())
    rollback=(e["rollback_to_old"]==e["cases"] and e["new_role_authority"]==0 and e["split_brain"]==0)
    damaged=all(v==0 for v in f["commits"].values())
    pre=(g["commits"]==0 and g["metadata_changes"]==0)
    safe=all((single,coordinated,dwell,partial,rollback,damaged,pre))
    return {"SINGLE_ROLE_MIGRATION_SUCCESS":single,"COORDINATED_ROLE_MIGRATION_SUCCESS":coordinated,
            "DWELL_DISCIPLINE_PRESERVED":dwell,"PARTIAL_PROVENANCE_ABORTS":partial,
            "PARTIAL_COMMIT_ROLLBACK":rollback,"DAMAGED_WITNESS_ABORTS":damaged,
            "PRECOMMIT_ROLLBACK_CLEAN":pre,"SAFE_ROLE_MIGRATION":safe,
            "CORRELATED_ROLE_FORGERY_FAILURE":corr["counts"].get("H3_FULL_FORGERY_FALSE_COMMIT",0)>0,
            "ONE_OF_FOUR_FORGERY_SUPPRESSED":corr["counts"].get("H4_ONE_OF_FOUR_FALSE_COMMIT",0)==0}

def validate():
    assert tuple(fp2(x) for x in range(16)) == tuple(role_to_fp2(role2(x)) for x in range(16))
    assert tuple(INITIAL_ROLES).count(0)==3 and tuple(INITIAL_ROLES).count(1)==3 and tuple(INITIAL_ROLES).count(2)==3 and tuple(INITIAL_ROLES).count(3)==3
    for c in range(CELLS):
        assert peer_a(c)!=c and peer_b(c)!=c and peer_a(c)!=peer_b(c)
    assert DWELL==4
    assert CELLS*(ROLES-1)==36
    assert len(list(itertools.combinations(range(CELLS),2)))+len(list(itertools.combinations(range(CELLS),3)))+1==287
    subsets=[s for r in (1,2) for s in itertools.combinations(("TARGET","PEER_A","PEER_B"),r)]
    assert len(subsets)==6
    return {"single_migrations":36,"coordinated_coalitions":287,"partial_commit_subsets":6,
            "initial_role_counts":{str(r):INITIAL_ROLES.count(r) for r in range(ROLES)},"dwell":DWELL}

def run():
    mech=validate(); a=audit_a(); b=audit_b(); c=audit_c(); d=audit_d(); e=audit_e(); f=audit_f(); g=audit_g(); neg=negative_controls(); corr=correlated_holdouts()
    return {"schema":"yggdrasil.dg1r-05s-role-migration-consensus.v1","mechanical_valid":True,"mechanical":mech,
            "audit_a_single_cell":a,"audit_b_coordinated":b,"audit_c_dwell":c,"audit_d_partial_provenance":d,
            "audit_e_partial_commit":e,"audit_f_witness_damage":f,"audit_g_precommit_cancel":g,
            "negative_controls":neg,"correlated_forgery_boundary":corr,
            "signals":signals(a,b,c,d,e,f,g,corr),"canonical_scientific_execution":False,"stab18_r1_touched":False}

def enc(o): return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--out"); ap.add_argument("--mechanical-only",action="store_true"); a=ap.parse_args()
    if a.mechanical_only:
        print(enc({"mechanical_valid":True,"mechanical":validate()})); return
    if not a.out: raise SystemExit("--out required unless --mechanical-only")
    obj=run(); raw=(enc(obj)+"\n").encode(); Path(a.out).write_bytes(raw)
    print(enc({"output":a.out,"sha256":hashlib.sha256(raw).hexdigest(),"signals":obj["signals"]}))
if __name__=="__main__": main()
