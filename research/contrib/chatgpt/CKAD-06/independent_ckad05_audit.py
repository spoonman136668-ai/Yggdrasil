"""Independent raw checkpoint audit: stdlib only, no learner imports."""
import hashlib, json, struct, time
from functools import lru_cache
from pathlib import Path

start=time.monotonic()
root=Path(__file__).resolve().parent.parent/'CKAD-05'
sha=lambda b:hashlib.sha256(b).hexdigest()
canonical=lambda v:json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode('ascii')
r=json.loads((root/'result.json').read_text())
out=[]
for case in r['cases']:
    seed=case['seed'];raw=(root/f'seed-{seed}-complete-native-knowledge.json').read_bytes()
    assert sha(raw)==case['checkpoint_sha256']
    d=json.loads(raw);before=json.loads((root/f'seed-{seed}-before-trainingB.json').read_bytes())
    assert d['known_value_planes_uint16le']==before['known_value_planes_uint16le']
    pairs=list(struct.iter_unpack('<HH',bytes.fromhex(d['known_value_planes_uint16le'])))
    assert len(pairs)==10000 and all(k==1023 for k,v in pairs)
    h=hashlib.sha256()
    for entity,(known,values) in enumerate(pairs):
        for prop in range(10):
            h.update(entity.to_bytes(4,'little'));h.update(bytes((prop,(values>>prop)&1)))
    assert h.hexdigest()==case['synthetic_property_source_sha256']
    p=json.loads(d['native_relations_ascii'])['profiles'][0]
    assert p==json.loads(before['native_relations_ascii'])['profiles'][0]
    terms=[i for i in range(2048) if i.bit_count()<=p['degree']]
    weights=struct.unpack('<'+'f'*len(terms),bytes.fromhex(p['weights_float32_le']))
    active=[t for t,w in zip(terms,weights) if w==1]
    support=[int(s,16) for s in p['support_rows']]
    assert all((s&1)==((s>>1024)&1) for s in support)
    @lru_cache(maxsize=4096)
    def partial(value,known):
        unknown=1023^known;sub=unknown;answer=None
        while True:
            x=value|sub|1024
            candidate=sum((x&t)==t for t in active)&1
            if answer is not None and candidate!=answer:return None
            answer=candidate
            if sub==0:return answer
            sub=(sub-1)&unknown
    conditions={}
    for name,c in case['conditions'].items():
        mask=c['visible_mask']
        answers=[partial(pairs[e][1]&mask,mask) for e in range(6144,8192)]
        assert sha(canonical(answers))==c['native']['prediction_sha256']
        conditions[name]={'answered':sum(x is not None for x in answers),'prediction_sha256':sha(canonical(answers))}
    out.append({'seed':seed,'properties_verified':100000,'before_after_weights_equal':True,
                'unobserved_action0_unidentified':True,'conditions':conditions})
receipt={'schema':'ckad05.independent-raw-checkpoint-audit.v1','source_sha':'28948ec34d8f5727daa10578a34c96825e3c1a54','cases':out,'native_imports':0,'wall_seconds':time.monotonic()-start}
Path(__file__).with_name('independent_ckad05_audit_result.json').write_bytes(canonical(receipt)+b'\n')
print(json.dumps(receipt,indent=2))
