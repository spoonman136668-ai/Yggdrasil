"""Predata owner-side supervision primitives. No registered generator or primary CLI.

Local journal guarantees exclusive creation and readback, not owner authentication
or independent archive custody. A separately qualified native owner adapter must
authenticate admission, root identity and durable remote STARTED/raw receipts.
No code here issues authority or dispatches work.
"""
import hashlib
import json
import os
import re
import time
from pathlib import Path
from study_gate import TASKS, TOTAL_SECONDS, PER_ARM_SECONDS, classify
from study_worker import encode, digest, expected_stream_identity, verify_counterfactual_inputs, verify_pair

EXPERIMENT = 'ACE03-XFER01-DEV-A1'
MAX_RECORD = 262144

def require(ok, reason):
    if not ok:
        raise ValueError(reason)

def identity_shape(identity):
    fields = {'experiment','source_sha','source_tree','supervisor_blob','prereg_blob',
              'runner','runtime_sha256','admission_sha256','qualifier_run'}
    require(type(identity) is dict and set(identity)==fields, 'identity fields')
    require(identity['experiment']==EXPERIMENT, 'experiment identity')
    for field in ('source_sha','source_tree','supervisor_blob','prereg_blob'):
        require(type(identity[field]) is str and re.fullmatch('[0-9a-f]{40}',identity[field]), 'git identity')
    for field in ('runtime_sha256','admission_sha256'):
        require(type(identity[field]) is str and re.fullmatch('[0-9a-f]{64}',identity[field]), 'receipt identity')
    require(identity['runner'] in ('YGG-A-LINKDEADKB','YGG-B-LINKDEADKB','YGG-C-LINKDEADKB'), 'runner identity')
    require(type(identity['qualifier_run']) is int and identity['qualifier_run']>0, 'qualifier identity')

def match_identity(expected, observed):
    """Consistency only; trusted native adapter must authenticate both inputs."""
    identity_shape(expected); identity_shape(observed)
    require(expected==observed, 'admission/source/runner drift')

def write_new(path, value):
    raw=encode(value)
    require(0<len(raw)<=MAX_RECORD, 'record size')
    # Never overwrite or remove a partial file. Any uncertainty burns the slot.
    with path.open('xb') as out:
        out.write(raw); out.flush(); os.fsync(out.fileno())
    require(path.is_file() and not path.is_symlink() and path.read_bytes()==raw, 'record readback')
    return hashlib.sha256(raw).hexdigest()

def read_record(path):
    require(path.is_file() and not path.is_symlink() and 0<path.stat().st_size<=MAX_RECORD, 'record unavailable')
    raw=path.read_bytes()
    value=json.loads(raw)
    require(encode(value)==raw, 'record encoding')
    return value, hashlib.sha256(raw).hexdigest()

class Journal:
    """Exclusive experiment directory; local only, no authority or archive claims."""
    def __init__(self, owner_root, identity):
        identity_shape(identity)
        root=Path(owner_root)
        require(root.is_absolute() and root.is_dir() and not root.is_symlink()
                and root.resolve()==root, 'owner root missing or redirected')
        self.path=root/EXPERIMENT
        self.identity=dict(identity)
        self.path.mkdir(exist_ok=False)
        self.start_sha=write_new(self.path/'STARTED.json',dict(state='STARTED',identity=self.identity))
    def verify_started(self):
        require(self.path.is_dir() and not self.path.is_symlink() and self.path.resolve()==self.path, 'journal directory drift')
        value,h=read_record(self.path/'STARTED.json')
        require(value==dict(state='STARTED',identity=self.identity) and h==self.start_sha,'STARTED drift')
    def row(self, slot, row, expected):
        require(type(slot) is int and 0<=slot<2*len(TASKS), 'slot')
        self.verify_started()
        return write_new(self.path/('%03d.json'%slot),dict(slot=slot,row=row,expected=expected))
    def read_row(self, slot):
        value,h=read_record(self.path/('%03d.json'%slot))
        require(value['slot']==slot, 'slot drift')
        return value,h
    def terminal(self, state, detail):
        return write_new(self.path/'TERMINAL.json',dict(state=state,detail=detail))

def _collect(journal, build, execute, *, clock=time.monotonic):
    """Internal orchestration only. Native adapter must verify independent STARTED archive first.

    build and execute are supplied by owner adapter; qualification injects fabricated
    data only. No build_registered import or default executor.
    """
    journal.verify_started()
    require(len(TASKS)==240 and len(set(TASKS))==240, 'schedule identity')
    # A retained Journal object must not allow a second collection either.
    # Reject partial evidence before invoking any input builder or worker.
    require({p.name for p in journal.path.iterdir()}=={'STARTED.json'}, 'prior collection or partial evidence')
    write_new(journal.path/'COLLECTING.json',dict(state='COLLECTING',started_sha256=journal.start_sha))
    start=clock(); deadline=start+TOTAL_SECONDS
    inputs={}; hashes=[]; expected={}
    try:
        for traced in (False,True):
            for task in TASKS:
                began=clock()
                require(began<deadline, 'aggregate deadline')
                held,phases=build(task)
                spec=expected_stream_identity(phases)
                group=(task[0],task[1],task[3])
                fingerprint=digest([held,phases])
                require(inputs.setdefault(group,fingerprint)==fingerprint, 'arm/pass input parity')
                if task[3]:
                    original=(task[0],task[1],task[2],False)
                    prior_held,prior_phases=build(original)
                    require(tuple(prior_held)==tuple(held), 'counterfactual held parity')
                    require(inputs[(task[0],task[1],False)]==digest([prior_held,prior_phases]), 'counterfactual original drift')
                    before,after=verify_counterfactual_inputs(prior_phases,phases)
                    require(before==expected[original] and after==spec, 'counterfactual stream drift')
                require(expected.setdefault(task,spec)==spec, 'expected digest drift')
                stop=min(deadline,began+PER_ARM_SECONDS)
                require(clock()<stop, 'generation deadline')
                row=execute(task,held,phases,traced,stop)
                elapsed=clock()-began
                require(elapsed<=PER_ARM_SECONDS and clock()<=deadline, 'task deadline')
                # Include generation and full worker evaluation time in task wall.
                row=dict(row,wall_seconds=elapsed)
                require(tuple(row[k] for k in ('seed','family','arm','alter_prior'))==task, 'worker task drift')
                require((row['stream_sha256'],row['c_trace_sha256'])==spec, 'worker input digest drift')
                require(row['cold_identity'] is False, 'premature cold identity')
                hashes.append(journal.row(len(hashes),row,spec))
        elapsed=clock()-start
        require(elapsed<=TOTAL_SECONDS and len(hashes)==480, 'aggregate budget or incomplete')
        journal.terminal('RAW_COMPLETE',dict(rows=len(hashes),elapsed_seconds=elapsed,row_hashes=hashes))
        return dict(rows=len(hashes),elapsed_seconds=elapsed,row_hashes=hashes)
    except Exception as exc:
        # If even this write fails, STARTED still prevents any replay.
        journal.terminal('FAILED_CONSUMED',dict(rows=len(hashes),error=type(exc).__name__,reason=str(exc)[:400]))
        raise

def _classify_readback(journal, archived_terminal_sha, archived_row_hashes):
    """Arithmetic after independently authenticated archive readback by native adapter."""
    journal.verify_started()
    terminal,sha=read_record(journal.path/'TERMINAL.json')
    require(sha==archived_terminal_sha and terminal['state']=='RAW_COMPLETE','raw archive unavailable')
    detail=terminal['detail']
    require(detail['rows']==480 and detail['row_hashes']==archived_row_hashes and len(archived_row_hashes)==480,'raw archive drift')
    first=[]; second=[]; expected={}
    for slot,hash_ in enumerate(archived_row_hashes):
        item,h=journal.read_row(slot)
        require(h==hash_, 'raw row drift')
        task=TASKS[slot%len(TASKS)]
        row=item['row']
        require(tuple(row[k] for k in ('seed','family','arm','alter_prior'))==task, 'archived task drift')
        spec=tuple(item['expected'])
        require(expected.setdefault(task,spec)==spec, 'archived input drift')
        require(row['cold_identity'] is False, 'premature cold claim')
        (first if slot<len(TASKS) else second).append(row)
    for a,b in zip(first,second):
        verify_pair(a,b)
    return classify(first,second,detail['elapsed_seconds'],expected)

if __name__=='__main__':
    raise SystemExit('NO_PRIMARY_CLI: native owner admission and independent archive adapter required')
