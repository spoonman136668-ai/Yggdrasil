"""Frozen DWSA-03 source-only regression, no teacher model execution."""
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest

from dwsa02 import DIMS, STATE_SHA, ZIP_SHA, algebraic_route, compile_routes, read_archive, restore
from dwsa03 import (
    EPISODES, PREFIX, encode, evaluate, fixture_records,
    init_head, pack_rows, predict, reference_prevalence,
)


class DWSA03Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = os.environ.get('DWSA02_ARCHIVE_ZIP')
        if not source:
            raise unittest.SkipTest('explicit pre-existing engineering ZIP path required')
        cls.path=Path(source)
        cls.raw,cls.heads=read_archive(cls.path)
        cls.rows=fixture_records(cls.raw)

    def test_archive_identity_and_fixture_only(self):
        self.assertEqual(len(self.rows),EPISODES)
        self.assertEqual(self.raw['schema'],'yggdrasil.ckad.native-causal-amalgam.v1')
        self.assertEqual(json.loads(self.raw['native_ascii'])['source_mode'],'engineering_fixture_only')
        self.assertEqual(tuple(h['steps'] for h in self.heads),(2109,)*4)

    def test_feature_shape_and_proper_chronology(self):
        for k in range(4):
            first=encode(self.rows[0], (),k)
            self.assertEqual(tuple(map(len,first)),(DIMS[k],)*2)
            if k>=2:
                self.assertEqual(first[0][-40:],(0.0,)*40)
            late=encode(self.rows[25],self.rows[17:25],k)
            self.assertEqual(tuple(map(len,late)),(DIMS[k],)*2)
            self.assertEqual(late,encode(self.rows[25],self.rows[17:25],k))

    def test_archived_labels_not_used_in_current_prediction_input(self):
        row=self.rows[10]
        for head in range(4):
            flipped=list(row)
            flipped[3 if head in (0,2) else 5]^=1
            if head in (0,2):
                # transition does not use its s2 label
                self.assertEqual(encode(row,self.rows[2:10],head),
                                 encode(tuple(flipped),self.rows[2:10],head))
            else:
                # reward does not use its y label
                self.assertEqual(encode(row,self.rows[2:10],head),
                                 encode(tuple(flipped),self.rows[2:10],head))

    def test_compiled_fixed_bytes_and_recipient_probabilities(self):
        raw=compile_routes(self.heads)
        self.assertEqual(len(raw),320)
        self.assertEqual(restore(raw),restore(bytes(raw)))
        initial=restore(pack_rows(tuple(algebraic_route(init_head(i)) for i in range(4))))
        self.assertEqual(len(initial),4)
        for head in range(4):
            x=encode(self.rows[1],self.rows[:1],head)
            p=predict(initial[head],x)
            self.assertTrue(0<=p<=1)

    def test_exact_structural_oracle_dominates_quantized(self):
        recovered=restore(compile_routes(self.heads))
        self.assertEqual(tuple(len(v) for v in recovered),(8,12,88,92))
        for index,head in enumerate(self.heads):
            truth=algebraic_route(head)
            max_abs=max(map(abs,truth))
            scale=max_abs/127 or 1.0
            self.assertTrue(all(abs(a-b)<=scale/2+1e-12
                                for a,b in zip(recovered[index],truth)))

    def test_invalid_source_custody_rejected_before_native_read(self):
        data=bytearray(self.path.read_bytes())
        data[20]^=1
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'corrupted.zip'
            path.write_bytes(data)
            with self.assertRaises(ValueError):
                read_archive(path)

    def test_main_frozen_report_classification_and_controls(self):
        report=evaluate(self.path)
        self.assertEqual(report['teacher_forward_passes'],0)
        self.assertEqual(report['new_original_world_actions'],0)
        self.assertFalse(report['independently_heldout'])
        self.assertEqual(report['native_checkpoint_bytes'],320)
        self.assertEqual(report['prefix_fit_count'],PREFIX)
        self.assertEqual(report['late_training_recheck_count'],205)
        self.assertEqual(report['scientific'],'UNVERIFIED')
        for values in report['per_head'].values():
            self.assertEqual(len(values['metrics']),7)
            self.assertEqual(values['labels_in_late_training_recheck'],205)


if __name__=='__main__':
    unittest.main()
