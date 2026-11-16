"""CB5 source-blind mediator sensor discovery from real paid public actions.

No import of public_source, no hidden feature/source role/channel access.
Generic logic identifies paired sensor responses then tests their downstream
consequences on the earned binary action. Conventional posterior is independent.
"""
from __future__ import annotations
from hashlib import sha256
from itertools import combinations
import json
import struct

BIT_FIELDS=('before_state','target_feature','after_state','sensor_before','sensor_after','cost')
OUT_FIELDS=('before_state','target_channel','sensor_before','sensor_after','action','reward','cost')
MAX_PAID=11
MAGIC=b'CB5D'

def _four(features):
    if type(features) not in (tuple,list) or len(features)!=4 or len(set(features))!=4 or any(type(x) is not int or not 0<=x<32 for x in features):
        raise ValueError('CB5_FOUR_PUBLIC_STATE_BITS_REQUIRED')
    return tuple(sorted(features))

def _state(s):
    if type(s) is not tuple or len(s)!=8 or any(type(x) is not int or not 0<=x<16 for x in s):
        raise ValueError('CB5_PUBLIC_STATE')
    return s

def _sensors(s):
    if type(s) is not tuple or len(s)!=8 or any(type(x) is not int or x not in (0,1) for x in s):
        raise ValueError('CB5_PUBLIC_SENSORS')
    return s

def _bit_event(row,expected,baseline,sensors):
    if tuple(getattr(row,'_fields',()))!=BIT_FIELDS:
        raise ValueError('CB5_BIT_SCHEMA')
    before,feature,after,s0,s1,cost=row
    _state(before);_state(after);_sensors(s0);_sensors(s1)
    if type(feature) is not int or feature!=expected or type(cost) is not int or cost!=1:
        raise ValueError('CB5_BIT_ACTUAL_INTERVENTION')
    if baseline is not None and (baseline!=before or sensors!=s0):
        raise ValueError('CB5_BIT_RESET_CUSTODY')
    after_should=list(before);after_should[feature//4]^=1<<(feature%4)
    if after!=tuple(after_should):
        raise ValueError('CB5_BIT_NONPHYSICAL_CHANGE')
    return tuple(x!=y for x,y in zip(s0,s1))

def _out_event(row,expected,baseline,sensors):
    if tuple(getattr(row,'_fields',()))!=OUT_FIELDS:
        raise ValueError('CB5_EARNED_ACTION_SCHEMA')
    before,ch,s0,s1,action,reward,cost=row
    _state(before);_sensors(s0);_sensors(s1)
    if before!=baseline or s0!=sensors:
        raise ValueError('CB5_ACTION_RESET_CUSTODY')
    if type(ch) is not int or ch!=expected or type(action) is not int or action!=0 or type(reward) is not int or reward not in (-1,1) or type(cost) is not int or cost!=1:
        raise ValueError('CB5_ACTION_CHARGE_OR_EARNED_REWARD')
    after=list(sensors)
    if ch>=0:
        if not ch<8: raise ValueError('CB5_CHANNEL_RANGE')
        after[ch]^=1
    if s1!=tuple(after):
        raise ValueError('CB5_NONPHYSICAL_SENSOR_INTERVENTION')
    return reward

def _receipt(row):
    values=[]
    for part in row:
        if type(part) is tuple:values.append(list(part))
        else:values.append(part)
    raw=json.dumps(values,separators=(',',':'),allow_nan=False).encode('ascii')
    return len(raw).to_bytes(2,'big')+raw

class DirectCausalSensor:
    """Store only direct public sensor-change masks and earned action reversal."""
    def __init__(self,four_features):
        self.features=_four(four_features)
        self._baseline=None
        self._sensors=None
        self._responses={}
        self._baseline_reward=None
        self._candidate_channels=None
        self._probed=[]
        self._selected=None
        self._digest=sha256()
    def next_bit(self):
        return self.features[len(self._responses)] if len(self._responses)<4 else None
    def observe_bit(self,row):
        idx=self.next_bit()
        if idx is None or self._baseline_reward is not None:
            raise ValueError('CB5_UPSTREAM_CLOSED')
        changes=_bit_event(row,idx,self._baseline,self._sensors)
        if self._baseline is None:
            self._baseline=row.before_state;self._sensors=row.sensor_before
        self._responses[idx]=changes
        self._digest.update(_receipt(row))
    def candidates(self):
        if len(self._responses)!=4:raise ValueError('CB5_INCOMPLETE_UPSTREAM')
        if self._candidate_channels is None:
            out=[]
            for channel in range(8):
                responding=tuple(f for f in self.features if self._responses[f][channel])
                if len(responding)==2:out.append((channel,responding))
            if len(out)!=6 or set(r for _,r in out)!=set(combinations(self.features,2)):
                raise ValueError('CB5_SOURCE_HAS_NO_IDENTIFIABLE_PAIR_CHANNELS')
            self._candidate_channels=tuple(out)
        return self._candidate_channels
    def observe_baseline(self,row):
        self.candidates()
        if self._baseline_reward is not None:raise ValueError('CB5_DUPLICATE_BASELINE')
        reward=_out_event(row,-1,self._baseline,self._sensors)
        self._baseline_reward=reward
        self._digest.update(_receipt(row))
    def next_channel(self):
        if self._selected is not None:return None
        if self._baseline_reward is None:raise ValueError('CB5_BASELINE_UNOBSERVED')
        if len(self._probed)>=len(self.candidates()):
            raise ValueError('CB5_NO_CAUSAL_CHANNEL_DETECTED')
        return self.candidates()[len(self._probed)][0]
    def observe_sensor(self,row):
        channel=self.next_channel()
        result=_out_event(row,channel,self._baseline,self._sensors)
        # Prove public model change only after successful charged probe validation.
        self._probed.append(channel)
        self._digest.update(_receipt(row))
        if result != self._baseline_reward:
            self._selected=channel
    @property
    def selected(self):
        if self._selected is None:return None
        return self._selected,dict(self.candidates())[self._selected]
    @property
    def paid(self):return len(self._responses)+int(self._baseline_reward is not None)+len(self._probed)
    @property
    def no_downstream_guess(self):
        return self.candidates()[0]
    @property
    def wrong_attribution(self):
        if self._selected is None:return None
        channels=[v for v,_ in self.candidates()]
        return channels[(channels.index(self._selected)+1)%len(channels)]
    def snapshot(self):
        if self.selected is None:raise ValueError('CB5_UNSEALED_CAUSAL_EVIDENCE')
        ch,parents=self.selected
        payload=struct.pack('>4s4B3B',MAGIC,*self.features,ch,parents[0],parents[1])
        payload+=bytes([self.paid])+self._digest.digest()
        return payload+sha256(payload).digest()
    @classmethod
    def restore(cls,raw):
        if type(raw) is not bytes or len(raw)!=struct.calcsize('>4s4B3B')+1+64:
            raise ValueError('CB5_SNAPSHOT_FORMAT')
        if sha256(raw[:-32]).digest()!=raw[-32:]:
            raise ValueError('CB5_SNAPSHOT_CHECKSUM')
        parsed=struct.unpack('>4s4B3B',raw[:11])
        magic,*fields=parsed
        if magic!=MAGIC:raise ValueError('CB5_SNAPSHOT_VERSION')
        four=_four(fields[:4])
        ch,a,b=fields[4:]
        if not 0<=ch<8 or (a,b) not in combinations(four,2) or not 6<=raw[11]<=11:
            raise ValueError('CB5_SNAPSHOT_FIELDS')
        obj=cls(four)
        obj._selected=ch
        obj._candidate_channels=((ch,(a,b)),)
        obj._baseline_reward=1
        obj._probed=[ch]*(raw[11]-5)
        obj._responses={f:() for f in four}
        obj._digest=None
        obj._frozen=raw
        return obj
    def proof(self):
        return self.snapshot() if not hasattr(self,'_frozen') else self._frozen

class ConventionalSensorPosterior:
    """Separate exact discrete causal hypotheses from identical charged probes."""
    def __init__(self,four_features):
        self.features=_four(four_features)
        self._changes={}
        self._baseline=None
        self._sensors=None
        self._base_reward=None
        self._hypotheses=None
        self._tested=[]
        self._chosen=None
    def next_bit(self):
        return self.features[len(self._changes)] if len(self._changes)<4 else None
    def observe_bit(self,row):
        j=self.next_bit()
        if j is None or self._base_reward is not None:raise ValueError('CB5_BAYES_UPSTREAM_CLOSED')
        changed=_bit_event(row,j,self._baseline,self._sensors)
        if self._baseline is None:
            self._baseline=row.before_state
            self._sensors=row.sensor_before
        self._changes[j]=changed
    def _create_posterior(self):
        if len(self._changes)!=4:raise ValueError('CB5_BAYES_INCOMPLETE_FEATURE_OBSERVATIONS')
        if self._hypotheses is None:
            hypotheses={}
            for channel in range(8):
                affected=tuple(f for f in self.features if self._changes[f][channel])
                if len(affected)==2:hypotheses[channel]=affected
            if len(hypotheses)!=6 or set(hypotheses.values())!=set(combinations(self.features,2)):
                raise ValueError('CB5_BAYES_UNSUPPORTED_SOURCE')
            self._hypotheses=hypotheses
    def observe_baseline(self,row):
        self._create_posterior()
        if self._base_reward is not None:raise ValueError('CB5_BAYES_BASELINE_DUPLICATE')
        self._base_reward=_out_event(row,-1,self._baseline,self._sensors)
    def next_channel(self):
        if self._chosen is not None:return None
        if self._base_reward is None:raise ValueError('CB5_BAYES_BASELINE_MISSING')
        if not self._hypotheses:raise ValueError('CB5_BAYES_NO_SUPPORTED_MEDIATOR')
        return min(self._hypotheses)
    def observe_sensor(self,row):
        j=self.next_channel()
        earned=_out_event(row,j,self._baseline,self._sensors)
        self._tested.append(j)
        if earned != self._base_reward:
            self._chosen=(j,self._hypotheses[j])
        else:
            del self._hypotheses[j]
    @property
    def selected(self):
        return self._chosen
    @property
    def paid(self):
        return len(self._changes)+int(self._base_reward is not None)+len(self._tested)
