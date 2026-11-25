"""Fabricated archive controls and native GitHub artifact round-trip only."""
import json
import os
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from study_worker import encode
from study_supervisor import Journal, EXPERIMENT
from study_archive_adapter import (STARTED, RAW, sha, file_sha, read_archive,
                                   collect_after_started, classify_after_raw)
from test_study_supervisor import identity, fabricated, fabricated_row, Clock


def restore_fixture(root):
    # This reconstructs a FABRICATED test journal, never native admission.
    j=Journal.__new__(Journal)
    j.path=root/'journal'/EXPERIMENT
    j.identity=identity()
    j.start_sha=sha(encode(dict(state='STARTED',identity=j.identity)))
    j.verify_started()
    return j


def fake_zip(path, members, name='fixture'):
    with zipfile.ZipFile(path,'x') as z:
        for filename,data in members:
            z.writestr(filename,data)
    digest=file_sha(path)
    return dict(id=123,name=name,expired=False,digest='sha256:'+digest,
                size_in_bytes=path.stat().st_size,workflow_run=dict(id=456,head_sha='1'*40)),digest


def load(path, meta, digest, names, name='fixture'):
    return read_archive(path,meta,artifact_id=123,uploaded_digest=digest,name=name,
                        run_id=456,source_sha='1'*40,expected_names=names)


class ArchiveFixtures(unittest.TestCase):
    def test_original_metadata_and_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp).resolve()
            path=root/'remote.zip'
            meta,digest=fake_zip(path,[('STARTED.json',b'original')])
            self.assertEqual(load(path,meta,digest,STARTED),{'STARTED.json':b'original'})
            for key,value in [('id',124),('name','wrong'),('expired',True),('digest','sha256:'+'0'*64),
                              ('size_in_bytes',0),('workflow_run',dict(id=456,head_sha='2'*40))]:
                bad=dict(meta);bad[key]=value
                with self.assertRaises(ValueError):load(path,bad,digest,STARTED)
            with self.assertRaises(ValueError):load(path,meta,'0'*64,STARTED)
            raw=path.read_bytes();path.write_bytes(bytes([raw[0]^1])+raw[1:])
            with self.assertRaisesRegex(ValueError,'hash drift'):load(path,meta,digest,STARTED)

    def test_archive_member_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp).resolve()
            for i,members in enumerate([[('../STARTED.json',b'x')],[('STARTED.json',b'x'),('extra',b'y')],
                                       [('STARTED.json',b'x'),('STARTED.json',b'y')]]):
                path=root/('%d.zip'%i);meta,digest=fake_zip(path,members)
                with self.assertRaises(ValueError):load(path,meta,digest,STARTED)

    def test_started_archive_required_and_raw_tamper(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp).resolve();j=Journal(root,identity())
            def forbidden(*args):self.fail('collection before independent STARTED')
            with self.assertRaises(ValueError):
                collect_after_started(j,{'STARTED.json':b'wrong'},forbidden,forbidden)
            original={'STARTED.json':(j.path/'STARTED.json').read_bytes()}
            collect_after_started(j,original,fabricated,fabricated_row,clock=Clock())
            raw={p.name:p.read_bytes() for p in j.path.iterdir()}
            self.assertEqual(set(raw),RAW)
            missing=dict(raw);missing.pop('000.json')
            with self.assertRaises(ValueError):classify_after_raw(j,missing)
            altered=dict(raw);altered['000.json']=b'{}'
            with self.assertRaises(ValueError):classify_after_raw(j,altered)
            self.assertEqual(classify_after_raw(j,raw)['arithmetic_disposition'],'DEV_PASS_CONDITIONAL')
            with self.assertRaises(ValueError):
                collect_after_started(j,original,forbidden,forbidden)


def native_fixture():
    # The only CLI here is a transport qualification using fabricated rows.
    mode,root=sys.argv[1:]
    root=Path(root).resolve()
    if mode=='--fixture-prepare':
        root.mkdir(exist_ok=False)
        (root/'journal').mkdir()
        Journal(root/'journal',identity())
        print('ACE_ARCHIVE_FIXTURE_LOCAL_STARTED_ONLY',flush=True)
        return
    j=restore_fixture(root)
    tag='started' if mode=='--fixture-collect' else 'raw'
    if mode not in ('--fixture-collect','--fixture-classify'):
        raise ValueError('fixture mode')
    run_id=int(os.environ['GITHUB_RUN_ID'])
    meta=json.loads((root/(tag+'.metadata.json')).read_text(encoding='utf-8-sig'))
    archived=read_archive(root/(tag+'.zip'),meta,
        artifact_id=int(os.environ['ACE_ARCHIVE_ID']),
        uploaded_digest=os.environ['ACE_ARCHIVE_DIGEST'],
        name='ace03-archive-fixture-'+tag+'-'+str(run_id),
        run_id=run_id,source_sha=os.environ['GITHUB_SHA'],
        expected_names=STARTED if tag=='started' else RAW)
    if tag=='started':
        collect_after_started(j,archived,fabricated,fabricated_row,clock=Clock())
        print('ACE_ARCHIVE_FIXTURE_REMOTE_STARTED_PASS RAW_ROWS=480 FABRICATED_ONLY',flush=True)
    else:
        result=classify_after_raw(j,archived)
        if result['arithmetic_disposition']!='DEV_PASS_CONDITIONAL' or result['scientific_gain_verified']:
            raise ValueError('fabricated fixture classification')
        print('ACE_ARCHIVE_FIXTURE_REMOTE_RAW_PASS REGISTERED_WORLDS=0',flush=True)


if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1].startswith('--fixture-'):
        native_fixture()
    else:
        unittest.main()
