"""Fabricated data only; verifies UJ03A interface, accounting and negatives."""
import json
import time
import unittest

import torch
from uj03a_pilot import digest, select, pairs_for, run_arm, ARMS, group


def fixture():
    raw = b'\n'.join(json.dumps(dict(question='problem '+chr(97+i)+' asks 3+4',
        options=['A)1','B)2','C)3','D)4','E)5'],correct='ABCDE'[i%5])).encode()
        for i in range(8))
    return raw


class PilotTests(unittest.TestCase):
    def setUp(self):
        self.threads=torch.get_num_threads()
        self.det=torch.are_deterministic_algorithms_enabled()
        self.warn=torch.is_deterministic_algorithms_warn_only_enabled()
        torch.set_num_threads(1)
        torch.use_deterministic_algorithms(True)

    def tearDown(self):
        torch.set_num_threads(self.threads)
        torch.use_deterministic_algorithms(self.det,warn_only=self.warn)

    def test_selection_digest_and_grouping(self):
        raw=fixture()
        tr,di,m=select(raw,digest(raw),4,2)
        self.assertEqual((tr,di,m),select(raw,digest(raw),4,2))
        self.assertEqual(group('Case 12 + 5'),group('case 99 + 7'))
        self.assertFalse(set(group(r[2].decode()) for r in tr)&set(group(r[2].decode()) for r in di))
        with self.assertRaises(ValueError):
            select(raw,'0'*64,4,2)
        with self.assertRaises(ValueError):
            select(raw,digest(raw),8,2)

    def test_matched_training_and_controls(self):
        raw=fixture()
        tr,di,_=select(raw,digest(raw),4,2)
        for arm in ARMS:
            with self.subTest(arm=arm):
                result=run_arm(arm,1701,tr,di,time.monotonic()+30,epochs=1,batch=2)
                self.assertEqual(result['accounting']['steps'],2)
                self.assertEqual(result['accounting']['exposure_bytes'],
                                 sum(len(c)+len(y) for c,y in pairs_for(tr,'mixture')))
                self.assertEqual(result['after']['n'],2)
                self.assertTrue(0<=result['after']['accuracy']<=1)
        self.assertNotEqual(pairs_for(tr,'mixture'),pairs_for(tr,'shuffled'))
