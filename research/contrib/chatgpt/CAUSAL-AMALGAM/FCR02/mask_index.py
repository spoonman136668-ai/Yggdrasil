"""FCR02-DEV stage-separate prequential mask selector, public fixture only.

This is an opt-in research readout over already witnessed binary episodes; it
has NO source authority, no native or owner checkpoint mutation, and no claim
of scientific learning. No phase or heldout information reaches the learner.
"""
from __future__ import annotations

from hashlib import sha256
from itertools import combinations
import json

Q=1000000
CAP=1152
SCHEMA='yggdrasil.fcr02.stage-mask-index.development.v1'


def _require(v,tag):
    if not v: raise ValueError('FCR02_'+tag)


def _bit(v):
    _require(type(v) is int and v in (0,1),'PUBLIC_BIT'); return v


def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode('ascii')


def digest(x): return sha256(x).hexdigest()


def _prob(cell):
    a,b=cell
    return ((2*b+1)*Q)//(2*(a+b+1))


def _masks(n):
    return tuple(x for size in range(n+1) for x in combinations(range(n),size))


class StageBank:
    def __init__(self, kind):
        _require(kind in ('transition','reward'),'KIND')
        self.kind=kind
        self.masks=_masks(1 if kind=='transition' else 3)
        self.counts=[{} for _ in self.masks]
        self.loss=[0]*len(self.masks)
        self.events=0

    def _features(self, public):
        if self.kind=='transition':
            c,x1=public
            return (x1,), (c,)
        c,x1,s2,x2=public
        return (x2,), (c,x1,s2)

    def _key(self,public,mask):
        mandatory,extras=self._features(public)
        for v in mandatory+extras: _bit(v)
        return mandatory+tuple(extras[i] for i in mask)

    def _predicts(self,public):
        return [_prob(self.counts[i].get(self._key(public,mask),(0,0)))
                for i,mask in enumerate(self.masks)]

    def choice(self):
        return min(range(len(self.masks)),key=lambda i:(self.loss[i],len(self.masks[i]),self.masks[i]))

    def forecast(self,public):
        return self._predicts(public)[self.choice()]

    def observe(self,public,outcome):
        y=_bit(outcome)
        # Forecast every candidate before updating any count on the new row.
        probabilities=self._predicts(public)
        for i,mask in enumerate(self.masks):
            error=probabilities[i]-y*Q
            self.loss[i]+=(error*error)//Q
            cell=self.counts[i].setdefault(self._key(public,mask),[0,0])
            _require(sum(cell)<CAP,'COUNT_CAP')
            cell[y]+=1
        self.events+=1
        _require(self.events<=CAP,'EPISODE_CAP')

    def state(self):
        return {'kind':self.kind,'loss':self.loss,'events':self.events,
                'counts':[[[list(key),list(value)] for key,value in sorted(bank.items())]
                          for bank in self.counts]}


class StageMaskIndex:
    def __init__(self):
        self.transition=StageBank('transition')
        self.reward=StageBank('reward')
        self.ids=set()
        self._ledger=[]
        self._sealed=False

    def forecast_transition(self,context,first):
        _require(not self._sealed,'SEALED')
        return self.transition.forecast((_bit(context),_bit(first)))

    def forecast_reward(self,context,first,state,second):
        _require(not self._sealed,'SEALED')
        return self.reward.forecast(tuple(map(_bit,(context,first,state,second))))

    def observe_admitted_fixture(self,identifier,context,first,state,second,reward):
        """Only a caller with external native admission evidence could use this in production.

        Here admission is a source-free fixture assertion, not authenticated.
        """
        _require(not self._sealed,'SEALED')
        _require(type(identifier) is str and len(identifier)==64 and
                 set(identifier)<=set('0123456789abcdef'),'ID')
        row=tuple(map(_bit,(context,first,state,second,reward)))
        if identifier in self.ids:
            _require(False,'DUPLICATE_OR_CONFLICT')
        _require(len(self._ledger)<CAP,'LEDGER_CAP')
        # External source admission is NOT asserted by this function.
        self.transition.observe((row[0],row[1]),row[2])
        self.reward.observe(row[:4],row[4])
        self._ledger.append((identifier,*row))
        self.ids.add(identifier)

    def checkpoint(self,source_pin):
        _require(type(source_pin) is str and len(source_pin)==64 and
                 set(source_pin)<=set('0123456789abcdef'),'SOURCE_PIN')
        return canonical({'schema':SCHEMA,'source_pin':source_pin,
                          'ledger_digest':digest(canonical(self._ledger)),
                          'records':len(self._ledger),'transition':self.transition.state(),
                          'reward':self.reward.state(),'source_mode':'engineering_fixture_only',
                          'accepted_native':False,'scientific_pass':False})

    @classmethod
    def restore(cls,ledger,raw,sha,source_pin):
        _require(type(raw) is bytes and digest(raw)==sha,'COLD_SHA')
        def unique(pairs):
            d={}
            for k,v in pairs:
                _require(k not in d,'DUPLICATE_JSON_KEY');d[k]=v
            return d
        try: doc=json.loads(raw.decode('ascii'),object_pairs_hook=unique)
        except (ValueError,UnicodeError) as exc: raise ValueError('FCR02_BAD_JSON') from exc
        _require(type(doc) is dict and doc.get('schema')==SCHEMA
                 and doc.get('source_pin')==source_pin
                 and doc.get('source_mode')=='engineering_fixture_only'
                 and doc.get('accepted_native') is False
                 and doc.get('scientific_pass') is False
                 and canonical(doc)==raw,'COLD_CONTRACT')
        _require(type(ledger) is list and len(ledger)==doc['records']
                 and digest(canonical(ledger))==doc['ledger_digest'],'SOURCE_LEDGER_DRIFT')
        obj=cls()
        for identifier,c,x1,s2,x2,y in ledger:
            obj.observe_admitted_fixture(identifier,c,x1,s2,x2,y)
        _require(obj.checkpoint(source_pin)==raw,'COLD_REPLAY')
        return obj
