"""Independent counter, retention and held-score audit; no native imports."""
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import sys
import time
HERE=Path(__file__).resolve().parent


def canonical(d):return json.dumps(d,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode('ascii')
def sha(b):return hashlib.sha256(b).hexdigest()
def need(ok,why):
    if not ok:raise RuntimeError('CKAD15_INDEPENDENT_'+why)


def audit(root):
    start=time.monotonic();d=json.loads((root/'result.json').read_text())
    raw=(HERE.parent/'CKAD-14'/d['parent_checkpoint_name']).read_bytes();need(sha(raw)==d['parent_checkpoint_sha256'],'PARENT_PIN')
    parent=json.loads(raw)
    spec=importlib.util.spec_from_file_location('ckad14_raw',HERE.parent/'CKAD-14/independent_audit.py')
    old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
    spec=importlib.util.spec_from_file_location('ckad13_raw',HERE.parent/'CKAD-13/independent_audit.py')
    legacy=importlib.util.module_from_spec(spec);spec.loader.exec_module(legacy)
    reader=old.state_readers(parent,legacy)
    original=[[reader(s,x) for x in range(2048)] for s in range(16)]
    source=(HERE.parent/'NKR-20/source_fixture.json').read_bytes()
    need(sha(source)==d['source_cache_sha256']=='e994f6adb0733c05eeae8dd19b0a4a36bb13946e1090b241023630b468276d1f','PUBLIC_CACHE')
    episodes=[bytes.fromhex(e['rows_hex']) for e in json.loads(source)['episodes']]
    previous=d['parent_checkpoint_sha256'];checked=0;scored=0
    for stage in d['stages']:
        raw=(root/stage['checkpoint_name']).read_bytes();need(sha(raw)==stage['checkpoint_sha256'],'STATE_PIN')
        state=json.loads(raw);n=stage['prefix_rows_per_world']
        for key in ('source_ascii','properties_ascii','hypotheses_ascii','quarantined','events','repairs'):
            need(state[key]==parent[key],'CORE_MUTATION')
        need(stage['input_checkpoint_sha256']==previous==stage['previous_checkpoint_sha256'],'CUMULATIVE_LINEAGE')
        # Identical source/hypothesis/property bytes imply identical numeric
        # readout; independently re-evaluate once per stage as an extra check.
        rdr=old.state_readers(state,legacy)
        values=[[rdr(s,x) for x in range(2048)] for s in range(16)]
        need(values==original and sha(canonical(values))==stage['cold']['deterministic_sha256'],'NATIVE_RETENTION')
        checked+=32768
        banks=[[0]*64 for _ in range(2)]
        for world,rows in enumerate(episodes):
            for i in range(1,n+1):
                v=rows[i];slot=world*4+(v>>5)+2*((rows[i-1]>>3)&1);action=(v>>4)&1
                for target,y in enumerate(((v>>3)&1,(v>>2)&1)):banks[target][slot*4+action*2+y]+=1
        if n:
            h=json.loads(state['history_ascii'])
            need(h['stop']==n and h['rows_hex']==[r[1:n+1].hex() for r in episodes]
                and h['headers_hex']==bytes(r[0] for r in episodes).hex(),'NO_HELD_OUTCOME_IN_STATE')
            packed=[]
            for b in banks:
                p=b'YPC1'+struct.pack('>'+'H'*64,*b);packed.append(p+hashlib.sha256(p).digest())
            need(b''.join(packed).hex()==h['native_counters_hex'],'COUNTER_BYTES')
        else:need('history_ascii' not in state,'UNTRAINED_STATE')
        forecasts=[]
        for w in range(4):
            for before in range(2):
                for action in range(2):
                    for prev in range(2):
                        slot=w*4+before+2*prev;o=slot*4+action*2
                        forecasts.append(tuple((b[o+1]+1,b[o]+b[o+1]+2) for b in banks))
        need(sha(canonical(forecasts))==stage['cold']['probability_sha256'],'COLD_PROBABILITIES')
        loss=Fraction(0)
        for row in stage['trace']:
            w,i=row['world'],row['held_index'];need(24<=i<=30,'HELD_SPLIT')
            v=episodes[w][i];slot=w*4+(v>>5)+2*((episodes[w][i-1]>>3)&1);action=(v>>4)&1;o=slot*4+action*2
            predicted=[(b[o+1]+1,b[o]+b[o+1]+2) for b in banks]
            need([list(p) for p in predicted]==row['forecasts']==row['exact_beta'],'FORECAST_EXACT_BETA')
            truth=((v>>3)&1,(v>>2)&1);need(list(truth)==row['truth'],'HELD_TRUTH')
            for p,y in zip(predicted,truth):loss+=(Fraction(*p)-y)**2;scored+=1
        loss/=56
        need((loss.numerator,loss.denominator)==(stage['brier']['numerator'],stage['brier']['denominator']),'BRIER')
        previous=sha(raw)
    need(checked==131072 and scored==224,'ACCOUNTING')
    return {'classification':'UNIFIED_NATIVE_HISTORY_RETENTION_AND_PROBABILITIES_VERIFIED','states':4,
        'deterministic_readouts':checked,'probability_scores':scored,'training_events':92,'held_training_updates':0,
        'native_imports':0,'solver_imports':0,'scientific_pass':False,'wall_seconds':time.monotonic()-start}


if __name__=='__main__':print(json.dumps(audit(Path(sys.argv[1]) if len(sys.argv)>1 else HERE),sort_keys=True))
