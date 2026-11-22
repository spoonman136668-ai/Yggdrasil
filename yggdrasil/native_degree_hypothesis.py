"""Evidence-selected native polynomial representation, research only.

Choose a class using fitting constraints alone; calibrate once afterward.
The generic degree ordering is an inductive assumption, not a family oracle.
"""
import json
from yggdrasil.native_context_basis import NativeContextBasis,canonical,digest,pin,require,SOURCE_MODE
from yggdrasil.native_context_accumulator import NativeContextAccumulator
from yggdrasil.native_prior_hypothesis import input_order

SCHEMA='yggdrasil.ckad.native-degree-hypothesis.v1'
MAX_BYTES=9*1024*1024


class NativeDegreeHypothesis:
    __slots__=('_native','_source','_n','_fit_sha','_calibration_sha','_wrong','_unknown')

    @classmethod
    def fit_checkpoint(cls,raw,expected_sha256):
        source=NativeContextAccumulator.restore(raw,expected_sha256)
        p=source._model._profiles[0];bits=source._model.context_bits
        require(p.degree==bits+1 and all(x.source_records==0 for x in source._model._profiles[1:]),
                'DEGREE_REQUIRES_ISOLATED_COMPLETE_BASIS_VIEW')
        n=p.unique_inputs
        require(8<=n<=2048 and n%4==0 and p.source_records==n,'DEGREE_VIEW_COUNT')
        masks=sorted((x for x in range(1<<(bits+1)) if source._seen[0]&(1<<x)),key=input_order)
        rows=[[x&((1<<bits)-1),x>>bits,source.predict(0,x&((1<<bits)-1),x>>bits)] for x in masks]
        require(all(type(y) is int and y in (0,1) for c,a,y in rows),'DEGREE_SOURCE_WITNESS')
        fit=rows[:3*n//4];calibration=rows[3*n//4:];fit_sha=digest(canonical(fit))
        chosen=None
        for degree in range(1,bits+2):
            try:chosen=NativeContextBasis(bits).stage_fit(0,fit,fit_sha,max_degree=degree)
            except ValueError as exc:
                if str(exc)!='CKAD_NATIVE_MODEL_CLASS_INADEQUATE':raise
                continue
            break  # Calibration NEVER controls the class search.
        require(chosen is not None,'DEGREE_COMPLETE_CLASS_FAILED')
        predictions=[chosen.predict(0,c,a) for c,a,y in calibration]
        model=cls();model._native=chosen;model._source=expected_sha256;model._n=n
        model._fit_sha=fit_sha;model._calibration_sha=digest(canonical(calibration))
        model._wrong=sum(p is not None and p!=row[2] for p,row in zip(predictions,calibration))
        model._unknown=sum(p is None for p in predictions)
        return model

    @property
    def eligible(self):return self._wrong==0 and self._unknown==0

    def info(self):
        degree=self._native._profiles[0].degree
        return {'observations':self._n,'fit_observations':3*self._n//4,'calibration_observations':self._n//4,
            'selected_degree':degree,'rejected_fit_degrees':list(range(1,degree)),
            'calibration_wrong':self._wrong,'calibration_unidentified':self._unknown,'eligible':self.eligible,
            'status':'PROVISIONAL_ONLY','source_checkpoint_sha256':self._source,
            'fit_rows_sha256':self._fit_sha,'calibration_rows_sha256':self._calibration_sha}

    def predict_provisional(self,context,action):
        # Validate both inputs even when calibration denied the entire model.
        self._native._context(context)
        from yggdrasil.public_causal_cells import PublicCausalCells
        PublicCausalCells._bit(action,'ACTION')
        return self._native.predict(0,context,action) if self.eligible else None

    def checkpoint(self):
        raw=canonical({'schema':SCHEMA,'native_basis_ascii':self._native.checkpoint().decode('ascii'),
            'info':self.info(),'source_mode':SOURCE_MODE,'accepted_native':False,'scientific_pass':False})
        require(len(raw)<=MAX_BYTES,'DEGREE_CHECKPOINT_CAPACITY')
        return raw

    @classmethod
    def restore(cls,raw,expected_sha256):
        require(type(raw) is bytes and 0<len(raw)<=MAX_BYTES and pin(expected_sha256)
                and digest(raw)==expected_sha256,'DEGREE_CHECKPOINT_PIN')
        def unique(pairs):
            d={}
            for k,v in pairs:
                require(k not in d,'DEGREE_DUPLICATE_JSON_KEY');d[k]=v
            return d
        try:
            d=json.loads(raw.decode('ascii'),object_pairs_hook=unique)
            require(type(d) is dict and set(d)=={'schema','native_basis_ascii','info','source_mode','accepted_native','scientific_pass'}
                and d['schema']==SCHEMA and d['source_mode']==SOURCE_MODE and d['accepted_native'] is False
                and d['scientific_pass'] is False and canonical(d)==raw,'DEGREE_CHECKPOINT_CONTRACT')
            base=d['native_basis_ascii'].encode('ascii');native=NativeContextBasis.restore(base,digest(base));p=native._profiles[0]
            i=d['info'];n=i['observations']
            require(type(n) is int and 8<=n<=2048 and n%4==0 and p.source_records==3*n//4
                and p.unique_inputs==3*n//4 and all(x.source_records==0 for x in native._profiles[1:]),'DEGREE_FIT_COUNTS')
            require(all(pin(i[k]) for k in ('source_checkpoint_sha256','fit_rows_sha256','calibration_rows_sha256'))
                and p.source_sha256==i['fit_rows_sha256'],'DEGREE_SOURCE_BINDING')
            wrong=i['calibration_wrong'];unknown=i['calibration_unidentified']
            require(type(wrong) is int and type(unknown) is int and min(wrong,unknown)>=0
                and wrong+unknown<=n//4,'DEGREE_CALIBRATION_COUNTS')
            m=cls();m._native=native;m._source=i['source_checkpoint_sha256'];m._n=n
            m._fit_sha=i['fit_rows_sha256'];m._calibration_sha=i['calibration_rows_sha256'];m._wrong=wrong;m._unknown=unknown
            require(m.info()==i and m.checkpoint()==raw,'DEGREE_COLD_CONTRACT')
            return m
        except (ValueError,TypeError,KeyError,UnicodeError,AttributeError) as exc:
            raise ValueError('CKAD_NATIVE_DEGREE_CHECKPOINT_REJECTED') from exc
