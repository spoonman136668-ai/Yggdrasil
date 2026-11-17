"""Source-free unit fixtures only. No new scientific effect consumption."""
from hashlib import sha256
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch
import challenge as Q

def fixture():
    xs=tuple(sorted(range(64),key=lambda x:
        (sha256(('WSP135|ACTIONS|'+str(x)).encode()).digest(),x))[:32])
    return tuple((x,int((x&7)==7)^((x>>4)&1)) for x in xs)

class SourceFree(TestCase):
    def test_01_basis_source_isolation_and_32_rows(self):
        self.assertEqual(Q.FIVE_MASKS,(31,47,55,59,61,62))
        self.assertEqual(len(Q.LOW_FEATURES),57)
        txt=Path(__file__).with_name('challenge.py').read_text(encoding='utf8')
        for forbidden in ('import source','from source import','WSP146|SOURCE|','_truth('):
            self.assertNotIn(forbidden,txt)
        rows=fixture()
        for bad in (rows[:-1],rows[:-1]+((rows[0][0],0),),
                    rows[:-1]+((63,2),),rows[:-1]+((True,0),)):
            with self.assertRaises(ValueError):Q.challenge(bad)
    def test_02_no_confident_flip_or_creation(self):
        rows=fixture()
        v=Q.challenge(rows)
        self.assertEqual(len(v['original']),64)
        for original,challenged in zip(v['original'],v['challenged']):
            self.assertIn(challenged,(original,None))
        for original,baseline in zip(v['original'],v['depth_only']):
            self.assertIn(baseline,(original,None))
        self.assertEqual(v['challenged'],Q.challenge(rows)['challenged'])
    def test_03_competing_programs_fit_only_paid_data(self):
        rows=fixture()
        progs,overflow=Q.counterhypotheses(rows)
        self.assertIs(type(overflow),bool)
        for prog in progs:
            self.assertIn(prog[0],Q.FIVE_MASKS)
            self.assertLessEqual(len(prog),4)
            self.assertTrue(all((sum(int((x&m)==m) for m in prog)&1)==y
                                for x,y in rows))
    def test_04_no_unverified_state_and_overflow_abstains(self):
        rows=fixture()
        state=Q.H.fit(rows)
        with self.assertRaises(ValueError):
            Q.challenge(rows,dict(state,observed_sha256='0'*64))
        fake=dict(state,level=3)
        with patch.object(Q.H,'fit',return_value=fake):
            with patch.object(Q,'counterhypotheses',return_value=((),True)):
                out=Q.challenge(rows,fake)
                self.assertTrue(all(v is None for v in out['challenged']))
                self.assertTrue(all(v is None for v in out['depth_only']))

    def test_05_wsp146_owner_namespace_independent_postseal(self):
        xs=tuple(x for x,y in fixture())
        warm=xs[:20]
        fixed=xs
        random=warm+tuple(x for x in range(64) if x not in warm)[:12]
        adaptive=warm+tuple(x for x in range(63,-1,-1) if x not in warm)[:12]
        arms={'fixed':fixed,'random':random,'adaptive':adaptive}
        sealed={p:{x:None for x in range(64)} for p in arms}
        a=Q.hidden_future_questions(12345,arms,sealed)
        b=Q.hidden_future_questions(12345,arms,sealed)
        self.assertEqual(a,b)
        self.assertEqual(len(a),8)
        self.assertFalse(set(a)&set().union(*(set(v) for v in arms.values())))
        with self.assertRaises(ValueError):Q.hidden_future_questions(True,arms,sealed)
        with self.assertRaises(ValueError):Q.hidden_future_questions(12345,{'fixed':fixed},sealed)
        with self.assertRaises(ValueError):Q.hidden_future_questions(12345,arms,{p:{} for p in arms})
