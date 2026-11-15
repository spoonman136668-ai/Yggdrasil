"""F50 source-only checkpoint provenance, tamper and resource-stop guards.

Fixture checkpoint construction is a structural test: it is NOT real
pretraining, target learning, or scientific first-use.
"""
import tempfile
from pathlib import Path
import unittest
import numpy as np
import f50_source_fit as s
import f50_conventional_controls as c
import f50_worlds as world


class TestF50SourceCustody(unittest.TestCase):
    def fixture(self,kind):
        src={"size":1024,"frozen_prereg_blob":world.PREREG_BLOB,
             "fit_laws":819,"validation_laws":205,
             "source_data_sha256":"2"*64}
        training={"kind":kind,"status":"TRAINED_SOURCE_ONLY",
                  "source_training_complete":True,
                  "scientific_pass":False,"test_fixture_only":True}
        if kind=="graph_conditioned_logistic":
            model=np.arange(c.GRAPH_DIM+34+33+1,dtype=np.float64)/1000
        else:
            model=c.create_neural(kind)
        return src,training,model

    def test_frozen_three_arm_order_and_custody_schema(self):
        self.assertEqual(s.KINDS,("graph_conditioned_gru",
                                 "law_conditioned_set_mlp",
                                 "graph_conditioned_logistic"))
        self.assertEqual(s.SCHEMA,"yggdrasil.qtr01.f50.law-conditioned-source-fit.v1")
        self.assertEqual(world.BANK_SIZES,(4096,2048,1024))
        self.assertEqual(s.world.PREREG_BLOB,"4bd3c4e0d3de0e3910094e38c14a0141c97ad380")

    def test_checkpoint_roundtrip_all_three_and_copy_isolation(self):
        with tempfile.TemporaryDirectory() as tmp:
            for kind in s.KINDS:
                with self.subTest(kind=kind):
                    src,train,model=self.fixture(kind)
                    name=Path(tmp)/(kind+".npz")
                    sha,nbytes=s.write_checkpoint(name,kind,1024,model,
                            "a"*40,src,train)
                    self.assertEqual(nbytes,name.stat().st_size)
                    clone,meta=s.load_checkpoint(name,sha,"a"*40,
                            expected_kind=kind,expected_size=1024)
                    self.assertEqual(meta["kind"],kind)
                    self.assertEqual(meta["source_data_sha256"],"2"*64)
                    self.assertFalse(meta["scientific_pass"])
                    for key,weights in s._weight_arrays(kind,model).items():
                        np.testing.assert_array_equal(
                            weights,s._weight_arrays(kind,clone)[key])
                    with self.assertRaises(s.SourceFitRejected):
                        s.write_checkpoint(name,kind,1024,model,"a"*40,src,train)
                    data=name.read_bytes()
                    name.write_bytes(data[:-1]+bytes([data[-1]^1]))
                    with self.assertRaisesRegex(s.SourceFitRejected,"TAMPER"):
                        s.load_checkpoint(name,sha,"a"*40,
                            expected_kind=kind,expected_size=1024)

    def test_wrong_source_identity_and_kind_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            kind="graph_conditioned_logistic"
            src,train,model=self.fixture(kind)
            path=Path(tmp)/"logistic.npz"
            digest,_=s.write_checkpoint(path,kind,1024,model,
                    "a"*40,src,train)
            with self.assertRaises(s.SourceFitRejected):
                s.load_checkpoint(path,digest,"b"*40,expected_kind=kind,
                                  expected_size=1024)
            with self.assertRaises(s.SourceFitRejected):
                s.load_checkpoint(path,digest,"a"*40,
                                  expected_kind="law_conditioned_set_mlp",
                                  expected_size=1024)
            with self.assertRaises(s.SourceFitRejected):
                s.load_checkpoint(path,"0"*64,"a"*40,
                                  expected_kind=kind,expected_size=1024)

    def test_untrained_partial_or_wrong_frozen_meta_rejected(self):
        src,train,model=self.fixture("graph_conditioned_logistic")
        train["status"]="RESOURCE_STOP"
        with self.assertRaisesRegex(s.SourceFitRejected,"UNQUALIFIED"):
            s._source_meta("graph_conditioned_logistic",1024,
                           "a"*40,src,train)
        train["status"]="TRAINED_SOURCE_ONLY"
        src["frozen_prereg_blob"]="0"*40
        with self.assertRaises(s.SourceFitRejected):
            s._source_meta("graph_conditioned_logistic",1024,
                           "a"*40,src,train)

    def test_never_open_new_target_or_reserved_seed_in_checkpoint_code(self):
        for name in ("target_ast","target_law","evaluation_truth",
                     "sealed_heldout_inputs_for_evaluator_only"):
            self.assertNotIn(name,s.__dict__)
        with self.assertRaises(world.F50Rejected):
            world._check_dev_seed(4127)
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(world.F50Rejected):
                s.run(128,td,"a"*40)


if __name__=="__main__":
    unittest.main()
