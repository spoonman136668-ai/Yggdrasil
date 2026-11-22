"""CPR-02 source-free confirmation monitor; no original model or automatic speciation.

The caller must certify probe independence, same intervention and split custody.
A source pin and monotonic sequence are NOT themselves that certification.
"""
from hashlib import sha256
import json

SCHEMA = 'yggdrasil.cpr02.causal-confirm.v1'
SCALE = 1_000_000


def _pin(value):
    return type(value) is str and len(value) == 64 and all(c in '0123456789abcdef' for c in value)


def _label(y):
    if type(y) is not int or y not in (0, 1):
        raise ValueError('CPR02_LABEL')
    return y


def _predictions(probabilities, names):
    if type(probabilities) is not dict or set(probabilities) != names:
        raise ValueError('CPR02_EXPERT_SET')
    if any(type(p) is not int or not 0 <= p <= SCALE for p in probabilities.values()):
        raise ValueError('CPR02_PROBABILITY')
    return dict(probabilities)


class CausalConfirmationMonitor:
    """Append-only advisory monitor over unmodified CPR-01 routing.

    Probe forecasts must be supplied at route time, before the probe label.
    No oracle regime labels or automatic action/learner/checkpoint mutation.
    """
    def __init__(self, router, *, probe_source_sha256):
        if not _pin(probe_source_sha256) or router.window != 8:
            raise ValueError('CPR02_CONFIGURATION')
        self.router = router
        self.probe_source_sha256 = probe_source_sha256
        self.steps = 0
        self.alarm_active = False
        self.alarm_step = 0
        self.confirmations = 0
        self.confirmed_total = 0
        self.last_probe_sequence = -1
        self._pending = None

    def route(self, probabilities, intervention_id, *, probe=None):
        if self._pending is not None:
            raise ValueError('CPR02_PENDING')
        if type(intervention_id) is not str or not intervention_id or len(intervention_id) > 128:
            raise ValueError('CPR02_INTERVENTION')
        names = set(self.router.history)
        primary = _predictions(probabilities, names)
        candidate = None
        if probe is not None:
            if type(probe) is not dict or set(probe) != {'sequence', 'source_sha256', 'intervention_id', 'probabilities'}:
                raise ValueError('CPR02_PROBE_FIELDS')
            seq = probe['sequence']
            if (type(seq) is not int or seq <= self.last_probe_sequence
                    or probe['source_sha256'] != self.probe_source_sha256
                    or probe['intervention_id'] != intervention_id):
                raise ValueError('CPR02_PROBE_CUSTODY')
            candidate = {'sequence': seq, 'probabilities': _predictions(probe['probabilities'], names)}
        decision = self.router.route(primary)
        self.steps += 1
        if decision['selected'] is not None:
            self.alarm_active = False
            self.confirmations = 0
        if decision['speciation_signal']:
            self.alarm_active = True
            self.alarm_step = self.steps
            self.confirmations = 0
        self._pending = candidate if candidate is not None else False
        return {'selected': decision['selected'], 'raw_alarm': bool(decision['speciation_signal']),
                'advisory_active': self.alarm_active, 'confirmed_change': False}

    def observe(self, primary_label, *, probe_label=None):
        if self._pending is None:
            raise ValueError('CPR02_UNMATCHED')
        y = _label(primary_label)
        pending = self._pending
        if (pending is False) != (probe_label is None):
            raise ValueError('CPR02_PROBE_PAIR')
        mismatch = None
        if pending is not False:
            py = _label(probe_label)
            mismatch = all((p if py == 0 else SCALE - p) > c.threshold
                           for c in self.router.calibrations
                           for p in [pending['probabilities'][c.name]])
        # All input validation above: bad input does not alter the sidecar.
        self.router.observe(y)
        self._pending = None
        confirmed = False
        if pending is not False:
            self.last_probe_sequence = pending['sequence']
            if self.alarm_active and self.steps > self.alarm_step:
                if mismatch:
                    self.confirmations += 1
                    if self.confirmations == 2:
                        self.confirmed_total += 1
                        confirmed = True
                        self.alarm_active = False
                        self.confirmations = 0
                else:
                    self.alarm_active = False
                    self.confirmations = 0
        return {'confirmed_change': confirmed, 'probe_mismatch': mismatch,
                'advisory_active': self.alarm_active}

    def checkpoint(self):
        if self._pending is not None:
            raise ValueError('CPR02_INFLIGHT')
        raw = self.router.checkpoint()
        state = {'schema': SCHEMA, 'base_checkpoint_hex': raw.hex(),
                 'base_checkpoint_sha256': sha256(raw).hexdigest(),
                 'probe_source_sha256': self.probe_source_sha256, 'steps': self.steps,
                 'alarm_active': self.alarm_active, 'alarm_step': self.alarm_step,
                 'confirmations': self.confirmations, 'confirmed_total': self.confirmed_total,
                 'last_probe_sequence': self.last_probe_sequence}
        return json.dumps(state, sort_keys=True, separators=(',', ':')).encode()

    @classmethod
    def restore(cls, raw, expected_sha256, *, base_router_cls, model_pins, probe_source_sha256):
        if type(raw) is not bytes or not _pin(expected_sha256) or sha256(raw).hexdigest() != expected_sha256:
            raise ValueError('CPR02_CHECKPOINT_PIN')
        try:
            state = json.loads(raw)
            if set(state) != {'schema', 'base_checkpoint_hex', 'base_checkpoint_sha256',
                              'probe_source_sha256', 'steps', 'alarm_active', 'alarm_step',
                              'confirmations', 'confirmed_total', 'last_probe_sequence'}:
                raise ValueError('CPR02_SCHEMA')
            if state['schema'] != SCHEMA or state['probe_source_sha256'] != probe_source_sha256:
                raise ValueError('CPR02_SOURCE_PIN')
            base = base_router_cls.restore(bytes.fromhex(state['base_checkpoint_hex']),
                                           state['base_checkpoint_sha256'], model_pins=model_pins)
            monitor = cls(base, probe_source_sha256=probe_source_sha256)
            for name in ('steps', 'alarm_step', 'confirmations', 'confirmed_total', 'last_probe_sequence'):
                value = state[name]
                if type(value) is not int:
                    raise ValueError('CPR02_COUNTER_TYPE')
                setattr(monitor, name, value)
            if (type(state['alarm_active']) is not bool or monitor.steps < 0
                    or not 0 <= monitor.alarm_step <= monitor.steps
                    or monitor.confirmations not in (0, 1)
                    or monitor.confirmed_total < 0 or monitor.last_probe_sequence < -1
                    or (not state['alarm_active'] and monitor.confirmations != 0)
                    or (state['alarm_active'] and monitor.alarm_step == 0)):
                raise ValueError('CPR02_STATE')
            monitor.alarm_active = state['alarm_active']
            if monitor.checkpoint() != raw:
                raise ValueError('CPR02_NONCANONICAL')
            return monitor
        except (TypeError, ValueError, KeyError, OverflowError) as exc:
            raise ValueError('CPR02_CHECKPOINT_INVALID') from exc
