"""Opt-in readout invalidation after a witnessed model-class contradiction.

Preserves the disproved native state; does not invent replacement consequences,
erase old failures, authenticate a source, or learn a larger relation family.
"""
import json
from yggdrasil.native_context_basis import canonical, digest, pin, require, SOURCE_MODE
from yggdrasil.native_context_accumulator import NativeContextAccumulator, MAX_BYTES
from yggdrasil.public_causal_cells import PublicCausalCells

SCHEMA = 'yggdrasil.ckad.native-context-quarantine.v1'


class NativeContextQuarantine:
    __slots__ = ('_native', '_failures')

    def __init__(self, native=None):
        require(native is None or type(native) is NativeContextAccumulator, 'QUARANTINE_NATIVE_TYPE')
        self._native = NativeContextAccumulator() if native is None else native
        self._failures = ('',) * 16

    def stage_checked_update(self, address, records, expected_source_sha256, **kwargs):
        slot = PublicCausalCells._address(address, kwargs.get('retained', False))
        require(not self._failures[slot], 'QUARANTINED_REQUIRES_EXPLICIT_REPAIR')
        try:
            updated = self._native.stage_update(address, records, expected_source_sha256, **kwargs)
        except ValueError as exc:
            if str(exc) not in ('CKAD_NATIVE_MODEL_CLASS_INADEQUATE',
                                'CKAD_NATIVE_CUMULATIVE_MODEL_INADEQUATE'):
                raise
            # Source/type/pin/public-row validation precedes these particular
            # exceptions. Only admitted contradictory observations invalidate.
            candidate = NativeContextQuarantine(self._native)
            candidate._failures = (self._failures[:slot] + (expected_source_sha256,)
                                   + self._failures[slot + 1:])
            return candidate
        candidate = NativeContextQuarantine(updated)
        candidate._failures = self._failures
        return candidate

    def predict(self, address, context, action, *, retained=False):
        # Validate all normal query fields even when readout is quarantined.
        answer = self._native.predict(address, context, action, retained=retained)
        slot = PublicCausalCells._address(address, retained)
        return None if self._failures[slot] else answer

    def predict_partial(self, address, value_mask, known_mask, action, *, retained=False):
        answer = self._native.predict_partial(address,value_mask,known_mask,action,retained=retained)
        slot = PublicCausalCells._address(address, retained)
        return None if self._failures[slot] else answer

    def checkpoint(self):
        raw = canonical({'schema':SCHEMA,'native_accumulator_ascii':self._native.checkpoint().decode('ascii'),
            'contradiction_batch_sha256':self._failures,'source_mode':SOURCE_MODE,
            'accepted_native':False,'scientific_pass':False})
        require(len(raw)<=MAX_BYTES,'QUARANTINE_CHECKPOINT_CAPACITY')
        return raw

    @property
    def checkpoint_sha256(self):
        return digest(self.checkpoint())

    @classmethod
    def restore(cls, raw, expected_sha256):
        require(type(raw) is bytes and 0<len(raw)<=MAX_BYTES and pin(expected_sha256)
                and digest(raw)==expected_sha256,'QUARANTINE_CHECKPOINT_PIN')
        def unique(pairs):
            d={}
            for k,v in pairs:
                require(k not in d,'QUARANTINE_DUPLICATE_KEY');d[k]=v
            return d
        try:
            d=json.loads(raw.decode('ascii'),object_pairs_hook=unique)
            require(type(d) is dict and set(d)=={'schema','native_accumulator_ascii',
                    'contradiction_batch_sha256','source_mode','accepted_native','scientific_pass'}
                    and d['schema']==SCHEMA and d['source_mode']==SOURCE_MODE
                    and d['accepted_native'] is False and d['scientific_pass'] is False
                    and canonical(d)==raw,'QUARANTINE_CHECKPOINT_CONTRACT')
            native=d['native_accumulator_ascii'].encode('ascii')
            candidate=cls(NativeContextAccumulator.restore(native,digest(native)))
            flags=d['contradiction_batch_sha256']
            require(type(flags) is list and len(flags)==16 and all(x=='' or pin(x) for x in flags),
                    'QUARANTINE_FAILURE_PINS')
            candidate._failures=tuple(flags)
            require(candidate.checkpoint()==raw,'QUARANTINE_COLD_BYTES')
            return candidate
        except (ValueError,TypeError,KeyError,UnicodeError,AttributeError) as exc:
            raise ValueError('CKAD_NATIVE_QUARANTINE_CHECKPOINT_REJECTED') from exc
