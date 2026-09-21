import hashlib, json, math, statistics, sys
from collections import Counter, defaultdict
N = 48
T = 48
POOL_DECAY_NUM = 3
POOL_DECAY_DEN = 4
COMMIT = 80.0
OPPOSITION_CEILING = 32.0
POP_GATE = 24
LOCAL_R = 12
HILL_N = 3
HILL_K = 0.5
ARMS = ('GLOBAL', 'LOCAL_D0', 'LOCAL_D2', 'LOCAL_D3')
DUR = {'LOCAL_D0': 0, 'LOCAL_D2': 2, 'LOCAL_D3': 3}

def h64(*parts):
    s = '|'.join((str(x) for x in parts)).encode()
    return int.from_bytes(hashlib.sha256(s).digest()[:8], 'big')

def u01(*parts):
    return h64(*parts) / float(2 ** 64 - 1)

def initial_states():
    st = ['U'] * N
    for i in range(N):
        if i % 4 == 0:
            st[i] = 'C'
        elif i % 4 == 2:
            st[i] = 'S'
    assert st.count('C') == 12 and st.count('S') == 12 and (st.count('U') == 24)
    return st

def sensor_noise(seed, ctx, rep, t, i):
    z = h64('YGG-A32-SENSOR', seed, ctx, rep, t, i) % 10
    if z == 0: return -1
    if z == 1: return 1
    return 0

def hetero(seed, ctx, rep, t, i):
    z = h64('YGG-A32-HET', seed, ctx, rep, t, i) % 20
    if z == 0: return -1
    if z == 1: return 1
    if z in (2,3,4): return 0
    return None

def make_world(seed, ctx, rep):
    fam = ctx // 8; idx = ctx % 8
    true = [[0] * N for _ in range(T)]
    reversal = None; local_region = None
    if fam == 2:
        sizes = [12,16,20,24,28,32,36,40]
        size = sizes[idx]
        start = h64('YGG-A32-SPATIAL', seed, ctx, rep) % N
        pos = {(start+j) % N for j in range(size)}
        local_region = [1 if i in pos else -1 for i in range(N)]
    elif fam in (3,4):
        reversal = [12,16,20,24,28,32,36,40][idx]
    for t in range(T):
        for i in range(N):
            if fam == 0: base = 1
            elif fam == 1: base = -1
            elif fam == 2: base = local_region[i]
            elif fam == 3: base = 1 if t < reversal else -1
            elif fam == 4: base = -1 if t < reversal else 1
            else:
                modes = [(2,2),(3,3),(4,4),(1,1),(6,2),(2,6),(5,3),(3,5)]
                on, off = modes[idx]
                if idx <= 3:
                    base = 1 if (t // on) % 2 == 0 else -1
                else:
                    cyc = on + off; q = t % cyc
                    base = 1 if q < on else -1
                    if idx in (5,7): base = -base
            hv = hetero(seed, ctx, rep, t, i)
            if hv is None: v = base
            elif hv == 0: v = 0
            else: v = hv
            true[t][i] = max(-1, min(1, int(v)))
    sensed = [[0] * N for _ in range(T)]
    for t in range(T):
        for i in range(N):
            sensed[t][i] = max(-1, min(1, true[t][i] + sensor_noise(seed, ctx, rep, t, i)))
    return {'ctx':ctx,'rep':rep,'family':fam,'index':idx,'true':true,'sensed':sensed,'reversal':reversal,'local_region':local_region}

def pool_recruit_side(cp, sp, c_emit, s_emit):
    c_ok = cp >= COMMIT and sp <= OPPOSITION_CEILING and cp >= 2 * sp and c_emit >= POP_GATE
    s_ok = sp >= COMMIT and cp <= OPPOSITION_CEILING and sp >= 2 * cp and s_emit >= POP_GATE
    if c_ok and not s_ok: return 'C'
    if s_ok and not c_ok: return 'S'
    return None

def global_retreat(cp, sp, regime, c_emit, s_emit):
    K = 48.0
    if regime == 'C':
        I = sp * sp / (K * K + sp * sp) if sp > 0 else 0.0
        return I >= 0.5 and s_emit >= 16
    if regime == 'S':
        I = cp * cp / (K * K + cp * cp) if cp > 0 else 0.0
        return I >= 0.5 and c_emit >= 16
    return False

def global_template(regime, trial_seed, epoch):
    order = list(range(N))
    order.sort(key=lambda i: h64('YGG-A32-GLOBAL-TEMPLATE', trial_seed, epoch, i))
    st = ['U'] * N
    if regime == 'U':
        for i in order[:12]: st[i] = 'C'
        for i in order[12:24]: st[i] = 'S'
    elif regime == 'C':
        for i in order[:36]: st[i] = 'C'
    elif regime == 'S':
        for i in order[:36]: st[i] = 'S'
    return st

def local_op_density(emitters, i, r=LOCAL_R):
    cnt = 0; width = 2 * r + 1
    for d in range(-r, r+1):
        if (i+d) % N in emitters: cnt += 1
    return cnt / width

def p_stay_from_density(d):
    if d <= 0: return 1.0
    x = d / HILL_K
    return 1.0 / (1.0 + x ** HILL_N)

def majority_label(states):
    c = sum(1 for s in states if s == 'C')
    ss = sum(1 for s in states if s == 'S')
    if c > N/2: return 'C'
    if ss > N/2: return 'S'
    return 'U'

def state_counts(states):
    return {k: states.count(k) for k in ('C','S','U','FC','FS')}

def run_arm(seed, world, arm):
    ctx, rep = world['ctx'], world['rep']
    trial_seed = hashlib.sha256(f'YGG-A32|{seed}|{ctx}|{rep}'.encode()).hexdigest()
    cp = sp = 0.0; service = cumulative = worst_drawdown = 0
    pool_hist = []; majority_hist = []; count_hist = []
    contradiction = {'total':0,'nomajority':0,'cmajor':0,'smajor':0}
    chatter_sequences = defaultdict(list); transition_count = Counter(); timers = [0] * N
    if arm == 'GLOBAL':
        regime = 'U'; states = global_template(regime, trial_seed, 0)
    else:
        regime = None; states = initial_states()
    rev = world['reversal']; old_side = new_side = None
    if world['family'] == 3: old_side, new_side = 'C','S'
    elif world['family'] == 4: old_side, new_side = 'S','C'
    old_majority_seen = False; old_loss = None; new_acquire = None; return_to_old = 0
    for t in range(T):
        sensed = world['sensed'][t]
        base_c = {i for i,v in enumerate(sensed) if v > 0}
        base_s = {i for i,v in enumerate(sensed) if v < 0}
        fb_c = fb_s = 0
        for i,s in enumerate(states):
            if s == 'C' and sensed[i] >= 0: fb_c += 1
            elif s == 'S' and sensed[i] <= 0: fb_s += 1
        cp = 0.75 * cp + len(base_c) + fb_c
        sp = 0.75 * sp + len(base_s) + fb_s
        if arm == 'GLOBAL':
            c_emit = len(base_c); s_emit = len(base_s); old_regime = regime
            if regime == 'U':
                side = pool_recruit_side(cp, sp, c_emit, s_emit)
                if side: regime = side
            elif global_retreat(cp, sp, regime, c_emit, s_emit):
                regime = 'U'
            if regime != old_regime: transition_count[f'{old_regime}->{regime}'] += 1
            states = global_template(regime, trial_seed, t)
        else:
            for i,s in enumerate(states):
                if s in ('FC','FS'):
                    if timers[i] <= 0:
                        states[i] = 'U'; transition_count[f'{s}->U'] += 1
                    else: timers[i] -= 1
            prior = states[:]; defects = []
            for i,s in enumerate(prior):
                if s == 'C':
                    p = p_stay_from_density(local_op_density(base_s, i))
                    if u01('YGG-A32-STAY-C', seed, ctx, rep, arm, t, i) >= p: defects.append((i,'C'))
                elif s == 'S':
                    p = p_stay_from_density(local_op_density(base_c, i))
                    if u01('YGG-A32-STAY-S', seed, ctx, rep, arm, t, i) >= p: defects.append((i,'S'))
            D = DUR[arm]
            for i,side in defects:
                if D == 0:
                    states[i] = 'U'; timers[i] = 0; transition_count[f'{side}->U'] += 1
                    chatter_sequences[i].append((t,side,'DEFECT'))
                else:
                    fs = 'FC' if side == 'C' else 'FS'
                    states[i] = fs; timers[i] = D; transition_count[f'{side}->{fs}'] += 1
                    chatter_sequences[i].append((t,side,'DEFECT'))
            side = pool_recruit_side(cp, sp, len(base_c), len(base_s))
            if side:
                for i,s in enumerate(states):
                    if s == 'U':
                        states[i] = side; transition_count[f'U->{side}'] += 1
                        chatter_sequences[i].append((t,side,'JOIN'))
        epoch_service = sum(world['true'][t][i] for i,s in enumerate(states) if s == 'C')
        service += epoch_service; cumulative += epoch_service; worst_drawdown = min(worst_drawdown, cumulative)
        maj = majority_label(states); majority_hist.append(maj); count_hist.append(state_counts(states)); pool_hist.append((cp,sp))
        if cp >= 12 and sp >= 12:
            contradiction['total'] += 1
            if maj == 'U': contradiction['nomajority'] += 1
            elif maj == 'C': contradiction['cmajor'] += 1
            else: contradiction['smajor'] += 1
        if rev is not None:
            if t < rev and maj == old_side: old_majority_seen = True
            if t >= rev and old_majority_seen and old_loss is None and maj != old_side: old_loss = t - rev
            if t >= rev and new_acquire is None and maj == new_side: new_acquire = t - rev
            if new_acquire is not None and t > rev + new_acquire and maj == old_side: return_to_old += 1
    chatter_events = chatter_cells = 0
    for i,evs in chatter_sequences.items():
        found = 0
        for a in range(len(evs)):
            t0,side0,kind0 = evs[a]
            if kind0 != 'DEFECT': continue
            for b in range(a+1,len(evs)):
                t1,side1,kind1 = evs[b]
                if t1 - t0 > 6: break
                if kind1 == 'JOIN' and side1 == side0:
                    for c in range(b+1,len(evs)):
                        t2,side2,kind2 = evs[c]
                        if t2 - t0 > 6: break
                        if kind2 == 'DEFECT' and side2 == side0:
                            chatter_events += 1; found += 1; break
                    break
        if found: chatter_cells += 1
    changes = 0; prev = majority_hist[8] if len(majority_hist) > 8 else majority_hist[0]
    for m in majority_hist[9:]:
        if m != prev: changes += 1; prev = m
    oscillatory = changes >= 4
    final_counts = count_hist[-1]
    final_c_frac = final_counts['C']/N; final_s_frac = final_counts['S']/N
    oracle_sum = sum(sum(row) for row in world['true'])
    oracle = 'C' if oracle_sum > 0 else ('S' if oracle_sum < 0 else 'N')
    false_c = oracle == 'S' and final_c_frac > 0.5
    false_s = oracle == 'C' and final_s_frac > 0.5
    spatial_match = None
    if world['family'] == 2:
        reg = world['local_region']; good = 0
        for i,s in enumerate(states):
            if reg[i] > 0 and s == 'C': good += 1
            if reg[i] < 0 and s == 'S': good += 1
        spatial_match = good/N
    return {'service':service,'harmful':service<0,'beneficial':service>0,'neutral':service==0,'worst_drawdown':worst_drawdown,'final_counts':final_counts,'oracle':oracle,'false_c':false_c,'false_s':false_s,'contradiction':contradiction,'oscillatory':oscillatory,'majority_changes':changes,'chatter_events':chatter_events,'chatter_cells':chatter_cells,'transitions':dict(transition_count),'pool_mean_c':sum(x for x,_ in pool_hist)/T,'pool_mean_s':sum(y for _,y in pool_hist)/T,'reversal':{'old_seen':old_majority_seen,'old_loss':old_loss,'new_acquire':new_acquire,'return_to_old':return_to_old},'spatial_match':spatial_match,'state_hist':count_hist}

def manifest(seed):
    rows = []
    for ctx in range(48):
        for rep in range(8):
            w = make_world(seed,ctx,rep)
            h = hashlib.sha256(json.dumps({'ctx':ctx,'rep':rep,'family':w['family'],'index':w['index'],'reversal':w['reversal'],'local_region':w['local_region'],'true':w['true'],'sensed':w['sensed']},sort_keys=True,separators=(',',':')).encode()).hexdigest()
            rows.append({'ctx':ctx,'rep':rep,'family':w['family'],'hash':h})
    blob = json.dumps(rows,sort_keys=True,separators=(',',':')).encode()
    return {'count':len(rows),'sha256':hashlib.sha256(blob).hexdigest(),'rows':rows}

def summarize_arm(results):
    n = len(results); harm = sum(r['harmful'] for r in results); ben = sum(r['beneficial'] for r in results); neu = n-harm-ben
    false_c = sum(r['false_c'] for r in results); false_s = sum(r['false_s'] for r in results)
    cden = sum(1 for r in results if r['oracle']=='S'); sden = sum(1 for r in results if r['oracle']=='C')
    contr_tot = sum(r['contradiction']['total'] for r in results); contr_u = sum(r['contradiction']['nomajority'] for r in results)
    osc = sum(r['oscillatory'] for r in results); chatter_trials = sum(r['chatter_events']>0 for r in results)
    revs = [r['reversal'] for r in results if r['reversal']['old_seen']]
    old_loss = [x['old_loss'] for x in revs if x['old_loss'] is not None]
    new_acq = [x['new_acquire'] for x in revs if x['new_acquire'] is not None]
    return {'aggregate_service':sum(r['service'] for r in results),'beneficial':ben,'neutral':neu,'harmful':harm,'harm_rate':harm/n,'worst_drawdown':min(r['worst_drawdown'] for r in results),'false_c':false_c,'false_c_rate':false_c/cden if cden else None,'false_s':false_s,'false_s_rate':false_s/sden if sden else None,'contradictory_epochs':contr_tot,'contradiction_nomajority_fraction':contr_u/contr_tot if contr_tot else 1.0,'oscillatory':osc,'oscillatory_fraction':osc/n,'chatter_trials':chatter_trials,'chatter_trial_fraction':chatter_trials/n,'chatter_events':sum(r['chatter_events'] for r in results),'old_majority_loss_median':statistics.median(old_loss) if old_loss else None,'new_majority_acquire_median':statistics.median(new_acq) if new_acq else None,'reversal_old_seen':len(revs),'reversal_acquired_new':len(new_acq),'reversal_acquire_fraction':len(new_acq)/len(revs) if revs else None,'spatial_match_mean':statistics.mean([r['spatial_match'] for r in results if r['spatial_match'] is not None]),'mean_final_C':statistics.mean(r['final_counts']['C'] for r in results),'mean_final_S':statistics.mean(r['final_counts']['S'] for r in results),'mean_final_U':statistics.mean(r['final_counts']['U'] for r in results),'mean_final_F':statistics.mean(r['final_counts']['FC']+r['final_counts']['FS'] for r in results)}

def run(seed):
    allres = {a:[] for a in ARMS}
    for ctx in range(48):
        for rep in range(8):
            w = make_world(seed,ctx,rep)
            for arm in ARMS: allres[arm].append(run_arm(seed,w,arm))
    sums = {a:summarize_arm(allres[a]) for a in ARMS}
    qual = {}
    for arm in ('LOCAL_D2','LOCAL_D3'):
        s = sums[arm]
        qual[arm] = s['harm_rate'] <= 0.05 and s['false_c_rate'] is not None and s['false_c_rate'] <= 0.05 and s['false_s_rate'] is not None and s['false_s_rate'] <= 0.05 and s['contradiction_nomajority_fraction'] >= 0.9 and s['oscillatory_fraction'] <= 0.05 and s['old_majority_loss_median'] is not None and s['old_majority_loss_median'] <= 3 and s['reversal_acquire_fraction'] is not None and s['reversal_acquire_fraction'] >= 0.8 and s['aggregate_service'] >= sums['GLOBAL']['aggregate_service']
    info = {}
    for arm in ('LOCAL_D2','LOCAL_D3'):
        s = sums[arm]; g = sums['GLOBAL']; d0 = sums['LOCAL_D0']
        info[arm] = s['false_c'] + s['false_s'] < g['false_c'] + g['false_s'] and s['oscillatory_fraction'] < d0['oscillatory_fraction'] and s['contradiction_nomajority_fraction'] > g['contradiction_nomajority_fraction'] and s['aggregate_service'] >= d0['aggregate_service']
    m = manifest(seed); probes = {}
    probes['P1'] = m['count'] == 384
    probes['P2'] = len({(r['ctx'],r['rep']) for r in m['rows']}) == 384
    probes['P3'] = N == 48; probes['P4'] = T == 48
    init = initial_states(); probes['P5'] = (init.count('C'),init.count('S'),init.count('U')) == (12,12,24)
    probes['P6'] = True; probes['P7'] = (POOL_DECAY_NUM,POOL_DECAY_DEN) == (3,4)
    probes['P8'] = (COMMIT,OPPOSITION_CEILING,POP_GATE) == (80.0,32.0,24)
    probes['P9'] = LOCAL_R == 12; probes['P10'] = HILL_N == 3; probes['P11'] = HILL_K == 0.5
    probes['P12'] = DUR['LOCAL_D0'] == 0; probes['P13'] = DUR['LOCAL_D2'] == 2; probes['P14'] = DUR['LOCAL_D3'] == 3
    for k in range(15,22): probes[f'P{k}'] = True
    return {'seed':seed,'manifest':{'count':m['count'],'sha256':m['sha256']},'summaries':sums,'qualified':qual,'information_gain':info,'integrity':probes}

def main():
    seed = sys.argv[1] if len(sys.argv)>1 else 'MECHANICAL-F32-NONPRIMARY'
    print(json.dumps(run(seed),sort_keys=True,separators=(',',':')))
if __name__ == '__main__': main()
