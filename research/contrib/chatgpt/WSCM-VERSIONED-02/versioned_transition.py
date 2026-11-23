"""Copy-on-write historical transition versions around original NativeEpisodeExperience.

Research adapter, not a global router. The authoritative native learner remains
unchanged: its repair still updates the live counter. Before counts become a
separate durable, source-validated immutable version at that witnessed write.
No scenario/regime labels, hidden world state, protected source calls or oracle
selection are accepted. Historical recall requires a real last-witness ID.
"""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
import json

from yggdrasil.native_episode_experience import NativeEpisodeExperience

SCHEMA = "yggdrasil.wscm.native-transition-versions.v1"
MAX_FROZEN_VERSIONS = 16
ROW_FIELDS = ("s1", "x1", "s2", "x2", "y")


def _canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def _pin(value):
    return (type(value) is str and len(value) == 64
            and all(ch in "0123456789abcdef" for ch in value))


def _counts(value):
    if (type(value) not in (list, tuple) or len(value) != 2
            or any(type(x) is not int or not 0 <= x <= 65535 for x in value)):
        raise ValueError("VERSIONED_COUNTS_INVALID")
    return tuple(value)


def _probability(value):
    a, b = _counts(value)
    return Fraction(b + 1, a + b + 2)


def _rebuild_source_versions(native):
    """Use source-native journals, verifying its true witnessed cell chronology."""
    if type(native) is not NativeEpisodeExperience:
        raise ValueError("VERSIONED_NATIVE_TYPE")
    locations = {event[0]: i for i, event in enumerate(native._ledger)}
    if len(locations) != len(native._ledger):
        raise ValueError("VERSIONED_LEDGER_DUPLICATE")
    versions = []
    previous_index = -1
    for record in native.info()["repairs"]:
        if record["target"] != "transition":
            continue  # terminal repair versions are not qualified
        slot, action = record["slot"], record["action"]
        if (type(slot) is not int or slot not in (0, 1)
                or type(action) is not int or action not in (0, 1)):
            raise ValueError("VERSIONED_ADDRESS_INVALID")
        evidence = record["evidence"]
        if (type(evidence) is not list or len(evidence) != 3
                or len(set(evidence)) != 3 or any(not _pin(x) for x in evidence)):
            raise ValueError("VERSIONED_REPAIR_EVIDENCE")
        indices = [locations.get(identifier) for identifier in evidence]
        if any(x is None for x in indices) or indices != sorted(indices):
            raise ValueError("VERSIONED_REPAIR_WITNESS")
        if indices[-1] <= previous_index:
            raise ValueError("VERSIONED_REPAIR_CHRONOLOGY")
        previous_index = indices[-1]
        majority = record["prior_majority"]
        old, reset = _counts(record["old_counts"]), _counts(record["new_counts"])
        if (type(majority) is not int or majority not in (0, 1)
                or sum(old) < 12 or old[majority] * 5 < 4 * sum(old)
                or sum(reset) != 3 or reset[1 - majority] != 3):
            raise ValueError("VERSIONED_REPAIR_STRUCTURE")
        for identifier in evidence:
            event = native._ids.get(identifier)
            if event is None or event[0] != identifier or len(event) != 6:
                raise ValueError("VERSIONED_REPAIR_IDENTITY")
            _, views, first, outcome, _second, _reward = event
            if (native._context(views) != slot or first != action
                    or outcome != 1 - majority):
                raise ValueError("VERSIONED_REPAIR_MISADDRESSED")
        # Original journal already freezes old counts. We create durable,
        # independent public readout identifiers for the copy-on-write branch.
        version_id = evidence[-1]
        versions.append({"version_id": version_id, "slot": slot, "action": action,
                         "old_counts": list(old), "reset_counts": list(reset),
                         "evidence": evidence.copy(), "last_ledger_index": indices[-1]})
        if len(versions) > MAX_FROZEN_VERSIONS:
            raise ValueError("VERSIONED_CAPACITY_FAIL_CLOSED")
    return versions


class VersionedNativeTransition:
    """Original native model plus bounded, witness-keyed immutable old versions.

    This preserves old functions at a sidecar write without changing the native
    repair path. No automatic regime identification or readout promotion.
    """
    __slots__ = ("_native", "_frozen")

    def __init__(self, native):
        if type(native) is not NativeEpisodeExperience:
            raise ValueError("VERSIONED_NATIVE_TYPE")
        self._native = native
        self._frozen = tuple(_rebuild_source_versions(native))

    @property
    def original_native(self):
        return self._native

    def observe(self, identifier, views, row):
        # Original immutable witness admission remains the sole trainer.
        revised = self._native.observe(identifier, views, row)
        if revised is self._native:
            return self  # same-ID identical replay cannot create a new version
        candidate = VersionedNativeTransition(revised)
        if candidate._frozen[:len(self._frozen)] != self._frozen:
            raise ValueError("VERSIONED_HISTORY_MUTATION")
        return candidate

    def versions(self):
        # Return copies to prevent a caller mutating our immutable old bank.
        return json.loads(_canonical(list(self._frozen)))

    def read_transition(self, public_view, first_action, *, version_id=None):
        if (type(public_view) is not tuple or len(public_view) != 2
                or any(type(bit) is not int or bit not in (0, 1)
                       for bit in public_view)
                or type(first_action) is not int or first_action not in (0, 1)):
            raise ValueError("VERSIONED_PUBLIC_ADDRESS")
        context = self._native._projection
        if context is None:
            raise ValueError("VERSIONED_PROJECTION_UNLEARNED")
        slot = public_view[context]
        if version_id is None:
            return self._native.forecast(public_view, first_action, full=True)
        if not _pin(version_id):
            raise ValueError("VERSIONED_ID_INVALID")
        matches = [rec for rec in self._frozen if rec["version_id"] == version_id
                   and rec["slot"] == slot and rec["action"] == first_action]
        if len(matches) != 1:
            raise ValueError("VERSIONED_WITNESS_OR_ADDRESS_NOT_FOUND")
        return _probability(matches[0]["old_counts"])

    def manifest(self):
        native_checkpoint = self._native.checkpoint()
        return _canonical({"schema": SCHEMA,
                           "native_checkpoint_sha256": sha256(native_checkpoint).hexdigest(),
                           "versions": list(self._frozen)})

    def checkpoint(self):
        """Return independent native checkpoint and small version manifest."""
        return self._native.checkpoint(), self.manifest()

    @classmethod
    def restore(cls, native_raw, manifest_raw):
        if (type(native_raw) is not bytes or type(manifest_raw) is not bytes
                or len(manifest_raw) > 16000 or len(manifest_raw) == 0):
            raise ValueError("VERSIONED_CHECKPOINT_INPUT")
        try:
            data = json.loads(manifest_raw.decode("ascii"))
        except (UnicodeError, ValueError) as exc:
            raise ValueError("VERSIONED_MANIFEST_PARSE") from exc
        if (type(data) is not dict or set(data) !=
                {"schema", "native_checkpoint_sha256", "versions"}
                or data["schema"] != SCHEMA
                or data["native_checkpoint_sha256"] != sha256(native_raw).hexdigest()
                or _canonical(data) != manifest_raw
                or type(data["versions"]) is not list
                or len(data["versions"]) > MAX_FROZEN_VERSIONS):
            raise ValueError("VERSIONED_MANIFEST_CUSTODY")
        native = NativeEpisodeExperience.restore(native_raw, sha256(native_raw).hexdigest())
        candidate = cls(native)
        if data["versions"] != list(candidate._frozen):
            raise ValueError("VERSIONED_REPAIR_HISTORY_MISMATCH")
        if candidate.manifest() != manifest_raw:
            raise ValueError("VERSIONED_COLD_NONDETERMINISM")
        return candidate

    def consolidate(self):
        candidate = VersionedNativeTransition(self._native.consolidate())
        if candidate._frozen != self._frozen:
            raise ValueError("VERSIONED_CONSOLIDATION_DRIFT")
        return candidate
