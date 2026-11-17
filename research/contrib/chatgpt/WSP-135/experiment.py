"""WSP-135 new source-safe prospective latent-causal composition experiment."""
import time,tracemalloc
import source as S
import learner as N
import controls as C

ARMS=('LATENT_NUMERIC','INDEPENDENT_SYMBOLIC','FULLY_FITTED_CART','NO_UPDATE')
FAMILIES=('known','unfamiliar','off','transfer')
def fresh():return {key:{arm:{'correct':0,'wrong_confident':0,'abstained':0,'held':0,'source_calls':0} for arm in ARMS} for key in FAMILIES}
def add(dst,z):
    for key in dst:dst[key]+=z[key]

def run():
    t=time.perf_counter();cpu=time.process_time();tracemalloc.start()
    if N.schedule()!=C.action_order() or len(N.templates())!=len(C.codebooks()):raise AssertionError('CANDIDATE_CONTROL_ACTION_OR_COUNT')
    model=N.LatentInducer();sym=C.ExactSymbolicFactor();cart=C.FullyFitCART()
    score=fresh();views={};world_receipts=[];cart_training_errors=0;known_before=None
    for family,cohort in (('known',sorted(S.KNOWN)),('unfamiliar',sorted(S.UNFAMILIAR)),('off',sorted(S.OFF))):
        for seed in cohort:
            v=S.world(seed);c=S.Custodian(v,seed);views[v.law_id]=v
            for x in N.schedule():
                e=c.query(v.subject(x))
                model.observe(v,e);sym.observe(v,e);cart.observe(v,e)
            cart.fit(v)
            if len(c.events)!=32:raise AssertionError('SOURCE_BUDGET')
            cart_training_errors+=cart.training_errors(v)
            held=c.held()
            results={arm:{} for arm in ARMS}
            for subject,x in held:
                n=model.infer(v,subject)
                s=sym.infer(v,subject)
                if n!=s:raise AssertionError('INDEPENDENT_SYMBOLIC_MISMATCH')
                results['LATENT_NUMERIC'][subject]=n
                results['INDEPENDENT_SYMBOLIC'][subject]=s
                results['FULLY_FITTED_CART'][subject]=cart.infer(v,subject)
                results['NO_UPDATE'][subject]=None
            original=c.score_once(results['LATENT_NUMERIC'])
            add(score[family]['LATENT_NUMERIC'],original)
            world_receipts.append([seed,v.law_id,c.receipt,S.digest(results['LATENT_NUMERIC'])])
            for arm in ('INDEPENDENT_SYMBOLIC','FULLY_FITTED_CART','NO_UPDATE'):
                tally={'correct':0,'wrong_confident':0,'abstained':0,'held':len(held),'source_calls':32}
                for s,x in held:
                    z=results[arm][s]
                    if z is None:tally['abstained']+=1
                    elif z==c.truth[x]:tally['correct']+=1
                    else:tally['wrong_confident']+=1
                add(score[family][arm],tally)
        if family=='known':
            known_before={(v.law_id,x):model.infer(v,v.subject(x)) for v in (S.world(seed) for seed in S.KNOWN) for x in range(64)}
    saved=model.snapshot()
    restored=N.LatentInducer.restore(saved,views)
    if restored.snapshot()!=saved:raise AssertionError('COLD_RESTORE_MISMATCH')
    if known_before!={(v.law_id,x):model.infer(v,v.subject(x)) for v in (S.world(seed) for seed in S.KNOWN) for x in range(64)}:
        raise AssertionError('FAMILIAR_INTERFERENCE')
    transfer_same=0
    for seed in sorted(S.TRANSFER):
        v=S.world(seed);c=S.Custodian(v,seed)
        first=S.world(190000+seed-192000)
        outputs={arm:{} for arm in ARMS}
        for s,x in c.held():
            n=restored.infer(v,s)
            if n==model.infer(first,first.subject(x)):transfer_same+=1
            outputs['LATENT_NUMERIC'][s]=n
            outputs['INDEPENDENT_SYMBOLIC'][s]=sym.infer(v,s)
            outputs['FULLY_FITTED_CART'][s]=cart.infer(v,s)
            outputs['NO_UPDATE'][s]=None
            if n!=outputs['INDEPENDENT_SYMBOLIC'][s]:raise AssertionError('ZERO_SOURCE_RELABEL_PARITY')
        z=c.score_once(outputs['LATENT_NUMERIC'])
        add(score['transfer']['LATENT_NUMERIC'],z)
        for arm in ('INDEPENDENT_SYMBOLIC','FULLY_FITTED_CART','NO_UPDATE'):
            zs={'correct':0,'wrong_confident':0,'abstained':0,'held':64,'source_calls':0}
            for s,x in c.held():
                result=outputs[arm][s]
                if result is None:zs['abstained']+=1
                elif result==c.truth[x]:zs['correct']+=1
                else:zs['wrong_confident']+=1
            add(score['transfer'][arm],zs)
    k=score['known']['LATENT_NUMERIC'];u=score['unfamiliar']['LATENT_NUMERIC'];o=score['off']['LATENT_NUMERIC']
    passed=(k['correct']*100>=70*k['held'] and k['wrong_confident']*100<=10*k['held']
            and u['correct']*100>=55*u['held'] and u['wrong_confident']*100<=10*u['held']
            and o['wrong_confident']*100<=15*o['held'] and transfer_same==512)
    now=time.perf_counter();usedcpu=time.process_time();_,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
    return {'schema':'wsp135.latent-factor-public-development.result.v1',
            'status':'DEVELOPMENT_LATENT_FACTOR_SUPPORTED' if passed else 'DEVELOPMENT_LATENT_FACTOR_NO_GO',
            'scientific_pass':False,'native_admission':False,'original_source_first_use':False,
            'prereg_frozen':True,'model_supplied_two_pair_representation':True,
            'new_operator_invention_proven':False,
            'score':score,'transfer_prediction_identity':transfer_same,
            'cold_restore':True,'inherited_knowledge_unchanged':True,
            'per_world_receipts_sha256':S.digest(world_receipts),
            'learned_state_sha256':N.digest(saved),'cart_training_errors':cart_training_errors,
            'resource':{'cpu_seconds':round(usedcpu-cpu,3),'wall_seconds':round(now-t,3),
                        'peak_tracemalloc_bytes':peak, 'template_count':len(N.templates()),
                        'learned_world_count':len(views),'original_external_actions':0,'synthetic_actions':1024,
                        'energy':'UNQUALIFIED'},
            'limitations':['No independently withheld original source','Candidate and exact symbolic supplied same generic structural prior',
                           'No real causal effect grounding','No independent fully trained deep conventional baseline','No original native model admission']}
if __name__=='__main__': print('WSP135_SOURCE_SAFE_RESULT_JSON='+S.canon(run()))
