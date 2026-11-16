"""AAI-12W fixed mechanical source-only developmental evaluation."""
from __future__ import annotations
import argparse
import hashlib
import json
import time
import learner
import world

STRONG=('fully_fitted_id3_depth7','logistic_degree2_fullbatch200',
        'hamming_knn5','fixed_pair_relation_grammar')

def mean(a):return sum(a)/len(a) if a else 0.

def screen():
    assert tuple(world.WORLDS)==('novel','familiar','negative')
    observations={phase:{name:[] for name in learner.METHODS} for phase in world.WORLDS}
    by_world={name:{i:[] for i in range(12)} for name in learner.METHODS}
    times={name:0. for name in learner.METHODS}
    traces=[]; training_hash=[];cold_count=0
    for fix in world.FIXTURES:
        for phase,worlds in world.WORLDS.items():
            for wid in range(len(worlds)):
                train=world.train(fix,phase,wid)
                trials=world.evaluations(fix,phase,wid)
                public_training_states={tuple(r['x']) for r in train}
                if len(train)!=48 or len(trials)!=64:
                    raise AssertionError('source cohort drift')
                if any(tuple(x) in public_training_states for e in trials for x in e['predecessor_path']):
                    raise AssertionError('train/heldout predecessor-state collision')
                training_hash.append([fix,phase,wid,hashlib.sha256(learner.canonical(train).encode()).hexdigest()])
                for name in learner.METHODS:
                    t0=time.perf_counter()
                    trained=learner.train(name,train)
                    snapshot=learner.checkpoint(trained)
                    actor=learner.restore(snapshot)
                    if learner.checkpoint(actor)!=snapshot:raise AssertionError('cold state noncanonical')
                    cold_count+=1
                    correct=[]
                    for e in trials:
                        pred=learner.forecast(actor,e['x0'],e['y0'],e['actions'])
                        correct.append(int(pred==e['truth_y3']))
                    times[name]+=time.perf_counter()-t0
                    observations[phase][name].extend(correct)
                    if phase=='novel':by_world[name][wid].extend(correct)
                    traces.append([fix,phase,wid,name,correct])
    assert cold_count==2*20*len(learner.METHODS)
    for phase,count in [('novel',1536),('familiar',512),('negative',512)]:
        for method in learner.METHODS:
            if len(observations[phase][method])!=count:raise AssertionError('heldout budget drift')
    accuracy={phase:{name:round(mean(v),9) for name,v in bymethod.items()} for phase,bymethod in observations.items()}
    strongest=max(STRONG,key=lambda name:accuracy['novel'][name])
    candidate='ternary_causal';cand=accuracy['novel'][candidate]
    per_world=sum(mean(by_world[candidate][i])>=.8 for i in range(12))
    checks={
        'novel_gain_strongest_ge_0_08':cand>=accuracy['novel'][strongest]+.08-1e-10,
        'novel_gain_pair_grammar_ge_0_08':cand>=accuracy['novel']['fixed_pair_relation_grammar']+.08-1e-10,
        'novel_accuracy_ge_0_83':cand>=.83-1e-10,
        'novel_worlds_ge_0_80_at_least_10':per_world>=10,
        'familiar_drop_vs_strongest_le_0_04':accuracy['familiar'][candidate]>=max(accuracy['familiar'][m] for m in STRONG)-.04-1e-10,
        'negative_drop_vs_strongest_le_0_05':accuracy['negative'][candidate]>=max(accuracy['negative'][m] for m in STRONG)-.05-1e-10,
        'whole_model_cost_ratio_le_12':times[candidate]<=12*min(times[m] for m in STRONG),
    }
    return {
        'schema':'yggdrasil.aai12w.source-development.v1',
        'classification':'DEV_ADMITTED_SCIENCE_UNVERIFIED' if all(checks.values()) else 'DEV_NO_GO_NO_SCIENCE',
        'accuracy':accuracy,'strongest_novel_conventional':strongest,
        'novel_worlds_at_least_0_80':per_world,'frozen_checks':checks,
        'model_fit_restore_forecast_seconds':{k:round(v,6) for k,v in times.items()},
        'prediction_trace_sha256':hashlib.sha256(learner.canonical(traces).encode()).hexdigest(),
        'public_train_sha256':hashlib.sha256(learner.canonical(training_hash).encode()).hexdigest(),
        'cold_roundtrips':cold_count,'counts':{'novel':1536,'familiar':512,'negative':512},
        'source_only':True,'scientific_first_use_consumed':0,'native_model_changed':False
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--source-dev',action='store_true');p.add_argument('--primary',action='store_true')
    args=p.parse_args()
    if args.primary:p.error('AAI12W SCIENTIFIC FIRST USE DISARMED')
    if not args.source_dev:p.error('only the mechanical source --source-dev is registered')
    print('AAI12W_DEV='+json.dumps(screen(),sort_keys=True))

if __name__=='__main__':main()
