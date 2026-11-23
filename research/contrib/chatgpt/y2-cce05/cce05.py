"""CCE05: bounded online predictive-suffix cell birth and cold checkpoint.

Only public observations/actions enter the learner. Active cells are selected
by online prequential improvement against shorter public-history predictors.
This tests learned predictive contexts, NOT autonomous latent-world discovery.
"""
from __future__ import annotations
import hashlib
import json
import math

SCHEMA = 'yggdrasil.y2.cce05.v1'
DEPTH = 3
MAX_CELLS_PER_ACTION = 64
EPISODES = 192
HORIZON = 24


def bits(values, allowed, name):
    if type(values) is not tuple or any(type(v) is not int or v not in allowed for v in values):
        raise ValueError('CCE05_INVALID_' + name)


def check_episode(obs, actions):
    bits(obs, (0, 1), 'OBS')
    bits(actions, (0, 1, 2), 'ACTIONS')
    if len(obs) != len(actions) + 1 or not actions:
        raise ValueError('CCE05_EPISODE_LENGTH')


def key_for(action, pair_history, depth):
    return (action, tuple(pair_history[-depth:]) if depth else ())


def posterior(pair):
    return (pair[1] + 1) / (pair[0] + pair[1] + 2)


class PredictiveEcology:
    def __init__(self):
        self.counts = {}
        self.gains = {}
        self.events = 0
        self.episodes = 0
        self.selected = {}
        self.frozen = False

    def _prob(self, key):
        return posterior(self.counts.get(key, (0, 0)))

    def observe_episode(self, obs, actions):
        check_episode(obs, actions)
        if self.frozen or self.episodes >= EPISODES or len(actions) != HORIZON:
            raise ValueError('CCE05_FROZEN_OR_BUDGET')
        prior = []
        for t, action in enumerate(actions):
            y = obs[t + 1]
            maximum = min(DEPTH, len(prior))
            keys = [key_for(action, prior, k) for k in range(maximum + 1)]
            predictions = [self._prob(k) for k in keys]
            for depth in range(1, len(keys)):
                cell = keys[depth]
                self.gains[cell] = self.gains.get(cell, 0.0) + (predictions[depth - 1] - y) ** 2 - (predictions[depth] - y) ** 2
            for key in keys:
                pair = self.counts.setdefault(key, [0, 0])
                pair[y] += 1
            prior.append((action, y))
            self.events += 1
        self.episodes += 1

    def freeze(self):
        if self.frozen or self.episodes != EPISODES or self.events != EPISODES * HORIZON:
            raise ValueError('CCE05_INCOMPLETE_TRAINING')
        for action in range(3):
            admitted = []
            for (act, context), counts in self.counts.items():
                if act != action or not context:
                    continue
                n = sum(counts)
                parent = (action, context[1:])
                gain = self.gains.get((act, context), 0.0)
                if (n >= 12 and gain >= max(1.5, 0.02 * n)
                        and abs(posterior(counts) - self._prob(parent)) >= 0.08):
                    admitted.append((gain, (act, context)))
            admitted.sort(key=lambda item: (-item[0], item[1]))
            for _, key in admitted[:MAX_CELLS_PER_ACTION]:
                self.selected[key] = self.counts[key][:]
        self.counts = {key: value for key, value in self.counts.items() if not key[1] or key in self.selected}
        self.gains = {}
        self.frozen = True

    def predict(self, observations, past_actions, action, mode='cce'):
        bits(observations, (0, 1), 'OBS')
        bits(past_actions, (0, 1, 2), 'ACTIONS')
        if not self.frozen or len(observations) != len(past_actions) + 1 or type(action) is not int or action not in (0, 1, 2) or mode not in ('cce', 'depth1', 'depth3', 'iid'):
            raise ValueError('CCE05_PREDICTION_INVALID')
        if mode == 'iid':
            return 0.5
        history = tuple(zip(past_actions, observations[1:]))
        if mode == 'depth1':
            key = key_for(action, history, 1) if history else (action, ())
            return self._prob(key)
        if mode == 'depth3':
            key = key_for(action, history, min(3, len(history)))
            return self._prob(key)
        for depth in range(min(DEPTH, len(history)), 0, -1):
            key = key_for(action, history, depth)
            if key in self.selected:
                return posterior(self.selected[key])
        return self._prob((action, ()))

    def snapshot(self):
        if not self.frozen:
            raise ValueError('CCE05_NOT_FROZEN')
        data = {'schema': SCHEMA, 'episodes': self.episodes, 'events': self.events,
                'entries': [[action, [list(pair) for pair in context], counts[0], counts[1],
                             (action, context) in self.selected]
                            for (action, context), counts in sorted(self.counts.items())]}
        raw = json.dumps(data, sort_keys=True, separators=(',', ':')).encode('ascii')
        return b'CCE05.' + hashlib.sha256(raw).hexdigest().encode('ascii') + b'.' + raw

    @classmethod
    def restore(cls, payload):
        if type(payload) is not bytes:
            raise ValueError('CCE05_BAD_SNAPSHOT')
        parts = payload.split(b'.', 2)
        if len(parts) != 3 or parts[0] != b'CCE05' or len(parts[1]) != 64 or hashlib.sha256(parts[2]).hexdigest().encode('ascii') != parts[1]:
            raise ValueError('CCE05_BAD_SNAPSHOT')
        try:
            data = json.loads(parts[2])
            if type(data) is not dict or set(data) != {'schema', 'episodes', 'events', 'entries'} or data['schema'] != SCHEMA or data['episodes'] != EPISODES or data['events'] != EPISODES * HORIZON or type(data['entries']) is not list:
                raise ValueError('CCE05_BAD_SCHEMA')
            obj = cls()
            per_action = [0] * 3
            for record in data['entries']:
                if type(record) is not list or len(record) != 5:
                    raise ValueError('CCE05_BAD_ENTRY')
                action, pairs, zero, one, selected = record
                if type(action) is not int or action not in (0, 1, 2) or type(pairs) is not list or len(pairs) > DEPTH or type(selected) is not bool or any(type(n) is not int or not 0 <= n <= EPISODES * HORIZON for n in (zero, one)):
                    raise ValueError('CCE05_BAD_ENTRY')
                if any(type(pair) is not list or len(pair) != 2 or type(pair[0]) is not int or pair[0] not in (0, 1, 2) or type(pair[1]) is not int or pair[1] not in (0, 1) for pair in pairs):
                    raise ValueError('CCE05_BAD_CONTEXT')
                context = tuple(tuple(pair) for pair in pairs)
                key = (action, context)
                if key in obj.counts or (not context and selected) or (context and not selected) or (selected and zero + one < 12):
                    raise ValueError('CCE05_DUPLICATE_OR_INVALID_SELECTION')
                obj.counts[key] = [zero, one]
                if selected:
                    per_action[action] += 1
                    obj.selected[key] = [zero, one]
            if len(obj.counts) > 3 + 3 * MAX_CELLS_PER_ACTION or any(x > MAX_CELLS_PER_ACTION for x in per_action) or any((a, ()) not in obj.counts for a in range(3)) or sum(sum(obj.counts[a, ()]) for a in range(3)) != EPISODES * HORIZON:
                raise ValueError('CCE05_TOTAL_INVALID')
            obj.episodes = EPISODES
            obj.events = EPISODES * HORIZON
            obj.frozen = True
            return obj
        except (ValueError, TypeError, KeyError, UnicodeError) as exc:
            raise ValueError('CCE05_BAD_SNAPSHOT') from exc


class FullSuffixTable:
    """Fully trained unconstrained history-table controls on identical data."""
    def __init__(self, depth):
        if type(depth) is not int or depth not in (1, 3):
            raise ValueError('CCE05_BASELINE_DEPTH_INVALID')
        self.depth = depth
        self.counts = {}
        self.episodes = 0

    def observe_episode(self, obs, actions):
        check_episode(obs, actions)
        if self.episodes >= EPISODES or len(actions) != HORIZON:
            raise ValueError('CCE05_BASELINE_BUDGET')
        pairs = []
        for i, action in enumerate(actions):
            for depth in set((0, min(self.depth, len(pairs)))):
                key = key_for(action, pairs, min(depth, len(pairs)))
                cell = self.counts.setdefault(key, [0, 0])
                cell[obs[i + 1]] += 1
            pairs.append((action, obs[i + 1]))
        self.episodes += 1

    def predict(self, obs, actions, new_action):
        bits(obs, (0, 1), 'OBS')
        bits(actions, (0, 1, 2), 'ACTIONS')
        if self.episodes != EPISODES or len(obs) != len(actions) + 1 or type(new_action) is not int or new_action not in (0, 1, 2):
            raise ValueError('CCE05_BASELINE_UNTRAINED')
        pairs = tuple(zip(actions, obs[1:]))
        key = key_for(new_action, pairs, min(self.depth, len(pairs)))
        if key not in self.counts:
            key = (new_action, ())
        return posterior(self.counts[key])
