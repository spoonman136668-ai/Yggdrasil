import json
import subprocess
import sys
import unittest
from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_property_knowledge import NativePropertyKnowledge
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner


def fixture():
    p = NativePropertyKnowledge('ckad13-test', entities=8, context_bits=3)
    rows = [[e,b,(e>>b)&1] for e in range(8) for b in range(3)]
    p = p.stage_properties(rows, digest(canonical(rows)), source_namespace='ckad13-test')
    raw = p.checkpoint()
    return NativeCumulativeLearner(raw, digest(raw))


def rows():
    return [[x&7,x>>3,int(sum((x>>b)&1 for b in range(3))>=2)] for x in range(16)]


def train(m, slot, r, **kwargs):
    return m.observe(slot, r, digest(canonical(r)), source_ref='a'*64, **kwargs)


class IntegratedLearningTests(unittest.TestCase):
    def test_optional_backoff_untrained_types_and_legacy_readout_preserved(self):
        from pathlib import Path
        from yggdrasil.native_stochastic_history import SOURCE_PIN
        m=fixture();self.assertEqual(m.history_forecast_backoff(0,0,0,0),((1,2),(1,2)))
        with self.assertRaises(ValueError):m.history_forecast_backoff(0,0,0,True)
        source=(Path(__file__).resolve().parents[1]/'research/contrib/chatgpt/NKR-20/source_fixture.json').read_bytes()
        m=m.observe_cached_history(source,SOURCE_PIN,23);raw=m.checkpoint();old=m.history_forecast(0,0,0,0)
        m.history_forecast_backoff(0,0,0,0)
        self.assertEqual(m.checkpoint(),raw);self.assertEqual(m.history_forecast(0,0,0,0),old)

    def test_second_source_preserves_deterministic_and_first_source_state(self):
        from pathlib import Path
        from yggdrasil.native_stochastic_history import SOURCE_PIN as MDP_PIN
        from yggdrasil.native_dtr_history import SOURCE_PIN as DTR_PIN
        root=Path(__file__).resolve().parents[1]
        mdp=(root/'research/contrib/chatgpt/NKR-20/source_fixture.json').read_bytes()
        dtr=(root/'research/contrib/chatgpt/CKAD-16/source_public_fit.json').read_bytes()
        m=train(fixture(),0,rows()).observe_cached_history(mdp,MDP_PIN,23)
        raw=m.checkpoint();core=m._source.checkpoint();history=m._history.checkpoint()
        for stop in (64,128,192):
            m=m.observe_cached_dtr(dtr,DTR_PIN,stop);r=m.checkpoint();m=NativeCumulativeLearner.restore(r,digest(r))
            self.assertEqual(m._source.checkpoint(),core);self.assertEqual(m._history.checkpoint(),history)
            self.assertEqual([m.predict(0,x&7,x>>3) for x in range(16)],[r[2] for r in rows()])
        self.assertEqual(NativeCumulativeLearner.restore(raw,digest(raw)).checkpoint(),raw)
        self.assertIs(m.observe_cached_dtr(dtr,DTR_PIN,192),m)
        self.assertIs(m.observe_cached_history(mdp,MDP_PIN,23),m)

    def test_stochastic_history_updates_do_not_quarantine_deterministic_knowledge(self):
        from pathlib import Path
        from yggdrasil.native_stochastic_history import SOURCE_PIN
        source=(Path(__file__).resolve().parents[1]/'research/contrib/chatgpt/NKR-20/source_fixture.json').read_bytes()
        m=train(fixture(),0,rows());old=m.checkpoint();expected=[m.predict(0,x&7,x>>3) for x in range(16)]
        for stop in (8,16,23):
            m=m.observe_cached_history(source,SOURCE_PIN,stop)
            raw=m.checkpoint();m=NativeCumulativeLearner.restore(raw,digest(raw))
            self.assertEqual(expected,[m.predict(0,x&7,x>>3) for x in range(16)])
            self.assertEqual(m._quarantined,(False,)*16)
        self.assertEqual(NativeCumulativeLearner.restore(old,digest(old)).checkpoint(),old)
        self.assertGreater(m.info()['stochastic_history']['counter_keys_with_both_outcomes'],0)
        self.assertEqual(m.info()['stochastic_history']['training_events'],92)
        self.assertIs(m.observe_cached_history(source,SOURCE_PIN,23),m)

    def test_sparse_repair_cold_continuation_preserves_legacy_bytes_and_other_slots(self):
        remaining=(4,8,12,2)
        data=[[x&7,x>>3,int(x&3==3)] for x in range(16) if x not in remaining]
        m=train(fixture(),0,data);old=m.checkpoint();source=m._source.checkpoint()
        self.assertFalse(m._hypotheses[0].eligible)
        child,hyp,cost=m.repair_sparse(0)
        self.assertTrue(hyp.eligible);self.assertEqual(m.checkpoint(),old)
        self.assertEqual(child._source.checkpoint(),source)
        self.assertEqual(NativeCumulativeLearner.restore(old,digest(old)).checkpoint(),old)
        raw=child.checkpoint();child=NativeCumulativeLearner.restore(raw,digest(raw))
        self.assertEqual(child.checkpoint(),raw)
        rest=[[x&7,x>>3,int(x&3==3)] for x in remaining]
        script='''import json,sys
from yggdrasil.native_context_basis import canonical,digest
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner
p=json.load(sys.stdin);raw=p['raw'].encode('ascii');m=NativeCumulativeLearner.restore(raw,digest(raw))
m=m.observe(0,p['rest'],digest(canonical(p['rest'])),source_ref='a'*64)
raw=m.checkpoint();m=NativeCumulativeLearner.restore(raw,digest(raw))
print(json.dumps([m.predict(0,x&7,x>>3) for x in range(16)]))
'''
        p=subprocess.run([sys.executable,'-B','-c',script],input=json.dumps({'raw':raw.decode('ascii'),'rest':rest}),
                         text=True,capture_output=True,check=True,timeout=30)
        self.assertEqual(json.loads(p.stdout),[int(x&3==3) for x in range(16)])

    def test_denied_sparse_repair_preserves_full_parent_and_invalid_scope_fails(self):
        from unittest.mock import patch
        from types import SimpleNamespace
        data=[[x&7,x>>3,int(x&3==3)] for x in range(16) if x not in (4,8,12,2)]
        m=train(fixture(),0,data);raw=m.checkpoint()
        with patch('scipy.optimize.milp',return_value=SimpleNamespace(status=1,x=None)):
            child,hyp,cost=m.repair_sparse(0)
        self.assertIs(child,m);self.assertFalse(hyp.eligible);self.assertEqual(m.checkpoint(),raw)
        with self.assertRaises(ValueError):fixture().repair_sparse(0)

    def test_cumulative_learning_selects_class_retains_facts_and_old_slots(self):
        m = fixture(); facts = m._properties.checkpoint()
        for r in (rows()[:4], rows()[4:8], rows()[8:]):
            old = m.checkpoint(); child = train(m,0,r)
            self.assertEqual(m.checkpoint(),old); m=child
        self.assertEqual(m.info()['representations'][0]['selected_degree'],2)
        self.assertEqual([m.predict_entity(0,e,0) for e in range(8)], [r[2] for r in rows()[:8]])
        before = [m.predict(0,x&7,x>>3) for x in range(16)]
        m = train(m,1,[[c,a,1-y] for c,a,y in rows()])
        self.assertEqual(before,[m.predict(0,x&7,x>>3) for x in range(16)])
        self.assertEqual(m._properties.checkpoint(),facts)

    def test_conflict_quarantines_and_preserves_old_weights_and_negative_packet(self):
        m = train(fixture(),0,rows()); old = m._source.checkpoint()
        packet = [[0,0,1]]; child = train(m,0,packet)
        self.assertEqual(child._source.checkpoint(),old)
        self.assertTrue(all(child.predict(0,x&7,x>>3) is None for x in range(16)))
        self.assertEqual(child._events[-1]['conflicting_packet'],packet)
        self.assertEqual(NativeCumulativeLearner.restore(child.checkpoint(),digest(child.checkpoint())).checkpoint(),child.checkpoint())
        with self.assertRaises(ValueError):train(child,0,rows()[1:])

    def test_restart_then_continue_in_a_fresh_process(self):
        m = train(fixture(),0,rows()[:8]); raw = m.checkpoint()
        script = '''import json,sys
from yggdrasil.native_context_basis import canonical,digest
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner
p=json.load(sys.stdin);raw=p['raw'].encode('ascii');m=NativeCumulativeLearner.restore(raw,digest(raw))
m=m.observe(0,p['rows'],digest(canonical(p['rows'])),source_ref='a'*64)
print(json.dumps([m.predict(0,x&7,x>>3) for x in range(16)]))
'''
        p = subprocess.run([sys.executable,'-B','-c',script],input=json.dumps({'raw':raw.decode('ascii'),'rows':rows()[8:]}),text=True,capture_output=True,check=True,timeout=30)
        self.assertEqual(json.loads(p.stdout),[r[2] for r in rows()])

    def test_invalid_inputs_and_correlation_do_not_mutate_state(self):
        m = fixture(); raw = m.checkpoint()
        for data in ([[0,0,True]], [[True,0,0]], [[0,0,0],[0,0,1]]):
            with self.assertRaises(ValueError):train(m,0,data)
        with self.assertRaises(ValueError):train(m,0,rows(),source_kind='correlation_only')
        with self.assertRaises(ValueError):m.observe(0,rows(),'0'*64,source_ref='a'*64)
        with self.assertRaises(ValueError):m.propose(0,rows(),1)
        self.assertEqual(m.checkpoint(),raw)

    def test_replay_is_idempotent_and_outcome_blind_proposal_avoids_seen_inputs(self):
        m = train(fixture(),0,rows()[:8]); raw = m.checkpoint()
        self.assertIs(train(m,0,rows()[:8]),m)
        self.assertEqual(m.checkpoint(),raw)
        proposed = m.propose(0,[[r[0],r[1]] for r in rows()],8)
        self.assertEqual({tuple(x) for x in proposed},{(r[0],r[1]) for r in rows()[8:]})
        self.assertEqual(proposed,m.propose(0,list(reversed([[r[0],r[1]] for r in rows()])),8))

    def test_restore_rejects_changed_component_joins_flags_and_negative_provenance(self):
        m = train(fixture(),0,rows()); raw=m.checkpoint()
        self.assertEqual(NativeCumulativeLearner.restore(raw,digest(raw)).checkpoint(),raw)
        for key,value in [('accepted_native',True),('scientific_pass',True),('source_mode','real_world'),('quarantined',[True]+[False]*15),('hypotheses_ascii',[None]*16)]:
            d=json.loads(raw);d[key]=value;bad=canonical(d)
            with self.assertRaises(ValueError):NativeCumulativeLearner.restore(bad,digest(bad))
        with self.assertRaises(ValueError):NativeCumulativeLearner.restore(raw+b'\n',digest(raw+b'\n'))
        with self.assertRaises(ValueError):NativeCumulativeLearner.restore(raw,'0'*64)


if __name__ == '__main__':unittest.main()
