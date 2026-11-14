"""WSP105: frozen full-historical-TRAIN-only subject-specific two-hop DEV control.

This is a symbolic path baseline with frozen subject-neighbor selection, NOT a
fully trained knowledge-graph embedding, a novel direct-weight learner, or
scientific promotion. WSP103's original official validation/test data stay shut.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from hashlib import sha256
import heapq
import json
from pathlib import Path
import struct
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "WSP-103"))
sys.path.insert(0, str(ROOT / "WSP-104"))
from train_headroom_audit import (
    ARCHIVE_SHA, EXPECTED_ARCHIVE_BYTES, PACK_GROUP, RELATIONS,
    TRAIN_BYTES, TRAIN_ROWS, TRAIN_SHA, group_digest, heldout,
    load_custody_helpers, parse_triple,
)
from frequency_controls import open_train_only

CAPACITY = 64
QUERY_COUNT = 4096
SUBJECT_NEIGHBORS = 32
MAX_JOIN_UPDATES = 30_000_000
MAX_SCAN_WALL_SECONDS = 1200
NEIGHBOR_DOMAIN = b"WSP105-NEIGHBOR-v1\x00"
PACK_TRIPLE = struct.Struct("<III")
FROZEN_SAMPLE_SHA = "008249f2c9731a426645c584e887bb056662c96f8c2385ba946b98ca3d9f49dc"
FROZEN_WSP104_SCORE_SHA = "4a4364b6c4a806d2b69e9bb329e70f6c1f7d3f39fbafb68bb536d22fb9e2259a"
FROZEN_WSP104_FREQUENCY = (921, 1853, 2, 44)


def first_correct_rank(ranked, answers):
    return next((i + 1 for i, value in enumerate(ranked) if value in answers), 0)


def score_ranked(ranked, answers, acc):
    rank = first_correct_rank(ranked, answers)
    acc["hits1"] += int(rank == 1)
    acc["hits10"] += int(0 < rank <= 10)
    acc["sum_reciprocal"] += 1 / rank if rank else 0
    return rank


def selected_masked_groups_and_subject_paths(
    open_train, *, expected_rows=TRAIN_ROWS, expected_bytes=TRAIN_BYTES,
    expected_sha=TRAIN_SHA, expected_relations=RELATIONS,
    expected_sample_sha=FROZEN_SAMPLE_SHA,
    expected_frequency_sha=FROZEN_WSP104_SCORE_SHA,
    expected_frequency_scores=FROZEN_WSP104_FREQUENCY,
    query_count=QUERY_COUNT, capacity=CAPACITY,
    max_subject_neighbors=SUBJECT_NEIGHBORS,
    max_join_updates=MAX_JOIN_UPDATES,
    max_wall_seconds=MAX_SCAN_WALL_SECONDS,
):
    """Three source passes, with selected labels kept out of all path features.

    No model consumes any of the 1/32 entire (subject,predicate) hidden groups.
    A symbolic two-hop path is (query subject)--r1-->(retained neighbor)
    --r2-->(relation-specific frequency candidate). All predicates r1,r2
    are admitted *only* from retained training rows.
    """
    if not (0 < query_count <= QUERY_COUNT and
            1 <= capacity <= CAPACITY and
            1 <= max_subject_neighbors <= SUBJECT_NEIGHBORS and
            0 < max_join_updates <= MAX_JOIN_UPDATES and max_wall_seconds > 0):
        raise ValueError("preregistered candidate/query/path budget violated")
    start = time.monotonic()
    cpu = time.process_time()

    def bounded(handle):
        for i, raw in enumerate(handle):
            if i % 16384 == 0 and time.monotonic() - start > max_wall_seconds:
                raise TimeoutError("source-only symbolic path control exceeded budget")
            yield raw

    # PASS ONE: source provenance and sample membership, not target values.
    src_sha = sha256()
    selected_heap = []
    present = set()
    source_rows = 0
    source_bytes = 0
    hidden_rows = 0
    predicates = set()
    with open_train() as source:
        for raw in bounded(source):
            source_rows += 1
            source_bytes += len(raw)
            if source_rows > expected_rows or source_bytes > expected_bytes:
                raise ValueError("historical source inventory grew")
            s, p, _ = parse_triple(raw)
            src_sha.update(raw)
            predicates.add(p)
            digest = group_digest(s, p)
            if not heldout(digest):
                continue
            hidden_rows += 1
            key = (s, p)
            if key in present:
                continue
            priority = int.from_bytes(digest[8:16], "big")
            scalar = (s << 32) | p
            item = (-priority, -scalar, key)
            if len(selected_heap) < query_count:
                heapq.heappush(selected_heap, item)
                present.add(key)
            elif (priority, scalar) < (-selected_heap[0][0], -selected_heap[0][1]):
                displaced = heapq.heapreplace(selected_heap, item)
                present.remove(displaced[2])
                present.add(key)
    if (source_rows != expected_rows or source_bytes != expected_bytes or
            src_sha.hexdigest() != expected_sha or
            len(predicates) != expected_relations):
        raise ValueError("sealed train source SHA, breadth or cardinality drift")
    if len(selected_heap) != query_count:
        raise ValueError("not enough hidden source query groups")

    selected = {item[2]: set() for item in selected_heap}
    per_subject_queries = defaultdict(list)
    for query in selected:
        per_subject_queries[query[0]].append(query)
    subject_heaps = {}
    subject_seen = {}
    heavy = {}
    retained_rows = 0

    # PASS TWO: WSP104 retained-only candidate learner, masked answer witness,
    # and subject-local neighbors selected WITHOUT consulting masked answers.
    with open_train() as source:
        for raw in bounded(source):
            s, p, o = parse_triple(raw)
            if heldout(group_digest(s, p)):
                if (s, p) in selected:
                    selected[(s, p)].add(o)
                continue
            retained_rows += 1
            counters = heavy.setdefault(p, {})
            if o in counters:
                counters[o] += 1
            elif len(counters) < capacity:
                counters[o] = 1
            else:
                for obj in tuple(counters):
                    new = counters[obj] - 1
                    if new:
                        counters[obj] = new
                    else:
                        del counters[obj]

            if s not in per_subject_queries:
                continue
            pair = (p, o)
            heap = subject_heaps.setdefault(s, [])
            seen = subject_seen.setdefault(s, set())
            if pair in seen:
                continue
            priority = int.from_bytes(
                sha256(NEIGHBOR_DOMAIN + PACK_TRIPLE.pack(s, p, o)).digest()[:8],
                "big",
            )
            item = (-priority, -p, -o, pair)
            if len(heap) < max_subject_neighbors:
                heapq.heappush(heap, item)
                seen.add(pair)
            elif (priority, p, o) < (-heap[0][0], -heap[0][1], -heap[0][2]):
                displaced = heapq.heapreplace(heap, item)
                seen.remove(displaced[3])
                seen.add(pair)
    if retained_rows + hidden_rows != source_rows:
        raise AssertionError("retained and masked row counts inconsistent")
    if any(not answers for answers in selected.values()):
        raise AssertionError("selected masked group has no answers")

    witness = sha256()
    for (s, p), targets in sorted(selected.items()):
        witness.update(PACK_GROUP.pack(s, p))
        witness.update(struct.pack("<I", len(targets)))
        for target in sorted(targets):
            witness.update(struct.pack("<I", target))
    actual_sample_sha = witness.hexdigest()
    if expected_sample_sha is not None and actual_sample_sha != expected_sample_sha:
        raise ValueError("WSP103 frozen sample and answer witness mismatch")

    # No withheld answer values are referenced anywhere below until scoring.
    candidate_keys = {p: set(counters) for p, counters in heavy.items()}
    exact = {p: Counter() for p in candidate_keys}
    candidates_by_object = defaultdict(set)
    for p, objects in candidate_keys.items():
        if any(query_p == p for _, query_p in selected):
            for obj in objects:
                candidates_by_object[obj].add(p)
    neighbor_queries = defaultdict(lambda: defaultdict(set))
    for s, queries in per_subject_queries.items():
        for _, _, _, (r1, z) in subject_heaps.get(s, []):
            for query in queries:
                neighbor_queries[z][query[1]].add(query)
    path_votes = {}
    path_joins = 0
    recounted = 0

    # PASS THREE: exact WSP104 candidate counts + retained-only two-hop join.
    # Path evidence sees retained source edges ONLY and uses candidate IDs
    # selected independently of hidden answers.
    with open_train() as source:
        for raw in bounded(source):
            z, r2, obj = parse_triple(raw)
            if heldout(group_digest(z, r2)):
                continue
            recounted += 1
            if obj in candidate_keys.get(r2, ()):
                exact[r2][obj] += 1
            path_targets = neighbor_queries.get(z)
            if not path_targets:
                continue
            for target_predicate in candidates_by_object.get(obj, ()):
                for query in path_targets.get(target_predicate, ()):
                    vote = path_votes.setdefault(query, Counter())
                    vote[obj] += 1
                    path_joins += 1
                    if path_joins > max_join_updates:
                        raise MemoryError("frozen two-hop path-join limit exceeded")
    if recounted != retained_rows:
        raise AssertionError("source subset changed during recount")

    arm_names = ("frequency", "reverse", "path_only", "path_first")
    arms = {name: {"hits1": 0, "hits10": 0, "sum_reciprocal": 0.0}
            for name in arm_names}
    frequency_receipt = sha256()
    path_receipt = sha256()
    any_path = 0
    any_positive_in_top64 = 0
    empty_candidates = 0
    used_neighbors = sum(len(x) for x in subject_heaps.values())
    for query, targets in sorted(selected.items()):
        _, predicate = query
        base = sorted(candidate_keys.get(predicate, ()),
                      key=lambda obj: (-exact[predicate][obj], obj))
        if not base:
            empty_candidates += 1
        reverse = list(reversed(base))
        votes = path_votes.get(query, {})
        ranked_path = sorted(base, key=lambda obj: (-votes.get(obj, 0),
                                                    -exact[predicate][obj], obj))
        path_only = [obj for obj in ranked_path if votes.get(obj, 0) > 0]
        any_path += int(bool(path_only))
        any_positive_in_top64 += int(bool(targets.intersection(path_only)))
        order = {
            "frequency": base, "reverse": reverse,
            "path_only": path_only, "path_first": ranked_path,
        }
        for name, ranked in order.items():
            rank = score_ranked(ranked, targets, arms[name])
            if name in ("frequency", "reverse"):
                frequency_receipt.update(struct.pack("<II", len(ranked), rank))
            else:
                path_receipt.update(struct.pack("<II", len(ranked), rank))

    freq_checks = (arms["frequency"]["hits1"],
                   arms["frequency"]["hits10"],
                   arms["reverse"]["hits1"],
                   arms["reverse"]["hits10"])
    if expected_frequency_scores is not None and freq_checks != tuple(expected_frequency_scores):
        raise ValueError("WSP104 frozen frequency-control exact scores changed")
    if (expected_frequency_sha is not None and
            frequency_receipt.hexdigest() != expected_frequency_sha):
        raise ValueError("WSP104 frozen score SHA mismatch")

    for result in arms.values():
        result["hits1_rate"] = result["hits1"] / query_count
        result["hits10_rate"] = result["hits10"] / query_count
        result["mean_reciprocal_rank"] = result.pop("sum_reciprocal") / query_count

    return {
        "schema": "wsp105.historical-train-only-subject-two-hop-control.v1",
        "classification": "DEV_SYMBOLIC_PATH_COMPARISON_ONLY_NOT_TRAINED_KGE_OR_SCIENTIFIC_PASS",
        "source_rows": source_rows,
        "source_bytes": source_bytes,
        "source_sha256": src_sha.hexdigest(),
        "relations": len(predicates),
        "retained_training_rows": retained_rows,
        "masked_training_rows": hidden_rows,
        "selected_query_groups": query_count,
        "selected_query_answer_sha256": actual_sample_sha,
        "candidate_limit_per_relation": capacity,
        "neighbor_limit_per_query_subject": max_subject_neighbors,
        "sampled_retained_subject_neighbor_edges": used_neighbors,
        "queries_with_any_two_hop_candidate": any_path,
        "queries_with_any_true_answer_two_hop_candidate": any_positive_in_top64,
        "path_join_updates": path_joins,
        "queries_without_frequency_candidates": empty_candidates,
        "frequency_score_receipt_sha256": frequency_receipt.hexdigest(),
        "path_score_receipt_sha256": path_receipt.hexdigest(),
        "metrics": arms,
        "path_first_hits10_minus_frequency": (
            arms["path_first"]["hits10"] - arms["frequency"]["hits10"]),
        "official_validation_test_read": False,
        "novel_direct_weight_learner_trained": False,
        "fully_trained_conventional_embedding_model": False,
        "scientific_pass": False,
        "scanner_cpu_seconds": time.process_time() - cpu,
        "scanner_wall_seconds": time.monotonic() - start,
    }


def real_train_only():
    _download_once, inspect_members = load_custody_helpers()
    with tempfile.TemporaryDirectory(prefix="wsp105-path-control-") as directory:
        path = Path(directory) / "known-historical-source.tar.gz"
        start = time.monotonic()
        custody = _download_once(path)
        if (custody["compressed_sha256"] != ARCHIVE_SHA or
                custody["compressed_bytes"] != EXPECTED_ARCHIVE_BYTES):
            raise ValueError("noncanonical archive changed after custody")
        actual = {(m["path"], m["type"], m["uncompressed_bytes"])
                  for m in inspect_members(path)["members"]}
        known = {
            ("wikidata5m", "directory", 0),
            ("wikidata5m/train.txt", "file", TRAIN_BYTES),
            ("wikidata5m/valid.txt", "file", 109498),
            ("wikidata5m/test.txt", "file", 108932),
        }
        if actual != known:
            raise ValueError("archive file allowlist/size changed")
        result = selected_masked_groups_and_subject_paths(
            lambda: open_train_only(path))
        result["full_process_wall_seconds"] = time.monotonic() - start
        result["archive_sha256"] = ARCHIVE_SHA
        return result


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--frozen-train-only-subject-path-dev", action="store_true",
                    required=True)
    ap.parse_args()
    result = real_train_only()
    print("WSP105_TRAIN_ONLY_PATH_CONTROL=" +
          json.dumps(result, sort_keys=True, separators=(",", ":")), flush=True)
