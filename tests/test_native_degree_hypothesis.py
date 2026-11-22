import json
import unittest
from yggdrasil.native_context_basis import canonical,digest
from yggdrasil.native_context_accumulator import NativeContextAccumulator
from yggdrasil.native_prior_hypothesis import input_order
from yggdrasil.native_degree_hypothesis import NativeDegreeHypothesis


def view(labels,bits=3,degree=None):
    rows=[[x&((1<<bits)-1),x>>bits,int(y)] for x,y in enumerate(labels)]
    return NativeContextAccumulator(bits).stage_update(0,rows,digest(canonical(rows)),max_degree=degree or bits+1)


class NativeDegreeHypothesisTests(unittest.TestCase):
    def test_degree_selected_from_constraints_not_family_label(self):
        labels=[int(sum((x>>p)&1 for p in range(3))>=2) for x in range(16)]
        source=view(labels);raw=source.checkpoint();m=NativeDegreeHypothesis.fit_checkpoint(raw,digest(raw))
        self.assertEqual(m.info()['selected_degree'],2);self.assertEqual(m.info()['rejected_fit_degrees'],[1])
        self.assertTrue(m.eligible);self.assertEqual([m.predict_provisional(x&7,x>>3) for x in range(16)],labels)
        self.assertEqual(source.checkpoint(),raw)

    def test_calibration_failure_stops_without_searching_higher_class(self):
        order=sorted(range(16),key=input_order);labels=[0]*16
        for x in order[12:]:labels[x]=1
        source=view(labels);raw=source.checkpoint();m=NativeDegreeHypothesis.fit_checkpoint(raw,digest(raw))
        self.assertEqual(m.info()['selected_degree'],1);self.assertEqual(m.info()['rejected_fit_degrees'],[])
        self.assertEqual(m.info()['calibration_wrong'],4);self.assertFalse(m.eligible)
        self.assertTrue(all(m.predict_provisional(x&7,x>>3) is None for x in range(16)))

    def test_unidentified_calibration_cannot_be_mislabeled_correct(self):
        labels=[int(x==15) for x in range(16)]
        source=view(labels);raw=source.checkpoint();m=NativeDegreeHypothesis.fit_checkpoint(raw,digest(raw))
        self.assertFalse(m.eligible)
        self.assertGreater(m.info()['calibration_wrong']+m.info()['calibration_unidentified'],0)

    def test_isolated_complete_basis_and_exact_counts_required(self):
        labels=[x&1 for x in range(16)];source=view(labels,degree=1);raw=source.checkpoint()
        with self.assertRaises(ValueError):NativeDegreeHypothesis.fit_checkpoint(raw,digest(raw))
        source=view(labels);rows=[[0,0,0]];source=source.stage_update(1,rows,digest(canonical(rows)),max_degree=4);raw=source.checkpoint()
        with self.assertRaises(ValueError):NativeDegreeHypothesis.fit_checkpoint(raw,digest(raw))
        source=view(labels);raw=source.checkpoint()
        with self.assertRaises(ValueError):NativeDegreeHypothesis.fit_checkpoint(raw,'0'*64)

    def test_checkpoint_flags_trace_and_source_binding_are_strict(self):
        source=view([x&1 for x in range(16)]);raw=source.checkpoint();m=NativeDegreeHypothesis.fit_checkpoint(raw,digest(raw));raw=m.checkpoint()
        self.assertEqual(NativeDegreeHypothesis.restore(raw,digest(raw)).checkpoint(),raw)
        for key,value in [('selected_degree',3),('fit_rows_sha256','0'*64),('status','IDENTIFIED'),('eligible',False),('rejected_fit_degrees',[1]),('calibration_unidentified',99)]:
            d=json.loads(raw);d['info'][key]=value;bad=canonical(d)
            with self.assertRaises(ValueError):NativeDegreeHypothesis.restore(bad,digest(bad))
        d=json.loads(raw);d['source_mode']='original';bad=canonical(d)
        with self.assertRaises(ValueError):NativeDegreeHypothesis.restore(bad,digest(bad))
        with self.assertRaises(ValueError):NativeDegreeHypothesis.restore(raw+b'\n',digest(raw+b'\n'))

    def test_invalid_inputs_rejected_even_if_gate_denied(self):
        order=sorted(range(16),key=input_order);labels=[0]*16;labels[order[-1]]=1
        source=view(labels);raw=source.checkpoint();m=NativeDegreeHypothesis.fit_checkpoint(raw,digest(raw))
        for c,a in ((8,0),(0,2),(True,0),(0,True)):
            with self.assertRaises(ValueError):m.predict_provisional(c,a)


if __name__=='__main__':unittest.main()
