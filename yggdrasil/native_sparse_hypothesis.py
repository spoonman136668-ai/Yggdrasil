"""Bounded conventional sparse compilation into existing native ANF weights.

The sparse prior and integer solver are supplied training machinery, not novel
cognition or causal certification. Calibration is evaluated once after fitting.
No solver is required to restore or read the native numeric checkpoint.
"""
import json
import struct
import warnings

from yggdrasil.native_context_basis import canonical, digest, pin, require, feature_row, SOURCE_MODE
from yggdrasil.native_context_accumulator import NativeContextAccumulator
from yggdrasil.native_prior_hypothesis import input_order
from yggdrasil.public_causal_cells import PublicCausalCells

SCHEMA = 'yggdrasil.ckad.native-sparse-hypothesis.v1'
RULE = 'CONVENTIONAL_MINIMUM_SUPPORT_GF2_MILP8'
MAX_BYTES = 32768
MAX_WEIGHTS = 8


class NativeSparseHypothesis:
    __slots__ = ('_bits','_weights','_source','_n','_fit_errors','_cal_errors','_status')

    @classmethod
    def fit_checkpoint(cls, raw, expected_sha256):
        import time
        import numpy as np
        from scipy.optimize import milp, Bounds, LinearConstraint
        from scipy.sparse import coo_array, hstack, vstack, eye, csr_array

        source = NativeContextAccumulator.restore(raw, expected_sha256)
        bits = source._model.context_bits; p = source._model._profiles[0]
        require(p.degree == bits+1 and all(x.source_records == 0 for x in source._model._profiles[1:]),
                'SPARSE_ISOLATED_COMPLETE_BASIS')
        n = p.unique_inputs
        require(8 <= n <= 2048 and n%4 == 0 and p.source_records == n, 'SPARSE_VIEW_COUNT')
        masks = sorted((x for x in range(1 << (bits+1)) if source._seen[0] & (1 << x)), key=input_order)
        ys = [source.predict(0,x & ((1<<bits)-1),x>>bits) for x in masks]
        require(all(type(y) is int and y in (0,1) for y in ys), 'SPARSE_SOURCE_WITNESS')
        fit_n = 3*n//4; count = 1 << (bits+1)
        ii=[];jj=[]
        for i,x in enumerate(masks[:fit_n]):
            jj.append(0);ii.append(i);sub=x
            while sub:
                ii.append(i);jj.append(sub);sub=(sub-1)&x
        matrix=coo_array((np.ones(len(ii)),(np.array(ii,dtype=np.int32),np.array(jj,dtype=np.int32))),shape=(fit_n,count)).tocsc()
        parity=hstack((matrix,-2*eye(fit_n,format='csc')),format='csc')
        cap=csr_array(np.r_[np.ones(count),np.zeros(fit_n)].reshape(1,-1))
        constraints=vstack((parity,cap),format='csc')
        lower=np.r_[np.asarray(ys[:fit_n],dtype=float),0.]
        upper=np.r_[np.asarray(ys[:fit_n],dtype=float),float(MAX_WEIGHTS)]
        objective=np.r_[np.ones(count),np.zeros(fit_n)]
        start=time.monotonic()
        # SciPy forwards these explicit HiGHS options. Keep only its known
        # forwarding notice quiet; solver failures are retained as outcomes.
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore',message='Unrecognized options detected:.*')
            result=milp(objective,integrality=np.ones(count+fit_n,dtype=np.uint8),
                bounds=Bounds(np.zeros(count+fit_n),np.r_[np.ones(count),np.full(fit_n,4.)]),
                constraints=LinearConstraint(constraints,lower,upper),
                options={'presolve':True,'time_limit':30.,'node_limit':100000,
                         'mip_rel_gap':0.,'threads':1,'random_seed':0})
        seconds=time.monotonic()-start;status=int(result.status);weights=0
        if status==0:
            require(result.x is not None and all(abs(v-round(v))<=1e-6 for v in result.x),
                    'SPARSE_NONINTEGRAL_SOLVER')
            chosen=[m for m,v in enumerate(result.x[:count]) if round(v)==1]
            require(len(chosen)<=MAX_WEIGHTS and all(round(v) in (0,1) for v in result.x[:count]),
                    'SPARSE_WEIGHT_CAPACITY')
            weights=sum(1<<m for m in chosen)
        predictions=[(weights & feature_row(x,bits+1)).bit_count() & 1 for x in masks]
        obj=cls();obj._bits=bits;obj._weights=weights;obj._source=expected_sha256;obj._n=n
        obj._fit_errors=sum(p!=y for p,y in zip(predictions[:fit_n],ys[:fit_n]))
        obj._cal_errors=sum(p!=y for p,y in zip(predictions[fit_n:],ys[fit_n:]))
        obj._status=status
        if status==0:require(obj._fit_errors==0,'SPARSE_INVALID_OPTIMAL_WEIGHTS')
        def number(name):
            v=getattr(result,name,None)
            return None if v is None or not np.isfinite(v) else float(v)
        cost={'solver_seconds':seconds,'solver_status':status,'solver_nodes':number('mip_node_count'),
              'solver_primal_bound':number('fun'),'solver_dual_bound':number('mip_dual_bound')}
        return obj,cost

    @property
    def eligible(self):return self._status==0 and self._fit_errors==self._cal_errors==0

    def info(self):
        return {'observations':self._n,'fit_observations':3*self._n//4,'calibration_observations':self._n//4,
            'fit_errors':self._fit_errors,'calibration_errors':self._cal_errors,'solver_status':self._status,
            'active_weights':self._weights.bit_count(),'eligible':self.eligible,
            'status':'PROVISIONAL_ONLY','source_checkpoint_sha256':self._source,'rule':RULE}

    def predict_provisional(self,context,action):
        require(type(context) is int and 0<=context<1<<self._bits,'SPARSE_CONTEXT')
        PublicCausalCells._bit(action,'ACTION')
        return ((self._weights & feature_row(context|(action<<self._bits),self._bits+1)).bit_count()&1
                if self.eligible else None)

    def checkpoint(self):
        count=1<<(self._bits+1)
        weights=struct.pack('<'+'f'*count,*(float((self._weights>>m)&1) for m in range(count))).hex()
        raw=canonical({'schema':SCHEMA,'context_bits':self._bits,'weights_float32_le':weights,
            'info':self.info(),'source_mode':SOURCE_MODE,'accepted_native':False,'scientific_pass':False})
        require(len(raw)<=MAX_BYTES,'SPARSE_CHECKPOINT_CAPACITY');return raw

    @classmethod
    def restore(cls,raw,expected_sha256):
        require(type(raw) is bytes and 0<len(raw)<=MAX_BYTES and pin(expected_sha256)
                and digest(raw)==expected_sha256,'SPARSE_CHECKPOINT_PIN')
        def unique(pairs):
            d={}
            for k,v in pairs:require(k not in d,'SPARSE_DUPLICATE_KEY');d[k]=v
            return d
        try:
            d=json.loads(raw.decode('ascii'),object_pairs_hook=unique)
            require(type(d) is dict and set(d)=={'schema','context_bits','weights_float32_le','info',
                    'source_mode','accepted_native','scientific_pass'} and d['schema']==SCHEMA
                    and d['source_mode']==SOURCE_MODE and d['accepted_native'] is False
                    and d['scientific_pass'] is False and canonical(d)==raw,'SPARSE_CHECKPOINT_CONTRACT')
            bits=d['context_bits'];require(type(bits) is int and 1<=bits<=10,'SPARSE_BITS')
            count=1<<(bits+1);packed=d['weights_float32_le']
            require(type(packed) is str and len(packed)==8*count,'SPARSE_WEIGHTS')
            values=struct.unpack('<'+'f'*count,bytes.fromhex(packed))
            require(all(v in (0.,1.) for v in values)
                    and struct.pack('<'+'f'*count,*(float(int(v)) for v in values)).hex()==packed,'SPARSE_WEIGHT_BITS')
            i=d['info'];n=i['observations'];status=i['solver_status']
            require(type(n) is int and 8<=n<=min(2048,count) and n%4==0 and type(status) is int
                    and status in (0,1,2,3,4) and pin(i['source_checkpoint_sha256']), 'SPARSE_COUNTS')
            obj=cls();obj._bits=bits;obj._weights=sum(int(v)<<m for m,v in enumerate(values))
            require(obj._weights.bit_count()<=MAX_WEIGHTS and (status==0 or obj._weights==0),'SPARSE_FAILED_WEIGHTS')
            obj._n=n;obj._status=status;obj._source=i['source_checkpoint_sha256']
            for key,limit in (('fit_errors',3*n//4),('calibration_errors',n//4)):
                require(type(i[key]) is int and 0<=i[key]<=limit,'SPARSE_ERROR_COUNT')
            obj._fit_errors=i['fit_errors'];obj._cal_errors=i['calibration_errors']
            require((status!=0 or obj._fit_errors==0) and obj.info()==i and obj.checkpoint()==raw,
                    'SPARSE_COLD_CONTRACT')
            return obj
        except (ValueError,TypeError,KeyError,UnicodeError,AttributeError,struct.error) as exc:
            raise ValueError('CKAD_NATIVE_SPARSE_CHECKPOINT_REJECTED') from exc
