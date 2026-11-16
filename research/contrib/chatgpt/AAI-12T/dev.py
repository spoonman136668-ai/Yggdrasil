"""AAI-12T: isolated source-only, novelty-gated primitive induction.

No native Yggdrasil integration, scientific first-use, token prediction or hidden
world parameters available to any learner. See frozen prereg.json in repository.
"""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
import math
import time

ALL = (1 << 64) - 1
OPS = ('XOR', 'AND', 'OR')
FIXTURES = ('mechanical:alpha', 'mechanical:beta')
NOVEL = ((0,1,2,3,232),(1,2,4,5,104),(2,4,5,0,202),
         (0,3,5,1,41),(1,3,4,2,23),(0,2,5,4,113),
         (1,4,5,3,212),(0,1,4,5,75),(2,3,5,1,53),
         (0,3,4,2,194),(1,2,5,0,166),(0,2,3,5,107))
FAMILIAR = ((0,1,2,3,'XOR','AND','OR',0),
            (2,4,1,5,'AND','OR','XOR',1),
            (3,5,0,2,'OR','XOR','AND',0),
            (1,4,0,5,'AND','XOR','OR',1))
NEGATIVE = ('parity6', 'majority6', 'exactly_two6', 'sha256_truth6')
ARMS = ('fixed_program_3gate','always_ternary_256','knn5',
        'fully_fitted_id3','adaptive_no_growth','novelty_gate')
CATEGORIES = (('novel',NOVEL),('familiar',FAMILIAR),('negative',NEGATIVE))
VARS = tuple(sum(1 << x for x in range(64) if (x >> i) & 1) for i in range(6))
CATALOG = None
CATALOG_SECONDS = 0.


def gate(name,a,b):
    return a ^ b if name == 'XOR' else a & b if name == 'AND' else a | b if name == 'OR' else None


def source_mask(category,spec):
    """PRIVILEGED fixture. Models see only its consequences, never spec."""
    if category == 'novel':
        a,b,c,f,mask=spec
        return sum(((((mask >> (4*((x>>a)&1) + 2*((x>>b)&1) + ((x>>c)&1))) & 1) ^ ((x>>f)&1)) << x) for x in range(64))
    if category == 'familiar':
        a,b,c,d,l,r,root,flip=spec
        y=gate(root,gate(l,VARS[a],VARS[b]),gate(r,VARS[c],VARS[d]))
        return y ^ (ALL if flip else 0)
    if category == 'negative':
        def bit(x):
            if spec=='parity6': return x.bit_count() & 1
            if spec=='majority6': return int(x.bit_count()>=4)
            if spec=='exactly_two6': return int(x.bit_count()==2)
            if spec=='sha256_truth6':
                h=hashlib.sha256(f'AAI12T-negative6|{x}'.encode('ascii')).digest()
                return h[0]&1
            raise PermissionError('unregistered negative world')
        return sum(bit(x)<<x for x in range(64))
    raise PermissionError('scientific family first-use denied')


def ranked_source(fixture,category,idx):
    if fixture not in FIXTURES or category not in ('novel','familiar','negative'):
        raise PermissionError('AAI12T SCIENTIFIC FIRST USE DISARMED')
    count=dict((n,len(w)) for n,w in CATEGORIES)[category]
    if type(idx) != int or not 0<=idx<count:raise PermissionError('unlisted world')
    def key(x):
        return hashlib.sha256(f'AAI12T|{fixture}|{category}|{idx}|{x}'.encode('ascii')).digest(),x
    return sorted(range(64),key=key)


def paired_do_inputs(fixture,category,idx):
    seen=set();pairs=[]
    for x in ranked_source(fixture,category,idx):
        if x in seen:continue
        for bit in range(6):
            y=x^(1<<bit)
            if y not in seen:
                pairs.append((x,y));seen.update((x,y));break
        if len(pairs)==16:break
    assert len(pairs)==16 and len(seen)==32
    assert all((x^y).bit_count()==1 for x,y in pairs)
    return tuple(pairs)


def public_observations(truth,pairs):
    return tuple((x,(truth>>x)&1) for pair in pairs for x in pair)


def catalog():
    global CATALOG,CATALOG_SECONDS
    if CATALOG is None:
        start=time.perf_counter();lookup={}
        for a,b,c,d in itertools.permutations(range(6),4):
            for l,r,root in itertools.product(OPS,repeat=3):
                m=gate(root,gate(l,VARS[a],VARS[b]),gate(r,VARS[c],VARS[d]))
                for flip in (0,1):
                    truth=m ^ (ALL if flip else 0)
                    desc=(3+flip,a,b,c,d,OPS.index(l),OPS.index(r),OPS.index(root),flip)
                    if truth not in lookup or desc<lookup[truth]:lookup[truth]=desc
        CATALOG=tuple(sorted((desc,truth) for truth,desc in lookup.items()))
        CATALOG_SECONDS=time.perf_counter()-start
    return CATALOG


def fit_fixed(rows):
    seen=sum(1<<x for x,_ in rows)
    positive=sum(y<<x for x,y in rows)
    return min((((truth^positive)&seen).bit_count(),desc,truth) for desc,truth in catalog())[2]


def fit_ternary(rows):
    """Infer an 8-bit 3-input relation from public labels, not oracle tables."""
    choices=[]
    for triple in itertools.combinations(range(6),3):
        for fourth in range(6):
            if fourth in triple:continue
            votes=[[0,0] for _ in range(8)]
            for x,y in rows:
                code=4*((x>>triple[0])&1)+2*((x>>triple[1])&1)+((x>>triple[2])&1)
                votes[code][y^((x>>fourth)&1)]+=1
            table=sum(int(n1>n0)<<i for i,(n0,n1) in enumerate(votes))
            prediction=sum(((((table>>(4*((x>>triple[0])&1)+2*((x>>triple[1])&1)+((x>>triple[2])&1)))&1)^((x>>fourth)&1))<<x) for x in range(64))
            errors=sum(((prediction>>x)&1)!=y for x,y in rows)
            choices.append((errors,table.bit_count(),triple,fourth,table,prediction))
    _,_,triple,fourth,table,mask=min(choices)
    return (triple,fourth,table,mask)


def fit_knn(rows):return tuple(rows)


def entropy(rows):
    if not rows:return 0.
    p=sum(y for _,y in rows)/len(rows)
    return 0. if p in (0.,1.) else -p*math.log2(p)-(1-p)*math.log2(1-p)


def fit_id3(rows,cols=tuple(range(6))):
    if not rows:return ('leaf',0)
    if entropy(rows)==0 or not cols:return ('leaf',int(2*sum(y for _,y in rows)>=len(rows)))
    base=entropy(rows);candidate=None
    for col in cols:
        a=tuple(row for row in rows if not ((row[0]>>col)&1))
        b=tuple(row for row in rows if (row[0]>>col)&1)
        if not a or not b:continue
        gain=base-(len(a)*entropy(a)+len(b)*entropy(b))/len(rows)
        if candidate is None or gain>candidate[0]+1e-12:candidate=(gain,col,a,b)
    if candidate is None:return ('leaf',int(2*sum(y for _,y in rows)>=len(rows)))
    _,col,a,b=candidate
    rest=tuple(j for j in cols if j!=col)
    return ('branch',col,fit_id3(a,rest),fit_id3(b,rest))


def predict(mode,model,x):
    if mode=='fixed':return (model>>x)&1
    if mode=='ternary':return (model[3]>>x)&1
    if mode=='knn':
        near=sorted(enumerate(model),key=lambda i:((i[1][0]^x).bit_count(),i[0]))[:5]
        return int(sum(t[1][1] for t in near)>=3)
    if mode=='id3':
        tree=model
        while tree[0]=='branch':tree=tree[2+((x>>tree[1])&1)]
        return tree[1]
    raise ValueError('unrecognized model')


def fit(mode,rows):
    return {'fixed':fit_fixed,'ternary':fit_ternary,'knn':fit_knn,'id3':fit_id3}[mode](rows)


def select_mode(rows,allow_growth):
    train,valid=rows[:24],rows[24:]
    assert len(train)==24 and len(valid)==8
    options=['fixed','knn']+(['ternary'] if allow_growth else [])
    errors={}
    for mode in options:
        trained=fit(mode,train)
        errors[mode]=sum(predict(mode,trained,x)!=y for x,y in valid)
    ordinary='fixed' if errors['fixed']<=errors['knn'] else 'knn'
    if allow_growth and errors['ternary']<=errors[ordinary]-2:
        return 'ternary'
    return ordinary


def fit_arm(arm,rows):
    assert len(rows)==32 and len(set(x for x,_ in rows))==32
    if arm=='fixed_program_3gate':mode='fixed'
    elif arm=='always_ternary_256':mode='ternary'
    elif arm=='knn5':mode='knn'
    elif arm=='fully_fitted_id3':mode='id3'
    elif arm=='adaptive_no_growth':mode=select_mode(rows,False)
    elif arm=='novelty_gate':mode=select_mode(rows,True)
    else:raise ValueError('unregistered arm')
    return (mode,fit(mode,rows))


def checkpoint(arm,rows,trained):
    """Canonical public state includes the explicitly learned ternary primitive."""
    mode,model=trained
    if arm not in ARMS or len(rows)!=32 or len(set(x for x,y in rows))!=32:
        raise ValueError('unregistered or oversized public checkpoint')
    primitive = ({'triple':list(model[0]),'fourth':model[1],
                  'truth_table_u8':model[2]} if mode=='ternary' else None)
    data={'schema':'aai12t.public-cold.v1','arm':arm,
          'rows':rows,'mode':mode,'learned_primitive':primitive}
    return json.dumps(data,sort_keys=True,separators=(',',':'))


def restore_checkpoint(source):
    try:
        data=json.loads(source)
        if (type(data)!=dict or set(data)!={'schema','arm','rows','mode','learned_primitive'}
            or data['schema']!='aai12t.public-cold.v1' or data['arm'] not in ARMS
            or type(data['rows'])!=list or len(data['rows'])!=32
            or json.dumps(data,sort_keys=True,separators=(',',':'))!=source):
            raise ValueError('bad serialized cold source')
        rows=tuple(tuple(r) for r in data['rows'])
        if (len(set(x for x,y in rows))!=32
            or any(type(x)!=int or type(y)!=int or not 0<=x<64 or y not in (0,1) for x,y in rows)):
            raise ValueError('corrupted public rows')
        trained=fit_arm(data['arm'],rows)
        mode,model=trained
        primitive = ({'triple':list(model[0]),'fourth':model[1],
                      'truth_table_u8':model[2]} if mode=='ternary' else None)
        if mode!=data['mode'] or primitive!=data['learned_primitive']:
            raise ValueError('learned primitive corrupted or mode changed')
        return trained
    except (TypeError,KeyError,IndexError) as exc:
        raise ValueError('invalid cold source') from exc


def cold(arm,rows,trained):
    wire=checkpoint(arm,rows,trained)
    return restore_checkpoint(wire)==trained


def score():
    # Structural source-grammar novelty is mechanically checked before scoring.
    base={truth for _,truth in catalog()}
    if len(NOVEL)!=12 or len(FAMILIAR)!=4 or len(NEGATIVE)!=4:
        raise AssertionError('source world inventory drift')
    if any(source_mask('novel',w) in base for w in NOVEL):
        raise AssertionError('novel source target representable by old grammar')
    results={cat:{arm:[] for arm in ARMS} for cat,_ in CATEGORIES}
    world_acc={arm:{} for arm in ARMS};selected={cat:{arm:{} for arm in ARMS} for cat,_ in CATEGORIES}
    elapsed={arm:0. for arm in ARMS};audit=[]; cold_checks=0
    for category,worlds in CATEGORIES:
        for idx,spec in enumerate(worlds):
            truth=source_mask(category,spec)
            for fixture in FIXTURES:
                pairs=paired_do_inputs(fixture,category,idx)
                rows=public_observations(truth,pairs)
                seen={x for x,y in rows};unseen=tuple(x for x in range(64) if x not in seen)
                if len(rows)!=32 or len(unseen)!=32 or any(x in seen for x in unseen):
                    raise AssertionError('unequal fit/test public source')
                for arm in ARMS:
                    tic=time.perf_counter()
                    trained=fit_arm(arm,rows)
                    if not cold(arm,rows,trained):raise AssertionError('cold state not restored')
                    predictions=tuple(predict(*trained,x) for x in unseen)
                    elapsed[arm]+=time.perf_counter()-tic
                    scores=tuple(int(p==((truth>>x)&1)) for x,p in zip(unseen,predictions))
                    results[category][arm].extend(scores)
                    if category=='novel':world_acc[arm].setdefault(idx,[]).extend(scores)
                    selected[category][arm][(idx,fixture)]=trained[0]
                    audit.append([category,idx,fixture,arm,trained[0],list(predictions),sum(scores)])
                    cold_checks+=1
    acc={cat:{arm:round(sum(a)/len(a),9) for arm,a in byarm.items()} for cat,byarm in results.items()}
    conventional=('fixed_program_3gate','always_ternary_256','knn5','fully_fitted_id3','adaptive_no_growth')
    best_n=max(conventional,key=lambda arm:acc['novel'][arm])
    generic=('knn5','fully_fitted_id3','adaptive_no_growth')
    cand='novelty_gate'
    good_worlds=sum(sum(world_acc[cand][i])/len(world_acc[cand][i])>=.80 for i in range(12))
    novel_discovery=sum(all(selected['novel'][cand][(i,f)]=='ternary' for f in FIXTURES) for i in range(12))
    familiar_bad=sum(any(selected['familiar'][cand][(i,f)]=='ternary' for f in FIXTURES) for i in range(4))
    # Charge each method the complete original model fit+selection+evaluation+restore;
    # add nonamortized source-free fixed-grammar compilation to every method that uses it.
    for arm in ('fixed_program_3gate','adaptive_no_growth','novelty_gate'):
        elapsed[arm]+=CATALOG_SECONDS
    full_generic=min(elapsed[a] for a in generic)
    checks={
        'novel_gain_vs_strongest_control_at_least_0_03':acc['novel'][cand]>=acc['novel'][best_n]+.03-1e-10,
        'novel_gain_vs_no_growth_at_least_0_06':acc['novel'][cand]>=acc['novel']['adaptive_no_growth']+.06-1e-10,
        'nine_of_twelve_novel_worlds_at_least_0_80':good_worlds>=9,
        'eight_novel_worlds_both_fixtures_induce_ternary':novel_discovery>=8,
        'at_most_one_familiar_world_either_fixture_induces_ternary':familiar_bad<=1,
        'familiar_within_0_03_best_generic':acc['familiar'][cand]>=max(acc['familiar'][a] for a in generic)-.03-1e-10,
        'unrelated_negative_within_0_03_best_generic':acc['negative'][cand]>=max(acc['negative'][a] for a in generic)-.03-1e-10,
        'whole_source_fit_predict_cost_within_50x':elapsed[cand]<=50*full_generic,
    }
    return {
        'schema':'yggdrasil.aai12t.source-dev.v1',
        'classification':'DEV_ADMITTED_SCIENCE_UNVERIFIED' if all(checks.values()) else 'DEV_NO_GO_NO_SCIENCE',
        'accuracies':acc,'best_novel_control':best_n,'novel_worlds_above_0_80':good_worlds,
        'worlds_with_novelty_induction_both_fixtures':novel_discovery,
        'familiar_worlds_false_induction_either_fixture':familiar_bad,
        'frozen_checks':checks,'full_source_wall_seconds':{a:round(v,6) for a,v in elapsed.items()},
        'source_free_compiler_seconds':round(CATALOG_SECONDS,6),
        'trace_sha256':hashlib.sha256(json.dumps(audit,separators=(',',':')).encode('ascii')).hexdigest(),
        'cold_checks':cold_checks,
        'counts':{'novel_per_arm':768,'familiar_per_arm':256,'negative_per_arm':256},
        'source_only':True,'scientific_cohorts_used':0,'native_model_modified':False}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source-dev',action='store_true')
    parser.add_argument('--primary',action='store_true')
    args=parser.parse_args()
    if args.primary:parser.error('AAI12T SCIENTIFIC FIRST USE DISARMED')
    if not args.source_dev:parser.error('only source-dev registered; scientific first use disarmed')
    print('AAI12T_DEV='+json.dumps(score(),sort_keys=True),flush=True)


if __name__=='__main__':main()
