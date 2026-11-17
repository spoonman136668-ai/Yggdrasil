"""WSP136 prospective same-source causal identifiability-vs-learning gap.
Requires WSP135 source-blind fixed learner and symbolic conventional controls,
copied exact stronger SOURCE-GRAMMAR oracle from WSP135 PR1179.
Only WSP136 source/evaluator sees actual source truth.
"""
from __future__ import annotations
from hashlib import sha256
from importlib.util import module_from_spec,spec_from_file_location
from pathlib import Path
import time,tracemalloc,json,sys
import source as S
import oracle as O

ROOT=Path(__file__).resolve().parents[1]
def pinned(name,path):
    spec=spec_from_file_location(name,ROOT/'WSP-135'/path)
    m=module_from_spec(spec)
    sys.modules[name]=m
    spec.loader.exec_module(m)
    return m
N=pinned('_wsp136_pinned_wsp135_native','learner.py')
C=pinned('_wsp136_pinned_wsp135_control','controls.py')
ARMS=('DIRECT_LATENT','SAME_PRIOR_SYMBOLIC','SOURCE_GRAMMAR_ORACLE','FULLY_FITTED_CART','NO_UPDATE')
def empty():
    return {name:{'correct':0,'wrong_confident':0,'abstained':0,'held':0,'source_calls':0} for name in ARMS}
def add(total,d):
    for k in total:total[k]+=d[k]
def truth_mask(vals):
    return sum((int(y)<<x) for x,y in enumerate(vals))
def run():
    begin=time.perf_counter()
    start_cpu=time.process_time()
    tracemalloc.start()
    bank=O.candidate_bank()
    if len(bank)!=7062:raise AssertionError(('UNEXPECTED_ORACLE_GRAMMAR_SIZE',len(bank)))
    oracle=O.ExactOracle(bank)
    n=N.LatentInducer()
    sym=C.ExactSymbolicFactor()
    cart=C.FullyFitCART()
    scores={'known':empty(),'unfamiliar':empty(),'transfer':empty()}
    known_views={}
    source_views={}
    oracle_by_law={}
    per_world=[]
    source_members=0
    schedule=N.schedule()
    if schedule!=C.action_order() or len(schedule)!=32 or len(set(schedule))!=32:
        raise AssertionError('WSP136_ACTION_SCHEDULE_NOT_PINNED_OR_EQUAL')
    known_previous=None
    for family,seeds in (('known',sorted(S.KNOWN)),('unfamiliar',sorted(S.UNFAMILIAR))):
        for seed in seeds:
            v=S.world(seed)
            source_views[v.law_id]=v
            c=S.Custodian(v,seed)
            version=oracle.begin()
            for x in schedule:
                public=c.query(v.subject(x))
                n.observe(v,public)
                sym.observe(v,public)
                cart.observe(v,public)
                version.observe(x,public.effect)
            cart.fit(v)
            cold=version.restore()
            if cold.snapshot()!=version.snapshot():raise AssertionError('ORACLE_COLD_REPLAY_NOT_EQUAL')
            oracle_by_law[v.law_id]=version
            held=c.held()
            outputs={name:{} for name in ARMS}
            for subject,x in held:
                native=n.infer(v,subject)
                same=sym.infer(v,subject)
                expert=version.infer(x)
                trained=cart.infer(v,subject)
                if native!=same:raise AssertionError('EQUAL_PRIOR_SYMBOLIC_PARITY_FAILURE')
                outputs['DIRECT_LATENT'][subject]=native
                outputs['SAME_PRIOR_SYMBOLIC'][subject]=same
                outputs['SOURCE_GRAMMAR_ORACLE'][subject]=expert
                outputs['FULLY_FITTED_CART'][subject]=trained
                outputs['NO_UPDATE'][subject]=None
            source_members+=int(truth_mask(c.truth) in bank)
            if truth_mask(c.truth) not in bank:raise AssertionError('TRUE_LAW_NOT_IN_PRIVILEGED_GRAMMAR')
            for name in ARMS:
                measured={'correct':0,'wrong_confident':0,'abstained':0,'held':len(held),'source_calls':32}
                for subject,x in held:
                    prediction=outputs[name][subject]
                    if prediction is None:measured['abstained']+=1
                    elif prediction==c.truth[x]:measured['correct']+=1
                    else:measured['wrong_confident']+=1
                add(scores[family][name],measured)
            c.score_once(outputs['DIRECT_LATENT'])
            per_world.append([family,seed,v.law_id,c.receipt,S.digest(outputs['DIRECT_LATENT']),S.digest(outputs['SOURCE_GRAMMAR_ORACLE']),version.snapshot()])
            if family=='known':known_views[v.law_id]=v
        if family=='known':
            known_previous={(law,x):n.infer(v,v.subject(x)) for law,v in known_views.items() for x in range(64)}
    current={(law,x):n.infer(v,v.subject(x)) for law,v in known_views.items() for x in range(64)}
    if current!=known_previous:raise AssertionError('SOURCE_LEARNING_INTERFERENCE')
    snapshot=n.snapshot()
    restored=N.LatentInducer.restore(snapshot,source_views)
    if restored.snapshot()!=snapshot:raise AssertionError('SOURCE_LEARNING_COLD_RESTORE_FAILED')
    transfer_same=0
    for seed in sorted(S.TRANSFER):
        v=S.world(seed)
        c=S.Custodian(v,seed)
        original=S.world(194000+seed-196000)
        version=oracle_by_law[v.law_id]
        outputs={name:{} for name in ARMS}
        for subject,x in c.held():
            native=restored.infer(v,subject)
            if native==n.infer(original,original.subject(x)):transfer_same+=1
            same=sym.infer(v,subject)
            if native!=same:raise AssertionError('COLD_SOURCELESS_SYMBOLIC_MISMATCH')
            outputs['DIRECT_LATENT'][subject]=native
            outputs['SAME_PRIOR_SYMBOLIC'][subject]=same
            outputs['SOURCE_GRAMMAR_ORACLE'][subject]=version.infer(x)
            outputs['FULLY_FITTED_CART'][subject]=cart.infer(v,subject)
            outputs['NO_UPDATE'][subject]=None
        for name in ARMS:
            vals={'correct':0,'wrong_confident':0,'abstained':0,'held':64,'source_calls':0}
            for subject,x in c.held():
                prediction=outputs[name][subject]
                if prediction is None:vals['abstained']+=1
                elif prediction==c.truth[x]:vals['correct']+=1
                else:vals['wrong_confident']+=1
            add(scores['transfer'][name],vals)
        c.score_once(outputs['DIRECT_LATENT'])
    if transfer_same!=384:raise AssertionError('SOURCELESS_TRANSFER_MISMATCH')
    k=scores['known'];u=scores['unfamiliar']
    oracle_ok=(k['SOURCE_GRAMMAR_ORACLE']['correct']*100>=95*384 and
        u['SOURCE_GRAMMAR_ORACLE']['correct']*100>=95*384 and
        not k['SOURCE_GRAMMAR_ORACLE']['wrong_confident'] and
        not u['SOURCE_GRAMMAR_ORACLE']['wrong_confident'])
    native_gap_closed=(u['DIRECT_LATENT']['correct']*100>=95*u['SOURCE_GRAMMAR_ORACLE']['correct'] and
        u['DIRECT_LATENT']['wrong_confident']*100<=384 and oracle_ok)
    _,peak=tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {
       'schema':'wsp136.frozen-public-oracle-gap-result.v1',
       'status':'DEVELOPMENT_REPRESENTATION_GAP_CLOSED' if native_gap_closed else 'DEVELOPMENT_REPRESENTATION_GAP_OPEN',
       'information_sufficient_with_full_prior':oracle_ok,
       'same_information_symbolic_parity':True,
       'synthetic_only':True,'scientific_pass':False,'native_admission':False,
       'original_source_actions':0,'synthetic_source_actions':768,
       'private_source_grammar_given_to_oracle_only':True,
       'source_membership_count':source_members,
       'worlds':{'known':12,'unfamiliar':12,'transfer':6},
       'scores':scores,
       'oracle_minus_native_unfamiliar_correct':u['SOURCE_GRAMMAR_ORACLE']['correct']-u['DIRECT_LATENT']['correct'],
       'oracle_minus_native_known_correct':k['SOURCE_GRAMMAR_ORACLE']['correct']-k['DIRECT_LATENT']['correct'],
       'zero_call_identical_readouts':transfer_same,'cold_restore':True,'old_laws_unchanged':True,
       'source_receipts_sha256':S.digest(per_world),
       'source_grammar_sha256':oracle.bank_hash,
       'learned_state_sha256':N.digest(snapshot),
       'resource':{'cpu_seconds':round(time.process_time()-start_cpu,3),
                   'wall_seconds':round(time.perf_counter()-begin,3),
                   'peak_tracemalloc_bytes':peak, 'oracle_bank_size':len(bank),
                   'energy':'UNQUALIFIED'},
       'limits':['Exact oracle receives correct combined grammar not available to source-blind learner',
                 'Source synthetic only, not original scientific first-use',
                 'No native model promotion, new primitive invention, independent fully trained deep baseline, or demonstrated causal-world science']
    }
if __name__=='__main__':
    print('WSP136_RESULT_JSON='+S.canon(run()))
