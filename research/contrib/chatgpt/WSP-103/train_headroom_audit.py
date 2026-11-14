"""WSP-103: source-only structural headroom audit of the sealed WSP-102 train graph.

NO learner training, scoring, original benchmark validation/test access, scientific
promotion, or changes to Yggdrasil's accepted weights. The heldout group selection
is locked in prereg.json before this implementation.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
import heapq
from io import BytesIO
import json
from pathlib import Path
import struct
import tarfile
import tempfile
import time

GROUP_DOMAIN = b"WSP103-TRAIN-GROUP-v1\x00"
PACK_GROUP = struct.Struct("<II")
TRAIN_SHA = "2ef1a279f6393a8edfbb2b44114a2c97944272e5fe2a1bd2a7cbe48f94742f1a"
ARCHIVE_SHA = "ccda8bbcd3cf599b30dd3fd8979ac26e59b48fc53d23128882a044bfbb67f878"
TRAIN_ROWS = 21_343_681
TRAIN_BYTES = 436_189_882
RELATIONS = 828
MAX_WALL = 900
EXPECTED_ARCHIVE_BYTES = 174_515_774
QUERY_COUNT = 4096


def positive_identifier(item: bytes, prefix: bytes) -> int:
    if not item.startswith(prefix) or len(item) < 2 or not item[1:].isdigit():
        raise ValueError("not a Q/P identifier")
    if len(item) > 2 and item[1:2] == b"0":
        raise ValueError("noncanonical Q/P identifier")
    value = int(item[1:])
    if not 0 < value <= 0xFFFFFFFF:
        raise ValueError("identifier outside uint32")
    return value


def parse_triple(row: bytes) -> tuple[int, int, int]:
    if not row.endswith(b"\n") or len(row) > 10000 or b"\x00" in row:
        raise ValueError("not a bounded complete triple line")
    parts = row.rstrip(b"\r\n").split(b"\t")
    if len(parts) != 3:
        raise ValueError("not a Q/P/Q triple")
    return (positive_identifier(parts[0], b"Q"),
            positive_identifier(parts[1], b"P"),
            positive_identifier(parts[2], b"Q"))


def group_digest(s: int, p: int) -> bytes:
    return sha256(GROUP_DOMAIN + PACK_GROUP.pack(s, p)).digest()


def heldout(digest: bytes) -> bool:
    return digest[0] & 31 == 0


def _bounded_rows(handle, started, budget):
    for i, row in enumerate(handle):
        if i % 16384 == 0 and time.monotonic() - started > budget:
            raise TimeoutError("headroom audit time budget exceeded")
        yield row


def audit_streams(open_train, *, expected_rows=TRAIN_ROWS,
                  expected_bytes=TRAIN_BYTES, expected_sha=TRAIN_SHA,
                  expected_relations=RELATIONS, query_count=QUERY_COUNT,
                  max_wall_seconds=MAX_WALL):
    """Three passes, source-backed and bounded independent of evaluation outcomes.

    Pass 1: verify all train bytes and choose a fixed uniform-priority group cohort.
    Pass 2: collect only cohort answer-set cardinalities; no model gets these labels.
    Pass 3: compute retained TRAIN endpoint support, excluding *all* heldout groups.
    """
    if not (0 < query_count <= QUERY_COUNT):
        raise ValueError("invalid preregistered query budget")
    if expected_rows <= 0 or expected_bytes <= 0 or max_wall_seconds <= 0:
        raise ValueError("invalid source bound")
    started = time.monotonic()
    cpu_started = time.process_time()
    source_digest = sha256()
    byte_count = 0
    row_count = 0
    relation_ids = set()
    heldout_row_count = 0
    heap = []
    present = set()
    with open_train() as source:
        for row in _bounded_rows(source, started, max_wall_seconds):
            byte_count += len(row)
            row_count += 1
            if row_count > expected_rows or byte_count > expected_bytes:
                raise ValueError("train source exceeds frozen count")
            s, p, _ = parse_triple(row)
            source_digest.update(row)
            relation_ids.add(p)
            digest = group_digest(s, p)
            if heldout(digest):
                heldout_row_count += 1
                key = (s, p)
                if key in present:
                    continue
                priority = int.from_bytes(digest[8:16], "big")
                key_numeric = (s << 32) | p
                item = (-priority, -key_numeric, key)
                if len(heap) < query_count:
                    heapq.heappush(heap, item)
                    present.add(key)
                elif (priority, key_numeric) < (-heap[0][0], -heap[0][1]):
                    worst = heapq.heapreplace(heap, item)
                    present.remove(worst[2])
                    present.add(key)
    if (row_count != expected_rows or byte_count != expected_bytes or
        source_digest.hexdigest() != expected_sha or
        len(relation_ids) != expected_relations):
        raise ValueError("sealed source row, byte, SHA256 or relation drift")
    if len(heap) != query_count:
        raise ValueError("not enough distinct source-hidden query groups")

    selected = {item[2]: set() for item in heap}
    sample_subjects = {s for s, _ in selected}
    # Answers are never used to choose the heldout groups or tune any threshold.
    with open_train() as source:
        for row in _bounded_rows(source, started, max_wall_seconds):
            s, p, o = parse_triple(row)
            key = (s, p)
            if key in selected:
                selected[key].add(o)
    if any(not objects for objects in selected.values()):
        raise AssertionError("selected withheld source group is empty")

    sample_objects = set().union(*selected.values())
    subject_retained = Counter()
    object_retained = Counter()
    retained_count = 0
    leak_count = 0
    with open_train() as source:
        for row in _bounded_rows(source, started, max_wall_seconds):
            s, p, o = parse_triple(row)
            if heldout(group_digest(s, p)):
                # No heldout answer may enter any training-side evidence.
                continue
            retained_count += 1
            if (s, p) in selected:
                leak_count += 1
            if s in sample_subjects:
                subject_retained[s] += 1
            if o in sample_objects:
                object_retained[o] += 1
    if leak_count:
        raise AssertionError("heldout group exposed to retained training evidence")

    sample_canonical = sha256()
    group_cardinality = Counter()
    with_subject_support = 0
    with_object_support = 0
    with_both_support = 0
    for (s, p), objects in sorted(selected.items()):
        sample_canonical.update(PACK_GROUP.pack(s, p))
        sample_canonical.update(struct.pack("<I", len(objects)))
        for o in sorted(objects):
            sample_canonical.update(struct.pack("<I", o))
        group_cardinality[len(objects)] += 1
        has_subject = subject_retained[s] > 0
        has_any_object = any(object_retained[o] > 0 for o in objects)
        with_subject_support += has_subject
        with_object_support += has_any_object
        with_both_support += has_subject and has_any_object
    return {
        "schema": "wsp103.train-only-structural-headroom-audit.v1",
        "classification": "DEV_SOURCE_STRUCTURE_ONLY_NOT_IDENTIFIABILITY_OR_SCIENTIFIC_PASS",
        "source_train_sha256": source_digest.hexdigest(),
        "source_rows": row_count,
        "source_bytes": byte_count,
        "source_relation_types": len(relation_ids),
        "heldout_source_rows": heldout_row_count,
        "selected_distinct_query_groups": len(selected),
        "selected_group_answer_cardinality_histogram": dict(sorted(group_cardinality.items())),
        "selected_distinct_objects": len(sample_objects),
        "selected_query_answers_sha256": sample_canonical.hexdigest(),
        "retained_train_rows": retained_count,
        "with_subject_train_support": with_subject_support,
        "with_any_object_train_support": with_object_support,
        "with_both_endpoint_support": with_both_support,
        "selected_group_leakage_count": leak_count,
        "all_official_validation_test_untouched": True,
        "trained_conventional_baseline": False,
        "direct_weight_learner_trained": False,
        "scientific_pass": False,
        "cpu_seconds": time.process_time() - cpu_started,
        "wall_seconds": time.monotonic() - started,
    }


def run_train_only_source_audit() -> dict:
    from source_custody import _download_once, inspect_members
    with tempfile.TemporaryDirectory(prefix="wsp103-train-only-") as directory:
        archive_path = Path(directory) / "original-historical.tar.gz"
        custody = _download_once(archive_path)
        if (custody["compressed_sha256"] != ARCHIVE_SHA or
            custody["compressed_bytes"] != EXPECTED_ARCHIVE_BYTES):
            raise ValueError("archive hash/byte custody changed")
        members = inspect_members(archive_path)
        actual = {(m["path"], m["type"], m["uncompressed_bytes"])
                  for m in members["members"]}
        expected = {
            ("wikidata5m", "directory", 0),
            ("wikidata5m/train.txt", "file", TRAIN_BYTES),
            ("wikidata5m/valid.txt", "file", 109498),
            ("wikidata5m/test.txt", "file", 108932),
        }
        if actual != expected:
            raise ValueError("archive path and size seal changed")

        class TrainOnly:
            def __enter__(self):
                self.tar = tarfile.open(archive_path, mode="r:gz")
                member = self.tar.getmember("wikidata5m/train.txt")
                self.source = self.tar.extractfile(member)
                if self.source is None:
                    self.tar.close()
                    raise ValueError("train source cannot be read")
                return self.source

            def __exit__(self, exc_type, exc, tb):
                try:
                    self.source.close()
                finally:
                    self.tar.close()

        return audit_streams(TrainOnly)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--train-only-dev-source-headroom", action="store_true", required=True)
    parser.parse_args()
    result = run_train_only_source_audit()
    print("WSP103_SOURCE_HEADROOM=" + json.dumps(result, sort_keys=True, separators=(",", ":")), flush=True)
