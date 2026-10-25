"""R9 public-feedback noise-calibrated, independent-evidence causal belief gating.

Additive source-only hypothesis. Immutable R7/R8 fit source remains the parent.
Known limits: supplied causal candidate/low-dimensional observation-error model,
fixed change-prior odds, no independent original-world first-use or Pareto claim.
"""
from __future__ import annotations
import hashlib
import json
import math
from research.native.itd02.r7.learner import canon
from research.native.itd02.r8.revision import RevisionCells, _step

SCHEMA = 'yggdrasil.itd02.r9.independent-evidence-local-gate.v1'
CALIBRATION = 64
DISCOVERY = 32
VALIDATION_BUDGET = 48
PRIOR_ODDS = 0.0001

class EvidenceCells:
    def __init__(self, original_r7_checkpoint, world, action, calibration_action=0):
        if type(world) is not str or not world or len(world) > 60 or type(action) is not int or action not in (0, 1, 2):
            raise ValueError('R9_INVALID_CONTEXT')
        self.r8 = RevisionCells(original_r7_checkpoint)
        if world not in self.r8.base.models:
            raise ValueError('R9_UNKNOWN_WORLD')
        if type(calibration_action) is not int or calibration_action not in (0, 1, 2) or calibration_action == action:
            raise ValueError('R9_CALIBRATION_ACTION_MUST_BE_INDEPENDENT')
        self.world = world
        self.action = action
        self.calibration_action = calibration_action
        self.stage = 'calibration'
        self.calibration_rows = []
        self.calibration_mismatches = 0
        self.discovery_rows = []
        self.validation_rows = []
        self.noise = None
        self.log_odds = math.log(PRIOR_ODDS)
        self.mode_changes = 0
        self.informative = 0

    def stable(self, before):
        return self.r8.base.step(self.world, self.action, before)

    def candidate(self, before):
        if self.stage != 'validation':
            raise ValueError('R9_CANDIDATE_NOT_FROZEN')
        entry = self.r8.fast[self.world][str(self.action)]
        if entry is None:
            raise ValueError('R9_NO_CANDIDATE')
        return _step(entry, before)

    def _public(self, before, after):
        if type(before) is not int or not 0 <= before < 256 or type(after) is not int or not 0 <= after < 256:
            raise ValueError('R9_INVALID_PUBLIC_EFFECT')

    def calibrate(self, before, after):
        self._public(before, after)
        if self.stage != 'calibration' or len(self.calibration_rows) >= CALIBRATION or before in [x for x, _ in self.calibration_rows]:
            raise ValueError('R9_CALIBRATION_INVALID_PHASE_OR_DUPLICATE')
        wrong = self.r8.base.step(self.world, self.calibration_action, before) != after
        self.calibration_rows.append([before, after])
        self.calibration_mismatches += int(wrong)
        if len(self.calibration_rows) == CALIBRATION:
            # Beta(1,7) public-feedback error prior: FIT calibration estimates error.
            self.noise = (self.calibration_mismatches + 1) / (CALIBRATION + 8)
            if not 0 < self.noise < 0.5:
                raise ValueError('R9_CALIBRATED_SIGNAL_NOT_INFORMATIVE')
            self.stage = 'discovery'

    def discover(self, before, after):
        self._public(before, after)
        if (self.stage != 'discovery' or len(self.discovery_rows) >= DISCOVERY
            or before in [x for x, _ in self.discovery_rows]
            or before in [x for x, _ in self.calibration_rows]):
            raise ValueError('R9_DISCOVERY_INVALID_PHASE_OR_DUPLICATE')
        # Original unmodified R8 code, chosen public feedback only.
        self.r8.observe(self.world, self.action, before, after)
        self.discovery_rows.append([before, after])
        if len(self.discovery_rows) == DISCOVERY:
            if self.r8.mode[self.world][str(self.action)] != 'fast':
                raise ValueError('R9_NO_DISCOVERED_ALTERNATIVE')
            # DISCOVERY rows train proposal, but they NEVER update posterior odds.
            self.stage = 'validation'

    def predict(self, before):
        self._public(before, 0)
        if self.stage != 'validation':
            raise ValueError('R9_VALIDATION_NOT_INITIALIZED')
        return self.candidate(before) if self.log_odds >= 0 else self.stable(before)

    def selected_query(self, unavailable):
        if self.stage != 'validation' or type(unavailable) not in (set, list, tuple) or any(type(i) is not int or not 0 <= i < 256 for i in unavailable):
            raise ValueError('R9_INVALID_QUERY_UNIVERSE')
        previous = set(unavailable) | {x for x, _ in self.calibration_rows + self.discovery_rows + self.validation_rows}
        remaining = (i for i in range(256) if i not in previous)
        candidates = [x for x in remaining if self.stable(x) != self.candidate(x)]
        if candidates:
            return candidates[0]
        return next((x for x in range(256) if x not in previous), None)

    def observe(self, before, after):
        self._public(before, after)
        if (self.stage != 'validation' or len(self.validation_rows) >= VALIDATION_BUDGET
            or before in [x for x, _ in self.calibration_rows + self.discovery_rows + self.validation_rows]):
            raise ValueError('R9_VALIDATION_INVALID_PHASE_OR_DUPLICATE')
        old_choice = self.log_odds >= 0
        old = self.stable(before)
        new = self.candidate(before)
        next_odds = self.log_odds
        seen = self.informative
        # Held-out, actually observed chosen-action feedback -- no re-use of FIT.
        if old != new:
            if after == new:
                next_odds += math.log((1 - self.noise) / self.noise)
                seen += 1
            elif after == old:
                next_odds -= math.log((1 - self.noise) / self.noise)
                seen += 1
            # If neither hypothesis predicts the observation, neither gains evidence.
        self.validation_rows.append([before, after])
        self.log_odds = next_odds
        self.informative = seen
        if (self.log_odds >= 0) != old_choice:
            self.mode_changes += 1

    def checkpoint(self):
        data = dict(schema=SCHEMA, r8=self.r8.checkpoint().decode('utf-8'),
                    world=self.world, action=self.action, calibration_action=self.calibration_action, stage=self.stage,
                    calibration_rows=self.calibration_rows, calibration_mismatches=self.calibration_mismatches,
                    discovery_rows=self.discovery_rows, validation_rows=self.validation_rows,
                    noise=self.noise, log_odds=self.log_odds,
                    mode_changes=self.mode_changes, informative=self.informative)
        raw = canon(data)
        if len(raw) > 350000:
            raise ValueError('R9_CHECKPOINT_OVERSIZE')
        return canon(dict(data=data, sha256=hashlib.sha256(raw).hexdigest()))

    @classmethod
    def restore(cls, raw):
        try:
            if type(raw) is not bytes or not 0 < len(raw) < 350000:
                raise ValueError('R9_CHECKPOINT_SIZE')
            outer = json.loads(raw)
            if set(outer) != {'data', 'sha256'} or type(outer['data']) is not dict:
                raise ValueError('R9_CHECKPOINT_ENVELOPE')
            data = outer['data']
            keys = {'schema','r8','world','action','calibration_action','stage','calibration_rows','calibration_mismatches','discovery_rows','validation_rows','noise','log_odds','mode_changes','informative'}
            if (set(data) != keys or data['schema'] != SCHEMA or
                hashlib.sha256(canon(data)).hexdigest() != outer['sha256']):
                raise ValueError('R9_CHECKPOINT_AUTH')
            r8 = RevisionCells.restore(data['r8'].encode())
            obj = cls(r8.original_checkpoint, data['world'], data['action'], data['calibration_action'])
            if (data['stage'] not in ('calibration','discovery','validation') or
                type(data['calibration_mismatches']) is not int or
                type(data['mode_changes']) is not int or
                type(data['informative']) is not int or
                not 0 <= data['mode_changes'] <= data['informative'] <= VALIDATION_BUDGET or
                not 0 <= data['calibration_mismatches'] <= CALIBRATION or
                type(data['log_odds']) not in (float,int) or not math.isfinite(data['log_odds'])):
                raise ValueError('R9_CHECKPOINT_MODEL_INVALID')
            for field, maxsize in [('calibration_rows',CALIBRATION),('discovery_rows',DISCOVERY),('validation_rows',VALIDATION_BUDGET)]:
                rows = data[field]
                if (type(rows) is not list or len(rows) > maxsize or len(rows) != len({x for x, _ in rows}) or
                    any(type(row) is not list or len(row) != 2 or any(type(v) is not int or not 0 <= v < 256 for v in row) for row in rows)):
                    raise ValueError('R9_CHECKPOINT_ROWS_INVALID')
            if ((data['stage'] == 'calibration' and (len(data['calibration_rows']) >= CALIBRATION or data['noise'] is not None or data['discovery_rows'] or data['validation_rows'])) or
                (data['stage'] in ('discovery','validation') and len(data['calibration_rows']) != CALIBRATION) or
                (data['stage'] == 'discovery' and (len(data['discovery_rows']) >= DISCOVERY or data['validation_rows'])) or
                (data['stage'] == 'validation' and len(data['discovery_rows']) != DISCOVERY)):
                raise ValueError('R9_CHECKPOINT_PHASE_DRIFT')
            if data['noise'] is not None and (type(data['noise']) not in (float,int) or not 0 < data['noise'] < 0.5):
                raise ValueError('R9_CHECKPOINT_NOISE_INVALID')
            if (data['stage'] == 'validation' and (r8.mode[obj.world][str(obj.action)] != 'fast' or
                r8.online_events != DISCOVERY or data['noise'] != (data['calibration_mismatches']+1)/(CALIBRATION+8))):
                raise ValueError('R9_CHECKPOINT_LEARNER_MISMATCH')
            obj.r8 = r8
            for field in ('stage','calibration_rows','calibration_mismatches','discovery_rows','validation_rows','noise','log_odds','mode_changes','informative'):
                setattr(obj, field, data[field])
            return obj
        except (ValueError, KeyError, TypeError, OverflowError, AttributeError) as err:
            raise ValueError('R9_CHECKPOINT_REJECTED') from err
