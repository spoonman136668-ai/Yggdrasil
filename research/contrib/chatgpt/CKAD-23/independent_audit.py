"""Replay every frozen CKAD23 arm and gate without native learner imports.

This audits retained evidence; it acquires no new primary observations.
"""
import argparse
from fractions import Fraction
from hashlib import sha256
import importlib.util
from itertools import product
import json
import os
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
PREVIOUS = Path(os.environ.get('CKAD23_PARENT_DIRECTORY', str(HERE.parent / 'CKAD-22')))
SOURCE = PREVIOUS.parent / 'CKAD-20' / 'synthetic_world.py'
sys.path.insert(0, str(SOURCE.parent))
if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)
spec = importlib.util.spec_from_file_location('ckad23_independent_ckad22', PREVIOUS / 'independent_audit.py')
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
reference = prior.reference
canonical, sha, ratio = prior.canonical, prior.sha, prior.ratio
Mixture, Replay = prior.Mixture, prior.Replay
make_episode, public_views, rollout = prior.make_episode, prior.public_views, prior.rollout
BITS = prior.BITS
ARMS = ('detector_active', 'detector_random', 'no_reset', 'periodic32',
        'pooled_replay', 'trailing_mle', 'exact_mixture', 'frozen_ckad22')


def require(condition, label):
    if not condition:
        raise RuntimeError('CKAD23_ALL_ARM_' + label)


def random_actions(cohort, kind, seed, index):
    raw = sha256(f'ckad23/actions-v1/{cohort}/{kind}/{seed}/{index}'.encode('ascii')).digest()
    return raw[0] & 1, raw[1] & 1


class Monitor:
    def __init__(self, events):
        self.start = len(events)
        self.events = list(events)
        self.mixture = Mixture(self.events, novel=True)
        self.score = Fraction(1)
        self.detections = []

    def add(self, event):
        _, (view, _), first, state, second, reward = event
        p = self.mixture.forecast(view, first)
        q = self.mixture.forecast(view, first, state, second)
        likelihood = (p if state else 1-p) * (q if reward else 1-q)
        require(likelihood > 0, 'POSITIVE_LIKELIHOOD')
        self.mixture.add(event)
        self.events.append(event)
        self.score = max(Fraction(1), self.score / (4*likelihood))
        if self.score >= 16 and len(self.events)-self.mixture.start >= 8:
            self.detections.append({'event_id': event[0], 'evidence_count': len(self.events),
                                    'score': ratio(self.score)})
            self.mixture = Mixture(self.events, novel=True)
            self.score = Fraction(1)

    def info(self, *, hexadecimal=False):
        def encode(pair):
            return [format(value, 'x') for value in pair] if hexadecimal else pair
        return {'stream_start': self.start, 'score': encode(ratio(self.score)),
                'detections': [{**entry, 'score': encode(entry['score'])}
                               for entry in self.detections]}


def stream_checkpoint(replay, parent, monitor):
    material = {'projection': replay.projection, 'mismatches': replay.mismatches,
                'pending_streaks': sorted(replay.pending.items()), 'repairs': replay.repairs,
                'context': monitor.mixture.info(encode=True),
                'stream': monitor.info(hexadecimal=True)}
    for target, table in replay.counts.items():
        material[f'{target}_bank_sha256'] = reference.cell_bank_sha(table)
        material[f'{target}_loss'] = [ratio(value) for value in replay.losses[target]]
    experience = {'schema': 'yggdrasil.ckad.native-episode-experience.v4',
                  'repair': replay.repair, 'episodes': replay.events, 'novel': True,
                  'context_start': monitor.mixture.start, 'stream_start': monitor.start,
                  'state_sha256': sha(canonical(material))}
    return canonical({**parent, 'experience_ascii': canonical(experience).decode('ascii')})


def acquire(source, fixture, seed, index, arm, monitor):
    views = public_views(fixture)
    mixture = monitor.mixture
    if arm == 'random':
        first, second = random_actions('ckad23-stream', 'probe-random', seed, index)
        row = rollout(fixture, lambda _: first, lambda *_: second)
    elif index % 4 == 3:
        plan = mixture.plan(views[0])
        row = rollout(fixture, lambda _: plan['first_action'],
                      lambda _, first, state: plan['second_actions'][first][state])
    else:
        row = rollout(fixture, lambda _: mixture.explore(views[0]),
                      lambda _, first, state: mixture.explore(views[0], first, state))
    identifier = sha(canonical(['ckad23', source, 'ckad23-stream', seed, index, arm]))
    return [identifier, [list(view) for view in views], *[row[key] for key in ('x1','s2','x2','y')]]


def evaluate(forecast, seed, count, world, held_count):
    cohort = f'ckad23-held-{count}'
    views = list(product(BITS, repeat=2))
    plans = {v: prior.prior.plan(forecast, v) for v in views}
    transitions = {(v, a): forecast(v, a) for v in views for a in BITS}
    terminals = {(v, *h): forecast(v, *h) for v in views for h in product(BITS, repeat=3)}
    reward = distinct = disagreements = 0
    losses = [Fraction(), Fraction()]
    for i in range(held_count):
        fixture = make_episode(cohort=cohort, seed=seed, index=i, **world)
        view, alternate = public_views(fixture)
        distinct += view != alternate
        plan = plans[view]
        reward += rollout(fixture, lambda _: plan['first_action'],
                          lambda _, first, state: plan['second_actions'][first][state])['y']
        first, second = random_actions(cohort, 'held-matched', seed, i)
        observed = rollout(fixture, lambda _: first, lambda *_: second)
        state, actual = observed['s2'], observed['y']
        for target, (table, history, outcome) in enumerate((
                (transitions, (first,), state), (terminals, (first,state,second), actual))):
            p = table[(view, *history)]
            losses[target] += (p-outcome)**2
            disagreements += p != table[(alternate, *history)]
    return {'episodes': held_count, 'reward_sum': reward,
            'transition_brier': ratio(losses[0]/held_count),
            'terminal_brier': ratio(losses[1]/held_count),
            'pooled_brier': ratio(sum(losses)/(2*held_count)),
            'view_disagreements': disagreements, 'view_comparisons': 2*held_count,
            'distinct_view_episodes': distinct}


def verify_gates(result):
    def mean(arm, counts=(64,112,160)):
        rows = [row['evaluation'][arm] for case in result['seeds']
                for row in case['stream'] if row['count'] in counts]
        return Fraction(sum(row['reward_sum'] for row in rows), sum(row['episodes'] for row in rows))
    active = mean('detector_active')
    no_reset, periodic, mle = (mean(arm) for arm in ('no_reset','periodic32','trailing_mle'))
    final = mean('detector_active', (192,))
    false = {str(case['seed']): sum(not any(change < row['evidence_count']-448 <= change+16
                                              for change in (48,96,144))
                                     for row in case['active_detections']) for case in result['seeds']}
    gates = {'held_gain_vs_no_reset': active-no_reset >= Fraction(1,20),
             'held_vs_periodic32': active >= periodic, 'held_vs_trailing_mle': active >= mle,
             'final_returning_invariant': final >= Fraction(4,5),
             'max_three_false_alarms': all(n <= 3 for n in false.values())}
    metrics = {'held_detector_reward': ratio(active), 'held_no_reset_reward': ratio(no_reset),
               'held_periodic32_reward': ratio(periodic), 'held_trailing_mle_reward': ratio(mle),
               'gain_vs_no_reset': ratio(active-no_reset),
               'final_returning_invariant_reward': ratio(final), 'false_alarms': false}
    require(result['development_metrics'] == metrics and result['development_gates'] == gates,
            'FROZEN_METRICS_GATES')
    passed = all(gates.values())
    require(result['development_pass'] is passed and result['classification'] ==
            ('DEVELOPMENT_GO' if passed else 'DEVELOPMENT_NO_GO'), 'CLASSIFICATION')


def audit(root):
    start = time.monotonic()
    protocol = json.loads((HERE / 'prereg.json').read_bytes())
    result = json.loads((root / 'campaign-result.json').read_bytes())
    source = sha(SOURCE.read_bytes())
    require(source == protocol['source_sha256'] == result['source_sha256'], 'SOURCE_PIN')
    require(result['schema'] == 'yggdrasil.ckad23.unsignaled-context-development.result.v1'
            and result['stable_sha256'] == sha(canonical(reference.stable(result))), 'RESULT_HASH')
    require(result['scientific_pass'] is False and result['accepted_native'] is False
            and result['deployment'] == 'NONE', 'AUTHORITY')
    require([case['seed'] for case in result['seeds']] == protocol['seeds'], 'SEEDS')
    budget = protocol['budgets']
    held_count, length = budget['held_episodes_per_checkpoint'], budget['stream_episodes_per_seed_per_acquisition_arm']
    require(length == 192 and budget['phase_episodes'] == 48
            and budget['checkpoints'] == list(range(0,193,16)), 'SCHEDULE')
    require(0 <= result['whole_wall_seconds'] <= budget['max_wall_seconds'], 'WALL_BUDGET')
    expected_parity = {'forecasts': 192*48, 'decisions': 192*40, 'mismatches': 0}
    observed_rollouts = 0
    diagnostics = []
    all_ids = set()
    for case in result['seeds']:
        seed = case['seed']
        source_seed = seed + protocol['source_seed_offset']
        require(case['source_seed'] == source_seed, 'SOURCE_SEED')
        parent_raw = (PREVIOUS / f'seed-{seed}-expanded-native.json').read_bytes()
        require(sha(parent_raw) == protocol['parent_pins'][str(seed)] == case['parent_checkpoint_sha256'], 'PARENT_PIN')
        parent = json.loads(parent_raw)
        inherited = json.loads(parent['experience_ascii'])
        prefix = inherited['episodes']
        require(len(prefix) == 448 and canonical(parent) == parent_raw, 'PARENT_ENCODING')
        require(case['final_checkpoint_name'] == f'seed-{seed}-stream-native.json', 'STATE_NAME')
        raw = (root / case['final_checkpoint_name']).read_bytes()
        require(sha(raw) == case['final_checkpoint_sha256'] and len(raw) == case['final_checkpoint_bytes'], 'STATE_PIN')
        final = json.loads(raw)
        packet = json.loads(final['experience_ascii'])
        ledger = packet['episodes']
        require({**final, 'experience_ascii':parent['experience_ascii']} == parent
                and ledger[:448] == prefix and len(ledger) == 640, 'RETENTION')
        require(len({row[0] for row in ledger}) == 640, 'UNIQUE_LEDGER')
        active, random = Monitor(prefix), Monitor(prefix)
        replay = prior.prior.replay(prefix, True)
        frozen = Mixture(prefix[:inherited['context_start']], novel=True)
        for event in prefix[inherited['context_start']:] :
            frozen.add(event)
        require(prior.checkpoint(replay, parent, frozen)[0] == parent_raw, 'PARENT_REPLAY')
        no_reset, periodic = Mixture(prefix, novel=True), Mixture(prefix, novel=True)
        reports = case['stream']
        require([row['count'] for row in reports] == budget['checkpoints'], 'HELD_SCHEDULE')
        acquisition_rewards = {'active':0, 'random':0}
        for count in range(193):
            if count in budget['checkpoints']:
                report = reports[budget['checkpoints'].index(count)]
                world = protocol['phases'][0 if count == 0 else (count-1)//48]
                mle = reference.FullHistoryControl(replay.events, replay.projection, mle=True)
                experts = {'detector_active':active.mixture.forecast, 'detector_random':random.mixture.forecast,
                           'no_reset':no_reset.forecast, 'periodic32':periodic.forecast,
                           'pooled_replay':replay.predict, 'trailing_mle':mle.predict,
                           'exact_mixture':active.mixture.forecast, 'frozen_ckad22':frozen.forecast}
                require(set(report['evaluation']) == set(ARMS), 'HELD_ARMS')
                for arm, forecast in experts.items():
                    require(report['evaluation'][arm] == evaluate(forecast, source_seed, count, world, held_count),
                            f'HELD_{seed}_{count}_{arm}')
                    observed_rollouts += held_count
                require(report['active_detections'] == active.detections
                        and report['random_detections'] == random.detections
                        and report['active_score'] == ratio(active.score)
                        and report['random_score'] == ratio(random.score)
                        and report['context_start'] == active.mixture.start, 'MONITOR_TRACE')
                require(report['checkpoint_sha256'] == sha(stream_checkpoint(replay,parent,active)),
                        f'CHECKPOINT_REPLAY_{seed}_{count}')
            if count == 192:
                break
            if count and count % 32 == 0:
                periodic = Mixture(active.events, novel=True)
            world = protocol['phases'][count//48]
            fixture = make_episode(cohort='ckad23-stream', seed=source_seed, index=count, **world)
            event = acquire(source, fixture, source_seed, count, 'active', active)
            random_event = acquire(source, fixture, source_seed, count, 'random', random)
            require(ledger[448+count] == event, f'ACTIVE_SELECTED_RECEIPT_{seed}_{count}')
            require(not ({event[0],random_event[0]} & all_ids), 'ACQUISITION_IDENTITY')
            all_ids.update((event[0],random_event[0]))
            active.add(event); random.add(random_event)
            no_reset.add(event); periodic.add(event); replay.add(event)
            acquisition_rewards['active'] += event[-1]
            acquisition_rewards['random'] += random_event[-1]
        require(raw == stream_checkpoint(replay,parent,active), 'FULL_EXACT_STATE_REPLAY')
        require(case['active_detections'] == active.detections and case['random_detections'] == random.detections,
                'FINAL_MONITORS')
        readout = prior.prior.readout_pin(active.mixture)
        require(case['final_context_sha256'] == readout and case['cold'] ==
                {'sha256':sha(raw), 'readout_sha256':readout}, 'COLD_RECEIPT')
        require(case['parity'] == expected_parity, 'PARITY_COUNTS')
        diagnostics.append({'seed':seed, 'acquired_reward_sum':acquisition_rewards,
                            'active_alarm_steps':[e['evidence_count']-448 for e in active.detections],
                            'random_alarm_steps':[e['evidence_count']-448 for e in random.detections]})
    require(result['parity'] == {key:value*3 for key,value in expected_parity.items()}, 'TOTAL_PARITY')
    require(result['scope'] == {'active_stream_episodes':576, 'random_stream_episodes':576,
            'synthetic_actions':2304, 'held_episodes':3744, 'held_updates':0,
            'original_source_actions':0, 'protected_first_use':0}, 'RECORDED_SCOPE')
    require(observed_rollouts == 29952 and len(all_ids) == 1152, 'REPLAY_SCOPE')
    verify_gates(result)
    def held_mean(arm, counts):
        rows = [row['evaluation'][arm] for case in result['seeds'] for row in case['stream']
                if row['count'] in counts]
        total = sum(row['episodes'] for row in rows)
        return {'reward':ratio(Fraction(sum(row['reward_sum'] for row in rows), total)),
                'pooled_brier_decimal':format(float(sum(Fraction(*row['pooled_brier'])*row['episodes']
                                         for row in rows)/total), '.12f')}
    for entry in diagnostics:
        for arm in ('active','random'):
            alarms = entry[f'{arm}_alarm_steps']
            entry[f'{arm}_detection'] = {
                'boundaries':[{'change':change,
                               'first_alarm':next((n for n in alarms if change < n <= change+16),None),
                               'delay':next((n-change for n in alarms if change < n <= change+16),None)}
                              for change in (48,96,144)],
                'false_alarms':[n for n in alarms if not any(c < n <= c+16 for c in (48,96,144))]}
    held_summary = {'checkpoints_64_112_160':{arm:held_mean(arm,(64,112,160)) for arm in ARMS},
                    'final_checkpoint_192':{arm:held_mean(arm,(192,)) for arm in ARMS}}
    return {'independent_all_arm_audit':'PASS','held_summary':held_summary, 'native_imports':0, 'new_primary_observations':0,
            'verified_seeds':3, 'verified_checkpoints':39, 'verified_held_policy_rollouts':observed_rollouts,
            'verified_training_episodes':len(all_ids), 'full_state_bytes_replayed':True,
            'stable_sha256':result['stable_sha256'], 'diagnostics':diagnostics,
            'wall_seconds':time.monotonic()-start}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', nargs='?', type=Path, default=HERE)
    args = parser.parse_args()
    print(json.dumps(audit(args.directory), sort_keys=True))
