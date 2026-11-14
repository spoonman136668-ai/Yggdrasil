"""WSP104 bounded retained-only relation-frequency DEV baseline, not scientific AGI.

Three streamed passes over the independently sealed TRAIN member. Original
validation/test files, WSP101 cohorts, and accepted model weights are untouched.
"""
from __future__ import annotations

from collections import Counter
from contextlib import contextmanager
from hashlib import sha256
import heapq
import json
from pathlib import Path
import struct
import sys
import tarfile
import tempfile
import time

WSP103 = Path(__file__).resolve().parent.parent / "WSP-103"
sys.path.insert(0, str(WSP103))
from train_headroom_audit import (
    ARCHIVE_SHA, EXPECTED_ARCHIVE_BYTES, TRAIN_BYTES, TRAIN_ROWS, RELATIONS,
    TRAIN_SHA, PACK_GROUP, group_digest, heldout, parse_triple,
    load_custody_helpers,
)

CAPACITY = 64
QUERY_COUNT = 4096
MAX_WALL_SECONDS = 1200
FROZEN_ANSWERS_SHA = "008249f2c9731a426645c584e887bb056662c96f8c2385ba946b98ca3d9f49dc"


def train_candidates(open_train, *, expected_rows=TRAIN_ROWS, expected_bytes=TRAIN_BYTES,
                     expected_sha=TRAIN_SHA, expected_relations=RELATIONS,
                     query_count=QUERY_COUNT, capacity=CAPACITY,
                     expected_answers_sha=FROZEN_ANSWERS_SHA,
                     max_wall_seconds=MAX_WALL_SECONDS):
    """Candidate selection and all prediction features use only retained rows.

    Heldout group queries are selected by digest alone; no answers are used to
    choose models, thresholds, query memberships, or controls. First-use scores
    remain *DEV* because source is an already-known train-only graph.
    """
    if not (0 < query_count <= QUERY_COUNT and 1 <= capacity <= CAPACITY):
        raise ValueError("query/candidate bounds violated")
    started = time.monotonic()
    cpu = time.process_time()

    def bounded(stream):
        for index, raw in enumerate(stream):
            if index % 16384 == 0 and time.monotonic() - started > max_wall_seconds:
                raise TimeoutError("frozen source baseline budget exceeded")
            yield raw

    # Pass 1: full provenance and fixed query-group cohort, independent of values.
    sha = sha256()
    groups = []
    known = set()
    rows = 0
    bytes_seen = 0
    relations = set()
    hidden_rows = 0
    with open_train() as source:
        for raw in bounded(source):
            rows += 1
            bytes_seen += len(raw)
            if rows > expected_rows or bytes_seen > expected_bytes:
                raise ValueError("train source grew")
            s, p, _ = parse_triple(raw)
            sha.update(raw)
            relations.add(p)
            digest = group_digest(s, p)
            if not heldout(digest):
                continue
            hidden_rows += 1
            key = (s, p)
            if key in known:
                continue
            priority = int.from_bytes(digest[8:16], "big")
            key_numeric = (s << 32) | p
            item = (-priority, -key_numeric, key)
            if len(groups) < query_count:
                heapq.heappush(groups, item)
                known.add(key)
            elif (priority, key_numeric) < (-groups[0][0], -groups[0][1]):
                worst = heapq.heapreplace(groups, item)
                known.remove(worst[2])
                known.add(key)
    if (rows != expected_rows or bytes_seen != expected_bytes or
            sha.hexdigest() != expected_sha or len(relations) != expected_relations):
        raise ValueError("sealed training source provenance changed")
    if len(groups) != query_count:
        raise ValueError("not enough frozen query groups")

    selected = {item[2]: set() for item in groups}
    heavy = {}
    retained_rows = 0
    # Pass 2: collect hidden answers for scoring in a separate dict, while the
    # *model* receives only retained rows. Space-saving Misra-Gries counters
    # consume no hidden triple labels.
    with open_train() as source:
        for raw in bounded(source):
            s, p, obj = parse_triple(raw)
            digest = group_digest(s, p)
            if heldout(digest):
                if (s, p) in selected:
                    selected[(s, p)].add(obj)
                continue
            retained_rows += 1
            weights = heavy.setdefault(p, {})
            if obj in weights:
                weights[obj] += 1
            elif len(weights) < capacity:
                weights[obj] = 1
            else:
                for key in tuple(weights):
                    v = weights[key] - 1
                    if v:
                        weights[key] = v
                    else:
                        del weights[key]
    if retained_rows + hidden_rows != rows:
        raise AssertionError("retained/hidden counts inconsistent")
    if not all(selected.values()):
        raise ValueError("empty hidden test answer set")

    # WSP103 canonical group-answer SHA proves selection semantics match
    # the precommitted, already-audited source. The SHA never enters training.
    witness = sha256()
    for (s, p), targets in sorted(selected.items()):
        witness.update(PACK_GROUP.pack(s, p))
        witness.update(struct.pack("<I", len(targets)))
        for obj in sorted(targets):
            witness.update(struct.pack("<I", obj))
    sample_sha = witness.hexdigest()
    if expected_answers_sha is not None and sample_sha != expected_answers_sha:
        raise ValueError("masked query or answer witness differs from WSP103")

    # Pass 3: exact counts ONLY for candidates chosen from retained rows.
    candidate_keys = {p: set(counter) for p, counter in heavy.items()}
    exact = {p: Counter() for p in candidate_keys}
    retained_recount = 0
    with open_train() as source:
        for raw in bounded(source):
            s, p, obj = parse_triple(raw)
            if heldout(group_digest(s, p)):
                continue
            retained_recount += 1
            if obj in candidate_keys.get(p, ()):
                exact[p][obj] += 1
    if retained_recount != retained_rows:
        raise AssertionError("retained-only re-count drift")

    metrics = {
        "frequency": {"hits1": 0, "hits10": 0, "mrr_sum": 0.0},
        "reverse": {"hits1": 0, "hits10": 0, "mrr_sum": 0.0},
    }
    empty = 0
    candidate_total = 0
    digest = sha256()
    for (s, p), targets in sorted(selected.items()):
        ranked = sorted(candidate_keys.get(p, ()), key=lambda v: (-exact[p][v], v))
        if not ranked:
            empty += 1
        candidate_total += len(ranked)
        for label, ranked_arm in (("frequency", ranked), ("reverse", list(reversed(ranked)))):
            try:
                first = next(i + 1 for i, candidate in enumerate(ranked_arm)
                             if candidate in targets)
            except StopIteration:
                first = 0
            metrics[label]["hits1"] += int(first == 1)
            metrics[label]["hits10"] += int(0 < first <= 10)
            metrics[label]["mrr_sum"] += 1.0 / first if first else 0.0
            digest.update(struct.pack("<II", len(ranked_arm), first))
    for m in metrics.values():
        m["hits1_rate"] = m["hits1"] / query_count
        m["hits10_rate"] = m["hits10"] / query_count
        m["mean_reciprocal_rank"] = m.pop("mrr_sum") / query_count
    return {
        "schema": "wsp104.train-only-masked-frequency-baseline.v1",
        "classification": "DEV_HEURISTIC_CONTROL_ONLY_NOT_FULLY_TRAINED_KG_NEURAL_OR_SCIENTIFIC_PASS",
        "source_train_sha256": sha.hexdigest(),
        "source_rows": rows,
        "source_bytes": bytes_seen,
        "relation_types": len(relations),
        "masked_train_rows": hidden_rows,
        "retained_train_rows": retained_rows,
        "selected_query_groups": query_count,
        "frozen_query_answer_sha256": sample_sha,
        "relation_candidate_capacity": capacity,
        "mean_candidates_per_query": candidate_total / query_count,
        "queries_no_retained_candidates": empty,
        "selected_group_direct_lookup_hits": 0,
        "metrics": metrics,
        "score_receipt_sha256": digest.hexdigest(),
        "official_validation_test_read": False,
        "fully_trained_kg_neural_baseline": False,
        "novel_direct_weight_learner": False,
        "scientific_pass": False,
        "scanner_cpu_seconds": time.process_time() - cpu,
        "scanner_wall_seconds": time.monotonic() - started,
    }


@contextmanager
def open_train_only(archive_path):
    with tarfile.open(archive_path, mode="r:gz") as archive:
        member = archive.getmember("wikidata5m/train.txt")
        source = archive.extractfile(member)
        if source is None:
            raise ValueError("sealed archive train member not readable")
        with source:
            yield source


def original_train_only():
    _download_once, inspect_members = load_custody_helpers()
    with tempfile.TemporaryDirectory(prefix="wsp104-dev-baseline-") as work:
        path = Path(work) / "sealed-historical-source.tar.gz"
        started = time.monotonic()
        custody = _download_once(path)
        if (custody["compressed_sha256"] != ARCHIVE_SHA or
                custody["compressed_bytes"] != EXPECTED_ARCHIVE_BYTES):
            raise ValueError("historical sealed archive changed")
        actual = {(m["path"], m["type"], m["uncompressed_bytes"])
                  for m in inspect_members(path)["members"]}
        expected = {
            ("wikidata5m", "directory", 0),
            ("wikidata5m/train.txt", "file", TRAIN_BYTES),
            ("wikidata5m/valid.txt", "file", 109498),
            ("wikidata5m/test.txt", "file", 108932),
        }
        if actual != expected:
            raise ValueError("unexpected archive member or byte count")
        proof = train_candidates(lambda: open_train_only(path))
        proof["full_process_wall_seconds"] = time.monotonic() - started
        proof["archive_sha256"] = ARCHIVE_SHA
        return proof


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--frozen-train-only-frequency-dev", action="store_true", required=True)
    ap.parse_args()
    result = original_train_only()
    print("WSP104_TRAIN_ONLY_BASELINES=" + json.dumps(result, sort_keys=True,
                                                     separators=(",", ":")), flush=True)
