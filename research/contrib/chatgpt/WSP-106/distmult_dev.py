"""WSP106: bounded full-retained-TRAIN conventional DistMult embedding DEV pilot.

Fits standard subject/relation/object embeddings by negative logistic SGD over
ALL 20,677,636 retained historical edges, subject to preregistered four epochs.
Not claimed converged, strongest available baseline or scientific learning pass.
Official validation/test and protected original first-use records are untouched.
"""
from __future__ import annotations

from array import array
from collections import Counter
from contextlib import contextmanager
from hashlib import sha256
import heapq
import json
import math
import os
from pathlib import Path
import resource
import struct
import sys
import tempfile
import time

import numpy as np

WSP103 = Path(__file__).resolve().parent.parent / "WSP-103"
WSP104 = Path(__file__).resolve().parent.parent / "WSP-104"
sys.path.insert(0, str(WSP103))
sys.path.insert(0, str(WSP104))
from train_headroom_audit import (
    ARCHIVE_SHA, EXPECTED_ARCHIVE_BYTES, TRAIN_SHA, TRAIN_BYTES, TRAIN_ROWS,
    RELATIONS, PACK_GROUP, group_digest, heldout, parse_triple,
    load_custody_helpers,
)
from frequency_controls import open_train_only

SEED = 41061
DIM = 16
EPOCHS = 4
BATCH = 8192
LR = np.float32(0.08)
CAPACITY = 64
QUERY_COUNT = 4096
MAX_WALL_SECONDS = 3000
WSP103_SAMPLE_SHA = "008249f2c9731a426645c584e887bb056662c96f8c2385ba946b98ca3d9f49dc"
WSP104_FREQUENCY_RECEIPT = "4a4364b6c4a806d2b69e9bb329e70f6c1f7d3f39fbafb68bb536d22fb9e2259a"
WSP104_COUNTS = (921, 1853, 2, 44)
WSP105_CONTROL = (1190, 2038)
MAX_RSS_BYTES = 5 * 1024**3


def rss_max_bytes():
    # CI real-data qualification runs on Linux only.
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024


def check_budget(start, max_wall, *, rss_limit=MAX_RSS_BYTES):
    if time.monotonic() - start >= max_wall:
        raise TimeoutError("frozen full-retained training budget exceeded")
    if rss_max_bytes() >= rss_limit:
        raise MemoryError("frozen full-retained training RSS budget exceeded")


def sample_groups(open_train, *, rows=TRAIN_ROWS, byte_count=TRAIN_BYTES,
                  sha=TRAIN_SHA, predicates=RELATIONS, query_count=QUERY_COUNT,
                  start=None, wall=MAX_WALL_SECONDS):
    """Pass 1: immutable archive identity and masked query membership only."""
    if start is None:
        start = time.monotonic()
    digest = sha256()
    count = 0
    size = 0
    relations = set()
    hidden_rows = 0
    heap = []
    known = set()
    with open_train() as source:
        for index, raw in enumerate(source):
            if index % 16384 == 0:
                check_budget(start, wall)
            count += 1
            size += len(raw)
            if count > rows or size > byte_count:
                raise ValueError("historical source unexpectedly grew")
            s, p, _ = parse_triple(raw)
            digest.update(raw)
            relations.add(p)
            priority_digest = group_digest(s, p)
            if not heldout(priority_digest):
                continue
            hidden_rows += 1
            key = (s, p)
            if key in known:
                continue
            priority = int.from_bytes(priority_digest[8:16], "big")
            scalar = (s << 32) | p
            item = (-priority, -scalar, key)
            if len(heap) < query_count:
                heapq.heappush(heap, item)
                known.add(key)
            elif (priority, scalar) < (-heap[0][0], -heap[0][1]):
                displaced = heapq.heapreplace(heap, item)
                known.remove(displaced[2])
                known.add(key)
    if (digest.hexdigest() != sha or count != rows or
            size != byte_count or len(relations) != predicates):
        raise ValueError("sealed historical source integrity mismatch")
    if len(heap) != query_count:
        raise ValueError("expected frozen masked query groups missing")
    return {entry[2]: set() for entry in heap}, hidden_rows, digest.hexdigest()


def read_retained_and_candidates(open_train, selected, expected_hidden,
                                 *, expected_retained=20_677_636,
                                 expected_sample=WSP103_SAMPLE_SHA,
                                 capacity=CAPACITY, start=None, wall=MAX_WALL_SECONDS):
    """Pass 2: never admit masked training edges to model or candidate counters."""
    if start is None:
        start = time.monotonic()
    raw_edges = array("I")
    heavy = {}
    hidden_count = 0
    with open_train() as source:
        for i, raw in enumerate(source):
            if i % 16384 == 0:
                check_budget(start, wall)
            s, p, o = parse_triple(raw)
            if heldout(group_digest(s, p)):
                hidden_count += 1
                key = (s, p)
                if key in selected:
                    selected[key].add(o)
                continue
            raw_edges.extend((s, p, o))
            counter = heavy.setdefault(p, {})
            if o in counter:
                counter[o] += 1
            elif len(counter) < capacity:
                counter[o] = 1
            else:
                for obj in tuple(counter):
                    n = counter[obj] - 1
                    if n:
                        counter[obj] = n
                    else:
                        del counter[obj]
    if hidden_count != expected_hidden or len(raw_edges) != expected_retained * 3:
        raise ValueError("frozen masked/retained split changed")
    if not all(selected.values()):
        raise ValueError("masked selected query has empty value set")
    sample_sha = sha256()
    for (s, p), objects in sorted(selected.items()):
        sample_sha.update(PACK_GROUP.pack(s, p))
        sample_sha.update(struct.pack("<I", len(objects)))
        for o in sorted(objects):
            sample_sha.update(struct.pack("<I", o))
    if expected_sample is not None and sample_sha.hexdigest() != expected_sample:
        raise ValueError("WSP103 sample answer witness changed")
    return raw_edges, heavy, sample_sha.hexdigest()


def exact_candidate_rankings(edges, heavy, selected, *,
                             expected_receipt=WSP104_FREQUENCY_RECEIPT,
                             expected_counts=WSP104_COUNTS,
                             expected_recount=20_677_636, start=None,
                             wall=MAX_WALL_SECONDS):
    """WSP104 candidate learner replay, independent of model scores."""
    if start is None:
        start = time.monotonic()
    candidate_set = {p: set(c) for p, c in heavy.items()}
    exact = {p: Counter() for p in candidate_set}
    rows = np.frombuffer(edges, dtype=np.uint32).reshape((-1, 3))
    for i, (s, p, o) in enumerate(rows):
        if i % 16384 == 0:
            check_budget(start, wall)
        predicate = int(p)
        obj = int(o)
        if obj in candidate_set.get(predicate, ()):
            exact[predicate][obj] += 1
    if len(rows) != expected_recount:
        raise ValueError("retained training rows differ from WSP104")
    candidate_rank = {}
    for predicate, candidates in candidate_set.items():
        candidate_rank[predicate] = sorted(candidates,
                                          key=lambda obj: (-exact[predicate][obj], obj))
    receipt = sha256()
    hits = {"freq1": 0, "freq10": 0, "reverse1": 0, "reverse10": 0}
    for query, answers in sorted(selected.items()):
        base = candidate_rank.get(query[1], [])
        reverse = list(reversed(base))
        for label, ranked in (("freq", base), ("reverse", reverse)):
            rank = next((i + 1 for i, o in enumerate(ranked) if o in answers), 0)
            hits[label + "1"] += int(rank == 1)
            hits[label + "10"] += int(0 < rank <= 10)
            receipt.update(struct.pack("<II", len(ranked), rank))
    counts = (hits["freq1"], hits["freq10"], hits["reverse1"], hits["reverse10"])
    if expected_counts is not None and counts != tuple(expected_counts):
        raise ValueError("WSP104 original accuracy counts drifted")
    if expected_receipt is not None and receipt.hexdigest() != expected_receipt:
        raise ValueError("WSP104 original prediction receipt changed")
    return candidate_rank, receipt.hexdigest(), counts


def id_maps(edges):
    """No ID hashing. Full unique retained entity and predicate vocabulary."""
    triples = np.frombuffer(edges, dtype=np.uint32).reshape((-1, 3))
    if not triples.size:
        raise ValueError("empty training graph")
    entities = np.unique(np.concatenate((triples[:, 0], triples[:, 2])))
    predicates = np.unique(triples[:, 1])
    subjects = np.searchsorted(entities, triples[:, 0]).astype(np.int32)
    objects = np.searchsorted(entities, triples[:, 2]).astype(np.int32)
    relations = np.searchsorted(predicates, triples[:, 1]).astype(np.int32)
    if (entities.size > np.iinfo(np.int32).max or
        predicates.size > np.iinfo(np.int32).max):
        raise ValueError("full entity/relation mapping exceeds int32")
    return entities, predicates, subjects, relations, objects


def distmult_logits(E, R, s, p, o):
    return np.einsum("ij,ij,ij->i", E[s], R[p], E[o], optimize=False)


def batch_update(E, R, s, p, o, neg, lr=LR):
    """Standard DistMult negative-logistic SGD with exact source index updates."""
    s_emb = E[s]
    p_emb = R[p]
    o_emb = E[o]
    n_emb = E[neg]
    positive = np.einsum("ij,ij,ij->i", s_emb, p_emb, o_emb)
    negative = np.einsum("ij,ij,ij->i", s_emb, p_emb, n_emb)
    if not np.all(np.isfinite(positive)) or not np.all(np.isfinite(negative)):
        raise FloatingPointError("unbounded training logits")
    positive_safe = np.clip(positive, -25, 25)
    negative_safe = np.clip(negative, -25, 25)
    pos_coeff = np.float32(1) / (np.float32(1) + np.exp(-positive_safe)) - np.float32(1)
    neg_coeff = np.float32(1) / (np.float32(1) + np.exp(-negative_safe))
    pos_grad = pos_coeff[:, None]
    neg_grad = neg_coeff[:, None]
    shared = pos_grad * o_emb + neg_grad * n_emb
    gs = p_emb * shared
    go = p_emb * (pos_grad * s_emb)
    gn = p_emb * (neg_grad * s_emb)
    gr = s_emb * shared
    np.add.at(E, s, -lr * gs)
    np.add.at(E, o, -lr * go)
    np.add.at(E, neg, -lr * gn)
    np.add.at(R, p, -lr * gr)
    if not np.all(np.isfinite(E[s])) or not np.all(np.isfinite(R[p])):
        raise FloatingPointError("nonfinite conventional embedding training weights")
    loss = np.logaddexp(0, -positive).sum(dtype=np.float64)
    loss += np.logaddexp(0, negative).sum(dtype=np.float64)
    return float(loss)


def rank_score(E, R, entity_ids, predicate_ids, selected, candidate_rank):
    """Score only WSP104's same frozen 64-candidate-per-relation universe."""
    sum_rr = 0.0
    hits1 = 0
    hits10 = 0
    unknown_subjects = 0
    unknown_candidates = 0
    receipt = sha256()
    for (s, p), answers in sorted(selected.items()):
        candidates = candidate_rank.get(p, ())
        if not candidates:
            receipt.update(struct.pack("<II", 0, 0))
            continue
        query_s = int(np.searchsorted(entity_ids, s))
        query_p = int(np.searchsorted(predicate_ids, p))
        have_subject = query_s < len(entity_ids) and int(entity_ids[query_s]) == s
        have_predicate = query_p < len(predicate_ids) and int(predicate_ids[query_p]) == p
        if not have_subject or not have_predicate:
            unknown_subjects += 1
        values = np.asarray(candidates, dtype=np.uint32)
        ci = np.searchsorted(entity_ids, values)
        exists = ci < len(entity_ids)
        exists[exists] &= entity_ids[ci[exists]] == values[exists]
        unknown_candidates += int((~exists).sum())
        scores = np.full(len(values), -np.inf, dtype=np.float64)
        if have_subject and have_predicate and exists.any():
            scores[exists] = (
                E[ci[exists]] * (E[query_s] * R[query_p])[None, :]
            ).sum(axis=1).astype(np.float64)
        scored = sorted(range(len(candidates)), key=lambda i: (-scores[i], candidates[i]))
        rank = next((i + 1 for i, index in enumerate(scored)
                     if candidates[index] in answers), 0)
        hits1 += rank == 1
        hits10 += 0 < rank <= 10
        sum_rr += 1 / rank if rank else 0
        receipt.update(struct.pack("<II", len(candidates), rank))
    n = len(selected)
    return {
        "hits1": hits1, "hits10": hits10,
        "hits1_rate": hits1 / n, "hits10_rate": hits10 / n,
        "mrr": sum_rr / n,
        "unknown_subject_queries": unknown_subjects,
        "unknown_candidate_occurrences": unknown_candidates,
        "score_receipt_sha256": receipt.hexdigest(),
    }


def model_trial(edges, selected, candidate_rank, *,
                epochs=EPOCHS, batch=BATCH, dimension=DIM, lr=LR, seed=SEED,
                start=None, wall=MAX_WALL_SECONDS):
    if start is None:
        start = time.monotonic()
    if epochs <= 0 or dimension <= 0 or batch <= 0:
        raise ValueError("invalid training plan")
    entities, predicates, subjects, relations, objects = id_maps(edges)
    check_budget(start, wall)
    generator = np.random.Generator(np.random.PCG64(seed))
    E = generator.normal(0.0, 0.1, size=(len(entities), dimension)).astype(np.float32)
    R = (np.float32(1) + generator.normal(
        0.0, 0.02, size=(len(predicates), dimension)).astype(np.float32))
    untrained = rank_score(E, R, entities, predicates, selected, candidate_rank)
    losses = []
    n = len(subjects)
    for epoch in range(epochs):
        check_budget(start, wall)
        shuffle = generator.permutation(n)
        epoch_loss = 0.0
        for start_i in range(0, n, batch):
            if start_i % (batch * 16) == 0:
                check_budget(start, wall)
            idx = shuffle[start_i:start_i + batch]
            negative = generator.integers(0, len(entities), size=len(idx), dtype=np.int32)
            epoch_loss += batch_update(
                E, R, subjects[idx], relations[idx], objects[idx], negative, lr=lr)
        epoch_mean = epoch_loss / n
        if not math.isfinite(epoch_mean):
            raise FloatingPointError("nonfinite full-retained training loss")
        losses.append(epoch_mean)
    trained = rank_score(E, R, entities, predicates, selected, candidate_rank)
    return {
        "entity_vocabulary_size": len(entities),
        "relation_vocabulary_size": len(predicates),
        "retained_edges_trained_per_epoch": n,
        "epochs_completed": epochs,
        "dimension": dimension,
        "batch_size": batch,
        "seed": seed,
        "learning_rate": float(lr),
        "mean_train_logistic_loss_each_epoch": losses,
        "untrained": untrained, "trained": trained,
        "model_representation": "full-vocabulary nonhashed conventional DistMult",
    }


def run_real_source_trial():
    started = time.monotonic()
    cpu_start = time.process_time()
    downloader, inspect = load_custody_helpers()
    with tempfile.TemporaryDirectory(prefix="wsp106-full-distmult-dev-") as temp:
        archive = Path(temp) / "sealed-historical-train.tar.gz"
        custody = downloader(archive)
        if (custody["compressed_sha256"] != ARCHIVE_SHA or
            custody["compressed_bytes"] != EXPECTED_ARCHIVE_BYTES):
            raise ValueError("pinned archive bytes or SHA256 changed")
        members = {(x["path"], x["type"], x["uncompressed_bytes"])
                   for x in inspect(archive)["members"]}
        if members != {
            ("wikidata5m", "directory", 0),
            ("wikidata5m/train.txt", "file", TRAIN_BYTES),
            ("wikidata5m/valid.txt", "file", 109498),
            ("wikidata5m/test.txt", "file", 108932),
        }:
            raise ValueError("unexpected archive member inventory")

        open_train = lambda: open_train_only(archive)
        sample, hidden_count, src_sha = sample_groups(
            open_train, start=started)
        edges, heavy, sample_sha = read_retained_and_candidates(
            open_train, sample, hidden_count, start=started)
        ranked, witness, controls = exact_candidate_rankings(
            edges, heavy, sample, start=started)
        trial = model_trial(edges, sample, ranked, start=started)
        check_budget(started, MAX_WALL_SECONDS)
        return {
            "schema": "wsp106.full-historical-train-distmult-dev-pilot.v1",
            "classification": "DEV_FULL_RETAINED_EPOCH_BUDGET_NOT_PROVEN_CONVERGED_OR_SCIENTIFIC_PASS",
            "source_rows": TRAIN_ROWS,
            "source_bytes": TRAIN_BYTES,
            "source_train_sha256": src_sha,
            "archive_sha256": ARCHIVE_SHA,
            "retained_training_rows": len(edges) // 3,
            "masked_training_rows": hidden_count,
            "frozen_selected_query_groups": len(sample),
            "frozen_sample_answers_sha256": sample_sha,
            "wsp104_frequency_receipt_sha256": witness,
            "wsp104_frequency_and_reverse_counts": list(controls),
            "wsp105_strongest_symbolic_control_hits1_hits10": list(WSP105_CONTROL),
            "official_val_test_unopened": True,
            "first_use_original_science": False,
            "novel_direct_weight_programming_comparison": False,
            "scientific_pass": False,
            "max_rss_bytes": rss_max_bytes(),
            "training_scanner_cpu_seconds": time.process_time() - cpu_start,
            "full_process_wall_seconds": time.monotonic() - started,
            **trial,
        }


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--frozen-full-retained-distmult-dev", action="store_true", required=True)
    p.parse_args()
    outcome = run_real_source_trial()
    print("WSP106_FULL_RETAINED_DISTMULT=" +
          json.dumps(outcome, sort_keys=True, separators=(",", ":")), flush=True)
