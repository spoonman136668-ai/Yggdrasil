"""WSP140 prospective source-safe same-action cost/equivalence study.

Source-safe evaluator. Original unchanged WSP137 DirectArm and WSP140 FastArm
receive the SAME single publicly paid effect; oracle never guides action.
"""
from hashlib import sha256
from importlib.util import module_from_spec,spec_from_file_location
from pathlib import Path
import json,sys,time,tracemalloc
import source as S
import selector as SEL

def _import(name,path):
    x=spec_from_file_location(name,Path(__file__).resolve().parents[1]/path)
    m=module_from_spec(x);sys.modules[x.name]=m;x.loader.exec_module(m);return m
C=_import('_wsp138_pinned_symbolic','WSP-137/controls.py')
O=_import('_wsp138_pinned_reference_oracle','WSP-136/oracle.py')
POOL=SEL.available_pool()
COMMON=SEL.common_held()
ARMS=('original','lazy')
FAMILIES=('known','unfamiliar','off')
def measure_call(record,phase,callback,*args):
    w=time.perf_counter_ns();c=time.process_time_ns()
    try:return callback(*args)
    finally:
        record[phase+'_wall_ns']+=time.perf_counter_ns()-w
        record[phase+'_cpu_ns']+=time.process_time_ns()-c

def clocks():
    return {name+'_'+axis+'_ns':0 for name in
             ('choose','chooser_observe','observe','readout','snapshot','restore')
             for axis in ('wall','cpu')}
def attach_meter(obj,record):
    chooser=obj['chooser']
    method=chooser.observe
    def counted(x,y):
        return measure_call(record,'chooser_observe',method,x,y)
    chooser.observe=counted

def state_bytes(chooser):
    """Python container+slot counts; no immutable source-independent bank charge.
    This is an allocated-structure estimate, not RSS or process memory.
    """
    import sys as _s
    if isinstance(chooser,SEL.BitParallelPolicy):
        return (_s.getsizeof(chooser.alive)+_s.getsizeof(chooser.events)+
                _s.getsizeof(chooser.positive)+_s.getsizeof(chooser.negative)+
                _s.getsizeof(chooser.pending))
    return (_s.getsizeof(chooser.valid)+_s.getsizeof(chooser.lut)+
            sum(_s.getsizeof(row) for row in chooser.lut))
def summary(xs):
    return {k:round(v/1_000_000_000,7) for k,v in xs.items()}

def rate(pred,truth,rows):
    z={'correct':0,'wrong_confident':0,'abstained':0,'held':0}
    for subject,x in rows:
        y=pred[subject]
        z['held']+=1
        if y is None:z['abstained']+=1
        elif y==truth[x]:z['correct']+=1
        else:z['wrong_confident']+=1
    return z
def mask(bitlist):
    return sum(int(y)<<i for i,y in enumerate(bitlist))

def run():
    starting=time.perf_counter();cpu_start=time.process_time()
    tracemalloc.start()
    if len(POOL)!=48 or len(COMMON)!=16 or set(SEL.fixed_schedule())-POOL:
        raise AssertionError('WSP140_PUBLIC_ACTION_POOL_DRIFT')
    # Explicitly prewarm source-independent immutable banks before clocks start.
    if len(SEL.N.templates())!=17640 or len(C.BASE.codebooks())!=17640:
        raise AssertionError('WSP140_PINNED_FEATURE_CLASS_DRIFT')
    if len(SEL.original_ranked())!=17640:raise AssertionError('WSP140_PINNED_ORDER_DRIFT')
    # Warm source-independent original candidate ranking for both arms.\n    # Bit-parallel mask creation remains COLD and is included in optimized first choose.\n    SEL.BASE.candidate_preference()\n    oracle_bank=O.candidate_bank()
    if len(oracle_bank)!=7062:raise AssertionError('WSP140_PRIVILEGED_REFERENCE_DRIFT')
    oracle=O.ExactOracle(oracle_bank)
    model={'original':SEL.BASE.DirectArm('active'),'lazy':SEL.FastArm('active')}
    durations={p:clocks() for p in ARMS}
    scored={fam:{'common':{'correct':0,'wrong_confident':0,'abstained':0,'held':0},
                 'full_held':{'correct':0,'wrong_confident':0,'abstained':0,'held':0}}
            for fam in FAMILIES}
    refs={fam:{'symbolic':{'correct':0,'wrong_confident':0,'abstained':0,'held':0},
               'cart':{'correct':0,'wrong_confident':0,'abstained':0,'held':0},
               'oracle':{'correct':0,'wrong_confident':0,'abstained':0,'held':0}}
          for fam in FAMILIES}
    def add(to,from_):
        for key in to:to[key]+=from_[key]
    receipts=[];per_world=[];views={}
    material_bytes={'original':0,'lazy':0}
    known_before=None
    original_source_actions=0
    for family,seeds in (('known',sorted(S.KNOWN)),('unfamiliar',sorted(S.UNFAMILIAR)),('off',sorted(S.OFF))):
        for seed in seeds:
            v=S.world(seed);views[v.law_id]=v
            cust=S.Custodian(v,seed)
            clock={'original':durations['original'],'lazy':durations['lazy']}
            for j in range(32):
                # Alternate which arm runs first per world and intervention.
                order=ARMS if (seed+j)&1==0 else ARMS[::-1]
                chosen={}
                for policy in order:
                    arm=model[policy]
                    chosen[policy]=measure_call(clock[policy],'choose',arm.choose,v,POOL)
                    if j==0:attach_meter(arm.states[v.law_id],clock[policy])
                if chosen['original']!=chosen['lazy']:
                    raise AssertionError(('WSP140_ACTION_SEQUENCE_DRIFT',family,seed,j,chosen))
                x=chosen['original']
                if x is None or x in COMMON:raise AssertionError('WSP140_UNPAID_ACTION_CHOICE')
                e=cust.query(v.subject(x))
                original_source_actions+=1
                for policy in order:
                    measure_call(clock[policy],'observe',model[policy].observe,v,e,POOL)
            if len(cust.events)!=32:raise AssertionError('WSP140_SOURCE_LEDGER_INCOMPLETE')
            st=model['original'].states[v.law_id]['chooser']
            ft=model['lazy'].states[v.law_id]['chooser']
            material_bytes['original']+=state_bytes(st)
            material_bytes['lazy']+=state_bytes(ft)
            all_pred={}
            for policy in ARMS:
                p=model[policy]
                all_pred[policy]=measure_call(durations[policy],'readout',
                    lambda: {s:p.infer(v,s) for s,x in v.records})
            if all_pred['original']!=all_pred['lazy']:
                raise AssertionError('WSP140_NUMERIC_PREDICTION_DRIFT')
            original=all_pred['original']
            rows=tuple((x,y) for law,s,x,y in model['original'].states[v.law_id]['events'])
            independent=C.fit_symbolic(rows)
            for subject,x in v.records:
                if C.infer_symbolic(independent,x)!=original[subject]:
                    raise AssertionError('WSP140_EQUAL_INFORMATION_SYMBOLIC_MISMATCH')
            conventional=C.BASE.FullyFitCART()
            for row in cust.events:
                from types import SimpleNamespace
                e=SimpleNamespace(law_id=row[0],subject=row[1],input=row[2],effect=row[3])
                conventional.observe(v,e)
            conventional.fit(v)
            ref=oracle.begin() if family!='off' else None
            if ref is not None:
                for row in cust.events:ref.observe(row[2],row[3])
                if ref.restore().snapshot()!=ref.snapshot():
                    raise AssertionError('WSP140_REFERENCE_COLD_CHECK_FAILED')
                if mask(cust.truth) not in oracle_bank:
                    raise AssertionError('WSP140_TRUE_SOURCE_NOT_IN_REFERENCE_GRAMMAR')
            held=cust.held()
            paired=tuple((s,x) for s,x in held if x in COMMON)
            if len(held)!=32 or len(paired)!=16:
                raise AssertionError('WSP140_PAIRED_HOLDOUT_MISMATCH')
            add(scored[family]['common'],rate(original,cust.truth,paired))
            add(scored[family]['full_held'],rate(original,cust.truth,held))
            for name,out in (('symbolic',{s:C.infer_symbolic(independent,x) for s,x in paired}),
                             ('cart',{s:conventional.infer(v,s) for s,x in paired}),
                             ('oracle',{s:ref.infer(x) if ref is not None else None for s,x in paired})):
                add(refs[family][name],rate(out,cust.truth,paired))
            actual=cust.score_once({s:original[s] for s,x in held})
            if {k:actual[k] for k in ('correct','wrong_confident','abstained','held')}!=rate(original,cust.truth,held):
                raise AssertionError('WSP140_SOURCE_SCORE_DISAGREEMENT')
            receipts.append([family,seed,v.law_id,cust.receipt,
                             S.digest([[s,x,original[s]] for s,x in held])])
            per_world.append([family,seed,cust.receipt,st.events,ft.events,
                              state_bytes(st),state_bytes(ft)])
        if family=='known':
            known_before={p:{(seed,x):model[p].infer(S.world(seed),S.world(seed).subject(x))
                          for seed in sorted(S.KNOWN) for x in range(64)} for p in ARMS}
    for p in ARMS:
        after={(seed,x):model[p].infer(S.world(seed),S.world(seed).subject(x))
               for seed in sorted(S.KNOWN) for x in range(64)}
        if after!=known_before[p]:raise AssertionError('WSP140_CUMULATIVE_RETENTION_DRIFT')
    snapshots={p:measure_call(durations[p],'snapshot',model[p].snapshot) for p in ARMS}
    if snapshots['original']!=snapshots['lazy']:
        raise AssertionError('WSP140_BYTE_IDENTICAL_LEARNED_STATE_FAILED')
    cold={p:measure_call(durations[p],'restore',
                        (SEL.BASE.DirectArm if p=='original' else SEL.FastArm).restore,
                        snapshots[p],views) for p in ARMS}
    if cold['original'].snapshot()!=cold['lazy'].snapshot():
        raise AssertionError('WSP140_COLD_RESTORED_BYTES_DISAGREE')
    transfer_correct=transfer_wrong=transfer_abstain=transfer_same=0
    for seed in sorted(S.TRANSFER):
        v=S.world(seed);cust=S.Custodian(v,seed)
        base=S.world(206000+seed-208000)
        transfer_outputs={}
        for subject,x in cust.held():
            old=model['original'].infer(base,base.subject(x))
            r=cold['original'].infer(v,subject)
            f=cold['lazy'].infer(v,subject)
            if r!=f or r!=old:raise AssertionError('WSP140_ZERO_CALL_TRANSFER_DRIFT')
            transfer_same+=1
            transfer_outputs[subject]=f
            if f is None:transfer_abstain+=1
            elif f==cust.truth[x]:transfer_correct+=1
            else:transfer_wrong+=1
        cust.score_once(transfer_outputs)
    if transfer_same!=384 or original_source_actions!=1024:
        raise AssertionError('WSP140_SOURCE_ACTIONS_OR_TRANSFER_BUDGET')
    global_bytes=SEL.global_cache_bytes()\n    slowdown=material_bytes['original']/max(1,material_bytes['lazy']+global_bytes)
    stats={}
    for p in ARMS:
        t=durations[p]
        stats[p]={
           'selector_wall_seconds':round((t['choose_wall_ns']+t['chooser_observe_wall_ns'])/1e9,7),
           'selector_cpu_seconds':round((t['choose_cpu_ns']+t['chooser_observe_cpu_ns'])/1e9,7),
           'full_model_wall_seconds':round(sum(t[phase+'_wall_ns'] for phase in ('choose','observe','readout','snapshot','restore'))/1e9,7),
           'full_model_cpu_seconds':round(sum(t[phase+'_cpu_ns'] for phase in ('choose','observe','readout','snapshot','restore'))/1e9,7),
           'profile_parts_seconds':summary(t)}
    ratios={name:stats['original'][name]/max(1e-9,stats['lazy'][name])
            for name in ('selector_wall_seconds','selector_cpu_seconds','full_model_wall_seconds','full_model_cpu_seconds')}
    cost_supported=(ratios['selector_wall_seconds']>=2.0 and ratios['selector_cpu_seconds']>=2.0
      and ratios['full_model_wall_seconds']>=1.25 and ratios['full_model_cpu_seconds']>=1.25
      and (material_bytes['lazy']+global_bytes)*4<=material_bytes['original'])
    peak=tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    return {
       'schema':'wsp138.prospective-lazy-sourceblind-cost-equality-result.v1',
       'status':'DEVELOPMENT_BITPARALLEL_COST_SUPPORTED_PLATFORM' if cost_supported else 'DEVELOPMENT_BITPARALLEL_COST_NO_GO_PLATFORM',
       'scientific_pass':False,'native_admission':False,'original_source_firstuse':False,
       'exact_full64_action_and_prediction_parity':True,
       'source_safe_calls':original_source_actions,
       'original_external_source_calls':0,
       'learner_algo_changed':False,
       'prior_knowledge_unchanged':True,
       'frozen_known_laws_preserved':True,
       'cold_restore_byte_identical':True,
       'zero_action_transfer_same':transfer_same,
       'zero_action_transfer_correct':transfer_correct,
       'zero_action_transfer_wrong':transfer_wrong,
       'zero_action_transfer_abstained':transfer_abstain,
       'family_worlds':{'known':12,'unfamiliar':12,'off':8,'transfer':6},
       'paired_scores':scored,'matched_controls':refs,
       'model_state_sha256':SEL.BASE.digest(snapshots['original']),
       'source_receipts_sha256':S.digest(receipts),
       'per_world_profile_receipts_sha256':S.digest(per_world),
       'policy_immutable_rank_sha256':S.digest(SEL.original_ranked()),
       'same_info_symbolic_prediction_parity':True,
       'eligible_public_actions':len(POOL),'public_paired_held_queries':len(COMMON),
       'cost':{
           'per_platform_gate_pass':cost_supported,
           'profiles':stats,
           'original_mutable_structural_bytes':material_bytes['original'],
           'lazy_mutable_structural_bytes':material_bytes['lazy'],\n           'global_mask_and_pair_cache_bytes':global_bytes,\n           'lazy_total_structural_with_global_cache_bytes':material_bytes['lazy']+global_bytes,
           'mutable_structure_ratio_old_over_new_including_global_masks':round(slowdown,6),
           'original_over_lazy_speedups':{k:round(v,6) for k,v in ratios.items()},
           'whole_trial_cpu_seconds':round(time.process_time()-cpu_start,3),
           'whole_trial_wall_seconds':round(time.perf_counter()-starting,3),
           'whole_trial_peak_tracemalloc_bytes':peak,
           'energy':'NOT_MEASURED','total_platform_charge':'UNQUALIFIED'
       },
       'limitations':['source-safe synthetic only; source oracle is reference with stronger prior',
         'no new primitive invention, no original CausalGym first-use or independent science',
         'public action availability reveals which 16 questions are excluded',
         'Python structural container estimate does not equal peak RSS or GPU/energy',
         'CPU and wall ratio values are same-process separated policy phases with a shared source, not external end-user throughput']
    }
if __name__=='__main__':print('WSP140_RESULT_JSON='+S.canon(run()))
