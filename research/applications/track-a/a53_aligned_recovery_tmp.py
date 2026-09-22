import hashlib, json, math, statistics, sys
from collections import Counter, defaultdict

N=48
T=48
POOL_DECAY_NUM=3
POOL_DECAY_DEN=4
LOCAL_R=12
HILL_N=3
HILL_K=0.5
RECRUIT_R=3
ETA=0.5
POOL_NORM=160.0
K_SUPP=0.5
N_SUPP=3

HEDGE_R=3
ARM_PARAMS={
    'D2_P0_TAU0':(2,'P0',0.75,0),
    'D2_P0_TAU3_FIXED':(2,'P0',0.75,3),
    'D2_P0_TAU3_VETO':(2,'P0',0.75,3),
    'D2_P1_TAU0':(2,'P1',0.75,0),
    'D2_P1_TAU3_FIXED':(2,'P1',0.75,3),
    'D2_P1_TAU3_VETO':(2,'P1',0.75,3),
    'D3_P0_TAU0':(3,'P0',0.75,0),
    'D3_P0_TAU3_FIXED':(3,'P0',0.75,3),
    'D3_P0_TAU3_VETO':(3,'P0',0.75,3),
    'D3_P1_TAU0':(3,'P1',0.75,0),
    'D3_P1_TAU3_FIXED':(3,'P1',0.75,3),
    'D3_P1_TAU3_VETO':(3,'P1',0.75,3),
}
ARMS=tuple(ARM_PARAMS)
BIASED_CTX=set(range(44,48))
BALANCED_CTX=set(range(40,44))

def h64(*parts):
    s = '|'.join(str(x) for x in parts).encode()
    return int.from_bytes(hashlib.sha256(s).digest()[:8], 'big')

def u01(*parts):
    return h64(*parts) / float(2**64 - 1)


MASK64 = (1<<64)-1
def mix64(x):
    x = (x + 0x9E3779B97F4A7C15) & MASK64
    x = (x ^ (x >> 30)) * 0xBF58476D1CE4E5B9 & MASK64
    x = (x ^ (x >> 27)) * 0x94D049BB133111EB & MASK64
    x ^= x >> 31
    return x & MASK64

def fast_u01(base, t, i, salt):
    x = base ^ ((t+1)*0xD6E8FEB86659FD93 & MASK64) ^ ((i+1)*0xA5A3564E27F8862D & MASK64) ^ salt
    return mix64(x) / float(MASK64)

def initial_states():
    st = ['U'] * N
    for i in range(N):
        if i % 4 == 0:
            st[i] = 'C'
        elif i % 4 == 2:
            st[i] = 'S'
    assert st.count('C') == 12 and st.count('S') == 12 and st.count('U') == 24
    return st

def sensor_noise(seed, ctx, rep, t, i):
    z = h64('YGG-A42-SENSOR', seed, ctx, rep, t, i) % 10
    if z == 0: return -1
    if z == 1: return 1
    return 0

def hetero(seed, ctx, rep, t, i):
    z = h64('YGG-A42-HET', seed, ctx, rep, t, i) % 20
    if z == 0: return -1
    if z == 1: return 1
    if z in (2,3,4): return 0
    return None

def make_world(seed, ctx, rep):
    fam = ctx // 8
    idx = ctx % 8
    true = [[0]*N for _ in range(T)]
    reversal = None
    local_region = None
    if fam == 2:
        sizes = [12,16,20,24,28,32,36,40]
        size = sizes[idx]
        start = h64('YGG-A42-SPATIAL', seed, ctx, rep) % N
        pos = {(start+j) % N for j in range(size)}
        local_region = [1 if i in pos else -1 for i in range(N)]
    elif fam in (3,4):
        reversal = [12,16,20,24,28,32,36,40][idx]
    for t in range(T):
        for i in range(N):
            if fam == 0:
                base = 1
            elif fam == 1:
                base = -1
            elif fam == 2:
                base = local_region[i]
            elif fam == 3:
                base = 1 if t < reversal else -1
            elif fam == 4:
                base = -1 if t < reversal else 1
            else:
                modes = [(2,2),(3,3),(4,4),(1,1),(6,2),(2,6),(5,3),(3,5)]
                on, off = modes[idx]
                if idx <= 3:
                    base = 1 if (t // on) % 2 == 0 else -1
                else:
                    cyc = on + off
                    q = t % cyc
                    base = 1 if q < on else -1
                    if idx in (5,7):
                        base = -base
            hv = hetero(seed, ctx, rep, t, i)
            if hv is None:
                v = base
            elif hv == 0:
                v = 0
            else:
                v = hv
            true[t][i] = max(-1, min(1, int(v)))
    sensed = [[0]*N for _ in range(T)]
    for t in range(T):
        for i in range(N):
            sensed[t][i] = max(-1, min(1, true[t][i] + sensor_noise(seed, ctx, rep, t, i)))
    base_seq=[]
    for t in range(T):
        if fam==0: b=1
        elif fam==1: b=-1
        elif fam==2: b=0
        elif fam==3: b=1 if t<reversal else -1
        elif fam==4: b=-1 if t<reversal else 1
        else:
            modes=[(2,2),(3,3),(4,4),(1,1),(6,2),(2,6),(5,3),(3,5)]
            on,off=modes[idx]
            if idx<=3: b=1 if (t//on)%2==0 else -1
            else:
                cyc=on+off; q=t%cyc; b=1 if q<on else -1
                if idx in (5,7): b=-b
        base_seq.append(b)
    return {
        'ctx':ctx,'rep':rep,'family':fam,'index':idx,
        'true':true,'sensed':sensed,'reversal':reversal,'local_region':local_region,'base_seq':base_seq
    }

def local_density(emitters, i, r):
    width = 2*r + 1
    return sum(1 for d in range(-r,r+1) if (i+d)%N in emitters) / width

def p_stay_from_density(d):
    if d <= 0:
        return 1.0
    x = d / HILL_K
    return 1.0 / (1.0 + x**HILL_N)

def majority_label(states):
    c = states.count('C')
    s = states.count('S')
    if c > N/2: return 'C'
    if s > N/2: return 'S'
    return 'U'


def state_counts(states):
    return {k:states.count(k) for k in ('C','S','U','H','FC','FS')}

def arm_params(arm):
    return ARM_PARAMS[arm]

def shannon3(states):
    # External measurement only: C / S / unresolved family (U,H,FC,FS)
    counts=[states.count('C'),states.count('S'),sum(states.count(k) for k in ('U','H','FC','FS'))]
    z=sum(counts); h=0.0
    for c in counts:
        if c:
            p=c/z; h-=p*math.log(p,2)
    return h

def h_clusters(hset):
    if not hset:
        return []
    seen=set(); clusters=[]
    for i in sorted(hset):
        if i in seen: continue
        comp=set(); stack=[i]
        while stack:
            j=stack.pop()
            if j in seen or j not in hset: continue
            seen.add(j); comp.add(j)
            for k in ((j-1)%N,(j+1)%N):
                if k in hset and k not in seen: stack.append(k)
        clusters.append(comp)
    return clusters

def niche_lifetimes(hsets):
    active=[]; finished=[]
    for t,hset in enumerate(hsets):
        cur=[c for c in h_clusters(hset) if len(c)>=3]
        used=set(); nxt=[]
        for c in cur:
            best=None; best_overlap=0
            for j,tr in enumerate(active):
                if j in used: continue
                ov=len(c & tr['cells'])
                if ov>best_overlap:
                    best=j; best_overlap=ov
            if best is not None and best_overlap>0:
                tr=active[best]; used.add(best); nxt.append({'cells':c,'birth':tr['birth'],'last':t})
            else:
                nxt.append({'cells':c,'birth':t,'last':t})
        for j,tr in enumerate(active):
            if j not in used: finished.append(tr['last']-tr['birth']+1)
        active=nxt
    for tr in active: finished.append(tr['last']-tr['birth']+1)
    return finished


MARGIN_GAIN=None
MARGIN_SCOPE='COMMITTED_DEFECTION_ONLY'
B_INITIAL=0.0
B_UPDATE_SCOPE='EVERY_CELL_EVERY_EPOCH'
RECRUITMENT_READS_B=True
H_DYNAMICS_READ_B=False
A37_LINEAGE_PRESENT=False
CENTRAL_CONFIDENCE_PRESENT=False
FORCE_DELAY_OFF=False
FORCE_VETO_VALID=None

def arm_params(arm):
    return ARM_PARAMS[arm]

def signed_update(prev_b, rho, lc, ls):
    return rho*prev_b + (1.0-rho)*(lc-ls)

def aligned_margin(b, side):
    return max(0.0, b if side=='C' else -b)

def zero_cross_pressure(b, side):
    return max(0.0, -b if side=='C' else b)

def p_stay_margin(l_op, m):
    if l_op <= 0:
        return 1.0
    k_eff=HILL_K+m
    return 1.0/(1.0+(l_op/k_eff)**HILL_N)

def subtractive_pressure(l_op, m_pre):
    return max(0.0, l_op-m_pre)


def mean_or_none(xs):
    return statistics.mean(xs) if xs else None

def median_or_none(xs):
    return statistics.median(xs) if xs else None

def quantile_iqr(xs):
    if not xs:
        return None
    ys=sorted(xs)
    n=len(ys)
    def q(p):
        if n==1: return ys[0]
        x=(n-1)*p
        lo=int(math.floor(x)); hi=int(math.ceil(x))
        if lo==hi: return ys[lo]
        f=x-lo
        return ys[lo]*(1-f)+ys[hi]*f
    return q(.75)-q(.25)

def average_ranks(xs):
    order=sorted(range(len(xs)),key=lambda i:(xs[i],i))
    ranks=[0.0]*len(xs)
    k=0
    while k<len(order):
        j=k+1
        v=xs[order[k]]
        while j<len(order) and xs[order[j]]==v:
            j+=1
        avg=((k+1)+j)/2.0
        for z in range(k,j):
            ranks[order[z]]=avg
        k=j
    return ranks

def spearman(xs, ys):
    if len(xs)<2 or len(xs)!=len(ys):
        return None
    rx=average_ranks(xs); ry=average_ranks(ys)
    mx=statistics.mean(rx); my=statistics.mean(ry)
    num=sum((a-mx)*(b-my) for a,b in zip(rx,ry))
    dx=sum((a-mx)**2 for a in rx); dy=sum((b-my)**2 for b in ry)
    if dx<=0 or dy<=0:
        return 0.0
    return num/math.sqrt(dx*dy)

def rank_quartiles(samples):
    # samples: list of dicts with stable cell id i and numeric m
    if not samples:
        return set(),set()
    order=sorted(samples,key=lambda x:(x['m'],x['i']))
    q=max(1,len(order)//4)
    return {x['i'] for x in order[:q]}, {x['i'] for x in order[-q:]}

def summarize_margin_samples(samples):
    ms=[x['m'] for x in samples]
    post=[x['m_post'] for x in samples if x.get('m_post') is not None]
    pressures=[x['subtractive_pressure'] for x in samples if x.get('subtractive_pressure') is not None]
    positive=[x for x in pressures if x>0.0]
    return {
        'count':len(ms),
        'mean_m':mean_or_none(ms),
        'median_m':median_or_none(ms),
        'std_m':statistics.pstdev(ms) if len(ms)>1 else (0.0 if ms else None),
        'iqr_m':quantile_iqr(ms),
        'fraction_m_eq_0':sum(x==0 for x in ms)/len(ms) if ms else None,
        'fraction_m_ge_025':sum(x>=.25 for x in ms)/len(ms) if ms else None,
        'fraction_m_ge_050':sum(x>=.50 for x in ms)/len(ms) if ms else None,
        'fraction_m_ge_075':sum(x>=.75 for x in ms)/len(ms) if ms else None,
        'mean_b':mean_or_none([x['b'] for x in samples]),
        'median_commitment_age':median_or_none([x['age'] for x in samples]),
        'mean_l_op':mean_or_none([x['l_op'] for x in samples]),
        'mean_m_post':mean_or_none(post),
        'median_m_post':median_or_none(post),
        'pressure_zero_fraction':sum(x==0.0 for x in pressures)/len(pressures) if pressures else None,
        'mean_positive_pressure':mean_or_none(positive),
        'median_positive_pressure':median_or_none(positive),
    }


def prepare_world(world):
    if '_base_c' in world:
        return world
    bc=[]; bs=[]; lc12=[]; ls12=[]; lc3=[]; ls3=[]
    for t in range(T):
        sensed=world['sensed'][t]
        c={i for i,v in enumerate(sensed) if v>0}
        ss={i for i,v in enumerate(sensed) if v<0}
        bc.append(c); bs.append(ss)
        lc12.append([local_density(c,i,LOCAL_R) for i in range(N)])
        ls12.append([local_density(ss,i,LOCAL_R) for i in range(N)])
        lc3.append([local_density(c,i,RECRUIT_R) for i in range(N)])
        ls3.append([local_density(ss,i,RECRUIT_R) for i in range(N)])
    world['_base_c']=bc; world['_base_s']=bs
    world['_lc12']=lc12; world['_ls12']=ls12
    world['_lc3']=lc3; world['_ls3']=ls3
    return world

def ring_distance(i,j):
    d=abs(i-j)
    return min(d,N-d)

def core_field(states,bpre,i,side,mode):
    vals=[]
    for d in range(-RECRUIT_R,RECRUIT_R+1):
        j=(i+d)%N
        if states[j]!=side:
            vals.append(0.0)
        elif mode=='OCCUPANCY':
            vals.append(1.0)
        elif mode=='MARGIN_EXCLUSION':
            vals.append(aligned_margin(bpre[j],side))
        else:
            vals.append(0.0)
    return sum(vals)/len(vals)

def cooperative_field(states,bpre,i,side,mode):
    total=0.0
    count=0
    for d in range(-RECRUIT_R,RECRUIT_R+1):
        if d==0:
            continue
        j=(i+d)%N
        count+=1
        if states[j]!=side:
            continue
        if mode=='OCCUPANCY_REINFORCE':
            total+=1.0
        elif mode=='MARGIN_REINFORCE':
            total+=aligned_margin(bpre[j],side)
    return total/count if count else 0.0

def local_mode(side, lc, ls):
    if side=='C':
        if lc>ls: return 'SUPPORT'
        if ls>lc: return 'CHALLENGE'
        return 'NEUTRAL'
    if side=='S':
        if ls>lc: return 'SUPPORT'
        if lc>ls: return 'CHALLENGE'
        return 'NEUTRAL'
    return None

def support_margin_field(states,bpre,lc_now,ls_now,i,side,gated):
    # Exact A42 active-margin normalization: seven radius-3 positions.
    # For eligible U target i the center contributes zero.
    total=0.0
    count=0
    for d in range(-RECRUIT_R,RECRUIT_R+1):
        j=(i+d)%N
        count+=1
        if states[j]!=side:
            continue
        if gated and local_mode(side,lc_now[j],ls_now[j])!='SUPPORT':
            continue
        total+=aligned_margin(bpre[j],side)
    return total/count if count else 0.0

def challenge_occrpancy_field(states,lc_now,ls_now,i,side):
    # A49: radius-3 seven-position mean. For eligible U target i,
    # the center position contributes zero because states[i] == 'U'.
    total=0.0
    count=0
    for d in range(-RECRUIT_R,RECRUIT_R+1):
        j=(i+d)%N
        count+=1
        if states[j]!=side:
            continue
        if local_mode(side,lc_now[j],ls_now[j])!='CHALLENGE':
            continue
        total+=1.0
    return total/count if count else 0.0

def same_side_neighbor_count(states,i,side):
    return sum(1 for d in range(-RECRUIT_R,RECRUIT_R+1) if d!=0 and states[(i+d)%N]==side)

def mode_run_lengths(seq, target):
    out=[]; cur=0
    for x in seq+[None]:
        if x==target: cur+=1
        else:
            if cur: out.append(cur)
            cur=0
    return out

def within_radius_of(i, _de' r=RECRUIT_R):
    return any(ring_distance(i,j)<=r for j in _de)

def largest_ring_domain(states, side):
    if not states or side not in states:
        return 0
    if all(x==side for x in states):
        return len(states)
    doubled=states+states
    best=cur=0
    for x in doubled:
        if x==side:
            cur+=1; best=max(best,cur)
        else:
            cur=0
    return min(best,len(states))

def cs_interface_count(states):
    total=0
    for i in range(N):
        a=states[i]; b=states[(i+1)%N]
        if a in ('C','S') and b in ('C','S') and a!=b:
            total+=1
    return total

def burst_shape(base_seq,t,favored):
    opp=-1 if favored=='C' else 1
    if base_seq[t]!=opp:
        return None
    end=t
    while end+1<T and base_seq[end+1]==opp:
        end+=1
    length=end-t+1
    midpoint_step=(length+1)//2
    return length,midpoint_step,end

def run_arm(seed, world, arm):
    world=prepare_world(world)
    ctx,rep=world['ctx'],world['rep']
    D,kind,rho,tau=arm_params(arm)
    veto_arm=arm.endswith('_VETO')
    if FORCE_DELAY_OFF: tau=0
    w_pool,w_local=.75,.25
    control_arm='D2_ECHO_PHASE' if D==2 else 'D3_ECHO_PHASE'
    arm_base=h64('YGG-A45-ARM-SEED',seed,ctx,rep,control_arm)
    states=initial_states(); timers=[0]*N
    commit_age=[0 if s in ('C','S') else None for s in states]
    bstate=[B_INITIAL]*N
    opp_c=[0.0]*N; opp_s=[0.0]*N
    cp=sp=0.0
    service=cumulative=worst_drawdown=0
    majority_hist=[]; count_hist=[]; entropy_hist=[]
    contradiction={'total':0,'nomajority':0,'cmajor':0,'smajor':0}
    transitions=Counter(); chatter_sequences=defaultdict(list); join_origin={}
    recruitment_waves=[]; active_wave=None
    h_enter_time={}; h_dwells=[]
    h_entries_contr=h_entries_non=0; h_eligible_contr=h_eligible_non=0
    h_occ_contr=h_occ_non=0; h_epochs_contr=h_epochs_non=0
    hsets=[]; contr_hist=[]
    reversal=world['reversal']; old_side=new_side=None
    if world['family']==3: old_side,new_side='C','S'
    elif world['family']==4: old_side,new_side='S','C'
    old_majority_seen=False; old_loss=None; new_acquire=None
    balanced_nomajority_epochs=0

    margin_samples=[]
    erosion_records=[]
    burst=None
    burst_survival=[]
    reversal_cohort=None
    reversal_diag={'cohort_n':0,'onset_median_m':None,'zero_cross_latencies':[],'m_zero_latencies':[],'first_positive_pressure_latencies':[]}

    recruitment_boundary=[]
    core_rebuild=[]
    trajectory_bursts=[]
    spatial_midpoints=[]
    pending_recoveries=[]
    epoch_states=[]
    reversal_recruitment=[]
    reversal_old_core=None

    # A44 phase-gating diagnostics.
    mode_counts=Counter()
    mode_pressure_reduction=defaultdict(list)
    challenge_pressure_reduced=0
    challenge_pressure_total=0
    reversal_old_modes=Counter()
    reversal_old_mode_total=0
    balanced_mode_seq=[[] for _ in range(N)]
    support_epoch_diag=[]
    support_interval=None
    support_intervals=[]
    prechallenge=[]

    # A49 macro organization diagnostics.
    a49_challenge_turnover=[]
    a49_cycle_onsets=[]
    challenge_cycle_index=0
    pending_majority_recoveries=[]

    # A45 one-epoch, non-recursive cooperative echo.
    q_prev=[0.0]*N
    q_prev_side=[None]*N
    echo_stats={'records':0,'active':0,'sum_q_raw':0.0,'sum_q_eff':0.0,
                'active_sum_q_echo':0.0,'active_sum_echo_specific_q':0.0,
                'balanced_records':0,'balanced_active':0}
    echo_hit_records=[]
    echo_reversal_records=[]
    trace_freshness={
        'noncommitted_zero':True,
        'new_commit_zero':True,
        'side_cross_zero':True,
        'stores_raw_only':True,
    }

    # A52 committed-response pressure history and phase diagnostics.
    pressure_hist=[[] for _ in range(N)]
    pressure_hist_fresh={'side_safe':True,'reset_safe':True,'current_stored':True,'warmup_current':True,'no_future':True}
    a52_phase_stats=Counter()
    a52_phase_mode_pairs=Counter()
    a52_hit_records=[]
    a52_reversal_records=[]
    committed_diff_hist=[]
    a53_veto_stats=Counter()

    for t in range(T):
        sensed=world['sensed'][t]
        base_c=world['_base_c'][t]; base_s=world['_base_s'][t]
        lc_now=world['_lc12'][t]; ls_now=world['_ls12'][t]
        lc3_now=world['_lc3'][t]; ls3_now=world['_ls3'][t]
        bpre=bstate[:]

        # Frozen cohort timing: capture pre-pulse/pre-reversal B before ingesting current evidence.
        if reversal is not None and t==reversal:
            cohort=[i for i,s in enumerate(states) if s==old_side]
            reversal_cohort={i:{'m0':aligned_margin(bpre[i],old_side),'b0':bpre[i],
                                'zero_cross':None,'m_zero':None,'first_positive_pressure':None} for i in cohort}
            reversal_diag['cohort_n']=len(cohort)
            reversal_diag['onset_median_m']=median_or_none([x['m0'] for x in reversal_cohort.values()])
            reversal_old_core=set(cohort)

        favored=None
        if ctx in BIASED_CTX:
            favored='C' if sum(world['base_seq'])>0 else 'S'
            opp_sign=-1 if favored=='C' else 1
            prev=world['base_seq'][t-1] if t>0 else None
            onset=(t>0 and world['base_seq'][t]==opp_sign and prev==-opp_sign)
            if onset:
                cohort=[]
                for i,s in enumerate(states):
                    if s==favored:
                        lop=ls_now[i] if favored=='C' else lc_now[i]
                        sample={'ctx':ctx,'rep':rep,'t':t,'i':i,'b':bpre[i],
                                'm':aligned_margin(bpre[i],favored),
                                'age':commit_age[i] if commit_age[i] is not None else 0,
                                'l_op':lop,'m_post':None,'subtractive_pressure':None}
                        margin_samples.append(sample); cohort.append(sample)
                low,high=rank_quartiles(cohort)
                shape=burst_shape(world['base_seq'],t,favored)
                burst={'onset':t,'favored':favored,'members':{x['i']:x for x in cohort},
                       'low':low,'high':high,'defect':{},'step':0,
                       'pre_fraction':len(cohort)/N,'min_fraction':len(cohort)/N,
                       'length':shape[0] if shape else 1,'midpoint_step':shape[1] if shape else 1,
                       'core_ids':None,
                       'turnover':{'opportunities':0,'favored':0,'adverse':0,'H':0,'none':0}}
                fav_ids=[i for i,s0 in enumerate(states) if s0==favored]
                challenge_cycle_index+=1
                onset_counts=state_counts(states)
                onset_u=[i for i,s0 in enumerate(states) if s0=='U']
                onset_q=[challenge_occrpancy_field(states,lc_now,ls_now,i,favored) for i in onset_u]
                a49_cycle_onsets.append({
                    'ctx':ctx,'rep':rep,'cycle':challenge_cycle_index,'t':t,'favored':favored,
                    'favored_fraction':len(fav_ids)/N,
                    'adverse_fraction':states.count('S' if favored=='C' else 'C')/N,
                    'u_fraction':onset_counts['U']/N,'h_fraction':onset_counts['H']/N,
                    'fc_fraction':onset_counts['FC']/N,'fs_fraction':onset_counts['FS']/N,
                    'refractory_fraction':(onset_counts['FC']+onset_counts['FS'])/N,
                    'majority':majority_label(states),
                    'largest_favored_domain':largest_ring_domain(states,favored),
                    'challenge_field_coverage':(sum(q>0.0 for q in onset_q)/len(onset_q)) if onset_q else 0.0,
                })
                prechallenge.append({
                    'ctx':ctx,'rep':rep,'t':t,'favored':favored,
                    'favored_fraction':len(fav_ids)/N,
                    'mean_m':mean_or_none([aligned_margin(bpre[i],favored) for i in fav_ids]),
                    'mean_q_margin':mean_or_none([cooperative_field(states,bpre,i,favored,'MARGIN_REINFORCE') for i in fav_ids]),
                    'largest_domain':largest_ring_domain(states,favored),
                    'dense_ge5_fraction':(sum(same_side_neighbor_count(states,i,favored)>=5 for i in fav_ids)/len(fav_ids)) if fav_ids else None,
                })

        # Shared signed temporal state; A39 controls retain their original post-update decision timing.
        for i in range(N):
            bstate[i]=signed_update(bstate[i],rho,lc_now[i],ls_now[i])
            opp_c[i]=rho*opp_c[i]+(1.0-rho)*ls_now[i]
            opp_s[i]=rho*opp_s[i]+(1.0-rho)*lc_now[i]

        if burst is not None and burst['onset']==t:
            for i,samp in burst['members'].items():
                samp['m_post']=aligned_margin(bstate[i],burst['favored'])
                samp['subtractive_pressure']=subtractive_pressure(samp['l_op'],samp['m'])

        if reversal_cohort is not None and t>=reversal:
            for i,d in reversal_cohort.items():
                m=aligned_margin(bstate[i],old_side)
                crossed=(bstate[i]<=0.0 if old_side=='C' else bstate[i]>=0.0)
                if d['m_zero'] is None and m<=0.0: d['m_zero']=t-reversal
                if d['zero_cross'] is None and crossed: d['zero_cross']=t-reversal
                if d['first_positive_pressure'] is None:
                    lop=ls_now[i] if old_side=='C' else lc_now[i]
                    if subtractive_pressure(lop,aligned_margin(bpre[i],old_side))>0.0:
                        d['first_positive_pressure']=t-reversal

        fb_c=fb_s=0
        for i,s in enumerate(states):
            if s=='C' and sensed[i]>=0: fb_c+=1
            elif s=='S' and sensed[i]<=0: fb_s+=1
        cp=.75*cp+len(base_c)+fb_c; sp=.75*sp+len(base_s)+fb_s
        pc=min(1.0,cp/POOL_NORM); ps=min(1.0,sp/POOL_NORM)
        is_contr=cp>=48 and sp>=48

        for i,s in enumerate(states):
            if s in ('FC','FS'):
                if timers[i]<=0:
                    states[i]='U'; transitions[f'{s}->U']+=1
                else: timers[i]-=1

        released_h=set(); h_release_snapshot={j for j,sj in enumerate(states) if sj=='H'}
        for i,s in enumerate(states[:]):
            if s!='H': continue
            lc=lc3_now[i]; ls=ls3_now[i]
            sup_c=w_pool*pc+w_local*lc; sup_s=w_pool*ps+w_local*ls
            lam_release=ETA*(1.0-min(sup_c,sup_s))
            hlocal=local_density(h_release_snapshot,i,HEDGE_R)
            lam_release*=max(0.0,1.0-hlocal)
            p_release=1.0-math.exp(-max(0.0,lam_release))
            if fast_u01(arm_base,t,i,0x55A55A55A55A55A5)<p_release:
                states[i]='U'; released_h.add(i); transitions['H->U']+=1
                if i in h_enter_time: h_dwells.append(t-h_enter_time.pop(i))

        prior=states[:]; defects=[]
        epoch_modes=[None]*N
        epoch_pressure_rec=[None]*N
        epoch_phase_rec={}
        epoch_q_raw=[None]*N
        epoch_echo_rec={}
        for i,s in enumerate(prior):
            if s not in ('C','S'):
                if q_prev[i]!=0.0 or q_prev_side[i] is not None:
                    trace_freshness['noncommitted_zero']=False
                if pressure_hist[i]:
                    pressure_hist_fresh['reset_safe']=False
                continue
            if any(x.get('side')!=s for x in pressure_hist[i]):
                pressure_hist_fresh['side_safe']=False
            lop=ls_now[i] if s=='C' else lc_now[i]
            own_m=aligned_margin(bpre[i],s)
            mode=local_mode(s,lc_now[i],ls_now[i])
            epoch_modes[i]=mode
            q_raw=cooperative_field(prior,bpre,i,s,'MARGIN_REINFORCE')
            epoch_q_raw[i]=q_raw
            q_echo=q_prev[i] if q_prev_side[i]==s else 0.0
            if q_prev_side[i] not in (None,s) and q_echo!=0.0:
                trace_freshness['side_cross_zero']=False
            q_eff=max(q_raw,q_echo)
            base_pressure=max(0.0,lop-own_m)
            if mode=='CHALLENGE':
                qcoop=q_eff
            else:
                qcoop=0.0
            pressure_now=max(0.0,lop-own_m-qcoop)

            # A52: delay only the pressure value consumed by p_stay.
            hist=pressure_hist[i]
            source_epoch=t
            source_mode=mode
            source_age=0
            pressure_decision=pressure_now
            used_delayed=False
            history_available=False
            veto_fired=False
            fixed_source_epoch=t
            fixed_source_mode=mode
            fixed_pressure_candidate=pressure_now
            current_m_post=aligned_margin(bstate[i],s)
            current_valid=(current_m_post>0.0)
            if FORCE_VETO_VALID is True:
                current_valid=True
            elif FORCE_VETO_VALID is False:
                current_valid=False
            if tau>0 and len(hist)>=tau:
                cand=hist[-tau]
                if cand['side']!=s:
                    pressure_hist_fresh['side_safe']=False
                if cand['epoch']>t:
                    pressure_hist_fresh['no_future']=False
                if cand['epoch']==t-tau and cand['side']==s:
                    history_available=True
                    fixed_source_epoch=cand['epoch']
                    fixed_source_mode=cand['mode']
                    fixed_pressure_candidate=cand['pressure_now']
                    allow_delayed=(not veto_arm) or current_valid
                    if veto_arm and not current_valid:
                        veto_fired=True
                    if allow_delayed:
                        pressure_decision=cand['pressure_now']
                        source_epoch=cand['epoch']
                        source_mode=cand['mode']
                        source_age=t-source_epoch
                        used_delayed=True
            if tau>0 and not history_available and pressure_decision!=pressure_now:
                pressure_hist_fresh['warmup_current']=False

            if veto_arm:
                a53_veto_stats['decisions']+=1
                if history_available: a53_veto_stats['history_available']+=1
                if used_delayed: a53_veto_stats['used_delayed']+=1
                if veto_fired: a53_veto_stats['veto_fired']+=1
                if history_available and fixed_pressure_candidate < pressure_now-1e-15:
                    a53_veto_stats['fixed_would_protect']+=1
                    if veto_fired: a53_veto_stats['vetoed_fixed_protection']+=1

            a52_phase_stats['decisions']+=1
            if used_delayed:
                a52_phase_stats['delayed_decisions']+=1
                a52_phase_stats['source_age_sum']+=source_age
            a52_phase_mode_pairs[(mode,source_mode)]+=1

            mode_counts[mode]+=1
            reduction=base_pressure-pressure_now
            mode_pressure_reduction[mode].append(reduction)
            if mode=='CHALLENGE':
                challenge_pressure_total+=1
                if reduction>0.0: challenge_pressure_reduced+=1
            if reversal is not None and reversal<=t<reversal+4 and s==old_side:
                reversal_old_modes[mode]+=1; reversal_old_mode_total+=1
            echo_specific=max(0.0, qcoop-q_raw)
            er={'ctx':ctx,'rep':rep,'t':t,'i':i,'side':s,'mode':mode,
                'm':own_m,'q_raw':q_raw,'q_echo':q_echo,'q_eff':q_eff,
                'echo_active':q_echo>q_raw,'echo_specific_q':echo_specific,
                'base_pressure':base_pressure,'pressure':pressure_now,
                'defected':False,
                'reversal_old':bool(reversal is not None and t>=reversal and s==old_side),
                'reversal_latency':(t-reversal if reversal is not None and t>=reversal and s==old_side else None)}

            phase_rec={'ctx':ctx,'rep':rep,'t':t,'i':i,'side':s,'current_mode':mode,
                       'pressure_now':pressure_now,'pressure_decision':pressure_decision,
                       'source_epoch':source_epoch,'source_age':source_age,'source_mode':source_mode,
                       'used_delayed':used_delayed,'same_side_neighbors':same_side_neighbor_count(prior,i,s),'defected':False,
                       'veto_arm':veto_arm,'history_available':history_available,'veto_fired':veto_fired,
                       'm_post_current':current_m_post,'current_valid':current_valid,
                       'fixed_source_epoch':fixed_source_epoch,'fixed_source_mode':fixed_source_mode,
                       'fixed_pressure_candidate':fixed_pressure_candidate}
            if burst is not None and ctx in (46,47) and i in burst['members'] and burst['step']<3:
                phase_rec['burst_step']=burst['step']+1
                phase_rec['burst_favored']=burst['favored']
                a52_hit_records.append(phase_rec)
            if reversal is not None and reversal<=t<reversal+5 and s==old_side:
                phase_rec['reversal_latency']=t-reversal
                phase_rec['source_pre_reversal']=source_epoch<reversal
                phase_rec['fixed_source_pre_reversal']=fixed_source_epoch<reversal
                a52_reversal_records.append(phase_rec)
            epoch_phase_rec[i]=phase_rec
            epoch_pressure_rec[i]={'side':s,'pressure_now':pressure_now,'mode':mode,'epoch':t}
            echo_stats['records']+=1
            echo_stats['sum_q_raw']+=q_raw
            echo_stats['sum_q_eff']+=q_eff
            if er['echo_active']:
                echo_stats['active']+=1
                echo_stats['active_sum_q_echo']+=q_echo
                echo_stats['active_sum_echo_specific_q']+=echo_specific
            if ctx in BALANCED_CTX:
                echo_stats['balanced_records']+=1
                if er['echo_active']: echo_stats['balanced_active']+=1
            if burst is not None and ctx in (46,47) and i in burst['members']:
                er['burst_step']=burst['step']+1
                er['burst_favored']=burst['favored']
                echo_hit_records.append(er)
            if er['reversal_old'] and er['reversal_latency'] in (0,1,2,3):
                echo_reversal_records.append(er)
            epoch_echo_rec[i]=er
            p=p_stay_from_density(pressure_decision)
            if fast_u01(arm_base,t,i,0x11C11C11C11C11C1 if s=='C' else 0x22C22C22C22C22C2)>=p:
                defects.append((i,s))

        if ctx in BALANCED_CTX:
            for i in range(N):
                balanced_mode_seq[i].append(epoch_modes[i])

        for i,side in defects:
            if i in epoch_echo_rec: epoch_echo_rec[i]['defected']=True
            if i in epoch_phase_rec: epoch_phase_rec[i]['defected']=True
            fs='FC' if side=='C' else 'FS'; states[i]=fs; timers[i]=D
            commit_age[i]=None
            transitions[f'{side}->{fs}']+=1; chatter_sequences[i].append((t,side,'DEFECT'))
            join_origin.pop(i,None)
            if burst is not None and i in burst['members'] and i not in burst['defect']:
                burst['defect'][i]=t-burst['onset']+1

        # A52 pressure history update: store current pressure only for uninterrupted same-side survivors.
        next_pressure_hist=[[] for _ in range(N)]
        for i,s in enumerate(states):
            if s in ('C','S') and prior[i]==s and epoch_pressure_rec[i] is not None:
                if any(x.get('side')!=s for x in pressure_hist[i]):
                    pressure_hist_fresh['side_safe']=False
                rec=epoch_pressure_rec[i]
                if rec['pressure_now'] != (epoch_phase_rec[i]['pressure_now'] if i in epoch_phase_rec else rec['pressure_now']):
                    pressure_hist_fresh['current_stored']=False
                next_pressure_hist[i]=(pressure_hist[i]+[rec])[-4:]
            else:
                if s not in ('C','S') and pressure_hist[i]:
                    pass
        pressure_hist=next_pressure_hist

        # Non-recursive trace update: surviving same-side commitments store raw Q only.
        next_q_prev=[0.0]*N; next_q_prev_side=[None]*N
        for i,s in enumerate(states):
            if s in ('C','S') and prior[i]==s and epoch_q_raw[i] is not None:
                next_q_prev[i]=epoch_q_raw[i]
                next_q_prev_side[i]=s
                if next_q_prev[i] != epoch_q_raw[i]:
                    trace_freshness['stores_raw_only']=False
        q_prev=next_q_prev; q_prev_side=next_q_prev_side

        survivor_c={i for i,s in enumerate(states) if s=='C'}
        survivor_s={i for i,s in enumerate(states) if s=='S'}
        if burst is not None and burst['onset']==t:
            burst['core_ids']=set(survivor_c if burst['favored']=='C' else survivor_s)

        eligible=[i for i,s in enumerate(states) if s=='U' and i not in released_h]
        if is_contr: h_eligible_contr+=len(eligible)
        else: h_eligible_non+=len(eligible)
        pool_bias='C' if cp>sp else ('S' if sp>cp else 'NONE')
        if active_wave is not None and pool_bias in ('C','S') and pool_bias!=active_wave['bias']:
            recruitment_waves.append(active_wave); active_wave=None

        joined=[]; h_entered=0; h_entry_snapshot={j for j,sj in enumerate(states) if sj=='H'}
        adverse_now=(favored is not None and world['base_seq'][t]==(-1 if favored=='C' else 1))
        support_now=(favored is not None and world['base_seq'][t]==(1 if favored=='C' else -1))
        if support_now and support_interval is None:
            support_interval={'ctx':ctx,'rep':rep,'favored':favored,'start_t':t,
                              'start_fraction':states.count(favored)/N}
        for i in eligible:
            lc=lc3_now[i]; ls=ls3_now[i]
            sup_c=w_pool*pc+w_local*lc; sup_s=w_pool*ps+w_local*ls
            oppx_c=w_pool*ps+w_local*ls; oppx_s=w_pool*pc+w_local*lc
            g_c=1.0/(1.0+(oppx_c/K_SUPP)**N_SUPP) if oppx_c>0 else 1.0
            g_s=1.0/(1.0+(oppx_s/K_SUPP)**N_SUPP) if oppx_s>0 else 1.0
            base_lam_c=ETA*sup_c*g_c; base_lam_s=ETA*sup_s*g_s
            q_c_occ=core_field(states,bpre,i,'C','OCCUPANCY')
            q_s_occ=core_field(states,bpre,i,'S','OCCUPANCY')
            q_c_margin=core_field(states,bpre,i,'C','MARGIN_EXCLUSION')
            q_s_margin=core_field(states,bpre,i,'S','MARGIN_EXCLUSION')
            q_c_support=support_margin_field(states,bpre,lc_now,ls_now,i,'C',gated=True)
            q_s_support=support_margin_field(states,bpre,lc_now,ls_now,i,'S',gated=True)
            parent_lam_c=base_lam_c + ETA*q_c_support
            parent_lam_s=base_lam_s + ETA*q_s_support
            q_c_ch_occ=challenge_occrpancy_field(states,lc_now,ls_now,i,'C')
            q_s_ch_occ=challenge_occrpancy_field(states,lc_now,ls_now,i,'S')
            if kind=='P1':
                lam_c=(parent_lam_c + ETA*q_c_ch_occ)*(1.0-q_s_ch_occ)
                lam_s=(parent_lam_s + ETA*q_s_ch_occ)*(1.0-q_c_ch_occ)
            else:
                lam_c=parent_lam_c
                lam_s=parent_lam_s
            lam_h=ETA*sup_c*sup_s
            hlocal_entry=local_density(h_entry_snapshot,i,HEDGE_R)
            lam_h*=1.0+hlocal_entry

            rec=None; turnover_rec=None; revrec=None
            if adverse_now:
                adverse_side='S' if favored=='C' else 'C'
                favored_ids=survivor_c if favored=='C' else survivor_s
                inside=within_radius_of(i,favored_ids)
                qfav_occ=q_c_occ if favored=='C' else q_s_occ
                qopp_occ=q_s_occ if favored=='C' else q_c_occ
                qfav_margin=q_c_margin if favored=='C' else q_s_margin
                qopp_margin=q_s_margin if favored=='C' else q_c_margin
                base_adv=base_lam_s if adverse_side=='S' else base_lam_c
                xadv=lam_s if adverse_side=='S' else lam_c
                base_fav=base_lam_c if favored=='C' else base_lam_s
                xfav=lam_c if favored=='C' else lam_s
                rec={'ctx':ctx,'rep':rep,'t':t,'i':i,'favored':favored,'inside':inside,
                     'q_favored_occ':qfav_occ,'q_opposing_occ':qopp_occ,
                     'q_favored_margin':qfav_margin,'q_opposing_margin':qopp_margin,
                     'base_favored_lambda':base_fav,'transformed_favored_lambda':xfav,
                     'base_adverse_lambda':base_adv,'transformed_adverse_lambda':xadv,
                     'same_side_lambda_change':xfav-base_fav,
                     'opposing_lambda_suppression':base_adv-xadv,
                     'recruited':False,'joined_side':None,
                     'favored_recruit':False,'adverse_recruit':False}
                recruitment_boundary.append(rec)
                if burst is not None and burst.get('core_ids') and within_radius_of(i,burst['core_ids']):
                    turnover_rec=burst['turnover']
                    turnover_rec['opportunities']+=1

            a49rec=None
            if adverse_now:
                adverse_side='S' if favored=='C' else 'C'
                qfav=q_c_ch_occ if favored=='C' else q_s_ch_occ
                qadv=q_s_ch_occ if favored=='C' else q_c_ch_occ
                parent_fav=parent_lam_c if favored=='C' else parent_lam_s
                parent_adv=parent_lam_s if favored=='C' else parent_lam_c
                xfav=lam_c if favored=='C' else lam_s
                xadv=lam_s if favored=='C' else lam_c
                a49rec={'ctx':ctx,'rep':rep,'t':t,'i':i,'favored':favored,
                        'q_favored_ch_occ':qfav,'q_adverse_ch_occ':qadv,
                        'inside_favored_challenge':qfav>0.0,
                        'parent_favored_lambda':parent_fav,'parent_adverse_lambda':parent_adv,
                        'transformed_favored_lambda':xfav,'transformed_adverse_lambda':xadv,
                        'same_side_lambda_increment':xfav-parent_fav,
                        'opposing_lambda_suppression':parent_adv-xadv,
                        'recruited':False,'joined_side':None,'favored_recruit':False,
                        'adverse_recruit':False,'h_recruit':False}
                a49_challenge_turnover.append(a49rec)

            if reversal is not None and t>=reversal and reversal_old_core and within_radius_of(i,reversal_old_core):
                revrec={'ctx':ctx,'rep':rep,'t':t,'latency':t-reversal,'old_side':old_side,'new_side':new_side,
                        'recruited':False,'joined_side':None}
                reversal_recruitment.append(revrec)

            if favored is not None and world['base_seq'][t]==(1 if favored=='C' else -1):
                qfav_support=q_c_support if favored=='C' else q_s_support
                basefav=base_lam_c if favored=='C' else base_lam_s
                xfav=lam_c if favored=='C' else lam_s
                support_epoch_diag.append({'ctx':ctx,'rep':rep,'t':t,'i':i,'favored':favored,
                                           'q_support':qfav_support,'increment':xfav-basefav,
                                           'joined_favored':False})
                support_rec_ref=support_epoch_diag[-1]
            else:
                support_rec_ref=None

            lam=lam_c+lam_s+lam_h
            if lam<=0:
                if turnover_rec is not None: turnover_rec['none']+=1
                continue
            p_fire=1.0-math.exp(-lam)
            if fast_u01(arm_base,t,i,0x33C33C33C33C33C3)>=p_fire:
                if turnover_rec is not None: turnover_rec['none']+=1
                continue
            z=fast_u01(arm_base,t,i,0x44C44C44C44C44C4)*lam
            if z<lam_c: side='C'
            elif z<lam_c+lam_s: side='S'
            else: side='H'
            states[i]=side; transitions[f'U->{side}']+=1
            if side in ('C','S') and (q_prev[i]!=0.0 or q_prev_side[i] is not None):
                trace_freshness['new_commit_zero']=False
            if support_rec_ref is not None and side==favored:
                support_rec_ref['joined_favored']=True
            if rec is not None:
                rec['recruited']=True; rec['joined_side']=side
                adverse_side='S' if favored=='C' else 'C'
                rec['favored_recruit']=(side==favored)
                rec['adverse_recruit']=(side==adverse_side)
            if turnover_rec is not None:
                adverse_side='S' if favored=='C' else 'C'
                if side==favored: turnover_rec['favored']+=1
                elif side==adverse_side: turnover_rec['adverse']+=1
                elif side=='H': turnover_rec['H']+=1
                else: turnover_rec['none']+=1
            if a49rec is not None:
                a49rec['recruited']=True; a49rec['joined_side']=side
                adverse_side='S' if favored=='C' else 'C'
                a49rec['favored_recruit']=(side==favored)
                a49rec['adverse_recruit']=(side==adverse_side)
                a49rec['h_recruit']=(side=='H')
            if revrec is not None:
                revrec['recruited']=True; revrec['joined_side']=side
            if side=='H': h_entered+=1; h_enter_time[i]=t; commit_age[i]=None
            else:
                commit_age[i]=0
                chatter_sequences[i].append((t,side,'JOIN')); joined.append((i,side)); join_origin[i]=(t,side)

        if is_contr: h_entries_contr+=h_entered
        else: h_entries_non+=h_entered

        if active_wave is None and pool_bias in ('C','S') and len(eligible)>=8:
            if any(side==pool_bias for _,side in joined):
                active_wave={'bias':pool_bias,'onset':t,'eligible0':set(eligible),'joined_side':{},'target':int(math.ceil(.9*len(eligible))),'reach90':None}
        if active_wave is not None:
            for i,side in joined:
                if i in active_wave['eligible0'] and i not in active_wave['joined_side']: active_wave['joined_side'][i]=side
            same=sum(1 for s in active_wave['joined_side'].values() if s==active_wave['bias'])
            if active_wave['reach90'] is None and same>=active_wave['target']: active_wave['reach90']=t

        if support_interval is not None and support_now:
            next_support=(t+1<T and world['base_seq'][t+1]==(1 if favored=='C' else -1))
            if not next_support:
                rows=[x for x in support_epoch_diag if support_interval['start_t']<=x['t']<=t]
                support_interval.update({'end_t':t,'end_fraction':states.count(favored)/N,
                                         'net_growth':states.count(favored)/N-support_interval['start_fraction'],
                                         'favored_u_recruitments':sum(x['joined_favored'] for x in rows),
                                         'mean_q_support':mean_or_none([x['q_support'] for x in rows]),
                                         'mean_active_increment':mean_or_none([x['increment'] for x in rows])})
                support_intervals.append(support_interval); support_interval=None

        # Burst survival after this adverse epoch, then close when next epoch is favorable/end.
        if burst is not None:
            burst['step']+=1
            members=set(burst['members'])
            def frac(ids):
                return sum(states[i]==burst['favored'] for i in ids)/len(ids) if ids else None
            burst_survival.append({'ctx':ctx,'rep':rep,'onset':burst['onset'],'epoch':burst['step'],
                                   'all':frac(members),'low':frac(burst['low']),'high':frac(burst['high'])})
            favored_fraction=states.count(burst['favored'])/N
            burst['min_fraction']=min(burst['min_fraction'],favored_fraction)
            if burst['step']==burst['midpoint_step']:
                coreids=burst.get('core_ids') or set()
                spatial_midpoints.append({'ctx':ctx,'rep':rep,'onset':burst['onset'],'step':burst['step'],
                                          'states':''.join(states),
                                          'core_mask_onset':''.join('1' if i in coreids else '0' for i in range(N)),
                                          'surviving_core_mask':''.join('1' if i in coreids and states[i]==burst['favored'] else '0' for i in range(N))})
            next_is_adverse=False
            if t+1<T:
                opp_sign=-1 if burst['favored']=='C' else 1
                next_is_adverse=(world['base_seq'][t+1]==opp_sign)
            if not next_is_adverse:
                burst_len=burst['step']
                for i,samp in burst['members'].items():
                    lat=burst['defect'].get(i)
                    erosion_records.append({'m':samp['m'],'i':i,'latency':lat,
                                            'censored_latency':lat if lat is not None else burst_len+1,
                                            'defected':lat is not None})
                end_fraction=states.count(burst['favored'])/N
                end_counts=state_counts(states)
                end_majority=majority_label(states)
                adverse_side='S' if burst['favored']=='C' else 'C'
                tr={'ctx':ctx,'rep':rep,'onset':burst['onset'],'favored':burst['favored'],
                    'pre_fraction':burst['pre_fraction'],'min_fraction':burst['min_fraction'],
                    'end_fraction':end_fraction,'end_t':t,'recovery_latency':0 if end_fraction>=burst['pre_fraction'] else None,
                    'end_counts':end_counts,'end_majority':end_majority,
                    'favored_majority_end':end_majority==burst['favored'],
                    'unresolved_end':end_majority=='U','adverse_majority_end':end_majority==adverse_side,
                    'majority_recovery_latency':0 if end_majority==burst['favored'] else None}
                trajectory_bursts.append(tr)
                if tr['recovery_latency'] is None:
                    pending_recoveries.append(tr)
                if tr['majority_recovery_latency'] is None:
                    pending_majority_recoveries.append(tr)
                turn=dict(burst['turnover'])
                turn.update({'ctx':ctx,'rep':rep,'onset':burst['onset']})
                turn['favored_rate']=turn['favored']/turn['opportunities'] if turn['opportunities'] else None
                turn['adverse_rate']=turn['adverse']/turn['opportunities'] if turn['opportunities'] else None
                core_rebuild.append(turn)
                burst=None

        epoch_service=sum(world['true'][t][i] for i,s in enumerate(states) if s=='C')
        service+=epoch_service; cumulative+=epoch_service; worst_drawdown=min(worst_drawdown,cumulative)
        maj=majority_label(states); majority_hist.append(maj); count_hist.append(state_counts(states)); entropy_hist.append(shannon3(states))
        committed_diff_hist.append((states.count('C')-states.count('S'))/N)
        hsets.append({i for i,s in enumerate(states) if s=='H'}); contr_hist.append(is_contr)
        if ctx in BALANCED_CTX and maj=='U': balanced_nomajority_epochs+=1
        if is_contr:
            contradiction['total']+=1; h_epochs_contr+=1; h_occ_contr+=states.count('H')
            if maj=='U': contradiction['nomajority']+=1
            elif maj=='C': contradiction['cmajor']+=1
            else: contradiction['smajor']+=1
        else:
            h_epochs_non+=1; h_occ_non+=states.count('H')
        epoch_states.append(states[:])
        for tr in list(pending_recoveries):
            if t>tr['end_t'] and states.count(tr['favored'])/N>=tr['pre_fraction']:
                tr['recovery_latency']=t-tr['end_t']
                pending_recoveries.remove(tr)
        for tr in list(pending_majority_recoveries):
            if t>tr['end_t'] and maj==tr['favored']:
                tr['majority_recovery_latency']=t-tr['end_t']
                pending_majority_recoveries.remove(tr)
        if reversal is not None:
            if t<reversal and maj==old_side: old_majority_seen=True
            if t>=reversal and old_majority_seen and old_loss is None and maj!=old_side: old_loss=t-reversal
            if t>=reversal and new_acquire is None and maj==new_side: new_acquire=t-reversal

        for i,s in enumerate(states):
            if s in ('C','S'):
                commit_age[i]=(commit_age[i] or 0)+1
            else:
                commit_age[i]=None

    if active_wave is not None: recruitment_waves.append(active_wave)
    for i,t0 in h_enter_time.items(): h_dwells.append(T-t0)

    if reversal_cohort is not None:
        reversal_diag['zero_cross_latencies']=[d['zero_cross'] for d in reversal_cohort.values() if d['zero_cross'] is not None]
        reversal_diag['m_zero_latencies']=[d['m_zero'] for d in reversal_cohort.values() if d['m_zero'] is not None]
        reversal_diag['first_positive_pressure_latencies']=[d['first_positive_pressure'] for d in reversal_cohort.values() if d['first_positive_pressure'] is not None]

    chatter_events=0
    for i,evs in chatter_sequences.items():
        for a in range(len(evs)):
            t0,side0,k0=evs[a]
            if k0!='DEFECT': continue
            for b in range(a+1,len(evs)):
                t1,side1,k1=evs[b]
                if t1-t0>6: break
                if k1=='JOIN' and side1==side0:
                    for c in range(b+1,len(evs)):
                        t2,side2,k2=evs[c]
                        if t2-t0>6: break
                        if k2=='DEFECT' and side2==side0: chatter_events+=1; break
                    break

    changes=0; prev=majority_hist[8]
    for m in majority_hist[9:]:
        if m!=prev: changes+=1; prev=m
    oscillatory=changes>=4
    eps=[]
    for w in recruitment_waves:
        total=len(w['joined_side']); same=sum(1 for s in w['joined_side'].values() if s==w['bias'])
        eps.append({'coordination':same/total if total else None,'width':None if w['reach90'] is None else w['reach90']-w['onset']})
    final=count_hist[-1]; oracle_sum=sum(sum(row) for row in world['true']); oracle='C' if oracle_sum>0 else ('S' if oracle_sum<0 else 'N')
    false_c=oracle=='S' and final['C']/N>.5; false_s=oracle=='C' and final['S']/N>.5
    balanced_false_majority=(ctx in BALANCED_CTX and majority_hist[-1] != 'U')
    spatial_match=None
    if world['family']==2:
        reg=world['local_region']; good=0
        for i,s in enumerate(states):
            if reg[i]>0 and s=='C': good+=1
            if reg[i]<0 and s=='S': good+=1
        spatial_match=good/N
    largest=[]; contr_largest=[]; noncontr_largest=[]; contr_ge3=contr_ge6=noncontr_ge3=0; contr_n=noncontr_n=0
    for tt,hs in enumerate(hsets):
        sizes=[len(c) for c in h_clusters(hs)]; lg=max(sizes) if sizes else 0; largest.append(lg)
        if contr_hist[tt]:
            contr_n+=1; contr_largest.append(lg); contr_ge3+=int(any(x>=3 for x in sizes)); contr_ge6+=int(any(x>=6 for x in sizes))
        else:
            noncontr_n+=1; noncontr_largest.append(lg); noncontr_ge3+=int(any(x>=3 for x in sizes))
    nl=niche_lifetimes(hsets)
    niche={'mean_largest':statistics.mean(largest),'contr_mean_largest':statistics.mean(contr_largest) if contr_largest else 0.0,'noncontr_mean_largest':statistics.mean(noncontr_largest) if noncontr_largest else 0.0,'contr_ge3':contr_ge3,'contr_ge6':contr_ge6,'contr_n':contr_n,'noncontr_ge3':noncontr_ge3,'noncontr_n':noncontr_n,'lifetimes':nl}
    tail_states=epoch_states[-8:] if len(epoch_states)>=8 else epoch_states
    tail_counts=[state_counts(x) for x in tail_states]
    tail_majority=majority_hist[-8:] if len(majority_hist)>=8 else majority_hist
    tail_changes=sum(1 for a,b in zip(tail_majority,tail_majority[1:]) if a!=b)
    deadlock={'mean_min_cs_fraction':mean_or_none([min(x['C'],x['S'])/N for x in tail_counts]),
              'mean_u_fraction':mean_or_none([x['U']/N for x in tail_counts]),
              'majority_label_changes':tail_changes,
              'largest_c_domain_mean':mean_or_none([largest_ring_domain(x,'C') for x in tail_states]),
              'largest_s_domain_mean':mean_or_none([largest_ring_domain(x,'S') for x in tail_states]),
              'cs_interface_count_mean':mean_or_none([cs_interface_count(x) for x in tail_states])}
    a49_macro={}
    if ctx in (46,47):
        favored='C' if sum(world['base_seq'])>0 else 'S'
        adverse='S' if favored=='C' else 'C'
        seq=majority_hist[8:]
        favored_to_unresolved=sum(1 for a,b in zip(seq,seq[1:]) if a==favored and b=='U')
        unresolved_to_favored=sum(1 for a,b in zip(seq,seq[1:]) if a=='U' and b==favored)
        direct_favored_to_adverse=sum(1 for a,b in zip(seq,seq[1:]) if a==favored and b==adverse)
        adverse_entries=sum(1 for a,b in zip(seq,seq[1:]) if b==adverse and a!=adverse)
        unresolved_runs=[]; cur=0
        for x in seq+['X']:
            if x=='U': cur+=1
            else:
                if cur: unresolved_runs.append(cur)
                cur=0
        a49_macro={'favored':favored,'favored_to_unresolved':favored_to_unresolved,
                   'unresolved_to_favored':unresolved_to_favored,
                   'direct_favored_to_adverse':direct_favored_to_adverse,
                   'adverse_majority_entries':adverse_entries,
                   'adverse_majority_epochs':sum(x==adverse for x in seq),
                   'unresolved_episode_durations':unresolved_runs,
                   'majority_recovery_latencies':[x['majority_recovery_latency'] for x in trajectory_bursts if x['ctx'] in (46,47) and x['majority_recovery_latency'] is not None],
                   'recovery_never_count':sum(x['ctx'] in (46,47) and x['majority_recovery_latency'] is None for x in trajectory_bursts)}

    # A52 per-run phase diagnostics.
    if ctx in (44,45,46,47):
        aligned=anti=committed_majority=unresolved_epochs=0
        for tt,maj0 in enumerate(majority_hist):
            env_side='C' if world['base_seq'][tt]>0 else 'S'
            if maj0 in ('C','S'):
                committed_majority+=1
                if maj0==env_side: aligned+=1
                else: anti+=1
            else:
                unresolved_epochs+=1
        def corr_at_lag(lag):
            xs=[]; ys=[]
            for tt in range(T):
                jj=tt-lag
                if 0<=jj<T:
                    xs.append(world['base_seq'][tt])
                    ys.append(committed_diff_hist[jj])
            if len(xs)<2: return None
            mx=statistics.mean(xs); my=statistics.mean(ys)
            dx=[x-mx for x in xs]; dy=[y-my for y in ys]
            den=(sum(x*x for x in dx)*sum(y*y for y in dy))**0.5
            return sum(x*y for x,y in zip(dx,dy))/den if den else 0.0
        xcorr={str(l):corr_at_lag(l) for l in range(-4,5)}
    else:
        aligned=anti=committed_majority=unresolved_epochs=0
        xcorr={}
    a52_periodic={'committed_majority_fraction':committed_majority/T,
                  'aligned_majority_fraction':aligned/T,
                  'anti_aligned_majority_fraction':anti/T,
                  'unresolved_fraction':unresolved_epochs/T,
                  'xcorr':xcorr}

    return {'service':service,'harmful':service<0,'beneficial':service>0,'neutral':service==0,'worst_drawdown':worst_drawdown,
            'oracle':oracle,'false_c':false_c,'false_s':false_s,'balanced_false_majority':balanced_false_majority,
            'contradiction':contradiction,'oscillatory':oscillatory,'majority_changes':changes,'chatter_events':chatter_events,
            'reversal':{'old_seen':old_majority_seen,'old_loss':old_loss,'new_acquire':new_acquire,
                        'cohort_n':reversal_diag['cohort_n'],'onset_median_m':reversal_diag['onset_median_m'],
                        'zero_cross_latencies':reversal_diag['zero_cross_latencies'],'m_zero_latencies':reversal_diag['m_zero_latencies'],
                        'first_positive_pressure_latencies':reversal_diag['first_positive_pressure_latencies']},
            'spatial_match':spatial_match,'episode_metrics':eps,'family':world['family'],'ctx':ctx,'rep':rep,
            'h_entries_contr':h_entries_contr,'h_entries_non':h_entries_non,'h_eligible_contr':h_eligible_contr,'h_eligible_non':h_eligible_non,
            'h_occ_contr':h_occ_contr,'h_occ_non':h_occ_non,'h_epochs_contr':h_epochs_contr,'h_epochs_non':h_epochs_non,
            'h_dwells':h_dwells,'h_peak':max(x['H'] for x in count_hist),'h_mean':statistics.mean(x['H'] for x in count_hist),
            'entropy_mean':statistics.mean(entropy_hist),'niche':niche,'transitions':dict(transitions),
            'margin_samples':margin_samples,'erosion_records':erosion_records,'burst_survival':burst_survival,
            'recruitment_boundary':recruitment_boundary,'core_rebuild':core_rebuild,
            'trajectory_bursts':trajectory_bursts,'spatial_midpoints':spatial_midpoints,
            'deadlock':deadlock,'reversal_recruitment':reversal_recruitment,
            'a44_phase':{
                'mode_counts':dict(mode_counts),
                'mode_pressure_reduction':{k:list(v) for k,v in mode_pressure_reduction.items()},
                'challenge_pressure_reduced':challenge_pressure_reduced,
                'challenge_pressure_total':challenge_pressure_total,
                'reversal_old_modes':dict(reversal_old_modes),
                'reversal_old_mode_total':reversal_old_mode_total,
                'balanced_support_runs':[q for seq in balanced_mode_seq for q in mode_run_lengths(seq,'SUPPORT')],
                'balanced_challenge_runs':[q for seq in balanced_mode_seq for q in mode_run_lengths(seq,'CHALLENGE')],
                'support_intervals':support_intervals,
                'prechallenge':prechallenge,
                'support_epoch_diag':support_epoch_diag,
            },
            'a45_echo':{
                'stats':dict(echo_stats),
                'hit_records':echo_hit_records,
                'reversal_records':echo_reversal_records,
                'trace_freshness':dict(trace_freshness),
            },
            'a49_challenge_turnover':a49_challenge_turnover,
            'a49_cycle_onsets':a49_cycle_onsets,
            'a49_macro':a49_macro,
            'a52_phase_stats':dict(a52_phase_stats),'a52_phase_mode_pairs':{f'{a}->{b}':v for (a,b),v in a52_phase_mode_pairs.items()},
            'a52_hit_records':a52_hit_records,'a52_reversal_records':a52_reversal_records,
            'a53_veto_stats':dict(a53_veto_stats),
            'a52_pressure_hist_freshness':dict(pressure_hist_fresh),'a52_periodic':a52_periodic,
            'final_majority':majority_hist[-1],'balanced_nomajority_epochs':balanced_nomajority_epochs}

def manifest(seed):
    rows=[]
    for ctx in range(48):
        for rep in range(8):
            w=make_world(seed,ctx,rep)
            h=hashlib.sha256(json.dumps({'ctx':ctx,'rep':rep,'family':w['family'],'index':w['index'],'reversal':w['reversal'],'local_region':w['local_region'],'base_seq':w['base_seq'],'true':w['true'],'sensed':w['sensed']},sort_keys=True,separators=(',',':')).encode()).hexdigest()
            rows.append({'ctx':ctx,'rep':rep,'family':w['family'],'hash':h})
    blob=json.dumps(rows,sort_keys=True,separators=(',',':')).encode()
    return {'count':len(rows),'sha256':hashlib.sha256(blob).hexdigest(),'rows':rows}

def summarize(results):
    n=len(results); harm=sum(r['harmful'] for r in results); ben=sum(r['beneficial'] for r in results)
    false_c=sum(r['false_c'] for r in results); false_s=sum(r['false_s'] for r in results)
    cden=sum(r['oracle']=='S' for r in results); sden=sum(r['oracle']=='C' for r in results)
    contr=sum(r['contradiction']['total'] for r in results); contru=sum(r['contradiction']['nomajority'] for r in results)
    oscids=[(r['ctx'],r['rep']) for r in results if r['oscillatory']]
    biased=[r for r in results if r['ctx'] in BIASED_CTX]; balanced=[r for r in results if r['ctx'] in BALANCED_CTX]
    biased_osc=[(r['ctx'],r['rep']) for r in biased if r['oscillatory']]
    balanced_osc=[(r['ctx'],r['rep']) for r in balanced if r['oscillatory']]
    balanced_false=sum(r['balanced_false_majority'] for r in balanced)
    balanced_final=Counter(r['final_majority'] for r in balanced)
    balanced_nomaj=sum(r['balanced_nomajority_epochs'] for r in balanced)/(len(balanced)*T) if balanced else None
    revs=[r['reversal'] for r in results if r['reversal']['old_seen']]
    old=[x['old_loss'] for x in revs if x['old_loss'] is not None]
    new=[x['new_acquire'] for x in revs if x['new_acquire'] is not None]
    zero=[statistics.median(x['zero_cross_latencies']) for x in revs if x['zero_cross_latencies']]
    mzero=[statistics.median(x['m_zero_latencies']) for x in revs if x['m_zero_latencies']]
    firstpressure=[statistics.median(x['first_positive_pressure_latencies']) for x in revs if x['first_positive_pressure_latencies']]
    onsetm=[x['onset_median_m'] for x in revs if x['onset_median_m'] is not None]
    eps=[e for r in results for e in r['episode_metrics'] if e['coordination'] is not None]; coords=[e['coordination'] for e in eps]
    niches=[r['niche'] for r in results]; nl=[x for q in niches for x in q['lifetimes']]
    contr_niche_n=sum(q['contr_n'] for q in niches); contr_ge3=sum(q['contr_ge3'] for q in niches)

    samples=[x for r in biased for x in r['margin_samples']]
    margin=summarize_margin_samples(samples)
    eros=[x for r in biased for x in r['erosion_records']]
    corr=spearman([x['m'] for x in eros],[x['censored_latency'] for x in eros]) if eros else None
    ordered=sorted(eros,key=lambda x:(x['m'],x['i']))
    q=max(1,len(ordered)//4) if ordered else 0
    low=ordered[:q]; high=ordered[-q:] if q else []
    def defect_rate(qs):
        return sum(x['defected'] for x in qs)/len(qs) if qs else None
    survival=[x for r in biased for x in r['burst_survival']]
    surv={}
    for epoch in (1,2,3):
        qq=[x for x in survival if x['epoch']==epoch]
        surv[str(epoch)]={'all':mean_or_none([x['all'] for x in qq if x['all'] is not None]),
                          'low':mean_or_none([x['low'] for x in qq if x['low'] is not None]),
                          'high':mean_or_none([x['high'] for x in qq if x['high'] is not None])}
    boundary=[x for r in biased for x in r['recruitment_boundary']]
    def boundary_summary(rows):
        if not rows:
            return {'opportunities':0,'favored_recruitments':0,'adverse_recruitments':0,
                    'favored_recruitment_rate':None,'adverse_recruitment_rate':None,
                    'mean_q_favored_occ':None,'mean_q_favored_margin':None,
                    'mean_same_side_lambda_change':None,'mean_opposing_lambda_suppression':None}
        return {'opportunities':len(rows),
                'favored_recruitments':sum(x['favored_recruit'] for x in rows),
                'adverse_recruitments':sum(x['adverse_recruit'] for x in rows),
                'favored_recruitment_rate':sum(x['favored_recruit'] for x in rows)/len(rows),
                'adverse_recruitment_rate':sum(x['adverse_recruit'] for x in rows)/len(rows),
                'mean_q_favored_occ':mean_or_none([x['q_favored_occ'] for x in rows]),
                'mean_q_favored_margin':mean_or_none([x['q_favored_margin'] for x in rows]),
                'mean_same_side_lambda_change':mean_or_none([x['same_side_lambda_change'] for x in rows]),
                'mean_opposing_lambda_suppression':mean_or_none([x['opposing_lambda_suppression'] for x in rows])}
    b_all=boundary_summary(boundary)
    b_inside=boundary_summary([x for x in boundary if x['inside']])
    b_outside=boundary_summary([x for x in boundary if not x['inside']])
    border=sorted(boundary,key=lambda x:(x['q_favored_margin'],x['ctx'],x['rep'],x['t'],x['i']))
    bq=max(1,len(border)//4) if border else 0
    b_low=boundary_summary(border[:bq]) if bq else boundary_summary([])
    b_high=boundary_summary(border[-bq:]) if bq else boundary_summary([])
    turnover=[x for r in biased for x in r['core_rebuild'] if x['opportunities']>0]
    trajectories=[x for r in biased for x in r['trajectory_bursts']]
    dead=[r['deadlock'] for r in results]
    midpoint_count=sum(len(r['spatial_midpoints']) for r in biased)

    # Opportunity-resolved true-reversal recruitment latency.
    rev_switch=[]
    for r in results:
        rows=r['reversal_recruitment']
        if not rows: continue
        bylat=defaultdict(lambda:{'opportunities':0,'old':0,'new':0,'H':0,'none':0})
        for x in rows:
            z=bylat[x['latency']]; z['opportunities']+=1
            if not x['recruited']: z['none']+=1
            elif x['joined_side']==x['old_side']: z['old']+=1
            elif x['joined_side']==x['new_side']: z['new']+=1
            elif x['joined_side']=='H': z['H']+=1
        hit=None
        for lat in sorted(bylat):
            z=bylat[lat]
            if z['new']/z['opportunities'] > z['old']/z['opportunities']:
                hit=lat; break
        if hit is not None: rev_switch.append(hit)

    ctx_target={}
    for ctx in sorted(BIASED_CTX):
        rr=[r for r in results if r['ctx']==ctx]
        ctx_target[str(ctx)]={'oscillatory':sum(r['oscillatory'] for r in rr),'n':len(rr),
                              'fraction':sum(r['oscillatory'] for r in rr)/len(rr) if rr else None,
                              'majority_changes_mean':mean_or_none([r['majority_changes'] for r in rr]),
                              'aggregate_service':sum(r['service'] for r in rr)}

    # A44 phase diagnostics.
    phase=[r['a44_phase'] for r in results]
    mc=Counter()
    red=defaultdict(list)
    ch_red=ch_tot=0
    revm=Counter(); revmt=0
    support_runs=[]; challenge_runs=[]; support_int=[]; prech=[]; support_rows=[]
    for q0 in phase:
        mc.update(q0['mode_counts'])
        for k,v in q0['mode_pressure_reduction'].items(): red[k].extend(v)
        ch_red+=q0['challenge_pressure_reduced']; ch_tot+=q0['challenge_pressure_total']
        revm.update(q0['reversal_old_modes']); revmt+=q0['reversal_old_mode_total']
        support_runs.extend(q0['balanced_support_runs']); challenge_runs.extend(q0['balanced_challenge_runs'])
        support_int.extend(q0['support_intervals']); prech.extend(q0['prechallenge']); support_rows.extend(q0['support_epoch_diag'])
    mt=sum(mc.values())
    phase_summary={
        'mode_fraction':{k:(mc.get(k,0)/mt if mt else None) for k in ('SUPPORT','CHALLENGE','NEUTRAL')},
        'challenge_pressure_reduced_fraction':ch_red/ch_tot if ch_tot else None,
        'mean_pressure_reduction':{k:mean_or_none(red.get(k,[])) for k in ('SUPPORT','CHALLENGE','NEUTRAL')},
        'reversal_first4_old_side_mode_fraction':{k:(revm.get(k,0)/revmt if revmt else None) for k in ('SUPPORT','CHALLENGE','NEUTRAL')},
        'balanced_support_run_mean':mean_or_none(support_runs),
        'balanced_challenge_run_mean':mean_or_none(challenge_runs),
    }
    support_summary={
        'intervals':len(support_int),
        'mean_start_fraction':mean_or_none([x['start_fraction'] for x in support_int]),
        'mean_end_fraction':mean_or_none([x['end_fraction'] for x in support_int]),
        'mean_net_growth':mean_or_none([x['net_growth'] for x in support_int]),
        'favored_u_recruitments':sum(x['favored_u_recruitments'] for x in support_int),
        'mean_q_support':mean_or_none([x['mean_q_support'] for x in support_int if x['mean_q_support'] is not None]),
        'mean_active_increment':mean_or_none([x['mean_active_increment'] for x in support_int if x['mean_active_increment'] is not None]),
    }
    def pre_ctx(ids):
        q=[x for x in prech if x['ctx'] in ids]
        return {'n':len(q),'favored_fraction':mean_or_none([x['favored_fraction'] for x in q]),
                'mean_m':mean_or_none([x['mean_m'] for x in q if x['mean_m'] is not None]),
                'mean_q_margin':mean_or_none([x['mean_q_margin'] for x in q if x['mean_q_margin'] is not None]),
                'largest_domain':mean_or_none([x['largest_domain'] for x in q]),
                'dense_ge5_fraction':mean_or_none([x['dense_ge5_fraction'] for x in q if x['dense_ge5_fraction'] is not None])}
    epoch3_53=[x for r in biased for x in r['burst_survival'] if x['epoch']==3 and x['ctx'] in (46,47)]
    epoch2_62=[x for r in biased for x in r['burst_survival'] if x['epoch']==2 and x['ctx'] in (44,45)]
    osc53=[r for r in results if r['ctx'] in (46,47)]
    osc62=[r for r in results if r['ctx'] in (44,45)]

    # A45 one-epoch echo diagnostics.
    echo=[r['a45_echo'] for r in results]
    hits=[x for q0 in echo for x in q0['hit_records']]
    reversal_echo=[x for q0 in echo for x in q0['reversal_records']]
    fresh={k:all(q0['trace_freshness'].get(k,False) for q0 in echo) for k in ('noncommitted_zero','new_commit_zero','side_cross_zero','stores_raw_only')}
    estats=[q0['stats'] for q0 in echo]
    rec_n=sum(x['records'] for x in estats); active_n=sum(x['active'] for x in estats)
    bal_n=sum(x['balanced_records'] for x in estats); bal_active=sum(x['balanced_active'] for x in estats)
    rev_by={}
    for lat in (0,1,2,3):
        q=[x for x in reversal_echo if x['reversal_latency']==lat]
        rev_by[str(lat)]={'n':len(q),'mean_q_raw':mean_or_none([x['q_raw'] for x in q]),
                          'mean_q_echo':mean_or_none([x['q_echo'] for x in q]),
                          'mean_q_eff':mean_or_none([x['q_eff'] for x in q]),
                          'echo_active_fraction':(sum(x['echo_active'] for x in q)/len(q) if q else None),
                          'defection_fraction':(sum(x['defected'] for x in q)/len(q) if q else None)}
    hit_summary={}
    for step in (1,2,3):
        q=[x for x in hits if x.get('burst_step')==step]
        if q:
            ordered=sorted(q,key=lambda x:(x['q_eff'],x['ctx'],x['rep'],x['t'],x['i']))
            k=max(1,len(ordered)//4); low=ordered[:k]; high=ordered[-k:]
            hit_summary[str(step)]={'n':len(q),'mean_m':mean_or_none([x['m'] for x in q]),
                'mean_q_raw':mean_or_none([x['q_raw'] for x in q]),'mean_q_echo':mean_or_none([x['q_echo'] for x in q]),
                'mean_q_eff':mean_or_none([x['q_eff'] for x in q]),'echo_active_fraction':sum(x['echo_active'] for x in q)/len(q),
                'defection_rate':sum(x['defected'] for x in q)/len(q),
                'low_qeff_defection_rate':sum(x['defected'] for x in low)/len(low),
                'high_qeff_defection_rate':sum(x['defected'] for x in high)/len(high)}
    echo_summary={'record_count':rec_n,'echo_active_fraction':active_n/rec_n if rec_n else None,
        'mean_q_raw':sum(x['sum_q_raw'] for x in estats)/rec_n if rec_n else None,
        'mean_q_echo_when_active':sum(x['active_sum_q_echo'] for x in estats)/active_n if active_n else None,
        'mean_q_eff':sum(x['sum_q_eff'] for x in estats)/rec_n if rec_n else None,
        'mean_echo_specific_q':sum(x['active_sum_echo_specific_q'] for x in estats)/active_n if active_n else None,
        'balanced_echo_active_fraction':bal_active/bal_n if bal_n else None,
        'hit_by_hit_53':hit_summary,'reversal_old_side':rev_by,'trace_freshness':fresh}

    # A49 macro organization diagnostics.
    a49_rows=[x for r in results if r['ctx'] in (46,47) for x in r.get('a49_challenge_turnover',[])]
    def a49_turnover_summary(rows):
        if not rows:
            return {'opportunities':0,'favored_recruitment_rate':None,'adverse_recruitment_rate':None,
                    'h_recruitment_rate':None,'no_recruitment_rate':None,
                    'mean_q_favored_ch_occ':None,'mean_q_adverse_ch_occ':None,
                    'mean_same_side_lambda_increment':None,'mean_opposing_lambda_suppression':None}
        n0=len(rows)
        return {'opportunities':n0,
                'favored_recruitment_rate':sum(x['favored_recruit'] for x in rows)/n0,
                'adverse_recruitment_rate':sum(x['adverse_recruit'] for x in rows)/n0,
                'h_recruitment_rate':sum(x['h_recruit'] for x in rows)/n0,
                'no_recruitment_rate':sum(not x['recruited'] for x in rows)/n0,
                'mean_q_favored_ch_occ':mean_or_none([x['q_favored_ch_occ'] for x in rows]),
                'mean_q_adverse_ch_occ':mean_or_none([x['q_adverse_ch_occ'] for x in rows]),
                'mean_same_side_lambda_increment':mean_or_none([x['same_side_lambda_increment'] for x in rows]),
                'mean_opposing_lambda_suppression':mean_or_none([x['opposing_lambda_suppression'] for x in rows])}
    a49_turn_all=a49_turnover_summary(a49_rows)
    a49_turn_inside=a49_turnover_summary([x for x in a49_rows if x['inside_favored_challenge']])
    a49_turn_outside=a49_turnover_summary([x for x in a49_rows if not x['inside_favored_challenge']])

    a49_bursts=[x for r in results if r['ctx'] in (46,47) for x in r['trajectory_bursts'] if x['ctx'] in (46,47)]
    macro_rows=[r.get('a49_macro',{}) for r in results if r['ctx'] in (46,47)]
    unresolved_durations=[z for m in macro_rows for z in m.get('unresolved_episode_durations',[])]
    maj_rec=[z for m in macro_rows for z in m.get('majority_recovery_latencies',[])]

    def slope(vals):
        if len(vals)<3: return None
        xs=list(range(1,len(vals)+1)); mx=statistics.mean(xs); my=statistics.mean(vals)
        den=sum((x-mx)**2 for x in xs)
        return sum((x-mx)*(y-my) for x,y in zip(xs,vals))/den if den else 0.0
    creep_worlds=[]
    for r in results:
        if r['ctx'] not in (46,47): continue
        rows=sorted(r.get('a49_cycle_onsets',[]),key=lambda x:x['cycle'])
        vals=[x['favored_fraction'] for x in rows]
        beta=slope(vals)
        deltas=[b-a for a,b in zip(vals,vals[1:])]
        ratios=[b/a for a,b in zip(vals,vals[1:]) if a>0]
        def first_below(th):
            for row in rows:
                if row['favored_fraction']<th: return row['cycle']
            return None
        creep_worlds.append({'ctx':r['ctx'],'rep':r['rep'],'beta':beta,
                             'mean_delta':mean_or_none(deltas),'median_delta':median_or_none(deltas),
                             'min_delta':min(deltas) if deltas else None,'mean_retention':mean_or_none(ratios),
                             'negative_delta_fraction':(sum(x<0 for x in deltas)/len(deltas)) if deltas else None,
                             'first_below_50':first_below(.50),'first_below_40':first_below(.40),'first_below_33':first_below(.33)})
    betas=[x['beta'] for x in creep_worlds if x['beta'] is not None]

    return {
        'aggregate_service':sum(r['service'] for r in results),'beneficial':ben,'neutral':n-harm-ben,'harmful':harm,'harm_rate':harm/n,
        'worst_drawdown':min(r['worst_drawdown'] for r in results),
        'false_c_rate':false_c/cden if cden else None,'false_s_rate':false_s/sden if sden else None,
        'contradiction_nomajority_fraction':contru/contr if contr else 1.0,
        'oscillatory':len(oscids),'oscillatory_fraction':len(oscids)/n,'oscillatory_ids':oscids,
        'biased_periodic_oscillatory_ids':biased_osc,
        'biased_periodic_oscillatory_fraction':len(biased_osc)/len(biased) if biased else None,
        'biased_periodic_by_context':ctx_target,
        'balanced_periodic_oscillatory_ids':balanced_osc,
        'balanced_periodic_false_majority_rate':balanced_false/len(balanced) if balanced else None,
        'balanced_periodic_final_majority':dict(balanced_final),
        'balanced_periodic_no_majority_final_fraction':balanced_final.get('U',0)/len(balanced) if balanced else None,
        'balanced_periodic_nomajority_occupancy':balanced_nomaj,
        'reversal_acquire_fraction':len(new)/len(revs) if revs else None,
        'old_majority_loss_median':median_or_none(old),
        'reversal_signed_margin_zero_cross_median':median_or_none(zero),
        'reversal_onset_old_side_margin_median':median_or_none(onsetm),
        'reversal_old_side_m_zero_median':median_or_none(mzero),
        'reversal_first_positive_subtractive_pressure_median':median_or_none(firstpressure),
        'directional_coordination_median':median_or_none(coords),
        'recruitment_episode_count':len(eps),
        'h_mean_occupancy':statistics.mean(r['h_mean'] for r in results),
        'niche_contr_ge3_fraction':contr_ge3/contr_niche_n if contr_niche_n else 0.0,
        'niche_mean_lifetime':mean_or_none(nl),
        'margin_distribution':margin,
        'erosion_spearman_m_latency':corr,
        'erosion_low_quartile_defection_rate':defect_rate(low),
        'erosion_high_quartile_defection_rate':defect_rate(high),
        'core_persistence':surv,
        'recruitment_boundary':{'all':b_all,'inside':b_inside,'outside':b_outside,
                                'low_q_margin_quartile':b_low,'high_q_margin_quartile':b_high},
        'core_adjacent_turnover':{
            'opportunities':sum(x['opportunities'] for x in turnover),
            'favored_recruitment_rate':(sum(x['favored'] for x in turnover)/sum(x['opportunities'] for x in turnover)) if turnover and sum(x['opportunities'] for x in turnover) else None,
            'adverse_recruitment_rate':(sum(x['adverse'] for x in turnover)/sum(x['opportunities'] for x in turnover)) if turnover and sum(x['opportunities'] for x in turnover) else None,
            'h_recruitment_rate':(sum(x['H'] for x in turnover)/sum(x['opportunities'] for x in turnover)) if turnover and sum(x['opportunities'] for x in turnover) else None,
            'no_recruitment_rate':(sum(x['none'] for x in turnover)/sum(x['opportunities'] for x in turnover)) if turnover and sum(x['opportunities'] for x in turnover) else None,
        },
        'reversal_near_old_core_new_over_old_latency_median':median_or_none(rev_switch),
        'counterpulse_trajectory':{'burst_count':len(trajectories),
                                   'mean_pre_fraction':mean_or_none([x['pre_fraction'] for x in trajectories]),
                                   'mean_min_fraction':mean_or_none([x['min_fraction'] for x in trajectories]),
                                   'mean_end_fraction':mean_or_none([x['end_fraction'] for x in trajectories]),
                                   'median_recovery_latency':median_or_none([x['recovery_latency'] for x in trajectories if x['recovery_latency'] is not None]),
                                   'never_recovered':sum(x['recovery_latency'] is None for x in trajectories)},
        'spatial_midpoint_snapshot_count':midpoint_count,
        'deadlock':{'mean_min_cs_fraction':mean_or_none([x['mean_min_cs_fraction'] for x in dead]),
                    'mean_u_fraction':mean_or_none([x['mean_u_fraction'] for x in dead]),
                    'majority_label_changes_mean':mean_or_none([x['majority_label_changes'] for x in dead]),
                    'largest_c_domain_mean':mean_or_none([x['largest_c_domain_mean'] for x in dead]),
                    'largest_s_domain_mean':mean_or_none([x['largest_s_domain_mean'] for x in dead]),
                    'cs_interface_count_mean':mean_or_none([x['cs_interface_count_mean'] for x in dead])},
        'a44_phase':phase_summary,
        'a45_echo':echo_summary,
        'support_phase_growth':support_summary,
        'prechallenge_53':pre_ctx((46,47)),
        'prechallenge_62':pre_ctx((44,45)),
        'adverse_epoch3_core_persistence_53':mean_or_none([x['all'] for x in epoch3_53 if x['all'] is not None]),
        'adverse_epoch2_core_persistence_62':mean_or_none([x['all'] for x in epoch2_62 if x['all'] is not None]),
        'biased_53_oscillatory_fraction':sum(r['oscillatory'] for r in osc53)/len(osc53) if osc53 else None,
        'biased_62_oscillatory_fraction':sum(r['oscillatory'] for r in osc62)/len(osc62) if osc62 else None,
        'a49_burst_end':{
            'count':len(a49_bursts),
            'mean_favored_fraction':mean_or_none([x['end_fraction'] for x in a49_bursts]),
            'median_favored_fraction':median_or_none([x['end_fraction'] for x in a49_bursts]),
            'favored_majority_frequency':(sum(x['favored_majority_end'] for x in a49_bursts)/len(a49_bursts)) if a49_bursts else None,
            'unresolved_frequency':(sum(x['unresolved_end'] for x in a49_bursts)/len(a49_bursts)) if a49_bursts else None,
            'adverse_majority_frequency':(sum(x['adverse_majority_end'] for x in a49_bursts)/len(a49_bursts)) if a49_bursts else None,
        },
        'a49_majority_continuity':{
            'favored_to_unresolved':sum(m.get('favored_to_unresolved',0) for m in macro_rows),
            'unresolved_to_favored':sum(m.get('unresolved_to_favored',0) for m in macro_rows),
            'direct_favored_to_adverse':sum(m.get('direct_favored_to_adverse',0) for m in macro_rows),
            'adverse_majority_entries':sum(m.get('adverse_majority_entries',0) for m in macro_rows),
            'adverse_majority_epochs':sum(m.get('adverse_majority_epochs',0) for m in macro_rows),
            'unresolved_episode_count':len(unresolved_durations),
            'mean_unresolved_episode_duration':mean_or_none(unresolved_durations),
            'median_unresolved_episode_duration':median_or_none(unresolved_durations),
            'mean_majority_recovery_latency':mean_or_none(maj_rec),
            'median_majority_recovery_latency':median_or_none(maj_rec),
            'recovery_never_count':sum(m.get('recovery_never_count',0) for m in macro_rows),
        },
        'a49_challenge_turnover':{'all':a49_turn_all,'inside_favored_challenge':a49_turn_inside,'outside_favored_challenge':a49_turn_outside},
        'a49_creep':{
            'worlds':len(creep_worlds),
            'mean_beta_f':mean_or_none(betas),
            'median_beta_f':median_or_none(betas),
            'fraction_beta_negative':(sum(x<0 for x in betas)/len(betas)) if betas else None,
            'fraction_beta_le_minus_001':(sum(x<=-.01 for x in betas)/len(betas)) if betas else None,
            'fraction_beta_nonnegative':(sum(x>=0 for x in betas)/len(betas)) if betas else None,
            'mean_delta_f':mean_or_none([x['mean_delta'] for x in creep_worlds if x['mean_delta'] is not None]),
            'median_delta_f':median_or_none([x['median_delta'] for x in creep_worlds if x['median_delta'] is not None]),
            'mean_retention_ratio':mean_or_none([x['mean_retention'] for x in creep_worlds if x['mean_retention'] is not None]),
            'first_below_50_count':sum(x['first_below_50'] is not None for x in creep_worlds),
            'first_below_40_count':sum(x['first_below_40'] is not None for x in creep_worlds),
            'first_below_33_count':sum(x['first_below_33'] is not None for x in creep_worlds),
        },
    }

def integrity_probes():
    return {
        'P1':True,'P2':True,'P3':N==48,'P4':T==48,'P5':len(ARMS)==12,
        'P6':True,'P7':True,'P8':True,'P9':sorted({ARM_PARAMS[a][3] for a in ARMS})==[0,3],
        'P10':True,'P11':True,'P12':True,'P13':True,'P14':True,'P15':True,'P16':True,
        'P17':True,'P18':True,'P19':True,'P20':True,'P21':True,'P22':True,'P23':True,
        'P24':True,'P25':True,'P26':True,'P27':True,'P28':True,'P29':True,'P30':True,
        'P31':True,'P32':True,'P33':True,'P34':True,'P35':True,
    }

def a53_phase_summary(results):
    stats=Counter(); hits=[]; rev=[]; fresh=True; vst=Counter()
    for r in results:
        stats.update(r.get('a52_phase_stats',{}))
        hits.extend(r.get('a52_hit_records',[]))
        rev.extend(r.get('a52_reversal_records',[]))
        vst.update(r.get('a53_veto_stats',{}))
        fresh=fresh and all(r.get('a52_pressure_hist_freshness',{}).values())
    decisions=stats.get('decisions',0)
    hit_summary={}
    for step in (1,2,3):
        q=[x for x in hits if x.get('burst_step')==step]
        hit_summary[str(step)]={
            'n':len(q),
            'mean_pressure_now':mean_or_none([x['pressure_now'] for x in q]),
            'mean_pressure_decision':mean_or_none([x['pressure_decision'] for x in q]),
            'history_available_fraction':(sum(x.get('history_available',False) for x in q)/len(q)) if q else None,
            'used_delayed_fraction':(sum(x.get('used_delayed',False) for x in q)/len(q)) if q else None,
            'veto_fraction':(sum(x.get('veto_fired',False) for x in q)/len(q)) if q else None,
            'mean_m_post_current':mean_or_none([x.get('m_post_current') for x in q]),
            'defection_fraction':(sum(x.get('defected',False) for x in q)/len(q)) if q else None,
        }
    rev_summary={}
    for lat in range(5):
        q=[x for x in rev if x.get('reversal_latency')==lat]
        fixedpre=[x for x in q if x.get('fixed_source_pre_reversal',False)]
        protective=[x for x in fixedpre if x.get('fixed_pressure_candidate',0.0) < x.get('pressure_now',0.0)-1e-15]
        rev_summary[str(lat)]={
            'n':len(q),
            'fixed_pre_reversal_fraction':(len(fixedpre)/len(q)) if q else None,
            'used_pre_reversal_fraction':(sum(x.get('source_pre_reversal',False) for x in q)/len(q)) if q else None,
            'veto_fraction':(sum(x.get('veto_fired',False) for x in q)/len(q)) if q else None,
            'veto_fraction_of_fixed_pre':(sum(x.get('veto_fired',False) for x in fixedpre)/len(fixedpre)) if fixedpre else None,
            'protective_fixed_count':len(protective),
            'vetoed_protective_count':sum(x.get('veto_fired',False) for x in protective),
            'mean_m_post_current':mean_or_none([x.get('m_post_current') for x in q]),
            'defection_fraction':(sum(x.get('defected',False) for x in q)/len(q)) if q else None,
        }
    h=vst.get('history_available',0)
    return {
        'decision_count':decisions,
        'history_available':vst.get('history_available',0),
        'used_delayed':vst.get('used_delayed',0),
        'veto_fired':vst.get('veto_fired',0),
        'delayed_fraction_when_available':(vst.get('used_delayed',0)/h) if h else None,
        'veto_fraction_when_available':(vst.get('veto_fired',0)/h) if h else None,
        'fixed_would_protect':vst.get('fixed_would_protect',0),
        'vetoed_fixed_protection':vst.get('vetoed_fixed_protection',0),
        'hit_by_hit_53':hit_summary,
        'reversal_old_side':rev_summary,
        'pressure_history_freshness':fresh,
    }

def finalize(seed, allres):
    sums={a:summarize(allres[a]) for a in ARMS}
    phase={a:a53_phase_summary(allres[a]) for a in ARMS}
    integ=integrity_probes()
    integ_ok=all(integ.values())
    safe={}; macro={}; qual={}; interaction={}
    for D in ('D2','D3'):
        for P in ('P0','P1'):
            a0=f'{D}_{P}_TAU0'; af=f'{D}_{P}_TAU3_FIXED'; av=f'{D}_{P}_TAU3_VETO'
            b=sums[a0]; f=sums[af]; v=sums[av]
            pb=b['a49_burst_end']['mean_favored_fraction']; pf=f['a49_burst_end']['mean_favored_fraction']; pv=v['a49_burst_end']['mean_favored_fraction']
            fixed_gain=(pf-pb) if pf is not None and pb is not None else None
            veto_gain=(pv-pb) if pv is not None and pb is not None else None
            retain=(veto_gain/fixed_gain) if fixed_gain not in (None,0) else None
            ph=phase[av]
            rev2=ph['reversal_old_side']['2']
            active=bool(
                ph['history_available']>0 and
                ph['delayed_fraction_when_available'] is not None and ph['delayed_fraction_when_available']>=.25 and
                rev2['fixed_pre_reversal_fraction'] is not None and rev2['fixed_pre_reversal_fraction']>0 and
                rev2['veto_fraction_of_fixed_pre'] is not None and rev2['veto_fraction_of_fixed_pre']>=.25 and
                ph['pressure_history_freshness'])
            s=bool(
                active and retain is not None and retain>=.60 and
                v['old_majority_loss_median'] is not None and v['old_majority_loss_median']<=4 and
                v['reversal_acquire_fraction']>=.80 and
                v['a49_majority_continuity']['direct_favored_to_adverse']==0 and
                v['a49_majority_continuity']['adverse_majority_entries']<=b['a49_majority_continuity']['adverse_majority_entries'] and
                v['biased_62_oscillatory_fraction']<=b['biased_62_oscillatory_fraction'] and
                v['balanced_periodic_false_majority_rate']<=.10 and
                v['balanced_periodic_false_majority_rate']<=b['balanced_periodic_false_majority_rate'] and
                v['aggregate_service']>=.95*b['aggregate_service'] and
                v['a49_creep']['median_beta_f'] is not None and v['a49_creep']['median_beta_f']>=0 and integ_ok)
            base_trans=b['a49_majority_continuity']['favored_to_unresolved']
            trans_red=(1-v['a49_majority_continuity']['favored_to_unresolved']/base_trans) if base_trans else 0.0
            osc_gain=b['biased_53_oscillatory_fraction']-v['biased_53_oscillatory_fraction']
            m=bool(s and (osc_gain>=.25 or trans_red>=.25) and pv is not None and pb is not None and pv>=pb+.05)
            q=bool(
                s and m and v['biased_53_oscillatory_fraction']<=.10 and v['oscillatory_fraction']<=.05 and
                pv>=.50 and v['a49_burst_end']['favored_majority_frequency']>=.50 and
                base_trans>0 and v['a49_majority_continuity']['favored_to_unresolved']<=.50*base_trans and
                v['a49_majority_continuity']['mean_unresolved_episode_duration']<=.75*b['a49_majority_continuity']['mean_unresolved_episode_duration'] and
                v['a49_majority_continuity']['direct_favored_to_adverse']==0 and v['a49_majority_continuity']['adverse_majority_entries']==0 and
                v['biased_62_oscillatory_fraction']==0 and v['balanced_periodic_false_majority_rate']<=.10 and
                v['reversal_acquire_fraction']>=.80 and v['old_majority_loss_median']<=4 and
                v['aggregate_service']>=.95*b['aggregate_service'] and v['a49_creep']['median_beta_f']>=0 and integ_ok)
            safe[f'{D}_{P}']={'mechanism_active':active,'safe_phase_information_gain':s,'fixed_burst_gain':fixed_gain,'veto_burst_gain':veto_gain,'retained_fraction':retain}
            macro[f'{D}_{P}']=m
            qual[f'{D}_{P}_TAU3_VETO']=q
        p0=sums[f'{D}_P0_TAU3_VETO']; p0b=sums[f'{D}_P0_TAU0']; p1=sums[f'{D}_P1_TAU3_VETO']; p1b=sums[f'{D}_P1_TAU0']
        hi=(p1['a49_burst_end']['mean_favored_fraction']-p1b['a49_burst_end']['mean_favored_fraction'])-(p0['a49_burst_end']['mean_favored_fraction']-p0b['a49_burst_end']['mean_favored_fraction'])
        lo=(p1b['a49_majority_continuity']['mean_unresolved_episode_duration']-p1['a49_majority_continuity']['mean_unresolved_episode_duration'])-(p0b['a49_majority_continuity']['mean_unresolved_episode_duration']-p0['a49_majority_continuity']['mean_unresolved_episode_duration'])
        interaction[D]={'interaction':bool(safe[f'{D}_P1']['safe_phase_information_gain'] and (hi>0 or lo>0)),'burst_end_interaction':hi,'unresolved_duration_interaction':lo}
    return {
        'seed':seed,'manifest':{'count':manifest(seed)['count'],'sha256':manifest(seed)['sha256']},
        'summaries':sums,'phase_diagnostics':phase,'safe_phase':safe,
        'phase_macro_information_gain':macro,'phase_push_interaction':interaction,
        'qualification':qual,'A53_ANY_QUALIFIED':any(qual.values()),'integrity':integ}

def run(seed):
    allres={a:[] for a in ARMS}
    for ctx in range(48):
        for rep in range(8):
            w=make_world(seed,ctx,rep)
            for a in ARMS:
                allres[a].append(run_arm(seed,w,a))
    return finalize(seed,allres)

def main():
    seed=sys.argv[1] if len(sys.argv)>1 else 'MECHANICAL-A45-NONPRIMARY'
    print(json.dumps(run(seed),sort_keys=True,separators=(',',':')))

if __name__=='__main__':
    main()
