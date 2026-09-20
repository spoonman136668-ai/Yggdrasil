#!/usr/bin/env python3
import argparse, hashlib, json
from pathlib import Path
import numpy as np

WIDTH=128; LOGICAL_BLOCKS=12; DATA_PER_BLOCK=4; LOGICAL_BITS=48
LOCAL74_BITS=84; CROSS_BITS=44; POST_STEPS=32; DAMAGE_AFTER_STEPS=1024
WORLD_START=20260926053000; WORLD_COUNT=8; HORIZONS=(1,4,8,16,32)
MIX_RULES=np.asarray([90,150,110,22,30],dtype=np.uint16)
METHODS=("LOCAL84_GUARD","TISSUE74_XOR_BOTH","TISSUE74_XOR_LEFT","TISSUE74_DETECT_ONLY")
TISSUE_METHODS=METHODS[1:]
MAPPED_BLOCKS=np.asarray([1,3,5,7,9,11],dtype=np.int64)
DAMAGE_BLOCKS=(2,6,10)
DIST_BLOCKS=(2,10)
DATA_OFF=(2,4,5,6)
EXPECTED={"TWO_DATA2":2,"THREE_DATA3":3,"ALL_DATA4":4,"DATA2_PLUS_LEFT_CHECK1":3,"DISTRIBUTED_TWO_DATA2":4}


def eca_step_mixed(state,rules):
    left=np.roll(state,1); right=np.roll(state,-1); idx=(left<<2)|(state<<1)|right
    return ((rules>>idx)&1).astype(np.uint8)

def mixed_rules(rng,width):
    reps=width//len(MIX_RULES); rem=width%len(MIX_RULES)
    a=np.concatenate((np.tile(MIX_RULES,reps),MIX_RULES[:rem])).astype(np.uint16); rng.shuffle(a); return a

def h74_encode4(d):
    d1,d2,d3,d4=[int(x) for x in d]; o=np.empty(7,dtype=np.uint8)
    o[0]=d1^d2^d4; o[1]=d1^d3^d4; o[2]=d1; o[3]=d2^d3^d4; o[4]=d2; o[5]=d3; o[6]=d4
    return o

def h74_decode7(c): return c[[2,4,5,6]].copy()
def syndrome7(c):
    s1=int(c[0]^c[2]^c[4]^c[6]); s2=int(c[1]^c[2]^c[5]^c[6]); s4=int(c[3]^c[4]^c[5]^c[6]); return s1+2*s2+4*s4

def secded_encode4(d):
    c=h74_encode4(d); return np.concatenate((c,np.asarray([np.bitwise_xor.reduce(c)],dtype=np.uint8)))
def secded_decode8(c): return h74_decode7(c[:7])

def mapped_logical(rng):
    offs=rng.integers(0,4,size=len(MAPPED_BLOCKS),dtype=np.int64)
    return np.asarray([int(b*4+o) for b,o in zip(MAPPED_BLOCKS,offs)],dtype=np.int64)

def local84_phys_for_logical(lp):
    b=int(lp//4); off=int(lp%4); return b*8+DATA_OFF[off]
def tissue_phys_for_logical(lp):
    b=int(lp//4); off=int(lp%4); return b*7+DATA_OFF[off]

def cross_index(edge,k): return LOCAL74_BITS + edge*4 + k

def encode_local84(logical):
    out=np.zeros(WIDTH,dtype=np.uint8)
    for b in range(LOGICAL_BLOCKS): out[b*8:b*8+8]=secded_encode4(logical[b*4:(b+1)*4])
    return out

def decode_local84(state):
    x=np.empty(LOGICAL_BITS,dtype=np.uint8)
    for b in range(LOGICAL_BLOCKS): x[b*4:(b+1)*4]=secded_decode8(state[b*8:b*8+8])
    return x

def encode_tissue(logical):
    out=np.zeros(WIDTH,dtype=np.uint8)
    for b in range(LOGICAL_BLOCKS): out[b*7:b*7+7]=h74_encode4(logical[b*4:(b+1)*4])
    for e in range(LOGICAL_BLOCKS-1):
        a=logical[e*4:(e+1)*4]; b=logical[(e+1)*4:(e+2)*4]
        out[LOCAL74_BITS+e*4:LOCAL74_BITS+(e+1)*4]=a^b
    return out

def decode_tissue(state):
    x=np.empty(LOGICAL_BITS,dtype=np.uint8)
    for b in range(LOGICAL_BLOCKS): x[b*4:(b+1)*4]=h74_decode7(state[b*7:b*7+7])
    return x

def init_tel(): return {"syndrome_positive":0,"attempts":0,"agreements":0,"abstentions":0,"repairs":0,"false_repairs":0,"logical_bits_changed":0}

def repair_local84(state,tel):
    for b in range(LOGICAL_BLOCKS):
        s=b*8; c=state[s:s+8]; syn=syndrome7(c[:7]); parity=int(np.bitwise_xor.reduce(c))
        if syn: tel["syndrome_positive"]+=1
        if syn!=0 and parity==1:
            state[s+syn-1]^=1; tel["repairs"]+=1
        elif syn==0 and parity==1:
            state[s+7]^=1; tel["repairs"]+=1
        elif syn!=0 and parity==0:
            tel["abstentions"]+=1

def tissue_candidates(state,b):
    left=decode_tissue(state)[(b-1)*4:b*4] ^ state[LOCAL74_BITS+(b-1)*4:LOCAL74_BITS+b*4]
    right=decode_tissue(state)[(b+1)*4:(b+2)*4] ^ state[LOCAL74_BITS+b*4:LOCAL74_BITS+(b+1)*4]
    return left,right

def repair_tissue(state,method,ref_logical,tel):
    # snapshot decoded neighbors before any block repair so order cannot leak repaired state
    decoded=decode_tissue(state)
    cross=state[LOCAL74_BITS:].copy()
    for b in range(1,LOGICAL_BLOCKS-1):
        s=b*7; syn=syndrome7(state[s:s+7])
        if syn==0: continue
        tel["syndrome_positive"]+=1; tel["attempts"]+=1
        left=decoded[(b-1)*4:b*4] ^ cross[(b-1)*4:b*4]
        right=decoded[(b+1)*4:(b+2)*4] ^ cross[b*4:(b+1)*4]
        if method=="TISSUE74_DETECT_ONLY": tel["abstentions"]+=1; continue
        if method=="TISSUE74_XOR_BOTH":
            if not np.array_equal(left,right): tel["abstentions"]+=1; continue
            proposal=left; tel["agreements"]+=1
        else:
            proposal=left
        current=h74_decode7(state[s:s+7]); changed=int(np.sum(current!=proposal))
        if ref_logical is not None and not np.array_equal(proposal,ref_logical[b*4:(b+1)*4]): tel["false_repairs"]+=1
        state[s:s+7]=h74_encode4(proposal); tel["repairs"]+=1; tel["logical_bits_changed"]+=changed

def step(state,bit,mapped,rules,method,ref_logical=None,tel=None):
    if tel is None: tel=init_tel()
    if method=="LOCAL84_GUARD":
        repair_local84(state,tel); logical=decode_local84(state)
    else:
        repair_tissue(state,method,ref_logical,tel); logical=decode_tissue(state)
    logical[mapped]=np.uint8(bit); logical=eca_step_mixed(logical,rules)
    state[:]=encode_local84(logical) if method=="LOCAL84_GUARD" else encode_tissue(logical)
    return tel

def initial(method):
    z=np.zeros(LOGICAL_BITS,dtype=np.uint8); return encode_local84(z) if method=="LOCAL84_GUARD" else encode_tissue(z)

def prefix(u,mapped,rules,method):
    s=initial(method)
    for t in range(DAMAGE_AFTER_STEPS): step(s,int(u[t]),mapped,rules,method)
    return s

def method_mapped_phys(mapped,method):
    f=local84_phys_for_logical if method=="LOCAL84_GUARD" else tissue_phys_for_logical
    return np.asarray([f(int(lp)) for lp in mapped],dtype=np.int64)

def lesion_scenarios(method):
    out=[]
    for b in DAMAGE_BLOCKS:
        base=b*(8 if method=="LOCAL84_GUARD" else 7)
        out.append(("TWO_DATA2",(base+2,base+4)))
        out.append(("THREE_DATA3",(base+2,base+4,base+5)))
        out.append(("ALL_DATA4",(base+2,base+4,base+5,base+6)))
        if method in TISSUE_METHODS:
            out.append(("DATA2_PLUS_LEFT_CHECK1",(base+2,base+4,cross_index(b-1,0))))
    inds=[]
    for b in DIST_BLOCKS:
        base=b*(8 if method=="LOCAL84_GUARD" else 7); inds.extend((base+2,base+4))
    out.append(("DISTRIBUTED_TWO_DATA2",tuple(inds)))
    return out

def logical_from_state(state,method): return decode_local84(state) if method=="LOCAL84_GUARD" else decode_tissue(state)
def no_damage(pre,future,mapped,rules,method):
    a=pre.copy(); b=pre.copy()
    for bit in future:
        la=logical_from_state(a,method).copy(); lb=logical_from_state(b,method).copy()
        step(a,int(bit),mapped,rules,method,ref_logical=la); step(b,int(bit),mapped,rules,method,ref_logical=lb)
        if np.any(a!=b): return False
    return True

def one_scenario(pre,future,mapped,rules,method,fam,inds,mapped_phys):
    inds=np.asarray(inds,dtype=np.int64); assert len(inds)==EXPECTED[fam]; assert len(np.unique(inds))==EXPECTED[fam]; assert not np.any(np.isin(inds,mapped_phys))
    ref=pre.copy(); dmg=pre.copy(); dmg[inds]^=1; mask=np.zeros(WIDTH,dtype=bool); mask[inds]=True; outside=~mask
    telr=init_tel(); teld=init_tel(); pcurve=[]; lcurve=[]; logical_flags=[]; hm={}
    for h,bit in enumerate(future,start=1):
        ref_log=logical_from_state(ref,method).copy()
        step(ref,int(bit),mapped,rules,method,ref_logical=None,tel=telr)
        step(dmg,int(bit),mapped,rules,method,ref_logical=ref_log,tel=teld)
        pdiff=dmg!=ref; rlog=logical_from_state(ref,method); dlog=logical_from_state(dmg,method); ldiff=dlog!=rlog
        pdiv=float(np.mean(pdiff)); ldiv=float(np.mean(ldiff)); rec=float(1-np.mean(pdiff[mask])); outdiv=float(np.mean(pdiff[outside])); spread=int(np.sum(pdiff[outside])); pexact=bool(not np.any(pdiff)); lexact=bool(not np.any(ldiff))
        pcurve.append(pdiv); lcurve.append(ldiv); logical_flags.append(lexact)
        if h in HORIZONS: hm[f"h{h}"]={"whole_state_divergence":pdiv,"damaged_site_recovery":rec,"logical_data_divergence":ldiv,"outside_lesion_divergence":outdiv,"spread_count":spread,"exact_physical_match":pexact,"exact_logical_match":lexact}
    rt=None
    for h in range(1,POST_STEPS+1):
        if all(logical_flags[h-1:]): rt=h; break
    delta={k:int(teld[k]-telr[k]) for k in telr}
    return {"family":fam,"lesion_indices":[int(x) for x in inds],"actual_lesion_cardinality":int(len(inds)),"horizons":hm,"physical_divergence_area":float(np.sum(pcurve)),"logical_divergence_area":float(np.sum(lcurve)),"sustained_exact_logical_recovery":bool(rt is not None),"logical_recovery_time":rt,"repair_delta":delta}

def one_world(seed):
    rng=np.random.default_rng(np.random.PCG64(seed)); u=rng.integers(0,2,size=DAMAGE_AFTER_STEPS+POST_STEPS,dtype=np.uint8); mapped=mapped_logical(rng); rules=mixed_rules(rng,LOGICAL_BITS); future=u[DAMAGE_AFTER_STEPS:]
    methods={}
    for m in METHODS:
        pre=prefix(u,mapped,rules,m); mp=method_mapped_phys(mapped,m); ctl=no_damage(pre,future,mapped,rules,m); sc=[]
        for fam,inds in lesion_scenarios(m): sc.append(one_scenario(pre,future,mapped,rules,m,fam,inds,mp))
        methods[m]={"no_damage_control":bool(ctl),"scenarios":sc}
    return {"seed":int(seed),"mapped_logical":[int(x) for x in mapped],"methods":methods}

def q(v,p): return float(np.quantile(np.asarray(v,dtype=np.float64),p))
def family_rows(rows,m,f): return [s for r in rows for s in r["methods"][m]["scenarios"] if s["family"]==f]
def summarize_family(scs):
    o={"scenario_count":len(scs),"horizons":{}}
    for h in HORIZONS:
        k=f"h{h}"; fields=("whole_state_divergence","damaged_site_recovery","logical_data_divergence","outside_lesion_divergence","spread_count")
        d={f:[s["horizons"][k][f] for s in scs] for f in fields}
        o["horizons"][k]={"whole_state_divergence_median":q(d["whole_state_divergence"],.5),"damaged_site_recovery_median":q(d["damaged_site_recovery"],.5),"logical_data_divergence_median":q(d["logical_data_divergence"],.5),"outside_lesion_divergence_median":q(d["outside_lesion_divergence"],.5),"spread_count_median":q(d["spread_count"],.5),"exact_logical_match_rate":float(np.mean([s["horizons"][k]["exact_logical_match"] for s in scs]))}
    o["physical_divergence_area_median"]=q([s["physical_divergence_area"] for s in scs],.5); o["logical_divergence_area_median"]=q([s["logical_divergence_area"] for s in scs],.5); o["sustained_exact_logical_recovery_rate"]=float(np.mean([s["sustained_exact_logical_recovery"] for s in scs]))
    for key in ("syndrome_positive","attempts","agreements","abstentions","repairs","false_repairs","logical_bits_changed"):
        vals=[s["repair_delta"][key] for s in scs]; o[key+"_sum"]=int(np.sum(vals)); o[key+"_median"]=q(vals,.5)
    o["false_repair_fraction"]=float(o["false_repairs_sum"]/o["repairs_sum"]) if o["repairs_sum"] else 0.0
    return o

def reduction(v,ref): return 0.0 if ref<=1e-15 else float((ref-v)/ref)
def summarize(rows):
    valid=all(r["methods"][m]["no_damage_control"] for r in rows for m in METHODS); o={"worlds":len(rows),"mechanical_valid":bool(valid),"methods":{}}
    fams=("TWO_DATA2","THREE_DATA3","ALL_DATA4","DATA2_PLUS_LEFT_CHECK1","DISTRIBUTED_TWO_DATA2")
    for m in METHODS:
        o["methods"][m]={}
        for f in fams:
            scs=family_rows(rows,m,f)
            if scs:o["methods"][m][f]=summarize_family(scs)
    t=o["methods"]["TISSUE74_XOR_BOTH"]; ref=o["methods"]["LOCAL84_GUARD"]
    two=t["TWO_DATA2"]; neighbor=(two["horizons"]["h1"]["logical_data_divergence_median"]==0 and two["sustained_exact_logical_recovery_rate"]>=.9 and reduction(two["logical_divergence_area_median"],ref["TWO_DATA2"]["logical_divergence_area_median"])>=.75 and two["false_repair_fraction"]<=.01)
    block=False
    for f in ("THREE_DATA3","ALL_DATA4"):
        x=t[f]
        if x["horizons"]["h4"]["logical_data_divergence_median"]==0 and x["sustained_exact_logical_recovery_rate"]>=.75:block=True
    dist=t["DISTRIBUTED_TWO_DATA2"]; dist_sig=(dist["horizons"]["h4"]["logical_data_divergence_median"]==0 and dist["sustained_exact_logical_recovery_rate"]>=.75)
    both=t["DATA2_PLUS_LEFT_CHECK1"]; left=o["methods"]["TISSUE74_XOR_LEFT"]["DATA2_PLUS_LEFT_CHECK1"]
    two_side=(left["false_repair_fraction"]>0 and both["false_repair_fraction"]<=.5*left["false_repair_fraction"])
    o["neighbor_reconstruction_signal"]=bool(neighbor); o["block_reconstruction_signal"]=bool(block); o["distributed_tissue_signal"]=bool(dist_sig); o["two_sided_validation_value"]=bool(two_side)
    return o

def encode(o): return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def run():
    rows=[one_world(WORLD_START+i) for i in range(WORLD_COUNT)]; return {"schema":"yggdrasil.dg1r-05c-neighbor-reconstruction.v1","rows":rows,"summary":summarize(rows),"worlds":len(rows),"seed_start":WORLD_START,"seed_end":WORLD_START+WORLD_COUNT-1}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--out",required=True); a=ap.parse_args(); obj=run(); raw=(encode(obj)+"\n").encode(); Path(a.out).write_bytes(raw); print(encode({"output":a.out,"sha256":hashlib.sha256(raw).hexdigest(),"summary":obj["summary"],"worlds":obj["worlds"]}))
if __name__=="__main__":main()