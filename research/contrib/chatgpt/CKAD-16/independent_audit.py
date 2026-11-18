"""Raw two-stage counter/retention audit with zero native or solver imports."""
from fractions import Fraction
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
    if not ok:raise RuntimeError('CKAD16_INDEPENDENT_'+why)


def audit(root):
    start=time.monotonic();result=json.loads((root/'result.json').read_text())
    raw=(HERE.parent/'CKAD-15'/result['parent_checkpoint_name']).read_bytes()
    need(sha(raw)==result['parent_checkpoint_sha256'],'TRAINED_PARENT')
    original=json.loads(raw)
    def load(name,path):
        s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
    reader14=load('read14',HERE.parent/'CKAD-14/independent_audit.py')
    reader13=load('read13',HERE.parent/'CKAD-13/independent_audit.py')
    source=(root/'source_public_fit.json').read_bytes()
    need(sha(source)==result['source_canonical_sha256']=='016bf254ade33b936386abf7829ff90d765da71105e2beebcb130c95febe7d1d','DTR_SOURCE')
    replicas=json.loads(source)['replicas'];held={r['seed']:r for rep in replicas for r in rep['fit'][192:]}
    previous=result['parent_checkpoint_sha256'];checked=0;scored=0
    for stage in result['stages']:
        raw=(root/stage['checkpoint_name']).read_bytes();need(sha(raw)==stage['checkpoint_sha256'],'STATE_PIN')
        state=json.loads(raw);n=stage['prefix_episodes_per_replica']
        for key in ('properties_ascii','source_ascii','hypotheses_ascii','quarantined','events','repairs','history_ascii'):
            need(state[key]==original[key],'OLD_KNOWLEDGE_MUTATION')
        need(stage['input_checkpoint_sha256']==previous,'CUMULATIVE_LINEAGE')
        if n:need(stage['training']['fresh_process_training'] and stage['training']['input_checkpoint_sha256']==previous,'RESUMED_TRAINING')
        rdr=reader14.state_readers(state,reader13);values=[[rdr(s,x) for x in range(2048)] for s in range(16)]
        need(sha(canon(values))==stage['cold']['core_sha256'],'DETERMINISTIC_READOUT');checked+=32768
        history=json.loads(state['history_ascii']);hb=bytes.fromhex(history['native_counters_hex'])
        native_mdp=[]
        for w in range(4):
            for c in range(2):
                for a in range(2):
                    for prev in range(2):
                        o=(w*4+c+2*prev)*4+a*2;pair=[]
                        for bank in (hb[:164],hb[164:]):
                            counts=struct.unpack('>'+'H'*64,bank[4:-32]);pair.append((counts[o+1]+1,counts[o]+counts[o+1]+2))
                        native_mdp.append(pair)
        need(sha(canon(native_mdp))==stage['cold']['mdp_sha256'],'MDP_RETENTION')
        counts=[0]*64
        for part in replicas:
            for r in part['fit'][:n]:
                counts[(8+r['s1'])*4+r['x1']*2+r['s2']]+=1
                slot=r['s1']+2*r['x1']+4*r['s2'];counts[slot*4+2*r['x2']+r['y']]+=1
        if n:
            d=json.loads(state['dtr_ascii'])
            expected_rows=[bytes(r['s1']+2*r['x1']+4*r['s2']+8*r['x2']+16*r['y'] for r in p['fit'][:n]).hex() for p in replicas]
            need(d['rows_hex']==expected_rows and d['stop']==n,'HELD_ROWS_EXCLUDED')
            packet=b'YPC1'+struct.pack('>'+'H'*64,*counts);packet+=hashlib.sha256(packet).digest()
            need(packet.hex()==d['native_counters_hex'],'COUNTER_BYTES')
        else:need('dtr_ascii' not in state,'UNTRAINED_STATE')
        def probability(slot,action):
            o=slot*4+action*2;return (counts[o+1]+1,counts[o]+counts[o+1]+2)
        dtr=[probability(8+s,a) for s in range(2) for a in range(2)]
        dtr += [probability(s+2*a+4*t,b) for s in range(2) for a in range(2) for t in range(2) for b in range(2)]
        need(sha(canon(dtr))==stage['cold']['dtr_sha256'],'DTR_COLD_READOUT')
        losses=[Fraction(0),Fraction(0)];seen=set()
        for row in stage['trace']:
            seed=row['seed'];need(seed in held and seed not in seen,'HELD_EPISODE_IDENTITY');seen.add(seed)
            r=held[seed];p=[probability(8+r['s1'],r['x1']),probability(r['s1']+2*r['x1']+4*r['s2'],r['x2'])]
            need([list(q) for q in p]==row['forecasts']==row['exact_beta'],'EXACT_FORECASTS')
            truth=(r['s2'],r['y']);need(list(truth)==row['truth'],'HELD_TRUTH')
            for t in range(2):losses[t]+=(Fraction(*p[t])-truth[t])**2;scored+=1
        need(len(seen)==192,'HELD_COUNT')
        score=sum(losses)/384
        need((score.numerator,score.denominator)==(stage['brier_pooled']['numerator'],stage['brier_pooled']['denominator']),'BRIER')
        previous=sha(raw)
    need(checked==131072 and scored==1536,'ACCOUNTING')
    return {'classification':'TWO_SOURCE_NATIVE_RETENTION_AND_EPISODIC_PROBABILITIES_VERIFIED',
        'states':4,'deterministic_readouts':checked,'probability_scores':scored,'training_episodes':576,
        'held_training_updates':0,'native_imports':0,'solver_imports':0,'scientific_pass':False,'wall_seconds':time.monotonic()-start}


if __name__=='__main__':print(json.dumps(audit(Path(sys.argv[1]) if len(sys.argv)>1 else HERE),sort_keys=True))
