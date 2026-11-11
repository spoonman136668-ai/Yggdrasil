"""Evaluator-only causal world. Never imported by the numerical candidate."""
from knowledge import ACTIONS,bit,event_checked


class World:
    def __init__(self,identity):
        if type(identity) is not int or identity not in range(64):raise ValueError('WSP24_BAD_WORLD')
        self._c=tuple((identity>>j)&1 for j in range(6))

    def event(self,u,mask=0,x_value=0,y_value=0,flip_pair=None):
        for v in (u,x_value,y_value):bit(v)
        if type(mask) is not int or mask not in range(4):raise ValueError('WSP24_BAD_MASK')
        by,uy,xy,bz,xz,yz=self._c
        x=x_value if mask&1 else u
        y=y_value if mask&2 else by^(uy&u)^(xy&x)
        z=bz^(xz&x)^(yz&y)
        if flip_pair is not None and (x,y)==flip_pair:z^=1
        return event_checked((u,x,y,z,mask))

    def act(self,action):
        if action not in ACTIONS:raise ValueError('WSP24_BAD_ACTION')
        u,mask,value=action
        return self.event(u,mask,value if mask==1 else 0,value if mask==2 else 0)
