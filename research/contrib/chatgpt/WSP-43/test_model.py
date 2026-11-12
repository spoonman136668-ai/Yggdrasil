import itertools
import unittest
from model import NumericModel,GF2Regression,acquire
from heuristic import acquire as heuristic_acquire
from world import World


class Tests(unittest.TestCase):
    def test_exact_coefficients_for_interacting_full_vector_map(self):
        world=World(8,'eight_nonlinear','unit-exact')
        model,basis,rows,stats=acquire(8,world.apply,224)
        for group,truth in zip(model.groups,world.groups):
            self.assertTrue(all(dict(truth).get(m)==c for m,c in group))
        self.assertEqual(model.groups,tuple(world.groups))
        for a,x in itertools.product(range(2),range(256)):self.assertEqual(model.apply(a,x),world.apply(a,x))

    def test_no_partial_coefficient_write_on_budget_exhaustion(self):
        world=World(16,'thirtytwo_nonlinear','unit-partial')
        model,_,rows,stats=acquire(16,world.apply,128)
        self.assertTrue(all(s['queries']<=128 for s in stats))
        for group,truth in zip(model.groups,world.groups):self.assertTrue(all(dict(truth).get(m)==c for m,c in group))

    def test_independent_gf2_fit_complete_feature_vocabulary(self):
        world=World(8,'eight_nonlinear','unit-fit')
        model,_,rows,_=acquire(8,world.apply,224)
        fitted=GF2Regression(8,rows,model)
        self.assertEqual(fitted.training_errors,[0,0])
        self.assertEqual(fitted.groups,model.groups)

    def test_actual_budget_and_replay(self):
        world=World(8,'sixteen_nonlinear','unit-budget');calls=[]
        def probe(a,x):calls.append((a,x));return world.apply(a,x)
        first,_,rows,stats=acquire(8,probe,128)
        self.assertEqual(len(calls),len(rows));self.assertEqual(len(set(calls)),len(calls))
        second,_,again,s2=acquire(8,world.apply,128)
        self.assertEqual(first.snapshot(),second.snapshot());self.assertEqual(rows,again);self.assertEqual(stats,s2)

    def test_128_bit_affine_parameters_and_screen_contract(self):
        target=NumericModel(128,(((0,3),(1,1<<127)),((1<<127,7),)))
        model,_,_,_=acquire(128,target.apply,512)
        self.assertEqual(model.groups,target.groups)
        with self.assertRaises(ValueError):acquire(128,target.apply,128)

    def test_cold_and_canonical_negative(self):
        model=NumericModel(16,(((0,1),(7,8193)),((1,65535),)))
        snap=model.snapshot();self.assertEqual(NumericModel.restore(snap).snapshot(),snap)
        with self.assertRaises(ValueError):NumericModel.restore(snap+b'x')
        with self.assertRaises(ValueError):NumericModel(16,(((1,0),),()))

    def test_heuristic_same_ceiling_and_widths(self):
        world=World(8,'eight_nonlinear','unit-heuristic')
        model,_,rows,stats=heuristic_acquire(8,world.apply,224)
        self.assertTrue(all(s['queries']<=224 for s in stats))
        self.assertEqual(len(rows),sum(s['queries'] for s in stats))


if __name__=='__main__':unittest.main()
