"""CSMC-02 FIT-only readout snapshot + bounded provenance witness cache.

Exploratory supporting research; NOT an accepted learner, mutable memory, or
source authority. Requires the original unmodified native modules for readout.
"""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
import json
import zlib

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_episode_experience import NativeEpisodeExperience

SCHEMA = "yggdrasil.csmc02.two-tier-readout.v1"
ARCHIVE_SHA256 = "36f535c451c813dd56afd58c4f1833ac8e5fca98627d898a571e40c8bc8a0114"
COHORT = "amalgam-selection-transition-local-dev-v1"
PREFIX = b"CSM2"
MAX_CHECKPOINT = 8192
CACHE_SIZE = 8
# First eight public FIT observations, verified from the immutable archived
# source blob 9db0d3742fc8bd009c61d0864e4aba739a19e4e1.
# This is a fixed-cohort DEVELOPMENT anchor, not a generic source witness proof.
PINNED_CACHE_PUBLIC = bytes.fromhex("44e50907bd0e110c")


def pack_public(views, row):
    if (type(views) is not tuple or len(views) != 2 or
            any(type(v) is not tuple or len(v) != 2 for v in views) or
            type(row) is not dict or set(row) != {"s1", "x1", "s2", "x2", "y"}):
        raise ValueError("CSMC02_PUBLIC_SHAPE")
    bits = [*views[0], *views[1], *(row[k] for k in ("x1", "s2", "x2", "y"))]
    if any(type(bit) is not int or bit not in (0, 1) for bit in bits) or row["s1"] != views[0][0]:
        raise ValueError("CSMC02_PUBLIC_BITS")
    return int("".join(map(str, bits)), 2)


def unpack_public(byte):
    if type(byte) is not int or not (0 <= byte <= 255):
        raise ValueError("CSMC02_PUBLIC_BYTE")
    a, b, c, d, first, state, second, reward = (int(x) for x in f"{byte:08b}")
    return ((a, b), (c, d)), {"s1": a, "x1": first, "s2": state, "x2": second, "y": reward}


def _fraction(value):
    if (type(value) is not list or len(value) != 2 or
            any(type(n) is not int for n in value) or value[1] <= 0):
        raise ValueError("CSMC02_FRACTION_INVALID")
    return Fraction(*value)


class TwoTier:
    """Cold-restorable *readout* only. No observe(), context or repair API."""

    ARCHIVE_DIGEST = ARCHIVE_SHA256

    def __init__(self, payload):
        self._p = payload

    @classmethod
    def from_native(cls, native, *, archive_sha256=ARCHIVE_SHA256):
        if (type(native) is not NativeEpisodeExperience or len(native._ledger) != 50 or
                native._projection not in (0, 1) or native._repairs or native._streaks or
                native._context_start is not None or native._context_models or
                native._stream_start is not None or native._refresh_start is not None or
                native._context_novel):
            raise ValueError("CSMC02_NATIVE_MODE_UNSUPPORTED")
        if archive_sha256 != ARCHIVE_SHA256:
            raise ValueError("CSMC02_ORIGINAL_ARCHIVE_PIN")
        cache = []
        for i, event in enumerate(native._ledger[:CACHE_SIZE]):
            identifier, views, first, state, second, reward = event
            row = {"s1": views[0][0], "x1": first, "s2": state,
                   "x2": second, "y": reward}
            if identifier != digest(canonical([COHORT, (764013, 764029)[i // 32], i % 32])):
                raise ValueError("CSMC02_ORIGINAL_IDENTITY")
            cache.append([i, identifier, pack_public(views, row)])
        p = {"schema": SCHEMA, "archive_sha256": archive_sha256,
             "core": {"count": 50, "projection": native._projection,
                      "mismatches": list(native._mismatches),
                      "transition": native._transition._counts[:3],
                      "terminal": native._terminal._counts[:14],
                      "transition_loss": [[x.numerator, x.denominator] for x in native._transition_loss],
                      "terminal_loss": [[x.numerator, x.denominator] for x in native._terminal_loss]},
             "cache": cache}
        cls._validate(p)
        return cls(p)

    @staticmethod
    def _validate(p):
        if type(p) is not dict or set(p) != {"schema", "archive_sha256", "core", "cache"} or p["schema"] != SCHEMA or p["archive_sha256"] != ARCHIVE_SHA256:
            raise ValueError("CSMC02_SCHEMA_OR_SOURCE_INVALID")
        core = p["core"]
        if type(core) is not dict or set(core) != {"count", "projection", "mismatches", "transition", "terminal", "transition_loss", "terminal_loss"}:
            raise ValueError("CSMC02_CORE_SCHEMA_INVALID")
        if type(core["count"]) is not int or core["count"] != 50 or type(core["projection"]) is not int or core["projection"] not in (0, 1):
            raise ValueError("CSMC02_CORE_ID_INVALID")
        if type(core["mismatches"]) is not list or len(core["mismatches"]) != 2 or any(type(x) is not int or x < 0 or x > 8 for x in core["mismatches"]):
            raise ValueError("CSMC02_PROJECTION_INVALID")
        for name, limit in (("transition", 3), ("terminal", 14)):
            bank = core[name]
            if (type(bank) is not list or len(bank) != limit or
                    any(type(slot) is not list or len(slot) != 2 or
                        any(type(pair) is not list or len(pair) != 2 or
                            any(type(count) is not int or count < 0 or count > 65535 for count in pair)
                            for pair in slot) for slot in bank)):
                raise ValueError("CSMC02_BANK_INVALID")
        for key in ("transition_loss", "terminal_loss"):
            if type(core[key]) is not list or len(core[key]) != 2:
                raise ValueError("CSMC02_LOSS_SHAPE")
            [_fraction(x) for x in core[key]]
        cache = p["cache"]
        if type(cache) is not list or len(cache) != CACHE_SIZE:
            raise ValueError("CSMC02_CACHE_SIZE")
        for i, item in enumerate(cache):
            if type(item) is not list or len(item) != 3 or type(item[0]) is not int or item[0] != i or type(item[1]) is not str or item[1] != digest(canonical([COHORT, (764013, 764029)[i // 32], i % 32])):
                raise ValueError("CSMC02_CACHE_IDENTITY")
            unpack_public(item[2])
            if item[2] != PINNED_CACHE_PUBLIC[i]:
                raise ValueError("CSMC02_CACHE_SOURCE_PIN")

    def _encode(self, *, cache=True):
        p = self._p if cache else {"schema": SCHEMA, "archive_sha256": ARCHIVE_SHA256,
                                  "core": self._p["core"], "cache": []}
        # Baseline deliberately uses same codec and model state but no witnesses.
        raw = canonical(p)
        return PREFIX + zlib.compress(raw, level=9)

    def checkpoint(self):
        return self._encode(cache=True)

    def compact_only_checkpoint(self):
        return self._encode(cache=False)

    @classmethod
    def restore(cls, raw, expected_sha256):
        if type(raw) is not bytes or len(raw) > MAX_CHECKPOINT or not raw.startswith(PREFIX) or digest(raw) != expected_sha256:
            raise ValueError("CSMC02_CHECKPOINT_INTEGRITY")
        try:
            decoder = zlib.decompressobj()
            raw_json = decoder.decompress(raw[len(PREFIX):], max_length=16385)
            if (len(raw_json) > 16384 or not decoder.eof or
                    decoder.unconsumed_tail or decoder.unused_data):
                raise ValueError("CSMC02_ZLIB_BOUNDS")
            p = json.loads(raw_json)
        except (ValueError, zlib.error) as ex:
            raise ValueError("CSMC02_CHECKPOINT_FORMAT") from ex
        cls._validate(p)
        if canonical(p) != raw_json or cls(p).checkpoint() != raw:
            raise ValueError("CSMC02_NONCANONICAL")
        return cls(p)

    def _readout_native(self):
        """Invoke the original native class's unmodified forecast/propose code.

        This dummy has NO original ledger or legitimate future observe()/repair context;
        therefore only forecast()/propose() may be called on it.
        """
        n = NativeEpisodeExperience(repair=False)
        core = self._p["core"]
        n._projection = core["projection"]
        n._mismatches = core["mismatches"][:]
        for target, source in ((n._transition, core["transition"]), (n._terminal, core["terminal"])):
            target._counts[:len(source)] = [[arm[:] for arm in slot] for slot in source]
        n._transition_loss = [_fraction(x) for x in core["transition_loss"]]
        n._terminal_loss = [_fraction(x) for x in core["terminal_loss"]]
        return n

    def forecast(self, *args, **kwargs):
        return self._readout_native().forecast(*args, **kwargs)

    def propose(self, *args):
        return self._readout_native().propose(*args)

    def check_witness(self, identifier, views, row, *, archived_raw=None):
        """Authenticate prior FIT replay; never trains or mutates this snapshot.

        Uncached evidence requires complete archive bytes, verified before any
        event parsing. No archived bytes => fail closed (not an ID-free claim).
        """
        if type(identifier) is not str or len(identifier) != 64:
            raise ValueError("CSMC02_WITNESS_ID_INVALID")
        observed = pack_public(views, row)
        for slot, cached_id, cached_byte in self._p["cache"]:
            if identifier == cached_id:
                if (type(slot) is not int or slot not in range(CACHE_SIZE) or
                        cached_byte != PINNED_CACHE_PUBLIC[slot]):
                    raise ValueError("CSMC02_CACHE_SOURCE_PIN")
                if cached_byte != observed: raise ValueError("CSMC02_CONFLICTING_REPLAY")
                return "CACHE_EXACT_MATCH"
        if archived_raw is None:
            raise ValueError("CSMC02_ARCHIVE_REQUIRED_FOR_UNCACHED")
        if type(archived_raw) is not bytes or sha256(archived_raw).hexdigest() != self._p["archive_sha256"]:
            raise ValueError("CSMC02_ARCHIVE_INTEGRITY")
        archive = json.loads(archived_raw)
        if type(archive) is not list or len(archive) != 96:
            raise ValueError("CSMC02_ARCHIVE_SHAPE")
        for i, event in enumerate(archive[:50]):
            if event["id"] == identifier:
                if identifier != digest(canonical([COHORT, (764013, 764029)[i // 32], i % 32])):
                    raise ValueError("CSMC02_ARCHIVE_IDENTITY")
                src_views = tuple(tuple(x) for x in event["views"])
                if pack_public(src_views, event["row"]) != observed:
                    raise ValueError("CSMC02_CONFLICTING_REPLAY")
                return "ARCHIVE_EXACT_MATCH"
        raise ValueError("CSMC02_NOT_PRIOR_FIT_WITNESS")
