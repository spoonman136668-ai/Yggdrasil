"""DWSA-04: frozen 320-byte nonlinear recipient from stored weights (DEV only).

No donor forward calls, original-world first use, canonical learner mutations or
independent heldout evaluation. Implements DWSA-04-PROTOCOL.md.
"""
from __future__ import annotations
import hashlib, json, math, struct, sys, time
from pathlib import Path
from dwsa02 import DIMS, ZIP_SHA, STATE_SHA, compile_routes, read_archive, restore, gauge, algebraic_route
from dwsa03 import PREFIX, encode, fixture_records, fit_linear, init_head, pack_rows, predict, reference_prevalence, score_series

HEADS = ('action_transition','action_reward','temporal_transition','temporal_reward')
LEVELS = (-3, -1, 1, 3)

def require(ok, reason):
    if not ok: raise ValueError('DWSA04_REJECT_'+reason)

def pair_scale(values, divisor):
    raw = max(abs(x) for x in values)/divisor or 1.0
    bits = struct.pack('>e', raw)
    scale = struct.unpack('>e', bits)[0]
    require(math.isfinite(scale) and scale > 0, 'INVALID_SCALE')
    return bits, scale

def compile_student(heads):
    require(len(heads)==4, 'HEAD_COUNT')
    scales=bytearray(); enc=[]; pred=[]; eb=[]; pb=[]
    for i,h in enumerate(heads):
        require(len(h['encoder'])==8 and all(len(r)==DIMS[i] for r in h['encoder'])
                and len(h['encoder_bias'])==8 and len(h['predictor'])==2
                and all(len(r)==8 for r in h['predictor'])
                and len(h['predictor_bias'])==2, 'SOURCE_SHAPE')
        E=[v for row in h['encoder'] for v in row]
        P=[v for row in h['predictor'] for v in row]
        require(all(type(v) is float and math.isfinite(v) for v in E+P+h['encoder_bias']+h['predictor_bias']), 'SOURCE_VALUES')
        es,e=pair_scale(E,3); ps,p=pair_scale(P,7); scales.extend(es+ps)
        enc.extend(min(range(4),key=lambda j:(abs(x-LEVELS[j]*e),abs(LEVELS[j]),j)) for x in E)
        pred.extend(max(-7,min(7,round(x/p)))+7 for x in P)
        eb.extend(max(-127,min(127,round(x/e))) for x in h['encoder_bias'])
        pb.extend(max(-127,min(127,round(x/p))) for x in h['predictor_bias'])
    require((len(enc),len(pred),len(eb),len(pb))==(768,64,32,8), 'PARAM_COUNT')
    body=(b'DWN4\x01\x00\x00\x00'+bytes(scales)
          +bytes(sum(enc[i+j] << (6-2*j) for j in range(4)) for i in range(0,768,4))
          +bytes((pred[i]<<4)|pred[i+1] for i in range(0,64,2))
          +struct.pack('>32b',*eb)+struct.pack('>8b',*pb))
    require(len(body)==288, 'BODY_BYTES')
    return body+hashlib.sha256(body).digest()

def restore_student(raw):
    require(type(raw) is bytes and len(raw)==320, 'SIZE')
    body=raw[:288]
    require(body[:8]==b'DWN4\x01\x00\x00\x00' and hashlib.sha256(body).digest()==raw[288:], 'HEADER_OR_HASH')
    scales=[]
    for i in range(4):
        e,p=struct.unpack('>ee',body[8+4*i:12+4*i])
        require(math.isfinite(e) and e>0 and math.isfinite(p) and p>0, 'SCALE')
        scales.append((e,p))
    es=[(v>>shift)&3 for v in body[24:216] for shift in (6,4,2,0)]
    ps=[q for v in body[216:248] for q in (v>>4,v&15)]
    require(len(es)==768 and len(ps)==64 and all(q<15 for q in ps), 'P_ENCODING')
    eb=struct.unpack('>32b',body[248:280]); pb=struct.unpack('>8b',body[280:288])
    result=[];ei=pi=bi=qi=0
    for i,d in enumerate(DIMS):
        e,p=scales[i]
        E=[LEVELS[q]*e for q in es[ei:ei+8*d]];ei+=8*d
        P=[(q-7)*p for q in ps[pi:pi+16]];pi+=16
        B=[q*e for q in eb[bi:bi+8]];bi+=8
        Q=[q*p for q in pb[qi:qi+2]];qi+=2
        result.append((tuple(tuple(E[j*d:(j+1)*d]) for j in range(8)),tuple(B),
                       tuple(tuple(P[k*8:(k+1)*8]) for k in range(2)),tuple(Q)))
    return tuple(result)

def predict_student(head, features):
    E,B,P,Q=head
    z=[]
    for view in features:
        hidden=[math.tanh(math.fsum(w*x for w,x in zip(e,view))+b) for e,b in zip(E,B)]
        outs=[math.fsum(w*x for w,x in zip(p,hidden))+q for p,q in zip(P,Q)]
        z.append(outs[0]-outs[1])
    v=math.fsum(z)
    if v>=0: return 1/(1+math.exp(-v))
    t=math.exp(v);return t/(1+t)

def evaluate(path):
    start=time.perf_counter()
    state,heads=read_archive(Path(path))  # verifies exact ZIP/state SHA, no model imports
    episodes=fixture_records(state)       # engineering fixture, already trained upon
    raw=compile_student(heads)
    require(len(raw)==320 and raw==compile_student(heads), 'DUPLICATE')
    candidate=restore_student(raw)
    require(all(restore_student(bytes(raw))==candidate for _ in range(3)), 'COLD_RESTORES')
    corrupted=bytearray(raw);corrupted[60]^=1
    try: restore_student(bytes(corrupted))
    except ValueError: pass
    else: raise ValueError('DWSA04_REJECT_BYTE_CORRUPTION')
    records=[[] for _ in range(4)]
    for j,row in enumerate(episodes):
        for i in range(4):
            records[i].append((encode(row,episodes[max(0,j-8):j],i),row[3 if i%2==0 else 5]))
    trained=restore(compile_routes(heads))
    initial=restore(pack_rows(tuple(algebraic_route(init_head(i)) for i in range(4))))
    results={}; gauge_cases=0; max_gauge_error=0.0; passed=0
    for i,name in enumerate(HEADS):
        data=tuple(records[i]);late=data[PREFIX:];labels=tuple(y for _,y in late)
        fitted_route=fit_linear(data,i)
        fitted_rows=tuple(fitted_route if j==i else tuple(0.0 for _ in trained[j]) for j in range(4))
        fitted=restore(pack_rows(fitted_rows))[i]
        for seed in (101,202,303):
            hs=tuple(gauge(heads[j],seed) if j==i else heads[j] for j in range(4))
            variant=restore_student(compile_student(hs))[i]
            delta=max(abs(predict_student(variant,x)-predict_student(candidate[i],x)) for x,_ in data[:8])
            max_gauge_error=max(max_gauge_error,delta);gauge_cases+=1
        metrics={
          'nonlinear_320b':score_series(labels,tuple(predict_student(candidate[i],x) for x,_ in late))['brier'],
          'affine_320b':score_series(labels,tuple(predict(trained[i],x) for x,_ in late))['brier'],
          'fitted_logistic_320b':score_series(labels,tuple(predict(fitted,x) for x,_ in late))['brier'],
          'untrained_initializer_320b':score_series(labels,tuple(predict(initial[i],x) for x,_ in late))['brier'],
          'constant_half':score_series(labels,(0.5,)*len(late))['brier'],
          'prefix_prevalence':score_series(labels,(reference_prevalence(episodes,i),)*len(late))['brier'],
        }
        threshold=metrics['nonlinear_320b']+0.01<=min(metrics['affine_320b'],metrics['fitted_logistic_320b'])
        passed+=int(threshold)
        results[name]={'scores':metrics,'delta_over_affine':metrics['affine_320b']-metrics['nonlinear_320b'],
                       'delta_over_logistic':metrics['fitted_logistic_320b']-metrics['nonlinear_320b'],
                       'threshold_met':threshold,'late_training_rechecks':len(late)}
    require(gauge_cases==12 and max_gauge_error<=1e-10, 'GAUGE')
    macro={metric:sum(x['scores'][metric] for x in results.values())/4 for metric in next(iter(results.values()))['scores']}
    return {'schema':'dwsa04.nonlinear_recipient.dev.v1','source_zip_sha256':ZIP_SHA,
            'source_state_sha256':STATE_SHA,'source_mode':'engineering_fixture_only',
            'teacher_forward_passes':0,'original_world_actions':0,'independently_heldout':False,
            'native_checkpoint_bytes':len(raw),'checkpoint_sha256':hashlib.sha256(raw).hexdigest(),
            'cold_restores':3,'gauge_cases':gauge_cases,'max_gauge_probability_error':max_gauge_error,
            'checksum_corruption_rejected':True,'dev_signal_heads_passed':passed,
            'decision':'DWSA04_DEV_SCREEN_PASS_ONLY' if passed==4 else 'DWSA04_DEV_NO_GO',
            'scientific':'UNVERIFIED','deployment':'NONE','macro_brier':macro,'per_head':results,
            'local_wall_seconds':time.perf_counter()-start}

if __name__=='__main__':
    require(len(sys.argv)==2,'ZIP_ARGUMENT')
    print(json.dumps(evaluate(Path(sys.argv[1])),sort_keys=True,indent=2))
