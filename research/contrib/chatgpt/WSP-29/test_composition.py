import hashlib
import json
import unittest
from composition import Composition,PlasticNand,CONFIGS,route_bits,context
from controls import symbolic,symbolic_predict,feature_table,RAW,trained,predict

def payloads():
    a=PlasticNand();b=PlasticNand();b.rows[0]=[1,0,0];b.rows[1]=[0,1,0];b.rows[-1]=[0,0,0,1,0,0,0,0,0]
    return a.snapshot(),b.snapshot()

class CompositionTests(unittest.TestCase):
    def test_all_generic_routings_match_independent_symbolic_execution(self):
        model=Composition(payloads());model.occupied=1
        for cfg in CONFIGS:
            model.first,model.outer,model.inject=route_bits(cfg)
            for x in map(context,range(8)):self.assertEqual(model.predict(x),symbolic_predict(model.banks,cfg,x))
    def test_numeric_winner_and_frozen_bank_retention(self):
        m=Composition(payloads());old=m.payloads();base=m.base_outputs();target=(0,1,0)
        obs=tuple((context(i),symbolic_predict(m.banks,target,context(i))) for i in (0,1,2,4,7));choice=symbolic(m.banks,obs);m.learn(obs)
        self.assertEqual((m.first,m.outer,m.inject),route_bits(choice));self.assertEqual(m.payloads(),old);self.assertEqual(m.base_outputs(),base)
    def test_erasure_and_disabled_composition(self):
        m=Composition(payloads());self.assertIsNone(m.predict((0,0,0)))
        lesion=Composition(payloads(),0);lesion.occupied=1
        for cfg in CONFIGS:
            lesion.first,lesion.outer,lesion.inject=route_bits(cfg)
            for i in range(8):self.assertEqual(lesion.predict(context(i)),lesion.base_outputs()[cfg[1]][i])
    def test_cold_and_corruption(self):
        m=Composition(payloads()).learn(tuple((context(i),i%2) for i in (0,1,2,4,7)));raw=m.snapshot();r=Composition.restore(raw)
        self.assertEqual(r.snapshot(),raw);self.assertEqual(r.base_outputs(),m.base_outputs())
        for bad in (raw[:-1],raw+b'x',bytearray(raw),raw[:12]+bytes([raw[12]^1])+raw[13:]):
            with self.assertRaises(ValueError):Composition.restore(bad)
    def test_resigned_invalid_routing_and_schema(self):
        d=json.loads(Composition(payloads()).snapshot()[9:-32])
        for key,value in (('first',[1,0]),('occupied',True),('inject',[1,1,0]),('schema','bad'),('extra',0)):
            v=dict(d);v[key]=value;body=json.dumps(v,sort_keys=True,separators=(',',':')).encode();r=b'WSP29'+len(body).to_bytes(4,'big')+body;r+=hashlib.sha256(r).digest()
            with self.assertRaises(ValueError):Composition.restore(r)
    def test_invalid_interfaces_and_immutable_bank(self):
        with self.assertRaises(ValueError):Composition(list(payloads()))
        with self.assertRaises(ValueError):Composition(payloads(),True)
        m=Composition(payloads())
        with self.assertRaises(TypeError):m.banks[0][0][0]=1
        with self.assertRaises(ValueError):m.predict((True,0,1))
        with self.assertRaises(ValueError):m.learn(((context(0),2),)*5)
    def test_gradient_controls_really_fit_and_do_not_learn_unobserved_logits(self):
        obs=tuple((RAW[i],(i//2)%2) for i in (0,1,2,4,7));w,n,loss=trained(obs,8)
        self.assertGreater(n,0);self.assertLessEqual(loss,.01)
        self.assertTrue(all(predict(w,x)==y for x,y in obs));self.assertEqual([w[i] for i in (3,5,6)],[0.,0.,0.])
    def test_reused_feature_layout_uses_only_inferred_module_tables(self):
        m=Composition(payloads());table=feature_table(m.base_outputs());self.assertTrue(all(len(x)==20 for x in table))
        for i in range(8):
            self.assertEqual(table[i][12:],RAW[i])
            for j,cfg in enumerate(CONFIGS):self.assertEqual(table[i][j],symbolic_predict(m.banks,cfg,context(i)))
if __name__=='__main__':unittest.main()
