import hashlib
import json
import unittest
from fact_model import FactModel,PlasticNand,context,QUESTIONS,SOURCE_KNOWN,PUBLIC,MODES
from control_baseline import FitCache,RAW

def make(mode='no_query'):
    a=PlasticNand();b=PlasticNand();b.rows[-1]=[0,1,0,0,0,0,0,0,0]
    src=tuple(tuple((context(i),(i>>j)&1) for i in SOURCE_KNOWN) for j in (0,1));target=tuple((context(i),i%2) for i in PUBLIC)
    return FactModel((a.snapshot(),b.snapshot()),src,target,mode)
class FactTests(unittest.TestCase):
    def test_faithful_known_facts_and_local_source_update(self):
        m=make('source_first');before=m.effective_tables();raw=m.snapshot();q=m.query();self.assertEqual(q,('s',0,5));m.answer(q,1-before[0][5])
        self.assertEqual(m.source_labels[0][5],1-before[0][5])
        for b in range(2):
            for i in range(8):
                if (b,i)!=(0,5):self.assertEqual(m.effective_tables()[b][i],before[b][i])
        for i in PUBLIC:self.assertEqual(m.predict(context(i)),i%2)
    def test_planner_uses_only_live_evidence_and_does_not_mutate_it(self):
        m=make();raw=m.snapshot();p=m.plan();self.assertEqual(m.snapshot(),raw);self.assertEqual(len(p),7)
        for mode in MODES:
            child=m.clone(mode);self.assertEqual(child.plan(),p);self.assertEqual(child.plan_evaluations,0)
        self.assertEqual(m.plan_evaluations,1)
    def test_query_budget_unsolicited_and_contradiction_reject_without_mutation(self):
        m=make('source_first');raw=m.snapshot()
        with self.assertRaises(ValueError):m.answer(QUESTIONS[1],0)
        self.assertEqual(m.snapshot(),raw);m.answer(QUESTIONS[0],0);after=m.snapshot();m.answer(QUESTIONS[0],0);self.assertEqual(m.snapshot(),after)
        for q,y in ((QUESTIONS[1],0),(QUESTIONS[0],1)):
            with self.assertRaises(ValueError):m.answer(q,y)
            self.assertEqual(m.snapshot(),after)
        self.assertIsNone(m.query())
    def test_cold_snapshot_outputs_and_cache_reconstruction(self):
        m=make('connection_impact');q=m.query();m.answer(q,0);raw=m.snapshot();r=FactModel.restore(raw)
        self.assertEqual(r.snapshot(),raw);self.assertEqual(r._fallback,m._fallback);self.assertIsNone(r._plan)
        self.assertEqual([r.predict(context(i)) for i in range(8)],[m.predict(context(i)) for i in range(8)])
    def test_tamper_noncanonical_and_unknown_label_contamination(self):
        m=make();raw=m.snapshot()
        for bad in (raw[:-1],raw+b'x',bytearray(raw),raw[:12]+bytes([raw[12]^1])+raw[13:]):
            with self.assertRaises(ValueError):FactModel.restore(bad)
        d=json.loads(raw[9:-32])
        for key,value in (('query_used',True),('mode','bad'),('extra',0),('occupied',0)):
            v=dict(d);v[key]=value;body=json.dumps(v,sort_keys=True,separators=(',',':')).encode();r=b'WSP31'+len(body).to_bytes(4,'big')+body;r+=hashlib.sha256(r).digest()
            with self.assertRaises(ValueError):FactModel.restore(r)
        m.source_labels[0][5]=1
        with self.assertRaises(ValueError):m.snapshot()
    def test_corrupt_derived_fallback_is_not_serialized_as_knowledge(self):
        m=make();f=[list(x) for x in m._fallback];f[0][5]^=1;m._fallback=tuple(tuple(x) for x in f)
        with self.assertRaises(ValueError):m.snapshot()
    def test_actual_fact_readout_and_noquery_reject(self):
        m=make()
        for b in range(2):
            for i in SOURCE_KNOWN:self.assertEqual(m.effective_tables()[b][i],(i>>b)&1)
        with self.assertRaises(ValueError):m.answer(QUESTIONS[0],0)
        with self.assertRaises(ValueError):make('source_first').answer(('s',False,5),0)
        with self.assertRaises(ValueError):m.predict((True,0,1))
    def test_fit_cache_hits_only_exact_semantic_inputs(self):
        c=FitCache();obs=tuple((RAW[i],i%2) for i in PUBLIC);context_key={'source':'x','facts':[0,1],'representation':'raw'}
        a=c.fit(obs,8,context_key);b=c.fit(obs,8,context_key);self.assertEqual(a,b);self.assertEqual((c.logical_fits,c.fresh_fits,c.hits),(2,1,1))
        c.fit(obs,8,{**context_key,'facts':[1,1]});self.assertEqual(c.fresh_fits,2)
        other=tuple((x,1-y) for x,y in obs);c.fit(other,8,context_key);self.assertEqual(c.fresh_fits,3)
if __name__=='__main__':unittest.main()
