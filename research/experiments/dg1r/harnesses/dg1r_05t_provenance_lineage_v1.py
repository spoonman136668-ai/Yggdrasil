#!/usr/bin/env python3
import argparse, hashlib, itertools, json
from collections import Counter
from pathlib import Path

ROOTS=8
SLOTS=("DEMAND_A","DEMAND_B","PEER_A","PEER_B")
METHODS=("HEADCOUNT4","DISTINCT_HOLDER4","LINEAGE_DISJOINT4")
PAIR_INDEXES=tuple(itertools.combinations(range(4),2))


def rec(slot,holder,reported,actual=None):
    return {"slot":slot,"holder":holder,"reported":reported,"actual":reported if actual is None else actual}

def pairwise_disjoint(masks):
    return all((masks[i] & masks[j])==0 for i,j in PAIR_INDEXES)

def choose_slot_representatives(records, key):
    by={s:[r for r in records if r["slot"]==s] for s in SLOTS}
    if any(not by[s] for s in SLOTS): return []
    return itertools.product(*(by[s] for s in SLOTS))

def independent_quorum(records,key="actual"):
    for combo in choose_slot_representatives(records,key):
        holders=[r["holder"] for r in combo]
        masks=[r[key] for r in combo]
        if len(set(holders))<4: continue
        if any(m==0 for m in masks): continue
        if pairwise_disjoint(masks): return True
    return False

def method_authorizes(method,records):
    if method=="HEADCOUNT4":
        return len(records)>=4
    if method=="DISTINCT_HOLDER4":
        if len({r["holder"] for r in records})<4: return False
        return all(any(r["slot"]==s for r in records) for s in SLOTS)
    if method=="LINEAGE_DISJOINT4":
        return independent_quorum(records,"reported")
    raise KeyError(method)

def classify(method,records):
    auth=method_authorizes(method,records)
    truth=independent_quorum(records,"actual")
    if auth and truth: return "TRUE_AUTHORIZATION"
    if auth and not truth: return "FALSE_QUORUM_AUTHORIZATION"
    if (not auth) and truth: return "MISSED_TRUE_QUORUM"
    return "SAFE_ABSTAIN"

def audit_a():
    out={m:Counter() for m in METHODS}; clean=dup=0
    for roots in itertools.product(range(ROOTS),repeat=4):
        rs=[rec(SLOTS[i],i,1<<roots[i]) for i in range(4)]
        truth=len(set(roots))==4
        clean+=int(truth); dup+=int(not truth)
        for m in METHODS: out[m][classify(m,rs)]+=1
    return {"cases":clean+dup,"clean":clean,"duplicated":dup,"methods":{m:dict(sorted(c.items())) for m,c in out.items()}}

def clean_root_assignments():
    return itertools.permutations(range(ROOTS),4)

def audit_b():
    out={m:Counter() for m in METHODS}; n=0; examples=[]
    for roots in clean_root_assignments():
        spare=min(r for r in range(ROOTS) if r not in roots)
        for i,j in PAIR_INDEXES:
            masks=[1<<r for r in roots]
            masks[i] |= 1<<spare; masks[j] |= 1<<spare
            rs=[rec(SLOTS[k],k,masks[k]) for k in range(4)]
            n+=1
            for m in METHODS: out[m][classify(m,rs)]+=1
            if len(examples)<6: examples.append({"roots":roots,"pair":(i,j),"shared_extra":spare,"masks":masks})
    return {"cases":n,"methods":{m:dict(sorted(c.items())) for m,c in out.items()},"examples":examples}

def audit_c():
    sizes=(1,2,4,8,16,32); out={m:Counter() for m in METHODS}; rows=[]
    for root in range(ROOTS):
        for n in sizes:
            rs=[rec(SLOTS[i%4],1000+root*100+i,1<<root) for i in range(n)]
            for m in METHODS: out[m][classify(m,rs)]+=1
            rows.append({"root":root,"descendants":n,"effective_independent":int(independent_quorum(rs,"actual"))})
    return {"cases":len(rows),"methods":{m:dict(sorted(c.items())) for m,c in out.items()},"rows":rows}

def audit_d():
    n=0; auth=0; changed=0
    for roots in clean_root_assignments():
        base=[rec(SLOTS[i],i,1<<roots[i]) for i in range(4)]
        rot=[rec(SLOTS[i],100+i,1<<roots[i]) for i in range(4)]
        n+=1
        before=method_authorizes("LINEAGE_DISJOINT4",base); after=method_authorizes("LINEAGE_DISJOINT4",rot)
        auth+=int(after); changed+=int(before!=after)
    return {"cases":n,"authorized_after_rotation":auth,"decision_changes":changed}

def audit_e():
    n=0; auth=0
    for roots in clean_root_assignments():
        base=[rec(SLOTS[i],i,1<<roots[i]) for i in range(4)]
        for missing in range(4):
            rs=[r for i,r in enumerate(base) if i!=missing]
            n+=1; auth+=int(method_authorizes("LINEAGE_DISJOINT4",rs))
    return {"cases":n,"authorizations":auth}

def ordered_pair_partitions():
    roots=tuple(range(ROOTS))
    for p0 in itertools.combinations(roots,2):
        rem1=tuple(r for r in roots if r not in p0)
        for p1 in itertools.combinations(rem1,2):
            rem2=tuple(r for r in rem1 if r not in p1)
            for p2 in itertools.combinations(rem2,2):
                p3=tuple(r for r in rem2 if r not in p2)
                yield (p0,p1,p2,p3)

def audit_f():
    n=0; auth=0; false=0; examples=[]
    for pairs in ordered_pair_partitions():
        masks=[sum(1<<r for r in pair) for pair in pairs]
        rs=[rec(SLOTS[i],i,masks[i]) for i in range(4)]
        n+=1; a=method_authorizes("LINEAGE_DISJOINT4",rs); auth+=int(a); false+=int(a and not independent_quorum(rs,"actual"))
        if len(examples)<5: examples.append({"pairs":pairs,"masks":masks})
    return {"cases":n,"authorizations":auth,"false_authorizations":false,"examples":examples}

def audit_g():
    sizes=(1,2,4,8,16); out={m:Counter() for m in METHODS}; n=0
    for slot in SLOTS:
        for root in range(ROOTS):
            for count in sizes:
                rs=[rec(slot,5000+count*100+i,1<<root) for i in range(count)]
                n+=1
                for m in METHODS: out[m][classify(m,rs)]+=1
    return {"cases":n,"methods":{m:dict(sorted(c.items())) for m,c in out.items()}}

def holdouts():
    h=Counter()
    for actual_root in range(ROOTS):
        reported=tuple(range(4))
        rs=[rec(SLOTS[i],i,1<<reported[i],actual=1<<actual_root) for i in range(4)]
        h["H1_FORGED_LINEAGE_FALSE_AUTHORIZATION"]+=int(method_authorizes("LINEAGE_DISJOINT4",rs) and not independent_quorum(rs,"actual"))
        honest=[rec(SLOTS[i],i,1<<actual_root) for i in range(4)]
        h["H3_H1_TRUTHFUL_ABSTAIN"]+=int(not method_authorizes("LINEAGE_DISJOINT4",honest))
    for roots in clean_root_assignments():
        actual=[1<<r for r in roots]
        actual[1] |= actual[0]
        reported=[1<<r for r in roots]
        forged=[rec(SLOTS[i],i,reported[i],actual=actual[i]) for i in range(4)]
        truthful=[rec(SLOTS[i],i,actual[i]) for i in range(4)]
        h["H2_SINGLE_LINEAGE_LIE_FALSE_AUTHORIZATION"]+=int(method_authorizes("LINEAGE_DISJOINT4",forged) and not independent_quorum(forged,"actual"))
        h["H3_H2_TRUTHFUL_ABSTAIN"]+=int(not method_authorizes("LINEAGE_DISJOINT4",truthful))
    return {"counts":dict(sorted(h.items()))}

def primary_false_total(a,b,c,d,e,f,g):
    return sum(x["methods"]["LINEAGE_DISJOINT4"].get("FALSE_QUORUM_AUTHORIZATION",0) for x in (a,b,c,g)) + f["false_authorizations"]

def signals(a,b,c,d,e,f,g,h):
    la=a["methods"]["LINEAGE_DISJOINT4"]
    clean=(la.get("TRUE_AUTHORIZATION",0)==1680 and la.get("MISSED_TRUE_QUORUM",0)==0)
    duplicate=(la.get("FALSE_QUORUM_AUTHORIZATION",0)==0 and la.get("SAFE_ABSTAIN",0)==2416)
    distinct_exposed=a["methods"]["DISTINCT_HOLDER4"].get("FALSE_QUORUM_AUTHORIZATION",0)>0
    partial=b["methods"]["LINEAGE_DISJOINT4"].get("FALSE_QUORUM_AUTHORIZATION",0)==0 and b["methods"]["LINEAGE_DISJOINT4"].get("SAFE_ABSTAIN",0)==10080
    descend=c["methods"]["LINEAGE_DISJOINT4"].get("FALSE_QUORUM_AUTHORIZATION",0)==0
    headinflate=c["methods"]["HEADCOUNT4"].get("FALSE_QUORUM_AUTHORIZATION",0)>0
    rotation=(d["authorized_after_rotation"]==1680 and d["decision_changes"]==0)
    missing=e["authorizations"]==0
    compound=(f["authorizations"]==2520 and f["false_authorizations"]==0)
    fanout=g["methods"]["LINEAGE_DISJOINT4"].get("FALSE_QUORUM_AUTHORIZATION",0)==0 and g["methods"]["LINEAGE_DISJOINT4"].get("TRUE_AUTHORIZATION",0)==0
    false_total=primary_false_total(a,b,c,d,e,f,g)
    gain=all((clean,duplicate,partial,descend,rotation,missing,compound,fanout)) and false_total==0
    return {"CLEAN_SINGLE_ROOT_ACCEPTANCE":clean,"DUPLICATE_SINGLE_ROOT_REJECTION":duplicate,
            "DISTINCT_HOLDER_FALSE_QUORUM_EXPOSED":distinct_exposed,"PARTIAL_OVERLAP_REJECTION":partial,
            "DESCENDANT_INFLATION_REJECTED":descend,"HEADCOUNT_INFLATION_EXPOSED":headinflate,
            "HOLDER_ROTATION_PRESERVES_AUTHORITY":rotation,"MISSING_ROOT_ABSTAINS":missing,
            "COMPOUND_DISJOINT_ACCEPTANCE":compound,"COPY_FANOUT_NOT_COUNTED_AS_QUORUM":fanout,
            "ZERO_FALSE_PRIMARY":false_total==0,"PROVENANCE_INDEPENDENCE_GAIN":gain,
            "FORGED_LINEAGE_FALSE_AUTHORIZATION":h["counts"].get("H1_FORGED_LINEAGE_FALSE_AUTHORIZATION",0)>0,
            "SINGLE_LINEAGE_LIE_FAILURE":h["counts"].get("H2_SINGLE_LINEAGE_LIE_FALSE_AUTHORIZATION",0)>0}

def validate():
    assert ROOTS==8 and len(SLOTS)==4 and len(PAIR_INDEXES)==6
    assert 8**4==4096
    assert 8*7*6*5==1680
    assert 4096-1680==2416
    assert 1680*6==10080
    assert 1680*4==6720
    assert sum(1 for _ in ordered_pair_partitions())==2520
    return {"roots":8,"slots":4,"slot_pairs":6,"audit_a":4096,"audit_a_clean":1680,"audit_a_duplicate":2416,
            "audit_b":10080,"audit_e":6720,"audit_f":2520}

def run():
    mech=validate(); a=audit_a(); b=audit_b(); c=audit_c(); d=audit_d(); e=audit_e(); f=audit_f(); g=audit_g(); h=holdouts()
    return {"schema":"yggdrasil.dg1r-05t-provenance-lineage.v1","mechanical_valid":True,"mechanical":mech,
            "audit_a_single_root":a,"audit_b_partial_overlap":b,"audit_c_descendant_inflation":c,"audit_d_holder_rotation":d,
            "audit_e_missing_root":e,"audit_f_compound_disjoint":f,"audit_g_copy_fanout":g,"metadata_forgery_boundary":h,
            "signals":signals(a,b,c,d,e,f,g,h),"canonical_scientific_execution":False,"stab18_r1_touched":False}

def enc(o): return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--out"); ap.add_argument("--mechanical-only",action="store_true"); a=ap.parse_args()
    if a.mechanical_only:
        print(enc({"mechanical_valid":True,"mechanical":validate()})); return
    if not a.out: raise SystemExit("--out required unless --mechanical-only")
    obj=run(); raw=(enc(obj)+"\n").encode(); Path(a.out).write_bytes(raw)
    print(enc({"output":a.out,"sha256":hashlib.sha256(raw).hexdigest(),"signals":obj["signals"]}))
if __name__=="__main__": main()
