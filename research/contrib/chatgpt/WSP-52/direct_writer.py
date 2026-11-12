"""WSP52 bounded evidence-to-numeric-weight writer: NOT a trained neural net.

The only inputs are before/after states and complete *undelimited* acoustic bits.
No true codeword, role order, oracle target or latent world is read.

Learns finite segmentation hypotheses (4..6 bits per candidate word) and
writes integer association counts directly to sparse addressed weight maps.
A confident result must have independent grounded entity and effect evidence;
otherwise it abstains. This is a developmental candidate, not grammar induction.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import product
import json

SEGMENT_LENGTHS = (4, 5, 6)
MAX_SEGMENTATIONS = 27
MAX_WEIGHTS = 20_000


def _validate_state(state):
    if type(state) is not tuple or len(state) != 8 or any(type(x) is not int or x not in range(4) for x in state):
        raise ValueError('expected eight integer locations in range(4)')


def _parts(bits):
    if type(bits) is not str or not bits or set(bits) - {'0', '1'}:
        raise ValueError('raw stream must be nonempty binary')
    out = []
    for a, b, c in product(SEGMENT_LENGTHS, repeat=3):
        if a+b+c == len(bits):
            out.append((bits[:a], bits[a:a+b], bits[a+b:]))
    if len(out) > MAX_SEGMENTATIONS:
        raise ValueError('segmentation cap exceeded')
    return out


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True)


class DirectWeightWriter:
    """Direct sparse integer association-weight construction, no gradient steps.

    There are no lexical IDs in this model; each candidate is a raw substring.
    All six latent orderings are admissible through 3 potential entity positions.
    The source simulator's destination/verb decomposition is deliberately not used.
    """
    def __init__(self, *, min_entity=2, min_effect=2):
        if (min_entity, min_effect) != (2, 2):
            raise ValueError('developmental evidence thresholds are frozen')
        # (slot, raw acoustic candidate, observed entity) -> integer weight.
        self.entity_weights = Counter()
        # (entity slot, left other candidate, right other candidate, effect) -> weight.
        self.effect_weights = Counter()
        self.seen = {}    # observation conflicts, not available as model answers.
        self.conflicts = set()
        self.actions = 0
        self.informative = 0

    def observe(self, observation):
        before = observation.before
        after = observation.after
        bits = observation.acoustic_bits
        _validate_state(before)
        _validate_state(after)
        segmentations = _parts(bits)
        if type(observation.action_cost) is not int or observation.action_cost != 1 or type(observation.reset_cost) is not int or observation.reset_cost != 0:
            raise ValueError('unaccounted evidence action or reset')
        changed = [i for i, (a,b) in enumerate(zip(before, after)) if a != b]
        if len(changed) > 1:
            raise ValueError('multiple state changes violate supplied action library')
        key = (_canonical(before), bits)
        if key in self.seen and self.seen[key] != after:
            self.conflicts.add(key)
        self.seen[key] = after
        self.actions += 1
        if not changed:  # no observable entity; do not invent a target identity
            return
        self.informative += 1
        entity = changed[0]
        effect = after[entity]
        for words in segmentations:
            for entity_slot in range(3):
                entity_key = (entity_slot, words[entity_slot], entity)
                others = tuple(words[i] for i in range(3) if i != entity_slot)
                effect_key = (entity_slot, others[0], others[1], effect)
                self.entity_weights[entity_key] += 1
                self.effect_weights[effect_key] += 1
        if len(self.entity_weights) + len(self.effect_weights) > MAX_WEIGHTS:
            raise OverflowError('candidate-weight cap exceeded; no pruning by evaluation data')

    def _best(self, counts, min_support):
        if not counts:
            return None
        ranked = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
        if ranked[0][1] < min_support or len(ranked) > 1 and ranked[0][1] != sum(counts.values()):
            return None
        # Every observed label must agree. Ambiguous evidence => abstain.
        return ranked[0]

    def predict(self, before, acoustic_bits):
        _validate_state(before)
        segmentations = _parts(acoustic_bits)
        key = (_canonical(before), acoustic_bits)
        if key in self.conflicts:
            return None
        candidates = {}
        for words in segmentations:
            for slot in range(3):
                ent = Counter({k[2]: w for k, w in self.entity_weights.items() if k[:2] == (slot, words[slot])})
                parts = tuple(words[i] for i in range(3) if i != slot)
                eff = Counter({k[3]: w for k, w in self.effect_weights.items() if k[:3] == (slot, parts[0], parts[1])})
                best_ent = self._best(ent, 2)
                best_eff = self._best(eff, 2)
                if best_ent is None or best_eff is None:
                    continue
                entity, e_score = best_ent
                effect, f_score = best_eff
                new = list(before)
                new[entity] = effect
                outcome = tuple(new)
                score = min(e_score, f_score)
                candidates[outcome] = max(score, candidates.get(outcome, 0))
        if not candidates:
            return None
        ranked = sorted(candidates.items(), key=lambda x:(-x[1], x[0]))
        # Rival interpretations of similar support imply uncertainty.
        if len(ranked) > 1 and ranked[0][1] <= 2 * ranked[1][1]:
            return None
        return ranked[0][0]

    def numeric_weight_count(self):
        return len(self.entity_weights) + len(self.effect_weights)

    def snapshot(self):
        rows = {
            'schema': 'wsp52.direct-sparse-writer.v1',
            'entity': [list(k)+[v] for k,v in sorted(self.entity_weights.items())],
            'effect': [list(k)+[v] for k,v in sorted(self.effect_weights.items())],
            'seen': [[k[0],k[1],list(v)] for k,v in sorted(self.seen.items())],
            'conflicts': [list(k) for k in sorted(self.conflicts)],
            'actions': self.actions, 'informative': self.informative,
        }
        raw = _canonical(rows)
        return _canonical({'payload':rows,'sha256':sha256(raw.encode('ascii')).hexdigest()})

    @classmethod
    def restore(cls, data):
        try:
            decoded=json.loads(data)
            payload=decoded['payload']
            if set(decoded) != {'payload','sha256'} or _canonical(decoded) != data:
                raise ValueError('noncanonical envelope')
            if sha256(_canonical(payload).encode('ascii')).hexdigest()!=decoded['sha256']:
                raise ValueError('tampered payload')
            if payload['schema'] != 'wsp52.direct-sparse-writer.v1' or set(payload) != {'schema','entity','effect','seen','conflicts','actions','informative'}:
                raise ValueError('unknown model schema')
            self=cls()
            self.entity_weights = Counter({tuple(row[:3]):row[3] for row in payload['entity']})
            self.effect_weights = Counter({tuple(row[:4]):row[4] for row in payload['effect']})
            self.seen = {(k,bits):tuple(v) for k,bits,v in payload['seen']}
            self.conflicts = {tuple(row) for row in payload['conflicts']}
            self.actions = payload['actions']
            self.informative = payload['informative']
            if self.actions < 0 or self.informative < 0 or self.informative > self.actions:
                raise ValueError('invalid cost counters')
            if any(type(v) is not int or v<1 for v in self.entity_weights.values()) or any(type(v) is not int or v<1 for v in self.effect_weights.values()):
                raise ValueError('invalid weight magnitude')
            if self.numeric_weight_count() > MAX_WEIGHTS:
                raise ValueError('too many weights')
            if self.snapshot() != data:
                raise ValueError('noncanonical state')
            return self
        except (KeyError, TypeError, IndexError, UnicodeError, json.JSONDecodeError) as exc:
            raise ValueError('invalid model snapshot') from exc

    def capacity_bits(self):
        return 8 * len(self.snapshot().encode('ascii'))
