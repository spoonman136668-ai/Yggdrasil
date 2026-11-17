import json
import subprocess
import sys
import unittest
from yggdrasil.native_context_basis import canonical,digest
from yggdrasil.native_context_accumulator import NativeContextAccumulator
from yggdrasil.native_context_quarantine import NativeContextQuarantine
from yggdrasil.native_context_repair import repair_quarantined_basis


def packet(rows):
    return {'records':rows,'sha256':digest(canonical(rows))}


class NativeContextRepairTests(unittest.TestCase):
    def initial(self):
        rows=[[0,0,0],[1,0,0],[2,0,0]]
        n=NativeContextAccumulator(2).stage_update(0,rows,digest(canonical(rows)),max_degree=1)
        g=NativeContextQuarantine(n)
        bad=packet([[3,0,1]])
        g=g.stage_checked_update(0,bad['records'],bad['sha256'],max_degree=1)
        return g,bad

    def repair(self,g,batches,**kwargs):
        raw=g.checkpoint()
        return repair_quarantined_basis(raw,digest(raw),0,batches,max_degree=3,**kwargs)

    def test_rebuilds_only_witnesses_and_learns_rejected_effect(self):
        g,bad=self.initial();frozen=g.checkpoint()
        new,receipt=self.repair(g,[bad])
        self.assertEqual([new.predict(0,x,0) for x in range(4)],[0,0,0,1])
        self.assertIsNone(new.predict(0,3,1))
        self.assertEqual(receipt['retained_observed_inputs'],3)
        self.assertEqual(receipt['old_raw_rows_received'],0)
        self.assertEqual(g.checkpoint(),frozen)

    def test_other_active_and_retained_profiles_byte_exact(self):
        g,bad=self.initial()
        for a,r in [(1,False),(0,True)]:
            p=packet([[0,0,1]])
            g=g.stage_checked_update(a,p['records'],p['sha256'],max_degree=1,retained=r)
        new,_=self.repair(g,[bad])
        for slot in range(1,16):
            self.assertEqual(new._native._model._profiles[slot],g._native._model._profiles[slot])
            self.assertEqual(new._native._batches[slot],g._native._batches[slot])
            self.assertEqual(new._native._seen[slot],g._native._seen[slot])

    def test_rejected_packet_must_be_present_and_hash_matched(self):
        g,bad=self.initial()
        with self.assertRaisesRegex(ValueError,'MISSING_REJECTED'):
            self.repair(g,[packet([[0,1,0]])])
        wrong={'records':[[3,0,0]],'sha256':bad['sha256']}
        with self.assertRaisesRegex(ValueError,'SOURCE_PIN'):self.repair(g,[wrong])

    def test_later_conflict_does_not_clear_original_quarantine(self):
        g,bad=self.initial();raw=g.checkpoint()
        with self.assertRaises(ValueError):self.repair(g,[bad,packet([[3,0,0]])])
        self.assertEqual(g.checkpoint(),raw);self.assertTrue(g._failures[0])

    def test_original_source_mode_and_historical_labels_refused(self):
        g,bad=self.initial()
        for kwargs in ({'source_mode':'original'},{'source_kind':'historical_fact'}):
            with self.assertRaises(ValueError):self.repair(g,[bad],**kwargs)

    def test_expansion_requires_quarantine_and_strictly_larger_degree(self):
        g,bad=self.initial();raw=g.checkpoint()
        for degree in (0,1,4,True):
            with self.assertRaises(ValueError):
                repair_quarantined_basis(raw,digest(raw),0,[bad],max_degree=degree)
        fixed,_=self.repair(g,[bad])
        with self.assertRaisesRegex(ValueError,'REQUIRES_QUARANTINE'):self.repair(fixed,[bad])

    def test_cold_repair_receives_no_old_rows(self):
        g,bad=self.initial();raw=g.checkpoint()
        script='''import json,sys
from yggdrasil.native_context_repair import repair_quarantined_basis
from yggdrasil.native_context_basis import digest
p=json.load(sys.stdin);raw=p['checkpoint'].encode('ascii')
m,r=repair_quarantined_basis(raw,digest(raw),0,p['new_batches'],max_degree=3)
print(json.dumps({'answers':[m.predict(0,x,0) for x in range(4)],'receipt':r}))
'''
        p=subprocess.run([sys.executable,'-B','-c',script],input=json.dumps({'checkpoint':raw.decode('ascii'),'new_batches':[bad]}),
            text=True,capture_output=True,check=True,timeout=20)
        result=json.loads(p.stdout)
        self.assertEqual(result['answers'],[0,0,0,1]);self.assertEqual(result['receipt']['old_raw_rows_received'],0)

    def test_checkpoint_corruption_and_empty_packets_rejected(self):
        g,bad=self.initial();raw=g.checkpoint()
        with self.assertRaises(ValueError):repair_quarantined_basis(raw,'0'*64,0,[bad],max_degree=3)
        for batches in ([],[{'records':bad['records']}],[None]):
            with self.assertRaises(ValueError):self.repair(g,batches)

    def test_old_raw_witness_replay_is_explicitly_rejected(self):
        g,bad=self.initial()
        with self.assertRaisesRegex(ValueError,'OLD_RAW_ROW_REPLAY'):
            self.repair(g,[bad,packet([[0,0,0]])])


if __name__=='__main__':unittest.main()
