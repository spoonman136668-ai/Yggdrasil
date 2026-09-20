#!/usr/bin/env python3
import argparse, hashlib, itertools, json, math
from collections import Counter
from pathlib import Path

BLOCKS=12; CHECKS=20; KMAX=6
EDGES=(
(0,2,7,9),(1,3,6,11),(4,5,9,10,11),(2,3,5),(0,1,4,8),
(6,7,8,10),(2,4,6),(0,3,5,6,7),(1,7,10,11),(1,5,6,9),
(3,8,9,10),(0,4,8,11),(0,2,6,10),(1,3,4,7),(2,5,7,8,11),
(2,3,4,10),(0,1,5,10),(0,3,9,11),(1,2,8,9),(4,7,9),
)
EXPECTED_DEG=(7,7,7,7,7,6,6,7,6,7,7,6)
FP_ROWS=((1,1,1,1),(0,1,0,1),(0,0,1,1),(0,0,0,1))
METHODS=("COORD6_SYNDROME_ONLY","FP1_CONSENSUS","FP2_CONSENSUS","FP3_CONSENSUS","FP4_CONSENSUS")
CHALLENGES={
"BASE_WEAK4_MASK1106":(1,4,6,10),
"DIST3_WEAK5_MASK2243":(0,1,6,7,11),
"DIST4_MIN6_MASK249":(0,3,4,5,6,7),
}
RESOURCE_TOTALS={0:128,1:140,2:152,3:164,4:176}

def columns():
    out=[0]*BLOCKS
    for i,e in enumerate(EDGES):
        for b in e: out[b]|=1<<i
    return tuple(out)
COLS=columns()

def syndrome(mask):
    s=0
    while mask:
        l=mask & -mask; b=l.bit_length()-1; s ^= COLS[b]; mask ^= l
    return s

CODE_SYNS=tuple(syndrome(m) for m in range(1<<BLOCKS))
CANDS=tuple(
    (m.bit_count(),m,CODE_SYNS[m])
    for m in range(1,1<<BLOCKS) if m.bit_count()<=KMAX
)

def candidate_list(obs_syn):
    base=obs_syn.bit_count(); arr=[]
    for w,m,cs in CANDS:
        after=(obs_syn^cs).bit_count()
        if after<base: arr.append((w,base-after,m,after))
    arr.sort(key=lambda x:(x[0],-x[1],x[2]))
    return arr

CAND_CACHE={}
def candidates(obs_syn):
    if obs_syn not in CAND_CACHE: CAND_CACHE[obs_syn]=candidate_list(obs_syn)
    return CAND_CACHE[obs_syn]

def fp_rank(b):
    rows=[]
    for r in FP_ROWS[:b]:
        x=sum((bit&1)<<i for i,bit in enumerate(r))
        rows.append(x)
    basis={}
    for v in rows:
        while v:
            p=v.bit_length()-1
            if p in basis: v ^= basis[p]
            else: basis[p]=v; break
    return len(basis)

def fp_delta(plane_mask,b):
    out=0
    for i,row in enumerate(FP_ROWS[:b]):
        parity=0
        for p in range(4):
            if (plane_mask>>p)&1: parity ^= row[p]
        out |= parity<<i
    return out

def obs_fp_for_logical(block_plane_masks,b):
    return tuple(fp_delta(block_plane_masks.get(block,0),b) for block in range(BLOCKS))

def proposal_fp(proposals,b):
    per=[0]*BLOCKS
    for p,m in proposals.items():
        for block in range(BLOCKS):
            if (m>>block)&1: per[block] ^= 1<<p
    return tuple(fp_delta(per[block],b) for block in range(BLOCKS))

def compatible(proposals,obs,b):
    pred=proposal_fp(proposals,b)
    for block in range(BLOCKS):
        touched=any((m>>block)&1 for m in proposals.values())
        if touched and obs[block]==0: return False
        if pred[block] != obs[block]: return False
    return True

def coord6_single(obs_syn):
    xs=candidates(obs_syn)
    return xs[0] if xs else None

def fp_single(obs_syn,plane,obs,b):
    for row in candidates(obs_syn):
        m=row[2]
        if compatible({plane:m},obs,b): return row
    return None

def fp_multiplane(syn_by_plane,obs,b):
    planes=tuple(sorted(p for p,s in syn_by_plane.items() if s))
    if not planes:
        return {}
    lists=[]
    for p in planes:
        allowed=0
        for block,v in enumerate(obs):
            if v!=0: allowed |= 1<<block
        ls=[r for r in candidates(syn_by_plane[p]) if (r[2] & ~allowed)==0]
        if not ls: return None
        lists.append((p,ls))
    for combo in itertools.product(*(x[1] for x in lists)):
        props={lists[i][0]:combo[i][2] for i in range(len(lists))}
        if compatible(props,obs,b):
            return {"proposals":props,"rows":combo}
    return None

def label_single(candidate_mask,truth_mask):
    if candidate_mask is None: return "ABSTAIN"
    false=bool(candidate_mask & ~truth_mask)
    complete=(candidate_mask==truth_mask)
    if false: return "FALSE_AUTHORIZATION"
    if complete: return "COMPLETE_AUTHORIZATION"
    return "SAFE_PARTIAL_AUTHORIZATION"

def label_multiplane(props,truth):
    if props is None: return "ABSTAIN"
    planes=set(props)|set(truth)
    any_false=False
    for p in planes:
        pm=props.get(p,0); tm=truth.get(p,0)
        if pm & ~tm: any_false=True
    if any_false: return "FALSE_AUTHORIZATION"
    if all(props.get(p,0)==truth.get(p,0) for p in planes): return "COMPLETE_AUTHORIZATION"
    return "SAFE_PARTIAL_AUTHORIZATION"

def static_geometry():
    deg=tuple(sum(b in e for e in EDGES) for b in range(BLOCKS))
    pair=Counter()
    for e in EDGES:
        for a,b in itertools.combinations(e,2): pair[tuple(sorted((a,b)))]+=1
    syns=CODE_SYNS[1:]
    basis={}
    for v in COLS:
        x=v
        while x:
            p=x.bit_length()-1
            if p in basis: x ^= basis[p]
            else: basis[p]=x; break
    return {
        "rank":len(basis),"kernel_count":(1<<(BLOCKS-len(basis)))-1,
        "single_floor":min(x.bit_count() for x in COLS),
        "two_floor":min((COLS[a]^COLS[b]).bit_count() for a,b in itertools.combinations(range(BLOCKS),2)),
        "global_floor":min(x.bit_count() for x in syns if x),
        "max_pair_cooccurrence":max(pair.values()),"incidences":sum(len(e) for e in EDGES),"degree_vector":deg,
    }

def audit_a():
    out={m:Counter() for m in METHODS}; sizes={m:Counter() for m in METHODS}
    for plane in range(4):
        for truth in range(1,1<<BLOCKS):
            syn=CODE_SYNS[truth]; c=coord6_single(syn); cm=None if c is None else c[2]
            lab=label_single(cm,truth); out["COORD6_SYNDROME_ONLY"][lab]+=1
            if cm is not None: sizes["COORD6_SYNDROME_ONLY"][cm.bit_count()]+=1
            block_masks={b:(1<<plane) for b in range(BLOCKS) if (truth>>b)&1}
            for b in range(1,5):
                obs=obs_fp_for_logical(block_masks,b); c=fp_single(syn,plane,obs,b); cm=None if c is None else c[2]
                method=f"FP{b}_CONSENSUS"; lab=label_single(cm,truth); out[method][lab]+=1
                if cm is not None: sizes[method][cm.bit_count()]+=1
    return {m:{"labels":dict(sorted(out[m].items())),"candidate_sizes":{str(k):v for k,v in sorted(sizes[m].items())}} for m in METHODS}

def audit_b():
    out={m:Counter() for m in METHODS}; by_w={m:{str(w):Counter() for w in range(1,5)} for m in METHODS}
    for plane in range(4):
        zero_masks={b:obs_fp_for_logical({},b) for b in range(1,5)}
        for w in range(1,5):
            for slots in itertools.combinations(range(CHECKS),w):
                syn=sum(1<<i for i in slots); c=coord6_single(syn); cm=None if c is None else c[2]
                lab="ABSTAIN" if cm is None else "FALSE_AUTHORIZATION"
                out["COORD6_SYNDROME_ONLY"][lab]+=1; by_w["COORD6_SYNDROME_ONLY"][str(w)][lab]+=1
                for b in range(1,5):
                    c=fp_single(syn,plane,zero_masks[b],b); cm=None if c is None else c[2]
                    lab="ABSTAIN" if cm is None else "FALSE_AUTHORIZATION"; method=f"FP{b}_CONSENSUS"
                    out[method][lab]+=1; by_w[method][str(w)][lab]+=1
    return {m:{"labels":dict(sorted(out[m].items())),"by_weight":{w:dict(sorted(c.items())) for w,c in by_w[m].items()}} for m in METHODS}

def audit_c():
    out={m:Counter() for m in METHODS}; details=[]
    for fam,blocks in CHALLENGES.items():
        truth=sum(1<<b for b in blocks); syn=CODE_SYNS[truth]
        for plane in range(4):
            c=coord6_single(syn); cm=None if c is None else c[2]; lab=label_single(cm,truth); out["COORD6_SYNDROME_ONLY"][lab]+=1
            row={"family":fam,"plane":plane,"truth_mask":truth,"syndrome_weight":syn.bit_count(),"methods":{"COORD6_SYNDROME_ONLY":{"label":lab,"proposal_mask":cm}}}
            block_masks={b:(1<<plane) for b in blocks}
            for b in range(1,5):
                obs=obs_fp_for_logical(block_masks,b); c=fp_single(syn,plane,obs,b); cm=None if c is None else c[2]
                method=f"FP{b}_CONSENSUS"; lab=label_single(cm,truth); out[method][lab]+=1
                row["methods"][method]={"label":lab,"proposal_mask":cm}
            details.append(row)
    return {"summary":{m:dict(sorted(c.items())) for m,c in out.items()},"rows":details}

def audit_d():
    strata={m:{str(w):Counter() for w in range(1,5)} for m in METHODS}
    for block in range(BLOCKS):
        bm=1<<block
        for pmask in range(1,16):
            truth={p:bm for p in range(4) if (pmask>>p)&1}; syns={p:COLS[block] for p in truth}
            props={}
            for p,syn in syns.items():
                c=coord6_single(syn)
                if c is not None: props[p]=c[2]
            lab=label_multiplane(props if props else None,truth); strata["COORD6_SYNDROME_ONLY"][str(pmask.bit_count())][lab]+=1
            block_masks={block:pmask}
            for b in range(1,5):
                obs=obs_fp_for_logical(block_masks,b); res=fp_multiplane(syns,obs,b); pmap=None if res is None else res["proposals"]
                lab=label_multiplane(pmap,truth); strata[f"FP{b}_CONSENSUS"][str(pmask.bit_count())][lab]+=1
    return {m:{w:dict(sorted(c.items())) for w,c in d.items()} for m,d in strata.items()}

def incident(block): return [i for i,e in enumerate(EDGES) if block in e]

def audit_e():
    out={m:Counter() for m in METHODS}; rows=[]
    for block in range(BLOCKS):
        bm=1<<block; inc=incident(block)[:4]; check_syn=sum(1<<i for i in inc)
        for a in range(4):
            for bplane in range(4):
                if bplane==a: continue
                truth={a:bm}; syns={a:COLS[block],bplane:check_syn}; props={}
                for p,syn in syns.items():
                    c=coord6_single(syn)
                    if c is not None: props[p]=c[2]
                lab=label_multiplane(props if props else None,truth); false_b=bool(props.get(bplane,0)) if props else False
                out["COORD6_SYNDROME_ONLY"]["FALSE_PLANE_B" if false_b else "PLANE_B_SUPPRESSED"]+=1
                row={"block":block,"true_plane":a,"false_plane":bplane,"methods":{"COORD6_SYNDROME_ONLY":{"label":lab,"false_plane_authorized":false_b}}}
                block_masks={block:1<<a}
                for depth in range(1,5):
                    obs=obs_fp_for_logical(block_masks,depth); res=fp_multiplane(syns,obs,depth); pmap=None if res is None else res["proposals"]
                    false_b=bool(pmap and pmap.get(bplane,0)); method=f"FP{depth}_CONSENSUS"
                    out[method]["FALSE_PLANE_B" if false_b else "PLANE_B_SUPPRESSED"]+=1
                    row["methods"][method]={"label":label_multiplane(pmap,truth),"false_plane_authorized":false_b}
                rows.append(row)
    return {"summary":{m:dict(sorted(c.items())) for m,c in out.items()},"rows":rows}

def correlated_holdout():
    f1={f"FP{b}_CONSENSUS":Counter() for b in range(1,5)}
    for block in range(BLOCKS):
        syn=COLS[block]
        for plane in range(4):
            for depth in range(1,5):
                c=fp_single(syn,plane,(0,)*BLOCKS,depth); lab=label_single(None if c is None else c[2],1<<block)
                f1[f"FP{depth}_CONSENSUS"][lab]+=1
    f2={f"FP{b}_CONSENSUS":Counter() for b in range(1,5)}; examples=[]
    for w in range(1,5):
        for slots in itertools.combinations(range(CHECKS),w):
            syn=sum(1<<i for i in slots); base=coord6_single(syn)
            if base is None: continue
            cm=base[2]; plane=0
            for depth in range(1,5):
                obs=[0]*BLOCKS; val=fp_delta(1<<plane,depth)
                for block in range(BLOCKS):
                    if (cm>>block)&1: obs[block]=val
                c=fp_single(syn,plane,tuple(obs),depth); lab="ABSTAIN" if c is None else "FALSE_AUTHORIZATION"
                f2[f"FP{depth}_CONSENSUS"][lab]+=1
            if len(examples)<5: examples.append({"weight":w,"checks":slots,"coord6_mask":cm})
    return {"F1_LOGICAL_PLUS_FINGERPRINT_ERASURE":{m:dict(sorted(c.items())) for m,c in f1.items()},
        "F2_CHECK_ONLY_PLUS_FALSE_FINGERPRINT_SUPPORT":{m:dict(sorted(c.items())) for m,c in f2.items()},"F2_examples":examples}

def signals(a,b,c,d,e,corr):
    out={}
    for depth in range(1,5):
        m=f"FP{depth}_CONSENSUS"; spec=b[m]["labels"].get("FALSE_AUTHORIZATION",0)==0
        chall=(c["summary"][m].get("COMPLETE_AUTHORIZATION",0)==12 and c["summary"][m].get("FALSE_AUTHORIZATION",0)==0)
        alias=e["summary"][m].get("FALSE_PLANE_B",0)==0
        false_primary=a[m]["labels"].get("FALSE_AUTHORIZATION",0)+b[m]["labels"].get("FALSE_AUTHORIZATION",0)+c["summary"][m].get("FALSE_AUTHORIZATION",0)
        false_primary += sum(d[m][str(w)].get("FALSE_AUTHORIZATION",0) for w in range(1,5))
        f1bad=corr["F1_LOGICAL_PLUS_FINGERPRINT_ERASURE"][m].get("COMPLETE_AUTHORIZATION",0)<48
        f2bad=corr["F2_CHECK_ONLY_PLUS_FALSE_FINGERPRINT_SUPPORT"][m].get("FALSE_AUTHORIZATION",0)>0
        out[m]={"INDEPENDENT_CHECK_ONLY_SPECIFICITY":bool(spec),"CHALLENGE_COORDINATION_RECOVERY":bool(chall),
            "PLANE_ALIAS_SUPPRESSION":bool(alias),"SINGLE_PLANE_CELL_HEALTH":d[m]["1"].get("COMPLETE_AUTHORIZATION",0)==48,
            "TWO_PLANE_CELL_HEALTH":d[m]["2"].get("COMPLETE_AUTHORIZATION",0)==72,
            "THREE_PLANE_CELL_HEALTH":d[m]["3"].get("COMPLETE_AUTHORIZATION",0)==48,
            "FOUR_PLANE_CELL_HEALTH":d[m]["4"].get("COMPLETE_AUTHORIZATION",0)==12,
            "ZERO_FALSE_AUTH_PRIMARY_A_TO_E":false_primary==0 and alias,
            "INDEPENDENT_CONSENSUS_GAIN":bool(spec and chall and alias and false_primary==0),
            "CORRELATED_FORGERY_FAILURE":bool(f1bad or f2bad)}
    return out

def validate():
    g=static_geometry()
    assert g=={"rank":12,"kernel_count":0,"single_floor":6,"two_floor":8,"global_floor":4,"max_pair_cooccurrence":2,"incidences":80,"degree_vector":EXPECTED_DEG}
    assert tuple(fp_rank(b) for b in range(1,5))==(1,2,3,4)
    assert RESOURCE_TOTALS=={0:128,1:140,2:152,3:164,4:176}
    assert sum(math.comb(BLOCKS,k) for k in range(1,KMAX+1))==2509
    assert 4*((1<<BLOCKS)-1)==16380
    assert 4*sum(math.comb(CHECKS,w) for w in range(1,5))==24780
    assert len(CHALLENGES)*4==12
    assert BLOCKS*((1<<4)-1)==180
    assert BLOCKS*4*3==144

def run():
    validate(); a=audit_a(); b=audit_b(); c=audit_c(); d=audit_d(); e=audit_e(); corr=correlated_holdout()
    return {"schema":"yggdrasil.dg1r-05p-independent-self-health-consensus.v1","mechanical_valid":True,
        "topology_geometry":static_geometry(),"fingerprint_ranks":{f"FP{x}":fp_rank(x) for x in range(1,5)},
        "resource_totals":RESOURCE_TOTALS,"case_counts":{"audit_a":16380,"audit_b":24780,"audit_c":12,"audit_d":180,"audit_e":144},
        "audit_a_single_plane_logical":a,"audit_b_check_only":b,"audit_c_challenges":c,"audit_d_intra_cell_multiplane":d,
        "audit_e_cross_plane_alias":e,"correlated_forgery_boundary":corr,"signals":signals(a,b,c,d,e,corr),
        "canonical_scientific_execution":False,"stab18_r1_touched":False}

def enc(o): return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--out",required=True); a=ap.parse_args()
    obj=run(); raw=(enc(obj)+"\n").encode(); Path(a.out).write_bytes(raw)
    print(enc({"output":a.out,"sha256":hashlib.sha256(raw).hexdigest(),"mechanical_valid":obj["mechanical_valid"],"signals":obj["signals"],"case_counts":obj["case_counts"]}))
if __name__=="__main__": main()
