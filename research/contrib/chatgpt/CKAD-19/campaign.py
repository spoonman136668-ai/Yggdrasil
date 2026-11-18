"""CKAD19: isolated frequency-matched, tokenless causal-overhypothesis trial.

No integration with native runtime or original sources. Candidate hypotheses are
preprogrammed and public. Only chosen (x, y) observations reach the learner.
"""
import argparse
import hashlib
import json
import random
import subprocess
import sys
import tempfile
import time
from pathlib import Path

FAMILIES = ((1, 2, 4), (3, 5, 6))
RULES = tuple((f, mask, shift) for f in (0, 1) for mask in FAMILIES[f] for shift in (0, 1))
SEEDS = (101, 202, 303, 404, 505, 606, 707, 808, 909, 1001)
NOISE = .02
SCHEMA = 'yggdrasil.ckad19.family-evidence-sidecar.v1'


def canonical(v):
    return json.dumps(v, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode('ascii')


def digest(v):
    return hashlib.sha256(v).hexdigest()


def oracle(rule, x):
    f, mask, sign = rule
    return (((x & 7 & mask).bit_count() & 1) ^ (x >> 3) ^ sign)


def likelihood(rule, observations):
    v = 1.
    for x, y in observations:
        v *= (1 - NOISE) if oracle(rule, x) == y else NOISE
    return v


def infer_family(tasks):
    prior = [.5, .5]
    for task in tasks:
        marginal = [sum(likelihood(r, task) for r in RULES if r[0] == f) / 6 for f in (0, 1)]
        mass = [prior[f] * marginal[f] for f in (0, 1)]
        z = sum(mass)
        if z <= 0:
            raise ValueError('CKAD19_ZERO_POSTERIOR')
        prior = [x / z for x in mass]
    return prior


def forecast(prior, observations, x):
    weights = [prior[r[0]] / 6 * likelihood(r, observations) for r in RULES]
    denominator = sum(weights)
    return sum(w * oracle(rule, x) for w, rule in zip(weights, RULES)) / denominator


def exact_control(prior, observations, x):
    """Separate conventional enumeration, intentionally equal hypothesis class."""
    num, denom = 0., 0.
    for fam in range(2):
        for mask in FAMILIES[fam]:
            for sign in range(2):
                rule = (fam, mask, sign)
                w = prior[fam] / 6
                for u, y in observations:
                    w *= (1. - NOISE if oracle(rule, u) == y else NOISE)
                denom += w
                if oracle(rule, x):
                    num += w
    return num / denom


def train_case(seed, fam, hold):
    """Distinct 4 of 5 nonheld known-family rules; family is never returned."""
    options = [r for r in RULES if r[0] == fam and r != RULES[6*fam+hold]]
    rng = random.Random(seed * 100003 + fam * 4099 + hold * 71 + 19)
    tasks = []
    for rule in rng.sample(options, 4):
        actions = rng.sample(range(16), 5)
        tasks.append([[x, oracle(rule, x)] for x in actions])
    return tasks


def encode_state(tasks):
    return canonical({'schema': SCHEMA, 'tasks': tasks, 'prior': infer_family(tasks),
                      'accepted_native': False, 'scientific_pass': False})


def restore_state(raw, expected):
    if type(raw) is not bytes or digest(raw) != expected:
        raise ValueError('CKAD19_BAD_PIN')
    try:
        d = json.loads(raw)
        if (type(d) is not dict or set(d) != {'schema', 'tasks', 'prior', 'accepted_native', 'scientific_pass'} or
                d['schema'] != SCHEMA or d['scientific_pass'] is not False or d['accepted_native'] is not False or
                canonical(d) != raw or type(d['tasks']) is not list or len(d['tasks']) != 4):
            raise ValueError('CKAD19_BAD_SCHEMA')
        for task in d['tasks']:
            if (type(task) is not list or len(task) != 5 or len({row[0] for row in task}) != 5 or
                    any(type(row) is not list or len(row) != 2 or
                        type(row[0]) is not int or not 0 <= row[0] < 16 or
                        type(row[1]) is not int or row[1] not in (0,1) for row in task)):
                raise ValueError('CKAD19_BAD_DATA')
        if (type(d['prior']) is not list or len(d['prior']) != 2 or
                any(type(x) is not float for x in d['prior']) or
                any(abs(x-y)>1e-14 for x,y in zip(d['prior'],infer_family(d['tasks'])))):
            raise ValueError('CKAD19_POSTERIOR_TAMPER')
        return d['tasks'], d['prior']
    except (TypeError, AttributeError, KeyError, ValueError, IndexError) as e:
        raise ValueError('CKAD19_CHECKPOINT_REJECTED') from e


def select(prior, obs, *, seed, random_query):
    remaining = [x for x in range(16) if x not in [a for a,_ in obs]]
    if random_query:
        rng = random.Random(seed)
        # Reconstruct the same deterministic seeded random path from the length.
        previous = list(range(16))
        seen = []
        for _ in range(len(obs) + 1):
            x = rng.choice([u for u in previous if u not in seen])
            seen.append(x)
        return seen[-1]
    return max(remaining, key=lambda x: (forecast(prior, obs, x) *
                                          (1-forecast(prior, obs, x)), -x))


def freq_forecast(tasks, obs, x):
    action = x >> 3
    rows = [row for task in tasks for row in task] + obs
    relevant = [y for u,y in rows if (u >> 3) == action]
    return (1 + sum(relevant)) / (2 + len(relevant))


def score(predict, hidden):
    brier = sum((predict(x)-oracle(hidden,x))**2 for x in range(16)) / 16
    regret = 0
    for ctx in range(8):
        q0, q1 = predict(ctx), predict(ctx|8)
        chosen = int(q1 > q0)
        regret += 1 - oracle(hidden, ctx | (chosen<<3))
    return [brier, regret/8]


def shuffled(tasks, seed):
    out=[]
    for i,task in enumerate(tasks):
        labels=[y for _,y in task]
        random.Random(seed*107+i*173+19).shuffle(labels)
        out.append([[x,labels[j]] for j,(x,_) in enumerate(task)])
    return out


def ci95(values):
    rng = random.Random(19019)
    n = len(values)
    means = []
    for _ in range(1000):
        means.append(sum(values[rng.randrange(n)] for _ in range(n))/n)
    means.sort()
    return [means[25],means[974]]


def run():
    started=time.monotonic()
    for r in RULES:
        if sum(oracle(r,x) for x in range(16)) != 8:
            raise AssertionError('CKAD19_MARGINAL_NOT_BALANCED')
    traces=[]; cold=0; checked=0; negatives=[]
    for seed in SEEDS:
        for fam in (0,1):
            for hold in range(6):
                held = RULES[6*fam+hold]
                tasks = train_case(seed,fam,hold)
                state = encode_state(tasks)
                read, posterior = restore_state(state,digest(state))
                if read != tasks:
                    raise AssertionError('CKAD19_STATE_MISMATCH')
                try:
                    restore_state(state[:-1]+b'!',digest(state))
                    raise AssertionError('CKAD19_TAMPER_ACCEPTED')
                except ValueError:
                    pass
                if cold < 2:
                    with tempfile.TemporaryDirectory() as tmp:
                        f = Path(tmp)/'state.json';f.write_bytes(state)
                        cmd=[sys.executable,'-B',str(Path(__file__).resolve()),'--cold',str(f),'--pin',digest(state)]
                        subprocess.run(cmd,check=True,capture_output=True,timeout=15)
                    cold+=1
                baseline=[.5,.5]
                s_prior=infer_family(shuffled(tasks,seed+hold*41+fam*907))
                flipped=RULES[6*(1-fam)+hold]
                negatives.append({'seed':seed,'family':fam,'held':hold,
                                  'true_family_mass':posterior[fam],
                                  'shuffled_true_family_mass':s_prior[fam],
                                  'flipped_true_family_mass':posterior[1-fam],
                                  'flipped_rule':list(flipped)})
                records={}
                for arm in ('meta_active','flat_active','meta_random'):
                    prior=baseline if arm=='flat_active' else posterior
                    obs=[]
                    scores={}
                    for t in range(5):
                        pred=lambda x,p=prior,o=obs:forecast(p,o,x)
                        scores[str(t)]=score(pred,held)
                        for x in range(16):
                            if abs(pred(x)-exact_control(prior,obs,x))>1e-12:
                                raise AssertionError('CKAD19_EXACT_BAYES_PARITY')
                            checked+=1
                        if t<4:
                            x=select(prior,obs,seed=seed*313+fam*73+hold*7,random_query=arm=='meta_random')
                            obs.append([x,oracle(held,x)])
                    records[arm]={'metrics':scores,'queries':obs}
                records['frequency_shadow']={'metrics':{}, 'queries':list(records['meta_active']['queries'])}
                for t in range(5):
                    obs=records['meta_active']['queries'][:t]
                    records['frequency_shadow']['metrics'][str(t)] = score(
                        lambda x,tasks=tasks,obs=obs:freq_forecast(tasks,obs,x),held)
                traces.append({'seed':seed,'family':fam,'held_rule_index':hold,
                               'state_sha256':digest(state),'records':records})
    arms=['meta_active','flat_active','meta_random','frequency_shadow']
    names=['brier','regret']
    means={arm:{str(t):{name:sum(row['records'][arm]['metrics'][str(t)][i]
                      for row in traces)/len(traces) for i,name in enumerate(names)}
                      for t in range(5)} for arm in arms}
    gates={
        'balanced_marginals':True,
        'exact_control':checked==len(traces)*3*5*16,
        'cold_restoration':cold==2,
        'brier_meta_vs_flat_t2': means['meta_active']['2']['brier'] <= .85*means['flat_active']['2']['brier'],
        'regret_meta_vs_flat_t2': means['flat_active']['2']['regret']>0 and means['meta_active']['2']['regret'] <= .8*means['flat_active']['2']['regret'],
        'brier_meta_vs_freq_t2': means['meta_active']['2']['brier'] <= .85*means['frequency_shadow']['2']['brier'],
        'nondegenerate_random_t2': means['meta_random']['2']['regret']>0,
        'regret_active_vs_random_t2': means['meta_random']['2']['regret']>0 and means['meta_active']['2']['regret']<=.9*means['meta_random']['2']['regret']
    }
    pair_diffs={}
    for competitor in ('flat_active','meta_random','frequency_shadow'):
        pair_diffs[competitor]={name:{str(t):{
            'mean_delta':means['meta_active'][str(t)][name]-means[competitor][str(t)][name],
            'ci95':ci95([row['records']['meta_active']['metrics'][str(t)][i]-row['records'][competitor]['metrics'][str(t)][i] for row in traces])}
            for t in (1,2,4)} for i,name in enumerate(names)}
    summary={
       'schema':'yggdrasil.ckad19.result.v1','classification':('DEVELOPMENT_BENEFIT_SUPPORTED' if all(gates.values()) else 'DEVELOPMENT_NO_GO'),
       'cases':len(traces),'seeds':list(SEEDS),'rules':len(RULES),'all_rule_marginals':8,
       'training_tasks_per_case':4,'train_queries_per_task':5,'test_queries_per_arm':4,
       'matched_training_data':True,'held_rule_training_overlap':0,
       'checkpoint_cold_restores':cold,'exact_control_predictions_verified':checked,
       'arms':means,'gates':gates,'paired_deltas':pair_diffs,
       'negative':{k:sum(n[k] for n in negatives)/len(negatives) for k in ('true_family_mass','shuffled_true_family_mass','flipped_true_family_mass')},
       'traces':traces,'negative_traces':negatives,'scientific_pass':False,'accepted_native':False,'deployment':'NONE',
       'new_original_source_actions':0,'paid_apis':0}
    summary['stable_sha256']=digest(canonical(summary))
    summary['whole_wall_seconds']=time.monotonic()-started
    if summary['whole_wall_seconds']>120:
        raise RuntimeError('CKAD19_WALL_BUDGET')
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--cold',type=Path)
    parser.add_argument('--pin')
    parser.add_argument('--output-directory',type=Path)
    args=parser.parse_args()
    if args.cold:
        assert len(restore_state(args.cold.read_bytes(),args.pin)[1])==2
        print('CKAD19_COLD_PASS')
    else:
        if args.output_directory is None:parser.error('--output-directory required')
        args.output_directory.mkdir(parents=True,exist_ok=True)
        result=run()
        (args.output_directory/'result.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
        print(json.dumps({k:result[k] for k in ('classification','cases','arms','gates','negative','stable_sha256','whole_wall_seconds')},sort_keys=True))
