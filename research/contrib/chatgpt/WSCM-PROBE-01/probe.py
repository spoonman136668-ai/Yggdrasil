"""Witness-pinned structural diagnostic; source-free research, no regime labels.

A two-state exact Bayesian filter over one *real* archived native transition
repair. Unlike W16 loss routing, the evidence is the likelihood of the
actually intervened-upon public transition, never historical error ranking.
This intentionally matches a conventional two-state Bayes HMM, not a claim of
novel Bayesian inference or of learned memory improvements.
"""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
import json

from yggdrasil.native_episode_experience import NativeEpisodeExperience

SCHEMA = 'yggdrasil.wscm.probe01.v1'
HAZARD = Fraction(1, 16)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True, allow_nan=False).encode('ascii')


def bit(x):
    if type(x) is not int or x not in (0, 1):
        raise ValueError('PROBE_PUBLIC_BIT')
    return x


def ratio(x):
    return [x.numerator, x.denominator]


def version_source(versioned, identifier):
    matching = [v for v in versioned.versions() if v['version_id'] == identifier]
    if len(matching) != 1:
        raise ValueError('PROBE_REPAIR_CUSTODY')
    entry = matching[0]
    if entry['slot'] not in (0, 1) or entry['action'] not in (0, 1):
        raise ValueError('PROBE_REPAIR_ADDRESS')
    a, b = entry['old_counts']
    c, d = entry['reset_counts']
    if a + b < 12 or c + d != 3:
        raise ValueError('PROBE_REPAIR_COUNTS')
    return entry, Fraction(b + 1, a + b + 2), Fraction(d + 1, c + d + 2)


class WitnessCausalProbe:
    """Immutable readout-and-observation wrapper; never gets regime labels."""
    __slots__ = ('_versioned', '_repair_id', '_old', '_new', '_slot', '_action',
                 '_posterior_old', '_evidence', '_abstentions')

    def __init__(self, versioned, repair_id, *, posterior=Fraction(1,2),
                 evidence=0, abstentions=0):
        rec, old, new = version_source(versioned, repair_id)
        if (type(posterior) is not Fraction or not 0 <= posterior <= 1 or
                type(evidence) is not int or evidence < 0 or
                type(abstentions) is not int or abstentions < 0):
            raise ValueError('PROBE_STATE')
        if old == new:
            raise ValueError('PROBE_UNIDENTIFIABLE_REPAIR')
        self._versioned = versioned
        self._repair_id = repair_id
        self._old, self._new = old, new
        self._slot, self._action = rec['slot'], rec['action']
        self._posterior_old = posterior
        self._evidence = evidence
        self._abstentions = abstentions

    @property
    def original_native(self):
        return self._versioned.original_native

    @property
    def posterior_old(self):
        return self._posterior_old

    @property
    def counts(self):
        return (self._evidence, self._abstentions)

    def _context(self, view):
        if type(view) is not tuple or len(view) != 2:
            raise ValueError('PROBE_PUBLIC_VIEW')
        bits = tuple(bit(v) for v in view)
        projection = self.original_native._projection
        if projection is None:
            raise ValueError('PROBE_NO_PROJECTION')
        return bits[projection]

    def hypotheses(self, view, action):
        slot = self._context(view)
        action = bit(action)
        if slot == self._slot and action == self._action:
            return self._old, self._new
        shared = self.original_native.forecast(view, action, full=True)
        return shared, shared

    def choose(self, view):
        """Maximize observable old/new contrast, abstain if zero.

        This is an action proposal using only the publicly known context and
        actual historical repair hypotheses; no target-law or phase signal.
        """
        contrasts = [abs(self.hypotheses(view, a)[0] - self.hypotheses(view, a)[1])
                     for a in (0, 1)]
        action = int(contrasts[1] > contrasts[0])
        return action, contrasts[action] > 0

    def forecast(self, view, action):
        old, new = self.hypotheses(view, action)
        if old == new:
            return old
        prior = (1 - HAZARD) * self._posterior_old + HAZARD * (1 - self._posterior_old)
        return prior * old + (1 - prior) * new

    def witness(self, identifier, views, row):
        if type(views) is not tuple or len(views) != 2:
            raise ValueError('PROBE_PAIRED_VIEWS')
        public_view = views[0]
        action, informative = self.choose(public_view)
        if (type(row) is not dict or set(row) != {'s1','x1','s2','x2','y'}
                or bit(row['x1']) != action or bit(row['s2']) not in (0,1)
                or any(bit(row[k]) not in (0,1) for k in ('s1','x2','y'))):
            raise ValueError('PROBE_ACTION_OR_ROW')
        old,new = self.hypotheses(public_view, action)
        native_before = self.original_native
        updated = self._versioned.observe(identifier, views, row)
        if updated is self._versioned:
            raise ValueError('PROBE_NO_NEW_WITNESS')
        # Exactly one new source-native event, with no changed source history.
        if (len(updated.original_native._ledger) != len(native_before._ledger) + 1
                or updated.original_native._ledger[-1][0] != identifier
                or updated.original_native._ledger[:-1] != native_before._ledger):
            raise ValueError('PROBE_SOURCE_DRIFT')
        post = self._posterior_old
        if informative:
            prior = (1 - HAZARD) * post + HAZARD * (1 - post)
            obs = row['s2']
            lo = old if obs else 1-old
            ln = new if obs else 1-new
            total = prior * lo + (1-prior) * ln
            if total <= 0:
                raise ValueError('PROBE_ZERO_LIKELIHOOD')
            post = prior * lo / total
        return WitnessCausalProbe(updated, self._repair_id, posterior=post,
                                  evidence=self._evidence+int(informative),
                                  abstentions=self._abstentions+int(not informative))

    def checkpoint(self):
        native_raw, version_manifest = self._versioned.checkpoint()
        state = canonical({'schema':SCHEMA,
                           'native_sha256':sha256(native_raw).hexdigest(),
                           'version_manifest_sha256':sha256(version_manifest).hexdigest(),
                           'repair_id':self._repair_id,
                           'posterior_old':ratio(self._posterior_old),
                           'evidence':self._evidence,
                           'abstentions':self._abstentions})
        return native_raw, version_manifest, state

    @classmethod
    def restore(cls, native_raw, version_manifest, raw, version_type, *,
                expected_state_sha256):
        if (type(raw) is not bytes or len(raw)>2048 or len(raw)==0
                or type(expected_state_sha256) is not str or len(expected_state_sha256)!=64
                or sha256(raw).hexdigest()!=expected_state_sha256):
            raise ValueError('PROBE_COLD_INPUT_OR_PIN')
        try:
            state = json.loads(raw)
        except (ValueError, UnicodeError) as exc:
            raise ValueError('PROBE_COLD_PARSE') from exc
        if (type(state) is not dict or set(state) !=
            {'schema','native_sha256','version_manifest_sha256','repair_id',
             'posterior_old','evidence','abstentions'}
            or state['schema'] != SCHEMA or canonical(state) != raw
            or state['native_sha256'] != sha256(native_raw).hexdigest()
            or state['version_manifest_sha256'] != sha256(version_manifest).hexdigest()):
            raise ValueError('PROBE_COLD_CUSTODY')
        pair = state['posterior_old']
        if (type(pair) is not list or len(pair)!=2 or
            any(type(v) is not int for v in pair) or pair[1]<=0):
            raise ValueError('PROBE_COLD_POSTERIOR')
        restored_version = version_type.restore(native_raw,version_manifest)
        candidate = cls(restored_version, state['repair_id'],
                        posterior=Fraction(*pair), evidence=state['evidence'],
                        abstentions=state['abstentions'])
        if candidate.checkpoint() != (native_raw,version_manifest,raw):
            raise ValueError('PROBE_COLD_NONDETERMINISM')
        return candidate
