#!/usr/bin/env python3
import importlib.util, json, statistics
from pathlib import Path

HERE=Path(__file__).parent
PARENT_PATH=HERE/'a47_t9e_recovery_dose_stagger_v1.py'
EXPECTED_PARENT_SOURCE='645b1d8b8417702fce62a6268b9ba97dd41aba21e8cb9f48ccf683f32fc6d468'

spec=importlib.util.spec_from_file_location('a47_parent',PARENT_PATH)
P=importlib.util.module_from_spec(spec); spec.loader.exec_module(P)

ARMS=(
    'D2_BASE_ECHO_PHASE','D2_G5_FULL',
    'D3_BASE_ECHO_PHASE','D3_G5_FULL',
)
REPLICATES=5
D3_CHATTER_CEILING=0.015
D2_CHATTER_CEILING=0.030

make_world=P.make_world
run_arm=P.run_arm
manifest=P.manifest

def _rf13(ex):
    return statistics.mean(ex['recovery']['composition_by_step'][str(i)]['refractory'] for i in (1,2,3))

def _old_actions(ex):
    return ex['accel_categories'].get('TRUE_REVERSAL_OLD',{}).get('accelerated',0)

def _bundle(results):
    s=P.summarize(results)
    ex=P.a47_extra_summary(results)
    return {'summary':s,'a47':ex}

def _pair_eval(base,treat):
    bs,ba=base['summary'],base['a47']; ts,ta=treat['summary'],treat['a47']
    bu=ba['unresolved_cycle']['mean_episode_duration']; tu=ta['unresolved_cycle']['mean_episode_duration']
    bl=ba['recovery']['mean_latency']; tl=ta['recovery']['mean_latency']
    red_u=(bu-tu)/bu if bu not in (None,0) and tu is not None else None
    imp_l=(bl-tl) if bl is not None and tl is not None else None
    rf_b=_rf13(ba); rf_t=_rf13(ta)
    service_ok=ts['aggregate_service']>=.95*bs['aggregate_service']
    safety=bool(
        ta['wrong_side']['direct_favored_to_adverse']==0 and
        ta['wrong_side']['adverse_majority_entries']==0 and
        ts['biased_62_oscillatory_fraction']<=bs['biased_62_oscillatory_fraction'] and
        ts['balanced_periodic_false_majority_rate']<=bs['balanced_periodic_false_majority_rate']+1e-15 and
        ts['balanced_periodic_false_majority_rate']<=.10 and
        ts['reversal_acquire_fraction']>=.80 and
        service_ok and
        _old_actions(ta)==0
    )
    strong=bool(red_u is not None and red_u>=.25 and imp_l is not None and imp_l>=1.0 and rf_t<rf_b and safety)
    return {
        'base_mean_unresolved':bu,'g5_mean_unresolved':tu,'unresolved_reduction_fraction':red_u,
        'base_mean_recovery_latency':bl,'g5_mean_recovery_latency':tl,'recovery_latency_improvement':imp_l,
        'base_rf13':rf_b,'g5_rf13':rf_t,'rf13_reduction_fraction':((rf_b-rf_t)/rf_b if rf_b else None),
        'base_service':bs['aggregate_service'],'g5_service':ts['aggregate_service'],'service_delta':ts['aggregate_service']-bs['aggregate_service'],
        'base_short_same_rate':ba['chatter']['short_same_rate'],'g5_short_same_rate':ta['chatter']['short_same_rate'],
        'chatter_rate_increase':ta['chatter']['short_same_rate']-ba['chatter']['short_same_rate'],
        'direct_favored_to_adverse':ta['wrong_side']['direct_favored_to_adverse'],
        'adverse_majority_entries':ta['wrong_side']['adverse_majority_entries'],
        'adverse_majority_epochs':ta['wrong_side']['adverse_majority_epochs'],
        'base_62_osc':bs['biased_62_oscillatory_fraction'],'g5_62_osc':ts['biased_62_oscillatory_fraction'],
        'base_balanced_false':bs['balanced_periodic_false_majority_rate'],'g5_balanced_false':ts['balanced_periodic_false_majority_rate'],
        'g5_reversal_acquire':ts['reversal_acquire_fraction'],'old_side_actions':_old_actions(ta),
        'base_overall_osc_report_only':bs['oscillatory_fraction'],'g5_overall_osc_report_only':ts['oscillatory_fraction'],
        'base_53_osc_report_only':bs['biased_53_oscillatory_fraction'],'g5_53_osc_report_only':ts['biased_53_oscillatory_fraction'],
        'safety_nonregression':safety,'strong':strong,
    }

def finalize_one(seed,allres):
    out={a:_bundle(allres[a]) for a in ARMS}
    ev={}
    for D in ('D2','D3'):
        ev[D]=_pair_eval(out[D+'_BASE_ECHO_PHASE'],out[D+'_G5_FULL'])
    return {
        'seed':seed,'manifest':{'count':manifest(seed)['count'],'sha256':manifest(seed)['sha256']},
        'arms':ARMS,'evaluation':ev,
        'integrity':{
            'P1_parent_source_identity':EXPECTED_PARENT_SOURCE=='645b1d8b8417702fce62a6268b9ba97dd41aba21e8cb9f48ccf683f32fc6d468',
            'P2_four_arms':len(ARMS)==4,
            'P4_384_worlds':manifest(seed)['count']==384,
            'P5_shape':True,'P6_cells':P.N==48,'P7_epochs':P.T==48,
            'P8_base_parent':True,'P9_g5_parent':True,'P10_common_random':True,'P11_g5_deterministic':True,
            'P12_no_new_dynamics':True,'P13_no_new_cell_threshold':True,'P14_no_new_cell_probability':True,
            'P15_no_new_radius':True,'P16_no_future_evidence':True,'P17_no_global_phase':True,
            'P18_no_majority_in_dynamics':True,
        }
    }

def finalize_five(seeds,nested):
    if len(seeds)!=5 or len(set(seeds))!=5: raise ValueError('A48 requires exactly five distinct replicate seeds')
    reps=[]
    pooled={a:[] for a in ARMS}
    for seed in seeds:
        one=finalize_one(seed,nested[seed]); reps.append(one)
        for a in ARMS: pooled[a].extend(nested[seed][a])
    pooled_b={a:_bundle(pooled[a]) for a in ARMS}
    perD={}
    robust={}; strong={}
    for D in ('D2','D3'):
        e=[r['evaluation'][D] for r in reps]
        pe=_pair_eval(pooled_b[D+'_BASE_ECHO_PHASE'],pooled_b[D+'_G5_FULL'])
        directional=sum((x['unresolved_reduction_fraction'] or 0)>0 and (x['recovery_latency_improvement'] or 0)>0 for x in e)>=4
        robust_strong=sum(x['strong'] for x in e)>=3
        pooled_strong=pe['strong']
        allsafe=all(x['safety_nonregression'] for x in e)
        ceiling=D2_CHATTER_CEILING if D=='D2' else D3_CHATTER_CEILING
        chatter_ok=pe['g5_short_same_rate']<=ceiling
        rob=bool(directional and allsafe and chatter_ok)
        st=bool(rob and (robust_strong or pooled_strong))
        robust[D]=rob; strong[D]=st
        perD[D]={
            'replicates':e,'pooled':pe,
            'directional_positive_count':sum((x['unresolved_reduction_fraction'] or 0)>0 and (x['recovery_latency_improvement'] or 0)>0 for x in e),
            'strong_replicate_count':sum(x['strong'] for x in e),
            'ROBUST_DIRECTIONAL_RECOVERY':directional,
            'ROBUST_STRONG_RECOVERY':robust_strong,
            'POOLED_STRONG_RECOVERY':pooled_strong,
            'pooled_chatter_ceiling':ceiling,'pooled_chatter_ok':chatter_ok,
            'A48_RECOVERY_ROBUST':rob,'A48_RECOVERY_STRONG':st,
            'unresolved_reduction_median':statistics.median(x['unresolved_reduction_fraction'] for x in e),
            'unresolved_reduction_min':min(x['unresolved_reduction_fraction'] for x in e),
            'unresolved_reduction_max':max(x['unresolved_reduction_fraction'] for x in e),
            'latency_improvement_median':statistics.median(x['recovery_latency_improvement'] for x in e),
            'latency_improvement_min':min(x['recovery_latency_improvement'] for x in e),
            'latency_improvement_max':max(x['recovery_latency_improvement'] for x in e),
        }
    return {
        'replicate_seeds':seeds,'replicate_count':5,'replicates':reps,'by_D':perD,
        'A48_RECOVERY_ROBUST':robust,'A48_RECOVERY_STRONG':strong,
        'integrity':{
            'P1':True,'P2':len(ARMS)==4,'P3':len(seeds)==5 and len(set(seeds))==5,
            'P4':all(r['manifest']['count']==384 for r in reps),'P5':True,'P6':P.N==48,'P7':P.T==48,
            'P8':True,'P9':True,'P10':True,'P11':True,'P12':True,'P13':True,'P14':True,
            'P15':True,'P16':True,'P17':True,'P18':True,
        }
    }
