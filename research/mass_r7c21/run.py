"""R7-C21: source-original public sensor-memory ablation. No protected science."""
import argparse, collections, hashlib, json, os, resource, subprocess, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from research.mass_r7c20 import run as c20
from research.native.itd02.r3.navigator import Navigator
from research.native.itd02.r1.native_policy import canonical, features
HERE=Path(__file__).resolve().parent
P=json.loads((HERE/"PREREG.json").read_text())
assert P['parent_c20']=='8d5eecc04141401a5d4f102395cb7fa3637b493f'
assert P['original_r3']=='fbf78bcc6988755ba0e3e026f06d273839c1fa9f'
# Reuse the previously frozen, already authenticated FIT generator, keeping all FIT
# examples exactly the same as C20. Only TEST role and proposed mechanism change.
c20.P=dict(c20.P)
c20.P['roles']=dict(c20.P['roles'],dev_seeds=P['dev_roles']['fresh_dev_seeds'],
                    dev_cap_steps=P['dev_roles']['max_actions_per_episode'])
c20.P['source_original']=dict(c20.P['source_original'],gym_ids=P['source_types'])

class SensorMemory(Navigator):
    """Treat the current public front sensor as a persistent episode observation.

    This candidate intentionally does NOT alter native motor/local plasticity,
    does NOT see the full wall map, and does NOT infer hidden future outcomes.
    """
    def choose(self,st):
        features(st)
        edge=(st.x,st.y,st.direction)
        if st.front_blocked:
            self.blocked.add(edge)
            self.open_edges.discard(edge)
        else:
            self.open_edges.add(edge)
            self.blocked.discard(edge)
        return super().choose(st)

def cold_restore(arm,blob,expected):
    if arm!="native_sensor_memory":
        c20.cold({'guard_only':'patched'}.get(arm,arm),blob,expected)
        return
    source="""import sys
from research.mass_r7c21.run import SensorMemory
model=SensorMemory.restore(sys.stdin.buffer.read())
print(model.width,model.height)
"""
    p=subprocess.run([sys.executable,'-B','-c',source],input=blob,cwd=ROOT,
                     capture_output=True,timeout=30,
                     env=dict(os.environ,PYTHONPATH=str(ROOT),PYTHONDONTWRITEBYTECODE='1'))
    assert p.returncode==0,('FAILED_COLD_RESTORE',p.stderr.decode())
    assert p.stdout.decode().strip()==f"{expected[0]} {expected[1]}"

def choose_model(arm,selected):
    if arm=='original':return c20.make_model('original',selected)
    if arm=='guard_only':return c20.make_model('patched',selected)
    if arm=='conventional':return c20.make_model('conventional',selected)
    assert arm=='native_sensor_memory'
    p=SensorMemory()
    for family,seed,a,b,n,reward,terminal in selected:
        p.reset_episode(32,32)
        p.observe(b,a,n,reward,terminal,True)
    assert all(p._motor(d) is not None for d in range(4))
    assert p.core.blocked_samples==8 and p.core.core.feedback_updates==12
    return p

def evaluate(arm,model):
    totals={};eps=[]
    for family in P['source_types']:
        env=c20.env_make(family)
        tot={'episodes':0,'wins':0,'actions':0,'blocked_forward':0,
             'first_blocked_forward':0,'repeat_blocked_forward':0,'total_reward':0.}
        try:
            for seed in P['dev_roles']['fresh_dev_seeds']:
                o,_=env.reset(seed=seed)
                goal=c20.goal_from(o)
                width,height=map(int,o['image'].shape[:2])
                model.reset_episode(width,height)
                seen=set();trace=[];success=False
                for step in range(P['dev_roles']['max_actions_per_episode']):
                    b=c20.public(o,goal)
                    pose=(b.x,b.y,b.direction)
                    visited=pose in seen
                    seen.add(pose)
                    a=model.choose(b)
                    assert type(a)is int and a in (0,1,2)
                    nxt,reward,done,trunc,_=env.step(a)
                    n=c20.public(nxt,goal)
                    fail_move=(b.x,b.y)==(n.x,n.y)
                    if a==2 and b.front_blocked:assert fail_move, 'SOURCE_PUBLIC_FRONT_CONTRADICTION'
                    bad=(a==2 and b.front_blocked and fail_move)
                    if arm=='conventional':model.observe(b,a,n,float(reward),bool(done))
                    else:model.observe(b,a,n,float(reward),bool(done),False)
                    tot['actions']+=1;tot['total_reward']+=float(reward)
                    if bad:
                        tot['blocked_forward']+=1
                        tot['repeat_blocked_forward' if visited else 'first_blocked_forward']+=1
                    trace.append([b.x,b.y,b.direction,b.goal_x,b.goal_y,int(b.front_blocked),
                                  a,n.x,n.y,n.direction,int(n.front_blocked),float(reward),
                                  int(bool(done)),int(bool(trunc))])
                    o=nxt
                    if done or trunc:
                        success=bool(float(reward)>0)
                        break
                tot['episodes']+=1;tot['wins']+=int(success)
                blob=model.checkpoint() if arm=='conventional' else model.snapshot()
                cold_restore(arm,blob,(width,height))
                eps.append({'family':family,'seed':seed,'success':success,
                    'steps':len(trace),'trace':trace,
                    'trace_sha256':hashlib.sha256(canonical(trace)).hexdigest(),
                    'checkpoint_sha256':hashlib.sha256(blob).hexdigest(),
                    'checkpoint_bytes':len(blob)})
        finally:env.close()
        totals[family]=tot
    return totals,eps

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--arm',choices=P['arms'],required=True)
    ap.add_argument('--out',required=True)
    args=ap.parse_args()
    import gymnasium,minigrid
    c20.check_source()
    t0=time.process_time()
    rows,fit_sha,counts=c20.fit_data()
    model=choose_model(args.arm,rows)
    t1=time.process_time()
    totals,eps=evaluate(args.arm,model)
    t2=time.process_time()
    output={'schema':'mass.r7c21.public-original-source.v1',
       'arm':args.arm,'source_commit':P['original_source'].split('@')[-1],
       'native_head':P['original_r3'],
       'prereg_sha256':hashlib.sha256((HERE/'PREREG.json').read_bytes()).hexdigest(),
       'fit_sha256':fit_sha,'fit_rows':len(rows),'fit_source_actions':counts,
       'totals':totals,'episodes':eps,
       'max_checkpoint_bytes':max(x['checkpoint_bytes'] for x in eps),
       'cpu_fit_seconds':round(t1-t0,6),'cpu_dev_seconds':round(t2-t1,6),
       'peak_process_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
       'python':sys.version.split()[0],'gymnasium':gymnasium.__version__}
    Path(args.out).write_bytes(canonical(output)+b'\n')
    print('R7C21_ORIGINAL_PUBLIC',args.arm,json.dumps(totals,sort_keys=True))
if __name__=='__main__':main()
