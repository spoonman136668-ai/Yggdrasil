"""Fabricated API metadata only; never generate a registered world."""
import copy
import unittest
import owner_evidence_preflight as p


def fixture():
    base = p.PREFIX + '/actions/runs/' + str(p.RUN)
    jobs = [dict(name=n,id=i,run_id=p.RUN,head_sha=p.SOURCE,run_attempt=1,
                 status='completed',conclusion='success',runner_name='YGG-B-LINKDEADKB',
                 labels=['self-hosted','Windows','X64','yggdrasil','research-only'],
                 steps=[dict(name=s,status='completed',conclusion='success') for s in ss])
            for n,(i,ss) in p.JOBS.items()]
    artifacts = [dict(id=i,name='ace03-archive-fixture-'+t+'-'+str(p.RUN),expired=False,
                      digest='sha256:'+d,size_in_bytes=z,workflow_run=dict(id=p.RUN,head_sha=p.SOURCE))
                 for i,(t,d,z) in p.ARTIFACTS.items()]
    return {
        p.PREFIX+'/git/commits/'+p.SOURCE: dict(sha=p.SOURCE,tree=dict(sha=p.TREE)),
        p.PREFIX+'/git/ref/heads/'+p.BRANCH: dict(ref='refs/heads/'+p.BRANCH,object=dict(type='commit',sha=p.SOURCE)),
        base: dict(id=p.RUN,head_sha=p.SOURCE,head_branch=p.BRANCH,head_commit=dict(tree_id=p.TREE),
                   repository=dict(full_name=p.REPO),head_repository=dict(full_name=p.REPO),
                   path=p.WORKFLOW,event='push',run_attempt=1,status='completed',conclusion='success'),
        base+'/jobs?per_page=100': dict(total_count=2,jobs=jobs),
        base+'/artifacts?per_page=100': dict(total_count=2,artifacts=artifacts),
    }


class EvidenceTests(unittest.TestCase):
    def test_valid_never_admits(self):
        r=p.verify_evidence(fixture().__getitem__)
        self.assertTrue(r['qualification_metadata_verified'])
        self.assertFalse(r['native_admission_verified'])
        self.assertFalse(r['registered_execution_permitted'])

    def test_drift_and_incomplete_metadata(self):
        base=p.PREFIX+'/actions/runs/'+str(p.RUN)
        cases=[(p.PREFIX+'/git/commits/'+p.SOURCE,('tree','sha'),'0'*40),
               (p.PREFIX+'/git/ref/heads/'+p.BRANCH,('object','sha'),'0'*40),
               (base,('run_attempt',),2),(base,('conclusion',),'failure'),
               (base,('head_repository','full_name'),'other/repo'),
               (base+'/jobs?per_page=100',('total_count',),3),
               (base+'/jobs?per_page=100',('jobs',0,'runner_name'),'wrong'),
               (base+'/jobs?per_page=100',('jobs',0,'steps',0,'conclusion'),'skipped'),
               (base+'/jobs?per_page=100',('jobs',1,'head_sha'),'0'*40),
               (base+'/artifacts?per_page=100',('artifacts',0,'expired'),True),
               (base+'/artifacts?per_page=100',('artifacts',1,'digest'),'sha256:'+'0'*64),
               (base+'/artifacts?per_page=100',('artifacts',1,'workflow_run','id'),1)]
        for route,path,value in cases:
            with self.subTest(route=route,path=path):
                f=fixture(); node=f[route]
                for key in path[:-1]:node=node[key]
                node[path[-1]]=value
                with self.assertRaises(ValueError):p.verify_evidence(f.__getitem__)

    def test_duplicate_and_missing_fail_closed(self):
        base=p.PREFIX+'/actions/runs/'+str(p.RUN)
        f=fixture(); f[base+'/jobs?per_page=100']['jobs'][1]=copy.deepcopy(f[base+'/jobs?per_page=100']['jobs'][0])
        with self.assertRaises(ValueError):p.verify_evidence(f.__getitem__)
        f=fixture(); del f[base+'/artifacts?per_page=100']
        with self.assertRaises(KeyError):p.verify_evidence(f.__getitem__)


if __name__ == '__main__':
    unittest.main()
