import json
import subprocess
import sys
import unittest
from yggdrasil.native_context_basis import canonical,digest
from yggdrasil.native_context_accumulator import NativeContextAccumulator
from yggdrasil.native_context_quarantine import NativeContextQuarantine
from yggdrasil.native_prior_hypothesis import NativePriorHypothesis
from yggdrasil.native_knowledge_readout import NativeKnowledgeReadout,IDENTIFIED,PROVISIONAL,UNKNOWN


def fixture(value=1):
    from yggdrasil.native_prior_hypothesis import input_order
    rows=[[x,0,value] for x in sorted(range(8),key=input_order)]
    native=NativeContextAccumulator(3).stage_update(0,rows,digest(canonical(rows)),max_degree=4)
    raw=native.checkpoint();prior=NativePriorHypothesis.fit_checkpoint(raw,digest(raw))
    return NativeContextQuarantine(native),prior


class NativeKnowledgeReadoutTests(unittest.TestCase):
    def test_identified_precedence_and_explicit_provisional_status(self):
        base,prior=fixture();bundle=NativeKnowledgeReadout(base);raw=prior.checkpoint()
        updated=bundle.with_prior(0,raw,digest(raw))
        self.assertEqual(updated.readout(0,0,0)['status'],IDENTIFIED)
        self.assertEqual(updated.readout(0,0,1),{'value':1,'status':PROVISIONAL,'source_mode':'engineering_fixture_only','accepted_native':False})
        self.assertEqual(bundle.readout(0,0,1)['status'],UNKNOWN)

    def test_binding_preserves_all_source_bytes_and_exact_replay(self):
        base,prior=fixture();frozen=base.checkpoint();bundle=NativeKnowledgeReadout(base);raw=prior.checkpoint()
        updated=bundle.with_prior(0,raw,digest(raw))
        self.assertEqual(updated._base.checkpoint(),frozen)
        self.assertIs(updated.with_prior(0,raw,digest(raw)),updated)
        self.assertEqual(bundle._priors,(None,)*16)

    def test_wrong_source_pin_and_cross_address_binding_refused(self):
        base,prior=fixture();wrong,other=fixture(0);bundle=NativeKnowledgeReadout(base);raw=other.checkpoint()
        with self.assertRaisesRegex(ValueError,'WRONG_SOURCE'):bundle.with_prior(0,raw,digest(raw))
        raw=prior.checkpoint()
        with self.assertRaises(ValueError):bundle.with_prior(1,raw,digest(raw))
        with self.assertRaises(ValueError):bundle.with_prior(0,raw,'0'*64)

    def test_fabricated_fit_metadata_rejected_against_observed_values(self):
        base,prior=fixture();d=json.loads(prior.checkpoint());d['fit_errors']=1;bad=canonical(d)
        with self.assertRaisesRegex(ValueError,'FALSE_FIT_METADATA'):
            NativeKnowledgeReadout(base).with_prior(0,bad,digest(bad))

    def test_quarantined_source_cannot_be_bypassed_with_prior(self):
        base,prior=fixture();rows=[[0,0,0]]
        bad=base.stage_checked_update(0,rows,digest(canonical(rows)),max_degree=4)
        raw=prior.checkpoint()
        with self.assertRaisesRegex(ValueError,'QUARANTINED'):NativeKnowledgeReadout(bad).with_prior(0,raw,digest(raw))

    def test_cold_bundle_preserves_values_and_statuses_without_source(self):
        base,prior=fixture();p=prior.checkpoint();bundle=NativeKnowledgeReadout(base).with_prior(0,p,digest(p));raw=bundle.checkpoint()
        code='''import json,sys
from yggdrasil.native_knowledge_readout import NativeKnowledgeReadout
from yggdrasil.native_context_basis import digest
p=json.load(sys.stdin);raw=p.encode('ascii');m=NativeKnowledgeReadout.restore(raw,digest(raw))
print(json.dumps([m.readout(0,0,a) for a in (0,1)]))
'''
        p=subprocess.run([sys.executable,'-B','-c',code],input=json.dumps(raw.decode('ascii')),text=True,capture_output=True,check=True,timeout=20)
        self.assertEqual(json.loads(p.stdout),[bundle.readout(0,0,a) for a in (0,1)])

    def test_checkpoint_authority_flags_and_prior_shape_fail_closed(self):
        base,prior=fixture();raw=NativeKnowledgeReadout(base).checkpoint()
        for k,v in [('accepted_native',True),('source_mode','original'),('prior_hypotheses_ascii',[None])]:
            d=json.loads(raw);d[k]=v;bad=canonical(d)
            with self.assertRaises(ValueError):NativeKnowledgeReadout.restore(bad,digest(bad))

    def test_rejected_prior_does_not_remove_identified_knowledge(self):
        from yggdrasil.native_prior_hypothesis import input_order
        order=sorted(range(8),key=input_order);labels=[0]*8
        for x in order[6:]:labels[x]=1
        rows=[[x,0,labels[x]] for x in order]
        n=NativeContextAccumulator(3).stage_update(0,rows,digest(canonical(rows)),max_degree=4)
        raw=n.checkpoint();prior=NativePriorHypothesis.fit_checkpoint(raw,digest(raw));p=prior.checkpoint()
        b=NativeKnowledgeReadout(NativeContextQuarantine(n)).with_prior(0,p,digest(p))
        self.assertFalse(prior.eligible)
        for x in range(8):self.assertEqual(b.readout(0,x,0)['value'],labels[x])
        self.assertEqual(b.readout(0,0,1)['status'],UNKNOWN)


if __name__=='__main__':unittest.main()
