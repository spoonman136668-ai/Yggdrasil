"""Optional PROVISIONAL readout learned from retained native observations.

Reuses WSP147's strict-gain16-edit rule at the native context width. Its sparse
bias is supplied, not discovered. Calibration is not a confidence guarantee.
This never changes the identified-only native readout or accepted model state.
"""
import hashlib
import json
import struct
from yggdrasil.native_context_accumulator import NativeContextAccumulator
from yggdrasil.native_context_basis import canonical,digest,pin,require,feature_row,SOURCE_MODE
from yggdrasil.public_causal_cells import PublicCausalCells

SCHEMA='yggdrasil.ckad.native-prior-hypothesis.v1'
MAX_EDITS=16
MAX_BYTES=32768
RULE='WSP147_STRICT_GAIN16_GENERIC_MONOMIALS'


def input_order(mask):
    return hashlib.sha256(f'ckad09:input-order:{mask}'.encode('ascii')).digest()


def program_weights(rows,binary_inputs):
    """Original fixed greedy rule, generalized width/count; no new search."""
    require(type(binary_inputs) is int and 2<=binary_inputs<=11,'PRIOR_INPUT_BITS')
    require(type(rows) in (list,tuple) and 0<len(rows)<=2048
            and all(type(r) in (list,tuple) and len(r)==2 and type(r[0]) is int
                    and 0<=r[0]<1<<binary_inputs and type(r[1]) is int and r[1] in (0,1) for r in rows)
            and len({r[0] for r in rows})==len(rows),'PRIOR_ROWS')
    xs=tuple(x for x,y in rows);residual=sum(y<<i for i,(x,y) in enumerate(rows))
    columns=tuple(sum(int((x&m)==m)<<i for i,x in enumerate(xs)) for m in range(1<<binary_inputs))
    weights=0;writes=[]
    for _ in range(MAX_EDITS):
        best=None;bestkey=None
        for m,sign in enumerate(columns):
            gain=2*(residual&sign).bit_count()-sign.bit_count()
            if gain<=0:continue
            key=(-gain,m.bit_count(),m)
            if bestkey is None or key<bestkey:bestkey=key;best=m
        if best is None:break
        residual^=columns[best];weights^=1<<best;writes.append(best)
    return weights,tuple(writes),residual.bit_count()


class NativePriorHypothesis:
    """Separate prior-assumed predictions, never logically certified effects."""
    __slots__=('_bits','_weights','_writes','_source','_n','_fit_errors','_calibration_errors')

    @classmethod
    def fit_checkpoint(cls,raw,expected_sha256):
        source=NativeContextAccumulator.restore(raw,expected_sha256)
        p=source._model._profiles[0];bits=source._model.context_bits
        require(p.degree==bits+1 and all(x.source_records==0 for x in source._model._profiles[1:]),
                'PRIOR_REQUIRES_ISOLATED_COMPLETE_BASIS_VIEW')
        n=p.unique_inputs
        require(8<=n<=2048 and n%4==0 and p.source_records==n,'PRIOR_VIEW_COUNT')
        masks=sorted((x for x in range(1<<(bits+1)) if source._seen[0]&(1<<x)),key=input_order)
        rows=[(x,source.predict(0,x&((1<<bits)-1),x>>bits)) for x in masks]
        require(all(type(y) is int and y in (0,1) for x,y in rows),'PRIOR_SOURCE_WITNESS')
        fit_n=3*n//4
        weights,writes,errors=program_weights(rows[:fit_n],bits+1)
        calibration=sum(((weights&feature_row(x,bits+1)).bit_count()&1)!=y for x,y in rows[fit_n:])
        model=cls();model._bits=bits;model._weights=weights;model._writes=writes
        model._source=expected_sha256;model._n=n;model._fit_errors=errors;model._calibration_errors=calibration
        return model

    @property
    def eligible(self):
        return self._fit_errors==0 and self._calibration_errors==0

    def info(self):
        return {'observations':self._n,'fit_observations':3*self._n//4,'calibration_observations':self._n//4,
            'fit_errors':self._fit_errors,'calibration_errors':self._calibration_errors,'writes':list(self._writes),
            'eligible':self.eligible,'status':'PROVISIONAL_ONLY','source_checkpoint_sha256':self._source}

    def predict_provisional(self,context,action):
        require(type(context) is int and 0<=context<1<<self._bits,'PRIOR_CONTEXT')
        PublicCausalCells._bit(action,'ACTION')
        if not self.eligible:return None
        return (self._weights&feature_row(context|(action<<self._bits),self._bits+1)).bit_count()&1

    def checkpoint(self):
        count=1<<(self._bits+1)
        weights=struct.pack('<'+'f'*count,*(float((self._weights>>m)&1) for m in range(count))).hex()
        raw=canonical({'schema':SCHEMA,'context_bits':self._bits,'weights_float32_le':weights,
            'writes':self._writes,'source_checkpoint_sha256':self._source,'observations':self._n,
            'fit_errors':self._fit_errors,'calibration_errors':self._calibration_errors,
            'rule':RULE,'status':'PROVISIONAL_ONLY','source_mode':SOURCE_MODE,
            'accepted_native':False,'scientific_pass':False})
        require(len(raw)<=MAX_BYTES,'PRIOR_CHECKPOINT_CAPACITY')
        return raw

    @classmethod
    def restore(cls,raw,expected_sha256):
        require(type(raw) is bytes and 0<len(raw)<=MAX_BYTES and pin(expected_sha256)
                and digest(raw)==expected_sha256,'PRIOR_CHECKPOINT_PIN')
        def unique(pairs):
            d={}
            for k,v in pairs:require(k not in d,'PRIOR_DUPLICATE_KEY');d[k]=v
            return d
        try:
            d=json.loads(raw.decode('ascii'),object_pairs_hook=unique)
            require(type(d) is dict and set(d)=={'schema','context_bits','weights_float32_le','writes',
                'source_checkpoint_sha256','observations','fit_errors','calibration_errors','rule','status',
                'source_mode','accepted_native','scientific_pass'} and d['schema']==SCHEMA and d['rule']==RULE
                and d['status']=='PROVISIONAL_ONLY' and d['source_mode']==SOURCE_MODE
                and d['accepted_native'] is False and d['scientific_pass'] is False and canonical(d)==raw,
                'PRIOR_CHECKPOINT_CONTRACT')
            bits=d['context_bits'];require(type(bits) is int and 1<=bits<=10,'PRIOR_BITS')
            n=d['observations'];require(type(n) is int and 8<=n<=min(2048,1<<(bits+1)) and n%4==0,'PRIOR_COUNTS')
            require(type(d['fit_errors']) is int and 0<=d['fit_errors']<=3*n//4
                    and type(d['calibration_errors']) is int and 0<=d['calibration_errors']<=n//4
                    and pin(d['source_checkpoint_sha256']),'PRIOR_SOURCE_COUNTS')
            count=1<<(bits+1);packed=d['weights_float32_le']
            require(type(packed) is str and len(packed)==8*count,'PRIOR_WEIGHTS')
            values=struct.unpack('<'+'f'*count,bytes.fromhex(packed))
            require(all(v in (0.,1.) for v in values) and struct.pack('<'+'f'*count,*(float(int(v)) for v in values)).hex()==packed,'PRIOR_BINARY_WEIGHTS')
            writes=d['writes'];require(type(writes) is list and len(writes)<=MAX_EDITS
                and all(type(m) is int and 0<=m<count for m in writes),'PRIOR_EDITS')
            weights=0
            for m in writes:weights^=1<<m
            require(weights==sum(int(v)<<m for m,v in enumerate(values)),'PRIOR_TRACE_WEIGHTS')
            model=cls();model._bits=bits;model._weights=weights;model._writes=tuple(writes)
            model._source=d['source_checkpoint_sha256'];model._n=n
            model._fit_errors=d['fit_errors'];model._calibration_errors=d['calibration_errors']
            require(model.checkpoint()==raw,'PRIOR_COLD_BYTES');return model
        except (ValueError,TypeError,KeyError,UnicodeError,AttributeError,struct.error) as exc:
            raise ValueError('CKAD_NATIVE_PRIOR_CHECKPOINT_REJECTED') from exc
