"""Independent symbolic two-atom XOR composer for WSP83.
No numerical-model import, no public-feature shared implementation, no
private source; same hypothesis class and minimum-complexity rule.
"""
from itertools import product

STATES=frozenset(product((0,1),repeat=6))
ACTIONS=tuple(range(6))
BASIS=(
    (("zero",-1,-1),("one",-1,-1))
    +tuple(("action",a,-1) for a in ACTIONS)
    +tuple(("prior",a,-1) for a in ACTIONS)
    +tuple(("second_prior",a,-1) for a in ACTIONS)
    +(("prior_equal",-1,-1),)
    +tuple(("action_prior",a,b) for a in ACTIONS for b in ACTIONS)
    +tuple(("action_second_prior",a,b) for a in ACTIONS for b in ACTIONS)
    +tuple(("prior_pair",a,b) for a in ACTIONS for b in ACTIONS)
    +tuple(("prior_equal_action",a,-1) for a in ACTIONS)
)
COST={
    "zero":0,"one":1,"action":1,"prior":1,"second_prior":1,
    "prior_equal":2,"action_prior":3,"action_second_prior":3,
    "prior_pair":3,"prior_equal_action":4,
}
assert len(BASIS)==135


def _eval(descriptor,action,history):
    name,i,j=descriptor
    last=history[-1] if history else None
    earlier=history[-2] if len(history)>1 else None
    if name=="zero":
        return False
    if name=="one":
        return True
    if name=="action":
        return action==i
    if name=="prior":
        return last==i
    if name=="second_prior":
        return earlier==i
    if name=="prior_equal":
        return last is not None and earlier is not None and last==earlier
    if name=="action_prior":
        return action==i and last==j
    if name=="action_second_prior":
        return action==i and earlier==j
    if name=="prior_pair":
        return last==i and earlier==j
    if name=="prior_equal_action":
        return last is not None and earlier is not None and last==earlier and action==i
    raise ValueError("unknown Boolean basis descriptor")


class IndependentSymbolicXorComposer:
    def __init__(self,paid_ledger):
        ledger=tuple(paid_ledger)
        if len(ledger)!=384:
            raise ValueError("exact charged history 384 required")
        current=(0,)*6
        history=[]
        rows=[]
        for record in ledger:
            try:
                before,a,after,cost=(
                    record.before,record.action,record.after,record.action_cost)
            except AttributeError as exc:
                raise ValueError("missing independent observation") from exc
            if (type(before) is not tuple or before not in STATES or
                    type(after) is not tuple or after not in STATES or
                    type(a) is not int or a not in ACTIONS or
                    type(cost) is not int or cost!=1 or before!=current):
                raise ValueError("unpaid or noncontinuous independent history")
            rows.append((before,a,after,tuple(history)))
            current=after
            history.append(a)
        patterns=[]
        for feature in BASIS:
            mask=0
            for k,(_,action,_,past) in enumerate(rows):
                if _eval(feature,action,past):
                    mask|=1<<k
            patterns.append(mask)
        reversed_patterns={}
        for ix,pat in enumerate(patterns):
            reversed_patterns.setdefault(pat,[]).append(ix)
        self.candidates=[]
        for bit in range(6):
            target=0
            for k,(before,action,after,_) in enumerate(rows):
                if before[bit]^after[bit]^int(action==bit):
                    target|=1<<k
            found=[]
            for i,pat in enumerate(patterns):
                c=COST[BASIS[i][0]]
                if pat==target:
                    found.append((c,(i,)))
                for j in reversed_patterns.get(pat^target,()):
                    if j>i:
                        found.append((c+COST[BASIS[j][0]]+2,(i,j)))
            if not found:
                raise ValueError("independent finite feature composition insufficient")
            least=min(k for k,_ in found)
            winners=sorted(pair for complexity,pair in found if complexity==least)
            if len(winners)>200:
                raise ValueError("independent confidence class too large")
            self.candidates.append(tuple(winners))
        self.charged_actions=len(ledger)

    def predict(self,state,action,history=()):
        if (type(state) is not tuple or state not in STATES or
                type(action) is not int or action not in ACTIONS or
                type(history) not in (list,tuple) or
                any(type(v) is not int or v not in ACTIONS for v in history)):
            raise ValueError("invalid independent symbolic query")
        result=[]
        for bit,candidates in enumerate(self.candidates):
            possible=set()
            for choices in candidates:
                residual=0
                for index in choices:
                    residual ^= int(_eval(BASIS[index],action,history))
                possible.add(state[bit]^int(action==bit)^residual)
            if len(possible)!=1:
                return None
            result.append(next(iter(possible)))
        return tuple(result)
