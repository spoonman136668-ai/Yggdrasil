"""WSP157 authentic ALREADY CONSUMED public DTR FIT read-only safety tests."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

from yggdrasil.public_causal_cells import PublicCausalCells

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"research"/"contrib"/"chatgpt"/"WSP-157"/"audit.py"
spec=importlib.util.spec_from_file_location("_wsp157_historical_public_dtr",SCRIPT)
A=importlib.util.module_from_spec(spec)
spec.loader.exec_module(A)

class OriginalDTRRetrospectiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=A.read_original_fit()

    def test_01_original_public_bytes_reconstructed_source_receipts(self):
        self.assertEqual([len(x) for x in self.source],[256]*3)
        self.assertEqual(sum(len(x) for x in self.source),768)
        self.assertEqual(self.source[0][0]["seed"],1100000)
        self.assertEqual(self.source[2][255]["seed"],1120255)
        self.assertEqual(A.ORIGINAL_CANON_SHA,
                         "016bf254ade33b936386abf7829ff90d765da71105e2beebcb130c95febe7d1d")
        self.assertEqual(len(A.read_original_fit()),3)

    def test_02_corrupted_original_public_hash_refused_before_training(self):
        content=json.loads(A.DATA.read_text())
        prefix=content["packed_hex"]
        content["packed_hex"]=("00" if prefix[:2]!="00" else "01")+prefix[2:]
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"corrupted.json"
            p.write_text(json.dumps(content,indent=2,sort_keys=True)+"\n")
            with self.assertRaisesRegex(ValueError,"WSP157_PACKED_SOURCE_BYTES"):
                A.read_original_fit(p)
        self.assertEqual(A.read_original_fit(),self.source)

    def test_03_source_relabel_or_source_identity_failure(self):
        c=json.loads(A.DATA.read_text())
        for field,new in (("original_upstream","some-other-model"),
                          ("original_canonical_trace_sha256","0"*64),
                          ("new_original_actions",1),
                          ("protected_val_dev_contents_included",True),
                          ("fit_per_replica",257)):
            wrong=dict(c)
            wrong[field]=new
            with tempfile.TemporaryDirectory() as d:
                p=Path(d)/"bad.json"
                p.write_text(json.dumps(wrong,indent=2,sort_keys=True)+"\n")
                with self.subTest(field=field):
                    with self.assertRaises(ValueError):A.read_original_fit(p)

    def test_04_original_two_stage_mapping_and_no_terminal_state_invention(self):
        for source in self.source:
            for r in source:
                self.assertIn(r["s1"],(0,1))
                self.assertIn(r["x1"],(0,1))
                self.assertIn(r["s2"],(0,1))
                self.assertIn(r["x2"],(0,1))
                self.assertIn(r["y"],(0,1))
                a=(A.stage_slot(r),r["x1"],r["s2"])
                b=(A.reward_slot(r),r["x2"],r["y"])
                self.assertTrue(0<=a[0]<2)
                self.assertTrue(2<=b[0]<=9)
                self.assertTrue(all(type(v) is int and v in (0,1)
                                    for v in (a[1],a[2],b[1],b[2])))
        self.assertEqual(A.addr(9),(2,True))
        self.assertEqual(A.addr(6),(6,False))
        self.assertNotIn("after",A.features(self.source[0][0],"reward"))

    def test_05_native_actual_train_state_cold_versus_independent_batch(self):
        for source in self.source:
            for exposure in (32,64,128,192):
                train=source[:exposure]
                model=A.fit_native(train)
                c=A.independent_fits(train)
                self.assertEqual(len(model.snapshot()),164)
                self.assertEqual(PublicCausalCells.restore(model.snapshot()).snapshot(),
                                 model.snapshot())
                for held in source[192:256]:
                    for target in ("transition","reward"):
                        self.assertEqual(A.native_prob(model,held,target),
                                         A.beta(c,held,target))
                self.assertTrue(all(0<=v<=1 for v in
                    (A.mle(c,source[225],"reward"),
                     A.mle(c,source[225],"transition"))))

    def test_06_train_hold_separation_unchanged_by_only_held_labels(self):
        for source in self.source:
            before=A.fit_native(source[:128]).snapshot()
            changed=[dict(r) for r in source]
            for i in range(192,256):
                changed[i]["y"]^=1
                changed[i]["s2"]^=1
            after=A.fit_native(changed[:128]).snapshot()
            self.assertEqual(before,after)
            self.assertNotEqual(changed[192],source[192])

    def test_07_incremental_native_checkpoint_exact_retrain_parity(self):
        for source in self.source:
            native=A.fit_native(source[:32])
            for start,end in ((32,64),(64,128),(128,192)):
                for r in source[start:end]:
                    for target in ("transition","reward"):
                        slot,action,outcome=A.observation(r,target)
                        adr,ret=A.addr(slot)
                        native.observe(adr,action,outcome,retained=ret)
                fresh=A.fit_native(source[:end])
                self.assertEqual(native.snapshot(),fresh.snapshot())

    def test_08_independent_matched_controls_nonoracle(self):
        for target in ("transition","reward"):
            for source in self.source:
                train=source[:32]
                w,meta=A.logistic_fit(train,target)
                self.assertEqual(meta["fit_observations"],32)
                self.assertTrue(0<meta["iterations"]<=A.LOGISTIC_ITERS)
                self.assertIn("converged",meta)
                for held in source[192:196]:
                    self.assertTrue(0<A.logistic_prob(w,held,target)<1)
        # The source code has no environment imported or generated actions.
        script=SCRIPT.read_text()
        for banned in ("import causal_gym","from causal_gym","env.reset(",
                       "env.do(","run_original_source(","ctf_do(","get_graph"):
            self.assertNotIn(banned,script)

    def test_09_validation_denials_do_not_consume_original_source(self):
        c=json.loads(A.DATA.read_text())
        for field,bad in (("source_seed_rule","different rule"),
                          ("original_fit_json_sha256","f"*64)):
            x=copy.deepcopy(c)
            x[field]=bad
            # No real source I/O possible: neither import nor reset/do occurs.
            with tempfile.TemporaryDirectory() as d:
                p=Path(d)/"source.json"
                p.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n")
                with self.subTest(field=field):
                    with self.assertRaises(ValueError):A.read_original_fit(p)

if __name__=="__main__":
    unittest.main()
