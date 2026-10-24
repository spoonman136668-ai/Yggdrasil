import copy, importlib.util, json, pathlib, tempfile, unittest
from unittest.mock import patch

from verify_admission_snapshot import ROOT, PACKAGE, audit_package

class AuditTests(unittest.TestCase):
    def evidence(self):
        return json.loads((ROOT / 'upstream_readonly_evidence.json').read_text())
    def test_correct_package_still_holds(self):
        r=audit_package(evidence=self.evidence())
        self.assertEqual(r['status'],'HOLD')
        self.assertEqual(r['source_candidate_integrity'],'PASS')
        self.assertFalse(r['execution_permission'])
    def test_synthetic_success_not_source_permit(self):
        r=audit_package(evidence=self.evidence())
        self.assertFalse(r['scientific_admission'])
        self.assertIn('CKB_AUTHENTICATED_WRITER_IDENTITY',r['outstanding_authoritative_gates'])
    def test_r243_run_swap_rejected(self):
        e=self.evidence();e['r243']['qualified_run']=40084584132
        self.assertIn('R243_INACTIVE_BOUNDARY_DRIFT',audit_package(evidence=e)['violations'])
    def test_r243_head_swap_rejected(self):
        e=self.evidence();e['r243']['qualified_head']='0'*40
        self.assertIn('R243_INACTIVE_BOUNDARY_DRIFT',audit_package(evidence=e)['violations'])
    def test_false_live_activation_rejected(self):
        e=self.evidence();e['r243']['live_activation']=True
        self.assertIn('R243_INACTIVE_BOUNDARY_DRIFT',audit_package(evidence=e)['violations'])
    def test_false_writer_authentication_rejected(self):
        e=self.evidence();e['r243']['live_writer_authenticated']=True
        self.assertIn('R243_INACTIVE_BOUNDARY_DRIFT',audit_package(evidence=e)['violations'])
    def test_r234_as_live_rejected(self):
        e=self.evidence();e['r234']['active']=True
        self.assertIn('R234_PROPOSAL_PROVENANCE_DRIFT',audit_package(evidence=e)['violations'])
    def test_swapped_local_source_file_rejected(self):
        with patch('verify_admission_snapshot.sha256',return_value='0'*64):
            r=audit_package(evidence=self.evidence())
        self.assertEqual(r['source_candidate_integrity'],'FAIL')
        self.assertTrue(any(x.startswith('LOCAL_FILE_DRIFT:') for x in r['violations']))
    def test_missing_local_manifest_rejected(self):
        with tempfile.TemporaryDirectory() as p:
            r=audit_package(package=p,evidence=self.evidence())
            self.assertEqual(r['reason'],'LOCAL_PACKAGE_UNREADABLE')
            self.assertFalse(r['execution_permission'])
    def test_heldout_ref_is_not_per_host(self):
        e=self.evidence()
        self.assertEqual(e['r234']['seed_claim_namespace'],
            'refs/heads/scientific-custody/heldout-seed/{lane}/{seed-hex8}')
        self.assertFalse(e['r234']['per_arm_claims_proven'])

if __name__=='__main__':unittest.main()
