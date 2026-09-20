#!/usr/bin/env python3
import argparse, hashlib, json
from pathlib import Path
import numpy as np

WIDTH=128; BLOCKS=8; LOGICAL_BITS=32; LOCAL_BITS=64; NEAR_BASE=64; SECOND_BASE=96
POST_STEPS=32; DAMAGE_AFTER_STEPS=1024; WORLD_START=20260926055000; WORLD_COUNT=8
HORIZONS=(1,4,8,16,32); MIX_RULES=np.asarray([90,150,110,22,30],dtype=np.uint16)
METHODS=("TWO_WITNESS_NEAREST","QUORUM3_OF_4","QUORUM2_OF_4","QUORUM3_LOCAL_GATE","DETECT_ONLY")
MAPPED_BLOCKS=np.asarray([1,3,5,7],dtype=np.int64); DAMAGE_BLOCKS=(0,2,4,6); DIST_BLOCKS=(0,4)
DATA_OFF=(2,4,5,6)
EXPECTED={"LOCAL_DATA2":2,"LOCAL_SILENT3":3,"LOCAL_DATA2_PLUS_ONE_WITNESS":3,"TWO_CORRELATED_WITNESSES":2,"THREE_CORRELATED_WITNESSES":3,"DISTRIBUTED_LOCAL_DATA2":4}


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
def h74_decode7(c): return c[[2,4,5,6]].copy()
def syndrome7(c): return int(c[0]^c[2]^c[4]^c[6])+2*int(c[1]^c[2]^c[5]^c[6])+4*int(c[3]^c[4]^c[5]^c[6])
def secded_encode4(d):
    c=h74_encode4(d); return np.concatenate((c,np.asarray([np.bitwise_xor.reduce(c)],dtype=np.uint8)))
def secded_decode8(c): return h74_decode7(c[:7])
def local_status(c):
    syn=syndrome7(c[:7]); p=int(np.bitwise_xor.reduce(c))
    if syn==0 and p==0:return "clean"
    if syn!=0 and p==1:return "single_hamming"
    if syn==0 and p==1:return "single_p0"
    return "double_detected"

def mapped_logical(rng):
    offs=rng.integers(0,4,size=len(MAPPED_BLOCKS),dtype=np.int64)
    return np.asarray([int(b*4+o) for b,o in zip(MAPPED_BLOCKS,offs)],dtype=np.int64)
def local_phys_for_logical(lp): return int((lp//4)*8+DATA_OFF[lp%4])
def near_idx(edge,k): return NEAR_BASE+(edge%8)*4+k
def second_idx(edge,k): return SECOND_BASE+(edge%8)*4+k

def encode_state(logical):
    out=np.zeros(WIDTH,dtype=np.uint8)
    for b in range(BLOCKS): out[b*8:b*8+8]=secded_encode4(logical[b*4:(b+1)*4])
    for i in range(BLOCKS):
        out[near_idx(i,0):near_idx(i,0)+4]=logical[i*4:(i+1)*4]^logical[((i+1)%8)*4:((i+1)%8)*4+4]
        out[second_idx(i,0):second_idx(i,0)+4]=logical[i*4:(i+1)*4]^logical[((i+2)%8)*4:((i+2)%8)*4+4]
    return out

def decode_state(state):
    x=np.empty(LOGICAL_BITS,dtype=np.uint8)
    for b in range(BLOCKS):x[b*4:(b+1)*4]=secded_decode8(state[b*8:b*8+8])
    return x

def witness_candidates(state,b):
    d=decode_state(state)
    lm1=(b-1)%8; lp1=(b+1)%8; lm2=(b-2)%8; lp2=(b+2)%8
    L1=d[lm1*4:lm1*4+4]^state[near_idx(lm1,0):near_idx(lm1,0)+4]
    R1=d[lp1*4:lp1*4+4]^state[near_idx(b,0):near_idx(b,0)+4]
    L2=d[lm2*4:lm2*4+4]^state[second_idx(lm2,0):second_idx(lm2,0)+4]
    R2=d[lp2*4:lp2*4+4]^state[second_idx(b,0):second_idx(b,0)+4]
    return (L1,R1,L2,R2)
def candidate_groups(cands):
    groups=[]
    for c in cands:
        found=False
        for g in groups:
            if np.array_equal(c,g[0]):g[1]+=1;found=True;break
        if not found:groups.append([c.copy(),1])
    groups.sort(key=lambda x:x[1],reverse=True);return groups

def init_tel():return {"repairs":0,"false_repairs":0,"abstentions":0,"vote2":0,"vote3":0,"vote4":0,"local_clean":0,"local_nonclean":0}

def repair(state,method,ref_log,tel):
    decoded=decode_state(state)
    for b in range(BLOCKS):
        current=decoded[b*4:(b+1)*4]; status=local_status(state[b*8:b*8+8])
        tel["local_clean" if status=="clean" else "local_nonclean"]+=1
        cands=witness_candidates(state,b); proposal=None; votes=0
        if method=="DETECT_ONLY":continue
        if method=="TWO_WITNESS_NEAREST":
            if np.array_equal(cands[0],cands[1]):proposal=cands[0];votes=2
            else:tel["abstentions"]+=1;continue
        else:
            groups=candidate_groups(cands); best=groups[0]; second=groups[1][1] if len(groups)>1 else 0
            if method in ("QUORUM3_OF_4","QUORUM3_LOCAL_GATE"):
                if best[1]>=3:proposal=best[0];votes=best[1]
                else:tel["abstentions"]+=1;continue
            elif method=="QUORUM2_OF_4":
                if best[1]>=2 and best[1]>second:proposal=best[0];votes=best[1]
                else:tel["abstentions"]+=1;continue
        if proposal is None or np.array_equal(current,proposal):continue
        if votes==2:tel["vote2"]+=1
        elif votes==3:tel["vote3"]+=1
        elif votes==4:tel["vote4"]+=1
        if ref_log is not None and not np.array_equal(proposal,ref_log[b*4:(b+1)*4]):tel["false_repairs"]+=1
        state[b*8:b*8+8]=secded_encode4(proposal);tel["repairs"]+=1

def step(state,bit,mapped,rules,method,ref_log=None,tel=None):
    if tel is None:tel=init_tel()
    repair(state,method,ref_log,tel); logical=decode_state(state); logical[mapped]=np.uint8(bit); logical=eca_step_mixed(logical,rules); state[:]=encode_state(logical);return tel

def prefix(u,mapped,rules,method):
    s=encode_state(np.zeros(LOGICAL_BITS,dtype=np.uint8))
    for t in range(DAMAGE_AFTER_STEPS):step(s,int(u[t]),mapped,rules,method)
    return s

def mapped_phys(mapped):return np.asarray([local_phys_for_logical(int(lp)) for lp in mapped],dtype=np.int64)

def lesion_scenarios():
    out=[]
    for b in DAMAGE_BLOCKS:
        base=b*8
        out.append(("LOCAL_DATA2",(base+2,base+4)))
        out.append(("LOCAL_SILENT3",(base+2,base+4,base+5)))
        out.append(("LOCAL_DATA2_PLUS_ONE_WITNESS",(base+2,base+4,near_idx((b-1)%8,0))))
        out.append(("TWO_CORRELATED_WITNESSES",(near_idx((b-1)%8,0),near_idx(b,0))))
        out.append(("THREE_CORRELATED_WITNESSES",(near_idx((b-1)%8,0),near_idx(b,0),second_idx((b-2)%8,0))))
    inds=[]
    for b in DIST_BLOCKS:inds.extend((b*8+2,b*8+4))
    out.append(("DISTRIBUTED_LOCAL_DATA2",tuple(inds)))
    return out

def no_damage(pre,future,mapped,rules,method):
    a=pre.copy();b=pre.copy()
    for bit in future:
        la=decode_state(a).copy();lb=decode_state(b).copy();step(a,int(bit),mapped,rules,method,ref_log=la);step(b,int(bit),mapped,rules,method,ref_log=lb)
        if np.any(a!=b):return False
    return True

def one_scenario(pre,future,mapped,rules,method,fam,inds,mp):
    inds=np.asarray(inds,dtype=np.int64);assert len(inds)==EXPECTED[fam];assert len(np.unique(inds))==EXPECTED[fam];assert not np.any(np.isin(inds,mp))
    ref=pre.copy();dmg=pre.copy();dmg[inds]^=1;mask=np.zeros(WIDTH,dtype=bool);mask[inds]=True;outside=~mask;telr=init_tel();teld=init_tel();pc=[];lc=[];flags=[];hm={}
    for h,bit in enumerate(future,start=1):
        rlog=decode_state(ref).copy();step(ref,int(bit),mapped,rules,method,ref_log=None,tel=telr);step(dmg,int(bit),mapped,rules,method,ref_log=rlog,tel=teld)
        pd=dmg!=ref;ld=decode_state(dmg)!=decode_state(ref);pdiv=float(np.mean(pd));ldiv=float(np.mean(ld));outdiv=float(np.mean(pd[outside]));exact=bool(not np.any(ld));pc.append(pdiv);lc.append(ldiv);flags.append(exact)
        if h in HORIZONS:hm[f"h{h}"]={"physical_divergence":pdiv,"logical_divergence":ldiv,"outside_lesion_divergence":outdiv,"exact_logical_match":exact}
    rt=None
    for h in range(1,POST_STEPS+1):
        if all(flags[h-1:]):rt=h;break
    delta={k:int(teld[k]-telr[k]) for k in telr}
    return {"family":fam,"lesion_indices":[int(x) for x in inds],"actual_lesion_cardinality":int(len(inds)),"horizons":hm,"physical_divergence_area":float(np.sum(pc)),"logical_divergence_area":float(np.sum(lc)),"sustained_exact_logical_recovery":bool(rt is not None),"logical_recovery_time":rt,"repair_delta":delta}

def one_world(seed):
    rng=np.random.default_rng(np.random.PCG64(seed));u=rng.integers(0,2,size=DAMAGE_AFTER_STEPS+POST_STEPS,dtype=np.uint8);mapped=mapped_logical(rng);rules=mixed_rules(rng,LOGICAL_BITS);future=u[DAMAGE_AFTER_STEPS:];mp=mapped_phys(mapped);methods={}
    for m in METHODS:
        pre=prefix(u,mapped,rules,m);ctl=no_damage(pre,future,mapped,rules,m);sc=[one_scenario(pre,future,mapped,rules,m,f,i,mp) for f,i in lesion_scenarios()];methods[m]={"no_damage_control":bool(ctl),"scenarios":sc}
    return {"seed":int(seed),"mapped_logical":[int(x) for x in mapped],"methods":methods}
def q(v,p):return float(np.quantile(np.asarray(v,dtype=np.float64),p))
def fr(rows,m,f):return [s for r in rows for s in r["methods"][m]["scenarios"] if s["family"]==f]
def sf(scs):
    o={"scenario_count":len(scs),"horizons":{}}
    for h in HORIZONS:
        k=f"h{h}";o["horizons"][k]={"logical_divergence_median":q([s["horizons"][k]["logical_divergence"] for s in scs],.5),"physical_divergence_median":q([s["horizons"][k]["physical_divergence"] for s in scs],.5),"outside_lesion_divergence_median":q([s["horizons"][k]["outside_lesion_divergence"] for s in scs],.5),"exact_logical_match_rate":float(np.mean([s["horizons"][k]["exact_logical_match"] for s in scs]))}
    o["logical_divergence_area_median"]=q([s["logical_divergence_area"] for s in scs],.5);o["physical_divergence_area_median"]=q([s["physical_divergence_area"] for s in scs],.5);o["sustained_exact_logical_recovery_rate"]=float(np.mean([s["sustained_exact_logical_recovery"] for s in scs]))
    for key in ("repairs","false_repairs","abstentions","vote2","vote3","vote4","local_clean","local_nonclean"):
        vals=[s["repair_delta"][key] for s in scs];o[key+"_sum"]=int(np.sum(vals));o[key+"_median"]=q(vals,.5)
    o["false_repair_fraction"]=float(o["false_repairs_sum"]/o["repairs_sum"]) if o["repairs_sum"] else 0.0
    return o
def summarize(rows):
    valid=all(r["methods"][m]["no_damage_control"] for r in rows for m in METHODS);o={"worlds":len(rows),"mechanical_valid":bool(valid),"methods":{}}
    fams=("LOCAL_DATA2","LOCAL_SILENT3","LOCAL_DATA2_PLUS_ONE_WITNESS","TWO_CORRELATED_WITNESSES","THREE_CORRELATED_WITNESSES","DISTRIBUTED_LOCAL_DATA2")
    for m in METHODS:o["methods"][m]={f:sf(fr(rows,m,f)) for f in fams}
    q3=o["methods"]["QUORUM3_OF_4"]
    one=q3["LOCAL_DATA2_PLUS_ONE_WITNESS"];one_sig=(one["horizons"]["h1"]["logical_divergence_median"]==0 and one["sustained_exact_logical_recovery_rate"]>=.9 and one["false_repair_fraction"]<=.01 and one["logical_divergence_area_median"]==0)
    two=q3["TWO_CORRELATED_WITNESSES"];two_safe=(two["false_repairs_sum"]==0 and two["horizons"]["h4"]["logical_divergence_median"]==0)
    tworef=o["methods"]["TWO_WITNESS_NEAREST"]["TWO_CORRELATED_WITNESSES"];two_ref_fail=tworef["false_repair_fraction"]>.10
    dist=q3["DISTRIBUTED_LOCAL_DATA2"];dist_sig=(dist["horizons"]["h4"]["logical_divergence_median"]==0 and dist["sustained_exact_logical_recovery_rate"]>=.75)
    three=q3["THREE_CORRELATED_WITNESSES"];three_fail=three["false_repair_fraction"]>.10
    o["one_bad_witness_tolerance_signal"]=bool(one_sig);o["two_correlated_witness_safety"]=bool(two_safe);o["two_witness_control_failure"]=bool(two_ref_fail);o["distributed_quorum_signal"]=bool(dist_sig);o["three_correlated_witness_boundary"]=bool(three_fail)
    return o
def encode_json(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def run():
    rows=[one_world(WORLD_START+i) for i in range(WORLD_COUNT)];return {"schema":"yggdrasil.dg1r-05e-multiwitness-quorum.v1","rows":rows,"summary":summarize(rows),"worlds":len(rows),"seed_start":WORLD_START,"seed_end":WORLD_START+WORLD_COUNT-1}
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--out",required=True);a=ap.parse_args();obj=run();raw=(encode_json(obj)+"\n").encode();Path(a.out).write_bytes(raw);print(encode_json({"output":a.out,"sha256":hashlib.sha256(raw).hexdigest(),"summary":obj["summary"],"worlds":obj["worlds"]}))
if __name__=="__main__":main()