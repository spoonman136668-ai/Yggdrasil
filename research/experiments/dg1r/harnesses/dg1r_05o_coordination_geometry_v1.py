#!/usr/bin/env python3
import argparse, hashlib, itertools, json
from collections import Counter
from pathlib import Path

BLOCKS=12; CHECKS=20; KMAX=4
TOPOLOGIES={
'HYPER20_BASELINE':(
(0,2,7,9),(1,3,6,11),(4,5,9,10),(2,3,5,8),(0,1,4,8),(6,7,8,10),(2,4,6,11),(0,3,5,7),(1,7,10,11),(1,5,6,9),
(3,8,9,10),(0,4,8,11),(0,2,6,10),(1,3,4,7),(2,5,7,11),(2,3,4,10),(0,1,5,10),(0,3,9,11),(1,2,8,9),(4,6,7,9)),
'DIST3_05L':(
(0,2,7,9),(1,3,6,11),(4,5,9,10),(2,3,5,8),(0,1,4,8),(6,7,8,10),(2,4,6,11),(0,3,5,7),(7,10,11),(1,5,6,9),
(3,8,9,10),(0,4,5,8,11),(0,2,6,10),(1,3,4,7),(1,2,5,7,11),(2,3,4,10),(0,1,10),(0,3,9,11),(1,2,8,9),(4,6,7,9)),
'DIST4_05M':(
(0,2,7,9),(1,3,6,11),(4,5,9,10,11),(2,3,5),(0,1,4,8),(6,7,8,10),(2,4,6),(0,3,5,6,7),(1,7,10,11),(1,5,6,9),
(3,8,9,10),(0,4,8,11),(0,2,6,10),(1,3,4,7),(2,5,7,8,11),(2,3,4,10),(0,1,5,10),(0,3,9,11),(1,2,8,9),(4,7,9)),
}
CHALLENGES={
'BASE_WEAK4_MASK1106':(1,4,6,10),
'DIST3_WEAK5_MASK2243':(0,1,6,7,11),
'DIST4_MIN6_MASK249':(0,3,4,5,6,7),
}

def cols(edges):
    x=[0]*BLOCKS
    for i,e in enumerate(edges):
        for b in e: x[b]|=1<<i
    return tuple(x)

def syns(c):
    s=[0]*(1<<BLOCKS)
    for m in range(1,1<<BLOCKS):
        l=m&-m; b=l.bit_length()-1; s[m]=s[m^l]^c[b]
    return s

def candidates(s):
    out={}
    for k in range(1,KMAX+1):
        arr=[]
        for bs in itertools.combinations(range(BLOCKS),k):
            q=sum(1<<b for b in bs); arr.append((q,s[q],bs))
        out[k]=arr
    return out

def first_descent(mask,s,cands):
    base=s[mask].bit_count()
    if base==0: return {'category':'ZERO_SYNDROME','radius':None,'improving':0,'truth_aligned':0}
    for k in range(1,KMAX+1):
        imp=[]
        for q,qs,bs in cands[k]:
            after=(s[mask]^qs).bit_count()
            if after<base: imp.append((q,bs,base-after,after,(q & ~mask)==0))
        if imp:
            t=sum(x[4] for x in imp)
            cat='FALSE_ONLY_FIRST_DESCENT' if t==0 else ('TRUE_ONLY_FIRST_DESCENT' if t==len(imp) else 'MIXED_FIRST_DESCENT')
            return {'category':cat,'radius':k,'improving':len(imp),'truth_aligned':t}
    return {'category':'NO_DESCENT_LE4','radius':None,'improving':0,'truth_aligned':0}

def first_any_and_true(mask,s):
    base=s[mask].bit_count(); any_hit=None; true_hit=None
    for k in range(1,BLOCKS+1):
        ai=[]; ti=[]
        for bs in itertools.combinations(range(BLOCKS),k):
            q=sum(1<<b for b in bs); after=(s[mask]^s[q]).bit_count(); red=base-after
            if red>0:
                row=(red,bs,after)
                ai.append(row)
                if (q & ~mask)==0: ti.append(row)
        if any_hit is None and ai: any_hit={'radius':k,'count':len(ai),'best':max(ai)}
        if true_hit is None and ti: true_hit={'radius':k,'count':len(ti),'best':max(ti)}
        if any_hit and true_hit: break
    return any_hit,true_hit

def integrity_attraction(s,cands,weight):
    counts=Counter(); radii=Counter(); examples=[]
    for slots in itertools.combinations(range(CHECKS),weight):
        syndrome=sum(1<<i for i in slots); hit=None
        for k in range(1,KMAX+1):
            imp=[]
            for q,qs,bs in cands[k]:
                if (syndrome^qs).bit_count()<weight: imp.append(bs)
            if imp: hit=(k,len(imp),imp[0]); break
        if hit:
            counts['LOGICAL_ATTRACTION']+=1; radii[hit[0]]+=1
            if len(examples)<5: examples.append({'checks':slots,'radius':hit[0],'improving_count':hit[1],'first_candidate':hit[2]})
        else: counts['NO_LOGICAL_DESCENT_LE4']+=1
    return {'patterns':sum(counts.values()),'categories':dict(sorted(counts.items())),'attraction_radii':{str(k):v for k,v in sorted(radii.items())},'examples':examples}

def run():
    out={'schema':'yggdrasil.dg1r-05o-coordination-geometry.v1','status':'EXPLORATORY_DESIGN_ANALYSIS','kmax':KMAX,'topologies':{}}
    for name,edges in TOPOLOGIES.items():
        s=syns(cols(edges)); cands=candidates(s); cats=Counter(); byw={str(w):Counter() for w in range(1,BLOCKS+1)}
        for m in range(1,1<<BLOCKS):
            fd=first_descent(m,s,cands); cats[fd['category']]+=1; byw[str(m.bit_count())][fd['category']]+=1
        ch={}
        for fam,bs in CHALLENGES.items():
            m=sum(1<<b for b in bs); a,t=first_any_and_true(m,s)
            ch[fam]={'logical_blocks':bs,'syndrome_weight':s[m].bit_count(),'first_any_descent':a,'first_truth_aligned_descent':t}
        integ={str(w):integrity_attraction(s,cands,w) for w in range(1,5)}
        out['topologies'][name]={'logical_first_descent_categories':dict(sorted(cats.items())),
            'logical_first_descent_by_fault_weight':{w:dict(sorted(c.items())) for w,c in byw.items()},
            'challenge_geometry':ch,'integrity_only_attraction':integ}
    return out

def enc(o): return json.dumps(o,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out',required=True); a=ap.parse_args(); o=run(); raw=(enc(o)+'\n').encode(); Path(a.out).write_bytes(raw)
    print(enc({'output':a.out,'sha256':hashlib.sha256(raw).hexdigest(),'status':o['status']}))
if __name__=='__main__': main()
