import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from cases import ROOT,load_manifest,validate_manifest,MANIFEST_SHA
from run_dev import protected_ceiling
class ReplicationTests(unittest.TestCase):
    def test_all_manifest_cases_are_globally_disjoint_and_complete(self):
        d=load_manifest();old=set(d['old_unique_observed_targets']);cases=d['cases']
        self.assertEqual(len(cases),120);self.assertEqual(len({c['target'] for c in cases}),30)
        self.assertFalse(old&{c['target'] for c in cases});self.assertEqual(sum(c['protected_mask'].bit_count() for c in cases),444)
        self.assertEqual({s:sum(c['seed']==s for c in cases) for s in (17,29,43,71)},{17:30,29:30,43:30,71:30})
        self.assertTrue(all(c['old_target']^c['target']==32 and c['signature']==c['target']%32 for c in cases))
    def test_manifest_wrong_hash_and_transport_endings(self):
        raw=(ROOT/'cases.json').read_bytes().replace(b'\r\n',b'\n')
        self.assertEqual(hashlib.sha256(raw).hexdigest(),MANIFEST_SHA)
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'cases.json';p.write_bytes(raw.replace(b'\n',b'\r\n'));self.assertEqual(load_manifest(p),load_manifest())
            p.write_bytes(raw+b' ')
            with self.assertRaises(ValueError):load_manifest(p)
    def test_overlap_duplicate_missing_case_and_bad_types_rejected(self):
        d=load_manifest()
        for mutation in ('overlap','duplicate','missing','type','schema'):
            v=copy.deepcopy(d)
            if mutation=='overlap':v['cases'][0]['target']=v['cases'][0]['old_target']
            if mutation=='duplicate':v['cases'][1]=v['cases'][0]
            if mutation=='missing':v['cases'].pop()
            if mutation=='type':v['cases'][0]['protected_mask']=True
            if mutation=='schema':v['schema']='bad'
            with self.assertRaises(ValueError):validate_manifest(v)
    def test_protected_capacity_ceiling_small_independent_enumeration(self):
        reachable={0,3,12,63}
        for target in range(64):
            for mask in range(32):
                eligible=[v for v in reachable if all(((v>>j)&1)==((target>>j)&1) for j in range(5) if (mask>>j)&1)]
                if not eligible:
                    with self.assertRaises(ValueError):protected_ceiling(reachable,target,mask)
                else:
                    expected=max(sum(((v>>j)&1)==((target>>j)&1) for j in range(6)) for v in eligible)
                    self.assertEqual(protected_ceiling(reachable,target,mask),expected)
    def test_frozen_learner_source_matches_parent_provenance(self):
        p=json.loads((ROOT.parent/'WSP-27/provenance.json').read_text())
        for suffix in ('routed.py','diagnostics.py'):
            key='research/contrib/chatgpt/WSP-27/'+suffix
            raw=(ROOT.parent/'WSP-27'/suffix).read_bytes().replace(b'\r\n',b'\n')
            self.assertEqual(hashlib.sha256(raw).hexdigest(),p['files'][key]['sha256'])
if __name__=='__main__':unittest.main()
