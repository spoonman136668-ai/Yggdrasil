"""NR-M1X: independent selected-source terminal eligibility trace comparator.

Intentionally source-free abstract original-public feedback fixture. No Farama
environment reset/step, unchosen outcome, hidden mission map, or original goal.
"""
import unittest

from research.native.itd02.mg23.selected_target_cells import (
    TargetCreditCells, observed_key, WINDOW,
)
from research.native.itd02.mg19.original_mission_cells import OriginalMissionAdapter
from research.native.itd02.mg23.test_selected_target_cells import frame

class NRM1XOriginalSelectedDelayControl(unittest.TestCase):
    def run_source(self,terminal_positive):
        public=frame("pick up the yellow ball",0,(1,0,0))
        native=TargetCreditCells()
        adapter=OriginalMissionAdapter()
        adapter.reset_public(public)
        native.start_session(adapter,"nr-m1x-source-only-terminal",live=False)
        # One historical action outside the 32-step terminal window,
        # 31 zero-effect turns, one terminal action with source public unchanged.
        actions=[2]+[0]*31+[6]
        conventional={}
        trace=[]
        for ordinal,action in enumerate(actions):
            positive=terminal_positive and ordinal==len(actions)-1
            adapter.submit(action)
            adapter.complete(public,1.0 if positive else 0.0,positive,False)
            native.learn_selected(adapter,public,public)
            trace.append((observed_key(public),action))
            if len(trace)>WINDOW:
                trace=trace[-WINDOW:]
            if positive:
                for age,(key,selected) in enumerate(reversed(trace)):
                    conventional[(key,selected)]=conventional.get((key,selected),0)+WINDOW-age
        return native,public,conventional

    def test_same_information_tabular_eligibility_and_distractor_null(self):
        native,public,conventional=self.run_source(True)
        key=observed_key(public)
        self.assertEqual(len(native.trace),WINDOW)
        self.assertEqual(native.samples,33)
        row=native.cells[key]
        for action,stat in enumerate(row):
            self.assertEqual(stat["delayed"],conventional.get((key,action),0))
            self.assertEqual(stat["target"],0)
        self.assertEqual(row[2]["count"],1)
        self.assertEqual(row[2]["delayed"],0)
        self.assertEqual(row[0]["count"],31)
        self.assertEqual(row[0]["delayed"],496)
        self.assertEqual(row[6]["delayed"],32)
        selected=native.choose(public)
        self.assertEqual(selected["action"],0)
        self.assertEqual(selected["status"],
                         "MG23_LOCAL_OWN_SELECTED_PUBLIC_TARGET_OR_TERMINAL_CREDIT")
        checkpoint=native.checkpoint()
        cold=TargetCreditCells.restore(checkpoint)
        self.assertEqual(cold.checkpoint(),checkpoint)
        self.assertEqual(cold.cells[key][0]["delayed"],496)
        no_reward,p,_=self.run_source(False)
        self.assertEqual(no_reward.samples,33)
        self.assertTrue(all(stat["delayed"]==0 for stat in no_reward.cells[observed_key(p)]))

if __name__=="__main__":
    unittest.main()
