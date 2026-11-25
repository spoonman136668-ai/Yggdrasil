"""Independent GitHub artifact byte readback for ACE03 predata supervision.

No authority issuance, primary CLI, registered input builder or executor.
The native owner adapter must supply authenticated original artifact metadata.
"""
import hashlib
import re
import stat
import zipfile
from pathlib import Path
from study_supervisor import MAX_RECORD, require, _collect, _classify_readback
from study_gate import TASKS

MAX_ARCHIVE = 128 * 1024 * 1024
STARTED = frozenset({'STARTED.json'})
RAW = frozenset({'STARTED.json','COLLECTING.json','TERMINAL.json'} |
                {'%03d.json'%i for i in range(2*len(TASKS))})


def sha(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(65536),b''):
            h.update(block)
    return h.hexdigest()


def read_archive(path, meta, *, artifact_id, uploaded_digest, name, run_id,
                 source_sha, expected_names):
    """Validate independently downloaded ZIP bytes against original upload/API identity."""
    require(expected_names in (STARTED,RAW),'archive scope')
    require(type(artifact_id) is int and artifact_id>0 and type(run_id) is int and run_id>0,
            'artifact/run identity')
    require(type(source_sha) is str and re.fullmatch('[0-9a-f]{40}',source_sha),'source identity')
    require(type(uploaded_digest) is str and re.fullmatch('[0-9a-f]{64}',uploaded_digest),
            'upload digest unavailable')
    require(type(meta) is dict and meta.get('id')==artifact_id and meta.get('name')==name
            and meta.get('expired') is False,'remote artifact identity')
    run=meta.get('workflow_run')
    require(type(run) is dict and run.get('id')==run_id and run.get('head_sha')==source_sha,
            'remote run/source identity')
    require(meta.get('digest')=='sha256:'+uploaded_digest,'remote digest drift')
    path=Path(path)
    require(path.is_file() and not path.is_symlink() and path.resolve()==path.absolute(),
            'archive path missing or redirected')
    require(0<path.stat().st_size<=MAX_ARCHIVE and meta.get('size_in_bytes')==path.stat().st_size,
            'archive byte count')
    require(file_sha(path)==uploaded_digest,'archive byte hash drift')
    with zipfile.ZipFile(path,'r') as z:
        members=z.infolist()
        require(len(members)==len(expected_names) and {m.filename for m in members}==expected_names,
                'archive member set or duplicate')
        require(all(not m.is_dir() and not stat.S_ISLNK(m.external_attr>>16)
                    and 0<m.file_size<=MAX_RECORD and not m.flag_bits&1 for m in members),
                'archive member type or size')
        require(sum(m.file_size for m in members)<=MAX_ARCHIVE,'archive expanded size')
        return {m.filename:z.read(m) for m in members}


def compare_local(journal, archived, names):
    require(set(archived)==names,'archive member identity')
    journal.verify_started()
    for name in names:
        local=journal.path/name
        require(local.is_file() and not local.is_symlink() and local.resolve()==local
                and 0<local.stat().st_size<=MAX_RECORD,'local archive member drift')
        require(local.read_bytes()==archived[name],'archive/local byte mismatch: '+name)


def collect_after_started(journal, archived, build, execute, **kwargs):
    """Only an authenticated native adapter may provide registered build/execute."""
    compare_local(journal,archived,STARTED)
    return _collect(journal,build,execute,**kwargs)


def classify_after_raw(journal, archived):
    """Do not classify unarchived or altered raw data."""
    require({p.name for p in journal.path.iterdir()}==RAW,'local raw file set')
    compare_local(journal,archived,RAW)
    return _classify_readback(journal,sha(archived['TERMINAL.json']),
                              [sha(archived['%03d.json'%i]) for i in range(2*len(TASKS))])
