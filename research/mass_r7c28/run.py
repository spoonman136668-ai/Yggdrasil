"""Mass R7-C28: original-source FIT-only information-value identifiability.

Execute true Farama MiniGrid action-and-consequence forks. Never infer imagined
source outcomes, call source.unwrapped, or use known results from prior DEV.
"""
import argparse,hashlib,json,math,resource,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT))
from research.mass_r7c27 import run as c27
from research.mass_r7c25 import run as c25
from research.mass_r7c20 import run as c20
from research.native.itd02.r1.native_policy import canonical
P=json.loads((HERE/'PREREG.json').read_text())

def source_fit_forks(kind,model,roles):
    outputs=[]
    for family,seeds in roles.items():
        actual=c27.source_episodes(kind,model,family,seeds)
        assert len(actual)==len(seeds)
        outputs.extend(actual)
    return outputs

def extract(rows):
    events=[]
    for e in rows:
        for fork in e['forks']:
            data=fork['branches']
            info=data['information'];blind=data['information_blind'];sham=data['known_side_sham']
            assert info['first_source_row']==blind['first_source_row'],('SOURCE_NOT_MATCHED',e['seed'])
            assert info['first_revealed_observation']==blind['first_revealed_observation']
            assert info['first_action']==blind['first_action']
            before=fork['public_before']
            features={
                'family':e['family'],
                'turn':int(info['first_action']),
                'current_blocked':int(before['front_blocked']),
                'goal_near':int(abs(before['goal_x']-before['x'])+abs(before['goal_y']-before['y'])<=4)}
            info_r=info['reward'];blind_r=blind['reward']
            events.append({'family':e['family'],'seed':e['seed'],'fork_step':fork['fork_step'],
                'preaction_public':before,'public_context':features,
                'novel_front_blocked':info['new_obstacle_blocked'],
                'info_next_action':info['postturn_next_choice'],
                'blind_next_action':blind['postturn_next_choice'],
                'info_goal':info['success'],'blind_goal':blind['success'],
                'info_reward':info_r,'blind_reward':blind_r,'sham_reward':sham['reward'],
                'reward_effect':round(info_r-blind_r,9),
                'goal_effect':int(info['success'])-int(blind['success']),
                'route_confounded_info_minus_sham':round(info_r-sham['reward'],9),
                'changed_next_action':info['postturn_next_choice']!=blind['postturn_next_choice'],
                'same_motion_source_first_row_sha256':hashlib.sha256(canonical(info['first_source_row'])).hexdigest(),
                'factual_info_trace_sha256':info['trace_sha256'],
                'physical_blind_trace_sha256':blind['trace_sha256'],
                'native_episode_source_science_sha256':hashlib.sha256(canonical(fork)).hexdigest()})
    return events

def rowcounts(events):
    return {'actual_eligible_source_turns':len(events),
        'new_public_blocked':sum(e['novel_front_blocked']==1 for e in events),
        'new_public_clear':sum(e['novel_front_blocked']==0 for e in events),
        'blocked_next_action_changed':sum(e['novel_front_blocked']==1 and e['changed_next_action'] for e in events),
        'blocked_reward_nonzero':sum(e['novel_front_blocked']==1 and abs(e['reward_effect'])>1e-9 for e in events),
        'blocked_positive_reward_effect':sum(e['novel_front_blocked']==1 and e['reward_effect']>1e-9 for e in events),
        'blocked_goal_nonzero':sum(e['novel_front_blocked']==1 and e['goal_effect']!=0 for e in events),
        'blocked_positive_goal_effect':sum(e['novel_front_blocked']==1 and e['goal_effect']>0 for e in events),
        'all_choice_differences':sum(e['changed_next_action'] for e in events),
        'source_seeds_with_blocked':len({(e['family'],e['seed']) for e in events if e['novel_front_blocked']==1})}

def prior_key(feat):
    # Fixed rough bins, not optimized on actual outcomes.
    return (feat['family'],feat['current_blocked'],feat['goal_near'],feat['turn'])

def fit_model(events):
    # Beta(1,1) for positive source causal reward effect of using the signal
    # instead of blinding it after exactly the same physical turn.
    counts={}
    for e in events:
        key='|'.join(map(str,prior_key(e['public_context'])))
        count=counts.setdefault(key,[0,0])
        count[0]+=1;count[1]+=int(e['reward_effect']>1e-9)
    return {'schema':'mass.r7c28.bayesian-public-effect-value.v1',
            'context_counts':dict(sorted(counts.items())),
            'global_positive':sum(e['reward_effect']>1e-9 for e in events),
            'global_total':len(events),'prior_a':1,'prior_b':1,
            'threshold':0.5}

def predict(model,feat):
    key='|'.join(map(str,prior_key(feat)))
    n,k=model['context_counts'].get(key,(0,0))
    # Source-independent posterior shrinkage. No validation labels used to fit.
    return (k+1)/(n+2)

def validate(model,events):
    # True environment already executed both future branches. This is an
    # evaluation of the *one-reading use decision at each source fork*,
    # NOT self-directed multi-episode rollout for a novel learned navigator.
    rows=[]
    for e in events:
        posterior=predict(model,e['public_context'])
        choose_info=posterior>model['threshold']
        branch_reward=e['info_reward'] if choose_info else e['blind_reward']
        rows.append({'family':e['family'],'seed':e['seed'],
            'fork_step':e['fork_step'],'new_front_blocked':e['novel_front_blocked'],
            'posterior':round(posterior,6),'use_new_front_observation':choose_info,
            'actually_changed_next_action':e['changed_next_action'],
            'reward_use_policy':branch_reward,
            'reward_blind_only':e['blind_reward'],
            'reward_all_use':e['info_reward'],
            'info_minus_blind':e['reward_effect']})
    return {'forks':len(rows),'blocked_forks':sum(e['new_front_blocked'] for e in rows),
            'choose_information':sum(e['use_new_front_observation'] for e in rows),
            'total_learned_reward':round(sum(e['reward_use_policy'] for e in rows),8),
            'total_always_use_reward':round(sum(e['reward_all_use'] for e in rows),8),
            'total_never_use_reward':round(sum(e['reward_blind_only'] for e in rows),8),
            'learned_vs_blind':round(sum(e['reward_use_policy']-e['reward_blind_only'] for e in rows),8),
            'learned_vs_always_use':round(sum(e['reward_use_policy']-e['reward_all_use'] for e in rows),8),
            'per_fork_evaluated_original_action_receipts':rows}

def main():
    import gymnasium,minigrid
    ap=argparse.ArgumentParser()
    ap.add_argument('--kind',choices=('native','conventional'),required=True)
    ap.add_argument('--out',required=True)
    args=ap.parse_args()
    c20.check_source()
    assert P['original_source'].split('@')[-1]=='7f5853792ea7f04f75614661006d87fcf949f26d'
    t0=time.process_time()
    fit,fitsha,source_action_counts=c20.fit_data()
    assert len(fit)==12 and fitsha==P['frozen_twelve_actual_motor_FIT_sha256']
    model=c25.make('native_active' if args.kind=='native' else 'conventional_active',fit)
    training_episodes=source_fit_forks(args.kind,model,P['fit_training_seed_cohorts'])
    train=extract(training_episodes)
    stats=rowcounts(train)
    causal_ready=stats['new_public_blocked']>0 and stats['blocked_next_action_changed']>0 and (
       stats['blocked_reward_nonzero']>0 or stats['blocked_goal_nonzero']>0)
    if args.kind=='native' and not causal_ready:
        output={'schema':P['schema'],'kind':args.kind,'gate':'FIT_CAUSAL_INFORMATION_NOT_IDENTIFIED',
            'source_original_pin':P['original_source'],
            'prereg_sha256':hashlib.sha256((HERE/'PREREG.json').read_bytes()).hexdigest(),
            'fit_sha256':fitsha,'fit_original_action_count':source_action_counts,
            'fit_training':stats,'fit_training_forks':train,
            'fit_validation_episodes_consumed':0,'new_DEV_episodes_consumed':0,
            'cpu_fit_s':round(time.process_time()-t0,6),
            'whole_peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
        Path(args.out).write_bytes(canonical(output)+b'\n')
        print('R7C28_FIT_ONLY_BLOCKED_CAUSAL_GATE=NO_GO',args.kind,json.dumps(stats,sort_keys=True),flush=True)
        return
    model_of_value=fit_model(train)
    fit_validation_episodes=source_fit_forks(args.kind,model,P['fit_validation_seed_cohorts'])
    valid=extract(fit_validation_episodes)
    evaluation=validate(model_of_value,valid)
    output={'schema':P['schema'],'kind':args.kind,
        'gate':'FIT_CAUSAL_INFORMATION_IDENTIFIED_TRAIN_ONLY',
        'source_original_pin':P['original_source'],
        'prereg_sha256':hashlib.sha256((HERE/'PREREG.json').read_bytes()).hexdigest(),
        'fit_sha256':fitsha,'fit_original_action_count':source_action_counts,
        'fit_training':stats,'fit_training_forks':train,
        'learned_value_model':model_of_value,'fit_validation':rowcounts(valid),
        'fit_validation_results':evaluation,
        'fit_validation_original_source_forks':valid,
        'new_DEV_episodes_consumed':0,
        'cpu_fit_s':round(time.process_time()-t0,6),
        'whole_peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    Path(args.out).write_bytes(canonical(output)+b'\n')
    print('R7C28_FIT_ONLY_BLOCKED_CAUSAL_GATE=PASS',args.kind,json.dumps(stats,sort_keys=True),flush=True)
    print('R7C28_FIT_ONLY_VALUE_VALIDATION',args.kind,json.dumps({k:v for k,v in evaluation.items() if k!='per_fork_evaluated_original_action_receipts'},sort_keys=True),flush=True)
if __name__=='__main__':main()
