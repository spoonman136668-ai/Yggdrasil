"""AAI-11B: public do-action contrastive causal hypothesis tournament.

An independent learning signal, not a modification of AAI-11A's protected
memory. Grammar and planner are exactly the existing graph_recent8 control.
No hidden law/formulas, unchosen intervention outcomes, or science seeds.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"AAI-11A"))
sys.path.insert(0,str(HERE.parent/"AAI-11P"))
import world
import controls
import learner as graph


class InterventionTournament(graph.GraphWindow):
    """Eight public rows and their action counts, causal flips weight exactly 2."""

    def __init__(self):
        super().__init__("graph_recent8")
        self.action_counts=[]

    def _invalidate(self):
        super()._invalidate()
        self._selected_rules=None

    def observe(self,row):
        # Do public-field validation BEFORE any model state mutation.
        world.visible(row)
        step=row["actions_taken"]
        super().observe(row)
        self.action_counts.append(step)
        self.action_counts=self.action_counts[-8:]
        self._invalidate()
        if len(self.rows)!=len(self.action_counts):
            raise AssertionError("recent-eight public action alignment")

    def _selection(self):
        if self._selected_rules is None:
            loss=[list(a) for a in self.stats["mismatches"]]
            if len(self.rows)!=len(self.action_counts):
                raise AssertionError("invalid public history alignment")
            # The same eight rows used by the original graph_recent8. No
            # contrast may refer to an already-forgotten public observation.
            for i in range(1,len(self.rows)):
                if self.action_counts[i] != self.action_counts[i-1]+1:
                    continue
                x0,m0=self.rows[i-1]
                x1,m1=self.rows[i]
                if x0==x1:
                    continue  # setting a bit to its existing value is a no-op
                k0,k1=graph.x_key(x0),graph.x_key(x1)
                patterns=(
                    (graph.TRUTH01[k0],graph.TRUTH01[k1]),
                    (graph.TRUTH01[k0],graph.TRUTH01[k1]),
                    (graph.TRUTH2[k0][m0[0]][m0[1]],
                     graph.TRUTH2[k1][m1[0]][m1[1]]),
                )
                for out,(before,after) in enumerate(patterns):
                    true_flip=m0[out]^m1[out]
                    row=loss[out]
                    for h in range(len(row)):
                        if (before[h]^after[h])!=true_flip:
                            row[h]+=2
            self._selected_rules=tuple(
                min(range(n),key=lambda j:loss[out][j])
                for out,n in enumerate(graph.SIZES)
            )
        return self._selected_rules

    def predict(self,x):
        k=graph.x_key(x)
        if k not in self._pred_cache:
            h0,h1,h2=self._selection()
            m0=graph.TRUTH01[k][h0]
            m1=graph.TRUTH01[k][h1]
            m2=graph.TRUTH2[k][m0][m1][h2]
            self._pred_cache[k]=(graph.CONFIDENCE[m0],
                                 graph.CONFIDENCE[m1],
                                 graph.CONFIDENCE[m2])
        return self._pred_cache[k]

    def state(self):
        return {
            "type":"aai11b.intervention-tournament.v1",
            "public_rows":[[list(x),list(m),n]
                           for (x,m),n in zip(self.rows,self.action_counts)]
        }


def checkpoint(model):
    if not isinstance(model,InterventionTournament):
        raise TypeError("expected frozen interventional tournament")
    if len(model.rows)!=len(model.action_counts):
        raise ValueError("invalid public history size")
    return controls.canonical(model.state())


def restore(payload):
    doc=json.loads(payload)
    if controls.canonical(doc)!=payload or type(doc) is not dict or set(doc)!={"type","public_rows"}:
        raise ValueError("invalid canonical contrast checkpoint")
    if doc["type"]!="aai11b.intervention-tournament.v1" or type(doc["public_rows"]) is not list:
        raise ValueError("wrong contrast checkpoint")
    if len(doc["public_rows"])>8:
        raise ValueError("public memory exceeds matched eight rows")
    model=InterventionTournament()
    for item in doc["public_rows"]:
        if type(item) is not list or len(item)!=3:
            raise ValueError("invalid contrast public row")
        x=world.bits(item[0],6)
        m=world.bits(item[1],3)
        step=item[2]
        if type(step) is not int or step not in (0,1,2):
            raise ValueError("non-public action count")
        model._append((x,m))
        model.action_counts.append(step)
    model._invalidate()
    if checkpoint(model)!=payload:
        raise ValueError("cold restore not byte-identical")
    return model
