"""R7-C24: genuine public action-level information probes, native vs fitted conventional.

Source original and Yggdrasil owner R3 unchanged. Re-use 12 previously frozen
authentic FIT events; no hidden map, source tile types or policy seed.
"""
import argparse,collections,copy,hashlib,json,math,os,resource,subprocess,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT))
from research.mass_r7c23 import run as c23
from research.mass_r7c22 import run as c22
from research.mass_r7c20 import run as c20
from research.native.itd02.r1.native_policy import PublicGrid,canonical
P=json.loads((HERE/'PREREG.json').read_text())
D=c20.DIR

def info_turn(st,choice,known,blocked):
    """Select a one-step rotation to inspect an unknown but goal-relevant edge.

    This is not an oracle: the newly exposed tile will only be observed
    *after* the turn is actually executed.
    """
    if choice not in (0,1):return choice,False
    turns={0:(st.direction-1)%4,1:(st.direction+1)%4}
    other=1-choice
    chosen=(st.x,st.y,turns[choice])
    target=(st.x,st.y,turns[other])
    if chosen not in known or chosen not in blocked or target in known:
        return choice,False
    goal=(st.goal_x,st.goal_y)
    def h(e):
        dx,dy=D[e[2]]
        return abs(e[0]+dx-goal[0])+abs(e[1]+dy-goal[1])
    # No hidden occupancy and no further probing if both are already observed.
    if h(target)<=h(chosen):
        return other,True
    return choice,False

class NativeActive(c23.NativeSelective):
    def choose(self,st):
        action=super().choose(st)
        new,probe=info_turn(st,action,self.evidence,self.blocked)
        self.last_information_probe=probe
        return new

class ConventionalFull(c23.ConventionalProbabilistic):
    """Separate source-fitted empirical motor + discounted Beta, fully persisted."""
    def __init__(self,fit):
        super().__init__(fit)
        self.last_information_probe=False
    def checkpoint(self):
        parent=json.loads(super().checkpoint())
        posterior=[[list(k),[float(a),float(b),int(t)]]
                   for k,(a,b,t) in sorted(self.posterior.items())]
        data={'schema':'mass.r7c24.full-conventional-public-state.v1',
              'base':parent,'clock':self.clock,'posterior':posterior}
        return canonical({'data':data,'sha256':hashlib.sha256(canonical(data)).hexdigest()})
    @classmethod
    def restore(cls,blob):
        wire=json.loads(blob)
        if set(wire)!={'data','sha256'}:raise ValueError('CONVENTIONAL_ENVELOPE')
        data=wire['data']
        if (data.get('schema')!='mass.r7c24.full-conventional-public-state.v1' or
          hashlib.sha256(canonical(data)).hexdigest()!=wire['sha256']):
            raise ValueError('CONVENTIONAL_INTEGRITY')
        base=data['base']
        if hashlib.sha256(canonical(base['body'])).hexdigest()!=base['sha256']:
            raise ValueError('CONVENTIONAL_INNER_INTEGRITY')
        obj=cls.__new__(cls)
        x=base['body']
        obj.motor={int(k):tuple(v) for k,v in x['motor'].items()}
        assert set(obj.motor)==set(range(4))
        obj.w=int(x['w']);obj.h=int(x['h'])
        obj.blocked={tuple(v) for v in x['blocked']}
        obj.open={tuple(v) for v in x['open']}
        obj.visits=collections.Counter({tuple(k):v for k,v in x['visits']})
        obj.records=collections.defaultdict(lambda:[0,0])
        obj.clock=int(data['clock'])
        obj.posterior={}
        for k,v in data['posterior']:
            key=tuple(k)
            a,b,t=v
            if (key in obj.posterior or len(key)!=3 or any(type(q)!=int for q in key) or
                not math.isfinite(a) or not math.isfinite(b) or
                a<1 or b<1 or type(t)!=int or t<0 or t>obj.clock):
                raise ValueError('CONVENTIONAL_POSTERIOR_CORRUPTED')
            obj.posterior[key]=(a,b,t)
        obj.last_information_probe=False
        return obj

class ConventionalActive(ConventionalFull):
    def choose(self,st):
        preferred=super().choose(st)
        alt,probe=info_turn(st,preferred,self.posterior,self.blocked)
        self.last_information_probe=probe
        return alt

def make(arm,fit):
    if arm=='native_selective':return c23.make('native_selective',fit)
    if arm=='native_active':
        m=NativeActive()
        for f,s,a,b,n,r,t in fit:
            m.reset_episode(32,32)
            m.observe(b,a,n,r,t,True)
        assert all(m._motor(k) is not None for k in range(4))
        return m
    if arm=='conventional_persistent':
        return c20.Conventional(fit)
    if arm=='conventional_bayesian':
        return ConventionalFull(fit)
    if arm=='conventional_active':
        return ConventionalActive(fit)
    raise ValueError('INVALID_ARM')

def snapshot(arm,model):
    return (model.checkpoint() if arm.startswith('conventional') else model.snapshot())

def restored_model(arm,data):
    if arm=='native_selective':return c23.NativeSelective.restore(data)
    if arm=='native_active':return NativeActive.restore(data)
    if arm=='conventional_persistent':
        base=json.loads(data)
        if hashlib.sha256(canonical(base['body'])).hexdigest()!=base['sha256']:
            raise ValueError('PERSISTENT_INTEGRITY')
        x=base['body']
        m=c20.Conventional.__new__(c20.Conventional)
        m.motor={int(k):tuple(v) for k,v in x['motor'].items()}
        m.w=int(x['w']);m.h=int(x['h'])
        m.blocked={tuple(v) for v in x['blocked']}
        m.open={tuple(v) for v in x['open']}
        m.visits=collections.Counter({tuple(k):v for k,v in x['visits']})
        m.records=collections.defaultdict(lambda:[0,0])
        return m
    if arm=='conventional_bayesian':return ConventionalFull.restore(data)
    if arm=='conventional_active':return ConventionalActive.restore(data)
    raise ValueError('UNKNOWN_ARM')

def cold_compare(arm,model,next_public):
    original=copy.deepcopy(model)
    expect=original.choose(next_public)
    checkpoint=snapshot(arm,model)
    payload=canonical({'arm':arm,'checkpoint':checkpoint.decode(),
      'public':next_public.__dict__,'expected':expect})
    program="""import json,sys
from research.mass_r7c24.run import restored_model
from research.native.itd02.r1.native_policy import PublicGrid
p=json.loads(sys.stdin.buffer.read())
m=restored_model(p['arm'],p['checkpoint'].encode())
s=PublicGrid(**p['public'])
assert m.choose(s)==p['expected'], 'RESTORED_ACTION_DIVERGENCE'
print('R7C24_COLD_STATE_ACTION=PASS')
"""
    r=subprocess.run([sys.executable,'-B','-c',program],input=payload,
         capture_output=True,cwd=ROOT,timeout=35,
         env=dict(os.environ,PYTHONPATH=str(ROOT),PYTHONDONTWRITEBYTECODE='1'))
    assert r.returncode==0,(arm,'COLD_ACTION_FAIL',r.stderr.decode())
    assert 'R7C24_COLD_STATE_ACTION=PASS' in r.stdout.decode()
    return len(checkpoint)

def run_family(arm,model,family,seeds):
    env=c20.env_make(family)
    total={'episodes':0,'wins':0,'collision_terminal':0,'horizon':0,'steps':0,
           'reward_sum':0.,'public_blocked_forward':0,'information_turns':0}
    episodes=[]
    try:
        for seed in seeds:
            obs,_=env.reset(seed=seed)
            goal=c20.goal_from(obs)
            dims=tuple(int(x) for x in obs['image'].shape[:2])
            model.reset_episode(*dims)
            trace=[];win=False;collision=False;horizon=False;checkpoint_3=0
            for step in range(P['actions_per_episode_cap']):
                before=c22.public_dynamic(obs,goal)
                action=model.choose(before)
                assert type(action)==int and action in (0,1,2)
                is_probe=bool(getattr(model,'last_information_probe',False)) if arm in ('native_active','conventional_active') else False
                after_obs,reward,done,trunc,_=env.step(action)
                after=c22.public_dynamic(after_obs,goal)
                reward=float(reward)
                if arm.startswith('conventional'):model.observe(before,action,after,reward,bool(done))
                else:model.observe(before,action,after,reward,bool(done),False)
                total['steps']+=1;total['reward_sum']+=reward
                total['public_blocked_forward']+=int(action==2 and before.front_blocked)
                total['information_turns']+=int(is_probe)
                trace.append([before.x,before.y,before.direction,before.goal_x,before.goal_y,
                              int(before.front_blocked),action,int(is_probe),
                              after.x,after.y,after.direction,int(after.front_blocked),
                              reward,int(bool(done)),int(bool(trunc))])
                obs=after_obs
                # Clone the *actual* learned history after step3. Fresh Python
                # interpreter must yield exactly the same NEXT public choice.
                if step==2 and not(done or trunc):
                    checkpoint_3=cold_compare(arm,model,after)
                if done or trunc:
                    win=reward>0
                    collision=bool(done and reward<0)
                    horizon=bool(trunc)
                    break
            total['episodes']+=1;total['wins']+=int(win)
            total['collision_terminal']+=int(collision);total['horizon']+=int(horizon)
            if not checkpoint_3:
                final=c22.public_dynamic(obs,goal)
                checkpoint_3=cold_compare(arm,model,final)
            blob=snapshot(arm,model)
            episodes.append({'family':family,'seed':seed,'won':win,
               'steps':len(trace),'collision_terminal':collision,'horizon':horizon,
               'trace':trace,'trace_sha256':hashlib.sha256(canonical(trace)).hexdigest(),
               'checkpoint_sha256':hashlib.sha256(blob).hexdigest(),
               'checkpoint_bytes':len(blob),'cold_step3_checkpoint_bytes':checkpoint_3})
    finally:env.close()
    return total,episodes

def main():
    import gymnasium,minigrid
    ap=argparse.ArgumentParser()
    ap.add_argument('--arm',choices=P['arms'],required=True)
    ap.add_argument('--out',required=True)
    args=ap.parse_args()
    c20.check_source()
    assert P['immutable_source']['upstream'].split('@')[-1]=='7f5853792ea7f04f75614661006d87fcf949f26d'
    t0=time.process_time()
    fit,fit_hash,counts=c20.fit_data()
    assert fit_hash==P['fit']['expected_sha256'] and len(fit)==12
    model=make(args.arm,fit)
    t1=time.process_time()
    totals={};episodes=[]
    for fam,seeds in P['public_dev'].items():
        result,records=run_family(args.arm,model,fam,seeds)
        totals[fam]=result;episodes.extend(records)
    t2=time.process_time()
    out={'schema':P['schema'],'arm':args.arm,
         'source':P['immutable_source']['upstream'],
         'native_head':P['immutable_source']['original_r3_head'],
         'prereg_sha256':hashlib.sha256((HERE/'PREREG.json').read_bytes()).hexdigest(),
         'fit_sha256':fit_hash,'fit_rows':len(fit),'fit_counts':counts,
         'totals':totals,'episodes':episodes,
         'max_checkpoint_bytes':max(e['checkpoint_bytes'] for e in episodes),
         'max_cold_step3_bytes':max(e['cold_step3_checkpoint_bytes'] for e in episodes),
         'cpu_fit_s':round(t1-t0,6),'cpu_dev_s':round(t2-t1,6),
         'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
         'gymnasium':gymnasium.__version__}
    Path(args.out).write_bytes(canonical(out)+b'\n')
    print('R7C24_AUTHENTIC_PUBLIC_EPISODES',args.arm,json.dumps(totals,sort_keys=True))
if __name__=='__main__':main()
