"""Independent symbolic WSP84 three-variable Boolean operator learner.

Never imports numeric learner, private source, or evaluator. Uses independent
Boolean membership predicates and exact paid-history ledger consistency,
then a table lookup rather than numerical ReLU minterms. Hypothesis
class and action budget match the candidate, so a tie is NOT superiority.
"""
from itertools import combinations,product

ACTIONS=tuple(range(6))
STATES=frozenset(product((0,1),repeat=6))
MASKS=tuple(combinations(ACTIONS,3))
ATOMS=tuple((slot,mask) for slot in (0,1,2) for mask in MASKS)
assert len(ATOMS)==60


def _valid(s,a,h):
    return (type(s) is tuple and s in STATES
            and type(a) is int and a in ACTIONS
            and type(h) in (list,tuple)
            and all(type(x) is int and x in ACTIONS for x in h))


def _active(atom,action,history):
    slot,mask=atom
    observed=(action if slot==0 else
              history[-1] if slot==1 and history else
              history[-2] if slot==2 and len(history)>=2 else None)
    return observed is not None and observed in mask


class IndependentTruthTableControl:
    def __init__(self,charged):
        ledger=tuple(charged)
        if len(ledger)!=384:
            raise ValueError("strong symbolic control needs all paid actions")
        current=(0,)*6
        history=[]
        training=[]
        for row in ledger:
            try:
                before,action,after,cost=(
                    row.before,row.action,row.after,row.action_cost)
            except AttributeError as exc:
                raise ValueError("missing public observation") from exc
            if (type(before) is not tuple or before not in STATES
                    or type(after) is not tuple or after not in STATES
                    or type(action) is not int or action not in ACTIONS
                    or type(cost) is not int or cost!=1 or before!=current):
                raise ValueError("noncontinuous or unpaid source evidence")
            training.append((before,action,after,tuple(history)))
            current=after
            history.append(action)
        full=(1<<len(training))-1
        signatures=[]
        for atom in ATOMS:
            bits=0
            for n,(_,action,_,past) in enumerate(training):
                if _active(atom,action,past):
                    bits|=1<<n
            signatures.append(bits)
        self.solutions=[]
        for bit in ACTIONS:
            wanted=0
            for n,(before,action,after,_) in enumerate(training):
                if before[bit]^after[bit]^int(action==bit):
                    wanted|=1<<n
            if wanted in (0,full):
                self.solutions.append([((),(int(wanted==full),))])
                continue
            found=[]
            for arity in (1,2,3):
                for combo in combinations(range(len(ATOMS)),arity):
                    # Independent Boolean partition, not reused numeric
                    # learner feature values or truth-table implementation.
                    table=[]
                    possible=True
                    for cell in range(1<<arity):
                        support=full
                        for j,feature in enumerate(combo):
                            membership=signatures[feature]
                            support&=(membership if cell&(1<<j)
                                      else full^membership)
                        if support==0:
                            possible=False
                            break  # Never fill unseen table cells.
                        overlap=wanted&support
                        if overlap!=0 and overlap!=support:
                            possible=False
                            break
                        table.append(int(overlap==support))
                    if possible:
                        found.append((combo,tuple(table)))
                        if len(found)>64:
                            raise ValueError("symbolic operator underidentified")
                if found:
                    break
            if not found:
                raise ValueError("no Boolean operator of <=3 indicators explains paid data")
            self.solutions.append(found)
        self.charged_actions=384

    def predict(self,state,action,history=()):
        if not _valid(state,action,history):
            raise ValueError("invalid symbolic public action/history")
        out=[]
        for bit,all_solutions in enumerate(self.solutions):
            possible=set()
            for feature_ids,truth_table in all_solutions:
                pattern=sum(int(_active(ATOMS[id],action,history))<<j
                            for j,id in enumerate(feature_ids))
                residual=truth_table[pattern]
                possible.add(state[bit]^int(action==bit)^residual)
            if len(possible)!=1:
                return None
            out.append(next(iter(possible)))
        return tuple(out)
