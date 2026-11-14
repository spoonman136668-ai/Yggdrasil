"""WSP85 source-blind paid causal-intervention selector.

The policy uses only the continuous charged PUBLIC ledger. It does not
import any evaluator/source module and never sees latent masks, private
truth labels, or a reset. All 20x20x20 candidate three-slot membership
hypotheses are fitted to observed public residuals with PARTIAL truth
tables, then each legal next action is valued by its disagreement across
compatible hypotheses. The deterministic two-step lookahead makes
otherwise rare action histories reachable.

Crucial scientific boundary: the finite mask grammar and lookahead
ranking were designed by researchers before outcomes; NOT autonomous
causal operator invention or a generally intelligent controller.
"""
from __future__ import annotations
from collections import Counter
from itertools import combinations

ACTIONS=tuple(range(6))
BALANCED=tuple(combinations(ACTIONS,3))
assert len(BALANCED)==20
MAX_POLICY_MODELS=512
REFIT_EVERY=12
FIRST_ACTIVE_STEP=144
LAST_STEP_EXCLUSIVE=384


class HypothesisInterventionPolicy:
    def __init__(self):
        self._models=[]
        self._last_refit=None
        self._last_public_target_bit=None
        self.refits=0
        self.max_candidates_kept=0
        self.max_candidates_total=0
        self.learned_residual_refits=0
        self.chosen_action_records=[]

    @staticmethod
    def _validate_history(ledger,history):
        if (type(history) not in (tuple,list)
                or any(type(a) is not int or a not in ACTIONS for a in history)
                or len(ledger)!=len(history)):
            raise ValueError("missing or inconsistent paid-action history")
        state=(0,)*6
        for row,a in zip(ledger,history):
            if (row.before!=state or row.action!=a
                    or type(row.action_cost) is not int or row.action_cost!=1
                    or type(row.after) is not tuple or len(row.after)!=6
                    or any(type(b) is not int or b not in (0,1)
                           for b in row.after)):
                raise ValueError("unpaid, altered or discontinuous public source row")
            state=row.after

    def _fit_version_space(self,ledger,history):
        n=len(ledger)
        if n==0:
            self._models=[]
            return
        bits=(1<<n)-1
        signatures=[[0]*20 for _ in range(3)]
        residual=[0]*6
        for t,(row,a) in enumerate(zip(ledger,history)):
            if row.action!=a:
                raise ValueError("paid action discrepancy")
            slots=(a,history[t-1] if t>=1 else None,
                   history[t-2] if t>=2 else None)
            for slot,observed in enumerate(slots):
                if observed is not None:
                    for k,mask in enumerate(BALANCED):
                        if observed in mask:
                            signatures[slot][k]|=1<<t
            for bit in ACTIONS:
                if row.before[bit]^row.after[bit]^int(bit==a):
                    residual[bit]|=1<<t

        target=max(ACTIONS,key=lambda bit:(residual[bit].bit_count(),-bit))
        if residual[target]==0:
            self._models=[]
            self._last_public_target_bit=None
            self.refits+=1
            return

        selected=[]
        total=0
        target_bits=residual[target]
        sigA,sigB,sigC=signatures
        for i,posA in enumerate(sigA):
            for j,posB in enumerate(sigB):
                # Four public (current,last) buckets; all eight operator
                # cells can remain unknown, but a cell cannot contradict
                # any physically charged outcome.
                negA=bits^posA
                negB=bits^posB
                sub=(negA&negB,posA&negB,negA&posB,posA&posB)
                for k,posC in enumerate(sigC):
                    masks=[cell & (bits^posC) for cell in sub]+[
                        cell & posC for cell in sub]
                    table=[]
                    compatible=True
                    for cell in masks:
                        matches=cell&target_bits
                        if cell and matches and matches!=cell:
                            compatible=False
                            break
                        table.append(None if cell==0 else int(matches==cell))
                    if compatible:
                        total+=1
                        if len(selected)<MAX_POLICY_MODELS:
                            selected.append((i,j,k,tuple(table)))
        self._models=selected
        self._last_public_target_bit=target
        self.max_candidates_kept=max(self.max_candidates_kept,len(selected))
        self.max_candidates_total=max(self.max_candidates_total,total)
        self.learned_residual_refits+=1
        self.refits+=1

    def _disagreement(self,action,history):
        if not self._models:
            return 0.0
        prev=history[-1] if history else None
        prev2=history[-2] if len(history)>=2 else None
        positive=0.0
        for mask_a,mask_prev,mask_prev2,table in self._models:
            cell=(int(action in BALANCED[mask_a])
                  +2*int(prev is not None and prev in BALANCED[mask_prev])
                  +4*int(prev2 is not None and prev2 in BALANCED[mask_prev2]))
            label=table[cell]
            positive+=0.5 if label is None else label
        probability=positive/len(self._models)
        return 4.0*probability*(1.0-probability)

    @staticmethod
    def _triple_counts(history):
        return Counter((history[i-2],history[i-1],history[i])
                       for i in range(2,len(history)))

    @staticmethod
    def _novelty(action,history,counts):
        prev=history[-1] if history else -1
        prev2=history[-2] if len(history)>=2 else -1
        return 1.0/(1.0+counts.get((prev2,prev,action),0))

    def _ranking(self,action,history,counts):
        present=self._disagreement(action,history)
        novelty=self._novelty(action,history,counts)
        future_history=tuple(history[-1:])+(action,)
        best_future=max(
            self._disagreement(next_action,future_history)
            for next_action in ACTIONS)
        future_novelty=max(
            self._novelty(next_action,future_history,counts)
            for next_action in ACTIONS)
        # Frozen source-blind utility weights (NOT fitted to outcomes).
        return 10.0*present+3.0*best_future+2.0*novelty+0.5*future_novelty

    def choose(self,step,paid_ledger,action_history):
        if (type(step) is not int or not FIRST_ACTIVE_STEP<=step<LAST_STEP_EXCLUSIVE
                or len(paid_ledger)!=step or len(action_history)!=step):
            raise PermissionError("WSP85 only selects physically paid StageB actions")
        self._validate_history(paid_ledger,action_history)
        if step==FIRST_ACTIVE_STEP or (step-FIRST_ACTIVE_STEP)%REFIT_EVERY==0:
            self._fit_version_space(paid_ledger,action_history)
            self._last_refit=step
        counts=self._triple_counts(action_history)
        ranking=[self._ranking(action,action_history,counts)
                 for action in ACTIONS]
        best=max(ACTIONS,key=lambda action:(ranking[action],-action))
        self.chosen_action_records.append({
            "charged_step":step,
            "selected_public_action":best,
            "active_models":len(self._models),
            "public_target_detected":self._last_public_target_bit is not None,
            "score":round(ranking[best],8),
        })
        return best

    def receipt(self):
        return {
            "source_blind_version_space_refits":self.refits,
            "max_consistent_hypotheses_total":self.max_candidates_total,
            "max_consistent_hypotheses_considered":self.max_candidates_kept,
            "refits_after_public_residual":self.learned_residual_refits,
            "paid_StageB_choices":len(self.chosen_action_records),
            "any_direct_private_source_lookups":False,
        }
