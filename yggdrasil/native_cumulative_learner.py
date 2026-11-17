"""Opt-in cumulative CKAD integration over existing native representations.

Fixture witnesses are provenance-pinned development data, not authenticated
real-world do outcomes. No controller, source actor, or accepted-model authority.
The property image and every old constraint survive updates. Degree selection
remains provisional; inconsistent deterministic outcomes quarantine the slot.
"""
import json

from yggdrasil.native_context_basis import canonical, digest, pin, require, SOURCE_MODE, SOURCE_KIND
from yggdrasil.native_context_accumulator import NativeContextAccumulator
from yggdrasil.native_degree_hypothesis import NativeDegreeHypothesis
from yggdrasil.native_property_knowledge import NativePropertyKnowledge
from yggdrasil.native_prior_hypothesis import input_order
from yggdrasil.public_causal_cells import PublicCausalCells

SCHEMA = 'yggdrasil.ckad.native-cumulative-learner.v1'
MAX_BYTES = 16 * 1024 * 1024
MAX_EVENTS = 128


def coordinates(slot):
    require(type(slot) is int and 0 <= slot < 16, 'INTEGRATED_SLOT')
    return (slot, False) if slot < 7 else (slot - 7, True)


class NativeCumulativeLearner:
    """One immutable train/save/restore interface; no rival memory substrate."""
    __slots__ = ('_properties', '_source', '_hypotheses', '_quarantined', '_events')

    def __init__(self, property_raw, expected_sha256):
        self._properties = NativePropertyKnowledge.restore(property_raw, expected_sha256)
        self._source = NativeContextAccumulator(self._properties._bits)
        self._hypotheses = (None,) * 16
        self._quarantined = (False,) * 16
        self._events = ()

    def _copy(self):
        obj = object.__new__(NativeCumulativeLearner)
        for name in self.__slots__:
            setattr(obj, name, getattr(self, name))
        return obj

    def _rows(self, slot):
        a, r = coordinates(slot)
        bits = self._source._model.context_bits
        seen = self._source._seen[slot]
        return [[x & ((1 << bits) - 1), x >> bits,
                 self._source.predict(a, x & ((1 << bits) - 1), x >> bits, retained=r)]
                for x in sorted(range(1 << (bits + 1)), key=input_order) if seen & (1 << x)]

    def _view(self, slot):
        rows = self._rows(slot)
        bits = self._source._model.context_bits
        return NativeContextAccumulator(bits).stage_update(
            0, rows, digest(canonical(rows)), max_degree=bits + 1).checkpoint()

    def observe(self, slot, records, expected_sha256, *, source_ref,
                source_mode=SOURCE_MODE, source_kind=SOURCE_KIND):
        """Train only on revealed engineering witnesses; keep negative evidence.

        No family label, truth function, hidden source state, or evaluator is an
        input. Repeated witnessed inputs do not become extra training examples.
        A deterministic contradiction returns a quarantined copy, never erases
        the old weights or invents a corrected outcome.
        """
        a, r = coordinates(slot)
        require(source_mode == SOURCE_MODE and source_kind == SOURCE_KIND,
                'INTEGRATED_ORIGINAL_CAUSAL_SOURCE_UNQUALIFIED')
        require(pin(source_ref) and pin(expected_sha256)
                and type(records) is list and 0 < len(records) <= 2048
                and digest(canonical(records)) == expected_sha256, 'INTEGRATED_SOURCE_PIN')
        seen = {}
        for row in records:
            require(type(row) is list and len(row) == 3, 'INTEGRATED_PUBLIC_ROW')
            c = self._source._model._context(row[0])
            action = PublicCausalCells._bit(row[1], 'ACTION')
            y = PublicCausalCells._bit(row[2], 'PUBLIC_OUTCOME')
            key = c | (action << self._source._model.context_bits)
            require(key not in seen or seen[key] == y, 'INTEGRATED_INTERNAL_CONFLICT')
            seen[key] = y
        event_key = digest(canonical([slot, expected_sha256, source_ref]))
        if any(e['event_key'] == event_key for e in self._events):
            return self
        require(not self._quarantined[slot], 'INTEGRATED_QUARANTINED')
        require(len(self._events) < MAX_EVENTS, 'INTEGRATED_EVENT_CAPACITY')
        conflicts = [row for row in records if self._source._seen[slot] &
                     (1 << (row[0] | (row[1] << self._source._model.context_bits))) and
                     self._source.predict(a, row[0], row[1], retained=r) != row[2]]
        event = {'event_key': event_key, 'slot': slot, 'source_ref': source_ref,
                 'source_sha256': expected_sha256, 'records': len(records),
                 'status': 'QUARANTINED' if conflicts else 'ACQUIRED',
                 'conflicting_packet': records if conflicts else None}
        obj = self._copy()
        if conflicts:
            obj._quarantined = self._quarantined[:slot] + (True,) + self._quarantined[slot+1:]
        else:
            bits = self._source._model.context_bits
            fresh = [[x & ((1 << bits)-1), x >> bits, y] for x, y in seen.items()
                     if not self._source._seen[slot] & (1 << x)]
            if fresh:
                obj._source = self._source.stage_update(a, fresh, digest(canonical(fresh)),
                                                       max_degree=bits+1, retained=r)
            n = obj._source._seen[slot].bit_count()
            hyp = None
            if n >= 8 and n % 4 == 0:
                raw = obj._view(slot)
                hyp = NativeDegreeHypothesis.fit_checkpoint(raw, digest(raw))
            obj._hypotheses = self._hypotheses[:slot] + (hyp,) + self._hypotheses[slot+1:]
        obj._events = self._events + (event,)
        return obj

    def predict(self, slot, context, action, *, provisional=True):
        a, r = coordinates(slot)
        require(type(provisional) is bool, 'INTEGRATED_PROVISIONAL_FLAG')
        answer = self._source.predict(a, context, action, retained=r)
        if self._quarantined[slot]:
            return None
        if answer is not None or not provisional:
            return answer
        hyp = self._hypotheses[slot]
        return hyp.predict_provisional(context, action) if hyp is not None else None

    def predict_entity(self, slot, entity, action):
        p = self._properties
        p._entity(entity)
        require(p._known[entity] == (1 << p._bits)-1, 'INTEGRATED_INCOMPLETE_CONTEXT')
        return self.predict(slot, p._values[entity], action)

    def propose(self, slot, public_inputs, count):
        """Select cached/public action inputs without inspecting their outcomes.

        Priority is unknown provisional readout, then an unobserved alternative
        at an observed context, then the existing deterministic SHA ordering.
        This heuristic is not a claim of optimal intervention value.
        """
        coordinates(slot)
        require(not self._quarantined[slot] and type(count) is int and count > 0,
                'INTEGRATED_PROPOSAL')
        require(type(public_inputs) is list and len(public_inputs) <= 2048,
                'INTEGRATED_PUBLIC_INPUTS')
        bits = self._source._model.context_bits
        masks = set()
        for row in public_inputs:
            require(type(row) is list and len(row) == 2, 'INTEGRATED_PROPOSAL_LABEL_LEAK')
            c = self._source._model._context(row[0])
            action = PublicCausalCells._bit(row[1], 'ACTION')
            masks.add(c | (action << bits))
        old = self._source._seen[slot]
        fresh = [x for x in masks if not old & (1 << x)]
        def priority(x):
            c, a = x & ((1 << bits)-1), x >> bits
            return (self.predict(slot, c, a) is not None,
                    not bool(old & (1 << (x ^ (1 << bits)))), input_order(x))
        return [[x & ((1 << bits)-1), x >> bits] for x in sorted(fresh, key=priority)[:count]]

    def info(self):
        return {'stored_properties': self._properties.property_count,
                'observed_inputs': [s.bit_count() for s in self._source._seen],
                'quarantined': list(self._quarantined),
                'representations': [h.info() if h is not None else None for h in self._hypotheses],
                'events': len(self._events), 'accepted_native': False, 'scientific_pass': False}

    def checkpoint(self):
        raw = canonical({'schema': SCHEMA, 'source_mode': SOURCE_MODE,
            'properties_ascii': self._properties.checkpoint().decode('ascii'),
            'source_ascii': self._source.checkpoint().decode('ascii'),
            'hypotheses_ascii': [h.checkpoint().decode('ascii') if h is not None else None
                                 for h in self._hypotheses],
            'quarantined': self._quarantined, 'events': self._events,
            'accepted_native': False, 'scientific_pass': False})
        require(len(raw) <= MAX_BYTES, 'INTEGRATED_CHECKPOINT_CAPACITY')
        return raw

    @classmethod
    def restore(cls, raw, expected_sha256):
        require(type(raw) is bytes and 0 < len(raw) <= MAX_BYTES and pin(expected_sha256)
                and digest(raw) == expected_sha256, 'INTEGRATED_CHECKPOINT_PIN')
        def unique(pairs):
            d = {}
            for k, v in pairs:
                require(k not in d, 'INTEGRATED_DUPLICATE_KEY'); d[k] = v
            return d
        try:
            d = json.loads(raw.decode('ascii'), object_pairs_hook=unique)
            require(type(d) is dict and set(d) == {'schema','source_mode','properties_ascii',
                'source_ascii','hypotheses_ascii','quarantined','events','accepted_native','scientific_pass'}
                and d['schema'] == SCHEMA and d['source_mode'] == SOURCE_MODE
                and d['accepted_native'] is False and d['scientific_pass'] is False
                and canonical(d) == raw, 'INTEGRATED_CHECKPOINT_CONTRACT')
            p = d['properties_ascii'].encode('ascii'); obj = cls(p, digest(p))
            s = d['source_ascii'].encode('ascii')
            obj._source = NativeContextAccumulator.restore(s, digest(s))
            require(obj._source._model.context_bits == obj._properties._bits, 'INTEGRATED_CONTEXT_JOIN')
            hs, qs, es = d['hypotheses_ascii'], d['quarantined'], d['events']
            require(type(hs) is list and len(hs) == 16 and type(qs) is list and len(qs) == 16
                and all(type(q) is bool for q in qs) and type(es) is list and len(es) <= MAX_EVENTS,
                'INTEGRATED_STATE_SHAPE')
            hypotheses = []
            for slot, h in enumerate(hs):
                n = obj._source._seen[slot].bit_count()
                require((h is not None) == (n >= 8 and n % 4 == 0), 'INTEGRATED_HYPOTHESIS_REQUIRED')
                if h is None:
                    hypotheses.append(None); continue
                h = h.encode('ascii'); hyp = NativeDegreeHypothesis.restore(h, digest(h))
                require(hyp.info()['source_checkpoint_sha256'] == digest(obj._view(slot)),
                        'INTEGRATED_HYPOTHESIS_SOURCE_JOIN')
                hypotheses.append(hyp)
            keys = set(); flags = [False]*16
            for e in es:
                require(type(e) is dict and set(e) == {'event_key','slot','source_ref','source_sha256',
                    'records','status','conflicting_packet'}, 'INTEGRATED_EVENT_SCHEMA')
                coordinates(e['slot'])
                require(pin(e['source_ref']) and pin(e['source_sha256'])
                    and e['event_key'] == digest(canonical([e['slot'],e['source_sha256'],e['source_ref']]))
                    and e['event_key'] not in keys and type(e['records']) is int
                    and 0 < e['records'] <= 2048, 'INTEGRATED_EVENT_PIN')
                require(not flags[e['slot']], 'INTEGRATED_POST_QUARANTINE_EVENT')
                keys.add(e['event_key'])
                if e['status'] == 'QUARANTINED':
                    packet = e['conflicting_packet']
                    require(type(packet) is list and len(packet) == e['records']
                            and digest(canonical(packet)) == e['source_sha256'], 'INTEGRATED_CONFLICT_PIN')
                    a, r = coordinates(e['slot']); bits = obj._source._model.context_bits
                    contradictions = 0
                    for row in packet:
                        require(type(row) is list and len(row) == 3, 'INTEGRATED_CONFLICT_ROW')
                        c = obj._source._model._context(row[0]); PublicCausalCells._bit(row[1], 'ACTION')
                        PublicCausalCells._bit(row[2], 'PUBLIC_OUTCOME')
                        old = obj._source.predict(a, c, row[1], retained=r)
                        contradictions += old is not None and old != row[2]
                    require(contradictions > 0, 'INTEGRATED_FAKE_QUARANTINE')
                    flags[e['slot']] = True
                else:
                    require(e['status'] == 'ACQUIRED' and e['conflicting_packet'] is None,
                            'INTEGRATED_EVENT_STATUS')
            require(flags == qs, 'INTEGRATED_QUARANTINE_LEDGER')
            obj._hypotheses = tuple(hypotheses); obj._quarantined = tuple(qs); obj._events = tuple(es)
            require(obj.checkpoint() == raw, 'INTEGRATED_COLD_BYTES')
            return obj
        except (ValueError, TypeError, KeyError, UnicodeError, AttributeError, IndexError) as exc:
            raise ValueError('CKAD_INTEGRATED_CHECKPOINT_REJECTED') from exc
