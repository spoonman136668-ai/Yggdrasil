"""NCI-NOVEL-02 research-only public-variable relevance and causal forecasts.

Receives only source-declared public tuples and observed action consequences. Never
imports the source/evaluator module, owner checkpoints or Yggdrasil runtime.
"""
from __future__ import annotations
import hashlib
import json
import math
import zlib
from collections import defaultdict
from itertools import combinations

NOISE = .06
STAGES = ('t', 'y')
GATING_SUPPORT = .90
GATING_RECENT_BRIER = .15
MIN_WITNESSES = 32


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('ascii')


def digest(blob):
    return hashlib.sha256(blob).hexdigest()


def bit(value):
    if type(value) is not int or value not in (0, 1):
        raise ValueError('NOT_BINARY_PUBLIC_VALUE')
    return value


def feature_index(features):
    return sum(bit(x) << i for i, x in enumerate(features))


def functions(n):
    """Signature search is canonical, deduped, and contains no evaluator truth."""
    if n not in (5, 6):
        raise ValueError('UNSUPPORTED_PUBLIC_FEATURE_COUNT')
    count = 1 << n
    basis = [sum(((j >> i) & 1) << j for j in range(count)) for i in range(n)]
    universe = (1 << count) - 1
    unique = {}

    def add(signature, cost):
        for value in (signature, signature ^ universe):
            unique[value] = min(cost, unique.get(value, 100))

    add(0, 0)
    for f in basis:
        add(f, 1)
    for length in range(2, 5):
        for indices in combinations(range(n), length):
            mask = 0
            for j in indices:
                mask ^= basis[j]
            add(mask, length - 1)
    for i, j in combinations(range(n), 2):
        for op in (basis[i] & basis[j], basis[i] | basis[j]):
            add(op, 2)
            for third in range(n):
                if third not in (i, j):
                    add(op ^ basis[third], 3)
    def used(mask, i):
        return any((mask >> x) & 1 != (mask >> (x ^ (1 << i))) & 1 for x in range(count))
    return [(mask, cost, used(mask, 3)) for mask, cost in sorted(unique.items())]

TEMPLATES = {n: functions(n) for n in (5, 6)}


class GrammarPosterior:
    def __init__(self, stage, kind):
        if kind not in ('GATED_MAP', 'BMA', 'NO_X3'):
            raise ValueError('GRAMMAR_KIND')
        self.stage, self.kind = stage, kind
        n = 5 if stage == 't' else 6
        self.template = tuple((mask,cost,uses) for mask,cost,uses in TEMPLATES[n]
                              if kind != 'NO_X3' or not uses)
        self.scores = [-.55 * cost for _, cost, _ in self.template]
        self.errors=[]
        self.count=0
        self.seen=set()

    def probabilities(self):
        m=max(self.scores)
        weights=[math.exp(s-m) for s in self.scores]
        mass=sum(weights)
        return [w/mass for w in weights]

    def evidence(self):
        post=self.probabilities()
        support=sum(p for p,(_,_,uses) in zip(post,self.template) if uses)
        # x3 is at position 3: compare every other public coordinate, not x3.
        paired=set()
        for ctx in self.seen:
            if ctx[3] == 0:
                alternate=(*ctx[:3], 1, *ctx[4:])
                if alternate in self.seen:
                    paired.add(ctx[:3]+ctx[4:])
        recent=sum(self.errors)/len(self.errors) if self.errors else None
        identified=(self.kind != 'NO_X3' and self.count>=MIN_WITNESSES
                    and support>=GATING_SUPPORT and len(paired)>=2
                    and recent is not None and recent<=GATING_RECENT_BRIER)
        return {'factor4_support':support,'paired_public_contrasts':len(paired),
                'recent_brier':recent,'identified':identified,'witnesses':self.count}

    def forecast(self, features):
        ix=feature_index(features)
        probs=self.probabilities()
        bma=sum(p * ((1-NOISE) if (mask >> ix)&1 else NOISE)
                for p,(mask,_,_) in zip(probs,self.template))
        if self.kind!='GATED_MAP' or not self.evidence()['identified']:
            return bma
        j=max(range(len(probs)),key=lambda i:(probs[i],-self.template[i][1],-self.template[i][0]))
        return (1-NOISE) if (self.template[j][0] >> ix)&1 else NOISE

    def update(self, features, outcome, forecast):
        ix=feature_index(features)
        bit(outcome)
        self.seen.add(tuple(features))
        self.errors.append((forecast-outcome)**2)
        if len(self.errors)>24:self.errors.pop(0)
        self.count+=1
        ok=math.log(1-NOISE)
        bad=math.log(NOISE)
        for i,(mask,_,_) in enumerate(self.template):
            self.scores[i] += ok if ((mask >> ix)&1)==outcome else bad

    def snapshot(self):
        return {'kind':self.kind,'stage':self.stage,'scores':[s.hex() for s in self.scores],
                'errors':[e.hex() for e in self.errors],'count':self.count,
                'seen':sorted(map(list,self.seen))}

    @classmethod
    def restore(cls, state):
        model=cls(state['stage'],state['kind'])
        if len(state['scores'])!=len(model.scores):raise ValueError('GRAMMAR_DRIFT')
        model.scores=[float.fromhex(s) for s in state['scores']]
        model.errors=[float.fromhex(e) for e in state['errors']]
        model.count=state['count'];model.seen={tuple(x) for x in state['seen']}
        return model


class BetaControl:
    def __init__(self, stage, kind):
        if kind not in ('FULL','BACKOFF','RECURRENT'):raise ValueError('BETA_KIND')
        self.stage,self.kind=stage,kind
        self.counts=defaultdict(lambda:[0,0])
        self.previous=0
        self.count=0

    def key(self,features):
        if self.kind=='RECURRENT':return tuple(features)+(self.previous,)
        return tuple(features)

    def forecast(self,features):
        if self.kind=='BACKOFF':
            out=[]; n=len(features)
            # Fits every subset, including the full context, on the same tape.
            for mask in range(1<<n):
                key=(mask, tuple(features[j] for j in range(n) if mask>>j&1))
                neg,pos=self.counts.get(key,(0,0))
                total=neg+pos
                weight=(total+1)/(total+4) * 1/(2**(mask.bit_count()))
                out.append(((pos+.5)/(total+1),weight))
            return sum(p*w for p,w in out)/sum(w for _,w in out)
        neg,pos=self.counts.get(self.key(features),(0,0))
        return (pos+.5)/(neg+pos+1)

    def update(self,features,outcome,forecast):
        if self.kind=='BACKOFF':
            n=len(features)
            for mask in range(1<<n):
                key=(mask,tuple(features[j] for j in range(n) if mask>>j&1))
                self.counts[key][outcome]+=1
        else:self.counts[self.key(features)][outcome]+=1
        self.count+=1
        self.previous=outcome

    def evidence(self):
        return {'factor4_support':None,'paired_public_contrasts':None,
                'recent_brier':None,'identified':False,'witnesses':self.count}

    def snapshot(self):
        return {'kind':self.kind,'stage':self.stage,'previous':self.previous,
                'count':self.count,'counts':[(repr(k),v) for k,v in sorted(self.counts.items())]}

    @classmethod
    def restore(cls,state):
        import ast
        model=cls(state['stage'],state['kind'])
        model.count=state['count'];model.previous=state['previous']
        for key,counts in state['counts']:
            value=ast.literal_eval(key)
            if type(value) is not tuple:raise ValueError('BAD_CONTEXT_KEY')
            model.counts[value]=counts
        return model


class ResearchArm:
    def __init__(self, kind):
        if kind not in ('GATED_MAP','BMA','NO_X3','FULL','BACKOFF','RECURRENT','FROZEN_OLD'):
            raise ValueError('UNKNOWN_ARM')
        self.kind=kind
        self.models={}
        self.receipts={}
        self.event_count=0
        self.root='0'*64

    def component(self,ids,stage):
        ids=tuple(ids)
        if len(ids)!=6 or len(set(ids))!=6 or any(type(x) is not str or not x for x in ids):
            raise ValueError('PUBLIC_VARIABLE_IDENTITIES')
        if stage not in STAGES:raise ValueError('INVALID_STAGE')
        key=(ids,stage)
        if key not in self.models:
            model_kind='BMA' if self.kind=='FROZEN_OLD' else self.kind
            self.models[key]=(GrammarPosterior(stage,model_kind)
                              if model_kind in ('GATED_MAP','BMA','NO_X3')
                              else BetaControl(stage,model_kind))
        return self.models[key]

    def predict(self,ids,stage,features):
        return self.component(ids,stage).forecast(features)

    def admit(self,ids,stage,features,outcome,witness):
        bit(outcome)
        if not (type(witness) is str and len(witness)==64 and all(c in '0123456789abcdef' for c in witness)):
            raise ValueError('INVALID_WITNESS')
        event=digest(canonical([list(ids),stage,list(features),outcome]))
        previous=self.receipts.get(witness)
        if previous is not None:
            if previous!=event:raise ValueError('WITNESS_REBOUND')
            return 'DUPLICATE'
        if self.kind=='FROZEN_OLD' and str(ids[0]).startswith('new.'):
            # Control never learns new material and never changes old state.
            return 'FROZEN_SKIP'
        model=self.component(ids,stage)
        before=model.forecast(features)
        model.update(features,outcome,before)
        self.receipts[witness]=event
        self.event_count+=1
        self.root=digest((self.root+witness+event).encode('ascii'))
        return 'ADMITTED'

    def old_digest(self,old_ids):
        old={stage:self.component(old_ids,stage).snapshot() for stage in STAGES}
        return digest(canonical(old))

    def checkpoint(self):
        obj={'schema':'nci-novel02.additive-source-free-research.v1',
             'kind':self.kind,'root':self.root,'event_count':self.event_count,
             'models':[{ 'ids':list(ids), 'stage':stage, 'state':model.snapshot()}
                       for (ids,stage),model in sorted(self.models.items())],
             'receipts':sorted([k,v] for k,v in self.receipts.items()),
             'native_accepted':False,'source_mode':'SELF_AUTHORED_SYNTHETIC_DEV'}
        raw=b'NC2Z' + zlib.compress(canonical(obj),level=9)
        if len(raw)>65536:raise ValueError('RESEARCH_CHECKPOINT_CAP_EXCEEDED')
        return raw

    @classmethod
    def restore(cls,raw,expected_sha):
        if digest(raw)!=expected_sha:raise ValueError('CHECKPOINT_SHA_MISMATCH')
        if not raw.startswith(b'NC2Z') or len(raw)>65536:
            raise ValueError('CHECKPOINT_ENVELOPE')
        decoder=zlib.decompressobj()
        decoded=decoder.decompress(raw[4:], max_length=2_000_000)
        if not decoder.eof or decoder.unused_data or decoder.unconsumed_tail or len(decoded)>2_000_000:
            raise ValueError('CHECKPOINT_DECODE_LIMIT')
        data=json.loads(decoded)
        if (set(data)!={'schema','kind','root','event_count','models','receipts',
                       'native_accepted','source_mode'} or
            data['schema']!='nci-novel02.additive-source-free-research.v1' or
            data['native_accepted'] is not False or
            data['source_mode']!='SELF_AUTHORED_SYNTHETIC_DEV'):
            raise ValueError('CHECKPOINT_SCHEMA')
        arm=cls(data['kind']);arm.root=data['root'];arm.event_count=data['event_count']
        arm.receipts=dict(data['receipts'])
        for row in data['models']:
            ids=tuple(row['ids']);stage=row['stage']
            obj=row['state']
            model=GrammarPosterior.restore(obj) if obj['kind'] in ('GATED_MAP','BMA','NO_X3') else BetaControl.restore(obj)
            if obj['stage']!=stage:raise ValueError('RESTORE_STAGE_DRIFT')
            arm.models[(ids,stage)]=model
        if len(arm.receipts)!=arm.event_count or arm.checkpoint()!=raw:
            raise ValueError('CHECKPOINT_RESTORE_DRIFT')
        return arm
