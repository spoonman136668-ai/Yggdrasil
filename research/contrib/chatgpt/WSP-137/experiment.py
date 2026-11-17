"""WSP137 prospective equal-action-budget fixed-vs-active causal acquisition.

No read of earlier WSP136 exposed source. Reuse pinned WSP135 numeric fit,
independent symbolic and conventional CART; grammar oracle is evaluator-only.
"""
from hashlib import sha256
from importlib.util import module_from_spec,spec_from_file_location
from pathlib import Path
import time,tracemalloc,json,sys
import source as S
import policy as P
import controls as C

def _load_qualified_oracle():
    path=Path(__file__).resolve().parents[1]/'WSP-136'/'oracle.py'
    spec=spec_from_file_location('_wsp137_privileged_reference_oracle',path)
    obj=module_from_spec(spec);sys.modules[spec.name]=obj;spec.loader.exec_module(obj)
    return obj
O=_load_qualified_oracle()
POLICIES=('fixed','active')
MODELS=('numeric','symbolic','cart','privileged_oracle','no_update')
def empty():return {'correct':0,'wrong_confident':0,'abstained':0,'held':0}
def add(a,b):
    for key in a:a[key]+=b[key]
def score(outputs,truth,rows):
    z=empty()
    for s,x in rows:
        y=outputs[s]
        z['held']+=1
        if y is None:z['abstained']+=1
        elif y==truth[x]:z['correct']+=1
        else:z['wrong_confident']+=1
    return z
def num_mask(bits):
    return sum(int(y)<<x for x,y in enumerate(bits))
def run():
    start_wall=time.perf_counter();start_cpu=time.process_time()
    tracemalloc.start()
    pool=P.available_pool()
    common=P.common_held()
    original_fixed=P.fixed_schedule()
    if len(pool)!=48 or len(common)!=16 or not set(original_fixed)<=pool:
        raise AssertionError('WSP137_INVALID_FROZEN_PAIRED_HOLDOUT')
    if len(P.N.templates())!=17640 or len(C.BASE.codebooks())!=17640:
        raise AssertionError('WSP137_PINNED_GENERIC_GRAMMAR_DRIFT')
    bank=O.candidate_bank()
    if len(bank)!=7062:raise AssertionError('WSP137_PRIOR_REFERENCE_ORACLE_DRIFT')
    oracle=O.ExactOracle(bank)
    models={policy:P.DirectArm(policy) for policy in POLICIES}
    views={}
    old_known=None
    metrics={family:{p:{arm:{'common':empty(),'arm_unqueried':empty()}
              for arm in MODELS} for p in POLICIES} for family in ('known','unfamiliar','off')}
    receipts=[]
    source_oracle_membership={'known':0,'unfamiliar':0,'off':0}
    unique_actions={'known':{'fixed':0,'active':0},'unfamiliar':{'fixed':0,'active':0},'off':{'fixed':0,'active':0}}
    paired_diffs=[]
    for family,seeds in (('known',sorted(S.KNOWN)),('unfamiliar',sorted(S.UNFAMILIAR)),('off',sorted(S.OFF))):
        for seed in seeds:
            view=S.world(seed)
            views[view.law_id]=view
            truth=None
            views_by_policy={}
            source_by_policy={}
            for policy in POLICIES:
                model=models[policy]
                cust=S.Custodian(view,seed)
                conventional=C.BASE.FullyFitCART()
                version=oracle.begin() if family!='off' else None
                for iteration in range(32):
                    x=model.choose(view,pool)
                    if x in common or x not in pool:
                        raise AssertionError('WSP137_COMMON_HELD_QUERY_LEAK')
                    evidence=cust.query(view.subject(x))
                    model.observe(view,evidence,pool)
                    conventional.observe(view,evidence)
                    if version is not None:version.observe(x,evidence.effect)
                if len(cust.events)!=32:raise AssertionError('WSP137_SOURCE_CALL_COUNT')
                conventional.fit(view)
                state=model.states[view.law_id]
                symbolic=C.fit_symbolic(tuple((row[2],row[3]) for row in state['events']))
                predictions={arm:{} for arm in MODELS}
                for s,x in view.records:
                    y=model.infer(view,s)
                    independent=C.infer_symbolic(symbolic,x)
                    if y!=independent:
                        raise AssertionError('WSP137_SAME_INFORMATION_SYMBOLIC_DIFFERENCE')
                    predictions['numeric'][s]=y
                    predictions['symbolic'][s]=independent
                    predictions['cart'][s]=conventional.infer(view,s)
                    predictions['privileged_oracle'][s]=version.infer(x) if version is not None else None
                    predictions['no_update'][s]=None
                if version is not None and version.restore().snapshot()!=version.snapshot():
                    raise AssertionError('WSP137_PRIVILEGED_ORACLE_COLD_RESTORE')
                held=cust.held()
                common_rows=tuple((s,x) for s,x in held if x in common)
                if len(held)!=32 or len(common_rows)!=16:raise AssertionError('WSP137_NONPAIRED_HELD_SET')
                for arm in MODELS:
                    add(metrics[family][policy][arm]['common'],score(predictions[arm],cust.truth,common_rows))
                    add(metrics[family][policy][arm]['arm_unqueried'],score(predictions[arm],cust.truth,held))
                # Freeze the full 32 withheld response before any downstream score read.
                native=cust.score_once({s:predictions['numeric'][s] for s,x in held})
                if native!=dict(metrics_dummy:=score(predictions['numeric'],cust.truth,held),source_calls=32):
                    raise AssertionError('WSP137_SOURCE_OWNED_SCORE_DISAGREEMENT')
                views_by_policy[policy]=predictions
                source_by_policy[policy]=cust
                unique_actions[family][policy]+=len(cust.events)
                receipts.append([seed,family,policy,view.law_id,cust.receipt,
                  S.digest([[s,x,predictions['numeric'][s]] for s,x in held]),
                  S.digest([[s,x,predictions['privileged_oracle'][s]] for s,x in held])])
            # audit only after BOTH policy arms and both result maps are already frozen
            if family in ('known','unfamiliar') and num_mask(source_by_policy['fixed'].truth) not in bank:
                raise AssertionError('WSP137_TRUE_LAW_NOT_IN_FULL_REFERENCE_GRAMMAR')
            source_oracle_membership[family]+=int(num_mask(source_by_policy['fixed'].truth) in bank)
            fixed=views_by_policy['fixed']['numeric']
            active=views_by_policy['active']['numeric']
            paired_diffs.append([seed,family,[(x,fixed[view.subject(x)],active[view.subject(x)])
                                    for x in sorted(common)]])
        if family=='known':
            old_known={policy:{(law,x):models[policy].infer(v,v.subject(x))
                        for law,v in views.items() for x in range(64)}
                        for policy in POLICIES}
    for policy in POLICIES:
        current={(law,x):models[policy].infer(S.world(seed),S.world(seed).subject(x))
                 for seed in sorted(S.KNOWN)
                 for law in (S.world(seed).law_id,)
                 for x in range(64)}
        if current!=old_known[policy]:
            raise AssertionError('WSP137_INTERFERENCE_WITH_EARLIER_LAWS')
    snapshots={policy:models[policy].snapshot() for policy in POLICIES}
    cold={policy:P.DirectArm.restore(snapshots[policy],views) for policy in POLICIES}
    if any(cold[p].snapshot()!=snapshots[p] for p in POLICIES):
        raise AssertionError('WSP137_COLD_SNAPSHOT_MISMATCH')
    transfer={p:{arm:empty() for arm in ('numeric','symbolic')} for p in POLICIES}
    transfer_identical={p:0 for p in POLICIES}
    for seed in sorted(S.TRANSFER):
        v=S.world(seed)
        base=S.world(198000+seed-200000)
        c=S.Custodian(v,seed)
        for policy in POLICIES:
            model=models[policy];loaded=cold[policy]
            pred={}
            for s,x in c.held():
                y=loaded.infer(v,s)
                if y==model.infer(base,base.subject(x)):
                    transfer_identical[policy]+=1
                pred[s]=y
            add(transfer[policy]['numeric'],score(pred,c.truth,c.held()))
            add(transfer[policy]['symbolic'],score(pred,c.truth,c.held()))
            if transfer[policy]['numeric']!=transfer[policy]['symbolic']:
                raise AssertionError('WSP137_TRANSFER_NUMERIC_SYMBOLIC_DRIFT')
        c.score_once({s:cold['active'].infer(v,s) for s,x in c.held()})
    if transfer_identical!={'fixed':384,'active':384}:
        raise AssertionError('WSP137_COLD_ZERO_SOURCE_TRANSFER_MISMATCH')
    known=metrics['known']
    unknown=metrics['unfamiliar']
    neg=metrics['off']
    def value(g,p,k):return g[p]['numeric']['common'][k]
    unfamiliar_gain=value(unknown,'active','correct')-value(unknown,'fixed','correct')
    familiar_loss=value(known,'fixed','correct')-value(known,'active','correct')
    passes=(unfamiliar_gain*100>=5*192 and
            value(unknown,'active','wrong_confident')*100<=192 and
            familiar_loss*100<=5*192 and
            value(neg,'active','wrong_confident')*100<=10*128)
    # WSP137 primary common16 held values are the same world/action questions per arm.
    source_actions={p:sum(unique_actions[g][p] for g in unique_actions) for p in POLICIES}
    if source_actions!={'fixed':1024,'active':1024}:
        raise AssertionError('WSP137_SOURCE_BUDGET_NOT_MATCHED')
    peak=tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    return {
       'schema':'wsp137.public-causal-active-structure-selection-result.v1',
       'status':'DEVELOPMENT_ACTIVE_SELECTION_SUPPORTED' if passes else 'DEVELOPMENT_ACTIVE_SELECTION_NO_GO',
       'scientific_pass':False,'native_admission':False,'genuine_new_primitive_invented':False,
       'accepted_main_changed':False,'original_external_source_actions':0,
       'source_calls_by_policy':source_actions,'source_safe_total_synthetic_effects':2048,
       'model_representation':'PINNED_WSP135_17640_TWO_PAIR_LATENT_TEMPLATES',
       'source_grammar_prior_to_candidate':False,'privileged_oracle_for_scoring_only':True,
       'shared_held':sorted(common),'eligible_source_actions':len(pool),
       'common_held_per_world':16,'arm_specific_full_unqueried_per_world':32,
       'family_worlds':{'known':12,'unfamiliar':12,'off':8,'transfer':6},
       'scores':metrics,'transfer':transfer,'transfer_identical':transfer_identical,
       'source_oracle_membership':source_oracle_membership,
       'unfamiliar_active_minus_fixed_common_correct':unfamiliar_gain,
       'familiar_active_loss_common_correct':familiar_loss,
       'independent_symbolic_action_and_prediction_parity':True,
       'all_old_known_readouts_unchanged':True,'cold_restore':True,
       'source_receipts_sha256':S.digest(receipts),
       'paired_common_readouts_sha256':S.digest(paired_diffs),
       'state_sha256':{p:P.digest(snapshots[p]) for p in POLICIES},
       'resource':{'cpu_seconds':round(time.process_time()-start_cpu,3),
                   'wall_seconds':round(time.perf_counter()-start_wall,3),
                   'peak_tracemalloc_bytes':peak,
                   'energy':'UNQUALIFIED'},
       'limitations':['Public synthetic only; no original CausalGym first-use or source-owner scientific custody',
                      'Public action pool excludes and reveals the location of common evaluation queries',
                      'Policy chooses more informative data within a supplied generic latent prior, not unsupplied primitive invention',
                      'Independent equally informed symbolic baseline ties at same actions',
                      'No fully trained deep conventional baseline or matched model energy/compute qualification']
    }
if __name__=='__main__': print('WSP137_RESULT_JSON='+S.canon(run()))
