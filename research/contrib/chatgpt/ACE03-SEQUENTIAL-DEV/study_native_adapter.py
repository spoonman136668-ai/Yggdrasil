"""Native owner-bound ACE03 DEV entrypoint. No authority creation or retries.

The native owner policy must already exist in the machine registry. The signed
CMS content comes from outside the checkout. Nothing provisions that trust.
This module cannot promote results or use protected data.
"""
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from study_supervisor import EXPERIMENT, Journal, require, identity_shape, read_record, write_new
from study_archive_adapter import STARTED, RAW, sha, file_sha, read_archive, collect_after_started, classify_after_raw
from study_gate import TASKS, TOTAL_SECONDS

SCHEMA='yggdrasil.ace03.native-dev-admission.v1'
REPO='spoonman136668-ai/Yggdrasil'
BRANCH='refs/heads/research/ace03-sequential-contract-dev-20261124'
PREREG='fd79c0a85ed92b31abc585c5b243d5f1edde98b9'
POLICY=r'SOFTWARE\CKBR\Yggdrasil\ACE03'
SIDECAR=Path(r'C:\ProgramData\CKBR\research-sidecar-yggdrasil')
NATIVE_PYTHON=SIDECAR/'python312'/'python.exe'


def git(*args):
    return subprocess.check_output(['git',*args],cwd=HERE,text=True).strip()


def json_object(raw):
    def unique(pairs):
        obj={}
        for k,v in pairs:
            require(k not in obj,'duplicate JSON field')
            obj[k]=v
        return obj
    return json.loads(raw,object_pairs_hook=unique)


def check_admission(a, expected, now):
    fields={'schema','experiment','scope','qualified_sha','qualified_tree','prereg_blob',
            'supervisor_blob','adapter_blob','runtime_sha256','runner','qualifier_run',
            'request_nonce','expires_utc','max_tasks','total_seconds','protected_first_use',
            'promotion','paid_services'}
    require(type(a) is dict and set(a)==fields,'signed admission fields')
    require(a['schema']==SCHEMA and a['experiment']==EXPERIMENT and
            a['scope']=='bounded-dev-only','signed admission scope')
    require(type(a['max_tasks']) is int and a['max_tasks']==2*len(TASKS)==480
            and type(a['total_seconds']) is int and a['total_seconds']==TOTAL_SECONDS,
            'signed admission budget')
    require(all(a[k] is False for k in ('protected_first_use','promotion','paid_services')),
            'prohibited authority')
    require(all(a[k]==v and type(a[k]) is type(v) for k,v in expected.items()),
            'signed admission identity drift')
    require(type(a['request_nonce']) is str and re.fullmatch('[0-9a-f]{64}',a['request_nonce']),
            'request nonce')
    require(type(a['expires_utc']) is str and re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z',a['expires_utc']),
            'expiry format')
    expires=dt.datetime.strptime(a['expires_utc'],'%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=dt.timezone.utc)
    require(now.tzinfo is not None and now<expires<=now+dt.timedelta(days=7),'admission expired or too broad')


def machine_policy():
    # HKLM policy is supplied by the native owner/administrator, never the repo.
    # This reads only. Absence is a hard stop, not permission to provision.
    require(sys.platform=='win32','native Windows required')
    import winreg
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,POLICY,0,
                        winreg.KEY_READ|winreg.KEY_WOW64_64KEY) as key:
        pin,kind=winreg.QueryValueEx(key,'OwnerCertificateSha256')
        require(kind==winreg.REG_SZ and re.fullmatch('[0-9a-f]{64}',pin),'owner trust pin')
        root,kind=winreg.QueryValueEx(key,'OwnerJournalRoot')
        require(kind==winreg.REG_SZ,'native root type')
    root=Path(root)
    require(root.is_absolute() and root.is_dir() and root.resolve()==root and
            not root.is_symlink() and root!=SIDECAR and SIDECAR in root.parents,
            'native custody root invalid')
    return pin,root


def authenticated_content(pin,root):
    cms=root/'owner-admission.p7m'
    require(cms.is_file() and not cms.is_symlink() and cms.resolve()==cms
            and 0<cms.stat().st_size<=65536,'native signed receipt missing')
    # Use system PowerShell and .NET CMS verification, with a machine-local
    # externally provisioned exact signing-certificate SHA256 pin. No signing.
    ps=Path(os.environ['SystemRoot'])/'System32'/'WindowsPowerShell'/'v1.0'/'powershell.exe'
    command=r"""
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Security
$cms=New-Object System.Security.Cryptography.Pkcs.SignedCms
$cms.Decode([IO.File]::ReadAllBytes($env:ACE_CMS_PATH))
if($cms.Detached -or $cms.SignerInfos.Count -ne 1){throw 'CMS_SIGNER_COUNT'}
$cms.CheckSignature($true)
$s=$cms.SignerInfos[0]
if($null -eq $s.Certificate){throw 'CMS_CERT_MISSING'}
$hash=[Security.Cryptography.SHA256]::Create()
try{$actual=([BitConverter]::ToString($hash.ComputeHash($s.Certificate.RawData))).Replace('-','').ToLowerInvariant()}finally{$hash.Dispose()}
if($actual -cne $env:ACE_CERT_SHA256){throw 'CMS_OWNER_PIN_MISMATCH'}
if([DateTime]::UtcNow -lt $s.Certificate.NotBefore.ToUniversalTime() -or [DateTime]::UtcNow -gt $s.Certificate.NotAfter.ToUniversalTime()){throw 'CMS_CERT_EXPIRED'}
[Console]::Write([Convert]::ToBase64String($cms.ContentInfo.Content))
"""
    env=dict(os.environ,ACE_CMS_PATH=str(cms),ACE_CERT_SHA256=pin)
    import base64
    r=subprocess.run([str(ps),'-NoProfile','-NonInteractive','-Command',command],
                     env=env,capture_output=True,timeout=30,check=True)
    require(len(r.stdout)<=65536,'signed content size')
    raw=base64.b64decode(r.stdout,validate=True)
    require(0<len(raw)<=16384,'signed receipt size')
    return raw


# GET-only qualification evidence. No issuance of owner authority.
WORKFLOW='.github/workflows/direct-research-qualification.yml'
OWNER='spoonman136668-ai'
PREFIX='/repos/'+REPO
QUAL_STEPS={
    'windows':('Checkout exact candidate','Verify source lock and phase custody',
        'Full repository regression and frozen atlas check',
        'All ACE03 fixtures and syntax build',
        'Read back original started archive and verify bytes',
        'Read back original raw archive and verify bytes',
        'Native admission policy availability (read-only)','Final exact worktree'),
    'linux':('Exact frozen source, atlas, full regression and ACE03 build',),
}


def verify_run_identity(doc, run_id, source, tree):
    require(doc['id']==run_id and doc['head_sha']==source
            and doc['head_commit']['tree_id']==tree
            and doc['head_branch']==BRANCH.removeprefix('refs/heads/')
            and doc['repository']['full_name']==REPO
            and doc['head_repository']['full_name']==REPO
            and doc['path']==WORKFLOW and doc['event']=='push'
            and doc['run_attempt']==1 and doc['actor']['login']==OWNER
            and doc['triggering_actor']['login']==OWNER,'authenticated workflow identity')


def exact_run_index(doc, key, field, count):
    rows=doc[key]
    require(type(rows) is list and doc['total_count']==len(rows)==count,
            'incomplete or extra '+key)
    index={row[field]:row for row in rows}
    require(len(index)==count,'duplicate '+key)
    return index


def verify_qualification(get, req, head, tree, current_run, runner):
    """Read-only evidence; neither this result nor GitHub identity admits a study."""
    qid=req['qualifier_run']
    require(type(qid) is int and type(current_run) is int and 0<qid<current_run,
            'qualification must precede request')
    for value in (req['qualified_sha'],req['qualified_tree'],head,tree):
        require(type(value) is str and re.fullmatch('[0-9a-f]{40}',value),'exact source identity')
    current=PREFIX+'/actions/runs/'+str(current_run)
    original=PREFIX+'/actions/runs/'+str(qid)
    now=get(current)
    verify_run_identity(now,current_run,head,tree)
    require(now['status']=='in_progress' and now['conclusion'] is None,
            'current run not active')
    q=get(original)
    verify_run_identity(q,qid,req['qualified_sha'],req['qualified_tree'])
    require(q['status']=='completed' and q['conclusion']=='success','qualification not successful')
    jobs=exact_run_index(get(original+'/jobs?per_page=100'),'jobs','name',2)
    require(set(jobs)==set(QUAL_STEPS),'required qualification platforms')
    for name,steps in QUAL_STEPS.items():
        job=jobs[name]
        require(job['run_id']==qid and job['head_sha']==req['qualified_sha']
                and job['run_attempt']==1 and job['status']=='completed'
                and job['conclusion']=='success','qualified job identity')
        seen={step['name']:step for step in job['steps']}
        require(len(seen)==len(job['steps']) and all(
            s in seen and seen[s]['status']=='completed' and seen[s]['conclusion']=='success'
            for s in steps),'qualified step missing or failed')
    require(jobs['windows']['runner_name']==runner and
            {'self-hosted','Windows','X64','yggdrasil','research-only'}<=set(jobs['windows']['labels']),
            'qualified native runner mismatch')
    require('ubuntu-latest' in jobs['linux']['labels'],'qualified Linux runner mismatch')
    items=exact_run_index(get(original+'/artifacts?per_page=100'),'artifacts','name',2)
    expected={'ace03-archive-fixture-'+tag+'-'+str(qid) for tag in ('started','raw')}
    require(set(items)==expected and len({v['id'] for v in items.values()})==2,'qualification archive identity')
    for item in items.values():
        require(type(item['id']) is int and item['id']>0
                and item['expired'] is False and re.fullmatch('sha256:[0-9a-f]{64}',item['digest'])
                and type(item['size_in_bytes']) is int and item['size_in_bytes']>0
                and item['workflow_run']['id']==qid
                and item['workflow_run']['head_sha']==req['qualified_sha'],
                'qualification archive missing or altered')
    return qid


def native_qualification_get(req, current_run):
    """Bounded GET only; credential comes from the native workflow, never source."""
    from urllib.request import Request, build_opener, HTTPRedirectHandler
    class NoRedirect(HTTPRedirectHandler):
        def redirect_request(self, *args, **kwargs):
            raise ValueError('qualification redirect forbidden')
    token=os.environ.pop('ACE_QUAL_READ_TOKEN','')
    require(bool(token) and not any(c in token for c in ('\r','\n')),'native read credential missing')
    base=PREFIX+'/actions/runs/'+str(req['qualifier_run'])
    allowed={base,base+'/jobs?per_page=100',base+'/artifacts?per_page=100',
             PREFIX+'/actions/runs/'+str(current_run)}
    def get(route):
        require(route in allowed,'qualification route forbidden')
        request=Request('https://api.github.com'+route,headers={
            'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json',
            'X-GitHub-Api-Version':'2022-11-28','User-Agent':'ace03-native-qualification'})
        with build_opener(NoRedirect()).open(request,timeout=20) as response:
            require(response.status==200,'qualification GET status')
            raw=response.read(1048577)
        require(len(raw)<=1048576,'qualification response too large')
        return json_object(raw)
    return get


def context():
    # Only the exact native research workflow can call the adapter. These
    # environment checks are not by themselves authentication.
    require(sys.platform=='win32' and Path(sys.executable).resolve()==NATIVE_PYTHON.resolve(),
            'native runtime mismatch')
    expected_env={'GITHUB_ACTIONS':'true','GITHUB_REPOSITORY':REPO,'GITHUB_REF':BRANCH,
                  'GITHUB_ACTOR':'spoonman136668-ai','GITHUB_TRIGGERING_ACTOR':'spoonman136668-ai',
                  'GITHUB_RUN_ATTEMPT':'1','GITHUB_EVENT_NAME':'push'}
    require(all(os.environ.get(k)==v for k,v in expected_env.items()),'workflow custody')
    top=Path(git('rev-parse','--show-toplevel')).resolve()
    head=git('rev-parse','HEAD')
    require(head==os.environ.get('GITHUB_SHA') and Path.cwd().resolve()==top and
            not git('status','--porcelain','--untracked-files=all'),'checkout custody')
    req_path=HERE/'native_execution_request.json'
    require(req_path.is_file() and not req_path.is_symlink(),'explicit request missing')
    req=json_object(req_path.read_bytes())
    require(type(req) is dict and set(req)=={'qualified_sha','qualified_tree','qualifier_run','request_nonce'},
            'request fields')
    require(type(req['qualifier_run']) is int and req['qualifier_run']>0,'qualification run identity')
    parent=git('rev-parse','HEAD^')
    require(parent==req['qualified_sha'] and git('rev-parse',parent+'^{tree}')==req['qualified_tree'],
            'qualified parent drift')
    require(git('diff','--name-only',parent,head).splitlines()==[req_path.relative_to(top).as_posix()],
            'request-only transition required')
    manifest=HERE/'prereg.json'
    require(git('rev-parse','HEAD:'+manifest.relative_to(top).as_posix())==PREREG,'preregistration drift')
    m=json_object(manifest.read_bytes())
    require(m['authority']['execution_admitted'] is False and m['authority']['protected_first_use'] is False
            and len(m['source_blobs'])==17,'manifest scope')
    for path,blob in m['source_blobs'].items():
        require(git('rev-parse','HEAD:'+path)==blob,'frozen source drift')
    runtime= file_sha(NATIVE_PYTHON)
    runner=os.environ.get('RUNNER_NAME','')
    pin,root=machine_policy()
    raw=authenticated_content(pin,root)
    admission=json_object(raw)
    expected=dict(req,prereg_blob=PREREG,
        supervisor_blob=git('rev-parse','HEAD:'+(HERE/'study_supervisor.py').relative_to(top).as_posix()),
        adapter_blob=git('rev-parse','HEAD:'+(HERE/'study_native_adapter.py').relative_to(top).as_posix()),
        runner=runner,runtime_sha256=runtime)
    check_admission(admission,expected,dt.datetime.now(dt.timezone.utc))
    current_run=int(os.environ['GITHUB_RUN_ID'])
    head_tree=git('rev-parse','HEAD^{tree}')
    verify_qualification(native_qualification_get(req,current_run),req,head,head_tree,current_run,runner)
    identity=dict(experiment=EXPERIMENT,source_sha=head,source_tree=head_tree,
        supervisor_blob=expected['supervisor_blob'],prereg_blob=PREREG,runner=runner,
        runtime_sha256=runtime,admission_sha256=sha(raw),qualifier_run=req['qualifier_run'])
    identity_shape(identity)
    return root,identity


def reopen(root,identity):
    # A new stage may read, but can never create or replace the existing claim.
    j=Journal.__new__(Journal)
    j.path=root/EXPERIMENT
    j.identity=identity
    _,j.start_sha=read_record(j.path/'STARTED.json')
    j.verify_started()
    return j


def archive(stage,root,identity):
    # Read-back files are obtained by the qualified run-scoped archive workflow.
    out=Path(os.environ['ACE_ARCHIVE_ROOT']).resolve(strict=True)
    require(out.is_dir() and out!=root and root not in out.parents and out not in root.parents,
            'archive staging overlaps native journal')
    run_id=int(os.environ['GITHUB_RUN_ID'])
    return read_archive(out/(stage+'.zip'),json_object((out/(stage+'.metadata.json')).read_bytes().decode('utf-8-sig')),
        artifact_id=int(os.environ['ACE_ARCHIVE_ID']),uploaded_digest=os.environ['ACE_ARCHIVE_DIGEST'],
        name='ace03-native-'+stage+'-'+str(run_id),run_id=run_id,
        source_sha=identity['source_sha'],expected_names=STARTED if stage=='started' else RAW)


def main():
    require(len(sys.argv)==2 and sys.argv[1] in ('--prepare','--collect','--classify'),'explicit native stage')
    root,identity=context()
    stage=sys.argv[1]
    if stage=='--prepare':
        j=Journal(root,identity)
        print('ACE_NATIVE_STARTED_SHA256='+j.start_sha,flush=True)
        return 0
    j=reopen(root,identity)
    if stage=='--collect':
        remote=archive('started',root,identity)
        # Registered inputs are imported only after owner admission and remote
        # STARTED proof. _collect rejects all repeated/partial collection.
        from study_worker import build_registered, execute_explicit
        result=collect_after_started(j,remote,build_registered,execute_explicit)
        print('ACE_NATIVE_RAW_ROWS='+str(result['rows']),flush=True)
        return 0
    remote=archive('raw',root,identity)
    result=classify_after_raw(j,remote)
    # Final classification is outside the archived raw directory.
    write_new(root/(EXPERIMENT+'-classification.json'),result)
    print('ACE_NATIVE_DEV_CLASSIFICATION='+json.dumps(result,sort_keys=True,allow_nan=False),flush=True)
    return int(result['arithmetic_disposition']=='INVALID')


if __name__=='__main__':
    raise SystemExit(main())
