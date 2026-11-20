#!/usr/bin/env python3
"""Fresh process ENERGY-59 checkpoint-function restore verification; no scorer import."""
import argparse,hashlib,itertools,json
from pathlib import Path
import numpy as np
terms=tuple(c for k in (2,3) for c in itertools.combinations(range(12),k))
def feature(x):
 s=2*np.asarray(x,dtype=np.int8)-1
 return np.column_stack([np.prod(s[:,list(c)],axis=1) for c in terms])
def run(raw):
 j=json.loads(Path(raw).read_text());checks=0;max_diff=0.;sha=[]
 for c in j['cases']:
  w=c['world'];f=c['fit'];cp=json.loads(json.dumps(f['checkpoint'],sort_keys=True,separators=(',',':')))
  digest=hashlib.sha256(json.dumps(cp,sort_keys=True,separators=(',',':')).encode()).hexdigest();assert digest==f['checkpoint_sha256'];sha.append(digest)
  x=np.asarray(w['x'],dtype=np.int8);y=np.asarray(w['y'],dtype=float)
  assert len(cp['snapshots'])>1
  for phase in 'ABC':
   p=slice(*w['spans']['probe_'+phase]);h=slice(*w['spans']['held_'+phase]);px=feature(x[p]);hx=feature(x[h]);py=y[p]
   models=[(np.asarray(z['coef'],dtype=float),float(z['intercept'])) for z in cp['snapshots']]
   loss=np.asarray([np.mean((px@co+inter-py)**2) for co,inter in models]);ord=np.argsort(loss,kind='stable');i,k=map(int,ord[:2]);a=cp['snapshots']
   merge=len(set(a[i]['support'])&set(a[k]['support']))>=3 and loss[k]-loss[i]<.04
   za=hx@models[i][0]+models[i][1]
   if merge:za=0.5*(za+(hx@models[k][0]+models[k][1]))
   old=np.asarray(f['predictions']['energy_consensus'][phase]);diff=float(np.max(np.abs(za-old)))
   max_diff=max(diff,max_diff);assert diff<1e-12,(w['seed'],w['world_id'],w['family'],phase,diff)
   checks+=len(old)
 return {'status':'PASS','worlds':len(j['cases']),'fresh_process':True,'predictions_checked':checks,'maximum_absolute_diff':max_diff,'checkpoint_sha256s':sha}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('primary');p.add_argument('--out',required=True);a=p.parse_args();r=run(a.primary);Path(a.out).write_text(json.dumps(r,sort_keys=True,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k!='checkpoint_sha256s'}))
