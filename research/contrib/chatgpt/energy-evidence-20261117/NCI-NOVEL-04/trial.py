"""Frozen source-free operator induction: one-world fit, validated controls, held scores."""
from __future__ import annotations
import json
from time import perf_counter,process_time
import argparse
from collections import defaultdict
from learner import ResearchArm,digest,canonical
import world

ARMS=('MAP','BMA','NOX3','FULL','BACKOFF')
STRONG=('BMA','FULL','BACKOFF')

def predict_reward(model,ids,x,a1):
    p=model.forecast(ids,'t',(*x,a1))
    def second(state):
        return max(model.forecast(ids,'y',(*x,state,a2)) for a2 in (0,1))
    return (1-p)*second(0)+p*second(1)

def act(model,ids,x,seed,family,index):
    a1=max((0,1),key=lambda a:(predict_reward(model,ids,x,a),-a))
    return a1

def one_episode(model,seed,family,phase,index,policy='balanced',update=False):
    ids=world.ids(phase)
    x=world.inputs(seed,family,phase,index)
    a1=world.balanced(seed,family,phase,index,'t') if policy=='balanced' else act(model,ids,x,seed,family,index)
    xt=(*x,a1)
    p_t=model.forecast(ids,'t',xt)
    s2=world.reveal(seed,family,phase,index,'t',x,a1)
    a2=(world.balanced(seed,family,phase,index,'y') if policy=='balanced'
        else max((0,1),key=lambda a:(model.forecast(ids,'y',(*x,s2,a)),-a)))
    xy=(*x,s2,a2)
    p_y=model.forecast(ids,'y',xy)
    y=world.reveal(seed,family,phase,index,'y',x,a1,s2,a2)
    if update:
        model.admit(ids,'t',xt,s2,world.witness(seed,family,phase,index,'t'))
        model.admit(ids,'y',xy,y,world.witness(seed,family,phase,index,'y'))
    return {'brier':((p_t-s2)**2+(p_y-y)**2)/2,
            'reward':y,'t_prob':p_t,'y_prob':p_y,'a1':a1,'a2':a2}

def mean(data):
    return sum(data)/len(data) if data else None

def single(seed,family):
    models={k:ResearchArm(k) for k in ARMS}
    for phase in ('old_fit','new_fit'):
        for ix in range(world.COUNTS[phase]):
            for m in models.values():one_episode(m,seed,family,phase,ix,update=True)
    old_hash={k:m.old_digest(world.OLD_IDS) for k,m in models.items()}
    validations={k:mean([one_episode(m,seed,family,'valid',i)['brier']
                         for i in range(world.COUNTS['valid'])]) for k,m in models.items()}
    best=min(STRONG,key=lambda k:(validations[k],STRONG.index(k)))
    held={k:mean([one_episode(m,seed,family,'held_shared',i)['brier']
                  for i in range(world.COUNTS['held_shared'])]) for k,m in models.items()}
    policy={k:mean([one_episode(m,seed,family,'held_policy',i,'learned')['reward']
                    for i in range(world.COUNTS['held_policy'])]) for k,m in models.items() if k in ('MAP',best,'BMA','FULL')}
    old_return={k:mean([one_episode(m,seed,family,'return_old',i)['brier']
                        for i in range(world.COUNTS['return_old'])]) for k,m in models.items()}
    restored={}
    old_stable={}
    max_checkpoint=0
    for k,m in models.items():
        raw=m.checkpoint();max_checkpoint=max(max_checkpoint,len(raw))
        again=ResearchArm.restore(raw,digest(raw))
        restored[k]=again.checkpoint()==raw
        old_stable[k]=again.old_digest(world.OLD_IDS)==old_hash[k]
    evidence={s:models['MAP'].evidence(world.NEW_IDS,s) for s in ('t','y')}
    return {'seed':seed,'family':family,'valid':validations,'selected_control':best,
            'held':held,'policy':policy,'old_return':old_return,'old_stable':old_stable,
            'cold_exact':restored,'candidate_evidence':evidence,'max_checkpoint_bytes':max_checkpoint,
            'train_events_per_arm':2*(world.COUNTS['old_fit']+world.COUNTS['new_fit']),
            'total_actions_per_arm':2*sum(world.COUNTS.values())}

def summary(worlds):
    novels=[z for z in worlds if z['family'] in world.FAMILIES[:4]]
    kinds=world.FAMILIES
    family=[]
    for f in kinds:
        subs=[w for w in worlds if w['family']==f]
        if not subs:continue
        candidate=mean([w['held']['MAP'] for w in subs]);selected=mean([w['held'][w['selected_control']] for w in subs]);no4=mean([w['held']['NOX3'] for w in subs]);
        reward=mean([w['policy']['MAP'] for w in subs]);rewardcontrol=mean([w['policy'][w['selected_control']] for w in subs]);
        family.append({'family':f,'map_brier':candidate,'selected_brier':selected,'no_x3_brier':no4,
                       'bma_brier':mean([w['held']['BMA'] for w in subs]),
                       'full_brier':mean([w['held']['FULL'] for w in subs]),
                       'map_policy_reward':reward,'selected_policy_reward':rewardcontrol,
                       'identified_worlds':sum(z['candidate_evidence']['t']['identified'] and z['candidate_evidence']['y']['identified'] for z in subs),
                       'representation_10pct':candidate<=.9*no4,
                       'superiority_5pct':candidate<=.95*selected and reward-rewardcontrol>=.01})
    negative=[w for w in worlds if w['family'] in world.FAMILIES[4:]]
    negatives={'unknown_in_unidentifiable':sum(not w['candidate_evidence']['t']['identified'] and not w['candidate_evidence']['y']['identified'] for w in worlds if w['family']=='unidentifiable_fourth'),
               'unknown_out_of_degree':sum(not w['candidate_evidence']['t']['identified'] and not w['candidate_evidence']['y']['identified'] for w in worlds if w['family']=='out_of_degree_four'),
               'unknown_unchanged':sum(not w['candidate_evidence']['t']['identified'] and not w['candidate_evidence']['y']['identified'] for w in worlds if w['family']=='unchanged')}
    return {'families':family,'novel_representation_gates':sum(w['representation_10pct'] for w in family[:4]),
            'novel_superiority_gates':sum(w['superiority_5pct'] for w in family[:4]),
            'negatives':negatives,
            'old_bank_stable':all(all(w['old_stable'].values()) for w in worlds),
            'cold_checkpoint_exact':all(all(w['cold_exact'].values()) for w in worlds),
            'max_checkpoint_bytes':max(w['max_checkpoint_bytes'] for w in worlds),
            'held_mean_map':mean([w['held']['MAP'] for w in novels]),
            'held_mean_valid_selected_control':mean([w['held'][w['selected_control']] for w in novels]),
            'total_worlds':len(worlds)}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--pilot',action='store_true')
    parser.add_argument('--primary',action='store_true')
    parser.add_argument('--output',required=True)
    args=parser.parse_args()
    if args.pilot==args.primary:raise ValueError('PILOT_OR_PRIMARY_REQUIRED')
    seeds=(world.PILOT,) if args.pilot else world.SEEDS
    fams=world.FAMILIES[:2] if args.pilot else world.FAMILIES
    start=perf_counter();cpu=process_time()
    worlds=[single(seed,f) for seed in seeds for f in fams]
    result={'schema':'nci-novel04.source-free-result.v1','mode':'PILOT' if args.pilot else 'PRIMARY_ONCE',
            'seeds':list(seeds),'families':list(fams),'worlds':worlds,
            'summary':summary(worlds),
            'cpu_seconds':process_time()-cpu,'wall_seconds':perf_counter()-start,
            'source_kind':'SELF_AUTHORED_SYNTHETIC_DEV','native_accepted':False,'scientific_pass':False}
    raw=canonical(result)
    with open(args.output,'wb') as f:f.write(raw+b'\n')
    print(json.dumps({'mode':result['mode'],'source_worlds':len(worlds),
                      'summary':result['summary'],'CPU':result['cpu_seconds'],
                      'wall':result['wall_seconds'],'sha256':digest(raw+b'\n')},sort_keys=True))

if __name__=='__main__':main()
