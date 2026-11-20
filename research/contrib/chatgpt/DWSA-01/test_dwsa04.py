"""Frozen DWSA04 source-only DEV qualification on archived engineering fixture."""
import hashlib, os, struct, unittest
from pathlib import Path
from dwsa02 import read_archive, gauge
from dwsa03 import fixture_records, encode
from dwsa04 import compile_student, restore_student, predict_student, evaluate

class DWSA04Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path=os.environ.get('DWSA02_ARCHIVE_ZIP')
        if not path:raise unittest.SkipTest('Pinned engineering fixture ZIP required')
        cls.path=Path(path)
        cls.state,cls.heads=read_archive(cls.path)
        cls.episodes=fixture_records(cls.state)
        cls.raw=compile_student(cls.heads)

    def test_source_is_engineering_fixture_only(self):
        import json
        native=json.loads(self.state['native_ascii'])
        self.assertEqual(native['source_mode'],'engineering_fixture_only')
        self.assertFalse(native['accepted_native'])
        self.assertEqual(len(self.episodes),1025)

    def test_320_bytes_deterministic(self):
        self.assertEqual(len(self.raw),320)
        self.assertEqual(self.raw,compile_student(self.heads))
        self.assertEqual(self.raw[288:],hashlib.sha256(self.raw[:288]).digest())

    def test_three_cold_restores(self):
        self.assertEqual(len(restore_student(self.raw)),4)
        for _ in range(3):self.assertEqual(restore_student(bytes(self.raw)),restore_student(self.raw))

    def test_corrupt_checksum_and_header_rejected(self):
        for index in (0,7,60,287,319):
            altered=bytearray(self.raw);altered[index]^=1
            with self.assertRaises(ValueError):restore_student(bytes(altered))

    def test_invalid_four_bit_value_rejected(self):
        altered=bytearray(self.raw)
        altered[216]=(15<<4)|(altered[216]&15)
        altered[288:]=hashlib.sha256(altered[:288]).digest()
        with self.assertRaisesRegex(ValueError,'P_ENCODING'):restore_student(bytes(altered))

    def test_valid_hidden_symmetries(self):
        base=restore_student(self.raw)
        for i in range(4):
            features=[encode(self.episodes[j],self.episodes[max(0,j-8):j],i) for j in range(8)]
            for seed in (101,202,303):
                modified=tuple(gauge(self.heads[k],seed) if k==i else self.heads[k] for k in range(4))
                variant=restore_student(compile_student(modified))[i]
                self.assertLessEqual(max(abs(predict_student(base[i],x)-predict_student(variant,x)) for x in features),1e-10)

    def test_invalid_shapes_rejected(self):
        modified=list(self.heads)
        h={**modified[0], 'encoder':[list(x) for x in modified[0]['encoder']]}
        h['encoder'][0].pop()
        modified[0]=h
        with self.assertRaisesRegex(ValueError,'SOURCE_SHAPE'):compile_student(tuple(modified))

    def test_original_world_first_use_not_claimed_and_no_go(self):
        r=evaluate(self.path)
        self.assertEqual(r['decision'],'DWSA04_DEV_NO_GO')
        self.assertEqual(r['dev_signal_heads_passed'],0)
        self.assertEqual(r['teacher_forward_passes'],0)
        self.assertEqual(r['original_world_actions'],0)
        self.assertEqual(r['scientific'],'UNVERIFIED')
        self.assertFalse(r['independently_heldout'])
        self.assertEqual(r['native_checkpoint_bytes'],320)

if __name__=='__main__':unittest.main()
