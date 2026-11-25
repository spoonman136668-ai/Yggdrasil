"""P0 source-free fixtures, including strict leakage and provenance negatives."""
from collections import Counter
from fractions import Fraction
import json
import time
import unittest
from uj04p_source_audit import extract,parse_fragment,pools,audit,decision,chain_key
from uj03a_pilot import digest

def raw_fixture(answer='A'):
    return b'\n'.join(json.dumps(dict(question='example '+chr(97+i),
        options=['A)1','B)2','C)3','D)4','E)5'],correct=answer,
        rationale=f'{i+10}+2={i+12};{i+12}*2={2*(i+12)}')).encode() for i in range(12))

class SourceGateTests(unittest.TestCase):
    def test_valid_exact_chain_and_spans(self):
        text='unrelated prose\n -1.5 + 2.5 = 1 ; 1 * 3 = 3\nend'
        run,reason,counts=extract(text)
        self.assertIsNone(reason)
        self.assertEqual(chain_key([s for s,_ in run]),(('-3/2','+','5/2','1'),('1','*','3','3')))
        self.assertEqual(text[slice(*run[0][1])],' -1.5 + 2.5 = 1 ')
        self.assertEqual(counts['verified_equation'],2)
        self.assertEqual(parse_fragment('2/4=0.5')[0][3],Fraction(1,2))
    def test_invalid_equations(self):
        for text,reason in [('1/0=0','zero_divisor'),('1+2=4','conflicting_arithmetic'),
            ('18446744073709551616+1=18446744073709551617','numeric_bound')]:
            self.assertEqual(extract(text)[1],reason)
        self.assertEqual(parse_fragment('answer: 1+2=3')[1],'unsupported')
        self.assertEqual(parse_fragment('1+2+3=6')[1],'unsupported')
        self.assertEqual(extract('1+2=3;3*2=6;1+1=4')[1],'conflicting_arithmetic')
    def test_linkage(self):
        self.assertEqual(extract('1+2=3;3+3=6')[1],'ambiguous_linkage')
        self.assertEqual(extract('1+2=3;3*2=6;3+4=7')[1],'branching_linkage')
        self.assertEqual(extract('1+2=3;prose;3*2=6')[1],'no_eligible_chain')
        self.assertEqual(extract('1+2=3;3+4=7;7+8=15;15+16=31;31+32=63')[1],'no_eligible_chain')
        self.assertEqual(extract('1+2=3;3*2=6;20+1=21;21*2=42')[0][0][0][0],1)
    def test_source_custody_and_no_answer_leakage(self):
        raw=raw_fixture()
        report,receipts=audit(raw,digest(raw),2,4,4)
        self.assertEqual([x['count'] for x in report['group_partitions']],[2,4,4])
        self.assertEqual(report['fit']['accepted_chains'],4)
        self.assertEqual(report['diagnostic']['accepted_chains'],4)
        self.assertEqual(report['exact_full_chain_overlap'],0)
        self.assertFalse(report['source_feasible'])
        self.assertEqual(report['model_training_steps'],0)
        changed=raw_fixture('E')
        other,rr=audit(changed,digest(changed),2,4,4)
        self.assertEqual(report['group_partitions'][1]['group_sha256'],other['group_partitions'][1]['group_sha256'])
        self.assertEqual([r['steps'] for r in receipts['fit']],[r['steps'] for r in rr['fit']])
        with self.assertRaises(ValueError):
            pools(raw,'0'*64,2,4,4)
        with self.assertRaises(RuntimeError):
            audit(raw,digest(raw),2,4,4,time.monotonic()-1)
    def test_frozen_gate(self):
        a=dict(accepted_chains=256,op_transitions={'+':64,'*':64})
        b=dict(accepted_chains=64,ordered_pair_chain_counts={'+*':16,'*+':16})
        self.assertTrue(decision(a,b,0)['source_feasible'])
        self.assertFalse(decision(a,b,1)['source_feasible'])
        b['ordered_pair_chain_counts']['*+']=15
        self.assertFalse(decision(a,b,0)['source_feasible'])
