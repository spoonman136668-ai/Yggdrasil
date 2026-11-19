"""Raw counter-only audit of the integrated known readout."""
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import struct
import sys
import time
HERE=Path(__file__).resolve().parent


def canon(d):return json.dumps(d,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode('ascii')
def sha(b):return hashlib.sha256(b).hexdigest()
def need(ok,why):
    if not ok:raise RuntimeError('CKAD17_INDEPENDENT_'+why)


def audit(root):
    start=time.monotonic();d=json.loads((root/'result.json').read_text())
    raw=(root/d['checkpoint_name']).read_bytes();old=(HERE.parent/'CKAD-16'/d['parent_checkpoint_name']).read_bytes()
    need(raw==old and sha(raw)==d['checkpoint_sha256'],'LEARNED_BYTES')
    history=json.loads(json.loads(raw)['history_ascii']);b=bytes.fromhex(history['native_counters_hex'])
    banks=[struct.unpack('>'+'H'*64,part[4:-32]) for part in (b[:164],b[164:])]
    def forecast(w,c,a,r):
        result=[]
        for bank in banks:
            offsets=[(w*4+c+2*i)*4+a*2 for i in (0,1)];zero=offsets[0];one=offsets[1];child=offsets[r]
            parent=Fraction(bank[zero+1]+bank[one+1]+1,sum(bank[x]+bank[x+1] for x in offsets)+2)
            q=(bank[child+1]+4*parent)/(bank[child]+bank[child+1]+4)
            result.append((q.numerator,q.denominator))
        return result
    forecasts=[forecast(w,c,a,r) for w in range(4) for c in range(2) for a in range(2) for r in range(2)]
    need(sha(canon(forecasts))==d['cold']['backoff_sha256'],'COLD_PROBABILITIES')
    cache=(HERE.parent/'NKR-20/source_fixture.json').read_bytes()
    need(sha(cache)=='e994f6adb0733c05eeae8dd19b0a4a36bb13946e1090b241023630b468276d1f','PUBLIC_CACHE')
    episodes=[bytes.fromhex(e['rows_hex']) for e in json.loads(cache)['episodes']];loss=Fraction(0);count=0
    for row in d['trace']:
        w,i=row['world'],row['held_index'];need(24<=i<=30,'HELD_SPLIT')
        v=episodes[w][i];p=forecast(w,v>>5,(v>>4)&1,(episodes[w][i-1]>>3)&1)
        need([list(q) for q in p]==row['new_forecasts']==row['exact_backoff'],'READOUT')
        truth=((v>>3)&1,(v>>2)&1);need(list(truth)==row['truth'],'TRUTH')
        for q,y in zip(p,truth):loss+=(Fraction(*q)-y)**2;count+=1
    loss/=56;need(count==56 and (loss.numerator,loss.denominator)==(d['brier']['numerator'],d['brier']['denominator']),'BRIER')
    return {'classification':'KNOWN_BACKOFF_READOUT_AND_UNCHANGED_STATE_VERIFIED','forecasts':count,
        'training_updates':0,'native_imports':0,'solver_imports':0,'scientific_pass':False,'wall_seconds':time.monotonic()-start}


if __name__=='__main__':print(json.dumps(audit(Path(sys.argv[1]) if len(sys.argv)>1 else HERE),sort_keys=True))
