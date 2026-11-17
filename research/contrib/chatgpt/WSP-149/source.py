"""WSP-149 independent prospective source-safe custodian only. Never import in learners."""
from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
import json, random

FIT=frozenset(range(310000,310016))
NOVEL=frozenset(range(311000,311032))
KNOWN=frozenset(range(312000,312008))
OFF=frozenset(range(313000,313008))
TRANSFER=frozenset(range(314000,314008))  # cold-relabel only
ALLOWED=FIT|NOVEL|KNOWN|OFF|TRANSFER
PROTECTED=frozenset().union(*(frozenset(range(k,k+64)) for k in (310800,311800,312800,313800,314800)))
OPS=("AND","OR","XOR","XNOR")
# WSP149: all 64 typed action coordinates are legal before post-commit query selection.

def canon(v):return json.dumps(v,sort_keys=True,separators=(',',':'))
def digest(v):return sha256(canon(v).encode()).hexdigest()
def _guard(seed):
    if type(seed) is not int or seed not in ALLOWED or seed in PROTECTED:
        raise PermissionError("WSP149_SOURCE_FIRST_USE_OR_UNREGISTERED_DENIED")
def _base(seed): return 310000+seed-314000 if seed in TRANSFER else seed
def _kind(seed):
    if seed in FIT:return 'FIT'
    if seed in NOVEL:return 'NOVEL'
    if seed in KNOWN:return 'KNOWN'
    if seed in OFF:return 'OFF'
    raise PermissionError('WSP149_BAD_KIND')
def _rng(kind,seed):
    return random.Random(int.from_bytes(sha256(('WSP149|SOURCE|'+kind+'|'+str(seed)).encode()).digest(),'big'))
def _gate(op,a,b):
    if op=='AND':return a&b
    if op=='OR':return a|b
    if op=='XOR':return a^b
    if op=='XNOR':return 1^(a^b)
    raise AssertionError('BAD_OP')
@lru_cache(maxsize=100)
def _truth(seed):
    _guard(seed)
    base=_base(seed)
    kind=_kind(base)
    rng=_rng(kind,base)
    p=list(range(6));rng.shuffle(p)
    out=[]
    for x in range(64):
        b=tuple((x>>i)&1 for i in range(6))
        if kind=='FIT':
            v=(b[p[0]]&b[p[1]])^(b[p[2]]|b[p[3]])^b[p[4]]^(base&1)
        elif kind=='NOVEL':
            # Independent held generator: unseen conditional-plus-nested
            # interaction, with permuted roles, no evaluator labels in learner.
            v=(((b[p[0]]^b[p[1]])&(b[p[2]]|b[p[3]]))^
                ((b[p[4]]&b[p[5]]) if b[p[0]] else (b[p[1]]^b[p[5]]))^
                (base&1))
        elif kind=='KNOWN':
            v=(b[p[0]]&b[p[1]])^b[p[2]]^(base&1)
        elif kind=='OFF':
            v=rng.randrange(2)
        else:raise PermissionError('WSP149_BAD_KIND')
        out.append(v)
    return tuple(out)

@dataclass(frozen=True)
class View:
    law_id:int
    cohort:str
    records:tuple
    legal:frozenset
    by_x:dict
    by_subject:dict
    def subject(self,x):
        if type(x) is not int or x not in self.by_x:raise ValueError('BAD_TYPED_ACTION')
        return self.by_x[x]
    def input(self,subject):
        if type(subject) is not int or subject not in self.by_subject:raise ValueError('BAD_ACTION')
        return self.by_subject[subject]
    def fingerprint(self): return digest([self.law_id,self.cohort,self.records])
@lru_cache(maxsize=80)
def world(seed):
    _guard(seed)
    base=_base(seed)
    law=int.from_bytes(sha256(('WSP149|LAW|'+str(base)).encode()).digest()[:8],'big')
    rr=random.Random(seed)
    ids=rr.sample(range(seed*1000,seed*1000+1000),64)
    records=[(ids[x],x) for x in range(64)]
    rr.shuffle(records)
    cohort='transfer' if seed in TRANSFER else 'probe'
    return View(law,cohort,tuple(records),frozenset(ids) if cohort=='probe' else frozenset(),{x:s for s,x in records},{s:x for s,x in records})
@dataclass(frozen=True)
class Evidence:
    law_id:int
    subject:int
    input:int
    effect:int
    receipt:str
class Custodian:
    def __init__(self,view,seed):
        _guard(seed)
        if type(view) is not View or view is not world(seed):raise PermissionError('SOURCE_VIEW_MISMATCH')
        self.view=view
        self.truth=_truth(seed)  # PRIVATE evaluator-owned; never handed to policy
        self.budget=0 if view.cohort=='transfer' else 32
        self.receipt=digest([view.fingerprint(),'begin'])
        self.events=[]
        self.seen=set()
        self.scored=False
    def query(self,subject):
        if (self.scored or len(self.events)>=self.budget or type(subject) is not int
            or subject not in self.view.legal or subject in self.seen):
            raise PermissionError('WSP149_UNAUTHORIZED_EFFECT')
        x=self.view.input(subject)
        row=[self.view.law_id,subject,x,self.truth[x]]
        self.receipt=digest([self.receipt,row])
        self.seen.add(subject)
        self.events.append(row)
        return Evidence(*row,self.receipt)
    def held(self):return tuple((s,x) for s,x in self.view.records if s not in self.seen)
    def score_once(self,pred):
        if self.scored or len(self.events)!=self.budget or set(pred)!={s for s,x in self.held()}:
            raise PermissionError('WSP149_SCORE_REPLAY_BUDGET_OR_MISSING')
        correct=wrong=abstained=0
        for s,x in self.held():
            y=pred[s]
            if y is None:abstained+=1
            elif type(y) is not int or y not in (0,1):raise ValueError('BAD_PRED')
            elif y==self.truth[x]:correct+=1
            else:wrong+=1
        self.scored=True
        return {'correct':correct,'wrong_confident':wrong,'abstained':abstained,'held':len(pred),'source_calls':self.budget}

def open_original(seed):raise PermissionError('WSP149_ORIGINAL_SCIENCE_FIRST_USE_DENIED')

class OwnerPostCommit:
    """Source-private post-prediction evaluator; cannot score during acquisition.

    Every arm's 64 public typed-state predictions must be finalized and supplied
    as immutable tuples BEFORE the owner resolves even one held query location.
    """
    POLICIES=frozenset(('fixed','random','adaptive'))
    def __init__(self,view,seed,paid_arms):
        _guard(seed)
        if type(view) is not View or view is not world(seed):
            raise PermissionError('WSP149_OWNER_VIEW_MISMATCH')
        if type(paid_arms) is not dict or set(paid_arms)!=self.POLICIES:
            raise PermissionError('WSP149_OWNER_MISSING_ARM')
        self.view=view
        self.seed=seed
        self.paid_arms=paid_arms
        self.scored=False
    def score_once(self,sealed):
        if self.scored or type(sealed) is not dict or set(sealed)!=self.POLICIES:
            raise PermissionError('WSP149_OWNER_SCORE_REPLAY_OR_UNSEALED')
        paid=set()
        prior_names=None
        canonical={}
        warm=tuple(sorted(range(64),key=lambda x:(
            sha256(('WSP135|ACTIONS|'+str(x)).encode()).digest(),x))[:20])
        for name in sorted(self.POLICIES):
            cust=self.paid_arms[name]
            if (type(cust) is not Custodian or cust.view is not self.view
                or cust.scored or cust.budget!=32 or len(cust.events)!=32
                or len(cust.seen)!=32 or cust.truth!=_truth(self.seed)):
                raise PermissionError('WSP149_OWNER_UNQUALIFIED_EFFECT_CUSTODY')
            xs=tuple(row[2] for row in cust.events)
            if xs[:20]!=warm or len(set(xs))!=32:
                raise PermissionError('WSP149_OWNER_MISSING_COMMON_WARM')
            paid.update(xs)
            models=sealed[name]
            if type(models) is not dict or not models or (
                prior_names is not None and set(models)!=prior_names):
                raise PermissionError('WSP149_OWNER_UNQUALIFIED_MODEL_SET')
            prior_names=set(models)
            canonical[name]={}
            for model,predictions in models.items():
                if (type(model) is not str or not model or type(predictions) is not tuple
                    or len(predictions)!=64 or
                    any(x is not None and (type(x) is not int or x not in (0,1))
                        for x in predictions)):
                    raise PermissionError('WSP149_OWNER_MISSING_FINAL_64_PREDICTIONS')
                canonical[name][model]=predictions
        unseen=frozenset(range(64))-paid
        if len(unseen)<8:raise AssertionError('WSP149_OWNER_HELD_UNION_TOO_LARGE')
        law=self.view.law_id
        held=tuple(sorted(unseen,key=lambda x:(
            sha256(('WSP149|HELD|'+str(law)+'|'+str(x)).encode()).digest(),x))[:8])
        truth=_truth(self.seed)
        scores={}
        for name in sorted(self.POLICIES):
            cust=self.paid_arms[name]
            held32=tuple(x for x in range(64) if x not in set(row[2] for row in cust.events))
            scores[name]={}
            for model,output in canonical[name].items():
                def tally(contexts):
                    correct=wrong=abstained=0
                    for x in contexts:
                        y=output[x]
                        if y is None:abstained+=1
                        elif y==truth[x]:correct+=1
                        else:wrong+=1
                    return {'correct':correct,'wrong_confident':wrong,
                            'abstained':abstained,'held':len(contexts)}
                scores[name][model]={'paired':tally(held),'arm_unseen32':tally(held32)}
            cust.scored=True
        self.scored=True
        return {'held_queries_after_all_output_seals':held,
                'held_sha256':digest([law,held]),
                'prediction_seal_sha256':digest(canonical),
                'source_private_scores':scores,
                'source_paid_events':sum(len(c.events) for c in self.paid_arms.values()),
                'source_effect_receipts_sha256':digest([
                    [n,self.paid_arms[n].receipt] for n in sorted(self.POLICIES)])}
