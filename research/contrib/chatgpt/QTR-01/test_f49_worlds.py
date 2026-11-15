"""F49 frozen world-construction checks; never sample target outcomes."""
import json
import tempfile
from pathlib import Path
from unittest import TestCase, main
from unittest.mock import patch
import f49_worlds as f


class TestF49WorldConstruction(TestCase):
    def test_frozen_blob_and_tamper(self):
        p=f.freeze()
        self.assertEqual(p["schema"],f.SCHEMA)
        self.assertEqual(p["task"]["source_bank_sizes_high_first"],[1024,512,256])
        self.assertEqual(p["task"]["development_seeds"],[163,167,173])
        self.assertEqual(p["prereg_metrics"]["requirements"]["b16_gain_over_best_single_control_min"],.05)
        self.assertTrue(all(p["safety"].values()))
        modified=json.loads(f.PREREG.read_text())
        modified["prereg_metrics"]["requirements"]["b16_gain_over_best_single_control_min"]=0
        with tempfile.TemporaryDirectory() as td:
            bad=Path(td)/"tampered.json"
            bad.write_text(json.dumps(modified),encoding="utf-8")
            with self.assertRaisesRegex(f.F49Rejected,"FROZEN_PREREG_BLOB_CHANGED"):
                f.freeze(bad)

    def test_source_banks_unique_exhaustive_and_scalar_parity(self):
        for size in f.BANK_SIZES:
            bank=f.source_bank(size)
            self.assertEqual(len(bank),size)
            self.assertEqual(len({f.signature(ast) for ast in bank}),size)
            self.assertLessEqual(max(map(f.ast_depth,bank)),2)
            for ast in bank[::max(1,size//16)]:
                truth=f.truth_bits(ast)
                for a in (0,1,4,73,128,255):
                    for prev in (0,17,252):
                        for ctx in range(4):
                            idx=a | (prev<<8) | (ctx<<16)
                            self.assertEqual((truth>>idx)&1,f.evaluate(ast,a,prev,ctx))

    def test_nine_worlds_novel_and_no_target_outcomes(self):
        for size in f.BANK_SIZES:
            for seed in f.SEEDS:
                admission=f.check_target_admission(size,seed)
                self.assertTrue(admission["source_unique_full_domain"])
                self.assertTrue(admission["target_out_of_bank_full_domain"])
                self.assertLessEqual(f.ast_depth(f.target_ast(size,seed)),4)
                row=f.preflight_world(size,seed)
                self.assertEqual(row["status"],"F49_WORLD_ADMISSION_ONLY_NO_TARGET_OBSERVATIONS")
                self.assertEqual(row["source_training_trajectories"],size*64)
                self.assertEqual(row["public_candidate_trajectories"],256)
                self.assertEqual(row["sealed_evaluator_trajectories"],256)
                self.assertNotIn("target_ast",row)
                self.assertNotIn("target_function_digest_evaluator_only",row)
                self.assertIs(row["scientific_pass"],False)
                self.assertIs(row["accepted_weights_modified"],False)

    def test_training_public_eval_disjoint_and_deterministic(self):
        for size in f.BANK_SIZES:
            rows=f.training_inputs(size)
            train={x for row in rows for x in row}
            self.assertEqual(len(train),size*64)
            for seed in f.SEEDS:
                public,evaluation=f._trajectories_for_world(size,seed)
                self.assertEqual(public,f.public_query_pool(size,seed))
                self.assertEqual(len(set(public)),256)
                self.assertEqual(len(set(evaluation)),256)
                self.assertFalse(train.intersection(public))
                self.assertFalse(train.intersection(evaluation))
                self.assertFalse(set(public).intersection(evaluation))
                self.assertTrue(all(x[0] and x[1] and x[0]!=x[1] and 0<=x[2]<4
                                    for x in (*public,*evaluation)))

    def test_source_training_no_hidden_target_data(self):
        for index in (0,13,127,255):
            row=f.source_training_row(256,index)
            self.assertEqual(row,f.source_training_row(256,index))
            self.assertEqual(len(row),64)
            self.assertTrue(all(y0 in (0,1) and y1 in (0,1) for _,(y0,y1) in row))
        ast=("and",f.leaf(8),f.leaf(0))
        self.assertEqual(f.evaluate(ast,1,0,0),0)
        self.assertEqual(f.evaluate(ast,1,1,0),1)

    def test_protected_and_malformed_rejected(self):
        for size,seed in ((1024,179),(256,181),(512,172),(1024,True),
                          (128,163),(True,163)):
            with self.assertRaises(f.F49Rejected):
                f.target_ast(size,seed)
        for seed in (179,181,True,-1):
            with self.assertRaises(f.F49Rejected): f.public_query_pool(256,seed)
        for bad in ((True,0,0),(256,0,0),(0,-1,0),(1,0,4),(1,1,False)):
            with self.assertRaises(f.F49Rejected): f.evaluate(f.leaf(0),*bad)
        with self.assertRaises(f.F49Rejected): f.ast_depth(("leaf",18))
        with self.assertRaises(f.F49Rejected): f.source_training_row(256,True)

    def test_novelty_collision_fails_closed(self):
        bank=list(f.source_bank(256))
        bank[0]=f.target_ast(256,167)
        with patch.object(f,"source_bank",return_value=tuple(bank)):
            with self.assertRaisesRegex(f.F49Rejected,"TASK_INVALID_SOURCE_COLLISION"):
                f.check_target_admission(256,167)


if __name__=="__main__":
    main()
