"""Existing native counters over public two-stage DTR histories, cached only.

First-stage state transitions and terminal outcomes have distinct addresses.
Immediate zero reward is never treated as the final consequence. No simulator
runtime, private source state, source oracle, or policy execution is involved.
"""
import json
from yggdrasil.native_context_basis import canonical,digest,pin,require
from yggdrasil.public_causal_cells import PublicCausalCells

SCHEMA='yggdrasil.ckad.native-dtr-history.v1'
SOURCE_PIN='016bf254ade33b936386abf7829ff90d765da71105e2beebcb130c95febe7d1d'
PREFIX_PINS={64:'b00de5384f1cc9d0f65fb00788dcd3bc50c031969a5c17ebe50e3f537c1ef286',
    128:'1ee34cc368b90f0445dc2bc5532f024faf09e797f0efb3c9f6c3ea03d4f58e16',
    192:'de6e2bb77d8b378d6c776a9b011129b6e4e6298953f1f66379f4f4e84955f571'}
MAX_BYTES=4096


def address(slot):return (slot,False) if slot<7 else (slot-7,True)


class NativeDTRHistory:
    __slots__=('_bank','_rows')

    def __init__(self):
        self._bank=PublicCausalCells();self._rows=(b'',)*3

    @staticmethod
    def validate(*values):
        for v in values:PublicCausalCells._bit(v,'DTR_PUBLIC_BIT')

    def _observe(self,packed):
        require(type(packed) is int and 0<=packed<32,'DTR_PUBLIC_RECORD')
        s1=packed&1;x1=(packed>>1)&1;s2=(packed>>2)&1;x2=(packed>>3)&1;y=packed>>4
        a,r=address(8+s1);self._bank.observe(a,x1,s2,retained=r)
        a,r=address(s1+2*x1+4*s2);self._bank.observe(a,x2,y,retained=r)

    def stage_prefix(self,raw,expected_sha256,stop):
        require(type(raw) is bytes and len(raw)<=200000 and expected_sha256==SOURCE_PIN
                and digest(raw)==SOURCE_PIN,'DTR_UNQUALIFIED_SOURCE')
        require(type(stop) is int and stop in (64,128,192),'DTR_FROZEN_PREFIX')
        old=len(self._rows[0]);require(stop>=old,'DTR_PREFIX_REWIND')
        d=json.loads(raw);require(d['schema']=='mass.dtr02.fit-public-traces.v1' and len(d['replicas'])==3,'DTR_SOURCE_SCHEMA')
        data=[]
        for replica,part in enumerate(d['replicas']):
            require(part['index']==replica and len(part['fit'])==256,'DTR_EPISODE_COUNT')
            packed=[]
            for i,row in enumerate(part['fit']):
                require(set(row)=={'s1','x1','s2','x2','y','seed'} and type(row['seed']) is int
                    and row['seed']==1100000+10000*replica+i,'DTR_EVENT_IDENTITY')
                self.validate(*(row[k] for k in ('s1','x1','s2','x2','y')))
                require(row['x1']==(i%4)//2 and row['x2']==i%2,'DTR_ORIGINAL_ACTION_PLAN')
                if i<stop:packed.append(row['s1']+2*row['x1']+4*row['s2']+8*row['x2']+16*row['y'])
            data.append(bytes(packed))
        rows=tuple(data);require(all(n[:old]==o for n,o in zip(rows,self._rows)),'DTR_PREFIX_DRIFT')
        if stop==old:return self
        obj=NativeDTRHistory();obj._bank=PublicCausalCells.restore(self._bank.snapshot());obj._rows=rows
        for row in rows:
            for v in row[old:]:obj._observe(v)
        return obj

    def transition(self,s1,x1):
        self.validate(s1,x1);a,r=address(8+s1)
        return self._bank.outcome_probability(a,x1,retained=r)

    def terminal(self,s1,x1,s2,x2):
        self.validate(s1,x1,s2,x2);a,r=address(s1+2*x1+4*s2)
        return self._bank.outcome_probability(a,x2,retained=r)

    def info(self):
        n=len(self._rows[0])
        return {'source_cache_sha256':SOURCE_PIN,'episodes_per_replica':n,'training_episodes':3*n,
            'outcome_updates':6*n,'native_counter_bytes':164,'native_counter_sha256':digest(self._bank.snapshot()),
            'history':'terminal uses s1,x1,s2,x2; transition uses s1,x1','causal_policy_value_identified':False}

    def checkpoint(self):
        d={'schema':SCHEMA,'rows_hex':[r.hex() for r in self._rows],'stop':len(self._rows[0]),
            'native_counters_hex':self._bank.snapshot().hex(),'source_cache_sha256':SOURCE_PIN,
            'source_class':'PREVIOUSLY_CONSUMED_PUBLIC_DTR_FIT','accepted_native':False,'scientific_pass':False}
        raw=canonical(d);require(len(raw)<=MAX_BYTES,'DTR_CHECKPOINT_CAPACITY');return raw

    @classmethod
    def restore(cls,raw,expected_sha256):
        require(type(raw) is bytes and 0<len(raw)<=MAX_BYTES and pin(expected_sha256)
                and digest(raw)==expected_sha256,'DTR_CHECKPOINT_PIN')
        def unique(pairs):
            d={}
            for k,v in pairs:require(k not in d,'DTR_DUPLICATE_KEY');d[k]=v
            return d
        try:
            d=json.loads(raw.decode('ascii'),object_pairs_hook=unique)
            require(type(d) is dict and set(d)=={'schema','rows_hex','stop','native_counters_hex',
                'source_cache_sha256','source_class','accepted_native','scientific_pass'} and d['schema']==SCHEMA
                and d['source_cache_sha256']==SOURCE_PIN and d['source_class']=='PREVIOUSLY_CONSUMED_PUBLIC_DTR_FIT'
                and d['accepted_native'] is False and d['scientific_pass'] is False and canonical(d)==raw,'DTR_CONTRACT')
            stop=d['stop'];require(type(stop) is int and stop in PREFIX_PINS,'DTR_PREFIX_CONTRACT')
            require(digest(canonical({k:d[k] for k in ('rows_hex','stop')}))==PREFIX_PINS[stop],'DTR_PREFIX_PIN')
            obj=cls();obj._rows=tuple(bytes.fromhex(r) for r in d['rows_hex'])
            require(len(obj._rows)==3 and all(len(r)==stop for r in obj._rows),'DTR_PREFIX_SHAPE')
            for row in obj._rows:
                for v in row:obj._observe(v)
            require(obj._bank.snapshot().hex()==d['native_counters_hex'] and obj.checkpoint()==raw,'DTR_COUNTER_RECONSTRUCTION')
            return obj
        except (ValueError,TypeError,KeyError,UnicodeError,AttributeError,IndexError) as exc:
            raise ValueError('CKAD_NATIVE_DTR_CHECKPOINT_REJECTED') from exc
