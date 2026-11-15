"""F42: source-free exact indexed relation storage and negative controls."""
from hashlib import sha256
import json
import struct
import tempfile
from pathlib import Path
import unittest

from f26_semantic_association import NotAdmitted
from f42_exact_index_dev import (
    ExactIndex, MAGIC, PREREG, preregistration, source_facts, measure
)


def with_digest(payload):
    return payload + sha256(payload).digest()


def mutate_body(snapshot, offset, value):
    payload = bytearray(snapshot[:-32])
    payload[offset] = value
    return with_digest(bytes(payload))


class TestF42ExactIndex(unittest.TestCase):
    def test_source_preregistration_immutable_and_no_first_use(self):
        frozen = preregistration()
        self.assertEqual(frozen["parent_source_commit"],
                         "24dc2248bb3e2cc8bc2a42e2e3170eddbe0a35cd")
        self.assertEqual(frozen["encoding_contract"]["full_payload_bytes"],630)
        self.assertEqual(frozen["expected"]["triples"], 82)
        for v in frozen["fences"].values():
            self.assertIs(v, True)
        with tempfile.TemporaryDirectory() as td:
            modified = json.loads(PREREG.read_text(encoding="utf-8"))
            modified["evaluation"]["frozen_go"]["composition_false_positives"] = 100
            path = Path(td)/"mutated.json"
            path.write_text(json.dumps(modified),encoding="utf-8")
            with self.assertRaisesRegex(NotAdmitted,"FROZEN_PREREG_HASH_MISMATCH"):
                preregistration(path)

    def test_exact_f32_f35_f39_source_inventory(self):
        q, p, old, added = source_facts()
        self.assertEqual((len(q),len(p),len(old),len(added)),(78,8,33,49))
        self.assertEqual(len(set(old+added)), 82)

    def test_canonical_encoding_and_cross_order_parity(self):
        q,p,old,added = source_facts()
        a,b = ExactIndex(q,p),ExactIndex(q,p)
        for e in old+added:
            a.insert(e)
        for e in reversed(old+added):
            b.insert(e)
        snapshot=a.snapshot()
        self.assertEqual(snapshot,b.snapshot())
        self.assertEqual(snapshot,ExactIndex.restore(snapshot).snapshot())
        self.assertEqual(snapshot[:4],MAGIC)
        header_magic,nq,np,nt=struct.unpack_from("<4sBBH",snapshot)
        self.assertEqual((header_magic,nq,np,nt),(MAGIC,78,8,82))
        self.assertEqual(len(snapshot),630)
        self.assertEqual(sha256(snapshot[:-32]).digest(),snapshot[-32:])

    def test_negative_corrupt_digest_and_truncation(self):
        q,p,old,added=source_facts()
        mem=ExactIndex(q,p)
        for e in old+added: mem.insert(e)
        raw=mem.snapshot()
        for corrupted in (
            raw[:-1],raw+b"\x00",
            raw[:-1]+bytes([raw[-1]^1]),
            bytes([raw[0]^1])+raw[1:]
        ):
            with self.subTest(length=len(corrupted)),self.assertRaises(NotAdmitted):
                ExactIndex.restore(corrupted)
        with self.assertRaisesRegex(NotAdmitted,"TRUNCATED_OR_NONCANONICAL"):
            ExactIndex.restore(b"")

    def test_negative_noncanonical_or_duplicate_index(self):
        q,p,old,added=source_facts()
        mem=ExactIndex(q,p)
        for e in old+added: mem.insert(e)
        raw=mem.snapshot()
        offset=8+4*(len(q)+len(p))
        # Validly recomputed checksums do not rescue two duplicate rows.
        dup = bytearray(raw[:-32])
        dup[offset+3:offset+6] = dup[offset:offset+3]
        with self.assertRaisesRegex(NotAdmitted,"DUPLICATE_OR_NONCANONICAL"):
            ExactIndex.restore(with_digest(bytes(dup)))
        # Nor can an attested payload encode a noncanonical row order.
        swapped=bytearray(raw[:-32])
        a,b=bytes(swapped[offset:offset+3]),bytes(swapped[offset+3:offset+6])
        self.assertNotEqual(a,b)
        swapped[offset:offset+3]=b
        swapped[offset+3:offset+6]=a
        with self.assertRaisesRegex(NotAdmitted,"DUPLICATE_OR_NONCANONICAL"):
            ExactIndex.restore(with_digest(bytes(swapped)))
        with self.assertRaisesRegex(NotAdmitted,"OUT_OF_RANGE_INDEX"):
            ExactIndex.restore(mutate_body(raw, offset, 255))

    def test_negative_noncanonical_dictionary_even_with_valid_digest(self):
        q,p,old,added=source_facts()
        mem=ExactIndex(q,p)
        for e in old+added: mem.insert(e)
        raw=mem.snapshot()
        with self.assertRaisesRegex(NotAdmitted,"INVALID_INDEX_VOCABULARY"):
            ExactIndex.restore(mutate_body(raw, 8, 0))
        # Reverse two Q numeric IDs; checksum is updated but canonical check fails.
        changed=bytearray(raw[:-32])
        changed[8:12],changed[12:16]=bytes(changed[12:16]),bytes(changed[8:12])
        with self.assertRaisesRegex(NotAdmitted,"INVALID_INDEX_VOCABULARY"):
            ExactIndex.restore(with_digest(bytes(changed)))

    def test_negative_unknown_coordinate_duplicate_and_missing_delete(self):
        q,p,old,added=source_facts()
        m=ExactIndex(q,p)
        m.insert(old[0])
        with self.assertRaisesRegex(NotAdmitted,"DUPLICATE_OR_EXCESS"):
            m.insert(old[0])
        with self.assertRaisesRegex(NotAdmitted,"UNKNOWN_VOCABULARY"):
            m.insert((999999999,p[0],q[0]))
        with self.assertRaisesRegex(NotAdmitted,"UNKNOWN_VOCABULARY"):
            m.contains((q[0],99999,q[1]))
        with self.assertRaisesRegex(NotAdmitted,"DELETION_OF_UNSEEN"):
            m.delete(old[1])

    def test_invalid_coordinate_and_vocabulary_shape(self):
        for q,p in (
            ([],[1]), ([0,1],[1]), ([1,1],[1]), ([2,1],[1]),
            ([1],[1,1]), ([1],[]), (list(range(1,257)),[1])
        ):
            with self.subTest(q=len(q),p=len(p)),self.assertRaisesRegex(NotAdmitted,"INVALID_INDEX_VOCABULARY"):
                ExactIndex(q,p)
        m=ExactIndex((1,2),(3,))
        for invalid in ((1,3),[1,3,2],(True,3,2),(0,3,2),(1,3,2,4)):
            with self.subTest(invalid=invalid),self.assertRaisesRegex(NotAdmitted,"INVALID_NUMERIC_TRIPLE"):
                m.insert(invalid)

    def test_incremental_cold_and_delete_readd(self):
        q,p,old,added=source_facts()
        mem=ExactIndex(q,p)
        for e in old:mem.insert(e)
        old_snap=mem.snapshot()
        self.assertEqual(len(ExactIndex.restore(old_snap).decoded_triples()),33)
        for e in added:mem.insert(e)
        snap=mem.snapshot()
        cold=ExactIndex.restore(snap)
        self.assertEqual(set(cold.decoded_triples()),set(old+added))
        one=min(old+added)
        cold.delete(one)
        deleted=ExactIndex.restore(cold.snapshot())
        self.assertFalse(deleted.contains(one))
        self.assertEqual(len(deleted.decoded_triples()),81)
        deleted.insert(one)
        self.assertEqual(deleted.snapshot(),snap)

    def test_real_archived_mechanics_and_all_bounded_queries(self):
        v=measure()
        self.assertEqual(v["classification"],"DEV_EXACT_INDEX_GO")
        self.assertEqual((v["q_entity_vocab_size"],v["p_predicate_vocab_size"]),(78,8))
        self.assertEqual(v["source_triples"],82)
        self.assertEqual(v["total_reversible_graph_payload_bytes"],630)
        self.assertEqual(v["raw_numeric_triplet_control_bytes"],984)
        self.assertEqual(v["absolute_payload_savings_bytes"],354)
        self.assertEqual(v["coordinate_vocabulary_bytes"],344)
        self.assertEqual(v["byte_indexed_triplet_bytes"],246)
        self.assertEqual(v["membership_candidate_count"],48672)
        self.assertEqual(v["twohop_candidate_count"],49920)
        self.assertEqual(v["source_witnessed_positive_twohop_queries"],46)
        self.assertEqual((v["membership_confusion"]["tp"],
                          v["membership_confusion"]["fp"],
                          v["membership_confusion"]["fn"]),(82,0,0))
        self.assertEqual((v["twohop_confusion"]["tp"],
                          v["twohop_confusion"]["fp"],
                          v["twohop_confusion"]["fn"]),(46,0,0))
        self.assertTrue(v["cold_snapshot_byte_exact"])
        self.assertTrue(v["reversible_delete_readd_byte_exact"])
        self.assertEqual(v["source_inclusive_raw_and_archive_bytes"]-
                         v["source_inclusive_index_and_archive_bytes"],354)
        for field in ("scientific_pass","native_recipient_weights_edited",
                      "reserved_scientific_first_use_consumed",
                      "fully_trained_comparison_performed"):
            self.assertIs(v[field], False)
        self.assertEqual(v["new_source_requests"],0)


if __name__ == "__main__":
    unittest.main()
