#!/usr/bin/env python3
import argparse, hashlib, itertools, json, math
from collections import Counter
from pathlib import Path
import numpy as np

WIDTH=128; BLOCKS=12; LOGICAL_BITS=48; CHECKS=20; PLANES=4; KMAX=6
POST_STEPS=32; PREFIX_STEPS=1024; WORLD_START=20260926061000; WORLD_COUNT=12
HORIZONS=(1,4,8,16,32); MIX_RULES=np.asarray([90,150,110,22,30],dtype=np.uint16)
MAPPED_BLOCKS=np.asarray([1,4,7,10],dtype=np.int64)
EDGES=(
(0,2,7,9),(1,3,6,11),(4,5,9,10,11),(2,3,5),(0,1,4,8),
(6,7,8,10),(2,4,6),(0,3,5,6,7),(1,7,10,11),(1,5,6,9),
(3,8,9,10),(0,4,8,11),(0,2,6,10),(1,3,4,7),(2,5,7,8,11),
(2,3,4,10),(0,1,5,10),(0,3,9,11),(1,2,8,9),(4,7,9),
)
EXPECTED_DEG=(7,7,7,7,7,6,6,7,6,7,7,6)
FP_ROWS=((1,1,1,1),(0,1,0,1),(0,0,1,1),(0,0,0,1))
RESOURCE_TOTALS={0:128,1:140,2:152,3:164,4:176}
METHODS=("NO_REPAIR","GREEDY_FIRSTSHOT","CROSSPLANE2_FIRSTSHOT","COORD6_SYNDROME_FIRSTSHOT","FP1_FIRSTSHOT","FP2_FIRSTSHOT","FP3_FIRSTSHOT","FP4_FIRSTSHOT")
FP_METHOD_DEPTH={f"FP{d}_FIRSTSHOT":d for d in range(1,5)}
FAMILIES=(
"LOCAL_DATA2_D6","DISTRIBUTED_DATA2","DATA2_PLUS_CHECK2_D6","DATA2_PLUS_CHECK3_D7",
"CHECK4_BIT0_D6","CHECK4_BIT0_D7","CHECK4_BITS01_D6","SINGLE_DATA1_D6",
"BASE_WEAK4_MASK1106","DIST3_WEAK5_MASK2243","DIST4_MIN6_MASK249",
)
CHALLENGE_BLOCKS={
"BASE_WEAK4_MASK1106":(1,4,6,10),
"DIST3_WEAK5_MASK2243":(0,1,6,7,11),
"DIST4_MIN6_MASK249":(0,3,4,5,6,7),
}
LEGACY=("LOCAL_DATA2_D6","DISTRIBUTED_DATA2","DATA2_PLUS_CHECK2_D6","DATA2_PLUS_CHECK3_D7")
CHECK_ONLY=("CHECK4_BIT0_D6","CHECK4_BIT0_D7","CHECK4_BITS01_D6")
CHALLENGES=tuple(CHALLENGE_BLOCKS)

H=np.zeros((CHECKS,BLOCKS),dtype=np.uint8)
for i,e in enumerate(EDGES): H[i,list(e)]=1

def columns():
    out=[0]*BLOCKS
    for i,e in enumerate(EDGES):
        for b in e: out[b]|=1<<i
    return tuple(out)
COLS=columns()

def code_syndrome(mask):
    s=0
    while mask:
        l=mask & -mask; b=l.bit_length()-1; s ^= COLS[b]; mask ^= l
    return s
CODE_SYNS=tuple(code_syndrome(m) for m in range(1<<BLOCKS))
CAND_MASKS=tuple(m for m in range(1,1<<BLOCKS) if m.bit_count()<=KMAX)
CAND_CACHE={}

def candidates(obs_syn):
    if obs_syn in CAND_CACHE: return CAND_CACHE[obs_syn]
    base=obs_syn.bit_count(); arr=[]
    for m in CAND_MASKS:
        after=(obs_syn^CODE_SYNS[m]).bit_count()
        if after<base: arr.append((m.bit_count(),base-after,m,after))
    arr.sort(key=lambda x:(x[0],-x[1],x[2]))
    CAND_CACHE[obs_syn]=tuple(arr); return CAND_CACHE[obs_syn]

def gf2_rank(cols):
    basis={}
    for v in cols:
        x=int(v)
        while x:
            p=x.bit_length()-1
            if p in basis: x ^= basis[p]
            else: basis[p]=x; break
    return len(basis)

def static_geometry():
    pair=Counter()
    for e in EDGES:
        for a,b in itertools.combinations(e,2): pair[tuple(sorted((a,b)))]+=1
    syns=CODE_SYNS[1:]
    return {
        "rank":gf2_rank(COLS),"kernel_count":sum(x==0 for x in syns),
        "single_floor":min(x.bit_count() for x in COLS),
        "two_floor":min((COLS[a]^COLS[b]).bit_count() for a,b in itertools.combinations(range(BLOCKS),2)),
        "global_floor":min(x.bit_count() for x in syns if x),
        "max_pair_cooccurrence":max(pair.values()),"incidences":sum(len(e) for e in EDGES),
        "degree_vector":tuple(sum(b in e for e in EDGES) for b in range(BLOCKS)),
    }

def fp_rank(depth):
    rows=[]
    for r in FP_ROWS[:depth]: rows.append(sum((bit&1)<<i for i,bit in enumerate(r)))
    return gf2_rank(rows)

def fp_value(bits4,depth):
    out=0
    for i,row in enumerate(FP_ROWS[:depth]):
        parity=0
        for p in range(PLANES): parity ^= (int(bits4[p]) & int(row[p]))
        out |= parity<<i
    return out

def stored_fingerprints(logical,depth):
    m=logical.reshape(BLOCKS,PLANES)
    return tuple(fp_value(m[b],depth) for b in range(BLOCKS))

def observed_fp_delta(stored,logical,depth):
    now=stored_fingerprints(logical,depth)
    return tuple(int(stored[b])^int(now[b]) for b in range(BLOCKS))

def proposal_fp(proposals,depth):
    per=[0]*BLOCKS
    for p,m in proposals.items():
        for b in range(BLOCKS):
            if (m>>b)&1: per[b] ^= 1<<p
    out=[]
    for b in range(BLOCKS):
        bits=[(per[b]>>p)&1 for p in range(PLANES)]
        out.append(fp_value(bits,depth))
    return tuple(out)

def compatible(proposals,obs,depth):
    pred=proposal_fp(proposals,depth)
    for b in range(BLOCKS):
        touched=any((m>>b)&1 for m in proposals.values())
        if touched and obs[b]==0: return False
        if pred[b]!=obs[b]: return False
    return True

def eca_step_mixed(s,r):
    l=np.roll(s,1); rr=np.roll(s,-1); idx=(l<<2)|(s<<1)|rr
    return ((r>>idx)&1).astype(np.uint8)

def mixed_rules(rng,w):
    reps=w//len(MIX_RULES); rem=w%len(MIX_RULES)
    a=np.concatenate((np.tile(MIX_RULES,reps),MIX_RULES[:rem])).astype(np.uint16); rng.shuffle(a); return a

def mapped_logical(rng):
    offs=rng.integers(0,4,size=len(MAPPED_BLOCKS),dtype=np.int64)
    return np.asarray([int(b*4+o) for b,o in zip(MAPPED_BLOCKS,offs)],dtype=np.int64)

def encode_state(logical):
    out=np.zeros(WIDTH,dtype=np.uint8); out[:LOGICAL_BITS]=logical
    for i,e in enumerate(EDGES):
        v=np.zeros(PLANES,dtype=np.uint8)
        for b in e: v ^= logical[b*PLANES:(b+1)*PLANES]
        out[LOGICAL_BITS+i*PLANES:LOGICAL_BITS+(i+1)*PLANES]=v
    return out

def decode_state(state): return state[:LOGICAL_BITS].copy()

def syndrome_matrix(state):
    logical=decode_state(state).reshape(BLOCKS,PLANES); checks=state[LOGICAL_BITS:].reshape(CHECKS,PLANES)
    return checks ^ ((H@logical)&1)

def syn_int_by_plane(state):
    sm=syndrome_matrix(state); out={}
    for p in range(PLANES):
        x=0
        for i in range(CHECKS):
            if sm[i,p]: x|=1<<i
        out[p]=x
    return out

def dynamics_step(state,bit,mapped,rules):
    logical=decode_state(state); logical[mapped]=np.uint8(bit)
    logical=eca_step_mixed(logical,rules); state[:]=encode_state(logical)

def prefix(u,mapped,rules):
    s=encode_state(np.zeros(LOGICAL_BITS,dtype=np.uint8))
    for t in range(PREFIX_STEPS): dynamics_step(s,int(u[t]),mapped,rules)
    return s

def data_pos(b,p): return b*PLANES+p
def check_pos(slot,p): return LOGICAL_BITS+slot*PLANES+p
def incident(block): return [i for i,e in enumerate(EDGES) if block in e]
def mapped_plane_by_block(mapped): return {int(x//PLANES):int(x%PLANES) for x in mapped}

def safe_plane(mapped,blocks):
    mp=mapped_plane_by_block(mapped); excluded={mp[b] for b in blocks if b in mp}
    for p in range(PLANES):
        if p not in excluded: return p
    raise AssertionError("no safe plane")

def lesion(mapped,fam):
    logical=[]; checks=[]; sp=None
    if fam=="LOCAL_DATA2_D6": logical=[data_pos(5,0),data_pos(5,1)]
    elif fam=="DISTRIBUTED_DATA2": logical=[data_pos(2,0),data_pos(2,1),data_pos(8,0),data_pos(8,1)]
    elif fam=="DATA2_PLUS_CHECK2_D6": logical=[data_pos(5,0),data_pos(5,1)]; checks=[check_pos(s,0) for s in incident(5)[:2]]
    elif fam=="DATA2_PLUS_CHECK3_D7": logical=[data_pos(2,0),data_pos(2,1)]; checks=[check_pos(s,0) for s in incident(2)[:3]]
    elif fam=="CHECK4_BIT0_D6": checks=[check_pos(s,0) for s in incident(5)[:4]]
    elif fam=="CHECK4_BIT0_D7": checks=[check_pos(s,0) for s in incident(2)[:4]]
    elif fam=="CHECK4_BITS01_D6":
        for s in incident(5)[:4]: checks.extend((check_pos(s,0),check_pos(s,1)))
    elif fam=="SINGLE_DATA1_D6": logical=[data_pos(5,0)]
    elif fam in CHALLENGE_BLOCKS:
        bs=CHALLENGE_BLOCKS[fam]; sp=safe_plane(mapped,bs); logical=[data_pos(b,sp) for b in bs]
    else: raise KeyError(fam)
    inds=tuple(logical+checks)
    return inds,len(logical),len(checks),sp

def validate_lesion(mapped,fam):
    inds,lc,cc,sp=lesion(mapped,fam)
    assert len(inds)==lc+cc and len(set(inds))==len(inds)
    assert sum(x<LOGICAL_BITS for x in inds)==lc and sum(x>=LOGICAL_BITS for x in inds)==cc
    expected={"LOCAL_DATA2_D6":(2,0),"DISTRIBUTED_DATA2":(4,0),"DATA2_PLUS_CHECK2_D6":(2,2),"DATA2_PLUS_CHECK3_D7":(2,3),
      "CHECK4_BIT0_D6":(0,4),"CHECK4_BIT0_D7":(0,4),"CHECK4_BITS01_D6":(0,8),"SINGLE_DATA1_D6":(1,0),
      "BASE_WEAK4_MASK1106":(4,0),"DIST3_WEAK5_MASK2243":(5,0),"DIST4_MIN6_MASK249":(6,0)}
    assert (lc,cc)==expected[fam]
    if fam in CHALLENGE_BLOCKS:
        mp=mapped_plane_by_block(mapped)
        for b in CHALLENGE_BLOCKS[fam]:
            if b in mp: assert sp!=mp[b]
    elif lc:
        assert not np.any(np.isin(np.asarray([x for x in inds if x<LOGICAL_BITS],dtype=np.int64),mapped))
    if fam.startswith("CHECK4") or "PLUS_CHECK" in fam:
        block=5 if "D6" in fam else 2
        slots=[(x-LOGICAL_BITS)//PLANES for x in inds if x>=LOGICAL_BITS]
        assert all(block in EDGES[s] for s in slots)
    return inds,lc,cc,sp

def greedy_proposal(state):
    sm=syndrome_matrix(state); flips=np.zeros((BLOCKS,PLANES),dtype=np.uint8); iters=0; support=[0]*BLOCKS
    for p in range(PLANES):
        s=sm[:,p].copy(); used=np.zeros(BLOCKS,dtype=bool); it=0
        while it<4:
            cur=int(np.sum(s)); best_red=0; best=None
            for b in range(BLOCKS):
                if used[b]: continue
                red=cur-int(np.sum(s ^ H[:,b]))
                if red>best_red: best_red=red; best=b
            if best is None or best_red<=0: break
            used[best]=True; flips[best,p]=1; s ^= H[:,best]; it+=1
        iters+=it
    for b in range(BLOCKS): support[b]=int(np.sum(flips[b,:]))
    return flips,iters,tuple(support)

def coord6_proposals(state):
    syns=syn_int_by_plane(state); props={}; rows={}
    for p,syn in syns.items():
        if not syn: continue
        xs=candidates(syn)
        if xs:
            props[p]=xs[0][2]; rows[p]=xs[0]
    return props,rows

def fp_proposals(state,stored,depth,obs_override=None):
    syns=syn_int_by_plane(state); active=tuple(sorted(p for p,s in syns.items() if s))
    obs=tuple(obs_override) if obs_override is not None else observed_fp_delta(stored,decode_state(state),depth)
    if not active: return None,{},obs
    allowed=0
    for b,v in enumerate(obs):
        if v!=0: allowed|=1<<b
    lists=[]
    for p in active:
        ls=[r for r in candidates(syns[p]) if (r[2] & ~allowed)==0]
        if not ls: return None,{},obs
        lists.append((p,ls))
    for combo in itertools.product(*(x[1] for x in lists)):
        props={lists[i][0]:combo[i][2] for i in range(len(lists))}
        if compatible(props,obs,depth): return props,{lists[i][0]:combo[i] for i in range(len(lists))},obs
    return None,{},obs

def proposal_array(props):
    arr=np.zeros((BLOCKS,PLANES),dtype=np.uint8)
    if props is None: return arr
    for p,m in props.items():
        for b in range(BLOCKS):
            if (m>>b)&1: arr[b,p]=1
    return arr

def array_to_props(arr):
    props={}
    for p in range(PLANES):
        m=0
        for b in range(BLOCKS):
            if arr[b,p]: m|=1<<b
        if m: props[p]=m
    return props

def evaluate_proposal(arr,current,reference):
    cm=current.reshape(BLOCKS,PLANES); rm=reference.reshape(BLOCKS,PLANES)
    proposed=int(np.sum(arr)); false=0; truth=np.zeros_like(arr)
    for b in range(BLOCKS):
        for p in range(PLANES):
            if cm[b,p]!=rm[b,p]: truth[b,p]=1
            if arr[b,p] and int(cm[b,p]^1)!=int(rm[b,p]): false+=1
    complete=bool(np.array_equal(arr,truth)); safe=bool(false==0 and proposed>0 and not complete)
    return proposed,false,complete,safe,int(np.sum(truth))

def apply_array(state,arr):
    if int(np.sum(arr)):
        lm=decode_state(state).reshape(BLOCKS,PLANES); lm ^= arr; state[:LOGICAL_BITS]=lm.reshape(LOGICAL_BITS)

def firstshot(state,reference,method,stored_by_depth,fp_obs_override=None):
    before=int(np.sum(syndrome_matrix(state))); current=decode_state(state); abstain=False; fingerprint_ok=None; rows={}; support=None; iters=0
    if method=="NO_REPAIR": arr=np.zeros((BLOCKS,PLANES),dtype=np.uint8); abstain=True
    elif method in ("GREEDY_FIRSTSHOT","CROSSPLANE2_FIRSTSHOT"):
        inferred,iters,support=greedy_proposal(state); arr=inferred.copy()
        if method=="CROSSPLANE2_FIRSTSHOT":
            for b in range(BLOCKS):
                if support[b]<2: arr[b,:]=0
        abstain=bool(np.sum(arr)==0)
    elif method=="COORD6_SYNDROME_FIRSTSHOT":
        props,rows=coord6_proposals(state); arr=proposal_array(props); abstain=bool(np.sum(arr)==0)
    elif method in FP_METHOD_DEPTH:
        depth=FP_METHOD_DEPTH[method]
        override=None if fp_obs_override is None else fp_obs_override.get(depth)
        props,rows,obs=fp_proposals(state,stored_by_depth[depth],depth,override)
        arr=proposal_array(props); abstain=bool(np.sum(arr)==0); fingerprint_ok=bool(props is not None and compatible(props,obs,depth))
    else: raise KeyError(method)
    proposed,false,complete,safe,truth_n=evaluate_proposal(arr,current,reference)
    apply_array(state,arr)
    after=int(np.sum(syndrome_matrix(state)))
    applied=int(np.sum(arr))
    return {"proposal_array":arr,"proposed_logical_flips":proposed,"applied_logical_flips":applied,"false_proposed_logical_flips":false,
      "false_applied_logical_flips":false,"complete_firstshot_correction":complete,"safe_partial_firstshot_correction":safe,
      "abstain":bool(abstain),"syndrome_weight_before":before,"syndrome_weight_after":after,"fingerprint_compatible":fingerprint_ok,
      "candidate_coalition_size_by_plane":{str(p):int(m.bit_count()) for p,m in array_to_props(arr).items()},
      "plane_support":None if support is None else list(support),"decoder_iterations":iters,"truth_logical_flips":truth_n}

def world_design(seed):
    rng=np.random.default_rng(np.random.PCG64(seed)); u=rng.integers(0,2,size=PREFIX_STEPS+POST_STEPS,dtype=np.uint8)
    mapped=mapped_logical(rng); rules=mixed_rules(rng,LOGICAL_BITS); return u,mapped,rules

def one_episode(pre,future,mapped,rules,method,fam,fp_override_builder=None):
    inds,lc,cc,sp=validate_lesion(mapped,fam); inds=np.asarray(inds,dtype=np.int64)
    ref=pre.copy(); dmg=pre.copy(); stored={d:stored_fingerprints(decode_state(pre),d) for d in range(1,5)}
    dmg[inds]^=1
    override=None
    if fp_override_builder is not None: override=fp_override_builder(dmg,stored)
    shot=firstshot(dmg,decode_state(ref),method,stored,override)
    pc=[]; lc_curve=[]; flags=[]; hm={}
    for h,bit in enumerate(future,start=1):
        dynamics_step(ref,int(bit),mapped,rules); dynamics_step(dmg,int(bit),mapped,rules)
        pd=dmg!=ref; ld=decode_state(dmg)!=decode_state(ref); p=float(np.mean(pd)); l=float(np.mean(ld)); exact=bool(not np.any(ld))
        pc.append(p); lc_curve.append(l); flags.append(exact)
        if h in HORIZONS: hm[f"h{h}"]={"physical_divergence":p,"logical_divergence":l,"exact_logical_match":exact}
    rt=None
    for h in range(1,POST_STEPS+1):
        if all(flags[h-1:]): rt=h; break
    return {"family":fam,"lesion_indices":[int(x) for x in inds],"logical_flip_count":lc,"integrity_flip_count":cc,"safe_plane":sp,
      "firstshot":{k:v for k,v in shot.items() if k!="proposal_array"},"horizons":hm,
      "logical_divergence_area":float(np.sum(lc_curve)),"physical_divergence_area":float(np.sum(pc)),
      "sustained_exact_logical_recovery":bool(rt is not None),"logical_recovery_time":rt}

def no_damage_control(pre,future,mapped,rules,method):
    ref=pre.copy(); x=pre.copy(); stored={d:stored_fingerprints(decode_state(pre),d) for d in range(1,5)}
    shot=firstshot(x,decode_state(ref),method,stored)
    assert shot["applied_logical_flips"]==0
    for bit in future:
        dynamics_step(ref,int(bit),mapped,rules); dynamics_step(x,int(bit),mapped,rules)
        assert np.array_equal(ref,x)
    return True

def mechanical_precheck():
    g=static_geometry(); assert g=={"rank":12,"kernel_count":0,"single_floor":6,"two_floor":8,"global_floor":4,"max_pair_cooccurrence":2,"incidences":80,"degree_vector":EXPECTED_DEG}
    assert tuple(fp_rank(d) for d in range(1,5))==(1,2,3,4); assert RESOURCE_TOTALS=={0:128,1:140,2:152,3:164,4:176}
    assert sum(math.comb(BLOCKS,k) for k in range(1,KMAX+1))==2509
    lesion_checks=0; controls=0
    for i in range(WORLD_COUNT):
        u,mapped,rules=world_design(WORLD_START+i); pre=prefix(u,mapped,rules); future=u[PREFIX_STEPS:]
        for fam in FAMILIES: validate_lesion(mapped,fam); lesion_checks+=1
        for method in METHODS: assert no_damage_control(pre,future,mapped,rules,method); controls+=1
    # Explicit FP parity/alias sanity: planes 0+1 cancel under FP1 but not FP2.
    bits=[1,1,0,0]; assert fp_value(bits,1)==0 and fp_value(bits,2)!=0
    return {"mechanical_valid":True,"geometry":g,"fingerprint_ranks":{f"FP{d}":fp_rank(d) for d in range(1,5)},
      "resource_totals":RESOURCE_TOTALS,"candidate_masks":2509,"lesion_validations":lesion_checks,"no_damage_controls":controls,
      "worlds":WORLD_COUNT,"seed_start":WORLD_START,"seed_end":WORLD_START+WORLD_COUNT-1,"repair_opportunities_per_episode":1,
      "canonical_scientific_execution":False,"stab18_r1_touched":False}

def one_world(seed):
    u,mapped,rules=world_design(seed); pre=prefix(u,mapped,rules); future=u[PREFIX_STEPS:]; methods={}
    for method in METHODS:
        methods[method]={"scenarios":[one_episode(pre,future,mapped,rules,method,fam) for fam in FAMILIES]}
    # Correlated holdouts only for FP methods.
    corr={}
    for method,depth in FP_METHOD_DEPTH.items():
        def f1_builder(dmg,stored,d=depth):
            # Force observed delta to zero by treating stored fingerprint as current fingerprint.
            return {d:(0,)*BLOCKS}
        f1=one_episode(pre,future,mapped,rules,method,"SINGLE_DATA1_D6",f1_builder)
        def f2_builder(dmg,stored,d=depth):
            props,_=coord6_proposals(dmg); pred=proposal_fp(props,d) if props else (0,)*BLOCKS
            return {d:pred}
        f2=one_episode(pre,future,mapped,rules,method,"CHECK4_BIT0_D6",f2_builder)
        corr[method]={"CF1_LOGICAL_PLUS_FP_ERASURE":f1,"CF2_CHECK_ONLY_PLUS_FALSE_FP_SUPPORT":f2}
    return {"seed":int(seed),"mapped_logical":[int(x) for x in mapped],"methods":methods,"correlated_holdouts":corr}

def q(v,p=.5): return float(np.quantile(np.asarray(v,dtype=np.float64),p))
def family_rows(rows,method,fam): return [s for r in rows for s in r["methods"][method]["scenarios"] if s["family"]==fam]
def summarize_family(scs):
    o={"scenario_count":len(scs),"complete_firstshot_correction_count":sum(s["firstshot"]["complete_firstshot_correction"] for s in scs),
      "safe_partial_firstshot_correction_count":sum(s["firstshot"]["safe_partial_firstshot_correction"] for s in scs),
      "abstain_count":sum(s["firstshot"]["abstain"] for s in scs),
      "proposed_logical_flips_sum":sum(s["firstshot"]["proposed_logical_flips"] for s in scs),
      "applied_logical_flips_sum":sum(s["firstshot"]["applied_logical_flips"] for s in scs),
      "false_proposed_logical_flips_sum":sum(s["firstshot"]["false_proposed_logical_flips"] for s in scs),
      "false_applied_logical_flips_sum":sum(s["firstshot"]["false_applied_logical_flips"] for s in scs),
      "logical_divergence_area_median":q([s["logical_divergence_area"] for s in scs]),
      "physical_divergence_area_median":q([s["physical_divergence_area"] for s in scs]),
      "sustained_exact_logical_recovery_rate":float(np.mean([s["sustained_exact_logical_recovery"] for s in scs])),"horizons":{}}
    for h in HORIZONS:
        k=f"h{h}"; o["horizons"][k]={"logical_divergence_median":q([s["horizons"][k]["logical_divergence"] for s in scs]),
          "physical_divergence_median":q([s["horizons"][k]["physical_divergence"] for s in scs]),
          "exact_logical_match_rate":float(np.mean([s["horizons"][k]["exact_logical_match"] for s in scs]))}
    return o

def summarize(rows):
    methods={m:{f:summarize_family(family_rows(rows,m,f)) for f in FAMILIES} for m in METHODS}
    signals={}
    cross=methods["CROSSPLANE2_FIRSTSHOT"]
    for d in range(1,5):
        m=f"FP{d}_FIRSTSHOT"; x=methods[m]
        legacy=True
        for f in LEGACY:
            legacy &= x[f]["false_applied_logical_flips_sum"]==0 and x[f]["logical_divergence_area_median"]<=cross[f]["logical_divergence_area_median"]+1e-15 and x[f]["sustained_exact_logical_recovery_rate"]+1e-15>=cross[f]["sustained_exact_logical_recovery_rate"]
        check=all(x[f]["applied_logical_flips_sum"]==0 and x[f]["false_applied_logical_flips_sum"]==0 and x[f]["logical_divergence_area_median"]==0 for f in CHECK_ONLY)
        single=x["SINGLE_DATA1_D6"]["complete_firstshot_correction_count"]==WORLD_COUNT and x["SINGLE_DATA1_D6"]["false_applied_logical_flips_sum"]==0 and x["SINGLE_DATA1_D6"]["logical_divergence_area_median"]==0 and x["SINGLE_DATA1_D6"]["sustained_exact_logical_recovery_rate"]==1.0
        challenge=all(x[f]["complete_firstshot_correction_count"]==WORLD_COUNT and x[f]["false_applied_logical_flips_sum"]==0 and x[f]["logical_divergence_area_median"]==0 and x[f]["sustained_exact_logical_recovery_rate"]==1.0 for f in CHALLENGES)
        false_total=sum(x[f]["false_applied_logical_flips_sum"] for f in FAMILIES)
        signals[m]={"LEGACY_LOGICAL_PRESERVATION":bool(legacy),"CHECK_ONLY_SPECIFICITY":bool(check),"SINGLE_BIT_RECOVERY":bool(single),"CHALLENGE_DYNAMIC_RECOVERY":bool(challenge),"ZERO_FALSE_APPLIED_PRIMARY":false_total==0,"FIRSTSHOT_AUTHORITY_TRANSFER":bool(legacy and check and single and challenge and false_total==0),"resource_total_bits":RESOURCE_TOTALS[d]}
    # correlated boundaries
    corr={}
    for d in range(1,5):
        m=f"FP{d}_FIRSTSHOT"; f1=[r["correlated_holdouts"][m]["CF1_LOGICAL_PLUS_FP_ERASURE"] for r in rows]; f2=[r["correlated_holdouts"][m]["CF2_CHECK_ONLY_PLUS_FALSE_FP_SUPPORT"] for r in rows]
        corr[m]={"CF1_ERASURE_FAILURE":any(not s["firstshot"]["complete_firstshot_correction"] for s in f1),
          "CF1_abstain_count":sum(s["firstshot"]["abstain"] for s in f1),"CF1_logical_divergence_area_median":q([s["logical_divergence_area"] for s in f1]),
          "CF2_FORGED_SUPPORT_FAILURE":any(s["firstshot"]["false_applied_logical_flips"]>0 for s in f2),
          "CF2_false_applied_logical_flips_sum":sum(s["firstshot"]["false_applied_logical_flips"] for s in f2),"CF2_logical_divergence_area_median":q([s["logical_divergence_area"] for s in f2])}
    resource={}
    for d in range(1,5):
        m=f"FP{d}_FIRSTSHOT"; resource[m]={"resource_total_bits":RESOURCE_TOTALS[d],"applied_repairs":sum(methods[m][f]["applied_logical_flips_sum"] for f in FAMILIES),"abstentions":sum(methods[m][f]["abstain_count"] for f in FAMILIES),"complete_corrections":sum(methods[m][f]["complete_firstshot_correction_count"] for f in FAMILIES),"false_applied_flips":sum(methods[m][f]["false_applied_logical_flips_sum"] for f in FAMILIES)}
    return {"methods":methods,"signals":signals,"correlated_boundaries":corr,"resource_sensitivity":resource}

def run():
    rows=[one_world(WORLD_START+i) for i in range(WORLD_COUNT)]
    return {"schema":"yggdrasil.dg1r-05q-self-health-consensus-firstshot-dynamic.v1","mechanical_valid":True,"rows":rows,"summary":summarize(rows),"worlds":WORLD_COUNT,"seed_start":WORLD_START,"seed_end":WORLD_START+WORLD_COUNT-1,"canonical_scientific_execution":False,"stab18_r1_touched":False}

def enc(o): return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--out"); ap.add_argument("--precheck",action="store_true"); a=ap.parse_args()
    if a.precheck:
        print(enc(mechanical_precheck())); return
    if not a.out: ap.error("--out required unless --precheck")
    obj=run(); raw=(enc(obj)+"\n").encode(); Path(a.out).write_bytes(raw)
    print(enc({"output":a.out,"sha256":hashlib.sha256(raw).hexdigest(),"mechanical_valid":obj["mechanical_valid"],"signals":obj["summary"]["signals"],"correlated_boundaries":obj["summary"]["correlated_boundaries"],"resource_sensitivity":obj["summary"]["resource_sensitivity"]}))
if __name__=="__main__": main()
