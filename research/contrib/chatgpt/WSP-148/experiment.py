"""WSP148: frozen query-blind, source-feedback-conditioned causal acquisition.

The original source owner remains the only truth reader and post-seal evaluator.
Candidate and conventional learners receive exactly their arm's 32 paid public
action/consequence pairs and return 64 predictions before any held x is chosen.
"""
from importlib.util import module_from_spec,spec_from_file_location
from pathlib import Path
from types import SimpleNamespace
from time import perf_counter_ns,process_time_ns
import sys,tracemalloc

import source as S
import repair as W
from hashlib import sha256

ROOT=Path(__file__).resolve().parents[1]
def load(name,path):
    sp=spec_from_file_location(name,ROOT/path)
    m=module_from_spec(sp);sys.modules[sp.name]=m;sp.loader.exec_module(m)
    return m
Z=load('_wsp148_poly','WSP-147/poly_control.py')
OLD=load('_wsp148_single16','WSP-147/direct.py')
P=load('_wsp148_original_wsp145_selector','WSP-145/selector.py')
H=P.H
F=load('_wsp148_independent_exact_symbolic','WSP-143/flat_control.py')
D=load('_wsp148_pinned_three_term_direct','WSP-142/direct_weights.py')
N=load('_wsp148_pinned_native_style_latent','WSP-135/learner.py')
C=load('_wsp148_pinned_fully_fitted_cart','WSP-135/controls.py')

POLICIES=('fixed','random','adaptive')
METHODS=('hierarchical','equal_prior_symbolic','original_3term',
         'original_latent','fully_fitted_cart','no_update',
         'block_weight','single24','parent_single16','full_poly_symbolic')
FAMILIES=(('known',tuple(sorted(S.KNOWN))),
          ('three',tuple(sorted(S.UNFAMILIAR))),
          ('nested',tuple(sorted(S.NESTED))),
          ('cross',tuple(sorted(S.CROSS))),
          ('off',tuple(sorted(S.OFF))))
def zero():
    return {'correct':0,'wrong_confident':0,'abstained':0,'held':0}
def accumulate(a,b):
    for k in a:a[k]+=b[k]
def percent(v,k):
    return 100*v[k]/v['held'] if v['held'] else 0.0

def train_from_paid(rows,view):
    if len(rows)!=32 or len(set(x for x,y in rows))!=32:
        raise AssertionError('WSP148_UNQUALIFIED_TRAIN_ROWS')
    model=H.fit(rows)
    weights=W.program(rows,block_width=2)
    single=W.program(rows,block_width=1)
    old16=OLD.program_weights(rows)
    poly=Z.fit(rows)
    symbolic=F.symbolic_fit(rows)
    if (model['level'],model['terms'],model['degree'],
        model['tied_count'],model['overflow'])!=(
        symbolic['level'],symbolic['terms'],symbolic['degree'],
        symbolic['count'],symbolic['overflow']):
        raise AssertionError('WSP148_INDEPENDENT_SYMBOLIC_STRUCTURE_MISMATCH')
    direct=D.fit(rows)
    latent=N.fit(rows)
    cart=C.FullyFitCART()
    for x,y in rows:
        cart.observe(view,SimpleNamespace(law_id=view.law_id,
                              subject=view.subject(x),input=x,effect=y))
    cart.fit(view)
    if view.law_id not in cart.models or len(cart.examples[view.law_id])!=32:
        raise AssertionError('WSP148_CONVENTIONAL_NOT_FULLY_FITTED')
    out={m:[] for m in METHODS}
    for x in range(64):
        a=H.predict(model,x)
        b=F.symbolic_predict(symbolic,x)
        if a!=b:
            raise AssertionError(('WSP148_SYMB_PARITY',view.law_id,x))
        out['hierarchical'].append(a)
        out['equal_prior_symbolic'].append(b)
        out['original_3term'].append(D.predict(direct,x))
        out['original_latent'].append(N.predict(latent,x))
        out['fully_fitted_cart'].append(cart.infer(view,view.subject(x)))
        out['no_update'].append(None)
        out['block_weight'].append(W.predict(weights,x))
        out['single24'].append(W.predict(single,x))
        out['parent_single16'].append(OLD.predict(old16,x))
        out['full_poly_symbolic'].append(Z.predict(poly,x))
    if any(out['full_poly_symbolic'][x]!=y for x,y in rows):
        raise AssertionError('WSP148_POLY_TRAIN_MISMATCH')
    return model,weights,{key:tuple(v) for key,v in out.items()},dict(
      block_writes=weights['individual_writes'],block_residual=weights['residual_errors'],
      single_writes=single['individual_writes'],single_residual=single['residual_errors'],
      block_cpu_s=weights['cpu_s'],single_cpu_s=single['cpu_s'],
      old16_cpu_s=old16['cpu_s'],poly_cpu_s=poly['cpu_s'],poly_rank=poly['rank'],
      block_exact_fit=weights['has_exact_fit'],single_exact_fit=single['has_exact_fit'])

def charge_arm(view,seed,name):
    cust=S.Custodian(view,seed)
    t0=perf_counter_ns();c0=process_time_ns()
    rows=[]
    def charge(x):
        if type(x) is not int or not 0<=x<64:
            raise PermissionError('WSP148_INVALID_TYPED_INTERVENTION')
        event=cust.query(view.subject(x))
        if (event.law_id,event.input,event.subject)!=(
                view.law_id,x,view.subject(x)):
            raise AssertionError('WSP148_INVALID_SOURCE_PUBLIC_RECEIPT')
        rows.append((x,event.effect))
        return event.effect
    if name=='fixed': actions=P.fixed_schedule()
    elif name=='random': actions=P.random_schedule(view.law_id)
    elif name=='adaptive': actions=None
    else:raise ValueError('WSP148_UNKNOWN_POLICY')
    if actions is None:
        active=P.adaptive_schedule(view.law_id,charge)
        if active!=tuple(rows):
            raise AssertionError('WSP148_ADAPTIVE_ACTION_HISTORY_DRIFT')
    else:
        for x in actions:charge(x)
    if len(rows)!=32 or tuple(x for x,y in rows[:20])!=P.WARM:
        raise AssertionError('WSP148_SOURCE_CHARGE_BUDGET_OR_WARM_DRIFT')
    model,weights,output,extras=train_from_paid(tuple(rows),view)
    elapsed={'wall_s':round((perf_counter_ns()-t0)/1e9,6),
             'cpu_s':round((process_time_ns()-c0)/1e9,6)}
    elapsed.update(extras)
    return cust,tuple(rows),model,weights,output,elapsed

def run():
    start_wall=perf_counter_ns();start_cpu=process_time_ns()
    tracemalloc.start()
    if (len(P.FIXED)!=32 or P.WARM!=P.FIXED[:20]
        or len(P.MASKS)!=63 or len(N.templates())!=17640
        or len(D.FEATURES)!=63):
        raise AssertionError('WSP148_INHERITED_MODEL_DRIFT')
    data={f:{p:{m:{'paired':zero(),'arm_unseen32':zero()}
                 for m in METHODS}
             for p in POLICIES} for f,seeds in FAMILIES}
    per_world=[]
    witnesses=[]
    known={p:{} for p in POLICIES}
    costs={p:{'cpu_s':0.0,'wall_s':0.0,'block_cpu_s':0.0,'single_cpu_s':0.0,'old16_cpu_s':0.0,'poly_cpu_s':0.0} for p in POLICIES}
    events={p:0 for p in POLICIES}
    withheld_sha=[]
    for family,seeds in FAMILIES:
        for seed in seeds:
            view=S.world(seed)
            paid={};rows_by={};states={};weight_states={};predictions={};trial_timing={}
            for policy in POLICIES:
                c,rows,model,weights,output,timing=charge_arm(view,seed,policy)
                paid[policy]=c
                rows_by[policy]=rows
                states[policy]=model
                weight_states[policy]=weights
                predictions[policy]=output
                trial_timing[policy]=timing
                costs[policy]['cpu_s']+=timing['cpu_s']
                costs[policy]['wall_s']+=timing['wall_s']
                for key in ('block_cpu_s','single_cpu_s','old16_cpu_s','poly_cpu_s'):
                    costs[policy][key]+=timing[key]
                events[policy]+=len(rows)
                if family=='known':
                    known[policy][view.law_id]={'rows':rows,'state':model,
                        'outputs':output['hierarchical'],
                        'weights':weights,'block_outputs':output['block_weight']}
            # No selector/learner is called after the owner receives all
            # fully frozen 64-state output vectors for all arms/controls.
            owner=S.OwnerPostCommit(view,seed,paid)
            decision=owner.score_once(predictions)
            held=decision['held_queries_after_all_output_seals']
            # Separate source-blind WSP148 namespace audit, after full seals.
            union=set().union(*(set(x for x,y in rows_by[p]) for p in POLICIES))
            unseen=set(range(64))-union
            if len(unseen)<8:raise AssertionError('WSP148_QUERY_UNION_OVER_BUDGET')
            corroborate=tuple(sorted(unseen,key=lambda x:(
                sha256(('WSP148|HELD|'+str(view.law_id)+'|'+str(x)).encode()).digest(),x))[:8])
            if tuple(held)!=tuple(corroborate) or len(held)!=8:
                raise AssertionError('WSP148_OWNER_POSTSEAL_QUERIES_DISAGREE')
            if decision['source_paid_events']!=96:
                raise AssertionError('WSP148_BAD_PER_WORLD_ACTION_BUDGET')
            withheld_sha.append([family,seed,decision['held_sha256'],
                                  decision['prediction_seal_sha256']])
            for p in POLICIES:
                for m in METHODS:
                    for split in ('paired','arm_unseen32'):
                        accumulate(data[family][p][m][split],
                                   decision['source_private_scores'][p][m][split])
            per_world.append({'family':family,'seed':seed,
                'common_held_sha256':decision['held_sha256'],
                'prediction_seal_sha256':decision['prediction_seal_sha256'],
                'disjoint_unseen_count':len(set(range(64))-
                    set().union(*(set(x for x,y in rows_by[p]) for p in POLICIES))),
                'per_policy':{p:{
                    'action_history_sha256':S.digest(rows_by[p]),
                    'state_sha256':H.digest(states[p]),
                    'programmed_weights_sha256':S.digest([weight_states[p]['weights'],weight_states[p]['edits']]),
                    'programmed_weight_edits':weight_states[p]['individual_writes'],
                    'programmed_weight_residual':weight_states[p]['residual_errors'],
                     'block_exact_fit':trial_timing[p]['block_exact_fit'],
                     'single_exact_fit':trial_timing[p]['single_exact_fit'],
                     'single_residual':trial_timing[p]['single_residual'],
                    'level':states[p]['level'],
                    'tied':states[p]['tied_count'],
                    'paired_scores':decision['source_private_scores'][p],
                    'elapsed':trial_timing[p]
                    } for p in POLICIES}})
            witnesses.append([family,seed,
                decision['source_effect_receipts_sha256'],
                decision['prediction_seal_sha256'],decision['held_sha256']])
    if (events!={p:2048 for p in POLICIES}
        or len(per_world)!=64):
        raise AssertionError('WSP148_UNAUTHORIZED_OR_INCOMPLETE_PUBLIC_SOURCE')
    # All worlds learned; prove old paid facts still replay bit-for-bit.
    for p in POLICIES:
        for law,rec in known[p].items():
            after=H.restore(H.canon(rec['state']),rec['rows'])
            if any(H.predict(after,x)!=rec['outputs'][x] for x in range(64)):
                raise AssertionError('WSP148_OLD_WORLD_INTERFERENCE')
    cold={p:0 for p in POLICIES}
    cold_scores={p:zero() for p in POLICIES}
    for seed in sorted(S.TRANSFER):
        view=S.world(seed)
        for p in POLICIES:
            cust=S.Custodian(view,seed)
            if cust.budget!=0 or cust.events:
                raise AssertionError('WSP148_RELABELED_SOURCE_CHARGED')
            old=known[p][view.law_id]
            restored=H.restore(H.canon(old['state']),old['rows'])
            output=tuple(H.predict(restored,x) for x in range(64))
            if output!=old['outputs']:
                raise AssertionError('WSP148_INHERITED_COLD_DRIFT')
            restored_weight=W.restore(old['weights'],old['rows'])
            block_output=W.predictions(restored_weight)
            if block_output!=old['block_outputs']:
                raise AssertionError('WSP148_DIRECT_COLD_DRIFT')
            cold[p]+=sum(block_output[x]==old['block_outputs'][x] for x in range(64))
            # Owner-only cold scoring, not candidate feedback.
            outcome=cust.score_once({s:output[x] for s,x in cust.held()})
            accumulate(cold_scores[p],{k:outcome[k] for k in zero()})
    if cold!={p:512 for p in POLICIES}:
        raise AssertionError('WSP148_COLD_KNOWLEDGE_IDENTITY_FAIL')
    candidate=data['nested']['adaptive']['block_weight']['paired']
    strong={m:data['nested']['adaptive'][m]['paired'] for m in
        ('single24','fully_fitted_cart','full_poly_symbolic')}
    best=max(strong,key=lambda m:(strong[m]['correct'],m))
    improvement=100*(candidate['correct']-strong[best]['correct'])/256
    nested_worlds=[rec for rec in per_world if rec['family']=='nested']
    if len(nested_worlds)!=32:raise AssertionError('WSP148_PRIMARY_WORLD_COUNT_DRIFT')
    block_exact=sum(bool(rec['per_policy']['adaptive']['block_exact_fit']) for rec in nested_worlds)
    single_exact=sum(bool(rec['per_policy']['adaptive']['single_exact_fit']) for rec in nested_worlds)
    exact_gain=block_exact-single_exact
    other={fam:{'block':data[fam]['adaptive']['block_weight']['paired'],
                 'best_control_correct':max(data[fam]['adaptive'][m]['paired']['correct']
                         for m in ('single24','fully_fitted_cart','full_poly_symbolic'))}
            for fam in ('known','three','cross')}
    eligible=(exact_gain>=8 and improvement>=3 and candidate['correct']>=160
         and percent(candidate,'wrong_confident')<=1
         and all(100*(v['best_control_correct']-v['block']['correct'])/
                 v['block']['held']<=5 and percent(v['block'],'wrong_confident')<=1
                 for fam,v in other.items() if fam in ('known','three'))
         and percent(other['cross']['block'],'wrong_confident')<=2
         and percent(data['off']['adaptive']['block_weight']['paired'],
                     'wrong_confident')<=2)
    _,peak=tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {
        'schema':'wsp148.coordinated-weight-repair-nested-grammar-development-result.v1',
        'status':'DEVELOPMENT_COORDINATED_WEIGHT_REPAIR_SUPPORTED' if eligible
                  else 'DEVELOPMENT_COORDINATED_WEIGHT_REPAIR_NO_GO',
        'scientific_pass':False,'native_admission':False,
        'source_safe_charged_public_effects':sum(events.values()),
        'protected_original_effects':0,
        'per_policy_charged_source_effects':events,
        'cohorts':{f:len(seeds) for f,seeds in FAMILIES},
        'all_64_predictions_committed_before_any_held_selection':True,
        'actual_queryblind_unseen_questions_per_world':8,
        'equal_prior_independent_flat_symbolic_tie_all':True,
        'all_policies_budget_32':True,
        'exact_cold_old_law_retention':cold,
        'cold_relabel_truth_scores':cold_scores,
        'scores':data,
        'nested_block_gain_over_best_same_arm_control_pp':improvement,
        'nested_strongest_same_arm_control':best,
        'nested_block_correct':candidate['correct'],
        'nested_block_confident_wrong_pct':percent(candidate,'wrong_confident'),
        'other_family_noninferiority':other,
        'source_owner_receipts_sha256':S.digest(witnesses),
        'private_future_selection_sha256':S.digest(withheld_sha),
        'per_world':per_world,
        'resource':{'total_wall_s':round((perf_counter_ns()-start_wall)/1e9,3),
            'total_cpu_s':round((process_time_ns()-start_cpu)/1e9,3),
            'peak_tracemalloc_bytes':peak,
            'per_policy_acquisition_plus_full_fit_and_readout':{
                p:{k:round(v,6) for k,v in costs[p].items()}
                for p in POLICIES},
            'energy':'NOT_MEASURED'},
        'limitations':[
          'New independent public synthetic nested-composition and threshold grammar, not physical causal evidence',
          'Hidden x selected after prediction seals from action-disjoint union, but selection depends on policy acquisition',
          'Each within-law eight held queries is correlated, worlds/seeds are primary units',
          'Independent hierarchical/symbolic, same-evidence full polynomial, capacity-matched single24, and fully fitted CART controls',
          'Fully fitted CART is conventional only, not independent fully trained recurrent comparator',
          'Only within-law post-action generalization; no cross-world learning, original first-use or native model promotion',
          'CPU and tracked allocations measured; RSS, GPU energy and true original scientific improvement unverified'
        ]
    }

if __name__=='__main__':
    print('WSP148_RESULT_JSON='+S.canon(run()))
