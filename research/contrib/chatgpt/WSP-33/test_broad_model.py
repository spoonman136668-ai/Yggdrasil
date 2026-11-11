import hashlib
import json
import unittest
from broad_model import BroadModel,PlasticNand,context,SOURCE_KNOWN,PUBLIC,QUESTIONS,MODES,BUDGETS,MAGIC
from run_dev import symbolic

def make(mode='source_four'):
    a=PlasticNand();b=PlasticNand();b.rows[-1]=[0,1,0,0,0,0,0,0,0]
    src=tuple(tuple((context(i),(i>>j)&1) for i in SOURCE_KNOWN) for j in (0,1))
    return BroadModel((a.snapshot(),b.snapshot()),src,tuple((context(i),i%2) for i in PUBLIC),mode)

class BroadTests(unittest.TestCase):
    def test_two_facts_survive_cold_boundary_and_every_original_fact(self):
        m=make();banks=m.payloads();acquired=[]
        for _ in range(4):
            q=m.query();y=1-m._source(q[1],context(q[2]));before=m.effective_tables();m.answer(q,y);acquired.append((q,y))
            for b in range(2):
                for i in range(8):
                    if (b,i)!=(q[1],q[2]):self.assertEqual(m.effective_tables()[b][i],before[b][i])
            raw=m.snapshot();m=BroadModel.restore(raw);self.assertEqual(m.snapshot(),raw)
            for qq,yy in acquired:self.assertEqual(m._source(qq[1],context(qq[2])),yy)
            for b in range(2):
                for i in SOURCE_KNOWN:self.assertEqual(m._source(b,context(i)),(i>>b)&1)
            for i in PUBLIC:self.assertEqual(m.predict(context(i)),i%2)
            self.assertEqual(m.payloads(),banks)
        self.assertIsNone(m.query())
    def test_budget_contradiction_unsolicited_and_replay_atomic(self):
        for mode in MODES:
            m=make(mode);acquired=[]
            for _ in range(BUDGETS[mode]):
                q=m.query();raw=m.snapshot();other=next((qq for qq in QUESTIONS if qq!=q and not m.source_known[qq[1]][qq[2]]),('t',0,3))
                with self.assertRaises(ValueError):m.answer(other,0)
                self.assertEqual(m.snapshot(),raw);m.answer(q,1);acquired.append(q)
                raw=m.snapshot();m.answer(q,1);self.assertEqual(m.snapshot(),raw)
                with self.assertRaises(ValueError):m.answer(q,0)
                self.assertEqual(m.snapshot(),raw)
            raw=m.snapshot();self.assertIsNone(m.query());other=next((q for q in QUESTIONS if not m.source_known[q[1]][q[2]]),('t',0,3))
            with self.assertRaises(ValueError):m.answer(other,0)
            self.assertEqual(m.snapshot(),raw)
    def test_planning_counterfactuals_do_not_write_and_known_questions_excluded(self):
        m=make();raw=m.snapshot();first=m.plan();self.assertEqual(m.snapshot(),raw)
        self.assertEqual(m.plan(),first);self.assertEqual(m.plan_evaluations,1)
        q=m.query();m.answer(q,0);self.assertIsNone(m._plan);scores=m.plan()
        self.assertEqual(scores[QUESTIONS.index(q)],-1);self.assertNotEqual(m.query(),q)
        cold=BroadModel.restore(m.snapshot());self.assertEqual(cold.query(),m.query())
    def test_only_actual_facts_affect_questions_and_readout(self):
        a=make();b=make();self.assertEqual(a.query(),b.query())
        for y in (0,1):
            aa=a.clone();bb=b.clone();q=aa.query();aa.answer(q,y);bb.answer(q,y)
            self.assertEqual(aa.query(),bb.query());self.assertEqual(aa.snapshot(),bb.snapshot())
    def test_symbolic_control_agrees_across_all_answers(self):
        for mode in MODES:
            for bits in range(16):
                m=make(mode)
                for step in range(BUDGETS[mode]):m.answer(m.query(),(bits>>step)&1)
                for i in range(8):self.assertEqual(m.predict(context(i)),symbolic(m,i))
    def test_checkpoint_corruption_and_semantic_tampering_reject(self):
        m=make();raw=m.snapshot()
        for bad in (raw[:-1],raw+b'x',raw[:9]+b'x'+raw[10:],b''):
            with self.assertRaises(ValueError):BroadModel.restore(bad)
        data=json.loads(raw[9:-32]);data['query_used']=4
        body=json.dumps(data,sort_keys=True,separators=(',',':')).encode();prefix=MAGIC+len(body).to_bytes(4,'big')+body
        with self.assertRaises(ValueError):BroadModel.restore(prefix+hashlib.sha256(prefix).digest())
    def test_unknown_label_contamination_rejects(self):
        m=make();m.source_labels[0][5]=1
        with self.assertRaises(ValueError):m.snapshot()
    def test_answer_types_addresses_and_target_queries_reject(self):
        m=make();raw=m.snapshot()
        for q,y in ((('t',0,3),0),(('s',False,5),0),(('s',0,5),True),(('s',0,4),0)):
            with self.assertRaises(ValueError):m.answer(q,y)
            self.assertEqual(m.snapshot(),raw)


class CertificationTests(unittest.TestCase):
    def test_incomplete_knowledge_never_receives_certificate(self):
        from certifier import certify
        m=make()
        with self.assertRaises(ValueError):certify(m)
        for _ in range(3):
            q=m.query();m.answer(q,(q[2]>>q[1])&1)
            with self.assertRaises(ValueError):certify(m)
    def test_true_connections_and_every_certificate_agree(self):
        from certifier import certify,route_output,CONFIGS
        # All 12 recipes on a complete synthetic source pair; no primary cohort.
        tables=tuple(tuple((i>>b)&1 for i in range(8)) for b in (0,1))
        for j,cfg in enumerate(CONFIGS):
            m=make();m.target_labels=[route_output(tables,cfg,i) if i in PUBLIC else 0 for i in range(8)];m._fit()
            for _ in range(4):
                q=m.query();m.answer(q,tables[q[1]][q[2]])
            info=certify(m);self.assertIn(j,info['compatible_configs'])
            for i,y in zip((3,5,6),info['certified_predictions']):
                if y is not None:self.assertEqual(y,route_output(tables,cfg,i))
            raw=m.snapshot();certify(m);self.assertEqual(m.snapshot(),raw)
    def test_certifier_is_not_a_candidate_dependency(self):
        from pathlib import Path
        source=Path(__file__).with_name('broad_model.py').read_text()
        self.assertNotIn('import certifier',source);self.assertNotIn('from certifier',source)

if __name__=='__main__':unittest.main()
