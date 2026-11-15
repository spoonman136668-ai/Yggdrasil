#!/usr/bin/env python3
"""QTR-01 F42: lossless, compact Q-P-Q indexed graph, archived DEV only.

This is an exact symbolic knowledge-coordinate baseline, not native learning.
No new source, heldout, model, network or scheduled task is accessed.
"""
from hashlib import sha1, sha256
from itertools import product
import json
from pathlib import Path
import struct
from time import perf_counter

from f26_semantic_association import NotAdmitted, qnum
from f38_composition_dev import exact_answer_set
from f40_component_isolation_audit import audit, read_archives, validate
from f41_bit_scaling_dev import confusion

HERE = Path(__file__).resolve().parent
PREREG = HERE / "f42_prereg.json"
SCHEMA = "yggdrasil.qtr01.f42.lossless-indexed-knowledge-dev.v1"
PREREG_BLOB = "b9350c4278404a6f7f6a203d861a7132791313c5"
MAGIC = b"F42\x01"
RAW_HEADER = 8
DIGEST_LEN = 32
ROOTS = ("Q2", "Q5", "Q17", "Q30", "Q42", "Q64", "Q76", "Q80", "Q90", "Q95")


def preregistration(path=PREREG):
    raw = Path(path).read_bytes()
    git_blob = sha1(b"blob " + str(len(raw)).encode("ascii") + b"\x00" + raw).hexdigest()
    if git_blob != PREREG_BLOB:
        raise NotAdmitted("F42_FROZEN_PREREG_HASH_MISMATCH")
    doc = json.loads(raw)
    go = doc.get("evaluation", {}).get("frozen_go", {})
    encoding = doc.get("encoding_contract", {})
    source = doc.get("archive_custody", [])
    fences = doc.get("fences", {})
    if (doc.get("schema") != SCHEMA
        or doc.get("status") != "FROZEN_BEFORE_F42_EXECUTABLE_OR_FIRST_RESULT"
        or doc.get("parent_source_commit") != "24dc2248bb3e2cc8bc2a42e2e3170eddbe0a35cd"
        or doc.get("expected") != {
            "qids":78, "predicates":8, "triples":82,
            "old_triples":33, "new_triples":49,
            "undirected_components":7, "observed_twohop_queries":46, "root_count":10}
        or doc.get("evaluation", {}).get("roots") != list(ROOTS)
        or [(d.get("sha256"), d.get("rows")) for d in source] != [
            ("e9ead9ac15e4ecbe4d99216cda43657e1aeb030d22f59fd852f8b99fa0d440eb", 13),
            ("cf5ffeab63384a61e66e30930f16ce3af07df81cb28472b0142f7a5c6b673954", 20),
            ("7d223dcb9d9082059cdc237d7a551c2a3a0f21ca81824318bec1624aa25c4044", 49)]
        or encoding.get("full_payload_bytes") != 630
        or encoding.get("baseline_triple_coordinate_bytes") != 984
        or encoding.get("minimum_declared_saving_bytes") != 354
        or go != {
            "source_positive_recall":1,
            "membership_false_positives":0,
            "composition_false_positives":0,
            "composition_false_negatives":0,
            "serialized_payload_bytes_max":630,
            "raw_coordinate_bytes":984,
            "cold_bit_exact":True,
            "delete_one_readd_exact":True,
            "cross_platform_byte_digest_equal":True}
        or any(fences.get(flag) is not True for flag in (
            "no_new_source_http", "no_reserved_qid_first_use",
            "no_native_recipient_weights", "no_scientific_first_use",
            "no_other_model_changes", "no_merge", "no_main_or_accepted_ref",
            "no_controller_or_scheduler", "no_paid_api",
            "no_touch_original_f41", "no_unapproved_deployment"))):
        raise NotAdmitted("F42_FROZEN_CONTRACT_DRIFT")
    return doc


def is_strictly_increasing(vals):
    return all(type(x) is int and 0 < x < 2**32 for x in vals) and (
        all(x < y for x, y in zip(vals, vals[1:])))


class ExactIndex:
    """Stores known Q/P integer coordinates with a reversible 1-byte local ID index."""

    def __init__(self, qids, predicates):
        if (type(qids) not in (list, tuple) or type(predicates) not in (list, tuple)
            or not 0 < len(qids) <= 255 or not 0 < len(predicates) <= 255
            or not is_strictly_increasing(qids)
            or not is_strictly_increasing(predicates)):
            raise NotAdmitted("F42_INVALID_INDEX_VOCABULARY")
        self.qids = tuple(qids)
        self.predicates = tuple(predicates)
        self.qindex = {v: i for i, v in enumerate(self.qids)}
        self.pindex = {v: i for i, v in enumerate(self.predicates)}
        self._edges = set()

    def _ordinals(self, triple):
        if type(triple) is not tuple or len(triple) != 3 or any(type(x) is not int or not 0 < x < 2**32 for x in triple):
            raise NotAdmitted("F42_INVALID_NUMERIC_TRIPLE")
        s, p, o = triple
        if s not in self.qindex or o not in self.qindex or p not in self.pindex:
            raise NotAdmitted("F42_UNKNOWN_VOCABULARY_COORDINATE")
        return (self.qindex[s], self.pindex[p], self.qindex[o])

    def insert(self, triple):
        ords = self._ordinals(triple)
        if ords in self._edges or len(self._edges) >= 65535:
            raise NotAdmitted("F42_DUPLICATE_OR_EXCESS_SOURCE_FACT")
        self._edges.add(ords)

    def delete(self, triple):
        ords = self._ordinals(triple)
        if ords not in self._edges:
            raise NotAdmitted("F42_DELETION_OF_UNSEEN_FACT")
        self._edges.remove(ords)

    def contains(self, triple):
        return self._ordinals(triple) in self._edges

    def decoded_triples(self):
        return tuple((self.qids[s], self.predicates[p], self.qids[o])
                     for s, p, o in sorted(self._edges))

    def snapshot(self):
        header = struct.pack("<4sBBH", MAGIC, len(self.qids),
                             len(self.predicates), len(self._edges))
        numeric_vocab = struct.pack("<" + "I" * (len(self.qids) + len(self.predicates)),
                                    *self.qids, *self.predicates)
        indices = b"".join(bytes(t) for t in sorted(self._edges))
        original = header + numeric_vocab + indices
        return original + sha256(original).digest()

    @classmethod
    def restore(cls, raw):
        if type(raw) is not bytes or len(raw) < RAW_HEADER + DIGEST_LEN:
            raise NotAdmitted("F42_TRUNCATED_OR_NONCANONICAL_SNAPSHOT")
        magic, nq, np, count = struct.unpack_from("<4sBBH", raw, 0)
        if magic != MAGIC or not nq or not np:
            raise NotAdmitted("F42_HEADER_VERSION_OR_COUNTS_INVALID")
        expected = RAW_HEADER + 4*(nq + np) + 3*count + DIGEST_LEN
        if len(raw) != expected or sha256(raw[:-DIGEST_LEN]).digest() != raw[-DIGEST_LEN:]:
            raise NotAdmitted("F42_SNAPSHOT_LENGTH_OR_DIGEST_MISMATCH")
        offset = RAW_HEADER
        vocabulary = struct.unpack_from("<" + "I"*(nq+np), raw, offset)
        qids, predicates = vocabulary[:nq], vocabulary[nq:]
        index = cls(qids, predicates)
        offset += 4*(nq+np)
        payload = raw[offset:-DIGEST_LEN]
        ordered = tuple(tuple(payload[i:i+3]) for i in range(0, len(payload), 3))
        if len(set(ordered)) != count or list(ordered) != sorted(ordered):
            raise NotAdmitted("F42_DUPLICATE_OR_NONCANONICAL_TRIPLET_ORDER")
        for a, p, b in ordered:
            if a >= nq or b >= nq or p >= np:
                raise NotAdmitted("F42_OUT_OF_RANGE_INDEX")
            index.insert((qids[a], predicates[p], qids[b]))
        if index.snapshot() != raw:
            raise NotAdmitted("F42_NONCANONICAL_COLD_REHYDRATION")
        return index


def source_facts():
    p = preregistration()
    archive = audit()
    if (archive["distinct_triples"] != 82
        or archive["distinct_entities"] != 78
        or archive["local_graph_components"] != 7
        or archive["scientific_pass"] is not False
        or archive["global_historical_first_use_certified"] is not False
        or archive["new_source_requests"] != 0):
        raise NotAdmitted("F42_ORIGINAL_ARCHIVE_AUDIT_DRIFT")
    docs = read_archives()
    groups, rows, _ = validate(docs)
    if [len(g) for g in groups] != [13, 20, 49]:
        raise NotAdmitted("F42_ARCHIVE_GROUP_BOUNDARY_DRIFT")
    triples = tuple((qnum(s, "Q"), qnum(pred, "P"), qnum(o, "Q"))
                    for s, pred, o in rows)
    if len(set(triples)) != 82:
        raise NotAdmitted("F42_SOURCE_DUPLICATE")
    qids = tuple(sorted(set(x for s, _, o in triples for x in (s, o))))
    pids = tuple(sorted(set(pred for _, pred, _ in triples)))
    if len(qids) != p["expected"]["qids"] or len(pids) != p["expected"]["predicates"]:
        raise NotAdmitted("F42_VOCABULARY_SIZE_DRIFT")
    return qids, pids, triples[:33], triples[33:]


def measure():
    p = preregistration()
    qids, pids, original, added = source_facts()
    graph = original + added
    started = perf_counter()
    memory = ExactIndex(qids, pids)
    for edge in original:
        memory.insert(edge)
    first_cold = ExactIndex.restore(memory.snapshot())
    if set(first_cold.decoded_triples()) != set(original):
        raise NotAdmitted("F42_OLD_SOURCE_COLD_RESTORE_MISMATCH")
    for edge in added:
        memory.insert(edge)
    snapshot = memory.snapshot()
    cold = ExactIndex.restore(snapshot)
    if snapshot != cold.snapshot() or set(cold.decoded_triples()) != set(graph):
        raise NotAdmitted("F42_INCREMENTAL_COLD_RESTORE_DRIFT")

    roots = tuple(qnum(x,"Q") for x in ROOTS)
    actual_members = set(cold.decoded_triples())
    truth_members = set(graph)
    member_total = len(qids)*len(pids)*len(qids)
    actual_member_conf = confusion(actual_members, truth_members, member_total)

    # Compose the bounded 49,920-query universe against same sourced graph.
    exact_source_twohop = exact_answer_set(graph, roots, pids, qids)
    observed_twohop = exact_answer_set(cold.decoded_triples(), roots, pids, qids)
    candidate_total = len(roots)*len(pids)*len(pids)*len(qids)
    twohop_score = confusion(observed_twohop, exact_source_twohop, candidate_total)
    if len(exact_source_twohop) != p["expected"]["observed_twohop_queries"]:
        raise NotAdmitted("F42_TWOHOP_SOURCE_QUERY_DRIFT")

    # Deliberate development-only reversible update, not source revision science.
    chosen = min(graph)
    cold.delete(chosen)
    deleted = ExactIndex.restore(cold.snapshot())
    if (deleted.contains(chosen) or len(deleted.decoded_triples()) != 81
        or set(deleted.decoded_triples()) != truth_members - {chosen}):
        raise NotAdmitted("F42_DELETE_SOURCE_NEGATIVE_CONTROL_FAILED")
    deleted.insert(chosen)
    restored = ExactIndex.restore(deleted.snapshot())
    if restored.snapshot() != snapshot:
        raise NotAdmitted("F42_READD_NOT_EXACT_OR_CANONICAL")

    source_bytes = tuple((HERE/"evidence"/entry["file"]).stat().st_size
                         for entry in p["archive_custody"])
    raw_numeric_coordinate_bytes = len(graph)*12
    actual_payload = len(snapshot)
    expected_length = 8 + 4*(len(qids)+len(pids)) + 3*len(graph) + 32
    if actual_payload != expected_length:
        raise NotAdmitted("F42_SNAPSHOT_LAYOUT_DRIFT")
    metrics = {
        "schema":SCHEMA,
        "source_parent":p["parent_source_commit"],
        "classification":"DEV_EXACT_INDEX_GO",
        "archived_source_rows":[13,20,49],
        "source_archive_external_bytes":sum(source_bytes),
        "source_archive_external_bytes_per_file":source_bytes,
        "source_triples":len(graph),
        "old_source_facts_cold_restored":len(original),
        "new_source_facts_programmed":len(added),
        "q_entity_vocab_size":len(qids),
        "p_predicate_vocab_size":len(pids),
        "header_bytes":8,
        "coordinate_vocabulary_bytes":4*(len(qids)+len(pids)),
        "byte_indexed_triplet_bytes":3*len(graph),
        "sha256_trailer_bytes":32,
        "total_reversible_graph_payload_bytes":actual_payload,
        "raw_numeric_triplet_control_bytes":raw_numeric_coordinate_bytes,
        "absolute_payload_savings_bytes":raw_numeric_coordinate_bytes-actual_payload,
        "relative_payload_savings_fraction":(raw_numeric_coordinate_bytes-actual_payload)/raw_numeric_coordinate_bytes,
        "source_inclusive_index_and_archive_bytes":sum(source_bytes)+actual_payload,
        "source_inclusive_raw_and_archive_bytes":sum(source_bytes)+raw_numeric_coordinate_bytes,
        "source_labels_and_claim_witnesses_not_embedded_in_index":True,
        "snapshot_sha256":sha256(snapshot).hexdigest(),
        "membership_candidate_count":member_total,
        "membership_confusion":actual_member_conf,
        "twohop_candidate_count":candidate_total,
        "source_witnessed_positive_twohop_queries":len(exact_source_twohop),
        "twohop_confusion":twohop_score,
        "cold_snapshot_byte_exact":True,
        "reversible_delete_readd_byte_exact":True,
        "canonical_sorted_index":True,
        "evaluation_wall_seconds_dev_only":round(perf_counter()-started,6),
        "new_source_requests":0,
        "reserved_scientific_first_use_consumed":False,
        "fully_trained_comparison_performed":False,
        "native_recipient_weights_edited":False,
        "scientific_pass":False
    }
    go = p["evaluation"]["frozen_go"]
    if not (
        actual_member_conf["recall"] == go["source_positive_recall"]
        and actual_member_conf["fp"] == go["membership_false_positives"]
        and actual_member_conf["fn"] == 0
        and twohop_score["fp"] == go["composition_false_positives"]
        and twohop_score["fn"] == go["composition_false_negatives"]
        and actual_payload <= go["serialized_payload_bytes_max"]
        and raw_numeric_coordinate_bytes == go["raw_coordinate_bytes"]):
        metrics["classification"] = "DEV_EXACT_INDEX_NO_GO"
    return metrics


def main():
    report = measure()
    print("F42_EXACT_INDEX_SOURCE_ONLY_RESULT="+json.dumps(report,sort_keys=True,separators=(",", ":")))
    print("F42_NEW_SCIENCE_FIRST_USE=NONE")
    if report["classification"] != "DEV_EXACT_INDEX_GO":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
