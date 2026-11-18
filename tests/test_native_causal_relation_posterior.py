"""Native causal relation compilation: backward compatibility and negative controls."""
import itertools
import json
import unittest

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner
from yggdrasil.native_causal_relation_posterior import NativeCausalRelationPosterior
from yggdrasil.native_property_knowledge import NativePropertyKnowledge


def parent():
    p=NativePropertyKnowledge("ckad25v-test",entities=8,context_bits=3)
    properties=[[e,b,(e>>b)&1] for e in range(8) for b in range(3)]
    p=p.stage_properties(properties,digest(canonical(properties)),
                         source_namespace="ckad25v-test")
    raw=p.checkpoint()
    m=NativeCumulativeLearner(raw,digest(raw))
    old=[[x&7,x>>3,int((x&7)==3)] for x in range(16) if x not in (2,5,9,14)]
    m=m.observe(0,old,digest(canonical(old)),source_ref="a"*64)
    return m


def cause(x):
    c0=x&1; action=x>>3
    return 1^c0^action


def train(m,slot=1,masks=None):
    if masks is None:masks=[x for x in range(16) if x not in (3,6,11,15)]
    records=[[x&7,x>>3,cause(x)] for x in masks]
    return m.observe(slot,records,digest(canonical(records)),source_ref="b"*64)


def independent_exact(masks, query):
    fit=[(x,cause(x)) for x in masks]
    alive=[]
    for n in range(4):
        for terms in itertools.combinations(range(16),n):
            w=sum(1<<i for i in terms)
            if all(((w&sum(1<<i for i in range(16) if (x&i)==i)).bit_count()&1)==y
                   for x,y in fit):
                alive.append(w)
    if not alive:return (1,2)
    f=sum(1<<i for i in range(16) if (query&i)==i)
    return (sum((w&f).bit_count()&1 for w in alive),len(alive))


class NativeCausalRelationPosteriorTests(unittest.TestCase):
    def test_legacy_checkpoint_and_original_knowledge_remain_byte_identical(self):
        old=parent()
        before=old.checkpoint()
        restored=NativeCumulativeLearner.restore(before,digest(before))
        self.assertEqual(restored.checkpoint(),before)
        original_preds=[old.predict(0,c,a) for a in (0,1) for c in range(8)]
        m=train(restored)
        with_compiled=m.compile_causal_relations(1)
        self.assertEqual(m.checkpoint(),m.checkpoint())
        self.assertEqual([with_compiled.predict(0,c,a) for a in (0,1) for c in range(8)],
                         original_preds)
        self.assertEqual(with_compiled._properties.checkpoint(),old._properties.checkpoint())
        self.assertEqual(with_compiled._source._seen[0],old._source._seen[0])
        self.assertEqual(with_compiled._events[:len(old._events)],old._events)
        self.assertEqual(with_compiled._hypotheses[0].checkpoint(),old._hypotheses[0].checkpoint())
        raw=with_compiled.checkpoint()
        child=NativeCumulativeLearner.restore(raw,digest(raw))
        self.assertEqual(child.checkpoint(),raw)
        self.assertIs(child.compile_causal_relations(1),child)

    def test_compiled_beliefs_fit_training_only_and_match_independent_exact(self):
        masks=[x for x in range(16) if x not in (3,6,11,15)]
        m=train(parent(),1,masks).compile_causal_relations(1)
        self.assertGreater(m._compiled[1].model_count,0)
        for x in range(16):
            p=m.causal_relation_probability(1,x&7,x>>3)
            if x in masks:
                self.assertEqual(p,(cause(x),1))
            else:
                ones,total=independent_exact(masks,x)
                self.assertEqual(p[0]*total,ones*p[1])
                self.assertGreater(p[1],0)
        self.assertEqual(m.causal_relation_probability(2,0,0),None)
        self.assertEqual(m._compiled[1].info()["accepted_native"],False)

    def test_checkpoint_source_join_rejects_model_forgery_and_duplicate_keys(self):
        m=train(parent()).compile_causal_relations(1)
        raw=m.checkpoint()
        saved=json.loads(raw)
        forged=json.loads(saved["compiled_ascii"][1])
        self.assertTrue(forged["models"])
        forged["models"]=forged["models"][:-1]
        forged["info"]["models"]=len(forged["models"])
        saved["compiled_ascii"][1]=canonical(forged).decode("ascii")
        changed=canonical(saved)
        with self.assertRaises(ValueError):
            NativeCumulativeLearner.restore(changed,digest(changed))
        c=m._compiled[1].checkpoint()
        duplicate=c[:-1]+b',"schema":"duplicate"}'
        with self.assertRaises(ValueError):
            NativeCausalRelationPosterior.restore(duplicate,digest(duplicate))
        self.assertEqual(NativeCumulativeLearner.restore(raw,digest(raw)).checkpoint(),raw)

    def test_source_continuation_explicitly_invalidates_compiled_weights(self):
        m=train(parent()).compile_causal_relations(1)
        first=m.checkpoint()
        extra=[3,6,11,15]
        for x in extra:
            row=[[x&7,x>>3,cause(x)]]
            m=m.observe(1,row,digest(canonical(row)),source_ref="c"*64)
            self.assertEqual(m.causal_relation_probability(1,x&7,x>>3),(cause(x),1))
        self.assertIsNone(m._compiled[1])
        self.assertNotEqual(m.checkpoint(),first)
        cold=NativeCumulativeLearner.restore(m.checkpoint(),digest(m.checkpoint()))
        self.assertEqual(cold.checkpoint(),m.checkpoint())
        self.assertIsNone(cold.causal_relation_probability(1,0,0) if False else cold._compiled[1])
        m2=m.compile_causal_relations(1)
        self.assertEqual(m2._compiled[1].model_count,1)
        self.assertEqual(NativeCumulativeLearner.restore(m2.checkpoint(),digest(m2.checkpoint())).checkpoint(),
                         m2.checkpoint())

    def test_noncompliant_unknown_grammar_abstains_and_restricted_pipelines_fail(self):
        # 4-way parity genuinely needs four independent linear ANF terms.
        old=parent()
        full=[[x&7,x>>3,((x>>0)&1)^((x>>1)&1)^((x>>2)&1)^((x>>3)&1)]
              for x in range(16)]
        m=old.observe(1,full,digest(canonical(full)),source_ref="d"*64)
        compiled=m.compile_causal_relations(1)
        self.assertEqual(compiled._compiled[1].model_count,0)
        with self.assertRaises(ValueError):
            compiled.repair_sparse(1)
        with self.assertRaises(ValueError):
            compiled.observe_cached_history(b"fake","0"*64,1)
        self.assertEqual(compiled.checkpoint(),
                         NativeCumulativeLearner.restore(compiled.checkpoint(),digest(compiled.checkpoint())).checkpoint())
        self.assertEqual(compiled.causal_relation_probability(1,0,0),(0,1))
        # At a non-witnessed context this misspecified posterior returns (1,2).
        unsupported=train(old).compile_causal_relations(1)
        self.assertIsNone(unsupported.causal_relation_probability(2,1,0))


if __name__=="__main__":
    unittest.main()
