#!/usr/bin/env python3
"""Reconstruct and verify ENERGY-56 exact original scorer/audit receipts."""
from pathlib import Path
import sys,io,tarfile,hashlib,json
D=Path(__file__).resolve().parent
sha=lambda x:hashlib.sha256(x).hexdigest()
def verify():
 m=json.loads((D/'archive_manifest.json').read_text());res=json.loads((D/'result.json').read_text());
 raw=b''
 for p in m['parts']:
  data=(D/p['name']).read_bytes()
  assert sha(data)==p['sha256'] and len(data)==p['size'],('bad evidence part',p['name']);raw+=data
 assert sha(raw)==m['evidence_archive_sha256'] and len(raw)==m['packed_byte_size']
 assert sha((D/'source.tar.bz2').read_bytes())==m['source_sha256']
 assert res['classification']==m['classification']=='SCREEN_NO_GO'
 assert res['gates_passed']==4 and res['gates_total']==8
 assert res['reserved_primary_seeds_unconsumed']==[9911,9923,9941]
 with tarfile.open(fileobj=io.BytesIO(raw),mode='r:bz2') as tar:
  names=set(tar.getnames());assert names==set(m['file_sha256'])
  for n,expected in m['file_sha256'].items():
   actual=tar.extractfile(n).read();assert sha(actual)==expected,('bad evidence file',n)
  scored=json.loads(tar.extractfile('screen.json').read());aud=json.loads(tar.extractfile('screen_audit.json').read());replay=json.loads(tar.extractfile('screen_replay.json').read());rec=json.loads(tar.extractfile('replay_receipt.json').read())
 assert scored['seeds']==[99917] and len(scored['data'])==6 and len(scored['aggregate'])==8
 assert aud['audit']=='PASS' and aud['independently_refit_predictions']==17249
 assert all(len({*c['world']['causal_ids']})==512 for c in scored['data'])
 for arm in scored['aggregate']:
  for ctx in ('old','new','cold'):
   v=sum(c['mse'][arm][ctx] for c in scored['data'])/len(scored['data'])
   assert abs(v-scored['aggregate'][arm][ctx])<1e-9
 sem=lambda z: {**{k:v for k,v in z.items() if k!='total_seconds'},'data':[{k:v for k,v in case.items() if k!='seconds_total_case'} for case in z['data']]}
 payload=json.dumps(sem(scored),sort_keys=True,separators=(',',':')).encode();assert payload==json.dumps(sem(replay),sort_keys=True,separators=(',',':')).encode()
 assert sha(payload)==rec['semantic_sha256']==res['replay_non_timing_semantic_sha256']
 return {'status':'PASS','archive_sha256':sha(raw),'parts':len(m['parts']),'worlds':6,'arms':8,'audit_checks':17249,'replay_semantics_sha256':sha(payload),'frozen_gates_passed':4,'frozen_gates_total':8}
if __name__=='__main__':
 print(json.dumps(verify(),sort_keys=True,indent=2))
