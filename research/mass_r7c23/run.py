"""Original-source R7-C23: public-only selective, TTL and Bayesian edge-belief learning.

Owner R3 module remains immutable. Every trained candidate uses the identical
twelve original-source public FIT events frozen in R7-C20–C23.
"""
import argparse, collections, hashlib, json, math, os, resource, subprocess, sys, time
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT))
from research.mass_r7c22 import run as c22
from research.mass_r7c21 import run as c21
from research.mass_r7c20 import run as c20
from research.native.itd02.r3.navigator import Navigator
from research.native.itd02.r1.native_policy import canonical,features
P=json.loads((HERE/"PREREG.json").read_text())

class NativeSelective(Navigator):
    """Revise episodic spatial beliefs on real public sensor contradictions only."""
    def __init__(self):
        super().__init__()
        self.evidence={}
    def reset_episode(self,width,height):
        super().reset_episode(width,height)
        self.evidence={}
    def choose(self,st):
        features(st)
        now=self.steps
        edge=(st.x,st.y,st.direction)
        status=int(st.front_blocked)
        old=self.evidence.get(edge)
        if old is None:
            self.evidence[edge]={'time':now,'status':status,'streak':1,'flips':0,'blocked_seen':status,'clear_seen':1-status}
        else:
            flips=old['flips']+int(old['status']!=status)
            streak=old['streak']+1 if old['status']==status else 1
            self.evidence[edge]={'time':now,'status':status,'streak':streak,
                 'flips':flips,'blocked_seen':old['blocked_seen']+status,
                 'clear_seen':old['clear_seen']+1-status}
        self.blocked.clear()
        self.open_edges.clear()
        for k,rec in self.evidence.items():
            age=now-rec['time']
            if rec['status']:
                ttl=(1 if rec['flips'] else (10000 if rec['streak']>=3 else 2))
                if age<=ttl:self.blocked.add(k)
            elif age<=3:self.open_edges.add(k)
        return super().choose(st)
    def snapshot(self):
        base=super().snapshot()
        evidence=[[list(edge),rec] for edge,rec in sorted(self.evidence.items())]
        payload={'schema':'mass.r7c23.selective-native-public.v1',
                 'owner_r3':P['owner_native_head'],'base':base.decode(),'evidence':evidence}
        return canonical({'data':payload,'sha256':hashlib.sha256(canonical(payload)).hexdigest()})
    @classmethod
    def restore(cls,raw):
        if type(raw) is not bytes or not 0<len(raw)<262144:
            raise ValueError('R7C23_BAD_SNAPSHOT_SIZE')
        wire=json.loads(raw)
        if set(wire)!={'data','sha256'}:raise ValueError('R7C23_SNAPSHOT_SCHEMA')
        data=wire['data']
        if (data['schema']!='mass.r7c23.selective-native-public.v1' or
            data['owner_r3']!=P['owner_native_head'] or
            hashlib.sha256(canonical(data)).hexdigest()!=wire['sha256']):
            raise ValueError('R7C23_AUTHENTICATED_SNAPSHOT_FAIL')
        parent=Navigator.restore(data['base'].encode())
        obj=cls()
        obj.__dict__.update(parent.__dict__)
        evidence={}
        for k,v in data['evidence']:
            edge=tuple(k)
            if (len(edge)!=3 or not all(type(n)is int for n in edge) or
                not isinstance(v,dict) or set(v)!={'time','status','streak','flips','blocked_seen','clear_seen'} or
                not all(type(n)is int and n>=0 for n in v.values()) or
                v['status'] not in (0,1) or v['time']>obj.steps or edge in evidence):
                raise ValueError('R7C23_INVALID_BELIEF')
            evidence[edge]=v
        if len(evidence)>4096:raise ValueError('R7C23_BELIEF_OVERFLOW')
        obj.evidence=evidence
        return obj

class ConventionalTTL(c20.Conventional):
    """Independent conventional empirical motor + fixed 2-step occupancy expiry."""
    def reset_episode(self,width,height):
        super().reset_episode(width,height)
        self.clock=0
        self.evidence={}
    def choose(self,st):
        now=self.clock
        edge=(st.x,st.y,st.direction)
        self.evidence[edge]=(now,bool(st.front_blocked))
        self.blocked.clear()
        self.open.clear()
        for key,(tick,blocked) in self.evidence.items():
            if now-tick<=2:
                (self.blocked if blocked else self.open).add(key)
        self.clock+=1
        return super().choose(st)

class ConventionalProbabilistic(c20.Conventional):
    """Independent conventional learned motor and discounted Beta edge occupancy."""
    def reset_episode(self,width,height):
        super().reset_episode(width,height)
        self.clock=0
        self.posterior={}
    def choose(self,st):
        now=self.clock
        edge=(st.x,st.y,st.direction)
        a,b,last=self.posterior.get(edge,(1.0,1.0,now))
        decay=0.8**max(0,now-last)
        a=1+(a-1)*decay+int(bool(st.front_blocked))
        b=1+(b-1)*decay+int(not bool(st.front_blocked))
        self.posterior[edge]=(a,b,now)
        self.blocked.clear()
        self.open.clear()
        for key,(a,b,tick) in self.posterior.items():
            decay=0.8**max(0,now-tick)
            aa=1+(a-1)*decay
            bb=1+(b-1)*decay
            p=aa/(aa+bb)
            if p>=0.60:self.blocked.add(key)
            elif p<=0.40:self.open.add(key)
        self.clock+=1
        return super().choose(st)

def make(arm,fit):
    if arm=='native_selective':
        m=NativeSelective()
        for family,seed,action,b,n,r,t in fit:
            m.reset_episode(32,32)
            m.observe(b,action,n,r,t,True)
        assert all(m._motor(d) is not None for d in range(4))
        assert m.core.core.feedback_updates==12
        return m
    if arm=='native_persistent':return c21.choose_model('native_sensor_memory',fit)
    if arm=='original':return c21.choose_model('original',fit)
    if arm=='conventional_recent':return c22.ConventionalRecent(fit)
    if arm=='conventional_ttl':return ConventionalTTL(fit)
    if arm=='conventional_probabilistic':return ConventionalProbabilistic(fit)
    raise ValueError('UNKNOWN_ARM')

def cold(arm,blob,dims):
    if arm=='native_selective':
        prog="""import sys
from research.mass_r7c23.run import NativeSelective
m=NativeSelective.restore(sys.stdin.buffer.read())
assert len(m.evidence)>0
print(m.width,m.height)
"""
        r=subprocess.run([sys.executable,'-B','-c',prog],input=blob,cwd=ROOT,
            capture_output=True,timeout=30,
            env=dict(os.environ,PYTHONPATH=str(ROOT),PYTHONDONTWRITEBYTECODE='1'))
        assert r.returncode==0,('COLD_NATIVE_SELECTIVE_FAIL',r.stderr.decode())
        assert r.stdout.decode().strip()==f'{dims[0]} {dims[1]}'
    elif arm=='native_persistent':c21.cold_restore('native_sensor_memory',blob,dims)
    elif arm=='original':c21.cold_restore('original',blob,dims)
    else:c21.cold_restore('conventional',blob,dims)

def run_family(arm,model,family,seeds):
    env=c20.env_make(family)
    summary={'episodes':0,'wins':0,'collision_terminated':0,'horizons':0,'actions':0,
             'public_blocked_forward':0,'physical_no_motion_forward':0,'source_reward_sum':0.0,
             'observed_front_cell_reversals':0}
    episodes=[]
    try:
        for seed in seeds:
            obs,_=env.reset(seed=seed)
            goal=c20.goal_from(obs)
            dims=tuple(map(int,obs['image'].shape[:2]))
            model.reset_episode(*dims)
            trace=[]
            seen_cells={}
            success=False
            terminal_negative=False
            horizon=False
            for step in range(P['dev']['source_task_action_cap']):
                b=c22.public_dynamic(obs,goal)
                dx,dy=c20.DIR[b.direction]
                front=(b.x+dx,b.y+dy)
                status=int(b.front_blocked)
                if front in seen_cells and seen_cells[front]!=status:
                    summary['observed_front_cell_reversals']+=1
                seen_cells[front]=status
                action=model.choose(b)
                assert type(action)is int and action in (0,1,2)
                nxt,reward,done,truncated,_=env.step(action)
                n=c22.public_dynamic(nxt,goal)
                reward=float(reward)
                if arm.startswith('conventional'):
                    model.observe(b,action,n,reward,bool(done))
                else:
                    model.observe(b,action,n,reward,bool(done),False)
                summary['actions']+=1
                summary['source_reward_sum']+=reward
                summary['public_blocked_forward']+=int(action==2 and b.front_blocked)
                summary['physical_no_motion_forward']+=int(action==2 and (b.x,b.y)==(n.x,n.y))
                trace.append([b.x,b.y,b.direction,b.goal_x,b.goal_y,status,action,
                    n.x,n.y,n.direction,int(n.front_blocked),reward,
                    int(bool(done)),int(bool(truncated))])
                obs=nxt
                if done or truncated:
                    success=reward>0
                    terminal_negative=bool(done and reward<0)
                    horizon=bool(truncated)
                    break
            summary['episodes']+=1
            summary['wins']+=int(success)
            summary['collision_terminated']+=int(terminal_negative)
            summary['horizons']+=int(horizon)
            blob=model.checkpoint() if arm.startswith('conventional') else model.snapshot()
            cold(arm,blob,dims)
            episodes.append({'family':family,'seed':seed,'steps':len(trace),
                'success':success,'collision_terminated':terminal_negative,'truncated':horizon,
                'trace':trace,'trace_sha256':hashlib.sha256(canonical(trace)).hexdigest(),
                'checkpoint_bytes':len(blob),'checkpoint_sha256':hashlib.sha256(blob).hexdigest()})
    finally:env.close()
    return summary,episodes

def main():
    import gymnasium,minigrid
    ap=argparse.ArgumentParser()
    ap.add_argument('--arm',choices=P['arms'],required=True)
    ap.add_argument('--out',required=True)
    args=ap.parse_args()
    c20.check_source()
    assert P['original_source'].split('@')[-1]=='7f5853792ea7f04f75614661006d87fcf949f26d'
    t0=time.process_time()
    fit,fit_sha,counts=c20.fit_data()
    assert fit_sha==P['fit']['expected_fit_sha256']
    model=make(args.arm,fit)
    t1=time.process_time()
    totals={};episodes=[]
    for family,seeds in ((P['static_original'],P['dev']['static_seeds']),
                         (P['moving_original'],P['dev']['dynamic_seeds'])):
        summary,logs=run_family(args.arm,model,family,seeds)
        totals[family]=summary;episodes.extend(logs)
    t2=time.process_time()
    output={'schema':P['schema'],'arm':args.arm,
        'protocol_sha256':hashlib.sha256((HERE/'PREREG.json').read_bytes()).hexdigest(),
        'upstream':P['original_source'].split('@')[-1],
        'owner_native_head':P['owner_native_head'],
        'fit_sha256':fit_sha,'fit_rows':len(fit),'fit_counts':counts,
        'totals':totals,'episodes':episodes,
        'max_checkpoint_bytes':max(e['checkpoint_bytes'] for e in episodes),
        'cpu_fit_seconds':round(t1-t0,6),'cpu_dev_seconds':round(t2-t1,6),
        'peak_process_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'gymnasium':gymnasium.__version__}
    Path(args.out).write_bytes(canonical(output)+b'\n')
    print('R7C23_ORIGINAL_PUBLIC',args.arm,json.dumps(totals,sort_keys=True))
if __name__=='__main__':main()
