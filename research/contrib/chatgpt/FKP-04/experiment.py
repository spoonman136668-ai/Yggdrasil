"""FKP04 first DEV-only causal memory and active intervention comparison."""
from __future__ import annotations
from array import array
import hashlib, json, random, statistics, time
from source import Mechanisms, World, DEV_KEY, N_MECH, N_STATES, N_HIST, N_PAID


def learn_real_transitions(source:Mechanisms):
    t=time.perf_counter()
    direct=array('H')
    for m in range(N_MECH):
        for state in range(N_STATES):direct.append(source.step(m,state))
    assert len(direct)==N_HIST
    # Both representations receive the EXACT same 1,048,576 observations.
    conventional=array('H',direct)
    return direct,conventional,time.perf_counter()-t

class NumericMemory:
    def __init__(self,values:array):
        if len(values)!=N_HIST:raise ValueError('BAD_MEMORY_SIZE')
        self.weights=values
    def step(self,mechanism:int,state:int)->int:
        if type(mechanism) is not int or not 0<=mechanism<N_MECH:raise ValueError('UNSEEN_MECHANISM')
        if type(state) is not int or not 0<=state<N_STATES:raise ValueError('BAD_STATE')
        return self.weights[mechanism*N_STATES+state]
    def compose(self,a,b,s,order):
        return self.step(b,self.step(a,s)) if order==0 else self.step(a,self.step(b,s))
    def cold(self):
        serialized=self.weights.tobytes()
        restored=NumericMemory(array('H',self.weights))
        assert restored.weights.tobytes()==serialized
        return restored,hashlib.sha256(serialized).hexdigest(),len(serialized)


def policy_actions(mem:NumericMemory,pool:tuple[int,...],a:int,b:int,policy:str,seed:int):
    if policy=='active':
        discriminating=tuple(x for x in pool if mem.compose(a,b,x,0)!=mem.compose(a,b,x,1))
        return (discriminating+tuple(x for x in pool if x not in discriminating))[:N_PAID]
    if policy=='random':return tuple(random.Random(seed^10101).sample(pool,N_PAID))
    if policy=='coverage':
        picked=[]
        while len(picked)<N_PAID:
            options=[x for x in pool if x not in picked]
            def score(x):return min((x^p).bit_count() for p in picked) if picked else min(x.bit_count(),12-x.bit_count())
            picked.append(max(options,key=lambda x:(score(x),-pool.index(x))))
        return tuple(picked)
    raise ValueError('INVALID_POLICY')

def fit_order(mem:NumericMemory,a:int,b:int,observations:tuple[tuple[int,int],...]):
    remaining={0,1}
    for x,y in observations:
        remaining={order for order in remaining if mem.compose(a,b,x,order)==y}
    if not remaining:return None
    return min(remaining)

def paired_ci(differences):
    rnd=random.Random(9090);n=len(differences)
    samples=sorted(sum(differences[rnd.randrange(n)] for _ in range(n))/n for _ in range(10000))
    return [samples[249],samples[9749]

def run():
    started=time.perf_counter()
    source=Mechanisms(DEV_KEY)
    data,comparison,original_training=learn_real_transitions(source)
    native=NumericMemory(data)
    conventional=NumericMemory(comparison)
    native_restored,digest,bytes_count=native.cold()
    assert digest==conventional.cold()[1]
    assert bytes_count==2097152
    rows=[]
    sequential_states=[]
    for seed in range(500,516):
        info=World(seed,source).public_view()
        a,b=info.mechanism_a,info.mechanism_b
        pred={};orient={};measure={};queries={}
        for arm in ('active','random','coverage','exact_table'):
            world=World(seed,source)
            alg='active' if arm=='exact_table' else arm
            memory=conventional if arm=='exact_table' else native_restored
            t=time.perf_counter()
            chosen=policy_actions(memory,info.public_pool,a,b,alg,seed)
            seen=tuple((x,world.observe(x)) for x in chosen)
            assert world.charged==N_PAID
            guess=fit_order(memory,a,b,seen)
            orient[arm]=guess
            pred[arm]=tuple(memory.compose(a,b,x,guess or 0) for x in info.held_states)
            measure[arm]=time.perf_counter()-t
            queries[arm]=chosen
        pred['no_history']=info.held_states
        # All predictions created BEFORE evaluator reveals any held answer.
        evaluator=World(seed,source)
        truth=evaluator.dev_eval(info.held_states)
        true_order=evaluator.dev_private_order()
        scores={arm:sum(x==y for x,y in zip(pred[arm],truth))/len(truth) for arm in pred}
        correct={arm:int(orient[arm]==true_order) for arm in orient}
        assert pred['active']==pred['exact_table'] and queries['active']==queries['exact_table']
        sequential_states.append((a,b,orient['active'],info.held_states,pred['active']))
        rows.append({'seed':seed,'scores':scores,'order_correct':correct,
                     'first_discriminating_candidates':sum(native.compose(a,b,x,0)!=native.compose(a,b,x,1) for x in info.public_pool),
                     'policy_seconds':measure,'active_random_overlap':len(set(queries['active'])&set(queries['random']))})
    # Interference/cold retention: all old world programs must remain exact.
    checkpoint,after_sha,_=native.cold()
    assert after_sha==digest
    retained=sum(tuple(checkpoint.compose(a,b,x,order or 0) for x in held)==original
                 for a,b,order,held,original in sequential_states)
    means={arm:statistics.mean(row['scores'][arm] for row in rows) for arm in rows[0]['scores']}
    accuracy_diff={b:statistics.mean(r['scores']['active']-r['scores'][b] for r in rows)
                   for b in ('random','coverage','no_history','exact_table')}
    ci={b:paired_ci([r['scores']['active']-r['scores'][b] for r in rows])
        for b in ('random','coverage','exact_table')}
    orient_correct={arm:sum(r['order_correct'][arm] for r in rows) for arm in ('active','random','coverage','exact_table')}
    return {'schema':'fkp04.dev-results.v1','protected_source_used':False,'histories':N_HIST,
            'native_weights_bytes':bytes_count,'cold_checksum_sha256':digest,'retained_worlds':retained,
            'dev_worlds':len(rows),'held_per_world':len(info.held_states),'paid_actions_per_policy':N_PAID,
            'exact_held_accuracy':means,'accuracy_diff':accuracy_diff,'ci':ci,
            'correct_world_orders':orient_correct,'foundation_original_training_seconds':original_training,
            'total_process_seconds':time.perf_counter()-started,'rows':rows}

if __name__=='__main__':
 print(json.dumps(run(),sort_keys=True))
