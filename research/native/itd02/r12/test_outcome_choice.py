"""R12 original-native action choice on selected source-PUBLIC fixture outcomes only."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

from research.native.itd02.r10.public_adapter import DoorKeyPublicAdapter, MISSION
from research.native.itd02.r11.affordance_cells import PublicAffordanceCells
from research.native.itd02.r12.outcome_choice import select_public_action


def view(front=(1,0,0), held=(1,0,0), direction=0):
    im = [[[1,0,0] for _ in range(7)] for _ in range(7)]
    im[3][5] = list(front)
    im[3][6] = list(held)
    return {"image":im,"direction":direction,"mission":MISSION}


KEY=(5,4,0)
LOCKED=(4,4,2)
OPEN=(4,4,0)
GOAL=(8,1,0)


def add_example(native, conventional, name, before, action, after,
                reward=0.0, terminated=False):
    source=DoorKeyPublicAdapter()
    source.reset_public(before)
    native.start_session(source,name)
    source.submit(action)
    event=source.complete(after,reward,terminated,False)
    native.learn_selected(source)
    conventional.fit(event)
    return event


class IndependentConventionalPolicy:
    """Separate conventional count histogram, feature extractor and utility policy."""
    def __init__(self):
        self.counts={}
    @staticmethod
    def key(front,held,action):
        return (tuple(front), None if held is None else tuple(held[:2]),action)
    @staticmethod
    def label(event):
        b,e=event["front_before"],event["front_after"]
        return (b != e, b[0] == e[0] == 4 and b[2] != e[2],
                event["carried_before"] != event["carried_after"],
                event["heading_before"] != event["heading_after"],
                event["reward"] > 0,event["terminated"],event["truncated"])
    def fit(self,event):
        k=self.key(event["front_before"],event["carried_before"],event["action"])
        d=self.counts.setdefault(k,{})
        outcome=self.label(event)
        d[outcome]=d.get(outcome,0)+1
    def select(self,public,objective,costs,min_samples):
        front=public["image"][3][5]
        carried=public["image"][3][6]
        held=carried if carried[0] in (5,6,7) else None
        feature={"carrying_changed":2,"visible_door_state_changed":1,"positive_reward":4}[objective]
        candidates=[]
        for a in range(7):
            rows=self.counts.get(self.key(front,held,a))
            if rows is None: continue
            n=sum(rows.values())
            if n < min_samples: continue
            p=sum(count for event,count in rows.items() if event[feature])/n
            value=p-costs[a]
            if p > 0 and value > 0: candidates.append((value,a))
        return sorted(candidates,key=lambda item:(-item[0],item[1]))[0][1] if candidates else None


def train():
    learner=PublicAffordanceCells()
    conventional=IndependentConventionalPolicy()
    examples=[
      ("key-pickup",view(front=KEY),3,view(front=(1,0,0),held=KEY),0,False),
      ("key-toggle-failure",view(front=KEY),5,view(front=KEY),0,False),
      ("door-locked-no-carry",view(front=LOCKED),5,view(front=LOCKED),0,False),
      ("door-locked-with-carry",view(front=LOCKED,held=KEY),5,view(front=OPEN,held=KEY),0,False),
      ("door-locked-forward-blocked",view(front=LOCKED,held=KEY),2,view(front=LOCKED,held=KEY),0,False),
      ("goal-forward-returns-reward",view(front=GOAL),2,view(front=(1,0,0)),0.75,True),
    ]
    for name,b,a,n,reward,done in examples:
        add_example(learner,conventional,name,b,a,n,reward,done)
    return learner,conventional


def git_blob(path):
    b=Path(path).read_bytes().replace(b"\r\n",b"\n")
    if b"\r" in b: raise ValueError("R12_UNCANONICAL_GIT_SOURCE")
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()


class R12SourceOnly(unittest.TestCase):
    def test_original_R7_R11_native_bytes_unchanged(self):
        root=Path(__file__).resolve().parents[1]
        blobs={
          "r7/learner.py":"204ecd993b954b23e66d6d1e8b3568e7c93183c5",
          "r8/revision.py":"346fb9eb7462208a6cbd28cfb51716c22e5ec857",
          "r9/evidence_cells.py":"66ec3befe92e2d2c2b7116217354a40f59e659d7",
          "r10/public_adapter.py":"3917d36ce9f86a2c1b998a0a2f93fb27674a9205",
          "r11/affordance_cells.py":"614c7dfb1b43f485009b70cb85e9b7b5119cafc2",
        }
        for name,digest in blobs.items():
            with self.subTest(name=name):self.assertEqual(git_blob(root/name),digest)

    def test_learned_key_pickup_is_selected_for_public_carrying_intent(self):
        n,b=train()
        query=view(front=KEY,direction=3)
        decision=select_public_action(n,query,"carrying_changed",costs=[.1]*7)
        self.assertEqual(decision["status"],"SELECT_LEARNED_PUBLIC_ACTION")
        self.assertEqual(decision["action"],3)
        self.assertEqual(decision["action_name"],"pickup")
        self.assertEqual(decision["expected_benefit"],1.0)
        self.assertEqual(decision["net_benefit"],.9)
        self.assertEqual(b.select(query,"carrying_changed",[.1]*7,1),3)

    def test_learned_key_carry_condition_changes_door_choice(self):
        n,b=train()
        carried=view(front=LOCKED,held=KEY,direction=2)
        not_carried=view(front=LOCKED,direction=1)
        with_key=select_public_action(n,carried,"visible_door_state_changed")
        without=select_public_action(n,not_carried,"visible_door_state_changed")
        self.assertEqual(with_key["action"],5)
        self.assertEqual(with_key["action_name"],"toggle")
        self.assertIsNone(without["action"])
        self.assertIn(3,with_key["unknown_actions"])
        self.assertEqual(b.select(carried,"visible_door_state_changed",[0]*7,1),5)
        self.assertIsNone(b.select(not_carried,"visible_door_state_changed",[0]*7,1))

    def test_reward_goal_is_only_explicit_pretrained_public_intent(self):
        n,b=train()
        with_goal=view(front=GOAL,direction=1)
        r=select_public_action(n,with_goal,"positive_reward",costs=[.25]*7)
        self.assertEqual(r["action"],2)
        self.assertEqual(r["expected_benefit"],1.0)
        self.assertEqual(r["net_benefit"],.75)
        self.assertEqual(b.select(with_goal,"positive_reward",[.25]*7,1),2)
        # NO global goal-location oracle: no public reward training => abstain.
        other=select_public_action(n,view(front=(2,5,0)),"positive_reward")
        self.assertIsNone(other["action"])

    def test_uncertainty_and_observation_cost_prevent_unjustified_action(self):
        n,b=train()
        key=view(front=KEY)
        # Give same source-public chosen context three additional failures.
        for i in range(3):
            add_example(n,b,f"noisy-pickup-{i}",key,3,key)
        observed=select_public_action(n,key,"carrying_changed",costs=[.4]*7)
        self.assertEqual(observed["status"],"ABSTAIN_NO_LEARNED_POSITIVE_ACTION")
        self.assertIsNone(observed["action"]) # 1/4 observed successes, cost .4
        self.assertIsNone(b.select(key,"carrying_changed",[.4]*7,1))
        # Lower query cost changes choice using exactly the SAME learned data.
        lowcost=select_public_action(n,key,"carrying_changed",costs=[.2]*7)
        self.assertEqual(lowcost["action"],3)
        self.assertEqual(lowcost["expected_benefit"],.25)
        self.assertAlmostEqual(lowcost["net_benefit"],.05)
        self.assertEqual(b.select(key,"carrying_changed",[.2]*7,1),3)
        self.assertIsNone(select_public_action(n,key,"carrying_changed",costs=[0]*7,min_samples=5)["action"])

    def test_equal_public_information_parity_on_840_queries(self):
        n,b=train()
        checked=0
        for front in (KEY,LOCKED,OPEN,GOAL,(2,5,0)):
            for held in ((1,0,0),KEY):
                for direction in range(4):
                    for action in ("carrying_changed","visible_door_state_changed","positive_reward"):
                        obs=view(front=front,held=held,direction=direction)
                        costs=[.2]*7
                        ours=select_public_action(n,obs,action,costs=costs,min_samples=1)
                        conventional=b.select(obs,action,costs,min_samples=1)
                        self.assertEqual(ours["action"],conventional)
                        checked+=1
        # 5 public front states × 2 carried visibility × 4 headings × 3 goals.
        self.assertEqual(checked,120)

    def test_invalid_intents_costs_private_fields_fail_closed(self):
        n,b=train()
        ordinary=view(front=KEY)
        raw=n.checkpoint()
        for objective in ("unlock",0,None,"all_actions"):
            with self.assertRaises(ValueError):select_public_action(n,ordinary,objective)
        for costs in ([0]*6,[0]*8,[0,0,0,0,0,-1,0],[0,0,0,0,0,float("nan"),0],[0,0,0,0,0,True,0]):
            with self.assertRaises(ValueError):select_public_action(n,ordinary,"carrying_changed",costs=costs)
        for evidence in (0,True,1.0,4097):
            with self.assertRaises(ValueError):select_public_action(n,ordinary,"carrying_changed",min_samples=evidence)
        leaked=copy.deepcopy(ordinary);leaked["agent_pos"]=[3,4]
        with self.assertRaises(ValueError):select_public_action(n,leaked,"carrying_changed")
        self.assertEqual(n.checkpoint(),raw)

    def test_cold_os_restored_native_knowledge_still_controls_decision(self):
        n,b=train()
        raw=n.checkpoint()
        code=("import json,sys;from research.native.itd02.r11.affordance_cells import PublicAffordanceCells;"
              "from research.native.itd02.r12.outcome_choice import select_public_action;"
              "from research.native.itd02.r10.public_adapter import MISSION;"
              "n=PublicAffordanceCells.restore(sys.stdin.buffer.read());"
              "im=[[[1,0,0] for _ in range(7)] for _ in range(7)];"
              "im[3][5]=[4,4,2];im[3][6]=[5,4,0];"
              "r=select_public_action(n,{'image':im,'direction':3,'mission':MISSION},'visible_door_state_changed');"
              "print(json.dumps({'action':r['action'],'samples':n.samples,'status':r['status']}))")
        p=subprocess.run([sys.executable,"-B","-c",code],input=raw,capture_output=True,timeout=30)
        self.assertEqual(p.returncode,0,p.stderr.decode())
        self.assertEqual(json.loads(p.stdout),{"action":5,"samples":6,"status":"SELECT_LEARNED_PUBLIC_ACTION"})


if __name__=="__main__":unittest.main()
