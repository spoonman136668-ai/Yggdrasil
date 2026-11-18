"""Single preregistered YNCA-12 Pass-B novelty correction. NOT native Yggdrasil."""
import argparse
import hashlib
import json
import math
import sys
import time
import tracemalloc
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import experiment as base

B_SEED=181200
B_WORLDS=64


def pair_evidence(items, comps):
    ll,_=comps
    lookup={t:i for i,t in enumerate(base.CANDIDATES)}
    return math.fsum(w*(ll[lookup[a]]+ll[lookup[b]])*.5 for (a,b),w in items)


def gate(items, comps):
    known=base.predict_pair(items,comps)
    unknown=base.no_memory(comps)
    known_likelihood=pair_evidence(items,comps)
    unknown_likelihood=math.fsum(comps[0])/len(base.CANDIDATES)
    trust=known_likelihood/(known_likelihood+unknown_likelihood)
    return tuple(trust*p+(1-trust)*q for p,q in zip(known,unknown))


def score(kind, models):
    methods=('GATED_TOP6_PAIR','GATED_FULL_PAIR','UNGATED_TOP6','UNGATED_FULL_PAIR',
             'SINGLE_BAYES','FREQUENCY','NO_MEMORY')
    errs={k:[] for k in methods};hits={k:[] for k in methods}
    restored=models['restored']
    for i in range(B_WORLDS):
        obs,truth=base.new_world(kind,i+10000)
        comp=base.test_components(obs)
        full=tuple(base.pair_items(models['pair_full']))
        preds={
            'GATED_TOP6_PAIR':gate(restored,comp),
            'GATED_FULL_PAIR':gate(full,comp),
            'UNGATED_TOP6':base.predict_pair(restored,comp),
            'UNGATED_FULL_PAIR':base.predict_pair(full,comp),
            'SINGLE_BAYES':base.predict_single(models['single'],comp),
            'FREQUENCY':base.predict_frequency(models['frequency'],obs),
            'NO_MEMORY':base.no_memory(comp),
        }
        for x in sorted(set(base.ACTIONS)-{x for x,_ in obs}):
            for name,pred in preds.items():
                errs[name].append((pred[x]-truth[x])**2)
                hits[name].append(int((pred[x]>=.5)==truth[x]))
    return {name:{'brier':round(math.fsum(errs[name])/len(errs[name]),9),
                  'accuracy':round(math.fsum(hits[name])/len(hits[name]),9)} for name in methods}


def evaluate():
    start=time.perf_counter();cpu_start=time.process_time();tracemalloc.start()
    base.A_SEED=B_SEED
    assert len(base.PAIRS)==300 and base.TRAIN_WORLDS==32
    history=[base.new_world('train',i)[0] for i in range(base.TRAIN_WORLDS)]
    models=base.learn(history)
    serialized=json.dumps(models['top6'],sort_keys=True,separators=(',',':'))
    restored=tuple(((int(a),int(b)),float(w)) for (a,b),w in json.loads(serialized))
    models['restored']=restored
    probe=base.test_components(base.new_world('familiar',9999)[0])
    maxerr=max(abs(a-b) for a,b in zip(gate(models['top6'],probe),gate(restored,probe)))
    fam=score('familiar',models)
    novel=score('novel',models)
    combined={name:round((fam[name]['brier']+novel[name]['brier'])/2,9) for name in fam}
    nonpair=('SINGLE_BAYES','FREQUENCY','NO_MEMORY')
    best_fam=min(fam[name]['brier'] for name in nonpair)
    best_combined=min(combined[name] for name in nonpair)
    current=fam['GATED_TOP6_PAIR'];full=fam['GATED_FULL_PAIR']
    gates={
       'familiar_gain_vs_nonpair':best_fam-current['brier']>=.02,
       'familiar_within_1_15x_gated_full':current['brier']<=full['brier']*1.15,
       'familiar_accuracy_loss_le_2pp':full['accuracy']-current['accuracy']<=.02,
       'novel_harm_le_0_02':novel['GATED_TOP6_PAIR']['brier']-novel['NO_MEMORY']['brier']<=.02,
       'combined_gain_vs_nonpair':best_combined-combined['GATED_TOP6_PAIR']>=.02,
       'cold_parity_le_1e12':maxerr<=1e-12,
    }
    peak=tracemalloc.get_traced_memory()[1];tracemalloc.stop()
    return {'schema':'ynca12.passB.novelty-gate.v1','status':'FROZEN_DEVELOPMENT_B',
        'seed':B_SEED,'training_worlds':base.TRAIN_WORLDS,'revealed_training_pairs':128,
        'test_worlds_per_family':B_WORLDS,'held_assignments_per_family':384,
        'memory_pairs':len(restored),'memory_sha256':hashlib.sha256(serialized.encode()).hexdigest(),
        'cold_prediction_max_abs_error':maxerr,
        'familiar':fam,'novel':novel,'combined_brier':combined,'gates':gates,'development_go':all(gates.values()),
        'resource':{'wall_seconds':round(time.perf_counter()-start,6),'cpu_seconds':round(time.process_time()-cpu_start,6),
                    'tracemalloc_peak_bytes':peak},
        'claims':{'native_trained':False,'scientific_pass':False,'deployed':False,'original_science_first_use':False}}


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--split',choices=('B',),required=True)
    p.parse_args()
    print(json.dumps(evaluate(),sort_keys=True,indent=2))
