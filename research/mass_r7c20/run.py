"""Mass R7-C20 public development on pinned authentic Farama MiniGrid. No protected first-use."""
import collections, hashlib, heapq, importlib.util, json, os, random, resource, subprocess, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from research.native.itd02.r3.navigator import Navigator
from research.native.itd02.r1.native_policy import PublicGrid,canonical
P=json.loads((HERE/'PREREG.json').read_text())
DIR=((1,0),(0,1),(-1,0),(0,-1))
def check_source():
    for name,want in [('r1/native_policy.py','3aa22b1e418a7f8cd9619c476f02b8c614917b16'),('r2/affordance_cells.py','f7e47dfef309e1c0bcc871d518154fd950b3eca0'),('r3/navigator.py','5348238f4ec2183bea29262659883391b5f429fd')]:
        got=subprocess.check_output(['git','hash-object',str(ROOT/'research/native/itd02'/name)],text=True).strip()
        assert got==want,(name,got)
def patched():
    source=(ROOT/'research/native/itd02/r3/navigator.py').read_text()
    old='                    if edge in self.blocked:continue\n                    dx,dy=self._motor(d)'
    new='                    if edge in self.blocked:continue\n                    if first<0 and pose==start and st.front_blocked:continue\n                    dx,dy=self._motor(d)'
    assert source.count(old)==1
    path=HERE/'_dev_r3_guard.py';path.write_text(source.replace(old,new))
    spec=importlib.util.spec_from_file_location('r7c20_dev_patch',path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod.Navigator
def public(o,goal):
    import numpy as np
    from minigrid.core.constants import OBJECT_TO_IDX as T
    img=o['image'];assert img.ndim==3 and img.shape[2]==3
    xy=np.argwhere(img[:,:,0]==T['agent']);assert len(xy)==1,('AGENT_COUNT',len(xy))
    x,y=map(int,xy[0]);d=int(o['direction']);assert d in range(4)
    dx,dy=DIR[d];fx,fy=x+dx,y+dy
    if not (0<=fx<img.shape[0] and 0<=fy<img.shape[1]):blocked=True
    else:
        token=int(img[fx,fy,0])
        assert token in (T['wall'],T['empty'],T['goal'],T['agent']),('UNKNOWN_PUBLIC_TILE',token)
        blocked=token==T['wall']
    return PublicGrid(x,y,goal[0],goal[1],d,bool(blocked))
def goal_from(o):
    import numpy as np
    from minigrid.core.constants import OBJECT_TO_IDX as T
    xy=np.argwhere(o['image'][:,:,0]==T['goal'])
    assert len(xy)==1,('GOAL_COUNT',len(xy))
    return tuple(map(int,xy[0]))
def env_make(family):
    import gymnasium as gym
    from minigrid.wrappers import FullyObsWrapper
    return FullyObsWrapper(gym.make(family))
def fit_data():
    allrows=[];counts=collections.Counter(); nsteps=P['roles']['fit_steps_per_family']//len(P['roles']['fit_seeds'])
    for family in P['source_original']['gym_ids']:
        env=env_make(family)
        try:
            for seed in P['roles']['fit_seeds']:
                rng=random.Random(910300+seed);spent=0
                while spent<nsteps:
                    o,_=env.reset(seed=seed);goal=goal_from(o)
                    while spent<nsteps:
                        b=public(o,goal);action=rng.randrange(3)
                        new,reward,terminated,truncated,_=env.step(action);n=public(new,goal)
                        allrows.append((family,seed,action,b,n,float(reward),bool(terminated)))
                        counts[family]+=1;spent+=1;o=new
                        if terminated or truncated:break
        finally:env.close()
        assert counts[family]==P['roles']['fit_steps_per_family']
    movements={};blocked=[]
    for row in allrows:
        family,seed,a,b,n,_,_=row
        if a!=2:continue
        md=abs(n.x-b.x)+abs(n.y-b.y)
        if not b.front_blocked and md==1:movements.setdefault(b.direction,row)
        if b.front_blocked and md==0 and len(blocked)<8:blocked.append(row)
    assert len(movements)==4 and len(blocked)==8,('INSUFFICIENT_PUBLIC_FIT',sorted(movements),len(blocked))
    selected=[movements[d] for d in range(4)]+blocked
    def serial(row):
        f,s,a,b,n,r,t=row
        return [f,s,a,b.__dict__,n.__dict__,r,t]
    fit_hash=hashlib.sha256(canonical([serial(x) for x in selected])).hexdigest()
    return selected,fit_hash,dict(counts)
class Conventional:
    """Separately implemented learned-motor A* with online *public* observed spatial occupancy."""
    def __init__(self,fit):
        self.motor={};self.records=collections.defaultdict(lambda:[0,0])
        for d in range(4):
            c=collections.Counter((n.x-b.x,n.y-b.y) for f,s,a,b,n,r,t in fit if a==2 and b.direction==d and abs(n.x-b.x)+abs(n.y-b.y)==1)
            assert c
            self.motor[d]=c.most_common(1)[0][0]
        for f,s,a,b,n,r,t in fit:
            if a==2:
                k=bool(b.front_blocked);self.records[k][0]+=1;self.records[k][1]+=int(b.x==n.x and b.y==n.y)
        assert self.records[True]==[8,8] and self.records[False]==[4,0]
        self.reset_episode(8,8)
    def reset_episode(self,w,h):
        self.w=w;self.h=h;self.blocked=set();self.open=set();self.visits=collections.Counter()
    def choose(self,b):
        edge=(b.x,b.y,b.direction)
        if b.front_blocked:self.blocked.add(edge);self.open.discard(edge)
        else:self.open.add(edge);self.blocked.discard(edge)
        start=(b.x,b.y,b.direction);target=(b.goal_x,b.goal_y)
        if start[:2]==target:return 0
        q=[(0.,0.,0,start,-1)];dist={start:0.};serial=0
        while q:
            _,cost,_,s,initial=heapq.heappop(q)
            if cost>dist.get(s,float('inf'))+1e-9:continue
            x,y,d=s
            if (x,y)==target:return initial if initial>=0 else 0
            actions=[(0,(x,y,(d-1)%4),.35),(1,(x,y,(d+1)%4),.35)]
            if s not in self.blocked:
                dx,dy=self.motor[d];xx,yy=x+dx,y+dy
                if 0<=xx<self.w and 0<=yy<self.h:
                    weight=(1. if s in self.open else 1.35)+.04*min(10,self.visits.get((xx,yy,d),0))
                    actions.append((2,(xx,yy,d),weight))
            for a,n,w in actions:
                alt=cost+w
                if alt+1e-9<dist.get(n,float('inf')):
                    dist[n]=alt;serial+=1
                    h=abs(n[0]-target[0])+abs(n[1]-target[1])
                    heapq.heappush(q,(alt+h,alt,serial,n,a if initial<0 else initial))
        return 0
    def observe(self,b,a,n,r,t):
        edge=(b.x,b.y,b.direction)
        if a==2:
            if (b.x,b.y)==(n.x,n.y):self.blocked.add(edge);self.open.discard(edge)
            else:self.open.add(edge);self.blocked.discard(edge)
        self.visits[(n.x,n.y,n.direction)]+=1
    def checkpoint(self):
        data={'motor':{str(k):list(v) for k,v in self.motor.items()},'w':self.w,'h':self.h,
              'blocked':[list(v) for v in sorted(self.blocked)],'open':[list(v) for v in sorted(self.open)],
              'visits':[[list(k),v] for k,v in sorted(self.visits.items())]}
        return canonical({'body':data,'sha256':hashlib.sha256(canonical(data)).hexdigest()})
def make_model(arm,fit):
    if arm=='conventional':return Conventional(fit)
    p=(Navigator if arm=='original' else patched())()
    for family,seed,a,b,n,reward,term in fit:
        p.reset_episode(32,32);p.observe(b,a,n,reward,term,True)
    assert all(p._motor(d) is not None for d in range(4))
    assert p.core.blocked_samples==8 and p.core.core.feedback_updates==12
    return p
def cold(arm,blob,expected):
    if arm=='conventional':
        program='''import json,hashlib,sys
from research.native.itd02.r1.native_policy import canonical
w=json.loads(sys.stdin.buffer.read()); assert hashlib.sha256(canonical(w["body"])).hexdigest()==w["sha256"]
print(w["body"]["w"],w["body"]["h"])'''
    elif arm=='original':
        program='''import sys
from research.native.itd02.r3.navigator import Navigator
p=Navigator.restore(sys.stdin.buffer.read());print(p.width,p.height)'''
    else:
        program=f'''import importlib.util,sys
spec=importlib.util.spec_from_file_location("r7c20_dev_patch",{str(HERE/'_dev_r3_guard.py')!r})
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
p=mod.Navigator.restore(sys.stdin.buffer.read());print(p.width,p.height)'''
    r=subprocess.run([sys.executable,'-B','-c',program],input=blob,capture_output=True,timeout=25,cwd=ROOT,env=dict(os.environ,PYTHONPATH=str(ROOT),PYTHONDONTWRITEBYTECODE='1'))
    assert r.returncode==0,('COLD_FAIL',r.stdout.decode(),r.stderr.decode())
    assert r.stdout.decode().strip()==f'{expected[0]} {expected[1]}'
def dev_evaluate(arm,model):
    totals={};episodes=[];sizes=[]
    for family in P['source_original']['gym_ids']:
        env=env_make(family)
        try:
            result={'episodes':0,'wins':0,'actions':0,'blocked_forward':0,'first_blocked_forward':0,'repeat_blocked_forward':0,'total_reward':0.0}
            for seed in P['roles']['dev_seeds']:
                ob,_=env.reset(seed=seed);goal=goal_from(ob)
                width,height=map(int,ob['image'].shape[:2])
                model.reset_episode(width,height)
                visited=set();trace=[];won=False;result['episodes']+=1
                for step in range(P['roles']['dev_cap_steps']):
                    b=public(ob,goal);pose=(b.x,b.y,b.direction);seen=pose in visited;visited.add(pose)
                    action=model.choose(b);assert type(action)==int and action in (0,1,2)
                    next_obs,reward,done,truncated,_=env.step(action)
                    n=public(next_obs,goal)
                    if action==2 and b.front_blocked:assert (b.x,b.y)==(n.x,n.y),'PUBLIC_SENSOR_CONTRADICTED'
                    wasted=action==2 and b.front_blocked and (b.x,b.y)==(n.x,n.y)
                    if arm=='conventional':model.observe(b,action,n,float(reward),bool(done))
                    else:model.observe(b,action,n,float(reward),bool(done),False)
                    result['actions']+=1;result['total_reward']+=float(reward)
                    if wasted:
                        result['blocked_forward']+=1
                        result['repeat_blocked_forward' if seen else 'first_blocked_forward']+=1
                    trace.append([b.x,b.y,b.direction,int(b.front_blocked),action,n.x,n.y,n.direction,float(reward)])
                    ob=next_obs
                    if done or truncated:won=float(reward)>0;break
                result['wins']+=int(won)
                blob=model.checkpoint() if arm=='conventional' else model.snapshot()
                sizes.append(len(blob));cold(arm,blob,(width,height))
                episodes.append({'family':family,'seed':seed,'success':won,'steps':len(trace),
                    'trace_sha256':hashlib.sha256(canonical(trace)).hexdigest(),'checkpoint_sha256':hashlib.sha256(blob).hexdigest(),'checkpoint_bytes':len(blob)})
            totals[family]=result
        finally:env.close()
    return totals,episodes,max(sizes)
def main():
    import argparse,gymnasium,minigrid
    ap=argparse.ArgumentParser();ap.add_argument('--arm',choices=['original','patched','conventional'],required=True);ap.add_argument('--out',required=True);args=ap.parse_args()
    check_source();t0=time.process_time()
    selected,fit_sha,counts=fit_data();model=make_model(args.arm,selected);t1=time.process_time()
    totals,episodes,size=dev_evaluate(args.arm,model);t2=time.process_time()
    output={'arm':args.arm,'upstream':P['source_original']['commit'],'original_head':P['yggdrasil']['r3_head'],
        'prereg_sha256':hashlib.sha256((HERE/'PREREG.json').read_bytes()).hexdigest(),
        'fit_sha256':fit_sha,'fit_rows':len(selected),'fit_total':counts,'totals':totals,'episodes':episodes,
        'max_checkpoint_bytes':size,'cpu_fit_seconds':round(t1-t0,5),'cpu_dev_seconds':round(t2-t1,5),
        'peak_process_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'python':sys.version.split()[0],'gymnasium':gymnasium.__version__}
    Path(args.out).write_bytes(canonical(output)+b'\n')
    print('R7C20_PUBLIC_ORIGINAL_SOURCE',args.arm,json.dumps({'fit_sha256':fit_sha,'totals':totals,'max_checkpoint_bytes':size},sort_keys=True))
if __name__=='__main__':main()
