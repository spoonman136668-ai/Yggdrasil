"""Bounded integration of the qualified NKR20 two native counter banks.

Only a hash-authenticated, previously consumed public cache is admitted. Past
training prefixes alone enter state. This estimates observational transition
probabilities; it does not identify unobserved causal policy effects.
"""
import json
import struct
from yggdrasil.native_context_basis import canonical, digest, pin, require
from yggdrasil.public_causal_cells import PublicCausalCells

SCHEMA='yggdrasil.ckad.native-stochastic-history.v1'
SOURCE_PIN='e994f6adb0733c05eeae8dd19b0a4a36bb13946e1090b241023630b468276d1f'
PREFIX_PINS = {
    8:'350867edac14e83fca0ce35f2b3b67825174b1db692881b8ad765b17187ed8ee',
    16:'cf85604734078c06d525adfce504eb8cc60bfdb4932f1f6beaa83f61f9349b76',
    23:'16f5b71867cd5723c9bf1650707ddb4ebb8099c916cc9fffb057b6db51b4b3d6',
}
MAX_BYTES=4096


class NativeStochasticHistory:
    __slots__=('_banks','_headers','_rows')

    def __init__(self):
        self._banks=(PublicCausalCells(),PublicCausalCells())
        self._headers=b'';self._rows=(b'',)*4

    @staticmethod
    def address(world,before,action,previous_reward):
        require(type(world) is int and 0<=world<4,'HISTORY_WORLD')
        PublicCausalCells._bit(before,'HISTORY_BEFORE')
        PublicCausalCells._bit(action,'ACTION')
        PublicCausalCells._bit(previous_reward,'PREVIOUS_REWARD')
        slot=world*4+before+2*previous_reward
        return ((slot,False) if slot<7 else (slot-7,True))

    def _append(self,world,packed,previous):
        require(type(packed) is int and 0<=packed<64 and not packed&3
                and (packed>>5)==((previous>>2)&1),'HISTORY_PUBLIC_CHRONOLOGY')
        before=packed>>5;action=(packed>>4)&1;previous_reward=(previous>>3)&1
        address,retained=self.address(world,before,action,previous_reward)
        for bank,outcome in zip(self._banks,((packed>>3)&1,(packed>>2)&1)):
            bank.observe(address,action,outcome,retained=retained)

    def stage_prefix(self,raw,expected_sha256,stop):
        require(type(raw) is bytes and len(raw)<=8192 and expected_sha256==SOURCE_PIN
                and digest(raw)==SOURCE_PIN,'HISTORY_UNQUALIFIED_SOURCE')
        require(type(stop) is int and stop in (8,16,23),'HISTORY_FROZEN_PREFIX')
        old=len(self._rows[0]);require(stop>=old,'HISTORY_PREFIX_REWIND')
        data=json.loads(raw);episodes=[bytes.fromhex(e['rows_hex']) for e in data['episodes']]
        headers=bytes(e[0] for e in episodes);rows=tuple(e[1:stop+1] for e in episodes)
        require(len(headers)==4 and all(len(r)==stop for r in rows),'HISTORY_SOURCE_ROWS')
        require(not self._headers or (self._headers==headers
                and all(r[:old]==p for r,p in zip(rows,self._rows))),'HISTORY_SOURCE_DRIFT')
        if stop==old:return self
        obj=NativeStochasticHistory();obj._headers=headers;obj._rows=rows
        obj._banks=tuple(PublicCausalCells.restore(b.snapshot()) for b in self._banks)
        for world,r in enumerate(rows):
            for i in range(old,stop):obj._append(world,r[i],headers[world] if i==0 else r[i-1])
        return obj

    def predict(self,world,before,action,previous_reward):
        address,retained=self.address(world,before,action,previous_reward)
        return tuple(b.outcome_probability(address,action,retained=retained) for b in self._banks)

    def counters(self):return b''.join(b.snapshot() for b in self._banks)

    def info(self):
        counts=[]
        for b in self._banks:counts.extend(struct.unpack('>'+'H'*64,b.snapshot()[4:-32]))
        return {'source_cache_sha256':SOURCE_PIN,'mode':'public_state_and_previous_reward',
            'observations_per_world':len(self._rows[0]),'training_events':4*len(self._rows[0]),
            'outcome_updates':8*len(self._rows[0]),'native_counter_bytes':328,
            'native_counter_sha256':digest(self.counters()),
            'counter_keys_with_both_outcomes':sum(counts[i]>0 and counts[i+1]>0 for i in range(0,len(counts),2)),
            'causal_policy_value_identified':False}

    def checkpoint(self):
        require(len(self._headers)==4,'HISTORY_UNINITIALIZED_CHECKPOINT')
        d={'schema':SCHEMA,'headers_hex':self._headers.hex(),'rows_hex':[r.hex() for r in self._rows],
            'stop':len(self._rows[0]),'native_counters_hex':self.counters().hex(),
            'source_cache_sha256':SOURCE_PIN,'source_class':'PREVIOUSLY_CONSUMED_PUBLIC_SIMULATOR_CACHE',
            'scientific_pass':False,'accepted_native':False}
        raw=canonical(d);require(len(raw)<=MAX_BYTES,'HISTORY_CHECKPOINT_CAPACITY');return raw

    @classmethod
    def restore(cls,raw,expected_sha256):
        require(type(raw) is bytes and 0<len(raw)<=MAX_BYTES and pin(expected_sha256)
                and digest(raw)==expected_sha256,'HISTORY_CHECKPOINT_PIN')
        def unique(pairs):
            d={}
            for k,v in pairs:require(k not in d,'HISTORY_DUPLICATE_KEY');d[k]=v
            return d
        try:
            d=json.loads(raw.decode('ascii'),object_pairs_hook=unique)
            require(type(d) is dict and set(d)=={'schema','headers_hex','rows_hex','stop','native_counters_hex',
                'source_cache_sha256','source_class','scientific_pass','accepted_native'}
                and d['schema']==SCHEMA and d['source_cache_sha256']==SOURCE_PIN
                and d['source_class']=='PREVIOUSLY_CONSUMED_PUBLIC_SIMULATOR_CACHE'
                and d['scientific_pass'] is False and d['accepted_native'] is False
                and canonical(d)==raw,'HISTORY_CHECKPOINT_CONTRACT')
            stop=d['stop'];require(type(stop) is int and stop in (8,16,23),'HISTORY_PREFIX_CONTRACT')
            prefix={k:d[k] for k in ('headers_hex','rows_hex','stop')}
            require(digest(canonical(prefix))==PREFIX_PINS[stop],'HISTORY_SOURCE_PREFIX_PIN')
            obj=cls();obj._headers=bytes.fromhex(d['headers_hex']);obj._rows=tuple(bytes.fromhex(r) for r in d['rows_hex'])
            require(len(obj._headers)==4 and len(obj._rows)==4 and all(len(r)==stop for r in obj._rows),'HISTORY_SHAPE')
            for world,r in enumerate(obj._rows):
                for i,v in enumerate(r):obj._append(world,v,obj._headers[world] if i==0 else r[i-1])
            require(obj.counters().hex()==d['native_counters_hex'] and obj.checkpoint()==raw,'HISTORY_COUNTER_RECONSTRUCTION')
            return obj
        except (ValueError,TypeError,KeyError,UnicodeError,AttributeError,IndexError) as exc:
            raise ValueError('CKAD_NATIVE_HISTORY_CHECKPOINT_REJECTED') from exc
