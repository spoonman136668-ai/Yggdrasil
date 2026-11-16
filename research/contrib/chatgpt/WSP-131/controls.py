"""WSP131 independent exact symbolic permutation search, fixed information design,
and fully grown conventional CART. NO source or binder imports.

Symbolic control reconstructs all 720 mappings from a separate WSP130
strong-symbolic warm prior. Fixed policy maximizes candidate-pair separation
using only this known prior and does not observe target outcomes.
"""
from __future__ import annotations
from itertools import permutations
from math import inf

def _remap(x,perm):
    z=x&192
    for frombit,tobit in enumerate(perm):
        if x&(1<<frombit):
            z|=1<<tobit
    return z

class _Dummy:
    cohort="transfer"
    def __init__(self,law):
        self.law_id=law
    def input(self,x):
        if type(x) is not int or not 0<=x<256:
            raise ValueError("WSP131_SYMBOLIC_BAD_INPUT")
        return x

class _Known:
    def __init__(self,prior,law):
        v=_Dummy(law)
        self.truth=tuple(prior.infer(v,x) for x in range(256))
        if any(bit not in (0,1) for bit in self.truth):
            raise ValueError("WSP131_SYMBOLIC_WARM_NOT_LEARNED")
        self.perms=list(permutations(range(6)))
        self.rows=[tuple(self.truth[_remap(x,p)] for x in range(256))
                   for p in self.perms]
        self.positives=[0]*256
        for i,signature in enumerate(self.rows):
            for x,val in enumerate(signature):
                if val:
                    self.positives[x]|=1<<i

class _SymbolicWorld:
    def __init__(self,view,known):
        self.view=view
        self.known=known
        self.candidates=list(range(len(known.perms)))
        self.events={}
    def observe(self,x,effect):
        if x in self.events:
            raise ValueError("WSP131_SYMBOLIC_DUPLICATE")
        self.events[x]=effect
        self.candidates=[i for i in self.candidates
                         if self.known.rows[i][x]==effect]
    def infer(self,x):
        if not self.candidates:return None
        first=self.known.rows[self.candidates[0]][x]
        for idx in self.candidates[1:]:
            if self.known.rows[idx][x]!=first:
                return None
        return first
    def resolved(self):
        if not self.candidates:return False
        first=self.known.rows[self.candidates[0]]
        return all(self.known.rows[i]==first for i in self.candidates[1:])

class ExactPermutationSymbolic:
    def __init__(self,prior):
        self.prior=prior
        self.known={}
        self.states={}
        self.old_bindings={}
    def _known(self,law):
        if law not in self.known:
            self.known[law]=_Known(self.prior,law)
        return self.known[law]
    def _state(self,view,create=False):
        if view.cohort=="transfer":
            return self.old_bindings.get(view.law_id)
        if view.seed not in self.states and create:
            st=_SymbolicWorld(view,self._known(view.law_id))
            self.states[view.seed]=st
            self.old_bindings.setdefault(view.law_id,st)
        st=self.states.get(view.seed)
        if (st is not None and st.view is not view and
            st.view.fingerprint()!=view.fingerprint()):
            raise ValueError("WSP131_SYMBOLIC_VIEW_DRIFT")
        return st
    def observe(self,view,evidence):
        if (view.cohort!="probe" or evidence.seed!=view.seed or
                evidence.law_id!=view.law_id or
                evidence.subject not in view.legal or
                view.input(evidence.subject)!=evidence.input or
                type(evidence.effect) is not int or evidence.effect not in (0,1)):
            raise ValueError("WSP131_SYMBOLIC_UNVERIFIED_EVIDENCE")
        self._state(view,True).observe(evidence.input,evidence.effect)
    def infer(self,view,subject):
        st=self._state(view)
        return None if st is None else st.infer(view.input(subject))
    def resolved(self,view):
        st=self._state(view)
        return st is not None and st.resolved()
    def remaining(self,view):
        st=self._state(view)
        return None if st is None else len(st.candidates)

def _plan_for_known(known):
    # Pair partition refinement: maximize the expected number of distinct
    # permutation hypotheses that a single *unobserved* response separates.
    groups=[(1<<720)-1]
    used=set()
    output=[]
    allbit=(1<<720)-1
    for _ in range(32):
        best_x=None;best_gain=0
        for x in range(256):
            if x in used:continue
            one=known.positives[x]
            gain=0
            for group in groups:
                n1=(group&one).bit_count()
                if n1:
                    n0=group.bit_count()-n1
                    gain+=n0*n1
            if gain>best_gain:
                best_x=x;best_gain=gain
        if best_x is None:
            best_x=next(x for x in range(256) if x not in used)
        used.add(best_x)
        output.append(best_x)
        one=known.positives[best_x]
        parts=[]
        for group in groups:
            yes=group&one
            no=group&(allbit^one)
            if yes:parts.append(yes)
            if no:parts.append(no)
        groups=parts
    return tuple(output)

class FixedSourceBlindSchedule:
    def __init__(self,symbolic):
        self.symbolic=symbolic
        self.cache={}
    def plan(self,view):
        law=view.law_id
        if law not in self.cache:
            self.cache[law]=_plan_for_known(self.symbolic._known(law))
        return self.cache[law]
    def choose(self,view,used):
        for x in self.plan(view):
            if x not in used:
                return view.subject(x)
        return None

def _majority(rows):
    yes=sum(bit for x,bit in rows)
    return int(yes>len(rows)-yes)

def _cart_fit(rows,remaining=tuple(range(8))):
    if not rows:
        return ("leaf",0)
    ys={value for _,value in rows}
    if len(ys)==1 or not remaining:
        return ("leaf",_majority(rows))
    best=None;best_quality=inf;parts=None
    for bit in remaining:
        left=[record for record in rows if not record[0]&(1<<bit)]
        right=[record for record in rows if record[0]&(1<<bit)]
        if not left or not right:continue
        quality=0
        for group in (left,right):
            yes=sum(v for _,v in group)
            quality+=(len(group)*len(group)-yes*yes-(len(group)-yes)**2)/len(group)
        if quality<best_quality:
            best_quality=quality
            best=bit
            parts=(left,right)
    if best is None:
        return ("leaf",_majority(rows))
    next_bits=tuple(bit for bit in remaining if bit!=best)
    return ("node",best,_cart_fit(parts[0],next_bits),
                     _cart_fit(parts[1],next_bits))

def _cart_predict(node,x):
    if node[0]=="leaf":return node[1]
    return _cart_predict(node[3] if x&(1<<node[1]) else node[2],x)

class FullyFitCART:
    def __init__(self):
        self.rows={}
        self.fitted={}
        self.cache={}
    def observe(self,view,evidence):
        if (view.cohort!="probe" or evidence.seed!=view.seed or
                evidence.law_id!=view.law_id or
                evidence.subject not in view.legal or
                view.input(evidence.subject)!=evidence.input or
                type(evidence.effect) is not int or evidence.effect not in (0,1)):
            raise ValueError("WSP131_CART_EVIDENCE_INVALID")
        rows=self.rows.setdefault(view.seed,{})
        if evidence.input in rows:
            raise ValueError("WSP131_CART_DUPLICATE")
        rows[evidence.input]=evidence.effect
        self.fitted.pop(view.seed,None)
    def fit(self,view):
        if view.seed not in self.rows or not self.rows[view.seed]:
            self.fitted[view.seed]=None
        else:
            self.fitted[view.seed]=_cart_fit(sorted(self.rows[view.seed].items()))
    def infer(self,view,subject):
        if view.cohort=="transfer":
            return None
        if view.seed not in self.fitted:self.fit(view)
        tree=self.fitted[view.seed]
        return None if tree is None else _cart_predict(tree,view.input(subject))

class StalePrior:
    def __init__(self,prior):
        self.prior=prior
    def observe(self,view,evidence):return None
    def infer(self,view,subject):
        return self.prior.infer(_Dummy(view.law_id),view.input(subject))

class NoUpdate:
    def observe(self,view,evidence):return None
    def infer(self,view,subject):return None
