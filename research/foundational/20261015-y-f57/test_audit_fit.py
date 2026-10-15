"""Y-F57 independent decoder negative controls, no science first use."""
import importlib.util
import pathlib
import sys
import unittest
HERE=pathlib.Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location("y57a",HERE/"audit_fit.py")
a=importlib.util.module_from_spec(s)
sys.modules[s.name]=a
s.loader.exec_module(a)

class SourceFreeReceipt(unittest.TestCase):
    def test_directional_public_witness(self):
        public=[[100,0,200,0],[200,1,300,1]]
        self.assertTrue(a.witnessed((100,300,(0,2)),public))
        self.assertTrue(a.witnessed((300,100,(3,1)),public))
        self.assertFalse(a.witnessed((100,300,(0,4)),public))
        self.assertFalse(a.witnessed((100,300,(1,2)),public))
    def test_decoding_rejects_malformed_len(self):
        with self.assertRaises(AssertionError):a.decode("00"*11+"05")
    def test_answers_use_only_retained_codes(self):
        mem=[(100,200,(0,)),(200,300,(2,))]
        q={"start":100,"ops":[[0,1],[1,1]],"answer":300}
        self.assertEqual(a.answer(mem,q),1)
        self.assertEqual(a.answer(mem,dict(q,answer=200)),0)
        self.assertEqual(a.answer([],q),0)

if __name__=="__main__":unittest.main()
