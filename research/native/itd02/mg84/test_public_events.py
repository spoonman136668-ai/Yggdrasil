"""MG84 observation-only public goal-event instrumentation tests, no world steps."""
import unittest
from research.native.itd02.mg84.paired_original_dev import (
    public_object_hits, public_selected_effect)
from research.native.itd02.mg28.test_selected_change_cells import frame

class PublicEventTest(unittest.TestCase):
    def test_visible_public_semantics_are_not_privileged(self):
        obs=frame()
        obs["image"][1][2]=[5,0,0]
        obs["image"][2][3]=[4,2,1]
        obs["image"][4][2]=[8,1,0]
        self.assertEqual(public_object_hits(obs),{
            "visible_key":True,"visible_door":True,"visible_goal":True})
        self.assertEqual(public_object_hits(frame()),{
            "visible_key":False,"visible_door":False,"visible_goal":False})
    def test_public_selected_key_disappearance_is_not_claimed_ground_truth(self):
        before=frame()
        before["image"][3][5]=[5,0,0]
        after=frame()
        self.assertEqual(public_selected_effect(before,3,after),
                         {"possible_public_key_pickup":True,"public_door_open":False})
        self.assertFalse(public_selected_effect(before,2,after)
                         ["possible_public_key_pickup"])
        self.assertFalse(public_selected_effect(before,3,frame(heading=1))
                         ["possible_public_key_pickup"])
    def test_direct_public_door_open_transition(self):
        before=frame()
        before["image"][3][5]=[4,0,1]
        after=frame()
        after["image"][3][5]=[4,0,0]
        self.assertTrue(public_selected_effect(before,5,after)["public_door_open"])
        self.assertFalse(public_selected_effect(before,3,after)["public_door_open"])
        after["image"][3][5]=[4,1,0]
        self.assertFalse(public_selected_effect(before,5,after)["public_door_open"])
    def test_no_route_or_hidden_state_required(self):
        before=frame()
        after=frame()
        self.assertEqual(public_selected_effect(before,5,after),
                         {"possible_public_key_pickup":False,"public_door_open":False})

if __name__=="__main__":
    unittest.main()
