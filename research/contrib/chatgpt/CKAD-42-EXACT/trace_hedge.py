"""Fixture-only first-divergence diagnosis of online Hedge weights.

No CKAD scientific generators, original development seeds or held first-use.
Trace is deliberately bounded to the first 180 engineering fixture events.
"""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
FIX=HERE.parent/"CKAD-42-ENG"/"fixtures.py"
spec=importlib.util.spec_from_file_location("ckad42_hedge_trace_fixture",FIX)
F=importlib.util.module_from_spec(spec)
spec.loader.exec_module(F)
M=F.M

def trace():
    relation=M.NativeInterventionRelations()
    rows=[]
    for t in range(180):
        identifier,views,row=F.fixture_event("action_interactions",t)
        first,next_state,second,reward=(row[k] for k in ("x1","s2","x2","y"))
        i_t=relation._inputs(views[0],first)
        i_y=relation._inputs(views[0],first,next_state,second)
        operands=[]
        for mode in ("full","short"):
            p=relation.transition.predict(i_t,mode)
            q=relation.terminal.predict(i_y,mode)
            loss=((p-next_state)**2+(q-reward)**2)/2
            factor=M._portable_exp(-M.ETA*loss)
            operands.extend((p.hex(),q.hex(),loss.hex(),factor.hex()))
        before=tuple(v.hex() for v in relation.hedge)
        relation.observe(identifier,views,row)
        after=tuple(v.hex() for v in relation.hedge)
        rows.append([t,*operands,*before,*after])
    print("CKAD42_EXACT_HEDGE_TRACE="+json.dumps({
        "schema":"yggdrasil.ckad42.exact-hedge-fixture-trace.v1",
        "source":"action_interactions engineering fixture only",
        "events":180,"orig_science_replayed":False,
        "columns":["t","p_full","q_full","loss_full","factor_full",
                   "p_short","q_short","loss_short","factor_short",
                   "hedge_before_full","hedge_before_short",
                   "hedge_after_full","hedge_after_short"],
        "rows":rows},separators=(",",":")))

if __name__=="__main__":
    trace()
