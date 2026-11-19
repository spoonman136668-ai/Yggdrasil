"""Independent raw-state/weight audit: no native or solver imports."""
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import sys
import time

HERE=Path(__file__).resolve().parent


def canon(d):return json.dumps(d,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode('ascii')
def sha(b):return hashlib.sha256(b).hexdigest()
def need(ok,why):
    if not ok:raise RuntimeError('CKAD14_INDEPENDENT_'+why)


def sparse_reader(raw):
    d=json.loads(raw);info=d['info'];bits=d['context_bits'];count=1<<(bits+1)
    values=struct.unpack('<'+'f'*count,bytes.fromhex(d['weights_float32_le']))
    need(all(v in (0.,1.) for v in values),'WEIGHTS_BINARY')
    terms=[t for t,v in enumerate(values) if v==1.]
    need(len(terms)<=8 and len(terms)==info['active_weights'],'WEIGHT_CAPACITY')
    eligible=info['solver_status']==0 and info['fit_errors']==info['calibration_errors']==0
    need(eligible==info['eligible'],'ADMISSION')
    return lambda x:sum((x&t)==t for t in terms)%2 if eligible else None


def state_readers(d,legacy):
    src=json.loads(d['source_ascii']);basis=json.loads(src['native_basis_ascii']);bits=basis['context_bits']
    base=[legacy.reader(p,bits) for p in basis['profiles']];hyps=[]
    for raw in d['hypotheses_ascii']:
        if raw is None:hyps.append(lambda x:None);continue
        h=json.loads(raw)
        if h['schema']=='yggdrasil.ckad.native-sparse-hypothesis.v1':hyps.append(sparse_reader(raw))
        else:
            p=legacy.reader(json.loads(h['native_basis_ascii'])['profiles'][0],bits)
            hyps.append(p if h['info']['eligible'] else lambda x:None)
    def output(s,x):
        if d['quarantined'][s]:return None
        y=base[s](x)
        return y if y is not None else hyps[s](x)
    return output


def audit(root):
    start=time.monotonic();result=json.loads((root/'result.json').read_text())
    spec=importlib.util.spec_from_file_location('legacy_raw_reader',HERE.parent/'CKAD-13/independent_audit.py')
    legacy=importlib.util.module_from_spec(spec);spec.loader.exec_module(legacy)
    previous=json.loads((HERE.parent/'CKAD-13/result.json').read_text());count=0;adopted=0
    for p in result['parents']:
        old=(HERE.parent/'CKAD-13'/p['parent_name']).read_bytes();raw=(root/p['checkpoint_name']).read_bytes()
        need(sha(old)==p['parent_sha256'] and sha(raw)==p['checkpoint_sha256'],'CHECKPOINT_PINS')
        before=json.loads(old);after=json.loads(raw)
        need(before['source_ascii']==after['source_ascii'] and before['properties_ascii']==after['properties_ascii']
            and before['quarantined']==after['quarantined'] and before['events']==after['events'],'STATE_ERASURE')
        a=state_readers(before,legacy);b=state_readers(after,legacy);values=[]
        for s in range(16):
            line=[]
            for x in range(2048):
                y=a(s,x);z=b(s,x)
                need(y is None or y==z,'PREVIOUS_READOUT_LOST');line.append(z);count+=1
            values.append(line)
        need(sha(canon(values))==p['cold']['readouts_sha256'],'FULL_NATIVE_NUMERIC_READOUT')
        for c in (c for c in result['cases'] if c['seed']==p['seed']):
            hraw=(root/c['checkpoint_name']).read_bytes();need(sha(hraw)==c['checkpoint_sha256'],'HYPOTHESIS_PIN')
            hp=sparse_reader(hraw);h=json.loads(hraw)
            # Independent reconstruction of the already-consumed evaluator law.
            seed,slot=c['seed'],c['slot'];degree=(1,2,3,5)[slot//4]
            high=[x for x in range(1,2048) if x.bit_count()==degree]
            low=[x for x in range(2048) if x.bit_count()<degree]
            key=lambda x:sha(canon([seed,slot,x]))
            terms=sorted(high,key=key)[:3]+sorted(low,key=key)[:2]
            seen=set(sorted(range(2048),key=lambda x:sha(canon([seed,'train',x])))[:512])
            held=[x for x in range(2048) if x not in seen];pred=[hp(x) for x in held]
            truth=[sum((x&t)==t for t in terms)%2 for x in held]
            scores={'correct':sum(y==z for y,z in zip(pred,truth)),
                'incorrect':sum(y is not None and y!=z for y,z in zip(pred,truth)),
                'abstained':sum(y is None for y in pred),'questions':len(held),
                'prediction_sha256':sha(canon(pred))}
            need(scores==c['native_sparse'],'INDEPENDENT_HELD_SCORE')
            if c['real_adopted']:
                need(c['arm']=='REAL' and after['hypotheses_ascii'][slot]==hraw.decode('ascii'), 'ADOPTED_WEIGHTS')
                adopted+=1
            elif c['arm']=='REAL':
                need(after['hypotheses_ascii'][slot]==before['hypotheses_ascii'][slot], 'FAILED_REPAIR_CHANGED_STATE')
    need(count==98304,'READOUT_ACCOUNTING')
    return {'classification':'CUMULATIVE_SPARSE_RAW_STATE_AND_NEGATIVES_VERIFIED',
        'readouts':count,'parents':3,'hypotheses':12,'adopted_repairs':adopted,
        'native_imports':0,'solver_imports':0,'scientific_pass':False,'wall_seconds':time.monotonic()-start}


if __name__=='__main__':print(json.dumps(audit(Path(sys.argv[1]) if len(sys.argv)>1 else HERE),sort_keys=True))
