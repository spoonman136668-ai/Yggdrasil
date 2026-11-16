"""CB4 public *synthetic* intervention source. Source-private law stays here.

The mechanism readout is an additional public outcome obtainable only by a
charged controlled intervention. This is not an owner-hidden scientific world.
"""
from __future__ import annotations
from collections import namedtuple
import random
import binding

WORLDS = tuple(range(82400, 82432))
TRAIN_ROWS = 515
TEST_ROWS = 128
PREREG_PRIVATE_CONFIGS = (
    ((1, 6), (17, 22)),
    ((10, 15), (12, 27)),
    ((14, 24), (4, 9)),
    ((5, 31), (3, 21)),
)
PublicStep = namedtuple('PublicStep', binding.FIELDS)
PublicPast = namedtuple('PublicPast', binding.PAST_FIELDS)
PublicProbe = namedtuple('PublicProbe', 'before_state target_feature after_state mediator_before mediator_after cost')


def _seed(seed):
    if type(seed) is not int or seed not in WORLDS:
        raise PermissionError('CB4_NEW_PUBLIC_COHORT_ONLY')
    return seed


def _private_features(seed):
    return PREREG_PRIVATE_CONFIGS[(_seed(seed) - WORLDS[0]) % 4]


def _mediator(seed, state):
    content, _ = _private_features(seed)
    bits = binding._feature_bits(state, 0, 0)
    return ((bits >> content[0]) & 1) ^ ((bits >> content[1]) & 1)


def _action_target(seed, state, prev, older):
    content, gate = _private_features(seed)
    bits = binding._feature_bits(state, prev, older)
    x, y = ((bits >> b) & 1 for b in content)
    g0, g1 = ((bits >> b) & 1 for b in gate)
    return x ^ y ^ int(2*x+y == 2*g0+g1)


def training(seed):
    rng = random.Random(_seed(seed))
    states = [tuple(rng.randrange(16) for _ in range(8)) for _ in range(TRAIN_ROWS+1)]
    actions = [rng.randrange(2) for _ in range(TRAIN_ROWS)]
    rewards = [0] * TRAIN_ROWS
    for t in range(3, TRAIN_ROWS):
        earned_index = t-2
        actual = _action_target(seed, states[earned_index], actions[earned_index-1],
                                actions[earned_index-2] if earned_index >= 2 else 0)
        rewards[t] = 1 if actions[earned_index] == actual else -1
    return tuple(PublicStep(states[t], actions[t], states[t+1], rewards[t], False,
                    tuple(PublicPast(states[j], actions[j], rewards[j], states[j+1], False)
                          for j in range(max(0,t-16), t)))
                 for t in range(TRAIN_ROWS))


def queries(seed):
    rng = random.Random(_seed(seed)+1000)
    for _ in range(TEST_ROWS):
        s0 = tuple(rng.randrange(16) for _ in range(8))
        s1 = tuple(rng.randrange(16) for _ in range(8))
        state = tuple(rng.randrange(16) for _ in range(8))
        p0, p1 = rng.randrange(2), rng.randrange(2)
        past = (PublicPast(s0,p0,0,s1,False),PublicPast(s1,p1,0,state,False))
        yield (state, past, _action_target(seed,state,p1,p0))


class PublicInterventionSource:
    """Reset to the SAME public baseline before each charged do(bit flip)."""
    MAX_PAID_PROBES = 3
    def __init__(self, seed):
        self._seed = _seed(seed)
        rng = random.Random(seed+3000)
        self._baseline = tuple(rng.randrange(16) for _ in range(8))
        self._paid = 0
        self._used = set()

    @property
    def paid(self):
        return self._paid

    def probe(self, feature):
        if type(feature) is not int or not 0 <= feature < 32:
            raise ValueError('CB4_NOT_A_PHYSICAL_STATE_BIT')
        if self._paid >= self.MAX_PAID_PROBES:
            raise ValueError('CB4_PAID_PROBE_BUDGET')
        if feature in self._used:
            raise ValueError('CB4_DUPLICATE_PROBE')
        before = self._baseline
        after = list(before)
        after[feature//4] ^= 1 << (feature%4)
        after = tuple(after)
        prior = _mediator(self._seed, before)
        after_readout = _mediator(self._seed, after)
        self._paid += 1
        self._used.add(feature)
        return PublicProbe(before, feature, after, prior, after_readout, 1)


def _owner_audit(seed):
    c,g = _private_features(seed)
    return tuple(sorted(c)), tuple(sorted(g))
