"""Native source-trained history-conditioned action choice and cold custody."""
import unittest

from yggdrasil.native_context_basis import canonical,digest
from yggdrasil.native_cumulative_learner import NativeCumulativeLearner
from test_native_causal_witness import train
from test_native_causal_state_acquisition import observed


def trained_history():
    _,m=train()
    saved=[m._compiled[x].checkpoint() for x in (1,2,3)]
    # Actual witnessed consequences are source stored, not guessed by agent.
    for slot,inputs,flip,src in (
        (12,(12,13),12,"a"),
        (13,(12,14),12,"b"),
        (14,(13,15),None,"c"),
    ):
        rows=observed("C",list(inputs))
        if flip is not None:
            rows[0][2]^=1
        m=m.observe(slot,rows,digest(canonical(rows)),source_ref=src*64)
    return m,saved


class HistoryConditionedProbeTests(unittest.TestCase):
    def test_history_updates_native_action_choice_and_cold_restore(self):
        m,saved=trained_history()
        before=m.checkpoint()
        actions=[[k&7,k>>3] for k in (12,13,14,15)]
        chosen=m.propose_source_change_witnesses(3,(12,13,14),actions)
        self.assertEqual(chosen,[[4,1],[6,1]])
        self.assertEqual([m._compiled[k].checkpoint() for k in (1,2,3)],saved)
        cold=NativeCumulativeLearner.restore(before,digest(before))
        self.assertEqual(cold.checkpoint(),before)
        self.assertEqual(
            cold.propose_source_change_witnesses(3,(12,13,14),actions),chosen)
        self.assertEqual(m.checkpoint(),before)

    def test_real_target_interventions_stored_in_new_slot15(self):
        m,saved=trained_history()
        chosen=m.propose_source_change_witnesses(
            3,(12,13,14),[[x&7,x>>3] for x in (12,13,14,15)])
        target=[row+[observed("C",[row[0]|(row[1]<<3)])[0][2]^1]
                if row==chosen[0] else
                row+[observed("C",[row[0]|(row[1]<<3)])[0][2]]
                for row in chosen]
        updated,p,status=m.validate_causal_source_with_witnesses(
            3,target,digest(canonical(target)),source_ref="d"*64,
            evidence_slot=15,query_context=5,query_action=1)
        self.assertEqual(status,"FALSIFIED")
        self.assertEqual(p,(1,2))
        self.assertEqual(updated._source._seen[15].bit_count(),2)
        self.assertEqual([updated._compiled[x].checkpoint() for x in (1,2,3)],saved)
        raw=updated.checkpoint()
        self.assertEqual(NativeCumulativeLearner.restore(raw,digest(raw)).checkpoint(),raw)

    def test_history_and_future_leakage_fails_closed(self):
        m,_=trained_history()
        old=m.checkpoint()
        actions=[[k&7,k>>3] for k in (12,13,14,15)]
        bad=[
            (3,(12,13),actions,2),
            (3,(12,13,15),actions,2),
            (3,(12,12,14),actions,2),
            (3,(12,13,14),actions[:3]+[actions[0]],2),
            (3,(12,13,14),actions[:3]+[[0,0]],2),
            (3,(12,13,14),actions,3),
            (4,(12,13,14),actions,2),
        ]
        for slot,history,candidates,n in bad:
            with self.subTest(slot=slot,history=history,candidates=candidates),self.assertRaises(ValueError):
                m.propose_source_change_witnesses(slot,history,candidates,count=n)
        self.assertEqual(m.checkpoint(),old)


if __name__=="__main__":unittest.main()
