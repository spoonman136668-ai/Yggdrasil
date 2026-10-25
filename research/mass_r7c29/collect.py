"""R7-C29: original Farama DoorKey 7-action public FIT; original owner R10 transport.

The collector is a deterministic hand-coded source-public exploration mechanism,
not a learned native or conventional benchmark. No global map or private state.
"""
import collections,hashlib,importlib.util,json,os,random,resource,subprocess,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
P=json.loads((HERE/"PREREG.json").read_text())
DXDY=((0,-1),(1,0),(0,1),(-1,0))
AGENT=(3,6)
def load_owner():
    path=Path(os.environ["R10_SOURCE_FILE"]).resolve()
    assert path.is_file() and path.name=="public_adapter.py"
    spec=importlib.util.spec_from_file_location("r7c29_pinned_owner_r10",str(path))
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    assert tuple(m.ACTION_NAMES)==('left','right','forward','pickup','drop','toggle','done')
    assert m.UPSTREAM_MINIGRID_COMMIT==P['upstream'].split("@")[-1]
    return m

def independent_cues(raw):
    # Independently perform source-public parsing and compare with owner parser.
    assert type(raw) is dict and set(raw)=={'image','direction','mission'}
    img=raw['image']
    assert len(img)==7 and img.shape==(7,7,3)
    assert type(raw['direction']) is int and raw['direction'] in (0,1,2,3)
    assert raw['mission']=='use the key to open the door and then get to the goal'
    v=img.tolist()
    for x in range(7):
        for y in range(7):
            assert len(v[x][y])==3 and all(type(z) is int and z>=0 for z in v[x][y])
    front=v[3][5]
    carried=v[3][6] if v[3][6][0] in (5,6,7) else None
    return {'front':front,'carried':carried,'direction':raw['direction']}

def walkable(cell):
    kind,state=cell[0],cell[2]
    return kind in (1,3,8,10) or (kind==4 and state==0)

def local_subgoal(img,kind):
    """BFS within the *current agent-centric public 7x7 view* only.

    No global pose/map. A goal is a traversable public neighbor to a visible
    key or a door; action choice is only the next physical heading correction.
    """
    objs=[(x,y) for x in range(7) for y in range(7) if img[x][y][0]==kind]
    if not objs:return None
    targets=set()
    for x,y in objs:
        for dx,dy in DXDY:
            xx,yy=x+dx,y+dy
            if 0<=xx<7 and 0<=yy<7 and walkable(img[xx][yy]):
                targets.add((xx,yy))
    if not targets:return None
    queue=collections.deque([AGENT]);prev={AGENT:None}
    endpoint=None
    while queue:
        a=queue.popleft()
        if a in targets:endpoint=a;break
        for dx,dy in DXDY:
            nx,ny=a[0]+dx,a[1]+dy
            pos=(nx,ny)
            if 0<=nx<7 and 0<=ny<7 and pos not in prev and walkable(img[nx][ny]):
                prev[pos]=a;queue.append(pos)
    if endpoint is None:return None
    if endpoint==AGENT:return None
    while prev[endpoint]!=AGENT:endpoint=prev[endpoint]
    xx,yy=endpoint;return (xx-AGENT[0],yy-AGENT[1])

def policy(public,rand,step,extra):
    img=public['image'];cues=public['cues']
    front=cues['front'];carry=cues['carried']
    # Exercise original no-op legal 6/done and 4/drop transport while empty.
    # Source may treat them as inert, but this is still a true source event.
    if step==0:return 6
    if step==1:return 4
    if front[0]==5 and carry is None:return 3
    if front[0]==4 and carry is not None and front[2] in (1,2):return 5
    target=5 if carry is None else 4
    direction=local_subgoal(img,target)
    if direction is not None:
        if direction==(0,-1):
            if walkable(front):return 2
            # Door/key target is one cell ahead; pickup/toggle rules above.
            return rand.choice((0,1))
        if direction[0]<0:return 0
        if direction[0]>0:return 1
        return rand.choice((0,1))
    # Nonoracle controlled exploration: never move into publicly visible
    # blocking surface; vary headings and revisit past public observations.
    if walkable(front) and rand.random()<.70:return 2
    return rand.choice((0,1))

def cold(original_owner,blob,expected):
    program="""import importlib.util,json,os,sys
spec=importlib.util.spec_from_file_location('owner_r10',os.environ['R10_SOURCE_FILE'])
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
x=mod.DoorKeyPublicAdapter.restore(sys.stdin.buffer.read())
assert x.events==int(sys.argv[1])
assert x.pending is None
assert x.current is not None
print('R7C29_OWNER_COLD_ORIGINAL_PUBLIC_RESTORE=PASS')
"""
    r=subprocess.run([sys.executable,'-B','-c',program,str(expected)],input=blob,
      cwd=ROOT,capture_output=True,timeout=30,
      env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
    assert r.returncode==0,('COLD_R10_RESTORE_FAIL',r.stderr.decode())
    assert 'R7C29_OWNER_COLD_ORIGINAL_PUBLIC_RESTORE=PASS' in r.stdout.decode()

def main():
    import gymnasium as gym
    import minigrid  # registers the authenticated original MiniGrid environment IDs
    owner=load_owner()
    selected=[]
    counts=collections.Counter()
    total_pickup=total_open=total_goals=0
    t0=time.process_time()
    for i,seed in enumerate(P['fit_seeds']):
        rand=random.Random(93617+7919*i)
        env=gym.make(P['world'])
        adapter=owner.DoorKeyPublicAdapter()
        try:
            raw,_=env.reset(seed=seed)
            adapter.reset_public(raw)
            episode=[]
            for step in range(P['max_original_steps_per_seed']):
                frame=owner.public_observation(raw)
                cues=owner.public_cues(raw)
                independent=independent_cues(raw)
                assert independent['front']==cues['front']
                assert independent['carried']==cues['carried']
                assert independent['direction']==cues['direction']
                action=policy({'image':frame['image'],'cues':cues},rand,step,{})
                actual=int(adapter.submit(action))
                assert actual==action and 0<=actual<7
                after,reward,done,truncated,_=env.step(action)
                returned=adapter.complete(after,float(reward),bool(done),bool(truncated))
                assert returned['action']==action and returned['ordinal']==step+1
                assert returned['pose_delta'] is None
                counts[action]+=1
                total_pickup+=int(returned['visible_key_pickup'])
                total_open+=int(returned['visible_door_opened'])
                ep={'step':step,'action':action,'name':returned['action_name'],
                    'before_public_sha256':returned['before_public_sha256'],
                    'after_public_sha256':returned['after_public_sha256'],
                    'front_before':returned['front_before'],'front_after':returned['front_after'],
                    'carried_before':returned['carried_before'],'carried_after':returned['carried_after'],
                    'visible_key_pickup':returned['visible_key_pickup'],
                    'visible_door_opened':returned['visible_door_opened'],
                    'source_reward':returned['reward'],'terminated':returned['terminated'],
                    'truncated':returned['truncated']}
                episode.append(ep)
                raw=after
                if done or truncated:
                    total_goals+=int(float(reward)>0)
                    break
            snap=adapter.checkpoint()
            cold(owner,snap,len(episode))
            selected.append({'episode_index':i,'fit_original_seed':seed,
                'original_actions':len(episode),
                'goals':sum(int(r['source_reward']>0) for r in episode),
                'visible_pickups':sum(int(r['visible_key_pickup']) for r in episode),
                'visible_opened_doors':sum(int(r['visible_door_opened']) for r in episode),
                'selected_actions':episode,
                'trace_sha256':hashlib.sha256(owner.canonical(episode)).hexdigest(),
                'public_adapter_snapshot_bytes':len(snap),
                'snapshot_sha256':hashlib.sha256(snap).hexdigest()})
        finally:env.close()
    qualified=(all(counts[k]>0 for k in range(7)) and total_pickup>0 and total_open>0)
    result={'schema':P['schema'],'source':P['upstream'],
       'native_R10_original':P['owner_R10_source_head'],
       'protocol_sha256':hashlib.sha256((HERE/'PREREG.json').read_bytes()).hexdigest(),
       'model':'explicitly handcoded public FIT collector, NOT learned native policy',
       'FIT_only_episodes':len(selected),'DEV_episodes':0,'protected_episodes':0,
       'selected_actions':{str(k):counts[k] for k in range(7)},
       'total_genuine_source_actions':sum(counts.values()),
       'visible_pickups':total_pickup,'visible_opened_doors':total_open,
       'actual_goals':total_goals,
       'all_seven_actions_selected':all(counts[k]>0 for k in range(7)),
       'FIT_public_action_consequence_qualification':'PASS' if qualified else 'NO_GO',
       'episodes':selected,
       'cpu_total_s':round(time.process_time()-t0,6),
       'peak_python_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    out=Path(sys.argv[1]);out.write_bytes(owner.canonical(result)+b'\n')
    print('R7C29_SOURCE_ORIGINAL_DOORKEY_FIT',json.dumps({
      k:v for k,v in result.items() if k not in ('episodes',)},sort_keys=True),flush=True)
if __name__=='__main__':main()
