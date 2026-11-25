"""Bounded explicit-event worker and two-pass orchestration library.

No primary CLI, source authority, or dispatch. Only the supervisor builds
registered inputs; the worker accepts public events and evaluator laws.
First pass: uninterrupted. Second pass: fresh child at each phase boundary.
"""
import base64
import hashlib
import json
import math
import subprocess
import sys
import time
from pathlib import Path

from transfer_study_eval import (ARMS, make_arm, forecast, checkpoint, split,
    events, probability_tenths, expected_brier)
from study_gate import (TASKS, PER_ARM_SECONDS, TOTAL_SECONDS, allocation_probe,
    peak_rss_bytes, DETERMINISTIC, classify, RSS_CAP, TRACE_CAP)

MAX_REQUEST = 262144
MAX_REPLY = 262144


def encode(x):
    return json.dumps(x, separators=(',', ':'), sort_keys=True, allow_nan=False).encode('ascii')


def digest(x):
    return hashlib.sha256(encode(x)).hexdigest()


def readout_digest(model, held):
    return digest([forecast(model,k,p) for k in range(3) for p in held])


def law_score(model,key,held,law):
    return expected_brier(model,key,held,lambda p,j: law[p][j])[0]


def worker(req):
    """Execute at most four explicit phases. No external inputs or child processes."""
    start = time.perf_counter()
    arm,seed,traced = req['arm'],req['seed'],req['traced']
    held = tuple(req['held'])
    if arm not in ARMS or type(seed) is not int or not 0<=seed<2**32 or type(traced) is not bool:
        raise ValueError('worker identity')
    if not 1<=len(held)<=128 or len(set(held))!=len(held) or any(type(p) is not int or not 0<=p<512 for p in held):
        raise ValueError('held patterns')
    phases = req['phases']
    if not 1<=len(phases)<=4 or sum(len(p['events']) for p in phases)>2816:
        raise ValueError('event budget')
    indices = [p['phase'] for p in phases]
    if indices!=list(range(indices[0],indices[0]+len(indices))) or not 0<=indices[0]<=indices[-1]<=3:
        raise ValueError('phase order')
    if any(not 1<=len(p['events'])<=(1024,1024,512,256)[p['phase']] for p in phases):
        raise ValueError('phase budget')
    reports = []
    # Trace the complete worker-side model/evaluator allocation, not just checkpoint bytes.
    with allocation_probe(traced) as mem:
        model = make_arm(arm,seed)
        raw = req['checkpoint']
        if raw is not None:
            raw = base64.b64decode(raw,validate=True)
            if len(raw)>16384:
                raise ValueError('checkpoint size')
            restored = type(model).restore(raw)
            if hasattr(model,'mode') and (restored.mode,restored.seed)!=(model.mode,model.seed):
                raise ValueError('control identity')
            model = restored
            if checkpoint(model)!=raw or readout_digest(model,held)!=req['expected_before']:
                raise ValueError('cold restore identity')
        elif indices[0]!=0 or req['expected_before'] is not None:
            raise ValueError('missing predecessor')
        if model.cursor!=req['expected_cursor']:
            raise ValueError('initial cursor')
        for p in phases:
            phase = p['phase']
            laws = {}
            for name in ('a_law','c_law'):
                table = p[name]
                if len(table)!=len(held) or any(len(row)!=4 or any(type(v) is not int or v not in (1,5,9) for v in row) for row in table):
                    raise ValueError('law shape')
                laws[name] = dict(zip(held,table))
            cold = law_score(model,2,held,laws['c_law']) if phase==3 else None
            early = []
            stream = hashlib.sha256()
            for k,pat,y in p['events']:
                if pat in held:
                    raise ValueError('held leakage')
                q,_ = forecast(model,k,pat)
                stream.update(encode([k,pat,y])+b'\n')
                if phase==3:
                    early.append(math.fsum((a-b)**2 for a,b in zip(q,y))/4)
                model.observe(model.cursor,k,pat,tuple(y))
            raw = checkpoint(model)
            report = dict(phase=phase, cursor=model.cursor, stream_sha256=stream.hexdigest(),
                a_brier=law_score(model,0,held,laws['a_law']),
                readout_sha256=readout_digest(model,held),
                checkpoint=dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
            if phase==3:
                q,abstain=forecast(model,None,held[0])
                report.update(c_cold=cold,c_early=math.fsum(early)/len(early),
                    c_final=law_score(model,2,held,laws['c_law']),
                    balanced_null_brier=expected_brier(model,p['negative_key'],held,lambda pat,j:5)[0],
                    c_forecast_sha256=digest([forecast(model,2,pat) for pat in held]),
                    unknown_abstentions=abstain,unknown_prediction=list(q))
            reports.append(report)
        result = dict(reports=reports,checkpoint=base64.b64encode(raw).decode('ascii'))
    result.update(mem,compute_seconds=time.perf_counter()-start)
    return result


def child(req, timeout):
    payload=encode(req)
    if len(payload)>MAX_REQUEST or not 0<timeout<=PER_ARM_SECONDS:
        raise ValueError('request or time budget')
    # Direct child only; subprocess.run kills/waits on timeout, no grandchildren.
    p=subprocess.run([sys.executable,'-B',str(Path(__file__).resolve()),'--explicit-worker'],
                     input=payload,capture_output=True,timeout=timeout,check=True)
    if len(p.stdout)>MAX_REPLY:
        raise ValueError('reply budget')
    return json.loads(p.stdout)


def execute_explicit(task,held,phases,traced,deadline):
    """One explicit task; fresh subprocess per phase only in traced pass."""
    start=time.monotonic()
    seed,family,arm,alter=task
    if type(traced) is not bool or len(phases)!=4:
        raise ValueError('task shape')
    reports=[]; raw=None; prior=None; cursor=0; compute=0.; rss=0; trace=0
    groups=[[p] for p in phases] if traced else [phases]
    for group in groups:
        remaining=min(deadline,start+PER_ARM_SECONDS)-time.monotonic()
        if remaining<=0:
            raise TimeoutError('task budget')
        out=child(dict(arm=arm,seed=seed,traced=traced,held=held,phases=group,
                       checkpoint=raw,expected_before=prior,expected_cursor=cursor),remaining)
        if [p['phase'] for p in out['reports']]!=[p['phase'] for p in group]:
            raise ValueError('worker phase identity')
        for report,spec in zip(out['reports'],group):
            cursor+=len(spec['events'])
            if report['cursor']!=cursor:
                raise ValueError('worker cursor')
        reports.extend(out['reports']); raw=out['checkpoint']; prior=reports[-1]['readout_sha256']
        compute+=out['compute_seconds']; rss=max(rss,out['peak_rss_bytes'])
        if traced: trace=max(trace,out['traced_peak_bytes'])
        elif out['traced_peak_bytes'] is not None: raise ValueError('trace mismatch')
    final=reports[-1]
    # Parent peak + largest child peak is a conservative bound, not simultaneous RSS.
    rss+=peak_rss_bytes()
    wall=time.monotonic()-start
    if rss>RSS_CAP or (traced and trace>TRACE_CAP) or wall>PER_ARM_SECONDS:
        raise ValueError('resource cap')
    row=dict(seed=seed,family=family,arm=arm,alter_prior=alter,cursor=cursor,
             cold_identity=False,wall_seconds=wall,compute_seconds=compute,
             peak_rss_bytes=rss,traced_peak_bytes=trace if traced else None,
             a_boundaries=[r['a_brier'] for r in reports],
             checkpoint_boundaries=[r['checkpoint'] for r in reports],
             readout_boundaries=[r['readout_sha256'] for r in reports],
             stream_sha256=digest([r['stream_sha256'] for r in reports]),
             c_trace_sha256=final['stream_sha256'])
    row.update({k:final[k] for k in ('c_cold','c_early','c_final','balanced_null_brier',
        'c_forecast_sha256','unknown_abstentions','unknown_prediction')})
    return row


def build_registered(task):
    """Evaluator-only source generation. Call only after native run admission."""
    if task not in TASKS:
        raise ValueError('registered task identity')
    seed,family,arm,alter=task
    train,held=split(seed)
    phases=[]
    for phase in range(4):
        laws={name:[[probability_tenths(seed,family,target,p,j) for j in range(4)] for p in held]
              for name,target in [('a_law',0),('c_law',3)]}
        phases.append(dict(phase=phase,events=list(events(seed,family,phase,train,alter_prior=alter)),
                           negative_key=0 if family=='unobservable_AB_alias' else 2,**laws))
    return held,phases


def verify_pair(first,second):
    """Only a matching independent cold pass may mark cold_identity true."""
    fields=tuple(f for f in DETERMINISTIC if f!='cold_identity')+('readout_boundaries',)
    if any(first[k]!=second[k] for k in ('seed','family','arm','alter_prior')+fields):
        raise ValueError('uninterrupted vs cold reproduction mismatch')
    first['cold_identity']=second['cold_identity']=True


def execute_registered_task(task,traced,deadline):
    """Library entry only; native admission, prereg/source locks required externally."""
    start=time.monotonic()
    held,phases=build_registered(task)
    row=execute_explicit(task,held,phases,traced,min(deadline,start+PER_ARM_SECONDS))
    row['wall_seconds']=time.monotonic()-start
    if row['wall_seconds']>PER_ARM_SECONDS or time.monotonic()>deadline:
        raise TimeoutError('task including generation budget')
    return row


if __name__=='__main__':
    if sys.argv[1:]!=['--explicit-worker']:
        raise SystemExit('no primary CLI; native admission required')
    data=sys.stdin.buffer.read(MAX_REQUEST+1)
    if len(data)>MAX_REQUEST:
        raise ValueError('request budget')
    result=encode(worker(json.loads(data)))
    if len(result)>MAX_REPLY:
        raise ValueError('reply budget')
    sys.stdout.buffer.write(result)
