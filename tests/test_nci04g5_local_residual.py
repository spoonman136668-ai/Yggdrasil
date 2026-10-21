"""NCI-04G5 necessary observation seam, not regeneration evidence."""
import hashlib
import struct
import unittest
from yggdrasil.task_runtime import LocalTaskRuntime
from yggdrasil.nci04g5_local_residual import LocalResidualAdapter, WIRE_BYTES

class NativeLocalResidualContract(unittest.TestCase):
    def test_two_locally_distinguishable_worlds_same_prestate(self):
        runtime=LocalTaskRuntime()
        runtime.lesion([0])
        adapter=LocalResidualAdapter(runtime)
        initial=runtime.snapshot()
        # The surviving sender is cell 7, immediate neighbor of damaged 0.
        # Own prior [self,left,right] and its OWN next-bit, no target truth.
        first=adapter.emit(0,7,(0,0,1),0,1)
        second=adapter.emit(0,7,(0,0,1),1,1)
        self.assertEqual(len(first),38)
        self.assertEqual(len(second),WIRE_BYTES)
        self.assertNotEqual(first,second)
        a=adapter.verify(first,initial)
        b=adapter.verify(second,initial)
        self.assertNotEqual(a["signed_residual_i8"],b["signed_residual_i8"])
        self.assertEqual(a["own_next_bit"],0)
        self.assertEqual(b["own_next_bit"],1)
        self.assertEqual(a["recipient"],0)
        self.assertEqual(a["sender"],7)
        self.assertEqual(runtime.snapshot(),initial,"observer modified native learned state")
        self.assertEqual(LocalTaskRuntime.restore(initial).snapshot(),initial)

    def test_indistinguishable_worlds_must_not_claim_recovery(self):
        runtime=LocalTaskRuntime()
        runtime.lesion([0])
        adapter=LocalResidualAdapter(runtime)
        pre=runtime.snapshot()
        # A changed *damaged-cell* function with identical surviving cell
        # experiences is still information-theoretically invisible here.
        message1=adapter.emit(0,1,(1,0,0),1,7)
        message2=adapter.emit(0,1,(1,0,0),1,7)
        self.assertEqual(message1,message2)
        self.assertEqual(adapter.verify(message1,pre)["evidence_basis"],
            "native-neighbor-own-transition; stream-attestation-unproven")

    def test_no_damaged_target_label_global_sensor_or_nonlocal_delivery(self):
        runtime=LocalTaskRuntime()
        runtime.lesion([0])
        adapter=LocalResidualAdapter(runtime)
        before=runtime.snapshot()
        invalid=[
            lambda:adapter.emit(0,2,(0,0,0),1,1), # not one-hop neighbor
            lambda:adapter.emit(1,0,(0,0,0),1,1), # damaged sender
            lambda:adapter.emit(0,1,[0]*8,1,1),  # would expose global sensors
            lambda:adapter.emit(0,1,(0,0,0),2,1),# invalid own local bit
            lambda:adapter.emit(0,1,(0,0,0),1,65536)]
        for action in invalid:
            with self.assertRaises(ValueError):action()
        self.assertEqual(runtime.snapshot(),before)
        msg=adapter.emit(0,1,(0,0,0),1,1)
        tampered=bytearray(msg);tampered[-1]^=1
        with self.assertRaises(ValueError):adapter.verify(bytes(tampered),before)
        with self.assertRaises(ValueError):adapter.verify(msg,before+" ")
        with self.assertRaises(ValueError):
            adapter.verify(struct.pack("!BBHbB32s",1,255,1,5,1,hashlib.sha256(before.encode()).digest()),before)
        self.assertEqual(runtime.snapshot(),before)

if __name__=="__main__":unittest.main()
