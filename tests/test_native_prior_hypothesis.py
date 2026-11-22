import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest
from yggdrasil.native_context_accumulator import NativeContextAccumulator
from yggdrasil.native_context_basis import canonical,digest
from yggdrasil.native_prior_hypothesis import NativePriorHypothesis,program_weights,input_order


def view(labels):
    rows=[[x&3,x>>2,int(y)] for x,y in enumerate(labels)]
    return NativeContextAccumulator(2).stage_update(0,rows,digest(canonical(rows)),max_degree=3)


class NativePriorHypothesisTests(unittest.TestCase):
    def test_original_qualified_rule_matches_without_more_edits(self):
        path=Path(__file__).resolve().parents[1]/'research/contrib/chatgpt/CKAD-09/reference/wsp147_direct.py'
        self.assertEqual(digest(path.read_bytes()),'b9867fbd7549f24a1b64121ce7702646a3c2d31e5d8f60d4c3670dc78705fec8')
        spec=importlib.util.spec_from_file_location('fixed_wsp147_reference',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        rows=tuple((x,(x&1)^int((x&6)==6)) for x in range(32))
        expected=m.program_weights(rows);weights,writes,errors=program_weights(rows,6)
        self.assertEqual((weights,writes,errors),(expected['weights'],expected['writes'],expected['residual_errors']))
        self.assertLessEqual(len(writes),16)

    def test_native_view_learns_and_keeps_input_checkpoint_exact(self):
        source=view([x&1 for x in range(8)]);raw=source.checkpoint()
        m=NativePriorHypothesis.fit_checkpoint(raw,digest(raw))
        self.assertTrue(m.eligible)
        self.assertEqual([m.predict_provisional(x&3,x>>2) for x in range(8)],[x&1 for x in range(8)])
        self.assertEqual(source.checkpoint(),raw)

    def test_calibration_failure_abstains_without_refitting(self):
        order=sorted(range(8),key=input_order);labels=[0]*8
        for x in order[6:]:labels[x]=1
        source=view(labels);raw=source.checkpoint();m=NativePriorHypothesis.fit_checkpoint(raw,digest(raw))
        self.assertEqual(m.info()['fit_errors'],0);self.assertEqual(m.info()['calibration_errors'],2)
        self.assertFalse(m.eligible);self.assertEqual(m.info()['writes'],[])
        self.assertTrue(all(m.predict_provisional(x&3,x>>2) is None for x in range(8)))

    def test_source_pin_and_other_address_information_rejected(self):
        source=view([1]*8);raw=source.checkpoint()
        with self.assertRaises(ValueError):NativePriorHypothesis.fit_checkpoint(raw,'0'*64)
        rows=[[x&3,x>>2,1] for x in range(8)]
        mixed=source.stage_update(1,rows,digest(canonical(rows)),max_degree=3);raw=mixed.checkpoint()
        with self.assertRaisesRegex(ValueError,'ISOLATED'):NativePriorHypothesis.fit_checkpoint(raw,digest(raw))

    def test_narrow_prior_cannot_be_smuggled_in_source_view(self):
        rows=[[x&3,x>>2,x&1] for x in range(8)]
        m=NativeContextAccumulator(2).stage_update(0,rows,digest(canonical(rows)),max_degree=1);raw=m.checkpoint()
        with self.assertRaises(ValueError):NativePriorHypothesis.fit_checkpoint(raw,digest(raw))

    def test_checkpoint_trace_flags_and_counts_are_validated(self):
        source=view([1]*8);raw=source.checkpoint();m=NativePriorHypothesis.fit_checkpoint(raw,digest(raw));saved=m.checkpoint()
        self.assertEqual(NativePriorHypothesis.restore(saved,digest(saved)).checkpoint(),saved)
        for key,value in [('writes',[]),('accepted_native',True),('status','IDENTIFIED'),('calibration_errors',99),('source_mode','original')]:
            d=json.loads(saved);d[key]=value;bad=canonical(d)
            with self.assertRaises(ValueError):NativePriorHypothesis.restore(bad,digest(bad))

    def test_cold_inference_needs_no_source_outcomes(self):
        source=view([1]*8);raw=source.checkpoint();m=NativePriorHypothesis.fit_checkpoint(raw,digest(raw));raw=m.checkpoint()
        code='''import json,sys
from yggdrasil.native_prior_hypothesis import NativePriorHypothesis
from yggdrasil.native_context_basis import digest
p=json.load(sys.stdin);raw=p.encode('ascii');m=NativePriorHypothesis.restore(raw,digest(raw))
print(json.dumps([m.predict_provisional(x&3,x>>2) for x in range(8)]))
'''
        p=subprocess.run([sys.executable,'-B','-c',code],input=json.dumps(raw.decode('ascii')),text=True,capture_output=True,check=True,timeout=20)
        self.assertEqual(json.loads(p.stdout),[1]*8)
        self.assertNotIn('records',json.loads(raw));self.assertNotIn('outcomes',json.loads(raw))

    def test_invalid_inputs_are_rejected_even_when_gate_fails(self):
        order=sorted(range(8),key=input_order);labels=[0]*8
        labels[order[-1]]=1;source=view(labels);raw=source.checkpoint();m=NativePriorHypothesis.fit_checkpoint(raw,digest(raw))
        with self.assertRaises(ValueError):m.predict_provisional(True,0)
        with self.assertRaises(ValueError):m.predict_provisional(0,2)
        with self.assertRaises(ValueError):program_weights([(0,0),(0,1)],3)


if __name__=='__main__':unittest.main()
