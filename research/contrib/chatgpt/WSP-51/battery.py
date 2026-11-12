"""Frozen WSP51 finite-world learning assay; synthetic external contributor evidence."""
import argparse
import json
import time
from grounding import DirectLearner, TableLearner, TrainedLearner, Erased, World, ROLES

SEEDS = {'DEV':(103,), 'PRIMARY':(2309,2311,2333,2357)}
ENCODINGS = ('identity','permuted','shifted')
ARMS = ('direct','trained','table','erased')

def score_world(cohort, seed, encoding):
    world = World(cohort,seed,encoding)
    models = {'direct':DirectLearner(),'trained':TrainedLearner(),'table':TableLearner(),'erased':Erased()}
    source = world.evidence()
    if len(source)!=10:raise AssertionError('data budget')
    elapsed={}
    for name,model in models.items():
        t0=time.perf_counter()
        for event in source:model.observe(event)
        if name=='trained':model.train()
        elapsed[name]=time.perf_counter()-t0
    counts={a:0 for a in ARMS}
    observed={a:0 for a in ARMS}
    total=0
    for verb in range(2):
        for obj in range(4):
            for side in range(2):
                cmd=(world.forms['verb',verb],world.forms['noun',obj],world.forms['destination',side])
                state=tuple(((seed+17*verb+5*obj+3*side+j)>>j)&1 for j in range(4))
                expected=world.true_result(verb,obj,side,state)
                for name,model in models.items():
                    counts[name]+=int(model.result(cmd,state)==expected)
                total+=1
    for role in ROLES:
        num=4 if role=='noun' else 2
        for y in range(num):
            acoustic=world.forms[role,y]
            for name,model in models.items():
                if name=='direct':got=model.planes[role].read(acoustic)
                elif name=='table':got=model.maps[role].get(acoustic)
                elif name=='trained':
                    w=model.weight[role][acoustic]
                    got=max(range(len(w)),key=lambda j:w[j]) if acoustic in model.seen[role] else None
                else:got=None
                observed[name]+=int(got==y)
    unknown_wrong={name:0 for name in ARMS}
    swaps_wrong={name:0 for name in ARMS}
    verb, noun, destination = (world.forms['verb',0],world.forms['noun',0],world.forms['destination',0])
    unknown=[(verb,world.unknown[0],destination),(world.unknown[1],noun,destination),
             (verb,noun,world.unknown[2]),(verb,world.unknown[3],destination)]
    swapped=[(noun,verb,destination),(destination,noun,verb),
             (noun,destination,verb),(destination,verb,noun)]
    for name,model in models.items():
        for u in unknown:unknown_wrong[name]+=int(model.decode(u) is not None)
        for u in swapped:swaps_wrong[name]+=int(model.decode(u) is not None)
    direct=models['direct']
    before={role:[direct.planes[role].read(world.forms[role,y]) for y in range(4 if role=='noun' else 2)] for role in ROLES}
    direct.observe(('noun',world.synonym,0))
    synonym_ok=(direct.planes['noun'].read(world.synonym)==0)
    uncorrupted=all(direct.planes[r].read(world.forms[r,y])==value for r in ROLES for y,value in enumerate(before[r]))
    direct.observe(('noun',world.forms['noun',3],1))
    contradiction_detected=direct.planes['noun'].read(world.forms['noun',3]) is None
    other_facts_retained=all(direct.planes[r].read(world.forms[r,y])==value for r in ROLES for y,value in enumerate(before[r]) if not(r=='noun' and y==3))
    restored=DirectLearner.restore(direct.snapshot())
    cold_parity=restored.snapshot()==direct.snapshot()
    for verb in range(2):
        for obj in range(4):
            for side in range(2):
                u=(world.forms['verb',verb],world.forms['noun',obj],world.forms['destination',side])
                s=(0,1,0,1)
                cold_parity=cold_parity and restored.result(u,s)==direct.result(u,s)
    try:
        DirectLearner.restore(direct.snapshot()+b'!')
        tamper_rejected=False
    except ValueError:tamper_rejected=True
    return {
        'cohort':cohort,'seed':seed,'encoding':encoding,'lexicon_sha256':world.digest,
        'source_experiences':len(source),'sensor_resets':4,'source_action_steps':4,
        'heldout_commands':total,'correct':counts,'observed_grounding_correct':observed,
        'unknown_false_confidence':unknown_wrong,'slot_order_false_confidence':swaps_wrong,
        'synonym_ok':synonym_ok,'prior_facts_untouched_after_synonym':uncorrupted,
        'contradiction_detected':contradiction_detected,'noncontradicted_facts_retained':other_facts_retained,
        'cold_parity':cold_parity,'tamper_rejected':tamper_rejected,
        'training_updates':models['trained'].training_updates,'direct_write_events':direct.source_events,
        'direct_capacity_bits_nominal':(256*2+256+256+256*3+256*3),
        'trainable_control_parameters':256*(4+2+2),
        'elapsed_source_fit_seconds':elapsed,
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--cohort',choices=('DEV','PRIMARY'),default='DEV')
    a=parser.parse_args()
    start=time.perf_counter()
    rows=[score_world(a.cohort,seed,enc) for seed in SEEDS[a.cohort] for enc in ENCODINGS]
    total=sum(r['heldout_commands'] for r in rows)
    correct={name:sum(r['correct'][name] for r in rows) for name in ARMS}
    conditions=len(rows)
    valid=all(r['source_experiences']==10 and r['source_action_steps']==4 and r['sensor_resets']==4 and r['direct_write_events']==12 and r['training_updates']==2800 and r['tamper_rejected'] for r in rows)
    qualified=(correct['direct']>=0.95*total and all(r['observed_grounding_correct']['direct']==8 for r in rows)
        and all(not r['unknown_false_confidence']['direct'] and not r['slot_order_false_confidence']['direct'] for r in rows)
        and all(r[k] for r in rows for k in ('synonym_ok','prior_facts_untouched_after_synonym','contradiction_detected','noncontradicted_facts_retained','cold_parity')))
    superiority=(correct['direct'] >= max(correct['table'],correct['trained'])+0.05*total)
    classification='INVALID_PROTOCOL' if not valid else ('BOUNDED_SUPPORTED_NO_SUPERIORITY' if qualified and not superiority else 'SCIENTIFIC_CANDIDATE_UNQUALIFIED' if qualified else 'NEGATIVE_OR_MIXED')
    receipt={'schema':'wsp51.microgrounding.dev-primary.v1','cohort':a.cohort,'condition_count':conditions,
        'heldout_total':total,'correct':correct,'protocol_valid':valid,'bounded_requirements_met':qualified,
        'superiority_over_strongest_control':superiority,'classification':classification,
        'overall_seconds':time.perf_counter()-start,'rows':rows}
    print('WSP51_RECEIPT '+json.dumps(receipt,sort_keys=True,separators=(',',':')),flush=True)
    if not valid:raise SystemExit(2)

if __name__=='__main__':main()
