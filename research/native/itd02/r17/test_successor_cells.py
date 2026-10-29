"""R17 focused original source selected consequence tests; no simulator."""
import unittest
from research.native.itd02.r10.public_adapter import DoorKeyPublicAdapter,MISSION
from research.native.itd02.r17.successor_cells import SuccessorCells

def public(front=1):
    frame=[[[1,0,0] for _ in range(7)] for _ in range(7)]
    if front!=1:frame[3][5]=[front,0,0]
    return {"image":frame,"direction":0,"mission":MISSION}

def learn(actor,adapter,before,action,after):
    adapter.submit(action)
    adapter.complete(after,0.0,False,False)
    return actor.learn_selected(adapter,before,after)

class R17SelectedSourceTests(unittest.TestCase):
    def test_authenticated_selected_reversal_is_disfavored(self):
        actor=SuccessorCells();a=public();b=public(front=4)
        adapter=DoorKeyPublicAdapter()
        adapter.reset_public(a)
        actor.start_session(adapter,"r17-original-selected-cycle",live=True)
        learn(actor,adapter,a,5,b)
        learn(actor,adapter,b,5,a)
        choice=actor.choose(a)
        self.assertNotEqual(choice["action"],5)
        self.assertFalse(choice["external_fallback"])
        self.assertEqual(actor.samples,2)
        self.assertEqual(actor.parent.samples,2)
        checkpoint=actor.checkpoint()
        cold=SuccessorCells.restore(checkpoint)
        self.assertEqual(cold.checkpoint(),checkpoint)
        self.assertEqual(cold.choose(a),choice)
        with self.assertRaises(ValueError):SuccessorCells.restore(checkpoint+b"0")

    def test_repeated_no_progress_source_escape_and_reset(self):
        actor=SuccessorCells();a=public()
        adapter=DoorKeyPublicAdapter();adapter.reset_public(a)
        actor.start_session(adapter,"r17-original-selfloop",live=True)
        choices=set()
        for i in range(9):
            chosen=actor.choose(a)["action"]
            choices.add(chosen)
            learn(actor,adapter,a,chosen,a)
        self.assertGreaterEqual(len(choices),4)
        self.assertEqual(actor.parent.samples,9)
        self.assertEqual(actor.samples,9)
        fresh=DoorKeyPublicAdapter()
        fresh.reset_public(a)
        actor.start_session(fresh,"r17-cold-next-episode",live=True)
        self.assertEqual(actor.attempts,{})
        self.assertEqual(actor.visits,{})
        self.assertEqual(actor.samples,9)

    def test_unreturned_wrong_and_duplicate_selected_rejected(self):
        actor=SuccessorCells();a=public()
        adapter=DoorKeyPublicAdapter();adapter.reset_public(a)
        actor.start_session(adapter,"r17-strict-source",live=True)
        with self.assertRaises(ValueError):actor.learn_selected(adapter,a,a)
        adapter.submit(1)
        with self.assertRaises(ValueError):actor.learn_selected(adapter,a,a)
        adapter.complete(a,0.0,False,False)
        with self.assertRaises(ValueError):actor.learn_selected(adapter,public(front=4),a)
        self.assertEqual(actor.samples,0)
        self.assertEqual(actor.parent.samples,0)
        actor.learn_selected(adapter,a,a)
        with self.assertRaises(ValueError):actor.learn_selected(adapter,a,a)
        self.assertEqual(actor.samples,1)

if __name__=="__main__":unittest.main()
