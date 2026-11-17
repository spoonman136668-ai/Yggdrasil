"""Source-blind active interventions for WSP137. Public typed x and actual paid
observations only; never imports the source, score or 7,062-function oracle.
The downstream numeric representation/fit/readout is EXACT pinned WSP135.
"""
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import SimpleNamespace
import json, sys

PATH=Path(__file__).resolve().parents[1] / 'WSP-135' / 'learner.py'
SPEC=spec_from_file_location('_wsp137_pinned_wsp135_learner',PATH)
N=module_from_spec(SPEC)
sys.modules[SPEC.name]=N
SPEC.loader.exec_module(N)

SCHEMA='wsp137.active-sourceblind-latent.v1'
def canon(o):return json.dumps(o,sort_keys=True,separators=(',',':'))
def digest(o):return sha256(canon(o).encode()).hexdigest()
def fixed_schedule():return N.schedule()

def common_held():
    not_fixed=tuple(x for x in range(64) if x not in set(N.schedule()))
    if len(not_fixed)!=32:raise AssertionError('WSP137_FIXED_ACTIONS_NOT_32')
    return frozenset(sorted(not_fixed,key=lambda x:(sha256(('WSP137|COMMONHELD|'+str(x)).encode()).digest(),x))[:16])
def available_pool():
    p=frozenset(range(64))-common_held()
    if len(p)!=48 or not set(fixed_schedule())<=p:raise AssertionError('WSP137_SOURCE_BLIND_POOL_BAD')
    return p

def candidate_preference():
    return tuple(sorted(range(len(N.templates())),
      key=lambda i:(sha256(('WSP137|PROBE|'+str(i)).encode()).digest(),i)))

class ActivePolicy:
    def __init__(self):
        bank=N.templates()
        self.bank=bank
        self.ranked=candidate_preference()
        self.valid=bytearray([1])*len(bank)
        self.lut=[[-1]*16 for _ in bank]
        self.events=[]
        self.pending=None
    def choose(self,legal):
        if len(self.events)>=32:return None
        used={x for x,y in self.events}
        pool=[x for x in legal if x not in used]
        if not pool:raise ValueError('WSP137_NO_PAID_ACTION_REMAINING')
        if len(self.events)<4:
            pick=fixed_schedule()[len(self.events)]
            if pick not in pool:raise ValueError('WSP137_MISSING_ORIGINAL_FOUR_PROBES')
        else:
            selected=[]
            for i in self.ranked:
                if self.valid[i]:
                    selected.append(i)
                    if len(selected)>=256:break
            if not selected:
                order=[x for x in fixed_schedule() if x in pool]
                pick=order[0] if order else min(pool)
            else:
                choices=[]
                for x in pool:
                    pos=neg=unknown=0
                    for i in selected:
                        val=self.lut[i][self.bank[i][x]]
                        if val==1:pos+=1
                        elif val==0:neg+=1
                        else:unknown+=1
                    choices.append((min(pos,neg),unknown,-x,x))
                pick=max(choices)[-1]
        self.pending=pick
        return pick
    def observe(self,x,y):
        if x!=self.pending or x in {v for v,w in self.events} or len(self.events)>=32 or type(y) is not int or y not in (0,1):
            raise ValueError('WSP137_ACTIVE_UNEXPECTED_EFFECT_OR_REPLAY')
        for i,valid in enumerate(self.valid):
            if not valid:continue
            row=self.lut[i]
            c=self.bank[i][x]
            old=row[c]
            if old>=0 and old!=y:self.valid[i]=0
            else:row[c]=y
        self.events.append((x,y))
        self.pending=None

class DirectArm:
    def __init__(self,policy):
        if policy not in ('fixed','active'):raise ValueError('WSP137_POLICY_INVALID')
        self.policy=policy
        self.states={}
    def _state(self,view,create=False):
        st=self.states.get(view.law_id)
        if st is None and create:
            if view.cohort!='probe':raise PermissionError('WSP137_ZERO_CALL_TRANSFER_TRAIN')
            st={'fingerprint':view.fingerprint(),'receipt':digest([view.fingerprint(),'begin']),'events':[],'chosen':[]}
            if self.policy=='active':st['chooser']=ActivePolicy()
            self.states[view.law_id]=st
        if st is not None and view.cohort=='probe' and st['fingerprint']!=view.fingerprint():
            raise ValueError('WSP137_VIEW_CHANGED')
        return st
    def choose(self,view,legal):
        if view.cohort!='probe':raise PermissionError('WSP137_CANNOT_PROBE_TRANSFER')
        st=self._state(view,True)
        if len(st['events'])>=32:return None
        if self.policy=='fixed':
            x=fixed_schedule()[len(st['events'])]
        else:x=st['chooser'].choose(legal)
        if x not in legal or x in {row[2] for row in st['events']}:
            raise ValueError('WSP137_QUERY_NOT_LEGAL_OR_REPLAY')
        return x
    def observe(self,view,e,legal):
        st=self._state(view,True)
        if (view.cohort!='probe' or len(st['events'])>=32 or
            type(e.law_id) is not int or e.law_id!=view.law_id or
            type(e.input) is not int or type(e.subject) is not int or
            e.input not in legal or e.subject!=view.subject(e.input) or
            type(e.effect) is not int or e.effect not in (0,1) or
            any(row[2]==e.input for row in st['events'])):
            raise ValueError('WSP137_INVALID_SOURCE_EVIDENCE')
        if self.policy=='fixed' and e.input!=fixed_schedule()[len(st['events'])]:
            raise ValueError('WSP137_FIXED_ACTION_DRIFT')
        if self.policy=='active' and st['chooser'].pending!=e.input:
            raise ValueError('WSP137_ACTIVE_ACTION_DRIFT')
        row=[e.law_id,e.subject,e.input,e.effect]
        if digest([st['receipt'],row])!=e.receipt:
            raise ValueError('WSP137_BAD_SOURCE_RECEIPT')
        if self.policy=='active':st['chooser'].observe(e.input,e.effect)
        st['events'].append(row)
        st['receipt']=e.receipt
        if len(st['events'])==32:
            st['chosen']=N.fit(tuple((x,y) for law,sub,x,y in st['events']))
    def infer(self,view,subject):
        st=self._state(view)
        if st is None or len(st['events'])!=32:return None
        return N.predict(st['chosen'],view.input(subject))
    def snapshot(self):
        public={}
        for law,st in sorted(self.states.items()):
            public[str(law)]={k:st[k] for k in ('fingerprint','receipt','events','chosen')}
        body={'schema':SCHEMA,'policy':self.policy,'states':public}
        return canon({'payload':body,'sha256':digest(body)})
    @classmethod
    def restore(cls,snapshot,views):
        try:
            raw=json.loads(snapshot)
            body=raw['payload']
            if body['schema']!=SCHEMA or raw['sha256']!=digest(body):
                raise ValueError('WSP137_BAD_SNAPSHOT_SHA')
            obj=cls(body['policy'])
            for key in sorted(body['states'],key=int):
                if str(int(key))!=key or int(key) not in views:raise ValueError('WSP137_FORGED_LAW')
                v=views[int(key)]
                stored=body['states'][key]
                if stored['fingerprint']!=v.fingerprint():raise ValueError('WSP137_FORGED_VIEW')
                for row in stored['events']:
                    x=obj.choose(v,available_pool())
                    if x!=row[2]:raise ValueError('WSP137_QUERY_ORDER_FORGED')
                    st=obj._state(v,True)
                    receipt=digest([st['receipt'],row])
                    e=SimpleNamespace(law_id=row[0],subject=row[1],input=row[2],effect=row[3],receipt=receipt)
                    obj.observe(v,e,available_pool())
                actual=obj.states[int(key)]
                if {k:actual[k] for k in ('fingerprint','receipt','events','chosen')}!=stored:
                    raise ValueError('WSP137_FORGED_NUMERIC_STATE')
            if obj.snapshot()!=snapshot:raise ValueError('WSP137_NONCANONICAL_SNAPSHOT')
            return obj
        except (TypeError,KeyError,IndexError,AttributeError) as e:
            raise ValueError('WSP137_MALFORMED_SNAPSHOT') from e
