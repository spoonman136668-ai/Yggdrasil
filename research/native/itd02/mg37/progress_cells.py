"""MG37 opt-in local-cell reward evidence guard; source-free only.

Caller supplies chosen-action public reward AFTER the original action completes.
No hidden map/pose/goal, environment stepping, or scientific first-use here.
"""
import math
MIN_EVIDENCE=3
IMPROVEMENT_MARGIN=0.1

class LocalProgressCells:
    def __init__(self):
        self.count=[0]*7
        self.reward_sum=[0.0]*7

    def observe_selected(self, action, reward):
        if type(action) is not int or action not in range(7):
            raise ValueError("MG37_INVALID_SELECTED_ACTION")
        if type(reward) not in (int,float) or not math.isfinite(reward) or not -1<=reward<=1:
            raise ValueError("MG37_INVALID_PUBLIC_REWARD")
        self.count[action]+=1
        self.reward_sum[action]+=reward

    def choose(self, parent):
        if type(parent) is not int or parent not in range(7):
            raise ValueError("MG37_INVALID_PARENT")
        if self.count[parent]<MIN_EVIDENCE:
            return parent,False
        base=self.reward_sum[parent]/self.count[parent]
        best=base
        selected=parent
        for action in range(7):
            if action==parent or self.count[action]<MIN_EVIDENCE:
                continue
            mean=self.reward_sum[action]/self.count[action]
            if mean>0 and mean>base+IMPROVEMENT_MARGIN and mean>best+IMPROVEMENT_MARGIN:
                best=mean
                selected=action
        return selected, selected!=parent
