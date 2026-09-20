#!/usr/bin/env python3
import argparse, hashlib, json
from pathlib import Path
import numpy as np

WIDTH=128; BLOCKS=12; LOGICAL_BITS=48; POST_STEPS=32; DAMAGE_AFTER_STEPS=1024
WORLD_START=20260926056000; WORLD_COUNT=8; HORIZONS=(1,4,8,16,32)
MIX_RULES=np.asarray([90,150,110,22,30],dtype=np.uint16)
METHODS=("CHAIN_HAMMING_48","SPARSE18_MAJORITY_48","SPARSE20_MAJORITY_48","SPARSE20_DETECT_ONLY")
MAPPED_BLOCKS=np.asarray([1,4,7,10],dtype=np.int64); DATA_OFF=(2,4,5,6)
CYCLE=[(i,(i+1)%12) for i in range(12)]
MATCH=[(i,i+6) for i in range(6)]
EXTRA=[(0,3),(6,9)]
EDGES18=CYCLE+MATCH
EDGES20=EDGES18+EXTRA
EXPECTED={"LOCAL_DATA2_DEG3":2,"LOCAL_DATA2_PLUS_ONE_WITNESS_DEG3":3,"TWO_CORRELATED_WITNESSES_DEG3":2,"LOCAL_DATA2_PLUS_ONE_WITNESS_DEG4":3,"TWO_CORRELATED_WITNESSES_DEG4":2,"DISTRIBUTED_LOCAL_DATA2":4}


def eca_step_mixed(s,r):
    l=np.roll(s,1); rr=np.roll(s,-1); idx=(l<<2)|(s<<1)|rr
    return ((r>>idx)&1).astype(np.uint8)
def mixed_rules(rng,w):
    reps=w//len(MIX_RULES); rem=w%len(MIX_RULES)
    a=np.concatenate((np.tile(MIX_RULES,reps),MIX_RULES[:rem])).astype(np.uint16); rng.shuffle(a); return a

def h74_encode4(d):
    d1,d2,d3,d4=[int(x) for x in d]; o=np.empty(7,dtype=np.uint8)
    o[0]=d1^d2^d4; o[1]=d1^d3^d4; o[2]=d1; o[3]=d2^d3^d4; o[4]=d2; o[5]=d3; o[6]=d4
    return o
def h74_decode7(c):return c[[2,4,5,6]].copy()
def syndrome7(c):return int(c[0]^c[2]^c[4]^c[6])+2*int(c[1]^c[2]^c[5]^c[6])+4*int(c[3]^c[4]^c[5]^c[6])
def mapped_logical(rng):
    offs=rng.integers(0,4,size=len(MAPPED_BLOCKS),dtype=np.int64)
    return np.asarray([int(b*4+o) for b,o in zip(MAPPED_BLOCKS,offs)],dtype=np.int64)

def chain_edge_idx(a,b):
    if abs(a-b)==1:return min(a,b)
    if {a,b}=={0,11}:return 11
    raise KeyError((a,b))
def chain_check_pos(a,b,k):return 84+chain_edge_idx(a,b)*4+k
def sparse_edge_index(edges,a,b):
    for i,(u,v) in enumerate(edges):
        if {u,v}=={a,b}:return i
    raise KeyError((a,b))
def sparse_check_pos(edges,a,b,k):return 48+sparse_edge_index(edges,a,b)*4+k

def encode_chain(logical):
    out=np.zeros(WIDTH,dtype=np.uint8)
    for b in range(BLOCKS):out[b*7:b*7+7]=h74_encode4(logical[b*4:(b+1)*4])
    for i in range(11):out[84+i*4:84+(i+1)*4]=logical[i*4:(i+1)*4]^logical[(i+1)*4:(i+2)*4]
    return out
def decode_chain(state):
    x=np.empty(LOGICAL_BITS,dtype=np.uint8)
    for b in range(BLOCKS):x[b*4:(b+1)*4]=h74_decode7(state[b*7:b*7+7])
    return x

def encode_sparse(logical,edges):
    out=np.zeros(WIDTH,dtype=np.uint8); out[:48]=logical
    for i,(a,b) in enumerate(edges):out[48+i*4:48+(i+1)*4]=logical[a*4:(a+1)*4]^logical[b*4:(b+1)*4]
    return out
def decode_sparse(state):return state[:48].copy()

def init_tel():return {"repairs":0,"false_repairs":0,"abstentions":0,"vote2":0,"vote3":0,"vote4":0,"syndrome_positive":0}

def repair_chain(state,ref,tel):
    d=decode_chain(state); cross=state[84:].copy()
    for b in range(1,11):
        syn=syndrome7(state[b*7:b*7+7])
        if not syn:continue
        tel["syndrome_positive"]+=1
        left=d[(b-1)*4:b*4]^cross[(b-1)*4:b*4]
        right=d[(b+1)*4:(b+2)*4]^cross[b*4:(b+1)*4]
        if not np.array_equal(left,right):tel["abstentions"]+=1;continue
        cur=d[b*4:(b+1)*4]
        if np.array_equal(cur,left):continue
        if ref is not None and not np.array_equal(left,ref[b*4:(b+1)*4]):tel["false_repairs"]+=1
        state[b*7:b*7+7]=h74_encode4(left);tel["repairs"]+=1;tel["vote2"]+=1

def sparse_candidates(state,edges,b):
    d=decode_sparse(state); out=[]
    for i,(u,v) in enumerate(edges):
        if u==b:
            out.append(d[v*4:(v+1)*4]^state[48+i*4:48+(i+1)*4])
        elif v==b:
            out.append(d[u*4:(u+1)*4]^state[48+i*4:48+(i+1)*4])
    return out
def groups(cands):
    gs=[]
    for c in cands:
        for g in gs:
            if np.array_equal(c,g[0]):g[1]+=1;break
        else:gs.append([c.copy(),1])
    gs.sort(key=lambda z:z[1],reverse=True);return gs

def repair_sparse(state,edges,detect_only,ref,tel):
    d=decode_sparse(state)
    for b in range(BLOCKS):
        c=sparse_candidates(state,edges,b);g=groups(c);best=g[0];degree=len(c);need=degree//2+1
        if best[1]<need:
            tel["abstentions"]+=1;continue
        proposal=best[0];cur=d[b*4:(b+1)*4]
        if detect_only or np.array_equal(cur,proposal):continue
        if ref is not None and not np.array_equal(proposal,ref[b*4:(b+1)*4]):tel["false_repairs"]+=1
        state[b*4:(b+1)*4]=proposal;tel["repairs"]+=1
        if best[1]==2:tel["vote2"]+=1
        elif best[1]==3:tel["vote3"]+=1
        elif best[1]>=4:tel["vote4"]+=1

def representation(method):
    if method=="CHAIN_HAMMING_48":return "chain",None
    if method=="SPARSE18_MAJORITY_48":return "sparse",EDGES18
    return "sparse",EDGES20

def decode_state(state,method):
    kind,edges=representation(method);return decode_chain(state) if kind=="chain" else decode_sparse(state)
def encode_state(logical,method):
    kind,edges=representation(method);return encode_chain(logical) if kind=="chain" else encode_sparse(logical,edges)
def repair(state,method,ref,tel):
    kind,edges=representation(method)
    if kind=="chain":repair_chain(state,ref,tel)
    else:repair_sparse(state,edges,method=="SPARSE20_DETECT_ONLY",ref,tel)
def step(state,bit,mapped,rules,method,ref=None,tel=None):
    if tel is None:tel=init_tel()
    repair(state,method,ref,tel);d=decode_state(state,method);d[mapped]=np.uint8(bit);d=eca_step_mixed(d,rules);state[:]=encode_state(d,method);return tel
def prefix(u,mapped,rules,method):
    s=encode_state(np.zeros(LOGICAL_BITS,dtype=np.uint8),method)
    for t in range(DAMAGE_AFTER_STEPS):step(s,int(u[t]),mapped,rules,method)
    return s
def mapped_phys(mapped,method):
    if method=="CHAIN_HAMMING_48":return np.asarray([int((lp//4)*7+DATA_OFF[lp%4]) for lp in mapped],dtype=np.int64)
    return mapped.copy()

def witness_pos(method,a,b,k):
    if method=="CHAIN_HAMMING_48":return chain_check_pos(a,b,k)
    edges=EDGES18 if method=="SPARSE18_MAJORITY_48" else EDGES20
    return sparse_check_pos(edges,a,b,k)
def data_pos(method,b,k):
    return b*7+DATA_OFF[k] if method=="CHAIN_HAMMING_48" else b*4+k

def lesion_scenarios(method):
    out=[]
    out.append(("LOCAL_DATA2_DEG3",(data_pos(method,2,0),data_pos(method,2,1))))
    out.append(("LOCAL_DATA2_PLUS_ONE_WITNESS_DEG3",(data_pos(method,2,0),data_pos(method,2,1),witness_pos(method,1,2,0))))
    out.append(("TWO_CORRELATED_WITNESSES_DEG3",(witness_pos(method,1,2,0),witness_pos(method,2,3,0))))
    out.append(("LOCAL_DATA2_PLUS_ONE_WITNESS_DEG4",(data_pos(method,3,0),data_pos(method,3,1),witness_pos(method,2,3,0))))
    out.append(("TWO_CORRELATED_WITNESSES_DEG4",(witness_pos(method,2,3,0),witness_pos(method,3,4,0))))
    out.append(("DISTRIBUTED_LOCAL_DATA2",(data_pos(method,2,0),data_pos(method,2,1),data_pos(method,8,0),data_pos(method,8,1))))
    return out

def no_damage(pre,future,mapped,rules,method):
    a=pre.copy();b=pre.copy()
    for bit in future:
        ra=decode_state(a,method).copy();rb=decode_state(b,method).copy();step(a,int(bit),mapped,rules,method,ref=ra);step(b,int(bit),mapped,rules,method,ref=rb)
        if np.any(a!=b):return False
    return True

def one_scenario(pre,future,mapped,rules,method,fam,inds,mp):
    inds=np.asarray(inds,dtype=np.int64);assert len(inds)==EXPECTED[fam];assert len(np.unique(inds))==EXPECTED[fam];assert not np.any(np.isin(inds,mp))
    ref=pre.copy();dmg=pre.copy();dmg[inds]^=1;telr=init_tel();teld=init_tel();pc=[];lc=[];flags=[];hm={}
    for h,bit in enumerate(future,start=1):
        rlog=decode_state(ref,method).copy();step(ref,int(bit),mapped,rules,method,ref=None,tel=telr);step(dmg,int(bit),mapped,rules,method,ref=rlog,tel=teld)
        pd=dmg!=ref;ld=decode_state(dmg,method)!=decode_state(ref,method);p=float(np.mean(pd));l=float(np.mean(ld));exact=bool(not np.any(ld));pc.append(p);lc.append(l);flags.append(exact)
        if h in HORIZONS:hm[f"h{h}"]={"physical_divergence":p,"logical_divergence":l,"exact_logical_match":exact}
    rt=None
    for h in range(1,POST_STEPS+1):
        if all(flags[h-1:]):rt=h;break
    delta={k:int(teld[k]-telr[k]) for k in telr}
    return {"family":fam,"lesion_indices":[int(x) for x in inds],"actual_lesion_cardinality":int(len(inds)),"horizons":hm,"physical_divergence_area":float(np.sum(pc)),"logical_divergence_area":float(np.sum(lc)),"sustained_exact_logical_recovery":bool(rt is not None),"logical_recovery_time":rt,"repair_delta":delta}
def one_world(seed):
    rng=np.random.default_rng(np.random.PCG64(seed));u=rng.integers(0,2,size=DAMAGE_AFTER_STEPS+POST_STEPS,dtype=np.uint8);mapped=mapped_logical(rng);rules=mixed_rules(rng,LOGICAL_BITS);future=u[DAMAGE_AFTER_STEPS:];methods={}
    for m in METHODS:
        pre=prefix(u,mapped,rules,m);mp=mapped_phys(mapped,m);ctl=no_damage(pre,future,mapped,rules,m);sc=[one_scenario(pre,future,mapped,rules,m,f,i,mp) for f,i in lesion_scenarios(m)];methods[m]={"no_damage_control":bool(ctl),"scenarios":sc}
    return {"seed":int(seed),"mapped_logical":[int(x) for x in mapped],"methods":methods}
def q(v,p):return float(np.quantile(np.asarray(v,dtype=np.float64),p))
def fr(rows,m,f):return [s for r in rows for s in r["methods"][m]["scenarios"] if s["family"]==f]
def sf(scs):
    o={"scenario_count":len(scs),"horizons":{}}
    for h in HORIZONS:
        k=f"h{h}";o["horizons"][k]={"logical_divergence_median":q([s["horizons"][k]["logical_divergence"] for s in scs],.5),"physical_divergence_median":q([s["horizons"][k]["physical_divergence"] for s in scs],.5),"exact_logical_match_rate":float(np.mean([s["horizons"][k]["exact_logical_match"] for s in scs]))}
    o["logical_divergence_area_median"]=q([s["logical_divergence_area"] for s in scs],.5);o["physical_divergence_area_median"]=q([s["physical_divergence_area"] for s in scs],.5);o["sustained_exact_logical_recovery_rate"]=float(np.mean([s["sustained_exact_logical_recovery"] for s in scs]))
    for key in ("repairs","false_repairs","abstentions","vote2","vote3","vote4","syndrome_positive"):
        vals=[s["repair_delta"][key] for s in scs];o[key+"_sum"]=int(np.sum(vals));o[key+"_median"]=q(vals,.5)
    o["false_repair_fraction"]=float(o["false_repairs_sum"]/o["repairs_sum"]) if o["repairs_sum"] else 0.0
    return o
def summarize(rows):
    valid=all(r["methods"][m]["no_damage_control"] for r in rows for m in METHODS);o={"worlds":len(rows),"mechanical_valid":bool(valid),"methods":{}}
    fams=tuple(EXPECTED)
    for m in METHODS:o["methods"][m]={f:sf(fr(rows,m,f)) for f in fams}
    s20=o["methods"]["SPARSE20_MAJORITY_48"]
    x=s20["LOCAL_DATA2_PLUS_ONE_WITNESS_DEG4"];eff=(x["horizons"]["h1"]["logical_divergence_median"]==0 and x["sustained_exact_logical_recovery_rate"]>=.9 and x["false_repair_fraction"]<=.01 and x["logical_divergence_area_median"]==0)
    y=s20["TWO_CORRELATED_WITNESSES_DEG4"];safe=(y["false_repairs_sum"]==0 and y["horizons"]["h4"]["logical_divergence_median"]==0)
    b18=o["methods"]["SPARSE18_MAJORITY_48"]["TWO_CORRELATED_WITNESSES_DEG3"]["false_repair_fraction"]>.10
    b20=o["methods"]["SPARSE20_MAJORITY_48"]["TWO_CORRELATED_WITNESSES_DEG3"]["false_repair_fraction"]>.10
    dist=s20["DISTRIBUTED_LOCAL_DATA2"];dist_sig=(dist["horizons"]["h4"]["logical_divergence_median"]==0 and dist["sustained_exact_logical_recovery_rate"]>=.75)
    chain=o["methods"]["CHAIN_HAMMING_48"]
    alloc=(eff and chain["LOCAL_DATA2_PLUS_ONE_WITNESS_DEG4"]["logical_divergence_area_median"]>x["logical_divergence_area_median"] and s20["LOCAL_DATA2_DEG3"]["logical_divergence_area_median"]<=chain["LOCAL_DATA2_DEG3"]["logical_divergence_area_median"])
    o["sparse_capacity_efficiency_signal"]=bool(eff);o["degree4_two_fault_safety"]=bool(safe);o["degree3_boundary_methods"]=[m for m,b in (("SPARSE18_MAJORITY_48",b18),("SPARSE20_MAJORITY_48",b20)) if b];o["allocation_advantage"]=bool(alloc);o["distributed_sparse_repair_signal"]=bool(dist_sig)
    o["efficiency"]={"CHAIN_HAMMING_48":{"logical_bits":48,"redundancy_bits":80},"SPARSE18_MAJORITY_48":{"logical_bits":48,"active_redundancy_bits":72,"inert_bits":8},"SPARSE20_MAJORITY_48":{"logical_bits":48,"redundancy_bits":80},"DG1R05E_REFERENCE":{"logical_bits":32,"redundancy_bits":96}}
    return o
def encode_json(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def run():
    rows=[one_world(WORLD_START+i) for i in range(WORLD_COUNT)];return {"schema":"yggdrasil.dg1r-05f-sparse-integrity-efficiency.v1","rows":rows,"summary":summarize(rows),"worlds":len(rows),"seed_start":WORLD_START,"seed_end":WORLD_START+WORLD_COUNT-1}
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--out",required=True);a=ap.parse_args();obj=run();raw=(encode_json(obj)+"\n").encode();Path(a.out).write_bytes(raw);print(encode_json({"output":a.out,"sha256":hashlib.sha256(raw).hexdigest(),"summary":obj["summary"],"worlds":obj["worlds"]}))
if __name__=="__main__":main()