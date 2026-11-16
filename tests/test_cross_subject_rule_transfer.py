"""NKR-11: source-free subject-disjoint transfer and leakage falsification."""
from __future__ import annotations

from collections import defaultdict
import importlib.util
from pathlib import Path
import unittest

SCRIPT=Path(__file__).resolve().parents[1] / "research/contrib/chatgpt/NKR-11/heldout_transfer.py"
spec=importlib.util.spec_from_file_location("nkr11_source_free",SCRIPT)
study=importlib.util.module_from_spec(spec)
spec.loader.exec_module(study)


class FakeImage:
    def __init__(self, rows):
        self.rows=tuple(sorted(rows))
        self.lookups=[]
        self.index=defaultdict(list)
        for s,p,o in self.rows:
            self.index[(s,p)].append(o)

    def __len__(self):
        return len(self.rows)

    def row_at(self,i):
        return self.rows[i]

    def objects(self,s,p,*,limit=8):
        self.lookups.append((s,p))
        return sorted(self.index[(s,p)])[:limit]


def fixture(n=96):
    rows=[]
    for s in range(1,n+1):
        rows.extend([(s,11,10000+s),
                     (10000+s,12,20000+s),
                     (s,15,20000+s)])
    return rows


class SubjectDisjointTransferTests(unittest.TestCase):
    def test_source_free_positive_and_strong_equal_information_tie(self):
        image=FakeImage(fixture())
        before=image.rows
        result=study.run_dev(image)
        self.assertEqual(result["all_heldout_hits10"],result["symbolic_hits10"])
        self.assertGreaterEqual(result["rule_templates_selected"],1)
        self.assertGreater(result["all_heldout_hits10"],0)
        self.assertGreater(result["heldout_covered_groups"],0)
        self.assertGreater(result["distinct_train_subjects"],0)
        self.assertGreater(result["distinct_heldout_subjects"],0)
        self.assertTrue(result["source_subjects_disjoint"])
        self.assertEqual(result["verified_new_real_world_facts"],0)
        self.assertEqual(result["identified_causal_laws"],0)
        self.assertFalse(result["scientific_pass"])
        self.assertFalse(result["native_accepted"])
        self.assertFalse(result["original_scientific_first_use"])
        self.assertEqual(image.rows,before)
        self.assertEqual(result["all_heldout_hits10"]-result["frequency_hits10"],
                         result["native_win_prior_loss"]-result["prior_win_native_loss"])
        self.assertEqual(study.run_dev(FakeImage(fixture()))["selected_rules_p3_p1_p2_support"],
                         result["selected_rules_p3_p1_p2_support"])

    def test_predictor_never_requests_direct_target_relation(self):
        image=FakeImage(fixture())
        rules=[[15,11,12,31]]
        s=next(x for x in range(1,97) if study._bucket(x)==0)
        original=(s,15,20000+s)
        # Change ONLY a heldout direct target fact, while leaving its
        # witnessed path inputs identical. The prediction must be invariant.
        first=study._native_predict(image,s,15,rules)
        self.assertEqual(first,[20000+s])
        self.assertNotIn((s,15),image.lookups)
        altered=[r for r in image.rows if r!=original]
        altered.append((s,15,30000+s))
        mutant=FakeImage(altered)
        self.assertEqual(study._native_predict(mutant,s,15,rules),first)
        self.assertNotIn((s,15),mutant.lookups)
        self.assertEqual(study._symbolic_predict(mutant,s,15,rules),first)
        self.assertNotIn((s,15),mutant.lookups)

    def test_missing_training_target_witness_abstains(self):
        # Only the source legs exist, no p15 direct training witness.
        rows=[r for r in fixture() if r[1]!=15]
        image=FakeImage(rows)
        result=study.run_dev(image)
        self.assertEqual(result["rule_templates_selected"],0)
        self.assertEqual(result["heldout_covered_groups"],0)
        self.assertEqual(result["all_heldout_hits10"],0)
        self.assertFalse(result["frozen_dev_threshold_pass"])

    def test_duplicate_training_facts_do_not_inflate_rule_support(self):
        rows=fixture()
        s=next(x for x in range(1,97) if study._bucket(x)!=0)
        raw=FakeImage(rows)
        _,_,_=study._mine_training(
            raw,[r for r in raw.rows if study._bucket(r[0])!=0],
            __import__("time").monotonic()+60)
        duplicates=FakeImage(rows+[(s,15,20000+s)]*20)
        # Direct duplicates must not create 20 additional supporting subjects.
        original=study.run_dev(raw)
        repeated=study.run_dev(duplicates)
        self.assertEqual(repeated["selected_rules_p3_p1_p2_support"],
                         original["selected_rules_p3_p1_p2_support"])

    def test_invalid_source_budgets_and_split_determinism(self):
        with self.assertRaisesRegex(ValueError,"NKR11_EMPTY_SOURCE"):
            study.run_dev(FakeImage([]))
        with self.assertRaisesRegex(ValueError,"NKR11_WALL_LIMIT_INVALID"):
            study.run_dev(FakeImage(fixture()),max_seconds=1000)
        self.assertEqual(study._bucket(55),study._bucket(55))
        self.assertEqual(study._anchors(1),(0,))
        many=study._anchors(100000)
        self.assertEqual(len(many),study.MAX_ANCHORS)
        self.assertEqual(many[0],0)
        self.assertEqual(many[-1],99999)
        self.assertEqual(len(set(many)),len(many))

    def test_bad_source_type_and_fake_causal_template_refused(self):
        image=FakeImage(fixture())
        class Bad:
            def __len__(self):
                return len(image)
            def row_at(self,i):
                return (True,15,9) if i==0 else image.row_at(i)
        with self.assertRaisesRegex(ValueError,"NKR11_UNTYPED_SOURCE_TRIPLE"):
            study.run_dev(Bad())
        with self.assertRaisesRegex(AssertionError,"NKR11_TARGET_PASSED_TO_PREDICTOR"):
            study._native_predict(image,1,15,[[15,15,12,7]])
        with self.assertRaisesRegex(AssertionError,"NKR11_CONTROL_TARGET_READ"):
            study._symbolic_predict(image,1,15,[[15,11,15,7]])


if __name__=="__main__":
    unittest.main()
