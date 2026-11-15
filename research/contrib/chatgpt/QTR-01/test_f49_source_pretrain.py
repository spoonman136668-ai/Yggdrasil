"""F49 source-only training reproducibility, receipt, and storage negative tests."""
from hashlib import sha256
import tempfile
import unittest
from pathlib import Path
import numpy as np
import f49_source_pretrain as p
import f49_conventional_controls as c


class SourceOnlyTests(unittest.TestCase):
    def test_full_source_pins_and_accounting(self):
        self.assertEqual(p.BANK_SIZES, (1024,512,256))
        self.assertEqual(p.KINDS, ("conventional_mlp","conventional_logistic"))
        self.assertEqual(p.FROZEN_BLOB, "839309211feef018d1c308091716bc6e0d4e7a70")
        self.assertNotIn("target_ast",p.__dict__)
        self.assertNotIn("target_law",p.__dict__)
        self.assertNotIn("SEEDS",p.__dict__)

    def test_canonical_dataset_sha_and_malformed(self):
        x = np.zeros((10,18), dtype=np.float64)
        y = np.zeros(10, dtype=np.float64)
        a=p.source_dataset_digest(x,y)
        self.assertEqual(a,p.source_dataset_digest(x.copy(),y.copy()))
        y[5]=1
        self.assertNotEqual(a,p.source_dataset_digest(x,y))
        with self.assertRaises(c.ControlRejected):
            p.source_dataset_digest(x[:3],y)

    def test_cold_checkpoint_roundtrip_and_unchanged_source(self):
        with tempfile.TemporaryDirectory() as td:
            source="a"*40
            source_hash="b"*64
            for kind in p.KINDS:
                model = c.MLP(seed=11) if kind=="conventional_mlp" else c.Logistic()
                model.steps=3
                if kind=="conventional_mlp":
                    model.m[0][0,0]=0.123
                    model.v[2][1,1]=0.456
                else:
                    model.w[0]=0.123
                path=Path(td)/(kind+".npz")
                digest,nbytes,recovered = p.write_checkpoint(
                    path,kind,256,model,{"dummy_fit":True},source_hash,source,0.5)
                self.assertEqual(nbytes,len(path.read_bytes()))
                self.assertEqual(digest,sha256(path.read_bytes()).hexdigest())
                self.assertEqual(recovered.source_observations,256*128)
                self.assertEqual(recovered.model.steps,3)
                before=[z.copy() for z in p._model_arrays(kind,model).values()]
                clone=recovered.clone_model()
                self.assertIsNot(clone,model)
                for lhs,rhs in zip(before,p._model_arrays(kind,recovered.model).values()):
                    self.assertTrue(np.array_equal(lhs,rhs))
                with self.assertRaisesRegex(c.ControlRejected,"REFUSE_OVERWRITE"):
                    p.write_checkpoint(path,kind,256,model,{},source_hash,source,0.5)
                data=path.read_bytes()
                path.write_bytes(data[:-1]+bytes([data[-1]^1]))
                with self.assertRaisesRegex(c.ControlRejected,"HASH_MISMATCH"):
                    p.load_checkpoint(path,digest,source)

    def test_source_sha_and_inventory_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            model=c.Logistic()
            path=Path(td)/"model.npz"
            with self.assertRaises(c.ControlRejected):
                p.write_checkpoint(path,"conventional_logistic",256,model,{},
                                   "b"*64,"not-a-commit",1.0)
            self.assertFalse(path.exists())
            digest,_,_=p.write_checkpoint(path,"conventional_logistic",256,model,{},
                                           "b"*64,"a"*40,1.0)
            with self.assertRaises(c.ControlRejected):
                p.load_checkpoint(path,digest,"f"*40)
            with self.assertRaises(c.ControlRejected):
                p.load_checkpoint(path,"0"*64,"a"*40)

    def test_source_only_entry_does_not_allow_unregistered_banks(self):
        with tempfile.TemporaryDirectory() as td:
            for bad in (128,True,179):
                with self.assertRaises(c.ControlRejected):
                    p.train_bank(bad,td,"a"*40)


if __name__=="__main__":
    unittest.main()
