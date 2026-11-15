"""WSP116 source-safe fixtures; NO historical archive/heldout source is touched."""
from __future__ import annotations
import hashlib
from io import BytesIO
from pathlib import Path
import struct
import sys
import unittest

import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import tiered


def fabricated_source():
    """Real schema only, fictional Q/P IDs, nonprivileged known fixture."""
    lines=[]
    for s in range(101,165):
        for p in range(1,4):
            for k in range(2):
                o=101+((s*11+p*17+k*3)%64)
                lines.append(f"Q{s}\tP{p}\tQ{o}\n".encode("ascii"))
    return b"".join(lines)


class TestWSP116(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=fabricated_source()
        cls.facts=len(cls.raw.splitlines())
        cls.digest=hashlib.sha256(cls.raw).hexdigest()
        cls.kwargs=dict(expected_rows=cls.facts,
                        expected_bytes=len(cls.raw),
                        expected_sha=cls.digest,
                        expected_relations=3,query_count=4,
                        expected_answers_sha=None,expected_full=None,
                        expected_freq_sha=None,max_wall_seconds=30)

    @staticmethod
    def opened(raw):
        class Stream:
            def __enter__(self):
                self.buf=BytesIO(raw)
                return self.buf
            def __exit__(self,*exc):
                self.buf.close()
        return Stream()

    def test_three_pass_nested_real_format_and_exact_numeric_symbolic_parity(self):
        result=tiered.evaluate(lambda:self.opened(self.raw),**self.kwargs)
        self.assertEqual(result["schema"],
                         "wsp116.consumed-historical-realgraph-tiered-source.v1")
        self.assertFalse(result["development_first_use"])
        self.assertFalse(result["protected_first_use"])
        self.assertFalse(result["official_validation_test_opened"])
        self.assertFalse(result["scientific_pass"])
        self.assertEqual(result["source_rows"],self.facts)
        self.assertEqual(result["source_train_sha256"],self.digest)
        self.assertEqual(result["masked_query_groups"],4)
        self.assertEqual(len(result["tiers"]),3)
        tiers=result["tiers"]
        self.assertEqual([a["source_fraction_num"] for a in tiers],[16,64,256])
        self.assertLessEqual(tiers[0]["retained_source_facts"],tiers[1]["retained_source_facts"])
        self.assertLessEqual(tiers[1]["retained_source_facts"],tiers[2]["retained_source_facts"])
        self.assertEqual(tiers[2]["retained_source_facts"],
                         self.facts-result["masked_training_rows"])
        for t in tiers:
            self.assertEqual(t["programmed_raw_numeric_bytes"],
                             12*t["retained_source_facts"])
            self.assertEqual(t["programmed_raw_uint32_fact_weights"],
                             3*t["retained_source_facts"])
            self.assertEqual(len(t["programmed_numeric_cold_sha256"]),64)
            self.assertEqual(t["numeric_symbolic_rank_parity_queries"],4)
            self.assertLessEqual(t["metrics"]["path_first"]["hits1"],4)
        self.assertEqual(len(result["full_minus_quarter_bootstrap_world_ci95"]),2)
        repeat=tiered.evaluate(lambda:self.opened(self.raw),**self.kwargs)
        self.assertEqual([x["programmed_numeric_cold_sha256"] for x in tiers],
                         [x["programmed_numeric_cold_sha256"] for x in repeat["tiers"]])
        self.assertEqual(result["full_minus_quarter_path_first_hits1_count"],
                         repeat["full_minus_quarter_path_first_hits1_count"])

    def test_tier_membership_independent_of_scoring_and_frozen(self):
        records=[(101,2,103),(119,1,122),(155,3,111)]
        bins=[tiered.member_bucket(*x) for x in records]
        self.assertEqual(bins,[tiered.member_bucket(*x) for x in records])
        self.assertTrue(all(0<=b<256 for b in bins))
        for s,p,o in records:
            expected=hashlib.sha256(tiered.TIER_DOMAIN+
                        struct.pack("<III",s,p,o)).digest()[0]
            self.assertEqual(tiered.member_bucket(s,p,o),expected)
        self.assertEqual(tiered.TIERS,(16,64,256))

    def test_rank_weights_equal_independent_symbolic(self):
        base=[12,9,21,7]
        votes={7:2,12:2,9:5}
        counts={9:100,12:50,7:50,21:1000}
        symbolic=sorted(base,key=lambda x:(-votes.get(x,0),-counts.get(x,0),x))
        self.assertEqual(tiered.numpy_rank(base,counts,votes),symbolic)
        self.assertEqual(tiered.numpy_rank([],counts,votes),[])
        with self.assertRaises(ValueError):
            tiered.paired_bootstrap([1],[1,0])
        with self.assertRaises(ValueError):
            tiered.paired_bootstrap([2],[0])

    def test_source_sha_and_answer_custody_must_match(self):
        bad=dict(self.kwargs,expected_sha="0"*64)
        with self.assertRaisesRegex(ValueError,"SHA_ROW_RELATION_OR_SAMPLE_DRIFT"):
            tiered.evaluate(lambda:self.opened(self.raw),**bad)
        bad_answer=dict(self.kwargs,expected_answers_sha="0"*64)
        with self.assertRaisesRegex(ValueError,"ANSWER_WITNESS_DRIFT"):
            tiered.evaluate(lambda:self.opened(self.raw),**bad_answer)
        with self.assertRaisesRegex(ValueError,"FROZEN_SOURCE_LIMIT"):
            tiered.evaluate(lambda:self.opened(self.raw),
                            **dict(self.kwargs,query_count=0))

    def test_no_hidden_learning_or_original_source_in_fixtures(self):
        import ast
        source=(HERE/"tiered.py").read_text(encoding="utf-8")
        ast.parse(source)
        self.assertNotIn("env.unwrapped",source)
        self.assertNotIn("train.txt"+"test.txt",source)
        self.assertIn("WSP116-TIER-v1",source)
        self.assertIn("open_train_only",source)
        self.assertIn("scientific_pass",source)

if __name__=="__main__":
    unittest.main()
