#!/usr/bin/env python3
import argparse, hashlib, itertools, json, math
from collections import Counter
from pathlib import Path

ROOTS=8
SLOTS=("REG_A","REG_B","REG_C","REG_D")
QUORUM=3
METHODS=("HEADCOUNT3","DISTINCT_HOLDER3","LINEAGE_QUORUM3")


def singleton(r): return 1<<r

def pairwise_disjoint(masks):
    return all((a & b)==0 for a,b in itertools.combinations(masks,2))

def lineage_quorum3(votes):
    masks=[v["verified_lineage"] for v in votes if v.get("present",True)]
    for combo in itertools.combinations(masks,QUORUM):
        if all(m not in (None,0) for m in combo) and pairwise_disjoint(combo):
            return True
    return False

def authorize(method,votes):
    present=[v for v in votes if v.get("present",True)]
    if method=="HEADCOUNT3":
        return len(present)>=QUORUM
    if method=="DISTINCT_HOLDER3":
        return len({v["holder_id"] for v in present})>=QUORUM
    if method=="LINEAGE_QUORUM3":
        return lineage_quorum3(present)
    raise KeyError(method)

def votes_from_masks(masks,holders=None,present=None,self_claims=None):
    n=len(masks)
    if holders is None: holders=[f"H{i}" for i in range(n)]
    if present is None: present=[True]*n
    if self_claims is None: self_claims=list(masks)
    return [{"slot":SLOTS[i] if i<len(SLOTS) else f"EXTRA_{i}",
             "holder_id":holders[i],"verified_lineage":masks[i],
             "self_claim":self_claims[i],"present":present[i]} for i in range(n)]

def ordered_pair_partitions(items):
    items=tuple(items)
    for p0 in itertools.combinations(items,2):
        rem0=tuple(x for x in items if x not in p0)
        for p1 in itertools.combinations(rem0,2):
            rem1=tuple(x for x in rem0 if x not in p1)
            p2=tuple(sorted(rem1))
            yield (tuple(sorted(p0)),tuple(sorted(p1)),p2)

def audit_a():
    out={m:Counter() for m in METHODS}; qualified=unqualified=0
    for a in itertools.product(range(ROOTS),repeat=4):
        truth=len(set(a))>=3
        qualified+=int(truth); unqualified+=int(not truth)
        votes=votes_from_masks([singleton(r) for r in a])
        for m in METHODS:
            ok=authorize(m,votes)
            out[m]["TRUE_AUTH" if ok and truth else "FALSE_AUTH" if ok else "ABSTAIN"]+=1
    return {"cases":4096,"qualified":qualified,"unqualified":unqualified,
            "methods":{m:dict(sorted(c.items())) for m,c in out.items()}}

def audit_b():
    auth={m:0 for m in METHODS}; cases=0
    for shared in range(ROOTS):
        for other in range(ROOTS):
            if other==shared: continue
            for different_slot in range(4):
                cases+=1
                roots=[shared]*4; roots[different_slot]=other
                v=votes_from_masks([singleton(r) for r in roots])
                for m in METHODS: auth[m]+=int(authorize(m,v))
    return {"cases":cases,"authorizations":auth}

def audit_c():
    auth={m:0 for m in METHODS}; cases=0
    for a,b in itertools.combinations(range(ROOTS),2):
        for slots_a in itertools.combinations(range(4),2):
            cases+=1
            roots=[b]*4
            for i in slots_a: roots[i]=a
            v=votes_from_masks([singleton(r) for r in roots])
            for m in METHODS: auth[m]+=int(authorize(m,v))
    return {"cases":cases,"authorizations":auth}

def audit_d():
    auth=0; cases=0
    for a in itertools.product(range(ROOTS),repeat=4):
        if len(set(a))!=3: continue
        cases+=1; auth+=int(lineage_quorum3(votes_from_masks([singleton(r) for r in a])))
    return {"cases":cases,"authorizations":auth}

def audit_e():
    auth=0; cases=0
    for roots in itertools.combinations(range(ROOTS),3):
        for ordered in itertools.permutations(roots,3):
            for missing in range(4):
                cases+=1
                masks=[]; holders=[]
                j=0
                for i in range(4):
                    if i==missing: continue
                    masks.append(singleton(ordered[j])); holders.append(f"H{i}"); j+=1
                auth+=int(lineage_quorum3(votes_from_masks(masks,holders=holders)))
    return {"cases":cases,"authorizations":auth}

def audit_f():
    auth=0; cases=0; samples=[]
    for chosen in itertools.combinations(range(ROOTS),6):
        for parts in ordered_pair_partitions(chosen):
            cases+=1
            masks=[sum(singleton(r) for r in pair) for pair in parts]
            ok=lineage_quorum3(votes_from_masks(masks))
            auth+=int(ok)
            if len(samples)<6: samples.append({"parts":parts,"masks":masks})
    return {"cases":cases,"authorizations":auth,"examples":samples}

def audit_g():
    auth=0; cases=0
    for chosen in itertools.combinations(range(ROOTS),6):
        for parts in ordered_pair_partitions(chosen):
            base=[sum(singleton(r) for r in pair) for pair in parts]
            for i,j in itertools.combinations(range(3),2):
                cases+=1; masks=list(base)
                shared_bit=masks[i] & -masks[i]
                masks[j] |= shared_bit
                auth+=int(lineage_quorum3(votes_from_masks(masks)))
    return {"cases":cases,"authorizations":auth}

def audit_h():
    unchanged=0; cases=0
    for a in itertools.product(range(ROOTS),repeat=4):
        if len(set(a))<3: continue
        cases+=1; masks=[singleton(r) for r in a]
        before=lineage_quorum3(votes_from_masks(masks))
        holders=[f"ROT_{i}_{r}" for i,r in enumerate(a)]
        after=lineage_quorum3(votes_from_masks(masks,holders=holders))
        unchanged+=int(before==after==True)
    return {"cases":cases,"unchanged":unchanged}

def audit_i():
    cand_auth=head_auth=distinct_auth=0; cases=0
    for r in range(ROOTS):
        for fanout in (3,4,8,16):
            cases+=1
            n=min(fanout,4)
            masks=[singleton(r)]*n
            holders=[f"R{r}_D{i}" for i in range(n)]
            v=votes_from_masks(masks,holders=holders)
            cand_auth+=int(authorize("LINEAGE_QUORUM3",v))
            head_auth+=int(authorize("HEADCOUNT3",v))
            distinct_auth+=int(authorize("DISTINCT_HOLDER3",v))
    return {"cases":cases,"candidate_authorizations":cand_auth,"headcount_authorizations":head_auth,
            "distinct_holder_authorizations":distinct_auth}

def audit_j():
    auth={m:0 for m in METHODS}; cases=0
    for shared in range(ROOTS):
        for honest in range(ROOTS):
            if honest==shared: continue
            for cls in ("OMISSION","INSERTION"):
                cases+=1
                masks=[singleton(shared)]*3+[singleton(honest)]
                present=[True,True,True,False]
                v=votes_from_masks(masks,present=present)
                for m in METHODS: auth[m]+=int(authorize(m,v))
    return {"cases":cases,"authorizations":auth}

def holdouts():
    h1=0; h1_cases=0
    for roots in itertools.permutations(range(ROOTS),4):
        h1_cases+=1
        masks=[singleton(r) for r in roots]
        v=votes_from_masks(masks,present=[True,True,True,False])
        h1+=int(lineage_quorum3(v))
    h2=0; h2_cases=0
    for ids in itertools.permutations(range(ROOTS),3):
        h2_cases+=1
        masks=[singleton(r) for r in ids]
        h2+=int(lineage_quorum3(votes_from_masks(masks)))
    # Same actual source is evaluator truth; candidate only sees distinct verified root masks.
    selfclaim_unchanged=0; selfclaim_cases=0
    for a in itertools.product(range(ROOTS),repeat=4):
        selfclaim_cases+=1
        masks=[singleton(r) for r in a]
        bogus=[singleton((r+1)%ROOTS) for r in a]
        v=votes_from_masks(masks,self_claims=bogus)
        selfclaim_unchanged+=int(lineage_quorum3(v)==(len(set(a))>=3))
    return {"H1_independent_three_root_collusion_cases":h1_cases,"H1_false_authorizations":h1,
            "H2_root_compromise_cases":h2_cases,"H2_false_authorizations":h2,
            "H3_self_claim_cases":selfclaim_cases,"H3_decisions_unchanged":selfclaim_unchanged}

def signals(a,b,c,d,e,f,g,h,i,j,hold):
    cand=a["methods"]["LINEAGE_QUORUM3"]
    single=(a["qualified"]==3696 and a["unqualified"]==400 and cand.get("TRUE_AUTH",0)==3696 and cand.get("FALSE_AUTH",0)==0 and cand.get("ABSTAIN",0)==400)
    vals={
      "SINGLE_ROOT_QUORUM_EXACT":single,
      "HEADCOUNT_DUPLICATION_EXPOSED":a["methods"]["HEADCOUNT3"].get("FALSE_AUTH",0)>0,
      "TRIPLE_DESCENDANT_FALSE_QUORUM_REJECTED":b["authorizations"]["LINEAGE_QUORUM3"]==0,
      "PAIR_DUPLICATION_REJECTED":c["authorizations"]["LINEAGE_QUORUM3"]==0,
      "THREE_ROOT_LIVENESS_PRESERVED":d["cases"]==2016 and d["authorizations"]==2016,
      "ONE_REPLICA_LOSS_WITH_INDEPENDENT_QUORUM":e["cases"]==1344 and e["authorizations"]==1344,
      "COMPOUND_DISJOINT_REGISTRY_ACCEPTANCE":f["cases"]==2520 and f["authorizations"]==2520,
      "PARTIAL_REGISTRY_OVERLAP_REJECTED":g["authorizations"]==0,
      "REGISTRY_HOLDER_ROTATION_PRESERVES_QUORUM":h["cases"]==3696 and h["unchanged"]==3696,
      "REGISTRY_DESCENDANT_FANOUT_NOT_QUORUM":i["candidate_authorizations"]==0,
      "SAME_LINEAGE_REGISTRY_MAJORITY_COLLAPSED":j["authorizations"]["LINEAGE_QUORUM3"]==0,
      "REGISTRY_SELF_CLAIM_IGNORED":hold["H3_decisions_unchanged"]==hold["H3_self_claim_cases"],
    }
    vals["LINEAGE_QUALIFIED_REGISTRY_GAIN"]=all(vals.values())
    vals["INDEPENDENT_THREE_ROOT_COLLUSION_FAILURE"]=hold["H1_false_authorizations"]>0
    vals["ROOT_COMPROMISE_FAILURE"]=hold["H2_false_authorizations"]>0
    return vals

def validate():
    assert ROOTS==8 and len(SLOTS)==4 and QUORUM==3
    qa=sum(1 for a in itertools.product(range(ROOTS),repeat=4) if len(set(a))>=3)
    assert qa==3696 and 4096-qa==400
    assert 8*7*4==224
    assert math.comb(8,2)*math.comb(4,2)==168
    assert sum(1 for a in itertools.product(range(ROOTS),repeat=4) if len(set(a))==3)==2016
    assert math.comb(8,3)*math.factorial(3)*4==1344
    assert sum(1 for chosen in itertools.combinations(range(8),6) for _ in ordered_pair_partitions(chosen))==2520
    return {"A":4096,"A_qualified":3696,"A_unqualified":400,"B":224,"C":168,"D":2016,
            "E":1344,"F":2520,"H":3696,"I":32,"J":112}

def run():
    mech=validate(); a=audit_a(); b=audit_b(); c=audit_c(); d=audit_d(); e=audit_e(); f=audit_f()
    g=audit_g(); h=audit_h(); i=audit_i(); j=audit_j(); hold=holdouts()
    return {"schema":"yggdrasil.dg1r-05w-lineage-qualified-registry-quorum.v1","mechanical_valid":True,"mechanical":mech,
            "audit_a":a,"audit_b":b,"audit_c":c,"audit_d":d,"audit_e":e,"audit_f":f,"audit_g":g,
            "audit_h":h,"audit_i":i,"audit_j":j,"correlated_boundary":hold,
            "signals":signals(a,b,c,d,e,f,g,h,i,j,hold),
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
