"""WSP107: independent projected TransE embedding for frozen historical TRAIN-only DEV.

Distinct conventional metric-embedding baseline from WSP106's failed bilinear
DistMult. All settings were frozen in WSP-107/prereg.json first. Never open
canonical validation/test or protected original first-use data. Do not promote.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
import math
from pathlib import Path
import sys
import tempfile
import time
import struct

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "WSP-106"))
from distmult_dev import (
    ARCHIVE_SHA, EXPECTED_ARCHIVE_BYTES, TRAIN_SHA, TRAIN_BYTES, TRAIN_ROWS,
    WSP103_SAMPLE_SHA, WSP104_FREQUENCY_RECEIPT, WSP104_COUNTS,
    load_custody_helpers, open_train_only,
    sample_groups, read_retained_and_candidates, exact_candidate_rankings,
    id_maps, check_budget, rss_max_bytes,
)

SEED = 1076107
DIM = 16
EPOCHS = 4
BATCH = 4096
LR = np.float32(0.02)
MARGIN = np.float32(1.0)
MAX_WALL_SECONDS = 2700
MAX_RSS_BYTES = 5 * 1024**3
WSP105_HITS = (1190, 2038)
WSP105_MRR = 0.3617429325369139


def project_rows(weights, selected=None):
    """L2 unit-ball projection, including zero vectors, no hidden labels."""
    if selected is None:
        w = weights
    else:
        selected = np.unique(np.asarray(selected, dtype=np.int32))
        w = weights[selected]
    norms = np.linalg.norm(w, axis=1)
    divisor = np.maximum(np.float32(1.0), norms).astype(np.float32)
    projected = w / divisor[:, None]
    if not np.all(np.isfinite(projected)):
        raise FloatingPointError("TransE projection yielded nonfinite embeddings")
    if selected is None:
        weights[:] = projected
    else:
        weights[selected] = projected


def transe_batch(E, P, s, relation, o, negative, *, lr=LR, margin=MARGIN):
    """Projected sparse per-edge SGD on TransE's squared-distance hinge loss.

    The reference implementation is intentionally explicit: any duplicate
    entity IDs within a batch have gradients added before one unit-ball
    projection of touched rows. No hidden targets enter the optimizer.
    """
    source = E[s]
    pred = P[relation]
    positive = E[o]
    corrupted = E[negative]
    diff_pos = source + pred - positive
    diff_neg = source + pred - corrupted
    sq_pos = np.einsum("ij,ij->i", diff_pos, diff_pos)
    sq_neg = np.einsum("ij,ij->i", diff_neg, diff_neg)
    losses = margin + sq_pos - sq_neg
    if not np.all(np.isfinite(losses)):
        raise FloatingPointError("TransE nonfinite margin prior to update")
    active = losses > 0
    loss_sum = float(np.maximum(losses, 0).sum(dtype=np.float64))
    if active.any():
        sa = s[active]
        pa = relation[active]
        oa = o[active]
        na = negative[active]
        dp = diff_pos[active]
        dn = diff_neg[active]
        # d/d(source, relation): 2 * ((s+r-o)-(s+r-n)) = 2 * (n-o)
        shared = np.float32(2) * (dp - dn)
        grad_o = -np.float32(2) * dp
        grad_n = np.float32(2) * dn
        np.add.at(E, sa, -lr * shared)
        np.add.at(P, pa, -lr * shared)
        np.add.at(E, oa, -lr * grad_o)
        np.add.at(E, na, -lr * grad_n)
        project_rows(E, np.concatenate((sa, oa, na)))
        project_rows(P, pa)
    if not np.all(np.isfinite(E[np.unique(s)])):
        raise FloatingPointError("TransE entity weights became nonfinite")
    return loss_sum, int(active.sum())


def score_transe(E, P, entities, relations, selected, candidate_rank):
    """Score the identical WSP104 top64-per-relation candidates; no new pool."""
    hits1 = 0
    hits10 = 0
    sum_reciprocal = 0.0
    unknown_subject_queries = 0
    unknown_candidate_occurrences = 0
    receipt = sha256()
    for (s, relation), answers in sorted(selected.items()):
        candidates = candidate_rank.get(relation, ())
        if not candidates:
            receipt.update(struct.pack("<II", 0, 0))
            continue
        si = int(np.searchsorted(entities, s))
        ri = int(np.searchsorted(relations, relation))
        have_s = si < len(entities) and int(entities[si]) == s
        have_r = ri < len(relations) and int(relations[ri]) == relation
        if not (have_s and have_r):
            unknown_subject_queries += 1
        values = np.asarray(candidates, dtype=np.uint32)
        ci = np.searchsorted(entities, values)
        exists = ci < len(entities)
        exists[exists] &= entities[ci[exists]] == values[exists]
        unknown_candidate_occurrences += int((~exists).sum())
        scores = np.full(len(values), -np.inf, dtype=np.float64)
        if have_s and have_r and exists.any():
            delta = E[si][None, :] + P[ri][None, :] - E[ci[exists]]
            scores[exists] = -np.einsum("ij,ij->i", delta, delta)
        order = sorted(range(len(candidates)), key=lambda i: (-scores[i], candidates[i]))
        rank = next((i + 1 for i, index in enumerate(order)
                     if candidates[index] in answers), 0)
        hits1 += int(rank == 1)
        hits10 += int(0 < rank <= 10)
        sum_reciprocal += 1 / rank if rank else 0.0
        receipt.update(struct.pack("<II", len(candidates), rank))
    n = len(selected)
    return {
        "hits1": hits1, "hits10": hits10,
        "hits1_rate": hits1 / n, "hits10_rate": hits10 / n,
        "mean_reciprocal_rank": sum_reciprocal / n,
        "unknown_subject_queries": unknown_subject_queries,
        "unknown_candidate_occurrences": unknown_candidate_occurrences,
        "score_receipt_sha256": receipt.hexdigest(),
    }


def fit_projected_transe(edges, selected, candidate_rank, *,
                        epochs=EPOCHS, dimension=DIM, batch_size=BATCH,
                        lr=LR, margin=MARGIN, seed=SEED,
                        started=None, wall_seconds=MAX_WALL_SECONDS):
    if started is None:
        started = time.monotonic()
    if epochs <= 0 or dimension <= 0 or batch_size <= 0 or float(lr) <= 0:
        raise ValueError("invalid projected TransE training parameters")
    entities, relations, subjects, relations_index, objects = id_maps(edges)
    check_budget(started, wall_seconds, rss_limit=MAX_RSS_BYTES)
    generator = np.random.Generator(np.random.PCG64(seed))
    init_scale = 1.0 / math.sqrt(dimension)
    E = generator.normal(0.0, init_scale,
                         size=(len(entities), dimension)).astype(np.float32)
    P = generator.normal(0.0, init_scale,
                         size=(len(relations), dimension)).astype(np.float32)
    project_rows(E)
    project_rows(P)
    untrained = score_transe(E, P, entities, relations, selected, candidate_rank)
    n = len(subjects)
    epoch_receipts = []
    for epoch in range(epochs):
        check_budget(started, wall_seconds, rss_limit=MAX_RSS_BYTES)
        order = generator.permutation(n)
        total_hinge = 0.0
        total_active = 0
        epoch_started = time.monotonic()
        for first in range(0, n, batch_size):
            if first % (batch_size * 16) == 0:
                check_budget(started, wall_seconds, rss_limit=MAX_RSS_BYTES)
            sample = order[first:first+batch_size]
            corrupted = generator.integers(
                0, len(entities), size=len(sample), dtype=np.int32)
            loss, active = transe_batch(
                E, P, subjects[sample], relations_index[sample],
                objects[sample], corrupted, lr=lr, margin=margin)
            total_hinge += loss
            total_active += active
        epoch_receipts.append({
            "epoch": epoch + 1,
            "retained_edges_processed": n,
            "mean_train_hinge_loss": total_hinge / n,
            "active_margin_fraction": total_active / n,
            "epoch_wall_seconds": time.monotonic() - epoch_started,
        })
    trained = score_transe(E, P, entities, relations, selected, candidate_rank)
    # Independent in-memory cold copy proves deterministic score restoration
    # but not cross-task retention, persistent knowledge, or model promotion.
    cold_score = score_transe(E.copy(), P.copy(), entities.copy(), relations.copy(),
                             selected, candidate_rank)
    if cold_score != trained:
        raise AssertionError("TransE cold-copy scores changed")
    return {
        "model_family": "TransE full-vocabulary projected sparse SGD",
        "entity_vocabulary_size": len(entities),
        "relation_vocabulary_size": len(relations),
        "retained_edges_trained_per_epoch": n,
        "training_epochs_completed": epochs,
        "embedding_dimension": dimension,
        "batch_size": batch_size,
        "seed": seed,
        "learning_rate": float(lr),
        "margin": float(margin),
        "training_epoch_receipts": epoch_receipts,
        "untrained": untrained,
        "trained": trained,
        "cold_copy_predictions_identical": True,
    }


def run_real_source():
    started = time.monotonic()
    cpu_start = time.process_time()
    _download_once, inspect_members = load_custody_helpers()
    with tempfile.TemporaryDirectory(prefix="wsp107-projected-transe-") as directory:
        archive = Path(directory) / "sealed-historical.tar.gz"
        custody = _download_once(archive)
        if (custody["compressed_sha256"] != ARCHIVE_SHA or
                custody["compressed_bytes"] != EXPECTED_ARCHIVE_BYTES):
            raise ValueError("sealed historical source archive changed")
        members = {(m["path"], m["type"], m["uncompressed_bytes"])
                   for m in inspect_members(archive)["members"]}
        if members != {
            ("wikidata5m", "directory", 0),
            ("wikidata5m/train.txt", "file", TRAIN_BYTES),
            ("wikidata5m/valid.txt", "file", 109498),
            ("wikidata5m/test.txt", "file", 108932),
        }:
            raise ValueError("archive member custody changed")
        open_train = lambda: open_train_only(archive)
        selected, hidden, source_sha = sample_groups(
            open_train, start=started, wall=MAX_WALL_SECONDS)
        edges, heavy, witness = read_retained_and_candidates(
            open_train, selected, hidden, start=started, wall=MAX_WALL_SECONDS)
        candidates, frequency_receipt, counts = exact_candidate_rankings(
            edges, heavy, selected, start=started, wall=MAX_WALL_SECONDS)
        result = fit_projected_transe(
            edges, selected, candidates, started=started,
            wall_seconds=MAX_WALL_SECONDS)
        check_budget(started, MAX_WALL_SECONDS, rss_limit=MAX_RSS_BYTES)
        return {
            "schema": "wsp107.full-retained-historical-projected-transe-dev.v1",
            "classification": "DEV_EXPLORATORY_CONVENTIONAL_TRANSLATION_BASELINE_NOT_INDEPENDENT_SCIENTIFIC_PASS",
            "source_archive_sha256": ARCHIVE_SHA,
            "source_train_sha256": source_sha,
            "historical_source_rows": TRAIN_ROWS,
            "retained_training_rows": len(edges) // 3,
            "masked_training_rows": hidden,
            "frozen_masked_query_groups": len(selected),
            "wsp103_masked_answer_sha256": witness,
            "wsp104_original_frequency_receipt_sha256": frequency_receipt,
            "wsp104_frequency_reverse_counts": counts,
            "wsp105_symbolic_path_first_hits1": WSP105_HITS[0],
            "wsp105_symbolic_path_first_hits10": WSP105_HITS[1],
            "wsp105_symbolic_path_first_mrr": WSP105_MRR,
            "wsp106_failed_distmult_preserved": True,
            "official_validation_test_read": False,
            "original_scientific_first_use": False,
            "fully_converged_baseline_demonstrated": False,
            "direct_weight_programmer_trained": False,
            "scientific_pass": False,
            "peak_rss_bytes": rss_max_bytes(),
            "full_process_cpu_seconds": time.process_time() - cpu_start,
            "full_process_wall_seconds": time.monotonic() - started,
            **result,
        }


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--frozen-transe-historical-dev", action="store_true", required=True)
    ap.parse_args()
    result = run_real_source()
    print("WSP107_PROJECTED_TRANSE_DEV=" +
          json.dumps(result, sort_keys=True, separators=(",", ":")), flush=True)
