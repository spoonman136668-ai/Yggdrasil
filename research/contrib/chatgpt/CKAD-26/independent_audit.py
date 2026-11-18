"""Independent retained-receipt fixed-share reference and CKAD26 qualification.

Imports historical independent references and source fixtures only. Never imports
native learner code or the training campaign, and never acquires training data.
"""
import argparse
import copy
from fractions import Fraction
from hashlib import sha256
import importlib.util
from itertools import product
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PREVIOUS = HERE.parent / 'CKAD-25'
INITIAL = HERE.parent / 'CKAD-24'
SOURCE = HERE.parent / 'CKAD-20' / 'synthetic_world.py'
spec = importlib.util.spec_from_file_location('ckad26_independent_previous', PREVIOUS/'independent_audit.py')
previous = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous)
canonical, sha, ratio = previous.canonical, previous.sha, previous.ratio
reference, Mixture = previous.reference, previous.Mixture
Replay = previous.previous.previous.Replay
make_episode, public_views, rollout = previous.make_episode, previous.public_views, previous.rollout
plan = previous.previous.previous.prior.prior.plan
readout_pin = previous.previous.previous.prior.prior.readout_pin
BITS = (0, 1)
RATE = Fraction(1,32)
ARMS = ('native_refresh','native_product','exact_refresh','refresh_no_alarm','product_no_alarm',
        'prior_only','pooled_replay','trailing_mle','frozen_ckad24')
MONITOR_ARMS = ('native_refresh','native_product','refresh_no_alarm','product_no_alarm','prior_only')
SCHEMA = 'yggdrasil.ckad26.retained-context-refresh.result.v1'


def require(condition, label):
    if not condition:
        raise RuntimeError('CKAD26_INDEPENDENT_'+label)


stable = previous.stable
learned_projection = previous.learned_projection
phase_world = previous.phase_world
held_mean = previous.held_mean


def prior_weights(mixture):
    count = len(mixture.models)
    if mixture.novel:
        return [Fraction(7,8*(count-1))]*(count-1)+[Fraction(1,8)]
    return [Fraction(1,count)]*count


class RefreshMixture(Mixture):
    """An exact posterior followed by fixed-share return to the context prior."""
    def __init__(self, events, *, repair=True, novel=True, rate=RATE):
        super().__init__(events, repair=repair, novel=novel)
        self.rate = Fraction(rate)

    def add(self, event):
        # Historical add scores before the adaptive member receives this event.
        super().add(event)
        self.weights = [(1-self.rate)*posterior+self.rate*prior
                        for posterior,prior in zip(self.weights,prior_weights(self),strict=True)]


def activate(monitor, rate=RATE, *, alarm=True):
    """Preserve the inherited context weights and monitor score at activation."""
    monitor.__class__ = RefreshMonitor
    monitor.rate, monitor.alarm = Fraction(rate), alarm
    monitor.refresh_start = len(monitor.events) if rate else None
    monitor.mixture.__class__ = RefreshMixture
    monitor.mixture.rate = Fraction(rate)
    return monitor


class RefreshMonitor(previous.Monitor):
    def add(self, event):
        _, (view,_), first,state,second,reward = event
        p = self.mixture.forecast(view,first)
        q = self.mixture.forecast(view,first,state,second)
        likelihood = (p if state else 1-p)*(q if reward else 1-q)
        require(likelihood > 0,'POSITIVE_LIKELIHOOD')
        self.mixture.add(event)
        self.events.append(event)
        self.score = max(Fraction(1),self.score/(4*likelihood))
        if self.alarm and self.score >= 16 and len(self.events)-self.mixture.start >= 8:
            self.detections.append({'event_id':event[0],'evidence_count':len(self.events),
                                    'score':ratio(self.score)})
            self.mixture = RefreshMixture(self.events,novel=True,rate=self.rate)
            self.score = Fraction(1)


def restore_monitor(events, rate=RATE, *, alarm=True, refresh_start=832):
    require(len(events) >= refresh_start >= 448,'MONITOR_PREFIX')
    monitor = previous.restore_monitor(events[:refresh_start])
    activate(monitor,rate,alarm=alarm)
    for event in events[refresh_start:]:
        monitor.add(event)
    return monitor


def stream_checkpoint(replay, parent, monitor):
    if getattr(monitor,'refresh_start',None) is None:
        return previous.previous.previous.stream_checkpoint(replay,parent,monitor)
    require(monitor.rate == RATE,'NATIVE_CHECKPOINT_RATE')
    material = {'projection':replay.projection,'mismatches':replay.mismatches,
                'pending_streaks':sorted(replay.pending.items()),'repairs':replay.repairs,
                'context':monitor.mixture.info(encode=True),'stream':monitor.info(hexadecimal=True),
                'refresh':{'refresh_start':monitor.refresh_start,'rate':[1,32]}}
    for target,table in replay.counts.items():
        material[f'{target}_bank_sha256'] = reference.cell_bank_sha(table)
        material[f'{target}_loss'] = [ratio(value) for value in replay.losses[target]]
    packet = {'schema':'yggdrasil.ckad.native-episode-experience.v5','repair':replay.repair,
              'episodes':replay.events,'novel':True,'context_start':monitor.mixture.start,
              'stream_start':monitor.start,'refresh_start':monitor.refresh_start,'refresh_rate':[1,32],
              'state_sha256':sha(canonical(material))}
    return canonical({**parent,'experience_ascii':canonical(packet).decode('ascii')})


def random_actions(cohort, kind, seed, index):
    digest = sha256(f'ckad26/actions-v1/{cohort}/{kind}/{seed}/{index}'.encode('ascii')).digest()
    return digest[0]&1,digest[1]&1


def evaluate(forecast, seed, count, world, held_count):
    cohort = f'ckad26-held-{count}'
    views = list(product(BITS,repeat=2))
    plans = {view:plan(forecast,view) for view in views}
    transitions = {(view,action):forecast(view,action) for view in views for action in BITS}
    terminals = {(view,*history):forecast(view,*history) for view in views for history in product(BITS,repeat=3)}
    reward = disagreements = distinct = 0
    losses = [Fraction(),Fraction()]
    for index in range(held_count):
        fixture = make_episode(cohort=cohort,seed=seed,index=index,**world)
        view,alternate = public_views(fixture)
        distinct += view != alternate
        policy = plans[view]
        reward += rollout(fixture,lambda _:policy['first_action'],
                          lambda _,first,state:policy['second_actions'][first][state])['y']
        first,second = random_actions(cohort,'held-matched',seed,index)
        row = rollout(fixture,lambda _:first,lambda *_:second)
        for target,(table,history,outcome) in enumerate(((transitions,(first,),row['s2']),
                                                       (terminals,(first,row['s2'],second),row['y']))):
            probability = table[(view,*history)]
            losses[target] += (probability-outcome)**2
            disagreements += probability != table[(alternate,*history)]
    return {'episodes':held_count,'reward_sum':reward,'transition_brier':ratio(losses[0]/held_count),
            'terminal_brier':ratio(losses[1]/held_count),'pooled_brier':ratio(sum(losses)/(2*held_count)),
            'view_disagreements':disagreements,'view_comparisons':2*held_count,'distinct_view_episodes':distinct}


def development(seeds):
    reward = {arm:held_mean(seeds,arm) for arm in ARMS}
    brier = {arm:held_mean(seeds,arm,field='pooled_brier') for arm in ARMS}
    post = {arm:held_mean(seeds,arm,(16,64,96,160)) for arm in ARMS}
    final = {arm:held_mean(seeds,arm,(192,)) for arm in ARMS}
    per_seed = {str(case['seed']):held_mean([case],'native_refresh')-held_mean([case],'native_product') for case in seeds}
    active = reward['native_refresh']
    gates = {'whole_curve_gain_vs_product':active-reward['native_product']>=Fraction(3,100),
             'whole_curve_vs_trailing_mle':active>=reward['trailing_mle'],
             'per_seed_whole_curve_no_loss':all(value>=0 for value in per_seed.values()),
             'seed101_gain_vs_product':per_seed['101']>=Fraction(1,20),
             'post16_gain_vs_frozen':post['native_refresh']-post['frozen_ckad24']>=Fraction(1,20),
             'final_returning_invariant':final['native_refresh']>=Fraction(4,5),
             'final_retention_vs_product':final['native_refresh']>=final['native_product']-Fraction(1,20),
             'final_retention_vs_frozen':final['native_refresh']>=final['frozen_ckad24']-Fraction(1,20),
             'whole_curve_brier_vs_product':brier['native_refresh']<=brier['native_product']}
    metrics = {'whole_curve_reward':{arm:ratio(value) for arm,value in reward.items()},
               'whole_curve_pooled_brier':{arm:ratio(value) for arm,value in brier.items()},
               'per_seed_reward_delta':{seed:ratio(value) for seed,value in per_seed.items()},
               'post16_reward':{arm:ratio(value) for arm,value in post.items()},
               'post16_gain_vs_frozen':ratio(post['native_refresh']-post['frozen_ckad24']),
               'final_reward':{arm:ratio(value) for arm,value in final.items()}}
    return gates,metrics


def verify_gates(result):
    gates,metrics = development(result['seeds'])
    require(result['development_gates']==gates and result['development_metrics']==metrics,'FROZEN_METRICS_GATES')
    passed = all(gates.values())
    require(result['development_pass'] is passed and result['classification']==
            ('DEVELOPMENT_GO' if passed else 'DEVELOPMENT_NO_GO'),'CLASSIFICATION')


def verify_training_source(candidate):
    require(type(candidate) is str and re.fullmatch(r'[0-9a-f]{40}',candidate),'SOURCE_COMMIT_FORMAT')
    if not (ROOT/'.git').exists():
        require(not os.environ.get('GITHUB_ACTIONS'),'CI_GIT_CUSTODY_REQUIRED')
        return False
    protocol = json.loads((HERE/'prereg.json').read_bytes())
    paths = [path.relative_to(ROOT).as_posix() for path in sorted((ROOT/'yggdrasil').glob('*.py'))]
    paths += [f'research/contrib/chatgpt/CKAD-26/{name}' for name in
              ('campaign.py','prereg.json','independent_audit.py')]
    paths += ['research/contrib/chatgpt/CKAD-20/synthetic_world.py']
    paths += [path.relative_to(ROOT).as_posix()
              for era in range(19,26) for name in ('campaign.py','independent_audit.py','prereg.json')
              if (path := HERE.parent/f'CKAD-{era}'/name).exists()]
    for relative in paths:
        try:
            frozen = subprocess.check_output(['git','show',f'{candidate}:{relative}'],cwd=ROOT)
            require(frozen==(ROOT/relative).read_bytes(),'FROZEN_TRAINING_BYTES_'+relative)
            if '/CKAD-26/' not in relative and relative not in (
                    'yggdrasil/native_episode_experience.py','yggdrasil/native_cumulative_learner.py'):
                inherited = subprocess.check_output(['git','show',f"{protocol['parent']}:{relative}"],cwd=ROOT)
                require(inherited==frozen,'PARENT_HISTORY_UNCHANGED_'+relative)
        except subprocess.CalledProcessError as exc:
            raise RuntimeError('CKAD26_INDEPENDENT_SOURCE_GIT_OBJECT') from exc
    require(subprocess.check_output(['git','show','25e83a20c973bba98d170757771777c400cf6acb:research/contrib/chatgpt/CKAD-26/prereg.json'],cwd=ROOT)
            ==(HERE/'prereg.json').read_bytes(),'FIRST_PREREG_BYTES')
    return True


def capacity_receipt(seed, ledger, pin):
    receipt = previous.capacity_receipt(seed,ledger,pin)
    identifier = sha(canonical(['ckad26-capacity-unit',seed]))
    event = ledger[-1]
    projection = learned_projection(ledger)
    row = {'s1':event[1][0][projection],'x1':event[2],'s2':event[3],'x2':event[4],'y':event[5]}
    return {**receipt,'unit_event_id':identifier,'packet_sha256':sha(canonical([identifier,event[1],row]))}


def verify_capacity(case, ledger, pin):
    require(len(ledger)==1024 and case['capacity_probe']==capacity_receipt(case['seed'],ledger,pin),'CAPACITY_PROBE')


def detection(monitor):
    return previous.detection(monitor)


def audit(root=HERE):
    start = time.monotonic()
    require(not any(name=='yggdrasil' or name.startswith('yggdrasil.') for name in sys.modules),'NATIVE_IMPORT_FENCE')
    protocol = json.loads((HERE/'prereg.json').read_bytes())
    result = json.loads((root/'campaign-result.json').read_bytes())
    source = sha(SOURCE.read_bytes())
    require(source==protocol['source_sha256']==result['source_sha256'],'SOURCE_PIN')
    require(result['schema']==SCHEMA and result['stable_sha256']==sha(canonical(stable(result))),'RESULT_HASH')
    custody = verify_training_source(result['source_candidate_sha'])
    require(result['scientific_pass'] is False and result['accepted_native'] is False and result['deployment']=='NONE','AUTHORITY')
    require([case['seed'] for case in result['seeds']]==protocol['seeds'],'SEEDS')
    budget = protocol['budgets']
    require(budget['checkpoints']==list(range(0,193,16)) and budget['refresh_rate']==[1,32]
            and budget['initial_episodes']==832 and budget['final_episodes']==1024
            and budget['post16_checkpoints']==[16,64,96,160]
            and budget['boundaries']==[48,80,144] and budget['retained_receipts_per_seed']==192,'SCHEDULE')
    require(0<=result['whole_wall_seconds']<=budget['max_wall_seconds'],'WALL_BUDGET')
    expected_parity = {'forecasts':218*48,'decisions':218*40,'mismatches':0}
    identities,rollouts,diagnostics = set(),0,[]
    for case in result['seeds']:
        seed = case['seed']
        source_seed = seed+protocol['held_source_seed_offset']
        require(case['source_seed']==source_seed,'SOURCE_SEED')
        initial_raw = (INITIAL/f'seed-{seed}-coverage-native.json').read_bytes()
        receipts_raw = (PREVIOUS/f'seed-{seed}-capacity-native.json').read_bytes()
        require(sha(initial_raw)==case['parent_checkpoint_sha256']==protocol['initial_pins'][str(seed)],'PARENT_PIN')
        require(sha(receipts_raw)==case['receipt_state_sha256']==protocol['receipt_state_pins'][str(seed)],'RECEIPT_PIN')
        parent = json.loads(initial_raw)
        packet = json.loads(parent['experience_ascii'])
        prefix = packet['episodes']
        receipts = json.loads(json.loads(receipts_raw)['experience_ascii'])['episodes']
        require(len(prefix)==832 and len(receipts)==1024 and receipts[:832]==prefix
                and packet['stream_start']==448 and canonical(parent)==initial_raw,'MATCHED_LEDGER')
        require(len({row[0] for row in receipts})==1024,'RECEIPT_IDENTITIES')
        projection = learned_projection(prefix)
        replay = previous.previous.previous.prior.prior.replay(prefix,True)
        product_monitor = previous.restore_monitor(prefix)
        require(previous.previous.previous.stream_checkpoint(replay,parent,product_monitor)==initial_raw,'PARENT_EXACT_REPLAY')
        monitors = {'native_refresh':restore_monitor(prefix),'native_product':product_monitor,
                    'refresh_no_alarm':restore_monitor(prefix,alarm=False),
                    'product_no_alarm':restore_monitor(prefix,rate=Fraction(),alarm=False),
                    'prior_only':restore_monitor(prefix,rate=Fraction(1))}
        active = monitors['native_refresh']
        frozen = copy.deepcopy(product_monitor.mixture)
        name = f'seed-{seed}-refresh-native.json'
        require(case['final_checkpoint_name']==name,'STATE_NAME')
        raw = (root/name).read_bytes()
        require(sha(raw)==case['final_checkpoint_sha256'] and len(raw)==case['final_checkpoint_bytes'],'STATE_PIN')
        final = json.loads(raw)
        experience = json.loads(final['experience_ascii'])
        require(canonical(final)==raw and {**final,'experience_ascii':parent['experience_ascii']}==parent
                and experience['episodes']==receipts and experience['schema']=='yggdrasil.ckad.native-episode-experience.v5'
                and experience['refresh_start']==832 and experience['refresh_rate']==[1,32],'RETENTION')
        reports = case['stream']
        require([row['count'] for row in reports]==budget['checkpoints'],'HELD_SCHEDULE')
        reward,midstream = 0,None
        for count in range(193):
            if count==81:
                checkpoint = stream_checkpoint(replay,parent,active)
                require(midstream is not None,'MIDSTREAM_PARENT_RECEIPT')
                midstream.update({'method':'fresh_process_actual_retained_receipt_update_then_continue',
                    'continued_count':81,'continued_event_id':active.events[-1][0],
                    'continued_sha256':sha(checkpoint),'continued_readout_sha256':readout_pin(active.mixture)})
            if count in budget['checkpoints']:
                row = reports[budget['checkpoints'].index(count)]
                world = phase_world(protocol,max(0,count-1))
                mle = reference.FullHistoryControl(replay.events,projection,mle=True)
                experts = {arm:monitor.mixture.forecast for arm,monitor in monitors.items()}
                experts.update(exact_refresh=active.mixture.forecast,pooled_replay=replay.predict,
                               trailing_mle=mle.predict,frozen_ckad24=frozen.forecast)
                require(set(row['evaluation'])==set(ARMS),'HELD_ARMS')
                for arm,forecast in experts.items():
                    require(row['evaluation'][arm]==evaluate(forecast,source_seed,count,world,96),f'HELD_{seed}_{count}_{arm}')
                    rollouts += 96
                require(row['monitors']=={arm:monitor.info() for arm,monitor in monitors.items()},'MONITOR_TRACE')
                require(row['context_starts']=={arm:monitor.mixture.start for arm,monitor in monitors.items()},'CONTEXT_TRACE')
                require(row['retained_receipt_reward']==reward,'RECEIPT_REWARD_TRACE')
                checkpoint = stream_checkpoint(replay,parent,active)
                require(row['checkpoint_sha256']==sha(checkpoint),f'CHECKPOINT_REPLAY_{seed}_{count}')
                require(row['product_checkpoint_sha256']==sha(stream_checkpoint(replay,parent,product_monitor)),f'PRODUCT_REPLAY_{seed}_{count}')
                if count==80:
                    midstream = {'count':80,'sha256':sha(checkpoint),'readout_sha256':readout_pin(active.mixture)}
            if count==192:
                break
            event = receipts[832+count]
            require(event[0] not in identities,'RECEIPT_IDENTITY')
            identities.add(event[0])
            replay.add(event)
            for monitor in monitors.values():
                monitor.add(event)
            reward += event[-1]
        require(raw==stream_checkpoint(replay,parent,active),'FULL_EXACT_STATE_REPLAY')
        require(stream_checkpoint(replay,parent,product_monitor)==receipts_raw,'PRODUCT_ORIGINAL25_EXACT')
        require(case['monitors']=={arm:monitor.info() for arm,monitor in monitors.items()},'FINAL_MONITORS')
        require(case['retained_receipt_reward']==reward,'FINAL_REWARD')
        require(case['change_detection']=={arm:detection(monitor) for arm,monitor in monitors.items()},'DETECTION_DIAGNOSTICS')
        readout = readout_pin(active.mixture)
        require(case['midstream_restore']==midstream,'MIDSTREAM_CONTINUATION_RECEIPT')
        require(case['cold']=={'sha256':sha(raw),'readout_sha256':readout}
                and case['final_context_sha256']==readout,'COLD_RECEIPT')
        require(case['parity']==expected_parity,'PARITY_COUNTS')
        verify_capacity(case,receipts,sha(raw))
        children = case['resource_accounting']['cold_children']
        require([child['count'] for child in children]==[81,192] and
                all(child['cpu_seconds']>=0 and child['wall_seconds']>=0 and child['peak_rss_bytes']>0 for child in children),'CHILD_RESOURCE_SCOPE')
        diagnostics.append({'seed':seed,'retained_receipt_reward':reward,
                            'detection':{arm:detection(monitor) for arm,monitor in monitors.items()}})
    require(len(identities)==576 and rollouts==33696,'REPLAY_SCOPE')
    scope = {'retained_unique_receipts':576,'native_replayed_admissions':1152,
             'new_training_source_episodes':0,'new_training_source_actions':0,
             'held_source_episodes':3744,'held_policy_rollouts':33696,
             'held_matched_brier_trajectories':3744,'evaluation_action_callbacks':74880,
             'held_updates':0,'original_source_actions':0,'protected_first_use':0,'capacity_unit_probes':3}
    require(result['scope']==scope,'RECORDED_SCOPE')
    require(result['parity']=={key:value*3 for key,value in expected_parity.items()},'TOTAL_PARITY')
    resources = result['resource_accounting']
    require(result['parent_cpu_seconds']>=0 and result['parent_peak_rss_bytes']>0 and
            resources['parent_cpu_seconds']==result['parent_cpu_seconds'] and
            resources['parent_peak_rss_bytes']==result['parent_peak_rss_bytes'] and
            resources['whole_process_peak_rss_bytes'] is None,'PARENT_RESOURCE_SCOPE')
    child_cpu = sum(child['cpu_seconds'] for case in result['seeds'] for child in case['resource_accounting']['cold_children'])
    require(abs(resources['measured_child_cpu_seconds']-child_cpu)<1e-7 and
            abs(resources['parent_plus_measured_child_cpu_seconds']-result['parent_cpu_seconds']-child_cpu)<1e-7,'CPU_ACCOUNTING')
    verify_gates(result)
    return {'independent_all_arm_audit':'PASS','native_imports':0,'new_primary_observations':0,
            'git_training_source_custody_checked':custody,'verified_seeds':3,'verified_checkpoints':39,
            'verified_training_episodes':576,'verified_held_policy_rollouts':rollouts,
            'full_state_bytes_replayed':True,'capacity_probes_verified':3,'product_original25_exact':True,
            'stable_sha256':result['stable_sha256'],'diagnostics':diagnostics,
            'held_summary':{arm:{'reward':ratio(held_mean(result['seeds'],arm)),
                'pooled_brier_decimal':format(float(held_mean(result['seeds'],arm,field='pooled_brier')),'.12f')} for arm in ARMS},
            'wall_seconds':time.monotonic()-start}


if __name__=='__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory',nargs='?',type=Path,default=HERE)
    arguments = parser.parse_args()
    print(json.dumps(audit(arguments.directory),sort_keys=True))
