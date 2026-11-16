"""CB4 source-blind active mechanism probes for a previously learned 4-bit law.

Does NOT import the generator. Probe evidence consists only of a public state
transition and a separately measured binary mediator before/after. Both native-
style and conventional references know the prespecified 2-of-4 role cardinality.
"""
from __future__ import annotations
from itertools import combinations
from hashlib import sha256
import json
import struct

PROBE_FIELDS = ('before_state','target_feature','after_state','mediator_before','mediator_after','cost')
MAX_PROBES = 3
SNAP_MAGIC = b'CB4R'


def _features(value):
    if type(value) not in (list,tuple) or len(value)!=4 or any(
       type(x) is not int or not 0<=x<32 for x in value) or len(set(value))!=4:
        raise ValueError('CB4_MUST_DISCOVER_FOUR_PHYSICALLY_PROBEABLE_BITS')
    return tuple(sorted(value))


def _public_probe(row, expected_feature, expected_baseline):
    if tuple(getattr(row,'_fields',())) != PROBE_FIELDS:
        raise ValueError('CB4_PUBLIC_PROBE_SCHEMA')
    before, feature, after, mb, ma, cost = row
    if type(before) is not tuple or type(after) is not tuple or len(before)!=8 or len(after)!=8:
        raise ValueError('CB4_PUBLIC_PROBE_STATES')
    if any(type(x) is not int or not 0<=x<16 for x in before+after):
        raise ValueError('CB4_PUBLIC_PROBE_UINT4')
    if type(feature) is not int or feature != expected_feature or not 0<=feature<32:
        raise ValueError('CB4_PROBE_ACTION_MISMATCH')
    if expected_baseline is not None and before != expected_baseline:
        raise ValueError('CB4_RESET_BASELINE_CHANGED')
    predicted=list(before);predicted[feature//4]^=1<<(feature%4)
    if tuple(predicted)!=after:
        raise ValueError('CB4_NONPHYSICAL_BIT_FLIP')
    if type(mb) is not int or type(ma) is not int or mb not in (0,1) or ma not in (0,1) or type(cost) is not int or cost != 1:
        raise ValueError('CB4_PUBLIC_MEDIATOR_OR_COST')
    return mb!=ma


class DirectRoleProbe:
    """Small direct-written diagnostic: probe first two indices, then third if needed."""
    def __init__(self, four_features):
        self.features=_features(four_features)
        self._observations={}
        self._digest=sha256()
        self._baseline=None
        self._roles=None

    def next_feature(self):
        if self._roles is not None: return None
        f=self.features
        if len(self._observations)<2:
            return f[len(self._observations)]
        if len(self._observations)==2:
            v=[self._observations[f[0]],self._observations[f[1]]]
            if v[0]==v[1]:
                self._finish()
                return None
            return f[2]
        self._finish()
        return None

    def _finish(self):
        f=self.features
        c=[j for j,v in self._observations.items() if v]
        n=len(self._observations)
        if n==2 and len(c) in (0,2):
            if len(c)==0: c=list(f[2:])
        elif n==3:
            if len(c)==1: c.append(f[3])
        else:
            raise ValueError('CB4_INSUFFICIENT_ROLE_PROOF')
        if len(c)!=2:
            raise ValueError('CB4_UNSUPPORTED_ROLE_ASSIGNMENT')
        content=tuple(sorted(c))
        gate=tuple(x for x in f if x not in c)
        self._roles=(content,gate)

    def observe_public(self, probe):
        feature=self.next_feature()
        if feature is None:
            raise ValueError('CB4_ALREADY_DONE')
        effect=_public_probe(probe,feature,self._baseline)
        if self._baseline is None:self._baseline=probe.before_state
        # Everything validated before committing evidence and cost.
        canonical=json.dumps([list(probe.before_state),probe.target_feature,list(probe.after_state),
                               probe.mediator_before,probe.mediator_after,probe.cost],separators=(',',':')).encode('ascii')
        self._digest.update(len(canonical).to_bytes(2,'big')+canonical)
        self._observations[feature]=effect

    @property
    def roles(self):
        if self._roles is None:
            self.next_feature()
        return self._roles

    @property
    def paid_probes(self):return len(self._observations)

    SNAPSHOT_FORMAT = '>4s4BBB32s'
    SNAPSHOT_BYTES = struct.calcsize(SNAPSHOT_FORMAT)+32

    def snapshot(self):
        if hasattr(self,'_frozen'):
            return self._frozen
        if self.roles is None:
            raise ValueError('CB4_UNFINISHED_PROOF')
        if self.paid_probes not in (2,3):
            raise ValueError('CB4_INCORRECT_BUDGET')
        c,g=self.roles
        if tuple(sorted(c+g))!=self.features:
            raise ValueError('CB4_INCOMPLETE_ROLES')
        mask=sum(1<<i for i,f in enumerate(self.features) if f in c)
        body=struct.pack(self.SNAPSHOT_FORMAT,SNAP_MAGIC,*self.features,mask,
                         self.paid_probes,self._digest.digest())
        result=body+sha256(body).digest()
        assert len(result)==self.SNAPSHOT_BYTES and len(result)<=128
        return result

    @classmethod
    def restore(cls,serialized):
        if type(serialized) is not bytes or len(serialized)!=cls.SNAPSHOT_BYTES:
            raise ValueError('CB4_SNAPSHOT_ENVELOPE')
        if sha256(serialized[:-32]).digest()!=serialized[-32:]:
            raise ValueError('CB4_BAD_CHECKSUM')
        try:
            magic,a,b,c,d,mask,paid,digest=struct.unpack(cls.SNAPSHOT_FORMAT,serialized[:-32])
            f=_features((a,b,c,d))
            if magic!=SNAP_MAGIC or mask.bit_count()!=2 or mask>>4 or paid not in (2,3):
                raise ValueError('CB4_BAD_MODEL_FIELDS')
            content=tuple(f[i] for i in range(4) if mask&(1<<i))
            gates=tuple(f[i] for i in range(4) if not mask&(1<<i))
            obj=cls(f);obj._roles=(content,gates);obj._frozen=serialized
            obj._observations={j:None for j in f[:paid]}
            return obj
        except (ValueError,TypeError,struct.error) as e:
            raise ValueError('CB4_INVALID_SNAPSHOT') from e


class ConventionalExactPartitions:
    """Independent conventional 6-hypothesis categorical elimination control."""
    def __init__(self, four_features):
        self.features=_features(four_features)
        self.posterior={pair:1 for pair in combinations(self.features,2)}
        self.evidence=[]
        self.baseline=None

    def next_feature(self):
        remaining=list(self.posterior)
        if len(remaining)==1:return None
        # Same frozen first-two-then-third intervention opportunities as direct model.
        if len(self.evidence)<2:return self.features[len(self.evidence)]
        if len(self.evidence)<3:return self.features[2]
        raise ValueError('CB4_BAYES_UNRESOLVED')

    def observe_public(self,row):
        j=self.next_feature()
        if j is None:raise ValueError('CB4_BAYES_ALREADY_DECIDED')
        observed=_public_probe(row,j,self.baseline)
        if self.baseline is None:self.baseline=row.before_state
        new={pair:v for pair,v in self.posterior.items() if (j in pair)==observed}
        if not new:raise ValueError('CB4_BAYES_INCONSISTENT_PUBLIC_FEEDBACK')
        self.posterior=new
        self.evidence.append((j,observed))

    @property
    def roles(self):
        if len(self.posterior)!=1:return None
        c=next(iter(self.posterior))
        return c,tuple(x for x in self.features if x not in c)

    @property
    def paid_probes(self):return len(self.evidence)
