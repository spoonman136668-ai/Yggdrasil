import hashlib
import json
import unittest
from synaptic_bank import SynapticBank, PlasticNand, context, WIDTH


class WSP17Tests(unittest.TestCase):
    def graph(self, bit):
        m=PlasticNand();m.rows[-1]=[int(i==bit) for i in range(9)]
        return m.rows

    def test_numeric_first_free_and_known_key_replace(self):
        b=SynapticBank()
        self.assertEqual(b.write(context(5),self.graph(0)),1)
        self.assertEqual(b.write(context(2),self.graph(1)),1)
        self.assertEqual(b.occupied,[1,1,0,0])
        before=b.synapses[1][:]
        self.assertEqual(b.write(context(5),self.graph(2)),1)
        self.assertEqual(b.synapses[1],before)
        self.assertEqual(b.occupied,[1,1,0,0])

    def test_all_context_execution_routes_independently(self):
        b=SynapticBank()
        for k in range(4):b.write(context(k),self.graph(k%3))
        for k in range(4):
            for i in range(8):self.assertEqual(b.predict(context(k),context(i)),context(i)[k%3])

    def test_unknown_and_erased_are_abstentions(self):
        b=SynapticBank()
        for i in range(8):self.assertIsNone(b.predict(context(0),context(i)))
        b.write(context(0),self.graph(0))
        self.assertIsNone(b.predict(context(7),context(0)))

    def test_full_capacity_rejects_without_any_state_change(self):
        b=SynapticBank()
        for k in range(4):b.write(context(k),self.graph(k%3))
        raw=b.snapshot()
        self.assertEqual(b.write(context(4),self.graph(1)),0)
        self.assertEqual(b.snapshot(),raw)
        self.assertEqual(b.write(context(1),self.graph(2)),1)

    def test_cold_bytes_and_synaptic_identity(self):
        b=SynapticBank();b.write(context(3),self.graph(2))
        c=SynapticBank.restore(b.snapshot())
        self.assertEqual(b.snapshot(),c.snapshot())
        self.assertEqual(c.read(context(3)),(1,self.graph(2)))
        self.assertEqual(4*(WIDTH+4),316)

    def test_corrupt_truncated_oversized_rejected(self):
        raw=SynapticBank().snapshot()
        for bad in (raw[:-1],raw+b'x',raw[:-1]+bytes([raw[-1]^1]),b'x'*5000):
            with self.assertRaises(ValueError):SynapticBank.restore(bad)

    def test_forged_digest_cannot_authorize_duplicate_keys(self):
        b=SynapticBank()
        b.write(context(0),self.graph(0));b.write(context(1),self.graph(1))
        d=json.loads(b.snapshot()[9:-32]);d['keys'][1]=d['keys'][0]
        body=json.dumps(d,sort_keys=True,separators=(',',':')).encode()
        p=b'WSP17'+len(body).to_bytes(4,'big')+body
        with self.assertRaises(ValueError):SynapticBank.restore(p+hashlib.sha256(p).digest())

    def test_inactive_nonzero_and_boolean_synapses_fail_closed(self):
        b=SynapticBank();b.keys[0][0]=1
        with self.assertRaises(ValueError):b.snapshot()
        b=SynapticBank();b.occupied[0]=True
        with self.assertRaises(ValueError):b.snapshot()
        b=SynapticBank();b.synapses[0][0]=True
        with self.assertRaises(ValueError):b.predict(context(0),context(0))

    def test_payload_and_key_validation_before_mutation(self):
        b=SynapticBank();raw=b.snapshot()
        for key,rows in (([0,0,0],self.graph(0)),(context(0),[[1]])):
            with self.assertRaises(ValueError):b.write(key,rows)
        self.assertEqual(raw,b.snapshot())

    def test_bank_and_payload_are_isolated(self):
        rows=self.graph(0);a=SynapticBank();b=SynapticBank()
        a.write(context(0),rows);raw=a.snapshot();rows[-1][0]=0
        self.assertEqual(a.snapshot(),raw)
        self.assertEqual(b.snapshot(),SynapticBank().snapshot())


if __name__=='__main__':unittest.main()
