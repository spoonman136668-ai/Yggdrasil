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
