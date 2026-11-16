"""CB5 public synthetic mechanism source. Sensor identity and causal roles stay private.

Eight observable sensor channels are permuted per world. Six sensors respond to
two of four relevant public-state bit interventions; only one has a direct
causal effect on action-conditioned earned reward under do(sensor=value).
"""
from __future__ import annotations
from collections import namedtuple
from itertools import combinations
import random
import binding

SEEDS = tuple(range(82500, 82532))
TRAIN_ROWS = 515
TEST_ROWS = 128
PRIVATE_STRUCTURES = (
    ((1, 6), (17, 22)),
    ((10, 15), (12, 27)),
    ((14, 24), (4, 9)),
    ((5, 31), (3, 21)),
)
PublicStep = namedtuple('PublicStep', binding.FIELDS)
PublicPast = namedtuple('PublicPast', binding.PAST_FIELDS)
PublicBitProbe = namedtuple('PublicBitProbe','before_state target_feature after_state sensor_before sensor_after cost')
PublicOutcomeProbe = namedtuple('PublicOutcomeProbe','before_state target_channel sensor_before sensor_after action reward cost')


def _seed(seed):
    if type(seed) is not int or seed not in SEEDS:
        raise PermissionError('CB5_PUBLIC_DEV_SEEDS_ONLY')
    return seed


def _hidden(seed):
    return PRIVATE_STRUCTURES[(_seed(seed)-SEEDS[0]) % len(PRIVATE_STRUCTURES)]


def _permutation(seed):
    order=list(range(8))
    random.Random(_seed(seed)+2000).shuffle(order)
    return tuple(order)


def _bit(state, index):
    return (state[index // 4] >> (index % 4)) & 1


def _sensor_state(seed, state):
    c,g = _hidden(seed)
    four=tuple(sorted(c+g))
    pairs=tuple(combinations(four, 2))
    outputs=[_bit(state,a)^_bit(state,b) for a,b in pairs]
    outputs.extend((_bit(state,0),_bit(state,2)))
    order=_permutation(seed)
    return tuple(outputs[i] for i in order)


def _mediator_channel(seed):
    c,_ = _hidden(seed)
    four=tuple(sorted(sum((_hidden(seed)), ())))
    pairs=tuple(combinations(four,2))
    index=pairs.index(tuple(sorted(c)))
    return _permutation(seed).index(index)


def _target(seed,state,prev,older, forced_channel=None):
    c,g=_hidden(seed)
    x,y=(_bit(state,b) for b in c)
    g0,g1=(_bit(state,b) for b in g)
    mediator=x^y
    if forced_channel == _mediator_channel(seed):
        mediator ^= 1
    return mediator ^ int(2*x+y == 2*g0+g1)


def training(seed):
    rng=random.Random(_seed(seed))
    states=[tuple(rng.randrange(16) for _ in range(8)) for _ in range(TRAIN_ROWS+1)]
    actions=[rng.randrange(2) for _ in range(TRAIN_ROWS)]
    reward=[0]*TRAIN_ROWS
    for t in range(3, TRAIN_ROWS):
        credited=t-2
        good=_target(seed,states[credited],actions[credited-1],
                     actions[credited-2] if credited >= 2 else 0)
        reward[t] = 1 if actions[credited]==good else -1
    return tuple(PublicStep(states[t],actions[t],states[t+1],reward[t],False,
                 tuple(PublicPast(states[j],actions[j],reward[j],states[j+1],False)
                       for j in range(max(0,t-16),t))) for t in range(TRAIN_ROWS))


def unseen_queries(seed):
    rng=random.Random(_seed(seed)+1000)
    for _ in range(TEST_ROWS):
        earlier=tuple(rng.randrange(16) for _ in range(8))
        previous=tuple(rng.randrange(16) for _ in range(8))
        state=tuple(rng.randrange(16) for _ in range(8))
        p0,p1=rng.randrange(2),rng.randrange(2)
        hist=(PublicPast(earlier,p0,0,previous,False),PublicPast(previous,p1,0,state,False))
        yield state,hist,_target(seed,state,p1,p0)


class PaidInterventionWorld:
    """Every request charges one public action, reset to same state each time."""
    MAX_SENSOR_PROBES=6
    def __init__(self,seed):
        self._seed=_seed(seed)
        rng=random.Random(seed+4000)
        self._before=tuple(rng.randrange(16) for _ in range(8))
        self._sensors=_sensor_state(seed,self._before)
        self._bit_probed=set()
        self._sensor_probed=set()
        self._baseline_done=False
        self._charged=0

    @property
    def paid(self):return self._charged

    def bit_probe(self,index):
        if type(index) is not int or not 0<=index<32 or index in self._bit_probed:
            raise ValueError('CB5_INVALID_PUBLIC_BIT_PROBE')
        if self._baseline_done or len(self._bit_probed)>=4:
            raise ValueError('CB5_UPSTREAM_PROBE_PHASE_CLOSED')
        after=list(self._before)
        after[index//4] ^= 1 << (index%4)
        after=tuple(after)
        sensor_after=_sensor_state(self._seed,after)
        self._bit_probed.add(index)
        self._charged+=1
        return PublicBitProbe(self._before,index,after,self._sensors,sensor_after,1)

    def baseline_action(self,action=0):
        if len(self._bit_probed)!=4 or self._baseline_done or type(action) is not int or action!=0:
            raise ValueError('CB5_BASELINE_ACTION_PHASE')
        good=_target(self._seed,self._before,0,0)
        self._charged+=1
        self._baseline_done=True
        return PublicOutcomeProbe(self._before,-1,self._sensors,self._sensors,
                                  action,1 if action==good else -1,1)

    def sensor_action(self,index,action=0):
        if not self._baseline_done or type(index) is not int or not 0<=index<8:
            raise ValueError('CB5_INVALID_SENSOR_PROBE')
        if index in self._sensor_probed or len(self._sensor_probed)>=self.MAX_SENSOR_PROBES:
            raise ValueError('CB5_SENSOR_ACTION_BUDGET')
        if type(action) is not int or action!=0:
            raise ValueError('CB5_PUBLIC_BINARY_BASELINE_ACTION')
        after=list(self._sensors)
        after[index]^=1
        good=_target(self._seed,self._before,0,0,forced_channel=index)
        self._sensor_probed.add(index)
        self._charged+=1
        return PublicOutcomeProbe(self._before,index,self._sensors,tuple(after),
                                  action,1 if action==good else -1,1)


def _private_audit(seed):
    content,gate=_hidden(seed)
    return tuple(sorted(content)),tuple(sorted(gate)),_mediator_channel(seed)
