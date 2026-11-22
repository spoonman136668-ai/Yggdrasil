"""Opt-in source-bound composition of frozen native knowledge and priors.

Readout only: no training-rule call, environment action or controller. Known
answers retain precedence; prior-based outputs remain explicitly provisional.
Byte/source consistency does not authenticate original-world causal authority.
"""
import json
from yggdrasil.native_context_accumulator import NativeContextAccumulator
from yggdrasil.native_context_quarantine import NativeContextQuarantine
from yggdrasil.native_prior_hypothesis import NativePriorHypothesis,input_order
from yggdrasil.native_context_basis import canonical,digest,pin,require,feature_row,SOURCE_MODE
from yggdrasil.public_causal_cells import PublicCausalCells

SCHEMA='yggdrasil.ckad.native-knowledge-readout.v1'
MAX_BYTES=12*1024*1024
IDENTIFIED='IDENTIFIED_WITHIN_DECLARED_CLASS'
PROVISIONAL='PROVISIONAL_HYPOTHESIS'
UNKNOWN='UNKNOWN'


class NativeKnowledgeReadout:
    __slots__=('_base','_priors')

    def __init__(self,base):
        require(type(base) is NativeContextQuarantine,'READOUT_NATIVE_TYPE')
        self._base=base;self._priors=(None,)*16

    def with_prior(self,address,raw,expected_sha256,*,retained=False):
        slot=PublicCausalCells._address(address,retained)
        prior=NativePriorHypothesis.restore(raw,expected_sha256)
        native=self._base._native;bits=native._model.context_bits
        require(not self._base._failures[slot],'READOUT_QUARANTINED_SOURCE')
        p=native._model._profiles[slot]
        require(prior._bits==bits and prior._n==p.unique_inputs,'READOUT_SOURCE_DIMENSIONS')
        existing=self._priors[slot]
        if existing is not None:
            require(existing.checkpoint()==raw,'READOUT_PRIOR_ALREADY_BOUND')
            return self
        masks=sorted((x for x in range(1<<(bits+1)) if native._seen[slot]&(1<<x)),key=input_order)
        rows=[]
        for x in masks:
            y=self._base.predict(address,x&((1<<bits)-1),x>>bits,retained=retained)
            require(y is not None,'READOUT_UNIDENTIFIED_OBSERVATION')
            rows.append([x&((1<<bits)-1),x>>bits,y])
        # Reconstruct only the deterministic source-view encoding. No learned
        # hypothesis is fitted/modified, and no outside outcome source is read.
        view=NativeContextAccumulator(bits).stage_update(0,rows,digest(canonical(rows)),max_degree=bits+1)
        require(view.checkpoint_sha256==prior._source,'READOUT_WRONG_SOURCE_BINDING')
        split=3*len(rows)//4;errors=[0,0]
        for i,(c,a,y) in enumerate(rows):
            predicted=(prior._weights&feature_row(c|(a<<bits),bits+1)).bit_count()&1
            errors[int(i>=split)]+=predicted!=y
        require(errors==[prior._fit_errors,prior._calibration_errors],'READOUT_FALSE_FIT_METADATA')
        candidate=NativeKnowledgeReadout(self._base)
        candidate._priors=self._priors[:slot]+(prior,)+self._priors[slot+1:]
        return candidate

    def readout(self,address,context,action,*,retained=False):
        value=self._base.predict(address,context,action,retained=retained)
        slot=PublicCausalCells._address(address,retained)
        status=IDENTIFIED if value is not None else UNKNOWN
        if value is None and self._priors[slot] is not None:
            value=self._priors[slot].predict_provisional(context,action)
            if value is not None:status=PROVISIONAL
        return {'value':value,'status':status,'source_mode':SOURCE_MODE,'accepted_native':False}

    def checkpoint(self):
        raw=canonical({'schema':SCHEMA,'native_knowledge_ascii':self._base.checkpoint().decode('ascii'),
            'prior_hypotheses_ascii':[p.checkpoint().decode('ascii') if p is not None else None for p in self._priors],
            'source_mode':SOURCE_MODE,'accepted_native':False,'scientific_pass':False})
        require(len(raw)<=MAX_BYTES,'READOUT_CHECKPOINT_CAPACITY');return raw

    @classmethod
    def restore(cls,raw,expected_sha256):
        require(type(raw) is bytes and 0<len(raw)<=MAX_BYTES and pin(expected_sha256)
                and digest(raw)==expected_sha256,'READOUT_CHECKPOINT_PIN')
        def unique(pairs):
            d={}
            for k,v in pairs:require(k not in d,'READOUT_DUPLICATE_KEY');d[k]=v
            return d
        try:
            d=json.loads(raw.decode('ascii'),object_pairs_hook=unique)
            require(type(d) is dict and set(d)=={'schema','native_knowledge_ascii','prior_hypotheses_ascii',
                'source_mode','accepted_native','scientific_pass'} and d['schema']==SCHEMA
                and d['source_mode']==SOURCE_MODE and d['accepted_native'] is False
                and d['scientific_pass'] is False and canonical(d)==raw,'READOUT_CHECKPOINT_CONTRACT')
            base=d['native_knowledge_ascii'].encode('ascii')
            candidate=cls(NativeContextQuarantine.restore(base,digest(base)))
            priors=d['prior_hypotheses_ascii']
            require(type(priors) is list and len(priors)==16,'READOUT_PRIOR_SLOTS')
            for slot,p in enumerate(priors):
                if p is None:continue
                require(type(p) is str,'READOUT_PRIOR_BYTES')
                prior=p.encode('ascii');a,r=(slot,False) if slot<7 else (slot-7,True)
                candidate=candidate.with_prior(a,prior,digest(prior),retained=r)
            require(candidate.checkpoint()==raw,'READOUT_COLD_BYTES');return candidate
        except (ValueError,TypeError,KeyError,UnicodeError,AttributeError) as exc:
            raise ValueError('CKAD_NATIVE_READOUT_CHECKPOINT_REJECTED') from exc
