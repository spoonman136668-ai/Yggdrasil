"""C34 source-free action-history contract and causal-custody tests."""
import hashlib
import json
import unittest

from research.native.itd02.r1.native_policy import PublicGrid,canonical
from research.mass_r7c34.belief import (
    SourceBeliefBeta,prior_token,key_current,source_sequences,
    sequence_support,shuffled_histories
)


def public(x=2,y=2,direction=0,blocked=False):
    return PublicGrid(x,y,6,6,direction,blocked)


def record(action=0,target=1,history=(2,0,1),blocked=False):
    return {"family":"MiniGrid-FourRooms-v0","seed":46101,"ordinal":1,
     "before":public(blocked=blocked),"chosen_action":action,
     "returned_front":target,"prior_history":history}


def real_shape(step=0,action=0,before=None,after=None,returnfront=False):
    b=before or public()
    aft=after or public(direction=(b.direction+(-1 if action==0 else 1))%4,
                         blocked=returnfront)
    return {"family":"MiniGrid-FourRooms-v0","seed":46101,"step":step,
            "before":b.__dict__,"chosen_action":action,"information_turn":False,
            "returned_after":aft.__dict__,"returned_reward":0.,
            "terminated":False,"truncated":False}


class C34CausalPriorHistoryUnit(unittest.TestCase):
    def test_source_observed_previous_action_consequence_not_future(self):
        previous=real_shape(action=2,after=public(x=3))
        q=prior_token(public(x=3),previous)
        self.assertEqual(q,(2,0,1))
        self.assertEqual(prior_token(public(),None),None)

    def test_original_public_future_label_never_predictor_input(self):
        m=SourceBeliefBeta(True)
        item=record(action=1,target=0)
        p=m.predict(item)
        changed={**item,"returned_front":1}
        self.assertEqual(m.predict(changed),p)
        m.observe(changed)
        self.assertNotEqual(m.predict(item),p)

    def test_both_action_conditioned_prior_and_current_counts(self):
        m=SourceBeliefBeta(True)
        sample=record(action=0,target=1,history=(2,0,1))
        first=m.predict(sample)
        for _ in range(6):m.observe(sample)
        self.assertGreater(m.predict(sample),first)
        self.assertEqual(m.base[key_current(sample)],[6,6])
        self.assertEqual(m.updates,6)
        other=record(action=1,target=1,history=(2,0,1))
        self.assertEqual(m.predict(other),0.5)

    def test_same_current_public_cue_different_retained_history(self):
        m=SourceBeliefBeta(True)
        h1=record(action=0,target=1,history=(0,1,0))
        h2=record(action=0,target=0,history=(2,0,1))
        for _ in range(5):m.observe(h1)
        for _ in range(5):m.observe(h2)
        self.assertGreater(m.predict(h1),m.predict(h2))
        markov=SourceBeliefBeta(False)
        for _ in range(5):markov.observe(h1)
        for _ in range(5):markov.observe(h2)
        self.assertEqual(markov.predict(h1),markov.predict(h2))

    def test_markov_model_no_stale_episode_hidden_posterior(self):
        m=SourceBeliefBeta(False)
        a=record(history=(2,0,1))
        b=record(history=(1,1,0))
        m.observe(a)
        self.assertEqual(m.predict(a),m.predict(b))
        self.assertEqual(m.conditional,{})

    def test_checkpoint_restored_identical_predictions_and_hash(self):
        m=SourceBeliefBeta(True)
        for i in range(20):
            m.observe(record(action=i%3,target=i%2,
                             history=(i%3,i%2,int(i%3==2))))
        saved=m.checkpoint()
        clone=SourceBeliefBeta.restore(saved)
        self.assertEqual(saved,clone.checkpoint())
        for k in range(3):
            x=record(action=k,history=(2,1,0))
            self.assertEqual(m.predict(x),clone.predict(x))

    def test_tampered_checkpoint_must_fail_closed(self):
        m=SourceBeliefBeta(True)
        m.observe(record())
        frame=json.loads(m.checkpoint())
        frame["payload"]["updates"]=99
        with self.assertRaisesRegex(ValueError,"TAMPERED"):
            SourceBeliefBeta.restore(canonical(frame))
        frame["sha256"]=hashlib.sha256(canonical(frame["payload"])).hexdigest()
        with self.assertRaisesRegex(ValueError,"BASE_TOTAL"):
            SourceBeliefBeta.restore(canonical(frame))

    def test_private_previous_action_payload_forbidden(self):
        m=SourceBeliefBeta(True)
        with self.assertRaisesRegex(ValueError,"MALFORMED"):
            m.observe(record(),history_override=(2,0,1,{"hidden_map":4}))
        bad=record();bad["before"]={"x":1,"private_map":123}
        with self.assertRaises(ValueError):
            m.predict(bad)

    def test_real_sequence_support_counts_and_inverse_without_simulation(self):
        first=real_shape(step=0,action=0,before=public(direction=0),
              after=public(direction=3))
        second=real_shape(step=1,action=1,before=public(direction=3),
               after=public(direction=0))
        third=real_shape(step=2,action=2,before=public(direction=0),
                after=public(x=3,direction=0))
        seq={("MiniGrid-FourRooms-v0",46101):[first,second,third]}
        x=[{"before":PublicGrid(**r["before"]),"chosen_action":r["chosen_action"],
            "returned_front":int(r["returned_after"]["front_blocked"])}
           for r in seq[("MiniGrid-FourRooms-v0",46101)]]
        report=sequence_support(seq,x)
        self.assertEqual(report["original_physical_two_action_windows"],2)
        self.assertEqual(report["original_physical_three_action_windows"],1)
        self.assertEqual(report["two_action_adjacent_inverse_turns"],1)
        self.assertEqual(report["observed_two_action_pair_counts"],{"01":1,"12":1})

    def test_shuffled_previous_actions_only_within_source_family(self):
        one=record(history=(0,0,0))
        two={**record(history=(2,1,1)),"ordinal":2}
        three={**record(history=(1,0,1)),"family":"OtherOriginalFamily"}
        four={**record(history=(0,1,0)),"family":"OtherOriginalFamily","ordinal":2}
        shifted=shuffled_histories([one,two,three,four])
        self.assertEqual(shifted[0],two["prior_history"])
        self.assertEqual(shifted[1],one["prior_history"])
        self.assertEqual(shifted[2],four["prior_history"])
        self.assertEqual(shifted[3],three["prior_history"])

    def test_episode_boundary_missingness_is_not_false_clear(self):
        first=record(history=None)
        m=SourceBeliefBeta(True)
        m.observe(first)
        self.assertEqual(m.conditional,{})
        self.assertEqual(m.predict(first),m.predict({**first,"prior_history":(0,0,0)}))

if __name__=="__main__":
    unittest.main()
