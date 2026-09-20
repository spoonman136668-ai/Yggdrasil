#!/usr/bin/env python3
import argparse, hashlib, json
from pathlib import Path
import numpy as np

WIDTH=128; BLOCKS=16; LOGICAL_BITS=64; POST_STEPS=32; DAMAGE_AFTER_STEPS=1024
WORLD_START=20260926052000; WORLD_COUNT=8; HORIZONS=(1,4,8,16,32)
MIX_RULES=np.asarray([90,150,110,22,30],dtype=np.uint16)
METHODS=("HAM74_ALWAYS","HAM74_H6_GATE","SECDED84_GUARD","SECDED84_FORCE","DETECT_ONLY")
SECDED_METHODS=("SECDED84_GUARD","SECDED84_FORCE","DETECT_ONLY")
MAPPED_BLOCKS=np.asarray([1,2,5,7,10,11,13,14],dtype=np.int64)
DATA_PHYS_OFFSETS=np.asarray([2,4,5,6],dtype=np.int64)
DAMAGE_BLOCKS=(0,4,8,12)
DISTRIBUTED_TWO_BLOCKS=(0,8)


def eca_step_mixed(state,rules):
    left=np.roll(state,1); right=np.roll(state,-1)
    idx=(left<<2)|(state<<1)|right
    return ((rules>>idx)&1).astype(np.uint8)


def mixed_rules(rng,width):
    reps=width//len(MIX_RULES); rem=width%len(MIX_RULES)
    a=np.concatenate((np.tile(MIX_RULES,reps),MIX_RULES[:rem])).astype(np.uint16)
    rng.shuffle(a); return a


def h74_encode4(d):
    o=np.empty(7,dtype=np.uint8); d1,d2,d3,d4=[int(v) for v in d]
    o[0]=d1^d2^d4; o[1]=d1^d3^d4; o[2]=d1; o[3]=d2^d3^d4; o[4]=d2; o[5]=d3; o[6]=d4
    return o


def h74_decode7(c): return c[[2,4,5,6]].copy()

def syndrome7(c):
    s1=int(c[0]^c[2]^c[4]^c[6]); s2=int(c[1]^c[2]^c[5]^c[6]); s4=int(c[3]^c[4]^c[5]^c[6])
    return s1+2*s2+4*s4


def secded_encode4(d):
    c7=h74_encode4(d); p0=np.uint8(np.bitwise_xor.reduce(c7))
    return np.concatenate((c7,np.asarray([p0],dtype=np.uint8)))


def secded_decode8(c): return h74_decode7(c[:7])


def mapped_logical_positions(rng):
    offs=rng.integers(0,4,size=len(MAPPED_BLOCKS),dtype=np.int64)
    return np.asarray([int(b*4+o) for b,o in zip(MAPPED_BLOCKS,offs)],dtype=np.int64)


def mapped_physical_positions(mapped_logical):
    return np.asarray([int((lp//4)*8+DATA_PHYS_OFFSETS[lp%4]) for lp in mapped_logical],dtype=np.int64)


def encode_state(logical,method,controllers=None):
    out=np.zeros(WIDTH,dtype=np.uint8)
    for b in range(BLOCKS):
        d=logical[b*4:(b+1)*4]
        s=b*8
        if method in SECDED_METHODS:
            out[s:s+8]=secded_encode4(d)
        else:
            out[s:s+7]=h74_encode4(d)
            out[s+7]=0 if controllers is None else controllers[b]
    return out


def decode_state(state,method):
    logical=np.empty(LOGICAL_BITS,dtype=np.uint8)
    for b in range(BLOCKS):
        s=b*8
        logical[b*4:(b+1)*4]=secded_decode8(state[s:s+8]) if method in SECDED_METHODS else h74_decode7(state[s:s+7])
    return logical


def update_h6(state):
    for b in range(BLOCKS):
        s=b*8; ones=int(np.sum(state[s:s+7]))
        if ones>=6: state[s+7]=1
        elif ones<=1: state[s+7]=0


def init_tel():
    return {"syndrome_positive":0,"overall_parity_positive":0,"corrections":0,"abstentions":0,"detected_double":0,"false_corrections":0,"targets":{str(i):0 for i in range(1,9)}}


def record_correction(state,ref_pre,idx,tel):
    tel["corrections"]+=1; tel["targets"][str(idx+1)]+=1
    if ref_pre is not None and state[idx]==ref_pre[idx]: tel["false_corrections"]+=1
    state[idx]^=1


def repair_phase(state,method,ref_pre,tel):
    for b in range(BLOCKS):
        s=b*8
        if method in ("HAM74_ALWAYS","HAM74_H6_GATE"):
            syn=syndrome7(state[s:s+7])
            if syn:
                tel["syndrome_positive"]+=1
                do=True
                if method=="HAM74_H6_GATE":
                    n=int(state[s+7]); do=int(np.sum(state[s:s+7]==n))>=4
                if do: record_correction(state,ref_pre,s+syn-1,tel)
                else: tel["abstentions"]+=1
            continue
        c=state[s:s+8]; syn=syndrome7(c[:7]); parity=int(np.bitwise_xor.reduce(c))
        if syn: tel["syndrome_positive"]+=1
        if parity: tel["overall_parity_positive"]+=1
        if syn==0 and parity==0:
            continue
        if syn!=0 and parity==1:
            record_correction(state,ref_pre,s+syn-1,tel)
        elif syn==0 and parity==1:
            record_correction(state,ref_pre,s+7,tel)
        else: # syn != 0 and parity == 0 -> detected double
            tel["detected_double"]+=1
            if method=="SECDED84_FORCE": record_correction(state,ref_pre,s+syn-1,tel)
            else: tel["abstentions"]+=1


def step(state,bit,mapped_logical,rules,method,ref_pre=None,tel=None):
    if tel is None: tel=init_tel()
    repair_phase(state,method,ref_pre,tel)
    logical=decode_state(state,method)
    logical[mapped_logical]=np.uint8(bit)
    logical=eca_step_mixed(logical,rules)
    ctr=state[7::8].copy() if method in ("HAM74_ALWAYS","HAM74_H6_GATE") else None
    state[:]=encode_state(logical,method,controllers=ctr)
    if method=="HAM74_H6_GATE": update_h6(state)
    return tel


def prefix(u,mapped,rules,method):
    state=encode_state(np.zeros(LOGICAL_BITS,dtype=np.uint8),method,controllers=np.zeros(BLOCKS,dtype=np.uint8))
    for t in range(DAMAGE_AFTER_STEPS): step(state,int(u[t]),mapped,rules,method)
    return state


def lesion_scenarios(method):
    sc=[]
    for b in DAMAGE_BLOCKS:
        sc.append(("ONE1",(b*8+2,)))
        sc.append(("TWO2",(b*8+2,b*8+4)))
        sc.append(("THREE3",(b*8+1,b*8+2,b*8+4)))
        if method in SECDED_METHODS: sc.append(("PARITY1",(b*8+7,)))
    inds=[]
    for b in DISTRIBUTED_TWO_BLOCKS: inds.extend((b*8+2,b*8+4))
    sc.append(("DISTRIBUTED_TWO2",tuple(inds)))
    return sc

EXPECTED={"ONE1":1,"TWO2":2,"THREE3":3,"PARITY1":1,"DISTRIBUTED_TWO2":4}


def no_damage_control(pre,future,mapped,rules,method):
    a=pre.copy(); b=pre.copy()
    for bit in future:
        step(a,int(bit),mapped,rules,method); step(b,int(bit),mapped,rules,method)
        if np.any(a!=b): return False
    return True


def one_scenario(pre,future,mapped,mapped_phys,rules,method,family,indices):
    inds=np.asarray(indices,dtype=np.int64)
    assert len(inds)==EXPECTED[family]
    assert len(np.unique(inds))==EXPECTED[family]
    assert not np.any(np.isin(inds,mapped_phys))
    ref=pre.copy(); dmg=pre.copy(); dmg[inds]^=1
    mask=np.zeros(WIDTH,dtype=bool); mask[inds]=True; outside=~mask
    telr=init_tel(); teld=init_tel(); curve=[]; flags=[]; hm={}
    for h,bit in enumerate(future,start=1):
        ref_pre=ref.copy()
        step(ref,int(bit),mapped,rules,method,ref_pre=None,tel=telr)
        step(dmg,int(bit),mapped,rules,method,ref_pre=ref_pre,tel=teld)
        diff=dmg!=ref; whole=float(np.mean(diff)); rec=float(1-np.mean(diff[mask])); out=float(np.mean(diff[outside])); spread=int(np.sum(diff[outside])); exact=bool(not np.any(diff))
        curve.append(whole); flags.append(exact)
        if h in HORIZONS: hm[f"h{h}"]={"whole_state_divergence":whole,"damaged_site_recovery":rec,"outside_lesion_divergence":out,"spread_count":spread,"full_recovery":exact}
    rt=None
    for h in range(1,POST_STEPS+1):
        if all(flags[h-1:]): rt=h; break
    delta={}
    for k in ("syndrome_positive","overall_parity_positive","corrections","abstentions","detected_double","false_corrections"):
        delta[k]=int(teld[k]-telr[k])
    delta["targets"]={k:int(teld["targets"][k]-telr["targets"][k]) for k in teld["targets"]}
    return {"family":family,"lesion_indices":[int(v) for v in inds],"actual_lesion_cardinality":int(len(inds)),"horizons":hm,"excess_divergence_area":float(np.sum(curve)),"full_recovery":bool(rt is not None),"recovery_time":rt,"repair_delta":delta}


def one_world(seed):
    rng=np.random.default_rng(np.random.PCG64(seed))
    u=rng.integers(0,2,size=DAMAGE_AFTER_STEPS+POST_STEPS,dtype=np.uint8)
    mapped=mapped_logical_positions(rng); mapped_phys=mapped_physical_positions(mapped); rules=mixed_rules(rng,LOGICAL_BITS); future=u[DAMAGE_AFTER_STEPS:]
    methods={}
    for method in METHODS:
        pre=prefix(u,mapped,rules,method); control=no_damage_control(pre,future,mapped,rules,method); rows=[]
        for fam,inds in lesion_scenarios(method): rows.append(one_scenario(pre,future,mapped,mapped_phys,rules,method,fam,inds))
        methods[method]={"no_damage_control":bool(control),"scenarios":rows}
    return {"seed":int(seed),"mapped_logical":[int(v) for v in mapped],"mapped_physical":[int(v) for v in mapped_phys],"methods":methods}


def q(v,p): return float(np.quantile(np.asarray(v,dtype=np.float64),p))

def family_rows(rows,method,fam): return [s for r in rows for s in r["methods"][method]["scenarios"] if s["family"]==fam]


def summarize_family(scs):
    o={"scenario_count":len(scs),"horizons":{}}
    for h in HORIZONS:
        k=f"h{h}"; whole=[s["horizons"][k]["whole_state_divergence"] for s in scs]; rec=[s["horizons"][k]["damaged_site_recovery"] for s in scs]; out=[s["horizons"][k]["outside_lesion_divergence"] for s in scs]; spread=[s["horizons"][k]["spread_count"] for s in scs]; exact=[s["horizons"][k]["full_recovery"] for s in scs]
        o["horizons"][k]={"whole_state_divergence_median":q(whole,.5),"whole_state_divergence_p90":q(whole,.9),"damaged_site_recovery_median":q(rec,.5),"damaged_site_recovery_p10":q(rec,.1),"outside_lesion_divergence_median":q(out,.5),"outside_lesion_divergence_p90":q(out,.9),"spread_count_median":q(spread,.5),"exact_match_rate":float(np.mean(exact))}
    auc=[s["excess_divergence_area"] for s in scs]; full=[s["full_recovery"] for s in scs]
    o["excess_divergence_area_median"]=q(auc,.5); o["excess_divergence_area_p90"]=q(auc,.9); o["full_recovery_rate"]=float(np.mean(full))
    for key in ("syndrome_positive","overall_parity_positive","corrections","abstentions","detected_double","false_corrections"):
        vals=[s["repair_delta"][key] for s in scs]; o[key+"_median"]=q(vals,.5); o[key+"_sum"]=int(np.sum(vals))
    cor=o["corrections_sum"]; o["false_correction_fraction"]=float(o["false_corrections_sum"]/cor) if cor else 0.0
    return o


def reduction(v,ref): return 0.0 if ref<=1e-15 else float((ref-v)/ref)


def summarize(rows):
    valid=all(r["methods"][m]["no_damage_control"] for r in rows for m in METHODS)
    o={"worlds":len(rows),"mechanical_valid":bool(valid),"methods":{}}
    families=("ONE1","TWO2","THREE3","PARITY1","DISTRIBUTED_TWO2")
    for m in METHODS:
        o["methods"][m]={}
        for fam in families:
            scs=family_rows(rows,m,fam)
            if scs: o["methods"][m][fam]=summarize_family(scs)
    a=o["methods"]["HAM74_ALWAYS"]["ONE1"]; g=o["methods"]["SECDED84_GUARD"]["ONE1"]
    one=(a["horizons"]["h4"]["whole_state_divergence_median"]==0 and a["full_recovery_rate"]>=.9 and g["horizons"]["h4"]["whole_state_divergence_median"]==0 and g["full_recovery_rate"]>=.9)
    two_g=o["methods"]["SECDED84_GUARD"]["TWO2"]; two_a=o["methods"]["HAM74_ALWAYS"]["TWO2"]
    det_rate=two_g["detected_double_sum"]/max(1,two_g["scenario_count"])
    double_signal=(det_rate>=.95 and two_g["corrections_sum"]==0 and two_g["false_correction_fraction"]<=.01 and (two_a["false_correction_fraction"]>=.5 or two_a["excess_divergence_area_median"]>=1.25*two_g["excess_divergence_area_median"]))
    abst=False
    for fam in ("TWO2","DISTRIBUTED_TWO2"):
        guard=o["methods"]["SECDED84_GUARD"][fam]; force=o["methods"]["SECDED84_FORCE"][fam]
        auc_red=reduction(guard["excess_divergence_area_median"],force["excess_divergence_area_median"])
        out_red=reduction(guard["horizons"]["h8"]["outside_lesion_divergence_median"],force["horizons"]["h8"]["outside_lesion_divergence_median"])
        if auc_red>=.25 and out_red>=.25: abst=True
    parity_guard=(one and double_signal and two_g["false_correction_fraction"] < max(two_a["false_correction_fraction"], o["methods"]["SECDED84_FORCE"]["TWO2"]["false_correction_fraction"]))
    o["one_bit_repair_signal"]=bool(one); o["double_error_detection_signal"]=bool(double_signal); o["abstention_value_signal"]=bool(abst); o["parity_guardian_signal"]=bool(parity_guard)
    return o


def encode(o): return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False)

def run():
    rows=[one_world(WORLD_START+i) for i in range(WORLD_COUNT)]
    return {"schema":"yggdrasil.dg1r-05b-parity-guardian-boundary.v1","rows":rows,"summary":summarize(rows),"worlds":len(rows),"seed_start":WORLD_START,"seed_end":WORLD_START+WORLD_COUNT-1}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--out",required=True); args=ap.parse_args(); obj=run(); raw=(encode(obj)+"\n").encode(); Path(args.out).write_bytes(raw); print(encode({"output":args.out,"sha256":hashlib.sha256(raw).hexdigest(),"summary":obj["summary"],"worlds":obj["worlds"]}))
if __name__=="__main__": main()