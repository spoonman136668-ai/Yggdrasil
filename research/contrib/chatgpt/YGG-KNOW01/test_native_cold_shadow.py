"""KNOW06: source-free negative controls for archived checkpoint parsing."""
import unittest
from native_cold_shadow import valid_nested, digest, JOINT_SHA, NATIVE_SHA
import json

def canon(d):
    return json.dumps(d,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode("ascii")

def fixture(**kwargs):
    native={"schema":"yggdrasil.ckad.native-cumulative-learner.v5",
            "source_mode":"engineering_fixture_only","accepted_native":False,"scientific_pass":False}
    native.update(kwargs)
    nr=canon(native)
    joint={"schema":"yggdrasil.ckad.native-causal-amalgam.v1",
           "native_ascii":nr.decode("ascii"),"native_parent_sha256":"a"*64,
           "specialist_parent_sha256":"b"*64,
           "action_heads":[{},{}],"temporal_heads":[{},{}]}
    return canon(joint),nr

def altered(raw, **change):
    x=json.loads(raw)
    x.update(change)
    return canon(x)

class Know06Tests(unittest.TestCase):
    def test_fixture_only_contract(self):
        raw,n=fixture()
        self.assertEqual(valid_nested(raw,digest(raw),digest(n)),n)
    def test_archived_hashes_are_not_synthetic(self):
        raw,n=fixture()
        self.assertNotEqual(digest(raw),JOINT_SHA)
        self.assertNotEqual(digest(n),NATIVE_SHA)
    def test_wrong_joint_pin(self):
        raw,n=fixture()
        with self.assertRaisesRegex(ValueError,"JOINT_EXTERNAL_SHA"):
            valid_nested(raw)
    def test_wrong_native_pin(self):
        raw,n=fixture()
        with self.assertRaisesRegex(ValueError,"NATIVE_EXTERNAL_SHA"):
            valid_nested(raw,digest(raw),"0"*64)
    def test_fake_acceptance_blocked(self):
        for key,val in [("accepted_native",True),("scientific_pass",True),
                        ("source_mode","real_world"),("schema","owner")]:
            raw,n=fixture(**{key:val})
            with self.subTest(key=key),self.assertRaisesRegex(ValueError,"NATIVE_RESEARCH_ONLY"):
                valid_nested(raw,digest(raw),digest(n))
    def test_missing_head_blocked(self):
        raw,n=fixture()
        v=altered(raw,action_heads=[])
        with self.assertRaisesRegex(ValueError,"JOINT_CONTRACT"):
            valid_nested(v,digest(v),digest(n))
    def test_unknown_promoted_joint_blocked(self):
        raw,n=fixture()
        v=altered(raw,schema="accepted")
        with self.assertRaisesRegex(ValueError,"JOINT_CONTRACT"):
            valid_nested(v,digest(v),digest(n))
    def test_duplicate_json_field(self):
        v=b'{"schema":1,"schema":2}'
        with self.assertRaisesRegex(ValueError,"DUPLICATE_KEY"):
            valid_nested(v,digest(v),"0"*64)
    def test_extra_fields_blocked(self):
        raw,n=fixture()
        v=altered(raw,causal_claim="approved")
        with self.assertRaisesRegex(ValueError,"JOINT_CONTRACT"):
            valid_nested(v,digest(v),digest(n))
    def test_noncanonical_blocked(self):
        raw,n=fixture()
        v=raw+b" "
        with self.assertRaisesRegex(ValueError,"JOINT_CONTRACT"):
            valid_nested(v,digest(v),digest(n))
    def test_no_training_method(self):
        from native_cold_shadow import FrozenNative
        self.assertFalse(hasattr(FrozenNative,"observe_experience"))
        self.assertFalse(hasattr(FrozenNative,"stage"))
        self.assertFalse(hasattr(FrozenNative,"train"))
if __name__=="__main__":
    unittest.main()
