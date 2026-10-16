"""Y-F61 source-free validation auditor adversarial preflight; no data generated."""
import importlib.util,json,pathlib,struct,sys,unittest
HERE=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("y61_source_free_independent_audit",
                                            HERE/"audit_fit_validation.py")
a=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=a;spec.loader.exec_module(a)
def encode(start,end,codes):
    bits=0
    for i,code in enumerate(codes):bits|=code<<(3*i)
    return (struct.pack("<II",start,end)+bits.to_bytes(3,"little")+
            bytes([len(codes)])).hex()
class IndependentAuditor(unittest.TestCase):
    def test_frozen_control_identity_without_source(self):
        p=json.loads((HERE/"prereg.json").read_text())
        self.assertEqual(p["frozen_controls"],list(a.ARMS))
        self.assertEqual(a.ARMS[0],"learned_query_value_retention")
        self.assertEqual(a.ARMS[6],"offline_public_noncompetitive")
    def test_lossless_decoder_rejects_tamper(self):
        rec=(10,30,(0,2))
        self.assertEqual(a.unpack(encode(*rec)),rec)
        with self.assertRaises(AssertionError):a.unpack("00"*11)
        raw=bytes.fromhex(encode(*rec))
        with self.assertRaises(AssertionError):a.unpack((raw[:11]+b"\x07").hex())
    def test_independently_reconstruct_public_role_path(self):
        public=[(10,0,20),(20,1,30)]
        rec=a.unpack(encode(10,30,(0,2)))
        a.prove_public_path(rec,public)
        future=dict(start=10,ops=[[0,1],[1,1]],answer=30)
        self.assertEqual(a.solve([rec],future),30)
        with self.assertRaises(AssertionError):
            a.prove_public_path((10,30,(2,0)),public)
        with self.assertRaises(AssertionError):
            a.prove_public_path((10,31,(0,2)),public)
        self.assertIsNone(a.solve([],future))
    def test_false_authority_fails_closed(self):
        p=json.loads((HERE/"prereg.json").read_text())
        with self.assertRaises(AssertionError):
            a.audit(dict(schema="wrong"),p)
if __name__=="__main__":unittest.main()
