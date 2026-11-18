"""YNCA-10: bounded tokenless operator-memory induction from consequences.

No Yggdrasil native learner modified. 3-bit Boolean operator is absent from
known library, generated privately by the synthetic task source; trained memory
is inferred only from noisy intervention outcomes. Inference sees no true table.
"""
import argparse
import hashlib
import itertools
import json
import math
import random

PERMS=tuple(itertools.permutations(range(3)))
TABLES=tuple(range(256))
NOISE=.10
N_TRAIN=48
OBS_TRAIN=5
OBS_TEST=3
TOP_K=8
SPLITS={'A':(610001,610049,620001,620065,51001),
        'B':(710001,710049,720001,720129,52001)}


def rng(*tokens):
    s=":".join(map(str,tokens)).encode()
    return random.Random(int.from_bytes(hashlib.sha256(s).digest()[:16],"big"))


def bit(table, action):
    return (table >> action) & 1


def perm_action(action,perm):
    return sum(((action >> perm[i]) & 1)<<i for i in range(3))


def known_operators():
    fns=[lambda x,y,z: x&y&z,
         lambda x,y,z: x|y|z,
         lambda x,y,z: x^y^z,
         lambda x,y,z: int(x+y+z>=2),
         lambda x,y,z: int(x+y+z==1),
         lambda x,y,z: y if x else z,
         lambda x,y,z: x&y,
         lambda x,y,z: x|y,
         lambda x,y,z: x^y,
         lambda x,y,z: x]
    lib=set()
    for fn in fns:
        for p in PERMS:
            table=sum(fn(*[((a>>p[i])&1) for i in range(3)])<<a for a in range(8))
            lib.add(table)
            lib.add(table^255)
    return tuple(sorted(lib))

KNOWN=known_operators()
NOVEL=tuple(t for t in TABLES if t not in KNOWN)


def hidden_table(split):
    return rng('hidden-operator',split,SPLITS[split][-1]).choice(NOVEL)


def generate_worlds(split,train=True):
    begin,end= (SPLITS[split][:2] if train else SPLITS[split][2:4])
    table=hidden_table(split)
    count=OBS_TRAIN if train else OBS_TEST
    for seed in range(begin,end):
        r=rng('world',split,'train' if train else 'test',seed)
        permutation=r.choice(PERMS)
        actions=r.sample(range(8),count)
        obs=[]
        for action in actions:
            true=bit(table,perm_action(action,permutation))
            observed=true ^ int(r.random()<NOISE)
            obs.append((action,observed))
        yield {'observations':tuple(obs),'permutation':permutation,'seed':seed}


def logsumexp(xs):
    m=max(xs)
    return m+math.log(math.fsum(math.exp(x-m) for x in xs))


def loglik(table,perm,obs):
    return sum(math.log(1-NOISE if bit(table,perm_action(a,perm))==y else NOISE)
               for a,y in obs)


def train_posterior(split, population=TABLES):
    worlds=tuple(generate_worlds(split,True))
    scores=[]
    for table in population:
        likelihood=0.
        for w in worlds:
            likelihood+=logsumexp([loglik(table,p,w['observations']) for p in PERMS])-math.log(len(PERMS))
        scores.append(likelihood)
    normalizer=logsumexp(scores)
    return {t: math.exp(v-normalizer) for t,v in zip(population,scores)}


def compress(posterior,k=TOP_K):
    top=sorted(posterior,key=lambda t:(-posterior[t],t))[:k]
    z=sum(posterior[t] for t in top)
    return {t:posterior[t]/z for t in top}


def predict(prior,obs):
    # Exact permutation-marginalized posterior for the provided table prior.
    pairs=[]
    for t,weight in prior.items():
        if weight<=0: continue
        for p in PERMS:
            pairs.append((math.log(weight/len(PERMS))+loglik(t,p,obs),t,p))
    z=logsumexp([a for a,_,_ in pairs])
    prediction=[0.]*8
    for logw,t,p in pairs:
        w=math.exp(logw-z)
        for a in range(8):
            prediction[a]+=w*bit(t,perm_action(a,p))
    return tuple(prediction)


def empirical_table_prior(split):
    # Fully fitted conventional observed-action frequency baseline.
    successes=[1.]*8
    trials=[2.]*8
    for w in generate_worlds(split,True):
        for a,y in w['observations']:
            trials[a]+=1
            successes[a]+=y
    return tuple(successes[a]/trials[a] for a in range(8))


def local_frequency_predict(fitted,obs):
    successes=[fitted[a]*2 for a in range(8)]
    trials=[2.]*8
    for a,y in obs:
        successes[a]+=y
        trials[a]+=1
    return tuple(successes[a]/trials[a] for a in range(8))


def eval_split(split):
    true=hidden_table(split)
    posterior=train_posterior(split)
    exact_generator_prior=train_posterior(split,NOVEL)
    compact=compress(posterior)
    independent={t:1/256 for t in TABLES}
    known={t:1/len(KNOWN) for t in KNOWN}
    oracle={true:1.}
    histogram=empirical_table_prior(split)
    # The compact trained memory is a serialized state, *not* an oracle table.
    frozen_memory=json.dumps({'type':'operator_memory','k':TOP_K,'weights':{str(t):v for t,v in compact.items()}},sort_keys=True)
    restored=json.loads(frozen_memory)
    recovered={int(t):v for t,v in restored['weights'].items()}
    assert recovered==compact
    methods=('UNTRAINED_EXACT','KNOWN_LIBRARY','FITTED_FREQUENCY','EXACT_HIERARCHICAL_BAYES','EXACT_GENERATOR_BAYES','COMPACT_LEARNED','PRIVILEGED_ORACLE')
    errors={m:[] for m in methods}
    accuracies={m:[] for m in methods}
    for w in generate_worlds(split,False):
        obs=w['observations']
        seen={a for a,_ in obs}
        goal=tuple(bit(true,perm_action(a,w['permutation'])) for a in range(8))
        predictions={
            'UNTRAINED_EXACT':predict(independent,obs),
            'KNOWN_LIBRARY':predict(known,obs),
            'FITTED_FREQUENCY':local_frequency_predict(histogram,obs),
            'EXACT_HIERARCHICAL_BAYES':predict(posterior,obs),
            'EXACT_GENERATOR_BAYES':predict(exact_generator_prior,obs),
            'COMPACT_LEARNED':predict(recovered,obs),
            'PRIVILEGED_ORACLE':predict(oracle,obs),
        }
        for m in methods:
            # Score on entirely UNOBSERVED intervention assignments only.
            unseen=[a for a in range(8) if a not in seen]
            errors[m].extend((predictions[m][a]-goal[a])**2 for a in unseen)
            accuracies[m].extend(int((predictions[m][a]>=.5)==goal[a]) for a in unseen)
    metrics={m:{'brier':round(math.fsum(errors[m])/len(errors[m]),8),
                'accuracy':round(math.fsum(accuracies[m])/len(accuracies[m]),8)} for m in methods}
    # A is only a diagnostic of independent learning. B's frozen correction
    # is cross-world compressed operator memory; never inspect B to tune it.
    exact=min(metrics['EXACT_HIERARCHICAL_BAYES']['brier'],metrics['EXACT_GENERATOR_BAYES']['brier'])
    base=metrics['UNTRAINED_EXACT']['brier']
    candidate=metrics['COMPACT_LEARNED']['brier']
    rel=(base-candidate)/base if base else 0
    ratio=candidate/exact if exact else float('inf')
    strongest_exact_accuracy=max(metrics['EXACT_HIERARCHICAL_BAYES']['accuracy'],metrics['EXACT_GENERATOR_BAYES']['accuracy'])
    conditional_pass=(rel>=.15 and ratio<=1.10 and
                      metrics['COMPACT_LEARNED']['accuracy'] >= strongest_exact_accuracy-.02)
    # The 256-vs-8 reduction is only in test-time operator enumeration,
    # *not* an end-to-end wallclock/energy claim (training enumerates all 256).
    trained_orbit={sum(bit(true,perm_action(a,p))<<a for a in range(8)) for p in PERMS}
    return {'split':split,'worlds_train':N_TRAIN,'worlds_test':SPLITS[split][3]-SPLITS[split][2],
            'interventions_per_train_world':OBS_TRAIN,'interventions_per_test_world':OBS_TEST,
            'unobserved_actions_per_test_world':8-OBS_TEST,
            'operator_class':'unlisted operator sampled outside pre-specified known-library family',
            'operator_table_count':len(TABLES),'known_library_count':len(KNOWN),'novel_table_count':len(NOVEL),
            'trained_operator_orbit_mass':round(math.fsum(posterior[t] for t in trained_orbit),8),
            'compressed_orbit_mass':round(math.fsum(compact.get(t,0) for t in trained_orbit),8),
            'compressed_memory_entries':len(compact),'full_bayes_entries':len(posterior),
            'test_inference_table_evaluations_reduction':len(posterior)/len(compact),
            'estimated_likelihood_factor_reduction_end_to_end':round((len(posterior)*N_TRAIN*OBS_TRAIN+len(posterior)*(SPLITS[split][3]-SPLITS[split][2])*OBS_TEST)/(len(posterior)*N_TRAIN*OBS_TRAIN+len(compact)*(SPLITS[split][3]-SPLITS[split][2])*OBS_TEST),8),
            'cold_serialization_prediction_parity':recovered==compact,
            'metrics':metrics,'relative_brier_improvement_vs_untrained':round(rel,8),
            'brier_ratio_vs_exact_trained_bayes':round(ratio,8),
            'decision':'DEVELOPMENT_SIGNAL' if conditional_pass else 'DEVELOPMENT_MIXED_OR_NO_GO',
            'claims':{'native_yggdrasil_trained':False,'scientific_pass':False,'deployed':False}}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--split',choices=('A','B'),required=True)
    args=parser.parse_args()
    print(json.dumps(eval_split(args.split),indent=2,sort_keys=True))

if __name__=='__main__':main()
