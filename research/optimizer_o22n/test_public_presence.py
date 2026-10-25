"""O22-N public unknown/not-observed admission certificate; zero source episodes."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

from research.native.itd02.r1.native_policy import PublicGrid, features
from research.optimizer_o22n.public_presence import (
    FrontFrame, PolicyPresenceLedger, mask_at_source_return
)


def state(blocked,ordinal=1):
    return FrontFrame.from_public(
        PublicGrid(x=2,y=3,goal_x=6,goal_y=6,direction=1,
                   front_blocked=blocked),ordinal)


class O22NSourceContract(unittest.TestCase):
    def test_original_native_source_immutable_type_boundary(self):
        root=Path(__file__).resolve().parents[2]
        for p,sha in {
          "research/native/itd02/r1/native_policy.py":
             "3aa22b1e418a7f8cd9619c476f02b8c614917b16",
          "research/native/itd02/r3/navigator.py":
             "5348238f4ec2183bea29262659883391b5f429fd",
        }.items():
            raw=(root/p).read_bytes().replace(b"\r\n",b"\n")
            self.assertEqual(
                hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest(),
                sha)
        with self.assertRaises(ValueError):
            features(PublicGrid(2,3,6,6,1,None))

    def test_witnessed_false_is_not_unknown_and_no_boolean_fallback(self):
        clear=state(False)
        blocked=state(True)
        self.assertTrue(clear.observed)
        self.assertFalse(clear.front_blocked)
        self.assertTrue(blocked.front_blocked)
        masked=clear.withhold()
        self.assertIsNone(masked.front_blocked)
        self.assertFalse(masked.observed)
        self.assertEqual(clear.require_r1_boolean().front_blocked,False)
        self.assertEqual(blocked.require_r1_boolean().front_blocked,True)
        with self.assertRaisesRegex(ValueError,"UNKNOWN"):
            masked.require_r1_boolean()
        self.assertNotEqual(clear.public_wire(),masked.public_wire())
        print("O22N_UNKNOWN_IS_NOT_PUBLIC_CLEAR=PASS")

    def test_blinding_does_not_leak_observed_true_or_false(self):
        blocked=mask_at_source_return(state(True),1,0)
        clear=mask_at_source_return(state(False),1,0)
        self.assertEqual(blocked,clear)
        self.assertIsNone(blocked.front_blocked)
        self.assertEqual(blocked.ordinal,1)
        self.assertEqual((blocked.x,blocked.y,blocked.direction),(2,3,1))
        with self.assertRaisesRegex(ValueError,"UNKNOWN"):
            blocked.require_r1_boolean()
        self.assertNotEqual(state(True),blocked)
        print("O22N_SAME_PHYSICAL_PUBLIC_POSE_BLINDING=PASS")

    def test_source_return_grammar_and_boolean_coercion_rejected(self):
        a=state(True,1)
        for invalid in ((a,3,0),(a,True,0),(a,1,1),(a,1,2)):
            with self.assertRaises(ValueError):
                mask_at_source_return(*invalid)
        with self.assertRaises(ValueError):
            mask_at_source_return(a.withhold(),1,0)
        for fake in (
            FrontFrame(2,3,6,6,1,1,False,False),
            FrontFrame(2,3,6,6,1,1,True,None),
            FrontFrame(2,3,6,6,1,1,True,0)
        ):
            with self.assertRaises(ValueError):fake.validate()
        with self.assertRaises(ValueError):
            FrontFrame.from_wire({"x":2,"hidden_source_grid":42})
        print("O22N_FAKE_CLEAR_ABSENT_SOURCE_REJECTED=PASS")

    def test_policy_memory_remembers_only_exposed_source_front(self):
        native=PolicyPresenceLedger()
        conventional=PolicyPresenceLedger()
        mask=mask_at_source_return(state(True),0,0)
        for arm in (native,conventional):
            arm.ingest(mask)
            self.assertEqual(arm.front_status((2,3,1)),"UNKNOWN")
        self.assertEqual(native.checkpoint(),conventional.checkpoint())
        with self.assertRaisesRegex(ValueError,"REPLAY"):
            native.ingest(mask)
        native.ingest(state(False,2))
        self.assertEqual(native.front_status((2,3,1)),"CLEAR")
        self.assertEqual(conventional.front_status((2,3,1)),"UNKNOWN")
        # A current front clearing is a DIFFERENT later witnessed ordinal.
        print("O22N_EQUAL_NATIVE_CONVENTIONAL_PRESENCE_RIGHTS=PASS")

    def test_true_fresh_python_cold_presence_and_tamper(self):
        memory=PolicyPresenceLedger()
        memory.ingest(state(True,1).withhold())
        cp=memory.checkpoint()
        self.assertEqual(PolicyPresenceLedger.restore(cp).checkpoint(),cp)
        code=(
            "import json,sys;"
            "from research.optimizer_o22n.public_presence import PolicyPresenceLedger;"
            "m=PolicyPresenceLedger.restore(sys.stdin.buffer.read());"
            "f=m.views[-1];"
            "print(json.dumps({'status':m.front_status((2,3,1)),"
            "'present':f.observed,'blocked':f.front_blocked,'ordinal':f.ordinal}))"
        )
        p=subprocess.run([sys.executable,"-B","-c",code],input=cp,
                          capture_output=True,timeout=20)
        self.assertEqual(p.returncode,0,p.stderr.decode())
        self.assertEqual(json.loads(p.stdout),{
            "status":"UNKNOWN","present":False,"blocked":None,"ordinal":1
        })
        bad=json.loads(cp)
        bad["data"]["views"][0]["front_blocked"]=False
        with self.assertRaises(ValueError):
            PolicyPresenceLedger.restore(json.dumps(bad).encode())
        print("O22N_FRESH_PROCESS_UNKNOWN_STATUS_RETENTION=PASS")


if __name__=="__main__":
    unittest.main(verbosity=2)
