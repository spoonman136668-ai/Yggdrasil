"""Q0 fabricated source and annotation negatives; no external data."""
import json
import time
import unittest
from uj03a_pilot import group
from uj04q_source_audit import annotations,select_gsm,audit,git_blob,old_groups,old_receipt_keys

def fixture(final='8'):
    return b'\n'.join(json.dumps(dict(question='question '+chr(97+i),
        answer=f'First <<{i+10}+2={i+12}>> then <<{i+12}*2={2*(i+12)}>>\n#### {final}')).encode()
        for i in range(12))

class Q0Tests(unittest.TestCase):
    def test_explicit_annotations_and_spans(self):
        text='text <<1+2=3>> more <<3*4=12>>\n#### 12'
        run,reason,counts=annotations(text)
        self.assertIsNone(reason)
        self.assertEqual([text[slice(*span)] for _,span in run],['<<1+2=3>>','<<3*4=12>>'])
        self.assertEqual(counts['verified_equation'],2)
        self.assertEqual(annotations('1+2=3;3*4=12')[1],'no_annotation')
        self.assertEqual(annotations(text.replace('#### 12','#### <<1/0=1>>'))[0],run)
    def test_malformed_and_invalid(self):
        for text in ('<<1+2=3','1+2=3>>','<<<1+2=3>>','<<1+<<2=3>>',
                     '<<1+2=3>>>','<<1+2=3>4>>'):
            self.assertEqual(annotations(text)[1],'malformed_annotation')
        self.assertEqual(annotations('<<1+2=4>>')[1],'conflicting_arithmetic')
        self.assertEqual(annotations('<<1/0=0>>')[1],'zero_divisor')
        self.assertEqual(annotations('<<1+2=3>> <<1+2+3=6>> <<3*2=6>>')[1],'no_eligible_chain')
    def test_linkage(self):
        self.assertEqual(annotations('<<1+2=3>> <<3+3=6>>')[1],'ambiguous_linkage')
        self.assertEqual(annotations('<<1+2=3>> <<3*2=6>> <<3+4=7>>')[1],'branching_linkage')
        self.assertEqual(annotations('<<1+2=3>> <<3+4=7>> <<7+8=15>> <<15+16=31>> <<31+32=63>>')[1],'no_eligible_chain')
    def test_partition_and_no_answer_leakage(self):
        raw=fixture()
        excluded={group('question a')}
        report,r=audit(raw,excluded,time.monotonic()+30,4,4)
        other,s=audit(fixture('99'),excluded,time.monotonic()+30,4,4)
        self.assertEqual(report['source_counts']['excluded_old_groups'],1)
        self.assertEqual([x['group_sha256'] for x in report['group_partitions']],
                         [x['group_sha256'] for x in other['group_partitions']])
        self.assertEqual([x['steps'] for x in r['fit']],[x['steps'] for x in s['fit']])
        self.assertEqual(report['fit']['accepted_chains'],4)
        self.assertEqual(report['diagnostic']['accepted_chains'],4)
        self.assertEqual(report['exact_full_chain_overlap'],0)
        self.assertFalse(report['cross_source_chain_overlap_verified'])
        self.assertFalse(report['source_feasible'])
        self.assertEqual(report['model_training_steps'],0)
    def test_schema_and_custody_fail_closed(self):
        for raw in (b'{"question":"q","answer":1}',b'\xff',b'bad'):
            with self.assertRaises(ValueError):
                select_gsm(raw,set(),1,1)
        with self.assertRaises(ValueError):
            select_gsm(fixture(),set(),12,12)
        with self.assertRaises(ValueError):
            old_groups(b'fake')
        with self.assertRaises(ValueError):
            old_receipt_keys(b'fake')
        self.assertEqual(git_blob(b''),'e69de29bb2d1d6434b8b29ae775ad8c2e48c5391')
        with self.assertRaises(RuntimeError):
            audit(fixture(),set(),time.monotonic()-1,4,4)
