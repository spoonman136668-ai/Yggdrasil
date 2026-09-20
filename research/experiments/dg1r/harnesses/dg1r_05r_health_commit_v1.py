#!/usr/bin/env python3
import argparse, hashlib, itertools, json, math
from collections import Counter
from pathlib import Path

BLOCKS=12; PLANES=4; CHECKS=20; DWELL=4
EDGES=(
(0,2,7,9),(1,3,6,11),(4,5,9,10,11),(2,3,5),(0,1,4,8),
(6,7,8,10),(2,4,6),(0,3,5,6,7),(1,7,10,11),(1,5,6,9),
(3,8,9,10),(0,4,8,11),(0,2,6,10),(1,3,4,7),(2,5,7,8,11),
(2,3,4,10),(0,1,5,10),(0,3,9,11),(1,2,8,9),(4,7,9),
)
EXPECTED_DEG=(7,7,7,7,7,6,6,7,6,7,7,6)
FP_ROWS=((1,1,1,1),(0,1,0,1),(0,0,1,1),(0,0,0,1))
ROLE_ROWS=((1,0,1,0),(0,1,0,1))
DEPTHS=(2,3,4)
RESOURCE_TOTALS={2:200,3:212,4:224}
METHODS=("SELF_STABLE","STRUCTURAL_STABLE","INDEPENDENT_QUORUM")


def cols():
    out=[0]*BLOCKS
    for i,e in enumerate(EDGES):
        for b in e: out[b] |= 1<<i
    return tuple(out)
COLS=cols()

def gf2_rank(vs):
    basis={}
    for x in vs:
        v=int(x)
        while v:
            p=v.bit_length()-1
            if p in basis: v ^= basis[p]
            else: basis[p]=v; break
    return len(basis)

def syndrome(mask):
    s=0
    for b in range(BLOCKS):
        if (mask>>b)&1: s ^= COLS[b]
    return s

def static_geometry():
    syn=[syndrome(m) for m in range(1,1<<BLOCKS)]
    pair=Counter()
    for e in EDGES:
        for a,b in itertools.combinations(e,2): pair[tuple(sorted((a,b)))]+=1
    return {
        "rank":gf2_rank(COLS),
        "kernel_count":sum(x==0 for x in syn),
        "single_floor":min(c.bit_count() for c in COLS),
        "two_floor":min((COLS[a]^COLS[b]).bit_count() for a,b in itertools.combinations(range(BLOCKS),2)),
        "global_floor":min(x.bit_count() for x in syn if x),
        "max_pair_cooccurrence":max(pair.values()),
        "incidences":sum(len(e) for e in EDGES),
        "degree_vector":tuple(sum(b in e for e in EDGES) for b in range(BLOCKS)),
    }

def linear_map(x, rows, depth=None):
    if depth is None: depth=len(rows)
    out=0
    for i,row in enumerate(rows[:depth]):
        v=0
        for p,c in enumerate(row):
            if c and ((x>>p)&1): v ^= 1
        out |= v<<i
    return out

def fp(x,b): return linear_map(x,FP_ROWS,b)
def role(x): return linear_map(x,ROLE_ROWS,2)
def role_preserving(delta): return role(delta)==0

def peer_a(c): return (c+4)%12
def peer_b(c): return (c+8)%12

def method_commit(method, visible_change, structural_clean, role_matches_a, role_matches_b, stable=True):
    if not visible_change or not stable: return False
    if method=="SELF_STABLE": return True
    if method=="STRUCTURAL_STABLE": return bool(structural_clean)
    if method=="INDEPENDENT_QUORUM": return bool(structural_clean and role_matches_a and role_matches_b)
    raise KeyError(method)

def classify(commit, benign):
    if commit and benign: return "BENIGN_COMMIT"
    if commit and not benign: return "POISON_COMMIT"
    return "SAFE_ABSTAIN"

def audit_a(depth):
    by_method={m:Counter() for m in METHODS}; transitions=0; benign=0; harmful=0; aliases=0
    examples=[]
    for cell in range(BLOCKS):
        for base in range(16):
            base_role=role(base)
            for delta in range(1,16):
                transitions+=1; new=base^delta; is_benign=(role(new)==base_role)
                if is_benign: benign+=1
                else: harmful+=1
                visible=fp(delta,depth)!=0
                if (not is_benign) and not visible: aliases+=1
                structural_clean=True
                a_match=(base_role==role(new)); b_match=a_match
                for m in METHODS:
                    c=method_commit(m,visible,structural_clean,a_match,b_match)
                    lab=classify(c,is_benign); by_method[m][lab]+=1
                    if is_benign and visible and not c: by_method[m]["MISSED_BENIGN_REFRESH"]+=1
                    if (not is_benign) and (not visible): by_method[m]["UNDETECTED_HARMFUL_ALIAS"]+=1
                if len(examples)<8 and not is_benign and visible:
                    examples.append({"cell":cell,"base":base,"delta":delta,"fp_delta":fp(delta,depth),"role_delta":role(delta)})
    return {"transitions":transitions,"role_preserving":benign,"role_changing":harmful,"harmful_aliases":aliases,
            "methods":{m:dict(sorted(c.items())) for m,c in by_method.items()},"examples":examples}

def audit_b(depth):
    by_method={m:Counter() for m in METHODS}; n=0
    for cell in range(BLOCKS):
        for base in range(16):
            for delta in range(1,16):
                if role_preserving(delta): continue
                n+=1; visible=fp(delta,depth)!=0
                for m in METHODS:
                    c=method_commit(m,visible,False,False,False)
                    by_method[m][classify(c,False)]+=1
    return {"cases":n,"methods":{m:dict(sorted(c.items())) for m,c in by_method.items()}}

def audit_c(depth):
    by_method={m:Counter() for m in METHODS}; n=0
    preserve_deltas=[d for d in range(1,16) if role_preserving(d)]
    harmful_deltas=[d for d in range(1,16) if not role_preserving(d)]
    for cell in range(BLOCKS):
        for base in range(16):
            for d1 in preserve_deltas:
                mid=base^d1
                for d2 in harmful_deltas:
                    n+=1
                    for m in METHODS:
                        v1=fp(d1,depth)!=0
                        c1=method_commit(m,v1,True,True,True)
                        by_method[m]["BENIGN_FIRST_COMMIT" if c1 else "BENIGN_FIRST_NO_COMMIT"]+=1
                        v2=fp(d2,depth)!=0
                        c2=method_commit(m,v2,True,False,False)
                        by_method[m]["HARMFUL_SECOND_POISON" if c2 else "HARMFUL_SECOND_REJECTED"]+=1
    return {"cases":n,"methods":{m:dict(sorted(c.items())) for m,c in by_method.items()}}

def audit_d(depth):
    first_delta=min(d for d in range(1,16) if role_preserving(d))
    visible=fp(first_delta,depth)!=0
    coalitions=list(itertools.combinations(range(BLOCKS),2))+list(itertools.combinations(range(BLOCKS),3))+[tuple(range(BLOCKS))]
    rows=[]; total_changed=0; commits=0; unchanged_commits=0
    for co in coalitions:
        eligible=0; committed=0
        for c in range(BLOCKS):
            changed=c in co
            if changed:
                total_changed+=1
                if visible: eligible+=1
                if method_commit("INDEPENDENT_QUORUM",visible,True,True,True): committed+=1; commits+=1
            else:
                if method_commit("INDEPENDENT_QUORUM",False,True,True,True): unchanged_commits+=1
        rows.append({"coalition":co,"changed":len(co),"eligible_visible":eligible,"committed":committed})
    return {"coalitions":len(coalitions),"first_role_preserving_delta":first_delta,"fp_delta":fp(first_delta,depth),
            "total_changed_cells":total_changed,"eligible_visible_changed":sum(r["eligible_visible"] for r in rows),
            "committed":commits,"unchanged_commits":unchanged_commits,"rows":rows[:10]}

def audit_e(depth):
    preserve=[d for d in range(1,16) if role_preserving(d)]
    out={"E1_A_UNAVAILABLE":0,"E2_B_UNAVAILABLE":0,"E3_DISAGREE":0}; cases=0
    for cell in range(BLOCKS):
        for base in range(16):
            for d in preserve:
                cases+=1; visible=fp(d,depth)!=0
                if method_commit("INDEPENDENT_QUORUM",visible,True,False,True): out["E1_A_UNAVAILABLE"]+=1
                if method_commit("INDEPENDENT_QUORUM",visible,True,True,False): out["E2_B_UNAVAILABLE"]+=1
                if method_commit("INDEPENDENT_QUORUM",visible,True,True,False): out["E3_DISAGREE"]+=1
    return {"cases_per_condition":cases,"commits":out}

def correlated(depth):
    f1_poison=0; f1_cases=0; f2_alias=0; f2_cases=0; f3_poison=0
    for cell in range(BLOCKS):
        for base in range(16):
            for d in range(1,16):
                if role_preserving(d): continue
                f1_cases+=1; visible=fp(d,depth)!=0
                if method_commit("INDEPENDENT_QUORUM",visible,True,True,True): f1_poison+=1
                if not visible: f2_alias+=1
                f2_cases+=1
                if method_commit("INDEPENDENT_QUORUM",visible,True,True,False): f3_poison+=1
    return {"F1_peer_forgery_cases":f1_cases,"F1_poison_commits":f1_poison,
            "F2_role_change_cases":f2_cases,"F2_harmful_alias_misses":f2_alias,
            "F3_one_peer_forged_poison_commits":f3_poison}

def signals(depth,a,b,c,d,e,corr):
    q=a["methods"]["INDEPENDENT_QUORUM"]
    benign_ok=q.get("MISSED_BENIGN_REFRESH",0)==0
    poison_ok=q.get("POISON_COMMIT",0)==0
    alias_free=a["harmful_aliases"]==0
    stale=b["methods"]["INDEPENDENT_QUORUM"].get("POISON_COMMIT",0)==0
    slow=c["methods"]["INDEPENDENT_QUORUM"].get("HARMFUL_SECOND_POISON",0)==0
    coord=(d["committed"]==d["eligible_visible_changed"] and d["unchanged_commits"]==0)
    degr=all(v==0 for v in e["commits"].values())
    safe=all((benign_ok,poison_ok,stale,slow,coord,degr))
    return {
        "BENIGN_REFRESH_PRESERVED":benign_ok,
        "HARMFUL_POISON_REJECTED":poison_ok,
        "HARMFUL_ALIAS_FREE":alias_free,
        "STALE_DAMAGE_REJECTED":stale,
        "SLOW_DRIFT_POISON_REJECTED":slow,
        "COORDINATED_BENIGN_REFRESH":coord,
        "DEGRADED_PROVENANCE_ABSTAINS":degr,
        "SAFE_HEALTH_MEMORY_COMMIT":safe,
        "CORRELATED_PEER_FORGERY_FAILURE":corr["F1_poison_commits"]>0,
        "HARMFUL_ALIAS_MISS":corr["F2_harmful_alias_misses"]>0,
        "ONE_PEER_FORGERY_SUPPRESSED":corr["F3_one_peer_forged_poison_commits"]==0,
    }

def validate():
    g=static_geometry()
    assert g=={"rank":12,"kernel_count":0,"single_floor":6,"two_floor":8,"global_floor":4,"max_pair_cooccurrence":2,
               "incidences":80,"degree_vector":EXPECTED_DEG}, g
    assert gf2_rank([linear_map(1<<p,ROLE_ROWS,2) for p in range(4)])==2
    assert tuple(gf2_rank([linear_map(1<<p,FP_ROWS,b) for p in range(4)]) for b in DEPTHS)==(2,3,4)
    assert RESOURCE_TOTALS=={2:200,3:212,4:224}
    for c in range(BLOCKS):
        assert peer_a(c)!=c and peer_b(c)!=c and peer_a(c)!=peer_b(c)
    assert DWELL==4
    assert BLOCKS*16*15==2880
    assert len([d for d in range(1,16) if role_preserving(d)])==3
    assert len([d for d in range(1,16) if not role_preserving(d)])==12
    assert math.comb(12,2)+math.comb(12,3)+1==287
    return g

def run():
    g=validate(); out={"schema":"yggdrasil.dg1r-05r-health-memory-commit-drift.v1","mechanical_valid":True,
        "topology_geometry":g,"dwell":DWELL,"resource_totals":{str(k):v for k,v in RESOURCE_TOTALS.items()},"depths":{}}
    for depth in DEPTHS:
        a=audit_a(depth); b=audit_b(depth); c=audit_c(depth); d=audit_d(depth); e=audit_e(depth); corr=correlated(depth)
        out["depths"][f"FP{depth}"]={"audit_a":a,"audit_b":b,"audit_c":c,"audit_d":d,"audit_e":e,
            "correlated_boundary":corr,"signals":signals(depth,a,b,c,d,e,corr)}
    out["canonical_scientific_execution"]=False; out["stab18_r1_touched"]=False
    return out

def enc(o): return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--out"); ap.add_argument("--mechanical-only",action="store_true"); a=ap.parse_args()
    if a.mechanical_only:
        g=validate(); print(enc({"mechanical_valid":True,"geometry":g,"audit_a_count":2880,"dwell":DWELL,"resource_totals":RESOURCE_TOTALS})); return
    if not a.out: raise SystemExit("--out required unless --mechanical-only")
    o=run(); raw=(enc(o)+"\n").encode(); Path(a.out).write_bytes(raw)
    print(enc({"output":a.out,"sha256":hashlib.sha256(raw).hexdigest(),"signals":{k:v["signals"] for k,v in o["depths"].items()}}))
if __name__=="__main__": main()
