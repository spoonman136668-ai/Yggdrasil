import itertools
import unittest
from model import NumericModel, SymbolicExecution, KernelRegression, acquire, random_transcript, rotate
from battery import World


class Tests(unittest.TestCase):
    def test_grows_degree_six_not_in_wsp40_vocabulary(self):
        target=NumericModel(8,((63,),(126,)))
        model,rows,stats=acquire(8,target.apply,128)
        self.assertEqual(model.terms,target.terms)
        self.assertTrue(all(s['queries']<=128 for s in stats))
        for a,x in itertools.product(range(2),range(256)):
            self.assertEqual(model.apply(a,x),target.apply(a,x))

    def test_constant_and_zero_rules(self):
        target=NumericModel(8,((0,),()))
        model,_,_=acquire(8,target.apply,64)
        self.assertEqual(model.terms,target.terms)

    def test_kernel_fully_fits_unique_observations(self):
        target=NumericModel(8,((3,7),(63,)))
        transcript=random_transcript(8,target.apply,[64,64])
        fitted=KernelRegression(8,transcript)
        self.assertLess(max(fitted.max_errors),1e-7)
        for a,x,y in transcript:
            self.assertEqual(fitted.apply(a,x),target.apply(a,x))

    def test_budget_actual_queries_and_replay(self):
        calls=[]
        world=World(8,'arbitrary_hash','unittest')
        def probe(a,x):
            calls.append((a,x))
            return world.apply(a,x)
        first,rows,stats=acquire(8,probe,64)
        self.assertEqual(len(calls),len(rows))
        self.assertEqual(len(set(calls)),len(calls))
        self.assertTrue(all(s['queries']<=64 and s['updates']<=512 and s['terms']<=32 for s in stats))
        second,replay,again=acquire(8,world.apply,64)
        self.assertEqual(first.snapshot(),second.snapshot())
        self.assertEqual(rows,replay)
        self.assertEqual(stats,again)

    def test_symbolic_parity_high_degree_and_constant(self):
        model=NumericModel(8,((0,3,127),(63,255)))
        reference=SymbolicExecution(model)
        for a,x in itertools.product(range(2),range(256)):
            self.assertEqual(model.apply(a,x),reference.apply(a,x))

    def test_checkpoint_and_isolated_world(self):
        target=NumericModel(8,((63,),(126,)))
        first,_,_=acquire(8,target.apply,64)
        frozen=first.snapshot()
        acquire(8,World(8,'arbitrary_hash','another').apply,64)
        self.assertEqual(first.snapshot(),frozen)
        self.assertEqual(NumericModel.restore(frozen).snapshot(),frozen)
        with self.assertRaises(ValueError): NumericModel.restore(frozen+b'x')
        with self.assertRaises(ValueError): NumericModel(8,((7,3),()))
        with self.assertRaises(ValueError): NumericModel(8,((256,),()))
        with self.assertRaises(ValueError): first.apply(True,0)


if __name__=='__main__':unittest.main()
