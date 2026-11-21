"""CASP-02: one experimental source-free compositional readout, no model admission.

Store independently updated CASP-01 local causal capsules; at genuinely new public
cues, consult a shared posterior over 16 affine GF(2) action-consequence rules.
The disclosed hypothesis family is a modeling prior, not discovery of a new law.
"""
from fractions import Fraction
from math import gcd
import json

from capsule_memory_dev import CapsuleMemory, canonical, digest, bit, view_key

SCHEMA = 'yggdrasil.amalgam.casp02.compositional.v1'
HYPOTHESES = tuple((mask >> i) & 1 for mask in range(16) for i in range(4))


def affine_outcome(rule, cue, action):
    return (rule & 1) ^ (((rule >> 1) & 1) & action) ^ (
        ((rule >> 2) & 1) & cue[0]) ^ (((rule >> 3) & 1) & cue[1])


class CompositionalCapsules:
    """One prior, action-consequence evidence, and local recall; not a new owner."""
    def __init__(self, max_capsules=4, max_events=256, max_repairs=4):
        self.local = CapsuleMemory(max_capsules, max_events, max_repairs)
        self._shared_weights = [1] * 16

    def predict(self, cue, action):
        cue = view_key(cue)
        action = bit(action)
        if cue in self.local._cells:
            # Preserve old, independently trained local inference exactly.
            return self.local.predict(cue, action)
        expected = sum(w * affine_outcome(rule, cue, action)
                       for rule, w in enumerate(self._shared_weights))
        return Fraction(sum(self._shared_weights) + 14 * expected,
                        16 * sum(self._shared_weights))

    def observe(self, evidence_id, cue, action, outcome):
        cue = view_key(cue)
        action, outcome = bit(action), bit(outcome)
        changed = self.local.observe(evidence_id, cue, action, outcome)
        if changed:
            updated = [w * (15 if affine_outcome(rule, cue, action) == outcome else 1)
                       for rule, w in enumerate(self._shared_weights)]
            g = 0
            for w in updated:
                g = gcd(g, w)
            self._shared_weights = [w // g for w in updated]
        return changed

    def checkpoint(self):
        return canonical({'schema': SCHEMA, 'local_ascii': self.local.checkpoint().decode('ascii'),
                          'shared_weights': self._shared_weights})

    @classmethod
    def restore(cls, raw, expected_sha256):
        if (type(raw) is not bytes or len(raw) > 2**20 or
                type(expected_sha256) is not str or digest(raw) != expected_sha256):
            raise ValueError('CASP02_CHECKPOINT_PIN')
        try:
            doc = json.loads(raw)
            if set(doc) != {'schema', 'local_ascii', 'shared_weights'} or doc['schema'] != SCHEMA:
                raise ValueError('CASP02_SCHEMA')
            local_raw = doc['local_ascii'].encode('ascii')
            local = CapsuleMemory.restore(local_raw, digest(local_raw))
            rebuilt = cls(local.max_capsules, local.max_events, local.max_repairs)
            for identifier, cue, action, outcome in local._records:
                rebuilt.observe(identifier, cue, action, outcome)
            if rebuilt.checkpoint() != raw:
                raise ValueError('CASP02_RECOMPUTATION_OR_TAMPER')
        except (KeyError, UnicodeError, TypeError, json.JSONDecodeError) as exc:
            raise ValueError('CASP02_BAD_CHECKPOINT') from exc
        return rebuilt
