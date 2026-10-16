"""F94 pure source contract tests. No registered or synthetic source accessed."""
from __future__ import annotations
import importlib.util,sys,unittest
from pathlib import Path
source=Path(__file__).with_name("single_deviation_feasibility.py")
s=importlib.util.spec_from_file_location("f94_unittest",source)
M=importlib.util.module_from_spec(s);sys.modules[s.name]=M;s.loader.exec_module(M)
class F94Contracts(unittest.TestCase):
 def test_every_public_prefix_is_in_one_period(self):
  assert [M.period(i) for i in range(72)]==(
   ["early"]*24+["middle"]*24+["late"]*24)
 def test_period_outside_public_bounds_fails(self):
  for i in (-1,72):
   with self.assertRaises(AssertionError):M.period(i)
 def test_safe_overlap_counts_identical_native_records(self):
  baseline=tuple((i,i+1,(0,)) for i in range(12))
  alternative=baseline[:10]+((100,101,(2,)),(101,102,(4,)))
  self.assertTrue(M.admissible_overlap(baseline,alternative))
  self.assertFalse(M.admissible_overlap(baseline,baseline[:9]+((100,101,(2,)),)))
 def test_short_baseline_overlap_threshold_is_bounded(self):
  base=((1,2,(0,)),)
  self.assertTrue(M.admissible_overlap(base,()))
  self.assertTrue(M.admissible_overlap(base,base))
 def test_empty_rows_have_zero_counts(self):
  s=M.summarize([])
  self.assertEqual(s["cases"],0)
  self.assertEqual(s["total_native_counterfactuals"],0)
  self.assertEqual(s["f60_failed_cases_with_one_step_rescue"],0)
  self.assertEqual(set(s["by_period"]),set(M.PERIODS))
 def test_no_source_or_future_accepted_by_overlap_helper(self):
  import inspect
  self.assertEqual(tuple(inspect.signature(M.admissible_overlap).parameters),
                   ("baseline","alternative"))
if __name__=="__main__":unittest.main()
