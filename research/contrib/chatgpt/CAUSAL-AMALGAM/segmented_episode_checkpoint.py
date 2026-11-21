"""G38 DEV-only lossless external episode-checkpoint envelope.

Does not change native restore, episode admission, actor, or memory policy.
Only source-native episode checkpoint bytes can be represented. The code
cannot create new witness capacity or confer owner/source custody.
"""

from hashlib import sha256
import json
import re
import zlib

SCHEMA = "yggdrasil.ckad.external-episode-segments.dev.v1"
NATIVE_SCHEMAS = frozenset(
    f"yggdrasil.ckad.native-episode-experience.v{v}" for v in range(1, 7)
)
MAX_CHECKPOINT_BYTES = 160 * 1024
MAX_EPISODES = 1152
SEGMENT_LENGTH = 32
MAX_RAW_SEGMENT_BYTES = 16 * 1024
MAX_COMPRESSED_SEGMENT_BYTES = MAX_RAW_SEGMENT_BYTES + 64
HASH = re.compile(r"[0-9a-f]{64}\Z")


def canonical(value):
    """Match the existing native canonical ASCII JSON contract."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def _digest(raw):
    return sha256(raw).hexdigest()


def _require(test, code):
    if not test:
        raise ValueError(code)


def _load(raw, error):
    _require(type(raw) is bytes, error)
    try:
        doc = json.loads(raw.decode("ascii"))
        _require(canonical(doc) == raw, error)
    except (UnicodeError, TypeError, ValueError, RecursionError, OverflowError) as exc:
        raise ValueError(error) from exc
    return doc


def _validate_checkpoint(raw):
    _require(type(raw) is bytes and 0 < len(raw) <= MAX_CHECKPOINT_BYTES,
             "G38_RAW_BOUNDS")
    doc = _load(raw, "G38_NATIVE_CANONICAL")
    _require(type(doc) is dict and doc.get("schema") in NATIVE_SCHEMAS,
             "G38_NATIVE_SCHEMA")
    rows = doc.get("episodes")
    _require(type(rows) is list and 0 <= len(rows) <= MAX_EPISODES,
             "G38_EPISODES_BOUNDS")
    ids = set()
    for row in rows:
        _require(type(row) is list and len(row) == 6, "G38_ROW_SHAPE")
        identifier, views, *bits = row
        _require(type(identifier) is str and HASH.fullmatch(identifier)
                 and identifier not in ids, "G38_ROW_IDENTITY")
        ids.add(identifier)
        _require(type(views) is list and len(views) == 2
                 and all(type(view) is list and len(view) == 2
                         and all(type(bit) is int and bit in (0, 1) for bit in view)
                         for view in views)
                 and all(type(bit) is int and bit in (0, 1) for bit in bits),
                 "G38_ROW_DATA")
    return doc


def seal(native_raw):
    """Return a canonical manifest and immutable ordered compressed segments.

    Caller owns storage and integrity of both manifest and segment blobs.
    No model mutation or first-use world action occurs here.
    """
    doc = _validate_checkpoint(native_raw)
    episodes = doc["episodes"]
    metadata = {key: value for key, value in doc.items() if key != "episodes"}
    chunks = []
    entries = []
    for start in range(0, len(episodes), SEGMENT_LENGTH):
        stop = min(start + SEGMENT_LENGTH, len(episodes))
        raw_chunk = canonical(episodes[start:stop])
        _require(len(raw_chunk) <= MAX_RAW_SEGMENT_BYTES, "G38_CHUNK_BOUNDS")
        compressed = zlib.compress(raw_chunk, level=9)
        _require(len(compressed) <= MAX_COMPRESSED_SEGMENT_BYTES,
                 "G38_COMPRESSED_BOUNDS")
        entries.append({"start": start, "stop": stop,
                        "sha256": _digest(raw_chunk), "bytes": len(raw_chunk),
                        "compressed_sha256": _digest(compressed),
                        "compressed_bytes": len(compressed)})
        chunks.append(compressed)
    manifest = {
        "schema": SCHEMA,
        "native_checkpoint_sha256": _digest(native_raw),
        "native_checkpoint_bytes": len(native_raw),
        "native_metadata": metadata,
        "native_metadata_sha256": _digest(canonical(metadata)),
        "episode_count": len(episodes),
        "segment_length": SEGMENT_LENGTH,
        "segments": entries,
    }
    return canonical(manifest), tuple(chunks)


def restore(manifest_raw, chunks):
    """Fail closed, rehydrate byte-identical original native checkpoint.

    NativeEpisodeExperience.restore is deliberately NOT invoked here; its
    separate owner qualification must verify live parity and custody.
    """
    manifest = _load(manifest_raw, "G38_MANIFEST_CANONICAL")
    _require(type(manifest) is dict
             and set(manifest) == {"schema", "native_checkpoint_sha256",
                                   "native_checkpoint_bytes", "native_metadata",
                                   "native_metadata_sha256", "episode_count",
                                   "segment_length", "segments"}
             and manifest["schema"] == SCHEMA, "G38_MANIFEST_SCHEMA")
    count = manifest["episode_count"]
    entries = manifest["segments"]
    _require(type(count) is int and 0 <= count <= MAX_EPISODES
             and type(entries) is list
             and len(entries) == (count + SEGMENT_LENGTH - 1) // SEGMENT_LENGTH
             and type(manifest["segment_length"]) is int
             and manifest["segment_length"] == SEGMENT_LENGTH
             and type(chunks) in (tuple, list)
             and len(chunks) == len(entries), "G38_SEGMENT_COUNT")
    metadata = manifest["native_metadata"]
    _require(type(metadata) is dict and "episodes" not in metadata
             and metadata.get("schema") in NATIVE_SCHEMAS
             and _digest(canonical(metadata)) == manifest["native_metadata_sha256"],
             "G38_METADATA")
    records = []
    for i, (entry, blob) in enumerate(zip(entries, chunks, strict=True)):
        expected = i * SEGMENT_LENGTH
        end = min(expected + SEGMENT_LENGTH, count)
        _require(type(entry) is dict and set(entry) == {
            "start", "stop", "sha256", "bytes", "compressed_sha256",
            "compressed_bytes"} and type(entry["start"]) is int
            and type(entry["stop"]) is int
            and entry["start"] == expected and entry["stop"] == end,
            "G38_CHUNK_ORDER")
        _require(type(blob) is bytes and type(entry["compressed_bytes"]) is int
                 and len(blob) == entry["compressed_bytes"]
                 and len(blob) <= MAX_COMPRESSED_SEGMENT_BYTES
                 and _digest(blob) == entry["compressed_sha256"],
                 "G38_CHUNK_COMPRESSED_PIN")
        decoder = zlib.decompressobj()
        try:
            raw_chunk = decoder.decompress(blob, MAX_RAW_SEGMENT_BYTES + 1)
            _require(decoder.eof and not decoder.unused_data
                     and not decoder.unconsumed_tail, "G38_CHUNK_DECOMPRESSION")
        except zlib.error as exc:
            raise ValueError("G38_CHUNK_DECOMPRESSION") from exc
        _require(type(entry["bytes"]) is int
                 and 0 < len(raw_chunk) == entry["bytes"] <= MAX_RAW_SEGMENT_BYTES
                 and _digest(raw_chunk) == entry["sha256"],
                 "G38_CHUNK_RAW_PIN")
        batch = _load(raw_chunk, "G38_CHUNK_CANONICAL")
        _require(type(batch) is list and len(batch) == end - expected,
                 "G38_CHUNK_LENGTH")
        records.extend(batch)
    native_raw = canonical({**metadata, "episodes": records})
    _require(type(manifest["native_checkpoint_bytes"]) is int
             and len(native_raw) == manifest["native_checkpoint_bytes"]
             and len(native_raw) <= MAX_CHECKPOINT_BYTES
             and _digest(native_raw) == manifest["native_checkpoint_sha256"],
             "G38_ROOT_PIN")
    _validate_checkpoint(native_raw)
    return native_raw
