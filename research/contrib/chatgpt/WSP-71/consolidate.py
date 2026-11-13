"""WSP71: source-blind gradientless fast->durable neural weight consolidation.

All student models reuse the Stage-A teacher's numerical *hidden* ReLU weight
bank, then directly edit a fresh durable numerical readout through rank-one
ridge updates. "Dreams" are self-generated LABELS of the saved Stage-A
teacher at public hypothetical state/action inputs, never evaluator oracle
outcomes. All students see exactly the same 96 charged Phase-B observations;
matched controls get the same number of extra numerical updates.

No source import, privileged physics, causal symbolic rule compiler, gradient,
autoregressive token objectives, or live training reset in this module.
"""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
from random import Random
import sys

_PARENT=Path(__file__).resolve().parents[1]/"WSP-69"
sys.path.insert(0,str(_PARENT))
from growing_neural import FeatureGrowthNeural,STATES,ACTIONS,check


DREAM_MAX=32
PHASE_B_CHARGES=96


def stable_rank(seed,state,action,scope):
    h=sha256(f"WSP71|{scope}|{seed}|{state}|{action}".encode("ascii")).digest()
    return h


def visible_dreams(cold_teacher,phase_a_ledger,seed):
    """Bounded, source-blind dream proposals plus all attempted query receipts.

    Public hypothetical inputs are NOT fresh paid source transitions. Exact
    teacher output labels and confidence come from the teacher's own neural
    matrix, so they can be wrong when audited against withheld physics.
    """
    seen_a={(s,a) for s,a,y in phase_a_ledger}
    result=[]
    attempted=0
    for s,a in sorted(((s,a) for s in STATES for a in ACTIONS),
                      key=lambda k:(int(k in seen_a),
                                    stable_rank(seed,k[0],k[1],"dream"))):
        attempted+=1
        prediction=cold_teacher.predict(s,a)
        if prediction is None:
            continue
        result.append((s,a,prediction))
        if len(result)>=DREAM_MAX:
            break
    return tuple(result),attempted


def distinct_charged_A(rows,seed):
    table={}
    for s,a,y in rows:
        if (s,a) in table and table[(s,a)]!=y:
            raise ValueError("non-Markov conflicting charged A facts")
        table[(s,a)]=y
    return tuple((s,a,table[s,a]) for s,a in
                 sorted(table,key=lambda k:stable_rank(
                     seed,k[0],k[1],"realA")))


def select_rehearsal(teacher,phase_a_ledger,phase_b_ledger,seed):
    if (len(phase_a_ledger)!=96 or len(phase_b_ledger)!=96 or
            not all(type(s) is tuple and s in STATES and a in ACTIONS and
                    type(y) is tuple and y in STATES for s,a,y in
                    tuple(phase_a_ledger)+tuple(phase_b_ledger))):
        raise ValueError("training custody invalid")
    dreamed,query_count=visible_dreams(teacher,phase_a_ledger,seed)
    true_A=distinct_charged_A(phase_a_ledger,seed)
    # All controlled arms receive exactly k extra weight-space updates;
    # never backfill absent teacher predictions with evaluator labels.
    k=min(DREAM_MAX,len(dreamed),len(true_A))
    dreams=tuple(dreamed[:k])
    stored=tuple(true_A[:k])
    rng=Random(int.from_bytes(sha256(
        f"WSP71|B-repeat|{seed}".encode("ascii")).digest(),"big"))
    duplicates=tuple(phase_b_ledger[rng.randrange(len(phase_b_ledger))]
                     for _ in range(k))
    corrupted=tuple((s,(a+1)%4,y) for s,a,y in dreams)
    return {
        "k":k,
        "dreams":dreams,
        "stored_A":stored,
        "B_repeats":duplicates,
        "scrambled_dreams":corrupted,
        "teacher_query_count":query_count,
        "teacher_confident_candidate_count":len(dreamed),
        "actual_A_distinct":len(true_A)
    }


class DurableNeuralWeights:
    """Numerical-only student, with replay labels never in cold snapshot."""

    gradient_updates=0

    def __init__(self,teacher_snapshot):
        teacher=FeatureGrowthNeural.restore(teacher_snapshot)
        self.model=FeatureGrowthNeural()
        self.model.hidden_weights=[list(w) for w in teacher.hidden_weights]
        self.model.hidden_biases=list(teacher.hidden_biases)
        self.model._init_readout()
        self.model.growth_rounds=2
        self.model.charged_actions=96  # 96 legitimate Phase-B physical charges
        self.weight_edit_count=0
        self.physical_rows=0
        self.rehearsal_rows=0

    def fit_phase_b(self,rows):
        if len(rows)!=PHASE_B_CHARGES or self.weight_edit_count:
            raise ValueError("bounded Phase-B physical evidence required")
        for s,a,y in rows:
            self._update(s,a,y)
            self.physical_rows+=1

    def replay(self,rows):
        if self.physical_rows!=PHASE_B_CHARGES or self.rehearsal_rows:
            raise ValueError("rehearsal requires charged Phase B first")
        if len(rows)>DREAM_MAX:
            raise ValueError("bounded synthetic memory budget")
        for s,a,y in rows:
            self._update(s,a,y)
            self.rehearsal_rows+=1

    def _update(self,state,action,target):
        check(state,action)
        check(target,action)
        self.model._learn_row(state,action,target)
        self.weight_edit_count+=1

    def predict(self,state,action):
        return self.model.predict(state,action)

    def raw(self,state,action):
        return self.model.raw(state,action)

    def snapshot(self):
        result=self.model.snapshot()
        for forbidden in ('"ledger"','"centers"','"source"','"dreams"','"target_rows"'):
            if forbidden in result:
                raise AssertionError("cold neural weight snapshot leaked memory")
        return result

    @staticmethod
    def restore(raw):
        return FeatureGrowthNeural.restore(raw)

    def snapshot_bytes(self):
        return len(self.snapshot().encode("ascii"))
