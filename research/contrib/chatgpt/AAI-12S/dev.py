"""AAI-12S source-only mechanical study of composing causal Boolean relations.
No native model modifications, independent scientific first use, or hidden evaluator use.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import time

OPS = ('XOR', 'AND', 'OR')
ALL64 = (1 << 64) - 1
FIT = (
    (0,1,2,3,'XOR','AND','OR',0),
    (2,4,1,5,'AND','OR','XOR',1),
    (3,5,0,2,'OR','XOR','AND',0),
    (1,4,0,5,'AND','XOR','OR',1),
)
TRANSFER = (
    (0,2,1,3,'XOR','OR','AND',0),
    (1,3,2,5,'AND','XOR','OR',0),
    (5,3,0,4,'OR','AND','XOR',1),
    (2,0,3,1,'XOR','AND','AND',1),
    (3,4,1,5,'OR','XOR','XOR',0),
    (4,0,5,2,'AND','OR','OR',1),
    (1,5,0,3,'XOR','XOR','AND',0),
    (0,4,2,5,'AND','AND','OR',1),
    (5,1,4,2,'OR','OR','XOR',0),
    (3,0,5,4,'XOR','AND','XOR',1),
    (4,2,1,0,'AND','OR','XOR',0),
    (2,5,3,4,'OR','XOR','OR',1),
)
NEGATIVE = ('parity6','majority6','exactly_two','parity5_and_last')
FIXTURES = ('mechanical:alpha','mechanical:beta')
ARMS = ('synth_composed','depth6_fully_fitted_id3','degree3_fully_trained_logistic_500',
        'hamming_knn5','recent_public_table','single_gate_only')
FEATURES = tuple(itertools.chain.from_iterable(itertools.combinations(range(6), k) for k in range(4)))
assert len(FEATURES) == 42


def gate(op, a, b):
    if op == 'XOR': return a ^ b
    if op == 'AND': return a & b
    if op == 'OR': return a | b
    raise ValueError('unknown relation primitive')


def expr_mask(spec):
    """Only fixture generator calls this with hidden source specification."""
    a,b,c,d,left,right,root,neg = spec
    bitmasks = tuple(sum(1<<x for x in range(64) if x & (1<<i)) for i in range(6))
    val = gate(root,gate(left,bitmasks[a],bitmasks[b]),gate(right,bitmasks[c],bitmasks[d]))
    return (val ^ ALL64) if neg else val


def negative_mask(name):
    if name not in NEGATIVE: raise PermissionError('unregistered negative world')
    bits = []
    for x in range(64):
        n = x.bit_count()
        bit = {
            'parity6': n & 1,
            'majority6': int(n >= 4),
            'exactly_two': int(n == 2),
            'parity5_and_last': int(((x & 31).bit_count() & 1) and bool(x & 32)),
        }[name]
        bits.append(bit)
    return sum(v<<x for x,v in enumerate(bits))


def order_key(fix, label, x):
    if fix not in FIXTURES or type(label) is not str or not label.startswith(('fit:', 'transfer:', 'negative:')):
        raise PermissionError('AAI12S SCIENTIFIC FIRST USE DISARMED')
    return hashlib.sha256(f'AAI12S|{fix}|{label}|{x}'.encode('ascii')).digest()


def witness_pairs(fix,label):
    """Eight disjoint genuine one-bit public do transitions: 16 distinct x values."""
    ranking = sorted(range(64), key=lambda x: (order_key(fix,label,x),x))
    seen = set(); pairs = []
    for x in ranking:
        if x in seen: continue
        for bit in range(6):
            y=x^(1<<bit)
            if y not in seen:
                seen.update((x,y)); pairs.append((x,y)); break
        if len(pairs)==8: break
    if len(pairs)!=8 or len(seen)!=16 or any((a^b).bit_count()!=1 for a,b in pairs):
        raise AssertionError('source public-do budget drift')
    return tuple(pairs)


def observations(mask,pairs):
    return tuple((x,(mask>>x)&1) for a,b in pairs for x in (a,b))


def bitmask_for_var(i):
    return sum(1<<x for x in range(64) if x & (1<<i))


VARS = tuple(bitmask_for_var(i) for i in range(6))


def programs(composed):
    """Enumerate all well-typed compositional programs from source-free grammar.

    Duplicates are collapsed by extensionally identical 64-bit truth tables;
    cost and lexicographic tie-break do not inspect any target labels.
    """
    out = {}
    if composed:
        for binding in itertools.permutations(range(6),4):
            a,b,c,d = binding
            for left,right,root in itertools.product(OPS,repeat=3):
                expr=gate(root,gate(left,VARS[a],VARS[b]),gate(right,VARS[c],VARS[d]))
                for neg in (0,1):
                    table=expr ^ (ALL64 if neg else 0)
                    desc=(3+neg,*binding,OPS.index(left),OPS.index(right),OPS.index(root),neg)
                    if table not in out or desc < out[table]: out[table]=desc
    else:
        for a,b in itertools.permutations(range(6),2):
            for op in OPS:
                table=gate(op,VARS[a],VARS[b])
                for neg in (0,1):
                    truth=table ^ (ALL64 if neg else 0)
                    desc=(1+neg,a,b,OPS.index(op),neg)
                    if truth not in out or desc < out[truth]:out[truth]=desc
    return tuple(sorted(((desc,truth) for truth,desc in out.items())))


COMPOSED_PROGRAMS = programs(True)
SINGLE_PROGRAMS = programs(False)


def synth_fit(rows,composed):
    evidence=sum(1<<x for x,_ in rows)
    positives=sum(y<<x for x,y in rows)
    pool=COMPOSED_PROGRAMS if composed else SINGLE_PROGRAMS
    _,_,best=min((((truth ^ positives)&evidence).bit_count(),desc,truth) for desc,truth in pool)
    return best


def entropy(rows):
    if not rows:return 0.
    p=sum(y for _,y in rows)/len(rows)
    return 0. if p in (0.,1.) else -p*math.log2(p)-(1-p)*math.log2(1-p)


def id3(rows,remaining,depth):
    if not rows:return ('leaf',0)
    if depth==0 or not remaining or entropy(rows)==0:
        return ('leaf',int(sum(y for _,y in rows)*2>=len(rows)))
    base=entropy(rows); best_gain=-1.;best_col=None;best_parts=None
    for col in remaining:
        parts=([r for r in rows if not (r[0]>>col)&1],[r for r in rows if (r[0]>>col)&1])
        if not all(parts):continue
        gain=base-sum(len(p)*entropy(p) for p in parts)/len(rows)
        if gain>best_gain+1e-12:
            best_gain,best_col,best_parts=gain,col,parts
    if best_col is None:return ('leaf',int(sum(y for _,y in rows)*2>=len(rows)))
    rest=tuple(i for i in remaining if i!=best_col)
    return ('branch',best_col,id3(best_parts[0],rest,depth-1),id3(best_parts[1],rest,depth-1))


def features(x):return tuple(int(all((x>>i)&1 for i in ids)) for ids in FEATURES)


def logistic_fit(rows):
    """Full-batch 500 fixed-epoch squarefree degree<=3 logistic control."""
    train=[(features(x),y) for x,y in rows];w=[0.]*len(FEATURES)
    for _ in range(500):
        gradient=[0.]*len(w)
        for f,y in train:
            z=sum(v*wi for v,wi in zip(f,w));p=1/(1+math.exp(-max(-30.,min(30.,z))))
            e=p-y
            for i,val in enumerate(f):gradient[i]+=e*val
        for i in range(len(w)):
            w[i]-=.5*(gradient[i]/len(rows)+(.01*w[i] if i else 0.))
    return tuple(w)


def train_arm(name,rows):
    if name=='synth_composed':return synth_fit(rows,True)
    if name=='single_gate_only':return synth_fit(rows,False)
    if name=='depth6_fully_fitted_id3':return id3(rows,tuple(range(6)),6)
    if name=='degree3_fully_trained_logistic_500':return logistic_fit(rows)
    if name in ('hamming_knn5','recent_public_table'):return tuple(rows)
    raise ValueError('invalid arm')


def predict_arm(name,model,x):
    if name in ('synth_composed','single_gate_only'):return (model>>x)&1
    if name=='depth6_fully_fitted_id3':
        node=model
        while node[0]=='branch':node=node[2+((x>>node[1])&1)]
        return node[1]
    if name=='degree3_fully_trained_logistic_500':
        z=sum(v*wi for v,wi in zip(features(x),model))
        return int(z>=0.)
    if name=='hamming_knn5':
        near=sorted(enumerate(model),key=lambda kv:((kv[1][0]^x).bit_count(),kv[0]))[:5]
        return int(sum(row[1][1] for row in near)>=3)
    if name=='recent_public_table':
        exact=[y for a,y in model if a==x]
        return int(sum(exact)*2>=len(exact)) if exact else int(sum(y for _,y in model)*2>=len(model))
    raise ValueError('invalid arm')


def mean(items):return sum(items)/len(items) if items else 0.


def score_screen():
    if (len(FIT),len(TRANSFER),len(NEGATIVE),len(FIXTURES))!=(4,12,4,2):
        raise AssertionError('frozen world budget changed')
    results={category:{n:[] for n in ARMS} for category in ('transfer','fit','negative')}
    per_world={n:[] for n in ARMS}
    seconds={n:0. for n in ARMS}
    trace=[]
    for category,worlds in (('fit',FIT),('transfer',TRANSFER),('negative',NEGATIVE)):
        for widx,world in enumerate(worlds):
            truth=negative_mask(world) if category=='negative' else expr_mask(world)
            for fix in FIXTURES:
                label=f'{category}:{widx}'
                pairs=witness_pairs(fix,label)
                rows=observations(truth,pairs)
                used={x for x,_ in rows}
                test=tuple(x for x in range(64) if x not in used)
                if len(rows)!=16 or len(used)!=16 or len(test)!=48:
                    raise AssertionError('public budget or disjointness drift')
                for name in ARMS:
                    tick=time.perf_counter()
                    model=train_arm(name,rows)
                    guesses=tuple(predict_arm(name,model,x) for x in test)
                    seconds[name]+=time.perf_counter()-tick
                    correct=sum(pred==((truth>>x)&1) for x,pred in zip(test,guesses))
                    results[category][name].extend(int(pred==((truth>>x)&1)) for x,pred in zip(test,guesses))
                    trace.append((category,widx,fix,name,correct,guesses))
                    if category=='transfer':per_world[name].append((widx,correct/48))
    summary={category:{name:round(mean(vals),9) for name,vals in by_arm.items()} for category,by_arm in results.items()}
    conventional=tuple(n for n in ARMS if n not in ('synth_composed','single_gate_only'))
    best=max(conventional,key=lambda n:summary['transfer'][n]);candidate='synth_composed'
    world_85=sum(mean([acc for i,acc in per_world[candidate] if i==idx])>=.85 for idx in range(len(TRANSFER)))
    checks={
        'transfer_gain_0_05':summary['transfer'][candidate]>=summary['transfer'][best]+.05-1e-10,
        'same_input_single_gate_gain_0_10':summary['transfer'][candidate]>=summary['transfer']['single_gate_only']+.10-1e-10,
        'at_least_10_of_12_transfer_worlds_above_0_85':world_85>=10,
        'non_grammar_drop_at_most_0_02':summary['negative'][candidate]>=max(summary['negative'][n] for n in conventional)-.02-1e-10,
        'familiar_drop_at_most_0_02':summary['fit'][candidate]>=max(summary['fit'][n] for n in conventional)-.02-1e-10,
        'full_fit_predict_wall_ratio_at_most_10':seconds[candidate]<=10*min(seconds[n] for n in conventional),
    }
    return {
        'schema':'yggdrasil.aai12s.source-dev.v1',
        'classification':'DEV_ADMITTED_SCIENCE_UNVERIFIED' if all(checks.values()) else 'DEV_NO_GO_NO_SCIENCE',
        'accuracy':summary,'transfer_best_conventional':best,
        'candidate_minus_best_transfer_accuracy':round(summary['transfer'][candidate]-summary['transfer'][best],9),
        'worlds_above_0_85':world_85,'frozen_checks':checks,
        'source_fit_predict_seconds':{n:round(s,6) for n,s in seconds.items()},
        'total_source_transfer_test_cases_per_arm':1152,
        'source_only':True,'scientific_cohorts_consumed':0,
        'trace_sha256':hashlib.sha256(json.dumps(trace,separators=(',',':')).encode()).hexdigest(),
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source-dev',action='store_true')
    ap.add_argument('--primary',action='store_true')
    args=ap.parse_args()
    if args.primary:ap.error('AAI12S SCIENTIFIC FIRST USE DISARMED')
    if not args.source_dev:ap.error('only the frozen --source-dev source-only fixture is permitted')
    print('AAI12S_DEV='+json.dumps(score_screen(),sort_keys=True),flush=True)

if __name__=='__main__':main()
