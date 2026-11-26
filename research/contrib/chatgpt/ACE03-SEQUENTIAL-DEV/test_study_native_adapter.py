"""Admission validation fixtures only. No machine trust changes or registered data."""
import datetime as dt
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import study_native_adapter as n
from study_supervisor import Journal
from test_study_supervisor import identity

NOW=dt.datetime(2026,1,1,tzinfo=dt.timezone.utc)

def fixture():
    expected=dict(qualified_sha='1'*40,qualified_tree='2'*40,qualifier_run=123,
        request_nonce='3'*64,prereg_blob=n.PREREG,supervisor_blob='4'*40,
        adapter_blob='5'*40,runner='YGG-B-LINKDEADKB',runtime_sha256='6'*64)
    a=dict(expected,schema=n.SCHEMA,experiment=n.EXPERIMENT,scope='bounded-dev-only',
        expires_utc='2026-01-02T00:00:00Z',max_tasks=480,total_seconds=14400,
        protected_first_use=False,promotion=False,paid_services=False)
    return a,expected

class NativeFixtures(unittest.TestCase):
    def test_admission_scope_and_binding(self):
        a,e=fixture();n.check_admission(a,e,NOW)
        for key,value in [('qualified_sha','7'*40),('runner','YGG-A-LINKDEADKB'),
            ('qualifier_run',True),('max_tasks',481),('total_seconds',14401),
            ('protected_first_use',True),('promotion',True),('paid_services',True),
            ('request_nonce','bad'),('expires_utc','2025-12-31T00:00:00Z'),
            ('expires_utc','2026-02-01T00:00:00Z'),('scope','production')]:
            bad=dict(a);bad[key]=value
            with self.assertRaises(ValueError):n.check_admission(bad,e,NOW)
        with self.assertRaises(ValueError):n.check_admission(dict(a,extra=True),e,NOW)
    def test_duplicate_fields(self):
        with self.assertRaises(ValueError):n.json_object(b'{"a":1,"a":2}')
    def test_no_context_no_claim(self):
        with patch.dict(n.os.environ,{},clear=True):
            with self.assertRaises(ValueError):n.context()
    def test_reopen_checks_exact_claim(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp).resolve()
            with self.assertRaises(ValueError):n.reopen(root,identity())
            j=Journal(root,identity())
            self.assertEqual(n.reopen(root,identity()).start_sha,j.start_sha)
            altered=dict(identity(),source_sha='7'*40)
            with self.assertRaises(ValueError):n.reopen(root,altered)
            with self.assertRaises(FileExistsError):Journal(root,identity())

if __name__=='__main__':unittest.main()
