"""AAI-12X frozen source-only, disjoint-world model/efficiency evaluation."""
from __future__ import annotations
import argparse
import hashlib
import json
import time
import world
import reference_w as legacy
import optimized

ARMS=('optimized_ternary','reference_ternary_AAI12W','fixed_pair_relation_grammar',
      'fully_fitted_id3_depth7','logistic_degree2_fullbatch200',
      'hamming_knn5','persistence_no_memory')
FITTED=('fixed_pair_relation_grammar','fully_fitted_id3_depth7',
        'logistic_degree2_fullbatch200','hamming_knn5')


def load():
    t0=time.perf_counter()
    cohort=[]
    for fixture in world.FIXTURES:
        for phase,items in world.WORLDS.items():
            for wid in range(len(items)):
                rows=world.train(fixture,phase,wid)
                cases=world.evaluations(fixture,phase,wid)
                fit_states={tuple(row['x']) for row in rows}
                if len(rows)!=48 or len(cases)!=64 or any(tuple(x) in fit_states for trial in cases for x in trial['predecessor_path']):
                    raise AssertionError('AAI12X invalid source disjointness or budget')
                cohort.append((fixture,phase,wid,rows,cases))
    if len(cohort)!=72:raise AssertionError('AAI12X wrong world count')
    digest=hashlib.sha256(legacy.canonical([[f,p,i,rows,
        [[q['x0'],q['y0'],q['actions']] for q in cases]] for f,p,i,rows,cases in cohort]).encode()).hexdigest()
    return cohort,digest,time.perf_counter()-t0


def screen(cohort,source_digest,source_seconds):
    outcomes={p:{arm:[] for arm in ARMS} for p in world.WORLDS}
    per_world={i:[] for i in range(16)}
    elapsed={arm:0. for arm in ARMS}
    trace=[]; exact_programs=0; identical_forecasts=0; cold_count=0
    for fix,phase,wid,rows,cases in cohort:
        states={}; forecasts={}
        for arm in ARMS:
            t0=time.perf_counter()
            if arm=='optimized_ternary':
                model=optimized.train(rows)
            else:
                name='ternary_causal' if arm=='reference_ternary_AAI12W' else arm
                model=legacy.train(name,rows)
            snapshot=legacy.checkpoint(model)
            restored=legacy.restore(snapshot)
            if legacy.checkpoint(restored)!=snapshot:raise AssertionError('AAI12X invalid cold restore')
            cold_count+=1
            pred=tuple(legacy.forecast(restored,t['x0'],t['y0'],t['actions']) for t in cases)
            elapsed[arm]+=time.perf_counter()-t0
            states[arm]=restored;forecasts[arm]=pred
            correct=[int(y==t['truth_y3']) for y,t in zip(pred,cases)]
            outcomes[phase][arm].extend(correct)
            if arm=='optimized_ternary' and phase=='novel':per_world[wid].extend(correct)
            trace.append([fix,phase,wid,arm,correct])
        a=states['optimized_ternary']
        b=states['reference_ternary_AAI12W']
        if a!=b:raise AssertionError('AAI12X exact fitted program mismatch')
        if forecasts['optimized_ternary']!=forecasts['reference_ternary_AAI12W']:
            raise AssertionError('AAI12X exact heldout predictions mismatch')
        exact_programs+=1
        identical_forecasts+=len(cases)
    if cold_count!=72*7 or identical_forecasts!=72*64:
        raise AssertionError('AAI12X incomplete cold or parity budget')
    accuracy={phase:{a:round(sum(vals)/len(vals),9) for a,vals in by.items()} for phase,by in outcomes.items()}
    if any(len(outcomes[p][a])!=expected for p,expected in [('novel',3072),('familiar',768),('negative',768)] for a in ARMS):
        raise AssertionError('AAI12X observation budget mismatch')
    best=max(FITTED,key=lambda a:accuracy['novel'][a])
    novel=accuracy['novel']['optimized_ternary']
    novel_worlds=sum(sum(per_world[i])/len(per_world[i])>=.8 for i in range(16))
    speedup=elapsed['reference_ternary_AAI12W']/elapsed['optimized_ternary']
    fastest=min(elapsed[a] for a in FITTED)
    cost_ratio=elapsed['optimized_ternary']/fastest
    gates={
      'exact_equivalent_program_and_all_predictions':exact_programs==72 and identical_forecasts==4608,
      'novel_accuracy_at_least_0_83':novel>=.83-1e-10,
      'novel_gain_over_strongest_fitted_at_least_0_08':novel>=accuracy['novel'][best]+.08-1e-10,
      'at_least_14_of_16_novel_worlds_above_0_80':novel_worlds>=14,
      'familiar_noninferiority_within_0_04':accuracy['familiar']['optimized_ternary']>=max(accuracy['familiar'][a] for a in FITTED)-.04-1e-10,
      'negative_noninferiority_within_0_05':accuracy['negative']['optimized_ternary']>=max(accuracy['negative'][a] for a in FITTED)-.05-1e-10,
      'speedup_over_reference_at_least_2':speedup>=2,
      'cost_ratio_vs_fastest_fitted_at_most_12':cost_ratio<=12,
    }
    return {
      'schema':'yggdrasil.aai12x.source-dev.v1',
      'classification':'DEV_GO_SCIENCE_UNVERIFIED' if all(gates.values()) else 'DEV_NO_GO_NO_SCIENCE',
      'accuracy':accuracy,'best_novel_fitted_control':best,
      'novel_worlds_at_least_0_80':novel_worlds,'program_parity_worlds':exact_programs,
      'prediction_parity_cases':identical_forecasts,'cold_roundtrips':cold_count,
      'model_fit_cold_restore_forecast_seconds':{a:round(v,6) for a,v in elapsed.items()},
      'reference_speedup':round(speedup,6),'vs_fastest_fitted_cost_ratio':round(cost_ratio,6),
      'source_materialization_seconds':round(source_seconds,6),
      'source_digest_sha256':source_digest,
      'trace_sha256':hashlib.sha256(legacy.canonical(trace).encode()).hexdigest(),
      'gates':gates,'scientific_cohorts_used':0,'native_changed':False,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--source-dev',action='store_true')
    p.add_argument('--primary',action='store_true')
    args=p.parse_args()
    if args.primary:p.error('AAI12X SCIENTIFIC FIRST USE DISARMED')
    if not args.source_dev:p.error('only source-only --source-dev allowed')
    cohort,h,dt=load()
    print('AAI12X_DEV='+json.dumps(screen(cohort,h,dt),sort_keys=True),flush=True)

if __name__=='__main__':main()
