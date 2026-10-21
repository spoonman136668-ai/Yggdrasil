"""MR15: non-oracle local bit deltas from an ORIGINAL MiniGrid public view.

The only input is the 7x7x3 image returned as *public observation* by the
original upstream environment. Privileged environment internals, hidden
object identities, mission, direction, reward, termination, evaluator truth,
and target-role labels are NOT accepted by this adapter.

Eight spatial locations are fixed geometrically, not named by object type.
For each, a bit tells whether its original three observation bytes changed
since the previous publicly observed frame. The 24 raw bytes needed for
temporal comparison stay in an UNTRAINED input sidecar, never in learner
features. Count those plus eight bits of last observed state in resources.

Development observation interface only: no Yggdrasil learner update,
skill attribution, functional recovery, independent holdout or promotion.
"""
import json
import re

SCHEMA = "yggdrasil.mr15.public-view-local-delta.v1"
SOURCE_COMMIT = "7f5853792ea7f04f75614661006d87fcf949f26d"
# 8 spatially adjacent observer-relative locations on MiniGrid's 7x7 view.
# The center is deliberately omitted; this is geometry, not a role registry.
POSITIONS = ((2,3),(3,3),(4,3),(2,4),(4,4),(2,5),(3,5),(4,5))


def public_raw_view(image):
    # Refuse image dictionaries, metadata, privileged state, reward, object
    # tables, render frames, color labels or silently coerced non-uint8 input.
    if (getattr(image, "shape", None) != (7,7,3) or
        getattr(getattr(image, "dtype", None), "name", None) != "uint8"):
        raise ValueError("MR15_PUBLIC_VIEW_UINT8_7X7X3_REQUIRED")
    raw = tuple(int(image[x,y,c]) for x,y in POSITIONS for c in range(3))
    if len(raw) != 24 or any(type(b) is not int or not 0<=b<=255 for b in raw):
        raise ValueError("MR15_PUBLIC_VIEW_RAW_BUDGET")
    return raw


class PublicViewLocalDelta:
    __slots__ = ("_raw", "_bits", "_steps", "_source_commit")

    def __init__(self, source_commit=SOURCE_COMMIT):
        if source_commit != SOURCE_COMMIT:
            raise ValueError("MR15_EXTERNAL_SOURCE_IDENTITY_DRIFT")
        self._source_commit = source_commit
        self._raw = None
        self._bits = (0,)*8
        self._steps = 0

    @property
    def bits(self):
        return self._bits

    @property
    def steps(self):
        return self._steps

    def prime(self, image):
        if self._raw is not None:
            raise ValueError("MR15_VIEW_ALREADY_PRIMED")
        raw = public_raw_view(image)
        self._raw = raw
        return self._bits

    def observe_after_native_step(self, action, next_public_image):
        if self._raw is None:
            raise ValueError("MR15_VIEW_NOT_PRIMED")
        if type(action) is not int or not 0<=action<=6:
            raise ValueError("MR15_INVALID_NATIVE_ACTION")
        if self._steps>=4096:
            raise ValueError("MR15_NATIVE_STEP_BUDGET")
        next_raw = public_raw_view(next_public_image)
        changed = tuple(int(next_raw[i*3:i*3+3] != self._raw[i*3:i*3+3])
                        for i in range(8))
        preceding = self._bits
        # Everything above is computed and checked before source-state commit.
        self._raw = next_raw
        self._bits = changed
        self._steps += 1
        return {
            "prior_local_bits": list(preceding),
            "observed_action": action,
            "observed_next_local_bits": list(changed),
            "original_public_tiles_compared": 8,
            "source_commit": self._source_commit,
            "raw_temporal_sidecar_bytes": 24,
            "last_binary_observation_bits": 8,
            "additional_trainable_parameters": 0,
            "privileged_world_fields_consumed": 0,
        }

    def snapshot(self):
        return json.dumps({
            "schema": SCHEMA, "source_commit": self._source_commit,
            "prior_public_raw": list(self._raw) if self._raw is not None else None,
            "last_delta_bits": list(self._bits), "steps": self._steps
        },sort_keys=True,separators=(",",":"))

    @classmethod
    def restore(cls, snapshot):
        if type(snapshot) is not str or len(snapshot)>1024:
            raise ValueError("MR15_INVALID_SNAPSHOT_SIZE")
        try:
            p=json.loads(snapshot)
        except (ValueError,TypeError) as exc:
            raise ValueError("MR15_INVALID_SNAPSHOT_JSON") from exc
        if (type(p) is not dict or set(p)!={
            "schema","source_commit","prior_public_raw","last_delta_bits","steps"
        } or p["schema"]!=SCHEMA or p["source_commit"]!=SOURCE_COMMIT):
            raise ValueError("MR15_INVALID_SNAPSHOT_SCHEMA")
        raw=p["prior_public_raw"];bits=p["last_delta_bits"];steps=p["steps"]
        if (raw is not None and
                (type(raw) is not list or len(raw)!=24 or any(
                    type(v) is not int or not 0<=v<=255 for v in raw))):
            raise ValueError("MR15_INVALID_SNAPSHOT_RAW")
        if (type(bits) is not list or len(bits)!=8 or any(
            type(v) is not int or v not in (0,1) for v in bits) or
            type(steps) is not int or not 0<=steps<=4096 or
            (raw is None and (steps!=0 or bits != [0]*8))):
            raise ValueError("MR15_INVALID_SNAPSHOT_BITS")
        m=cls()
        m._raw=tuple(raw) if raw is not None else None
        m._bits=tuple(bits)
        m._steps=steps
        if m.snapshot()!=snapshot:
            raise ValueError("MR15_NONCANONICAL_SNAPSHOT")
        return m
