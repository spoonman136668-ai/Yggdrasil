"""Raw-checkpoint qualification. Deliberately imports no Yggdrasil code."""
import hashlib
import json
from pathlib import Path
import struct
import sys
import time


def canon(d):return json.dumps(d,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode('ascii')
def sha(b):return hashlib.sha256(b).hexdigest()
def need(ok,why):
    if not ok:raise RuntimeError('CKAD13_INDEPENDENT_'+why)


def document(s):
    raw=s.encode('ascii') if isinstance(s,str) else s
    d=json.loads(raw);need(canon(d)==raw,'CANONICAL');return d


def reader(profile,bits):
    terms=[x for x in range(1<<(bits+1)) if x.bit_count()<=profile['degree']]
    ws=struct.unpack('<'+'f'*len(terms),bytes.fromhex(profile['weights_float32_le']))
    need(all(w in (0.,1.) for w in ws),'BINARY_NATIVE_WEIGHTS')
    weights={t for t,w in zip(terms,ws) if w==1.}
    support={int(s,16).bit_length()-1:int(s,16) for s in profile['support_rows']}
    def predict(x):
        subsets=[0];sub=x
        while sub:
            if sub.bit_count()<=profile['degree']:subsets.append(sub)
            sub=(sub-1)&x
        row=sum(1<<t for t in subsets);v=row
        while v:
            pivot=v.bit_length()-1
            if pivot not in support:return None
            v^=support[pivot]
        return len(weights.intersection(subsets))%2
    return predict


def audit(root):
    start=time.monotonic();result=json.loads((root/'result.json').read_text())
    total=0;facts=0;lineage=0
    for case in result['cases']:
        prior=None;prior_events=[];fact_pin=None
        for stage in case['stages']:
            raw=(root/stage['checkpoint_name']).read_bytes();need(sha(raw)==stage['checkpoint_sha256'],'STATE_PIN')
            d=document(raw);need(not d['scientific_pass'] and not d['accepted_native'],'AUTHORITY_FLAGS')
            p=document(d['properties_ascii']);planes=bytes.fromhex(p['known_value_planes_uint16le'])
            count=sum(k.bit_count() for k,v in struct.iter_unpack('<HH',planes))
            need(count==100000 and sha(d['properties_ascii'].encode('ascii'))==case['property_source_sha256'],'FACT_RETENTION')
            need(fact_pin is None or fact_pin==sha(planes),'FACT_BYTES');fact_pin=sha(planes)
            if stage['stage']=='F':facts+=count
            src=document(d['source_ascii']);basis=document(src['native_basis_ascii']);bits=basis['context_bits']
            source_readers=[reader(p,bits) for p in basis['profiles']]
            hyp=[]
            for h in d['hypotheses_ascii']:
                if h is None:hyp.append(None);continue
                hd=document(h);bd=document(hd['native_basis_ascii'])
                hyp.append((reader(bd['profiles'][0],bits),hd['info']['eligible']))
            all_answers=[]
            for slot in (0,2,4,8,1,5,12,13):
                vals=[];seen=int(src['observed_input_masks'][slot],16)
                need(seen.bit_count()==stage['info']['observed_inputs'][slot],'OBSERVATION_COUNT')
                for x in range(1<<(bits+1)):
                    y=source_readers[slot](x)
                    if y is None and hyp[slot] is not None and hyp[slot][1]:y=hyp[slot][0](x)
                    if d['quarantined'][slot]:y=None
                    vals.append(y)
                    if seen&(1<<x) and not d['quarantined'][slot]:need(y is not None,'WITNESSED_ABSTENTION')
                all_answers.append(vals);total+=len(vals)
            need(sha(canon(all_answers))==stage['cold']['answers_sha256'],'ALL_RAW_READOUTS')
            need(d['events'][:len(prior_events)]==prior_events,'EVENT_ERASURE')
            if prior is not None:
                need(stage['input_checkpoint_sha256']==prior==stage['previous_stage_checkpoint_sha256'],'LINEAGE');lineage+=1
            prior=sha(raw);prior_events=d['events']
            for event in d['events']:
                if event['status']=='QUARANTINED':
                    packet=event['conflicting_packet'];need(sha(canon(packet))==event['source_sha256'],'NEGATIVE_EVIDENCE')
                    need(any(source_readers[event['slot']](c|(a<<bits))!=y for c,a,y in packet),'REAL_CONTRADICTION')
    need(facts==300000 and lineage==15,'FINAL_ACCOUNTING')
    return {'classification':'RAW_NATIVE_STATE_AND_LINEAGE_VERIFIED','checkpoints':18,
        'readouts':total,'retained_properties':facts,'cumulative_transitions':lineage,
        'scientific_pass':False,'native_imports':0,'wall_seconds':time.monotonic()-start}


if __name__=='__main__':
    root=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parent
    print(json.dumps(audit(root),sort_keys=True))
