#!/usr/bin/env python3
"""QTR F34: program source association bits directly; DEV, not recipient weights.

The exact first-party CC0 archive remains the sole information source.
This representation answers ONLY full Q-P-Q membership queries. It cannot
enumerate objects, recall original language labels, delete facts or learn.
"""
from hashlib import blake2b, sha256
from itertools import product
import json
from pathlib import Path
import struct

from f26_semantic_association import NotAdmitted, qnum

SOURCE = Path(__file__).parent / "evidence" / "f32_source_snapshot.json"
POLICY = Path(__file__).with_name("f34_prereg.json")
SOURCE_SHA256 = "e9ead9ac15e4ecbe4d99216cda43657e1aeb030d22f59fd852f8b99fa0d440eb"
PREREG_COMMIT = "4267cb0accbb14f99f5f110e24d463bececcaeb5"
SCHEMA = "yggdrasil.qtr01.f34.direct-binary-association-weight-dev.v1"
BITS = 512
K = 3
BYTES = 64
PERSON = b"QTRF34"


def preflight():
    p = json.loads(POLICY.read_text(encoding="utf-8"))
    if (p.get("schema") != SCHEMA or
        p.get("status") != "FROZEN_BEFORE_BITWEIGHT_CODE_AND_RESULTS" or
        p.get("source_sha256") != SOURCE_SHA256 or
        p.get("source_git_blob") != "453dad0363689cff785c26db5441555c6841f95d" or
        p.get("source_rows") != 13 or
        p.get("source_integer_triplet_bytes") != 156 or
        p.get("source_observed_twohop_queries") != 0 or
        p.get("frozen_go", {}).get("false_positive_rate_max") != 0.01 or
        p.get("frozen_go", {}).get("weight_bytes") != BYTES or
        p.get("frozen_go", {}).get("observed_source_membership_count") != 13 or
        p.get("frozen_go", {}).get("cold_snapshot_exact") is not True):
        raise NotAdmitted("F34_SOURCE_OR_FROZEN_WEIGHT_SCOPE_DRIFT")
    return p


def parse_source(raw):
    if type(raw) is not bytes or sha256(raw).hexdigest() != SOURCE_SHA256:
        raise NotAdmitted("F34_FIRST_PARTY_SOURCE_HASH_MISMATCH")
    d = json.loads(raw)
    if (d.get("schema") != "yggdrasil.qtr01.f31.first-party-all-language-fact-custody.v1" or
        d.get("structured_data_license") != "CC0" or
        d.get("native_recipient_model_weights_edited") is not False or
        d.get("scientific_pass") is not False or
        d.get("matched_symbolic_numeric_control", {}).get("actual_observed_twohop_queries") != 0):
        raise NotAdmitted("F34_NOT_THE_VERIFIED_F31_SOURCE")
    rows = d.get("typed_source_rows")
    if type(rows) is not list or len(rows) != 13:
        raise NotAdmitted("F34_SOURCE_COUNT_DRIFT")
    triples = []
    for row in rows:
        if type(row) is not dict or not all(row.get(k) for k in (
            "s_label", "p_label", "o_label",
            "s_language", "p_language", "o_language", "source_claim"
        )):
            raise NotAdmitted("F34_SOURCE_LABEL_PROVENANCE_MISSING")
        if (not row["source_claim"].startswith(row["s"] + "$") or
            type(row.get("source_revision")) is not int or row["source_revision"] <= 0):
            raise NotAdmitted("F34_FIRST_PARTY_CLAIM_OR_REVISION_MISSING")
        triples.append((qnum(row["s"], "Q"), qnum(row["p"], "P"), qnum(row["o"], "Q")))
    if len(set(triples)) != 13:
        raise NotAdmitted("F34_DUPLICATE_SOURCE_TRIPLE")
    return sorted(triples)


def load_triples():
    preflight()
    return parse_source(SOURCE.read_bytes())


class DirectBitWeights:
    """Exactly 512 bytes? No: 512 individual BITS = 64 persistent payload bytes."""
    def __init__(self, raw=None):
        if raw is None:
            self.data = bytearray(BYTES)
        elif type(raw) is bytes and len(raw) == BYTES:
            self.data = bytearray(raw)
        else:
            raise NotAdmitted("F34_NONCANONICAL_BITWEIGHT_SNAPSHOT")

    @staticmethod
    def slots(triple):
        if (type(triple) is not tuple or len(triple) != 3 or
            any(type(v) is not int or not 0 < v < 2**32 for v in triple)):
            raise NotAdmitted("F34_INVALID_NUMERIC_SOURCE_OR_QUERY")
        packed = struct.pack("<III", *triple)
        digest = blake2b(packed, digest_size=16, person=PERSON).digest()
        return tuple(struct.unpack_from("<I", digest, i * 4)[0] % BITS for i in range(K))

    def program(self, triple):
        for pos in self.slots(triple):
            self.data[pos >> 3] |= 1 << (pos & 7)

    def contains(self, triple):
        return all(self.data[pos >> 3] & (1 << (pos & 7)) for pos in self.slots(triple))

    def snapshot(self):
        return bytes(self.data)


def measurement(triples):
    if len(triples) != 13 or len(set(triples)) != 13:
        raise NotAdmitted("F34_PROTECTED_SOURCE_COUNT_CHANGED")
    weights = DirectBitWeights()
    for triple in triples:
        weights.program(triple)
    raw = weights.snapshot()
    cold = DirectBitWeights(raw)
    ids = sorted(set(x for s, _, o in triples for x in (s, o)))
    props = sorted(set(p for _, p, _ in triples))
    baseline = set(triples)
    false_neg = sum(not weights.contains(x) for x in triples)
    universe_size = len(ids) * len(props) * len(ids)
    unseen = [t for t in product(ids, props, ids) if t not in baseline]
    false_pos = sum(weights.contains(x) for x in unseen)
    negatives = len(unseen)
    fpr = false_pos / negatives
    cold_matches = cold.snapshot() == raw and all(
        cold.contains(t) == weights.contains(t) for t in product(ids, props, ids)
    )

    shuffled = [(s, p, triples[(i + 1) % len(triples)][2])
                for i, (s, p, _) in enumerate(triples)]
    if set(shuffled) == baseline:
        raise NotAdmitted("F34_SHUFFLED_NEGATIVE_NOT_DIFFERENT")
    sham = DirectBitWeights()
    for t in shuffled:
        sham.program(t)
    source_recognition_in_sham = sum(sham.contains(x) for x in triples)

    added = unseen[:3]
    if len(added) != 3:
        raise NotAdmitted("F34_INSUFFICIENT_SOURCE_DOMAIN_NEGATIVE_CONTROLS")
    additive = DirectBitWeights(raw)
    for t in added:
        additive.program(t)
    old_source_preserved = all(additive.contains(x) for x in triples)
    synthetic_additions_recognized = all(additive.contains(x) for x in added)

    if not (len(raw) == BYTES and false_neg == 0 and
            fpr <= 0.01 and cold_matches and old_source_preserved and
            synthetic_additions_recognized and source_recognition_in_sham < 13):
        raise NotAdmitted("F34_FROZEN_DEVELOPMENT_WEIGHT_GATE_NO_GO")
    return {
        "source_sha256": SOURCE_SHA256,
        "source_positive_triples": len(triples),
        "source_subject_object_ids": len(ids),
        "source_predicate_ids": len(props),
        "finite_source_domain_queries": universe_size,
        "source_unseen_triples_in_finite_domain": negatives,
        "false_negatives": false_neg,
        "false_positives": false_pos,
        "false_positive_rate": fpr,
        "direct_programmed_weight_payload_bytes": len(raw),
        "exact_sparse_control_triplet_bytes": len(triples) * 12,
        "hashes_per_membership": K,
        "exact_cold_snapshot_and_query_parity": cold_matches,
        "shuffled_control_original_hits": source_recognition_in_sham,
        "synthetic_added_non_source_triples": len(added),
        "old_source_membership_preserved_after_synthetic_additions": old_source_preserved,
        "source_has_real_composable_twohop_queries": False,
        "can_enumerate_objects_or_delete_fact": False,
        "source_label_and_provenance_storage_not_in_payload": True,
        "neural_recipient_weights_edited": False,
        "scientific_pass": False,
        "development_bitweight_result": "F34_DEV_BITWEIGHT_CANDIDATE_ONLY",
    }


def main():
    obj = measurement(load_triples())
    print("F34_DIRECT_WEIGHTS_RESULT=" + json.dumps(obj, sort_keys=True, separators=(",", ":")))
    print("F34_NO_NATIVE_NEURAL_MODEL_FIRST_USE=PASS")


if __name__ == "__main__":
    main()
