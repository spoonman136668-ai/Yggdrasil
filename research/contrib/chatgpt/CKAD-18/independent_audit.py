"""Independent full-state, retained-witness and score audit; stdlib only."""
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import sys
import time
HERE=Path(__file__).resolve().parent
NEW=(3,6,7,9,10,11,14,15)
OLD=(0,1,2,4,5,8,12,13)


def canon(d):return json.dumps(d,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode('ascii')
def sha(b):return hashlib.sha256(b).hexdigest()
def need(ok,why):
    if not ok:raise RuntimeError('CKAD18_INDEPENDENT_'+why)


def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m


def probabilities(d):
    b=bytes.fromhex(json.loads(d['history_ascii'])['native_counters_hex'])
    banks=[struct.unpack('>'+'H'*64,p[4:-32]) for p in (b[:164],b[164:])]
    mdp=[];backoff=[]
    for w in range(4):
        for c in range(2):
            for a in range(2):
                for r in range(2):
                    direct=[];hierarchical=[]
                    for bank in banks:
                        offsets=[(w*4+c+2*i)*4+a*2 for i in (0,1)];o=offsets[r]
                        direct.append((bank[o+1]+1,bank[o]+bank[o+1]+2))
                        parent=Fraction(sum(bank[x+1] for x in offsets)+1,sum(bank[x]+bank[x+1] for x in offsets)+2)
                        q=(bank[o+1]+4*parent)/(bank[o]+bank[o+1]+4);hierarchical.append((q.numerator,q.denominator))
                    mdp.append(direct);backoff.append(hierarchical)
    b=bytes.fromhex(json.loads(d['dtr_ascii'])['native_counters_hex'])
    bank=struct.unpack('>'+'H'*64,b[4:-32])
    def pred(s,a):
        o=s*4+a*2;return (bank[o+1]+1,bank[o]+bank[o+1]+2)
    dtr=[pred(8+s,a) for s in range(2) for a in range(2)]+[
        pred(s+2*a+4*t,z) for s in range(2) for a in range(2) for t in range(2) for z in range(2)]
    return {'mdp':mdp,'mdp_backoff':backoff,'dtr':dtr}


def score(pred,truth):
    return {'correct':sum(p==y for p,y in zip(pred,truth)),'incorrect':sum(p is not None and p!=y for p,y in zip(pred,truth)),
        'abstained':sum(p is None for p in pred),'questions':len(truth),'prediction_sha256':sha(canon(pred))}


def audit(root):
    start=time.monotonic();result=json.loads((root/'result.json').read_text())
    r14=module('ckad18_independent14',HERE.parent/'CKAD-14/independent_audit.py')
    r13=module('ckad18_independent13',HERE.parent/'CKAD-13/independent_audit.py')
    controls_raw=(HERE.parent/'CKAD-06/result.json').read_bytes()
    need(hashlib.sha1(b'blob '+str(len(controls_raw)).encode()+b'\0'+controls_raw).hexdigest()==result['control_git_blob'],'CONTROL_CUSTODY')
    controls={(c['seed'],c['slot']):c for c in json.loads(controls_raw)['cases'] if c['degree']==11}
    witnesses=json.loads((HERE.parent/'CKAD-08/result.json').read_text())
    known=json.loads((HERE.parent/'CKAD-17/seed-101-qualified-full-state.json').read_bytes())
    count=0;facts=0;held_count=0;losses=0;gain=0
    for p in result['parents']:
        seed=p['seed'];oldpath=HERE.parent/('CKAD-17' if seed==101 else 'CKAD-14')/p['parent_name']
        old=oldpath.read_bytes();raw=(root/p['checkpoint_name']).read_bytes()
        need(sha(old)==p['parent_sha256'] and sha(raw)==p['checkpoint_sha256'],'CHECKPOINT_PINS')
        before=json.loads(old);after=json.loads(raw);need(canon(after)==raw,'CANONICAL_STATE')
        need(not after['scientific_pass'] and not after['accepted_native'],'NO_PROMOTION')
        need(before['properties_ascii']==after['properties_ascii'] and before['quarantined']==after['quarantined']
            and after['quarantined']==[s==5 for s in range(16)],'FACT_OR_QUARANTINE_ERASURE')
        prop=json.loads(after['properties_ascii']);planes=bytes.fromhex(prop['known_value_planes_uint16le'])
        n=sum(k.bit_count() for k,v in struct.iter_unpack('<HH',planes));need(n==100000,'FACT_COUNT');facts+=n
        need(after['events'][:len(before['events'])]==before['events']
            and after['repairs'][:len(before['repairs'])]==before['repairs'],'NEGATIVE_LINEAGE_ERASURE')
        sa=json.loads(before['source_ascii']);sb=json.loads(after['source_ascii'])
        ba=json.loads(sa['native_basis_ascii']);bb=json.loads(sb['native_basis_ascii'])
        for s in OLD:
            need(before['hypotheses_ascii'][s]==after['hypotheses_ascii'][s]
                and ba['profiles'][s]==bb['profiles'][s]
                and sa['observed_input_masks'][s]==sb['observed_input_masks'][s]
                and sa['batch_ledgers'][s]==sb['batch_ledgers'][s],'OLD_RELATION_MUTATION')
        for k in ('history_ascii','dtr_ascii'):
            need(after[k]==known[k],'KNOWN_PROBABILITY_BYTES')
            if k in before:need(before[k]==after[k],'PROBABILITY_FORGETTING')
        need(sha(canon(probabilities(after)))==p['cold']['probabilities_sha256']==result['probabilities_sha256'],'PROBABILITY_READOUT')
        a=r14.state_readers(before,r13);b=r14.state_readers(after,r13)
        values=[[b(s,x) for x in range(2048)] for s in range(16)]
        need(sha(canon(values))==p['cold']['core_sha256'],'COLD_CORE')
        for s in range(16):
            for x in range(2048):
                y=a(s,x);losses+=y is not None and y!=values[s][x];count+=1
        wp=next(c for c in witnesses['cases'] if c['seed']==seed)
        wr=(HERE.parent/'CKAD-08'/wp['checkpoint_name']).read_bytes();need(sha(wr)==wp['checkpoint_sha256']==p['source_sha256'],'WITNESS_PIN')
        wd=json.loads(wr);need(not any(wd['contradiction_batch_sha256']),'SOURCE_QUARANTINE')
        ws=json.loads(wd['native_accumulator_ascii']);wb=json.loads(ws['native_basis_ascii'])
        witness_readers=[r13.reader(profile,10) for profile in wb['profiles']]
        for c in (c for c in result['cases'] if c['seed']==seed):
            s=c['slot'];degree=(1,2,3,5)[s//4]
            hi=[x for x in range(1,2048) if x.bit_count()==degree];lo=[x for x in range(2048) if x.bit_count()<degree]
            key=lambda x:sha(canon([seed,s,x]));terms=sorted(hi,key=key)[:3]+sorted(lo,key=key)[:2]
            seen=set(sorted(range(2048),key=lambda x:sha(canon([seed,'train',x])))[:512])
            need(int(ws['observed_input_masks'][s],16)==sum(1<<x for x in seen),'OBSERVED_WITNESSES')
            truth=lambda x:sum((x&t)==t for t in terms)%2
            rows=[[x&1023,x>>10,truth(x)] for x in sorted(seen)]
            need(sha(canon(rows))==c['source_sha256'],'SOURCE_ROWS')
            need(all(witness_readers[s](x)==truth(x) for x in seen),'AUTHENTICATED_OUTCOMES')
            if s!=5:
                need(int(sb['observed_input_masks'][s],16)==sum(1<<x for x in seen)
                    and all(values[s][x]==truth(x) for x in seen),'ACQUIRED_WITNESSES')
            held=[x for x in range(2048) if x not in seen];ys=[truth(x) for x in held]
            sc=score([values[s][x] for x in held],ys)
            need(sc==c['native'] and score([a(s,x) for x in held],ys)==c['parent_native'],'HELD_SCORE')
            ctrl=controls[seed,s];need(ctrl['source_sha256']==sha(canon(rows))
                and ctrl['steps'][-1]['exposures']==512
                and ctrl['steps'][-1]['fully_trained_cart']['score']==c['fully_trained_cart'],'REUSED_CONTROL')
            if s==5:need(all(y is None for y in values[s]),'QUARANTINE_READOUT')
            held_count+=len(held);gain+=sc['correct']-c['parent_native']['correct']
    need(count==98304 and held_count==73728 and facts==300000 and losses==0,'ACCOUNTING_OR_RETENTION')
    return {'classification':'FULL_RETAINED_WITNESS_SCOPE_AND_NEGATIVES_VERIFIED','states':3,'readouts':count,
        'held_scores':held_count,'retained_properties':facts,'previous_answers_changed':losses,'additional_correct':gain,
        'native_imports':0,'solver_imports':0,'original_source_actions':0,'scientific_pass':False,'wall_seconds':time.monotonic()-start}


if __name__=='__main__':print(json.dumps(audit(Path(sys.argv[1]) if len(sys.argv)>1 else HERE),sort_keys=True))
