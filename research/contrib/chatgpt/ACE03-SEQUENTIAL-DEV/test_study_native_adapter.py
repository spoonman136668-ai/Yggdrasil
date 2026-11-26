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
    def test_independent_qualification_evidence(self):
        req=dict(qualified_sha='1'*40,qualified_tree='2'*40,qualifier_run=100)
        head,tree,current='3'*40,'4'*40,101
        runner='YGG-B-LINKDEADKB'
        base=n.PREFIX+'/actions/runs/100'
        def run(i,s,t,status,conclusion):
            return dict(id=i,head_sha=s,head_commit=dict(tree_id=t),
                head_branch=n.BRANCH.removeprefix('refs/heads/'),
                repository=dict(full_name=n.REPO),head_repository=dict(full_name=n.REPO),
                path=n.WORKFLOW,event='push',run_attempt=1,actor=dict(login=n.OWNER),
                triggering_actor=dict(login=n.OWNER),status=status,conclusion=conclusion)
        def evidence():
            jobs=[dict(name=k,run_id=100,head_sha=req['qualified_sha'],run_attempt=1,
                status='completed',conclusion='success',runner_name=runner,
                labels=['self-hosted','Windows','X64','yggdrasil','research-only'] if k=='windows'
                    else ['ubuntu-latest'],
                steps=[dict(name=s,status='completed',conclusion='success') for s in steps])
                for k,steps in n.QUAL_STEPS.items()]
            items=[dict(id=i,name='ace03-archive-fixture-'+tag+'-100',expired=False,
                digest='sha256:'+'a'*64,size_in_bytes=123,
                workflow_run=dict(id=100,head_sha=req['qualified_sha']))
                for i,tag in enumerate(('started','raw'),1)]
            return {base:run(100,req['qualified_sha'],req['qualified_tree'],'completed','success'),
                n.PREFIX+'/actions/runs/101':run(101,head,tree,'in_progress',None),
                base+'/jobs?per_page=100':dict(total_count=2,jobs=jobs),
                base+'/artifacts?per_page=100':dict(total_count=2,artifacts=items)}
        self.assertEqual(n.verify_qualification(evidence().__getitem__,req,head,tree,current,runner),100)
        for route,path,value in [
            (base,('conclusion',),'failure'),(base,('run_attempt',),2),
            (base,('head_commit','tree_id'),'0'*40),
            (base,('triggering_actor','login'),'other'),
            (n.PREFIX+'/actions/runs/101',('status',),'completed'),
            (n.PREFIX+'/actions/runs/101',('head_sha',),'0'*40),
            (base+'/jobs?per_page=100',('total_count',),3),
            (base+'/jobs?per_page=100',('jobs',0,'runner_name'),'wrong'),
            (base+'/jobs?per_page=100',('jobs',0,'steps',0,'conclusion'),'skipped'),
            (base+'/jobs?per_page=100',('jobs',1,'labels'),['wrong']),
            (base+'/artifacts?per_page=100',('artifacts',0,'expired'),True),
            (base+'/artifacts?per_page=100',('artifacts',1,'workflow_run','id'),99),
            (base+'/artifacts?per_page=100',('artifacts',1,'id'),1)]:
            with self.subTest(route=route,path=path):
                f=evidence(); node=f[route]
                for key in path[:-1]:node=node[key]
                node[path[-1]]=value
                with self.assertRaises(ValueError):
                    n.verify_qualification(f.__getitem__,req,head,tree,current,runner)
        with self.assertRaises(ValueError):
            n.verify_qualification(evidence().__getitem__,req,head,tree,100,runner)

    def test_native_qualification_requires_read_credential(self):
        with patch.dict(n.os.environ,{},clear=True):
            with self.assertRaises(ValueError):
                n.native_qualification_get(dict(qualifier_run=100),101)

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
