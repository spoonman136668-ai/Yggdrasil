"""DWSA-03: descriptive offline fixed-footprint functional-signal diagnostic.

PREREG 037557374badeefa76bb122ceaae1f369f2e095c.
Reads a pre-consumed engineering fixture only. No source actor or donor inference.
"""
from __future__ import annotations

import hashlib
import json
import math
try:
    import resource
except ImportError:
    resource = None
import struct
import sys
import time
from pathlib import Path

from dwsa02 import (
    DIMS, BODY_BYTES, NATIVE_BYTES, ZIP_SHA, STATE_SHA, MAGIC,
    algebraic_route, compile_routes, read_archive, restore, sha,
)

EPISODES = 1025
PREFIX = 820
BATCH_STEPS = 200
LR = 0.1
L2 = 0.001
HEADS = 4


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError('DWSA03_REJECT_' + reason)


def bit(v: object) -> int:
    require(type(v) is int and v in (0, 1), 'PUBLIC_BIT')
    return v


def fixture_records(raw_state: dict) -> tuple:
    require(raw_state['schema'] == 'yggdrasil.ckad.native-causal-amalgam.v1', 'TOP_SCHEMA')
    nested = json.loads(raw_state['native_ascii'])
    require(nested['source_mode'] == 'engineering_fixture_only' and
            nested['accepted_native'] is False and
            nested['scientific_pass'] is False, 'SOURCE_MODE')
    readout = json.loads(nested['experience_ascii'])
    require(readout['schema'] == 'yggdrasil.ckad.native-episode-experience.v6',
            'EPISODE_SCHEMA')
    records = readout['episodes']
    require(type(records) is list and len(records) == EPISODES, 'EPISODE_COUNT')
    ids = set()
    frozen = []
    for row in records:
        require(type(row) is list and len(row) == 6 and
                type(row[0]) is str and len(row[0]) == 64 and
                all(c in '0123456789abcdef' for c in row[0]) and
                row[0] not in ids, 'EPISODE_ID')
        ids.add(row[0])
        views = row[1]
        require(type(views) is list and len(views) == 2 and
                all(type(v) is list and len(v) == 2 for v in views), 'PUBLIC_VIEWS')
        for v in views:
            for x in v:
                bit(x)
        for x in row[2:]:
            bit(x)
        frozen.append((row[0], tuple(tuple(v) for v in views), *row[2:]))
    return tuple(frozen)


def encode(row: tuple, previous: tuple, head: int) -> tuple:
    _, views, x1, s2, x2, y = row
    temporal = head >= 2
    transition = head in (0, 2)
    extras = (x1,) if transition else (x1, s2, x2)
    out = []
    past = previous[-8:]
    for view in views:
        v = [2*bit(q)-1 for q in (*view, *extras)]
        if temporal:
            for age in range(8):
                if age < len(past):
                    _, pv, px1, ps2, px2, py = past[-age-1]
                    scale = 1.0/(age+1)
                    v.extend((
                        scale*(1 if pv[0][0] == view[0] else -1),
                        scale*(1 if px1 == extras[0] else -1),
                        scale*(2*ps2-1), scale*(2*px2-1), scale*(2*py-1),
                    ))
                else:
                    v.extend((0.0,)*5)
        require(len(v) == DIMS[head], 'FEATURE_DIMENSION')
        out.append(tuple(v))
    return tuple(out)


def init_head(index: int) -> dict:
    d = DIMS[index]
    salt = (3, 7, 13, 17)[index]
    scale = 0.075 if index < 2 else 0.055
    if index < 2:
        e = [[scale*math.sin((j+1)*(i+2)*(salt+1)) for i in range(d)] for j in range(8)]
        p = [[scale*math.cos((k+1)*(j+2)*(salt+3)) for j in range(8)] for k in range(2)]
    else:
        e = [[scale*math.sin((j+2)*(i+1)*(salt+1)) for i in range(d)] for j in range(8)]
        p = [[scale*math.cos((k+2)*(j+1)*(salt+2)) for j in range(8)] for k in range(2)]
    return {'encoder':e, 'encoder_bias':[0.0]*8, 'predictor':p,
            'predictor_bias':[0.0]*2}


def pack_rows(routes: tuple[tuple[float, ...], ...]) -> bytes:
    require(len(routes) == HEADS and all(len(row)==2*DIMS[i]+2 for i,row
                                        in enumerate(routes)), 'ROUTE_ROSTER')
    body = bytearray(MAGIC + b'\x01' + bytes(DIMS))
    scales = []
    quantized = []
    for row in routes:
        require(all(math.isfinite(v) for v in row), 'NONFINITE_ROUTE')
        scale = max(map(abs,row))/127 or 1.0
        require(math.isfinite(scale) and scale > 0, 'BAD_SCALE')
        scales.append(scale)
        quantized.extend(max(-127,min(127,round(v/scale))) for v in row)
    require(len(quantized)==200,'PACK_COUNT')
    for s in scales:
        body.extend(struct.pack('>d',s))
    body.extend(struct.pack('>200b',*quantized))
    body.extend(bytes(BODY_BYTES-len(body)))
    require(len(body)==BODY_BYTES,'PACK_SIZE')
    raw=bytes(body)+hashlib.sha256(body).digest()
    require(len(raw)==NATIVE_BYTES,'NATIVE_BYTES')
    return raw


def predict(route: tuple, features: tuple) -> float:
    d=len(features[0])
    a=route[:d]
    b=route[d:2*d]
    bias=route[2*d]-route[2*d+1]
    z=math.fsum(math.fsum((v-u)*x for v,u,x in zip(a,b,view))
                for view in features)/len(features)+bias
    value=2*z
    if value >= 0:
        return 1.0/(1.0+math.exp(-value))
    t=math.exp(value)
    return t/(1.0+t)


def reference_prevalence(data: tuple, head: int) -> float:
    positives=sum(row[3 if head in (0,2) else 5] for row in data[:PREFIX])
    return (positives+1)/(PREFIX+2)


def fit_linear(data: tuple, head: int) -> tuple[float,...]:
    """Independent, prefix-only, controlled directly fitted logistic model."""
    d=DIMS[head]
    samples=[]
    for feats,label in data[:PREFIX]:
        x=tuple((a+b)*0.5 for a,b in zip(*feats))
        samples.append((x,label))
    w=[0.0]*d
    bias=0.0
    for _ in range(BATCH_STEPS):
        grad=[0.0]*d
        gb=0.0
        for x,y in samples:
            z=2*(math.fsum(w[i]*x[i] for i in range(d))+bias)
            if z >= 0:
                p=1/(1+math.exp(-z))
            else:
                t=math.exp(z)
                p=t/(1+t)
            error=2*(p-y)
            gb+=error
            for i in range(d):
                grad[i]+=error*x[i]
        for i in range(d):
            w[i]-=LR*(grad[i]/PREFIX+L2*w[i])
        bias-=LR*gb/PREFIX
    return tuple(w[i]/2 for i in range(d))+tuple(-w[i]/2 for i in range(d))+(bias/2,-bias/2)


def score_series(rows: tuple, probabilities: tuple) -> dict:
    require(len(rows)==len(probabilities), 'SCORE_LENGTH')
    brier=math.fsum((p-y)**2 for p,y in zip(probabilities, rows))/len(rows)
    logloss=-math.fsum(y*math.log(max(1e-12,min(1-1e-12,p))) +
                           (1-y)*math.log(max(1e-12,min(1-1e-12,1-p)))
                           for p,y in zip(probabilities,rows))/len(rows)
    accuracy=sum((int(p>0.5)==y) for p,y in zip(probabilities,rows))/len(rows)
    return {'brier':brier, 'logloss':logloss, 'accuracy':accuracy}


def evaluate(path: Path) -> dict:
    started=time.perf_counter()
    state,heads=read_archive(path)  # verifies SHA; no native model import / restore
    episodes=fixture_records(state)
    trained_raw=compile_routes(heads)
    trained=restore(trained_raw)
    exact=tuple(algebraic_route(h) for h in heads)
    initial=restore(pack_rows(tuple(algebraic_route(init_head(i)) for i in range(4))))
    sham_heads=[]
    for h in heads:
        sham_heads.append({**h,'predictor':[row[1:]+row[:1] for row in h['predictor']]})
    sham=restore(pack_rows(tuple(algebraic_route(h) for h in sham_heads)))
    data=[[] for _ in range(4)]
    for pos,row in enumerate(episodes):
        for head in range(4):
            label=row[3] if head in (0,2) else row[5]
            data[head].append((encode(row,episodes[max(0,pos-8):pos],head),label))
    results={}
    minimum_delta=0.01
    all_strong=True
    for i in range(4):
        records=tuple(data[i])
        fitted=fit_linear(records,i)
        fitted_rows=tuple(fitted if k==i else tuple(0.0 for _ in exact[k])
                          for k in range(4))
        fitted=restore(pack_rows(fitted_rows))[i]
        late=records[PREFIX:]
        labels=tuple(y for x,y in late)
        route_cases={
            'compiled_trained':trained[i],
            'exact_weight_algebra':exact[i],
            'untrained_same_arch_init':initial[i],
            'readout_shuffled_sham':sham[i],
            'prefix_fitted_logistic_320b':fitted,
        }
        metrics={name:score_series(labels,tuple(predict(route,x) for x,y in late))
                 for name,route in route_cases.items()}
        control_p=reference_prevalence(episodes,i)
        metrics['constant_prefix_laplace']=score_series(labels,(control_p,)*len(late))
        metrics['zero_half']=score_series(labels,(0.5,)*len(late))
        c=metrics['compiled_trained']['brier']
        delta0=metrics['zero_half']['brier']-c
        delta1=metrics['constant_prefix_laplace']['brier']-c
        signal=(delta0>=minimum_delta and delta1>=minimum_delta)
        all_strong=all_strong and signal
        results[('action_transition','action_reward','temporal_transition',
                 'temporal_reward')[i]]={
            'labels_in_late_training_recheck':len(late),
            'late_positive_count':sum(labels),
            'prefix_positive_count':sum(y for x,y in records[:PREFIX]),
            'metrics':metrics,
            'brier_delta_over_half':delta0,
            'brier_delta_over_prefix_prevalence':delta1,
            'frozen_signal_threshold_met':signal,
        }
    macro={name:sum(results[key]['metrics'][name]['brier'] for key in results)/4
           for name in results['action_transition']['metrics']}
    elapsed=time.perf_counter()-started
    return {
        'schema':'dwsa03.retro_training_reuse.v1',
        'pre_score_protocol_commit':'037557374badeefa76bb122ceaae1f369f2e095c',
        'source_zip_sha256':ZIP_SHA,'source_state_sha256':STATE_SHA,
        'source_mode':'engineering_fixture_only', 'episode_count':EPISODES,
        'prefix_fit_count':PREFIX,'late_training_recheck_count':EPISODES-PREFIX,
        'independently_heldout':False,'source_first_use':False,
        'teacher_forward_passes':0,'new_original_world_actions':0,
        'native_checkpoint_bytes':len(trained_raw),
        'baseline_training_steps':BATCH_STEPS,
        'scientific':'UNVERIFIED','deployment':'NONE',
        'decision':('RETROSPECTIVE_SIGNAL_DEV_PASS_ONLY' if all_strong else
                    'RETROSPECTIVE_SIGNAL_NO_GO'),
        'per_head':results, 'macro_brier':macro,
        'runtime_wall_seconds_local_diagnostic':elapsed,
        'peak_rss_kib_linux':(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                              if resource is not None and sys.platform.startswith('linux')
                              else None),
    }


if __name__=='__main__':
    require(len(sys.argv)==2,'USAGE_ZIP_PATH')
    print(json.dumps(evaluate(Path(sys.argv[1])),indent=2,sort_keys=True))
