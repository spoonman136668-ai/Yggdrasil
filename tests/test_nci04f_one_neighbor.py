"""NCI04F: one informative surviving neighbor, the other has no signal.

This test leaves NCI04E's original distributed-setpoint mechanism unchanged.
It records authentic negative development outcomes instead of relaxing the
frozen consensus threshold. No post-lesion target labels are passed.
"""
import json
import os
import unittest
from yggdrasil.distributed_setpoint import DistributedSetpoint

def observation(t, impossible=False):
    x = [(t + 3*i) % 2 for i in range(8)]
    x[2] = t % 2
    x[4] = (t//2) % 2
    y = x[:]
    y[3] = (t//4)%2 if impossible else x[2]
    return x,y

def marginal_predict(counts,observed_bit):
    zero,one = counts[observed_bit]
    if zero+one < 8:
        return None
    p = (one+1)/(zero+one+2)
    if p>=.80:
        return 1
    if p<=.20:
        return 0
    return None

def perform():
    m = DistributedSetpoint()
    for t in range(64):
        x,y=observation(t)
        m.observe(x,y)
    left_count,right_count=m.has_neighbor_memory(3)
    if (left_count,right_count)!=(64,64):
        raise RuntimeError("PRELESION_LOCAL_CUSTODY_NOT_64_AND_64")
    # The left neighbor's own learned count table is an equal-observation
    # fully trained conventional one-hop lookup baseline.
    left_table=[row[:] for row in m.shadow[2][1]]
    m.lesion(3)
    m.regrow_blank(3)
    candidate_known=0
    candidate_correct=0
    left_control_correct=0
    right_informative=0
    for t in range(64,80):
        x,y=observation(t)
        m.exchange_one_hop(x)
        candidate=m.recovered_function(3)
        if candidate is not None:
            candidate_known+=1
            candidate_correct+=int(candidate==y[3])
        single=marginal_predict(left_table,x[2])
        left_control_correct+=int(single is not None and single==y[3])
        right_informative+=int(m._predict_neighbor(4,0,x[4]) is not None)
    impossible=DistributedSetpoint()
    for t in range(64):
        x,y=observation(t,impossible=True)
        impossible.observe(x,y)
    impossible.lesion(3)
    impossible.regrow_blank(3)
    hallucinated=0
    for t in range(64,80):
        x,y=observation(t,impossible=True)
        impossible.exchange_one_hop(x)
        hallucinated+=int(impossible.recovered_function(3) is not None)
    success=(candidate_correct>=1 and hallucinated==0)
    return {
        "schema":"nci04f.yggdrasil.sourcefree-v1",
        "result":"PASS_NECESSARY_CONDITION_ONLY" if success else "NEGATIVE",
        "original_candidate_source_untouched":True,
        "damage_cell":3,
        "surviving_neighbor_observations":[left_count,right_count],
        "candidate_known_predictions":candidate_known,
        "candidate_correct_predictions":candidate_correct,
        "conventional_local_lookup_correct":left_control_correct,
        "right_neighbor_confident_predictions":right_informative,
        "heldout_postlesion_trials":16,
        "postlesion_target_supervision":0,
        "irrecoverable_hard_false_predictions":hallucinated,
        "scientific_first_use":0,
        "native_general_regeneration_accepted":False,
    }

class NCI04F(unittest.TestCase):
    def test_frozen_asymmetric_survival_and_abstention(self):
        result=perform()
        self.assertEqual(result,perform())
        self.assertEqual(result["conventional_local_lookup_correct"],16)
        self.assertEqual(result["right_neighbor_confident_predictions"],0)
        self.assertEqual(result["irrecoverable_hard_false_predictions"],0)
        self.assertEqual(result["postlesion_target_supervision"],0)
        self.assertIn(result["result"],("NEGATIVE","PASS_NECESSARY_CONDITION_ONLY"))
        raw=json.dumps(result,sort_keys=True)
        print("NCI04F_Y_RESULT="+raw)
        if path:=os.environ.get("NCI04F_RESULT_PATH"):
            with open(path,"x",encoding="utf8") as f:
                f.write(raw+"\n")

if __name__=="__main__":
    unittest.main()
