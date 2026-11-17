"""Source-safe public schema fences. No permitted effect call is made here."""
from unittest import TestCase
from unittest.mock import patch
from pathlib import Path
import source as S
import exact_weights as W

class PublicCustodyPreflight(TestCase):
    def test_01_scope_and_no_protected_first_use(self):
        self.assertEqual(tuple(map(len,(S.FIT,S.NOVEL,S.KNOWN,S.OFF,S.TRANSFER))),
                         (16,32,8,8,8))
        self.assertEqual(len(S.FIT|S.NOVEL|S.KNOWN|S.OFF),64)
        self.assertFalse(S.ALLOWED&S.PROTECTED)
        with patch.object(S.random,'Random',
                          side_effect=AssertionError('SOURCE_RNG_NOT_ALLOWED')):
            for bad in (True,False,'310000',309999,310016,310800,
                        311032,311800,312008,312800,313008,313800,
                        314008,314800,300000,302000,280000,260000):
                with self.subTest(seed=bad):
                    with self.assertRaises(PermissionError):S.world(bad)
                    with self.assertRaises(PermissionError):S._truth(bad)
                    with self.assertRaises(PermissionError):S.open_original(bad)
    def test_02_public_only_no_owner_effects(self):
        v=S.world(310000)
        self.assertEqual(len(v.records),64)
        self.assertEqual(len(v.legal),64)
        self.assertEqual(set(v.by_x),set(range(64)))
        self.assertFalse(hasattr(v,'truth'))
        with self.assertRaises(PermissionError):
            S.OwnerPostCommit(v,310000,{})
        code=Path(W.__file__).read_text(encoding='utf8')
        self.assertNotIn('import source',code)
        self.assertNotIn('from source import',code)
        self.assertNotIn('_truth(',code)
        self.assertFalse(Path(__file__).with_name('result.json').exists())
        # NEVER make allowed Custodian.query() or _truth() here.
