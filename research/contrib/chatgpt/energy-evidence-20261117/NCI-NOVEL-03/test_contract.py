import unittest
import hashlib
from experiment import (
    FAMILIES, OOD, SEEDS, PILOT_SEED, STAGES, PHASES,
    SourceWorld, ExactGrammarBMA, FullBeta, BackoffBeta,
    signatures, run_world, serial, digest, score,
)


class Contract(unittest.TestCase):
    def test_primary_isolation(self):
        self.assertNotIn(PILOT_SEED, SEEDS)
        self.assertEqual(len(SEEDS), len(set(SEEDS)))
        self.assertEqual(len(FAMILIES), 8)
        self.assertEqual(len(OOD), 3)

    def test_registered_action_budget(self):
        self.assertEqual(sum(PHASES.values()), 896)
        self.assertEqual(2*8*sum(PHASES.values()), 14336)

    def test_source_witnesses_are_deterministic(self):
        a=SourceWorld(PILOT_SEED, 'novel_guard')
        b=SourceWorld(PILOT_SEED, 'novel_guard')
        self.assertEqual(a.reveal('OLD_FIT',0,0,1),b.reveal('OLD_FIT',0,0,1))

    def test_source_does_not_expose_true_law(self):
        w=SourceWorld(PILOT_SEED, 'outside_rank2')
        row=w.reveal('NEW_FIT',2,1,0)
        self.assertEqual(set(row), {'context','a1','s2','a2','y','witness','public_factor_ids'})

    def test_grammar_bounded(self):
        for n in (5,6):
            x=signatures(n)
            self.assertEqual(len(x),len({m for m,_ in x}))
            self.assertEqual(x,signatures(n))
            self.assertTrue(all(cost<=3 for _,cost in x))

    def test_known_new_law_representable(self):
        w=SourceWorld(PILOT_SEED, 'novel_guard')
        for stage in STAGES:
            n=5 if stage=='t' else 6
            funcs={mask for mask,_ in signatures(n)}
            signature=0
            for ix in range(1<<n):
                values=tuple((ix>>j)&1 for j in range(n))
                if stage=='t': outcome=w._truth('NEW_FIT',values[:4],values[4])
                else:outcome=w._truth('NEW_FIT',values[:4],0,values[4],values[5])
                signature|=outcome<<ix
            self.assertIn(signature,funcs)

    def test_source_family_outside_grammar(self):
        w=SourceWorld(PILOT_SEED, 'outside_rank2')
        for stage in STAGES:
            n=5 if stage=='t' else 6
            signature=0
            for ix in range(1<<n):
                f=tuple(ix>>j&1 for j in range(n))
                v=w._truth('NEW_FIT',f[:4],f[4]) if stage=='t' else w._truth('NEW_FIT',f[:4],0,f[4],f[5])
                signature|=v<<ix
            self.assertNotIn(signature, {mask for mask,_ in signatures(n)})

    def test_unidentifiable_never_varies_new_x3(self):
        w=SourceWorld(PILOT_SEED,'unidentifiable_x3')
        self.assertTrue(all(w.public_context('NEW_FIT',i)[3]==0 for i in range(100)))

    def test_prequential_evidence_nonmutation(self):
        m=FullBeta(5)
        f=(0,1,0,1,1)
        first=m.predict(f)
        for _ in range(5):self.assertEqual(m.predict(f),first)
        self.assertEqual(m.observations,0)
        m.learn(f,1)
        self.assertGreater(m.predict(f),first)

    def test_grammarmodel_updates_only_postoutcome(self):
        b=ExactGrammarBMA(5)
        f=(1,0,1,0,0)
        before=digest(serial(b.snapshot()))
        b.predict(f)
        self.assertEqual(digest(serial(b.snapshot())),before)
        b.learn(f,1)
        self.assertNotEqual(digest(serial(b.snapshot())),before)

    def test_full_beta_bounded_scores(self):
        for cls in (ExactGrammarBMA,FullBeta,BackoffBeta):
            m=cls(5)
            self.assertGreater(m.predict((1,0,0,1,1)),0)
            self.assertLess(m.predict((1,0,0,1,1)),1)

    def test_immutable_old_bank_pilot(self):
        result=run_world(PILOT_SEED,'novel_guard')
        self.assertTrue(result['cold_old_unchanged'])
        self.assertEqual(result['source_actions'],1792)
        self.assertEqual(result['new_training_actions'],1024)

    def test_invalid_source_rejected(self):
        with self.assertRaises(ValueError):SourceWorld(999,'novel_guard')
        with self.assertRaises(ValueError):SourceWorld(PILOT_SEED,'nonexistent')

    def test_invalid_prob_rejected(self):
        with self.assertRaises(ValueError):score(0,1)
        with self.assertRaises(ValueError):score(1,1)


if __name__=='__main__':unittest.main()

class ExtendedControls(unittest.TestCase):
    def test_pilot_ood_unknown_class(self):
        result=run_world(PILOT_SEED,'outside_rank2')
        self.assertTrue(result['alarm'])
        self.assertEqual(result['relation_identity'],'UNKNOWN_OUTSIDE_GRAMMAR')

    def test_unchanging_fourth_factor_unknown(self):
        result=run_world(PILOT_SEED,'unidentifiable_x3')
        self.assertEqual(result['public_x3_counts'][1],0)
        self.assertEqual(result['relation_identity'],'UNKNOWN_NONIDENTIFIABLE_X3')

    def test_finite_causal_factor_support(self):
        m=ExactGrammarBMA(5)
        p=m.fourth_factor_support()
        self.assertTrue(0<p<1)
        for k in range(16):
            f=tuple((k>>i)&1 for i in range(5))
            m.learn(f, f[3])
        self.assertGreater(m.fourth_factor_support(),p)


class TemporalControls(unittest.TestCase):
    def test_first_stage_cannot_depend_on_future_action(self):
        for fam in FAMILIES:
            w=SourceWorld(PILOT_SEED,fam)
            for i in range(20):
                a=w.reveal('NEW_FIT',i,1,0)
                b=w.reveal('NEW_FIT',i,1,1)
                self.assertEqual(a['s2'],b['s2'])

    def test_new_factor_identity_public_and_separate(self):
        w=SourceWorld(PILOT_SEED,'novel_guard')
        e=w.reveal('NEW_FIT',0,0,0)
        self.assertEqual(e['public_factor_ids'],('new.x0','new.x1','new.x2','new.x3'))
        old=w.reveal('OLD_FIT',0,0,0)
        self.assertEqual(old['public_factor_ids'],('old.x0','old.x1','old.x2','old.x3'))
