import itertools
import unittest
from model import NumericModel,SymbolicExecution,KernelRegression,acquire
from battery import World


class Tests(unittest.TestCase):
    def test_whole_affine_map_acquired_without_background(self):
        world=World(8,'affine','unit-affine')
        model,basis,rows,stats=acquire(8,world.apply,64)
        self.assertEqual(model.groups,tuple(world.groups))
        self.assertEqual(basis.groups,model.groups)
        for a,x in itertools.product(range(2),range(256)):self.assertEqual(model.apply(a,x),world.apply(a,x))

    def test_full_vector_nonlinear_feature_and_bias(self):
        target=NumericModel(8,(((0,15),(1,3),(63,173)),((3,255),(127,17))))
        model,basis,rows,stats=acquire(8,target.apply,128)
        self.assertEqual(model.groups,target.groups)
        self.assertNotEqual(basis.groups,target.groups)
        for a,x in itertools.product(range(2),range(256)):self.assertEqual(model.apply(a,x),target.apply(a,x))

    def test_kernel_fits_all_output_bits(self):
        world=World(8,'four_nonlinear','unit-kernel')
        _,_,rows,_=acquire(8,world.apply,64)
        model=KernelRegression(8,rows)
        self.assertLess(max(model.max_errors),1e-7)
        for a,x,y in rows:self.assertEqual(model.apply(a,x),y)

    def test_actual_query_budget_and_determinism(self):
        world=World(8,'eight_nonlinear','unit-budget');calls=[]
        def probe(a,x):calls.append((a,x));return world.apply(a,x)
        model,_,rows,stats=acquire(8,probe,64)
        self.assertEqual(len(calls),len(rows));self.assertEqual(len(set(calls)),len(calls))
        self.assertTrue(all(s['queries']<=64 and s['updates']<=256 and s['cells']<=41 for s in stats))
        second,_,again,other=acquire(8,world.apply,64)
        self.assertEqual(model.snapshot(),second.snapshot());self.assertEqual(rows,again);self.assertEqual(stats,other)

    def test_independent_execution_and_cold_restore(self):
        model=NumericModel(8,(((0,1),(3,27),(255,255)),((1,128),(7,255))))
        reference=SymbolicExecution(model)
        for a,x in itertools.product(range(2),range(256)):self.assertEqual(model.apply(a,x),reference.apply(a,x))
        snap=model.snapshot();self.assertEqual(NumericModel.restore(snap).snapshot(),snap)
        with self.assertRaises(ValueError):NumericModel.restore(snap+b'x')
        with self.assertRaises(ValueError):NumericModel(8,(((3,0),),()))
        with self.assertRaises(ValueError):NumericModel(8,(((3,1),(3,2)),()))
        with self.assertRaises(ValueError):model.apply(True,0)

    def test_no_collateral_change_after_second_world(self):
        first,_,_,_=acquire(8,World(8,'four_nonlinear','first').apply,64)
        snap=first.snapshot();acquire(8,World(8,'eight_nonlinear','second').apply,64)
        self.assertEqual(first.snapshot(),snap)


if __name__=='__main__':unittest.main()
