import copy
import hashlib
import tempfile
import unittest
from pathlib import Path
from diagnostic import read_verified,validate_trace,select_diagnostics,fit,PUBLIC,HIDDEN,majority_bound,independent_bound,information_partition,response_tables
from composition import Composition,PlasticNand,CONFIGS,route_bits,context
class DiagnosticTests(unittest.TestCase):
    def test_group_refinement_can_remove_source_uncertainty(self):
        rows=[(0,0,0,(0,0,0)),(0,1,0,(1,1,1))]
        self.assertEqual(majority_bound(rows),3);self.assertEqual(majority_bound(rows,True),6)
        self.assertEqual(independent_bound(rows),3);self.assertEqual(independent_bound(rows,True),6)
        p=information_partition(6,3,6);self.assertEqual((p['source_information_value_bound'],p['remaining_connection_information_ambiguity']),(3,0))
    def test_known_sources_can_leave_connection_ambiguity(self):
        rows=[(0,0,0,(0,0,0)),(0,0,0,(1,1,1))]
        self.assertEqual(majority_bound(rows,True),3)
        p=information_partition(6,3,3);self.assertEqual((p['source_information_value_bound'],p['remaining_connection_information_ambiguity']),(0,3))
        with self.assertRaises(ValueError):information_partition(6,5,4)
    def test_oracle_can_trade_previously_correct_observed_points(self):
        target=(0,)*8;a=[0]*8;b=[0]*8;c=[1]*8
        a[0]=1;b[1]=1
        for i in HIDDEN:a[i]=1;c[i]=0
        first,tie,any_route=select_diagnostics((tuple(a),tuple(b),tuple(c)),target)
        self.assertEqual((first,tie,any_route),(0,1,1))
        self.assertEqual(fit(a,target,PUBLIC),fit(b,target,PUBLIC));self.assertEqual(a[1],target[1]);self.assertNotEqual(b[1],target[1])
    def test_oracle_language_bound_can_ignore_training_fit(self):
        target=(0,)*8;a=tuple(0 if i in PUBLIC else 1 for i in range(8));b=tuple(1 if i in PUBLIC else 0 for i in range(8))
        self.assertEqual(select_diagnostics((a,b),target),(0,0,1))
    def test_cached_tables_match_generic_graphs(self):
        a=PlasticNand();b=PlasticNand();b.rows[-1]=[0,1,0,0,0,0,0,0,0]
        m=Composition((a.snapshot(),b.snapshot()));responses=response_tables(m.base_outputs());m.occupied=1
        for cfg,p in zip(CONFIGS,responses):
            m.first,m.outer,m.inject=route_bits(cfg)
            self.assertEqual(tuple(m.predict(context(i)) for i in range(8)),p)
    def test_hash_and_line_ending_custody(self):
        raw=b'one\ntwo\n';sha=hashlib.sha256(raw).hexdigest()
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'source';p.write_bytes(raw.replace(b'\n',b'\r\n'));self.assertEqual(read_verified(p,sha),raw)
            with self.assertRaises(ValueError):read_verified(p,'0'*64)
    def test_duplicate_truncated_malformed_trace_rejected(self):
        rows=[[n//32,(n%32)//2,n%2,0]+[[0]*8 for _ in range(5)]+[0,'0'*64] for n in range(1920)]
        self.assertEqual(len(validate_trace(rows)),1920)
        for mutation in ('duplicate','truncated','checkpoint','bit'):
            bad=copy.deepcopy(rows)
            if mutation=='duplicate':bad[1]=bad[0]
            if mutation=='truncated':bad.pop()
            if mutation=='checkpoint':bad[0][10]='bad'
            if mutation=='bit':bad[0][4][0]=True
            with self.assertRaises(ValueError):validate_trace(bad)
if __name__=='__main__':unittest.main()
