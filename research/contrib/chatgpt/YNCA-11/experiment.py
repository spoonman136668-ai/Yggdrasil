"""YNCA11 isolated tokenless operator memory: interference and composition."""
import argparse, hashlib, itertools, json, math, random

PERMS = tuple(itertools.permutations(range(3)))
ACTIONS = tuple(range(8))
NOISE=0.12
TOPK=3
N_TRAIN_PER_CONTEXT=8
TRAIN_OBS=4
N_TEST_SINGLE=64
N_TEST_COMPOSE=64
SPLITS={"A":(91000,92000,93000),"B":(101000,102000,103000)}

def rng(*args):
    return random.Random(int.from_bytes(hashlib.sha256(':'.join(map(str,args)).encode()).digest()[:16],'big'))

def bit(t,x):return (t>>x)&1

def permute(x,p):return sum(((x>>p[i])&1)<<i for i in range(3))

def table_permute(t,p):return sum(bit(t,permute(x,p))<<x for x in ACTIONS)

def candidate_library():
    # One representative per permutation orbit, excluding trivial projections,
    # parity and constants. The fixed 24-table hypothesis family is shared by all.
    reps=[]
    for t in range(256):
        orbit=tuple(table_permute(t,p) for p in PERMS)
        if t!=min(orbit) or min(t.bit_count(),8-t.bit_count())<2:continue
        reps.append(t)
    r=rng('candidate-vocabulary-v1')
    r.shuffle(reps)
    return tuple(sorted(reps[:24]))

CANDIDATES=candidate_library()

def truth(opA,opB,kind,x):
    if kind=='A':return bit(opA,x)
    if kind=='B':return bit(opB,x)
    # Composition B(A(x0,x1,x2), x1, x2): new relationship created by reuse.
    return bit(opB,bit(opA,x) | (x & 6))

def chosen_ops(split):
    r=rng('op-selection',split,SPLITS[split][0])
    a,b=r.sample(CANDIDATES,2)
    return a,b

def noisy_world(split,kind,seed,samples):
    a,b=chosen_ops(split)
    r=rng('world',split,kind,seed)
    p=r.choice(PERMS)
    xs=r.sample(ACTIONS,samples)
    obs=tuple((x,truth(a,b,kind,permute(x,p)) ^ (r.random()<NOISE)) for x in xs)
    return tuple((x,int(y)) for x,y in obs),p

def context_train(split):
    # Strict interleaving A4,B4,A4,B4; no longer run of A after final B.
    base=SPLITS[split][1]
    chunks=[]
    for block in range(2):
        for kind in ('A','B'):
            for j in range(4):
                seed=base + (block*2+('B'==kind))*4+j
                obs,_=noisy_world(split,kind,seed,TRAIN_OBS)
                chunks.append((kind,obs))
    return chunks

def posterior_one(worlds):
    scores=[]
    for t in CANDIDATES:
        z=0
        for obs in worlds:
            # Unknown permutation integrated out per world.
            l=[]
            for p in PERMS:
                errors=sum(bit(t,permute(x,p))!=y for x,y in obs)
                l.append((TRAIN_OBS-errors)*math.log1p(-NOISE)+errors*math.log(NOISE))
            z+=logsumexp(l)-math.log(len(PERMS))
        scores.append(z)
    n=logsumexp(scores)
    return {t:math.exp(z-n) for t,z in zip(CANDIDATES,scores)}

def logsumexp(xs):
    m=max(xs)
    return m+math.log(math.fsum(math.exp(x-m) for x in xs))

def bank(split):
    history=context_train(split)
    a=posterior_one([obs for kind,obs in history if kind=='A'])
    b=posterior_one([obs for kind,obs in history if kind=='B'])
    # Ignoring context pools all worlds; literal overwriting retains only final B slot.
    shared=posterior_one([obs for _,obs in history])
    return {'separate':(a,b),'shared':(shared,shared),'last_B':(b,b),'history':history}

def compress(prior):
    keep=sorted(prior,key=lambda t:(-prior[t],t))[:TOPK]
    mass=math.fsum(prior[t] for t in keep)
    return {t:prior[t]/mass for t in keep}

def prediction(priorA,priorB,kind,obs,return_evidence=False):
    # Enumerate all model hypotheses and all unknown role permutations.
    # No true operator or ground truth enters the policy.
    hyps=[]
    A=priorA.items() if kind in ('A','C') else [(0,1.)]
    B=priorB.items() if kind in ('B','C') else [(0,1.)]
    for a,pa in A:
        for b,pb in B:
            for p in PERMS:
                err=sum(truth(a,b,kind,permute(x,p))!=y for x,y in obs)
                lk=err*math.log(NOISE)+(len(obs)-err)*math.log1p(-NOISE)
                hyps.append((math.log(pa*pb/len(PERMS))+lk,a,b,p))
    n=logsumexp([v[0] for v in hyps])
    result=[0.]*8
    for score,a,b,p in hyps:
        w=math.exp(score-n)
        for x in ACTIONS:
            result[x]+=w*truth(a,b,kind,permute(x,p))
    return (tuple(result),math.exp(n)) if return_evidence else tuple(result)


def gated_prediction(knownA,knownB,kind,obs):
    if kind!='C':return prediction(knownA,knownB,kind,obs)
    neutral={t:1/len(CANDIDATES) for t in CANDIDATES}
    old,old_likelihood=prediction(knownA,knownB,kind,obs,True)
    fresh,fresh_likelihood=prediction(neutral,neutral,kind,obs,True)
    trust=old_likelihood/(old_likelihood+fresh_likelihood)
    return tuple(trust*a+(1-trust)*b for a,b in zip(old,fresh))


def frequency_control(history):
    counts={k:[2.]*8 for k in ('A','B')}
    hits={k:[1.]*8 for k in ('A','B')}
    for kind,obs in history:
        for x,y in obs:
            counts[kind][x]+=1;hits[kind][x]+=y
    freq={k:tuple(hits[k][x]/counts[k][x] for x in ACTIONS) for k in ('A','B')}
    return freq

def freq_predict(freq,kind,obs):
    if kind!='C':
        hits=[2*freq[kind][x] for x in ACTIONS]
        counts=[2.]*8
        for x,y in obs:hits[x]+=y;counts[x]+=1
        return tuple(hits[x]/counts[x] for x in ACTIONS)
    # Trained single-context frequency alone cannot capture composition;
    # compare with exact structured Bayes, not falsely claim no-composition control.
    return tuple([.5]*8)

def evaluate(split):
    a,b=chosen_ops(split)
    mem=bank(split)
    pA,pB=mem['separate']
    compact=(compress(pA),compress(pB))
    # This memory is serializable and restorable without original training worlds.
    saved=json.dumps({'A':{str(k):v for k,v in compact[0].items()},'B':{str(k):v for k,v in compact[1].items()}},sort_keys=True)
    obj=json.loads(saved)
    restored=tuple({int(k):v for k,v in obj[label].items()} for label in ('A','B'))
    assert restored==compact
    freq=frequency_control(mem['history'])
    prior={t:1/len(CANDIDATES) for t in CANDIDATES}
    methods=('NO_MEMORY','SHARED_UNTAGGED','LAST_B_OVERWRITE','TRAINED_FREQUENCY','TWO_SLOT_TOP3','GATED_TOP3','FULL_CONTEXT_BAYES','GATED_FULL_BAYES','ORACLE_TABLE')
    results={s:{m:[] for m in methods} for s in ('A','B','C')}
    recall={}
    base=SPLITS[split][2]
    for kind in ('A','B','C'):
        for j in range(N_TEST_COMPOSE if kind=='C' else N_TEST_SINGLE):
            obs,p=noisy_world(split,kind,base+['A','B','C'].index(kind)*1000+j,2 if kind=='C' else 3)
            unseen=[x for x in ACTIONS if x not in {q for q,_ in obs}]
            target=[truth(a,b,kind,permute(x,p)) for x in ACTIONS]
            options={
                'NO_MEMORY':(prior,prior),
                'SHARED_UNTAGGED':mem['shared'],
                'LAST_B_OVERWRITE':mem['last_B'],
                'TWO_SLOT_TOP3':restored,
                'GATED_TOP3':restored,
                'FULL_CONTEXT_BAYES':mem['separate'],
                'GATED_FULL_BAYES':mem['separate'],
                'ORACLE_TABLE':({a:1.},{b:1.})
            }
            for label,post in options.items():
                pred=(gated_prediction if label in ('GATED_TOP3','GATED_FULL_BAYES') else prediction)(post[0],post[1],kind,obs)
                results[kind][label].extend([(pred[x]-target[x])**2 for x in unseen])
            pred=freq_predict(freq,kind,obs)
            results[kind]['TRAINED_FREQUENCY'].extend([(pred[x]-target[x])**2 for x in unseen])
    metrics={k:{m:round(math.fsum(v)/len(v),8) for m,v in block.items()} for k,block in results.items()}
    # A after B is the late-return cold recall target; C is novel composition.
    return {'schema':'ynca11.operator-interference.v1','split':split,'candidate_library_size':len(CANDIDATES),
        'trained_worlds_per_context':N_TRAIN_PER_CONTEXT,'interleaving_sequence':'AAAA-BBBB-AAAA-BBBB',
        'per_training_world_interventions':TRAIN_OBS,'test_worlds_per_type':N_TEST_SINGLE,
        'per_test_single_observations':3,'per_test_composition_observations':2,
        'memory_entries':{kind:len(p) for kind,p in zip(('A','B'),restored)},
        'memory_cold_json_sha256':hashlib.sha256(saved.encode()).hexdigest(),
        'memory_cold_roundtrip_exact':restored==compact,
        'metrics':metrics,
        'claims':{'native_yggdrasil_trained':False,'scientific_pass':False,'deployed':False}}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--split',choices=('A','B'),required=True)
    print(json.dumps(evaluate(p.parse_args().split),sort_keys=True,indent=2))
