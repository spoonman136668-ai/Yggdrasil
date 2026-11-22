"""CAID-05: read-only, source-pinned native causal history support.

Only accepted NativeEpisodeExperience public witness tuples are summarized.
These are action-conditioned observational sufficient statistics, NOT a
reconstructed hidden regime, a causal graph, a replacement learner, or policy
admission. An unobserved intervention must abstain rather than invent effects.
Frozen source boundary: Yggdrasil PR #1278 head 86264b41a08d49f558418c0fba367f3a2636befa.
"""
from __future__ import annotations

import hashlib
import json
from collections import defaultdict

SCHEMA = "yggdrasil.caid05.native-public-history-readout.v1"
NATIVE_EPISODE_GIT_BLOB_SHA1 = "5a18b00a4c4131526e71f51d63dfd9eb9471c81e"
MAX_NATIVE_DEFAULT = 1024
MAX_NATIVE_GROWN = 1152


def _bit(value, label):
    if type(value) is not int or value not in (0, 1):
        raise ValueError("CAID05_" + label)
    return value


def _pin(value):
    return type(value) is str and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def _view(value):
    if type(value) is not tuple or len(value) != 2:
        raise ValueError("CAID05_PUBLIC_VIEW")
    return tuple(_bit(x, "PUBLIC_VIEW_BIT") for x in value)


def _ledger_item(event):
    if type(event) is not tuple or len(event) != 6:
        raise ValueError("CAID05_NATIVE_EVENT_SHAPE")
    identifier, views, first, state, second, reward = event
    if not _pin(identifier):
        raise ValueError("CAID05_NATIVE_EVENT_PIN")
    if type(views) is not tuple or len(views) != 2:
        raise ValueError("CAID05_NATIVE_PAIRED_VIEWS")
    pair = tuple(_view(v) for v in views)
    return identifier, pair, _bit(first, "FIRST_ACTION"), _bit(state, "PUBLIC_NEXT_STATE"), _bit(second, "SECOND_ACTION"), _bit(reward, "PUBLIC_OUTCOME")


class PublicHistorySupport:
    """A read-only sufficient-statistic readout, NOT a context-switching agent.

    Supports exact public intervention keys. Does not infer a previously
    unseen action effect from the current observation or unspecified priors.
    A Beta(1,1) mean is returned only after at least one witnessed sample;
    it is a conditional reward estimate, not an identified causal effect.
    """

    def __init__(self, ledger, projection, *, source_checkpoint_sha256):
        if type(ledger) is not tuple or not 8 <= len(ledger) <= MAX_NATIVE_GROWN:
            raise ValueError("CAID05_NATIVE_WITNESS_COUNT")
        if type(projection) is not int or projection not in (0, 1):
            raise ValueError("CAID05_PROJECTION_NOT_LEARNED")
        if not _pin(source_checkpoint_sha256):
            raise ValueError("CAID05_CHECKPOINT_PIN")
        self.source_checkpoint_sha256 = source_checkpoint_sha256
        self.projection = projection
        self.observed = len(ledger)
        self.ambiguous = 0
        transitions = defaultdict(lambda: [0, 0])
        rewards = defaultdict(lambda: [0, 0])
        seen = set()
        for raw in ledger:
            identifier, views, x1, s2, x2, y = _ledger_item(raw)
            if identifier in seen:
                raise ValueError("CAID05_DUPLICATE_WITNESS_ID")
            seen.add(identifier)
            context1 = views[0][projection]
            context2 = views[1][projection]
            if context1 != context2:
                self.ambiguous += 1
                continue
            transitions[(context1, x1)][s2] += 1
            rewards[(context1, x1, s2, x2)][y] += 1
        self._transition = {k: tuple(v) for k, v in transitions.items()}
        self._reward = {k: tuple(v) for k, v in rewards.items()}

    @classmethod
    def from_native(cls, native, expected_checkpoint_sha256):
        """Require the *real* native admitted reader and exact checkpoint bytes.

        Cannot construct source authority from an arbitrary object with a
        matching private _ledger attribute. The native class remains owner.
        """
        from yggdrasil.native_episode_experience import NativeEpisodeExperience
        if type(native) is not NativeEpisodeExperience:
            raise TypeError("CAID05_NATIVE_READER_REQUIRED")
        checkpoint = native.checkpoint()
        if not _pin(expected_checkpoint_sha256) or hashlib.sha256(checkpoint).hexdigest() != expected_checkpoint_sha256:
            raise ValueError("CAID05_SOURCE_CHECKPOINT_MISMATCH")
        return cls(native._ledger, native._projection,
                   source_checkpoint_sha256=expected_checkpoint_sha256)

    @staticmethod
    def _mean(counts):
        if counts is None:
            return None
        fail, success = counts
        return (success + 1, fail + success + 2)

    def transition(self, public_view, first):
        view = _view(public_view)
        key = (view[self.projection], _bit(first, "FIRST_ACTION"))
        return self._mean(self._transition.get(key))

    def reward(self, public_view, first, next_state, second):
        view = _view(public_view)
        key = (view[self.projection], _bit(first, "FIRST_ACTION"),
               _bit(next_state, "PUBLIC_NEXT_STATE"), _bit(second, "SECOND_ACTION"))
        return self._mean(self._reward.get(key))

    def action_support(self, public_view, first, next_state):
        view = _view(public_view)
        prefix = (view[self.projection], _bit(first, "FIRST_ACTION"),
                  _bit(next_state, "PUBLIC_NEXT_STATE"))
        return tuple(sum(self._reward.get(prefix + (x2,), (0, 0))) for x2 in (0, 1))

    def document(self):
        return {
            "schema": SCHEMA,
            "native_source_checkpoint_sha256": self.source_checkpoint_sha256,
            "source_git_blob_sha1": NATIVE_EPISODE_GIT_BLOB_SHA1,
            "projection": self.projection,
            "observed_witnesses": self.observed,
            "ambiguous_context_witnesses": self.ambiguous,
            "transition_counts": [[*k, *v] for k, v in sorted(self._transition.items())],
            "reward_counts": [[*k, *v] for k, v in sorted(self._reward.items())],
            "mode": "read_only_witnessed_public_counts",
            "causal_graph_identified": False,
            "original_world_first_use": False,
            "native_accepted": False,
            "scientific_pass": False,
            "can_act": False,
        }

    @property
    def fingerprint(self):
        raw = json.dumps(self.document(), sort_keys=True, separators=(",", ":")).encode("ascii")
        return hashlib.sha256(raw).hexdigest()
