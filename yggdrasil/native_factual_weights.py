"""NKR-05: read-only memory mapped, full-scale native factual weight layer.

This is a *typed Q/P/Q factual memory*, NOT NKR-04's four-bit causal outcome
bank and not an accepted DG1-native architecture promotion. All materialized
facts come from an immutable historical TRAIN-only source. There are no
language labels or invented causal meanings; multi-hop results are hypotheses.
"""
from __future__ import annotations

import hashlib
import json
import mmap
from pathlib import Path
import struct

PACK = struct.Struct("<III")
ROW_BYTES = PACK.size
SCHEMA = "yggdrasil.native-factual-weights.v1"
MAX_ROWS = 25_000_000
MAX_BYTES = MAX_ROWS * ROW_BYTES


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def digest(value):
    return hashlib.sha256(value).hexdigest()


def _id(x):
    if type(x) is not int or not (0 < x <= 0xFFFFFFFF):
        raise ValueError("NKR05_QP_ID_INVALID")
    return x


class NativeFactualWeights:
    """Immutable mmap of sorted (Q-subject,P-relation,Q-object) uint32 weights.

    Exact binary-search evidence lookup. The separately pinned manifest SHA
    protects identity but DOES NOT prove historical statements are current.
    """
    __slots__ = ("path", "manifest", "_file", "_map", "_rows")

    def __init__(self, image_path, manifest_path, expected_manifest_sha256):
        if (type(expected_manifest_sha256) is not str
                or len(expected_manifest_sha256) != 64
                or any(x not in "0123456789abcdef"
                       for x in expected_manifest_sha256)):
            raise ValueError("NKR05_MANIFEST_PIN_INVALID")
        path = Path(image_path)
        meta = Path(manifest_path).read_bytes()
        if digest(meta) != expected_manifest_sha256:
            raise ValueError("NKR05_MANIFEST_PIN_MISMATCH")
        try:
            obj = json.loads(meta.decode("ascii"))
        except (ValueError, UnicodeError) as exc:
            raise ValueError("NKR05_MANIFEST_INVALID") from exc
        if meta != canonical(obj):
            raise ValueError("NKR05_MANIFEST_NONCANONICAL")
        if not isinstance(obj, dict) or obj.get("schema") != SCHEMA:
            raise ValueError("NKR05_SCHEMA_INVALID")
        if obj.get("accepted_native") is not False or obj.get("scientific_pass") is not False:
            raise ValueError("NKR05_UNSUPPORTED_ACCEPTANCE_CLAIM")
        rows = obj.get("records")
        byte_count = obj.get("numeric_bytes")
        if (type(rows) is not int or not (1 <= rows <= MAX_ROWS)
                or type(byte_count) is not int
                or byte_count != rows * ROW_BYTES):
            raise ValueError("NKR05_MANIFEST_COUNTS_INVALID")
        for key in ("packed_sha256", "source_train_sha256", "source_archive_sha256"):
            val = obj.get(key)
            if (type(val) is not str or len(val) != 64
                    or any(c not in "0123456789abcdef" for c in val)):
                raise ValueError("NKR05_MANIFEST_SOURCE_INVALID")
        if obj.get("data_kind") != "historical-train-only-QPQ":
            raise ValueError("NKR05_SOURCE_KIND_INVALID")
        if path.stat().st_size != byte_count:
            raise ValueError("NKR05_IMAGE_LENGTH_DRIFT")
        f = open(path, "rb")
        try:
            h = hashlib.sha256()
            while True:
                b = f.read(1 << 20)
                if not b:
                    break
                h.update(b)
            if h.hexdigest() != obj["packed_sha256"]:
                raise ValueError("NKR05_IMAGE_HASH_DRIFT")
            f.seek(0)
            view = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        except BaseException:
            f.close()
            raise
        self.path = str(path)
        self.manifest = obj
        self._file = f
        self._map = view
        self._rows = rows

    def __len__(self):
        return self._rows

    def close(self):
        if self._map is not None:
            self._map.close()
            self._map = None
        if self._file is not None:
            self._file.close()
            self._file = None

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        self.close()

    def _row(self, index):
        if self._map is None:
            raise ValueError("NKR05_MEMORY_CLOSED")
        return PACK.unpack_from(self._map, index * ROW_BYTES)

    def row_at(self, index):
        if type(index) is not int or not (0 <= index < self._rows):
            raise IndexError("NKR05_RECORD_INDEX_INVALID")
        return self._row(index)

    def _lower(self, subject, predicate, obj=0):
        """First triple >= query under lexicographic packed-row order."""
        low, high = 0, self._rows
        want = (subject, predicate, obj)
        while low < high:
            mid = (low + high) // 2
            if self._row(mid) < want:
                low = mid + 1
            else:
                high = mid
        return low

    def has_fact(self, subject, predicate, obj):
        subject, predicate, obj = _id(subject), _id(predicate), _id(obj)
        at = self._lower(subject, predicate, obj)
        return at < self._rows and self._row(at) == (subject, predicate, obj)

    def objects(self, subject, predicate, *, limit=64, after=0):
        """All directly observed objects for a Q/P pair, bounded+paginated.

        No speculation, computed counterfactuals or fabricated semantic labels.
        Returned triples are exact source-backed historical TRAIN facts.
        """
        subject, predicate = _id(subject), _id(predicate)
        if type(limit) is not int or not 1 <= limit <= 256:
            raise ValueError("NKR05_QUERY_LIMIT_INVALID")
        if type(after) is not int or not 0 <= after <= 0xFFFFFFFF:
            raise ValueError("NKR05_QUERY_CURSOR_INVALID")
        start = self._lower(subject, predicate, after + 1)
        output = []
        while start < self._rows and len(output) < limit:
            s, p, obj = self._row(start)
            if (s, p) != (subject, predicate):
                break
            output.append(obj)
            start += 1
        return output

    def two_hop_candidates(self, subject, first_relation, second_relation,
                           *, max_intermediates=16, max_candidates=64):
        """Explicitly unsupported hypotheses from observed two-edge paths.

        The caller must NOT write these as verified facts or observed actions.
        This is compositional path traversal, not autonomous rule invention.
        """
        subject, first_relation, second_relation = (
            _id(subject), _id(first_relation), _id(second_relation))
        if (type(max_intermediates) is not int
                or not 1 <= max_intermediates <= 64
                or type(max_candidates) is not int
                or not 1 <= max_candidates <= 256):
            raise ValueError("NKR05_HYPOTHESIS_BUDGET_INVALID")
        mids = self.objects(subject, first_relation, limit=max_intermediates)
        results = []
        seen = set()
        for mid in mids:
            for obj in self.objects(mid, second_relation, limit=max_candidates):
                if obj not in seen:
                    seen.add(obj)
                    results.append(obj)
                    if len(results) == max_candidates:
                        return {"classification": "UNVERIFIED_PATH_HYPOTHESES",
                                "objects": results, "evidence_source_sha256":
                                self.manifest["source_train_sha256"]}
        return {"classification": "UNVERIFIED_PATH_HYPOTHESES",
                "objects": results, "evidence_source_sha256":
                self.manifest["source_train_sha256"]}
