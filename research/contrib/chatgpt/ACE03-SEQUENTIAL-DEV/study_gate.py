"""Pre-data study accounting and classification. No primary execution entrypoint."""
import math
import sys
from contextlib import contextmanager
from transfer_study_eval import SEEDS, FAMILIES, ARMS, CONVENTIONAL

PER_ARM_SECONDS = 60
TOTAL_SECONDS = 14400  # shared across both passes and counterfactuals
CHECKPOINT_CAP = 16384
RSS_CAP = 268435456
TRACE_CAP = 1048576
EVENTS = 2816

# Pass 1 untraced timing, pass 2 independent instrumented repetition.
# Only related candidate/local-only counterfactual; same C stream, flipped A/B.
PRIMARY = tuple((s,f,a,False) for s in SEEDS for f in FAMILIES for a in ARMS)
COUNTERFACTUAL = tuple((s,'related',a,True) for s in SEEDS for a in ('candidate','local-only'))
TASKS = PRIMARY + COUNTERFACTUAL


def peak_rss_bytes():
    if sys.platform == 'win32':
        import ctypes
        from ctypes import wintypes
        class Counters(ctypes.Structure):
            _fields_ = [('cb',wintypes.DWORD),('PageFaultCount',wintypes.DWORD)] + [
                (n,ctypes.c_size_t) for n in ('PeakWorkingSetSize','WorkingSetSize',
                    'QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage','QuotaPeakNonPagedPoolUsage',
                    'QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage')]
        kernel = ctypes.WinDLL('kernel32',use_last_error=True)
        kernel.GetCurrentProcess.restype = wintypes.HANDLE
        psapi = ctypes.WinDLL('psapi',use_last_error=True)
        get = psapi.GetProcessMemoryInfo
        get.argtypes = [wintypes.HANDLE,ctypes.POINTER(Counters),wintypes.DWORD]
        get.restype = wintypes.BOOL
        data = Counters(); data.cb = ctypes.sizeof(data)
        if not get(kernel.GetCurrentProcess(),ctypes.byref(data),data.cb):
            raise OSError(ctypes.get_last_error(),'GetProcessMemoryInfo')
        return data.PeakWorkingSetSize
    if sys.platform.startswith('linux') or sys.platform == 'darwin':
        import resource
        scale = 1 if sys.platform == 'darwin' else 1024
        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * scale
    raise RuntimeError('unsupported RSS platform')


@contextmanager
def allocation_probe(enabled):
    """Conservative worker-wide traced Python allocations, not native RSS."""
    import tracemalloc
    if type(enabled) is not bool or tracemalloc.is_tracing():
        raise ValueError('invalid trace state')
    result = {'traced_peak_bytes': None, 'peak_rss_bytes': None}
    if enabled:
        tracemalloc.start(1)
    try:
        yield result
    finally:
        if enabled:
            result['traced_peak_bytes'] = tracemalloc.get_traced_memory()[1]
            tracemalloc.stop()
        result['peak_rss_bytes'] = peak_rss_bytes()


def key(row):
    return (row['seed'],row['family'],row['arm'],row['alter_prior'])


def number(x,lo,hi):
    return type(x) in (int,float) and math.isfinite(x) and lo<=x<=hi


def valid_digest(s):
    return isinstance(s,str) and len(s)==64 and all(c in '0123456789abcdef' for c in s)


def index(rows, traced):
    out = {}
    for row in rows:
        k = key(row)
        if k not in TASKS or k in out or type(k[3]) is not bool:
            raise ValueError('task identity or duplicate')
        if row['cursor'] != EVENTS or row['cold_identity'] is not True:
            raise ValueError('event count or cold identity')
        if not number(row['wall_seconds'],0,PER_ARM_SECONDS):
            raise ValueError('arm wall budget')
        if not number(row['compute_seconds'],0,row['wall_seconds']):
            raise ValueError('compute accounting')
        if not number(row['peak_rss_bytes'],1,RSS_CAP):
            raise ValueError('worker RSS budget')
        if traced:
            if not number(row['traced_peak_bytes'],1,TRACE_CAP):
                raise ValueError('trace budget')
        elif row['traced_peak_bytes'] is not None:
            raise ValueError('timing pass must be untraced')
        for field in ('c_final','c_cold','c_early','balanced_null_brier'):
            if not number(row[field],0,1):
                raise ValueError('Brier range')
        if len(row['a_boundaries'])!=4 or any(not number(v,0,1) for v in row['a_boundaries']):
            raise ValueError('retention boundaries')
        if len(row['checkpoint_boundaries'])!=4:
            raise ValueError('checkpoint boundaries')
        for cp in row['checkpoint_boundaries']:
            if not number(cp['bytes'],1,CHECKPOINT_CAP) or not valid_digest(cp['sha256']):
                raise ValueError('checkpoint budget or digest')
        if row['unknown_abstentions']!=1 or row['unknown_prediction']!=[.5]*4:
            raise ValueError('unknown input parity')
        if not all(valid_digest(row[f]) for f in ('stream_sha256','c_trace_sha256','c_forecast_sha256')):
            raise ValueError('C evidence digest')
        out[k]=row
    if set(out)!=set(TASKS):
        raise ValueError('missing task evidence')
    return out


DETERMINISTIC = ('cursor','cold_identity','c_final','c_cold','c_early',
                 'balanced_null_brier','a_boundaries','checkpoint_boundaries',
                 'unknown_abstentions','unknown_prediction','stream_sha256','c_trace_sha256','c_forecast_sha256')


def classify(first, second, elapsed_seconds):
    """Arithmetic only. Cannot establish owner admission, custody or science."""
    try:
        if not number(elapsed_seconds,0,TOTAL_SECONDS):
            raise ValueError('total wall budget')
        a,b = index(first,False),index(second,True)
        if sum(r['wall_seconds'] for r in first+second)>elapsed_seconds:
            raise ValueError('elapsed time inconsistent with sequential execution')
        if any(a[k][f]!=b[k][f] for k in TASKS for f in DETERMINISTIC):
            raise ValueError('deterministic reproduction mismatch')
        failures=[]; gains=[]; ratios=[]; influence=[]
        for s in SEEDS:
            get=lambda f,n,x=False:a[(s,f,n,x)]
            for f in FAMILIES:
                if len({get(f,n)['stream_sha256'] for n in ARMS})!=1:
                    raise ValueError('arm input parity')
            if len({get('related',n,True)['stream_sha256'] for n in ('candidate','local-only')})!=1:
                raise ValueError('counterfactual input parity')
            cand=get('related','candidate')
            winner=min(CONVENTIONAL,key=lambda n:get('related',n)['c_final'])
            ctrl=get('related',winner)
            gain=ctrl['c_final']-cand['c_final']; gains.append(gain)
            if ctrl['compute_seconds']<=0:
                raise ValueError('invalid comparator timing')
            ratio=cand['compute_seconds']/ctrl['compute_seconds']; ratios.append(ratio)
            if ratio>2:
                raise ValueError('candidate exceeds compute match')
            for f in ('related','conflicting_C'):
                boundaries=get(f,'candidate')['a_boundaries']
                if max(boundaries)-boundaries[0]>.02:
                    failures.append((s,f,'retention'))
            for f in ('null','unobservable_AB_alias'):
                if get(f,'candidate')['balanced_null_brier']>.252:
                    failures.append((s,f,'null/alias'))
            if get('conflicting_C','candidate')['c_final']-get('conflicting_C','local-only')['c_final']>.02:
                failures.append((s,'conflicting_C','negative transfer'))
            for n in ('candidate','local-only'):
                if get('related',n)['c_trace_sha256']!=get('related',n,True)['c_trace_sha256']:
                    raise ValueError('counterfactual changed C stream')
            if any(get('related','local-only')[f]!=get('related','local-only',True)[f]
                   for f in ('c_final','c_forecast_sha256')):
                raise ValueError('local-only counterfactual independence')
            influence.append(get('related','candidate')['c_forecast_sha256'] !=
                             get('related','candidate',True)['c_forecast_sha256'])
            if gain<=0:
                failures.append((s,'related','paired gain'))
        mean=math.fsum(gains)/len(gains)
        if mean<.005:
            failures.append(('aggregate','related','mean gain'))
        return {'arithmetic_disposition':'DEV_NO_GO' if failures else 'DEV_PASS_CONDITIONAL',
                'failures':failures,'mean_gain':mean,'seed_gains':gains,'compute_ratios':ratios,
                'counterfactual_candidate_influenced':influence, 'scientific_gain_verified':False}
    except (KeyError,TypeError,ValueError,OverflowError) as exc:
        return {'arithmetic_disposition':'INVALID','reason':str(exc),'scientific_gain_verified':False}
