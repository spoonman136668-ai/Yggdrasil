"""AAI-12R: source-only, pre-registered, bounded causal operator discovery.
Never use this as an independent scientific result or as a native Yggdrasil model.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import time
from copy import deepcopy
from itertools import product

FIT=((8,14,6,8),(14,6,8,14),(6,8,14,6),(8,6,14,8))
TRANSFER=((7,1,9,11),(11,13,2,4),(3,5,10,12),(1,7,11,9),
          (5,10,12,3),(9,2,4,13),(13,3,7,1),(2,11,5,10),
          (4,9,3,7),(12,5,1,2),(10,4,13,11),(7,12,9,5))
FIXTURES=('mechanical:alpha','mechanical:beta')
ARMS=('posterior_greedy_recent16','posterior_random_probe_recent16',
      'fixed_and_or_xor_greedy_recent16','operator_active_recent16')
ACTIONS=tuple((i,b) for i in range(8) for b in (0,1))
PUBLIC={'x','mediators','goal','reward','actions_taken'}
COST=.08


def index(fix,phase,law,event,field,mod):
    if fix not in FIXTURES or phase not in ('fit','challenge','eval','familiar'):
        raise PermissionError('AAI12R scientific first use disarmed')
    msg=f'AAI12R-v1|{fix}|{phase}|{law}|{event}|{field}'
    return int.from_bytes(hashlib.sha256(msg.encode('ascii')).digest()[:8],'big')%mod


def bits(x,n):
    if type(x) not in (list,tuple) or len(x)!=n or any(type(v)!=int or v not in (0,1) for v in x):
        raise ValueError('invalid public bits')
    return tuple(x)


def ops_forward(ops,x):
    x=bits(x,8)
    if len(ops)!=4 or any(type(mask)!=int or not 0<=mask<16 for mask in ops):
        raise ValueError('private source operator invalid')
    def apply(mask,a,b):return (mask>>(2*a+b))&1
    a=apply(ops[0],x[0],x[1]); b=apply(ops[1],x[2],x[3])
    c=apply(ops[2],a,x[4]);d=apply(ops[3],b,c)
    return (a,b,c,d)


def reward(m,g,steps):
    return round(sum(a==b for a,b in zip(bits(m,4),bits(g,4)))-COST*steps,10)


def public(x,m,g,steps):
    return {'x':list(bits(x,8)),'mediators':list(bits(m,4)),'goal':list(bits(g,4)),
            'actions_taken':steps,'reward':reward(m,g,steps)}


def validate(row):
    if type(row)!=dict or set(row)!=PUBLIC:raise ValueError('private/public field mismatch')
    x=bits(row['x'],8);m=bits(row['mediators'],4);g=bits(row['goal'],4)
    k=row['actions_taken']
    if type(k)!=int or k not in (0,1,2) or type(row['reward']) not in (int,float):
        raise ValueError('invalid public counter/reward')
    if abs(row['reward']-reward(m,g,k))>1e-9:raise ValueError('bad public reward')
    return x,m


def start(ops,x,g):return public(x,ops_forward(ops,x),g,0)


def intervene(ops,row,action):
    x,m=validate(row)
    if row['actions_taken']>=2 or action not in ACTIONS or m!=ops_forward(ops,x):
        raise ValueError('unapproved intervention')
    y=list(x);y[action[0]]=action[1]
    return public(y,ops_forward(ops,y),row['goal'],row['actions_taken']+1)


def example_pair(ops,fix,phase,law,event):
    x=tuple(int(z) for z in f'{index(fix,phase,law,event,"x",256):08b}')
    g=tuple(int(z) for z in f'{index(fix,phase,law,event,"goal",16):04b}')
    row=start(ops,x,g)
    return row,intervene(ops,row,ACTIONS[index(fix,phase,law,event,'do',16)])


def context(fix,phase,law,event):
    x=tuple(int(z) for z in f'{index(fix,phase,law,event,"x",256):08b}')
    g=tuple(int(z) for z in f'{index(fix,phase,law,event,"goal",16):04b}')
    return x,g


class Learner:
    """Learner sees only public records. No operator/world/phase argument."""
    def __init__(self,name,rows=()):
        if name not in ARMS:raise ValueError('nonregistered arm')
        self.name=name;self.rows=[];self._cache={};self._stage_cache={}
        for row in rows:self.observe(row)

    def observe(self,row):
        validate(row)
        self.rows.append(deepcopy(row))
        self.rows=self.rows[-16:]
        self._cache.clear();self._stage_cache.clear()

    def stage(self,stage,a,b):
        key=(stage,a,b)
        if key in self._stage_cache:return self._stage_cache[key]
        # Same Beta(1,1) / sixteen-function uniform truth-table prior for full16 arms.
        outcomes=[]
        for row in self.rows:
            x,m=validate(row)
            u,v=((x[0],x[1]),(x[2],x[3]),(m[0],x[4]),(m[1],m[2]))[stage]
            if (u,v)==(a,b):outcomes.append(m[stage])
        if self.name=='fixed_and_or_xor_greedy_recent16':
            best=min((sum(((mask>>(2*u+v))&1)!=out for u,v,out in (
                (*((x[0],x[1]),(x[2],x[3]),(m[0],x[4]),(m[1],m[2]))[stage],m[stage])
                for row in self.rows for x,m in [validate(row)])),mask)
                for mask in (6,8,14))[1]
            bit=(best>>(2*a+b))&1
            result=.95 if bit else .05
        else:result=(1+sum(outcomes))/(2+len(outcomes))
        self._stage_cache[key]=result
        return result

    def predict(self,x):
        x=bits(x,8)
        if x in self._cache:return self._cache[x]
        p0=self.stage(0,x[0],x[1]);p1=self.stage(1,x[2],x[3])
        p2=sum((p0 if a else 1-p0)*self.stage(2,a,x[4]) for a in (0,1))
        p3=sum((p1 if b else 1-p1)*(p2 if c else 1-p2)*self.stage(3,b,c)
               for b,c in product((0,1),repeat=2))
        self._cache[x]=(p0,p1,p2,p3)
        return self._cache[x]

    def expectation(self,x,g,steps):
        return sum(p if target else 1-p for p,target in zip(self.predict(x),g))-COST*steps

    def greedy(self,row):
        x,_=validate(row);g=tuple(row['goal']);steps=row['actions_taken']
        if steps>=2:return None
        best=(float(row['reward']),None)
        for action in ACTIONS:
            y=list(x);y[action[0]]=action[1]
            val=self.expectation(y,g,steps+1)
            if steps==0:
                for other in ACTIONS:
                    z=y.copy();z[other[0]]=other[1]
                    val=max(val,self.expectation(z,g,2))
            if val>best[0]+1e-10:best=(val,action)
        return best[1]

    def choose(self,row,episode,fix,law):
        if row['actions_taken']>=2:return None
        candidate=self.greedy(row)
        if episode>=4 or row['actions_taken']!=0:return candidate
        if self.name=='posterior_random_probe_recent16':
            return ACTIONS[index(fix,'eval',law,episode,'RANDOM_PROBE',16)]
        if self.name!='operator_active_recent16':return candidate
        x,_=validate(row);g=tuple(row['goal'])
        best_baseline=max((self.expectation(tuple(x[:i]+(v,)+x[i+1:]),g,1)
                           for i,v in ACTIONS),default=float('-inf'))
        ranked=[]
        for action in ACTIONS:
            y=x[:action[0]]+(action[1],)+x[action[0]+1:]
            future=self.predict(y)
            val=self.expectation(y,g,1)
            if val>=best_baseline-.30:
                info=sum(p*(1-p) for p in future)
                if info>0:ranked.append((-info,ACTIONS.index(action),action))
        return min(ranked)[2] if ranked else candidate

    def checkpoint(self):
        return json.dumps({'schema':'aai12r.public.v1','name':self.name,'rows':self.rows},
                          sort_keys=True,separators=(',',':'))

    @classmethod
    def restore(cls,source):
        d=json.loads(source)
        if type(d)!=dict or set(d)!={'schema','name','rows'} or d['schema']!='aai12r.public.v1':
            raise ValueError('invalid cold checkpoint')
        if type(d['rows'])!=list or len(d['rows'])>16:raise ValueError('oversized state')
        agent=cls(d['name'],d['rows'])
        if agent.checkpoint()!=source:raise ValueError('cold state changed')
        return agent


def oracle(ops,x,g):
    initial=start(ops,x,g);scores=[initial]
    for a in ACTIONS:
        one=intervene(ops,initial,a);scores.append(one)
        for b in ACTIONS:scores.append(intervene(ops,one,b))
    return max(row['reward'] for row in scores),any(tuple(row['mediators'])==g for row in scores)


def episode_run(learner,ops,fix,law,ep,phase='eval'):
    x,g=context(fix,phase,law,ep);row=start(ops,x,g)
    learner.observe(row)
    actions=[]
    for _ in range(2):
        action=learner.choose(row,ep if phase=='eval' else 4+ep,fix,law)
        if action is None:break
        row=intervene(ops,row,action);learner.observe(row)
        actions.append(ACTIONS.index(action))
    return row,actions


def mean(seq):return sum(seq)/len(seq) if seq else 0.


def screen():
    if len(FIT)!=4 or len(TRANSFER)!=12 or len(FIXTURES)!=2:
        raise AssertionError('frozen source worlds drifted')
    records={arm:[] for arm in ARMS};familiar={arm:[] for arm in ARMS}
    times={arm:0. for arm in ARMS}; hashes=[];traces=[]
    for fix in FIXTURES:
        fitted={arm:Learner(arm) for arm in ARMS}
        for law,ops in enumerate(FIT):
            for t in range(8):
                for row in example_pair(ops,fix,'fit',law,t):
                    for arm in ARMS:fitted[arm].observe(row)
        saved={arm:model.checkpoint() for arm,model in fitted.items()}
        for law,ops in enumerate(TRANSFER):
            actors={arm:Learner.restore(saved[arm]) for arm in ARMS}
            for t in range(4):
                for row in example_pair(ops,fix,'challenge',law,t):
                    for arm in ARMS:actors[arm].observe(row)
            for ep in range(16):
                x,g=context(fix,'eval',law,ep)
                optim,reachable=oracle(ops,x,g)
                for arm in ARMS:
                    start_time=time.perf_counter()
                    row,acts=episode_run(actors[arm],ops,fix,law,ep)
                    times[arm]+=time.perf_counter()-start_time
                    records[arm].append((row['reward'],int(tuple(row['mediators'])==g),
                                         int(reachable),optim,ep))
                    traces.append([fix,law,ep,arm,row['reward'],acts])
                if ep%4==3:
                    for arm in ARMS:
                        cold=actors[arm].checkpoint()
                        actors[arm]=Learner.restore(cold)
                        hashes.append(hashlib.sha256(cold.encode()).hexdigest())
        for law,ops in enumerate(FIT):
            for ep in range(8):
                x,g=context(fix,'familiar',law,ep)
                for arm in ARMS:
                    actor=Learner.restore(saved[arm])
                    start_time=time.perf_counter()
                    row,_=episode_run(actor,ops,fix,law,ep,'familiar')
                    times[arm]+=time.perf_counter()-start_time
                    familiar[arm].append(row['reward'])
        for arm in ARMS:
            if fitted[arm].checkpoint()!=saved[arm]:raise AssertionError('fit source polluted')
    if any(len(v)!=384 for v in records.values()) or any(len(v)!=64 for v in familiar.values()):
        raise AssertionError('frozen source budget drifted')
    scores={}
    for arm,rows in records.items():
        late=[r for r in rows if r[4]>=4]
        reach=[r for r in late if r[2]]
        scores[arm]={'reward':round(mean([r[0] for r in rows]),9),
                     'late_reward':round(mean([r[0] for r in late]),9),
                     'late_reachable_hit_rate':round(mean([r[1] for r in reach]),9),
                     'hits':sum(r[1] for r in rows),'late_reachable_cases':len(reach),
                     'familiar_reward':round(mean(familiar[arm]),9),
                     'whole_episode_seconds':round(times[arm],6)}
    cand=scores['operator_active_recent16'];greedy=scores['posterior_greedy_recent16']
    controls=[scores[a] for a in ARMS if a!='operator_active_recent16' and a!='fixed_and_or_xor_greedy_recent16']
    best=max(controls,key=lambda m:m['reward'])
    checks={
      'reward_vs_strong_full16_at_least_0_08':cand['reward']>=best['reward']+.08-1e-10,
      'late_reward_vs_strong_full16_at_least_0_10':cand['late_reward']>=max(m['late_reward'] for m in controls)+.10-1e-10,
      'late_reachable_hit_rate_vs_strong_at_least_0_05':cand['late_reachable_hit_rate']>=max(m['late_reachable_hit_rate'] for m in controls)+.05-1e-10,
      'reward_vs_same_inference_greedy_at_least_0_05':cand['reward']>=greedy['reward']+.05-1e-10,
      'familiar_no_worse_than_strong_by_0_03':cand['familiar_reward']>=max(m['familiar_reward'] for m in controls)-.03-1e-10,
      'whole_episode_wall_ratio_below_2':cand['whole_episode_seconds']<=2*min(m['whole_episode_seconds'] for m in controls)+1e-10,
    }
    return {'schema':'yggdrasil.aai12r.source-dev.v1',
            'classification':'DEV_SCREEN_PASS_NEGATIVE_AND_REGRESSION_PENDING' if all(checks.values()) else 'DEV_NO_GO_NO_SCIENCE',
            'scores':scores,'frozen_checks':checks,'source_only':True,'scientific_cohorts_used':0,
            'trace_sha256':hashlib.sha256(json.dumps(traces,separators=(',',':')).encode()).hexdigest(),
            'cold_checkpoint_digest':hashlib.sha256(json.dumps(hashes,separators=(',',':')).encode()).hexdigest()}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source-dev',action='store_true')
    parser.add_argument('--primary',action='store_true')
    args=parser.parse_args()
    if args.primary:parser.error('AAI12R SCIENTIFIC FIRST USE DISARMED')
    if not args.source_dev:parser.error('AAI12R only frozen --source-dev is permitted')
    print('AAI12R_DEV='+json.dumps(screen(),sort_keys=True),flush=True)


if __name__=='__main__':main()
