"""Mass R7-C34 — original DoorKey public FIT: learned post-door source actions.

Owner R10/R11/R12 untouched. The pre-door collector is EXPLICITLY scripted.
After the first actually returned original door-open event, native-proxy and
independent conventional policies select ALL their own original actions.
"""
import collections,hashlib,json,os,random,resource,subprocess,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT))
from research.mass_r7c29 import collect as collector
sys.path.insert(0,str(Path(os.environ['OWNER_R11_ROOT']).resolve()))
from research.native.itd02.r10 import public_adapter as owner
P=json.loads((HERE/'PREREG.json').read_text())
SOURCE_ID='MiniGrid-DoorKey-8x8-v0'
def canon(data):
    return json.dumps(data,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def frame(raw):
    return owner.public_observation(collector.normalized_original_public(raw))
def cues(public):
    return owner.public_cues(public)
def local_key(public):
    img=public['image'];c=cues(public)
    pts=((3,5),(2,5),(4,5),(3,4),(2,4),(4,4))
    return str(public['direction'])+'|'+str(int(c['carried'] is not None))+'|'+','.join(
       str(img[x][y][0])+'-'+str(img[x][y][2]) for x,y in pts)
def global_key(public):
    return owner.digest(public)
def feature(kind,public):
    return local_key(public) if kind=='native_local' else global_key(public)
def fitted(kind,rows):
    context={}
    globalcounts=[[0,0.] for _ in range(7)]
    for row in rows:
        ctx=feature(kind,row['public'])
        bins=context.setdefault(ctx,[[0,0.] for _ in range(7)])
        a=row['action'];v=row['discounted_original_source_reward']
        bins[a][0]+=1;bins[a][1]+=v
        globalcounts[a][0]+=1;globalcounts[a][1]+=v
    return {'schema':'mass.r7c34.original-public-learned-return.v1',
        'kind':kind,'contexts':dict(sorted(context.items())),
        'global':globalcounts,'discount':0.97,'source':P['original_source']}
def select(model,public):
    ctx=feature(model['kind'],public)
    current=model['contexts'].get(ctx)
    vals=current if current is not None and any(k[0] for k in current) else model['global']
    # Choose highest source-FIT Monte Carlo expected return with Laplace-shrunk
    # denominator; near-zero observations may back off to global source data.
    return max(range(7),key=lambda a:(vals[a][1]/(vals[a][0]+1),-a))
def checkpoint(model):
    body=canon(model)
    return canon({'model':model,'sha256':hashlib.sha256(body).hexdigest()})
def restore(blob):
    try:
        wire=json.loads(blob)
        if set(wire)!= {'model','sha256'} or hashlib.sha256(canon(wire['model'])).hexdigest()!=wire['sha256']:
            raise ValueError('STATE_DIGEST')
        state=wire['model']
        if state['schema']!='mass.r7c34.original-public-learned-return.v1' or state['source']!=P['original_source']:
            raise ValueError('WRONG_SOURCE')
        if state['kind'] not in ('native_local','conventional_full'):raise ValueError('WRONG_KIND')
        return state
    except (ValueError,TypeError,KeyError) as exc:
        raise ValueError('COLD_SNAPSHOT_REJECTED') from exc
def cold(model,public,answer):
    program="""import json,sys
from research.mass_r7c34.run import restore,select
x=json.loads(sys.stdin.buffer.read())
model=restore(x['checkpoint'].encode())
assert select(model,x['public'])==x['action'],'COLD_WRONG_ACTION'
print('R7C34_COLD_MATCHED_LEARNED_CHOICE=PASS')
"""
    body=canon({'checkpoint':checkpoint(model).decode(),
                'public':public,'action':answer})
    r=subprocess.run([sys.executable,'-B','-c',program],cwd=ROOT,
         input=body,capture_output=True,timeout=35,
         env=dict(os.environ,OWNER_R11_ROOT=os.environ['OWNER_R11_ROOT'],
                  PYTHONPATH=str(ROOT),PYTHONDONTWRITEBYTECODE='1'))
    assert r.returncode==0,('COLD_FAILED',r.stderr.decode())
    assert 'R7C34_COLD_MATCHED_LEARNED_CHOICE=PASS' in r.stdout.decode()
def source_episode(seed,index,arm,model=None,training=False):
    import gymnasium as gym,minigrid
    env=gym.make(SOURCE_ID)
    ledger=owner.DoorKeyPublicAdapter()
    rng=random.Random(93617+7919*index)
    pre_rows=[]
    trace=[]
    opened=False
    opened_at=None
    first_cold=False
    try:
        raw,_=env.reset(seed=seed)
        ledger.reset_public(collector.normalized_original_public(raw))
        for t in range(P['source_episode_cap']):
            public=frame(raw)
            cs=cues(public)
            base=collector.policy({'image':public['image'],'cues':cs},rng,t,{})
            if opened and model is not None:
                action=select(model,public)
                assert type(action)is int and 0<=action<7
                if not first_cold:
                    cold(model,public,action)
                    first_cold=True
            else:
                action=base
            assert ledger.submit(action)==action
            nxt,reward,term,trunc,_=env.step(action)
            event=ledger.complete(collector.normalized_original_public(nxt),
                                  float(reward),bool(term),bool(trunc))
            was_post=opened
            if was_post:
                pre_rows.append({'public':public,'action':action,
                    'public_before_sha256':event['before_public_sha256']})
            if event['visible_door_opened'] and not opened:
                opened=True;opened_at=t+1
            trace.append([t,action,base,was_post,
                event['before_public_sha256'],event['after_public_sha256'],
                int(event['visible_key_pickup']),int(event['visible_door_opened']),
                float(reward),bool(term),bool(trunc)])
            raw=nxt
            if term or trunc:break
        reward_pos=bool(trace and trace[-1][8]>0)
        collected=[]
        if training and reward_pos and opened:
            for i,row in enumerate(pre_rows):
                collected.append({'public':row['public'],'action':row['action'],
                    'discounted_original_source_reward':round(float(trace[-1][8])*(0.97**(len(pre_rows)-i-1)),12)})
        return ({'seed':seed,'arm':arm,'source_goals':int(reward_pos),
            'door_opened':int(opened),'door_open_ordinal':opened_at,
            'source_actions':len(trace),'postdoor_actions':len(pre_rows),
            'learned_postdoor_actions':len(pre_rows) if model is not None else 0,
            'actual_reward_sum':round(sum(x[8] for x in trace),9),
            'trace_sha256':hashlib.sha256(canon(trace)).hexdigest(),
            'events':trace},collected)
    finally:env.close()
def main():
    import gymnasium,minigrid
    assert owner.UPSTREAM_MINIGRID_COMMIT==P['original_source'].split('@')[-1]
    t0=time.process_time()
    rows=[];fit_episodes=[]
    for i,seed in enumerate(P['training_source_seeds']):
        ep,selected=source_episode(seed,i,'original_public_collector_FIT',training=True)
        fit_episodes.append(ep);rows.extend(selected)
    observed_goals=sum(x['source_goals'] for x in fit_episodes)
    actual_post=sum(x['postdoor_actions'] for x in fit_episodes)
    fit_sha=hashlib.sha256(canon(rows)).hexdigest()
    qualified=observed_goals>0 and bool(rows)
    tfit=time.process_time()
    result={'schema':P['schema'],'source':P['original_source'],'owner_r12_sha':P['owner_r12_commit'],
        'prereg_sha256':hashlib.sha256((HERE/'PREREG.json').read_bytes()).hexdigest(),
        'FIT_actual_collector_episodes':fit_episodes,'FIT_goals':observed_goals,
        'FIT_genuine_postdoor_source_actions':actual_post,'FIT_positive_reward_rows':len(rows),
        'FIT_positive_training_digest':fit_sha,'FIT_qualifies_learned_postdoor':qualified,
        'new_DEV_or_protected_episodes_consumed':0}
    if qualified:
        models={k:fitted(k,rows) for k in ('native_local','conventional_full')}
        result['model_states']={k:{'sha256':hashlib.sha256(checkpoint(v)).hexdigest(),
            'checkpoint_bytes':len(checkpoint(v)),
            'fitted_contexts':len(v['contexts'])} for k,v in models.items()}
        results={}
        for arm in ('collector_baseline','native_local','conventional_full'):
            current=[]
            for i,seed in enumerate(P['validation_source_seeds']):
                ep,_=source_episode(seed,i+100,arm,models.get(arm))
                current.append(ep)
            results[arm]={'episodes':len(current),
                'actual_goals':sum(x['source_goals'] for x in current),
                'opened_doors':sum(x['door_opened'] for x in current),
                'physical_actions':sum(x['source_actions'] for x in current),
                'source_reward':round(sum(x['actual_reward_sum'] for x in current),9),
                'postdoor_decisions':sum(x['learned_postdoor_actions'] for x in current),
                'actual_original_source_episodes':current}
        result['FIT_validation']=results
    else:
        result['FIT_validation_not_consumed']=True
    result['fit_cpu_s']=round(tfit-t0,6)
    result['validation_cpu_s']=round(time.process_time()-tfit,6)
    result['peak_rss_kib']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    out=Path(sys.argv[1])
    out.write_bytes(canon(result)+b'\n')
    print('R7C34_ORIGINAL_SOURCE_FIT_GOALS='+str(observed_goals),flush=True)
    print('R7C34_FIT_CAUSAL_POSITIVE_RETURN_ROWS='+str(len(rows)),flush=True)
    print('R7C34_FIT_VALIDATION_ALLOWED='+str(qualified).upper(),flush=True)
    if qualified:
        print('R7C34_REAL_LEARNED_POSTDOOR',json.dumps({k:{i:v for i,v in val.items() if i!='actual_original_source_episodes'} for k,val in results.items()},sort_keys=True),flush=True)
if __name__=='__main__':main()
